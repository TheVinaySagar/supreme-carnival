# How the RL Model Decides Position Sizes

## 🎯 Executive Summary

**Current Implementation:** Your model uses **ALL-OR-NOTHING** trading:
- **BUY**: Uses 90% of available cash to buy maximum shares
- **SELL**: Sells 100% of holdings
- **HOLD**: Does nothing

**Capital Management:** Yes, capital gets locked when you buy, but there's a critical issue - the model has NO concept of position sizing or partial trades.

---

## 📊 Current Decision Logic

### Action Space (3 Discrete Actions)

```
0 = SELL ALL holdings
1 = HOLD (do nothing)  
2 = BUY with 90% of cash
```

**The model does NOT decide:**
- ❌ How many shares to buy
- ❌ What percentage of portfolio to risk
- ❌ Whether to buy 10% vs 100% of affordable shares

**The model ONLY decides:**
- ✅ Which of 3 actions to take: SELL/HOLD/BUY

---

## 💰 How BUY Works (Line by Line)

Let's trace through a BUY action with real numbers:

### Scenario: BUY Action Chosen
```python
# Initial State
portfolio = {
    "cash": $10,000,
    "holdings": 0 shares,
    "total_value": $10,000
}
current_price = $150 per share
```

### Step 1: Check if BUY is Valid
```python
if self.portfolio["cash"] > current_price:  # $10,000 > $150 ✓
    # Valid! Proceed with BUY
```

### Step 2: Calculate Shares to Buy
```python
# Use 90% of cash (keep 10% buffer)
shares_to_buy = int((self.portfolio["cash"] * 0.9) / current_price)
                = int(($10,000 * 0.9) / $150)
                = int($9,000 / $150)
                = int(60)
                = 60 shares
```

**Why 90% and not 100%?**
- Keeps small cash buffer for emergencies
- Avoids rounding issues that could overdraw account

### Step 3: Execute Purchase
```python
cost = shares_to_buy * current_price
     = 60 * $150
     = $9,000

self.portfolio["cash"] -= cost         # $10,000 - $9,000 = $1,000
self.portfolio["holdings"] += shares_to_buy  # 0 + 60 = 60 shares
```

### Step 4: Update Portfolio Value
```python
holdings_value = self.portfolio["holdings"] * current_price
                = 60 * $150
                = $9,000

self.portfolio["total_value"] = self.portfolio["cash"] + holdings_value
                                = $1,000 + $9,000
                                = $10,000
```

### Final State After BUY
```python
portfolio = {
    "cash": $1,000,        # 10% buffer remains
    "holdings": 60 shares,  # Locked capital: $9,000
    "total_value": $10,000
}
```

---

## 🔒 Capital Locking Mechanism

### Example: Multiple Trading Periods

#### Period 1: BUY
```
Cash: $10,000 → $1,000 (locked $9,000 in 60 shares @ $150)
Holdings: 0 → 60 shares
```

#### Period 2: Agent Chooses BUY Again
```python
if self.portfolio["cash"] > current_price:  # $1,000 > $150 ✓
    shares_to_buy = int(($1,000 * 0.9) / $150)
                  = int($900 / $150)
                  = 6 shares
    
    cost = 6 * $150 = $900
    
    # Update
    cash: $1,000 - $900 = $100
    holdings: 60 + 6 = 66 shares
```

**Capital Now Locked:** $9,900 in stocks, only $100 liquid

#### Period 3: Agent Chooses BUY Again
```python
if self.portfolio["cash"] > current_price:  # $100 < $150 ✗
    # INVALID! BUY ignored - insufficient cash
```

**This is the capital locking in action:** Once cash is spent, you CANNOT buy more until you SELL.

#### Period 4: Agent Chooses SELL
```python
if self.portfolio["holdings"] > 0:  # 66 > 0 ✓
    sell_value = 66 * current_price
                = 66 * $160  # Price went up!
                = $10,560
    
    self.portfolio["cash"] += sell_value  # $100 + $10,560 = $10,660
    self.portfolio["holdings"] = 0
```

**Capital Unlocked:** Now have $10,660 in cash, can buy again

---

## 🚨 Critical Problems with Current System

### Problem 1: No Gradual Position Building
```python
# Current: All-or-nothing
Episode Start: $10,000 cash
After 1st BUY: $1,000 cash, 60 shares (LOCKED)
After 2nd BUY: $100 cash, 66 shares (ALMOST FULLY LOCKED)

# What you SHOULD be able to do:
Episode Start: $10,000 cash
After BUY 20%: $8,000 cash, 13 shares (20% locked)
After BUY 30%: $5,600 cash, 33 shares (44% locked)
After BUY 50%: $2,800 cash, 50 shares (72% locked)
```

