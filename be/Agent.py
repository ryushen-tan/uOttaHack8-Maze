import torch
import torch.nn as nn
import torch.optim as optim
import random
from collections import deque
import os
import threading

class DQNAgent:
    def __init__(
        self,
        state_dim,
        action_dim,
        lr=1e-3,
        gamma=0.99,
        epsilon=1.0,
        epsilon_min=0.05,
        epsilon_decay=0.9999,
        buffer_size=100_000,
        batch_size=64,
        target_update=1000,
        device="cpu",
        model_path=None,
        save_interval=100
    ):
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.batch_size = batch_size
        self.target_update = target_update
        self.device = device
        self.save_interval = save_interval
        self.last_loss = 0.0
        self.lock = threading.Lock()

        if model_path is None:
            self.model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'model_eval.pth')
        else:
            self.model_path = model_path

        self.q_net = self._build_net().to(device)
        if os.path.exists(self.model_path):
            self.q_net.load_state_dict(torch.load(self.model_path, weights_only=True))
            print(f"Model Loaded from {self.model_path}!")
        self.target_net = self._build_net().to(device)
        self.target_net.load_state_dict(self.q_net.state_dict())
        self.target_net.eval()

        self.optimizer = optim.Adam(self.q_net.parameters(), lr=lr)
        self.replay = deque(maxlen=buffer_size)

        self.step_count = 0

    def _build_net(self):
        return nn.Sequential(
            nn.Linear(self.state_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 128),
            nn.ReLU(),
            nn.Linear(128, self.action_dim)
        )

    def act(self, state):
        with self.lock:
            if random.random() < self.epsilon:
                return random.randrange(self.action_dim)

            state_tensor = torch.tensor(state, dtype=torch.float32, device=self.device).unsqueeze(0)
            with torch.no_grad():
                return self.q_net(state_tensor).argmax(dim=1).item()

    def remember(self, state, action, reward, next_state, done):
        self.replay.append((state, action, reward, next_state, done))

    def train(self):
        with self.lock:
            if len(self.replay) < self.batch_size:
                return

            batch = random.sample(self.replay, self.batch_size)
            states, actions, rewards, next_states, dones = zip(*batch)
            states = torch.tensor(states, dtype=torch.float32, device=self.device)
            next_states = torch.tensor(next_states, dtype=torch.float32, device=self.device)
            actions = torch.tensor(actions, dtype=torch.long, device=self.device)
            rewards = torch.tensor(rewards, dtype=torch.float32, device=self.device)
            dones = torch.tensor(dones, dtype=torch.float32, device=self.device)

            q_values = self.q_net(states).gather(1, actions.unsqueeze(1)).squeeze(1)

            with torch.no_grad():
                next_q = self.target_net(next_states).max(1)[0]
                target = rewards + self.gamma * next_q * (1 - dones)

            loss = nn.functional.mse_loss(q_values, target)
            self.last_loss = loss.item()

            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()

            self.step_count += 1
            if self.step_count % self.target_update == 0:
                self.target_net.load_state_dict(self.q_net.state_dict())

            self.epsilon = max(self.epsilon * self.epsilon_decay, self.epsilon_min)

            if self.step_count % self.save_interval == 0:
                torch.save(self.q_net.state_dict(), self.model_path)

    def get_metrics(self):
        with self.lock:
            return {
                'epsilon': self.epsilon,
                'step_count': self.step_count,
                'replay_size': len(self.replay),
                'last_loss': self.last_loss
            }
    