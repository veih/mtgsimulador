"""
MTG Match Simulator - New Rules Engine (v2)
Motor de regras completo com pipeline correto:
  Resolve -> SBA -> Replacement -> Events -> Triggers -> Stack -> Priority
"""

import random
from typing import Optional, List, Dict
from .card import Card, Keyword, EffectType, SpellEffect, TargetType, Color
from .game_state import GameState, PlayerState
from .event_bus import GameEvent, Event, EventBus
from .trigger_manager import TriggerManager, TriggeredAbility, Stack, StackItem, StackItemType
from .sba_engine import SBAEngine, PriorityEngine
from .replacement_effects import ReplacementEffectManager, ReplacementEffect, ContinuousEffectManager
from .card_abilities_db import get_card_abilities, get_effect_name


class RulesEngineV2:
    """
    Motor de regras completo com arquitetura baseada em eventos.
    
    Pipeline de resolucao:
    1. Resolve Spell/Ability
    2. State-Based Actions
    3. Replacement Effects
    4. Generate Events
    5. Collect Triggers
    6. Put Triggers on Stack
    7. Priority
    8. Resolve Stack
    9. Repeat
    """
    
    def __init__(self, state: GameState, recorder=None):
        self.state = state
        self.recorder = recorder
        
        # Sistemas
        self.event_bus = EventBus()
        self.trigger_manager = TriggerManager(self.event_bus)
        self.stack = Stack(self.event_bus)
        self.sba_engine = SBAEngine(self.event_bus)
        self.priority_engine = PriorityEngine(self.event_bus)
        self.replacement_manager = ReplacementEffectManager(self.event_bus)
        self.continuous_effects = ContinuousEffectManager()
        
        # Log detalhado
        self.game_log: List[str] = []
        
        # Registra triggers das cartas iniciais
        self._register_initial_triggers()
    
    def _log(self, message: str):
        """Adiciona ao log do jogo."""
        self.game_log.append(message)
        if self.recorder:
            self.recorder.record_frame(self.state, message)
    
    def _register_initial_triggers(self):
        """Registra triggers das cartas que ja estao no jogo."""
        pass  # Triggers sao registradas quando cartas entram em campo
    
    def _register_card_triggers(self, card: Card, controller: PlayerState):
        """
        Registra os triggered abilities de uma carta no TriggerManager.
        Chamado sempre que um permanente entra em campo.
        """
        from .modern_card_abilities import MODERN_CARD_ABILITIES
        
        # Busca pelo nome normalizado
        card_name_lower = card.name.lower()
        abilities_data = MODERN_CARD_ABILITIES.get(card_name_lower, {})
        abilities_list = abilities_data.get('abilities', []) if isinstance(abilities_data, dict) else []
        
        for ability in abilities_list:
            if ability.get('type') != 'triggered':
                continue
            
            event_type = ability.get('event')
            effect_name = ability.get('effect', '')
            if not event_type or not effect_name:
                continue
            
            # Captura variaveis para o closure
            _card = card
            _controller = controller
            _effect_name = effect_name
            
            def make_effect(c, ctrl, eff):
                def trigger_effect(event, state):
                    # So dispara se a carta ainda esta em campo (ou para ETB, logo apos entrar)
                    opponent = state.player2 if ctrl == state.player1 else state.player1
                    self._resolve_card_effect(eff, c, ctrl, opponent)
                return trigger_effect
            
            trigger = TriggeredAbility(
                card=_card,
                event_type=event_type,
                condition=lambda e, c=_card, ctrl=_controller: c in ctrl.battlefield or True,
                effect=make_effect(_card, _controller, _effect_name)
            )
            self.trigger_manager.register_trigger(trigger)
            self._log(f"  Trigger registrado: {card.name} on {event_type}")
    
    # ─────────────────────────────────────────
    # Pipeline Principal
    # ─────────────────────────────────────────
    
    def resolve_pipeline(self):
        """
        Executa o pipeline completo de resolucao.
        Chamado sempre que algo resolve ou quando um jogador recebe prioridade.
        """
        changed = True
        max_iterations = 100  # Evita loop infinito
        
        iteration = 0
        while changed and iteration < max_iterations:
            iteration += 1
            changed = False
            
            # 1. State-Based Actions
            if self.sba_engine.check_and_apply(self.state):
                self._log("SBA aplicadas")
                changed = True
                continue
            
            # 2. Verifica se jogo acabou
            if self.state.is_game_over:
                self._log(f"Jogo acabou! Vencedor: {self.state.winner}")
                return
            
            # 3. Coleta triggers pendentes
            pending = self.trigger_manager.get_pending_triggers()
            if pending:
                self._log(f"Triggers pendentes: {len(pending)}")
                self.trigger_manager.put_triggers_on_stack(self.stack)
                changed = True
                continue
            
            # 4. Se a pilha nao esta vazia, resolve o topo
            if not self.stack.is_empty():
                self._resolve_top_of_stack()
                changed = True
                continue
    
    def _resolve_top_of_stack(self):
        """Resolve o item do topo da pilha."""
        item = self.stack.pop()
        if not item:
            return
        
        self._log(f"Resolvendo: {item.description}")
        
        if item.item_type == StackItemType.TRIGGERED_ABILITY:
            if item.ability and item.ability.effect:
                item.ability.effect(item.event, self.state)
            self.event_bus.emit_simple(GameEvent.ABILITY_RESOLVED, source=item.source)
        
        elif item.item_type == StackItemType.SPELL:
            self._resolve_spell_item(item)
            self.event_bus.emit_simple(GameEvent.SPELL_RESOLVED, source=item.source)
    
    # ─────────────────────────────────────────
    # Acoes do Jogador
    # ─────────────────────────────────────────
    
    def play_land(self, player: PlayerState, card: Card) -> bool:
        """Jogador joga um terreno."""
        if player.lands_played > 0:
            self._log(f"{player.name} ja jogou um terreno neste turno")
            return False
        
        if not card.is_land:
            self._log(f"{card.name} nao e um terreno")
            return False
        
        # Remove da mao
        if card in player.hand:
            player.hand.remove(card)
        
        # Coloca em campo
        card.tapped = False
        player.battlefield.append(card)
        player.lands_played += 1
        
        # Registra triggers da carta
        self._register_card_triggers(card, player)
        
        # Adiciona mana
        for color in card.land_mana:
            player.mana_pool[color] = player.mana_pool.get(color, 0) + 1
        
        # Evento
        self.event_bus.emit_simple(
            GameEvent.PLAY_LAND,
            source=card,
            target=player,
            controller=player
        )
        self.event_bus.emit_simple(
            GameEvent.PERMANENT_ENTERS,
            source=card,
            controller=player
        )
        
        self._log(f"{player.name} jogou {card.name}")
        
        # Pipeline
        self.resolve_pipeline()
        return True
    
    def _can_pay_mana_cost(self, player: PlayerState, card: Card) -> bool:
        """
        Verifica se o jogador pode pagar o custo da carta com o mana disponivel no pool.
        Valida requisitos por cor antes do custo generico.
        """
        cmc = getattr(card, 'cmc', 0)
        if cmc == 0:
            return True
        
        colors = getattr(card, 'colors', [])
        
        # Monta requisito colorido: quantas de cada cor sao necessarias
        colored_needed: Dict = {}
        for color in colors:
            colored_needed[color] = colored_needed.get(color, 0) + 1
        
        pool = dict(player.mana_pool)
        
        # 1. Verifica e desconta mana colorido
        for color, needed in colored_needed.items():
            available = pool.get(color, 0)
            if available < needed:
                return False
            pool[color] = available - needed
        
        # 2. Verifica custo generico com o mana restante
        generic_needed = cmc - sum(colored_needed.values())
        if generic_needed > 0:
            remaining_total = sum(pool.values())
            if remaining_total < generic_needed:
                return False
        
        return True
    
    def _pay_mana_cost(self, player: PlayerState, card: Card):
        """
        Deduz o custo de mana do pool do jogador.
        Assume que _can_pay_mana_cost ja foi verificado.
        """
        cmc = getattr(card, 'cmc', 0)
        colors = getattr(card, 'colors', [])
        
        # Desconta mana colorido primeiro
        colored_needed: Dict = {}
        for color in colors:
            colored_needed[color] = colored_needed.get(color, 0) + 1
        
        for color, needed in colored_needed.items():
            player.mana_pool[color] = player.mana_pool.get(color, 0) - needed
            if player.mana_pool[color] <= 0:
                del player.mana_pool[color]
        
        # Desconta custo generico com qualquer mana restante
        generic_needed = cmc - sum(colored_needed.values())
        for color in list(player.mana_pool.keys()):
            if generic_needed <= 0:
                break
            pay = min(player.mana_pool[color], generic_needed)
            player.mana_pool[color] -= pay
            generic_needed -= pay
            if player.mana_pool[color] <= 0:
                del player.mana_pool[color]
    
    def cast_spell(self, player: PlayerState, card: Card, targets: list = None) -> bool:
        """Jogador conjura uma magia."""
        if card not in player.hand:
            return False
        
        # Verifica custo de mana por cor
        if not self._can_pay_mana_cost(player, card):
            cmc = getattr(card, 'cmc', 0)
            total_mana = sum(player.mana_pool.values())
            self._log(f"Mana insuficiente para {card.name} (precisa {cmc}, tem {total_mana})")
            return False
        
        # Paga mana respeitando cores
        self._pay_mana_cost(player, card)
        
        # Remove da mao
        player.hand.remove(card)
        
        # Evento de conjuracao
        self.event_bus.emit_simple(
            GameEvent.CAST_SPELL,
            source=card,
            controller=player
        )
        
        # Coloca na pilha
        stack_item = StackItem(
            item_type=StackItemType.SPELL,
            source=card,
            controller=player,
            targets=targets or [],
            description=card.name
        )
        self.stack.push(stack_item)
        
        self._log(f"{player.name} conjurou {card.name}")
        
        # Pipeline
        self.resolve_pipeline()
        return True
    
    def suspend_card(self, player: PlayerState, card: Card, time_counters: int = 3, cost: int = 0) -> bool:
        """
        Suspende uma carta da mao.
        Exila a carta com marcadores de tempo.
        A cada upkeep, remove 1 marcador.
        Quando chega a 0, conjura sem pagar o custo.
        """
        if card not in player.hand:
            self._log(f"{card.name} nao esta na mao de {player.name}")
            return False
        
        # Verifica se a carta tem Suspend
        from .modern_card_abilities import get_card_abilities
        abilities = get_card_abilities(card.name)
        has_suspend = False
        for ability in abilities.get("abilities", []):
            if ability.get("type") == "special_action" and "suspend" in ability.get("effect", ""):
                has_suspend = True
                time_counters = ability.get("params", {}).get("time_counters", 3)
                cost = ability.get("params", {}).get("cost", 0)
                break
        
        if not has_suspend:
            self._log(f"{card.name} nao tem Suspend")
            return False
        
        # Paga o custo de Suspend (geralmente 0)
        if cost > 0:
            total_mana = sum(player.mana_pool.values())
            if total_mana < cost:
                self._log(f"Mana insuficiente para Suspend {card.name} (precisa {cost}, tem {total_mana})")
                return False
            
            # Paga mana
            remaining = cost
            for color in list(player.mana_pool.keys()):
                if remaining <= 0:
                    break
                pay = min(player.mana_pool[color], remaining)
                player.mana_pool[color] -= pay
                remaining -= pay
                if player.mana_pool[color] == 0:
                    del player.mana_pool[color]
        
        # Remove da mao
        player.hand.remove(card)
        
        # Adiciona marcadores de tempo
        card.time_counters = time_counters
        card.suspended = True
        
        # Exila a carta
        player.exile.append(card)
        
        # Registra trigger de upkeep para remover marcadores
        self._register_suspend_trigger(card, player)
        
        self._log(f"{player.name} suspendeu {card.name} com {time_counters} marcadores de tempo")
        
        # Pipeline
        self.resolve_pipeline()
        return True
    
    def _register_suspend_trigger(self, card: Card, player: PlayerState):
        """Registra o trigger de upkeep para remover marcadores de Suspend."""
        def remove_counter(event, state):
            if card.time_counters > 0:
                card.time_counters -= 1
                self._log(f"  Remove 1 marcador de {card.name} (restam {card.time_counters})")
                
                # Se chegou a 0, conjura sem pagar o custo
                if card.time_counters == 0:
                    self._cast_from_suspend(card, player)
        
        # Cria trigger
        trigger = TriggeredAbility(
            card=card,
            event_type=GameEvent.UPKEEP,
            condition=lambda e: card in player.exile and card.time_counters > 0,
            effect=remove_counter
        )
        
        # Registra no trigger manager
        self.trigger_manager.register_trigger(trigger)
        self._log(f"  Registrado trigger de upkeep para {card.name}")
    
    def _cast_from_suspend(self, card: Card, player: PlayerState):
        """Conjura uma carta do exilio quando seus marcadores de Suspend chegam a 0."""
        self._log(f"  Ultimo marcador removido! Conjura {card.name} sem pagar o custo")
        
        # Remove do exilio
        if card in player.exile:
            player.exile.remove(card)
        
        # Remove atributos de Suspend
        card.suspended = False
        card.time_counters = 0
        
        # Conjura sem pagar o custo (coloca em campo se for permanente, ou resolve se for magia)
        if card.is_creature or card.is_land or card.type in ['artifact', 'enchantment', 'planeswalker']:
            # Entra no campo
            card.tapped = False
            if card.is_creature:
                card.summoning_sick = True
            player.battlefield.append(card)
            # Registra triggers do permanente
            self._register_card_triggers(card, player)
            
            self.event_bus.emit_simple(
                GameEvent.PERMANENT_ENTERS,
                source=card,
                controller=player
            )
            self._log(f"  {card.name} entrou no campo de batalha")
        else:
            # Magia instantanea ou feiticaro - resolve o efeito
            self._resolve_spell_from_suspend(card, player)
    
    def _resolve_spell_from_suspend(self, card: Card, player: PlayerState):
        """Resolve o efeito de uma magia conjurada do Suspend."""
        opponent = self.state.player2 if player == self.state.player1 else self.state.player1
        effect_name = get_effect_name(card.name)
        
        if effect_name:
            self._resolve_card_effect(effect_name, card, player, opponent)
        
        # Vai para o cemiterio
        player.graveyard.append(card)
        self._log(f"  {card.name} foi para o cemiterio")
    
    def process_upkeep(self, player: PlayerState):
        """Processa a fase de upkeep do jogador."""
        self._log(f"--- Upkeep de {player.name} ---")
        
        # Emite evento de upkeep
        self.event_bus.emit_simple(GameEvent.UPKEEP, controller=player)
        
        # Pipeline para processar triggers
        self.resolve_pipeline()
    
    def _resolve_spell_item(self, item: StackItem):
        """Resolve uma magia da pilha."""
        card = item.source
        player = item.controller
        opponent = self.state.player2 if player == self.state.player1 else self.state.player1
        
        # Verifica habilidades especiais
        effect_name = get_effect_name(card.name)
        
        if effect_name:
            self._resolve_card_effect(effect_name, card, player, opponent)
        else:
            # Efeitos genericos baseados no tipo
            if card.is_creature:
                card.tapped = False
                card.summoning_sick = True
                player.battlefield.append(card)
                # Registra triggers ETB da criatura
                self._register_card_triggers(card, player)
                self.event_bus.emit_simple(
                    GameEvent.PERMANENT_ENTERS,
                    source=card,
                    controller=player
                )
                self._log(f"{card.name} entrou no campo de batalha")
            else:
                # Magia nao-criatura vai para o cemiterio
                player.graveyard.append(card)
    
    def _resolve_card_effect(self, effect_name: str, card: Card, player: PlayerState, opponent: PlayerState):
        """Resolve o efeito de uma carta usando o banco de dados."""
        self._log(f"  Resolvendo efeito: {effect_name}")
        
        if effect_name == "ad_nauseam_effect":
            self._resolve_ad_nauseam(player)
        
        elif effect_name == "angels_grace_effect":
            player.cant_lose_game_this_turn = True
            self._log(f"  {player.name} nao pode perder o jogo neste turno")
        
        elif effect_name == "phyrexian_unlife_effect":
            player.has_phyrexian_unlife = True
            card.tapped = False
            player.battlefield.append(card)
            self.event_bus.emit_simple(GameEvent.PERMANENT_ENTERS, source=card, controller=player)
            self._log(f"  Phyrexian Unlife entrou no campo")
        
        elif effect_name == "thassas_oracle_etb":
            card.tapped = False
            card.summoning_sick = True
            player.battlefield.append(card)
            self.event_bus.emit_simple(GameEvent.PERMANENT_ENTERS, source=card, controller=player)
            # Verifica devocao
            blue_devotion = sum(1 for c in player.battlefield if hasattr(c, 'colors') and Color.BLUE in getattr(c, 'colors', []))
            self._log(f"  Devocao a azul: {blue_devotion}")
            if blue_devotion >= 20:
                self.state.winner = 1 if player == self.state.player1 else 2
                self._log(f"  {player.name} ganha o jogo!")
        
        elif effect_name == "preordain_effect":
            # Scry 2 + draw 1
            if len(player.library) >= 2:
                top = player.library[:2]
                player.library = player.library[2:]
                # Simplificado: coloca a primeira de volta
                player.library.insert(0, top[1])
                player.hand.append(top[0])
                self.event_bus.emit_simple(GameEvent.CARD_DRAWN, source=player)
            self._log(f"  Preordain: scry 2, draw 1")
        
        elif effect_name == "profane_tutor_effect":
            # Busca a carta de maior CMC na biblioteca
            if player.library:
                best = max(player.library, key=lambda c: getattr(c, 'cmc', 0))
                player.library.remove(best)
                player.hand.append(best)
                player.life -= 2
                self.event_bus.emit_simple(GameEvent.LIFE_LOST, source=player, data={'amount': 2})
                self._log(f"  Profane Tutor: buscou {best.name}, perdeu 2 vida")
        
        elif effect_name == "lotus_bloom_mana":
            # Adiciona 3 mana de qualquer cor
            for _ in range(3):
                player.mana_pool[Color.COLORLESS] = player.mana_pool.get(Color.COLORLESS, 0) + 1
            self._log(f"  Lotus Bloom: +3 mana")
        
        elif effect_name == "pact_of_negation_effect" or effect_name == "force_of_negation_effect":
            # Contra magia do oponente
            if not self.stack.is_empty():
                countered = self.stack.pop()
                if countered:
                    self._log(f"  Contra: {countered.description}")
            # Vai para o campo como permanente (simplificado)
            player.battlefield.append(card)
            self.event_bus.emit_simple(GameEvent.PERMANENT_ENTERS, source=card, controller=player)
        
        elif effect_name == "path_to_exile_effect":
            # Exile criatura do oponente
            creatures = opponent.creatures_on_board
            if creatures:
                target = random.choice(creatures)
                opponent.battlefield.remove(target)
                opponent.exile.append(target)
                self.event_bus.emit_simple(GameEvent.CREATURE_DIED, source=target, controller=opponent)
                self._log(f"  Path to Exile: exilou {target.name}")
        
        elif effect_name == "sleight_of_hand_effect":
            if player.library:
                drawn = player.library.pop(0)
                player.hand.append(drawn)
                self.event_bus.emit_simple(GameEvent.CARD_DRAWN, source=player)
                self._log(f"  Sleight of Hand: comprou {drawn.name}")
        
        elif effect_name == "spoils_of_the_vault_effect":
            # Exile ate achar terreno
            cmc_total = 0
            while player.library:
                exiled = player.library.pop(0)
                player.exile.append(exiled)
                cmc_total += getattr(exiled, 'cmc', 0)
                if exiled.is_land:
                    exiled.tapped = True
                    player.battlefield.append(exiled)
                    break
            player.life += cmc_total
            self.event_bus.emit_simple(GameEvent.LIFE_GAINED, source=player, data={'amount': cmc_total})
            if player.library:
                drawn = player.library.pop(0)
                player.hand.append(drawn)
                self.event_bus.emit_simple(GameEvent.CARD_DRAWN, source=player)
            self._log(f"  Spoils of the Vault: ganhou {cmc_total} vida")
        
        else:
            # Efeito desconhecido, vai para o cemiterio
            player.graveyard.append(card)
            self._log(f"  Efeito desconhecido: {effect_name}")
    
    def _resolve_ad_nauseam(self, player: PlayerState):
        """Resolve o efeito de Ad Nauseam."""
        self._log("  Ad Nauseam: exilando cartas...")
        total_cmc = 0
        
        while player.library:
            card = player.library.pop(0)
            player.exile.append(card)
            
            if card.is_land:
                continue  # Continua exilando
            
            # Nao-terreno encontrado
            cmc = getattr(card, 'cmc', 0)
            total_cmc += cmc
            player.hand.append(card)
            self._log(f"    Exilou {card.name} (CMC {cmc})")
            break
        
        if total_cmc > 0:
            player.life -= total_cmc
            self.event_bus.emit_simple(GameEvent.LIFE_LOST, source=player, data={'amount': total_cmc})
            self._log(f"    Perdeu {total_cmc} vida (total: {player.life})")
    
    # ─────────────────────────────────────────
    # Combate
    # ─────────────────────────────────────────
    
    def declare_attackers(self, player: PlayerState, attackers: List[Card]):
        """Declara atacantes."""
        opponent = self.state.player2 if player == self.state.player1 else self.state.player1
        
        for creature in attackers:
            if creature in player.battlefield and creature.is_creature:
                if not creature.summoning_sick and not creature.tapped:
                    creature.has_attacked = True
                    creature.tapped = True  # Atacar vira a criatura
                    self.event_bus.emit_simple(
                        GameEvent.CREATURE_ATTACKED,
                        source=creature,
                        controller=player,
                        target=opponent
                    )
                    power = getattr(creature, 'effective_power', None)
                    if power is None:
                        power = getattr(creature, 'power', 0) or 0
                    opponent.life -= power
                    self.event_bus.emit_simple(
                        GameEvent.DAMAGE_DEALT,
                        source=creature,
                        target=opponent,
                        amount=power
                    )
                    self._log(f"  {creature.name} ataca por {power}")
        
        self.resolve_pipeline()
    
    # ─────────────────────────────────────────
    # Turno
    # ─────────────────────────────────────────
    
    def execute_turn(self, ai_player=None):
        """Executa um turno completo."""
        player = self.state.active_player
        opponent = self.state.non_active_player
        
        self._log(f"\n{'='*40}")
        self._log(f"TURNO {self.state.turn_number} - {player.name}")
        self._log(f"{'='*40}")
        
        # Untap
        self._log("Fase: Untap")
        for card in player.battlefield:
            card.tapped = False
            card.summoning_sick = False
            card.has_attacked = False
        player.mana_pool = {}
        player.lands_played = 0
        
        # Upkeep
        self._log("Fase: Upkeep")
        self.event_bus.emit_simple(GameEvent.PHASE_CHANGED, data={'phase': 'upkeep'})
        
        # Draw
        self._log("Fase: Draw")
        if player.library:
            drawn = player.library.pop(0)
            player.hand.append(drawn)
            player.cards_drawn_this_turn += 1
            self.event_bus.emit_simple(GameEvent.CARD_DRAWN, source=player)
            self._log(f"  Comprou: {drawn.name}")
        else:
            self._log("  Biblioteca vazia!")
        
        # Main Phase 1
        self._log("Fase: Main")
        self.event_bus.emit_simple(GameEvent.PHASE_CHANGED, data={'phase': 'main'})
        
        # IA joga
        if ai_player:
            ai_player.take_turn(player, opponent, self)
        else:
            # Joga terreno
            for card in player.hand[:]:
                if card.is_land and player.lands_played == 0:
                    self.play_land(player, card)
                    break
            
            # Conjura magias
            for card in player.hand[:]:
                if not card.is_land:
                    total_mana = sum(player.mana_pool.values())
                    cmc = getattr(card, 'cmc', 0)
                    if cmc <= total_mana:
                        self.cast_spell(player, card)
        
        # Combat
        self._log("Fase: Combat")
        self.event_bus.emit_simple(GameEvent.PHASE_CHANGED, data={'phase': 'combat'})
        
        attackers = [c for c in player.battlefield if c.is_creature and not c.tapped and not c.summoning_sick]
        if attackers:
            self.declare_attackers(player, attackers)
        
        # Main Phase 2
        self._log("Fase: Main 2")
        
        # End Step
        self._log("Fase: End")
        player.end_of_turn_cleanup()
        
        self.event_bus.emit_simple(GameEvent.TURN_ENDED, data={'turn': self.state.turn_number})
        
        # Pipeline final
        self.resolve_pipeline()
        
        # Proximo turno
        self.state.active_player_index = 1 - self.state.active_player_index
        if self.state.active_player_index == 0:
            self.state.turn_number += 1
    
    def get_log(self) -> List[str]:
        """Retorna o log do jogo."""
        return self.game_log
