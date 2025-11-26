#!/bin/bash
# Context Vault - Development Environment Setup Script

set -e  # Exit on error

echo "🔒 Context Vault - Development Setup"
echo "======================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Print step
step() {
    echo -e "${GREEN}[✓]${NC} $1"
}

# Print warning
warn() {
    echo -e "${YELLOW}[!]${NC} $1"
}

# Print error
error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Check prerequisites
echo "Checking prerequisites..."
echo ""

if ! command_exists docker; then
    error "Docker not found. Please install Docker Desktop from docker.com"
    exit 1
fi
step "Docker installed"

if ! command_exists python3; then
    error "Python 3 not found. Please install Python 3.11+ from python.org"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
if (( $(echo "$PYTHON_VERSION < 3.11" | bc -l) )); then
    error "Python 3.11+ required (found $PYTHON_VERSION)"
    exit 1
fi
step "Python 3.11+ installed ($PYTHON_VERSION)"

if ! command_exists node; then
    error "Node.js not found. Please install Node.js 18+ from nodejs.org"
    exit 1
fi

NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
if (( NODE_VERSION < 18 )); then
    error "Node.js 18+ required (found v$NODE_VERSION)"
    exit 1
fi
step "Node.js 18+ installed (v$(node --version))"

if ! command_exists git; then
    warn "Git not found (optional but recommended)"
else
    step "Git installed"
fi

echo ""

# Check Ollama
echo "Checking Ollama..."
if ! command_exists ollama; then
    warn "Ollama not found"
    echo "   Install from: https://ollama.com"
    echo "   Then run: ollama pull llama3.1:8b"
else
    step "Ollama installed"

    # Check if Ollama is running
    if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
        step "Ollama server running"

        # Check for llama3.1:8b model
        if ollama list | grep -q "llama3.1:8b"; then
            step "llama3.1:8b model installed"
        else
            warn "llama3.1:8b model not found"
            echo "   Run: ollama pull llama3.1:8b"
        fi
    else
        warn "Ollama server not running"
        echo "   Start with: ollama serve"
    fi
fi

echo ""

# Setup backend
echo "Setting up backend..."
cd backend

if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
    step "Virtual environment created"
else
    step "Virtual environment exists"
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing Python dependencies..."
pip install --upgrade pip >/dev/null 2>&1
pip install -r requirements.txt >/dev/null 2>&1
step "Python dependencies installed"

cd ..

echo ""

# Setup frontend
echo "Setting up frontend..."
cd frontend

if [ ! -d "node_modules" ]; then
    echo "Installing Node.js dependencies..."
    npm install >/dev/null 2>&1
    step "Node.js dependencies installed"
else
    step "Node.js dependencies exist"
fi

cd ..

echo ""

# Setup environment variables
echo "Setting up environment variables..."

if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        step ".env created from .env.example"

        warn "IMPORTANT: Edit .env file with your actual credentials"
        echo "   Required:"
        echo "   - APP_SECRET_KEY (run: openssl rand -base64 32)"
        echo "   - JWT_SECRET_KEY (run: openssl rand -base64 32)"
        echo ""
        echo "   Already configured:"
        echo "   - DATABASE_URL (Railway Postgres)"
        echo "   - GOOGLE_OAUTH_CLIENT_ID"
        echo "   - GOOGLE_OAUTH_CLIENT_SECRET"
        echo "   - EPIC_CLIENT_ID"
    else
        error ".env.example not found"
        exit 1
    fi
else
    step ".env file exists"
fi

echo ""

# Check database connection
echo "Checking database connection..."
if cd backend && source venv/bin/activate && python -c "
import os
from sqlalchemy import create_engine
try:
    engine = create_engine(os.getenv('DATABASE_URL', ''))
    with engine.connect() as conn:
        conn.execute('SELECT 1')
    print('✓ Database connection successful')
    exit(0)
except Exception as e:
    print(f'✗ Database connection failed: {e}')
    exit(1)
" 2>/dev/null; then
    step "Database connection successful"
    cd ..
else
    warn "Database connection failed (check DATABASE_URL in .env)"
    cd ..
fi

echo ""

# Run database migrations
echo "Running database migrations..."
cd backend
source venv/bin/activate
if alembic current >/dev/null 2>&1; then
    alembic upgrade head >/dev/null 2>&1
    step "Database migrations completed"
else
    warn "Alembic not configured yet (normal for initial setup)"
fi
cd ..

echo ""

# Summary
echo "======================================"
echo -e "${GREEN}✓ Setup complete!${NC}"
echo "======================================"
echo ""
echo "Next steps:"
echo ""
echo "1. Generate secret keys and update .env:"
echo "   openssl rand -base64 32  # Use for APP_SECRET_KEY"
echo "   openssl rand -base64 32  # Use for JWT_SECRET_KEY"
echo ""
echo "2. Start Ollama (if not already running):"
echo "   ollama serve"
echo ""
echo "3. Start the development servers:"
echo ""
echo "   Option A: Using Docker Compose (recommended):"
echo "   docker-compose up"
echo ""
echo "   Option B: Manual start:"
echo "   # Backend (terminal 1):"
echo "   cd backend && source venv/bin/activate"
echo "   uvicorn app.main:app --reload"
echo ""
echo "   # Frontend (terminal 2):"
echo "   cd frontend && npm run dev"
echo ""
echo "4. Access the application:"
echo "   Frontend: http://localhost:5173"
echo "   Backend:  http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "For detailed documentation, see: docs/"
echo ""
