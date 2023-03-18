from django.contrib import admin
from .models import *

class UserProfileAdmin(admin.ModelAdmin):
    
    list_per_page = 20
    ordering = ['user__date_joined']
    list_filter = ['user']
    list_display = ['user']
    search_fields = ['user']

    class Meta:
        model = UserProfile

admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Post)