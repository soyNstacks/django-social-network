from django.urls import path

from .views import *

app_name = 'chat'


urlpatterns = [
    # Path to list of chat rooms
    path('chat_room_list/', ChatRoomListView.as_view(), name='chatroom_list'),
    # Path to a chat room 
    path('<str:room_name>/', ChatRoomView.as_view(), name='chat_room'),    

]
  
