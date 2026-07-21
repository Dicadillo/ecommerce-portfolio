from drf_spectacular.utils import OpenApiExample, extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from config.openapi import BAD_REQUEST_RESPONSE, UNAUTHORIZED_RESPONSE
from users.serializers import (
    LoginSerializer,
    LogoutSerializer,
    ProfileSerializer,
    RefreshSerializer,
    RegisterSerializer,
)

login_response_serializer = inline_serializer(
    name="RespuestaLogin",
    fields={
        "acceso": serializers.CharField(help_text="Token JWT de acceso."),
        "refresco": serializers.CharField(help_text="Token JWT de refresco."),
    },
)
refresh_response_serializer = inline_serializer(
    name="RespuestaRefresco",
    fields={"acceso": serializers.CharField(help_text="Nuevo token JWT de acceso.")},
)


class RegisterView(APIView):
    authentication_classes = ()
    permission_classes = (AllowAny,)

    @extend_schema(
        tags=["Autenticación"],
        summary="Registrar un usuario",
        description="Crea un usuario tras validar sus datos y su contraseña.",
        request=RegisterSerializer,
        responses={201: ProfileSerializer, 400: BAD_REQUEST_RESPONSE},
        auth=[],
        examples=[
            OpenApiExample(
                "Solicitud de registro",
                value={
                    "usuario": "santi",
                    "correo": "santi@example.com",
                    "contrasena": "ClaveSegura!2026",
                    "confirmacion_contrasena": "ClaveSegura!2026",
                },
                request_only=True,
            ),
            OpenApiExample(
                "Usuario registrado",
                value={
                    "id": 1,
                    "usuario": "santi",
                    "correo": "santi@example.com",
                },
                response_only=True,
                status_codes=["201"],
            ),
        ],
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(ProfileSerializer(user).data, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    authentication_classes = ()
    permission_classes = (AllowAny,)

    @extend_schema(
        tags=["Autenticación"],
        summary="Iniciar sesión",
        description="Valida las credenciales y devuelve tokens JWT.",
        request=LoginSerializer,
        responses={
            200: login_response_serializer,
            400: BAD_REQUEST_RESPONSE,
            401: UNAUTHORIZED_RESPONSE,
        },
        auth=[],
        examples=[
            OpenApiExample(
                "Credenciales",
                value={"usuario": "santi", "contrasena": "ClaveSegura!2026"},
                request_only=True,
            ),
            OpenApiExample(
                "Tokens JWT",
                value={"acceso": "eyJ...acceso", "refresco": "eyJ...refresco"},
                response_only=True,
                status_codes=["200"],
            ),
        ],
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        return Response(
            {
                "acceso": serializer.validated_data["access"],
                "refresco": serializer.validated_data["refresh"],
            }
        )


class RefreshView(APIView):
    authentication_classes = ()
    permission_classes = (AllowAny,)

    @extend_schema(
        tags=["Autenticación"],
        summary="Refrescar el token de acceso",
        description="Emite un token de acceso nuevo a partir de un token de refresco.",
        request=RefreshSerializer,
        responses={200: refresh_response_serializer, 400: BAD_REQUEST_RESPONSE},
        auth=[],
        examples=[
            OpenApiExample(
                "Token de refresco",
                value={"refresco": "eyJ...refresco"},
                request_only=True,
            ),
            OpenApiExample(
                "Nuevo token",
                value={"acceso": "eyJ...acceso"},
                response_only=True,
                status_codes=["200"],
            ),
        ],
    )
    def post(self, request):
        serializer = RefreshSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({"acceso": serializer.validated_data["access"]})


class ProfileView(APIView):
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        tags=["Autenticación"],
        summary="Consultar el perfil",
        description="Requiere un token JWT Bearer y devuelve el usuario autenticado.",
        responses={200: ProfileSerializer, 401: UNAUTHORIZED_RESPONSE},
        examples=[
            OpenApiExample(
                "Perfil",
                value={
                    "id": 1,
                    "usuario": "santi",
                    "correo": "santi@example.com",
                },
                response_only=True,
            )
        ],
    )
    def get(self, request):
        return Response(ProfileSerializer(request.user).data)


class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        tags=["Autenticación"],
        summary="Cerrar sesión",
        description=(
            "Requiere un token JWT Bearer e invalida el token de refresco indicado."
        ),
        request=LogoutSerializer,
        responses={
            204: None,
            400: BAD_REQUEST_RESPONSE,
            401: UNAUTHORIZED_RESPONSE,
        },
        examples=[
            OpenApiExample(
                "Token que se invalidará",
                value={"refresco": "eyJ...refresco"},
                request_only=True,
            )
        ],
    )
    def post(self, request):
        serializer = LogoutSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
