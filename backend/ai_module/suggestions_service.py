"""
Service for generating intelligent conversation suggestions.
Analyzes conversation patterns and recommends related discussions.
"""

from typing import List, Dict
from collections import Counter
import re


class SuggestionsService:
    """
    Generates intelligent suggestions for related conversations
    based on topics, sentiment, and content similarity.
    """
    
    def get_related_conversations(self, current_conversation, all_conversations, limit=5) -> List[Dict]:
        """
        Find conversations related to the current one based on:
        - Shared topics
        - Similar sentiment
        - Content similarity
        - Temporal proximity
        """
        if not all_conversations:
            return []
        
        scored_conversations = []
        
        for conv in all_conversations:
            # Skip the current conversation
            if conv.id == current_conversation.id:
                continue
            
            # Skip conversations without analysis
            if not conv.topics:
                continue
            
            score = self._calculate_similarity_score(current_conversation, conv)
            
            if score > 0.1:  # Minimum threshold
                scored_conversations.append({
                    'conversation': conv,
                    'score': score,
                    'reason': self._get_similarity_reason(current_conversation, conv)
                })
        
        # Sort by score and return top results
        scored_conversations.sort(key=lambda x: x['score'], reverse=True)
        
        return [{
            'id': item['conversation'].id,
            'title': item['conversation'].title,
            'topics': item['conversation'].topics,
            'sentiment': item['conversation'].sentiment,
            'created_at': item['conversation'].created_at.isoformat(),
            'similarity_score': float(item['score']),
            'reason': item['reason']
        } for item in scored_conversations[:limit]]
    
    def _calculate_similarity_score(self, conv1, conv2) -> float:
        """Calculate overall similarity score between two conversations"""
        score = 0.0
        
        # Topic overlap (most important - 50% weight)
        if conv1.topics and conv2.topics:
            topics1 = set(conv1.topics)
            topics2 = set(conv2.topics)
            topic_overlap = len(topics1 & topics2) / len(topics1 | topics2)
            score += topic_overlap * 0.5
        
        # Sentiment match (20% weight)
        if conv1.sentiment and conv2.sentiment:
            if conv1.sentiment == conv2.sentiment:
                score += 0.2
            elif self._similar_sentiment(conv1.sentiment, conv2.sentiment):
                score += 0.1
        
        # Temporal proximity (15% weight)
        if conv1.created_at and conv2.created_at:
            time_diff = abs((conv1.created_at - conv2.created_at).days)
            if time_diff < 7:
                score += 0.15
            elif time_diff < 30:
                score += 0.10
            elif time_diff < 90:
                score += 0.05
        
        # Title/summary similarity (15% weight)
        text_similarity = self._calculate_text_similarity(
            f"{conv1.title} {conv1.summary or ''}",
            f"{conv2.title} {conv2.summary or ''}"
        )
        score += text_similarity * 0.15
        
        return min(score, 1.0)  # Cap at 1.0
    
    def _similar_sentiment(self, sent1: str, sent2: str) -> bool:
        """Check if two sentiments are similar"""
        positive_sentiments = {'positive', 'very positive'}
        negative_sentiments = {'negative', 'very negative'}
        
        return (
            (sent1 in positive_sentiments and sent2 in positive_sentiments) or
            (sent1 in negative_sentiments and sent2 in negative_sentiments)
        )
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate simple text similarity using word overlap"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0.0
    
    def _get_similarity_reason(self, conv1, conv2) -> str:
        """Generate human-readable reason for similarity"""
        reasons = []
        
        # Check topic overlap
        if conv1.topics and conv2.topics:
            shared_topics = set(conv1.topics) & set(conv2.topics)
            if shared_topics:
                topics_str = ', '.join(list(shared_topics)[:3])
                reasons.append(f"Shared topics: {topics_str}")
        
        # Check sentiment match
        if conv1.sentiment and conv2.sentiment and conv1.sentiment == conv2.sentiment:
            reasons.append(f"Similar sentiment ({conv1.sentiment})")
        
        # Check time proximity
        if conv1.created_at and conv2.created_at:
            time_diff = abs((conv1.created_at - conv2.created_at).days)
            if time_diff < 7:
                reasons.append("From the same week")
            elif time_diff < 30:
                reasons.append("From the same month")
        
        return " • ".join(reasons) if reasons else "Similar content"
    
    def get_topic_based_suggestions(self, topics: List[str], all_conversations, limit=5) -> List[Dict]:
        """Get conversation suggestions based on specific topics"""
        if not topics:
            return []
        
        topic_set = set(t.lower() for t in topics)
        scored_conversations = []
        
        for conv in all_conversations:
            if not conv.topics:
                continue
            
            conv_topics = set(t.lower() for t in conv.topics)
            overlap = len(topic_set & conv_topics)
            
            if overlap > 0:
                score = overlap / len(topic_set)
                scored_conversations.append({
                    'conversation': conv,
                    'score': score,
                    'matching_topics': list(topic_set & conv_topics)
                })
        
        scored_conversations.sort(key=lambda x: x['score'], reverse=True)
        
        return [{
            'id': item['conversation'].id,
            'title': item['conversation'].title,
            'topics': item['conversation'].topics,
            'created_at': item['conversation'].created_at.isoformat(),
            'matching_topics': item['matching_topics'],
            'relevance': float(item['score'])
        } for item in scored_conversations[:limit]]
    
    def get_trending_topics(self, conversations, days=30) -> List[Dict]:
        """Identify trending topics from recent conversations"""
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_convs = [c for c in conversations if c.created_at >= cutoff_date]
        
        if not recent_convs:
            return []
        
        # Count all topics
        topic_counter = Counter()
        for conv in recent_convs:
            if conv.topics:
                topic_counter.update(conv.topics)
        
        # Get top topics with their conversation counts
        trending = []
        for topic, count in topic_counter.most_common(10):
            trending.append({
                'topic': topic,
                'conversation_count': count,
                'percentage': round(count / len(recent_convs) * 100, 1)
            })
        
        return trending