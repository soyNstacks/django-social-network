import os
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from django.core.cache import cache 
from django.conf import settings
from django.core.validators import FileExtensionValidator 
from .backends import ValidateMediaExtensions

   
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, 
                                related_name='profile')
    date_of_birth = models.CharField(blank=False, 
                                     max_length=100)
    profile_picture = models.ImageField(upload_to='profile_pictures/', 
                                        default='profile_pictures/default.jpg')
    created_date = models.DateTimeField(default=timezone.now)
    friends = models.ManyToManyField(User, blank=True, 
                                     related_name='friends_list') 
 
    def __str__(self):  
        return self.user.username
    
    def last_seen(self):
        """
        Returns last seen of user
        """
        return cache.get('seen_%s' % self.user.username)
  
    def online(self):
        if self.last_seen():
            now = timezone.now
            if now > self.last_seen() + timezone.timedelta(
                        seconds=settings.USER_ONLINE_TIMEOUT):
                return False
            else:
                return True
        else:
            return False 
        
    def get_friends(self):
        """
        Returns user's list of friends
        """
        return self.friends.all()
    
    def is_friend(self, friend):
        """
        Check if user is in friends list
        """
        if friend in self.friends.all():
            return True
        return False
    
    
    def add_friend(self, usr):
        """ 
        Add friend if not in friends list
        """ 
        if not usr in self.friends.all():
            self.friends.add(usr)
            self.save()
            
    def remove_friend(self, friend):
        """ 
        Remove friend from friends list
        """ 
        if friend in self.friends.all():
            self.friends.remove(friend)
            self.save()
    
    @property
    def image_url(self):
        """
        Returns url of user's profile picture
        """
        if self.profile_picture and hasattr(self.profile_picture, 'url'):
            return self.profile_picture.url
        

class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_date = models.DateTimeField(default=timezone.now)
    body_text = models.TextField()
    media = models.FileField(upload_to='post_uploads/', null=True,
                        validators=[FileExtensionValidator(
        allowed_extensions=ValidateMediaExtensions.post_media_extensions())])

    def __str__(self):
        return self.author.username
    
    @property 
    def media_url(self):
        """
        Returns url of user's profile picture
        """
        if self.media and hasattr(self.media, 'url'):
            return self.media.url

    @property
    # source: https://stackoverflow.com/questions/61618008/django-audio-video-and-image-upload
    def media_type(self):
        """
        Checks file type from extension; image or video
        """
        if self.media:
            name, extension = os.path.splitext(self.media.name)
            clean_extension = extension.replace('.', '')
            if clean_extension in ValidateMediaExtensions.video_extensions():
                return 'video'
            if clean_extension in ValidateMediaExtensions.image_extensions():
                return 'image'



