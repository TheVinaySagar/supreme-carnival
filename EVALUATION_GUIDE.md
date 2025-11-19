# RL Agent Evaluation Guide

## Overview

This guide explains how to evaluate your trained RL trading agent on test data.

---

## 📍 Model Location

After training, your models are saved in:
```
tradingagents/rl/models/checkpoints/
```

**Model naming format:**
- `{MODEL_NAME}_episode_{N}.pt` - Checkpoint at episode N
- `{MODEL_NAME}_final.pt` - Final model after all episodes

**Example:**
- `RELIANCE_NS_2023_TRAIN_episode_50.pt`
- `RELIANCE_NS_2023_TRAIN_final.pt`

---

## 🚀 Quick Start - Evaluate on Test Data

### 1. Basic Evaluation (Fast, No LLM)

```bash
python -m tradingagents.rl.evaluate_rl_agent \
  --model-path tradingagents/rl/models/checkpoints/RELIANCE_NS_2023_TRAIN_final.pt \
  --tickers RELIANCE.NS \
  --start-date 2023-10-17 \
  --end-date 2023-12-22 \
  --initial-capital 10000 \
  --output-dir ./eval_results
```

**Use this for:** Quick testing without LLM analysis (faster)

---

### 2. Full Evaluation (With LLM Features)

```bash
python -m tradingagents.rl.evaluate_rl_agent \
  --model-path tradingagents/rl/models/checkpoints/RELIANCE_NS_2023_TRAIN_final.pt \
  --tickers RELIANCE.NS \
  --start-date 2023-10-17 \
  --end-date 2023-12-22 \
  --initial-capital 10000 \
  --use-llm-features \
  --save-trades \
  --output-dir ./eval_results
```

**Use this for:** Complete evaluation matching training conditions (uses cached LLM reports)

---

## 📊 What Gets Generated

After evaluation, you'll get these files in `eval_results/TICKER/`:

### 1. **Evaluation Report** (`TICKER_evaluation_report.txt`)
- Summary table comparing RL agent vs baselines
- Metrics: Return, Sharpe Ratio, Max Drawdown, Win Rate, etc.
- Human-readable text format

### 2. **Detailed Results** (`TICKER_detailed_results_TIMESTAMP.json`)
- Complete JSON with all metrics
- Portfolio value history
- Action sequences
- Baseline comparisons
- Timestamp for tracking multiple runs

### 3. **Trade Log** (`TICKER_trade_log_TIMESTAMP.csv`)
- Step-by-step trade details
- Columns: step, date, price, action, cash, holdings, portfolio_value, reward
- Easy to analyze in Excel/Python

### 4. **Portfolio History** (`TICKER_portfolio_history_TIMESTAMP.csv`)
- Time series of portfolio evolution
- Columns: date, price, portfolio_value, cash, holdings, action
- Perfect for plotting and visualization

---

## 📈 Key Metrics Explained

| Metric | Description | Good Value |
|--------|-------------|------------|
| **Total Return (%)** | Final profit/loss percentage | > 0% (positive) |
| **Sharpe Ratio** | Risk-adjusted returns | > 1.0 (good), > 2.0 (excellent) |
| **Max Drawdown (%)** | Largest peak-to-trough decline | < -10% (acceptable) |
| **Win Rate (%)** | Percentage of profitable trades | > 50% |
| **Volatility (%)** | Standard deviation of returns | Lower is more stable |
| **Number of Trades** | Total buy + sell actions | Balance efficiency vs activity |

---

## 🎯 Evaluation Workflow

### Step 1: Train on 80% data
```bash
python -m tradingagents.rl.train_rl_agent \
  --tickers RELIANCE.NS \
  --start-date 2023-01-02 \
  --end-date 2023-10-10 \
  --num-episodes 50 \
  --model-name RELIANCE_NS_2023_TRAIN \
  --use-llm-features
```

**This creates:**
- Training period: Jan 2 - Oct 10, 2023 (39 weeks, 80%)
- Model saved to: `tradingagents/rl/models/checkpoints/RELIANCE_NS_2023_TRAIN_final.pt`

---

### Step 2: Evaluate on 20% test data
```bash
python -m tradingagents.rl.evaluate_rl_agent \
  --model-path tradingagents/rl/models/checkpoints/RELIANCE_NS_2023_TRAIN_final.pt \
  --tickers RELIANCE.NS \
  --start-date 2023-10-17 \
  --end-date 2023-12-22 \
  --initial-capital 10000 \
  --use-llm-features \
  --save-trades \
  --output-dir ./eval_results
```

**This evaluates on:**
- Test period: Oct 17 - Dec 22, 2023 (10 weeks, 20%)
- Unseen data - measures generalization!

---

### Step 3: Analyze Results

**Check the evaluation report:**
```bash
cat eval_results/RELIANCE.NS/RELIANCE.NS_evaluation_report.txt
```

