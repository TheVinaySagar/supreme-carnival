"""
Training Script for RL Trading Agent

Train a DQN agent on historical trading data.
"""

import argparse
import os
import json
from datetime import datetime, timedelta
import numpy as np
from typing import List, Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.rl.rl_environment import TradingEnvironment
from tradingagents.rl.rl_trader import RLTradingAgent
from tradingagents.rl.replay_buffer import ReplayBuffer


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Train RL trading agent")
    
    parser.add_argument(
        "--tickers",
        type=str,
        nargs="+",
        default=["AAPL"],
        help="Stock tickers to train on (space-separated)"
    )
    parser.add_argument(
        "--start-date",
        type=str,
        default="2020-01-01",
        help="Training start date (YYYY-MM-DD)"
    )
    parser.add_argument(
        "--end-date",
        type=str,
        default="2024-12-31",
        help="Training end date (YYYY-MM-DD)"
    )
    parser.add_argument(
        "--num-episodes",
        type=int,
        default=50,
        help="Number of training episodes"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=32,
        help="Batch size for training"
    )
    parser.add_argument(
        "--buffer-size",
        type=int,
        default=10000,
        help="Replay buffer size"
    )
    parser.add_argument(
        "--initial-capital",
        type=float,
        default=10000.0,
        help="Initial capital for trading"
    )
    parser.add_argument(
        "--use-llm-features",
        action="store_true",
        help="Use LLM-generated features (slower but richer)"
    )
    parser.add_argument(
        "--checkpoint-freq",
        type=int,
        default=10,
        help="Save checkpoint every N episodes"
    )
    parser.add_argument(
        "--model-name",
        type=str,
        default="rl_trader",
        help="Name for saved model"
    )
    
    return parser.parse_args()


class TrainingLogger:
    """Logger for training metrics."""
    
    def __init__(self, log_dir: str):
        """Initialize logger."""
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        
        self.episode_logs = []
        self.log_file = os.path.join(log_dir, "training_log.json")
    
    def log_episode(self, episode: int, metrics: Dict[str, Any]):
        """Log episode metrics."""
        log_entry = {
            "episode": episode,
            "timestamp": datetime.now().isoformat(),
            **metrics
        }
        self.episode_logs.append(log_entry)
        
        # Save incrementally
        with open(self.log_file, 'w') as f:
            json.dump(self.episode_logs, f, indent=2)
    
    def print_episode_summary(self, episode: int, metrics: Dict[str, Any]):
        """Print episode summary."""
        print(f"\n{'='*60}")
        print(f"Episode {episode} Summary:")
        print(f"{'='*60}")
        print(f"Total Return: {metrics['total_return_pct']:.2f}%")
        print(f"Final Portfolio Value: ${metrics['final_portfolio_value']:.2f}")
        print(f"Total Reward: {metrics['total_reward']:.2f}")
        print(f"Average Reward: {metrics['avg_reward']:.4f}")
        print(f"Actions - SELL: {metrics['actions']['SELL']}, "
              f"HOLD: {metrics['actions']['HOLD']}, "
              f"BUY: {metrics['actions']['BUY']}")
        print(f"Epsilon: {metrics['epsilon']:.4f}")
        print(f"Avg Loss: {metrics['avg_loss']:.4f}")
        print(f"{'='*60}\n")


def train_episode(
    env: TradingEnvironment,
    agent: RLTradingAgent,
    replay_buffer: ReplayBuffer,
    batch_size: int
) -> Dict[str, Any]:
    """
    Train agent for one episode.
    
    Args:
        env: Trading environment
        agent: RL agent
        replay_buffer: Experience replay buffer
        batch_size: Batch size for training
        
    Returns:
        Dictionary with episode metrics
    """
    state = env.reset()
    done = False
    
    total_reward = 0.0
    episode_losses = []
    action_counts = {"SELL": 0, "HOLD": 0, "BUY": 0}
    action_names = ["SELL", "HOLD", "BUY"]
    
    step = 0
    while not done:
        # Select action
        action = agent.get_action(state, training=True)
        action_counts[action_names[action]] += 1
        
        # Take step
        next_state, reward, done, info = env.step(action)
        
        # Store experience
        replay_buffer.add(state, action, reward, next_state, done)
        
        # Train if enough experiences
        if len(replay_buffer) >= batch_size:
            states, actions, rewards, next_states, dones = replay_buffer.sample(batch_size)
            loss = agent.update(states, actions, rewards, next_states, dones)
            episode_losses.append(loss)
        
        total_reward += reward
        state = next_state
        step += 1
    
    # Compute metrics
    metrics = {
        "total_reward": total_reward,
        "avg_reward": total_reward / step if step > 0 else 0,
        "steps": step,
        "final_portfolio_value": info["portfolio_value"],
        "total_return_pct": info["return_pct"],
        "actions": action_counts,
        "epsilon": agent.epsilon,
        "avg_loss": np.mean(episode_losses) if episode_losses else 0.0,
        "buffer_size": len(replay_buffer)
    }
    
    return metrics


