from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.serializers import ErrorResponseSerializer, SuccessResponseSerializer

from .models import ProductCategory, RoomCategory
from .serializers import ProductCategorySerializer, RoomCategorySerializer


class RoomCategoryView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Room Categories"],
        description="List all room categories",
        responses={200: RoomCategorySerializer(many=True)},
        examples=[
            OpenApiExample(
                "Room Categories Response",
                value=[
                    {"name": "Kitchen", "image": "http://example.com/kitchen.jpg", "slug": "kitchen"},
                    {"name": "Living Room", "image": "http://example.com/living-room.jpg", "slug": "living-room"},
                ],
            )
        ],
    )
    def get(self, request):
        room_categories = RoomCategory.objects.all()
        serializer = RoomCategorySerializer(room_categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        tags=["Room Categories"],
        description="Create a new room category",
        request=RoomCategorySerializer,
        responses={201: RoomCategorySerializer, 400: ErrorResponseSerializer},
        examples=[
            OpenApiExample(
                "Create Room Category Request", value={"name": "Bedroom", "image": "http://example.com/bedroom.jpg"}
            )
        ],
    )
    def post(self, request):
        serializer = RoomCategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RoomCategoryDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Room Categories"],
        description="Get details of a specific room category by slug",
        responses={200: RoomCategorySerializer, 404: ErrorResponseSerializer},
        examples=[
            OpenApiExample(
                "Room Category Detail Response",
                value={"name": "Kitchen", "image": "http://example.com/kitchen.jpg", "slug": "kitchen"},
            )
        ],
    )
    def get(self, request, slug):
        room_category = get_object_or_404(RoomCategory, slug=slug)
        serializer = RoomCategorySerializer(room_category)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        tags=["Room Categories"],
        description="Update a room category",
        request=RoomCategorySerializer,
        responses={200: RoomCategorySerializer, 400: ErrorResponseSerializer, 404: ErrorResponseSerializer},
        examples=[
            OpenApiExample(
                "Update Room Category Request",
                value={"name": "Updated Bedroom", "image": "http://example.com/updated-bedroom.jpg"},
            )
        ],
    )
    def put(self, request, slug):
        room_category = get_object_or_404(RoomCategory, slug=slug)
        serializer = RoomCategorySerializer(room_category, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        tags=["Room Categories"],
        description="Delete a room category",
        responses={204: SuccessResponseSerializer, 404: ErrorResponseSerializer},
    )
    def delete(self, request, slug):
        room_category = get_object_or_404(RoomCategory, slug=slug)
        room_category.delete()
        return Response(
            {"message": "Room category deleted successfully."},
            status=status.HTTP_204_NO_CONTENT,
        )


class ProductCategoryView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Product Categories"],
        description="List all product categories",
        responses={200: ProductCategorySerializer(many=True)},
        examples=[
            OpenApiExample(
                "Product Categories Response",
                value=[
                    {"name": "Sofa", "image": "http://example.com/sofa.jpg", "slug": "sofa"},
                    {"name": "Chair", "image": "http://example.com/chair.jpg", "slug": "chair"},
                ],
            )
        ],
    )
    def get(self, request):
        product_categories = ProductCategory.objects.all()
        serializer = ProductCategorySerializer(product_categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        tags=["Product Categories"],
        description="Create a new product category",
        request=ProductCategorySerializer,
        responses={201: ProductCategorySerializer, 400: ErrorResponseSerializer},
        examples=[
            OpenApiExample(
                "Create Product Category Request", value={"name": "Table", "image": "http://example.com/table.jpg"}
            )
        ],
    )
    def post(self, request):
        serializer = ProductCategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductCategoryDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Product Categories"],
        description="Get details of a specific product category by slug",
        responses={200: ProductCategorySerializer, 404: ErrorResponseSerializer},
        examples=[
            OpenApiExample(
                "Product Category Detail Response",
                value={"name": "Chair", "image": "http://example.com/chair.jpg", "slug": "chair"},
            )
        ],
    )
    def get(self, request, slug):
        product_category = get_object_or_404(ProductCategory, slug=slug)
        serializer = ProductCategorySerializer(product_category)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        tags=["Product Categories"],
        description="Update a product category",
        request=ProductCategorySerializer,
        responses={200: ProductCategorySerializer, 400: ErrorResponseSerializer, 404: ErrorResponseSerializer},
        examples=[
            OpenApiExample(
                "Update Product Category Request",
                value={"name": "Updated Chair", "image": "http://example.com/updated-chair.jpg"},
            )
        ],
    )
    def put(self, request, slug):
        product_category = get_object_or_404(ProductCategory, slug=slug)
        serializer = ProductCategorySerializer(product_category, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        tags=["Product Categories"],
        description="Delete a product category",
        responses={204: SuccessResponseSerializer, 404: ErrorResponseSerializer},
    )
    def delete(self, request, slug):
        product_category = get_object_or_404(ProductCategory, slug=slug)
        product_category.delete()
        return Response(
            {"message": "Product category deleted successfully."},
            status=status.HTTP_204_NO_CONTENT,
        )
