from skyjo_env import SkyjoEnv
import numpy as np 

num_players = 3
env = SkyjoEnv(num_players)  # Initialize with the chosen number of players

# Start a new game
observation = env.reset()
env.render(is_reset=True)

done = False
while not done:
    for player_id in range(num_players):
        # Handle Draw Stage
        if player_id == env.agent_position:  # If it's Skybot's turn
            action_str = input("Skybot's turn to draw. Enter 0 to draw from deck, 1 to draw from discard pile: ")
            action = int(action_str)
        else:
            # Random draw action for other players
            action = np.random.choice([0, 1]) if env.discard_pile else 0        
        
        # Take a draw step in the environment using the action for the current player_id
        observation, reward, done, info = env.step(player_id, action)
        
        if player_id == env.agent_position:  # If it's Skybot's turn
            action_type_str = input("Enter 0 to swap a card, 1 to reveal a card: ")
            action_type = int(action_type_str)
            card_index_str = input("Enter card index to swap or reveal: ")
            card_index = int(card_index_str)
            action = (action_type, card_index)
        else:
            # Random decision action for other players
            action_type = np.random.choice([0, 1])
            card_index = np.random.choice(range(12))
            action = (action_type, card_index)
            

        # Take a decision step in the environment using the action for the current player_id
        observation, reward, done, info = env.step(player_id, action)
        env.render()

        print(f"Player {player_id}, Reward: {reward}, Game Over: {done}")

    if done:
        break
