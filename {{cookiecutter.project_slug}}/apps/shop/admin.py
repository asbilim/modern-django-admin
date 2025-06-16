from django.contrib import admin
from .models import ProductCategory, Product, Order, OrderItem

@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    class Meta:
        frontend_config = {
            'icon': 'folder',
            'category': 'Shop',
            'description': 'Manage product categories.',
            'include_in_dashboard': True,
        }

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'email',
                    'address', 'postal_code', 'city',
                    'status', 'created_at', 'updated_at']
    list_filter = ['status', 'created_at', 'updated_at']
    inlines = [OrderItemInline]
    class Meta:
        frontend_config = {
            'icon': 'shopping-cart',
            'category': 'Shop',
            'description': 'Manage customer orders.',
            'include_in_dashboard': True,
        }

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'price', 'stock', 'available', 'created_at', 'updated_at']
    list_filter = ['available', 'created_at', 'updated_at']
    list_editable = ['price', 'stock', 'available']
    prepopulated_fields = {'slug': ('name',)}
    class Meta:
        frontend_config = {
            'icon': 'package',
            'category': 'Shop',
            'description': 'Manage products.',
            'include_in_dashboard': True,
        }
