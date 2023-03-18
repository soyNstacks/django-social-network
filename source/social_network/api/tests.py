from django.contrib.auth.models import User
from account.models import UserProfile, Post
from .model_factories import *

import json
from rest_framework.test import APITestCase, APIClient
from .serializers import *
from django.urls import reverse


class AccountsGetListTest(APITestCase):
    """
    Test: GET method to return list of all user accounts 
    """

    # Initialise variables to use
    users = None
    good_url = ''

    def setUp(self):
        self.client = APIClient()
        # Instantiate factory and serializer objects to create object
        self.users = UserProfileFactory.create_batch(2)
        self.users[0].user.is_superuser = True
        self.users[0].user.is_staff = True

        # Set a good url
        self.good_url = reverse('api:account_list_api')

    def tearDown(self):

        # Reset test tables
        UserProfile.objects.all().delete()
        User.objects.all().delete()

        # Reset all primary keys to 0 
        UserFactory.reset_sequence(0)
        UserProfileFactory.reset_sequence(0)

    def test_account_return_success(self):
        # force login authentication for superuser user1
        self.client.force_authenticate(self.users[0].user)
        response = self.client.get(self.good_url, format='json')
        response.render()
        # Check that status code 200 is returned
        self.assertEqual(response.status_code, 200)

    def test_account_return_fail_on_not_permitted(self):
        # force login authentication for non-superuser user2
        self.client.force_authenticate(self.users[1].user)
        response = self.client.get(self.good_url, format='json')
        response.render()
        # Check that status code 403 forbidden is returned
        self.assertEqual(response.status_code, 403)

    def test_account_return_correct_count(self):
        # force login authentication for superuser user1
        self.client.force_authenticate(self.users[0].user)
        response = self.client.get(self.good_url, format='json')
        response.render()
        data = json.loads(response.content)
        # Check that 2 users were returned in the list
        self.assertEqual(data['count'], 2)
  
    def test_account_return_correct_details(self):
        # force login authentication for superuser user1
        self.client.force_authenticate(self.users[0].user)
        response = self.client.get(self.good_url, format='json')
        response.render()
        results = json.loads(response.content)['results']
        # Check that account details (username, email) returned were correct 
        for i in range(len(results)):
            self.assertEqual(results[i]['username'], self.users[i].user.username)
            self.assertEqual(results[i]['email'], self.users[i].user.email)
            

class AccountRetrieveTest(APITestCase):
    """
    Test: GET method to return details of account by queried username
    """

    # initialise variables to use
    user1 = None
    good_url = ''

    def setUp(self):
        self.client = APIClient()
        # Instantiate factory and serializer objects to create object
        self.user1 = UserProfileFactory.create()
        self.user1.user.is_superuser = True
        self.user1.user.is_staff = True

        # Set a good url
        self.good_url = reverse('api:account_profile_api', 
                                kwargs={'user__username': self.user1.user.username})
 
    def tearDown(self):

        # Reset test tables
        UserProfile.objects.all().delete()
        User.objects.all().delete()

        # Reset all primary keys to 0 
        UserFactory.reset_sequence(0)
        UserProfileFactory.reset_sequence(0)

    def test_account_detail_return_success(self):
        # force login authentication for superuser user1
        self.client.force_authenticate(self.user1.user)
        # Check that status code 200 is returned for valid GET request
        response = self.client.get(self.good_url, format='json')
        response.render()
        self.assertEqual(response.status_code, 200)
            
    def test_account_return_correct_details(self):
        # force login authentication for superuser user1
        self.client.force_authenticate(self.user1.user)
        response = self.client.get(self.good_url, format='json')
        response.render()
        data = json.loads(response.content)['user']
        # Check that account details (username, email) returned were correct 
        self.assertEqual(data['username'], self.user1.user.username)
        self.assertEqual(data['email'], self.user1.user.email)
        
        
class PostsRetrieveListTest(APITestCase):
    """
    Test: GET method to return list of all posts of queried user
    """

    # Initialise variables to use
    users = None
    good_url = ''

    def setUp(self):
        self.client = APIClient()
        # Instantiate factory and serializer objects to create object
        self.user1 = UserProfileFactory.create()
        self.user1.user.is_superuser = True
        self.user1.user.is_staff = True

        self.post1 = PostFactory.create(author=self.user1.user)
        self.post2 = PostFactory.create(author=self.user1.user)

        # Set a good url
        self.good_url = reverse('api:post_list_api', 
                                kwargs={'user__username': self.user1.user.username})

    def tearDown(self):

        # Reset test tables
        UserProfile.objects.all().delete()
        User.objects.all().delete()
        Post.objects.all().delete()

        # Reset all primary keys to 0 
        UserFactory.reset_sequence(0)
        UserProfileFactory.reset_sequence(0)
        PostFactory.reset_sequence(0)

    def test_post_return_success(self):
        # force login authentication for superuser user1
        self.client.force_authenticate(self.user1.user)
        response = self.client.get(self.good_url, format='json')
        response.render()
        # Check that status code 200 is returned
        self.assertEqual(response.status_code, 200)

    def test_post_return_correct_count(self):
        # force login authentication for superuser user1
        self.client.force_authenticate(self.user1.user)
        response = self.client.get(self.good_url, format='json')
        response.render()
        data = json.loads(response.content)
        
        # Check that 2 users were returned in the list
        self.assertEqual(data['count'], 2)

    def test_post_return_correct_details(self):
        # force login authentication for superuser user1
        self.client.force_authenticate(self.user1.user)
        response = self.client.get(self.good_url, format='json')
        response.render()
        results = json.loads(response.content)['results']
        
        # Check that account details (i.e. body_text, username) returned were correct 
        self.assertEqual(results[0]['author']['username'], self.post1.author.username)
        self.assertEqual(results[1]['author']['username'], self.post2.author.username)
        self.assertEqual(results[0]['body_text'], self.post1.body_text)
        self.assertEqual(results[1]['body_text'], self.post2.body_text)
