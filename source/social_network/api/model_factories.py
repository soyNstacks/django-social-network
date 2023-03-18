from factory.django import DjangoModelFactory
from factory import SubFactory
from django.contrib.auth.models import User
from account.models import UserProfile, Post 
import factory
import factory.fuzzy
from django.contrib.auth.hashers import make_password
from datetime import date

class UserFactory(DjangoModelFactory):
    """
    Factory for User 
    """
    username = factory.fuzzy.FuzzyText(length=10)
    email = factory.Faker('email')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    password = factory.LazyFunction(lambda: make_password('pi3.1415'))

    #is_superuser = True
    #is_staff = True

    class Meta:
        model = User


class UserProfileFactory(DjangoModelFactory):
    """
    Factory for UserProfile 
    """
    user = SubFactory(UserFactory)
    date_of_birth = date(1990, 5, 2)

    class Meta:
        model = UserProfile
  

class PostFactory(DjangoModelFactory):
    """
    Factory for Post 
    """
    # source: https://stackoverflow.com/questions/66381042/how-to-assign-the-attribute-of-subfactory-instead-of-the-subfactory-itself
    author = factory.SelfAttribute("profile.user")
    body_text = factory.Faker("sentence")
    media = factory.Faker("image_url")

    class Meta:
        model = Post

    class Params:
        profile = factory.SubFactory(UserProfileFactory)

    



  