# TradingAgents RL Module - Complete Guide

## 🎯 Overview

This guide covers the complete Reinforcement Learning (RL) module integrated into TradingAgents. The RL agent learns to make trading decisions (BUY/SELL/HOLD) by training on historical data and can work alongside or independently from the LLM-based trading system.

## 🏗️ Architecture

### **Option A: RL as Parallel Decision-Maker** (Implemented)

The RL agent runs in parallel with the LLM-based system:
- RL agent makes independent trading decisions
- Can optionally use LLM-generated features for richer state representation
- Learns from both profit rewards and alignment with expert LLM decisions
- Gradually becomes more independent as training progresses

### Components

```
tradingagents/rl/
├── __init__.py                 # Module exports
├── state_encoder.py            # Converts market data + LLM reports → RL state vectors
├── replay_buffer.py            # Stores experiences for off-policy learning
├── reward_calculator.py        # Multi-component reward function
├── rl_trader.py               # DQN agent implementation
├── rl_environment.py          # Gym-like trading environment
├── train_rl_agent.py          # Training script
├── evaluate_rl_agent.py       # Evaluation and comparison script
├── models/                    # Saved model checkpoints
│   └── checkpoints/
└── logs/                      # Training logs
```

## 📦 Installation

### 1. Install PyTorch

**For CPU (recommended for testing):**
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
```

**For GPU (CUDA 11.8):**
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

**For GPU (CUDA 12.1):**
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

### 2. Install Other Dependencies

```bash
cd /home/vinay/Documents/TradingAgents
pip install -r requirements.txt
```

### 3. Set Up API Keys

Make sure your `.env` file contains:
```bash
export OPENAI_API_KEY="your-openai-api-key-here"
```

Or set it in your shell:
```bash
export OPENAI_API_KEY="your-openai-api-key-here"
```

## 🚀 Quick Start

### Training Your First RL Agent

**Basic training (fast, no LLM features):**
```bash
python -m tradingagents.rl.train_rl_agent \
    --tickers AAPL \
    --start-date 2020-01-01 \
    --end-date 2023-12-31 \
    --num-episodes 50 \
    --initial-capital 10000
```

**Advanced training (with LLM features, slower but richer):**
```bash
python -m tradingagents.rl.train_rl_agent \
    --tickers AAPL TSLA MSFT \
    --start-date 2020-01-01 \
    --end-date 2023-12-31 \
    --num-episodes 100 \
    --use-llm-features \
    --initial-capital 10000 \
    --checkpoint-freq 10
```

### Evaluating Your Agent

```bash
python -m tradingagents.rl.evaluate_rl_agent \
    --model-path tradingagents/rl/models/rl_trader_final.pt \
    --tickers AAPL \
    --start-date 2024-01-01 \
    --end-date 2024-12-31 \
    --initial-capital 10000 \
    --output-dir ./eval_results
```

## 📊 Understanding the RL System

### State Space (Input to RL Agent)

The RL agent observes a **fixed-size vector** (~6,168 dimensions) containing:

1. **Market Features (15 dims):**
   - Current price, SMA (50, 200), EMA (10)
   - RSI, MACD, Bollinger Bands, ATR
   - Volume, VWMA, price momentum

2. **Portfolio Features (5 dims):**
   - Cash ratio, position ratio
   - Total value (log-scaled)
   - Unrealized P&L, total return

3. **Temporal Features (4 dims):**
   - Day of week, month, quarter, day of year

4. **Text Embeddings (6,144 dims = 4 × 1,536):**
   - Market report embedding (OpenAI text-embedding-3-small)
   - Social sentiment embedding
   - News analysis embedding
   - Fundamentals report embedding

### Action Space (Output from RL Agent)

3 discrete actions:
- **0 = SELL**: Liquidate all holdings
- **1 = HOLD**: Maintain current position
- **2 = BUY**: Buy as many shares as possible (90% of cash)

### Reward Function

Multi-component reward balancing multiple objectives:

```python
reward = α * profit_reward 
       + β * risk_penalty 
       + γ * alignment_reward 
       + δ * consistency_reward 
       + transaction_cost
