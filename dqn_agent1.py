import numpy as np
import random
import torch
import torch.nn as nn
import torch.optim as optim
from collections import deque
from poke_env.player import Player
from poke_env.environment import Battle

# Neural Network for Q-value approximation
class DQN(nn.Module):
    def __init__(self, state_size, action_size):
        super(DQN, self).__init__()
        self.fc1 = nn.Linear(state_size, 64)
        self.fc2 = nn.Linear(64, 64)
        self.fc3 = nn.Linear(64, action_size)

    def forward(self, state):
        x = torch.relu(self.fc1(state))
        x = torch.relu(self.fc2(x))
        return self.fc3(x)

# DQN Agent Class
class DQNAgent(Player):
    def __init__(self, env, epsilon=1.0, epsilon_decay=0.995, epsilon_min=0.01, gamma=0.99, lr=0.001, batch_size=32):
        super().__init__()
        self.env = env
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        self.gamma = gamma
        self.batch_size = batch_size
        self.lr = lr
        self.memory = deque(maxlen=10000)  # Experience replay buffer
        self.state_size = len(self.env.state)  # Set this to your state size
        self.action_size = len(self.env.action_space)  # Set this to your action space size
        
        # Initialize the Q-network and the target network
        self.model = DQN(self.state_size, self.action_size)
        self.target_model = DQN(self.state_size, self.action_size)
        self.target_model.load_state_dict(self.model.state_dict())  # Initialize target network
        self.optimizer = optim.Adam(self.model.parameters(), lr=self.lr)

    def act(self, state):
        if random.random() < self.epsilon:
            return random.choice(self.env.get_available_actions())  # Random action
        state_tensor = torch.tensor(state, dtype=torch.float32)
        q_values = self.model(state_tensor)
        return torch.argmax(q_values).item()

    def memorize(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def replay(self):
        if len(self.memory) < self.batch_size:
            return

        batch = random.sample(self.memory, self.batch_size)
        states, actions, rewards, next_states, dones = zip(*batch)

        states = torch.tensor(states, dtype=torch.float32)
        next_states = torch.tensor(next_states, dtype=torch.float32)
        rewards = torch.tensor(rewards, dtype=torch.float32)
        dones = torch.tensor(dones, dtype=torch.float32)

        # Get Q-values from the main model
        q_values = self.model(states)
        next_q_values = self.target_model(next_states)

        # Update Q-value for the action taken
        q_value = q_values.gather(1, torch.tensor(actions).view(-1, 1))

        # Compute target Q-values
        next_q_value = next_q_values.max(1)[0].detach()
        target = rewards + (self.gamma * next_q_value * (1 - dones))

        loss = nn.MSELoss()(q_value, target.view(-1, 1))

        # Perform gradient descent
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        # Update target model every few episodes
        self.update_target_model()

    def update_target_model(self):
        self.target_model.load_state_dict(self.model.state_dict())

    def train(self, num_episodes=1000):
        for episode in range(num_episodes):
            state = self.env.reset()
            done = False
            total_reward = 0

            while not done:
                action = self.act(state)
                next_state, reward, done, _ = self.env.step(action)
                self.memorize(state, action, reward, next_state, done)
                self.replay()

                state = next_state
                total_reward += reward

            # Reduce epsilon (exploration rate)
            if self.epsilon > self.epsilon_min:
                self.epsilon *= self.epsilon_decay

            print(f"Episode {episode}, Total Reward: {total_reward}, Epsilon: {self.epsilon}")

# Example: Initialize and train the agent
env = Battle()  # You need to provide an environment that matches your game scenario
agent = DQNAgent(env)

agent.train(num_episodes=1000)
