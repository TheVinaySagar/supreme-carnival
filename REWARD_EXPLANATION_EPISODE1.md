# Why Episode 1 Had -103 Reward for +7.73% Return

## Understanding the Mismatch

**Total Return** = Final portfolio value vs initial capital = **+7.73%** ✅  
**Total Reward** = Sum of all step rewards = **-103.29** ❌

These are DIFFERENT metrics!

---

## How Rewards Work

### 1. **Total Reward = Sum of Individual Step Rewards**

The agent takes 39 steps (weeks). Each step gets a reward based on:
- Portfolio value change from PREVIOUS step to CURRENT step
- Transaction costs if action changed

```
Episode has 39 steps
Total Reward = Step 1 reward + Step 2 reward + ... + Step 39 reward
```

### 2. **Path Matters, Not Just Final Destination**

Example path that gives +7.73% return but negative rewards:

```
Week 1: $10,000 (start)
Week 2: Buy 8 shares @ $1,085 → $8,684 value
Week 3: Price drops to $1,050 → Value = $8,400 → REWARD = -28 (loss!)
Week 4: Price rises to $1,110 → Value = $8,880 → REWARD = +4.8 (gain)
Week 5: Sell all → $8,880 cash
Week 6: Hold cash while market rises → OPPORTUNITY COST = -10
...
Week 39: Final = $10,773 → Total Return = +7.73% ✅
```

**But along the way:**
- Many steps with losses → Negative rewards
- Invalid actions (sell with no holdings) → -0.02 penalty each
- Holding cash during bull runs → Missed gains = negative rewards

---

## Episode 1 Analysis

### Actions Taken:
- **SELL: 14 times** (many invalid → 14 × -0.02 = -0.28)
- **HOLD: 15 times** (some with no holdings → no reward)
- **BUY: 10 times**

### Why Negative Total Reward?

1. **Early invalid actions**:
   - First 5 steps: All SELL/HOLD with no holdings
   - Debug shows: `before=$10000, after=$10000, return=0%`
   - But SELL attempts = -0.02 penalty each

2. **Price volatility losses**:
   - Buy at $1,085, price drops to $1,050 → -3.2% loss → Reward ≈ -6.4
   - Multiple cycles of buy-high, sell-low

3. **Missed opportunities**:
   - Holding cash while prices rise → No gains, but baseline moves up
   - Selling too early, buying too late

4. **Transaction costs**:
   - 14 SELLs + 10 BUYs = 24 action changes × -0.02 = -0.48

---

## The Root Cause: Portfolio Tracking Still Broken!

Look at the debug output:

```
🔍 REWARD CALC #1:
  before=$10000.00, after=$10000.00
  return=0.0000%
```

**This is WRONG!** Even after BUY/SELL actions, the values don't change.

### What's Happening:

The code shows:
```python
portfolio_value_before = self.prev_portfolio_value  # $10,000
action_executed = self._execute_action(action, current_price)  # BUY 8 shares
portfolio_value_after = self.portfolio["total_value"]  # Should be $1,316 cash + $8,684 holdings
```

But debug shows `after=$10000` → The portfolio value is NOT being updated!

---

## Next Steps

1. **Investigate portfolio value calculation**:
   - Check if `_execute_action()` actually updates portfolio
   - Verify `self.portfolio["total_value"]` is recalculated after actions

2. **Add more debug logging**:
   - Print portfolio state BEFORE and AFTER each action
   - Show cash, holdings, and calculated total value

3. **Fix the actual bug**:
   - The portfolio tracking fix didn't work
   - Need to find where portfolio value calculation is broken

---

## Expected Behavior

After fix, Episode 1 should show:

```
🔍 REWARD CALC #1:
  before=$10000.00, after=$10000.00  # HOLD with no holdings → correct
  return=0.0000%

🔍 REWARD CALC #10:
  before=$10044.00, after=$10620.00  # Price rose + action taken
  return=+5.73%
```

**Total Reward should be positive if final return is +7.73%!**
