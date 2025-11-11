import os
from typing import List, Dict
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


class QueryEngine:
    """
    Enhanced engine for querying past conversations using semantic search.
    Implements embeddings-based similarity for intelligent conversation retrieval.
    """
    
    def __init__(self, provider='openai'):
        self.provider = provider
        self.client = None
        self.embeddings_model = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize AI client and embeddings model"""
        api_key = os.getenv('OPENAI_API_KEY')
        
        # Try OpenAI first for embeddings
        if api_key and api_key.strip() and api_key != 'your-openai-key':
            try:
                import openai
                self.client = openai.OpenAI(api_key=api_key)
                self.provider = 'openai'
                print("✓ Using OpenAI for embeddings and queries")
            except Exception as e:
                print(f"OpenAI initialization failed: {e}")
                self._initialize_local_embeddings()
        else:
            self._initialize_local_embeddings()
    
    def _initialize_local_embeddings(self):
        """Initialize local embeddings model as fallback"""
        try:
            from sentence_transformers import SentenceTransformer
            self.embeddings_model = SentenceTransformer('all-MiniLM-L6-v2')
            self.provider = 'local'
            print("✓ Using local sentence-transformers for embeddings")
        except ImportError:
            print("⚠ sentence-transformers not installed, using keyword matching")
            self.provider = 'keyword'
    
    def query_conversations(self, query: str, conversations_queryset) -> Dict:
        """
        Query past conversations and generate AI response with semantic search.
        
        Args:
            query: User's question about past conversations
            conversations_queryset: Django queryset of Conversation objects
            
        Returns:
            Dict with response, conversations, and metadata
        """
        conversations = list(conversations_queryset)
        
        if not conversations:
            return {
                'response': 'No conversations found to query.',
                'conversations': [],
                'relevant_conversation_ids': []
            }
        
        # Find relevant conversations using semantic search
        relevant_convs = self._find_relevant_conversations(query, conversations)
        
        # Generate AI response based on relevant conversations
        response = self._generate_query_response(query, relevant_convs)
        
        # Extract related conversations (suggestions)
        related_suggestions = self._get_related_suggestions(relevant_convs)
        
        # Format conversation data with relevance scores
        conv_data = []
        conv_ids = []
        for conv, score in relevant_convs[:5]:  # Top 5 relevant
            conv_ids.append(conv.id)
            conv_data.append({
                'id': conv.id,
                'title': conv.title,
                'created_at': conv.created_at.isoformat(),
                'summary': conv.summary,
                'relevance_score': float(score),
                'message_count': conv.message_count,
                'topics': conv.topics,
                'sentiment': conv.sentiment
            })
        
        return {
            'response': response,
            'conversations': conv_data,
            'relevant_conversation_ids': conv_ids,
            'related_suggestions': related_suggestions
        }
    
    def _find_relevant_conversations(self, query: str, conversations: List) -> List:
        """
        Find conversations relevant to the query using embeddings-based semantic search.
        
        Returns:
            List of tuples (conversation, relevance_score) sorted by relevance
        """
        # Create text representations of conversations
        conv_texts = []
        for conv in conversations:
            # Combine title, summary, topics, and messages for comprehensive matching
            text = f"{conv.title}. "
            
            if conv.summary:
                text += f"{conv.summary}. "
            
            if conv.topics:
                text += f"Topics: {', '.join(conv.topics)}. "
            
            # Add message content (limited to avoid token limits)
            messages = conv.messages.all()[:10]
            message_text = " ".join([m.content for m in messages])
            text += f"Content: {message_text[:500]}"
            
            conv_texts.append(text)
        
        # Calculate similarity scores based on provider
        if self.provider == 'openai':
            scores = self._calculate_openai_similarity(query, conv_texts)
        elif self.provider == 'local':
            scores = self._calculate_local_similarity(query, conv_texts)
        else:
            scores = self._calculate_keyword_similarity(query, conv_texts)
        
        # Combine conversations with scores and sort
        scored_convs = list(zip(conversations, scores))
        scored_convs.sort(key=lambda x: x[1], reverse=True)
        
        # Filter by minimum relevance threshold (0.1 for keyword, 0.3 for embeddings)
        min_threshold = 0.1 if self.provider == 'keyword' else 0.3
        relevant = [(conv, score) for conv, score in scored_convs if score > min_threshold]
        
        return relevant
    
    def _calculate_openai_similarity(self, query: str, texts: List[str]) -> List[float]:
        """Calculate similarity using OpenAI embeddings API"""
        try:
            # Get query embedding
            query_response = self.client.embeddings.create(
                input=query,
                model="text-embedding-ada-002"
            )
            query_embedding = np.array(query_response.data[0].embedding)
            
            # Get text embeddings (batch if possible)
            texts_response = self.client.embeddings.create(
                input=texts[:20],  # Limit batch size
                model="text-embedding-ada-002"
            )
            text_embeddings = np.array([data.embedding for data in texts_response.data])
            
            # Calculate cosine similarity
            query_emb = query_embedding.reshape(1, -1)
            similarities = cosine_similarity(query_emb, text_embeddings)[0]
            
            # Pad with zeros if we had more texts than we processed
            if len(texts) > 20:
                similarities = np.concatenate([
                    similarities,
                    np.zeros(len(texts) - 20)
                ])
            
            return similarities.tolist()
            
        except Exception as e:
            print(f"Error calculating OpenAI similarity: {e}")
            return self._calculate_keyword_similarity(query, texts)
    
    def _calculate_local_similarity(self, query: str, texts: List[str]) -> List[float]:
        """Calculate similarity using local embeddings model"""
        try:
            # Generate embeddings
            query_embedding = self.embeddings_model.encode([query])[0]
            text_embeddings = self.embeddings_model.encode(texts)
            
            # Calculate cosine similarity
            query_emb = query_embedding.reshape(1, -1)
            similarities = cosine_similarity(query_emb, text_embeddings)[0]
            
            return similarities.tolist()
        except Exception as e:
            print(f"Error calculating local similarity: {e}")
            return self._calculate_keyword_similarity(query, texts)
    
    def _calculate_keyword_similarity(self, query: str, texts: List[str]) -> List[float]:
        """Fallback keyword-based similarity using TF-IDF"""
        from sklearn.feature_extraction.text import TfidfVectorizer
        
        try:
            # Combine query with texts for vectorization
            all_texts = [query] + texts
            
            # Create TF-IDF vectors
            vectorizer = TfidfVectorizer(stop_words='english', max_features=100)
            tfidf_matrix = vectorizer.fit_transform(all_texts)
            
            # Calculate cosine similarity between query and texts
            query_vec = tfidf_matrix[0:1]
            text_vecs = tfidf_matrix[1:]
            similarities = cosine_similarity(query_vec, text_vecs)[0]
            
            return similarities.tolist()
        except Exception as e:
            print(f"Error in keyword similarity: {e}")
            # Simple word overlap fallback
            query_words = set(query.lower().split())
            scores = []
            for text in texts:
                text_words = set(text.lower().split())
                intersection = len(query_words & text_words)
                union = len(query_words | text_words)
                score = intersection / union if union > 0 else 0
                scores.append(score)
            return scores
    
    def _generate_query_response(self, query: str, relevant_convs: List) -> str:
        """Generate AI response based on query and relevant conversations"""
        if not relevant_convs:
            return "I couldn't find any relevant conversations matching your query. Try different keywords or check if you have any completed conversations."
        
        # Prepare context from relevant conversations
        context = self._prepare_context(relevant_convs)
        
        if self.client and self.provider == 'openai':
            try:
                response = self.client.chat.completions.create(
                    model='gpt-3.5-turbo',
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an AI assistant that helps users understand their past conversations. Provide clear, insightful answers based on the conversation history. Highlight key themes, decisions, and patterns."
                        },
                        {
                            "role": "user",
                            "content": f"Based on these past conversations:\n\n{context}\n\nAnswer this question: {query}\n\nProvide a comprehensive answer with specific examples from the conversations."
                        }
                    ],
                    max_tokens=500,
                    temperature=0.7
                )
                return response.choices[0].message.content
            except Exception as e:
                print(f"Error generating AI response: {e}")
                return self._generate_basic_response(query, relevant_convs)
        else:
            return self._generate_basic_response(query, relevant_convs)
    
    def _prepare_context(self, relevant_convs: List, max_convs: int = 3) -> str:
        """Prepare comprehensive context string from relevant conversations"""
        context_parts = []
        
        for i, (conv, score) in enumerate(relevant_convs[:max_convs], 1):
            context_parts.append(f"\n{'='*60}")
            context_parts.append(f"Conversation {i}: {conv.title}")
            context_parts.append(f"Relevance: {score:.1%}")
            context_parts.append(f"Date: {conv.created_at.strftime('%Y-%m-%d %H:%M')}")
            
            if conv.summary:
                context_parts.append(f"\nSummary: {conv.summary}")
            
            if conv.topics:
                context_parts.append(f"Topics: {', '.join(conv.topics)}")
            
            if conv.sentiment:
                context_parts.append(f"Sentiment: {conv.sentiment}")
            
            # Add key messages
            messages = conv.messages.all()[:5]
            if messages:
                context_parts.append("\nKey Messages:")
                for msg in messages:
                    sender = "User" if msg.sender == 'user' else "AI"
                    content = msg.content[:150] + "..." if len(msg.content) > 150 else msg.content
                    context_parts.append(f"  {sender}: {content}")
            
            context_parts.append("")
        
        return "\n".join(context_parts)
    
    def _generate_basic_response(self, query: str, relevant_convs: List) -> str:
        """Generate enhanced response without AI API"""
        top_conv, score = relevant_convs[0]
        
        response = f"Based on {len(relevant_convs)} relevant conversation(s), here's what I found:\n\n"
        response += f"**Most Relevant:** '{top_conv.title}' (Match: {score:.1%})\n"
        response += f"**Date:** {top_conv.created_at.strftime('%B %d, %Y at %H:%M')}\n"
        
        if top_conv.summary:
            response += f"\n**Summary:** {top_conv.summary}\n"
        
        if top_conv.topics:
            response += f"\n**Key Topics:** {', '.join(top_conv.topics)}\n"
        
        if top_conv.sentiment:
            response += f"**Tone:** {top_conv.sentiment.capitalize()}\n"
        
        # Add insights from multiple conversations
        if len(relevant_convs) > 1:
            response += f"\n**Additional Context:** Found {len(relevant_convs)-1} other related conversation(s) "
            all_topics = set()
            for conv, _ in relevant_convs[1:4]:
                if conv.topics:
                    all_topics.update(conv.topics)
            if all_topics:
                response += f"covering: {', '.join(list(all_topics)[:5])}"
        
        return response
    
    def _get_related_suggestions(self, relevant_convs: List) -> List[Dict]:
        """Generate related conversation suggestions based on current results"""
        suggestions = []
        
        # Get unique topics from relevant conversations
        all_topics = set()
        for conv, _ in relevant_convs[:3]:
            if conv.topics:
                all_topics.update(conv.topics)
        
        if all_topics:
            suggestions.append({
                'type': 'topic',
                'text': f"Conversations about: {', '.join(list(all_topics)[:3])}",
                'topics': list(all_topics)[:3]
            })
        
        # Suggest time-based queries
        if relevant_convs:
            latest_conv = relevant_convs[0][0]
            suggestions.append({
                'type': 'time',
                'text': f"Recent conversations from {latest_conv.created_at.strftime('%B %Y')}",
                'date': latest_conv.created_at.isoformat()
            })
        
        return suggestions[:3]
