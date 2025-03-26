import time
import json
from poke_env.player import Player

# Load type chart from JSON
with open('type-chart.json', 'r') as f:
    TYPE_CHART = json.load(f)

# Dummy predicting agent based on history
class basic_Prediction_Agent(Player):
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

