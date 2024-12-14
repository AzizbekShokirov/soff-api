from django.forms import ValidationError
from products.serializers import ProductImageSerializer
from rest_framework import serializers

from cart.models import Cart, CartItem, Product


class CartProductSerializer(serializers.ModelSerializer):
    manufacturer = serializers.CharField(source="manufacturer.name")
    images = ProductImageSerializer(many=True)

    class Meta:
        model = Product
        fields = ["title", "price", "manufacturer", "images"]

    def get_total_price(self, obj):
        return obj.total_price()


class CartItemGETSerializer(serializers.ModelSerializer):
    product = CartProductSerializer()
    product_slug = serializers.SlugField(write_only=True)
    quantity = serializers.IntegerField(min_value=1)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ["product", "product_slug", "quantity", "total_price"]
        read_only_fields = [
            "product"
        ]  # product is in the response, but not in the request

    def get_total_price(self, obj):
        return obj.total_price()


class CartItemSerializer(serializers.ModelSerializer):
    product_slug = serializers.SlugField(write_only=True)
    quantity = serializers.IntegerField(min_value=1)

    class Meta:
        model = CartItem
        fields = ["product_slug", "quantity"]

    def validate_slug(self, product_slug):
        try:
            return Product.objects.get(slug=product_slug)
        except Product.DoesNotExist:
            raise ValidationError(f"Product with slug '{product_slug}' does not exist.")

    def create(self, validated_data):
        product_slug = validated_data.pop("product_slug")
        product = self.validate_slug(product_slug)
        cart = self.context["cart"]

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={"quantity": validated_data.get("quantity", 1)},
        )

        if not created:
            cart_item.quantity += validated_data.get("quantity", 1)
            cart_item.save()

        return cart_item

    def update(self, instance, validated_data):
        if "product_slug" in validated_data:
            product_slug = validated_data.pop("product_slug")
            product = self.validate_slug(product_slug)
            instance.product = product

        instance.quantity = validated_data.get("quantity", instance.quantity)
        instance.save()
        return instance


class CartSerializer(serializers.ModelSerializer):
    cart_items = CartItemGETSerializer(many=True, read_only=True)
    total_cost = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ["cart_items", "total_cost"]

    def get_total_cost(self, obj):
        return obj.total_cost()
