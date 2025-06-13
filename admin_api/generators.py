from django.contrib import admin
from django.db import models
from rest_framework import serializers, viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.urls import reverse, NoReverseMatch
from .permissions import AdminPermission
from .utils import get_model_metadata

class AdminAPIGenerator:
    """Automatically generate API endpoints for registered admin models"""
    
    @staticmethod
    def generate_serializer(model, model_admin):
        """Generate dynamic serializer based on admin configuration"""
        
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