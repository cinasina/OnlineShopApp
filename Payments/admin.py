from django.contrib import admin
from .models import Order, OrderItem


class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_price', 'status',)
    list_filter = ('user', 'status',)
    list_editable = ('status',)

    actions = ['mark_as_processing', 'mark_as_shipped', 'mark_as_delivered', 'mark_as_canceled', 'delete_selected']

    def mark_as_processing(self, request, queryset):
        queryset.update(status='processing')

    def mark_as_shipped(self, request, queryset):
        queryset.update(status='shipped')

    def mark_as_delivered(self, request, queryset):
        queryset.update(status='delivered')

    def mark_as_canceled(self, request, queryset):
        queryset.update(status='canceled')


class OrderItemsAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price', 'subtotal',)
    list_filter = ('order', 'product',)


admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemsAdmin)
