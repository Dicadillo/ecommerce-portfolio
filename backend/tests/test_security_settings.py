from django.conf import settings
from rest_framework.permissions import IsAuthenticated
from rest_framework.settings import api_settings


def test_api_is_private_by_default():
    assert api_settings.DEFAULT_PERMISSION_CLASSES == [IsAuthenticated]


def test_base_cookie_and_browser_security_settings_are_hardened():
    assert settings.SESSION_COOKIE_HTTPONLY is True
    assert settings.SESSION_COOKIE_SAMESITE == "Lax"
    assert settings.CSRF_COOKIE_SAMESITE == "Lax"
    assert settings.SECURE_CONTENT_TYPE_NOSNIFF is True
    assert settings.SECURE_REFERRER_POLICY == "same-origin"
    assert settings.X_FRAME_OPTIONS == "DENY"


def test_cors_uses_an_explicit_allowlist_and_correct_middleware_order():
    assert settings.CORS_ALLOWED_ORIGINS == [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]
    assert getattr(settings, "CORS_ALLOW_ALL_ORIGINS", False) is False
    assert "corsheaders" in settings.INSTALLED_APPS
    assert settings.MIDDLEWARE.index(
        "corsheaders.middleware.CorsMiddleware"
    ) < settings.MIDDLEWARE.index("django.middleware.common.CommonMiddleware")