```

**Components:**
- **Profit Reward**: Percentage return on portfolio value
- **Risk Penalty**: Penalizes high volatility and large drawdowns
- **Alignment Reward**: Bonus for agreeing with LLM expert (decays over time)
- **Consistency Reward**: Penalizes erratic trading behavior
- **Transaction Cost**: Small penalty for changing positions

### DQN Algorithm

Uses **Deep Q-Network** with:
- **Policy Network**: 3-layer MLP (state_dim → 256 → 128 → 3)
- **Target Network**: Stabilizes training, updated every 100 steps
- **Experience Replay**: 10,000 experiences buffer
- **Epsilon-Greedy**: Exploration starts at 1.0, decays to 0.01
- **Huber Loss**: Robust to outliers
- **Adam Optimizer**: Learning rate 1e-4

## 🎓 Training Configuration

### Key Hyperparameters

```python
config = {
    "rl_learning_rate": 1e-4,        # Adam learning rate
    "rl_gamma": 0.95,                # Discount factor
    "rl_epsilon_start": 1.0,         # Initial exploration
    "rl_epsilon_min": 0.01,          # Minimum exploration
    "rl_epsilon_decay": 0.995,       # Exploration decay rate
    "rl_batch_size": 32,             # Training batch size
    "rl_buffer_size": 10000,         # Replay buffer capacity
    "rl_target_update": 100,         # Target network update frequency
}
```

### Training Arguments

```bash
python -m tradingagents.rl.train_rl_agent --help

Arguments:
  --tickers TICKER [TICKER ...]    Stock tickers to train on (default: AAPL)
  --start-date YYYY-MM-DD          Training start date (default: 2020-01-01)
  --end-date YYYY-MM-DD            Training end date (default: 2024-12-31)
  --num-episodes N                 Number of training episodes (default: 50)
  --batch-size N                   Batch size (default: 32)
  --buffer-size N                  Replay buffer size (default: 10000)
  --initial-capital AMOUNT         Starting cash (default: 10000.0)
  --use-llm-features               Use LLM-generated features (slower)
  --checkpoint-freq N              Save every N episodes (default: 10)
  --model-name NAME                Model name (default: rl_trader)
```

## 📈 Evaluation & Metrics

### Metrics Calculated

1. **Returns:**
   - Total return percentage
   - Final portfolio value

2. **Risk-Adjusted:**
   - Sharpe ratio
   - Maximum drawdown
   - Volatility (standard deviation of returns)

3. **Trading:**
   - Win rate (profitable trades / total trades)
   - Number of trades
   - Action distribution (SELL/HOLD/BUY counts)

4. **Rewards:**
   - Total reward
   - Average reward per step

### Baselines for Comparison

The evaluation script automatically compares your RL agent against:

1. **Buy and Hold**: Buy at start, hold until end
2. **Random Strategy**: Random actions at each step

### Output Files

After evaluation, you'll get:

```
eval_results/
└── AAPL/
    ├── AAPL_evaluation_report.txt      # Human-readable comparison table
    └── AAPL_detailed_results.json      # Full results with time series data
```

## 🔧 Advanced Usage

### Custom Reward Function

Edit `tradingagents/rl/reward_calculator.py`:

```python
def calculate_total_reward(self, ...):
    # Modify weights
    self.profit_weight = 2.0        # Emphasize profit more
    self.risk_weight = 0.5          # Increase risk aversion
    self.alignment_weight = 0.0     # Disable alignment bonus
    
    # ... rest of calculation
```

### Using Trained Model in Code

```python
from tradingagents.rl.rl_trader import RLTradingAgent
from tradingagents.rl.state_encoder import TradingStateEncoder
import numpy as np

# Initialize
config = {"llm_provider": "openai", ...}
state_encoder = TradingStateEncoder(config)
agent = RLTradingAgent(state_dim=6168, action_dim=3)

# Load trained model
agent.load("tradingagents/rl/models/rl_trader_final.pt")
agent.set_eval_mode()

# Get state from your trading system
state = {
    "market_data": {...},
    "portfolio_state": {...},
    "trade_date": "2024-01-15",
    "market_report": "...",
    # ... other reports
}

# Encode and predict
state_vector = state_encoder.encode_state(state)
action = agent.get_action(state_vector, training=False)

