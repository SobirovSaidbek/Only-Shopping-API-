from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination


class CustomizedAssistantPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 35

    def get_paginated_response(self, data):
        response = {
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'count': self.page.paginator.count,
            'results': data
        }

        return Response(response)


