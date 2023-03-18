from django.conf import settings
from django.core.cache import cache 
from django.utils import timezone
from django.http import Http404
from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin 

class ActiveUserMiddleware(MiddlewareMixin):

    def process_request(self, request):
        current_user = request.user
        if request.user.is_authenticated:
            now = timezone.datetime.now()
            cache.set('seen_%s' % (current_user.username), now, 
                           settings.USER_LASTSEEN_TIMEOUT)
            

class RestrictConfidentialPageMiddleware(MiddlewareMixin):

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith("/admin/"):
            if not request.user.is_authenticated:
                return redirect('home')
            elif not request.user.is_staff or not request.user.is_superuser:
                raise Http404()

        response = self.get_response(request)
        return response  