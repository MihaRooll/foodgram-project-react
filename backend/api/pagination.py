from rest_framework.pagination import PageNumberPagination


class CustomPageNumberPagination(PageNumberPagination):
    """Custom pagination class having page_size_query_aram."""

    page_size_query_param = 'limit'
