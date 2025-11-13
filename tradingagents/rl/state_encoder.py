"""
State Encoder for RL Trading Agent

Converts TradingAgents state (market data + LLM reports) into fixed-size
numerical vectors suitable for RL algorithms.
"""

import numpy as np
from typing import Dict, Any, List, Optional
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class TradingStateEncoder:
    """Encodes trading state into RL-compatible feature vectors."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the state encoder.
        
        Args:
            config: Configuration dictionary with LLM settings
        """
        self.config = config
        
        # Initialize OpenAI client for embeddings
        self.client = OpenAI(
            base_url=config.get("backend_url", "https://api.openai.com/v1"),
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.embedding_model = "text-embedding-3-small"
        self.embedding_dim = 1536  # OpenAI text-embedding-3-small dimension
        
        # Define state space dimensions
        self.market_features_dim = 15  # Price, volume, technical indicators
        self.portfolio_features_dim = 5  # Cash, holdings, returns, etc.
        self.temporal_features_dim = 4  # Date features
        self.text_embedding_dim = self.embedding_dim * 4  # 4 reports
        
        self.total_dim = (
            self.market_features_dim + 
            self.portfolio_features_dim + 
            self.temporal_features_dim + 
            self.text_embedding_dim
        )
        
        print(f"RL State Encoder initialized with state dimension: {self.total_dim}")
    
    def get_embedding(self, text: str) -> np.ndarray:
        """
        Get embedding vector for text using OpenAI API.
        
        Args:
            text: Input text to embed
            
        Returns:
            Numpy array of embedding vector
        """
        if not text or text.strip() == "":
            # Return zero vector for empty text
            return np.zeros(self.embedding_dim)
        
        try:
            response = self.client.embeddings.create(
                model=self.embedding_model,
                input=text[:8000]  # Truncate to avoid token limits
            )
            return np.array(response.data[0].embedding)
        except Exception as e:
            print(f"Warning: Embedding failed ({e}), returning zero vector")
            return np.zeros(self.embedding_dim)
    
    def encode_market_data(self, market_data: Dict[str, Any]) -> np.ndarray:
        """
        Encode numerical market features.
        
        Args:
            market_data: Dictionary with market indicators
            
        Returns:
            Normalized feature vector
        """
        features = []
        
        # Price features (normalized by current price)
        price = market_data.get("price", 100.0)
        features.append(price / 1000.0)  # Normalize
        features.append(market_data.get("sma_50", price) / price)
        features.append(market_data.get("sma_200", price) / price)
        features.append(market_data.get("ema_10", price) / price)
        
        # Technical indicators (already in reasonable ranges)
        features.append(market_data.get("rsi", 50.0) / 100.0)  # 0-100 → 0-1
        features.append(np.tanh(market_data.get("macd", 0.0)))  # Normalize
        features.append(np.tanh(market_data.get("macd_signal", 0.0)))
        features.append(np.tanh(market_data.get("macd_hist", 0.0)))
        
        # Bollinger bands (normalized by price)
        features.append(market_data.get("boll_upper", price) / price)
        features.append(market_data.get("boll_lower", price) / price)
        features.append(market_data.get("boll_mid", price) / price)
        
        # Volatility
        features.append(np.tanh(market_data.get("atr", 1.0) / price))
        
        # Volume (log-normalized)
        volume = market_data.get("volume", 1000000)
        features.append(np.log(volume + 1) / 20.0)  # Normalize
        features.append(market_data.get("vwma", price) / price)
        
        # Price momentum (percentage change)
        features.append(np.tanh(market_data.get("price_change_pct", 0.0)))
        
        return np.array(features, dtype=np.float32)
    
    def encode_portfolio_state(self, portfolio: Dict[str, Any]) -> np.ndarray:
        """
        Encode portfolio state features.
        
        Args:
            portfolio: Dictionary with portfolio information
            
        Returns:
            Normalized feature vector
        """
        features = []
        
        total_value = portfolio.get("total_value", 10000.0)
        cash = portfolio.get("cash", 10000.0)
        position_value = total_value - cash
        
        # Normalized portfolio metrics
        features.append(cash / total_value)  # Cash ratio
        features.append(position_value / total_value)  # Position ratio
        features.append(np.log(total_value) / 15.0)  # Log total value
        features.append(np.tanh(portfolio.get("unrealized_pnl_pct", 0.0)))
        features.append(np.tanh(portfolio.get("total_return_pct", 0.0)))
        
        return np.array(features, dtype=np.float32)
    
    def encode_temporal_features(self, trade_date: str) -> np.ndarray:
        """
        Encode temporal features from date.
        
        Args:
            trade_date: Trading date in YYYY-MM-DD format
            
        Returns:
            Feature vector with temporal information
        """
        from datetime import datetime
        
        try:
            dt = datetime.strptime(trade_date, "%Y-%m-%d")
            
            # Cyclical encoding of time features
            day_of_week = dt.weekday() / 7.0
            month = dt.month / 12.0
            quarter = ((dt.month - 1) // 3) / 4.0
            day_of_year = dt.timetuple().tm_yday / 365.0
            
            return np.array([day_of_week, month, quarter, day_of_year], dtype=np.float32)
        except:
            return np.zeros(4, dtype=np.float32)
    
    def encode_text_reports(self, state: Dict[str, Any]) -> np.ndarray:
        """
        Encode LLM text reports into embeddings.
        
        Args:
            state: AgentState dictionary with text reports
            
        Returns:
            Concatenated embedding vectors
        """
        # Get embeddings for each report
        market_emb = self.get_embedding(state.get("market_report", ""))
        social_emb = self.get_embedding(state.get("sentiment_report", ""))
        news_emb = self.get_embedding(state.get("news_report", ""))
        fundamentals_emb = self.get_embedding(state.get("fundamentals_report", ""))
        
        # Concatenate all embeddings
        text_features = np.concatenate([
            market_emb,
            social_emb,
            news_emb,
            fundamentals_emb
        ])
        
        return text_features.astype(np.float32)
    
    def encode_state(self, state: Dict[str, Any]) -> np.ndarray:
        """
        Encode complete trading state into RL feature vector.
        
        Args:
            state: Complete AgentState dictionary
            
        Returns:
            Fixed-size numpy array representing the state
        """
        # Extract components
        market_data = state.get("market_data", {})
        portfolio = state.get("portfolio_state", {})
        trade_date = state.get("trade_date", "2024-01-01")
        
        # Encode each component
        market_features = self.encode_market_data(market_data)
        portfolio_features = self.encode_portfolio_state(portfolio)
        temporal_features = self.encode_temporal_features(trade_date)
        text_features = self.encode_text_reports(state)
        
        # Concatenate all features
        full_state = np.concatenate([
            market_features,
            portfolio_features,
            temporal_features,
            text_features
        ])
        
        # Verify dimension
        assert full_state.shape[0] == self.total_dim, \
            f"State dimension mismatch: {full_state.shape[0]} vs {self.total_dim}"
        
        return full_state
    
    def get_state_dim(self) -> int:
        """Return the total state dimension."""
        return self.total_dim
