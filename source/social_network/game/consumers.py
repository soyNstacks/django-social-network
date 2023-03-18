from django.contrib.auth.models import User
from .models import *
from django.db.models import Count

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
import json 


class GameConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        
        self.room_name = self.scope['url_route']['kwargs']['player_name']
        self.user = self.scope["user"]
        self.game_room_name = f'game_{self.room_name}_{self.user.username}'
        self.user_left =' '
        
        await self.get_room(self.game_room_name, self.room_name, self.user)

        # Join room 
        await self.channel_layer.group_add(
            self.game_room_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        print("Closed connection to: ", str(self.game_room_name))
                
        # Leave room 
        await self.channel_layer.group_discard(
            self.game_room_name,
            self.channel_name
        )

        await self.exit_room(self.game_room_name, self.user)

    # Receive message from WebSocket
    async def receive(self, text_data):
        data_json = json.loads(text_data)
        user = self.scope['user']
        event = data_json.get("event", None)
        message = data_json.get("message", None)
 
        if event == 'MOVE':
            # Send message to room group
            await self.channel_layer.group_send(
                self.game_room_name, {
                'type': 'send_message',
                "event": "MOVE"
            })

        if event == 'START':
            # Send message to room group
            await self.channel_layer.group_send(
                self.game_room_name, {
                'type': 'send_message',
                'event': "START"
            })

        if event == 'END':
            # Send message to room group
            await self.channel_layer.group_send(
                self.game_room_name, {
                'type': 'send_message',
                'message': message,
                'event': "END"
            })


    # Receive message from group chat
    async def send_message(self, res):

        await self.send(text_data=json.dumps({
            "payload": res,
        }))
    
    @database_sync_to_async
    def get_room(self, game_room_name, opponent_username, user):
        # get User of opponent
        opponent_user = User.objects.get(username=opponent_username)
        
        # get or create room
        rooms = GameRoom.objects.filter(room_name=game_room_name, is_active=True).all()
        qs = rooms.annotate(count=Count('users')).filter(users=user)\
                                                            .filter(users=opponent_user)\
                                                            .filter(count=2)
        
        # source: https://stackoverflow.com/questions/72325644/django-direct-assignment-to-the-forward-side-of-a-many-to-many-set-is-prohibite
        # check if room exists
        if not qs.exists(): 
            # create new room and add user to the room
            new_room = GameRoom(
                room_name=game_room_name
            )
            new_room.save()

        rooms.first().join_game(opponent_user)
        rooms.first().join_game(user)

        qs = rooms.annotate(count=Count('users')).filter(users=user)\
                                                            .filter(users=opponent_user)\
                                                            .filter(count=2)

        return qs.first()
    
    @database_sync_to_async
    def exit_room(self, game_room_name, user):
        # get room 
        room = GameRoom.objects.get(room_name=game_room_name, is_active=True)
        room.end_game(user)

        return