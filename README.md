# AI Chat Portal - Full Stack Application

A comprehensive full-stack web application with AI integration for intelligent chat management and conversation analysis.

## 🚀 Features

### Core Functionality
- **Real-time AI Chat**: Seamless conversations with LLM (OpenAI/Anthropic/Gemini)
- **Conversation Management**: Store, retrieve, and manage all chat histories
- **Intelligent Summarization**: Auto-generate summaries when conversations end
- **Conversation Intelligence**: Query past conversations with AI-powered semantic search
- **Topic Extraction**: Automatic identification of conversation topics
- **Sentiment Analysis**: Analyze emotional tone of conversations

### Technical Highlights
- RESTful API with Django REST Framework
- React frontend with modern UI/UX
- PostgreSQL database for reliable data storage
- Semantic search using embeddings
- Clean OOP architecture throughout
- Comprehensive error handling

## 📁 Project Structure

```
ai-chat-portal/
├── backend/
│   ├── chat_project/          # Django project settings
│   │   ├── __init__.py
│   │   ├── settings.py        # Configuration
│   │   ├── urls.py            # URL routing
│   │   ├── wsgi.py
│   │   └── asgi.py
│   ├── conversations/          # Main Django app
│   │   ├── __init__.py
│   │   ├── models.py          # Database models
│   │   ├── serializers.py     # DRF serializers
│   │   ├── views.py           # API views
│   │   ├── urls.py            # App URLs
│   │   └── admin.py           # Admin interface
│   ├── ai_module/             # AI services
│   │   ├── __init__.py
│   │   ├── chat_service.py    # LLM integration
│   │   ├── conversation_analyzer.py  # Analysis engine
│   │   ├── embeddings_service.py     # Embeddings
│   │   └── query_engine.py    # Query processing
│   ├── manage.py
│   ├── requirements.txt
│   └── .env                   # Environment variables
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatInterface.jsx       # Chat UI
│   │   │   ├── ConversationsList.jsx   # List view
│   │   │   ├── QueryInterface.jsx      # Intelligence UI
│   │   │   └── Navbar.jsx              # Navigation
│   │   ├── services/
│   │   │   └── api.js         # API client
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── index.html
├── README.md
└── setup.sh                   # Setup script
```

## 🛠️ Tech Stack

### Backend
- **Framework**: Django 4.2.7 + Django REST Framework 3.14.0
- **Database**: PostgreSQL (psycopg2-binary)
- **AI Integration**: 
  - OpenAI GPT-3.5/4
  - Anthropic Claude
  - Google Gemini
- **Additional**: 
  - sentence-transformers (embeddings)
  - scikit-learn (similarity calculations)
  - python-dotenv (environment management)

### Frontend
- **Framework**: React 18.2 with Vite
- **Styling**: Tailwind CSS 3.3
- **Routing**: React Router DOM 6.20
- **HTTP Client**: Axios 1.6
- **Icons**: Lucide React 0.294

## 📋 Prerequisites

- Python 3.8+
- Node.js 16+
- PostgreSQL 12+
- pip and npm

## 🔧 Installation & Setup

### 1. Clone Repository

```bash
git clone <your-repo-url>
cd ai-chat-portal
```

### 2. Database Setup

Create PostgreSQL database:

```bash
# Login to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE ai_chat_portal;

# Create user (optional)
CREATE USER chatuser WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE ai_chat_portal TO chatuser;

# Exit
\q
```

### 3. Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
SECRET_KEY=your-django-secret-key-here
DEBUG=True
DATABASE_NAME=ai_chat_portal
DATABASE_USER=postgres
DATABASE_PASSWORD=your-password
DATABASE_HOST=localhost
DATABASE_PORT=5432

# AI API Keys (get from respective providers)
OPENAI_API_KEY=sk-your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
GEMINI_API_KEY=your-gemini-key
EOF

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

Backend will run on `http://localhost:8000`

### 4. Frontend Setup

```bash
# Open new terminal and navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will run on `http://localhost:5173`

## 🔑 API Keys Setup

### Option 1: Use External APIs (Recommended for Production)

1. **OpenAI**: Get API key from https://platform.openai.com/api-keys
2. **Anthropic**: Get API key from https://console.anthropic.com/
3. **Google Gemini**: Get API key from https://makersuite.google.com/app/apikey

Add keys to `backend/.env` file.

### Option 2: Use LM Studio (Free Alternative)

1. Download LM Studio from https://lmstudio.ai/
2. Download a model (e.g., Llama 2, Mistral)
3. Start local server in LM Studio
4. Modify `ChatService` to use local endpoint

## 📡 API Documentation

### Base URL
```
http://localhost:8000/api/
```

### Endpoints

#### 1. Get All Conversations
```http
GET /api/conversations/
```

Query Parameters:
- `status`: Filter by status (active/ended)
- `search`: Search in titles
- `date_from`: Filter from date
- `date_to`: Filter to date

Response:
```json
[
  {
    "id": 1,
    "title": "Discussion about AI",
    "status": "ended",
    "created_at": "2024-01-01T10:00:00Z",
    "message_count": 10,
    "duration": 15.5,
    "topics": ["AI", "machine learning"],
    "latest_message": {...}
  }
]
```

#### 2. Get Specific Conversation
```http
GET /api/conversations/{id}/
```

