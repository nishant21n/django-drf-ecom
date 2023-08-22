from django.db import connection
from django.db.models import Prefetch
from drf_spectacular.utils import extend_schema
from pygments import highlight
from pygments.formatters import TerminalFormatter
from pygments.lexers import SqlLexer
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from sqlparse import format

from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer


class CategoryViewSet(viewsets.ViewSet):
    """
    A simple Viewset for viewing all categories
    """

    queryset = Category.objects.all()

    @extend_schema(responses=CategorySerializer)
    def list(self, request):
        serializer = CategorySerializer(self.queryset, many=True)
        return Response(serializer.data)


class ProductViewSet(viewsets.ViewSet):
    """
    A simple Viewset for viewing all products
    """

    queryset = Product.objects.all().is_active()

    lookup_field = "slug"

    def retrieve(self, request, slug=None):
        serializer = ProductSerializer(
            Product.objects.filter(slug=slug)
            .select_related("category")
            .prefetch_related(Prefetch("product_line__product_image"))
            .prefetch_related(Prefetch("product_line__attribute_value__attribute")),
            many=True,
        )
        data = Response(serializer.data)

        # q = list(connection.queries)
        # print(len(q))
        # for qs in q:
        #     sqlformatted = format(str(qs["sql"]), reindent=True)
        #     print(highlight(sqlformatted, SqlLexer(), TerminalFormatter()))

        return data

    @extend_schema(responses=ProductSerializer)
    def list(self, request):
        serializer = ProductSerializer(self.queryset, many=True)
        return Response(serializer.data)

    @action(
        methods=["get"],
        detail=False,
        url_path=r"category/(?P<slug>[\w-]+)",
    )
    def list_product_by_category_slug(self, request, slug=None):
        """
        An endpoint to return products by category
        """
        serializer = ProductSerializer(
            self.queryset.filter(category__slug=slug), many=True
        )
        return Response(serializer.data)
