#!/usr/bin/env bash
# Setup script for Bewerbungs Agent

set -e

echo "🚀 Setting up Bewerbungs Agent..."

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.11"

echo "Python version: $python_version"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "✅ Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Install package in development mode
echo "📦 Installing bewerbungs-agent in development mode..."
pip install -e .

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your configuration"
fi

# Initialize database
echo "🗄️  Initializing database..."
bewerbungs-agent init

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Configure .env with your settings"
echo "3. Set up Gmail API credentials (see README.md)"
echo "4. Create a user: bewerbungs-agent create-user --email your@email.com"
echo "5. Create a profile: bewerbungs-agent create-profile --user-id 1 --name 'Your Name' --skills 'Python,SQL' --cv-text 'path/to/cv.txt'"
echo ""
echo "Run 'bewerbungs-agent --help' for all commands"
