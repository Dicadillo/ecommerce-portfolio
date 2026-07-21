from django.contrib import admin

from cart.models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ("subtotal", "created_at", "updated_at")


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "active", "total_items", "total", "updated_at")
    list_filter = ("active",)
    search_fields = ("user__username", "user__email")
    readonly_fields = ("created_at", "updated_at", "total_items", "total")
    inlines = (CartItemInline,)


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("id", "cart", "product", "quantity", "subtotal", "updated_at")
    search_fields = ("product__name", "cart__user__username")
    list_select_related = ("cart", "product")
    readonly_fields = ("created_at", "updated_at", "subtotal")
