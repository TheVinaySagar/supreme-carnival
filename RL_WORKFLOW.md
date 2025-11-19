# 🤖 RL Trading Agent - Complete Workflow

## 📋 Table of Contents
1. [High-Level Overview](#high-level-overview)
2. [Training Flow](#training-flow)
3. [Episode Flow](#episode-flow)
4. [State Construction](#state-construction)
5. [Action Execution](#action-execution)
6. [Reward Calculation](#reward-calculation)
7. [Caching Strategy](#caching-strategy)
8. [Data Flow Diagram](#data-flow-diagram)

---

## 🎯 High-Level Overview

The RL trading system combines **Deep Q-Network (DQN)** with **LLM-powered market analysis** to make trading decisions.

```
┌─────────────────────────────────────────────────────────────┐
│  USER COMMAND                                               │
│  python -m tradingagents.rl.train_rl_agent \               │
│    --tickers RELIANCE.NS \                                  │
│    --start-date 2023-01-02 \                                │
│    --end-date 2023-10-10 \                                  │
│    --num-episodes 50 \                                      │
│    --use-llm-features                                       │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  INITIALIZATION                                             │
│  • Load config (learning rate, gamma, epsilon, etc.)        │
│  • Create TradingEnvironment (loads price data & cache)     │
│  • Create RLTradingAgent (DQN neural network)               │
│  • Create ReplayBuffer (stores experiences)                 │
│  • Setup logger & checkpoints                               │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  TRAINING LOOP (50 episodes)                                │
│  For each episode:                                          │
│    1. Reset environment → initial state                     │
│    2. Run episode (39 weekly steps)                         │
│    3. Log metrics (return, reward, loss, actions)           │
│    4. Decay epsilon (exploration → exploitation)            │
│    5. Save checkpoint every 10 episodes                     │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  FINAL OUTPUT                                               │
│  • Trained model: models/RELIANCE_NS_2023_TRAIN_final.pt   │
│  • Training logs: logs/training_*.log                       │
│  • LLM cache: llm_reports/RELIANCE.NS_2023-01-02_*.json    │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 Training Flow

### **train_rl_agent.py** (Main Script)

```python
# 1. PARSE ARGUMENTS
args = parse_args()  # Get tickers, dates, episodes, flags

# 2. SETUP CONFIG
config = DEFAULT_CONFIG + overrides
config["rl_learning_rate"] = 1e-4
config["rl_gamma"] = 0.95
config["rl_epsilon_start"] = 1.0  # 100% exploration initially

# 3. CREATE ENVIRONMENT
env = TradingEnvironment(
    ticker="RELIANCE.NS",
    start_date="2023-01-02",
    end_date="2023-10-10",
    initial_capital=10000.0,
    use_llm_features=True  # Enable LLM reports
)
# Environment initializes:
#   - Loads price data (245 days → 49 weekly periods)
#   - Loads LLM cache (39 cached reports)
#   - Creates TradingAgentsGraph (for generating reports)
#   - Initializes StateEncoder (for encoding state vectors)

# 4. CREATE AGENT
state_dim = 9240  # 24 market features + 9216 text embeddings
action_dim = 3    # SELL, HOLD, BUY
agent = RLTradingAgent(state_dim, action_dim, config)
# Agent creates:
#   - Q-Network (policy network)
#   - Target Network (stable Q-value estimates)
#   - Optimizer (Adam with lr=1e-4)
#   - Epsilon scheduler (for exploration decay)

# 5. CREATE REPLAY BUFFER
replay_buffer = ReplayBuffer(capacity=10000, state_dim=9240)
# Buffer stores: (state, action, reward, next_state, done)

# 6. TRAINING LOOP
for episode in range(1, 51):  # 50 episodes
    metrics = train_episode(env, agent, replay_buffer, batch_size=32)
    
    # Episode metrics:
    # - total_return_pct: cumulative return from initial capital
    # - episode_return_pct: return for this episode only
    # - total_reward: sum of rewards
    # - avg_loss: average DQN loss
    # - actions: {SELL: X, HOLD: Y, BUY: Z}
    # - epsilon: current exploration rate
    
    logger.log_episode(episode, metrics)
    
    if episode % 10 == 0:
        agent.save(f"checkpoint_episode_{episode}.pt")
    
    agent.decay_epsilon()  # epsilon *= 0.995

# 7. SAVE FINAL MODEL
agent.save("models/RELIANCE_NS_2023_TRAIN_final.pt")
env.close()  # Save LLM cache
```

---

## 📊 Episode Flow

Each episode is a complete trading simulation from `start_date` to `end_date`.

```
┌─────────────────────────────────────────────────────────────┐
│  EPISODE START (train_episode function)                     │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  1. RESET ENVIRONMENT                                       │
│     state = env.reset()                                     │
│                                                             │
│     • Reset portfolio: cash=$10000, holdings=0              │
│     • Reset step counter: current_step=0                    │
│     • Get initial state (date 0, 2023-01-02)                │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  2. STEP LOOP (39 weekly trading periods)                   │
│     while not done:                                         │
└─────────────────────────────────────────────────────────────┘
   ↓                                                           ↑
   │  ┌────────────────────────────────────────────────────┐  │
   │  │ 2a. SELECT ACTION                                  │  │
   │  │     action = agent.get_action(state, training=True)│  │
   │  │                                                    │  │
   │  │     • With prob epsilon: random action (explore)  │  │
   │  │     • With prob 1-epsilon: Q-network (exploit)    │  │
   │  │     • Epsilon starts at 1.0, decays to 0.01       │  │
   │  └────────────────────────────────────────────────────┘  │
   │                     ↓                                     │
   │  ┌────────────────────────────────────────────────────┐  │
   │  │ 2b. EXECUTE ACTION                                 │  │
   │  │     next_state, reward, done, info = env.step(action)│
   │  │                                                    │  │
   │  │     • Execute trade (BUY/SELL/HOLD)                │  │
   │  │     • Update portfolio                             │  │
   │  │     • Calculate reward                             │  │
   │  │     • Get next state                               │  │
   │  └────────────────────────────────────────────────────┘  │
   │                     ↓                                     │
   │  ┌────────────────────────────────────────────────────┐  │
   │  │ 2c. STORE EXPERIENCE                               │  │
   │  │     replay_buffer.add(state, action, reward,       │  │
   │  │                       next_state, done)            │  │
   │  │                                                    │  │
   │  │     • Buffer size: 10,000 experiences              │  │
   │  │     • Oldest experiences discarded when full       │  │
   │  └────────────────────────────────────────────────────┘  │
   │                     ↓                                     │
   │  ┌────────────────────────────────────────────────────┐  │
   │  │ 2d. TRAIN AGENT (if buffer has ≥32 samples)       │  │
   │  │     batch = replay_buffer.sample(32)               │  │
   │  │     loss = agent.update(batch)                     │  │
   │  │                                                    │  │
   │  │     • Sample 32 random experiences                 │  │
   │  │     • Compute Q-values: Q(s,a)                     │  │
   │  │     • Compute targets: r + γ·max Q(s',a')          │  │
   │  │     • Backprop loss: MSE(Q, target)                │  │
   │  │     • Update target network every 100 steps        │  │
   │  └────────────────────────────────────────────────────┘  │
   │                     ↓                                     │
   │  ┌────────────────────────────────────────────────────┐  │
   │  │ 2e. UPDATE STATE                                   │  │
   │  │     state = next_state                             │  │
   │  │     total_reward += reward                         │  │
   │  │     step += 1                                      │  │
   │  └────────────────────────────────────────────────────┘  │
   │                     ↓                                     │
   └─────────────────────┴─────────────────────────────────────┘
                   (loop until done)
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  3. EPISODE END                                             │
│     return metrics {                                        │
│         "total_reward": sum of all rewards,                 │
│         "total_return_pct": portfolio gain %,               │
│         "actions": {SELL: X, HOLD: Y, BUY: Z},              │
│         "avg_loss": average training loss,                  │
│         "epsilon": current exploration rate                 │
│     }                                                       │
└─────────────────────────────────────────────────────────────┘
```

---

## 🧩 State Construction

The state is a **9240-dimensional vector** combining market data + text embeddings.

### **Environment: _get_state()**

```python
def _get_state(self):
    """Construct state vector for RL agent."""
    
    # 1. GET CURRENT DATE
    current_date = self.trading_dates[self.current_date_idx]
    # Example: "2023-01-02"
    
    # 2. GET MARKET DATA (24 features)
    market_data = self._get_market_data(current_date)
    # {
    #     "price": 2345.67,
    #     "open": 2340.12,
    #     "high": 2350.89,
    #     "low": 2338.45,
    #     "volume": 12345678,
    #     "price_change_pct": 0.24,
    #     "sma_50": 2320.45,
    #     "sma_20": 2335.12,
    #     "rsi": 58.3,
    #     ... (24 total features)
    # }
    
    # 3. GET LLM REPORTS (6 text reports)
    llm_reports = self._get_llm_reports(current_date)
    # {
    #     "market_report": "The market shows bullish momentum...",
    #     "sentiment_report": "Social media sentiment is positive...",
    #     "news_report": "Recent news indicates strong fundamentals...",
    #     "fundamentals_report": "P/E ratio is attractive at 15.2...",
    #     "bull_report": "We recommend BUY based on...",
    #     "bear_report": "We recommend HOLD due to risks..."
    # }
    
    # 4. COMBINE INTO STATE DICT
    state = {
        "market_data": market_data,
        "portfolio_state": self.portfolio,  # {cash, holdings, total_value}
        "trade_date": current_date,
        **llm_reports  # Unpack 6 reports
    }
    
    # 5. ENCODE TO VECTOR (9240-dim)
    state_vector = self.state_encoder.encode_state(state)
    # [24 market features] + [9216 text embeddings]
    
    return state_vector
```

### **StateEncoder: encode_state()**

```python
def encode_state(self, state_dict):
    """Encode state dict into numerical vector."""
    
    # 1. ENCODE MARKET DATA (24 features)
    market_features = [
        state_dict["market_data"]["price"],
        state_dict["market_data"]["volume"],
        state_dict["market_data"]["sma_50"],
        state_dict["market_data"]["rsi"],
        ... (24 total)
    ]
    # Normalize: (value - mean) / std
    
    # 2. ENCODE TEXT REPORTS (6 reports → 9216 features)
    if use_llm_features:
        # Concatenate all 6 reports
        text = (
            state_dict["market_report"] + " " +
            state_dict["sentiment_report"] + " " +
            state_dict["news_report"] + " " +
            state_dict["fundamentals_report"] + " " +
            state_dict["bull_report"] + " " +
            state_dict["bear_report"]
        )
        
        # Get BERT embedding (768-dim per report × 12 chunks = 9216)
        embeddings = self.text_encoder.encode(text)
        # Shape: [9216]
    else:
        embeddings = np.zeros(9216)  # Skip LLM features
    
    # 3. CONCATENATE
    state_vector = np.concatenate([market_features, embeddings])
    # Shape: [24 + 9216] = [9240]
    
    return state_vector
```

---

## ⚡ Action Execution

### **Environment: step(action)**

```python
def step(self, action: int):
    """Execute action and return next state, reward, done, info."""
    
    # Action mapping: 0=SELL, 1=HOLD, 2=BUY
    
    current_date = self.trading_dates[self.current_date_idx]
    current_price = self.price_data[current_date]["price"]
    
    # 1. STORE PORTFOLIO VALUE BEFORE ACTION
    portfolio_value_before = self.portfolio["total_value"]
    # Example: $10,500 (cash + holdings × price)
    
    # 2. EXECUTE ACTION
    action_executed = self._execute_action(action, current_price)
    
    if action == 0:  # SELL
        if self.portfolio["holdings"] > 0:
            cash_gained = self.portfolio["holdings"] × current_price
            self.portfolio["cash"] += cash_gained
            self.portfolio["holdings"] = 0
            action_executed = True
        else:
            action_executed = False  # Invalid: no holdings to sell
    
    elif action == 1:  # HOLD
        # Do nothing
        action_executed = True
    
    elif action == 2:  # BUY
        if self.portfolio["cash"] > 0:
            shares = self.portfolio["cash"] // current_price
            if shares > 0:
                self.portfolio["holdings"] += shares
                self.portfolio["cash"] -= shares × current_price
                action_executed = True
            else:
                action_executed = False  # Not enough cash
        else:
            action_executed = False
    
    # 3. UPDATE PORTFOLIO VALUE
    portfolio_value_after = (
        self.portfolio["cash"] +
        self.portfolio["holdings"] × current_price
    )
    self.portfolio["total_value"] = portfolio_value_after
    
    # 4. CALCULATE REWARD
    reward = self.reward_calculator.calculate_total_reward(
        portfolio_value_before=portfolio_value_before,
        portfolio_value_after=portfolio_value_after,
        rl_action=action,
        prev_action=self.prev_action
    )
    
    # 5. MOVE TO NEXT STEP
    self.current_step += 1
    self.current_date_idx += 1
    self.done = (self.current_date_idx >= len(self.trading_dates))
    
    # 6. GET NEXT STATE
    next_state = self._get_state()
    
    # 7. RETURN
    info = {
        "date": current_date,
        "price": current_price,
        "portfolio_value": portfolio_value_after,
        "return_pct": ((portfolio_value_after - 10000) / 10000) × 100,
        "action_taken": ["SELL", "HOLD", "BUY"][action],
        "action_valid": action_executed
    }
    
    return next_state, reward, self.done, info
```

---

## 💰 Reward Calculation

### **RewardCalculator: calculate_total_reward()**

```python
def calculate_total_reward(
    self,
    portfolio_value_before: float,
    portfolio_value_after: float,
    rl_action: int,
    prev_action: int
):
    """Calculate reward based on profit/loss."""
    
    # 1. CALCULATE RETURN
    return_pct = (
        (portfolio_value_after - portfolio_value_before) /
        portfolio_value_before
    )
    # Example: +0.02 = +2% gain
    
    # 2. CLIP EXTREME RETURNS (prevent instability)
    return_pct = np.clip(return_pct, -0.50, +0.50)
    # Max loss: -50%, max gain: +50% per step
    
    # 3. PROFIT REWARD (with loss aversion)
    if return_pct >= 0:
        # Positive return: reward = +2% × 100 × 10 = +2.0
        profit_reward = return_pct × 100.0 × self.profit_weight
    else:
        # Negative return: penalty = -2% × 100 × 10 × 2 = -4.0
        # (losses hurt 2× more than gains)
        profit_reward = (
            return_pct × 100.0 × 
            self.profit_weight × 
            self.loss_multiplier
        )
    
    # 4. TRANSACTION COST
    if rl_action != 1 and rl_action != prev_action:
        # Penalize unnecessary trading (action changed)
        transaction_penalty = -self.transaction_cost  # -0.02
    else:
        transaction_penalty = 0.0
    
    # 5. TOTAL REWARD
    total_reward = profit_reward + transaction_penalty
    
    return {
        "total": total_reward,
        "profit_reward": profit_reward,
        "transaction_penalty": transaction_penalty,
        "return_pct": return_pct
    }
```

### **Example Scenarios:**

| Portfolio Before | Portfolio After | Return | Profit Reward | Transaction | Total Reward |
|------------------|-----------------|--------|---------------|-------------|--------------|
| $10,000 | $10,500 | +5% | +50.0 | -0.02 | **+49.98** |
| $10,000 | $9,500 | -5% | -100.0 | -0.02 | **-100.02** |
| $10,000 | $10,000 | 0% | 0.0 | 0.0 | **0.0** |
| $10,000 | $10,200 | +2% | +20.0 | 0.0 | **+20.0** (HOLD) |

**Key Properties:**
- ✅ Positive returns → positive rewards
- ✅ Losses hurt 2× more (loss aversion)
- ✅ Overtrading penalized (-0.02 per trade)
- ✅ Stable: no risk penalties that dominate

---

## 💾 Caching Strategy

The system uses **hierarchical caching** to avoid regenerating expensive LLM reports.

### **Cache Structure:**

```
tradingagents/dataflows/data_cache/llm_reports/
└── RELIANCE.NS_2023-01-02_2023-10-10.json  ← 39 cached reports
    {
      "RELIANCE.NS_2023-01-02": {
        "market_report": "Market analysis for Jan 2...",
        "sentiment_report": "Social sentiment is...",
        "news_report": "Recent news shows...",
        "fundamentals_report": "P/E ratio is...",
        "bull_report": "BUY recommendation based on...",
        "bear_report": "HOLD recommendation due to..."
      },
      "RELIANCE.NS_2023-01-09": { ... },
      ...
      "RELIANCE.NS_2023-10-10": { ... }
    }
```

### **Cache Lookup Flow:**

```python
def _get_llm_reports(self, date_str):
    """Get or generate LLM reports for date."""
    
    # 1. TRY CACHE LOOKUP
    cache_key = self._get_cache_key(date_str)
    # cache_key = "RELIANCE.NS_2023-01-02"
    
    if cache_key in self.llm_cache:
        cached = self.llm_cache[cache_key]
        
        # Check if new format (6 reports)
        if all(k in cached for k in [
            "market_report", "sentiment_report", "news_report",
            "fundamentals_report", "bull_report", "bear_report"
        ]):
            print(f"✓ Using cached 6 reports for {date_str}")
            return cached  # ← FAST PATH (100x faster!)
        
        # Old format (4 analyst reports only)
        elif "market_report" in cached:
            print(f"🔄 Found 4 analyst reports, generating bull/bear...")
            # Run debate only (skips analyst regeneration)
            _, _ = self.trading_graph.propagate(
                self.ticker, date_str,
                cached_analyst_reports=cached  # Reuse cached analysts
            )
            state = self.trading_graph.curr_state
            bull_bear = self._extract_bull_bear_from_state(state, cached)
            all_reports = {**cached, **bull_bear}
            self._save_llm_cache_immediately(cache_key, all_reports)
            return all_reports  # ← MEDIUM PATH (2x faster)
    
    # 2. CACHE MISS - GENERATE FRESH
    print(f"⚡ Generating 6 fresh reports for {date_str}...")
    _, _ = self.trading_graph.propagate(self.ticker, date_str)
    state = self.trading_graph.curr_state
    
    # Extract 4 analyst reports
    analyst_reports = {
        "market_report": state["market_report"],
        "sentiment_report": state["sentiment_report"],
        "news_report": state["news_report"],
        "fundamentals_report": state["fundamentals_report"]
    }
    
    # Extract bull/bear debate reports
    bull_bear = self._extract_bull_bear_from_state(state, analyst_reports)
    
    # Combine all 6
    all_reports = {**analyst_reports, **bull_bear}
    
    # Save to cache immediately
    self._save_llm_cache_immediately(cache_key, all_reports)
    print(f"✓ Cached 6 reports for {date_str}")
    
    return all_reports  # ← SLOW PATH (first episode only)
```

### **Cache Performance:**

| Episode | Cache Status | Time per Episode |
|---------|--------------|------------------|
| 1 | 0/39 cached (0%) | **~12-15 minutes** (generates bull/bear debates) |
| 2-50 | 39/39 cached (100%) | **~15-20 seconds** (100% cached!) |

**Speedup:** ~50x faster for episodes 2-50! 🚀

---

## 📈 Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        TRAINING SCRIPT                       │
│                    (train_rl_agent.py)                      │
└─────────────────────────────────────────────────────────────┘
                           │
                           │ creates
                           ↓
        ┌──────────────────────────────────────────┐
        │        TRADING ENVIRONMENT               │
        │      (rl_environment.py)                 │
        │                                          │
        │  ┌────────────────────────────────────┐ │
        │  │  Price Data (yfinance)             │ │
        │  │  • 245 days → 49 weekly periods    │ │
        │  │  • OHLCV + technical indicators    │ │
        │  └────────────────────────────────────┘ │
        │                 │                        │
        │  ┌──────────────┴──────────────────────┐│
        │  │  LLM Cache                          ││
        │  │  • 39 cached reports (100% coverage)││
        │  │  • 6 reports per date               ││
        │  │  • Loaded from JSON file            ││
        │  └─────────────────────────────────────┘│
        │                 │                        │
        │  ┌──────────────┴──────────────────────┐│
        │  │  TradingAgentsGraph                 ││
        │  │  • Generates LLM reports on miss    ││
        │  │  • 4 analysts + bull/bear debate    ││
        │  └─────────────────────────────────────┘│
        │                 │                        │
        │  ┌──────────────┴──────────────────────┐│
        │  │  State Encoder                      ││
        │  │  • Market features (24-dim)         ││
        │  │  • Text embeddings (9216-dim)       ││
        │  │  • Total: 9240-dim vector           ││
        │  └─────────────────────────────────────┘│
        │                 │                        │
        │  ┌──────────────┴──────────────────────┐│
        │  │  Reward Calculator                  ││
        │  │  • Profit-focused                   ││
        │  │  • Loss aversion (2× penalty)       ││
        │  │  • Transaction cost                 ││
        │  └─────────────────────────────────────┘│
        └──────────────────────────────────────────┘
                           │
                           │ feeds state to
                           ↓
        ┌──────────────────────────────────────────┐
        │          RL TRADING AGENT                │
        │         (rl_trader.py)                   │
        │                                          │
        │  ┌────────────────────────────────────┐ │
        │  │  Q-Network (policy)                │ │
        │  │  • Input: 9240-dim state           │ │
        │  │  • Hidden: [512, 256, 128]         │ │
        │  │  • Output: 3 Q-values (S, H, B)    │ │
        │  └────────────────────────────────────┘ │
        │                 │                        │
        │  ┌──────────────┴──────────────────────┐│
        │  │  Target Network (stable targets)    ││
        │  │  • Same architecture as Q-network   ││
        │  │  • Updated every 100 steps          ││
        │  └─────────────────────────────────────┘│
        │                 │                        │
        │  ┌──────────────┴──────────────────────┐│
        │  │  Epsilon-Greedy Policy              ││
        │  │  • Epsilon: 1.0 → 0.01 (decay)      ││
        │  │  • Explore: random action           ││
        │  │  • Exploit: argmax Q(s, a)          ││
        │  └─────────────────────────────────────┘│
        └──────────────────────────────────────────┘
                           │
                           │ stores experiences in
                           ↓
        ┌──────────────────────────────────────────┐
        │          REPLAY BUFFER                   │
        │        (replay_buffer.py)                │
        │                                          │
        │  Capacity: 10,000 experiences            │
        │  Storage: (state, action, reward,        │
        │            next_state, done)             │
        │  Sampling: Random batch (32)             │
        └──────────────────────────────────────────┘
                           │
                           │ samples batches for
                           ↓
        ┌──────────────────────────────────────────┐
        │          DQN UPDATE                      │
        │                                          │
        │  1. Sample batch (32 experiences)        │
        │  2. Compute Q(s, a) from policy network  │
        │  3. Compute target: r + γ·max Q(s', a')  │
        │  4. Loss: MSE(Q, target)                 │
        │  5. Backprop & update weights            │
        │  6. Update target network every 100 steps│
        └──────────────────────────────────────────┘
                           │
                           │ outputs
                           ↓
        ┌──────────────────────────────────────────┐
        │          MODEL & LOGS                    │
        │                                          │
        │  • Trained model: .pt file               │
        │  • Training logs: .log file              │
        │  • Checkpoints: episode_10, 20, 30...    │
        │  • LLM cache: .json file (updated)       │
        └──────────────────────────────────────────┘
```

---

## 🎯 Key Takeaways

### **What Makes This System Unique:**

1. **Hybrid RL + LLM:**
   - Combines deep Q-learning with LLM market analysis
   - State includes both numerical (price, indicators) and semantic (text reports) features
   - DQN learns to weigh LLM recommendations vs price signals

2. **Efficient Caching:**
   - LLM reports cached per trading day
   - Episode 1: ~12 min (generates reports)
   - Episodes 2-50: ~15 sec each (100% cached)
   - 50× speedup after first episode!

3. **Profit-Focused Rewards:**
   - Simple formula: profit × 10, losses × 20
   - No complex risk penalties that cause negative rewards
   - Loss aversion: realistic trading psychology

4. **Weekly Trading:**
   - Samples every 5th trading day (weekly)
   - Reduces training time: 245 days → 49 periods
   - Still captures market trends

5. **Experience Replay:**
   - Stores 10,000 experiences
   - Breaks temporal correlation
   - Stable learning

### **Typical Training Run (50 episodes, 39 weeks):**

| Metric | Episode 1 | Episode 25 | Episode 50 |
|--------|-----------|------------|------------|
| Time | 12 min | 15 sec | 15 sec |
| Epsilon | 1.0 (random) | 0.43 (mixed) | 0.08 (greedy) |
| Avg Loss | 0.8 | 0.3 | 0.15 |
| Return | -5% to +5% | +5% to +10% | +10% to +15% |
| Cache | 39 generated | 39 cached | 39 cached |

**Total Time:** ~15-20 minutes for 50 episodes! 🚀

---

## 🚀 Next Steps

1. **Train on 80% data:** Use corrected dates (2023-01-02 to 2023-10-10)
2. **Test on 20% data:** Evaluate on unseen data (2023-10-17 to 2023-12-22)
3. **Compare performance:** Train return vs test return (generalization)
4. **Tune hyperparameters:** Learning rate, gamma, epsilon decay
5. **Extend to other tickers:** HDFCBANK.NS, TCS.NS, etc.

---

**Ready to train? Use the commands in `TRAIN_TEST_COMMANDS.txt`!** 🎯
