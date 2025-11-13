# 🚀 EXECUTION INSTRUCTIONS - TradingAgents RL Module

## ✅ Prerequisites Check

Before starting, ensure you have:

1. **Python 3.8+** installed
2. **OpenAI API Key** (you mentioned you have premium)
3. **Git** (to clone/manage the repository)

## 📦 Step 1: Install Dependencies

### Install PyTorch

Choose based on your system:

**For CPU (Recommended for testing):**
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
```

**For GPU with CUDA 11.8:**
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

**For GPU with CUDA 12.1:**
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

### Install Other Requirements

```bash
cd /home/vinay/Documents/TradingAgents
pip install -r requirements.txt
```

## 🔑 Step 2: Configure API Key

Set your OpenAI API key:

```bash
export OPENAI_API_KEY="your-openai-api-key-here"
```

**To make it permanent**, add to your `~/.bashrc`:
```bash
echo 'export OPENAI_API_KEY="your-key-here"' >> ~/.bashrc
source ~/.bashrc
```

## 🧪 Step 3: Test the Installation

Run the test script to verify everything works:

```bash
cd /home/vinay/Documents/TradingAgents
python test_rl_basics.py
```

**Expected output:**
```
=== Testing RL State Encoder ===
RL State Encoder initialized with state dimension: 6168
Initializing state encoder...
Market embedding shape: 1536
...
✅ State encoder working correctly!
```

## 🎯 Step 4: Quick Start (Automated)

Run the automated quickstart script:

```bash
cd /home/vinay/Documents/TradingAgents
./quickstart_rl.sh
```

This will:
1. ✅ Verify your setup
2. 🧪 Run tests
3. 🎓 Train an RL agent (10 episodes on AAPL)
4. 📊 Evaluate the agent and compare with baselines

**Duration:** ~5-15 minutes depending on your system

## 📚 Step 5: Manual Training (Recommended)

### Option A: Fast Training (No LLM Features)

Train on a single ticker without LLM-generated features (faster):

```bash
python -m tradingagents.rl.train_rl_agent \
    --tickers AAPL \
    --start-date 2020-01-01 \
    --end-date 2023-12-31 \
    --num-episodes 50 \
    --initial-capital 10000 \
    --model-name rl_trader_fast
```

**Training time:** ~10-30 minutes

### Option B: Full Training (With LLM Features)

Train with rich LLM-generated features (slower but more powerful):

```bash
python -m tradingagents.rl.train_rl_agent \
    --tickers AAPL TSLA MSFT \
    --start-date 2020-01-01 \
    --end-date 2023-12-31 \
    --num-episodes 100 \
    --use-llm-features \
    --initial-capital 10000 \
    --checkpoint-freq 10 \
    --model-name rl_trader_full
```

**Training time:** ~1-3 hours (uses OpenAI API calls)

### Training Arguments Explained

```bash
--tickers AAPL TSLA         # Stocks to train on (space-separated)
--start-date 2020-01-01     # Training start date
--end-date 2023-12-31       # Training end date
--num-episodes 100          # How many training episodes (more = better)
--initial-capital 10000     # Starting cash amount
--use-llm-features          # Enable LLM reports (slower, richer state)
--checkpoint-freq 10        # Save model every N episodes
--model-name my_agent       # Name for saved model
--batch-size 32             # Training batch size
--buffer-size 10000         # Experience replay buffer size
```

## 📊 Step 6: Monitor Training

### Watch Training Progress

During training, you'll see output like:

```
Episode 10/100
  Training on AAPL...
    Return: 5.23%, Reward: 123.45, Epsilon: 0.950

=========================================================
Episode 10 Summary:
=========================================================
Total Return: 5.23%
Final Portfolio Value: $10523.45
Total Reward: 123.45
Average Reward: 0.52
Actions - SELL: 10, HOLD: 75, BUY: 15
Epsilon: 0.9500
Avg Loss: 0.0042
=========================================================
```

### Check Training Logs

```bash
cat tradingagents/rl/logs/training_log.json
```

Or use Python to analyze:

```python
import json
import pandas as pd

with open('tradingagents/rl/logs/training_log.json') as f:
    logs = json.load(f)

df = pd.DataFrame(logs)
print(df[['episode', 'total_return_pct', 'avg_reward', 'epsilon']])
```

## 🎓 Step 7: Evaluate Your Agent

After training, evaluate performance:

```bash
python -m tradingagents.rl.evaluate_rl_agent \
    --model-path tradingagents/rl/models/rl_trader_fast_final.pt \
    --tickers AAPL \
    --start-date 2024-01-01 \
    --end-date 2024-12-31 \
    --initial-capital 10000 \
    --output-dir ./eval_results/my_evaluation
```

### View Results

```bash
cat eval_results/my_evaluation/AAPL_evaluation_report.txt
```

**Example output:**
```
================================================================================
EVALUATION RESULTS: AAPL
================================================================================
                Return (%)  Sharpe Ratio  Max Drawdown (%)  Win Rate (%)  ...
RL Agent             12.45          1.23             -8.50         65.00
Buy and Hold          8.30          0.95            -12.30          0.00
Random               -2.10         -0.15            -25.40         48.00
================================================================================
```

## 🎨 Step 8: Use Your Trained Agent

### In Python Code

```python
from tradingagents.rl.rl_trader import RLTradingAgent
from tradingagents.rl.state_encoder import TradingStateEncoder
from tradingagents.default_config import DEFAULT_CONFIG

