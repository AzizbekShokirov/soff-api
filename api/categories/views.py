from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ProductCategory, RoomCategory
from .serializers import ProductCategorySerializer, RoomCategorySerializer


class RoomCategoryView(APIView):
    def get(self, request):
        categories = RoomCategory.objects.all()
        serializer = RoomCategorySerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=RoomCategorySerializer)
    def post(self, request):
        serializer = RoomCategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RoomCategoryDetailView(APIView):
    def get_object(self, category_id):
        try:
            return RoomCategory.objects.get(id=category_id)
        except RoomCategory.DoesNotExist:
            return Response(
                {"detail": "Room category not found."}, status=status.HTTP_404_NOT_FOUND
            )

    def get(self, request, category_id):
        category = self.get_object(category_id)
        serializer = RoomCategorySerializer(category)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=RoomCategorySerializer)
    def put(self, request, category_id):
        category = self.get_object(category_id)
        serializer = RoomCategorySerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, category_id):
        category = self.get_object(category_id)
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProductCategoryView(APIView):
    def get(self, request):
        categories = ProductCategory.objects.all()
        serializer = ProductCategorySerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=ProductCategorySerializer)
    def post(self, request):
        serializer = ProductCategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductCategoryDetailView(APIView):
    def get_object(self, category_id):
        try:
            return ProductCategory.objects.get(id=category_id)
        except ProductCategory.DoesNotExist:
            return Response(
                {"detail": "Product category not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

    def get(self, request, category_id):
        category = self.get_object(category_id)
        serializer = ProductCategorySerializer(category)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=ProductCategorySerializer)
    def put(self, request, category_id):
        category = self.get_object(category_id)
        serializer = ProductCategorySerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, category_id):
        category = self.get_object(category_id)
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
