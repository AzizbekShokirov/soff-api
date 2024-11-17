from django.contrib.auth.models import update_last_login
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Favorite, User, UserOTP
from .serializers import (
    EmailVerificationSerializer,
    FavoriteSerializer,
    LoginSerializer,
    OTPValidationSerializer,
    PasswordChangeSerializer,
    PasswordResetConfirmSerializer,
    ProfileSerializer,
    RefreshTokenSerializer,
    RegisterSerializer,
)
from .utils import (
    send_confirmation_email,
    send_otp_email,
)


class RegisterView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=RegisterSerializer)
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user_otp = UserOTP.objects.filter(user=user).first()
            if user_otp and user_otp.is_max_attempts_reached():
                return Response(
                    {
                        "error": "You have reached the maximum number of OTP attempts. Please try again later."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
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
            user_otp = UserOTP.objects.get(
                user__email=user.email, otp=serializer.validated_data["otp"]
            )
            # If OTP is valid, reset attempts and unblock the user if necessary
            if user_otp.otp == serializer.validated_data["otp"]:
                user_otp.otp_attempts = 3
                user_otp.is_blocked = False
                user_otp.save()
                # Activate the user
                user.is_active = True
                user.save()

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
                    {"message": "Logout successful"},
                    status=status.HTTP_205_RESET_CONTENT,
                )
            except TokenError:
                return Response(
                    {"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=EmailVerificationSerializer)
    def post(self, request):
        serializer = EmailVerificationSerializer(data=request.data)
        if serializer.is_valid():
            user = User.objects.get(email=serializer.validated_data["email"])
            user_otp = UserOTP.objects.filter(user=user).first()

            if user_otp and user_otp.is_max_attempts_reached():
                return Response(
                    {
                        "error": "You have reached the maximum number of attempts. Please try again later."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
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
        serializer = PasswordResetConfirmSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            email = request.data.get("email")
            user = User.objects.get(email=email)

            # Optionally reset the user's OTP data (e.g., set attempts to 0, or delete expired OTPs)
            user_otp = UserOTP.objects.get(user=user)
            user_otp.otp_attempts = 3
            user_otp.is_blocked = False
            user_otp.save()

            # Save the new password
            user.set_password(serializer.validated_data["new_password"])
            user.save()

            # Send a confirmation email
            send_confirmation_email(request, user, purpose="password_reset")

            return Response(
                {"success": "Password has been reset successfully."},
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OTPResendView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(serializer_class=EmailVerificationSerializer)
    def post(self, request):
        serializer = EmailVerificationSerializer(data=request.data)
        if serializer.is_valid():
            user = User.objects.get(email=serializer.validated_data["email"])
            if user.otp and user.otp.is_max_attempts_reached():
                return Response(
                    {
                        "error": "You have reached the maximum number of attempts. Please try again later."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            send_otp_email(user)
            return Response(
                {"message": "OTP has been resent to your email."},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TokenRefreshView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=RefreshTokenSerializer)
    def post(self, request):
        serializer = RefreshTokenSerializer(data=request.data)
        if serializer.is_valid():
            try:
                refresh_token = serializer.validated_data["refresh"]
                # Decode the refresh token and generate a new access token
                token = RefreshToken(refresh_token)
                new_access_token = token.access_token
                return Response(
                    {
                        "access": str(new_access_token),
                        "refresh": str(token),
                    },
                    status=status.HTTP_200_OK,
                )
            except TokenError:
                return Response(
                    {"error": "Invalid refresh token"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordChangeView(APIView):
    @swagger_auto_schema(request_body=PasswordChangeSerializer)
    def post(self, request):
        serializer = PasswordChangeSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(APIView):
    def get(self, request):
        user = request.user
        serializer = ProfileSerializer(user, data=request.data)
        if serializer.is_valid():
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(request_body=ProfileSerializer)
    def put(self, request):
        user = request.user
        serializer = ProfileSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FavoriteView(APIView):
    def get(self, request):
        favorites = Favorite.objects.filter(
            user=request.user, liked=True
        ).select_related("product")
        serializer = FavoriteSerializer(favorites, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=FavoriteSerializer)
    def post(self, request, product_id):
        favorite, created = Favorite.objects.get_or_create(
            user=request.user, product_id=product_id
        )
        favorite.liked = not favorite.liked  # Toggle liked status
        favorite.save()
        return Response({"message": "Favorite toggled."}, status=status.HTTP_200_OK)

    @swagger_auto_schema(responses={200: "All favorites unliked."})
    def delete(self, request):
        favorites = Favorite.objects.filter(user=request.user, liked=True)
        favorites.update(liked=False)
        return Response(
            {"message": "All favorites unliked."}, status=status.HTTP_200_OK
        )
