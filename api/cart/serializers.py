from rest_framework import serializers

from cart.models import Cart, CartItem, Product


class CartProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["slug", "title", "price"]


class CartItemSerializer(serializers.ModelSerializer):
    product = CartProductSerializer(
        read_only=True
    )  # This will only show the product in responses, not in the request
    product_slug = serializers.SlugField(write_only=True)

    class Meta:
        model = CartItem
        fields = ["id", "product", "product_slug", "quantity"]

    def create(self, validated_data):
        product_slug = validated_data.pop("product_slug")
        product = Product.objects.get(slug=product_slug)
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
            instance.product = Product.objects.get(slug=product_slug)

        instance.quantity = validated_data.get("quantity", instance.quantity)
        instance.save()
        return instance


class CartSerializer(serializers.ModelSerializer):
    cart_items = CartItemSerializer(many=True, read_only=True)
    total_cost = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ["cart_items", "total_cost"]

    def get_total_cost(self, obj):
        return obj.total_cost()
