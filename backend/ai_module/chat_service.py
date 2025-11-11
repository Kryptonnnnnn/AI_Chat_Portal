import os
import requests
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()


class ChatService:
    """
    Service class for handling AI chat interactions.
    Supports OpenAI, Anthropic, Gemini, and Ollama (local LLM).
    """
    
    def __init__(self, provider='ollama'):
        self.provider = provider
        self.client = None
        self.ollama_url = os.getenv('OLLAMA_URL', 'http://localhost:11434')
        self.ollama_model = os.getenv('OLLAMA_MODEL', 'llama3.2')
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the appropriate AI client based on provider"""
        
        # Try Ollama first (free and local)
        if self._check_ollama_available():
            self.provider = 'ollama'
            print(f"✓ Using Ollama ({self.ollama_model}) - Local LLM")
            return
        
        # Fallback to API keys
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key and api_key.strip() and api_key != 'your-openai-key':
            try:
                import openai
                self.client = openai.OpenAI(api_key=api_key)
                self.model = 'gpt-3.5-turbo'
                self.provider = 'openai'
                print("✓ Using OpenAI")
                return
            except Exception as e:
                print(f"OpenAI initialization failed: {e}")
        
        # Final fallback to mock
        print("✓ Using mock responses (no AI available)")
        self.provider = 'mock'
    
    def _check_ollama_available(self):
        """Check if Ollama is running and accessible"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=2)
            return response.status_code == 200
        except Exception:
            return False
    
    def get_response(self, user_message: str, chat_history: List[Dict] = None) -> str:
        """Get AI response to user message with conversation context."""
        if chat_history is None:
            chat_history = []
        
        try:
            if self.provider == 'ollama':
                return self._get_ollama_response(user_message, chat_history)
            elif self.provider == 'openai' and self.client:
                return self._get_openai_response(user_message, chat_history)
            else:
                return self._get_mock_response(user_message, chat_history)
        except Exception as e:
            print(f"Error getting AI response: {e}")
            return self._get_mock_response(user_message, chat_history)
    
    def _get_ollama_response(self, user_message: str, chat_history: List[Dict]) -> str:
        """Get response from Ollama (local LLM)"""
        try:
            # Build conversation context
            messages = []
            
            # Add system message
            messages.append({
                "role": "system",
                "content": "You are a helpful AI assistant. Provide clear, concise, and friendly responses."
            })
            
            # Add chat history
            for msg in chat_history[-10:]:  # Last 10 messages for context
                role = "user" if msg['sender'] == 'user' else "assistant"
                messages.append({
                    "role": role,
                    "content": msg['content']
                })
            
            # Add current message
            messages.append({
                "role": "user",
                "content": user_message
            })
            
            # Call Ollama API
            response = requests.post(
                f"{self.ollama_url}/api/chat",
                json={
                    "model": self.ollama_model,
                    "messages": messages,
                    "stream": False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('message', {}).get('content', 'No response generated')
            else:
                print(f"Ollama error: {response.status_code}")
                return self._get_mock_response(user_message, chat_history)
                
        except Exception as e:
            print(f"Ollama request failed: {e}")
            return self._get_mock_response(user_message, chat_history)
    
    def _get_openai_response(self, user_message: str, chat_history: List[Dict]) -> str:
        """Get response from OpenAI GPT"""
        messages = [
            {"role": "system", "content": "You are a helpful AI assistant."}
        ]
        
        for msg in chat_history:
            role = "user" if msg['sender'] == 'user' else "assistant"
            messages.append({"role": role, "content": msg['content']})
        
        messages.append({"role": "user", "content": user_message})
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )
        
        return response.choices[0].message.content
    
    def _get_mock_response(self, user_message: str, chat_history: List[Dict]) -> str:
        """Generate mock response when no AI provider is available."""
        import random
        
        responses = [
            f"Thanks for your message: '{user_message[:50]}...' I'm currently in demonstration mode. Install Ollama (free!) or add an API key for real AI responses!",
            f"I understand you're asking about '{user_message[:40]}...' This is a mock response. For real AI conversations, please set up Ollama or add an API key.",
            f"Regarding '{user_message[:45]}...', that's interesting! The chat system is working. Add Ollama (free local AI) or an API key for intelligent responses.",
            "The AI Chat Portal is functioning perfectly! To enable real AI responses: 1) Install Ollama (free), or 2) Add an OpenAI/Claude API key to .env",
        ]
        
        base_response = random.choice(responses)
        
        if len(chat_history) > 0:
            base_response += f"\n\n(This is message #{len(chat_history) + 1} in our conversation)"
        
        return base_response