Response:
```json
{
  "id": 1,
  "title": "Discussion about AI",
  "status": "ended",
  "messages": [
    {
      "id": 1,
      "content": "Hello!",
      "sender": "user",
      "timestamp": "2024-01-01T10:00:00Z"
    }
  ],
  "summary": "Conversation about AI applications",
  "topics": ["AI", "technology"],
  "sentiment": "positive"
}
```

#### 3. Send Chat Message
```http
POST /api/conversations/chat/
Content-Type: application/json

{
  "message": "Tell me about AI",
  "conversation_id": 1  // optional, null for new conversation
}
```

Response:
```json
{
  "conversation_id": 1,
  "user_message": {
    "id": 5,
    "content": "Tell me about AI",
    "sender": "user",
    "timestamp": "2024-01-01T10:05:00Z"
  },
  "ai_response": {
    "id": 6,
    "content": "AI is...",
    "sender": "ai",
    "timestamp": "2024-01-01T10:05:02Z"
  }
}
```

#### 4. End Conversation
```http
POST /api/conversations/{id}/end/
```

Response:
```json
{
  "id": 1,
  "status": "ended",
  "ended_at": "2024-01-01T10:15:00Z",
  "summary": "Generated summary...",
  "topics": ["AI", "technology"],
  "sentiment": "positive"
}
```

#### 5. Query Past Conversations
```http
POST /api/conversations/query/
Content-Type: application/json

{
  "query": "What did we discuss about AI?",
  "date_from": "2024-01-01T00:00:00Z",  // optional
  "date_to": "2024-12-31T23:59:59Z",    // optional
  "topics": ["AI"]  // optional
}
```

Response:
```json
{
  "query": "What did we discuss about AI?",
  "response": "Based on your conversations...",
  "relevant_conversations": [
    {
      "id": 1,
      "title": "AI Discussion",
      "relevance_score": 0.95,
      "summary": "...",
      "topics": ["AI"]
    }
  ],
  "total_searched": 10
}
```

## 🗄️ Database Schema

### Conversations Table
```sql
- id: INTEGER (Primary Key)
- title: VARCHAR(255)
- status: VARCHAR(10) ['active', 'ended']
- created_at: TIMESTAMP
- ended_at: TIMESTAMP (nullable)
- summary: TEXT (nullable)
- topics: JSONB (array of strings)
- sentiment: VARCHAR(50) (nullable)
```

### Messages Table
```sql
- id: INTEGER (Primary Key)
- conversation_id: INTEGER (Foreign Key -> Conversations)
- content: TEXT
- sender: VARCHAR(10) ['user', 'ai']
- timestamp: TIMESTAMP
- embedding: JSONB (nullable, for semantic search)
```

### ConversationQuery Table
```sql
- id: INTEGER (Primary Key)
- query_text: TEXT
- response: TEXT
- relevant_conversations: JSONB (array of conversation IDs)
- created_at: TIMESTAMP
```

## 🎨 UI Screenshots

### 1. Chat Interface
- Real-time messaging with AI
- Clean, modern design similar to ChatGPT
- Message history with timestamps
- New conversation and end conversation buttons

### 2. Conversations Dashboard
- Grid view of all conversations
- Search and filter capabilities
- Status indicators (active/ended)
- Quick access to view details

### 3. Conversation Intelligence
- Query interface for asking about past chats
- AI-generated responses with relevant excerpts
- Relevance scoring for matched conversations
- Date range and topic filtering

## 🧪 Testing

### Backend Tests
```bash
cd backend
python manage.py test
```

### Frontend Tests
```bash
cd frontend
npm test
```

### Sample Test Data

Create sample conversations:
```bash
python manage.py shell

from conversations.models import Conversation, Message
from datetime import datetime

# Create conversation
conv = Conversation.objects.create(
    title="Test Conversation",
    status="active"
)

# Add messages
Message.objects.create(
    conversation=conv,
    content="Hello, AI!",
    sender="user"
)

Message.objects.create(
    conversation=conv,
    content="Hello! How can I help you?",
    sender="ai"
)
```

## 🚀 Deployment

### Backend Deployment (Heroku/Railway)
1. Update `DEBUG=False` in settings
2. Configure `ALLOWED_HOSTS`
3. Set up production database
4. Collect static files: `python manage.py collectstatic`
5. Use gunicorn: `gunicorn chat_project.wsgi`

### Frontend Deployment (Vercel/Netlify)
1. Build: `npm run build`
2. Deploy `dist/` folder
3. Configure API base URL for production

## 🔐 Security Considerations

- Keep API keys in `.env` (never commit)
- Use HTTPS in production
- Implement rate limiting
- Add authentication/authorization
- Sanitize user inputs
- Use CORS properly

## 🎯 Future Enhancements

- [ ] User authentication and multi-user support
- [ ] Real-time WebSocket connections
- [ ] Voice input/output
- [ ] Export conversations (PDF, JSON, Markdown)
- [ ] Conversation sharing with unique links
- [ ] Dark mode toggle
- [ ] Analytics dashboard
- [ ] Message reactions and bookmarking
- [ ] Conversation threading

## 📝 Code Quality

- Clean, readable code with comments
- OOP principles throughout
- Proper error handling
- Type hints where applicable
- Modular architecture
- Separation of concerns

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## 📄 License

MIT License - feel free to use for your projects

## 👥 Author

Your Name - Full Stack Developer Assignment

## 🙏 Acknowledgments

- OpenAI for GPT API
- Anthropic for Claude API
- Google for Gemini API
- Django and React communities

---

**Note**: This project was created as part of a technical assessment. While AI tools were used for assistance, all code has been reviewed, understood, and can be explained and modified as needed.
