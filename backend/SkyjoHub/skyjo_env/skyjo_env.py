import gym
from gym import spaces
import numpy as np


class SkyjoEnv(gym.Env):
    def __init__(self,num_players,  max_players=8):
        super(SkyjoEnv, self).__init__()

        # Define the maximum number of players
        self.max_players = max_players

        self.num_players = num_players  # Set the actual number of players
    
        # Initialize player hands, active players get empty hands, inactive get placeholder data
        self.players_hands = []

        # Define action space
        # Define two separate action spaces
        self.action_space_draw = spaces.Discrete(2)  # Draw from deck (0) or discard pile (1)
        self.action_space_decision = spaces.Tuple((spaces.Discrete(2), spaces.Discrete(12)))  # (action_type: 0 swap the drawn card or 1 drop, card_index)

        # Define a variable to track the current stage ('draw' or 'decision')
        self.current_stage = 'draw'

        # Initialize a variable to store the drawn card during the decision stage
        self.drawn_card = None

        # Define observation space
        # Observation for each player: 12 cards
        # -3 for hidden cards
        # -4 for the placeholder for the drawn card during the draw stage/inexistent cards for inexistent players
        # Actual values (0 to 12) for visible cards
        # Each player has 12 cards, and one additional slot for the drawn card during the decision stage
        card_observation_space = spaces.Box(low=-4, high=12, shape=(13,), dtype=np.int32)  # +1 for the drawn card
        self.observation_space = spaces.Tuple([card_observation_space] * self.max_players + [spaces.Discrete(self.max_players)])

        self.scores = [0 for _ in range(self.max_players)]  # Initialize scores for each player

        # Initialize game state variables
        self.deck = self._create_deck()
        self.players_hands = []
        self.discard_pile = []
        self.hidden_cards_values = {}
        self.agent_position = None

    def _create_deck(self):
        # Deck composition: numbers from -2 to 12
        # Each number has a specific count to make a total of 150 cards
        # Adjust the counts per card as per the Skyjo rules
        card_counts = {-2: 5, -1: 10, 0: 10, 1: 10, 2: 10, 3: 10, 4: 10, 5: 10, 
                    6: 10, 7: 10, 8: 10, 9: 10, 10: 10, 11: 10, 12: 5}
        
        # Create the deck by repeating each card value its specific count
        deck = [card for card, count in card_counts.items() for _ in range(count)]
        
        # Shuffle the deck
        np.random.shuffle(deck)
        
        return deck

    def _deal_cards(self):
        # Initialize and deal cards for each player
        for i in range(self.max_players):
            if i < self.num_players:
                # Initialize player's hand with hidden cards
                hand = [-3] * 12  # All cards set to hidden initially
                self.hidden_cards_values[i] = [None] * 12  # Initialize hidden card values for this player
                # Randomly choose two cards to reveal
                indices_to_reveal = np.random.choice(range(12), size=2, replace=False)
                for idx in range(12):
                    if self.deck:
                        card = self.deck.pop()
                        if idx in indices_to_reveal:
                            hand[idx] = card  # Reveal the card
                        else:
                            self.hidden_cards_values[i][idx] = card  # Store the actual value of hidden cards
                
                # Append the placeholder for the drawn card slot
                hand.append(-4)
                # Add the hand to the players_hands list
                self.players_hands.append(hand)
            else:
                # Set hands for extra players (beyond num_players) to placeholders
                self.players_hands.append([-4] * 13)
    
    def reset(self):        
        # Shuffle the deck
        np.random.shuffle(self.deck)
        # Set the discard pile to empty initially
        self.discard_pile = []

        # Randomly determine the agent's position
        self.agent_position = np.random.choice(range(self.num_players))

        # Reset the current stage to 'draw'
        self.current_stage = 'draw'
        self.drawn_card = None
        
        # Deal cards to each player
        self._deal_cards()
        
        # Start the discard pile with the first card from the deck
        if self.deck:
            first_discard_card = self.deck.pop()
            self.discard_pile.append(first_discard_card)
            
        # Return the initial observation
        observation = self.players_hands + [self.agent_position]
        return observation

    def _reveal_hidden_card(self, player_id, card_index):
        """Reveal a hidden card."""
        player_hand = self.players_hands[player_id]
        if player_hand[card_index] == -3 and self.deck:  # Check if the card is hidden and deck is not empty
            card = self.deck.pop()  # Draw the actual value of the card
            player_hand[card_index] = card  # Reveal the card by updating its value
  
    def _swap_card(self, player_id, card_index):
        """Swap a card (visible or hidden) with the drawn card and handle hidden cards properly."""
        player_hand = self.players_hands[player_id]
        old_card_value = player_hand[card_index]  # This is -3 for hidden cards
        # Check if the card to be swapped is hidden, and if so, get its real value from another structure or handle accordingly
        if old_card_value == -3:
            # Assuming we have a structure that stores the actual values of hidden cards, like self.hidden_cards_values[player_id][card_index]
            old_card_value = self.hidden_cards_values[player_id][card_index]
        player_hand[card_index] = self.drawn_card
        self.drawn_card = old_card_value  # Store the old card's value to be used in discard
        return old_card_value

    def _is_card_hidden(self, player_id, card_index):
        """Check if the card at the given index in the agent's hand is hidden."""
        player_hand = self.players_hands[player_id]
        return player_hand[card_index][1] == 0

    def _discard_card(self, card):
        """Discard the given card."""
        self.discard_pile.append(card)

    def _execute_player_action(self,player_id, action):
        """logic for discarding, playing, and swapping cards"""

        action_type,card_index = action
        if action_type == 1 and not self.drawn_from_discard_memory:  # Reveal action
            self._reveal_hidden_card(player_id, card_index)
            self._discard_card(self.drawn_card)

        else: # Swap action            
            old_card = self._swap_card(player_id, card_index)
            self._discard_card(old_card)

    def _draw_card(self,draw_from_discard):
        """drawing card from the discard pile or from the deck"""
        if draw_from_discard and self.discard_pile:
            drawn_card = self.discard_pile.pop()
        else:
            drawn_card = self.deck.pop() if self.deck else None
        return drawn_card

    def _handle_column_disappearance(self):
        for player_hand in self.players_hands:
            for col_index in range(4):  # Assuming a 3x4 grid
                column_cards = [player_hand[row_index * 4 + col_index] for row_index in range(3)]
                
                # Check if all cards in the column are visible (not -3) and have the same value
                if all(card != -3 for card in column_cards):
                    unique_values = set(column_cards)
                    if len(unique_values) == 1:
                        # Remove the column by setting to -4 (removed state)
                        for row_index in range(3):
                            player_hand[row_index * 4 + col_index] = -4

    def _update_scores(self):
        for i, player_hand in enumerate(self.players_hands):
            round_score = sum(card for card in player_hand if card >= -2) 
            self.scores[i] += round_score  # Add to the accumulated score

    def _get_standard_observation(self):
        # Standard observation includes players' hands and the agent's position
        return self.players_hands + [self.agent_position]

    def _get_observation_with_drawn_card(self,player_id):
        # Get the standard observation
        observation = self._get_standard_observation()

        # Update the last card of the agent's hand to reflect the drawn card
        observation[player_id][-1] = self.drawn_card  # Represent the drawn card as visible

        return observation

    def step(self, player_id, action):
        reward = 0
        done = False
        info = {}       

        if self.current_stage == 'draw':
            print(f" -------------- Drawing stage for player {player_id} -------------- \n")
            print(f"Player {player_id} draws from {'discard pile' if action == 1 else 'deck'}")
            observation, done = self._handle_draw_stage(action, player_id)
            print(f"Player {player_id} drawn card value: {self.drawn_card}")
        elif self.current_stage == 'decision':
            print(f" -------------- Decision stage for player {player_id} -------------- \n")
            print(f"Player {player_id} decides on action type: {'swap' if action[0] == 0 else 'reveal'}, card index: {action[1]}")
            observation, reward, done = self._handle_decision_stage(player_id, action)
                
        return observation, reward, done, info

    def _handle_draw_stage(self, action, player_id):
        # Handle draw action
        self.drawn_card = self._draw_card(action)  # action is 0 or 1 for draw stage
        self.drawn_from_discard_memory = action

        # If no card can be drawn (deck and discard pile are empty), end the game
        if self.drawn_card is None:
            return self._get_standard_observation(), True  # Game over
        
        # Transition to the decision stage
        self.current_stage = 'decision'
        # Include the drawn card in the observation for the decision stage
        return self._get_observation_with_drawn_card(player_id), False

    def _handle_decision_stage(self, player_id, action):
        # Handle decision action (action is card_to_swap_index)
        
        self._execute_player_action(player_id, action)

        # Handle column disappearance
        self._handle_column_disappearance()

        # Calculate the reward (placeholder)
        reward = self._calculate_reward()

        # Check if the round is over (all cards of any player are face-up)
        round_over = self._check_round_over()
        if round_over:
            self._update_scores()  # Update scores at the end of the round        

        # Check if the game is over (placeholder)
        done = self._check_game_over()

        # Transition back to the draw stage for the next player
        self.current_stage = 'draw'
        self.drawn_card = None
        # Get the standard observation without the drawn card
        return self._get_standard_observation(), reward, done

    def _calculate_reward(self):
        pass

    def _check_game_over(self):
        # Check if any player's score has reached or exceeded 100 points
        if any(score >= 100 for score in self.scores):
            return True
        return False  # Continue the game if no end condition is met

    def _check_round_over(self):      
        # Check if any player has all their cards face-up or removed
        for player_hand in self.players_hands[:self.num_players]:
            if all(card >= -2 or card == -4 for card in player_hand):  # Check if all cards are visible or removed
                return True  # Game over if all cards of a player are face-up or removed
        return False
    
    def render(self, is_reset=False):
        if is_reset:
            print(' -------------- Game reset .. -------------- \n')
        num_rows = 3
        num_columns = 4
        print(' ')
        for i, player_hand in enumerate(self.players_hands):
            # Skip rendering for inactive players (entire hand is -4)
            if all(card == -4 for card in player_hand):
                continue

            # Display the hand for active players or Skybot
            if i == self.agent_position:
                print(f"Skybot's Hand (Player {i}):")
            else:
                print(f"Player {i}'s Hand:")
            
            for row in range(num_rows):
                row_str = '  '.join('*' if card == -3 else str(card) if card >= -2 else '' for card in player_hand[row * num_columns:(row + 1) * num_columns])
                print(row_str)
        
        # Display top of discard pile and cards left in deck
        top_of_discard_pile = self.discard_pile[-1] if self.discard_pile else 'Empty'
        cards_left_in_deck = len(self.deck)
        print(f"Top of Discard Pile: {top_of_discard_pile}")
        print(f"Cards left in Deck: {cards_left_in_deck}")

        # Display scores (only for active players)
        scores_str = ', '.join([f"Player {i}: {score}" for i, score in enumerate(self.scores) if i < len(self.players_hands) and not all(card == -4 for card in self.players_hands[i])])
        print(f"Scores: [{scores_str}]")
        print(' ')
        if is_reset:
            print(' -------------- Game reset done! -------------- \n')
