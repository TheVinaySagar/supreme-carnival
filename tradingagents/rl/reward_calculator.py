"""
Reward Calculator for RL Trading

Simplified profit-focused reward function with loss aversion and transaction costs.
"""

import numpy as np
from typing import Dict, Any, Optional


class RewardCalculator:
    """
    Calculates rewards for RL trading agent.
    
    Focuses on profit maximization with loss aversion and realistic transaction costs.
    """
    
    def __init__(
        self,
        profit_weight: float = 10.0,
        loss_multiplier: float = 2.0,
        transaction_cost: float = 0.02,
        max_return_clip: float = 0.50
    ):
        """
        Initialize reward calculator.
        
        Args:
            profit_weight: Weight for profit (default: 10.0 for strong profit signal)
            loss_multiplier: Multiplier for losses (default: 2.0, losses hurt 2× more)
            transaction_cost: Cost per transaction in reward units (default: 0.02 = ~0.2% effective)
            max_return_clip: Maximum return to clip at for stability (default: 0.50 = 50%)
        """
        self.profit_weight = profit_weight
        self.loss_multiplier = loss_multiplier
        self.transaction_cost = transaction_cost
        self.max_return_clip = max_return_clip
        

    
    def calculate_total_reward(
        self,
        portfolio_value_before: float,
        portfolio_value_after: float,
        rl_action: int,
        prev_action: int = 1,
        initial_capital: float = 10000.0,
        **kwargs  # Ignore other legacy parameters
    ) -> Dict[str, float]:
        """
        Calculate total reward: Profit (with loss aversion) - Transaction cost
        
        Formula:
            If profit: reward = return% × 100 × profit_weight
            If loss:   reward = return% × 100 × profit_weight × loss_multiplier
            Plus transaction cost if trading
        
        Args:
            portfolio_value_before: Portfolio value before action
            portfolio_value_after: Portfolio value after action
            rl_action: Action taken by RL agent (0=SELL, 1=HOLD, 2=BUY)
            prev_action: Previous action taken (default: 1=HOLD)
            initial_capital: Starting capital for scaling (default: 10000.0)
            **kwargs: Ignored legacy parameters for backwards compatibility
            
        Returns:
            Dictionary with reward components and total
            
        Exception Handling:
            - Returns zero reward if portfolio_value_before <= 0
            - Returns zero reward if values are NaN or Inf
            - Clips extreme returns to prevent instability
            - Scales down rewards if portfolio too small
            - Validates action values
        """
        # DEBUG: Print first 5 reward calculations
        if not hasattr(self, '_debug_count'):
            self._debug_count = 0
        if self._debug_count < 5:
            print(f"\n🔍 REWARD CALC #{self._debug_count + 1}:")
            print(f"  before=${portfolio_value_before:.2f}, after=${portfolio_value_after:.2f}")
            print(f"  return={(portfolio_value_after - portfolio_value_before) / portfolio_value_before * 100:.4f}%")
            self._debug_count += 1
        
        # EXCEPTION 1: Invalid portfolio values (zero, negative, NaN, Inf)
        if (not np.isfinite(portfolio_value_before) or 
            not np.isfinite(portfolio_value_after) or
            portfolio_value_before <= 0):
            return {
                "total": 0.0,
                "profit": 0.0,
                "transaction_cost": 0.0,
                "return_pct": 0.0,
                "clipped": False,
                "scaled": False
            }
        
        # EXCEPTION 2: Invalid action values
        if rl_action not in [0, 1, 2]:
            print(f"Warning: Invalid RL action {rl_action}, defaulting to HOLD (1)")
            rl_action = 1
        
        if prev_action not in [0, 1, 2]:
            print(f"Warning: Invalid prev_action {prev_action}, defaulting to HOLD (1)")
            prev_action = 1
        
        # Calculate return percentage
        return_pct = (portfolio_value_after - portfolio_value_before) / portfolio_value_before
        
        # EXCEPTION 3: Clip extreme returns to prevent gradient explosion
        original_return = return_pct
        return_pct = np.clip(return_pct, -self.max_return_clip, self.max_return_clip)
        clipped = (abs(original_return) > self.max_return_clip)
        
        if clipped:
            print(f"Warning: Return clipped from {original_return*100:.2f}% to {return_pct*100:.2f}%")
        
        # EXCEPTION 4: Scale down rewards if portfolio is very small (<10% of initial)
        portfolio_scale = 1.0
        scaled = False
        min_portfolio = initial_capital * 0.1
        
        if portfolio_value_before < min_portfolio:
            portfolio_scale = portfolio_value_before / min_portfolio
            scaled = True
            print(f"Warning: Portfolio ${portfolio_value_before:.2f} below ${min_portfolio:.2f}, scaling rewards by {portfolio_scale:.2f}")
        
        # Calculate profit reward with loss aversion
        if return_pct >= 0:
            # Profit: standard weight
            profit_reward = return_pct * 100.0 * self.profit_weight * portfolio_scale
        else:
            # Loss: extra penalty (losses hurt more than gains help)
            profit_reward = return_pct * 100.0 * self.profit_weight * self.loss_multiplier * portfolio_scale
        
        # Calculate transaction cost penalty
        transaction_penalty = 0.0
        if rl_action != 1 and rl_action != prev_action:  # Trading (not HOLD) and changed position
            transaction_penalty = -self.transaction_cost
        
        # Total reward
        total_reward = profit_reward + transaction_penalty
        
        # DEBUG: Print reward calculation for first few steps
        import os
        if os.getenv("DEBUG_REWARDS", "0") == "1":
            print(f"\n🔍 REWARD DEBUG:")
            print(f"  Portfolio: ${portfolio_value_before:.2f} → ${portfolio_value_after:.2f}")
            print(f"  Return: {return_pct*100:.4f}%")
            print(f"  Profit Reward: {profit_reward:.4f}")
            print(f"  Transaction Penalty: {transaction_penalty:.4f}")
            print(f"  Total Reward: {total_reward:.4f}")
            print(f"  Config: profit_weight={self.profit_weight}, loss_mult={self.loss_multiplier}")
        
        # Return breakdown for logging
        return {
            "total": total_reward,
            "profit": profit_reward,
            "transaction_cost": transaction_penalty,
            "return_pct": return_pct * 100.0,  # For logging (in %)
            "clipped": clipped,
            "scaled": scaled
        }
    
    def reset(self):
        """Reset internal state for new episode (no state to reset in simple version)."""
        pass
