from django.contrib import admin
from django.core.cache import cache

from .models import ChatRoom, ChatMessage


class MessageInline(admin.StackedInline):

    model = ChatMessage
    fields = ('sender', 'content', 'timestamp',)
    readonly_fields = ('sender', 'content', 'timestamp',)


class ChatAdmin(admin.ModelAdmin):

    model = ChatRoom
    inlines = (MessageInline,)

admin.site.register(ChatRoom, ChatAdmin)