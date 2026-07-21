from django.urls import path

from cart.views import (
    CartClearView,
    CartDetailView,
    CartItemDetailView,
    CartItemListView,
)

urlpatterns = [
    path("", CartDetailView.as_view(), name="cart-detail"),
    path("articulos/", CartItemListView.as_view(), name="cart-item-list"),
    path(
        "articulos/<int:item_id>/",
        CartItemDetailView.as_view(),
        name="cart-item-detail",
    ),
    path("vaciar/", CartClearView.as_view(), name="cart-clear"),
]
