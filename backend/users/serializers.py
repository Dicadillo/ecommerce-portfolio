from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from users.exceptions import InvalidCredentials

User = get_user_model()


class ProfileSerializer(serializers.ModelSerializer):
    usuario = serializers.CharField(source="username", read_only=True)
    correo = serializers.EmailField(source="email", read_only=True)

    class Meta:
        model = User
        fields = ("id", "usuario", "correo")
        read_only_fields = fields


class RegisterSerializer(serializers.Serializer):
    usuario = serializers.CharField(
        source="username",
        max_length=150,
        error_messages={"blank": "Este campo no puede estar vacío."},
    )
    correo = serializers.EmailField(
        source="email",
        error_messages={"invalid": "Introduce un correo electrónico válido."},
    )
    contrasena = serializers.CharField(
        source="password",
        write_only=True,
        trim_whitespace=False,
    )
    confirmacion_contrasena = serializers.CharField(
        source="password_confirmation",
        write_only=True,
        trim_whitespace=False,
    )

    def validate(self, attributes):
        username = attributes["username"]
        email = attributes["email"]
        password = attributes["password"]
        password_confirmation = attributes["password_confirmation"]

        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError(
                {"usuario": "Este nombre de usuario ya existe."}
            )

        if password != password_confirmation:
            raise serializers.ValidationError(
                {"confirmacion_contrasena": "Las contraseñas no coinciden."}
            )

        user = User(username=username, email=email)
        try:
            validate_password(password, user=user)
        except DjangoValidationError as error:
            raise serializers.ValidationError(
                {"contrasena": list(error.messages)}
            ) from error

        return attributes

    def create(self, validated_data):
        validated_data.pop("password_confirmation")
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    usuario = serializers.CharField(source="username")
    contrasena = serializers.CharField(
        source="password",
        write_only=True,
        trim_whitespace=False,
    )

    def validate(self, attributes):
        user = authenticate(
            request=self.context.get("request"),
            username=attributes["username"],
            password=attributes["password"],
        )
        if user is None:
            raise InvalidCredentials()

        refresh = RefreshToken.for_user(user)
        return {
            "user": user,
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }


class RefreshSerializer(serializers.Serializer):
    refresco = serializers.CharField(source="refresh", write_only=True)

    def validate(self, attributes):
        try:
            refresh = RefreshToken(attributes["refresh"])
        except TokenError as error:
            raise serializers.ValidationError(
                {"refresco": "El token de refresco no es válido."}
            ) from error

        return {"access": str(refresh.access_token)}


class LogoutSerializer(serializers.Serializer):
    refresco = serializers.CharField(source="refresh", write_only=True)

    def validate(self, attributes):
        try:
            token = RefreshToken(attributes["refresh"])
        except TokenError as error:
            raise serializers.ValidationError(
                {"refresco": "El token de refresco no es válido."}
            ) from error

        request = self.context["request"]
        if str(token["user_id"]) != str(request.user.pk):
            raise serializers.ValidationError(
                {"refresco": "El token no pertenece al usuario autenticado."}
            )

        attributes["token"] = token
        return attributes

    def create(self, validated_data):
        token = validated_data["token"]
        token.blacklist()
        return token
