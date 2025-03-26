import asyncio
from poke_env.player import RandomPlayer

from rule_based_agents import SimpleAI1, SimpleAI2, SimpleAI3

async def main():
    ai1 = SimpleAI1(battle_format="gen8randombattle")
    ai2 = SimpleAI2(battle_format="gen8randombattle")
    ai3 = SimpleAI3(battle_format="gen8randombattle")
    random_opponent = RandomPlayer(battle_format="gen8randombattle")

    await ai3.battle_against(random_opponent, n_battles=10)
    print(f"AI3 won {ai3.n_won_battles} / 10 battles.")


if __name__ == "__main__":
    asyncio.run(main())
