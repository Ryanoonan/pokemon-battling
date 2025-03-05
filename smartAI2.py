import json
from poke_env.player import Player


# Load type chart from the JSON file
with open('type-chart.json', 'r') as f:
    TYPE_CHART = json.load(f)

class SmarterAI2(Player):
    def choose_move(self, battle):
        if battle.available_moves:
            # Evaluate moves based on type effectiveness
            best_move = None
            best_score = -float('inf')

            for move in battle.available_moves:
                move_effectiveness = self.calculate_move_effectiveness(move, battle)
                move_score = move.base_power * move_effectiveness

                # Prioritize moves with the best score
                if move_score > best_score:
                    best_score = move_score
                    best_move = move

            return self.create_order(best_move)
        else:
            return self.choose_random_move(battle)

    def calculate_move_effectiveness(self, move, battle):
        # Check type effectiveness of the move
        attacker_type = move.type.name  # Type of the attacking move
        opponent_type = battle.opponent_active_pokemon.types[0].name  # Type of the opponent's active Pokemon

        # Get effectiveness from the loaded TYPE_CHART
        effectiveness = TYPE_CHART.get(attacker_type, {}).get(opponent_type, 1)
        
        # Factor in the possibility of a critical hit or status effects (future expansion)
        return effectiveness

    def choose_pokemon_to_switch(self, battle):
        # Switch logic based on Pokémon type matchups (simplified)
        if battle.available_pokemon:
            for pokemon in battle.available_pokemon:
                if self.is_strong_against_opponent(pokemon, battle.opponent_active_pokemon):
                    return pokemon
        return None

    def is_strong_against_opponent(self, pokemon, opponent_pokemon):
        # Check if the pokemon is strong against the opponent's type
        pokemon_types = [type.name for type in pokemon.types]
        opponent_types = [type.name for type in opponent_pokemon.types]
        
        for p_type in pokemon_types:
            for o_type in opponent_types:
                if TYPE_CHART.get(p_type, {}).get(o_type, 1) > 1:
                    return True
        return False

