"""Custom DRF pagination classes for Igar."""

from rest_framework.pagination import PageNumberPagination


class IgarPagination(PageNumberPagination):
    """Default pagination for Igar API endpoints."""

    page_size = 25
    page_size_query_param = "page_size"
    max_page_size = 100
