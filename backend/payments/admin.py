from django.contrib import admin

from payments.models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "order",
        "status",
        "amount",
        "reference",
        "provider",
        "created_at",
    )
    list_filter = ("status", "provider", "created_at")
    search_fields = ("reference", "order__user__username")
    readonly_fields = (
        "order",
        "status",
        "amount",
        "reference",
        "provider",
        "card_last_four",
        "created_at",
        "updated_at",
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
