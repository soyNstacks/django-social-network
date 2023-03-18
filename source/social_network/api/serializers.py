from django.contrib.auth.models import User
from rest_framework import serializers, fields
from account.models import *
from friend.models import *
from chat.models import *

class UserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'id', 'date_joined', 'last_login')
        read_only_fields = ('id', 'date_joined', 'last_login')

class UserProfileSerializer(serializers.ModelSerializer):
      
    user = UserSerializer(required=True)
    friends = UserSerializer(many=True, read_only=True)
    date_of_birth = fields.DateField(required=True)

    class Meta:
        model = UserProfile
        fields = ('user', 'date_of_birth', 'profile_picture', 'friends') 
    
    def create(self, validated_data):

        # create user 
        user = User.objects.create(
            username=validated_data['user']['username'],
            first_name=validated_data['user']['first_name'],
            last_name=validated_data['user']['last_name'],
            email=validated_data['user']['email'],
        )

        # create profile
        profile = UserProfile.objects.create( 
            user=user,
            date_of_birth=validated_data['date_of_birth'],
            profile_picture=validated_data['profile_picture'],
        )

        # return created object  
        return profile
 

class PostSerializer(serializers.ModelSerializer):

    # author = UserSerializer(required=True)
    
    class Meta:
        model = Post
        fields = ('author', 'body_text', 'media', 'media_type', 'created_date',)
        read_only_fields = ('media_type', 'created_date',)

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['author'] = UserSerializer(instance.author).data
        return response

    def create(self, validated_data):
 
        # create post 
        post = Post.objects.create(
            author = validated_data['author'],
            body_text = validated_data['body_text'],
            media = validated_data['media'],
        )

        return post


class FriendSerializer(serializers.ModelSerializer):
    
    friends = UserSerializer(many=True, read_only=True)

    class Meta:
        model = UserProfile
        fields = ('friends',)
        
class ChatRoomSerializer(serializers.ModelSerializer):

    users = serializers.StringRelatedField(many=True)

    class Meta:
        model = ChatRoom
        fields = ('room_name', 'users',)


class ChatMessageSerializer(serializers.ModelSerializer): 
    room = ChatRoomSerializer(read_only=True)

    class Meta:
        model = ChatMessage
        fields = ('room', 'timestamp', 'sender', 'content',)