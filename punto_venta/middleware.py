"""Middleware."""

# Python
import re
from datetime import date

# Django
from django.shortcuts import redirect


class ExpirationMiddleware:
    """Exiration Middleware.
    
    If the app expires, redirects to a specific page to tell you that."""

    def __init__(self, get_response):
        """Init method."""

        self.get_response = get_response

    def __call__(self, request):
        """Call method."""

        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        """Process view.

        Here is were the redirection happens.
        """

        if date.today() > date(2020, 12, 4):
            return redirect('/messages/times_up')
        pass
