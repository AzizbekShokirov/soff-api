from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import serializers

from accounts.models import Favorite, User
from accounts.utils import validate_otp, validate_password_data
from products.serializers import ProductSerializer


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
    image = serializers.ImageField(required=False)
    phone_number = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = [
            "email",
            "password",
            "password_confirm",
            "first_name",
            "last_name",
            "image",
            "phone_number",
        ]

    def validate(self, data):
        if User.objects.filter(email=data["email"]).exists():
            raise serializers.ValidationError("User with this email already exists.")

        validate_password(data["password"])
        return data

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            phone_number=validated_data.get("phone_number"),
            image=validated_data.get("image"),
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
        validate_password_data(
            user=self.context["request"].user,
            current_password=data["current_password"],
            new_password=data["new_password"],
            new_password_confirm=data["new_password_confirm"],
        )
        return data

    def save(self, **kwargs):
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save()
        return user


class PasswordResetConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.IntegerField()
    new_password = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"}
    )
    new_password_confirm = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"}
    )

    def validate(self, data):
        email = data.get("email")
        if not email:
            raise serializers.ValidationError("Email is required.")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")

        validate_password_data(
            user=user,
            current_password=None,  # No current password needed for reset
            new_password=data["new_password"],
            new_password_confirm=data["new_password_confirm"],
        )
        validate_otp(user, data["otp"])

        data["user"] = user
        return data

    def save(self, **kwargs):
        user = self.validated_data["user"]
        user.set_password(self.validated_data["new_password"])
        user.save()
        return user


class EmailValidationSerializer(serializers.Serializer):
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

        if not email:
            raise serializers.ValidationError("Email is required.")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")

        validate_otp(user, otp)
        return data


class RefreshTokenSerializer(serializers.Serializer):
    refresh = serializers.CharField(required=True, write_only=True)


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "first_name", "last_name", "image", "phone_number"]
        read_only_fields = ["email"]

    def validate(self, data):
        if "image" in data:
            if data["image"].size > 2 * 1024 * 1024:
                raise serializers.ValidationError(
                    "The image size should not exceed 2MB."
                )
        return data

    def update(self, instance, validated_data):
        if "image" in validated_data and instance.image:
            instance.image.delete()
        return super().update(instance, validated_data)


class FavoriteSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = Favorite
        fields = ["product"]
