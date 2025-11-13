# TradingAgents/test_rl_basics.py

"""
Test script for RL components.
Tests the state encoder, DQN agent, and environment integration.
"""

import os
import sys
sys.path.append(os.path.dirname(__file__))

from tradingagents.default_config import DEFAULT_CONFIG


def test_state_encoder():
    """Test the state encoder component."""
    
    print("=== Testing State Encoder ===")
    
    try:
        from tradingagents.rl.state_encoder import TradingStateEncoder
        
        config = DEFAULT_CONFIG.copy()
        config.update({
            "llm_provider": "openai",
            "backend_url": "https://api.openai.com/v1",
        })
        
        # Initialize state encoder
        print("Initializing state encoder...")
        state_encoder = TradingStateEncoder(config)
        
        # Create mock trading state
        mock_state = {
            "market_report": "Strong bullish momentum with RSI at 45 and positive sentiment.",
            "fundamentals_report": "Solid earnings growth and strong revenue trends.",
            "sentiment_report": "Positive social media sentiment and increased mentions.",
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
                "holdings": 0,
                "total_value": 10000.0,
                "unrealized_pnl_pct": 0.0,
                "total_return_pct": 0.0
            },
            "trade_date": "2024-01-15"
        }
        
        print("Testing embedding generation...")
        market_emb = state_encoder.get_embedding(mock_state["market_report"])
        fund_emb = state_encoder.get_embedding(mock_state["fundamentals_report"])
        
        print(f"Market embedding shape: {len(market_emb)}")
        print(f"Fundamentals embedding shape: {len(fund_emb)}")
        print(f"Market embedding (first 5): {market_emb[:5]}")
        
        print("\nEncoding complete trading state to RL vector...")
        rl_state = state_encoder.encode_state(mock_state)
        
        print("Encoding trading state to RL vector...")
        rl_state = state_encoder.encode_state(mock_state)
        
        print(f"RL state vector shape: {rl_state.shape}")
        print(f"RL state vector (first 10): {rl_state[:10]}")
        print(f"RL state vector dtype: {rl_state.dtype}")
        
        # Test reward calculation with RewardCalculator
        print("\nTesting reward calculation...")
        from tradingagents.rl.reward_calculator import RewardCalculator
        
        reward_calc = RewardCalculator()
        reward_info = reward_calc.calculate_total_reward(
            portfolio_value_before=10000.0,
            portfolio_value_after=10500.0,  # 5% gain
            rl_action=2,  # BUY
            llm_action=2,  # BUY (agreement)
            prev_action=1,  # HOLD
            episode_step=10,
            max_steps=100
        )
        print(f"Sample reward breakdown:")
        print(f"  Total: {reward_info['total']:.3f}")
        print(f"  Profit: {reward_info['profit']:.3f}")
        print(f"  Risk: {reward_info['risk']:.3f}")
        print(f"  Alignment: {reward_info['alignment']:.3f}")
        
        print("\n✅ State encoder working correctly!")
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
    
    # Test state encoder
    results.append(test_state_encoder())
    
    # Test RL components
    results.append(test_rl_components())
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary:")
    print("=" * 60)
    
    test_names = ["State Encoder", "RL Components"]
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