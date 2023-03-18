from django.db import models
from django.contrib.auth.models import User

class GameRoom(models.Model):
    room_name = models.CharField(max_length=80, blank=False, null=False)
    users = models.ManyToManyField(User, blank=False)
    is_active = models.BooleanField(null=False, default=True)

    def __str__(self):
        return self.room_name 

    @property
    def num_members(self):
        return self.users.count() 
    
    def join_game(self, user):
        if user not in self.users.all():
            self.users.add(user)
            self.save()

    def end_game(self, user):
        if user in self.users.all() and self.is_active == True:
            self.is_active = False 
            self.save()