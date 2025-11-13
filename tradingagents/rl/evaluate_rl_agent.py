"""
Evaluation Script for RL Trading Agent

Evaluate trained RL agent and compare with baselines.
"""

import argparse
import os
import json
import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, Any, List

from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.rl.rl_environment import TradingEnvironment
from tradingagents.rl.rl_trader import RLTradingAgent


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Evaluate RL trading agent")
    
    parser.add_argument(
        "--model-path",
        type=str,
        required=True,
        help="Path to trained model checkpoint"
    )
    parser.add_argument(
        "--tickers",
        type=str,
        nargs="+",
        default=["AAPL"],
        help="Stock tickers to evaluate on"
    )
    parser.add_argument(
        "--start-date",
        type=str,
        default="2024-01-01",
        help="Evaluation start date (YYYY-MM-DD)"
    )
    parser.add_argument(
        "--end-date",
        type=str,
        default="2024-12-31",
        help="Evaluation end date (YYYY-MM-DD)"
    )
    parser.add_argument(
        "--initial-capital",
        type=float,
        default=10000.0,
        help="Initial capital"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="./eval_results",
        help="Directory to save evaluation results"
    )
    
    return parser.parse_args()


class BaselineStrategy:
    """Baseline trading strategies for comparison."""
    
    @staticmethod
    def buy_and_hold(prices: List[float]) -> Dict[str, Any]:
        """
        Buy and hold strategy.
        
        Args:
            prices: List of prices over time
            
        Returns:
            Strategy results
        """
        if len(prices) < 2:
            return {"return_pct": 0.0, "actions": []}
        
        return_pct = (prices[-1] - prices[0]) / prices[0] * 100
        actions = [2] + [1] * (len(prices) - 1)  # BUY first, HOLD rest
        
        return {
            "return_pct": return_pct,
            "actions": actions,
            "name": "Buy and Hold"
        }
    
    @staticmethod
    def random_strategy(prices: List[float], seed: int = 42) -> Dict[str, Any]:
        """
        Random trading strategy.
        
        Args:
            prices: List of prices over time
            seed: Random seed
            
        Returns:
            Strategy results
        """
        np.random.seed(seed)
        actions = np.random.randint(0, 3, size=len(prices))
        
        # Simulate trading
        cash = 10000.0
        holdings = 0
        
        for i, (price, action) in enumerate(zip(prices, actions)):
            if action == 0 and holdings > 0:  # SELL
                cash += holdings * price
                holdings = 0
            elif action == 2 and cash > price:  # BUY
                shares = int((cash * 0.9) / price)
                cash -= shares * price
                holdings += shares
        
        final_value = cash + holdings * prices[-1]
        return_pct = (final_value - 10000.0) / 10000.0 * 100
        
        return {
            "return_pct": return_pct,
            "actions": actions.tolist(),
            "name": "Random"
        }


def evaluate_agent(
    env: TradingEnvironment,
    agent: RLTradingAgent,
    ticker: str
) -> Dict[str, Any]:
    """
    Evaluate RL agent on environment.
    
    Args:
        env: Trading environment
        agent: RL agent
        ticker: Stock ticker
        
    Returns:
        Evaluation results
    """
    agent.set_eval_mode()
    
    state = env.reset()
    done = False
    
    actions = []
    rewards = []
    portfolio_values = []
    dates = []
    prices = []
    
    while not done:
        action = agent.get_action(state, training=False)
        next_state, reward, done, info = env.step(action)
        
        actions.append(action)
        rewards.append(reward)
        portfolio_values.append(info["portfolio_value"])
        dates.append(info["date"])
        prices.append(info["price"])
        
        state = next_state
    
    # Calculate metrics
    action_names = ["SELL", "HOLD", "BUY"]
    action_counts = {name: actions.count(i) for i, name in enumerate(action_names)}
    
    returns = np.array(portfolio_values)
    returns_pct = (returns[1:] - returns[:-1]) / returns[:-1] * 100
    
    results = {
        "ticker": ticker,
        "final_portfolio_value": portfolio_values[-1],
        "total_return_pct": (portfolio_values[-1] - env.initial_capital) / env.initial_capital * 100,
        "total_reward": sum(rewards),
        "avg_reward": np.mean(rewards),
        "actions": action_counts,
        "num_trades": action_counts["SELL"] + action_counts["BUY"],
        "sharpe_ratio": np.mean(returns_pct) / np.std(returns_pct) if len(returns_pct) > 0 and np.std(returns_pct) > 0 else 0.0,
        "max_drawdown": calculate_max_drawdown(portfolio_values),
        "win_rate": calculate_win_rate(actions, prices),
        "volatility": np.std(returns_pct) if len(returns_pct) > 0 else 0.0,
        "dates": dates,
        "portfolio_values": portfolio_values,
        "actions_taken": actions,
        "prices": prices
    }
    
    return results


def calculate_max_drawdown(portfolio_values: List[float]) -> float:
    """Calculate maximum drawdown."""
    values = np.array(portfolio_values)
    running_max = np.maximum.accumulate(values)
    drawdown = (values - running_max) / running_max
    return float(np.min(drawdown) * 100)


