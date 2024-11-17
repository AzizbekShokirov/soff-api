from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from products.serializers import ProductSerializer
from rest_framework import serializers

from accounts.models import Favorite, User, UserOTP


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"}
    )
    password_confirm = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"}
    )
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    profile_picture = serializers.ImageField(required=False)
    phone_number = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = [
            "email",
            "password",
            "password_confirm",
            "first_name",
            "last_name",
            "profile_picture",
            "phone_number",
        ]

    def validate(self, data):
        if User.objects.filter(email=data["email"]).exists():
            raise serializers.ValidationError("User with this email already exists.")
        if data["password"] != data["password_confirm"]:
            raise serializers.ValidationError("Passwords do not match.")
        if data["password"] == data["email"]:
            raise serializers.ValidationError(
                "Password should not be the same as email."
            )
        if len(data["password"]) < 8:
            raise serializers.ValidationError(
                "Password should be at least 8 characters."
            )
        if not any(char.isdigit() for char in data["password"]):
            raise serializers.ValidationError(
                "Password should contain at least 1 digit."
            )
        if not any(char.isalpha() for char in data["password"]):
            raise serializers.ValidationError(
                "Password should contain at least 1 letter."
            )
        return data

    def create(self, validated_data):
        validate_password(validated_data["password"])

        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            phone_number=validated_data.get("phone_number"),
            profile_picture=validated_data.get("profile_picture"),
            is_active=False,
        )
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(style={"input_type": "password"}, write_only=True)

    def validate(self, data):
        user = authenticate(username=data["email"], password=data["password"])
        if not user:
            raise ValidationError("Invalid email or password.")
        if not user.is_active:
            raise serializers.ValidationError("Account is not verified.")
        data["user"] = user
        return data


class RefreshTokenSerializer(serializers.Serializer):
    refresh = serializers.CharField(required=True, write_only=True)


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "first_name", "last_name", "profile_picture", "phone_number"]
        read_only_fields = ["email", "is_staff"]


class FavoriteSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = Favorite
        fields = ["id", "product", "liked"]


class PasswordChangeSerializer(serializers.Serializer):
    current_password = serializers.CharField(
        write_only=True, style={"input_type": "password"}
    )
    new_password = serializers.CharField(
        write_only=True, style={"input_type": "password"}
    )
    new_password_confirm = serializers.CharField(
        write_only=True, style={"input_type": "password"}
    )

    def validate(self, data):
        user = self.context["request"].user
        
        if not user.check_password(data["current_password"]):
            raise ValidationError(
                {"current_password": "Current password is not correct."}
            )
        
        if data["new_password"] == data["current_password"]:
            raise ValidationError(
                {"new_password": "New password cannot be the same as the current password."}
            )
        
        if data["new_password"] != data["new_password_confirm"]:
            raise ValidationError({"new_password_confirm": "Passwords do not match."})
        
        validate_password(data["new_password"])
        return data

    def save(self, **kwargs):
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save()
        return user


class PasswordResetConfirmSerializer(serializers.Serializer):
    otp = serializers.IntegerField()
    new_password = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"}
    )
    new_password_confirm = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"}
    )

    def validate(self, data):
        # Ensure 'email' is passed correctly in the request body
        email = self.context["request"].data.get("email")

        if not email:
            raise serializers.ValidationError("Email is required.")
        if data["new_password"] != data["new_password_confirm"]:
            raise serializers.ValidationError("Passwords do not match.")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")

        if user.check_password(data["new_password"]):
            raise serializers.ValidationError(
                "New password cannot be the same as the current password."
            )
        validate_password(data["new_password"])
        # Validate OTP
        otp = data.get("otp")
        try:
            user_otp = UserOTP.objects.get(user__email=email, otp=otp)

            if user_otp.is_expired():
                raise serializers.ValidationError("OTP has expired. Please request a new one.")
            if user_otp.is_blocked:
                raise serializers.ValidationError("Your account is blocked due to too many failed OTP attempts.")
        except UserOTP.DoesNotExist:
            raise serializers.ValidationError("Invalid OTP.")

        return data


class EmailVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, data):
        if not data["email"]:
            raise serializers.ValidationError("Email is required.")
        
        if not User.objects.filter(email=data["email"]).exists():
            raise serializers.ValidationError("User with this email does not exist.")
        return data


class OTPValidationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.IntegerField()

    def validate(self, data):
        email = data.get("email")
        otp = data.get("otp")

        try:
            user = User.objects.get(email=email)
            user_otp = UserOTP.objects.get(user=user)
            if not user_otp:
                raise serializers.ValidationError("OTP for this user does not exist.")
            if user_otp.is_max_attempts_reached():
                user_otp.is_blocked = True
                raise serializers.ValidationError(
                    "Maximum OTP attempts reached. Please try again later."
                )
            if user_otp.is_blocked:
                raise serializers.ValidationError(
                    "Your account is blocked due to too many failed OTP attempts. Please try again later."
                )
            if user_otp.is_expired():
                user_otp.otp_attempts -= 1
                raise serializers.ValidationError(
                    "The OTP has expired. Please request a new one."
                )
            if user_otp.otp != otp:
                user_otp.otp_attempts -= 1
                user_otp.save()
                raise serializers.ValidationError("Invalid OTP.")

        except User.DoesNotExist:
            raise serializers.ValidationError("User does not exist.")
        except UserOTP.DoesNotExist:
            raise serializers.ValidationError("OTP for this user does not exist.")

        return data
