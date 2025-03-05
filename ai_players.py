from poke_env.player import Player


class SimpleAI(Player):
    def choose_move(self, battle):
        if battle.available_moves:
            best_move = max(battle.available_moves, key=lambda move: move.base_power)
            return self.create_order(best_move)
        else:
            return self.choose_random_move(battle)


# Smarter AI class - pick moves based on base power
class SmarterAI1(Player):
    def choose_move(self, battle):
        if battle.available_moves:
            # Simply select the move with the highest base power
            best_move = max(
                battle.available_moves,
                key=lambda move: move.base_power
            )
            return self.create_order(best_move)
        else:
            return self.choose_random_move(battle)
        