### Problem 2: Cannot Take Partial Profits
```python
# Current: Must sell 100% of holdings
Holdings: 66 shares worth $10,560
SELL: All 66 shares sold

# What you SHOULD be able to do:
Holdings: 66 shares worth $10,560
SELL 50%: 33 shares sold, keep 33 shares
SELL 25%: 16 shares sold, keep 50 shares
```

### Problem 3: No Risk Management
```python
# Current: No max position size
Episode 1, Day 1: BUY → 90% invested
Episode 1, Day 2: Price drops 10% → LOSE 9% of portfolio

# What you SHOULD have:
Max position size: 50% of portfolio
Even if model chooses BUY aggressively, never risk more than 50%
```

---

## 📐 Mathematical Proof of Capital Locking

### Formula for Maximum Trades
```
Given:
- Initial cash: C₀
- Stock price: P
- Buy percentage: 90%

Trade 1:
  Shares₁ = ⌊(C₀ × 0.9) / P⌋
  Cash₁ = C₀ - (Shares₁ × P)

Trade 2:
  Shares₂ = ⌊(Cash₁ × 0.9) / P⌋
  Cash₂ = Cash₁ - (Shares₂ × P)

Trade 3:
  Shares₃ = ⌊(Cash₂ × 0.9) / P⌋
  Cash₃ = Cash₂ - (Shares₃ × P)

Maximum consecutive BUYs ≈ log₀.₉(P/C₀) / log(0.9)
```

### Example Calculation
```
C₀ = $10,000
P = $150
Max BUYs = log₀.₉(150/10000) / log(0.9) ≈ 5-6 trades

After 5 consecutive BUYs:
  Cash < $150 → Cannot buy anymore → Capital fully locked
```

---

## 🔧 How to Fix This

### Solution 1: Expand Action Space (Discrete)

**Current (3 actions):**
```python
[SELL_ALL, HOLD, BUY_MAX]
```

**Improved (7 actions):**
```python
[
    0: SELL_ALL,
    1: SELL_50%,
    2: SELL_25%,
    3: HOLD,
    4: BUY_25%,
    5: BUY_50%,
    6: BUY_MAX
]
```

**Implementation:**
```python
def _execute_action(self, action: int, current_price: float):
    if action == 0:  # SELL ALL
        sell_pct = 1.0
    elif action == 1:  # SELL 50%
        sell_pct = 0.5
    elif action == 2:  # SELL 25%
        sell_pct = 0.25
    elif action == 3:  # HOLD
        return True
    elif action == 4:  # BUY 25%
        buy_pct = 0.25
    elif action == 5:  # BUY 50%
        buy_pct = 0.5
    elif action == 6:  # BUY MAX (90%)
        buy_pct = 0.9
```

### Solution 2: Continuous Action Space (Better!)

**Use PPO or DDPG instead of DQN:**
```python
# Model outputs continuous value: -1.0 to +1.0
action = agent.get_action(state)  # Returns e.g., 0.73

# Interpret as percentage:
if action < -0.1:  # Negative = SELL
    sell_pct = abs(action)  # -0.73 → SELL 73%
elif action > 0.1:  # Positive = BUY
    buy_pct = action  # 0.73 → BUY 73% of available
else:  # -0.1 to 0.1 = HOLD
    pass
```

**Advantages:**
- Agent learns exact position sizes
- Smooth transitions (no jumping from 0% to 90%)
- More realistic trading behavior

### Solution 3: Add Position Constraints

**Regardless of model choice:**
```python
MAX_POSITION_SIZE = 0.70  # Never more than 70% in stocks
MIN_CASH_RESERVE = 0.15   # Always keep 15% cash

def _execute_action(self, action: int, current_price: float):
    if action == BUY:
        # Calculate max shares considering constraints
        max_value_in_stocks = self.portfolio["total_value"] * MAX_POSITION_SIZE
        current_value_in_stocks = self.portfolio["holdings"] * current_price
        
        # Can only buy up to constraint
        available_to_buy = max_value_in_stocks - current_value_in_stocks
        
        # Also respect minimum cash reserve
        max_cash_to_spend = self.portfolio["cash"] - (self.portfolio["total_value"] * MIN_CASH_RESERVE)
        
        # Take minimum of both constraints
        actual_buy_amount = min(available_to_buy, max_cash_to_spend)
        
        shares_to_buy = int(actual_buy_amount / current_price)
```

---

## 📊 Real Example from Your Training

