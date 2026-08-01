"""
MTG Match Simulator - Simulador de Partidas V2
Usa RulesEngineV2 + StrategicAI + ManaSolver para simulacoes corretas.
"""

import random
import time
from dataclasses import dataclass, field
from typing import Optional
from .card import Card
from .game_state import GameState, PlayerState
from .rules_engine_v2 import RulesEngineV2
from .strategic_ai import StrategicAI
from .action_generator import ActionGenerator, ActionType
from .mana_solver import ManaSolver


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
# Simulador V2
# ─────────────────────────────────────────────

class MatchSimulatorV2:
    """Simula partidas MTG usando RulesEngineV2 + StrategicAI."""

    def __init__(self, deck_a: list, deck_b: list,
                 name_a: str = "Deck A", name_b: str = "Deck B",
                 verbosity: int = 0):
        self.deck_a = deck_a
        self.deck_b = deck_b
        self.name_a = name_a
        self.name_b = name_b
        self.verbosity = verbosity

    def simulate_match(self, match_number: int = 1, recorder=None) -> MatchResult:
        """Simula uma partida individual."""
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
        state = GameState(player1=p1, player2=p2, logging_enabled=True)

        # Cria RulesEngineV2
        engine = RulesEngineV2(state, recorder=recorder)
        state._engine = engine

        # Cria StrategicAI para ambos os jogadores
        ai1 = StrategicAI()
        ai2 = StrategicAI()

        # Cria ActionGenerator
        action_gen = ActionGenerator()
        mana_solver = ManaSolver()

        # Log inicial
        engine._log(f"=== Partida {match_number}: {self.name_a} vs {self.name_b} ===")
        engine._log(f"Mao inicial {self.name_a}: {[c.name for c in p1.hand]}")
        engine._log(f"Mao inicial {self.name_b}: {[c.name for c in p2.hand]}")

        # Loop principal do jogo
        max_turns = 100  # Evita loop infinito
        turn_count = 0

        while not state.is_game_over and turn_count < max_turns:
            turn_count += 1
            
            if state.active_player_index == 0:
                self._execute_player_turn(state, engine, ai1, action_gen, mana_solver, p1, p2)
            else:
                self._execute_player_turn(state, engine, ai2, action_gen, mana_solver, p2, p1)

        # Determina vencedor
        if state.winner is not None:
            if state.winner == 0:
                winner_name = self.name_a
            elif state.winner == 1:
                winner_name = self.name_b
            else:  # -1 = empate
                winner_name = "Empate"
        elif p1.life > p2.life:
            winner_name = self.name_a
        elif p2.life > p1.life:
            winner_name = self.name_b
        else:
            winner_name = "Empate"

        loser_name = self.name_b if winner_name == self.name_a else self.name_a

        # Cria resultado
        result = MatchResult(
            match_number=match_number,
            winner_name=winner_name,
            loser_name=loser_name,
            winner_life=max(p1.life, p2.life),
            loser_life=min(p1.life, p2.life),
            turns=turn_count,
            winner_deck=winner_name,
            loser_deck=loser_name,
            winner_damage_dealt=0,
            winner_life_gained=0,
            winner_creatures_lost=0,
            winner_spells_cast=0
        )

        if recorder:
            recorder.end_match(winner_name, turn_count)

        if self.verbosity > 0:
            print(f"Partida {match_number}: {winner_name} venceu em {turn_count} turnos")

        return result

    def _execute_player_turn(self, state, engine, ai, action_gen, mana_solver, player, opponent):
        """Executa o turno de um jogador usando StrategicAI."""
        engine._log(f"\n--- Turno de {player.name} ---")
        
        # Reseta pool de mana e contador de terrenos no inicio do turno
        player.mana_pool = {}
        player.lands_played = 0
        
        # Desvira todas as criaturas e terrenos (untap)
        for card in player.battlefield:
            card.tapped = False
            card.has_attacked = False
            if getattr(card, 'is_creature', False):
                card.summoning_sick = False
        
        # Fase de compra
        player.draw_cards(1)
        engine._log(f"{player.name} comprou uma carta")

        # Processa upkeep (para triggers de Suspend, etc.)
        engine.process_upkeep(player)

        # Fase principal - IA decide o que fazer
        max_actions = 20  # Evita loop infinito
        action_count = 0

        while action_count < max_actions:
            action_count += 1
            
            # Gera acoes disponiveis
            actions = action_gen.generate_all_actions(player, opponent, state)
            
            # IA escolhe a melhor acao
            decision = ai.decide(player, opponent, state)
            
            # Executa a acao
            if decision.action == "PLAY_LAND" and decision.target:
                card = decision.target
                if card in player.hand:
                    success = engine.play_land(player, card)
                    if success:
                        engine._log(f"  {player.name} jogou {card.name}")
                    else:
                        break
                else:
                    break
            
            elif decision.action == "CAST" and decision.target:
                card = decision.target
                plan = decision.plan
                
                if plan and plan.can_pay:
                    # Executa plano de mana: vira terrenos E adiciona mana ao pool
                    for step in plan.steps:
                        if step.source and hasattr(step.source, 'tapped'):
                            step.source.tapped = True
                            engine._log(f"  {player.name} virou {step.source.name} para mana")
                        # Adiciona mana produzido ao pool do jogador
                        for color, amount in step.mana_produced.items():
                            player.mana_pool[color] = player.mana_pool.get(color, 0) + amount
                    
                    # Conjura a magia
                    success = engine.cast_spell(player, card)
                    if success:
                        engine._log(f"  {player.name} conjurou {card.name}")
                    else:
                        break
                else:
                    # Tenta conjurar mesmo assim (pode ter mana no pool)
                    success = engine.cast_spell(player, card)
                    if success:
                        engine._log(f"  {player.name} conjurou {card.name}")
                    else:
                        break
            
            elif decision.action == "SUSPEND" and decision.target:
                card = decision.target
                success = engine.suspend_card(player, card)
                if success:
                    engine._log(f"  {player.name} suspendeu {card.name}")
                else:
                    break
            
            elif decision.action == "ATTACK":
                attackers = decision.target
                if attackers:
                    engine.declare_attackers(player, attackers)
                    engine._log(f"  {player.name} atacou com {len(attackers)} criatura(s)")
                break  # So ataca uma vez por turno
            
            elif decision.action == "PASS":
                engine._log(f"  {player.name} passou")
                break
            
            else:
                break

        # Fase de combate (se a IA nao decidiu atacar neste turno)
        # Evita ataque duplo verificando has_attacked nas criaturas
        attackers = [c for c in player.battlefield 
                     if hasattr(c, 'is_creature') and c.is_creature 
                     and not c.tapped and not getattr(c, 'summoning_sick', False)
                     and not getattr(c, 'has_attacked', False)]
        
        if attackers:
            engine.declare_attackers(player, attackers)
            engine._log(f"  {player.name} atacou com {len(attackers)} criatura(s)")

        # Fase de limpeza
        # Descarta cartas acima do limite (7)
        while len(player.hand) > 7:
            discarded = player.hand.pop()
            player.graveyard.append(discarded)
            engine._log(f"  {player.name} descartou {discarded.name}")

        # Proximo jogador
        state.active_player_index = 1 - state.active_player_index
        state.turn_number += 1

        # Pipeline de resolucao
        engine.resolve_pipeline()
