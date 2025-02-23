import asyncio
from poke_env import Player, RandomPlayer


# Code taken from https://github.com/hsahovic/poke-env
class YourFirstAgent(Player):
    def choose_move(self, battle):
        for move in battle.available_moves:
            if move.base_power > 90:
                # A powerful move! Let's use it
                return self.create_order(move)

        # No available move? Let's switch then!
        for switch in battle.available_switches:
            if switch.current_hp_fraction > battle.active_pokemon.current_hp_fraction:
                # This other pokemon has more HP left... Let's switch it in?
                return self.create_order(switch)

        # Not sure what to do?
        return self.choose_random_move(battle)


player1 = YourFirstAgent()
player2 = RandomPlayer()

asyncio.run(player1.battle_against(player2, n_battles=2))
