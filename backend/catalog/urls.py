from rest_framework.routers import SimpleRouter

from catalog.views import CategoryViewSet, ProductViewSet

router = SimpleRouter()
router.register("categorias", CategoryViewSet, basename="category")
router.register("productos", ProductViewSet, basename="product")

urlpatterns = router.urls
