# TradingAgents RL Module

## 📂 Module Structure

```
tradingagents/rl/
├── __init__.py                # Module initialization
├── state_encoder.py           # State → RL vector conversion
├── replay_buffer.py           # Experience replay
├── reward_calculator.py       # Multi-component reward function
├── rl_trader.py              # DQN agent
├── rl_environment.py         # Gym-like trading environment
├── train_rl_agent.py         # Training script
├── evaluate_rl_agent.py      # Evaluation script
├── models/                   # Saved models
│   └── checkpoints/
└── logs/                     # Training logs
```

## 🚀 Quick Usage

### Train
```bash
python -m tradingagents.rl.train_rl_agent --tickers AAPL --num-episodes 50
```

### Evaluate
```bash
python -m tradingagents.rl.evaluate_rl_agent \
    --model-path tradingagents/rl/models/rl_trader_final.pt \
    --tickers AAPL
```

## 📚 Documentation

See main project documentation files:
- `EXECUTION_INSTRUCTIONS.md` - Setup & usage
- `RL_GUIDE.md` - Complete feature guide  
- `RL_WORKFLOW_GUIDE.md` - Visual workflows

## 💡 Key Features

- **State Dimension**: 6,168 (market data + text embeddings)
- **Actions**: SELL (0), HOLD (1), BUY (2)
- **Algorithm**: Deep Q-Network (DQN)
- **Reward**: Multi-component (profit, risk, alignment, consistency)
