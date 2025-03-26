import sys
import asyncio
import logging
from tabulate import tabulate
from poke_env import RandomPlayer, cross_evaluate
from poke_env import Player, ShowdownServerConfiguration, AccountConfiguration

# Disable all warnings (including INFO, WARNING, etc.)
logging.basicConfig(level=logging.ERROR)

# # Add your src path to sys.path
# sys.path.append("../src")

# Initialize players

random_player = RandomPlayer()
second_player = RandomPlayer()
third_player = RandomPlayer()
players = [random_player, second_player, third_player]


# # No authentication required
# my_account_config = AccountConfiguration("my_username", None)
# player = Player(account_configuration=my_account_config)
# # Auto-generated configuration for local use
# player = Player()

account_config = AccountConfiguration("my_username", "super-secret-password")
player = RandomPlayer(server_configuration=ShowdownServerConfiguration, account_configuration=account_config)

# Initiating the battle with the `await` keyword to handle the async battle process
async def start_battles():
    for _ in range(5):  # Run 5 battles
        await random_player.battle_against(second_player, n_battles=1)

    # Print results after battles
    print(
        f"Player {random_player.username} won {random_player.n_won_battles} out of {random_player.n_finished_battles} played"
    )
    print(
        f"Player {second_player.username} won {second_player.n_won_battles} out of {second_player.n_finished_battles} played"
    )

    # Printing which battle random player won 
    for battle_tag, battle in random_player.battles.items():
        print(battle_tag, battle.won)

# Cross-evaluation function
async def cross_evaluation():
    return await cross_evaluate(players, n_challenges=5)

def display_cross_eval(cross_evaluation_results):
    # Create the table to display the cross-evaluation results
    table = [["-"] + [p.username for p in players]]
    for p_1, results in cross_evaluation_results.items():
        table.append([p_1] + [cross_evaluation_results[p_1].get(p_2, "-") for p_2 in results])

    # Print the table
    print(tabulate(table))

# Run the battle and cross-evaluation functions asynchronously
async def main():
    await start_battles()  # Run the 5 battles
    cross_evaluation_results = await cross_evaluation()  # Cross-evaluate players
    display = display_cross_eval(cross_evaluation_results)

# Running the main asynchronous function
asyncio.run(main())

