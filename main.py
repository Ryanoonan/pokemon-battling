import asyncio
from poke_env.player import RandomPlayer
from ai_players import SimpleAI, SmarterAI1
from smartAI2 import SmarterAI2
from smartAI3 import SmarterAI3
from smartAI4 import SmarterAI4
from rl_agents import basic_RLAgent, RLAgent1
# from dqn_agent import DQN_AI
# from dqn_agent1 import DQNAgent

async def main():
    ai4 = SmarterAI4(battle_format="gen8randombattle")
    ai3 = basic_RLAgent(battle_format="gen8randombattle")
    #ai = DQN_AI(battle_format="gen8randombattle")
    #ai6 = DQNAgent(battle_format="gen8randombattle")
    random_opponent = RandomPlayer(battle_format="gen8randombattle")

    await ai3.battle_against(ai4, n_battles=10)
    print(f"RL agent won {ai3.n_won_battles} / 10 battles.")

if __name__ == "__main__":
    asyncio.run(main())
