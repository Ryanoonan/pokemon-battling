import json
from poke_env.player import Player

# Load type chart from the JSON file
with open('../type-chart.json', 'r') as f:
    TYPE_CHART = json.load(f)

# Base AI class with common functionality
class SimpleAI(Player):
    def choose_move(self, battle):
        if battle.available_moves:
            best_move = self.evaluate_moves(battle)
            return self.create_order(best_move)
        else:
            return self.choose_random_move(battle)

    def evaluate_moves(self, battle):
        """Evaluate moves in child classes."""
        raise NotImplementedError("This method should be implemented in subclasses.")

    def calculate_move_effectiveness(self, move, battle):
        """Calculate type effectiveness for a move."""
        attacker_type = move.type.name  # Attacking move's type
        opponent_type = battle.opponent_active_pokemon.types[0].name  # Opponent's active Pokémon's type
        effectiveness = TYPE_CHART.get(attacker_type, {}).get(opponent_type, 1)
        return effectiveness

    def choose_pokemon_to_switch(self, battle):
        """Consider switching Pokémon based on type advantages."""
        if battle.available_pokemon:
            for pokemon in battle.available_pokemon:
                if self.is_strong_against_opponent(pokemon, battle.opponent_active_pokemon):
                    return pokemon
        return None

    def is_strong_against_opponent(self, pokemon, opponent_pokemon):
        """Check if the Pokémon is strong against the opponent's type."""
        pokemon_types = [type.name for type in pokemon.types]
        opponent_types = [type.name for type in opponent_pokemon.types]

        for p_type in pokemon_types:
            for o_type in opponent_types:
                if TYPE_CHART.get(p_type, {}).get(o_type, 1) > 1:
                    return True
        return False

# SimpleAI1 selects the move with the highest base power from available moves.
class SimpleAI1(SimpleAI):
    def evaluate_moves(self, battle):
        return max(battle.available_moves, key=lambda move: move.base_power)

# SimpleAI2 evaluates moves based on type effectiveness and base power.
class SimpleAI2(SimpleAI):
    def evaluate_moves(self, battle):
        best_move = None
        best_score = -float('inf')

        for move in battle.available_moves:
            move_effectiveness = self.calculate_move_effectiveness(move, battle)
            move_score = move.base_power * move_effectiveness

            if move_score > best_score:
                best_score = move_score
                best_move = move

        return best_move

# SimpleAI3 evaluates moves based on type effectiveness, priority, weather effects, and health.
class SimpleAI3(SimpleAI):
    def evaluate_moves(self, battle):
        best_move = None
        best_score = -float('inf')

        for move in battle.available_moves:
            move_effectiveness = self.calculate_move_effectiveness(move, battle)
            move_score = move.base_power * move_effectiveness

            if move.priority > 0:
                move_score += move.base_power * 0.5  # Give priority moves a bonus

            move_score += self.evaluate_weather(move, battle)

            if move_score > best_score:
                best_score = move_score
                best_move = move

        return best_move

    def evaluate_weather(self, move, battle):
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
                if pokemon.hp / pokemon.max_hp < 0.3:  # Low HP threshold
                    return pokemon
                if self.is_strong_against_opponent(pokemon, battle.opponent_active_pokemon):
                    return pokemon

        return None
