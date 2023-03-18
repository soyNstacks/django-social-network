from django.test import TestCase, Client
from django.contrib.auth.models import User 
from account.models import UserProfile, Post

from django.urls import reverse
from datetime import date


class RegistrationTestCase(TestCase):
    """
    Tests for user account creation process.
    """
    def setUp(self):
        self.client = Client()
        self.credentials = {
            'username': 'testusername1',
            'first_name': 'firstname',
            'last_name': 'lastname',
            'password1': '123secretpassword',
            'password2': '123secretpassword',
            'date_of_birth': date(1998, 2, 20),
            'email': 'testuser@test.com'
        }


    def test_signup(self):
        response = self.client.post(reverse('register'), 
                                    data=self.credentials)
        # check success status code
        self.assertEqual(response.status_code, 302)

        # retreive created user object
        user = User.objects.get(username=self.credentials['username'])
        # check email data was accurate
        self.assertEqual(user.email, self.credentials['email'])
        # check date_of_birth data was accurate
        self.assertEqual(user.profile.date_of_birth,  '1998-02-20')
        # check first_name, last_name data were accurate
        self.assertEqual(user.first_name,  self.credentials['first_name'])
        self.assertEqual(user.last_name,  self.credentials['last_name'])


class LoginTestCase(TestCase):
    """
    Tests for user login process.
    """
    def setUp(self):
        self.client = Client()
        self.credentials = {
            'username': 'testusername',
            'password': 'secretpassword',
            'date_of_birth': date(1998, 2, 20),
            'email': 'testuser@test.com'
        }

        User.objects.create_user(username=self.credentials['username'], 
                                 password=self.credentials['password'], 
                                 email=self.credentials['email'])
        self.user = User.objects.filter(username=self.credentials['username']).first()
        UserProfile.objects.create(user=self.user, 
                                   date_of_birth=self.credentials['date_of_birth'])

    def test_success_username_login(self):
        # Send credential data for login process
        response = self.client.post(reverse('login'), 
                                    data={'username': self.credentials['username'],
                                          'password': self.credentials['password']})
        # Check if user was redirected to home page after successful login
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/home')
        
    def test_success_email_login(self):
        # Send credential data for login process
        response = self.client.post(reverse('login'), 
                                    data={'username': self.credentials['email'],
                                          'password': self.credentials['password']})
        # Check if user was redirected to home page after successful login
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/home')

class UserProfileTestCase(TestCase):
    """
    Tests for user profile details after login.
    """
    def setUp(self):
        self.client = Client()
        self.credentials = {
            'username': 'testusername',
            'password': 'secretpassword',
            'date_of_birth': date(1998, 2, 20),
            'email': 'testuser@test.com'
        }

        User.objects.create_user(username=self.credentials['username'], 
                                 password=self.credentials['password'], 
                                 email=self.credentials['email'])
        self.user = User.objects.filter(username=self.credentials['username']).first()
        UserProfile.objects.create(user=self.user, 
                                   date_of_birth=self.credentials['date_of_birth'])

    def test_return_profile(self):
        # Send credential data for login process
        self.client.post(reverse('login'), data={
            'username': self.credentials['username'],
            'password': self.credentials['password']
        })
 
        # Get to profile page of currently logged user
        response = self.client.get(reverse('account:profile', 
                                           kwargs={'username': self.credentials['username']}))
        # Check status code for whether profile indeed exists 
        self.assertEqual(response.status_code, 200)
        # Check correct template was rendered
        self.assertTemplateUsed(response, 'account/profile.html')

    def test_password_change_url(self):
        # Send credential data for login process
        self.client.post(reverse('login'), data={
            'username': self.credentials['username'],
            'password': self.credentials['password']
        })

        # Get to profile page of logged in user
        response = self.client.post(reverse('account:password-change'),
                                    data={
                                        'password1': 'secretpassword123',
                                        'password2': 'secretpassword123'
                                    })
        
        # Check status code 
        self.assertEqual(response.status_code, 200)
        # Check correct template was rendered
        self.assertTemplateUsed(response, 'account/password_change.html')

        
