from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Product, Order, EmailTemplate
from .serializers import ProductSerializer, OrderSerializer, EmailTemplateSerializer
from rest_framework.permissions import IsAdminUser, AllowAny

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A viewset for viewing products.
    """
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'

class OrderViewSet(viewsets.ModelViewSet):
    """
    A viewset for creating and viewing orders.
    """
    serializer_class = OrderSerializer
    
    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and user.is_staff:
            return Order.objects.all()
        elif user.is_authenticated:
            return Order.objects.filter(user=user)
        return Order.objects.none()

    def get_permissions(self):
        if self.action == 'create':
            self.permission_classes = [AllowAny]
        else:
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()

class EmailTemplateViewSet(viewsets.ModelViewSet):
    """
    A viewset for managing email templates. Requires admin permissions.
    """
    queryset = EmailTemplate.objects.all()
    serializer_class = EmailTemplateSerializer
    permission_classes = [IsAdminUser]

    # This defines the available placeholders for each email event type.
    PLACEHOLDER_DEFINITIONS = {
        'new_order_admin_notification': {
            'description': 'Variables available for the new order notification email sent to admins.',
            'placeholders': [
                {'name': '{{ order.id }}', 'description': 'The unique ID of the order.'},
                {'name': '{{ order.full_name }}', 'description': "The customer's full name."},
                {'name': '{{ order.email }}', 'description': "The customer's email address."},
                {'name': '{{ order.shipping_address }}', 'description': 'The shipping address for the order.'},
                {'name': '{{ order.total_paid }}', 'description': 'The total amount paid for the order.'},
                {'name': '{{ items }}', 'description': 'A list of items in the order. You can loop through this, e.g., {% for item in items %}.'},
                {'name': '{{ site_name }}', 'description': 'The name of the website.'},
            ]
        },
        # ... other event types can be added here in the future
    }

    @action(detail=True, methods=['get'], url_path='placeholders')
    def placeholders(self, request, pk=None):
        """
        Returns the available template placeholders for a specific email template.
        """
        template = self.get_object()
        event_name = template.event_name
        
        placeholder_data = self.PLACEHOLDER_DEFINITIONS.get(event_name, {
            'description': 'No placeholder information available for this event type.',
            'placeholders': []
        })
        
        return Response(placeholder_data) 