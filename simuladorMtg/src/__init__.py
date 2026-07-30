"""
MTG Match Simulator
Simulador de partidas de Magic: The Gathering.
"""

from .card import Card, CardType, Color, ManaCost, Keyword, EffectType, SpellEffect
from .game_state import GameState, PlayerState
from .rules_engine import RulesEngine
from .player import AIPlayer
from .simulator import MatchSimulator, MatchupStats, MatchResult
from .replay import ReplayRecorder, ReplayManager
