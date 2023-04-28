from rest_framework.pagination import (LimitOffsetPagination,
                                       PageNumberPagination)


class LimitPageNumberPagination(LimitOffsetPagination, PageNumberPagination):
    default_limit = 10
    limit_query_param = 'limit'
    max_limit = 100

    page_query_param = 'page'
    page_size = 6
