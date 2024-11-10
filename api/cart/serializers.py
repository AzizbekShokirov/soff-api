from rest_framework import serializers

from .models import Cart, CartItem, Product

class CartProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "title", "price"]


class CartItemSerializer(serializers.ModelSerializer):
    product = CartProductSerializer(read_only=True)  # This will only show the product in responses, not in the request
    product_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = CartItem
        fields = ["id", "product", "product_id", "quantity"]

    def create(self, validated_data):
        product = Product.objects.get(id=validated_data.pop("product_id"))
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
