from django.shortcuts import render, redirect 
from django.http import JsonResponse
from django.contrib import messages

from django.views.generic import *
from django.contrib.auth.mixins import LoginRequiredMixin

from account.models import UserProfile
from friend.models import *
from account.helpers import *


class FriendListView(LoginRequiredMixin, View):
    model = User
    template_name = 'friend/friend_list.html'
    paginate_by = 5
 
    def get(self, request, **kwargs):
        current_user = request.user
        context = {}

        # get username from param
        username = kwargs.get("username")
        # get user profile from username 
        user_to_get = User.objects.get(username=username) 

        if user_to_get:
            # check if they are friends 
            is_friend = current_user.profile.is_friend(user_to_get)
            # check if user to search for is current user
            is_current_user = is_user(current_user, user_to_get)

            if not is_current_user and not is_friend:
                messages.error(request, 'Not permitted to view friends list. \
                               Add friend first.') 
 
            if is_current_user or is_friend:
                # get all friends from profile of user_to_get 
                friends_list = user_to_get.profile.friends.all()
                context['friends_list'] = friends_list
                context['user'] = user_to_get

            context['is_current_user'] = is_current_user
            context['is_friend'] = is_friend
            
            
        return render(request, "friend/friend_list.html", context)

class FriendRequestView(LoginRequiredMixin, ListView):
    template_name = 'friend/friend_requests.html'
    paginate_by = 5

    def get(self, request, **kwargs):
        """
        Returns a list of friend requests of current user
        """
      
        user = request.user  
        context = {}  
        # get username from param
        username = kwargs.get("username")
        # get user profile from username
        user_to_get = UserProfile.objects.get(user__username=username)
        
        # additional measure to prevent accessing other users' friend requests from url
        if user_to_get.user == user:
            # retrieve friend requests sent by curent user
            sent_requests = FriendRequest.objects.filter(from_user=user, is_active=True)
            if sent_requests.exists():
                context['sent_requests'] = sent_requests
                context['request_status'] = 1
            
            # retrieve friend requests received by curent user
            received_requests = FriendRequest.objects.filter(to_user=user, is_active=True)
            if received_requests.exists():
                context['received_requests'] = received_requests
                context['request_status'] = 2

            return render(request, self.template_name, context)
        
        else:
            messages.error(request, "Not permitted to view.")
    


class SendFriendRequest(LoginRequiredMixin, View):
    model = User
    template_name = 'friend/friend_requests.html'

    def post(self, request, **kwargs):
        """
        Creates new friend request if does not already exist. 
        """
        user = request.user
        to_username = request.POST.get("receiver_username")
        context = {}

        if to_username:
            is_friend = UserProfile.objects.get(user__username=user.username).is_friend(to_username) 

            # if not friends, check if friend request has already been sent
            if not is_friend:
                receiver = User.objects.get(username=to_username)
                success_response = "Success! Friend request sent."
                try:
                    # get all friend requests 
                    friend_requests = FriendRequest.objects.filter(from_user=user, to_user=receiver)
                    try:
                        # check if user has already sent friend requests through active requests
                        for request in friend_requests:
                            if request.is_active:
                                raise Exception("Friend request has already been sent.")
                        # otherwise create a new friend request
                        friend_request = FriendRequest(from_user=user, to_user=receiver)
                        friend_request.save() 
                        context['response'] = success_response
                    except Exception as e:
                        context['response'] = str(e)
                except FriendRequest.DoesNotExist:
                    # create new request if it does not exist
                    friend_request = FriendRequest(from_user=user, to_user=receiver)
                    friend_request.save()
                    context['response'] = success_response
        else:
            context['response'] = "Unable to send friend request. Please check the entered username and try again."

        return JsonResponse(context) 


class AcceptFriendRequest(LoginRequiredMixin, View):
    model = User
    template_name = 'friend/friend_requests.html'
    
    def post(self, request, **kwargs):
        """
        Once accepted, add to the friends list of both sending and receiving users 
        and resolve active request. 
        """

        user = request.user
        friend_request_id = request.POST.get("request_id") 
        context = {}

        if friend_request_id:
            friend_request = FriendRequest.objects.get(id=friend_request_id)

            if friend_request.to_user == user:
                if friend_request is not None: 
                    # accept friend request if request exists
                    friend_request.accept_request()
                    context['response'] = "Friend request accepted."
                else:
                    context['response'] = "An error occured. Please try again."
            else:
                context['response'] = "Unable to accept request that was not sent to you."
        else:
            context['response'] = "Unable to accept friend request as request does not exist."
        
        return JsonResponse(context)

   
class RejectFriendRequest(LoginRequiredMixin, View):
    model = User
    template_name = 'friend/friend_requests.html'
    
    def post(self, request, **kwargs):
        user = request.user
        context = {}

        friend_request_id = request.POST.get("request_id") 

        if friend_request_id:
            friend_request = FriendRequest.objects.get(id=friend_request_id)

            if friend_request.to_user == user:
                friend_request.reject_request()
                context['response'] = "Friend request successfully declined."
            else:
                context['response'] = "Unable to decline friend request that was not sent to you."
        else:
            context['response'] = "Unable to decline friend request as request does not exist."

    
        return JsonResponse(context)


class CancelFriendRequest(LoginRequiredMixin, View):
    model = User
    template_name = 'friend/friend_requests.html'
    
    def post(self, request, **kwargs):
        user = request.user
        context = {}
            
        friend_request_id = request.POST.get("request_id")
        try:
            friend_request = FriendRequest.objects.get(id=friend_request_id)
        except FriendRequest.DoesNotExist:
            context['response'] = "Unable to cancel friend request as request does not exist."

        if FriendRequest.objects.filter(id=friend_request_id).exists():
            if friend_request.from_user == user and friend_request.is_active:
                friend_request.cancel_request()
                context['response'] = "Friend request cancelled."
            else:
                context['response'] = "Unable to cancel friend request that was not sent to you."
        
        
        return JsonResponse(context)