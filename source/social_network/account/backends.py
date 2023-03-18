from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

from django.core import validators

# source: https://rahmanfadhil.com/django-login-with-email/
class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(Q(username__iexact=username) 
                                    | Q(email__iexact=username))
        except UserModel.DoesNotExist:
            UserModel().set_password(password)
            return
        except UserModel.MultipleObjectsReturned:
            user = UserModel.objects.filter(Q(username__iexact=username) 
                                       | Q(email__iexact=username)
                                       ).order_by('id').first()

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        

class ValidateMediaExtensions(): 

    def post_media_extensions():
        video_extensions = ['mp4','webm','ogg'] # HTML supported video formats
        unique_extensions = set(video_extensions 
                                + validators.get_available_image_extensions())
        
        return list(unique_extensions)
    
    def video_extensions():
        return ['mp4','webm','ogg'] # HTML supported video formats

    def image_extensions():
        return validators.get_available_image_extensions()
