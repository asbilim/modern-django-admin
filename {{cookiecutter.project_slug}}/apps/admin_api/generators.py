from django.contrib import admin
from django.db import models
from rest_framework import serializers, viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.urls import reverse, NoReverseMatch
from .permissions import AdminPermission
from .utils import get_model_metadata
from django.contrib.auth import get_user_model

class AdminAPIGenerator:
    """Automatically generate API endpoints for registered admin models"""
    
    @staticmethod
    def generate_serializer(model, model_admin):
        """Generate dynamic serializer based on admin configuration"""
        
        # Special handling for the User model to correctly handle passwords
        if model == get_user_model():
            
            def create(self, validated_data):
                # Use create_user to handle password hashing
                groups = validated_data.pop('groups', [])
                user_permissions = validated_data.pop('user_permissions', [])
                
                user = get_user_model().objects.create_user(**validated_data)
                
                if groups:
                    user.groups.set(groups)
                if user_permissions:
                    user.user_permissions.set(user_permissions)
                return user

            def update(self, instance, validated_data):
                # Handle password update separately
                password = validated_data.pop('password', None)
                
                # Handle M2M fields
                groups = validated_data.pop('groups', None)
                user_permissions = validated_data.pop('user_permissions', None)

                if password:
                    instance.set_password(password)
                
                if groups is not None:
                    instance.groups.set(groups)
                
                if user_permissions is not None:
                    instance.user_permissions.set(user_permissions)

                # Update other fields
                for attr, value in validated_data.items():
                    setattr(instance, attr, value)
                instance.save()

                return instance

            class Meta:
                pass
            
            Meta.model = model
            Meta.fields = [field.name for field in model._meta.fields] + ['groups', 'user_permissions']
            Meta.extra_kwargs = {
                'password': {'write_only': True, 'style': {'input_type': 'password'}}
            }
            
            attrs = {
                'Meta': Meta,
                'create': create,
                'update': update,
            }
            return type('UserAdminSerializer', (serializers.ModelSerializer,), attrs)
        
        class Meta:
            pass
        
        Meta.model = model
        Meta.fields = '__all__'
        Meta.read_only_fields = getattr(model_admin, 'readonly_fields', [])
        
        # Create dynamic serializer class
        attrs = {'Meta': Meta}
        
        # Add custom field handling
        for field in model._meta.fields:
            if hasattr(field, 'choices') and field.choices:
                attrs[f'{field.name}_display'] = serializers.CharField(
                    source=f'get_{field.name}_display',
                    read_only=True
                )
        
        # Add foreign key representations
        for field in model._meta.fields:
            if isinstance(field, models.ForeignKey):
                attrs[f'{field.name}_str'] = serializers.CharField(
                    source=f'{field.name}.__str__',
                    read_only=True
                )
        
        serializer_name = f'{model.__name__}AdminSerializer'
        return type(serializer_name, (serializers.ModelSerializer,), attrs)
    
    @staticmethod
    def generate_viewset(model, model_admin):
        """Generate dynamic viewset with admin functionality"""
        
        serializer_class = AdminAPIGenerator.generate_serializer(model, model_admin)
        
        class DynamicAdminViewSet(viewsets.ModelViewSet):
            permission_classes = [AdminPermission]
            filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
            
            # Configure filtering based on admin settings
            filterset_fields = getattr(model_admin, 'list_filter', [])
            search_fields = getattr(model_admin, 'search_fields', [])
            ordering_fields = '__all__'
            ordering = getattr(model_admin, 'ordering', ['-id'])
            
            def get_queryset(self):
                """Apply admin's queryset logic"""
                if hasattr(model_admin, 'get_queryset'):
                    return model_admin.get_queryset(self.request)
                return model.objects.all()
            
            @action(detail=False, methods=['post'], url_path='import')
            def bulk_import(self, request):
                """
                Bulk import objects from a JSON or CSV file.
                The file should be sent as multipart/form-data with the key 'file'.
                The file format is determined by the file extension (.json or .csv).
                An optional 'format' field can be used as a fallback.
                """
                from rest_framework.parsers import MultiPartParser, FormParser
                import json
                import csv
                import io

                self.parser_classes = [MultiPartParser, FormParser]
                
                file_obj = request.FILES.get('file')
                if not file_obj:
                    return Response({'error': 'File not provided.'}, status=400)

                # Determine file format: prioritize file extension, then 'format' param, then default to json
                filename = file_obj.name.lower()
                if filename.endswith('.json'):
                    file_format = 'json'
                elif filename.endswith('.csv'):
                    file_format = 'csv'
                else:
                    file_format = request.data.get('format', 'json').lower()

                try:
                    # Read the entire file content into a string for parsing
                    file_content = file_obj.read().decode('utf-8')
                    
                    if file_format == 'json':
                        data = json.loads(file_content)
                    elif file_format == 'csv':
                        csv_reader = csv.DictReader(io.StringIO(file_content))
                        data = list(csv_reader)
                    else:
                        return Response({'error': f"Unsupported format: {file_format}"}, status=400)
                except Exception as e:
                    return Response({'error': f"Error parsing file: {str(e)}"}, status=400)

                if not isinstance(data, list):
                    return Response({'error': 'File content should be a list of objects.'}, status=400)

                serializer = self.get_serializer(data=data, many=True)
                try:
                    serializer.is_valid(raise_exception=True)
                    self.perform_create(serializer)
                    return Response(
                        {'status': 'success', 'created_count': len(serializer.data)},
                        status=status.HTTP_201_CREATED
                    )
                except serializers.ValidationError as e:
                    return Response({'error': 'Validation Error', 'details': e.detail}, status=400)
                except Exception as e:
                    return Response({'error': f"An unexpected error occurred: {str(e)}"}, status=400)
            
            @action(detail=False, methods=['get'])
            def config(self, request):
                """Return admin configuration for frontend"""
                try:
                    # Build URL paths without the domain
                    model_url = reverse(f'admin_api:{model._meta.model_name}-list')
                except NoReverseMatch:
                    model_url = None

                config = {
                    'model_name': model._meta.model_name,
                    'verbose_name': str(model._meta.verbose_name),
                    'verbose_name_plural': str(model._meta.verbose_name_plural),
                    'api_url': model_url,
                    'model_url': model_url,
                    'fields': get_model_metadata(model, model_admin),
                    'admin_config': {
                        'list_display': getattr(model_admin, 'list_display', []),
                        'list_filter': getattr(model_admin, 'list_filter', []),
                        'search_fields': getattr(model_admin, 'search_fields', []),
                        'readonly_fields': getattr(model_admin, 'readonly_fields', []),
                        'ordering': getattr(model_admin, 'ordering', []),
                    },
                    'permissions': self._get_permissions_info(request),
                    'frontend_config': getattr(model_admin.Meta, 'frontend_config', {}) 
                                     if hasattr(model_admin, 'Meta') else {}
                }
                return Response(config)
            
            @action(detail=False, methods=['post'])
            def bulk_action(self, request):
                """Handle bulk actions"""
                action_name = request.data.get('action')
                ids = request.data.get('ids', [])
                
                if not action_name or not ids:
                    return Response({'error': 'Action and ids required'}, status=400)
                
                queryset = self.get_queryset().filter(id__in=ids)
                
                # Check if action exists in model_admin
                if hasattr(model_admin, action_name):
                    action_func = getattr(model_admin, action_name)
                    try:
                        action_func(model_admin, request, queryset)
                        return Response({'success': True, 'message': f'Action {action_name} completed'})
                    except Exception as e:
                        return Response({'error': str(e)}, status=400)
                
                return Response({'error': 'Action not found'}, status=404)
            
            @action(detail=False, methods=['get'])
            def export(self, request):
                """Export data in various formats"""
                format_type = request.query_params.get('format', 'csv')
                queryset = self.filter_queryset(self.get_queryset())
                
                if format_type == 'csv':
                    return self._export_csv(queryset)
                elif format_type == 'json':
                    return self._export_json(queryset)
                
                return Response({'error': 'Unsupported format'}, status=400)
            
            def _get_permissions_info(self, request):
                """Get user permissions for this model"""
                opts = model._meta
                return {
                    'add': request.user.has_perm(f'{opts.app_label}.add_{opts.model_name}'),
                    'change': request.user.has_perm(f'{opts.app_label}.change_{opts.model_name}'),
                    'delete': request.user.has_perm(f'{opts.app_label}.delete_{opts.model_name}'),
                    'view': request.user.has_perm(f'{opts.app_label}.view_{opts.model_name}'),
                }
            
            def _export_csv(self, queryset):
                import csv
                from django.http import HttpResponse
                
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = f'attachment; filename="{model._meta.model_name}.csv"'
                
                writer = csv.writer(response)
                
                # Write headers
                fields = [f.name for f in model._meta.fields]
                writer.writerow(fields)
                
                # Write data
                for obj in queryset:
                    writer.writerow([getattr(obj, field) for field in fields])
                
                return response
            
            def _export_json(self, queryset):
                from django.http import JsonResponse
                serializer = self.get_serializer(queryset, many=True)
                return JsonResponse(serializer.data, safe=False)
        
        DynamicAdminViewSet.serializer_class = serializer_class
        return DynamicAdminViewSet

    @classmethod
    def register_all(cls):
        """Register API endpoints for all admin models"""
        viewsets = {}
        
        for model, model_admin in admin.site._registry.items():
            viewset = cls.generate_viewset(model, model_admin)
            viewsets[model._meta.model_name] = viewset
        
        return viewsets 