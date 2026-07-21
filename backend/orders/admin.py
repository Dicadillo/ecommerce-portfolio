from django.contrib import admin

from orders.models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    can_delete = False
    readonly_fields = (
        "product",
        "product_name",
        "unit_price",
        "quantity",
        "subtotal",
    )

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "total", "created_at")
    list_filter = ("status", "country", "created_at")
    search_fields = ("user__username", "recipient_name", "postal_code")
    readonly_fields = (
        "user",
        "status",
        "recipient_name",
        "address",
        "city",
        "postal_code",
        "country",
        "total",
        "created_at",
        "updated_at",
    )
    inlines = (OrderItemInline,)

    def has_add_permission(self, request):
        return False


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "product_name", "unit_price", "quantity")
    search_fields = ("product_name", "order__user__username")
    readonly_fields = (
        "order",
        "product",
        "product_name",
        "unit_price",
        "quantity",
        "subtotal",
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
