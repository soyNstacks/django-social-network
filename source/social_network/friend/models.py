from django.db import models
from django.contrib.auth.models import User
from account.models import UserProfile

class FriendRequest(models.Model):

    from_user = models.ForeignKey(User, on_delete=models.CASCADE, 
                                  related_name='sender')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, 
                                related_name='receiver')
    is_active = models.BooleanField(blank=True, null=False, 
                                    default=True)
    timestamp = models.DateTimeField(auto_now_add=True) 


    def __str__(self):
        return self.from_user.username + " & " + self.to_user.username
    
    def accept_request(self):  
        """
        Accept request and add to both sender and receiver's friends lists
        """

        sender = self.from_user
        receiver = self.to_user
          
        if sender and receiver:
            # add to both lists
            receiver.profile.add_friend(sender)
            sender.profile.add_friend(receiver)
            # resolve friend request
            self.is_active = False
            self.save()

    def reject_request(self):
        """
        Reject and resolve the request without adding to friends list
        """
        self.is_active = False
        self.save()

    def cancel_request(self):
        """
        Cancel and resolve request
        """
        self.is_active = False
        self.save()

