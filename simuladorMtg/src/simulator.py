"""
MTG Match Simulator - Simulador de Partidas
Executa múltiplas partidas e coleta estatísticas.
"""

import random
import time
from dataclasses import dataclass, field
from typing import Optional
from .card import Card
from .game_state import GameState, PlayerState
from .rules_engine import RulesEngine
from .player import AIPlayer


# ─────────────────────────────────────────────
# Resultado de uma Partida
# ─────────────────────────────────────────────

@dataclass
class MatchResult:
    """Resultado de uma partida individual."""
    match_number: int
    winner_name: str
    loser_name: str
    winner_life: int
    loser_life: int
    turns: int
    winner_deck: str
    loser_deck: str
    winner_damage_dealt: int
    winner_life_gained: int
    winner_creatures_lost: int
    winner_spells_cast: int


# ─────────────────────────────────────────────
# Estatísticas do Matchup
# ─────────────────────────────────────────────

@dataclass
class MatchupStats:
    """Estatísticas de um matchup entre dois decks."""
    deck_a_name: str
    deck_b_name: str
    total_matches: int = 0
    deck_a_wins: int = 0
    deck_b_wins: int = 0
    draws: int = 0
    deck_a_avg_life: float = 0.0
    deck_b_avg_life: float = 0.0
    deck_a_avg_turns: float = 0.0
    deck_b_avg_turns: float = 0.0
    avg_game_length: float = 0.0
    deck_a_avg_damage: float = 0.0
    deck_b_avg_damage: float = 0.0
    deck_a_avg_spells: float = 0.0
    deck_b_avg_spells: float = 0.0
    results: list = field(default_factory=list)

    @property
    def deck_a_winrate(self) -> float:
        if self.total_matches == 0:
            return 0.0
        return (self.deck_a_wins / self.total_matches) * 100

    @property
    def deck_b_winrate(self) -> float:
        if self.total_matches == 0:
            return 0.0
        return (self.deck_b_wins / self.total_matches) * 100

    @property
    def superior_deck(self) -> str:
        if self.deck_a_winrate > self.deck_b_winrate:
            return self.deck_a_name
        elif self.deck_b_winrate > self.deck_a_winrate:
            return self.deck_b_name
        return "Empate"

    @property
    def winrate_difference(self) -> float:
        return abs(self.deck_a_winrate - self.deck_b_winrate)


# ─────────────────────────────────────────────
# Simulador
# ─────────────────────────────────────────────

