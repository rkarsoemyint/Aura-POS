from django.contrib import admin
from .models import Category, Product
from .models import Order, OrderItem

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock', 'created_at')
    list_filter = ('category',) 
    search_fields = ('name',)  

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0 
    readonly_fields = ('product', 'quantity', 'price') 

class OrderAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'total_amount', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('transaction_id',)
    inlines = [OrderItemInline] 

admin.site.register(Category)
admin.site.register(Product, ProductAdmin)
admin.site.register(Order, OrderAdmin)