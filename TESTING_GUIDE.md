# 📊 RELIANCE.NS Training & Testing Guide

## Dataset Split

### Full Dataset (2023)
- **Total:** 49 weeks (Jan 2 - Dec 29, 2023)
- **Split:** 80% Train / 20% Test

### Training Set (80%)
- **Weeks:** 39 weeks
- **Period:** Jan 2, 2023 - Oct 10, 2023
- **Cache:** `RELIANCE.NS_2023-01-01_2023-10-31_TRAIN.json`

### Testing Set (20%)
- **Weeks:** 10 weeks  
- **Period:** Oct 17, 2023 - Dec 22, 2023
- **Cache:** `RELIANCE.NS_2023-11-01_2023-12-31_TEST.json`

---

## 🚀 STEP 1: Train the Model

### Command:
```bash
python -m tradingagents.rl.train_rl_agent \
  --tickers RELIANCE.NS \
  --start-date 2023-01-02 \
  --end-date 2023-10-10 \
  --num-episodes 50 \
  --model-name RELIANCE_NS_2023_TRAIN \
  --use-llm-features
```

### What This Does:
- Trains DQN agent on **39 weeks** (Jan-Oct 2023)
- Uses cached LLM reports (4 analysts + bull/bear debates)
- Saves model checkpoints every 10 episodes
- Final model saved as: `models/RELIANCE_NS_2023_TRAIN_final.pth`

### Expected Time:
- **Episode 1:** ~12-15 minutes (generates bull/bear debates)
- **Episodes 2-50:** ~15-20 seconds each (uses cache)
- **Total:** ~15-20 minutes for 50 episodes

### Monitor Training:
Watch these metrics improve over episodes:
- ✅ **Total Return** should increase
- ✅ **Avg Reward** should become positive (with new reward function)
- ✅ **Avg Loss** should decrease to ~0.2-0.5

---

## 🧪 STEP 2: Evaluate on Test Set (Unseen Data)

### Command:
```bash
python -m tradingagents.rl.evaluate_rl_agent \
  --tickers RELIANCE.NS \
  --start-date 2023-10-17 \
  --end-date 2023-12-22 \
  --model-path models/RELIANCE_NS_2023_TRAIN_final.pth \
  --use-llm-features
```

### What This Does:
- Loads trained model
- Tests on **10 unseen weeks** (Oct-Dec 2023)
- No training/updates - pure evaluation
- Epsilon = 0 (no exploration, only exploitation)

### What to Check:
1. **Return on Test Set** - Is it positive?
2. **Comparison to Buy-and-Hold** - Does agent beat baseline?
3. **Consistency** - Does agent make reasonable trades?
4. **Sharpe Ratio** - Risk-adjusted returns

---

## 📈 STEP 3: Compare Performance

### Metrics to Compare:

| Metric | Training (39 weeks) | Testing (10 weeks) | Status |
|--------|--------------------|--------------------|--------|
| Total Return | ? | ? | Should be positive on both |
| Sharpe Ratio | ? | ? | Higher = better risk-adj return |
| Max Drawdown | ? | ? | Lower = better risk mgmt |
| Win Rate | ? | ? | % of profitable trades |
| Num Trades | ? | ? | Not overtrading? |

### Good Signs ✅
- Test return is **positive** (agent makes money)
- Test return is **>50% of train return** (generalizes well)
- Test return **beats buy-and-hold** baseline
- Agent doesn't overtrade (<30 trades in 10 weeks)
- Max drawdown < 15%

### Warning Signs ⚠️
- Test return is **negative** (loses money on unseen data)
- Test return is **<20% of train return** (overfitted)
- Agent trades excessively (>50 trades in 10 weeks)
- Large drawdowns (>30%)

---

## 🔍 STEP 4: Analyze Results

### Check Training Logs:
```bash
# View episode summaries
cat logs/training_RELIANCE_NS_2023_TRAIN.log
```

Look for:
- Episode returns trending upward
- Avg loss decreasing
- Epsilon decaying to 0.01

### Check Test Results:
```bash
# View test evaluation
cat logs/evaluation_RELIANCE_NS_test.log
```

Compare:
- Test vs Train returns
- Test vs Buy-and-Hold returns
- Action distribution (SELL/HOLD/BUY counts)

---

## 📊 STEP 5: Visualize (Optional)

If you have plotting tools:

