from django.http import Http404
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from cart.models import Cart, CartItem
from cart.serializers import CartItemSerializer, CartSerializer


class CartView(APIView):
    def get_cart(self, user):
        return Cart.objects.get_or_create(user=user)[0]

    def get(self, request):
        cart = self.get_cart(request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=CartItemSerializer)
    def post(self, request):
        cart = self.get_cart(request.user)
        serializer = CartItemSerializer(data=request.data, context={"cart": cart})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CartDetailView(APIView):
    def get_cart(self, user):
        return Cart.objects.get(user=user)

    def get_object_by_slug(self, product_slug, user):
        try:
            return CartItem.objects.get(product__slug=product_slug, cart__user=user)
        except CartItem.DoesNotExist:
            raise Http404

    def get(self, request, product_slug=None):
        cart_item = self.get_object_by_slug(product_slug, request.user)
        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=CartItemSerializer)
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

    def delete(self, request, product_slug=None):
        cart_item = self.get_object_by_slug(product_slug, request.user)
        cart_item.delete()
        return Response(
            {"message": "Item removed from cart."}, status=status.HTTP_204_NO_CONTENT
        )


class ClearCartView(APIView):
    def delete(self, request):
        cart = Cart.objects.get(user=request.user)
        cart.cart_items.all().delete()
        return Response({"message": "Cart cleared."}, status=status.HTTP_204_NO_CONTENT)
