from rest_framework.permissions import BasePermission

class AdminPermission(BasePermission):
    """
    Custom permission for admin API that respects Django admin permissions
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        # Staff users only
        if not request.user.is_staff:
            return False
        
        # Superusers have all permissions
        if request.user.is_superuser:
            return True
        
        # Check specific model permissions
        model = getattr(view, 'queryset', None)
        if model is not None:
            model = model.model
            opts = model._meta
            
            if request.method == 'GET':
                return request.user.has_perm(f'{opts.app_label}.view_{opts.model_name}')
            elif request.method == 'POST':
                return request.user.has_perm(f'{opts.app_label}.add_{opts.model_name}')
            elif request.method in ['PUT', 'PATCH']:
                return request.user.has_perm(f'{opts.app_label}.change_{opts.model_name}')
            elif request.method == 'DELETE':
                return request.user.has_perm(f'{opts.app_label}.delete_{opts.model_name}')
        
        return False
    
    def has_object_permission(self, request, view, obj):
        """Object-level permissions (can be extended for row-level security)"""
        return self.has_permission(request, view) 