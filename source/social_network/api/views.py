from django.shortcuts import render, redirect
from django.views.generic import View

class ApiListView(View):
    """
    Renders landing page for the social network platform.
    """
    template_name = 'api.html'

    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('home')
        return render(request, self.template_name) 
        