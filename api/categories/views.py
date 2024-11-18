from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from categories.models import ProductCategory, RoomCategory
from categories.serializers import ProductCategorySerializer, RoomCategorySerializer


class RoomCategoryView(APIView):
    def get(self, request):
        room_categories = RoomCategory.objects.all()
        serializer = RoomCategorySerializer(room_categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=RoomCategorySerializer)
    def post(self, request):
        serializer = RoomCategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RoomCategoryDetailView(APIView):
    def get(self, request, slug):
        room_category = get_object_or_404(RoomCategory, slug=slug)
        serializer = RoomCategorySerializer(room_category)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=RoomCategorySerializer)
    def put(self, request, slug):
        room_category = get_object_or_404(RoomCategory, slug=slug)
        serializer = RoomCategorySerializer(
            room_category, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, slug):
        room_category = get_object_or_404(RoomCategory, slug=slug)
        room_category.delete()
        return Response(
            {"message": "Room category deleted successfully."},
            status=status.HTTP_204_NO_CONTENT,
        )


class ProductCategoryView(APIView):
    def get(self, request):
        product_categories = ProductCategory.objects.all()
        serializer = ProductCategorySerializer(product_categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=ProductCategorySerializer)
    def post(self, request):
        serializer = ProductCategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductCategoryDetailView(APIView):
    def get(self, request, slug):
        product_category = get_object_or_404(ProductCategory, slug=slug)
        serializer = ProductCategorySerializer(product_category)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=ProductCategorySerializer)
    def put(self, request, slug):
        product_category = get_object_or_404(ProductCategory, slug=slug)
        serializer = ProductCategorySerializer(
            product_category, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, slug):
        product_category = get_object_or_404(ProductCategory, slug=slug)
        product_category.delete()
        return Response(
            {"message": "Product category deleted successfully."},
            status=status.HTTP_204_NO_CONTENT,
        )
