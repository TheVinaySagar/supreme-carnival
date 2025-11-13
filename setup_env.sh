#!/bin/bash

# Setup script for TradingAgents
# Creates .env file from template and installs dependencies

set -e

echo "=================================================="
echo "  TradingAgents Environment Setup"
echo "=================================================="
echo ""

# Check if .env already exists
if [ -f .env ]; then
    echo "⚠️  .env file already exists!"
    read -p "Do you want to overwrite it? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Keeping existing .env file."
        exit 0
    fi
fi

# Copy template
echo "📝 Creating .env file from template..."
cp .env.example .env

echo ""
echo "✅ .env file created!"
echo ""
echo "=================================================="
echo "  Configure Your API Keys"
echo "=================================================="
echo ""
echo "Please edit the .env file and add your API keys:"
echo ""
echo "  nano .env"
echo "  # or"
echo "  vim .env"
echo "  # or use any text editor"
echo ""
echo "Required keys:"
echo "  - OPENAI_API_KEY (for LLM features)"
echo ""
echo "Optional keys:"
echo "  - ANTHROPIC_API_KEY (for Claude)"
echo "  - GOOGLE_API_KEY (for Gemini)"
echo "  - FINNHUB_API_KEY (for market data)"
echo "  - REDDIT_* (for social sentiment)"
echo ""
echo "=================================================="
echo ""

read -p "Press Enter to open .env file in nano editor (or Ctrl+C to skip)..."
nano .env || true

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Install dependencies: pip install -r requirements.txt"
echo "  2. Test installation: python test_rl_basics.py"
echo "  3. Start training: python -m tradingagents.rl.train_rl_agent --tickers AAPL"
echo ""
