import asyncio
from poke_env.player import RandomPlayer
from ai_players import SimpleAI, SmarterAI1
from smartAI2 import SmarterAI2
from smartAI3 import SmarterAI3
from smartAI4 import SmarterAI4
from rl_agents import basic_RLAgent, RLAgent1
from simple_rl import DQNPlayer, train_dqn
import asyncio
import tensorflow as tf
from poke_env.player import RandomPlayer
from dqn_agent import DQNPlayer, train_dqn  # Import your RL agent and training function

MODEL_PATH = "dqn_model.h5"

async def main():
    # Train the model if not already trained
    try:
        model = tf.keras.models.load_model(MODEL_PATH)
        print("Loaded trained model.")
    except:
        print("No trained model found. Training now...")
        train_dqn()  # Train and save the model
    
    # Initialize the trained AI
    trained_ai = DQNPlayer(state_size=1, action_size=4)  
    random_opponent = RandomPlayer(battle_format="gen8randombattle")

    # Battle using trained AI
    await trained_ai.battle_against(random_opponent, n_battles=10)
    print(f"RL agent won {trained_ai.n_won_battles} / 10 battles.")

if __name__ == "__main__":
    asyncio.run(main())


# async def main():
#     #ai4 = SmarterAI4(battle_format="gen8randombattle")
#     #ai4 = SimpleAI(battle_format="gen8randombattle")
#     ai3 = SmarterAI4(battle_format="gen8randombattle")
#     ai4 = DQN_AI(battle_format="gen8randombattle")
#     #ai6 = DQNAgent(battle_format="gen8randombattle")
#     random_opponent = RandomPlayer(battle_format="gen8randombattle")

#     await ai3.battle_against(ai4, n_battles=10)
#     print(f"RL agent won {ai3.n_won_battles} / 10 battles.")

if __name__ == "__main__":
    asyncio.run(main())
