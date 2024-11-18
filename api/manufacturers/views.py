from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from manufacturers.models import Manufacturer
from manufacturers.serializers import ManufacturerSerializer


class ManufacturerView(APIView):
    def get(self, request):
        room_categories = Manufacturer.objects.all()
        serializer = ManufacturerSerializer(room_categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=ManufacturerSerializer)
    def post(self, request):
        serializer = ManufacturerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ManufacturerDetailView(APIView):
    def get(self, request, slug):
        room_category = get_object_or_404(Manufacturer, slug=slug)
        serializer = ManufacturerSerializer(room_category)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=ManufacturerSerializer)
    def put(self, request, slug):
        room_category = get_object_or_404(Manufacturer, slug=slug)
        serializer = ManufacturerSerializer(
            room_category, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, slug):
        room_category = get_object_or_404(Manufacturer, slug=slug)
        room_category.delete()
        return Response(
            {"message": "Manufacturer deleted successfully."},
            status=status.HTTP_204_NO_CONTENT,
        )
