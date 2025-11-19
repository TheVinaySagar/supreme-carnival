# 💰 Reward Function Explained

## 🎯 Purpose

The reward function is the **core learning signal** for the RL agent. It tells the agent:
- ✅ **What is good** (positive rewards)
- ❌ **What is bad** (negative rewards)

The agent's goal: **Maximize cumulative reward over time**

---

## 🧮 The Formula

```python
# STEP 1: Calculate return
return_pct = (portfolio_after - portfolio_before) / portfolio_before

# STEP 2: Apply profit/loss weighting
if return_pct >= 0:  # Profit
    profit_reward = return_pct × 100 × profit_weight
else:  # Loss
    profit_reward = return_pct × 100 × profit_weight × loss_multiplier

# STEP 3: Add transaction cost
if action_changed:  # BUY → SELL or SELL → BUY
    transaction_penalty = -0.02
else:
    transaction_penalty = 0

# STEP 4: Total reward
total_reward = profit_reward + transaction_penalty
```

---

## 🔧 Parameters

### **1. profit_weight = 10.0**
**What it does:** Scales up rewards to make them meaningful for learning.

**Why 10.0?**
- A 1% portfolio gain → +10 reward
- A 5% portfolio gain → +50 reward
- Without scaling, rewards would be tiny (0.1, 0.5) and hard to learn from

**Example:**
```python
return = +0.5%
reward = 0.005 × 100 × 10 = +5.0
```

---

### **2. loss_multiplier = 2.0**
**What it does:** Makes losses hurt **2× more** than gains help (loss aversion).

**Why 2.0?**
- Mirrors human psychology: losing $100 feels worse than gaining $100 feels good
- Encourages risk management
- Prevents reckless trading

**Example:**
```python
Gain +1%: reward = +1 × 100 × 10 = +10
Loss -1%: reward = -1 × 100 × 10 × 2 = -20  ← Hurts 2× more!
```

---

### **3. transaction_cost = 0.02**
**What it does:** Penalizes overtrading by subtracting -0.02 per trade.

**Why 0.02?**
- Realistic: Real trading has fees (~0.1-0.5% per trade)
- Prevents agent from trading every step
- Encourages strategic, not random, trading

**Example:**
```python
BUY when already bought: No penalty (no trade)
BUY → SELL: Penalty -0.02
SELL → BUY: Penalty -0.02
HOLD: No penalty
```

---

### **4. max_return_clip = 0.50**
**What it does:** Clips extreme returns to ±50% for stability.

**Why 0.50?**
- Prevents gradient explosions from rare huge gains/losses
- Keeps training stable
- Rarely triggered in normal trading

**Example:**
```python
If return = +80% (rare spike):
  Clipped to +50%
  reward = +50 × 100 × 10 = +5000 (instead of +8000)
```

---

## 📊 Concrete Examples

### **Example 1: Profitable Week**

```
Week 1 → Week 2:
  Portfolio: $10,000 → $10,200 (+2%)
  Action: BUY (changed from HOLD)

Calculation:
  return_pct = (10200 - 10000) / 10000 = +0.02 (2%)
  profit_reward = 0.02 × 100 × 10 = +20.0
  transaction_penalty = -0.02 (BUY is trade)
  total_reward = +20.0 - 0.02 = +19.98

✅ Positive reward for profit!
```

---

### **Example 2: Losing Week**

```
Week 2 → Week 3:
  Portfolio: $10,200 → $9,900 (-2.94%)
  Action: SELL (changed from BUY)

Calculation:
  return_pct = (9900 - 10200) / 10200 = -0.0294 (-2.94%)
  profit_reward = -0.0294 × 100 × 10 × 2 = -58.8 (2× penalty!)
  transaction_penalty = -0.02 (SELL is trade)
  total_reward = -58.8 - 0.02 = -58.82

❌ Negative reward for loss (2× penalty)
```

---

### **Example 3: Hold During Gain**

```
Week 3 → Week 4:
  Portfolio: $9,900 → $10,100 (+2.02%)
  Action: HOLD (no change)

Calculation:
  return_pct = (10100 - 9900) / 9900 = +0.0202 (+2.02%)
  profit_reward = 0.0202 × 100 × 10 = +20.2
  transaction_penalty = 0 (HOLD, no trade)
  total_reward = +20.2 + 0 = +20.2

✅ Positive reward for holding through gain!
```

---

### **Example 4: Hold During Loss**

```
Week 4 → Week 5:
  Portfolio: $10,100 → $9,800 (-2.97%)
  Action: HOLD (no change)

Calculation:
  return_pct = (9800 - 10100) / 10100 = -0.0297 (-2.97%)
  profit_reward = -0.0297 × 100 × 10 × 2 = -59.4
  transaction_penalty = 0 (HOLD, no trade)
  total_reward = -59.4 + 0 = -59.4

❌ Negative reward for holding through loss!
```

