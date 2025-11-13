"""
Reward Calculator for RL Trading

Implements multi-component reward function that balances profit,
risk, and alignment with expert LLM decisions.
"""

import numpy as np
from typing import Dict, Any, Optional, List
from collections import deque


class RewardCalculator:
    """Calculates rewards for RL trading agent."""
    
    def __init__(
        self,
        profit_weight: float = 1.0,
        risk_weight: float = 0.3,
        alignment_weight: float = 0.5,
        consistency_weight: float = 0.2
    ):
        """
        Initialize reward calculator.
        
        Args:
            profit_weight: Weight for profit component
            risk_weight: Weight for risk penalty
            alignment_weight: Weight for LLM alignment bonus (decreases over time)
            consistency_weight: Weight for consistency reward
        """
        self.profit_weight = profit_weight
        self.risk_weight = risk_weight
        self.alignment_weight = alignment_weight
        self.consistency_weight = consistency_weight
        
        # Track recent returns for risk calculation
        self.recent_returns = deque(maxlen=20)
        self.recent_actions = deque(maxlen=10)
        
    def calculate_profit_reward(
        self,
        portfolio_value_before: float,
        portfolio_value_after: float
    ) -> float:
        """
        Calculate profit-based reward.
        
        Args:
            portfolio_value_before: Portfolio value before action
            portfolio_value_after: Portfolio value after action
            
        Returns:
            Profit reward (percentage return)
        """
        if portfolio_value_before <= 0:
            return 0.0
        
        return_pct = (portfolio_value_after - portfolio_value_before) / portfolio_value_before
        
        # Store for risk calculation
        self.recent_returns.append(return_pct)
        
        return return_pct * 100.0  # Scale to percentage
    
    def calculate_risk_penalty(self) -> float:
        """
        Calculate risk penalty based on return volatility.
        
        Returns:
            Risk penalty (negative for high volatility)
        """
        if len(self.recent_returns) < 2:
            return 0.0
        
        returns_array = np.array(list(self.recent_returns))
        volatility = np.std(returns_array)
        
        # Penalize high volatility
        risk_penalty = -volatility * 100.0
        
        # Additional penalty for large drawdowns
        if len(self.recent_returns) >= 5:
            cumulative_returns = np.cumprod(1 + returns_array)
            running_max = np.maximum.accumulate(cumulative_returns)
            drawdown = (cumulative_returns - running_max) / running_max
            max_drawdown = np.min(drawdown)
            
            if max_drawdown < -0.1:  # More than 10% drawdown
                risk_penalty += max_drawdown * 50.0
        
        return risk_penalty
    
    def calculate_alignment_reward(
        self,
        rl_action: int,
        llm_action: Optional[int] = None
    ) -> float:
        """
        Calculate reward for alignment with LLM expert.
        
        Args:
            rl_action: Action taken by RL agent (0=SELL, 1=HOLD, 2=BUY)
            llm_action: Action suggested by LLM (None if not available)
            
        Returns:
            Alignment bonus/penalty
        """
        if llm_action is None:
            return 0.0
        
        if rl_action == llm_action:
            return 1.0  # Bonus for agreement
        else:
            return -0.5  # Small penalty for disagreement
    
    def calculate_consistency_reward(self, action: int) -> float:
        """
        Calculate reward for consistent (not erratic) trading behavior.
        
        Args:
            action: Current action
            
        Returns:
            Consistency reward
        """
        self.recent_actions.append(action)
        
        if len(self.recent_actions) < 3:
            return 0.0
        
        # Penalize excessive switching
        action_changes = 0
        for i in range(1, len(self.recent_actions)):
            if self.recent_actions[i] != self.recent_actions[i-1]:
                action_changes += 1
        
        # Too many changes = erratic behavior
        if action_changes > len(self.recent_actions) * 0.7:
            return -0.5
        
        return 0.0
    
    def calculate_transaction_cost(self, action: int, prev_action: int) -> float:
        """
        Calculate transaction cost penalty.
        
        Args:
            action: Current action
            prev_action: Previous action
            
        Returns:
            Transaction cost (negative)
        """
        # Penalize any change in position (trading costs)
        if action != prev_action and action != 1:  # If not holding
            return -0.1  # Small transaction cost
        return 0.0
    
    def calculate_total_reward(
        self,
        portfolio_value_before: float,
        portfolio_value_after: float,
        rl_action: int,
        llm_action: Optional[int] = None,
        prev_action: int = 1,
        episode_step: int = 0,
        max_steps: int = 100
    ) -> Dict[str, float]:
        """
        Calculate total reward with all components.
        
        Args:
            portfolio_value_before: Portfolio value before action
            portfolio_value_after: Portfolio value after action
            rl_action: Action taken by RL agent
            llm_action: Action suggested by LLM (optional)
            prev_action: Previous action taken
            episode_step: Current step in episode
            max_steps: Total steps in episode
            
        Returns:
            Dictionary with reward components and total
        """
        # Calculate individual components
        profit_reward = self.calculate_profit_reward(
            portfolio_value_before,
            portfolio_value_after
        )
        
        risk_penalty = self.calculate_risk_penalty()
        
        # Decay alignment weight over time (become more independent)
        progress = episode_step / max_steps if max_steps > 0 else 0
        current_alignment_weight = self.alignment_weight * (1.0 - progress * 0.5)
        
        alignment_reward = self.calculate_alignment_reward(rl_action, llm_action)
        consistency_reward = self.calculate_consistency_reward(rl_action)
        transaction_cost = self.calculate_transaction_cost(rl_action, prev_action)
        
        # Weighted sum
        total_reward = (
            self.profit_weight * profit_reward +
            self.risk_weight * risk_penalty +
            current_alignment_weight * alignment_reward +
            self.consistency_weight * consistency_reward +
            transaction_cost
        )
        
        # Return breakdown for logging
        return {
            "total": total_reward,
            "profit": profit_reward,
            "risk": risk_penalty,
            "alignment": alignment_reward,
            "consistency": consistency_reward,
            "transaction_cost": transaction_cost,
            "alignment_weight_used": current_alignment_weight
        }
    
    def reset(self):
        """Reset internal state for new episode."""
        self.recent_returns.clear()
        self.recent_actions.clear()
