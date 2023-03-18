from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from friend.models import FriendRequest
from .forms import *
from .helpers import *

from django.contrib import messages
from django.db.models.query_utils import Q

from django.views.generic import *
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

import logging

logger = logging.getLogger(__name__) 


class ProfileView(LoginRequiredMixin, DetailView):
    model = UserProfile
    login_url = 'login'
    template_name = 'account/profile.html'

    def get(self, request, *args, **kwargs): 
        context = {}

        username = kwargs.get("username")
        # get currently logged user
        current_user = request.user 

        # get user and profile from username 
        profile_to_get = UserProfile.objects.get(user__username=username)
        user_to_get = profile_to_get.user
        
        if user_to_get:
            is_friend = profile_to_get.is_friend(current_user) 
            
            # retrieve friends list
            friends_list = profile_to_get.get_friends()

            # check if is currently logged user
            is_current_user = is_user(current_user, user_to_get)
            
            if not is_friend and not is_current_user:
                # check if there exists a friend reequest between user_to_get and current_user
                has_sent_request = has_friend_request(current_user, user_to_get)
                has_received_request = has_friend_request(user_to_get, current_user)
                
                if has_sent_request: 
                    # current_user had sent user_to_get a request
                    friend_request_sent =  FriendRequest.objects.get(from_user=current_user, to_user=user_to_get, is_active=True)
                    context['request_status'] = 1 
                    context['friend_request_id'] = friend_request_sent.id

                elif has_received_request:
                    # user_to_get had sent current_user a request
                    friend_request_received = FriendRequest.objects.get(from_user=user_to_get, to_user=current_user, is_active=True)
                    context['request_status'] = 2
                    context['friend_request_id'] = friend_request_received.id

                else: 
                    context['request_status'] = 0

            # display confidential info if is_friend or is_current_user
            if is_friend or is_current_user: 
                context['posts'] = Post.objects.filter(author=user_to_get).all()

            # for public view
            context['user_to_get'] = user_to_get
            context['num_friends'] = friends_list.count()

            context['is_current_user'] = is_current_user 
            context['is_friend'] = is_friend
            
        return render(request, self.template_name, context)
    

class UserSearchView(LoginRequiredMixin, ListView):
    model = User
    paginate_by = 10
    template_name = 'account/search_users.html'

    def get_context_data(self, *args, **kwargs):
        context = super(UserSearchView, self).get_context_data(**kwargs)
        
        user_query = self.request.GET.get('q')
        if user_query:
            user_list = User.objects.filter(
                Q(username__icontains=user_query.strip())|
                Q(first_name__icontains=user_query.strip())|
                Q(last_name__icontains=user_query.strip())
            ).order_by('-last_login')
            
            user_count = user_list.count()
            context['user_list'] = user_list
            context['user_count'] = user_count

        return context
 
 
class EditProfileView(LoginRequiredMixin, UpdateView):
    template_name = 'account/profile_edit.html'
    
    def get(self, request, *args, **kwargs):
        user = request.user
        
        profile = get_object_or_404(UserProfile, user=user)

        user_form = EditUserForm(request.POST or None,
                            request.FILES or None, 
                            instance=user)
        add_form = UserExtraFieldsForm(request.POST or None,
                            request.FILES or None, 
                            instance=profile)

        context = {
            'user_form': user_form,
            'add_form': add_form,
            'profile': profile
        }

        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        user = request.user
        profile = get_object_or_404(UserProfile, user=user)

        user_form = EditUserForm(request.POST, instance=user)
        add_form = UserExtraFieldsForm(request.POST, request.FILES, instance=profile)
    
        if user_form.is_valid() and add_form.is_valid():
            user_form.save()
            add_form.save()

            username = kwargs.get("username") 

            messages.success(request, "Profile updated!")
            return redirect('/home')
        else:
            messages.add_message(request, messages.ERROR, "Please check again.")
 
        context = {
            'user_form': user_form,
            'add_form': add_form,
        }

        return render(request, self.template_name, context)


class ChangePasswordView(LoginRequiredMixin, UpdateView):
    template_name = 'account/password_change.html'
    
    def get(self, request, *args, **kwargs):
        user = request.user
          
        user_form = UserCreationForm(request.POST or None,
                            request.FILES or None, 
                            instance=user)

        context = {
            'user_form': user_form,
            'user': user
        }

        return render(request, self.template_name, context)
    
    def post(self, request):
        user = request.user
   
        user_form = UserCreationForm(request.POST, instance=user)
    
        if user_form.is_valid():
            user_form.save()

            messages.success(request, "Password successfuly changed.")
            return redirect('/home')
        else:
            messages.error(request, "Please check again.")
 
        context = {
            'user_form': user_form,
            'user': user
        }

        return render(request, self.template_name, context)
