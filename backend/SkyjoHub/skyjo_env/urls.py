from django.urls import path
from .views import GameActionView, StartGameView, RegisterPlayerView, ScoreTrackView

urlpatterns = [
    path('game-action/', GameActionView.as_view(), name='game_action_view'),
    path('start-game/', StartGameView.as_view(), name='start_game_view'),
    path('register-player/', RegisterPlayerView.as_view(), name='register_player_view'),
    path('track-score/', ScoreTrackView.as_view(), name='track_score_view'),
]
