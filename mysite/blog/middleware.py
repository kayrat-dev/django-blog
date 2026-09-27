from django.shortcuts import render
from django_ratelimit.exceptions import Ratelimited

class RatelimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            return self.get_response(request)
        except Ratelimited:
            return render(request, 'blog/post/403_ratelimit.html', {'message': 'You are sending requests too frequently. Please wait a moment and try again.'}, status=429)