# action: 0=SELL, 1=HOLD, 2=BUY
print(f"RL Agent decision: {['SELL', 'HOLD', 'BUY'][action]}")
```

### Continue Training from Checkpoint

```python
# In train_rl_agent.py, after creating agent:
agent.load("tradingagents/rl/models/checkpoints/rl_trader_episode_50.pt")

# Then continue training
```

## 📊 Monitoring Training

### Training Logs

Logs are saved to: `tradingagents/rl/logs/training_log.json`

```json
[
  {
    "episode": 1,
    "timestamp": "2024-01-15T10:30:00",
    "total_return_pct": 5.23,
    "final_portfolio_value": 10523.45,
    "total_reward": 123.45,
    "avg_reward": 0.52,
    "actions": {"SELL": 10, "HOLD": 75, "BUY": 15},
    "epsilon": 0.995,
    "avg_loss": 0.0042
  },
  ...
]
```

### What to Watch During Training

**Good signs:**
- ✅ Return percentage increasing over episodes
- ✅ Average loss stabilizing or decreasing
- ✅ Epsilon decaying smoothly
- ✅ Not all actions are the same (exploring)

**Warning signs:**
- ⚠️ Loss exploding (> 1.0)
- ⚠️ All actions become HOLD (agent gave up)
- ⚠️ Returns wildly fluctuating (instability)

## 🐛 Troubleshooting

### Issue: "Import torch could not be resolved"

**Solution:** Install PyTorch
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
```

### Issue: "OPENAI_API_KEY not found"

**Solution:** Set environment variable
```bash
export OPENAI_API_KEY="sk-..."
# Or add to ~/.bashrc for persistence
```

### Issue: Training is very slow

**Solutions:**
1. Don't use `--use-llm-features` (faster)
2. Reduce number of episodes
3. Use fewer tickers
4. Use cached data (set `online_tools: False` in config)

### Issue: Agent only learns to HOLD

**Solutions:**
1. Increase `profit_weight` in reward calculator
2. Decrease `risk_weight`
3. Add more diverse training data (multiple tickers)
4. Check if training data has enough volatility

### Issue: Out of memory

**Solutions:**
1. Reduce `buffer_size`
2. Reduce `batch_size`
3. Train on shorter time periods
4. Use CPU instead of GPU

## 📚 Next Steps

### 1. **Train on Your Data**
```bash
python -m tradingagents.rl.train_rl_agent \
    --tickers YOUR_TICKER \
    --start-date YYYY-MM-DD \
    --end-date YYYY-MM-DD \
    --num-episodes 100
```

### 2. **Evaluate Performance**
```bash
python -m tradingagents.rl.evaluate_rl_agent \
    --model-path tradingagents/rl/models/rl_trader_final.pt \
    --tickers YOUR_TICKER \
    --start-date YYYY-MM-DD \
    --end-date YYYY-MM-DD
```

### 3. **Compare with LLM System**
Run the same ticker through both systems and compare results:
- RL agent: Fast, data-driven decisions
- LLM system: Interpretable, reasoning-based decisions

### 4. **Experiment**
- Try different reward functions
- Add more features to state
- Use continuous actions for position sizing
- Implement PPO or SAC algorithms

## 🤝 Contributing

Ideas for improvements:
- [ ] Add support for multi-asset portfolios
- [ ] Implement PPO/SAC algorithms
- [ ] Add tensorboard logging
- [ ] Create visualization dashboard
- [ ] Implement online learning mode
- [ ] Add risk constraints (max position size, stop-loss)

## 📖 References

- **DQN Paper**: [Playing Atari with Deep Reinforcement Learning](https://arxiv.org/abs/1312.5602)
- **PyTorch RL Tutorial**: https://pytorch.org/tutorials/intermediate/reinforcement_q_learning.html
- **FinRL Library**: https://github.com/AI4Finance-Foundation/FinRL

---

**Questions? Issues?**
- Check existing GitHub issues: https://github.com/TauricResearch/TradingAgents/issues
- Join Discord: [TradingResearch Discord](https://discord.com/invite/hk9PGKShPK)

**Happy Training! 🚀**
