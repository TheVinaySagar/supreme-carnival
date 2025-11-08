# TradingAgents/test_rl_basics.py

"""
Simple test script for RL components without full TradingAgents dependencies.
This allows testing the embedding and RL systems independently.
"""

import os
import sys
sys.path.append(os.path.dirname(__file__))

from tradingagents.default_config import DEFAULT_CONFIG


def test_embedding_system():
    """Test the embedding system with sample trading reports."""
    
    print("=== Testing Embedding System ===")
    
    # Clean up any existing collections
    try:
        import chromadb
        from chromadb import Settings
        
        client = chromadb.Client(Settings(allow_reset=True))
        try:
            client.delete_collection("test_rl_encoder")
            print("Cleaned up existing test collection")
        except:
            pass
    except ImportError:
        print("ChromaDB not available")
        return
    
    # Test embedding functionality
    try:
        from tradingagents.agents.utils.memory import FinancialSituationMemory
        
        config = DEFAULT_CONFIG.copy()
        config.update({
            "llm_provider": "google",
            "backend_url": "https://generativelanguage.googleapis.com/v1",
        })
        
        # Initialize memory system with embeddings
        memory = FinancialSituationMemory("test_rl_encoder", config)
        
        # Test embeddings with sample reports
        bullish_report = """
        AAPL shows strong technical indicators with RSI at 45, indicating room for growth.
        The 50-day SMA is trending upward, and MACD shows bullish crossover.
        Strong earnings report and positive sentiment suggest continued momentum.
        """
        
        bearish_report = """
        AAPL exhibits weakness with RSI at 75, indicating overbought conditions.
        The 200-day SMA shows resistance, and MACD histogram is declining.
        Concerns about market saturation and increased competition create headwinds.
        """
        
        print("Getting embeddings for sample reports...")
        bullish_embedding = memory.get_embedding(bullish_report)
        bearish_embedding = memory.get_embedding(bearish_report)
        
        print(f"Bullish embedding shape: {len(bullish_embedding)}")
        print(f"Bearish embedding shape: {len(bearish_embedding)}")
        print(f"Bullish embedding (first 5): {bullish_embedding[:5]}")
        print(f"Bearish embedding (first 5): {bearish_embedding[:5]}")
        
        # Calculate similarity
        import numpy as np
        def cosine_similarity(a, b):
            return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
        
        similarity = cosine_similarity(bullish_embedding, bearish_embedding)
        print(f"Cosine similarity between reports: {similarity:.3f}")
        print(f"Distance: {1 - similarity:.3f}")
        
        print("✅ Embedding system working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing embedding system: {e}")
        return False


def test_state_encoder():
    """Test the RL state encoder component."""
    
    print("\n=== Testing RL State Encoder ===")
    
    try:
        from tradingagents.rl.state_encoder import TradingStateEncoder
        
        config = DEFAULT_CONFIG.copy()
        config.update({
            "llm_provider": "google",
            "backend_url": "https://generativelanguage.googleapis.com/v1",
        })
        
        # Initialize state encoder
        print("Initializing state encoder...")
        state_encoder = TradingStateEncoder(config)
        
        # Create mock trading state
        mock_state = {
            "market_report": "Strong bullish momentum with RSI at 45 and positive sentiment.",
            "fundamentals_report": "Solid earnings growth and strong revenue trends.",
            "social_report": "Positive social media sentiment and increased mentions.",
            "news_report": "Breaking news about product launch and partnership deals.",
            "market_data": {
                "price": 150.0,
                "volume": 1000000,
                "rsi": 45.0,
                "sma_50": 148.0,
                "sma_200": 145.0
            },
            "portfolio_state": {
                "cash": 10000.0,
                "holdings": {"AAPL": 100},
                "total_value": 25000.0
            }
        }
        
        print("Encoding trading state to RL vector...")
        rl_state = state_encoder.encode_state(mock_state)
        
        print(f"RL state vector shape: {rl_state.shape}")
        print(f"RL state vector (first 10): {rl_state[:10]}")
        print(f"RL state vector dtype: {rl_state.dtype}")
        
        # Test reward calculation
        print("Testing reward calculation...")
        reward = state_encoder.calculate_reward(
            action=1,  # BUY
            current_price=150.0,
            future_price=155.0,
            expert_decision=1,  # BUY
            portfolio_change=0.05
        )
        print(f"Sample reward: {reward:.3f}")
        
        print("✅ State encoder working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing state encoder: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_rl_components():
    """Test RL components if PyTorch is available."""
    
    print("\n=== Testing RL Components ===")
    
    try:
        import torch
        print(f"PyTorch version: {torch.__version__}")
        
        from tradingagents.rl.rl_trader import TradingDQN, RLTradingAgent
        
        # Test DQN network
        print("Testing DQN network...")
        state_dim = 775  # From state encoder
        action_dim = 3   # BUY, SELL, HOLD
        
        dqn = TradingDQN(state_dim, action_dim)
        
        # Test forward pass
        dummy_state = torch.randn(1, state_dim)
        q_values = dqn(dummy_state)
        
        print(f"DQN input shape: {dummy_state.shape}")
        print(f"DQN output shape: {q_values.shape}")
        print(f"Q-values: {q_values}")
        
        # Test RL agent
        print("Testing RL agent...")
        config = {
            "rl_learning_rate": 1e-4,
            "rl_gamma": 0.95,
            "rl_epsilon_start": 1.0,
            "rl_epsilon_min": 0.01,
            "rl_epsilon_decay": 0.995,
            "rl_batch_size": 32,
            "rl_buffer_size": 1000,
            "rl_target_update": 100,
        }
        
        rl_agent = RLTradingAgent(state_dim, action_dim, config)
        
        # Test action selection
        action = rl_agent.get_action(dummy_state.numpy().flatten())
        print(f"Selected action: {action}")
        
        print("✅ RL components working correctly!")
        return True
        
    except ImportError:
        print("❌ PyTorch not installed. Install with: pip install torch torchvision")
        return False
    except Exception as e:
        print(f"❌ Error testing RL components: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    
    print("=" * 60)
    print("Testing RL Integration Components")
    print("=" * 60)
    
    results = []
    
    # Test embedding system
    results.append(test_embedding_system())
    
    # Test state encoder
    results.append(test_state_encoder())
    
    # Test RL components
    results.append(test_rl_components())
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary:")
    print("=" * 60)
    
    test_names = ["Embedding System", "State Encoder", "RL Components"]
    for i, (name, result) in enumerate(zip(test_names, results)):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{name}: {status}")
    
    if all(results):
        print("\n🎉 All tests passed! RL system is ready for training.")
    else:
        print("\n⚠️  Some tests failed. Please check the error messages above.")
    
    print("\nNext steps:")
    print("1. If tests passed, try: python -m tradingagents.rl.train_rl_agent --num_episodes 10 --tickers AAPL")
    print("2. If PyTorch test failed, install: pip install torch torchvision")
    print("3. Check your Google API key is set in environment variables")


if __name__ == "__main__":
    main()