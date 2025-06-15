# myapp/pagination.py
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class CustomRoomPagination(PageNumberPagination):
    page_size_query_param = 'size'
    max_page_size = 10
    page_query_param = 'page'
    page_size = 10

    def get_paginated_response(self, data):
        total_items = self.page.paginator.count
        page_size = self.get_page_size(self.request)
        total_pages = (total_items + page_size - 1) // page_size if page_size > 0 else 0


        return Response({
            'currentPage': self.page.number,
            'pageSize': page_size,
            'nextPage': self.get_next_link().split('=')[-1] if self.get_next_link() else None,
            'previousPage': self.get_previous_link().split('=')[-1] if self.get_previous_link() else None,
            'hasNextPage': self.page.has_next(),
            'hasPreviousPage': self.page.has_previous(),
            'totalPages': total_pages,
            'content': data,
            'totalItems': total_items
        })