class MatchSimulator:
    """Simula partidas MTG entre dois decks."""

    def __init__(self, deck_a: list, deck_b: list,
                 name_a: str = "Deck A", name_b: str = "Deck B",
                 verbosity: int = 0):
        """
        deck_a, deck_b: listas de Card objects (60 cartas cada)
        name_a, name_b: nomes dos decks
        verbosity: 0=silencioso, 1=resumo, 2=detalhado
        """
        self.deck_a = deck_a
        self.deck_b = deck_b
        self.name_a = name_a
        self.name_b = name_b
        self.verbosity = verbosity

    def simulate_match(self, match_number: int = 1, recorder=None) -> MatchResult:
        """Simula uma partida individual.
        
        Args:
            match_number: Numero da partida
            recorder: ReplayRecorder opcional para gravar a partida
        """
        # Prepara decks frescos
        deck_a_cards = [c.copy() for c in self.deck_a]
        deck_b_cards = [c.copy() for c in self.deck_b]

        random.shuffle(deck_a_cards)
        random.shuffle(deck_b_cards)

        # Cria estados dos jogadores
        p1 = PlayerState(name=self.name_a, life=20, library=deck_a_cards)
        p2 = PlayerState(name=self.name_b, life=20, library=deck_b_cards)

        # Mao inicial (7 cartas)
        p1.draw_cards(7)
        p2.draw_cards(7)

        # Cria estado do jogo
        state = GameState(player1=p1, player2=p2, logging_enabled=(recorder is not None))

        # Inicia gravacao se houver recorder
        if recorder:
            recorder.start_match(self.name_a, self.name_b, match_number)
            recorder.record_frame(state, "start")

        # Cria IAs (agressividade ligeiramente diferente para variedade)
        ai1 = AIPlayer(aggressiveness=0.5 + random.uniform(-0.15, 0.15))
        ai2 = AIPlayer(aggressiveness=0.5 + random.uniform(-0.15, 0.15))

        # Cria motor de regras
        engine = RulesEngine(state)

        # Loop principal do jogo
        while not state.is_game_over:
            if state.active_player_index == 0:
                engine.execute_turn(ai1)
            else:
                engine.execute_turn(ai2)
            
            # Grava frame apos cada turno
            if recorder:
                recorder.record_frame(state)

        # Coleta resultado
        winner_idx = state.winner
        
        # Finaliza gravacao
        if recorder:
            if winner_idx == 0:
                recorder.end_match(p1.name, state.turn_number)
            elif winner_idx == 1:
                recorder.end_match(p2.name, state.turn_number)
            else:
                recorder.end_match("Empate", state.turn_number)
        
        if winner_idx == 0:
            winner = p1
            loser = p2
            winner_deck = self.name_a
            loser_deck = self.name_b
        elif winner_idx == 1:
            winner = p2
            loser = p1
            winner_deck = self.name_b
            loser_deck = self.name_a
        else:
            # Empate
            return MatchResult(
                match_number=match_number,
                winner_name="Empate",
                loser_name="Empate",
                winner_life=0, loser_life=0,
                turns=state.turn_number,
                winner_deck="", loser_deck="",
                winner_damage_dealt=0, winner_life_gained=0,
                winner_creatures_lost=0, winner_spells_cast=0,
            )

        return MatchResult(
            match_number=match_number,
            winner_name=winner.name,
            loser_name=loser.name,
            winner_life=winner.life,
            loser_life=max(loser.life, 0),
            turns=state.turn_number,
            winner_deck=winner_deck,
            loser_deck=loser_deck,
            winner_damage_dealt=winner.damage_dealt,
            winner_life_gained=winner.life_gained,
            winner_creatures_lost=winner.creatures_lost,
            winner_spells_cast=winner.spells_cast,
        )

    def simulate_matches(self, num_matches: int) -> MatchupStats:
        """Simula múltiplas partidas e coleta estatísticas."""
        stats = MatchupStats(deck_a_name=self.name_a, deck_b_name=self.name_b)
        total_a_life = 0
        total_b_life = 0
        total_a_damage = 0
        total_b_damage = 0
        total_a_spells = 0
        total_b_spells = 0
        total_turns = 0

        start_time = time.time()

        for i in range(1, num_matches + 1):
            result = self.simulate_match(match_number=i)
            stats.results.append(result)
            stats.total_matches += 1
            total_turns += result.turns

            if result.winner_name == self.name_a:
                stats.deck_a_wins += 1
            elif result.winner_name == self.name_b:
                stats.deck_b_wins += 1
            else:
                stats.draws += 1

            # Acumula stats para ambos os decks
            for r in [result]:
                if r.winner_deck == self.name_a:
                    total_a_life += r.winner_life
                    total_b_life += r.loser_life
                    total_a_damage += r.winner_damage_dealt
                    total_b_damage += 0
                    total_a_spells += r.winner_spells_cast
                elif r.winner_deck == self.name_b:
                    total_b_life += r.winner_life
                    total_a_life += r.loser_life
                    total_b_damage += r.winner_damage_dealt
                    total_a_damage += 0
                    total_b_spells += r.winner_spells_cast

            if self.verbosity >= 1:
                # Mostra progresso em marcos (25%, 50%, 75%, 100%)
                step = max(num_matches // 4, 1)
                if i % step == 0 or i == num_matches:
                    pct = (i / num_matches) * 100
                    print(f"  Progresso: {i}/{num_matches} ({pct:.0f}%)")

        # Calcula médias
        n = max(num_matches, 1)
        stats.avg_game_length = total_turns / n
        stats.deck_a_avg_life = total_a_life / n
        stats.deck_b_avg_life = total_b_life / n
        stats.deck_a_avg_damage = total_a_damage / n
        stats.deck_b_avg_damage = total_b_damage / n
        stats.deck_a_avg_spells = total_a_spells / n
        stats.deck_b_avg_spells = total_b_spells / n

        elapsed = time.time() - start_time

        if self.verbosity >= 1:
            print(f"\n  Simulacao concluida em {elapsed:.2f}s")

        return stats

    def simulate_and_record(self, num_matches: int, replay_dir: str = "replays") -> tuple:
        """Simula partidas e grava replays de todas elas.
        
        Args:
            num_matches: Numero de partidas para simular
            replay_dir: Diretorio para salvar os replays
            
        Returns:
            Tuple com (MatchupStats, lista de caminhos dos replays salvos)
        """
        from .replay import ReplayRecorder, ReplayManager
        
        replay_manager = ReplayManager(replay_dir)
        stats = MatchupStats(deck_a_name=self.name_a, deck_b_name=self.name_b)
        saved_replays = []
        total_a_life = 0
        total_b_life = 0
        total_a_damage = 0
        total_b_damage = 0
        total_a_spells = 0
        total_b_spells = 0
        total_turns = 0

        start_time = time.time()

        for i in range(1, num_matches + 1):
            # Cria recorder para esta partida
            recorder = ReplayRecorder()
            result = self.simulate_match(match_number=i, recorder=recorder)
            
            # Salva o replay
            replay_path = replay_manager.save_replay(recorder)
            saved_replays.append(replay_path)
            
            stats.results.append(result)
            stats.total_matches += 1
            total_turns += result.turns

            if result.winner_name == self.name_a:
                stats.deck_a_wins += 1
            elif result.winner_name == self.name_b:
                stats.deck_b_wins += 1
            else:
                stats.draws += 1

            for r in [result]:
                if r.winner_deck == self.name_a:
                    total_a_life += r.winner_life
                    total_b_life += r.loser_life
                    total_a_damage += r.winner_damage_dealt
                    total_a_spells += r.winner_spells_cast
                elif r.winner_deck == self.name_b:
                    total_b_life += r.winner_life
                    total_a_life += r.loser_life
                    total_b_damage += r.winner_damage_dealt
                    total_b_spells += r.winner_spells_cast

            if self.verbosity >= 1:
                step = max(num_matches // 4, 1)
                if i % step == 0 or i == num_matches:
                    pct = (i / num_matches) * 100
                    print(f"  Progresso: {i}/{num_matches} ({pct:.0f}%) - Replays salvos")

        n = max(num_matches, 1)
        stats.avg_game_length = total_turns / n
        stats.deck_a_avg_life = total_a_life / n
        stats.deck_b_avg_life = total_b_life / n
        stats.deck_a_avg_damage = total_a_damage / n
        stats.deck_b_avg_damage = total_b_damage / n
        stats.deck_a_avg_spells = total_a_spells / n
        stats.deck_b_avg_spells = total_b_spells / n

        elapsed = time.time() - start_time

        if self.verbosity >= 1:
            print(f"\n  Simulacao concluida em {elapsed:.2f}s")
            print(f"  {len(saved_replays)} replays salvos em: {replay_dir}/")

        return stats, saved_replays
