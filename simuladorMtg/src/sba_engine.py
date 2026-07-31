"""
MTG Match Simulator - SBA Engine & Priority Engine
Acoes baseadas em estado e sistema de prioridade.
"""

from typing import Any, List, Optional
from .event_bus import GameEvent, Event, EventBus


# ─────────────────────────────────────────────
# State-Based Actions (SBA) Engine
# ─────────────────────────────────────────────

class SBAEngine:
    """
    Verifica e aplica acoes baseadas em estado (regra 704).
    Sao verificadas sempre que um jogador receberia prioridade.
    """
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
    
    def check_and_apply(self, state) -> bool:
        """
        Verifica todas as SBAs e aplica as necessarias.
        Retorna True se alguma SBA foi aplicada.
        """
        applied = False
        
        # 1. Jogador com 0 ou menos vida perde o jogo
        for player_idx, player in enumerate([state.player1, state.player2]):
            if player.life <= 0:
                if not player.cant_lose_game_this_turn:
                    if not (player.has_phyrexian_unlife and player.life == 0):
                        state.winner = 2 if player_idx == 0 else 1
                        self.event_bus.emit_simple(
                            GameEvent.GAME_LOST,
                            source=player,
                            reason="life_total_zero"
                        )
                        applied = True
        
        # 2. Jogador que precisa comprar com biblioteca vazia perde
        for player_idx, player in enumerate([state.player1, state.player2]):
            if len(player.library) == 0 and len(player.hand) == 0:
                state.winner = 2 if player_idx == 0 else 1
                self.event_bus.emit_simple(
                    GameEvent.DECKOUT,
                    source=player
                )
                applied = True
        
        # 3. Criaturas com resistencia 0 ou menos vao para o cemiterio
        for player in [state.player1, state.player2]:
            dead_creatures = []
            for card in player.battlefield[:]:
                if hasattr(card, 'current_toughness') and card.current_toughness <= 0:
                    dead_creatures.append(card)
                elif hasattr(card, 'is_creature') and card.is_creature:
                    if hasattr(card, 'toughness') and card.toughness <= 0:
                        dead_creatures.append(card)
            
            for card in dead_creatures:
                player.battlefield.remove(card)
                player.graveyard.append(card)
                self.event_bus.emit_simple(
                    GameEvent.CREATURE_DIED,
                    source=card,
                    controller=player
                )
                applied = True
        
        # 4. Jogador com 10 ou mais marcadores de veneno perde
        for player_idx, player in enumerate([state.player1, state.player2]):
            poison = getattr(player, 'poison_counters', 0)
            if poison >= 10:
                state.winner = 2 if player_idx == 0 else 1
                self.event_bus.emit_simple(
                    GameEvent.GAME_LOST,
                    source=player,
                    reason="poison_counters"
                )
                applied = True
        
        # 5. Auras sem alvo legal vao para o cemiterio
        for player in [state.player1, state.player2]:
            for card in player.battlefield[:]:
                if hasattr(card, 'is_aura') and card.is_aura:
                    if not getattr(card, 'enchanted_target', None):
                        player.battlefield.remove(card)
                        player.graveyard.append(card)
                        applied = True
        
        # 6. Tokens que nao estao no campo de batalha cessam de existir
        # (ja sao removidos automaticamente)
        
        # 7. Esvazia mana pool no final de cada fase/etapa
        # (feito pelo Rules Engine)
        
        # 8. Dano letal em criaturas
        for player in [state.player1, state.player2]:
            for card in player.battlefield[:]:
                if hasattr(card, 'is_creature') and card.is_creature:
                    lethal = getattr(card, 'lethal_damage', 0)
                    if lethal > 0:
                        player.battlefield.remove(card)
                        player.graveyard.append(card)
                        self.event_bus.emit_simple(
                            GameEvent.CREATURE_DIED,
                            source=card,
                            controller=player
                        )
                        applied = True
        
        return applied


# ─────────────────────────────────────────────
# Priority Engine
# ─────────────────────────────────────────────

class PriorityEngine:
    """
    Gerencia o sistema de prioridade do jogo.
    Determina qual jogador pode tomar acoes.
    """
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self._priority_player: int = 0  # 0 = player1, 1 = player2
        self._passes_this_round: int = 0
    
    @property
    def priority_player_index(self) -> int:
        return self._priority_player
    
    def set_priority(self, player_index: int):
        """Define qual jogador tem prioridade."""
        self._priority_player = player_index
    
    def pass_priority(self):
        """Jogador ativo passa prioridade."""
        self._passes_this_round += 1
    
    def reset_passes(self):
        """Reseta os passes."""
        self._passes_this_round = 0
    
    def both_players_passed(self) -> bool:
        """Verifica se ambos jogadores passaram consecutivamente."""
        return self._passes_this_round >= 2
    
    def get_priority_player_name(self, state) -> str:
        """Retorna o nome do jogador com prioridade."""
        if self._priority_player == 0:
            return state.player1.name
        return state.player2.name
    
    def yield_priority(self, state):
        """Passa prioridade para o outro jogador."""
        self._priority_player = 1 - self._priority_player
        self._passes_this_round = 0
