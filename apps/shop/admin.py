from django.contrib import admin
from modeltranslation.admin import TabbedTranslationAdmin
from .models import Product, Order, OrderItem, EmailTemplate

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']
    extra = 0

@admin.register(Product)
class ProductAdmin(TabbedTranslationAdmin):
    list_display = ['name', 'slug', 'price', 'stock', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at', 'updated_at']
    list_editable = ['price', 'stock', 'is_active']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'description']

    class Meta:
        frontend_config = {
            'icon': 'package',
            'category': 'Shop',
            'description': 'Manage products in your store.',
            'include_in_dashboard': True,
        }

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'full_name', 'email', 'status', 'created_at', 'total_paid']
    list_filter = ['status', 'created_at']
    search_fields = ['id', 'full_name', 'email']
    inlines = [OrderItemInline]
    readonly_fields = ['created_at', 'updated_at', 'total_paid']

    class Meta:
        frontend_config = {
            'icon': 'shopping-cart',
            'category': 'Shop',
            'description': 'View and manage customer orders.',
            'include_in_dashboard': True,
        }

@admin.register(EmailTemplate)
class EmailTemplateAdmin(TabbedTranslationAdmin):
    list_display = ('event_name', 'description', 'subject', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('event_name', 'subject', 'body')
    
    class Meta:
        frontend_config = {
            'icon': 'mail',
            'category': 'Shop',
            'description': 'Manage email templates for shop notifications.',
        } 