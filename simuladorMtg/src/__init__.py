"""
MTG Match Simulator
Simulador de partidas de Magic: The Gathering.
"""

from .card import Card, CardType, Color, ManaCost, Keyword, EffectType, SpellEffect
from .game_state import GameState, PlayerState
from .rules_engine import RulesEngine
from .rules_engine_v2 import RulesEngineV2
from .event_bus import GameEvent, Event, EventBus
from .trigger_manager import TriggerManager, TriggeredAbility, Stack, StackItem, StackItemType
from .sba_engine import SBAEngine, PriorityEngine
from .replacement_effects import ReplacementEffectManager, ReplacementEffect, ContinuousEffectManager
from .card_abilities_db import get_card_abilities, has_ability, get_effect_name
from .modern_card_abilities import MODERN_CARD_ABILITIES, get_card_abilities as get_modern_abilities
from .mana_engine import ManaAbilityEngine, ManaAbility, ManaActionType, LAND_MANA_ABILITIES
from .mana_solver import ManaSolver, ManaPlan, ManaStep
from .strategic_ai import StrategicAI, LandPlanner, LandPlan, GameDecision
from .action_generator import ActionGenerator, GameAction, ActionType, SPECIAL_CARD_ACTIONS
from .player import AIPlayer
from .simulator import MatchSimulator, MatchupStats, MatchResult
from .replay import ReplayRecorder, ReplayManager
