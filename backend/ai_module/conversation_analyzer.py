import os
from typing import List, Dict
from collections import Counter
import re


class ConversationAnalyzer:
    """
    Enhanced analyzer that extracts insights, summaries, topics, sentiment,
    key decisions, and action items from conversations.
    """
    
    def __init__(self, provider='openai'):
        self.provider = provider
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize AI client for advanced analysis"""
        api_key = os.getenv('OPENAI_API_KEY')
        
        if api_key and api_key.strip() and api_key != 'your-openai-key':
            try:
                import openai
                self.client = openai.OpenAI(api_key=api_key)
                print("✓ Using OpenAI for conversation analysis")
            except Exception as e:
                print(f"OpenAI initialization failed: {e}")
                self.client = None
        else:
            print("✓ Using rule-based conversation analysis")
            self.client = None
    
    def analyze_conversation(self, messages: List[Dict]) -> Dict:
        """
        Perform comprehensive analysis of a conversation including:
        - Summary generation
        - Topic extraction
        - Sentiment analysis
        - Key decisions identification
        - Action items extraction
        - Key points highlighting
        """
        if not messages:
            return {
                'summary': 'No messages to analyze',
                'topics': [],
                'sentiment': 'neutral',
                'key_points': [],
                'decisions': [],
                'action_items': [],
                'word_count': 0
            }
        
        # Core analysis
        summary = self._generate_summary(messages)
        topics = self._extract_topics(messages)
        sentiment = self._analyze_sentiment(messages)
        key_points = self._extract_key_points(messages)
        
        # Advanced features
        decisions = self._extract_decisions(messages)
        action_items = self._extract_action_items(messages)
        
        # Statistics
        stats = self._calculate_stats(messages)
        
        return {
            'summary': summary,
            'topics': topics,
            'sentiment': sentiment,
            'key_points': key_points,
            'decisions': decisions,
            'action_items': action_items,
            **stats
        }
    
    def _generate_summary(self, messages: List[Dict]) -> str:
        """Generate AI-powered or rule-based summary"""
        if self.client:
            try:
                conversation_text = self._format_conversation(messages)
                
                response = self.client.chat.completions.create(
                    model='gpt-3.5-turbo',
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an expert at analyzing conversations. Provide a concise 2-3 sentence summary highlighting the main topics, key decisions, and outcomes."
                        },
                        {
                            "role": "user",
                            "content": f"Summarize this conversation:\n\n{conversation_text}"
                        }
                    ],
                    max_tokens=200,
                    temperature=0.5
                )
                
                return response.choices[0].message.content.strip()
            except Exception as e:
                print(f"Error generating AI summary: {e}")
                return self._generate_basic_summary(messages)
        
        return self._generate_basic_summary(messages)
    
    def _generate_basic_summary(self, messages: List[Dict]) -> str:
        """Generate rule-based summary"""
        user_messages = [m['content'] for m in messages if m['sender'] == 'user']
        
        if not user_messages:
            return "Conversation with AI assistant"
        
        # Identify main themes from questions and statements
        themes = []
        for msg in user_messages[:3]:  # First 3 messages often set the theme
            # Extract nouns and key phrases
            words = msg.lower().split()
            if len(words) > 3:
                themes.append(msg[:60])
        
        first_msg = user_messages[0][:100]
        
        if len(user_messages) > 5:
            summary = f"Comprehensive discussion starting with '{first_msg}...' "
            summary += f"The conversation covered {len(user_messages)} topics with "
            summary += f"{len(messages)} total exchanges."
        elif len(user_messages) > 1:
            last_msg = user_messages[-1][:80]
            summary = f"Conversation about '{first_msg}...' concluding with '{last_msg}...'"
        else:
            summary = f"Brief discussion: {first_msg}"
        
        return summary
    
    def _extract_decisions(self, messages: List[Dict]) -> List[str]:
        """
        Extract key decisions made during the conversation.
        Looks for decision-indicating phrases and commitment statements.
        """
        decisions = []
        
        # Decision indicator patterns
        decision_patterns = [
            r"(?i)(decided to|will|going to|agreed to|chose to|selected|picked)",
            r"(?i)(let's|we'll|we will|we should|we must)",
            r"(?i)(final decision|conclusion|determined that)",
            r"(?i)(approved|confirmed|settled on)"
        ]
        
        for msg in messages:
            content = msg['content']
            
            # Check for decision patterns
            for pattern in decision_patterns:
                if re.search(pattern, content):
                    # Extract the sentence containing the decision
                    sentences = re.split(r'[.!?]', content)
                    for sentence in sentences:
                        if re.search(pattern, sentence) and len(sentence.strip()) > 10:
                            decision = sentence.strip()
                            if len(decision) > 15:  # Avoid very short matches
                                decisions.append(decision[:150])
                                break
        
        # Remove duplicates while preserving order
        seen = set()
        unique_decisions = []
        for d in decisions:
            if d.lower() not in seen:
                seen.add(d.lower())
                unique_decisions.append(d)
        
        return unique_decisions[:5]  # Return top 5 decisions
    
    def _extract_action_items(self, messages: List[Dict]) -> List[str]:
        """
        Extract action items and tasks from the conversation.
        Looks for task-indicating phrases and commitments.
        """
        action_items = []
        
        # Action item patterns
        action_patterns = [
            r"(?i)(need to|have to|must|should|ought to)",
            r"(?i)(todo|to-do|task|action item)",
            r"(?i)(will (do|create|build|implement|design|develop))",
            r"(?i)(remember to|don't forget to)",
            r"(?i)(next step|next, we|then we)",
        ]
        
        for msg in messages:
            content = msg['content']
            
            # Check for action patterns
            for pattern in action_patterns:
                if re.search(pattern, content):
                    sentences = re.split(r'[.!?]', content)
                    for sentence in sentences:
                        if re.search(pattern, sentence) and len(sentence.strip()) > 10:
                            action = sentence.strip()
                            if len(action) > 15:
                                action_items.append(action[:150])
                                break
        
        # Also look for imperative sentences (commands/instructions)
        imperative_verbs = ['create', 'build', 'implement', 'design', 'develop', 
                           'make', 'add', 'update', 'change', 'fix', 'test']
        
        for msg in messages:
            if msg['sender'] == 'user':  # Focus on user requests
                content = msg['content']
                first_word = content.split()[0].lower() if content.split() else ''
                if first_word in imperative_verbs:
                    action_items.append(content[:150])
        
        # Remove duplicates
        seen = set()
        unique_actions = []
        for action in action_items:
            if action.lower() not in seen:
                seen.add(action.lower())
                unique_actions.append(action)
        
        return unique_actions[:7]  # Return top 7 action items
    
    def _extract_topics(self, messages: List[Dict]) -> List[str]:
        """Enhanced topic extraction using TF-IDF"""
        all_text = " ".join([m['content'] for m in messages])
        
        # Extended stop words
        stop_words = {
            'the', 'is', 'at', 'which', 'on', 'a', 'an', 'and', 'or', 'but',
            'in', 'with', 'to', 'for', 'of', 'as', 'by', 'that', 'this',
            'it', 'from', 'are', 'was', 'were', 'been', 'be', 'have', 'has',
            'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
            'can', 'may', 'might', 'must', 'i', 'you', 'he', 'she', 'we', 
            'they', 'what', 'how', 'when', 'where', 'why', 'who', 'your',
            'their', 'there', 'here', 'then', 'than', 'these', 'those'
        }
        
        # Extract words (4+ characters)
        words = re.findall(r'\b[a-zA-Z]{4,}\b', all_text.lower())
        
        # Filter stop words and count
        filtered_words = [w for w in words if w not in stop_words]
        word_counts = Counter(filtered_words)
        
        # Get top topics (minimum 2 occurrences)
        topics = [word for word, count in word_counts.most_common(10) if count > 1]
        
        return topics[:7]  # Return top 7 topics
    
    def _analyze_sentiment(self, messages: List[Dict]) -> str:
        """Enhanced sentiment analysis"""
        positive_words = {
            'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic',
            'love', 'like', 'enjoy', 'happy', 'glad', 'thank', 'thanks',
            'appreciate', 'perfect', 'awesome', 'brilliant', 'excited',
            'helpful', 'useful', 'nice', 'better', 'best', 'pleased'
        }
        
        negative_words = {
            'bad', 'terrible', 'awful', 'hate', 'dislike', 'angry', 'sad',
            'disappointed', 'frustrated', 'annoyed', 'problem', 'issue',
            'wrong', 'error', 'fail', 'failed', 'difficult', 'hard',
            'worse', 'worst', 'unhappy', 'upset', 'confused'
        }
        
        all_text = " ".join([m['content'] for m in messages]).lower()
        words = set(re.findall(r'\b[a-z]+\b', all_text))
        
        positive_count = len(words & positive_words)
        negative_count = len(words & negative_words)
        
        # More nuanced sentiment
        total = positive_count + negative_count
        if total == 0:
            return 'neutral'
        
        positive_ratio = positive_count / total
        
        if positive_ratio > 0.7:
            return 'very positive'
        elif positive_ratio > 0.55:
            return 'positive'
        elif positive_ratio > 0.45:
            return 'neutral'
        elif positive_ratio > 0.3:
            return 'negative'
        else:
            return 'very negative'
    
    def _extract_key_points(self, messages: List[Dict]) -> List[str]:
        """Extract key points and highlights from conversation"""
        key_points = []
        
        # Look for questions (important user interests)
        for msg in messages:
            if msg['sender'] == 'user':
                content = msg['content']
                if '?' in content:
                    questions = [s.strip() + '?' for s in content.split('?') if s.strip()]
                    key_points.extend(questions[:2])
        
        # Look for statements with key phrases
        key_phrases = ['i need', 'i want', 'can you', 'how to', 'what is', 'tell me about']
        for msg in messages:
            if msg['sender'] == 'user':
                content = msg['content'].lower()
                if any(phrase in content for phrase in key_phrases):
                    key_points.append(msg['content'][:100])
        
        return key_points[:5]
    
    def _calculate_stats(self, messages: List[Dict]) -> Dict:
        """Calculate detailed conversation statistics"""
        user_messages = [m for m in messages if m['sender'] == 'user']
        ai_messages = [m for m in messages if m['sender'] == 'ai']
        
        total_words = sum(len(m['content'].split()) for m in messages)
        user_words = sum(len(m['content'].split()) for m in user_messages)
        ai_words = sum(len(m['content'].split()) for m in ai_messages)
        
        return {
            'total_messages': len(messages),
            'user_messages': len(user_messages),
            'ai_messages': len(ai_messages),
            'word_count': total_words,
            'user_word_count': user_words,
            'ai_word_count': ai_words,
            'avg_message_length': total_words // len(messages) if messages else 0,
            'avg_user_length': user_words // len(user_messages) if user_messages else 0,
            'avg_ai_length': ai_words // len(ai_messages) if ai_messages else 0,
        }
    
    def _format_conversation(self, messages: List[Dict]) -> str:
        """Format messages for AI processing"""
        formatted = []
        for msg in messages:
            sender = "User" if msg['sender'] == 'user' else "AI"
            formatted.append(f"{sender}: {msg['content']}")
        return "\n".join(formatted)