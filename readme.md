Skyjo AI Environment
Skyjo is an engaging card game where players aim to achieve the lowest score by uncovering and collecting cards with minimal points. This AI environment simulates the Skyjo game, providing a platform for developing and testing Reinforcement Learning (RL) algorithms.

Game Overview:
Objective: Players strive to have the lowest score when the game ends. The game concludes when one player reveals all their cards, or a player's accumulated score reaches or exceeds 100 points over multiple rounds.
Card Values: The deck consists of cards numbered from -2 to 12.
Setup: Each player starts with a 3x4 grid of face-down cards, turning two cards face-up at the beginning.
Gameplay Mechanics:
Turns: On their turn, a player either draws from the deck or takes the top card from the discard pile.
Actions: Players can swap the drawn card with one of their face-down cards or discard it. If discarding, they must reveal a hidden card in their grid.
Column Clearing: If a column has face-up cards with the same value, they are removed, potentially lowering the player's score.
AI Environment:
Action Space: Defined as a tuple representing the choice of drawing a card and the decision to swap or reveal a card.
Observation Space: Includes all the players hands, each card's visibility status, and the top card of the discard pile.
Reinforcement Learning: The environment is designed for experimenting with various RL algorithms, allowing for the development of strategies to minimize scores and react to evolving game states.
