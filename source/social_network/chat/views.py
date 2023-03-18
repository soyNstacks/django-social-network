from django.shortcuts import render 
from .models import *

from django.views.generic import *
from django.contrib.auth.mixins import LoginRequiredMixin

import logging

logger = logging.getLogger(__name__)

class ChatRoomListView(LoginRequiredMixin, ListView):
    model = ChatRoom
    template_name = 'chat/chatroom_list.html' 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        
        rooms = ChatRoom.objects.filter(users=self.request.user).distinct() 
        room_name_list = []
        latest_message_list = [] 
        num_online_members = []
         
        if rooms.exists():
            for room in rooms:
                room_name_list.append(room.room_name)
                num_online_members.append(len(room.online_members()))

                # get most recently sent message in each room
                latest_message = ChatMessage.objects.by_timestamp(room).first()
                latest_message_list.append(latest_message)

        # zip to make key-value pair of str(room_name), num_members, num_active_users, list(latest_messages)
        context['rooms_messages'] = zip(room_name_list, 
                                        num_online_members,
                                        latest_message_list)
        
        friends_list = self.request.user.profile.get_friends() 
        context['friends_list'] = friends_list
        
        return context


class ChatRoomView(LoginRequiredMixin, View):
    template_name = 'chat/chatroom.html'
    # model = ChatMessage

    def get(self, request, room_name):
        
        room = ChatRoom.objects.filter(room_name=room_name).first()
        messages = []
        context = {}

        if room:
            messages = ChatMessage.objects.by_timestamp(room=room).reverse()
            num_members = room.num_members

            context['num_members'] = num_members
            context['online_members'] = room.online_members()

            if request.user in room.users.all():
                context['messages'] = messages

        context['room_name'] = room_name
        context['current_user'] = request.user.username

        return render(request, 'chat/chatroom.html', context)
  