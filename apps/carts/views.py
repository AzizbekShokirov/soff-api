from django.http import Http404
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.serializers import ErrorResponseSerializer, SuccessResponseSerializer

from .models import Cart, CartItem
from .serializers import CartItemSerializer, CartSerializer


class CartView(APIView):
    permission_classes = [IsAuthenticated]

    def get_cart(self, user):
        return Cart.objects.get_or_create(user=user)[0]

    @extend_schema(
        tags=["Carts"],
        description="Retrieve the current user's shopping cart",
        responses={200: CartSerializer},
        examples=[
            OpenApiExample(
                "Cart Response Example",
                value={
                    "cart_items": [
                        {
                            "product": {
                                "title": "Sample Product",
                                "slug": "sample-product",
                                "price": 99.99,
                                "manufacturer": "IKEA",
                                "images": [{"image": "http://example.com/image.jpg"}],
                            },
                            "quantity": 2,
                            "total_price": 199.98,
                        }
                    ],
                    "total_cost": 199.98,
                },
            )
        ],
    )
    def get(self, request):
        cart = self.get_cart(request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        tags=["Carts"],
        description="Add a product to the shopping cart",
        request=CartItemSerializer,
        responses={201: CartItemSerializer, 400: ErrorResponseSerializer},
        examples=[OpenApiExample("Add to Cart Request", value={"product_slug": "sample-product", "quantity": 1})],
    )
    def post(self, request):
        cart = self.get_cart(request.user)
        serializer = CartItemSerializer(data=request.data, context={"cart": cart})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CartDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_cart(self, user):
        return Cart.objects.get(user=user)

    def get_object_by_slug(self, product_slug, user):
        try:
            return CartItem.objects.get(product__slug=product_slug, cart__user=user)
        except CartItem.DoesNotExist:
            raise Http404

    @extend_schema(
        tags=["Carts"],
        description="Get details of a specific cart item by product slug",
        responses={200: CartItemSerializer, 404: ErrorResponseSerializer},
        examples=[OpenApiExample("Cart Item Response", value={"product_slug": "sample-product", "quantity": 2})],
    )
    def get(self, request, product_slug=None):
        cart_item = self.get_object_by_slug(product_slug, request.user)
        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        tags=["Carts"],
        description="Update the quantity of a product in the cart",
        request=CartItemSerializer,
        responses={200: CartItemSerializer, 400: ErrorResponseSerializer},
        examples=[OpenApiExample("Update Cart Item Request", value={"quantity": 3})],
    )
    def put(self, request, product_slug=None):
        cart_item = self.get_object_by_slug(product_slug, request.user)
        quantity_change = request.data.get("quantity")
        if quantity_change is None or quantity_change <= 0:
            return Response(
                {"error": "Quantity must be greater than zero"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        cart_item.quantity = quantity_change
        cart_item.save()
        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        tags=["Carts"],
        description="Remove a product from the cart",
        responses={204: SuccessResponseSerializer, 404: ErrorResponseSerializer},
    )
    def delete(self, request, product_slug=None):
        cart_item = self.get_object_by_slug(product_slug, request.user)
        cart_item.delete()
        return Response({"message": "Item removed from cart."}, status=status.HTTP_204_NO_CONTENT)


class ClearCartView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Carts"], description="Remove all items from the user's cart", responses={204: SuccessResponseSerializer}
    )
    def delete(self, request):
        cart = Cart.objects.get(user=request.user)
        cart.cart_items.all().delete()
        return Response({"message": "Cart cleared."}, status=status.HTTP_204_NO_CONTENT)
