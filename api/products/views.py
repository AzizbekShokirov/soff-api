from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.http import Http404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import Favorite

from .models import Product
from .serializers import (
    ProductSerializer,
)


class ProductView(APIView):
    @swagger_auto_schema(
        operation_description="Get a list of products with pagination",
        manual_parameters=[
            openapi.Parameter(
                "room_category",
                openapi.IN_QUERY,
                description="Filter by room category (e.g., kitchen, outdoor).",
                type=openapi.TYPE_STRING,
                required=False,
            ),
            openapi.Parameter(
                "product_category",
                openapi.IN_QUERY,
                description="Filter by product category (e.g., shelf, stool).",
                type=openapi.TYPE_STRING,
                required=False,
            ),
            openapi.Parameter(
                "min_price",
                openapi.IN_QUERY,
                description="Filter by minimum price.",
                type=openapi.TYPE_NUMBER,
                required=False,
            ),
            openapi.Parameter(
                "max_price",
                openapi.IN_QUERY,
                description="Filter by maximum price.",
                type=openapi.TYPE_NUMBER,
                required=False,
            ),
        ],
        responses={400: openapi.Response(description="Bad Request"),},
    )
    def get(self, request):
        queryset = Product.objects.all().order_by('id')
        room_category = request.query_params.get("room_category", None)
        product_category = request.query_params.get("product_category", None)
        min_price = request.query_params.get("min_price", None)
        max_price = request.query_params.get("max_price", None)

        filters = {}
        if room_category:
            room_categories = room_category.split(",")
            filters["room_category__id__in"] = room_categories
        if product_category:
            product_categories = product_category.split(",")
            filters["product_category__id__in"] = product_categories
        if min_price:
            try:
                filters["price__gte"] = float(min_price)
            except ValueError:
                return Response(
                    {"error": "Invalid min_price value"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        if max_price:
            try:
                filters["price__lte"] = float(max_price)
            except ValueError:
                return Response(
                    {"error": "Invalid max_price value"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        queryset = queryset.filter(**filters)

        paginator = PageNumberPagination()
        paginated_queryset = paginator.paginate_queryset(queryset, request)

        serializer = ProductSerializer(paginated_queryset, many=True)

        return paginator.get_paginated_response(serializer.data)

    @swagger_auto_schema(
        request_body=ProductSerializer, responses={201: ProductSerializer()}
    )
    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductDetailView(APIView):
    def get_object(self, product_id):
        try:
            return Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise Http404

    @swagger_auto_schema(responses={200: ProductSerializer()})
    def get(self, request, product_id):
        try:
            product = self.get_object(product_id)
            serializer = ProductSerializer(product)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Product.DoesNotExist:
            return Response(
                {"detail": "No Product matches the given query."},
                status=status.HTTP_404_NOT_FOUND,
            )

    @swagger_auto_schema(
        request_body=ProductSerializer, responses={200: ProductSerializer()}
    )
    def put(self, request, product_id):
        try:
            product = self.get_object(product_id)
            serializer = ProductSerializer(product, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Http404:
            return Response(
                {"detail": "No Product matches the given query."},
                status=status.HTTP_404_NOT_FOUND,
            )

    @swagger_auto_schema(responses={204: "Product deleted."})
    def delete(self, request, product_id):
        try:
            product = self.get_object(product_id)
            product.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Http404:
            return Response(
                {"detail": "No Product matches the given query."},
                status=status.HTTP_404_NOT_FOUND,
            )


class ProductLikeView(APIView):
    @swagger_auto_schema(
        responses={200: "Product liked and added to favorites."},
    )
    def post(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                {"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND
            )
        # Get or create the favorite entry
        favorite, created = Favorite.objects.get_or_create(
            user=request.user, product=product
        )
        favorite.liked = not favorite.liked  # Toggle the liked status
        favorite.save()

        if favorite.liked:
            message = "Product liked."
            status_code = status.HTTP_201_CREATED
        else:
            message = "Product unliked."
            status_code = status.HTTP_200_OK

        return Response(
            {"message": message}, status=status_code
        )


class ProductSearchView(APIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "q",
                openapi.IN_QUERY,
                description="Search query",
                type=openapi.TYPE_STRING,
                required=True,
            )
        ],
    )
    def get(self, request, *args, **kwargs):
        query = request.query_params.get("q", None)
        if query:
            search_query = SearchQuery(query)
            # Search across multiple fields using SearchVector
            products = Product.objects.annotate(
                search=SearchVector(
                    "title",
                    "description",
                    "manufacturer",
                    "material",
                    "room_category",
                    "product_category",
                    "color",
                ),
                rank=SearchRank(
                    SearchVector("title", "description"), search_query
                ),
            ).filter(search=query).order_by("-rank")

        paginator = PageNumberPagination()
        paginated_products = paginator.paginate_queryset(products, request)

        if paginated_products:
            serializer = ProductSerializer(paginated_products, many=True)
            return paginator.get_paginated_response(serializer.data)

        return Response(
            {"message": "No products found"}, status=status.HTTP_404_NOT_FOUND
        )
