"""
RL Trading Environment

Gym-like environment that wraps TradingAgents for RL training.
"""

import numpy as np
from typing import Dict, Any, Tuple, Optional, List
from datetime import datetime, timedelta
import pandas as pd
import os
import json
import hashlib

from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.rl.state_encoder import TradingStateEncoder
from tradingagents.rl.reward_calculator import RewardCalculator


class TradingEnvironment:
    """
    Gym-like trading environment for RL.
    
    Wraps TradingAgentsGraph and provides:
    - State observations (numerical + text embeddings)
    - Action execution (BUY/SELL/HOLD)
    - Reward calculation
    - Episode management
    """
    
    def __init__(
        self,
        ticker: str,
        start_date: str,
        end_date: str,
        initial_capital: float = 10000.0,
        config: Optional[Dict[str, Any]] = None,
        use_llm_features: bool = True
    ):
        """
        Initialize trading environment.
        
        Args:
            ticker: Stock ticker symbol
            start_date: Start date for episode (YYYY-MM-DD)
            end_date: End date for episode (YYYY-MM-DD)
            initial_capital: Starting cash
            config: Configuration dict
            use_llm_features: Whether to generate LLM reports for state
        """
        self.ticker = ticker
        self.start_date = datetime.strptime(start_date, "%Y-%m-%d")
        self.end_date = datetime.strptime(end_date, "%Y-%m-%d")
        self.initial_capital = initial_capital
        self.config = config or {}
        self.use_llm_features = use_llm_features
        
        # Initialize components
        self.state_encoder = TradingStateEncoder(self.config)
        self.reward_calculator = RewardCalculator()
        
        # LLM report cache (in-memory)
        self.llm_cache = {}
        self.cache_dir = os.path.join(
            self.config.get("data_cache_dir", "./tradingagents/dataflows/data_cache"),
            "llm_reports"
        )
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Trading agents (only if using LLM features)
        self.trading_graph = None
        if self.use_llm_features:
            self.trading_graph = TradingAgentsGraph(
                selected_analysts=["market", "news", "fundamentals", "social"],  # All 4 analysts
                debug=False,
                config=self.config
            )
            # Load cached reports if available
            self._load_llm_cache()
        
        # Load historical price data
        self.price_data = self._load_price_data()
        all_dates = list(self.price_data.keys())
        
        # Sample weekly (every 5 trading days) for more efficient training
        self.trading_dates = all_dates[::5]  # Take every 5th day
        
        print(f"Weekly sampling: {len(all_dates)} days → {len(self.trading_dates)} trading periods")
        
        # Episode state
        self.current_step = 0
        self.current_date_idx = 0
        self.portfolio = {
            "cash": initial_capital,
            "holdings": 0,
            "total_value": initial_capital,
            "unrealized_pnl_pct": 0.0,
            "total_return_pct": 0.0
        }
        self.prev_action = 1  # Start with HOLD
        self.done = False
        
        print(f"Environment initialized: {ticker} from {start_date} to {end_date}")
        print(f"Trading frequency: WEEKLY (every 5 trading days)")
        print(f"Trading periods: {len(self.trading_dates)} (~{len(self.trading_dates)/52:.1f} years)")
        print(f"State dimension: {self.state_encoder.get_state_dim()}")
    
    def _load_price_data(self) -> Dict[str, Dict[str, float]]:
        """
        Load historical price data from cache or yfinance.
        
        Returns:
            Dictionary mapping date strings to price data
        """
        import yfinance as yf
        
        # Try to load from cache
        cache_dir = self.config.get("data_cache_dir", "./tradingagents/dataflows/data_cache")
        cache_file = os.path.join(
            cache_dir,
            f"{self.ticker}-YFin-data-{self.start_date.strftime('%Y-%m-%d')}-{self.end_date.strftime('%Y-%m-%d')}.csv"
        )
        
        if os.path.exists(cache_file):
            print(f"Loading cached price data from {cache_file}")
            df = pd.read_csv(cache_file, index_col=0, parse_dates=True)
        else:
            print(f"Fetching price data for {self.ticker}...")
            ticker_obj = yf.Ticker(self.ticker)
            df = ticker_obj.history(
                start=self.start_date.strftime("%Y-%m-%d"),
                end=(self.end_date + timedelta(days=1)).strftime("%Y-%m-%d")
            )
            
            # Save to cache
            os.makedirs(cache_dir, exist_ok=True)
            df.to_csv(cache_file)
            print(f"Cached price data to {cache_file}")
        
        # Convert to dictionary format
        price_data = {}
        for date, row in df.iterrows():
            date_str = date.strftime("%Y-%m-%d")
            price_data[date_str] = {
                "price": float(row["Close"]),
                "open": float(row["Open"]),
                "high": float(row["High"]),
                "low": float(row["Low"]),
                "volume": float(row["Volume"]),
                "price_change_pct": float((row["Close"] - row["Open"]) / row["Open"] * 100) if row["Open"] > 0 else 0.0
            }
        
        return price_data
    
    def _get_market_data(self, date_str: str) -> Dict[str, float]:
        """
        Get market data for a specific date (with technical indicators).
        
        Args:
            date_str: Date in YYYY-MM-DD format
            
        Returns:
            Dictionary with price and indicators
        """
        if date_str not in self.price_data:
            return {}
        
        # Basic price data
        data = self.price_data[date_str].copy()
        
        # Calculate simple technical indicators
        # (In production, use stockstats or similar)
        dates = [d for d in self.trading_dates if d <= date_str][-50:]  # Last 50 days
        
        if len(dates) >= 2:
            prices = [self.price_data[d]["price"] for d in dates]
            
            # SMAs
            if len(prices) >= 50:
                data["sma_50"] = np.mean(prices[-50:])
            else:
                data["sma_50"] = np.mean(prices)
            
            if len(prices) >= 20:
                data["sma_200"] = np.mean(prices)  # Use available data
                data["ema_10"] = prices[-1]  # Simplified
            
            # RSI (simplified)
            if len(prices) >= 14:
                changes = np.diff(prices[-14:])
                gains = changes[changes > 0].sum() if len(changes[changes > 0]) > 0 else 0
                losses = -changes[changes < 0].sum() if len(changes[changes < 0]) > 0 else 0
                rs = gains / losses if losses > 0 else 100
                data["rsi"] = 100 - (100 / (1 + rs))
            else:
                data["rsi"] = 50.0
            
            # Bollinger Bands
            mean = np.mean(prices[-20:])
            std = np.std(prices[-20:])
            data["boll_mid"] = mean
            data["boll_upper"] = mean + 2 * std
            data["boll_lower"] = mean - 2 * std
            
            # MACD (simplified)
            data["macd"] = 0.0
            data["macd_signal"] = 0.0
            data["macd_hist"] = 0.0
            
            # ATR (simplified)
            if len(dates) >= 2:
                high_low = [self.price_data[d]["high"] - self.price_data[d]["low"] for d in dates[-14:]]
                data["atr"] = np.mean(high_low)
            
            # VWMA (volume-weighted)
            data["vwma"] = data["price"]
        
        return data
    
    def _get_cache_key(self, date_str: str) -> str:
        """
        Generate unique cache key for ticker + date combination.
        
        Args:
            date_str: Trading date
            
        Returns:
            Cache key string
        """
        key_str = f"{self.ticker}_{date_str}"
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def _load_llm_cache(self):
        """Load cached LLM reports from disk if available."""
        cache_file = os.path.join(
            self.cache_dir,
            f"{self.ticker}_{self.start_date.strftime('%Y-%m-%d')}_{self.end_date.strftime('%Y-%m-%d')}.json"
        )
        
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r') as f:
                    self.llm_cache = json.load(f)
                print(f"✓ Loaded {len(self.llm_cache)} cached LLM reports from {cache_file}")
            except Exception as e:
                print(f"Warning: Failed to load LLM cache: {e}")
                self.llm_cache = {}
        else:
            print(f"No cached LLM reports found. Will generate fresh reports.")
    
    def _save_llm_cache(self):
        """Save LLM reports cache to disk."""
        if not self.llm_cache:
            return
        
        cache_file = os.path.join(
            self.cache_dir,
            f"{self.ticker}_{self.start_date.strftime('%Y-%m-%d')}_{self.end_date.strftime('%Y-%m-%d')}.json"
        )
        
        try:
            with open(cache_file, 'w') as f:
                json.dump(self.llm_cache, f, indent=2)
            print(f"✓ Saved {len(self.llm_cache)} LLM reports to cache: {cache_file}")
        except Exception as e:
            print(f"Warning: Failed to save LLM cache: {e}")
    
    def _get_llm_reports(self, date_str: str) -> Dict[str, str]:
        """
        Get LLM reports for the current date (cached or freshly generated).
        
        This method implements intelligent caching:
        - First checks in-memory cache
        - If not found, generates reports via trading_graph
        - Saves to cache for reuse in future episodes
        
        Args:
            date_str: Trading date
            
        Returns:
            Dictionary with analyst reports
        """
        if not self.use_llm_features or self.trading_graph is None:
            return {
                "market_report": "",
                "sentiment_report": "",
                "news_report": "",
                "fundamentals_report": ""
            }
        
        # Check cache first
        cache_key = self._get_cache_key(date_str)
        if cache_key in self.llm_cache:
            return self.llm_cache[cache_key]
        
        # Generate fresh reports
        print(f"⚡ Generating LLM reports for {self.ticker} on {date_str}...")
        try:
            # Run trading graph to get LLM analysis
            _, _ = self.trading_graph.propagate(self.ticker, date_str)
            
            # Extract reports from final state
            state = self.trading_graph.curr_state
            reports = {
                "market_report": state.get("market_report", ""),
                "sentiment_report": state.get("sentiment_report", ""),
                "news_report": state.get("news_report", ""),
                "fundamentals_report": state.get("fundamentals_report", "")
            }
            
            # Cache the reports
            self.llm_cache[cache_key] = reports
            print(f"✓ Cached LLM reports for {date_str}")
            
            return reports
            
        except Exception as e:
            print(f"Warning: Failed to generate LLM reports: {e}")
            empty_reports = {
                "market_report": "",
                "sentiment_report": "",
                "news_report": "",
                "fundamentals_report": ""
            }
            # Cache empty reports to avoid retrying
            self.llm_cache[cache_key] = empty_reports
            return empty_reports
    
    def get_valid_actions(self, current_price: float) -> List[int]:
        """
        Get list of valid actions based on current portfolio state.
        
        Args:
            current_price: Current stock price
            
        Returns:
            List of valid action indices [0=SELL, 1=HOLD, 2=BUY]
        """
        valid = []
        
        # SELL (0) - only valid if we have holdings
        if self.portfolio["holdings"] > 0:
            valid.append(0)
        
        # HOLD (1) - always valid
        valid.append(1)
        
        # BUY (2) - only valid if we have enough cash
        if self.portfolio["cash"] > current_price:
            valid.append(2)
        
        return valid
    
    def _execute_action(self, action: int, current_price: float) -> bool:
        """
        Execute trading action.
        
        Args:
            action: 0=SELL, 1=HOLD, 2=BUY
            current_price: Current stock price
            
        Returns:
            True if action was valid and executed, False otherwise
        """
        action_executed = False
        
        if action == 0:  # SELL
            if self.portfolio["holdings"] > 0:
                # Sell all holdings
                sell_value = self.portfolio["holdings"] * current_price
                self.portfolio["cash"] += sell_value
                self.portfolio["holdings"] = 0
                action_executed = True
                print(f"    SELL executed: {self.portfolio['holdings']} shares → ${sell_value:.2f}")
            else:
                print(f"    SELL ignored: No holdings to sell")
        
        elif action == 2:  # BUY
            if self.portfolio["cash"] > current_price:
                # Buy as many shares as possible (leave 10% cash buffer)
                shares_to_buy = int((self.portfolio["cash"] * 0.9) / current_price)
                if shares_to_buy > 0:
                    cost = shares_to_buy * current_price
                    self.portfolio["cash"] -= cost
                    self.portfolio["holdings"] += shares_to_buy
                    action_executed = True
                    print(f"    BUY executed: {shares_to_buy} shares @ ${current_price:.2f}")
                else:
                    print(f"    BUY ignored: Insufficient cash")
            else:
                print(f"    BUY ignored: Insufficient cash (${self.portfolio['cash']:.2f} < ${current_price:.2f})")
        
        else:  # HOLD (1)
            action_executed = True
            print(f"    HOLD: Cash=${self.portfolio['cash']:.2f}, Holdings={self.portfolio['holdings']}")
        
        # Update portfolio value
        holdings_value = self.portfolio["holdings"] * current_price
        self.portfolio["total_value"] = self.portfolio["cash"] + holdings_value
        self.portfolio["unrealized_pnl_pct"] = (
            (self.portfolio["total_value"] - self.initial_capital) / self.initial_capital * 100
        )
        self.portfolio["total_return_pct"] = self.portfolio["unrealized_pnl_pct"]
        
        return action_executed
    
    def reset(self) -> np.ndarray:
        """
        Reset environment for new episode.
        
        Saves LLM cache to disk after first episode so subsequent
        episodes can reuse cached reports.
        
        Returns:
            Initial state observation
        """
        # Save cache after episode completes (if we have any cached data)
        if self.use_llm_features and self.llm_cache:
            self._save_llm_cache()
        
        self.current_step = 0
        self.current_date_idx = 0
        self.portfolio = {
            "cash": self.initial_capital,
            "holdings": 0,
            "total_value": self.initial_capital,
            "unrealized_pnl_pct": 0.0,
            "total_return_pct": 0.0
        }
        self.episode_start_value = self.initial_capital  # Track episode start for episode return
        self.prev_action = 1
        self.done = False
        self.reward_calculator.reset()
        
        # Get initial state
        return self._get_state()
    
    def _get_state(self) -> np.ndarray:
        """
        Get current state observation.
        
        Returns:
            State vector
        """
        if self.current_date_idx >= len(self.trading_dates):
            # Return zero state if out of bounds
            return np.zeros(self.state_encoder.get_state_dim(), dtype=np.float32)
        
        current_date = self.trading_dates[self.current_date_idx]
        
        # Get market data
        market_data = self._get_market_data(current_date)
        
        # Get LLM reports (optional)
        llm_reports = self._get_llm_reports(current_date)
        
        # Construct full state
        state = {
            "market_data": market_data,
            "portfolio_state": self.portfolio,
            "trade_date": current_date,
            **llm_reports
        }
        
        # Encode to vector
        return self.state_encoder.encode_state(state)
    
    def step(self, action: int) -> Tuple[np.ndarray, float, bool, Dict[str, Any]]:
        """
        Take one step in the environment.
        
        Args:
            action: Action to take (0=SELL, 1=HOLD, 2=BUY)
            
        Returns:
            Tuple of (next_state, reward, done, info)
        """
        if self.done:
            raise RuntimeError("Episode is done. Call reset() to start new episode.")
        
        # Get current price and valid actions
        current_date = self.trading_dates[self.current_date_idx]
        current_price = self.price_data[current_date]["price"]
        valid_actions = self.get_valid_actions(current_price)
        
        # Store portfolio value before action
        portfolio_value_before = self.portfolio["total_value"]
        
        # Execute action (returns True if valid, False if invalid)
        action_executed = self._execute_action(action, current_price)
        
        # Get portfolio value after action
        portfolio_value_after = self.portfolio["total_value"]
        
        # Move to next step
        self.current_step += 1
        self.current_date_idx += 1
        
        # Check if episode is done
        self.done = self.current_date_idx >= len(self.trading_dates)
        
        # Calculate reward
        reward_info = self.reward_calculator.calculate_total_reward(
            portfolio_value_before=portfolio_value_before,
            portfolio_value_after=portfolio_value_after,
            rl_action=action,
            llm_action=None,  # TODO: Get LLM action if needed
            prev_action=self.prev_action,
            episode_step=self.current_step,
            max_steps=len(self.trading_dates)
        )
        
        reward = reward_info["total"]
        self.prev_action = action
        
        # Get next state
        next_state = self._get_state()
        
        # Calculate episode return (return since episode start)
        episode_return_pct = ((portfolio_value_after - self.episode_start_value) / self.episode_start_value) * 100
        
        # Info dict
        action_names = ["SELL", "HOLD", "BUY"]
        info = {
            "date": current_date,
            "price": current_price,
            "portfolio_value": portfolio_value_after,
            "cash": self.portfolio["cash"],
            "holdings": self.portfolio["holdings"],
            "return_pct": self.portfolio["total_return_pct"],  # Total return from initial capital
            "episode_return_pct": episode_return_pct,  # Return for this episode only
            "reward_breakdown": reward_info,
            "action_taken": action_names[action],
            "action_valid": action_executed,
            "valid_actions": [action_names[a] for a in valid_actions]
        }
        
        return next_state, reward, self.done, info
    
    def get_state_dim(self) -> int:
        """Return state dimension."""
        return self.state_encoder.get_state_dim()
    
    def get_action_dim(self) -> int:
        """Return action dimension."""
        return 3  # SELL, HOLD, BUY
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get statistics about LLM report caching.
        
        Returns:
            Dictionary with cache statistics
        """
        total_dates = len(self.trading_dates)
        cached_dates = len(self.llm_cache)
        
        return {
            "total_trading_dates": total_dates,
            "cached_reports": cached_dates,
            "cache_coverage_pct": (cached_dates / total_dates * 100) if total_dates > 0 else 0,
            "cache_enabled": self.use_llm_features
        }
    
    def close(self):
        """
        Clean up resources and save cache.
        
        Call this when done with the environment to ensure cache is saved.
        """
        if self.use_llm_features and self.llm_cache:
            self._save_llm_cache()
            print(f"Environment closed. Cache saved with {len(self.llm_cache)} reports.")
