from django.contrib.auth.models import update_last_login
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiExample
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

from apps.products.models import Product
from .models import Favorite, User
from .serializers import (
    EmailValidationSerializer,
    FavoriteSerializer,
    FavoriteSlugSerializer,
    LoginSerializer,
    OTPValidationSerializer,
    PasswordChangeSerializer,
    PasswordResetSerializer,
    ProfileSerializer,
    RefreshTokenResponseSerializer,
    RefreshTokenSerializer,
    RegisterSerializer,
    ErrorResponseSerializer,
    SuccessResponseSerializer
)
from .utils import reset_otp_data, send_confirmation_email, send_otp_email


class CustomTokenRefreshView(TokenRefreshView):
    @extend_schema(
        request=RefreshTokenSerializer,
        responses={200: RefreshTokenResponseSerializer, 400: ErrorResponseSerializer},
        tags=["Users"],
    )
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            response.data["access"] = str(response.data["access"])
            response.data["refresh"] = str(response.data["refresh"])
        return response


class RegisterView(APIView):
    @extend_schema(
        tags=["Users"],
        description="Register a new user account. An OTP will be sent to the user's email for verification.",
        request=RegisterSerializer,
        responses={
            201: SuccessResponseSerializer,
            400: ErrorResponseSerializer
        },
        examples=[
            OpenApiExample(
                "Register Request",
                value={
                    "email": "user@example.com",
                    "password": "SecurePassword123",
                    "password_confirm": "SecurePassword123",
                    "first_name": "John",
                    "last_name": "Doe",
                    "phone_number": "+1234567890"
                }
            )
        ]
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            send_otp_email(user)
            return Response(
                {
                    "message": "You have registered successfully. We have sent you an OTP to verify your email. Please check your email.",
                    "user": {
                        "email": user.email,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                    },
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ConfirmEmailView(APIView):
    @extend_schema(
        tags=["Users"],
        description="Confirm a user's email address using the OTP that was sent after registration",
        request=OTPValidationSerializer,
        responses={
            200: SuccessResponseSerializer,
            400: ErrorResponseSerializer
        },
        examples=[
            OpenApiExample(
                "Confirm Email Request",
                value={
                    "email": "user@example.com",
                    "otp": 123456
                }
            )
        ]
    )
    def post(self, request):
        serializer = OTPValidationSerializer(data=request.data)
        if serializer.is_valid():
            user = User.objects.get(email=serializer.validated_data["email"])
            user.is_active = True
            user.save()
            reset_otp_data(user)
            send_confirmation_email(request, user, purpose="account_confirmation")
            return Response(
                {"message": "Email confirmed successfully. You can now log in."},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    @extend_schema(
        tags=["Users"],
        description="Authenticate a user and return JWT tokens",
        request=LoginSerializer,
        responses={
            200: {"type": "object", "properties": {
                "user": {"type": "object", "properties": {
                    "email": {"type": "string"},
                    "tokens": {"type": "object", "properties": {
                        "access": {"type": "string"},
                        "refresh": {"type": "string"}
                    }}
                }}
            }},
            400: ErrorResponseSerializer
        },
        examples=[
            OpenApiExample(
                "Login Request",
                value={
                    "email": "user@example.com",
                    "password": "SecurePassword123"
                }
            )
        ]
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            update_last_login(None, user)
            refresh_token = RefreshToken.for_user(user)
            tokens = {
                "access": str(refresh_token.access_token),
                "refresh": str(refresh_token),
            }
            return Response(
                {"user": {"email": user.email, "tokens": tokens}},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Users"],
        description="Logout a user by blacklisting their refresh token",
        request=RefreshTokenSerializer,
        responses={
            205: SuccessResponseSerializer,
            400: ErrorResponseSerializer
        },
        examples=[
            OpenApiExample(
                "Logout Request",
                value={
                    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
                }
            )
        ]
    )
    def post(self, request):
        serializer = RefreshTokenSerializer(data=request.data)
        if serializer.is_valid():
            refresh_token = serializer.validated_data["refresh"]
            try:
                # Decode the refresh token and blacklist it
                token = RefreshToken(refresh_token)
                token.blacklist()

                return Response(
                    {"message": "Logout successful."},
                    status=status.HTTP_205_RESET_CONTENT,
                )
            except TokenError:
                return Response(
                    {"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetView(APIView):
    @extend_schema(
        tags=["Users"],
        description="Request a password reset. An OTP will be sent to the user's email.",
        request=EmailValidationSerializer,
        responses={
            200: SuccessResponseSerializer,
            400: ErrorResponseSerializer
        },
        examples=[
            OpenApiExample(
                "Password Reset Request",
                value={
                    "email": "user@example.com"
                }
            )
        ]
    )
    def post(self, request):
        serializer = EmailValidationSerializer(data=request.data)
        if serializer.is_valid():
            user = User.objects.get(email=serializer.validated_data["email"])
            send_otp_email(user)
            return Response(
                {"message": "Password reset OTP has been sent to your email."},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(APIView):
    @extend_schema(
        tags=["Users"],
        description="Confirm password reset using OTP and set a new password",
        request=PasswordResetSerializer,
        responses={
            200: SuccessResponseSerializer,
            400: ErrorResponseSerializer
        },
        examples=[
            OpenApiExample(
                "Password Reset Confirm Request",
                value={
                    "email": "user@example.com",
                    "new_password": "NewSecurePassword123",
                    "new_password_confirm": "NewSecurePassword123"
                }
            )
        ]
    )
    def post(self, request):
        serializer = PasswordResetSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            user = serializer.save()
            reset_otp_data(user)
            send_confirmation_email(request, user, purpose="password_reset")
            return Response(
                {
                    "success": "Password has been reset successfully. Please log in with your new password."
                },
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OTPResendView(APIView):
    @extend_schema(
        tags=["Users"],
        description="Resend OTP to the user's email",
        request=EmailValidationSerializer,
        responses={
            200: SuccessResponseSerializer,
            400: ErrorResponseSerializer
        },
        examples=[
            OpenApiExample(
                "OTP Resend Request",
                value={
                    "email": "user@example.com"
                }
            )
        ]
    )
    def post(self, request):
        serializer = EmailValidationSerializer(data=request.data)
        if serializer.is_valid():
            user = User.objects.get(email=serializer.validated_data["email"])
            send_otp_email(user)
            return Response(
                {"message": "OTP has been resent to your email."},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OTPValidateView(APIView):
    @extend_schema(
        tags=["Users"],
        description="Validate an OTP",
        request=OTPValidationSerializer,
        responses={
            200: SuccessResponseSerializer,
            400: ErrorResponseSerializer
        },
        examples=[
            OpenApiExample(
                "OTP Validate Request",
                value={
                    "email": "user@example.com",
                    "otp": 123456
                }
            )
        ]
    )
    def post(self, request):
        serializer = OTPValidationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"success": "OTP validated successfully."}, status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordChangeView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Users"],
        description="Change the authenticated user's password",
        request=PasswordChangeSerializer,
        responses={
            204: SuccessResponseSerializer,
            400: ErrorResponseSerializer
        },
        examples=[
            OpenApiExample(
                "Password Change Request",
                value={
                    "current_password": "CurrentPassword123",
                    "new_password": "NewPassword123",
                    "new_password_confirm": "NewPassword123"
                }
            )
        ]
    )
    def post(self, request):
        serializer = PasswordChangeSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            user = serializer.save()
            update_session_auth_hash(
                request, request.user
            )  # Keep user logged in after password change
            send_confirmation_email(request, user, purpose="password_change")
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Users"],
        description="Get the authenticated user's profile information",
        responses={200: ProfileSerializer, 404: ErrorResponseSerializer},
        examples=[
            OpenApiExample(
                "Profile Response",
                value={
                    "email": "user@example.com",
                    "first_name": "John",
                    "last_name": "Doe",
                    "image": "http://example.com/profile.jpg",
                    "phone_number": "+1234567890"
                }
            )
        ]
    )
    def get(self, request):
        user = request.user
        serializer = ProfileSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        tags=["Users"],
        description="Update the authenticated user's profile information",
        request=ProfileSerializer,
        responses={
            200: ProfileSerializer,
            400: ErrorResponseSerializer
        },
        examples=[
            OpenApiExample(
                "Profile Update Request",
                value={
                    "first_name": "Updated First Name",
                    "last_name": "Updated Last Name",
                    "phone_number": "+1234567890",
                    "image": "http://example.com/new-avatar.jpg"
                }
            )
        ]
    )
    def put(self, request):
        user = request.user
        serializer = ProfileSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FavoriteView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Favorites"],
        description="Get list of user's favorite products with pagination",
        responses={200: FavoriteSerializer(many=True), 404: ErrorResponseSerializer},
        examples=[
            OpenApiExample(
                "Favorites Paginated Response",
                value={
                    "count": 2,
                    "next": None,
                    "previous": None,
                    "results": [
                        {
                            "title": "Modern Sofa",
                            "description": "A comfortable modern sofa",
                            "color": "Grey",
                            "material": "Fabric",
                            "price": 599.99,
                            "maximum_load": 500.00,
                            "length": 200.00,
                            "width": 90.00,
                            "height": 85.00,
                            "rating": 4.5,
                            "room_category": "living-room",
                            "product_category": "sofa",
                            "manufacturer": "ikea",
                            "images": [{"image": "http://example.com/sofa-1.jpg"}],
                            "is_ar": True,
                            "ar_model": "http://example.com/ar-model",
                            "ar_url": "http://example.com/ar-url",
                            "is_favorite": True,
                            "slug": "modern-sofa"
                        }
                    ]
                }
            )
        ]
    )
    def get(self, request):
        favorites = (
            Favorite.objects.filter(user=request.user, is_liked=True)
            .select_related("product")
            .order_by("product")
        )

        paginator = PageNumberPagination()
        paginated_products = paginator.paginate_queryset(favorites, request)

        serializer = FavoriteSerializer(
            paginated_products, many=True, context={"request": request}
        )
        return paginator.get_paginated_response(serializer.data)

    @extend_schema(
        tags=["Favorites"],
        description="Add a product to user's favorites",
        request=FavoriteSlugSerializer,
        responses={
            200: SuccessResponseSerializer,
            404: ErrorResponseSerializer
        },
        examples=[
            OpenApiExample(
                "Add Favorite Request",
                value={
                    "product_slug": "modern-sofa"
                }
            )
        ]
    )
    def post(self, request):
        product = get_object_or_404(Product, slug=request.data["product_slug"])
        try:
            favorite = Favorite.objects.get_or_create(
                user=request.user, product=product
            )[0]

            if not favorite.is_liked:
                favorite.is_liked = True
                favorite.save()
                return Response(
                    {"message": "Favorite added."}, status=status.HTTP_200_OK
                )
            return Response(
                {"message": "Favorite already added."}, status=status.HTTP_200_OK
            )
        except Favorite.DoesNotExist:
            return Response(
                {"error": "Favorite does not exist."}, status=status.HTTP_404_NOT_FOUND
            )

    @extend_schema(
        tags=["Favorites"],
        description="Clear all favorites",
        responses={200: SuccessResponseSerializer}
    )
    def delete(self, request):
        favorites = Favorite.objects.filter(user=request.user).select_related("product")
        for favorite in favorites:
            favorite.is_liked = False
            favorite.save()
        return Response(
            {"message": "All favorites deleted."}, status=status.HTTP_200_OK
        )


class FavoriteDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Favorites"],
        description="Get details of a favorite product",
        responses={
            200: FavoriteSerializer,
            404: ErrorResponseSerializer
        },
        examples=[
            OpenApiExample(
                "Favorite Detail Response",
                value={
                    "title": "Modern Sofa",
                    "description": "A comfortable modern sofa",
                    "color": "Grey",
                    "material": "Fabric",
                    "price": 599.99,
                    "maximum_load": 500.00,
                    "length": 200.00,
                    "width": 90.00,
                    "height": 85.00,
                    "rating": 4.5,
                    "room_category": "living-room",
                    "product_category": "sofa",
                    "manufacturer": "ikea",
                    "images": [{"image": "http://example.com/sofa-1.jpg"}],
                    "is_ar": True,
                    "ar_model": "http://example.com/ar-model",
                    "ar_url": "http://example.com/ar-url",
                    "is_favorite": True,
                    "slug": "modern-sofa"
                }
            )
        ]
    )
    def get(self, request, product_slug):
        product = get_object_or_404(Product, slug=product_slug)
        try:
            favorite = Favorite.objects.get(user=request.user, product=product)
            serializer = FavoriteSerializer(favorite)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Favorite.DoesNotExist:
            return Response(
                {"error": "Favorite does not exist."}, status=status.HTTP_404_NOT_FOUND
            )

    @extend_schema(
        tags=["Favorites"],
        description="Remove a product from favorites",
        responses={
            200: SuccessResponseSerializer,
            404: ErrorResponseSerializer
        }
    )
    def delete(self, request, product_slug):
        product = get_object_or_404(Product, slug=product_slug)
        try:
            favorite = Favorite.objects.get(user=request.user, product=product)
            if favorite.is_liked:
                favorite.is_liked = False
                favorite.save()
                return Response(
                    {"message": "Favorite deleted."}, status=status.HTTP_200_OK
                )
            return Response(
                {"message": "Favorite already deleted."}, status=status.HTTP_200_OK
            )
        except Favorite.DoesNotExist:
            return Response(
                {"error": "Favorite does not exist."}, status=status.HTTP_404_NOT_FOUND
            )
