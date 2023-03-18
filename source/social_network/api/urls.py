from django.contrib import admin
from django.urls import include, path 
 
from .api import * 
from .views import *

app_name = 'api'

urlpatterns = [
    # Retrieves list of avaialble API endpoints as a view
    path('', ApiListView.as_view(), name='api_list'),

    # Path to list of accounts
    path('profiles/', ListUsers.as_view(), name='account_list_api'), 
    # Path to create a new account
    path('profile/', CreateAccount.as_view(), name='create_account_api'),
    # Path to retrieve detailed profile information for a specified user
    path('profile/<str:user__username>/', RetrieveAccountDetails.as_view(), name='account_profile_api'),
    # Path to list of posts of specified user
    path('posts/<str:user__username>/', ListUserPosts.as_view(), name='post_list_api'),
    # Path to create a new post
    path('post/', CreateUserPost.as_view(), name='create_post_api'),
    # Path to friends list of specified user
    path('friends/<str:user__username>/', RetrieveFriendsDetails.as_view(), name='friends_details_api'),
    # Path to details of specified chatroom
    path('chatroom/<str:room_name>/', ChatRoomDetails.as_view(), name='chatroom_details_api'),

] 