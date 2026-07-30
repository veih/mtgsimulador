"""
MTG Match Simulator - Estado da Partida
Gerencia todas as zonas, vida, mana e estado geral do jogo.
"""

import random
from dataclasses import dataclass, field
from typing import Optional
from .card import Card, Zone, Color, Keyword


# ─────────────────────────────────────────────
# Estado do Jogador
# ─────────────────────────────────────────────

@dataclass
class PlayerState:
    """Estado completo de um jogador durante a partida."""
    name: str
    life: int = 20
    library: list = field(default_factory=list)    # Card objects
    hand: list = field(default_factory=list)
    battlefield: list = field(default_factory=list)
    graveyard: list = field(default_factory=list)
    exile: list = field(default_factory=list)
    mana_pool: dict = field(default_factory=dict)  # {Color: amount}
    lands_played: int = 0
    cards_drawn_this_turn: int = 0
    damage_dealt: int = 0
    life_gained: int = 0
    creatures_lost: int = 0
    spells_cast: int = 0

    @property
    def creatures_on_board(self) -> list:
        return [c for c in self.battlefield if c.is_creature]

    @property
    def lands_on_board(self) -> list:
        return [c for c in self.battlefield if c.is_land]

    @property
    def available_untapped_lands(self) -> list:
        return [c for c in self.lands_on_board if not c.tapped]

    @property
    def available_creatures_for_attack(self) -> list:
        """Criaturas que podem atacar (sem summoning sickness, desviradas)."""
        result = []
        for c in self.creatures_on_board:
            if c.tapped:
                continue
            if c.has_keyword(Keyword.HASTE):
                result.append(c)
            elif not c.summoning_sick:
                result.append(c)
        return result

    def calculate_mana_pool(self) -> dict:
        """Calcula o mana pool disponível (terrenos desvirados)."""
        pool = {}
        for land in self.available_untapped_lands:
            for color in land.land_mana:
                pool[color] = pool.get(color, 0) + 1
        return pool

    def can_cast(self, card: Card) -> bool:
        """Verifica se o jogador tem mana para conjurar a carta."""
        pool = self.calculate_mana_pool()
        return card.mana_cost.can_pay(pool)

    def move_card(self, card: Card, from_zone: Zone, to_zone: Zone):
        """Move uma carta entre zonas."""
        zones = {
            Zone.LIBRARY: self.library,
            Zone.HAND: self.hand,
            Zone.BATTLEFIELD: self.battlefield,
            Zone.GRAVEYARD: self.graveyard,
            Zone.EXILE: self.exile,
        }

        source = zones.get(from_zone, [])
        dest = zones.get(to_zone, [])

        if card in source:
            source.remove(card)

        if to_zone == Zone.BATTLEFIELD:
            card.tapped = False
            card.summoning_sick = True
            card.has_attacked = False
            card.current_power = -1
            card.current_toughness = -1

        dest.append(card)

    def draw_cards(self, count: int) -> list:
        """Compra cartas do topo da biblioteca."""
        drawn = []
        for _ in range(count):
            if not self.library:
                break
            card = self.library.pop(0)
            self.hand.append(card)
            drawn.append(card)
            self.cards_drawn_this_turn += 1
        return drawn

    def mill(self, count: int) -> list:
        """Coloca cartas do topo da biblioteca no cemitério."""
        milled = []
        for _ in range(count):
            if not self.library:
                break
            card = self.library.pop(0)
            self.graveyard.append(card)
            milled.append(card)
        return milled

    def shuffle_library(self):
        """Embaralha a biblioteca."""
        random.shuffle(self.library)

    def untap_all(self):
        """Desvira todos os permanentes."""
        for card in self.battlefield:
            card.tapped = False
            card.has_attacked = False

    def end_of_turn_cleanup(self):
        """Limpeza de final de turno."""
        # Remove summoning sickness de criaturas
        for c in self.creatures_on_board:
            c.summoning_sick = False
        # Reseta pumps temporários
        for c in self.creatures_on_board:
            c.reset_temporary()
        # Esvazia mana pool
        self.mana_pool = {}
        self.lands_played = 0
        self.cards_drawn_this_turn = 0

    def discard_random(self) -> Optional[Card]:
        """Descarta uma carta aleatória da mão."""
        if not self.hand:
            return None
        card = random.choice(self.hand)
        self.hand.remove(card)
        self.graveyard.append(card)
        return card

    def discard_non_land(self) -> Optional[Card]:
        """Descarta uma carta não-terreno aleatória."""
        non_lands = [c for c in self.hand if not c.is_land]
        if not non_lands:
            return self.discard_random()
        card = random.choice(non_lands)
        self.hand.remove(card)
        self.graveyard.append(card)
        return card

    @property
    def is_dead(self) -> bool:
        return self.life <= 0

    @property
    def has_no_cards(self) -> bool:
        """Verifica se a biblioteca está vazia (deck out)."""
        return len(self.library) == 0 and len(self.hand) == 0


