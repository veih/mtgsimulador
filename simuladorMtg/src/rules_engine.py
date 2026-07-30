"""
MTG Match Simulator - Rules Engine
Motor de regras: fases, combate, stack, efeitos e state-based actions.
"""

import random
from typing import Optional
from .card import (Card, Keyword, EffectType, SpellEffect, TargetType, Color)
from .game_state import GameState, PlayerState


class RulesEngine:
    """Motor de regras que processa cada fase do turno e resolve efeitos."""

    def __init__(self, state: GameState):
        self.state = state

    # ─────────────────────────────────────────
    # State-Based Actions (SBAs)
    # ─────────────────────────────────────────

    def check_state_based_actions(self):
        """Verifica e aplica SBAs (regra 704)."""
        changed = True
        iterations = 0
        while changed and iterations < 10:  # limite de seguranca
            changed = False
            iterations += 1
            for player in [self.state.player1, self.state.player2]:
                # Criatura com toughness <= 0 vai pro cemiterio
                dead = []
                for c in player.creatures_on_board:
                    if c.effective_toughness <= 0:
                        dead.append(c)

                for c in dead:
                    player.battlefield.remove(c)
                    c.current_power = -1
                    c.current_toughness = -1
                    player.graveyard.append(c)
                    self.state.log(f"  SBA: {c.name} foi destruida (toughness 0)")
                    changed = True

                # Vida <= 0 e tratado pelo is_game_over, nao aqui

                # Criatura com dano letal (marcado >= toughness)
                # Simplificado: usamos power/toughness direto

    def _has_indestructible(self, card: Card) -> bool:
        return card.has_keyword(Keyword.INDESTRUCTIBLE)

    # ─────────────────────────────────────────
    # Fases do Turno
    # ─────────────────────────────────────────

    def execute_turn(self, ai_controller=None):
        """Executa um turno completo."""
        s = self.state
        active = s.active_player
        inactive = s.non_active_player

        if s.is_game_over:
            return

        s.log(f"--- Turno {s.turn_number} - {active.name} ---")

        # 1. BEGINNING PHASE
        self._untap_step(active)
        self._upkeep_step(active)
        self._draw_step(active)

        if s.is_game_over:
            return

        # 2. PRECOMBAT MAIN PHASE
        s.phase = "precombat_main"
        if ai_controller:
            ai_controller.main_phase(active, inactive, s)
        if s.is_game_over:
            return

        # 3. COMBAT PHASE
        self._combat_phase(active, inactive, ai_controller)
        if s.is_game_over:
            return

        # 4. POSTCOMBAT MAIN PHASE
        s.phase = "postcombat_main"
        if ai_controller:
            ai_controller.main_phase(active, inactive, s)
        if s.is_game_over:
            return

        # 5. ENDING PHASE
        self._end_step(active)
        self._cleanup_step(active)

        # Fim do turno
        active.end_of_turn_cleanup()
        s.switch_active_player()
        s.turn_number += 1

    def _untap_step(self, player: PlayerState):
        """Fase de desvirar."""
        self.state.phase = "untap"
        player.untap_all()
        # Resetar pools de mana
        player.mana_pool = {}

    def _upkeep_step(self, player: PlayerState):
        """Fase de manutenção."""
        self.state.phase = "upkeep"
        # Triggers de upkeep seriam resolvidos aqui

    def _draw_step(self, player: PlayerState):
        """Fase de compra."""
        self.state.phase = "draw"
        if self.state.turn_number > 1 or self.state.active_player_index == 1:
            # Jogador que começa não compra no primeiro turno
            if self.state.turn_number == 1 and self.state.active_player_index == 0:
                return
            drawn = player.draw_cards(1)
            if drawn:
                self.state.log(f"  {player.name} comprou uma carta")
            else:
                self.state.log(f"  {player.name} não tem cartas para comprar!")

    # ─────────────────────────────────────────
    # Fase de Combate
    # ─────────────────────────────────────────

    def _combat_phase(self, attacker: PlayerState, defender: PlayerState,
                      ai_controller=None):
        """Executa a fase de combate completa."""
        s = self.state
        s.phase = "combat_begin"

        attackers = []
        blockers = []

        # Declare Attackers
        s.phase = "declare_attackers"
        if ai_controller:
            attackers = ai_controller.declare_attackers(attacker, defender, s)

        if not attackers:
            # Pula combate se não há atacantes
            s.phase = "combat_end"
            return

        atk_names = ", ".join([c.name for c in attackers])
        s.log(f"  [ATK] {attacker.name} ataca com: {atk_names}")

        # Declare Blockers
        s.phase = "declare_blockers"
        if ai_controller:
            blockers = ai_controller.declare_blockers(defender, attacker, attackers, s)

        if blockers:
            blk_names = ", ".join([f"{b[1].name}->{b[0].name}" for b in blockers])
            s.log(f"  [DEF] {defender.name} bloqueia: {blk_names}")

        # First Strike Damage Step
        has_first_strike_atk = any(c.has_keyword(Keyword.FIRST_STRIKE) or
                                   c.has_keyword(Keyword.DOUBLE_STRIKE)
                                   for c in attackers)
        has_first_strike_blk = any(c.has_keyword(Keyword.FIRST_STRIKE) or
                                   c.has_keyword(Keyword.DOUBLE_STRIKE)
                                   for _, c in blockers)

        if has_first_strike_atk or has_first_strike_blk:
            s.phase = "first_strike_damage"
            self._combat_damage_step(attacker, defender, attackers, blockers,
                                     first_strike_only=True)
            self.check_state_based_actions()

        # Regular Damage Step
        s.phase = "damage"
        self._combat_damage_step(attacker, defender, attackers, blockers,
                                 first_strike_only=False)
        self.check_state_based_actions()

        # End of combat
        s.phase = "combat_end"
        # Reset attack flags
        for c in attackers:
            if not c.has_keyword(Keyword.VIGILANCE):
                c.tapped = True
            c.has_attacked = True

    def _combat_damage_step(self, attacker: PlayerState, defender: PlayerState,
                            attackers: list, blockers: list,
                            first_strike_only: bool = False):
        """Resolve dano de combate."""
        # Mapeia bloqueadores para cada atacante (usa id() pois Card nao e hashable)
        block_map = {}
        for target, blocker in blockers:
            tid = id(target)
            if tid not in block_map:
                block_map[tid] = []
            block_map[tid].append(blocker)

        # Dano de atacantes nao-bloqueados -> jogador defensor
        for atk_creature in attackers:
            if first_strike_only:
                if not (atk_creature.has_keyword(Keyword.FIRST_STRIKE) or
                        atk_creature.has_keyword(Keyword.DOUBLE_STRIKE)):
                    continue

            if id(atk_creature) not in block_map:
                # Dano direto ao jogador
                dmg = atk_creature.effective_power
                defender.life -= dmg
                attacker.damage_dealt += dmg
                self.state.log(
                    f"  [DMG] {atk_creature.name} causa {dmg} dano a {defender.name}"
                    f" ({defender.name}: {defender.life} vida)"
                )
                # Lifelink
                if atk_creature.has_keyword(Keyword.LIFELINK):
                    attacker.life += dmg
                    attacker.life_gained += dmg
                    self.state.log(f"  [HEAL] {attacker.name} ganha {dmg} vida (Lifelink)")
            else:
                # Criatura está sendo bloqueada
                blks = block_map[id(atk_creature)]
                total_blocker_power = sum(b.effective_power for b in blks)

                # Atacante dá dano aos bloqueadores
                atk_dmg = atk_creature.effective_power
                remaining_dmg = atk_dmg

                for blk in blks:
                    if atk_creature.has_keyword(Keyword.DEATHTOUCH):
                        # Deathtouch: 1 dano é letal
                        blk.current_power = blk.effective_power
                        blk.current_toughness = -999  # marca como morto
                        self.state.log(
                            f"  [DEATH] {atk_creature.name} (Deathtouch) destrói {blk.name}"
                        )
                        remaining_dmg = 0
                        break
                    else:
                        dmg_to_blk = min(remaining_dmg, blk.effective_toughness)
                        blk.current_toughness = blk.effective_toughness - dmg_to_blk
                        remaining_dmg -= dmg_to_blk
                        self.state.log(
                            f"  [COMBAT] {atk_creature.name} dá {dmg_to_blk} dano a {blk.name}"
                        )

                    if remaining_dmg <= 0:
                        break

                # Trample: dano excedente vai ao jogador
                if atk_creature.has_keyword(Keyword.TRAMPLE) and remaining_dmg > 0:
                    defender.life -= remaining_dmg
                    attacker.damage_dealt += remaining_dmg
                    self.state.log(
                        f"  [DMG] Trample! {remaining_dmg} dano excedente a {defender.name}"
                    )

                # Lifelink
                if atk_creature.has_keyword(Keyword.LIFELINK):
                    life_gain = min(atk_dmg, atk_creature.effective_power)
                    attacker.life += life_gain
                    attacker.life_gained += life_gain

                # Bloqueadores dão dano de volta ao atacante
                for blk in blks:
                    if first_strike_only:
                        if not (blk.has_keyword(Keyword.FIRST_STRIKE) or
                                blk.has_keyword(Keyword.DOUBLE_STRIKE)):
                            continue

                    blk_dmg = blk.effective_power

                    if blk.has_keyword(Keyword.DEATHTOUCH):
                        atk_creature.current_toughness = -999
                        self.state.log(
                            f"  [DEATH] {blk.name} (Deathtouch) destrói {atk_creature.name}"
                        )
                    else:
                        atk_creature.current_toughness = (
                            atk_creature.effective_toughness - blk_dmg
                        )
                        self.state.log(
                            f"  [COMBAT] {blk.name} dá {blk_dmg} dano a {atk_creature.name}"
                        )

                    if blk.has_keyword(Keyword.LIFELINK):
                        defender.life += blk_dmg
                        defender.life_gained += blk_dmg

    # ─────────────────────────────────────────
    # Resolução de Magias
    # ─────────────────────────────────────────

    def resolve_spell(self, card: Card, caster: PlayerState,
                      target_player: Optional[PlayerState] = None,
                      target_creature: Optional[Card] = None):
        """Resolve uma magia conjurada."""
        s = self.state
        s.log(f"  [SPELL] {caster.name} conjura {card.name} {card.mana_cost}")
        caster.spells_cast += 1

        for effect in card.effects:
            self._resolve_effect(effect, card, caster, target_player, target_creature)

        # Coloca a carta no cemitério (exceto se for permanente que entra em campo)
        if card.card_type in (card.card_type.INSTANT, card.card_type.SORCERY):
            if card in caster.hand:
                caster.hand.remove(card)
            caster.graveyard.append(card)

        self.check_state_based_actions()

    def _resolve_effect(self, effect: SpellEffect, card: Card,
                        caster: PlayerState,
                        target_player: Optional[PlayerState],
                        target_creature: Optional[Card]):
        """Resolve um efeito individual."""
        s = self.state
        opponent = s.player2 if caster is s.player1 else s.player1

        if effect.effect_type == EffectType.DAMAGE:
            if effect.target_type == TargetType.PLAYER:
                target = target_player or opponent
                target.life -= effect.value
                caster.damage_dealt += effect.value
                s.log(f"  [DMG] {card.name}: {effect.value} dano a {target.name} "
                      f"({target.name}: {target.life} vida)")
            elif effect.target_type == TargetType.CREATURE:
                if target_creature:
                    target_creature.current_toughness = (
                        target_creature.effective_toughness - effect.value
                    )
                    s.log(f"  [DMG] {card.name}: {effect.value} dano a {target_creature.name}")
                else:
                    # Dano ao jogador oponente se sem criatura alvo
                    target = target_player or opponent
                    target.life -= effect.value
                    caster.damage_dealt += effect.value
                    s.log(f"  [DMG] {card.name}: {effect.value} dano a {target.name}")
            else:  # ANY
                # Prioriza criatura, senão jogador
                if target_creature:
                    target_creature.current_toughness = (
                        target_creature.effective_toughness - effect.value
                    )
                    s.log(f"  [DMG] {card.name}: {effect.value} dano a {target_creature.name}")
                else:
                    target = target_player or opponent
                    target.life -= effect.value
                    caster.damage_dealt += effect.value
                    s.log(f"  [DMG] {card.name}: {effect.value} dano a {target.name}")

        elif effect.effect_type == EffectType.GAIN_LIFE:
            target = target_player or caster
            target.life += effect.value
            caster.life_gained += effect.value
            s.log(f"  [HEAL] {card.name}: {target.name} ganha {effect.value} vida "
                  f"({target.name}: {target.life} vida)")

        elif effect.effect_type == EffectType.DESTROY_CREATURE:
            if target_creature and not self._has_indestructible(target_creature):
                owner = caster if target_creature in caster.battlefield else opponent
                if target_creature in owner.battlefield:
                    owner.battlefield.remove(target_creature)
                    target_creature.current_power = -1
                    target_creature.current_toughness = -1
                    owner.graveyard.append(target_creature)
                    owner.creatures_lost += 1
                    s.log(f"  [DEST] {card.name}: destrói {target_creature.name}")

        elif effect.effect_type == EffectType.EXILE:
            if target_creature:
                owner = caster if target_creature in caster.battlefield else opponent
                if target_creature in owner.battlefield:
                    owner.battlefield.remove(target_creature)
                    target_creature.current_power = -1
                    target_creature.current_toughness = -1
                    owner.exile.append(target_creature)
                    owner.creatures_lost += 1
                    s.log(f"  [EXILE] {card.name}: exila {target_creature.name}")
                    # Ganha vida igual ao poder (Swords to Plowshares)
                    if len(card.effects) > 1:
                        life_gain = target_creature.power
                        caster.life += life_gain
                        caster.life_gained += life_gain
                        s.log(f"  [HEAL] Ganha {life_gain} vida pelo poder da criatura")

        elif effect.effect_type == EffectType.DRAW_CARD:
            drawn = caster.draw_cards(effect.value)
            s.log(f"  [DRAW] {card.name}: {caster.name} compra {len(drawn)} carta(s)")

        elif effect.effect_type == EffectType.ADD_MANA:
            # Mana ramp: adiciona mana genérico ao pool
            for color in [Color.WHITE, Color.BLUE, Color.BLACK, Color.RED, Color.GREEN]:
                caster.mana_pool[color] = caster.mana_pool.get(color, 0) + effect.value
            s.log(f"  [MANA] {card.name}: adiciona {effect.value} mana de qualquer cor")

        elif effect.effect_type == EffectType.PUMP:
            if target_creature:
                target_creature.current_power = (
                    target_creature.effective_power + effect.value
                )
                target_creature.current_toughness = (
                    target_creature.effective_toughness + effect.value2
                )
                s.log(f"  [PUMP] {card.name}: {target_creature.name} recebe "
                      f"+{effect.value}/+{effect.value2}")

        elif effect.effect_type == EffectType.MILL:
            target = target_player or opponent
            milled = target.mill(effect.value)
            s.log(f"  [MILL] {card.name}: {target.name} coloca {len(milled)} carta(s) "
                  f"do topo no cemitério")

    # ─────────────────────────────────────────
    # Fase Final
    # ─────────────────────────────────────────

    def _end_step(self, player: PlayerState):
        """Fase de final."""
        self.state.phase = "end"
        # Triggers de "no final do turno" seriam resolvidos aqui

    def _cleanup_step(self, player: PlayerState):
        """Fase de limpeza."""
        self.state.phase = "cleanup"
        # Descarta até 7 cartas
        while len(player.hand) > 7:
            discarded = player.discard_random()
            if discarded:
                self.state.log(f"  [DISCARD] {player.name} descarta {discarded.name}")

    # ─────────────────────────────────────────
    # Jogo de Terrenos
    # ─────────────────────────────────────────

    def play_land(self, player: PlayerState, land: Card):
        """Joga um terreno da mão."""
        if player.lands_played >= 1:
            return False
        if not land.is_land:
            return False

        player.hand.remove(land)
        land.tapped = False
        land.summoning_sick = False
        player.battlefield.append(land)
        player.lands_played += 1
        self.state.log(f"  [LAND] {player.name} joga {land.name}")
        return True

    def tap_land_for_mana(self, player: PlayerState, land: Card) -> Optional[Color]:
        """Vira um terreno para produzir mana."""
        if land.tapped or not land.is_land:
            return None
        land.tapped = True
        color = next(iter(land.land_mana))
        player.mana_pool[color] = player.mana_pool.get(color, 0) + 1
        return color
