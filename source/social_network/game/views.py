from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from .models import *
from friend.models import FriendRequest

from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.db.models.query_utils import Q
from django.db.models.functions import Concat 
from django.db.models import Value as V

from django.views.generic import *
from django.views.generic.edit import FormMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin

import random
import logging

logger = logging.getLogger(__name__)

  
class CreateGameRoomView(LoginRequiredMixin, View):
    template_name = 'game/create_game.html'

    def get(self, request):
        context = {}
        # Get user's list of friends
        context['friends_list'] = request.user.profile.get_friends()

        return render(request, self.template_name, context)
     
    def post(self, request, *args, **kwargs):
        player_name = request.POST.get("player_name")
        char_choice = request.POST.get("character_choice")

        return redirect(
            '/game/%s?&choice=%s' 
            %(player_name, char_choice)
        )
     

class GameView(LoginRequiredMixin, View):
    template_name = 'game/game.html'

    def get(self, request, player_name):
        choice = request.GET.get("choice")

        if choice not in ['X', 'O']:
            raise Http404("Choice does not exist")
        
        context = {
            "char_choice": choice, 
            "player_name": player_name
        }

        return render(request, self.template_name, context)  
    
# source: https://github.com/krazygaurav/Django-channels-Tic-Tac-Toe/blob/main/static/js/game.js