from django.urls import include, path
from .views import *
from django.contrib.auth.views import LogoutView 
from django.contrib.auth import views as auth_views

  
app_name = 'account' 

# top level route is /account

urlpatterns = [
    # User profile information 
    path('profile/<str:username>/', ProfileView.as_view(), name='profile'),
    # Edit user personal profile information 
    path('profile/<str:username>/edit', EditProfileView.as_view(), name='profile-edit'),
    # Edit user confidential information 
    path('profile/changepassword', auth_views.PasswordChangeView.as_view(
            template_name='account/password_change.html',
            success_url = '/home'
        ), name='password-change'),
    # Search results for profile
    path('search/', UserSearchView.as_view(), name='search-profile'), 
]
    