"""
Quick test to demonstrate LLM caching functionality
"""

from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.rl.rl_environment import TradingEnvironment
import time

def test_llm_caching():
    """Test LLM report caching with a small date range."""
    
    print("="*60)
    print("LLM Cache Test")
    print("="*60)
    
    # Small date range for quick test
    ticker = "AAPL"
    start_date = "2024-01-02"
    end_date = "2024-01-05"
    
    config = DEFAULT_CONFIG.copy()
    config.update({
        "llm_provider": "openai",
        "backend_url": "https://api.openai.com/v1",
        "deep_think_llm": "gpt-4o-mini",
        "quick_think_llm": "gpt-4o-mini",
    })
    
    print(f"\nTesting with {ticker} from {start_date} to {end_date}")
    print(f"This will use a very short date range to demonstrate caching.")
    
    # First run - generates cache
    print("\n" + "="*60)
    print("First Episode - Cache Generation")
    print("="*60)
    
    env1 = TradingEnvironment(
        ticker=ticker,
        start_date=start_date,
        end_date=end_date,
        use_llm_features=True,
        config=config
    )
    
    cache_stats = env1.get_cache_stats()
    print(f"\nInitial cache status:")
    print(f"  Cached reports: {cache_stats['cached_reports']}/{cache_stats['total_trading_dates']}")
    print(f"  Coverage: {cache_stats['cache_coverage_pct']:.1f}%")
    
    print("\nRunning first episode (this may take 1-2 minutes)...")
    start_time = time.time()
    
    state = env1.reset()
    done = False
    steps = 0
    
    while not done:
        action = 1  # HOLD
        state, reward, done, info = env1.step(action)
        steps += 1
    
    first_episode_time = time.time() - start_time
    
    cache_stats = env1.get_cache_stats()
    print(f"\n✓ First episode completed in {first_episode_time:.2f} seconds")
    print(f"  Steps: {steps}")
    print(f"  Cache now contains: {cache_stats['cached_reports']} reports")
    print(f"  Coverage: {cache_stats['cache_coverage_pct']:.1f}%")
    
    # Save cache
    env1.close()
    
    # Second run - uses cache
    print("\n" + "="*60)
    print("Second Episode - Cache Reuse")
    print("="*60)
    
    env2 = TradingEnvironment(
        ticker=ticker,
        start_date=start_date,
        end_date=end_date,
        use_llm_features=True,
        config=config
    )
    
    cache_stats = env2.get_cache_stats()
    print(f"\nCache loaded:")
    print(f"  Cached reports: {cache_stats['cached_reports']}/{cache_stats['total_trading_dates']}")
    print(f"  Coverage: {cache_stats['cache_coverage_pct']:.1f}%")
    
    print("\nRunning second episode (should be instant)...")
    start_time = time.time()
    
    state = env2.reset()
    done = False
    steps = 0
    
    while not done:
        action = 1  # HOLD
        state, reward, done, info = env2.step(action)
        steps += 1
    
    second_episode_time = time.time() - start_time
    
    print(f"\n✓ Second episode completed in {second_episode_time:.2f} seconds")
    print(f"  Steps: {steps}")
    
    # Show speedup
    speedup = first_episode_time / second_episode_time if second_episode_time > 0 else 0
    
    print("\n" + "="*60)
    print("Results")
    print("="*60)
    print(f"First episode time:  {first_episode_time:.2f} seconds")
    print(f"Second episode time: {second_episode_time:.2f} seconds")
    print(f"Speedup factor:      {speedup:.1f}x")
    print(f"\nWith 50 episodes:")
    print(f"  Without cache: {50 * first_episode_time / 60:.1f} minutes")
    print(f"  With cache:    {(first_episode_time + 49 * second_episode_time) / 60:.1f} minutes")
    print(f"  Time saved:    {(50 * first_episode_time - (first_episode_time + 49 * second_episode_time)) / 60:.1f} minutes")
    
    env2.close()
    
    print("\n✓ Cache test completed successfully!")
    print(f"Cache file: tradingagents/dataflows/data_cache/llm_reports/{ticker}_{start_date}_{end_date}.json")

if __name__ == "__main__":
    test_llm_caching()
