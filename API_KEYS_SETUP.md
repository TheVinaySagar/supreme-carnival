# 🔑 Quick Setup: Free Data Source API Keys

## What You Need (All FREE!)

### 1. OpenAI API Key (Required for LLM)
**Cost:** Pay-as-you-go (gpt-4o-mini: ~$0.15 per 1M tokens)

**Get it:**
1. Visit: https://platform.openai.com/api-keys
2. Sign up / Log in
3. Click "Create new secret key"
4. Copy the key (starts with `sk-proj-...`)
5. Add to `.env`:
   ```bash
   OPENAI_API_KEY=sk-proj-your-key-here
   ```

---

### 2. Finnhub API Key (Optional - For News)
**Cost:** FREE (60 calls/minute)

**Get it:**
1. Visit: https://finnhub.io/register
2. Fill in email and password
3. Verify email
4. Go to: https://finnhub.io/dashboard
5. Copy your API key
6. Add to `.env`:
   ```bash
   FINNHUB_API_KEY=your-key-here
   ```

**What it gives you:**
- Company news articles
- Up to 60 requests per minute
- Historical news data

---

### 3. Reddit API Credentials (Optional - For Social Sentiment)
**Cost:** FREE (unlimited for read-only)

**Get it:**
1. Visit: https://www.reddit.com/prefs/apps
2. Log in to Reddit
3. Scroll down, click "create another app..."
4. Fill in:
   - Name: `TradingAgents`
   - Type: Select **"script"**
   - Description: `Trading sentiment analysis`
   - About URL: (leave blank)
   - Redirect URI: `http://localhost:8080`
5. Click "create app"
6. Copy the credentials:
   - **Client ID**: Under the app name (14 characters)
   - **Client Secret**: Click "edit", shows "secret" field

7. Add to `.env`:
   ```bash
   REDDIT_CLIENT_ID=your-14-char-id
   REDDIT_CLIENT_SECRET=your-secret-here
   REDDIT_USER_AGENT=TradingAgents/1.0 by YourRedditUsername
   ```

**What it gives you:**
- Social media sentiment from financial subreddits
- Post titles, scores, comments
- Trending stock discussions

---

## Complete .env File Template

```bash
# =============================================
# TradingAgents Configuration
# =============================================

# OpenAI (REQUIRED for LLM features)
OPENAI_API_KEY=sk-proj-your-key-here

# Finnhub (OPTIONAL - for news data)
FINNHUB_API_KEY=your-finnhub-key-here

# Reddit (OPTIONAL - for social sentiment)
REDDIT_CLIENT_ID=your-14-char-id
REDDIT_CLIENT_SECRET=your-secret-here
REDDIT_USER_AGENT=TradingAgents/1.0 by YourUsername

# Alternative LLM Providers (OPTIONAL)
ANTHROPIC_API_KEY=sk-ant-your-key
GOOGLE_API_KEY=AIzaSy-your-key

# Settings (OPTIONAL)
TRADINGAGENTS_RESULTS_DIR=./results
```

---

## Quick Test

After setting up your `.env` file, test that everything works:

```bash
# Test OpenAI connection
python -c "from dotenv import load_dotenv; import os; load_dotenv(); from openai import OpenAI; client = OpenAI(); print('✅ OpenAI connected!')"

# Test Finnhub (if configured)
python -c "from dotenv import load_dotenv; import os; load_dotenv(); import finnhub; client = finnhub.Client(api_key=os.getenv('FINNHUB_API_KEY')); print('✅ Finnhub connected!', client.company_profile2(symbol='AAPL')['name'])"

# Test Reddit (if configured)
python -c "from dotenv import load_dotenv; import os; load_dotenv(); import praw; reddit = praw.Reddit(client_id=os.getenv('REDDIT_CLIENT_ID'), client_secret=os.getenv('REDDIT_CLIENT_SECRET'), user_agent=os.getenv('REDDIT_USER_AGENT')); print('✅ Reddit connected!', reddit.read_only)"
```

---

## Cost Breakdown

### With All Free APIs:

| Service | Free Tier | What You Get |
|---------|-----------|--------------|
| **yfinance** | Unlimited | Price data, technical indicators, fundamentals |
| **Finnhub** | 60 calls/min | Company news, earnings, financial data |
| **Reddit** | Unlimited (read) | Social sentiment, trending discussions |
| **OpenAI** | Pay-as-you-go | LLM for analysis (gpt-4o-mini: $0.15/$0.60 per 1M) |

### Example Daily Costs:

**Traditional TradingAgents (1 decision/day):**
- LLM calls: ~$0.03-0.05
- Data APIs: $0 (all free)
- **Total: ~$0.05/day = $1.50/month**

**RL Training (without LLM):**
- LLM calls: $0
- Data APIs: $0
- **Total: $0**

**RL Training (with LLM, 100 episodes):**
- LLM calls: ~$0.30
- Data APIs: $0
- **Total: $0.30 one-time**

---

## Alternative: No API Keys at All!

If you don't want to set up ANY API keys:

### Option 1: Use Cached Data Only
```python
config = DEFAULT_CONFIG.copy()
config["online_tools"] = False  # Use cached CSV files
# Don't use --use-llm-features flag in RL training
```

**What you can do:**
- ✅ Train RL agents on historical data
- ✅ Backtest strategies
- ✅ Test the system
- ❌ Can't get real-time news/sentiment
- ❌ Can't use LLM analysis features

### Option 2: Use Free Local LLM (Ollama)
```bash
# Install Ollama
curl https://ollama.ai/install.sh | sh

# Download a model
ollama pull llama3.1

# Configure TradingAgents
config["llm_provider"] = "ollama"
config["quick_think_llm"] = "llama3.1"
config["backend_url"] = "http://localhost:11434/v1"
```

**What you can do:**
- ✅ Run LLM analysis locally (FREE!)
- ✅ No OpenAI API costs
- ⚠️ Slower than cloud LLMs
- ⚠️ Lower quality than GPT-4

---

## Recommended Minimal Setup

**For getting started:**
```bash
# Just OpenAI key - everything else is optional
OPENAI_API_KEY=sk-proj-your-key-here
```

**Cost:** ~$0.05 per trading decision

**What you get:**
- ✅ Full LLM analysis
- ✅ Price data (yfinance - free)
- ✅ Technical indicators (free)
- ❌ No real-time news (but not critical)
- ❌ No social sentiment (but not critical)

---

## Pro Setup (All APIs)

**For production trading:**
```bash
OPENAI_API_KEY=sk-proj-your-key-here
FINNHUB_API_KEY=your-key-here
REDDIT_CLIENT_ID=your-id
REDDIT_CLIENT_SECRET=your-secret
REDDIT_USER_AGENT=TradingAgents/1.0
```

**Cost:** ~$0.05 per trading decision (same, APIs are free!)

**What you get:**
- ✅ Full LLM analysis
- ✅ Price data
- ✅ Technical indicators
- ✅ Real-time news
- ✅ Social sentiment
- ✅ Complete market picture

---

## Summary

**Minimum required:** Just OpenAI API key  
**Recommended:** OpenAI + Finnhub (both take 2 minutes to set up)  
**Pro:** All APIs (takes 10 minutes total)  

**All data APIs are FREE - only pay for LLM usage!** 🎉
