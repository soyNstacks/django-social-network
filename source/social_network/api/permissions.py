from rest_framework.permissions import BasePermission
from django.contrib.auth.models import User 

class IsSuperUser(BasePermission):
    """
    Allows access only to superusers.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_superuser)
    
class IsCurrentUser(BasePermission):
    """
    Allows access only if is current user.
    """
    message = 'You must be the owner of this username.'
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return request.user == obj.user
    
      
class IsCurrentUserRetrieval(BasePermission):
    """
    Allows access only if is current user.
    """
    message = 'You must be the owner of this username.'

    def has_permission(self, request, view):
        if request.user.is_superuser or request.user.is_staff:
            return request.user == request.user.is_superuser
        return request.user == User.objects.get(username=view.kwargs['user__username'])
    
    









