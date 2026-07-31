"""
MTG Match Simulator - Trigger Manager & Stack System
Gerencia habilidades desencadeadas e a pilha (stack).
"""

from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum, auto
from .event_bus import GameEvent, Event, EventBus


# ─────────────────────────────────────────────
# Trigger Manager
# ─────────────────────────────────────────────

@dataclass
class TriggeredAbility:
    """Uma habilidade desencadeada."""
    card: Any               # Carta que possui a habilidade
    event_type: GameEvent   # Evento que dispara a habilidade
    condition: Callable = None  # Condicao adicional (recebe event, retorna bool)
    effect: Callable = None    # Efeito quando resolve (recebe event, state)
    description: str = ""
    
    def matches(self, event: Event) -> bool:
        """Verifica se o evento dispara esta habilidade."""
        if event.event_type != self.event_type:
            return False
        if self.condition and not self.condition(event):
            return False
        return True


@dataclass
class PendingTrigger:
    """Uma trigger que esta na fila aguardando para ir para a pilha."""
    ability: TriggeredAbility
    event: Event
    controller: Any  # Jogador que controla a trigger


class TriggerManager:
    """
    Gerencia todas as habilidades desencadeadas do jogo.
    Quando um evento ocorre, verifica quais triggers disparam.
    """
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self._registered_triggers: List[TriggeredAbility] = []
        self._pending_triggers: List[PendingTrigger] = []
        
        # Registra listener no event bus
        self.event_bus.subscribe(GameEvent.PERMANENT_ENTERS, self._on_permanent_enters)
        self.event_bus.subscribe(GameEvent.CARD_DRAWN, self._on_card_drawn)
        self.event_bus.subscribe(GameEvent.CREATURE_DIED, self._on_creature_died)
        self.event_bus.subscribe(GameEvent.LIFE_LOST, self._on_life_lost)
        self.event_bus.subscribe(GameEvent.SPELL_RESOLVED, self._on_spell_resolved)
    
    def register_trigger(self, ability: TriggeredAbility):
        """Registra uma habilidade desencadeada."""
        self._registered_triggers.append(ability)
    
    def unregister_trigger(self, ability: TriggeredAbility):
        """Remove uma habilidade desencadeada."""
        if ability in self._registered_triggers:
            self._registered_triggers.remove(ability)
    
    def unregister_triggers_for_card(self, card):
        """Remove todas as triggers de uma carta."""
        self._registered_triggers = [
            t for t in self._registered_triggers if t.card != card
        ]
    
    def _on_permanent_enters(self, event: Event):
        """Quando um permanente entra no campo de batalha."""
        self._check_triggers(event)
    
    def _on_card_drawn(self, event: Event):
        """Quando uma carta e comprada."""
        self._check_triggers(event)
    
    def _on_creature_died(self, event: Event):
        """Quando uma criatura morre."""
        self._check_triggers(event)
    
    def _on_life_lost(self, event: Event):
        """Quando um jogador perde vida."""
        self._check_triggers(event)
    
    def _on_spell_resolved(self, event: Event):
        """Quando uma magia resolve."""
        self._check_triggers(event)
    
    def _check_triggers(self, event: Event):
        """Verifica quais triggers disparam para um evento."""
        for ability in self._registered_triggers:
            if ability.matches(event):
                # Determina o controlador
                controller = getattr(event.source, 'controller', None)
                if controller is None:
                    controller = event.data.get('controller')
                
                pending = PendingTrigger(
                    ability=ability,
                    event=event,
                    controller=controller
                )
                self._pending_triggers.append(pending)
    
    def get_pending_triggers(self) -> List[PendingTrigger]:
        """Retorna as triggers pendentes."""
        return self._pending_triggers[:]
    
    def clear_pending_triggers(self):
        """Limpa as triggers pendentes."""
        self._pending_triggers.clear()
    
    def put_triggers_on_stack(self, stack):
        """Coloca as triggers pendentes na pilha."""
        for pending in self._pending_triggers:
            stack_item = StackItem(
                item_type=StackItemType.TRIGGERED_ABILITY,
                source=pending.ability.card,
                controller=pending.controller,
                ability=pending.ability,
                event=pending.event,
                description=f"{pending.ability.card.name} trigger"
            )
            stack.push(stack_item)
        
        self._pending_triggers.clear()


# ─────────────────────────────────────────────
# Stack System
# ─────────────────────────────────────────────

class StackItemType(Enum):
    """Tipo de item na pilha."""
    SPELL = auto()
    ACTIVATED_ABILITY = auto()
    TRIGGERED_ABILITY = auto()


@dataclass
class StackItem:
    """Um item na pilha."""
    item_type: StackItemType
    source: Any           # Carta que criou o item
    controller: Any       # Jogador que controla
    ability: Any = None   # Habilidade (para triggered/activated)
    event: Any = None     # Evento (para triggered)
    targets: List = field(default_factory=list)
    description: str = ""
    can_be_countered: bool = True
    
    def __repr__(self):
        return f"StackItem({self.item_type.name}, {self.description})"


class Stack:
    """
    A pilha do jogo de Magic.
    Ultimo a entrar, primeiro a sair (LIFO).
    """
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self._items: List[StackItem] = []
    
    def push(self, item: StackItem):
        """Coloca um item na pilha."""
        self._items.append(item)
        self.event_bus.emit_simple(
            GameEvent.SPELL_PUT_ON_STACK,
            source=item.source,
            description=item.description
        )
    
    def pop(self) -> Optional[StackItem]:
        """Remove e retorna o item do topo da pilha."""
        if not self._items:
            return None
        return self._items.pop()
    
    def peek(self) -> Optional[StackItem]:
        """Retorna o item do topo sem remover."""
        if not self._items:
            return None
        return self._items[-1]
    
    def is_empty(self) -> bool:
        """Verifica se a pilha esta vazia."""
        return len(self._items) == 0
    
    def clear(self):
        """Limpa a pilha."""
        self._items.clear()
    
    def get_items(self) -> List[StackItem]:
        """Retorna todos os itens na pilha."""
        return self._items[:]
    
    def counter_target(self, item: StackItem) -> bool:
        """Contra um item especifico na pilha."""
        if item in self._items:
            self._items.remove(item)
            self.event_bus.emit_simple(
                GameEvent.SPELL_COUNTERED,
                source=item.source,
                description=item.description
            )
            return True
        return False
    
    def __len__(self):
        return len(self._items)