# ─────────────────────────────────────────────
# Estado da Partida
# ─────────────────────────────────────────────

@dataclass
class GameState:
    """Estado completo de uma partida MTG."""
    player1: PlayerState
    player2: PlayerState
    turn_number: int = 1
    active_player_index: int = 0   # 0 = player1, 1 = player2
    phase: str = "beginning"
    stack: list = field(default_factory=list)
    game_log: list = field(default_factory=list)
    winner: Optional[int] = None
    max_turns: int = 100
    logging_enabled: bool = False  # desativado por padrao para performance
    _log_max: int = 20             # mantem so as ultimas N mensagens

    @property
    def active_player(self) -> PlayerState:
        return self.player1 if self.active_player_index == 0 else self.player2

    @property
    def non_active_player(self) -> PlayerState:
        return self.player2 if self.active_player_index == 0 else self.player1

    @property
    def active_player_name(self) -> str:
        return self.active_player.name

    @property
    def is_game_over(self) -> bool:
        if self.winner is not None:
            return True
        if self.player1.is_dead:
            self.winner = 1
            return True
        if self.player2.is_dead:
            self.winner = 0
            return True
        # Deck out
        if self.player1.has_no_cards and len(self.player1.library) == 0:
            self.winner = 1
            return True
        if self.player2.has_no_cards and len(self.player2.library) == 0:
            self.winner = 0
            return True
        # Limite de turnos
        if self.turn_number > self.max_turns:
            # Quem tiver mais vida ganha
            if self.player1.life > self.player2.life:
                self.winner = 0
            elif self.player2.life > self.player1.life:
                self.winner = 1
            else:
                self.winner = -1  # empate
            return True
        return False

    def log(self, message: str):
        if not self.logging_enabled:
            return
        self.game_log.append(f"[T{self.turn_number}] {message}")
        # Limita o tamanho do log
        if len(self.game_log) > self._log_max:
            self.game_log = self.game_log[-self._log_max:]

    def switch_active_player(self):
        self.active_player_index = 1 - self.active_player_index

    def get_player_by_index(self, index: int) -> PlayerState:
        return self.player1 if index == 0 else self.player2

    def get_player_index(self, player: PlayerState) -> int:
        return 0 if player is self.player1 else 1

    def summary(self) -> dict:
        """Retorna um resumo do estado atual."""
        return {
            "turn": self.turn_number,
            "phase": self.phase,
            "p1": {
                "name": self.player1.name,
                "life": self.player1.life,
                "hand": len(self.player1.hand),
                "library": len(self.player1.library),
                "battlefield": len(self.player1.battlefield),
                "graveyard": len(self.player1.graveyard),
            },
            "p2": {
                "name": self.player2.name,
                "life": self.player2.life,
                "hand": len(self.player2.hand),
                "library": len(self.player2.library),
                "battlefield": len(self.player2.battlefield),
                "graveyard": len(self.player2.graveyard),
            }
        }
