"""
MTG Match Simulator - Replacement Effects & Continuous Effects
Gerencia efeitos de substituicao e efeitos continuos em camadas.
"""

from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum, auto
from .event_bus import GameEvent, Event, EventBus


# ─────────────────────────────────────────────
# Replacement Effects
# ─────────────────────────────────────────────

class ReplacementEffect:
    """
    Um efeito de substituicao.
    Substitui um evento por outro ou previne o evento.
    """
    
    def __init__(self, source, event_to_replace: GameEvent, 
                 replacement_func: Callable = None,
                 prevent: bool = False,
                 duration: str = "permanent",
                 description: str = ""):
        self.source = source
        self.event_to_replace = event_to_replace
        self.replacement_func = replacement_func
        self.prevent = prevent
        self.duration = duration  # "permanent", "until_end_of_turn", "one_time"
        self.description = description
        self._used = False
    
    def applies(self, event: Event) -> bool:
        """Verifica se este replacement se aplica ao evento."""
        return event.event_type == self.event_to_replace
    
    def apply(self, event: Event) -> bool:
        """
        Aplica o replacement effect.
        Retorna False para prevenir o evento, True para permitir.
        """
        if self.prevent:
            return False
        
        if self.replacement_func:
            self.replacement_func(event)
        
        if self.duration == "one_time":
            self._used = True
        
        return True


class ReplacementEffectManager:
    """Gerencia todos os replacement effects ativos."""
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self._effects: List[ReplacementEffect] = []
    
    def add_effect(self, effect: ReplacementEffect):
        """Adiciona um replacement effect."""
        self._effects.append(effect)
        
        # Registra no event bus
        def handler(event):
            if effect.applies(event):
                return effect.apply(event)
            return None
        
        self.event_bus.add_replacement_effect(handler)
    
    def remove_effect(self, effect: ReplacementEffect):
        """Remove um replacement effect."""
        if effect in self._effects:
            self._effects.remove(effect)
    
    def remove_effects_for_source(self, source):
        """Remove todos os efeitos de uma fonte."""
        self._effects = [e for e in self._effects if e.source != source]
    
    def get_active_effects(self) -> List[ReplacementEffect]:
        """Retorna os efeitos ativos."""
        return [e for e in self._effects if not e._used]


# ─────────────────────────────────────────────
# Continuous Effect Layers
# ─────────────────────────────────────────────

class Layer(Enum):
    """Camadas de efeitos continuos (regra 613)."""
    COPY = 1           # 613.1a
    CONTROL = 2        # 613.1b
    TEXT = 3           # 613.1c
    TYPE = 4           # 613.1d
    COLOR = 5          # 613.1e
    ADD_REMOVETYPES = 6  # 613.1f
    PT_MODIFY = 7      # 613.1g (power/toughness)
    PT_SET = 7         # 613.1g
    PT_COUNTERS = 7    # 613.1g
    PT_SWAP = 7        # 613.1g


@dataclass
class ContinuousEffect:
    """Um efeito continuo que modifica caracteristicas de objetos."""
    source: Any
    layer: int
    target: Any = None
    modification: Dict = field(default_factory=dict)
    duration: str = "permanent"  # "permanent", "until_end_of_turn", "until_leaves_battlefield"
    description: str = ""
    _active: bool = True
    
    def applies_to(self, obj) -> bool:
        """Verifica se o efeito se aplica ao objeto."""
        if self.target is None:
            return True
        return obj == self.target


class ContinuousEffectManager:
    """
    Gerencia efeitos continuos em camadas.
    Aplica na ordem correta das camadas.
    """
    
    def __init__(self):
        self._effects: List[ContinuousEffect] = []
    
    def add_effect(self, effect: ContinuousEffect):
        """Adiciona um efeito continuo."""
        self._effects.append(effect)
    
    def remove_effect(self, effect: ContinuousEffect):
        """Remove um efeito continuo."""
        if effect in self._effects:
            self._effects.remove(effect)
    
    def remove_effects_for_source(self, source):
        """Remove todos os efeitos de uma fonte."""
        self._effects = [e for e in self._effects if e.source != source]
    
    def apply_all(self, game_object):
        """
        Aplica todos os efeitos continuos a um objeto.
        Segue a ordem das camadas.
        """
        # Ordena por camada
        sorted_effects = sorted(self._effects, key=lambda e: e.layer)
        
        for effect in sorted_effects:
            if effect._active and effect.applies_to(game_object):
                self._apply_effect(effect, game_object)
    
    def _apply_effect(self, effect: ContinuousEffect, obj):
        """Aplica um efeito continuo a um objeto."""
        mod = effect.modification
        
        # Power/Toughness
        if 'power' in mod:
            if hasattr(obj, 'current_power'):
                if effect.layer == 7:
                    if 'set' in mod:
                        obj.current_power = mod['power']
                    else:
                        obj.current_power += mod['power']
        
        if 'toughness' in mod:
            if hasattr(obj, 'current_toughness'):
                if effect.layer == 7:
                    if 'set' in mod:
                        obj.current_toughness = mod['toughness']
                    else:
                        obj.current_toughness += mod['toughness']
        
        # Types
        if 'add_type' in mod:
            if hasattr(obj, 'types'):
                if mod['add_type'] not in obj.types:
                    obj.types.append(mod['add_type'])
        
        if 'remove_type' in mod:
            if hasattr(obj, 'types') and mod['remove_type'] in obj.types:
                obj.types.remove(mod['remove_type'])
        
        # Colors
        if 'add_color' in mod:
            if hasattr(obj, 'colors'):
                if mod['add_color'] not in obj.colors:
                    obj.colors.append(mod['add_color'])
        
        # Keywords
        if 'add_keyword' in mod:
            if hasattr(obj, 'keywords'):
                if mod['add_keyword'] not in obj.keywords:
                    obj.keywords.append(mod['add_keyword'])
        
        if 'remove_keyword' in mod:
            if hasattr(obj, 'keywords') and mod['remove_keyword'] in obj.keywords:
                obj.keywords.remove(mod['remove_keyword'])
    
    def get_active_effects(self) -> List[ContinuousEffect]:
        """Retorna os efeitos ativos."""
        return [e for e in self._effects if e._active]
    
    def clear_expired(self):
        """Remove efeitos expirados."""
        self._effects = [e for e in self._effects if e._active]
