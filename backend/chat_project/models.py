from django.db import models

class Conversation(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('ended', 'Ended'),
    ]
    
    title = models.CharField(max_length=255, default="New Conversation")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    summary = models.TextField(blank=True, null=True)
    topics = models.JSONField(default=list, blank=True)
    sentiment = models.CharField(max_length=50, blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['status']),
        ]
        
    def __str__(self):  
        return f"{self.title} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
    
    @property
    def duration(self):
        if self.ended_at:
            delta = self.ended_at - self.created_at
            return round(delta.total_seconds() / 60, 2)
        return None

    @property
    def message_count(self):
        return self.messages.count()

class Message(models.Model):
    SENDER_CHOICES = [
        ('user', 'User'),
        ('ai', 'AI'),
    ]
    
    conversation = models.ForeignKey(
        Conversation, 
        on_delete=models.CASCADE, 
        related_name='messages'
    )       
    content = models.TextField()
    sender = models.CharField(max_length=10, choices=SENDER_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['timestamp']
        indexes = [
            models.Index(fields=['conversation', 'timestamp']),
            models.Index(fields=['sender']),
        ]
        
    def __str__(self):
        return f"{self.sender}: {self.content[:50]}..."

class ConversationQuery(models.Model):
    query_text = models.TextField()
    response = models.TextField()
    relevant_conversations = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"Query: {self.query_text[:50]}..."  





