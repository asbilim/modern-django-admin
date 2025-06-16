# apps/blog/pagination.py
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class BlogPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            'success': True,
            'message': 'Data retrieved successfully.',
            'meta': {
                'pagination': {
                    'next': self.get_next_link(),
                    'previous': self.get_previous_link(),
                    'count': self.page.paginator.count,
                    'total_pages': self.page.paginator.num_pages,
                    'current_page': self.page.number,
                    'page_size': self.get_page_size(self.request),
                }
            },
            'data': data
        }) 