```python
import json
import matplotlib.pyplot as plt

# Plot training progress
with open('results/RELIANCE_NS_2023_TRAIN_metrics.json') as f:
    train_metrics = json.load(f)

plt.figure(figsize=(12, 4))

plt.subplot(1, 3, 1)
plt.plot(train_metrics['episode_returns'])
plt.title('Training Returns per Episode')
plt.xlabel('Episode')
plt.ylabel('Return %')

plt.subplot(1, 3, 2)
plt.plot(train_metrics['avg_losses'])
plt.title('Training Loss per Episode')
plt.xlabel('Episode')
plt.ylabel('Avg Loss')

plt.subplot(1, 3, 3)
plt.plot(train_metrics['epsilon'])
plt.title('Exploration Rate (Epsilon)')
plt.xlabel('Episode')
plt.ylabel('Epsilon')

plt.tight_layout()
plt.savefig('training_progress.png')
```

---

## 🎯 Success Criteria

### Minimum Requirements:
- ✅ Train return: **>5%** on 39 weeks
- ✅ Test return: **>3%** on 10 weeks (positive!)
- ✅ Test/Train ratio: **>0.4** (not overfitted)

### Good Performance:
- ✅ Train return: **>10%**
- ✅ Test return: **>5%**
- ✅ Test/Train ratio: **>0.6**
- ✅ Beats buy-and-hold on test set

### Excellent Performance:
- ✅ Train return: **>15%**
- ✅ Test return: **>10%**
- ✅ Test/Train ratio: **>0.8**
- ✅ Sharpe ratio: **>1.5**
- ✅ Max drawdown: **<10%**

---

## 🔧 Troubleshooting

### Problem: Test return is negative
**Solution:**
- Train for more episodes (50 → 100)
- Check if reward function is working (should be positive)
- Verify test data isn't corrupted

### Problem: Test return << Train return (overfitting)
**Solution:**
- Add regularization (increase epsilon_min)
- Reduce network complexity
- Add dropout layers
- Use more diverse training data

### Problem: Agent overtrades
**Solution:**
- Increase transaction_cost (0.02 → 0.05)
- Adjust reward function weights
- Review action selection logic

### Problem: Agent never trades
**Solution:**
- Decrease transaction_cost (0.02 → 0.01)
- Check if profit_weight is too low
- Verify epsilon is decaying properly

---

## 📝 Example Results Format

### Training Summary (Episode 50):
```
Total Return: 12.34%
Final Portfolio: $11,234.56
Avg Reward: +2.45
Avg Loss: 0.23
Actions - SELL: 15, HOLD: 180, BUY: 18
```

### Test Summary:
```
Total Return: 8.56%
Final Portfolio: $10,856.00
Buy-and-Hold Return: 6.23%
Agent Beat Baseline: ✅ Yes (+2.33%)
Max Drawdown: -8.45%
Sharpe Ratio: 1.82
```

---

## 🚨 Important Notes

1. **Cache Files Required:**
   - Training needs: `RELIANCE.NS_2023-01-01_2023-10-31_TRAIN.json`
   - Testing needs: `RELIANCE.NS_2023-11-01_2023-12-31_TEST.json`
   - Both files already created! ✅

2. **Model Checkpoints:**
   - Saved every 10 episodes in `models/` directory
   - Can resume training from checkpoint
   - Best model = lowest loss or highest return

3. **LLM Features:**
   - Must use `--use-llm-features` for both train and test
   - State dimension: 9,240 (includes text embeddings)
   - Without flag: only 24 dimensions (basic features)

4. **Reproducibility:**
   - Set random seed for reproducible results
   - Cache ensures same LLM reports across runs
   - DQN is stochastic (epsilon-greedy exploration)

---

## 🎓 What Good Test Results Mean

### Generalization
If test return ≈ train return → Agent **generalizes well** to unseen data

### Robustness  
If test return > 0 → Agent **learned real patterns**, not noise

### Skill
If test return > buy-and-hold → Agent has **trading skill**, not luck

### Stability
If max drawdown < 15% → Agent manages **risk properly**

---

## 📞 Next Steps After Testing

1. **If results are good:**
   - ✅ Deploy model for live/paper trading
   - ✅ Test on other tickers (HDFCBANK.NS, TCS.NS)
   - ✅ Extend to 2024 data

2. **If results are mediocre:**
   - 🔄 Tune hyperparameters (learning rate, gamma, batch size)
   - 🔄 Adjust reward function weights
   - 🔄 Train for more episodes (100-200)

3. **If results are poor:**
   - ⚠️ Review reward function (is it aligned?)
   - ⚠️ Check data quality (cache corruption?)
   - ⚠️ Simplify network architecture
   - ⚠️ Use longer training periods (full year)

---

**Good luck with training! 🚀**

Run the commands in order and monitor the results. The 80/20 split ensures you can measure true out-of-sample performance!