def main():
    """Main training function."""
    args = parse_args()
    
    print("="*60)
    print("RL Trading Agent Training")
    print("="*60)
    print(f"Tickers: {args.tickers}")
    print(f"Training Period: {args.start_date} to {args.end_date}")
    print(f"Episodes: {args.num_episodes}")
    print(f"Use LLM Features: {args.use_llm_features}")
    print(f"Initial Capital: ${args.initial_capital}")
    print("="*60)
    
    # Setup configuration
    config = DEFAULT_CONFIG.copy()
    config.update({
        "llm_provider": "openai",
        "backend_url": "https://api.openai.com/v1",
        "deep_think_llm": "gpt-4o-mini",
        "quick_think_llm": "gpt-4o-mini",
        "max_debate_rounds": 1,
        "online_tools": False,  # Use cached data for speed
        "rl_learning_rate": 1e-4,
        "rl_gamma": 0.95,
        "rl_epsilon_start": 1.0,
        "rl_epsilon_min": 0.01,
        "rl_epsilon_decay": 0.995,
        "rl_batch_size": args.batch_size,
        "rl_buffer_size": args.buffer_size,
        "rl_target_update": 100,
    })
    
    # Initialize components
    print("\nInitializing environment and agent...")
    
    # Use first ticker for initialization
    ticker = args.tickers[0]
    env = TradingEnvironment(
        ticker=ticker,
        start_date=args.start_date,
        end_date=args.end_date,
        initial_capital=args.initial_capital,
        config=config,
        use_llm_features=args.use_llm_features
    )
    
    state_dim = env.get_state_dim()
    action_dim = env.get_action_dim()
    
    agent = RLTradingAgent(state_dim, action_dim, config)
    replay_buffer = ReplayBuffer(capacity=args.buffer_size, state_dim=state_dim)
    
    # Setup logging
    log_dir = os.path.join(config["project_dir"], "tradingagents/rl/logs")
    logger = TrainingLogger(log_dir)
    
    # Setup model saving
    model_dir = os.path.join(config["project_dir"], "tradingagents/rl/models/checkpoints")
    os.makedirs(model_dir, exist_ok=True)
    
    print("\nStarting training...")
    print("="*60)
    
    # Show initial cache statistics
    if args.use_llm_features:
        cache_stats = env.get_cache_stats()
        print(f"\nLLM Cache Status:")
        print(f"  - Cached Reports: {cache_stats['cached_reports']}/{cache_stats['total_trading_dates']}")
        print(f"  - Coverage: {cache_stats['cache_coverage_pct']:.1f}%")
        if cache_stats['cached_reports'] > 0:
            print(f"  ✓ Using cached reports - subsequent episodes will be 100x faster!")
        else:
            print(f"  ⚠ No cache - first episode will generate reports (slower)")
    
    # Training loop
    try:
        for episode in range(1, args.num_episodes + 1):
            print(f"\nEpisode {episode}/{args.num_episodes}")
            
            # Train on each ticker
            all_metrics = []
            for ticker in args.tickers:
                print(f"  Training on {ticker}...")
                
                # Create environment for this ticker
                if ticker != env.ticker:
                    old_env = env
                    env = TradingEnvironment(
                        ticker=ticker,
                        start_date=args.start_date,
                        end_date=args.end_date,
                        initial_capital=args.initial_capital,
                        config=config,
                        use_llm_features=args.use_llm_features
                    )
                    old_env.close()
                
                # Train episode
                metrics = train_episode(env, agent, replay_buffer, args.batch_size)
                metrics["ticker"] = ticker
                all_metrics.append(metrics)
                
                print(f"    Return: {metrics['total_return_pct']:.2f}%, "
                      f"Reward: {metrics['total_reward']:.2f}, "
                      f"Epsilon: {metrics['epsilon']:.4f}")
                
                # Show cache stats after first episode
                if episode == 1 and args.use_llm_features:
                    cache_stats = env.get_cache_stats()
                    print(f"    Cache: {cache_stats['cached_reports']} reports cached "
                          f"({cache_stats['cache_coverage_pct']:.1f}% coverage)")
            
            # Aggregate metrics
            avg_metrics = {
                "total_return_pct": np.mean([m["total_return_pct"] for m in all_metrics]),
                "final_portfolio_value": np.mean([m["final_portfolio_value"] for m in all_metrics]),
                "total_reward": np.mean([m["total_reward"] for m in all_metrics]),
                "avg_reward": np.mean([m["avg_reward"] for m in all_metrics]),
                "actions": {
                    "SELL": sum(m["actions"]["SELL"] for m in all_metrics),
                    "HOLD": sum(m["actions"]["HOLD"] for m in all_metrics),
                    "BUY": sum(m["actions"]["BUY"] for m in all_metrics),
                },
                "epsilon": agent.epsilon,
                "avg_loss": np.mean([m["avg_loss"] for m in all_metrics]),
                "tickers": args.tickers
            }
            
            # Log and print
            logger.log_episode(episode, avg_metrics)
            logger.print_episode_summary(episode, avg_metrics)
            
            # Save checkpoint
            if episode % args.checkpoint_freq == 0:
                checkpoint_path = os.path.join(
                    model_dir,
                    f"{args.model_name}_episode_{episode}.pt"
                )
                agent.save(checkpoint_path)
                print(f"Checkpoint saved to {checkpoint_path}")
        
        # Save final model (after all episodes complete)
        final_model_path = os.path.join(
            config["project_dir"],
            "tradingagents/rl/models",
            f"{args.model_name}_final.pt"
        )
        agent.save(final_model_path)
        print(f"\n{'='*60}")
        print(f"Training complete! Final model saved to {final_model_path}")
        print(f"Training logs saved to {logger.log_file}")
        print(f"{'='*60}")
        
    finally:
        # Always close environment to save cache
        print("\nClosing environment and saving cache...")
        env.close()
        if args.use_llm_features:
            cache_stats = env.get_cache_stats()
            print(f"Final cache: {cache_stats['cached_reports']} reports saved")


if __name__ == "__main__":
    main()
