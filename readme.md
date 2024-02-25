**Skyjo AI Environment**

Skyjo is an engaging card game where players aim to achieve the lowest score by uncovering and collecting cards with minimal points. This AI environment simulates the Skyjo game, providing a platform for developing and testing Reinforcement Learning (RL) algorithms.

**Game Overview:**

<ins>Objective:</ins> Players strive to have the lowest score when the game ends. The game concludes when one player reveals all their cards, or a player's accumulated score reaches or exceeds 100 points over multiple rounds.
<ins>Card Values:</ins> The deck consists of cards numbered from -2 to 12.
<ins>Setup:</ins> Each player starts with a 3x4 grid of face-down cards, turning two cards face-up at the beginning.

**Gameplay Mechanics:**

<ins>Turns:</ins> On their turn, a player either draws from the deck or takes the top card from the discard pile.
<ins>Actions:</ins> Players can swap the drawn card with one of their face-down cards or discard it. If discarding, they must reveal a hidden card in their grid.
<ins>Column Clearing:</ins> If a column has face-up cards with the same value, they are removed, potentially lowering the player's score.

**AI Environment:**

<ins>Action Space:</ins>

The action space is a composite of two stages:
* Draw Stage: A discrete space where 0 represents drawing from the deck and 1 represents drawing from the discard pile.
* Decision Stage: A tuple space consisting of:
  * A discrete action 0 to swap the drawn card with one from the hand or 1 to drop the drawn card.
  * A discrete space representing the card index in the player's hand to swap or reveal (ranging from 0 to 11).

<ins>Observation Space:</ins> 

The observation space for each player includes:
* A 13-dimensional space for the player's hand, with card values ranging from -4 (placeholder for the drawn card during the draw stage/inexistent cards for inexistent players) to 12 (actual card values), and -3 for hidden cards.
* The visibility status of each card in the hand is implicitly represented by its value (-3 for hidden, actual values for visible).
* The top card of the discard pile and the number of cards left in the deck are included in the environment's global state, accessible to all players.

The observation space is designed to provide a comprehensive view of the current game state from the perspective of each player, including the visibility of their own cards and the known cards in the game (such as the top card of the discard pile).

**Reinforcement Learning:**

The environment is designed for experimenting with various RL algorithms, allowing for the development of strategies to minimize scores and react to evolving game states.
