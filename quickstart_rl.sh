#!/bin/bash

# Quick Start Script for TradingAgents RL Module
# This script helps you quickly train and evaluate an RL trading agent

set -e  # Exit on error

echo "===================================="
echo "TradingAgents RL Quick Start"
echo "===================================="
echo ""

# Check if OPENAI_API_KEY is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ Error: OPENAI_API_KEY environment variable is not set!"
    echo ""
    echo "Please set it using:"
    echo "  export OPENAI_API_KEY='your-api-key-here'"
    echo ""
    echo "Or add it to your ~/.bashrc:"
    echo "  echo 'export OPENAI_API_KEY=\"your-api-key-here\"' >> ~/.bashrc"
    echo "  source ~/.bashrc"
    exit 1
fi

echo "✅ OPENAI_API_KEY is set"
echo ""

# Check if PyTorch is installed
echo "Checking for PyTorch..."
if python -c "import torch" 2>/dev/null; then
    echo "✅ PyTorch is installed"
    TORCH_VERSION=$(python -c "import torch; print(torch.__version__)")
    echo "   Version: $TORCH_VERSION"
else
    echo "❌ PyTorch is not installed"
    echo ""
    echo "Installing PyTorch (CPU version)..."
    pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
    echo "✅ PyTorch installed"
fi

echo ""
echo "===================================="
echo "Step 1: Testing RL Components"
echo "===================================="
echo ""

python test_rl_basics.py

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Tests failed! Please check the errors above."
    exit 1
fi

echo ""
echo "===================================="
echo "Step 2: Training RL Agent (Quick)"
echo "===================================="
echo ""
echo "Training on AAPL with 10 episodes (fast test)..."
echo ""

python -m tradingagents.rl.train_rl_agent \
    --tickers AAPL \
    --start-date 2022-01-01 \
    --end-date 2023-12-31 \
    --num-episodes 10 \
    --initial-capital 10000 \
    --checkpoint-freq 5 \
    --model-name rl_trader_quickstart

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Training failed! Please check the errors above."
    exit 1
fi

echo ""
echo "===================================="
echo "Step 3: Evaluating RL Agent"
echo "===================================="
echo ""

python -m tradingagents.rl.evaluate_rl_agent \
    --model-path tradingagents/rl/models/rl_trader_quickstart_final.pt \
    --tickers AAPL \
    --start-date 2024-01-01 \
    --end-date 2024-12-31 \
    --initial-capital 10000 \
    --output-dir ./eval_results/quickstart

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Evaluation failed! Please check the errors above."
    exit 1
fi

echo ""
echo "===================================="
echo "✅ Quick Start Complete!"
echo "===================================="
echo ""
echo "Your RL agent has been trained and evaluated!"
echo ""
echo "📁 Files created:"
echo "  - Model: tradingagents/rl/models/rl_trader_quickstart_final.pt"
echo "  - Training logs: tradingagents/rl/logs/training_log.json"
echo "  - Evaluation: eval_results/quickstart/AAPL_evaluation_report.txt"
echo ""
echo "📖 Next steps:"
echo "  1. Check the evaluation report:"
echo "     cat eval_results/quickstart/AAPL_evaluation_report.txt"
echo ""
echo "  2. Train for longer (better results):"
echo "     python -m tradingagents.rl.train_rl_agent --num-episodes 100"
echo ""
echo "  3. Train on multiple tickers:"
echo "     python -m tradingagents.rl.train_rl_agent --tickers AAPL TSLA MSFT"
echo ""
echo "  4. Read the full guide:"
echo "     cat RL_GUIDE.md"
echo ""
echo "Happy Trading! 🚀"