Looking at Episode 50:
```json
{
  "episode": 50,
  "actions": {
    "SELL": 1,
    "HOLD": 8,
    "BUY": 40
  }
}
```

### What Actually Happened:

```
Step 1: BUY → Locked $9,000 (90% of $10,000)
Step 2: BUY → Locked $900 (90% of $1,000)
Step 3: BUY → Locked $90 (90% of $100)
Step 4: BUY → IGNORED (cash < $150)
Step 5: BUY → IGNORED (cash < $150)
...
Step 40: BUY → IGNORED (cash < $150)
```

**Out of 40 BUY actions:**
- ~3-4 actually executed
- ~36-37 were IGNORED due to insufficient cash

**This is why you NEED to penalize invalid actions!**

---

## 🎯 Recommended Immediate Fix

### Add to `_execute_action()`:

```python
def _execute_action(self, action: int, current_price: float) -> bool:
    """Execute action and return whether it was valid."""
    
    action_executed = False
    
    if action == 0:  # SELL
        if self.portfolio["holdings"] > 0:
            # Calculate what percentage to sell (default: 100%)
            sell_percentage = 1.0  # TODO: Make this configurable
            
            shares_to_sell = int(self.portfolio["holdings"] * sell_percentage)
            sell_value = shares_to_sell * current_price
            
            self.portfolio["cash"] += sell_value
            self.portfolio["holdings"] -= shares_to_sell
            action_executed = True
            
            print(f"    SELL: {shares_to_sell}/{self.portfolio['holdings']+shares_to_sell} shares "
                  f"({sell_percentage*100:.0f}%) → ${sell_value:.2f}")
        else:
            print(f"    SELL INVALID: No holdings")
    
    elif action == 2:  # BUY
        if self.portfolio["cash"] > current_price:
            # Calculate what percentage to buy (default: 90%)
            buy_percentage = 0.9  # TODO: Make this configurable
            
            # Respect position limits
            max_position_value = self.portfolio["total_value"] * 0.70  # 70% max
            current_position_value = self.portfolio["holdings"] * current_price
            
            if current_position_value < max_position_value:
                available_to_invest = min(
                    self.portfolio["cash"] * buy_percentage,
                    max_position_value - current_position_value
                )
                
                shares_to_buy = int(available_to_invest / current_price)
                
                if shares_to_buy > 0:
                    cost = shares_to_buy * current_price
                    self.portfolio["cash"] -= cost
                    self.portfolio["holdings"] += shares_to_buy
                    action_executed = True
                    
                    print(f"    BUY: {shares_to_buy} shares @ ${current_price:.2f} "
                          f"(${cost:.2f}, {(cost/self.portfolio['total_value'])*100:.1f}% of portfolio)")
                else:
                    print(f"    BUY INVALID: Insufficient cash")
            else:
                print(f"    BUY INVALID: Max position limit reached (70%)")
        else:
            print(f"    BUY INVALID: Cash ${self.portfolio['cash']:.2f} < Price ${current_price:.2f}")
    
    else:  # HOLD
        action_executed = True
        holdings_value = self.portfolio["holdings"] * current_price
        print(f"    HOLD: Cash=${self.portfolio['cash']:.2f} ({(self.portfolio['cash']/self.portfolio['total_value'])*100:.0f}%), "
              f"Holdings={self.portfolio['holdings']} shares (${holdings_value:.2f}, "
              f"{(holdings_value/self.portfolio['total_value'])*100:.0f}%)")
    
    # Update portfolio value
    holdings_value = self.portfolio["holdings"] * current_price
    self.portfolio["total_value"] = self.portfolio["cash"] + holdings_value
    self.portfolio["total_return_pct"] = (
        (self.portfolio["total_value"] - self.initial_capital) / self.initial_capital * 100
    )
    
    return action_executed
```

---

## 💡 Key Takeaways

1. **Capital IS locked** when you buy - this is correct and intentional
2. **Position sizing is FIXED** at 90% per trade - this is the problem
3. **No partial trades** - must sell/buy all-or-nothing
4. **Many BUY actions are IGNORED** due to locked capital
5. **Model doesn't learn constraints** because invalid actions aren't penalized

### To Make Model Production-Ready:

1. ✅ **Add position limits** (max 70% in stocks)
2. ✅ **Penalize invalid actions** (reward -= 1.0)
3. ✅ **Better logging** (show % of portfolio traded)
4. 🔄 **Future: Expand action space** (25%, 50%, 100% trades)
5. 🔄 **Future: Use continuous actions** (PPO/DDPG)

The math and capital tracking is already correct - you just need better control over position sizing! 🎯
