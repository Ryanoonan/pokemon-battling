import time
import json
from poke_env.player import Player

# Load type chart from JSON
with open('type-chart.json', 'r') as f:
    TYPE_CHART = json.load(f)

class basic_RLAgent(Player):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.opponent_move_history = []

    def choose_move(self, battle):
        if battle.available_moves:
            predicted_move = self.predict_opponent_move(battle)
            best_move = self.choose_counter_move(predicted_move, battle)
            return self.create_order(best_move)
        else:
            return self.choose_random_move(battle)
    
    def predict_opponent_move(self, battle):
        if len(self.opponent_move_history) > 1:
            # Check the last few moves and predict based on frequency
            last_moves = self.opponent_move_history[-2:]
            predicted_move = self.predict_based_on_history(last_moves)
            return predicted_move
        return None
    
    def predict_based_on_history(self, history):
        # For simplicity, just predict based on the last move (you could implement more advanced models here)
        last_move = history[-1]
        if last_move.type.name == 'fire':
            # Example: if the opponent used a fire move, predict they'll use it again
            return last_move
        # Else, return a default move (e.g., a safe move like a status move)
        return history[0]

    def choose_counter_move(self, predicted_move, battle):
        if predicted_move:
            # Try to switch to a Pokémon or use a move that counters the predicted move
            # Example: if opponent used a Fire-type move, switch to a Water-type Pokémon
            counter_move = self.counter_move_based_on_prediction(predicted_move, battle)
            return counter_move
        return self.choose_random_move(battle)
    
    def counter_move_based_on_prediction(self, predicted_move, battle):
        # Use type chart or other logic to counter the predicted move
        # Example: if predicted_move is fire, choose water-type move
        if predicted_move and predicted_move.type.name == 'fire':
            # Find Water-type move or Pokémon to counter Fire
            for move in battle.available_moves:
                if move.type.name == 'water':
                    return move
        return battle.available_moves[0]  # Fallback to first available move

class RLAgent1(Player):
    
    def choose_move(self, battle):
        if battle.available_moves:
            best_move = None
            best_score = -float('inf')
            
            start_time = time.time()  # Start timer
            
            time_limit = 2  # Set a time limit in seconds for move selection (adjust as needed)
            max_moves_to_evaluate = 5  # Limit number of moves to evaluate
            
            # Sort moves by base power and type effectiveness initially
            sorted_moves = sorted(battle.available_moves, key=lambda move: move.base_power, reverse=True)
            
            for move in sorted_moves[:max_moves_to_evaluate]:  # Evaluate only top N moves
                if time.time() - start_time > time_limit:
                    print("Time limit reached, stopping search.")
                    break  # Stop evaluating moves if the time limit is reached
                
                move_effectiveness = self.calculate_move_effectiveness(move, battle)
                move_score = move.base_power * move_effectiveness

                # Factor in priority moves
                if move.priority > 0:
                    move_score += move.base_power * 0.5  # Give priority moves a bonus

                # Factor in weather effects (e.g., boost Water-type moves in rain)
                move_score += self.evaluate_weather(move, battle)

                # Prioritize moves with the best score
                if move_score > best_score:
                    best_score = move_score
                    best_move = move

            # If no move was selected due to time limit, fall back to a random move
            if not best_move:
                print("No move selected within the time limit, choosing randomly.")
                best_move = self.choose_random_move(battle)
                
            return self.create_order(best_move)
        else:
            return self.choose_random_move(battle)

    def calculate_move_effectiveness(self, move, battle):
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
