from decimal import Decimal

from django.core.validators import MaxValueValidator, MinValueValidator
from rest_framework import serializers

from accounts.models import Favorite
from categories.models import ProductCategory, RoomCategory
from manufacturers.models import Manufacturer
from products.models import Product, ProductImage


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["image"]


class ProductSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=255)
    description = serializers.CharField(max_length=1000)
    color = serializers.CharField(max_length=255)
    material = serializers.CharField(max_length=255)
    price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[
            MaxValueValidator(Decimal("99999999.99")),
            MinValueValidator(Decimal("0.00")),
        ],
    )
    maximum_load = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[
            MaxValueValidator(Decimal("99999999.99")),
            MinValueValidator(Decimal("0.00")),
        ],
    )
    length = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[
            MaxValueValidator(Decimal("99999999.99")),
            MinValueValidator(Decimal("0.00")),
        ],
    )
    width = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[
            MaxValueValidator(Decimal("99999999.99")),
            MinValueValidator(Decimal("0.00")),
        ],
    )
    height = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[
            MaxValueValidator(Decimal("99999999.99")),
            MinValueValidator(Decimal("0.00")),
        ],
    )
    rating = serializers.DecimalField(
        max_digits=3,
        decimal_places=1,
        required=False,
        validators=[
            MaxValueValidator(Decimal("5.0")),
            MinValueValidator(Decimal("0.0")),
        ],
    )
    room_category = serializers.SlugRelatedField(
        slug_field="slug", queryset=RoomCategory.objects.all()
    )
    product_category = serializers.SlugRelatedField(
        slug_field="slug", queryset=ProductCategory.objects.all()
    )
    manufacturer = serializers.SlugRelatedField(
        slug_field="slug", queryset=Manufacturer.objects.all()
    )
    images = ProductImageSerializer(many=True)
    is_ar = serializers.BooleanField()
    ar_model = serializers.URLField()
    ar_url = serializers.URLField()
    is_favorite = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        exclude = ["id"]

    def create(self, validated_data):
        images_data = validated_data.pop("images")
        room_category_data = validated_data.pop("room_category")
        product_category_data = validated_data.pop("product_category")
        manufacturer_data = validated_data.pop("manufacturer")

        room_category = RoomCategory.objects.get(**room_category_data)

        product_category = ProductCategory.objects.get(**product_category_data)

        manufacturer = Manufacturer.objects.get(**manufacturer_data)

        product = Product.objects.create(
            room_category=room_category,
            product_category=product_category,
            manufacturer=manufacturer,
            **validated_data,
        )

        # Create ProductImage instances
        for image_data in images_data:
            ProductImage.objects.create(product=product, **image_data)

        return product

    def update(self, instance, validated_data):
        images_data = validated_data.pop("images", None)  # Get images data
        room_category_data = validated_data.pop("room_category", None)
        product_category_data = validated_data.pop("product_category", None)
        manufacturer_data = validated_data.pop("manufacturer", None)

        if room_category_data:
            room_category, created = RoomCategory.objects.get(
                id=instance.room_category.id, defaults=room_category_data
            )
            instance.room_category = room_category

        if product_category_data:
            product_category, created = ProductCategory.objects.get(
                id=instance.product_category.id, defaults=product_category_data
            )
            instance.product_category = product_category

        if manufacturer_data:
            manufacturer, created = Manufacturer.objects.get(
                id=instance.manufacturer.id, defaults=manufacturer_data
            )
            instance.manufacturer = manufacturer

        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        # Update images
        if images_data is not None:
            # Clear existing images
            instance.images.all().delete()
            # Create new images
            for image_data in images_data:
                ProductImage.objects.create(product=instance, **image_data)

        return instance

    def get_is_favorite(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return Favorite.objects.filter(user=user, product=obj, is_liked=True).exists()
        return False