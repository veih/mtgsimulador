"""
MTG Match Simulator - AI Player
IA para tomada de decisões durante a partida.
"""

import random
from typing import Optional
from .card import Card, Keyword, CardType, Color
from .game_state import GameState, PlayerState


class AIPlayer:
    """IA que controla as decisões de um jogador durante a partida."""

    def __init__(self, aggressiveness: float = 0.5):
        """
        aggressiveness: 0.0 = defensivo, 1.0 = agressivo
        """
        self.aggressiveness = aggressiveness

    # ─────────────────────────────────────────
    # Fase Principal
    # ─────────────────────────────────────────

    def main_phase(self, active: PlayerState, opponent: PlayerState,
                   state: GameState):
        """Decide o que fazer na fase principal."""
        # 1. Jogar terreno
        self._play_best_land(active)

        # 2. Conjurar criaturas
        self._cast_creatures(active, opponent, state)

        # 3. Conjurar magias de remoção
        self._cast_removal(active, opponent, state)

        # 4. Conjurar outras magias
        self._cast_other_spells(active, opponent, state)

    def _play_best_land(self, player: PlayerState):
        """Joga o melhor terreno da mão."""
        lands = [c for c in player.hand if c.is_land]
        if not lands:
            return

        # Prioriza terrenos que produzem cores necessárias
        # Simplificado: joga o primeiro terreno disponível
        land = lands[0]
        player.hand.remove(land)
        land.tapped = False
        land.summoning_sick = False
        player.battlefield.append(land)
        player.lands_played += 1

    def _cast_creatures(self, player: PlayerState, opponent: PlayerState,
                        state: GameState):
        """Conjura criaturas da mão, da mais cara para a mais barata."""
        creatures = [
            c for c in player.hand
            if c.card_type == CardType.CREATURE and player.can_cast(c)
        ]
        # Ordena por mana value (maior primeiro - ramp strategy)
        creatures.sort(key=lambda c: c.mana_value, reverse=True)

        for creature in creatures:
            if player.can_cast(creature):
                self._cast_creature(player, creature, state)

    def _cast_creature(self, player: PlayerState, creature: Card,
                       state: GameState):
        """Conjura uma criatura."""
        pool = player.calculate_mana_pool()
        if not creature.mana_cost.can_pay(pool):
            return

        player.mana_pool = creature.mana_cost.pay(pool)
        player.hand.remove(creature)

        # Entra no campo de batalha
        creature.tapped = False
        creature.summoning_sick = True
        creature.has_attacked = False
        player.battlefield.append(creature)

        state.log(f"  [CARD] {player.name} conjura {creature.name} "
                  f"{creature.mana_cost} ({creature.power}/{creature.toughness})")

        # Resolve ETB effects
        for effect in creature.effects:
            from .rules_engine import RulesEngine
            engine = RulesEngine(state)
            engine._resolve_effect(effect, creature, player, None, None)

    def _cast_removal(self, player: PlayerState, opponent: PlayerState,
                      state: GameState):
        """Conjura magias de remoção."""
        from .card import EffectType
        removal_spells = [
            c for c in player.hand
            if c.card_type in (CardType.INSTANT, CardType.SORCERY)
            and player.can_cast(c)
            and any(e.effect_type in (EffectType.DESTROY_CREATURE, EffectType.EXILE,
                                      EffectType.DAMAGE)
                    for e in c.effects)
        ]
        removal_spells.sort(key=lambda c: c.mana_value)

        for spell in removal_spells:
            if spell not in player.hand:
                continue
            if not player.can_cast(spell):
                continue

            pool = player.calculate_mana_pool()
            player.mana_pool = spell.mana_cost.pay(pool)
            player.hand.remove(spell)

            # Escolhe alvo
            target_creature = None
            target_player = None

            for effect in spell.effects:
                if effect.effect_type in (EffectType.DESTROY_CREATURE, EffectType.EXILE):
                    # Remove a maior criatura do oponente
                    creatures = opponent.creatures_on_board
                    if creatures:
                        target_creature = max(creatures,
                                              key=lambda c: c.effective_power)
                elif effect.effect_type == EffectType.DAMAGE:
                    # Dano em criatura se puder matá-la, senão no jogador
                    creatures = opponent.creatures_on_board
                    lethal_targets = [c for c in creatures
                                     if c.effective_toughness <= effect.value]
                    if lethal_targets:
                        target_creature = max(lethal_targets,
                                              key=lambda c: c.effective_power)
                    else:
                        target_player = opponent

            from .rules_engine import RulesEngine
            engine = RulesEngine(state)
            engine.resolve_spell(spell, player, target_player, target_creature)

    def _cast_other_spells(self, player: PlayerState, opponent: PlayerState,
                           state: GameState):
        """Conjura magias que não são criaturas nem remoção."""
        from .card import EffectType
        other_spells = [
            c for c in player.hand
            if c.card_type in (CardType.INSTANT, CardType.SORCERY)
            and player.can_cast(c)
            and not any(e.effect_type in (EffectType.DESTROY_CREATURE, EffectType.EXILE)
                        for e in c.effects)
        ]
        other_spells.sort(key=lambda c: c.mana_value)

        for spell in other_spells:
            if spell not in player.hand:
                continue
            if not player.can_cast(spell):
                continue

            pool = player.calculate_mana_pool()
            player.mana_pool = spell.mana_cost.pay(pool)
            player.hand.remove(spell)

            target_player = None
            target_creature = None

            for effect in spell.effects:
                if effect.effect_type == EffectType.GAIN_LIFE:
                    target_player = player
                elif effect.effect_type == EffectType.PUMP:
                    creatures = player.creatures_on_board
                    if creatures:
                        target_creature = max(creatures,
                                              key=lambda c: c.effective_power)
                elif effect.effect_type == EffectType.DAMAGE:
                    target_player = opponent

            from .rules_engine import RulesEngine
            engine = RulesEngine(state)
            engine.resolve_spell(spell, player, target_player, target_creature)

    # ─────────────────────────────────────────
    # Combate
    # ─────────────────────────────────────────

    def declare_attackers(self, attacker: PlayerState, defender: PlayerState,
                          state: GameState) -> list:
        """Declara atacantes."""
        available = attacker.available_creatures_for_attack

        if not available:
            return []

        # Estratégia: se agressivo, ataca com tudo
        # Se defensivo, só ataca se puder matar ou se o oponente estiver baixo
        if self.aggressiveness >= 0.7:
            return list(available)

        if self.aggressiveness >= 0.4:
            # Ataca se tem vantagem de poder total ou oponente está baixo
            total_power = sum(c.effective_power for c in available)
            opponent_creatures = defender.creatures_on_board
            opponent_power = sum(c.effective_power for c in opponent_creatures)

            if defender.life <= 10:
                return list(available)
            if total_power > opponent_power:
                return list(available)
            # Só ataca com criaturas que não serão trocadas desfavoravelmente
            safe = [c for c in available
                    if c.effective_power <= 2 or c.effective_toughness > 3]
            return safe if safe else []

        # Defensivo: só ataca com criaturas evasivas ou se muito maior
        evasive = [c for c in available
                   if c.has_keyword(Keyword.FLYING) or c.has_keyword(Keyword.MENACE)]
        if evasive and (defender.life <= 12 or len(available) > len(defender.creatures_on_board) + 1):
            return evasive

        total_power = sum(c.effective_power for c in available)
        if total_power >= defender.life:
            return list(available)

        return []

    def declare_blockers(self, defender: PlayerState, attacker: PlayerState,
                         attackers: list, state: GameState) -> list:
        """Declara bloqueadores."""
        available_blockers = [
            c for c in defender.creatures_on_board
            if not c.tapped
        ]

        if not available_blockers:
            return []

        blockers = []
        used_blockers = set()

        for atk_creature in attackers:
            if atk_creature in [b[0] for b in blockers]:
                continue

            # Encontra o melhor bloqueador
            best_blocker = None
            best_score = -999

            for blk in available_blockers:
                if id(blk) in used_blockers:
                    continue

                score = self._block_score(blk, atk_creature, defender)
                if score > best_score:
                    best_score = score
                    best_blocker = blk

            if best_blocker and best_score > -100:
                blockers.append((atk_creature, best_blocker))
                used_blockers.add(id(best_blocker))

        return blockers

    def _block_score(self, blocker: Card, attacker: Card,
                     defender: PlayerState) -> float:
        """Calcula o score de bloquear um atacante com um bloqueador."""
        score = 0.0

        # Pode matar o atacante?
        can_kill = blocker.effective_power >= attacker.effective_toughness
        # Sobrevive ao bloque?
        survives = blocker.effective_toughness > attacker.effective_power

        if attacker.has_keyword(Keyword.DEATHTOUCH):
            # Deathtouch: qualquer dano é letal, então só bloqueia se for indestrutível
            if blocker.has_keyword(Keyword.INDESTRUCTIBLE):
                return 100
            return -200

        if can_kill and survives:
            score += 50  # Troca favorável
        elif can_kill and not survives:
            # Troca justa ou desfavorável
            if attacker.mana_value >= blocker.mana_value:
                score += 20
            else:
                score -= 10
        elif not can_kill and survives:
            score += 5  # Absorve dano sem morrer
        else:
            score -= 30  # Morre sem matar

        # Prioriza bloquear criaturas com evasão
        if attacker.has_keyword(Keyword.FLYING):
            if blocker.has_keyword(Keyword.FLYING) or blocker.has_keyword(Keyword.REACH):
                score += 30
            else:
                return -999  # Não pode bloquear

        # Se o defensor está baixo de vida, prioriza bloquear
        if defender.life <= 8:
            score += 40
        elif defender.life <= 12:
            score += 20

        # Menace precisa de 2 bloqueadores (simplificado: não bloqueia)
        if attacker.has_keyword(Keyword.MENACE):
            score -= 20

        return score
