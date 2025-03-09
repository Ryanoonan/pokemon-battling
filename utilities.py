import json
from poke_env.environment.abstract_battle import AbstractBattle
from poke_env.environment.move import Move
from poke_env.environment.move_category import MoveCategory
from poke_env.environment.pokemon import Pokemon
from poke_env.environment.pokemon_type import PokemonType
with open('type-chart2.json', 'r') as f:
    TYPE_CHART = json.load(f)

def damage_estimate(user : Pokemon, move : Move, target : Pokemon) -> int: 
  """
    Estimates the damage based on the official formula:\n
    https://bulbapedia.bulbagarden.net/wiki/Damage
  """
  level=user.level
  if move.category ==MoveCategory.PHYSICAL: a=stat_calculator(user, 'atk')
  elif move.category ==MoveCategory.SPECIAL: a=stat_calculator(user, 'spa')
  else: return 0
  
  if move.defensive_category==MoveCategory.PHYSICAL: d=stat_calculator(user, 'def')
  else: d=stat_calculator(user, 'spd')
  power=move.base_power
  stab=user.stab_multiplier if move.type in user.types else 1

  # Look up the effectiveness from the JSON type chart
  effectiveness = move.type.damage_multiplier(type_1=target.type_1, type_2=target.type_2, type_chart=TYPE_CHART)  # Default effectiveness is 1 (no effect)

  damage=2*level/5 + 2
  damage*=power*(a/d)
  damage/=50
  damage+=2
  damage*=stab*effectiveness
  
  return damage

def stat_calculator(pokemon : Pokemon, stat_name : str, iv : int=31,ev : int=84, nature : int=1):
  """
    Estimates the stat based on the official formula:\n
    https://bulbapedia.bulbagarden.net/wiki/Stat
  """
  base=pokemon.base_stats[stat_name]
  level=pokemon.level

  stat=2*base+iv+(ev/4)
  stat*=level
  stat/=100
  stat+=5
  stat*=nature

  return stat