from django.contrib import admin
from django.urls import include, path 

from .views import * 
from django.contrib.auth.decorators import login_required

app_name = 'game' 

urlpatterns = [
    # Path to game
    path('', CreateGameRoomView.as_view(), name='create_game'),    
    path('<str:player_name>/', GameView.as_view(), name='game_room'), 
] 