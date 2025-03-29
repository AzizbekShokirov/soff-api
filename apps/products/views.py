from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.http import Http404
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.serializers import ErrorResponseSerializer, SuccessResponseSerializer

from .models import Product
from .serializers import ProductSerializer


class ProductView(APIView):
    @extend_schema(
        tags=["Products"],
        description="List all products with pagination",
        responses={200: ProductSerializer(many=True)},
        examples=[
            OpenApiExample(
                "Products Paginated Response",
                value={
                    "count": 100,
                    "next": "http://api.example.org/products/?page=2",
                    "previous": None,
                    "results": [
                        {
                            "title": "Modern Sofa",
                            "description": "A comfortable modern sofa",
                            "color": "Grey",
                            "material": "Fabric",
                            "price": 599.99,
                            "maximum_load": 500.00,
                            "length": 200.00,
                            "width": 90.00,
                            "height": 85.00,
                            "rating": 4.5,
                            "room_category": "living-room",
                            "product_category": "sofa",
                            "manufacturer": "ikea",
                            "images": [{"image": "http://example.com/sofa-1.jpg"}],
                            "is_ar": True,
                            "ar_model": "http://example.com/ar-model",
                            "ar_url": "http://example.com/ar-url",
                            "is_favorite": False,
                            "slug": "modern-sofa",
                        }
                    ],
                },
            )
        ],
    )
    def get(self, request):
        queryset = Product.objects.all().order_by("title")
        paginator = PageNumberPagination()
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        serializer = ProductSerializer(paginated_queryset, many=True, context={"request": request})
        return paginator.get_paginated_response(serializer.data)

    @extend_schema(
        tags=["Products"],
        description="Create a new product",
        request=ProductSerializer,
        responses={201: ProductSerializer, 400: ErrorResponseSerializer},
        examples=[
            OpenApiExample(
                "Create Product Request",
                value={
                    "title": "Modern Coffee Table",
                    "description": "A stylish coffee table for your living room",
                    "color": "Brown",
                    "material": "Wood",
                    "price": 199.99,
                    "maximum_load": 100.00,
                    "length": 120.00,
                    "width": 60.00,
                    "height": 45.00,
                    "room_category": "living-room",
                    "product_category": "table",
                    "manufacturer": "ikea",
                    "images": [{"image": "http://example.com/table-1.jpg"}],
                    "is_ar": False,
                    "ar_model": "",
                    "ar_url": "",
                },
            )
        ],
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

    @extend_schema(
        tags=["Products"],
        description="Get details of a specific product by slug",
        responses={200: ProductSerializer, 404: ErrorResponseSerializer},
    )
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

    @extend_schema(
        tags=["Products"],
        description="Update a product's information",
        request=ProductSerializer,
        responses={200: ProductSerializer, 400: ErrorResponseSerializer, 404: ErrorResponseSerializer},
        examples=[
            OpenApiExample(
                "Update Product Request",
                value={
                    "price": 179.99,
                    "color": "Dark Brown",
                    "is_ar": True,
                    "ar_model": "http://example.com/updated-ar-model",
                },
            )
        ],
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

    @extend_schema(
        tags=["Products"],
        description="Delete a product",
        responses={204: SuccessResponseSerializer, 404: ErrorResponseSerializer},
    )
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
    @extend_schema(
        tags=["Products"],
        description="Filter products by various criteria including room category, product category, manufacturer, and price range",
        parameters=[
            OpenApiParameter(
                name="room_category",
                description="Filter by room category (e.g., kitchen, outdoor). Use commas to filter by multiple categories.",
                type=OpenApiTypes.STR,
                required=False,
                examples=[
                    OpenApiExample("Single category", value="living-room"),
                    OpenApiExample("Multiple categories", value="living-room,bedroom,kitchen"),
                ],
            ),
            OpenApiParameter(
                name="product_category",
                description="Filter by product category (e.g., shelf, stool). Use commas to filter by multiple categories.",
                type=OpenApiTypes.STR,
                required=False,
                examples=[
                    OpenApiExample("Single category", value="sofa"),
                    OpenApiExample("Multiple categories", value="sofa,chair,table"),
                ],
            ),
            OpenApiParameter(
                name="manufacturer",
                description="Filter by manufacturer (e.g., dafna, ikea). Use commas to filter by multiple manufacturers.",
                type=OpenApiTypes.STR,
                required=False,
                examples=[
                    OpenApiExample("Single manufacturer", value="ikea"),
                    OpenApiExample("Multiple manufacturers", value="ikea,dafna"),
                ],
            ),
            OpenApiParameter(
                name="min_price",
                description="Filter by minimum price.",
                type=OpenApiTypes.NUMBER,
                required=False,
                examples=[OpenApiExample("Minimum price", value=100)],
            ),
            OpenApiParameter(
                name="max_price",
                description="Filter by maximum price.",
                type=OpenApiTypes.NUMBER,
                required=False,
                examples=[OpenApiExample("Maximum price", value=500)],
            ),
        ],
        responses={200: ProductSerializer(many=True), 400: ErrorResponseSerializer},
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

        serializer = ProductSerializer(paginated_queryset, many=True, context={"request": request})

        return paginator.get_paginated_response(serializer.data)


class ProductSearchView(APIView):
    @extend_schema(
        tags=["Products"],
        description="Search for products using full-text search. Searches across title, description, manufacturer, material, categories, and color fields.",
        parameters=[
            OpenApiParameter(
                name="q",
                description="Search query text",
                type=OpenApiTypes.STR,
                required=True,
                examples=[
                    OpenApiExample("Basic search", value="leather sofa"),
                    OpenApiExample("Specific search", value="ikea kitchen table"),
                ],
            )
        ],
        responses={200: ProductSerializer(many=True), 400: ErrorResponseSerializer},
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
        serializer = ProductSerializer(paginated_products, many=True, context={"request": request})
        return paginator.get_paginated_response(serializer.data)
