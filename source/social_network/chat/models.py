from django.db import models
from django.contrib.auth.models import User

 
class ChatRoom(models.Model):
    room_name = models.CharField(max_length=128, 
                                 unique=True, 
                                 blank=False)
    users = models.ManyToManyField(User, blank=True)

    def __str__(self):
        return self.room_name 
 
    @property
    def num_members(self):
        """
        Returns number of members in room
        """
        return self.users.count() 
    
    def online_members(self):
        """
        Returns a list of members who are online 
        """
        online_list = []
        for member in self.users.all(): 
            if member.profile.online: 
                online_list.append(member)
        return online_list
    
    def join_room(self, user):
        """
        Adds user object to room 
        """
        if user not in self.users.all():
            self.users.add(user)
            self.save()

    def leave_room(self, user):
        """
        Removes user object from room 
        """
        if user in self.users.all():
            self.users.remove(user)
            self.save()


class MessageManager(models.Manager):  
 
    def by_timestamp(self, room):
        """
        Returns messages in sequence by timestamp
        """ 
        return ChatMessage.objects.filter(room=room).order_by("-timestamp")
    

class ChatMessage(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, 
                             related_name="room_message")
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True) 
    content = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='chat_uploads/', 
                              blank=True, null=True)
  
    objects = MessageManager()

    def __str__(self):
        return self.content


