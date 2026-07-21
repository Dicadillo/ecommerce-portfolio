from django.urls import path

from users.views import LoginView, LogoutView, ProfileView, RefreshView, RegisterView

urlpatterns = [
    path("registro/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("refrescar/", RefreshView.as_view(), name="token-refresh"),
    path("perfil/", ProfileView.as_view(), name="profile"),
    path("logout/", LogoutView.as_view(), name="logout"),
]
