from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q

from .models import Conversation, Message, ConversationQuery
from .serializers import (
    ConversationSerializer, ConversationListSerializer,
    MessageSerializer, ConversationQuerySerializer,
    ChatMessageSerializer, QueryRequestSerializer
)
from ai_module.chat_service import ChatService
from ai_module.conversation_analyzer import ConversationAnalyzer
from ai_module.query_engine import QueryEngine


class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing conversations.
    Provides CRUD operations and custom actions for chat functionality.
    """
    queryset = Conversation.objects.all()
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return ConversationListSerializer
        return ConversationSerializer
    
    def list(self, request):
        """
        GET /api/conversations/
        Retrieve all conversations with optional filtering
        """
        queryset = self.get_queryset()
        
        # Filter by status
        status_filter = request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Search by title
        search = request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(title__icontains=search)
        
        # Date range filtering
        date_from = request.query_params.get('date_from', None)
        date_to = request.query_params.get('date_to', None)
        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, pk=None):
        """
        GET /api/conversations/{id}/
        Get specific conversation with full message history
        """
        try:
            conversation = self.get_object()
            serializer = self.get_serializer(conversation)
            return Response(serializer.data)
        except Conversation.DoesNotExist:
            return Response(
                {'error': 'Conversation not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'])
    def chat(self, request):
        """
        POST /api/conversations/chat/
        Send a message and get AI response
        Body: {
            "message": "user message",
            "conversation_id": 123 (optional)
        }
        """
        serializer = ChatMessageSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        user_message = serializer.validated_data['message']
        conversation_id = serializer.validated_data.get('conversation_id')
        
        try:
            # Get or create conversation
            if conversation_id:
                conversation = Conversation.objects.get(id=conversation_id)
                if conversation.status == 'ended':
                    return Response(
                        {'error': 'Cannot send messages to ended conversation'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            else:
                # Create new conversation with title from first message
                title = user_message[:50] + "..." if len(user_message) > 50 else user_message
                conversation = Conversation.objects.create(title=title)
            
            # Save user message
            user_msg = Message.objects.create(
                conversation=conversation,
                content=user_message,
                sender='user'
            )
            
            # Get chat history for context
            chat_history = list(conversation.messages.values('content', 'sender'))
            
            # Get AI response using ChatService
            chat_service = ChatService()
            ai_response = chat_service.get_response(user_message, chat_history[:-1])
            
            # Save AI message
            ai_msg = Message.objects.create(
                conversation=conversation,
                content=ai_response,
                sender='ai'
            )
            
            return Response({
                'conversation_id': conversation.id,
                'user_message': MessageSerializer(user_msg).data,
                'ai_response': MessageSerializer(ai_msg).data
            }, status=status.HTTP_201_CREATED)
            
        except Conversation.DoesNotExist:
            return Response(
                {'error': 'Conversation not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def end(self, request, pk=None):
        """
        POST /api/conversations/{id}/end/
        End conversation and generate summary
        """
        try:
            conversation = self.get_object()
            
            if conversation.status == 'ended':
                return Response(
                    {'error': 'Conversation already ended'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Update status and timestamp
            conversation.status = 'ended'
            conversation.ended_at = timezone.now()
            
            # Generate AI summary and analysis
            analyzer = ConversationAnalyzer()
            messages = list(conversation.messages.values('content', 'sender'))
            
            analysis = analyzer.analyze_conversation(messages)
            
            conversation.summary = analysis.get('summary', '')
            conversation.topics = analysis.get('topics', [])
            conversation.sentiment = analysis.get('sentiment', '')
            conversation.save()
            
            serializer = self.get_serializer(conversation)
            return Response(serializer.data)
            
        except Conversation.DoesNotExist:
            return Response(
                {'error': 'Conversation not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def query(self, request):
        """
        POST /api/conversations/query/
        Query AI about past conversations
        Body: {
            "query": "What did we discuss about...",
            "date_from": "2024-01-01T00:00:00Z" (optional),
            "date_to": "2024-12-31T23:59:59Z" (optional),
            "topics": ["topic1", "topic2"] (optional)
        }
        """
        serializer = QueryRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        query_text = serializer.validated_data['query']
        date_from = serializer.validated_data.get('date_from')
        date_to = serializer.validated_data.get('date_to')
        topics = serializer.validated_data.get('topics', [])
        
        try:
            # Filter conversations
            queryset = Conversation.objects.filter(status='ended')
            
            if date_from:
                queryset = queryset.filter(created_at__gte=date_from)
            if date_to:
                queryset = queryset.filter(created_at__lte=date_to)
            if topics:
                queryset = queryset.filter(topics__overlap=topics)
            
            # Use QueryEngine to find relevant conversations and generate response
            query_engine = QueryEngine()
            result = query_engine.query_conversations(query_text, queryset)
            
            # Save query for analytics
            query_record = ConversationQuery.objects.create(
                query_text=query_text,
                response=result['response'],
                relevant_conversations=result['relevant_conversation_ids']
            )
            
            return Response({
                'query': query_text,
                'response': result['response'],
                'relevant_conversations': result['conversations'],
                'total_searched': queryset.count()
            })
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

@action(detail=True, methods=['get'])
def related(self, request, pk=None):
    """
    GET /api/conversations/{id}/related/
    Get conversations related to this one
    """
    try:
        from ai_module.suggestions_service import SuggestionsService
        
        conversation = self.get_object()
        all_conversations = Conversation.objects.filter(status='ended').exclude(id=conversation.id)
        
        suggestions_service = SuggestionsService()
        related = suggestions_service.get_related_conversations(
            conversation, 
            all_conversations,
            limit=5
        )
        
        return Response({
            'conversation_id': conversation.id,
            'related_conversations': related
        })
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@action(detail=False, methods=['get'])
def trending(self, request):
    """
    GET /api/conversations/trending/
    Get trending topics from recent conversations
    """
    try:
        from ai_module.suggestions_service import SuggestionsService
        
        days = int(request.query_params.get('days', 30))
        conversations = Conversation.objects.filter(status='ended')
        
        suggestions_service = SuggestionsService()
        trending_topics = suggestions_service.get_trending_topics(conversations, days)
        
        return Response({
            'trending_topics': trending_topics,
            'period_days': days
        })
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class MessageViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing messages.
    Read-only access to message history.
    """
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    
    def get_queryset(self):
        """Filter messages by conversation if provided"""
        queryset = super().get_queryset()
        conversation_id = self.request.query_params.get('conversation_id', None)
        if conversation_id:
            queryset = queryset.filter(conversation_id=conversation_id)
        return queryset