def calculate_win_rate(actions: List[int], prices: List[float]) -> float:
    """Calculate win rate (profitable trades / total trades)."""
    if len(actions) < 2 or len(prices) < 2:
        return 0.0
    
    trades = []
    position = None
    entry_price = None
    
    for i, action in enumerate(actions):
        if action == 2 and position is None:  # BUY
            position = "long"
            entry_price = prices[i]
        elif action == 0 and position == "long":  # SELL
            exit_price = prices[i]
            profit = (exit_price - entry_price) / entry_price
            trades.append(profit > 0)
            position = None
            entry_price = None
    
    if len(trades) == 0:
        return 0.0
    
    return sum(trades) / len(trades) * 100


def generate_report(
    rl_results: Dict[str, Any],
    baselines: Dict[str, Dict[str, Any]],
    output_dir: str
):
    """
    Generate evaluation report.
    
    Args:
        rl_results: RL agent results
        baselines: Baseline strategy results
        output_dir: Output directory
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Create summary table
    summary = {
        "RL Agent": {
            "Return (%)": rl_results["total_return_pct"],
            "Sharpe Ratio": rl_results["sharpe_ratio"],
            "Max Drawdown (%)": rl_results["max_drawdown"],
            "Win Rate (%)": rl_results["win_rate"],
            "Volatility (%)": rl_results["volatility"],
            "Number of Trades": rl_results["num_trades"]
        }
    }
    
    for name, baseline in baselines.items():
        summary[name] = {
            "Return (%)": baseline["return_pct"],
            "Sharpe Ratio": baseline.get("sharpe_ratio", 0.0),
            "Max Drawdown (%)": baseline.get("max_drawdown", 0.0),
            "Win Rate (%)": baseline.get("win_rate", 0.0),
            "Volatility (%)": baseline.get("volatility", 0.0),
            "Number of Trades": baseline.get("num_trades", 0)
        }
    
    # Print summary
    print("\n" + "="*80)
    print(f"EVALUATION RESULTS: {rl_results['ticker']}")
    print("="*80)
    
    df = pd.DataFrame(summary).T
    print(df.to_string())
    
    print("\n" + "="*80)
    
    # Save to file
    report_path = os.path.join(output_dir, f"{rl_results['ticker']}_evaluation_report.txt")
    with open(report_path, 'w') as f:
        f.write("="*80 + "\n")
        f.write(f"EVALUATION RESULTS: {rl_results['ticker']}\n")
        f.write("="*80 + "\n\n")
        f.write(df.to_string())
        f.write("\n\n" + "="*80 + "\n")
    
    print(f"Report saved to {report_path}")
    
    # Save detailed results as JSON
    detailed_path = os.path.join(output_dir, f"{rl_results['ticker']}_detailed_results.json")
    detailed_results = {
        "rl_agent": rl_results,
        "baselines": baselines,
        "summary": summary
    }
    
    # Convert numpy types to native Python types for JSON serialization
    def convert_to_native(obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, dict):
            return {k: convert_to_native(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_to_native(item) for item in obj]
        return obj
    
    detailed_results = convert_to_native(detailed_results)
    
    with open(detailed_path, 'w') as f:
        json.dump(detailed_results, f, indent=2)
    
    print(f"Detailed results saved to {detailed_path}")


def main():
    """Main evaluation function."""
    args = parse_args()
    
    print("="*60)
    print("RL Trading Agent Evaluation")
    print("="*60)
    print(f"Model: {args.model_path}")
    print(f"Tickers: {args.tickers}")
    print(f"Evaluation Period: {args.start_date} to {args.end_date}")
    print("="*60)
    
    # Setup configuration
    config = DEFAULT_CONFIG.copy()
    config.update({
        "llm_provider": "openai",
        "backend_url": "https://api.openai.com/v1",
        "online_tools": False,
    })
    
    # Evaluate each ticker
    for ticker in args.tickers:
        print(f"\nEvaluating {ticker}...")
        
        # Create environment
        env = TradingEnvironment(
            ticker=ticker,
            start_date=args.start_date,
            end_date=args.end_date,
            initial_capital=args.initial_capital,
            config=config,
            use_llm_features=False  # Faster evaluation
        )
        
        # Load agent
        state_dim = env.get_state_dim()
        action_dim = env.get_action_dim()
        agent = RLTradingAgent(state_dim, action_dim, config)
        agent.load(args.model_path)
        
        # Evaluate RL agent
        rl_results = evaluate_agent(env, agent, ticker)
        
        # Evaluate baselines
        prices = rl_results["prices"]
        
        buy_hold = BaselineStrategy.buy_and_hold(prices)
        random_strat = BaselineStrategy.random_strategy(prices)
        
        baselines = {
            "Buy and Hold": buy_hold,
            "Random": random_strat
        }
        
        # Generate report
        output_dir = os.path.join(args.output_dir, ticker)
        generate_report(rl_results, baselines, output_dir)
    
    print("\n" + "="*60)
    print("Evaluation complete!")
    print(f"Results saved to {args.output_dir}")
    print("="*60)


if __name__ == "__main__":
    main()
