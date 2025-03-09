import json
from poke_env.player import Player
from poke_env.environment.abstract_battle import AbstractBattle
from poke_env.environment.move import Move
from poke_env.environment.pokemon import Pokemon
from poke_env.environment.pokemon_type import PokemonType
from utilities import damage_estimate


# Load the type chart from the JSON file
with open('type-chart.json', 'r') as f:
    TYPE_CHART = json.load(f)

class SmarterAI5(Player):
    def choose_move(self, battle : AbstractBattle):
        if battle.available_moves:
            # Evaluate moves based on type effectiveness, priority, and weather conditions
            best_move = None
            best_score = -float('inf')

            for move in battle.available_moves:
                #move_effectiveness = self.calculate_move_effectiveness(move, battle)
                move_score = damage_estimate(battle.active_pokemon, move, battle.opponent_active_pokemon)

                # Factor in STAB
                #for type in battle.active_pokemon.types:
                #  if type.name==move.type.name: move_score *= battle.active_pokemon.stab_multiplier

                # Factor in priority moves
                if move.priority > 0:
                    move_score += move.base_power * 0.5  # Give priority moves a bonus

                # Factor in weather effects (e.g., boost Water-type moves in rain)
                move_score += self.evaluate_weather(move, battle)

                # Prioritize moves with the best score
                if move_score > best_score:
                    best_score = move_score
                    best_move = move

            return self.create_order(best_move)
        else:
            return self.choose_random_move(battle)

    def calculate_move_effectiveness(self, move : Move, battle : AbstractBattle):
        # Get the opponent's active Pokémon type
        opponent_type = battle.opponent_active_pokemon.types[0].name
                

        # Look up the effectiveness from the JSON type chart
        effectiveness = 1  # Default effectiveness is 1 (no effect)
        move_type = move.type.name

        if move_type in TYPE_CHART and opponent_type in TYPE_CHART[move_type]:
            effectiveness = TYPE_CHART[move_type][opponent_type]
        
        return effectiveness

    def evaluate_weather(self, move, battle):
        # Example: boost Water-type moves in rain, Fire-type moves in sun
        weather = battle.weather  # Assuming 'weather' is available in battle

        effectiveness = 0
        if weather == 'rain' and move.type.name == 'water':
            effectiveness += 1.5  # Boost Water-type moves in rain
        elif weather == 'sun' and move.type.name == 'fire':
            effectiveness += 1.5  # Boost Fire-type moves in sun

        return effectiveness

    def choose_pokemon_to_switch(self, battle):
        # Switch logic based on health and type matchups
        if battle.available_pokemon:
            for pokemon in battle.available_pokemon:
                # Prioritize switch if the current Pokémon is low on health
                if pokemon.hp / pokemon.max_hp < 0.3:  # Low HP threshold
                    return pokemon

                # Switch to a Pokémon with type advantage over opponent's active Pokémon
                if self.is_strong_against_opponent(pokemon, battle.opponent_active_pokemon):
                    return pokemon

        return None

    def is_strong_against_opponent(self, pokemon, opponent_pokemon):
        # Check if the pokemon is strong against the opponent's type using the JSON type chart
        pokemon_types = [type.name for type in pokemon.types]
        opponent_types = [type.name for type in opponent_pokemon.types]
        
        for p_type in pokemon_types:
            for o_type in opponent_types:
                if p_type in TYPE_CHART and o_type in TYPE_CHART[p_type]:
                    if TYPE_CHART[p_type][o_type] > 1:
                        return True
        return False