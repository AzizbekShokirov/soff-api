from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Manufacturer
from .serializers import ManufacturerSerializer


class ManufacturerView(APIView):
    def get(self, request):
        categories = Manufacturer.objects.all()
        serializer = ManufacturerSerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=ManufacturerSerializer)
    def post(self, request):
        serializer = ManufacturerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ManufacturerDetailView(APIView):
    def get_object(self, manufacturer_id):
        try:
            return Manufacturer.objects.get(id=manufacturer_id)
        except Manufacturer.DoesNotExist:
            return Response(
                {"detail": "Manufacturer not found."}, status=status.HTTP_404_NOT_FOUND
            )

    def get(self, request, manufactuer_id):
        category = self.get_object(id=manufactuer_id)
        serializer = ManufacturerSerializer(category)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=ManufacturerSerializer)
    def put(self, request, manufactuer_id):
        category = self.get_object(id=manufactuer_id)
        serializer = ManufacturerSerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, manufactuer_id):
        category = self.get_object(id=manufactuer_id)
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
