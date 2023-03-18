from django.contrib.auth.models import User
from .models import *

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.exceptions import StopConsumer
from django.db.models import F
from django.utils import timezone
from channels.db import database_sync_to_async
import json
from uuid import uuid4
from django.core.files.base import ContentFile
import base64
 

class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        # Get room name
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        # Create group for group chat
        self.room_group_name = 'chat_%s' % self.room_name
        # Get current user object
        self.user = self.scope["user"]
        self.username = self.scope["user"].username
        # Create group for private chat 
        self.private_chat_name = f'private_{self.user.username}'
        
        # Get room, or create or add user if does not exist
        await self.get_room(self.room_name, self.user)

        # Join multi-user chat room
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        # Join private chat 
        await self.channel_layer.group_add(
            self.private_chat_name,
            self.channel_name
        )

        await self.accept()

        # inform the entrance in the group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_join',
                'username': self.username,
            }
        )

    async def disconnect(self, close_code):
        print("Closed connection to: ", str(self.room_name))
        
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        # Leave private room 
        await self.channel_layer.group_discard(
            self.private_chat_name,
            self.channel_name
        )

        # inform the departure in the group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_leave',
                'username': self.username,
            }
        )

        raise StopConsumer()

    # Receive message from WebSocket
    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        image = text_data_json.get('image', None)
        message = text_data_json.get('message', None)
        self.username = self.scope['user'].username

        if not self.user.is_authenticated: 
            return 

        # Get room 
        room = await self.get_room(self.room_name, self.user)


        if message.startswith('/private '):
            split = message.split(' ', 2)
            target = split[1]
            target_content = split[2]

            # Send private message to target user
            await self.channel_layer.group_send(
                f'private_{target}',
                {
                    'type': 'private_message',
                    'message': target_content,
                    'username': self.username,
                }
            )

            # Send private message delivered to target user
            await self.send(json.dumps({
                'type': 'private_message_delivered',
                'target': target,
                'message': target_content,
            }))

        
        if message == "permanent_exit":
            await self.exit_room(self.room_name, self.user)
            return await self.close()
        else:
            if image is not None:
                
                # decode base64 
                img_decoded = await self.decode_base64(image)

                if img_decoded:
                
                    # Send message to room group
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'chat_image',
                            'image': image,
                            'message': message,
                            'username': self.username,
                        }
                    )   

                    # save new message to database
                    await self.save_new_image(room, self.user, img_decoded, message)  
            else:
                # Send message to room group
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message': message,
                        'username': self.username,
                    }
                )

                # save new message to database
                await self.save_new_message(room, self.user, message)
            
    
    # Receive message from group chat
    async def chat_message(self, event):
        message = event.get('message', None)
        username = event['username']
  
        if message != "permanent_exit":
            # Send message to WebSocket
            await self.send(text_data=json.dumps({
                'type': 'chat_message',
                'message': message,
                'username': username 
            }))


    async def chat_image(self, event):
        message = event.get('message', None)
        image = event.get('image', None)
        username = event['username']

        if image is not None:
            # Send message to WebSocket
            await self.send(text_data=json.dumps({
                'type': 'chat_image',
                'image': image,
                'message': message,
                'username': username 
            }))


    async def user_join(self, event):
        await self.send(text_data=json.dumps(event))

    async def user_leave(self, event):
        await self.send(text_data=json.dumps(event)) 
        
    # source: https://stackoverflow.com/questions/65489550/are-there-any-clever-ways-to-save-files-with-web-socket-in-django
    async def decode_base64(self, str_base64):
        
        format, imgstr = str_base64.split(';base64,') 
        file_extension = format.split('/')[-1]
        return ContentFile(base64.b64decode(imgstr), 
                           name=uuid4().hex + "." + file_extension)
 
    @database_sync_to_async
    def get_room(self, room_name, user):
        # get or create room
        room = ChatRoom.objects.filter(room_name=room_name)
        
        # source: https://stackoverflow.com/questions/72325644/django-direct-assignment-to-the-forward-side-of-a-many-to-many-set-is-prohibite

        # check if room exists
        if not room.exists(): 
            # create new room and add user to the room
            new_room = ChatRoom(
                room_name=room_name
            )
            new_room.save()

        room.first().join_room(user)
        qs = ChatRoom.objects.filter(room_name=room_name, users=user)

        return qs.first()

    @database_sync_to_async
    def exit_room(self, room_name, user):
        # get room 
        room = ChatRoom.objects.get(room_name=room_name)
        room.leave_room(user)

        return
        
    @database_sync_to_async
    def save_new_message(self, room, user, message):

        # create new entry
        new_message = ChatMessage(sender=user, 
                            room=room, 
                            content=message)
        new_message.save()
        return new_message
    
    # source: https://github.com/django/channels/issues/1920
    @database_sync_to_async
    def save_new_image (self, room, user, decoded_image, message):
        message = ChatMessage(sender=user, 
                              room=room, 
                              content=message,
                              image=decoded_image)
        message.save()

        return message