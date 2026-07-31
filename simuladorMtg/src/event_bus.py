"""
MTG Match Simulator - Event Bus
Sistema central de eventos. Tudo no jogo gera eventos.
"""

from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, field
import time


class GameEvent(Enum):
    """Todos os eventos possiveis no jogo."""
    # Acoes de jogador
    CAST_SPELL = auto()
    ACTIVATE_ABILITY = auto()
    PLAY_LAND = auto()
    ATTACK = auto()
    BLOCK = auto()
    PASS_PRIORITY = auto()
    MULLIGAN = auto()
    
    # Spell/Ability resolution
    SPELL_RESOLVED = auto()
    SPELL_COUNTERED = auto()
    ABILITY_RESOLVED = auto()
    
    # Card movement
    CARD_DRAWN = auto()
    CARD_DISCARDED = auto()
    CARD_EXILED = auto()
    CARD_MILLED = auto()
    CARD_PUT_IN_HAND = auto()
    
    # Permanent events
    PERMANENT_ENTERS = auto()
    PERMANENT_LEAVES = auto()
    PERMANENT_TAPPED = auto()
    PERMANENT_UNTAPPED = auto()
    
    # Creature events
    CREATURE_DIED = auto()
    CREATURE_ATTACKED = auto()
    CREATURE_BLOCKED = auto()
    CREATURE_DEALT_DAMAGE = auto()
    
    # Life events
    LIFE_GAINED = auto()
    LIFE_LOST = auto()
    DAMAGE_DEALT = auto()
    
    # Mana events
    MANA_ADDED = auto()
    MANA_PAID = auto()
    
    # Turn events
    TURN_STARTED = auto()
    TURN_ENDED = auto()
    PHASE_CHANGED = auto()
    STEP_CHANGED = auto()
    
    # Stack events
    SPELL_PUT_ON_STACK = auto()
    SPELL_REMOVED_FROM_STACK = auto()
    
    # Library events
    LIBRARY_SEARCHED = auto()
    LIBRARY_SHUFFLED = auto()
    DECKOUT = auto()
    
    # Game events
    GAME_WON = auto()
    GAME_LOST = auto()
    
    # Counter events
    COUNTER_ADDED = auto()
    COUNTER_REMOVED = auto()
    
    # Special
    PAY_LIFE_COST = auto()
    EXILE_FROM_LIBRARY = auto()


@dataclass
class Event:
    """Um evento individual no jogo."""
    event_type: GameEvent
    source: Any = None          # Carta/jogador que causou o evento
    target: Any = None          # Alvo do evento
    data: Dict = field(default_factory=dict)  # Dados adicionais
    timestamp: float = field(default_factory=time.time)
    prevented: bool = False     # Se o evento foi prevenido
    modified: bool = False      # Se o evento foi modificado
    
    def __repr__(self):
        source_name = getattr(self.source, 'name', str(self.source)) if self.source else 'None'
        target_name = getattr(self.target, 'name', str(self.target)) if self.target else 'None'
        return f"Event({self.event_type.name}, source={source_name}, target={target_name}, data={self.data})"


class EventBus:
    """
    Barramento central de eventos.
    Todos os eventos do jogo passam por aqui.
    """
    
    def __init__(self):
        self._listeners: Dict[GameEvent, List[Callable]] = {}
        self._event_log: List[Event] = []
        self._pending_events: List[Event] = []
        self._replacement_effects: List[Callable] = []
    
    def subscribe(self, event_type: GameEvent, callback: Callable):
        """Registra um listener para um tipo de evento."""
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(callback)
    
    def unsubscribe(self, event_type: GameEvent, callback: Callable):
        """Remove um listener."""
        if event_type in self._listeners:
            self._listeners[event_type] = [
                cb for cb in self._listeners[event_type] if cb != callback
            ]
    
    def emit(self, event: Event) -> List[Any]:
        """
        Emite um evento.
        1. Aplica replacement effects
        2. Notifica todos os listeners
        3. Registra no log
        Retorna lista de resultados dos listeners.
        """
        if event.prevented:
            return []
        
        # Aplica replacement effects
        for replacement in self._replacement_effects:
            result = replacement(event)
            if result is False:
                event.prevented = True
                self._log_event(event)
                return []
        
        # Notifica listeners
        results = []
        listeners = self._listeners.get(event.event_type, [])
        for listener in listeners:
            try:
                result = listener(event)
                if result is not None:
                    results.append(result)
            except Exception as e:
                print(f"  [EVENT ERROR] {event.event_type.name}: {e}")
        
        self._log_event(event)
        return results
    
    def emit_simple(self, event_type: GameEvent, source=None, target=None, **data) -> List[Any]:
        """Atalho para emitir um evento simples."""
        event = Event(event_type=event_type, source=source, target=target, data=data)
        return self.emit(event)
    
    def add_replacement_effect(self, callback: Callable):
        """Adiciona um replacement effect."""
        self._replacement_effects.append(callback)
    
    def remove_replacement_effect(self, callback: Callable):
        """Remove um replacement effect."""
        if callback in self._replacement_effects:
            self._replacement_effects.remove(callback)
    
    def _log_event(self, event: Event):
        """Registra o evento no log."""
        self._event_log.append(event)
        # Mantem apenas os ultimos 500 eventos
        if len(self._event_log) > 500:
            self._event_log = self._event_log[-500:]
    
    def get_log(self, last_n: int = 50) -> List[Event]:
        """Retorna os ultimos N eventos."""
        return self._event_log[-last_n:]
    
    def clear_log(self):
        """Limpa o log de eventos."""
        self._event_log.clear()
    
    def clear_all(self):
        """Limpa tudo."""
        self._listeners.clear()
        self._event_log.clear()
        self._pending_events.clear()
        self._replacement_effects.clear()
