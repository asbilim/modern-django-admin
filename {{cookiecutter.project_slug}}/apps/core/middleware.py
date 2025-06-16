import time
from .models import RequestLog

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()
        
        response = self.get_response(request)
        
        # Only log API requests, and exclude admin/schema paths
        path = request.path_info
        if path.startswith('/api/') and not path.startswith('/api/admin/') and not path.startswith('/api/schema/'):
            end_time = time.time()
            response_time_ms = int((end_time - start_time) * 1000)
            
            user = request.user if request.user.is_authenticated else None
            
            # Get IP address
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip_address = x_forwarded_for.split(',')[0]
            else:
                ip_address = request.META.get('REMOTE_ADDR')

            RequestLog.objects.create(
                user=user,
                ip_address=ip_address,
                method=request.method,
                path=path,
                status_code=response.status_code,
                response_time_ms=response_time_ms,
            )
            
        return response 