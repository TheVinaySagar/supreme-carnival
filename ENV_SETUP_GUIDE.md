# 🔐 Environment Variables Setup Guide

## Quick Setup

### 1. Create .env file

Run the setup script:
```bash
./setup_env.sh
```

Or manually:
```bash
cp .env.example .env
nano .env  # Edit and add your API keys
```

### 2. Add Your API Keys

Edit `.env` file:

```bash
# Required for RL with LLM features
OPENAI_API_KEY=sk-proj-your-actual-key-here

# Optional: Alternative LLM providers
ANTHROPIC_API_KEY=your-anthropic-key-here
GOOGLE_API_KEY=your-google-key-here

# Optional: Market data
FINNHUB_API_KEY=your-finnhub-key-here

# Optional: Social media sentiment
REDDIT_CLIENT_ID=your-reddit-id
REDDIT_CLIENT_SECRET=your-reddit-secret
REDDIT_USER_AGENT=TradingAgents/1.0
```

### 3. Verify Setup

The `.env` file is automatically loaded by:
- ✅ Traditional TradingAgents (`main.py`, `cli/main.py`)
- ✅ RL Training (`tradingagents/rl/train_rl_agent.py`)
- ✅ RL Evaluation (`tradingagents/rl/evaluate_rl_agent.py`)
- ✅ State Encoder (for OpenAI embeddings)

## Usage

### No More Manual Exports!

**Before (old way):**
```bash
export OPENAI_API_KEY="sk-..."
export FINNHUB_API_KEY="..."
python main.py
```

**Now (new way):**
```bash
# Just run - keys loaded automatically from .env
python main.py
python -m tradingagents.rl.train_rl_agent --tickers AAPL
```

### Priority Order

1. **Environment variables** (if set in shell)
2. **.env file** (automatically loaded)
3. **Default values** (where applicable)

Example:
```bash
# This will override the .env file value
export OPENAI_API_KEY="temporary-key"
python main.py

# After exit, .env value is used again
```

## Security Best Practices

### ✅ DO:
- Keep `.env` file in project root
- Add `.env` to `.gitignore` (already done)
- Use `.env.example` as a template for others
- Never commit real API keys

### ❌ DON'T:
- Commit `.env` to git
- Share `.env` file publicly
- Hardcode API keys in source code
- Store keys in documentation

## Troubleshooting

### Problem: "OPENAI_API_KEY not found"

**Solution:**
```bash
# Check if .env exists
ls -la .env

# Check if python-dotenv is installed
pip show python-dotenv

# Verify .env has correct format (no quotes needed)
cat .env
# Should show: OPENAI_API_KEY=sk-...

# Test loading
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('Key loaded:', bool(os.getenv('OPENAI_API_KEY')))"
```

### Problem: Keys not loading

**Solution:**
```bash
# Ensure .env is in project root
pwd  # Should be /home/vinay/Documents/TradingAgents
ls .env  # Should exist

# Check file format (no spaces around =)
# Wrong: OPENAI_API_KEY = sk-...
# Wrong: OPENAI_API_KEY="sk-..."
# Correct: OPENAI_API_KEY=sk-...
```

### Problem: Different keys for different projects

**Solution:**
```bash
# Use separate .env files
cd /path/to/project1
cat .env  # Project 1 keys

cd /path/to/project2
cat .env  # Project 2 keys (different)

# Each project loads its own .env automatically
```

## Example .env File

```bash
# ==============================================
# TradingAgents API Keys
# ==============================================

# OpenAI (Required for LLM features)
OPENAI_API_KEY=sk-proj-abc123xyz...

# Anthropic Claude (Optional)
ANTHROPIC_API_KEY=sk-ant-abc123...

# Google Gemini (Optional)
GOOGLE_API_KEY=AIzaSy...

# Market Data (Optional)
FINNHUB_API_KEY=c123abc...

# Reddit (Optional - for social sentiment)
REDDIT_CLIENT_ID=AbC123XyZ
REDDIT_CLIENT_SECRET=abc123-xyz...
REDDIT_USER_AGENT=TradingAgents/1.0 by YourUsername

# Results Directory (Optional)
TRADINGAGENTS_RESULTS_DIR=./results
```

## Where Keys Are Used

### OpenAI API Key
- **Used by:** State encoder (embeddings), LLM agents
- **Required for:** `--use-llm-features` flag in RL training
- **Files:** `state_encoder.py`, all LLM agent nodes

### Finnhub API Key
- **Used by:** News data fetching
- **Required for:** `get_finnhub_news()` in dataflows
- **Files:** `finnhub_utils.py`, `interface.py`

### Reddit Keys
- **Used by:** Social media sentiment analysis
- **Required for:** Social Media Analyst agent
- **Files:** `reddit_utils.py`, `social_media_analyst.py`

## Migration from Old Setup

If you were using manual exports:

**Old setup:**
```bash
# In ~/.bashrc or run before each session
export OPENAI_API_KEY="..."
export FINNHUB_API_KEY="..."
```

**New setup:**
```bash
# One-time setup
cp .env.example .env
nano .env  # Add keys

# Keys now loaded automatically
python main.py  # Works!
```

## Multiple Environments

For development vs production:

```bash
# Development
cp .env.example .env.dev
# Edit .env.dev with dev keys

# Production
cp .env.example .env.prod
# Edit .env.prod with prod keys

# Use specific env file
python -c "from dotenv import load_dotenv; load_dotenv('.env.dev')"
```

## Summary

✅ **Setup complete!** Your API keys are now:
- Automatically loaded from `.env` file
- Kept secure (not in git)
- Easy to manage (one file)
- Portable across sessions

No more manual exports needed! 🎉
