from .models import *
from friend.models import FriendRequest
from django.http import Http404
    
def is_user(current_user, user_to_get):
    """
    Checks if user to get is the currently logged user. 
    Returns True if is current user, else False.
    """
    if user_to_get != current_user:
        return False
    elif user_to_get == current_user:
        return True


def has_friend_request(from_user, to_user):
    """
    Checks if friend request exists. 
    Returns True if it exists, else False.
    """
    try:
        return FriendRequest.objects.get(from_user=from_user, to_user=to_user, is_active=True)
    except FriendRequest.DoesNotExist:
        return False 
    
def has_user_profile_context(user):
    """
    Checks if user logging in has user profile. 
    Note: only superusers may not have a user profile if created through djange create superuser
    """
    try:
        UserProfile.objects.filter(user__profile=user.profile).first()
        return 0 # passes, has profile
    except UserProfile.DoesNotExist:
        if user.is_superuser: 
            return 1 # passes, is a super user
        else: 
            return 2 # fails, raise error