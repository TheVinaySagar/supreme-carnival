"""
DQN-based RL Trading Agent

Implements Deep Q-Network for trading decisions.
"""

import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from typing import Optional, Tuple
import os


class TradingDQN(nn.Module):
    """Deep Q-Network for trading."""
    
    def __init__(self, state_dim: int, action_dim: int, hidden_dims: Tuple[int, ...] = (256, 128)):
        """
        Initialize DQN network.
        
        Args:
            state_dim: Dimension of state vector
            action_dim: Number of possible actions
            hidden_dims: Sizes of hidden layers
        """
        super(TradingDQN, self).__init__()
        
        layers = []
        prev_dim = state_dim
        
        for hidden_dim in hidden_dims:
            layers.extend([
                nn.Linear(prev_dim, hidden_dim),
                nn.ReLU(),
                nn.Dropout(0.1)
            ])
            prev_dim = hidden_dim
        
        layers.append(nn.Linear(prev_dim, action_dim))
        
        self.network = nn.Sequential(*layers)
        
    def forward(self, state: torch.Tensor) -> torch.Tensor:
        """
        Forward pass through network.
        
        Args:
            state: State tensor
            
        Returns:
            Q-values for each action
        """
        return self.network(state)


class RLTradingAgent:
    """RL agent for trading decisions using DQN."""
    
    def __init__(
        self,
        state_dim: int,
        action_dim: int = 3,  # SELL, HOLD, BUY
        config: Optional[dict] = None
    ):
        """
        Initialize RL trading agent.
        
        Args:
            state_dim: Dimension of state space
            action_dim: Number of actions (default: 3)
            config: Configuration dictionary
        """
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.config = config or {}
        
        # Hyperparameters
        self.learning_rate = self.config.get("rl_learning_rate", 1e-4)
        self.gamma = self.config.get("rl_gamma", 0.95)
        self.epsilon = self.config.get("rl_epsilon_start", 1.0)
        self.epsilon_min = self.config.get("rl_epsilon_min", 0.01)
        self.epsilon_decay = self.config.get("rl_epsilon_decay", 0.995)
        self.target_update_freq = self.config.get("rl_target_update", 100)
        
        # Device
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"RL Agent using device: {self.device}")
        
        # Networks
        self.policy_net = TradingDQN(state_dim, action_dim).to(self.device)
        self.target_net = TradingDQN(state_dim, action_dim).to(self.device)
        self.target_net.load_state_dict(self.policy_net.state_dict())
        self.target_net.eval()
        
        # Optimizer
        self.optimizer = optim.Adam(self.policy_net.parameters(), lr=self.learning_rate)
        self.loss_fn = nn.SmoothL1Loss()  # Huber loss
        
        # Training state
        self.steps = 0
        self.episode = 0
        
    def get_action(self, state: np.ndarray, training: bool = True) -> int:
        """
        Select action using epsilon-greedy policy.
        
        Args:
            state: Current state vector
            training: Whether in training mode (uses epsilon-greedy)
            
        Returns:
            Selected action (0=SELL, 1=HOLD, 2=BUY)
        """
        # Exploration: random action
        if training and np.random.random() < self.epsilon:
            return np.random.randint(0, self.action_dim)
        
        # Exploitation: best action from Q-network
        with torch.no_grad():
            state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
            q_values = self.policy_net(state_tensor)
            action = q_values.argmax(dim=1).item()
        
        return action
    
    def update(
        self,
        states: np.ndarray,
        actions: np.ndarray,
        rewards: np.ndarray,
        next_states: np.ndarray,
        dones: np.ndarray
    ) -> float:
        """
        Update network using batch of experiences.
        
        Args:
            states: Batch of states
            actions: Batch of actions
            rewards: Batch of rewards
            next_states: Batch of next states
            dones: Batch of done flags
            
        Returns:
            Training loss
        """
        # Convert to tensors
        states = torch.FloatTensor(states).to(self.device)
        actions = torch.LongTensor(actions).to(self.device)
        rewards = torch.FloatTensor(rewards).to(self.device)
        next_states = torch.FloatTensor(next_states).to(self.device)
        dones = torch.FloatTensor(dones).to(self.device)
        
        # Current Q-values
        current_q_values = self.policy_net(states).gather(1, actions.unsqueeze(1)).squeeze()
        
        # Target Q-values (using target network)
        with torch.no_grad():
            next_q_values = self.target_net(next_states).max(dim=1)[0]
            target_q_values = rewards + (1 - dones) * self.gamma * next_q_values
        
        # Compute loss
        loss = self.loss_fn(current_q_values, target_q_values)
        
        # Optimize
        self.optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(self.policy_net.parameters(), 1.0)
        self.optimizer.step()
        
        # Update target network periodically
        self.steps += 1
        if self.steps % self.target_update_freq == 0:
            self.target_net.load_state_dict(self.policy_net.state_dict())
        
        # Decay epsilon
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
        
        return loss.item()
    
    def save(self, filepath: str):
        """
        Save agent state.
        
        Args:
            filepath: Path to save checkpoint
        """
        checkpoint = {
            "policy_net": self.policy_net.state_dict(),
            "target_net": self.target_net.state_dict(),
            "optimizer": self.optimizer.state_dict(),
            "epsilon": self.epsilon,
            "steps": self.steps,
            "episode": self.episode,
            "config": self.config
        }
        torch.save(checkpoint, filepath)
        print(f"Agent saved to {filepath}")
    
    def load(self, filepath: str):
        """
        Load agent state.
        
        Args:
            filepath: Path to load checkpoint from
        """
        if not os.path.exists(filepath):
            print(f"Warning: Checkpoint {filepath} not found")
            return
        
        checkpoint = torch.load(filepath, map_location=self.device)
        self.policy_net.load_state_dict(checkpoint["policy_net"])
        self.target_net.load_state_dict(checkpoint["target_net"])
        self.optimizer.load_state_dict(checkpoint["optimizer"])
        self.epsilon = checkpoint.get("epsilon", self.epsilon_min)
        self.steps = checkpoint.get("steps", 0)
        self.episode = checkpoint.get("episode", 0)
        print(f"Agent loaded from {filepath} (episode {self.episode}, epsilon {self.epsilon:.3f})")
    
    def set_eval_mode(self):
        """Set agent to evaluation mode (no exploration)."""
        self.policy_net.eval()
        self.epsilon = 0.0
    
    def set_train_mode(self):
        """Set agent to training mode."""
        self.policy_net.train()