class AccountSearchTestCase(TestCase):
    """
    Tests for correct user search result after login.
    """
    def setUp(self):
        self.client = Client()
        self.credentials = [{
            'username': 'testusername',
            'password': 'secretpassword',
            'date_of_birth': date(1998, 2, 20),
            'email': 'testuser@test.com'
        },
        {
            'username': 'testusername2',
            'password': 'secretpassword',
            'date_of_birth': date(1998, 2, 20),
            'email': 'testuser2@test.com'
        }]

        for user in self.credentials:
            User.objects.create_user(username=user['username'], 
                                    password=user['password'], 
                                    email=user['email'])
        
            UserProfile.objects.create(user=User.objects.filter(username=user['username']).first(), 
                                        date_of_birth=user['date_of_birth'])

    def test_success_search_account(self):
        # Send user1's account data for login process
        self.client.post(reverse('login'), data={
            'username': self.credentials[0]['username'],
            'password': self.credentials[0]['password']
        })

        response = self.client.get(reverse('account:search-profile'), 
                                   {'q': self.credentials[1]['username']})
        
        # retrieve user object from response
        user = response.context['user_list'][0]
        # Check if search result equal user2's username
        self.assertEqual(user.username, self.credentials[1]['username'])
        # Check status code 
        self.assertEqual(response.status_code, 200)
        # Check correct template was rendered
        self.assertTemplateUsed(response, 'account/search_users.html')
        
    def test_failed_search_account(self):
        # Send user1's account data for login process
        self.client.post(reverse('login'), data={
            'username': self.credentials[0]['username'],
            'password': self.credentials[0]['password']
        })

        response = self.client.get(reverse('account:search-profile'), 
                                   {'q': 'username doesnotexist'})
        
        # retrieve number of results from response
        num_result = response.context['user_count']

        # Check that zero existing results was returned
        self.assertEqual(num_result, 0)
        # Check status code 
        self.assertEqual(response.status_code, 200)
        # Check correct template was rendered
        self.assertTemplateUsed(response, 'account/search_users.html')


class PostTestCase(TestCase):
    """
    Tests for new post after login.
    """
    def setUp(self):
        self.client = Client()
        self.credentials = {
            'username': 'testusername',
            'password': 'secretpassword',
            'date_of_birth': date(1998, 2, 20),
            'email': 'testuser@test.com'
        }

        User.objects.create_user(username=self.credentials['username'], 
                                 password=self.credentials['password'], 
                                 email=self.credentials['email'])
        self.user = User.objects.filter(username=self.credentials['username']).first()
        UserProfile.objects.create(user=self.user, 
                                   date_of_birth=self.credentials['date_of_birth'])
        
        self.post = {
            'body_text': 'random caption',
            'author': self.user 
        }
        

    def test_post_create(self):
        # Send credential data for login process
        self.client.post(reverse('login'), data={
            'username': self.credentials['username'],
            'password': self.credentials['password']
        })

        # Get to profile page of logged in user
        response = self.client.post(reverse('home'), 
                                            data=self.post)
        
        # Check status code 
        self.assertEqual(response.status_code, 302)
        # Check if reloaded at home feed page
        self.assertEqual(response.url, '/home/')
        
        
    def test_post_details(self):
        # Send credential data for login process
        self.client.post(reverse('login'), data={
            'username': self.credentials['username'],
            'password': self.credentials['password']
        })


        Post.objects.create(author=self.post['author'],
                            body_text=self.post['body_text'])
        
        # Get to profile page of logged in user
        response = self.client.get(reverse('home'))
        resp_post = response.context['posts'].first()
        
        # Check status code 
        self.assertEqual(response.status_code, 200)
        # Check correct template was rendered
        self.assertTemplateUsed(response, 'social_network/home.html')
        # Check body_text is correct 
        self.assertEqual(resp_post.body_text, self.post['body_text'])
        # Check author is correct 
        self.assertEqual(resp_post.author, self.post['author'])