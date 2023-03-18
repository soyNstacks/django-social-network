from django.shortcuts import render, redirect, get_object_or_404
from account.models import *
from django.contrib.auth.models import User
from account.forms import *
from account.helpers import *

from django.urls import reverse_lazy, reverse
from braces.views import SelectRelatedMixin
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import LoginView
from django.db.models.query_utils import Q

from django.views.generic import *
from django.views.generic.edit import FormMixin
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

import logging
 
logger = logging.getLogger(__name__)


class LandingView(TemplateView):
    """
    Renders landing page for the social network platform.
    """
    template_name = 'social_network/index.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('home')
        else: 
            return render(request, self.template_name)
        

class UserLoginView(LoginView): 
    """
    Renders login page with form. 
    """
    template_name = 'social_network/login.html'
    form_class = LoginForm
    success_url = reverse_lazy('home')
    
    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('home')
        return super(UserLoginView, self).get(*args, **kwargs)
    

class UserRegistrationView(View): 
    """
    Renders user registration form.
    """
    template_name = 'social_network/register.html'
    success_url = reverse_lazy('home')
    registered = False
    
    def post(self, request, *args, **kwargs):
        registered = self.registered
        
        user_form = UserRegistrationForm(data=request.POST, files=request.FILES)
        add_form = UserExtraFieldsForm(data=request.POST, files=request.FILES)

        if user_form.is_valid() and add_form.is_valid():
            user_form.save()
            user = user_form.save()

            add_fields = add_form.save(commit=False)
            add_fields.user = user

            if 'date_of_birth' in user_form.cleaned_data:
                add_fields.date_of_birth = user_form.cleaned_data.get('date_of_birth')

            add_fields.save()
            registered = True
            messages.success(request, 'Account has been successfully created.') 

            # retrieve username and raw un-hashed passsword to login 
            username = user_form.cleaned_data.get('username')
            raw_password = user_form.cleaned_data.get('password1')
            
            user = authenticate(username=username, password=raw_password)

            if user is not None:
                #login with registered credentials
                login(self.request, user)
                return redirect('home')
            
        else:
            messages.error(request, user_form.errors, add_form.errors)

        context = {
            'user_form': user_form,
            'add_form': add_form,
            'registered': registered
        }

        return render(request, self.template_name, context)
    
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        
        user_form = UserRegistrationForm()
        add_form = UserExtraFieldsForm()

        context = {
            'user_form': user_form,
            'add_form': add_form,
            'registered': self.registered
        }
        
        return render(request, self.template_name, context)
    

class HomeFeed(LoginRequiredMixin, ListView, FormMixin):
    """
    Renders home feed unique to authenticated user.
    """
    model = Post
    template_name = 'social_network/home.html'
    paginate_by = 5
    #login_url = '/login'
    success_url = reverse_lazy('home')
    form_class = PostForm

    # source: https://github.com/legionscript/socialnetwork/blob/tutorial2/social/views.py
    # source: https://stackoverflow.com/questions/67956629/how-to-fetch-self-and-friends-posts-on-django-model
    
    def get_context_data(self, **kwargs):
        
        user = self.request.user
        context = super().get_context_data(**kwargs) 

        pass_user_profile = has_user_profile_context(user)
        if pass_user_profile == 1:
            messages.error("Please update your personal profile details.")
            return context
        elif pass_user_profile == 2:
            User.objects.get(username=user.username).is_active = False
            messages.error("Please sign up again.")
            redirect('register')
        
        elif pass_user_profile == 0:
            friends = user.profile.get_friends()
            # source: https://stackoverflow.com/questions/65141518/how-to-filter-posts-query-in-order-to-just-see-the-posts-of-friends-and-myself-i
            context['posts'] = Post.objects.filter(Q(author__in=friends) 
                                                    | Q(author=user)
                                                    ).order_by('-created_date')
            if friends is not None:
                context['friends'] = friends 
            else:
                context['friends'] = None 
              
            return context
    
    def get(self, request, *args, **kwargs):
        if request.user.is_superuser:
            messages.success(request, "Developer access")
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        form = PostForm(request.POST, request.FILES)

        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.author = request.user
            new_post.save()

            messages.success(self.request, 'Success! Post has been created.')
            form = PostForm()

            return self.form_valid(form)
        else: 
            return self.form_invalid(form)
        

class PostDetailView(LoginRequiredMixin, DetailView):
    """
    Renders detailed view of a single post. 
    """
    template_name = 'social_network/post_detail.html'
    model = Post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = Post.objects.filter(id=self.get_object().pk).first()
        return context
    
   
class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    To edit the body text of an existing post.
    """
    template_name = 'social_network/post_update.html'
    model = Post
    fields = ('body_text',)

    def test_func(self):
        """
        Test to check whether currently logged in user is the author of the post
        """
        obj = self.get_object()
        return obj.author == self.request.user
    
    def get_success_url(self):
        return reverse('post_detail', kwargs={'pk': self.kwargs['pk']})
    

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, 
                     SelectRelatedMixin, DeleteView):
    """
    To delete an existing post
    """
    template_name = 'social_network/post_confirm_delete.html'
    success_url = reverse_lazy('home')
    model = Post
    select_related=('author',)

    def test_func(self):
        """
        Test to check whether currently logged in user is the author of the post
        """
        obj = self.get_object()
        return obj.author == self.request.user
    
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(author=self.request.user)

    def delete(self,*args,**kwargs):
        messages.success(self.request,'Post deleted successfully.')
        return super().delete(*args,**kwargs)


# source: https://stackoverflow.com/questions/6548947/how-can-django-debug-toolbar-be-set-to-work-for-just-some-users
def show_toolbar(request):
    """
    Renders debugging toolbar only for developers / superusers
    """
    return request.user and request.user.is_superuser and request.user.profile != None
