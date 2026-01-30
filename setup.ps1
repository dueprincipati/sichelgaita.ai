# Pandada.AI Monorepo Setup Script for Windows
# Run with: .\setup.ps1

Write-Host "🚀 Setting up Pandada.AI Monorepo..." -ForegroundColor Cyan
Write-Host ""

# Check prerequisites
Write-Host "Checking prerequisites..." -ForegroundColor Yellow

# Check Node.js
if (!(Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Error: Node.js is required but not installed." -ForegroundColor Red
    Write-Host "   Please install Node.js 18.17.0 or higher from https://nodejs.org" -ForegroundColor Red
    exit 1
}

# Check Python
if (!(Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Error: Python 3 is required but not installed." -ForegroundColor Red
    Write-Host "   Please install Python 3.11 or higher from https://python.org" -ForegroundColor Red
    exit 1
}

# Check Poetry
if (!(Get-Command poetry -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Error: Poetry is required but not installed." -ForegroundColor Red
    Write-Host "   Please install Poetry from https://python-poetry.org/docs/#installation" -ForegroundColor Red
    exit 1
}

Write-Host "✅ All prerequisites installed" -ForegroundColor Green
Write-Host ""

# Check versions
$nodeVersion = node --version
$pythonVersion = python --version
$poetryVersion = poetry --version

Write-Host "Detected versions:" -ForegroundColor Cyan
Write-Host "  Node.js: $nodeVersion"
Write-Host "  Python: $pythonVersion"
Write-Host "  Poetry: $poetryVersion"
Write-Host ""

# Copy environment file
if (!(Test-Path .env)) {
    Write-Host "📝 Creating .env file from .env.example..." -ForegroundColor Yellow
    Copy-Item .env.example .env
    Write-Host "✅ Created .env file" -ForegroundColor Green
    Write-Host "⚠️  IMPORTANT: Please edit .env and configure your API keys before running the application" -ForegroundColor Yellow
    Write-Host ""
} else {
    Write-Host "ℹ️  .env file already exists, skipping..." -ForegroundColor Cyan
    Write-Host ""
}

# Install root dependencies
Write-Host "📦 Installing root dependencies..." -ForegroundColor Yellow
npm install
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Root dependencies installed" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to install root dependencies" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Setup frontend
Write-Host "🎨 Setting up frontend..." -ForegroundColor Yellow
Set-Location frontend
npm install
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Frontend dependencies installed" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to install frontend dependencies" -ForegroundColor Red
    exit 1
}
Set-Location ..
Write-Host ""

# Setup backend
Write-Host "🐍 Setting up backend..." -ForegroundColor Yellow
Set-Location backend
poetry install
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Backend dependencies installed" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to install backend dependencies" -ForegroundColor Red
    exit 1
}
Set-Location ..
Write-Host ""

# Summary
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "✅ Setup complete! Your Pandada.AI monorepo is ready." -ForegroundColor Green
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Edit .env file and configure your API keys:"
Write-Host "     - NEXT_PUBLIC_SUPABASE_URL"
Write-Host "     - NEXT_PUBLIC_SUPABASE_ANON_KEY"
Write-Host "     - GEMINI_API_KEY"
Write-Host ""
Write-Host "  2. Start the development servers:"
Write-Host "     npm run dev"
Write-Host ""
Write-Host "  3. Access the applications:"
Write-Host "     - Frontend: http://localhost:3000"
Write-Host "     - Backend API: http://localhost:8000"
Write-Host "     - API Docs: http://localhost:8000/docs"
Write-Host ""
Write-Host "Happy coding! 🚀" -ForegroundColor Cyan