**Expected output:**
```
================================================================================
EVALUATION RESULTS: RELIANCE.NS
================================================================================

                  Return (%)  Sharpe Ratio  Max Drawdown (%)  Win Rate (%)  ...
RL Agent               12.50          1.85             -8.20         62.50
Buy and Hold            8.30          1.20            -12.40         100.00
Random                 -2.10         -0.30            -18.50          40.00

================================================================================
```

**Interpret:**
- ✅ RL Agent beat Buy & Hold: Good generalization!
- ✅ Positive Sharpe Ratio: Risk-adjusted returns are positive
- ✅ Max Drawdown < -10%: Acceptable risk management
- ✅ Win Rate > 50%: More wins than losses

---

## 🔍 Advanced: Comparing Multiple Checkpoints

Test different episodes to find the best model:

```bash
# Test episode 20
python -m tradingagents.rl.evaluate_rl_agent \
  --model-path tradingagents/rl/models/checkpoints/RELIANCE_NS_2023_TRAIN_episode_20.pt \
  --tickers RELIANCE.NS \
  --start-date 2023-10-17 \
  --end-date 2023-12-22 \
  --output-dir ./eval_results/episode_20

# Test episode 30
python -m tradingagents.rl.evaluate_rl_agent \
  --model-path tradingagents/rl/models/checkpoints/RELIANCE_NS_2023_TRAIN_episode_30.pt \
  --tickers RELIANCE.NS \
  --start-date 2023-10-17 \
  --end-date 2023-12-22 \
  --output-dir ./eval_results/episode_30

# Test final (episode 50)
python -m tradingagents.rl.evaluate_rl_agent \
  --model-path tradingagents/rl/models/checkpoints/RELIANCE_NS_2023_TRAIN_final.pt \
  --tickers RELIANCE.NS \
  --start-date 2023-10-17 \
  --end-date 2023-12-22 \
  --output-dir ./eval_results/final
```

**Then compare:** Which episode performed best on test data?

---

## 🎨 Visualization (Coming Soon)

You can plot the portfolio history CSV:

```python
import pandas as pd
import matplotlib.pyplot as plt

# Load portfolio history
df = pd.read_csv("eval_results/RELIANCE.NS/RELIANCE.NS_portfolio_history_*.csv")

# Plot portfolio value over time
plt.figure(figsize=(12, 6))
plt.plot(df['date'], df['portfolio_value'], label='RL Agent')
plt.axhline(y=10000, color='r', linestyle='--', label='Initial Capital')
plt.xlabel('Date')
plt.ylabel('Portfolio Value ($)')
plt.title('RL Agent Performance - Test Period')
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('portfolio_performance.png')
plt.show()
```

---

## 🚨 Troubleshooting

### Error: "Model file not found"
**Solution:** Check the exact model path:
```bash
ls -lh tradingagents/rl/models/checkpoints/
```

### Error: "State dimension mismatch"
**Solution:** Ensure `--use-llm-features` matches training:
- If trained WITH LLM: use `--use-llm-features` in eval
- If trained WITHOUT LLM: omit `--use-llm-features` in eval

### Error: "No cached reports found"
**Solution:** First run will generate LLM reports. Subsequent runs will be fast (cached).

### Low test performance vs training
**Possible causes:**
- Overfitting: Model learned training data too well
- Market regime change: Test period has different characteristics
- Insufficient training episodes: Try training longer (100+ episodes)

---

## ✅ Success Criteria

Your model is **good** if:
1. ✅ Test return > 0% (profitable)
2. ✅ Test return > Buy & Hold (beats baseline)
3. ✅ Sharpe Ratio > 1.0 (risk-adjusted positive)
4. ✅ Max Drawdown > -15% (acceptable risk)
5. ✅ Win Rate > 50% (more wins than losses)

Your model is **excellent** if:
6. ✅ Test return > 10%
7. ✅ Sharpe Ratio > 2.0
8. ✅ Max Drawdown > -10%
9. ✅ Win Rate > 60%
10. ✅ Lower volatility than Buy & Hold

---

## 📚 Next Steps

1. **Run evaluation on your trained model**
2. **Analyze the results** (check report, trade log, portfolio history)
3. **Compare with baselines** (should beat Buy & Hold)
4. **Try different test periods** (different market conditions)
5. **Fine-tune hyperparameters** if needed
6. **Deploy best model** for live paper trading

---

## 🎯 Quick Reference

**Minimum command (fast):**
```bash
python -m tradingagents.rl.evaluate_rl_agent \
  --model-path tradingagents/rl/models/checkpoints/YOUR_MODEL_final.pt \
  --tickers YOUR_TICKER \
  --start-date TEST_START \
  --end-date TEST_END
```

**Recommended command (complete):**
```bash
python -m tradingagents.rl.evaluate_rl_agent \
  --model-path tradingagents/rl/models/checkpoints/YOUR_MODEL_final.pt \
  --tickers YOUR_TICKER \
  --start-date TEST_START \
  --end-date TEST_END \
  --use-llm-features \
  --save-trades \
  --output-dir ./eval_results
```

---

**Happy Evaluating! 🚀📈**
