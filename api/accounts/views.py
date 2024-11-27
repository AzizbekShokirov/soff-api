from django.contrib.auth.models import update_last_login
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from products.models import Product
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import Favorite, User
from accounts.serializers import (
    EmailValidationSerializer,
    FavoriteSerializer,
    FavoriteSlugSerializer,
    LoginSerializer,
    OTPValidationSerializer,
    PasswordChangeSerializer,
    PasswordResetConfirmSerializer,
    ProfileSerializer,
    RefreshTokenSerializer,
    RegisterSerializer,
)
from accounts.utils import reset_otp_data, send_confirmation_email, send_otp_email


class RegisterView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=RegisterSerializer)
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
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=OTPValidationSerializer)
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
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=LoginSerializer)
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            update_last_login(None, user)
            refresh_token = RefreshToken.for_user(user)
            tokens = {
                "refresh": str(refresh_token),
                "access": str(refresh_token.access_token),
            }
            return Response(
                {"user": {"email": user.email, "tokens": tokens}},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    @swagger_auto_schema(request_body=RefreshTokenSerializer)
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
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=EmailValidationSerializer)
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
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=PasswordResetConfirmSerializer)
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(
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
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=EmailValidationSerializer)
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


class PasswordChangeView(APIView):
    @swagger_auto_schema(request_body=PasswordChangeSerializer)
    def post(self, request):
        serializer = PasswordChangeSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            user = serializer.save()
            send_confirmation_email(request, user, purpose="password_change")
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(APIView):
    def get(self, request):
        user = request.user
        serializer = ProfileSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=ProfileSerializer)
    def put(self, request):
        user = request.user
        serializer = ProfileSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FavoriteView(APIView):
    def get(self, request):
        favorites = Favorite.objects.filter(user=request.user, liked=True).select_related("product")

        serializer = FavoriteSerializer(favorites, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=FavoriteSlugSerializer)
    def post(self, request):
        product = get_object_or_404(Product, slug=request.data["product_slug"])
        try:
            favorite = Favorite.objects.get_or_create(user=request.user, product=product)[0]
            if not favorite.liked:
                favorite.liked = True
                favorite.save()
                return Response({"message": "Favorite added."}, status=status.HTTP_200_OK)
            return Response(
                {"message": "Favorite already added."}, status=status.HTTP_200_OK
            )
        except Favorite.DoesNotExist:
            return Response(
                {"error": "Favorite does not exist."}, status=status.HTTP_404_NOT_FOUND
            )

    @swagger_auto_schema(responses={200: "All favorites deleted."})
    def delete(self, request):
        favorites = Favorite.objects.filter(user=request.user).select_related("product")
        for favorite in favorites:
            favorite.liked = False
            favorite.save()
        return Response(
            {"message": "All favorites deleted."}, status=status.HTTP_200_OK
        )


class FavoriteDetailView(APIView):
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

    @swagger_auto_schema(responses={200: "Favorite deleted."})
    def delete(self, request, product_slug):
        product = get_object_or_404(Product, slug=product_slug)
        try:
            favorite = Favorite.objects.get(user=request.user, product=product)
            if favorite.liked:
                favorite.liked = False
                favorite.save()
                return Response({"message": "Favorite deleted."}, status=status.HTTP_200_OK)
            return Response(
                {"message": "Favorite already deleted."}, status=status.HTTP_200_OK
            )
        except Favorite.DoesNotExist:
            return Response(
                {"error": "Favorite does not exist."}, status=status.HTTP_404_NOT_FOUND
            )
