import json
import numpy as np
from gymnasium.spaces import Box
from poke_env.player import Gen8EnvSinglePlayer, RandomPlayer
from poke_env.environment.abstract_battle import AbstractBattle
from gymnasium.utils.env_checker import check_env
from stable_baselines3 import DQN
from stable_baselines3.common.vec_env import DummyVecEnv
from loguru import logger


# --- Your environment definition (as provided) ---
def to_upper(d):
    if isinstance(d, list):
        return [to_upper(v) for v in d]
    if isinstance(d, str):
        return d.upper()
    if isinstance(d, dict):
        return {k.upper(): to_upper(v) for k, v in d.items()}
    return d


with open("type-chart.json", "r") as f:
    TYPE_CHART = json.load(f)
TYPE_CHART = to_upper(TYPE_CHART)


class SimpleRLPlayer(Gen8EnvSinglePlayer):
    def calc_reward(self, last_battle, current_battle) -> float:
        return self.reward_computing_helper(
            current_battle, fainted_value=2.0, hp_value=1.0, victory_value=30.0
        )

    def embed_battle(self, battle: AbstractBattle):
        # -1 indicates that the move does not have a base power or is not available
        moves_base_power = -np.ones(4)
        moves_dmg_multiplier = np.ones(4)
        for i, move in enumerate(battle.available_moves):
            moves_base_power[i] = move.base_power / 100  # Rescale base power
            if move.type:
                try:
                    multiplier = move.type.damage_multiplier(
                        battle.opponent_active_pokemon.type_1,
                        battle.opponent_active_pokemon.type_2,
                        type_chart=TYPE_CHART,
                    )
                    if isinstance(multiplier, float):
                        moves_dmg_multiplier[i] = multiplier
                except Exception as e:
                    # logger.warning(
                    #     f"Error with this type: {battle.opponent_active_pokemon.type_1}, error: {e}"
                    # )
                    pass
        # Count how many Pokémon have fainted in each team
        fainted_mon_team = len([mon for mon in battle.team.values() if mon.fainted]) / 6
        fainted_mon_opponent = (
            len([mon for mon in battle.opponent_team.values() if mon.fainted]) / 6
        )
        # Final vector with 10 components
        final_vector = np.concatenate(
            [
                moves_base_power,
                moves_dmg_multiplier,
                [fainted_mon_team, fainted_mon_opponent],
            ]
        )
        return np.float32(final_vector)

    def describe_embedding(self) -> Box:
        low = [-1, -1, -1, -1, 0, 0, 0, 0, 0, 0]
        high = [3, 3, 3, 3, 4, 4, 4, 4, 1, 1]
        return Box(
            low=np.array(low, dtype=np.float32),
            high=np.array(high, dtype=np.float32),
            dtype=np.float32,
        )

def main():
    # Create the opponent and environment instance
    opponent = RandomPlayer(battle_format="gen8randombattle")
    env_instance = SimpleRLPlayer(
        battle_format="gen8randombattle", opponent=opponent, start_challenging=True
    )

    # Wrap your environment in a DummyVecEnv to work with Stable Baselines3
    env = DummyVecEnv([lambda: env_instance])

    # Create a DQN model with an MLP policy; verbose=1 will print training info
    model = DQN("MlpPolicy", env, verbose=1)

    # Train the model for a given number of timesteps
    model.learn(total_timesteps=100000)

    # Save the trained model
    model.save("dqn_pokemon_model")

if __name__ == "__main__":
    main()
