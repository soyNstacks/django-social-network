from social_core.pipeline.partial import partial
from social_core.exceptions import AuthException
from account.models import UserProfile
from django.contrib.auth.models import User
from datetime import date 


@partial
def associate_by_email(backend, details, user=None, *args, **kwargs):
    if user:
        return None

    # Get email 
    email = details.get('email')
    if email:
        # Find and link accounts registered with the same email address
        users = list(backend.strategy.storage.user.get_users_by_email(email))

        active_users = [user for user in users if user.is_active]
        # Check if user with the same email exists
        if len(active_users) == 0:
            return None
        elif len(active_users) > 1:
                raise AuthException(
                    backend,
                    'Account with the same email address already exists.'
                )
        else:
            return {'user': active_users[0],
                    'is_new': False}
        

def create_profile(strategy, details, response, user, *args, **kwargs):
    if UserProfile.objects.filter(user=user).exists(): 
        pass
    else:
        if 'birthday' in response:
            date_of_birth = response.get('birthday')
            
        else:
            date_of_birth = date(1990, 1, 1)
        
        new_profile = UserProfile(user=user, date_of_birth=date_of_birth)
        new_profile.save()
    return kwargs