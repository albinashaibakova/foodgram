from django.conf import settings
from rest_framework import pagination

class FoodgramPaginator(pagination.PageNumberPagination):
    page_size_query_param = 'limit'
    page_size = getattr(settings, 'PAGE_SIZE', 6)
