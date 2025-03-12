from stable_baseline_poke_env_env import SimpleRLPlayer
from stable_baselines3.common.vec_env import DummyVecEnv
from poke_env.player import RandomPlayer
from stable_baselines3 import DQN
from numpy import ndarray
import asyncio


async def main():
    # Create a random opponent
    opponent = RandomPlayer(battle_format="gen8randombattle")

    # Instantiate your environment
    env_instance = SimpleRLPlayer(
        battle_format="gen8randombattle", opponent=opponent, start_challenging=True
    )

    # Wrap the environment in a DummyVecEnv for compatibility with Stable Baselines3
    env = DummyVecEnv([lambda: env_instance])

    # Load the saved DQN model (ensure "dqn_pokemon_model.zip" exists in your working directory)
    model = DQN.load("dqn_pokemon_model", env=env)

    # Reset the environment and run an episode
    obs = env.reset()
    terminated = False

    rl_wins = 0
    random_wins = 0

    print("Starting evaluation...")
    nb_games = 20
    for i in range(nb_games):
        while not terminated:
            # Predict the action using the trained model
            action, _states = model.predict(obs)
            obs, reward, terminated, truncated = env.step(action)
        #determine who one the game
        if reward > 30:
            rl_wins += 1
        else:
            random_wins += 1

        obs = env.reset()
        terminated = False
            

    print("Evaluation episode complete, results:")
    print(f"RL wins: {rl_wins}")
    print(f"Random wins: {random_wins}")


asyncio.run(main())