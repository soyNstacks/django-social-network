"""social_network URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView 
from rest_framework.schemas import get_schema_view
from django.views.generic import TemplateView

from .views import *

app_name = "socialnetwork"

urlpatterns = [ 
    # Landing page  
    path('', LandingView.as_view(), name='index'), 
    # Login 
    path('login/', UserLoginView.as_view(), name='login'), 
    # Sign up 
    path('register/', UserRegistrationView.as_view(), name='register'), 
    # Path to social oauth login / sign up
    path('oauth/', include('social_django.urls', namespace='social-oauth')),
    
    # Log out
    path('logout/', LogoutView.as_view(next_page='/login'),name='logout'),
    
    # Home feed including creation of new post 
    path('home/', HomeFeed.as_view(), name='home'),
    # Detailed post
    path('post/<int:pk>/', PostDetailView.as_view(), name='post_detail'),
    # Delete post
    path('post/delete/<int:pk>/', PostDeleteView.as_view(), name='post_delete'),
    # Edit or update post
    path('post/edit/<int:pk>/', PostUpdateView.as_view(), name='post_update'),

    # Path to user account urls
    path('account/', include('account.urls', namespace='account')),
    # Path to chat urls
    path('chat/', include('chat.urls', namespace='chat')),
    # Path to friend urls
    path('friend/', include('friend.urls', namespace='friend')),   
    # Path to game urls
    path('game/', include('game.urls', namespace='game')),

    # Admin site
    path('admin/', admin.site.urls),
    
    # Path to api
    path('api/', include('api.urls', namespace='api')),

    path('api_schema/', get_schema_view(
        title="Social Network API",
        description="API for developers of the Social Network Platform",
        version="1.0.0"
    ), name='api_schema'),

    path('docs/', TemplateView.as_view(
        template_name='swagger_docs.html',
        extra_context={'schema_url':'api_schema'}
        ), name='swagger-ui'),

    # Path to debug tool for optimisation 
    path('__debug__/', include('debug_toolbar.urls')),

]  


# source: https://stackoverflow.com/questions/34563454/django-imagefield-upload-to-path
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
