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
