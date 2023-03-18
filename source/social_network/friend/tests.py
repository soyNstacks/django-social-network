from django.test import TestCase, Client
from django.contrib.auth.models import User 
from django.contrib.auth import SESSION_KEY
from account.models import UserProfile, Post

from django.urls import reverse

