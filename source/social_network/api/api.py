from django.shortcuts import render
from .serializers import *
from rest_framework import generics, mixins
from account.models import UserProfile
from api.permissions import *
from rest_framework.permissions import IsAdminUser, IsAuthenticated

RETRIEVAL_PERMISSION_CLASSES = (IsCurrentUserRetrieval | IsAdminUser | IsSuperUser,)
LIST_PERMISSION_CLASSES = (IsCurrentUser | IsAdminUser | IsSuperUser,)
RESTRICTED_PERMISSION_CLASSES = (IsSuperUser | IsAdminUser,)


class ListUsers(generics.ListAPIView):
    """
    GET method to return list of all user accounts 
    """  
    queryset = User.objects.all().distinct()
    serializer_class = UserSerializer
    permission_classes = RESTRICTED_PERMISSION_CLASSES


class RetrieveAccountDetails(generics.RetrieveAPIView):
    """
    GET method to retrieve details of user account details with queried username
    """

    lookup_field = 'user__username'
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = RETRIEVAL_PERMISSION_CLASSES


class CreateAccount(mixins.CreateModelMixin, generics.GenericAPIView):
    """
    POST method to create new user account.  
    """

    # query to get all 
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = RESTRICTED_PERMISSION_CLASSES

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
    

class ListUserPosts(generics.ListAPIView):
    """
    GET method to return list of posts of queried username
    """
    queryset = Post.objects.all().distinct()
    serializer_class = PostSerializer
    permission_classes = RETRIEVAL_PERMISSION_CLASSES

    def filter_queryset(self, queryset):
        return queryset.filter(author__username=self.kwargs.get('user__username'))
    

class CreateUserPost(generics.CreateAPIView):
    """
    POST method to create new post
    """

    serializer_class = PostSerializer
    permission_classes = (IsCurrentUser, )

    
class RetrieveFriendsDetails(generics.RetrieveAPIView):
    """
    GET method to retrieve details about friends through queried username
    """
    lookup_field = 'user__username'
    queryset = UserProfile.objects.all()
    serializer_class = FriendSerializer
    permission_classes = RETRIEVAL_PERMISSION_CLASSES

 
class ChatRoomDetails(mixins.RetrieveModelMixin, generics.GenericAPIView): 
    """
    GET method to retrieve details about chatroom
    """
    lookup_field = 'room_name'
    queryset = ChatRoom.objects.all()
    serializer_class = ChatRoomSerializer
    permission_classes = RETRIEVAL_PERMISSION_CLASSES
    
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
 