from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.http import Http404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from products.models import Product
from products.serializers import ProductSerializer


class ProductView(APIView):
    @swagger_auto_schema(responses={200: ProductSerializer(many=True)})
    def get(self, request):
        queryset = Product.objects.all().order_by("title")
        paginator = PageNumberPagination()
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        serializer = ProductSerializer(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)

    @swagger_auto_schema(
        request_body=ProductSerializer,
        responses={201: ProductSerializer()},
    )
    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductDetailView(APIView):
    def get_object(self, product_slug):
        try:
            return Product.objects.get(slug=product_slug)
        except Product.DoesNotExist:
            raise Http404

    @swagger_auto_schema(responses={200: ProductSerializer()})
    def get(self, request, product_slug):
        try:
            product = self.get_object(product_slug)
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
    def put(self, request, product_slug):
        try:
            product = self.get_object(product_slug)
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
    def delete(self, request, product_slug):
        try:
            product = self.get_object(product_slug)
            product.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Http404:
            return Response(
                {"detail": "No Product matches the given query."},
                status=status.HTTP_404_NOT_FOUND,
            )


class ProductFilterView(APIView):
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
                "manufacturer",
                openapi.IN_QUERY,
                description="Filter by manufacturer (e.g., dafna, ikea).",
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
        responses={400: openapi.Response(description="Bad Request")},
    )
    def get(self, request):
        queryset = Product.objects.all().order_by("id")
        room_category = request.query_params.get("room_category", None)
        product_category = request.query_params.get("product_category", None)
        manufacturer = request.query_params.get("manufacturer", None)
        min_price = request.query_params.get("min_price", None)
        max_price = request.query_params.get("max_price", None)

        filters = {}
        if room_category:
            room_categories = room_category.split(",")
            filters["room_category__slug__in"] = room_categories
        if product_category:
            product_categories = product_category.split(",")
            filters["product_category__slug__in"] = product_categories
        if manufacturer:
            manufacturers = manufacturer.split(",")
            filters["manufacturer__slug__in"] = manufacturers

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
        if not query:
            return Response(
                {"detail": "Query parameter 'q' is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        search_query = SearchQuery(query)
        # Annotate products with search and rank fields
        products = (
            Product.objects.annotate(
                search=SearchVector(
                    "title",
                    "description",
                    "manufacturer__name",
                    "material",
                    "room_category__name",
                    "product_category__name",
                    "color",
                ),
                rank=SearchRank(SearchVector("title", "description"), search_query),
            )
            .filter(search=search_query)
            .order_by("-rank")
        )
        # Paginate the results
        paginator = PageNumberPagination()
        paginated_products = paginator.paginate_queryset(products, request)
        if paginated_products:
            serializer = ProductSerializer(paginated_products, many=True)
            return paginator.get_paginated_response(serializer.data)
        return Response(
            {"detail": "No products found"}, status=status.HTTP_404_NOT_FOUND
        )
