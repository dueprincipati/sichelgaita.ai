#!/bin/bash

echo "🚀 Setting up Sichelgaita.AI Monorepo..."
echo ""

# Check prerequisites
echo "Checking prerequisites..."

command -v node >/dev/null 2>&1 || { 
    echo "❌ Error: Node.js is required but not installed."
    echo "   Please install Node.js 18.17.0 or higher from https://nodejs.org"
    exit 1
}

command -v python3 >/dev/null 2>&1 || { 
    echo "❌ Error: Python 3 is required but not installed."
    echo "   Please install Python 3.11 or higher from https://python.org"
    exit 1
}

command -v poetry >/dev/null 2>&1 || { 
    echo "❌ Error: Poetry is required but not installed."
    echo "   Please install Poetry from https://python-poetry.org/docs/#installation"
    exit 1
}

echo "✅ All prerequisites installed"
echo ""

# Check versions
NODE_VERSION=$(node --version)
PYTHON_VERSION=$(python3 --version)
POETRY_VERSION=$(poetry --version)

echo "Detected versions:"
echo "  Node.js: $NODE_VERSION"
echo "  Python: $PYTHON_VERSION"
echo "  Poetry: $POETRY_VERSION"
echo ""

# Copy environment file
if [ ! -f .env ]; then
    echo "📝 Creating .env file from .env.example..."
    cp .env.example .env
    echo "✅ Created .env file"
    echo "⚠️  IMPORTANT: Please edit .env and configure your API keys before running the application"
    echo ""
else
    echo "ℹ️  .env file already exists, skipping..."
    echo ""
fi

# Install root dependencies
echo "📦 Installing root dependencies..."
npm install
if [ $? -eq 0 ]; then
    echo "✅ Root dependencies installed"
else
    echo "❌ Failed to install root dependencies"
    exit 1
fi
echo ""

# Setup frontend
echo "🎨 Setting up frontend..."
cd frontend
npm install
if [ $? -eq 0 ]; then
    echo "✅ Frontend dependencies installed"
else
    echo "❌ Failed to install frontend dependencies"
    exit 1
fi
cd ..
echo ""

# Setup backend
echo "🐍 Setting up backend..."
cd backend
poetry install
if [ $? -eq 0 ]; then
    echo "✅ Backend dependencies installed"
else
    echo "❌ Failed to install backend dependencies"
    exit 1
fi
cd ..
echo ""

# Summary
echo "════════════════════════════════════════════════════════════"
echo "✅ Setup complete! Your Pandada.AI monorepo is ready."
echo "════════════════════════════════════════════════════════════"
echo ""
echo "Next steps:"
echo "  1. Edit .env file and configure your API keys:"
echo "     - NEXT_PUBLIC_SUPABASE_URL"
echo "     - NEXT_PUBLIC_SUPABASE_ANON_KEY"
echo "     - GEMINI_API_KEY"
echo ""
echo "  2. Start the development servers:"
echo "     npm run dev"
echo ""
echo "  3. Access the applications:"
echo "     - Frontend: http://localhost:3000"
echo "     - Backend API: http://localhost:8000"
echo "     - API Docs: http://localhost:8000/docs"
echo ""
echo "Happy coding! 🚀"