# Setup
config = DEFAULT_CONFIG.copy()
config["llm_provider"] = "openai"

# Load agent
state_encoder = TradingStateEncoder(config)
agent = RLTradingAgent(state_dim=6168, action_dim=3)
agent.load("tradingagents/rl/models/rl_trader_fast_final.pt")
agent.set_eval_mode()

# Prepare state
state_dict = {
    "market_data": {
        "price": 175.50,
        "rsi": 52.3,
        "sma_50": 172.0,
        # ... other indicators
    },
    "portfolio_state": {
        "cash": 5000,
        "holdings": 50,
        "total_value": 13775,
        # ...
    },
    "trade_date": "2024-12-01",
    "market_report": "Technical indicators show...",
    "news_report": "Recent developments...",
    # ... other reports
}

# Get decision
state_vector = state_encoder.encode_state(state_dict)
action = agent.get_action(state_vector, training=False)

print(f"RL Decision: {['SELL', 'HOLD', 'BUY'][action]}")
```

## 🔧 Advanced Usage

### Continue Training from Checkpoint

```python
# In your training script or interactive session
from tradingagents.rl.rl_trader import RLTradingAgent

agent = RLTradingAgent(state_dim=6168, action_dim=3)
agent.load("tradingagents/rl/models/checkpoints/rl_trader_episode_50.pt")

# Continue training...
```

### Custom Reward Function

Edit `tradingagents/rl/reward_calculator.py`:

```python
class RewardCalculator:
    def __init__(
        self,
        profit_weight: float = 2.0,      # More emphasis on profit
        risk_weight: float = 0.5,        # Higher risk aversion
        alignment_weight: float = 0.0,   # Disable LLM alignment
        consistency_weight: float = 0.1
    ):
        # ...
```

### Train on Your Custom Data

```bash
python -m tradingagents.rl.train_rl_agent \
    --tickers YOUR_TICKER_1 YOUR_TICKER_2 \
    --start-date YYYY-MM-DD \
    --end-date YYYY-MM-DD \
    --num-episodes 200 \
    --model-name my_custom_agent
```

## 🐛 Troubleshooting

### Problem: "Import torch could not be resolved"

**Solution:**
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
```

### Problem: "OPENAI_API_KEY not found"

**Solution:**
```bash
export OPENAI_API_KEY="sk-your-key-here"
# Or add to ~/.bashrc for persistence
```

### Problem: Training is very slow

**Solutions:**
1. Don't use `--use-llm-features` flag
2. Reduce `--num-episodes`
3. Train on fewer tickers
4. Use CPU version of PyTorch

### Problem: Agent only learns to HOLD

**Solutions:**
1. Check your data has enough volatility
2. Increase training episodes (try 100-200)
3. Adjust reward weights (increase profit_weight)
4. Train on multiple diverse tickers

### Problem: Out of memory

**Solutions:**
1. Reduce `--batch-size` (try 16 or 8)
2. Reduce `--buffer-size` (try 5000)
3. Use CPU instead of GPU
4. Train on shorter time periods

## 📊 Performance Tips

### For Best Results:

1. **Train longer:** 100-200 episodes minimum
2. **Multiple tickers:** Train on 3-5 diverse stocks
3. **Longer history:** Use 3-5 years of training data
4. **Validate properly:** Test on completely unseen time periods
5. **Tune hyperparameters:** Experiment with learning rate, gamma, epsilon decay

### Expected Performance:

- **Training (50 episodes):** Agent should start seeing positive returns
- **Training (100+ episodes):** Agent should outperform random strategy
- **Well-trained (200+ episodes):** Agent may compete with or beat buy-and-hold

## 🎯 Recommended Workflow

### Day 1: Setup and Quick Test
```bash
# Install dependencies
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt

# Test installation
python test_rl_basics.py

# Quick training test (10 episodes)
./quickstart_rl.sh
```

### Day 2: Proper Training
```bash
# Train for real (50-100 episodes)
python -m tradingagents.rl.train_rl_agent \
    --tickers AAPL MSFT GOOGL \
    --start-date 2020-01-01 \
    --end-date 2023-12-31 \
    --num-episodes 100 \
    --model-name rl_trader_v1
```

### Day 3: Evaluation and Comparison
```bash
# Evaluate on test period
python -m tradingagents.rl.evaluate_rl_agent \
    --model-path tradingagents/rl/models/rl_trader_v1_final.pt \
    --tickers AAPL MSFT GOOGL \
    --start-date 2024-01-01 \
    --end-date 2024-12-31

# Compare with LLM system
# ... (run traditional TradingAgents)
```

## 📚 Full Documentation

For complete details, see:
- **RL_GUIDE.md** - Complete guide with all features
- **tradingagents/rl/** - Source code with inline documentation

## 🤝 Need Help?

1. Check the troubleshooting section above
2. Review RL_GUIDE.md for detailed explanations
3. Check GitHub issues
4. Join the Discord community

## 🎉 You're Ready!

Start with the quickstart script:
```bash
./quickstart_rl.sh
```

Then move on to full training once you're comfortable.

**Happy Training! 🚀**
