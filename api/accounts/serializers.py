from decimal import Decimal

from categories.models import ProductCategory, RoomCategory
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from manufacturers.models import Manufacturer
from products.models import Product
from products.serializers import ProductImageSerializer
from rest_framework import serializers

from accounts.models import Favorite, User, UserOTP
from accounts.utils import validate_otp, validate_password_data


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


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()
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

        # Check if OTP is validated before allowing password reset
        try:
            user_otp = UserOTP.objects.get(user=user)
            if not user_otp.is_validated:
                raise serializers.ValidationError(
                    "OTP has not been validated. Please validate it first."
                )
        except UserOTP.DoesNotExist:
            raise serializers.ValidationError("No OTP record found for this user.")

        # Validate new password with the provided data
        try:
            validate_password_data(
                user=user,
                current_password=None,  # No current password needed for reset
                new_password=data["new_password"],
                new_password_confirm=data["new_password_confirm"],
            )
        except ValidationError as e:
            raise serializers.ValidationError(str(e))

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
        data["user"] = user
        return data

    def save(self, **kwargs):
        user = self.validated_data["user"]
        user_otp = UserOTP.objects.get(user=user)
        user_otp.is_validated = True
        user_otp.save()
        return user


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


class FavoriteSlugSerializer(serializers.ModelSerializer):
    product_slug = serializers.SlugRelatedField(
        slug_field="slug", queryset=Product.objects.all()
    )

    class Meta:
        model = Favorite
        fields = ["product_slug"]


class FavoriteSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source="product.title", max_length=255)
    description = serializers.CharField(source="product.description", max_length=1000)
    color = serializers.CharField(source="product.color", max_length=255)
    material = serializers.CharField(source="product.material", max_length=255)
    price = serializers.DecimalField(
        source="product.price",
        max_digits=10,
        decimal_places=2,
        validators=[
            MaxValueValidator(Decimal("99999999.99")),
            MinValueValidator(Decimal("0.00")),
        ],
    )
    maximum_load = serializers.DecimalField(
        source="product.maximum_load",
        max_digits=10,
        decimal_places=2,
        validators=[
            MaxValueValidator(Decimal("99999999.99")),
            MinValueValidator(Decimal("0.00")),
        ],
    )
    length = serializers.DecimalField(
        source="product.length",
        max_digits=10,
        decimal_places=2,
        validators=[
            MaxValueValidator(Decimal("99999999.99")),
            MinValueValidator(Decimal("0.00")),
        ],
    )
    width = serializers.DecimalField(
        source="product.width",
        max_digits=10,
        decimal_places=2,
        validators=[
            MaxValueValidator(Decimal("99999999.99")),
            MinValueValidator(Decimal("0.00")),
        ],
    )
    height = serializers.DecimalField(
        source="product.height",
        max_digits=10,
        decimal_places=2,
        validators=[
            MaxValueValidator(Decimal("99999999.99")),
            MinValueValidator(Decimal("0.00")),
        ],
    )
    rating = serializers.DecimalField(
        source="product.rating",
        max_digits=3,
        decimal_places=1,
        required=False,
        validators=[
            MaxValueValidator(Decimal("5.0")),
            MinValueValidator(Decimal("0.0")),
        ],
    )
    room_category = serializers.SlugRelatedField(
        source="product.room_category",
        slug_field="slug",
        queryset=RoomCategory.objects.all(),
    )
    product_category = serializers.SlugRelatedField(
        source="product.product_category",
        slug_field="slug",
        queryset=ProductCategory.objects.all(),
    )
    manufacturer = serializers.SlugRelatedField(
        source="product.manufacturer",
        slug_field="slug",
        queryset=Manufacturer.objects.all(),
    )
    images = ProductImageSerializer(source="product.images", many=True)
    is_ar = serializers.BooleanField(source="product.is_ar")
    ar_model = serializers.URLField(source="product.ar_model")
    ar_url = serializers.URLField(source="product.ar_url")
    is_favorite = serializers.SerializerMethodField()
    slug = serializers.SlugField(source="product.slug")

    class Meta:
        model = Favorite
        fields = [
            "title",
            "description",
            "color",
            "material",
            "price",
            "maximum_load",
            "length",
            "width",
            "height",
            "rating",
            "room_category",
            "product_category",
            "manufacturer",
            "images",
            "is_ar",
            "ar_model",
            "ar_url",
            "is_favorite",
            "slug",
        ]

    def get_is_favorite(self, obj):
        # Logic for checking if the product is a favorite, for example:
        return obj.is_liked  # Or any other logic depending on your model structure
