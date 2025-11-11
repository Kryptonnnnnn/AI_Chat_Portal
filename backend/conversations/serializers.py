from rest_framework import serializers
from .models import Conversation, Message, ConversationQuery


class MessageSerializer(serializers.ModelSerializer):
    """
    Serializer for Message model.
    Handles conversion between Message instances and JSON.
    """
    class Meta:
        model = Message
        fields = ['id', 'content', 'sender', 'timestamp', 'conversation']
        read_only_fields = ['id', 'timestamp']


class ConversationSerializer(serializers.ModelSerializer):
    """
    Serializer for Conversation model with nested messages.
    Includes computed properties like duration and message count.
    """
    messages = MessageSerializer(many=True, read_only=True)
    duration = serializers.ReadOnlyField()
    message_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Conversation
        fields = [
            'id', 'title', 'status', 'created_at', 'ended_at', 
            'summary', 'topics', 'sentiment', 'messages', 
            'duration', 'message_count'
        ]
        read_only_fields = ['id', 'created_at']


class ConversationListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing conversations.
    Excludes messages for better performance.
    """
    message_count = serializers.ReadOnlyField()
    duration = serializers.ReadOnlyField()
    latest_message = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = [
            'id', 'title', 'status', 'created_at', 'ended_at',
            'message_count', 'duration', 'latest_message', 'topics'
        ]
    
    def get_latest_message(self, obj):
        """Get the most recent message preview"""
        last_message = obj.messages.last()
        if last_message:
            return {
                'content': last_message.content[:100],
                'sender': last_message.sender,
                'timestamp': last_message.timestamp
            }
        return None


class ConversationQuerySerializer(serializers.ModelSerializer):
    """
    Serializer for conversation queries.
    Stores user queries and AI responses about past conversations.
    """
    class Meta:
        model = ConversationQuery
        fields = ['id', 'query_text', 'response', 'relevant_conversations', 'created_at']
        read_only_fields = ['id', 'created_at']


class ChatMessageSerializer(serializers.Serializer):
    """
    Serializer for incoming chat messages.
    Used for validation of chat requests.
    """
    message = serializers.CharField(required=True, max_length=5000)
    conversation_id = serializers.IntegerField(required=False, allow_null=True)


class QueryRequestSerializer(serializers.Serializer):
    """
    Serializer for query requests about past conversations.
    """
    query = serializers.CharField(required=True, max_length=1000)
    date_from = serializers.DateTimeField(required=False, allow_null=True)
    date_to = serializers.DateTimeField(required=False, allow_null=True)
    topics = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=True
    )