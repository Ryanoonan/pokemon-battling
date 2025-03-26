import random
import numpy as np
import tensorflow as tf
from collections import deque
from poke_env.player import Player

# Hyperparameters
GAMMA = 0.99  # Discount factor
ALPHA = 0.001  # Learning rate
EPSILON = 1.0  # Exploration rate
EPSILON_DECAY = 0.995  # Decay rate for exploration
MIN_EPSILON = 0.01  # Minimum value for epsilon
BATCH_SIZE = 64  # Batch size for training
MEMORY_SIZE = 10000  # Size of experience replay buffer
TARGET_UPDATE_FREQ = 100  # Frequency to update the target network

# Experience Replay Memory
class ReplayMemory:
    def __init__(self, size):
        self.memory = deque(maxlen=size)
    
    def add(self, experience):
        self.memory.append(experience)
    
    def sample(self, batch_size):
        return random.sample(self.memory, batch_size)
    
    def size(self):
        return len(self.memory)

# DQN Class
class DQN:
    def __init__(self, state_size, action_size):
        self.state_size = state_size
        self.action_size = action_size
        
        # Create the main Q-network and target Q-network
        self.model = self.build_model()
        self.target_model = self.build_model()
        self.update_target_network()

        # Experience replay memory
        self.memory = ReplayMemory(MEMORY_SIZE)
    
    def build_model(self):
        # Build a simple neural network model using TensorFlow/Keras
        model = tf.keras.Sequential([
            tf.keras.layers.Dense(128, input_dim=self.state_size, activation='relu'),
            tf.keras.layers.Dense(128, activation='relu'),
            tf.keras.layers.Dense(self.action_size, activation='linear')
        ])
        model.compile(loss='mse', optimizer=tf.keras.optimizers.Adam(learning_rate=ALPHA))
        return model
    
    def update_target_network(self):
        # Update target network with weights of the online network
        self.target_model.set_weights(self.model.get_weights())
    
    def act(self, state):
        if np.random.rand() <= EPSILON:
            return random.randrange(self.action_size)  # Explore
        state = np.array(state).reshape(1, -1)
        q_values = self.model.predict(state)  # Predict Q-values
        return np.argmax(q_values[0])  # Exploit

    def train(self):
        if self.memory.size() < BATCH_SIZE:
            return
        
        # Sample a batch of experiences from memory
        batch = self.memory.sample(BATCH_SIZE)
        
        # Prepare the data for training
        states = np.array([experience[0] for experience in batch])
        actions = np.array([experience[1] for experience in batch])
        rewards = np.array([experience[2] for experience in batch])
        next_states = np.array([experience[3] for experience in batch])
        dones = np.array([experience[4] for experience in batch])
        
        # Predict Q-values for the next states using target network
        target_q_values = self.target_model.predict(next_states)
        
        # Update Q-values based on the Bellman equation
        targets = self.model.predict(states)
        for i in range(BATCH_SIZE):
            if dones[i]:
                targets[i][actions[i]] = rewards[i]  # Terminal state
            else:
                targets[i][actions[i]] = rewards[i] + GAMMA * np.max(target_q_values[i])  # Non-terminal state
        
        # Train the model using the updated Q-values
        self.model.fit(states, targets, epochs=1, verbose=0)

# Custom AI Player using DQN
class DQN_AI(Player):
    def __init__(self, state_size, action_size):
        super().__init__()
        self.dqn = DQN(state_size, action_size)
    
    def choose_move(self, battle):
        state = self.get_state(battle)
        action = self.dqn.act(state)
        move = self.get_move_from_action(action, battle)
        return self.create_order(move)
    
    def get_state(self, battle):
        # Extract state from the battle (e.g., HP, status, move types, etc.)
        state = []
        state.append(battle.active_pokemon.hp / battle.active_pokemon.max_hp)  # Current Pokémon's HP
        # Add more state features as needed (e.g., opponent's Pokémon, status effects, etc.)
        return np.array(state)
    
    def get_move_from_action(self, action, battle):
        # Convert action to a move based on the action index
        return battle.available_moves[action]

# Main loop (training)
def train_dqn():
    # Create environment (this can be your custom environment)
    battle_env = poke_env.PokemonBattleEnvironment()  # Assuming your environment is like this

    # Initialize the AI agent
    state_size = 10  # Example: number of features in the state
    action_size = len(battle_env.get_possible_moves())  # Number of possible moves
    ai_player = DQN_AI(state_size, action_size)
    
    for episode in range(1000):  # Example: train for 1000 episodes
        battle = battle_env.reset()  # Reset environment
        done = False
        
        while not done:
            action = ai_player.choose_move(battle)  # Choose action (move)
            next_battle, reward, done, _ = battle_env.step(action)  # Take action and get next state, reward
            state = ai_player.get_state(battle)
            next_state = ai_player.get_state(next_battle)
            
            # Store experience in replay memory
            ai_player.dqn.memory.add((state, action, reward, next_state, done))
            
            # Train the DQN model
            ai_player.dqn.train()
        
        # Update target network periodically
        if episode % TARGET_UPDATE_FREQ == 0:
            ai_player.dqn.update_target_network()

train_dqn()
