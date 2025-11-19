"""
Replay Buffer for Experience Storage

Stores and samples past experiences for off-policy RL training.
"""

import numpy as np
from typing import Tuple, List
import random
from collections import deque


class ReplayBuffer:
    """Experience replay buffer for DQN training."""
    
    def __init__(self, capacity: int = 10000, state_dim: int = None):
        """
        Initialize replay buffer.
        
        Args:
            capacity: Maximum number of experiences to store
            state_dim: Dimension of state vectors (for validation)
        """
        self.capacity = capacity
        self.state_dim = state_dim
        self.buffer = deque(maxlen=capacity)
        
    def add(
        self,
        state: np.ndarray,
        action: int,
        reward: float,
        next_state: np.ndarray,
        done: bool
    ):
        """
        Add an experience to the buffer.
        
        Args:
            state: Current state vector
            action: Action taken
            reward: Reward received
            next_state: Next state vector
            done: Whether episode is done
        """
        experience = (state, action, reward, next_state, done)
        self.buffer.append(experience)
    
    def sample(self, batch_size: int) -> Tuple[np.ndarray, ...]:
        """
        Sample a batch of experiences.
        
        Args:
            batch_size: Number of experiences to sample
            
        Returns:
            Tuple of (states, actions, rewards, next_states, dones)
        """
        if len(self.buffer) < batch_size:
            batch_size = len(self.buffer)
        
        experiences = random.sample(self.buffer, batch_size)
        
        states = np.array([exp[0] for exp in experiences], dtype=np.float32)
        actions = np.array([exp[1] for exp in experiences], dtype=np.int64)
        rewards = np.array([exp[2] for exp in experiences], dtype=np.float32)
        next_states = np.array([exp[3] for exp in experiences], dtype=np.float32)
        dones = np.array([exp[4] for exp in experiences], dtype=np.float32)
        
        return states, actions, rewards, next_states, dones
    
    def __len__(self) -> int:
        """Return current buffer size."""
        return len(self.buffer)
    
    def clear(self):
        """Clear the buffer."""
        self.buffer.clear()
    
    def save(self, filepath: str):
        """
        Save buffer to disk.
        
        Args:
            filepath: Path to save buffer
        """
        import pickle
        with open(filepath, 'wb') as f:
            pickle.dump(list(self.buffer), f)
        print(f"Buffer saved to {filepath}")
    
    def load(self, filepath: str):
        """
        Load buffer from disk.
        
        Args:
            filepath: Path to load buffer from
        """
        import pickle
        with open(filepath, 'rb') as f:
            experiences = pickle.load(f)
            self.buffer = deque(experiences, maxlen=self.capacity)
        print(f"Buffer loaded from {filepath} ({len(self.buffer)} experiences)")
