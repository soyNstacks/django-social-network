from django.contrib import admin
from django.urls import include, path 

from friend.views import * 
  
app_name = 'friend' 

urlpatterns = [
    path('friend_list/<str:username>', FriendListView.as_view(), name='friend_list'),
    
    path('friend_request_list/<str:username>/', FriendRequestView.as_view(), name='friend_request_list'),
    
    path('friend_request_send/', SendFriendRequest.as_view(), name='send_friend_request'),

    path('friend_request_accept/', AcceptFriendRequest.as_view(), name='accept_friend_request'),
    
    path('friend_request_decline/', RejectFriendRequest.as_view(), name='reject_friend_request'),
    
    path('friend_request_cancel/', CancelFriendRequest.as_view(), name='cancel_friend_request'),


]  