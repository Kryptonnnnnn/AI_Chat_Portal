
#!/bin/bash
# setup.sh - Complete automated setup script

echo "🚀 AI Chat Portal - Automated Setup"
echo "===================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed. Please install Python 3.8+${NC}"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js is not installed. Please install Node.js 16+${NC}"
    exit 1
fi

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo -e "${YELLOW}⚠️  PostgreSQL not found. Make sure PostgreSQL is installed and running.${NC}"
fi

echo -e "${GREEN}✓ Prerequisites check passed${NC}"
echo ""

# Create main project directory structure
echo "📁 Creating project structure..."
mkdir -p backend/chat_project backend/conversations backend/ai_module
mkdir -p frontend/src/components frontend/src/services

# ============================================
# BACKEND SETUP
# ============================================
echo ""
echo "📦 Setting up Backend..."
cd backend

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Create requirements.txt
cat > requirements.txt << 'EOF'
Django==4.2.7
djangorestframework==3.14.0
psycopg2-binary==2.9.9
python-dotenv==1.0.0
django-cors-headers==4.3.1
openai==1.3.0
anthropic==0.7.0
google-generativeai==0.3.1
sentence-transformers==2.2.2
numpy==1.24.3
scikit-learn==1.3.2
EOF

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file
echo "Creating .env file..."
cat > .env << 'EOF'
SECRET_KEY=django-insecure-change-this-in-production-$(openssl rand -base64 32)
DEBUG=True
DATABASE_NAME=ai_chat_portal
DATABASE_USER=postgres
DATABASE_PASSWORD=your_password_here
DATABASE_HOST=localhost
DATABASE_PORT=5432

# AI API Keys (Optional - system works without them using mock responses)
OPENAI_API_KEY=your-openai-key-here
ANTHROPIC_API_KEY=your-anthropic-key-here
GEMINI_API_KEY=your-gemini-key-here
EOF

# Initialize Django project if not exists
if [ ! -f "manage.py" ]; then
    echo "Initializing Django project..."
    django-admin startproject chat_project .
fi

# Create Django app if not exists
if [ ! -f "conversations/models.py" ]; then
    echo "Creating Django app..."
    python manage.py startapp conversations
fi

# Create __init__ files for ai_module
touch ai_module/__init__.py

echo ""
echo -e "${GREEN}✓ Backend setup complete${NC}"

# ============================================
# FRONTEND SETUP
# ============================================
cd ..
echo ""
echo "🎨 Setting up Frontend..."

# Initialize Vite React project if not exists
if [ ! -d "frontend/node_modules" ]; then
    cd frontend
    
    # Create package.json
    cat > package.json << 'EOF'
{
  "name": "ai-chat-portal-frontend",
  "private": true,
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "axios": "^1.6.2",
    "lucide-react": "^0.294.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.37",
    "@types/react-dom": "^18.2.15",
    "@vitejs/plugin-react": "^4.2.0",
    "autoprefixer": "^10.4.16",
    "postcss": "^8.4.31",
    "tailwindcss": "^3.3.5",
    "vite": "^5.0.0"
  }
}
EOF
    
    echo "Installing Node.js dependencies..."
    npm install
    
    # Initialize Tailwind
    echo "Configuring Tailwind CSS..."
    npx tailwindcss init -p
    
    cd ..
fi

echo ""
echo -e "${GREEN}✓ Frontend setup complete${NC}"

# ============================================
# CREATE .GITIGNORE
# ============================================
echo ""
echo "📝 Creating .gitignore..."
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/
*.egg-info/
dist/
build/
*.egg

# Django
*.log
db.sqlite3
db.sqlite3-journal
media/
staticfiles/
.env

# Node
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
dist/
.cache/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store

# Testing
.coverage
htmlcov/
.pytest_cache/

# Environment
.env.local
.env.*.local
EOF

echo -e "${GREEN}✓ .gitignore created${NC}"

# ============================================
# DATABASE SETUP
# ============================================
echo ""
echo "🗄️  Database Setup"
echo "=================="
echo ""
echo "Please run the following commands to set up PostgreSQL:"
echo ""
echo "1. Create database:"
echo "   psql -U postgres -c \"CREATE DATABASE ai_chat_portal;\""
echo ""
echo "2. Or manually:"
echo "   psql -U postgres"
echo "   CREATE DATABASE ai_chat_portal;"
echo "   \q"
echo ""

# ============================================
# FINAL INSTRUCTIONS
# ============================================
echo ""
echo "============================================"
echo -e "${GREEN}✅ Setup Complete!${NC}"
echo "============================================"
echo ""
echo "Next steps:"
echo ""
echo "1. Update backend/.env with your configuration:"
echo "   - Database password"
echo "   - API keys (optional)"
echo ""
echo "2. Create PostgreSQL database:"
echo "   createdb ai_chat_portal"
echo ""
echo "3. Run Django migrations:"
echo "   cd backend"
echo "   source venv/bin/activate  # On Windows: venv\\Scripts\\activate"
echo "   python manage.py migrate"
echo "   python manage.py createsuperuser  # Optional"
echo ""
echo "4. Start the backend server:"
echo "   python manage.py runserver"
echo "   Backend will run on: http://localhost:8000"
echo ""
echo "5. In a new terminal, start the frontend:"
echo "   cd frontend"
echo "   npm run dev"
echo "   Frontend will run on: http://localhost:5173"
echo ""
echo "6. Access the application:"
echo "   Open http://localhost:5173 in your browser"
echo ""
echo "7. Admin panel (optional):"
echo "   http://localhost:8000/admin"
echo ""
echo -e "${YELLOW}Note: The system works without API keys using mock responses.${NC}"
echo -e "${YELLOW}For full AI functionality, add API keys to backend/.env${NC}"
echo ""
echo "Happy coding! 🚀"
