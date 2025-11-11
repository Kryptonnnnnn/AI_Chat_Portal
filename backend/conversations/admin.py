from django.contrib import admin
from .models import Conversation, Message, ConversationQuery


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    """Admin interface for Conversation model"""
    list_display = ['id', 'title', 'status', 'created_at', 'message_count', 'duration']
    list_filter = ['status', 'created_at']
    search_fields = ['title', 'summary', 'topics']
    readonly_fields = ['created_at', 'ended_at', 'message_count', 'duration']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'status', 'created_at', 'ended_at')
        }),
        ('Analysis', {
            'fields': ('summary', 'topics', 'sentiment')
        }),
        ('Statistics', {
            'fields': ('message_count', 'duration')
        }),
    )


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """Admin interface for Message model"""
    list_display = ['id', 'conversation', 'sender', 'timestamp', 'content_preview']
    list_filter = ['sender', 'timestamp']
    search_fields = ['content']
    readonly_fields = ['timestamp']
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content Preview'


@admin.register(ConversationQuery)
class ConversationQueryAdmin(admin.ModelAdmin):
    """Admin interface for ConversationQuery model"""
    list_display = ['id', 'query_preview', 'created_at']
    list_filter = ['created_at']
    search_fields = ['query_text', 'response']
    readonly_fields = ['created_at']
    
    def query_preview(self, obj):
        return obj.query_text[:100] + '...' if len(obj.query_text) > 100 else obj.query_text
    query_preview.short_description = 'Query'
