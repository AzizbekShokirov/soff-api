from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiExample
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from apps.users.serializers import ErrorResponseSerializer, SuccessResponseSerializer
from .models import Manufacturer
from .serializers import ManufacturerSerializer


class ManufacturerView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Manufacturers"],
        description="List all furniture manufacturers",
        responses={200: ManufacturerSerializer(many=True)},
        examples=[
            OpenApiExample(
                "Manufacturers Response",
                value=[
                    {
                        "name": "IKEA",
                        "description": "Swedish furniture manufacturer",
                        "image": "http://example.com/ikea-logo.jpg",
                        "slug": "ikea"
                    },
                    {
                        "name": "Ashley Furniture",
                        "description": "American furniture manufacturer",
                        "image": "http://example.com/ashley-logo.jpg",
                        "slug": "ashley-furniture"
                    }
                ]
            )
        ]
    )
    def get(self, request):
        room_categories = Manufacturer.objects.all()
        serializer = ManufacturerSerializer(room_categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        tags=["Manufacturers"],
        description="Create a new manufacturer",
        request=ManufacturerSerializer,
        responses={
            201: ManufacturerSerializer,
            400: ErrorResponseSerializer
        },
        examples=[
            OpenApiExample(
                "Create Manufacturer Request",
                value={
                    "name": "Dafna",
                    "description": "Local furniture manufacturer",
                    "image": "http://example.com/dafna-logo.jpg"
                }
            )
        ]
    )
    def post(self, request):
        serializer = ManufacturerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ManufacturerDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Manufacturers"],
        description="Get details of a specific manufacturer by slug",
        responses={
            200: ManufacturerSerializer,
            404: ErrorResponseSerializer
        },
        examples=[
            OpenApiExample(
                "Manufacturer Detail Response",
                value={
                    "name": "IKEA",
                    "description": "Swedish furniture manufacturer",
                    "image": "http://example.com/ikea-logo.jpg",
                    "slug": "ikea"
                }
            )
        ]
    )
    def get(self, request, slug):
        room_category = get_object_or_404(Manufacturer, slug=slug)
        serializer = ManufacturerSerializer(room_category)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        tags=["Manufacturers"],
        description="Update a manufacturer's information",
        request=ManufacturerSerializer,
        responses={
            200: ManufacturerSerializer,
            400: ErrorResponseSerializer,
            404: ErrorResponseSerializer
        },
        examples=[
            OpenApiExample(
                "Update Manufacturer Request",
                value={
                    "name": "IKEA International",
                    "description": "Updated Swedish furniture manufacturer"
                }
            )
        ]
    )
    def put(self, request, slug):
        room_category = get_object_or_404(Manufacturer, slug=slug)
        serializer = ManufacturerSerializer(
            room_category, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        tags=["Manufacturers"],
        description="Delete a manufacturer",
        responses={
            204: SuccessResponseSerializer,
            404: ErrorResponseSerializer
        }
    )
    def delete(self, request, slug):
        room_category = get_object_or_404(Manufacturer, slug=slug)
        room_category.delete()
        return Response(
            {"message": "Manufacturer deleted successfully."},
            status=status.HTTP_204_NO_CONTENT,
        )
