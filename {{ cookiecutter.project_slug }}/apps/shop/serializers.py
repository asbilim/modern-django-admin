from rest_framework import serializers
from .models import Product, Order, OrderItem, EmailTemplate

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = OrderItem
        fields = ('id', 'product', 'product_id', 'price', 'quantity')
        read_only_fields = ('price',)

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    user = serializers.StringRelatedField()

    class Meta:
        model = Order
        fields = (
            'id', 'user', 'full_name', 'email', 'phone', 'shipping_address',
            'billing_address', 'status', 'total_paid', 'notes', 'items', 'created_at'
        )
        read_only_fields = ('user', 'status', 'total_paid', 'created_at')

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        
        # Calculate total
        total_paid = 0
        for item_data in items_data:
            product = Product.objects.get(id=item_data['product_id'])
            total_paid += product.price * item_data['quantity']
        
        validated_data['total_paid'] = total_paid
        
        # Assign user if authenticated
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            validated_data['user'] = request.user
            
        order = Order.objects.create(**validated_data)

        for item_data in items_data:
            product = Product.objects.get(id=item_data['product_id'])
            OrderItem.objects.create(
                order=order,
                product=product,
                price=product.price, # Set price from product at time of order
                quantity=item_data['quantity']
            )
            # You might want to decrease product stock here as well
            # product.stock -= item_data['quantity']
            # product.save()

        return order

class EmailTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailTemplate
        fields = '__all__' 