---

## 🧠 What the Agent Learns

### **Good Strategies (Positive Rewards):**
1. **Buy before price increases** → Get profit reward
2. **Sell before price decreases** → Avoid loss penalty
3. **Hold profitable positions** → Keep earning rewards
4. **Minimize unnecessary trades** → Avoid transaction costs

### **Bad Strategies (Negative Rewards):**
1. **Buy before price drops** → Get loss penalty (2×!)
2. **Sell before price rises** → Miss profit opportunity
3. **Hold losing positions** → Keep getting penalties
4. **Overtrade** → Accumulate transaction costs

---

## 📈 Reward-Return Relationship

The reward function creates a **strong correlation** between returns and rewards:

| Portfolio Return | Expected Reward | Interpretation |
|------------------|-----------------|----------------|
| +10% | +100 | Excellent! Strong positive signal |
| +5% | +50 | Good profit |
| +1% | +10 | Small gain |
| 0% | 0 | Neutral (no change) |
| -1% | -20 | Small loss (2× penalty) |
| -5% | -100 | Bad loss (2× penalty) |
| -10% | -200 | Terrible loss (2× penalty) |

**Key Insight:** Positive returns → Positive rewards, Negative returns → Negative rewards!

---

## 🎓 Why This Design?

### **1. Profit-Focused**
- Primary goal: Make money
- Directly rewards portfolio growth
- No complex risk penalties that confuse learning

### **2. Loss Aversion**
- Loss multiplier = 2.0 encourages caution
- Reflects real trading psychology
- Prevents overly aggressive strategies

### **3. Transaction Cost**
- Prevents overtrading
- Encourages patient, strategic trades
- Realistic modeling of real trading

### **4. Simple & Interpretable**
- Easy to understand what agent is learning
- Clear cause-effect relationship
- No hidden complexity

---

## 🔍 How It's Used in Training

### **Step-by-Step:**

```
1. Agent observes state (price, indicators, LLM reports)
   ↓
2. Agent selects action (BUY/SELL/HOLD)
   ↓
3. Environment executes trade
   ↓
4. Portfolio value changes (due to price + action)
   ↓
5. Reward calculated: compare portfolio before vs after
   ↓
6. Agent learns: "Did this action increase reward?"
   ↓
7. Agent updates policy: adjust Q-values
   ↓
8. Repeat for next step
```

### **Learning Mechanism:**

The agent uses **Q-learning** to learn which actions maximize future rewards:

```
Q(state, action) = immediate_reward + γ × max Q(next_state, next_action)
                   ↑                    ↑
                   This reward         Expected future rewards
```

Over many episodes, the agent learns:
- Which market conditions → BUY
- Which market conditions → SELL
- Which market conditions → HOLD

---

## 🐛 Common Issues & Fixes

### **Issue 1: Rewards are all negative despite positive returns**
**Cause:** Portfolio value tracking bug (using current price instead of previous)
**Fix:** Track `prev_portfolio_value` and use it for reward calculation

### **Issue 2: Rewards are too small (0.1, 0.5)**
**Cause:** profit_weight too low
**Fix:** Use profit_weight=10.0 to scale up rewards

### **Issue 3: Agent trades too much**
**Cause:** transaction_cost too low
**Fix:** Increase to 0.02 or higher

### **Issue 4: Agent is too risky**
**Cause:** loss_multiplier too low
**Fix:** Increase to 2.0 or higher for more conservative behavior

---

## 📊 Expected Episode Rewards

For a 39-step episode (39 weeks of trading):

| Episode Return | Expected Total Reward |
|----------------|-----------------------|
| +10% | +80 to +100 |
| +5% | +40 to +50 |
| 0% | -0.5 to +0.5 |
| -5% | -40 to -50 |
| -10% | -160 to -200 |

**Note:** Exact values vary based on:
- How returns are distributed across steps
- Number of trades (transaction costs)
- Volatility of individual steps

---

## 🎯 Summary

The reward function is **simple yet effective**:

```python
reward = (return% × 100 × 10) - (trades × 0.02)
         ↑                      ↑
         Profit/loss            Transaction cost
         (2× for losses)
```

**Design Goals:**
1. ✅ **Maximize profit** (profit_weight=10.0)
2. ✅ **Minimize losses** (loss_multiplier=2.0)
3. ✅ **Reduce overtrading** (transaction_cost=0.02)
4. ✅ **Stable learning** (clip extreme returns)

**Result:** Agent learns to be a **profitable, risk-aware trader**! 📈💰
