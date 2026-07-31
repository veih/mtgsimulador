"""
MTG Match Simulator - Sistema de Efeitos Inteligente
Parseia o texto das cartas e executa efeitos automaticamente.
"""

import re
from typing import Optional, List, Tuple
from .card import Card, EffectType, SpellEffect, TargetType, Color, Keyword
from .game_state import GameState, PlayerState


class CardEffectParser:
    """Parseia o texto de uma carta e gera efeitos."""
    
    @staticmethod
    def parse_card_text(card: Card) -> List[SpellEffect]:
        """Parseia o texto da carta e retorna lista de efeitos."""
        effects = []
        text = card.text.lower()
        
        # Dano
        dmg_match = re.search(r'deals?\s+(\d+)\s+damage', text)
        if dmg_match:
            dmg = int(dmg_match.group(1))
            if 'any target' in text or 'target creature or player' in text:
                effects.append(SpellEffect(EffectType.DAMAGE, dmg, target_type=TargetType.CREATURE_OR_PLAYER))
            elif 'target player' in text or 'target opponent' in text:
                effects.append(SpellEffect(EffectType.DAMAGE, dmg, target_type=TargetType.PLAYER))
            elif 'target creature' in text:
                effects.append(SpellEffect(EffectType.DAMAGE, dmg, target_type=TargetType.CREATURE))
            else:
                effects.append(SpellEffect(EffectType.DAMAGE, dmg, target_type=TargetType.CREATURE_OR_PLAYER))
        
        # Comprar cartas
        draw_match = re.search(r'draw\s+(\d+)\s+card', text)
        if draw_match:
            effects.append(SpellEffect(EffectType.DRAW_CARD, int(draw_match.group(1))))
        
        # Ganhar vida
        life_match = re.search(r'gain\s+(\d+)\s+life', text)
        if life_match:
            effects.append(SpellEffect(EffectType.GAIN_LIFE, int(life_match.group(1))))
        
        # Destruir criatura
        if 'destroy target creature' in text:
            effects.append(SpellEffect(EffectType.DESTROY_CREATURE, target_type=TargetType.CREATURE))
        
        # Exilar criatura
        if 'exile target creature' in text:
            effects.append(SpellEffect(EffectType.EXILE, target_type=TargetType.CREATURE))
        
        # +X/+Y (pump)
        pump_match = re.search(r'\+?(\d+)/\+?(\d+)', text)
        if pump_match and ('gets' in text or 'target creature gets' in text):
            effects.append(SpellEffect(EffectType.PUMP, int(pump_match.group(1)), int(pump_match.group(2))))
        
        # Mill
        mill_match = re.search(r'mill\s+(\d+)', text)
        if mill_match:
            effects.append(SpellEffect(EffectType.MILL, int(mill_match.group(1))))
        
        # Adicionar mana
        if 'add' in text and 'mana' in text:
            effects.append(SpellEffect(EffectType.ADD_MANA, 1))
        
        return effects


class AdvancedEffects:
    """Efeitos avançados para cartas específicas."""
    
    @staticmethod
    def resolve_ad_nauseam(card: Card, caster: PlayerState, state: GameState):
        """
        Ad Nauseam: Exile cards from the top of your library until you exile 
        a nonland card. You lose life equal to that card's mana value. 
        Put that card into your hand.
        """
        state.log(f"  [AD NAUSEAM] {caster.name} conjura Ad Nauseam")
        
        nonland_found = False
        total_cmc = 0
        exiled_cards = []
        
        while not nonland_found and len(caster.library) > 0:
            top_card = caster.library.pop(0)
            exiled_cards.append(top_card)
            
            if not top_card.is_land:
                nonland_found = True
                total_cmc = top_card.mana_value
                state.log(f"    Exilou {top_card.name} (CMC {total_cmc})")
            else:
                state.log(f"    Exilou {top_card.name} (terreno)")
        
        # Perde vida igual ao CMC
        caster.life -= total_cmc
        state.log(f"    {caster.name} perde {total_cmc} vida ({caster.life} vida)")
        
        # Coloca a carta não-terreno na mão
        if exiled_cards:
            nonland_card = exiled_cards[-1]
            caster.hand.append(nonland_card)
            state.log(f"    {caster.name} coloca {nonland_card.name} na mão")
        
        # Ad Nauseam vai para o exílio após resolver
        if card in caster.hand:
            caster.hand.remove(card)
        caster.exile.append(card)
    
    @staticmethod
    def resolve_angels_grace(card: Card, caster: PlayerState, state: GameState):
        """
        Angel's Grace: You can't lose the game this turn and your opponents 
        can't win the game this turn.
        """
        state.log(f"  [ANGEL'S GRACE] {caster.name} conjura Angel's Grace")
        caster.cant_lose_game_this_turn = True
        state.log(f"    {caster.name} não pode perder o jogo neste turno")
        
        # Angel's Grace vai para o exílio após resolver
        if card in caster.hand:
            caster.hand.remove(card)
        caster.exile.append(card)
    
    @staticmethod
    def resolve_phyrexian_unlife(card: Card, caster: PlayerState, state: GameState):
        """
        Phyrexian Unlife: As long as you have no life, you don't lose the game 
        and creatures you control have protection from all colors.
        """
        state.log(f"  [PHYREXIAN UNLIFE] {caster.name} conjura Phyrexian Unlife")
        
        # Coloca no campo de batalha (é um enchantment)
        if card in caster.hand:
            caster.hand.remove(card)
        caster.battlefield.append(card)
        caster.has_phyrexian_unlife = True
        state.log(f"    {caster.name} tem Phyrexian Unlife em campo")
    
    @staticmethod
    def resolve_thassas_oracle(card: Card, caster: PlayerState, state: GameState):
        """
        Thassa's Oracle: When Thassa's Oracle enters, look at the top X cards 
        of your library, where X is your devotion to blue. Put up to one of them 
        into your hand, then shuffle the rest into your library.
        
        WIN CONDITION: If your devotion to blue is 20 or greater, you win the game.
        """
        state.log(f"  [THASSA'S ORACLE] {caster.name} conjura Thassa's Oracle")
        
        # Calcula devoção a azul
        devotion = 0
        for permanent in caster.battlefield:
            if permanent.mana_cost.blue > 0:
                devotion += permanent.mana_cost.blue
        
        state.log(f"    Devoção a azul: {devotion}")
        
        # Condição de vitória
        if devotion >= 20:
            state.log(f"    ⚡ {caster.name} VENCE O JOGO com Thassa's Oracle! ⚡")
            state.winner = caster
            state.is_game_over = True
            return
        
        # Coloca Thassa's Oracle em campo
        if card in caster.hand:
            caster.hand.remove(card)
        card.tapped = False
        card.summoning_sick = True
        caster.battlefield.append(card)
        state.log(f"    Thassa's Oracle entra em campo")
    
    @staticmethod
    def resolve_preordain(card: Card, caster: PlayerState, state: GameState):
        """
        Preordain: Scry 2, then draw a card.
        """
        state.log(f"  [PREORDAIN] {caster.name} conjura Preordain")
        
        # Scry 2 (olha as 2 cartas do topo, decide se coloca no fundo)
        # Simplificado: apenas compra uma carta
        drawn = caster.draw_cards(1)
        if drawn:
            state.log(f"    {caster.name} comprou {drawn[0].name}")
        
        # Preordain vai para o cemitério
        if card in caster.hand:
            caster.hand.remove(card)
        caster.graveyard.append(card)
    
    @staticmethod
    def resolve_profane_tutor(card: Card, caster: PlayerState, state: GameState):
        """
        Profane Tutor: Search your library for a card, put it into your hand, 
        then shuffle. You lose 2 life.
        """
        state.log(f"  [PROFANE TUTOR] {caster.name} conjura Profane Tutor")
        
        # Busca a carta de maior CMC na biblioteca
        if len(caster.library) > 0:
            best_card = max(caster.library, key=lambda c: c.mana_value)
            caster.library.remove(best_card)
            caster.hand.append(best_card)
            state.log(f"    Buscou {best_card.name}")
        
        # Perde 2 de vida
        caster.life -= 2
        state.log(f"    Perde 2 vida ({caster.life} vida)")
        
        # Profane Tutor vai para o cemitério
        if card in caster.hand:
            caster.hand.remove(card)
        caster.graveyard.append(card)
    
    @staticmethod
    def resolve_lotus_bloom(card: Card, caster: PlayerState, state: GameState):
        """
        Lotus Bloom: Suspend 3—{0}. When Lotus Bloom enters, sacrifice it.
        Simplified: Add 3 mana of any color.
        """
        state.log(f"  [LOTUS BLOOM] {caster.name} conjura Lotus Bloom")
        
        # Adiciona 3 mana de qualquer cor
        for color in [Color.WHITE, Color.BLUE, Color.BLACK, Color.RED, Color.GREEN]:
            caster.mana_pool[color] = caster.mana_pool.get(color, 0) + 3
        
        state.log(f"    Adiciona 3 mana de qualquer cor")
        
        # Lotus Bloom vai para o exílio após resolver
        if card in caster.hand:
            caster.hand.remove(card)
        caster.exile.append(card)
    
    @staticmethod
    def resolve_pact_of_negation(card: Card, caster: PlayerState, state: GameState):
        """
        Pact of Negation: Counter target spell. At the beginning of your next upkeep, 
        pay {3}{U}{U}. If you don't, you lose the game.
        Simplified: Counter target spell.
        """
        state.log(f"  [PACT OF NEGATION] {caster.name} conjura Pact of Negation")
        state.log(f"    Contra-magia alvo")
        
        # Pact vai para o exílio após resolver
        if card in caster.hand:
            caster.hand.remove(card)
        caster.exile.append(card)
    
    @staticmethod
    def resolve_force_of_negation(card: Card, caster: PlayerState, state: GameState):
        """
        Force of Negation: Counter target spell. If you cast this spell without paying 
        its mana cost, exile a blue card from your hand.
        Simplified: Counter target spell.
        """
        state.log(f"  [FORCE OF NEGATION] {caster.name} conjura Force of Negation")
        state.log(f"    Contra-magia alvo")
        
        # Force vai para o exílio após resolver
        if card in caster.hand:
            caster.hand.remove(card)
        caster.exile.append(card)
    
    @staticmethod
    def resolve_path_to_exile(card: Card, caster: PlayerState, state: GameState, target_creature: Card = None):
        """
        Path to Exile: Exile target creature. Its controller may search their library 
        for a basic land card and put it onto the battlefield tapped.
        """
        state.log(f"  [PATH TO EXILE] {caster.name} conjura Path to Exile")
        
        if target_creature:
            # Exila a criatura
            owner = caster if target_creature in caster.battlefield else state.player2 if target_creature in state.player2.battlefield else None
            if owner:
                owner.battlefield.remove(target_creature)
                owner.exile.append(target_creature)
                state.log(f"    Exila {target_creature.name}")
                
                # Oponente busca terreno básico
                opponent = state.player2 if caster is state.player1 else state.player1
                basic_lands = [c for c in opponent.library if c.is_land and c.name in ['Plains', 'Island', 'Swamp', 'Mountain', 'Forest']]
                if basic_lands:
                    land = basic_lands[0]
                    opponent.library.remove(land)
                    land.tapped = True
                    opponent.battlefield.append(land)
                    state.log(f"    {opponent.name} busca {land.name} (virado)")
        
        # Path vai para o exílio após resolver
        if card in caster.hand:
            caster.hand.remove(card)
        caster.exile.append(card)
    
    @staticmethod
    def resolve_sleight_of_hand(card: Card, caster: PlayerState, state: GameState):
        """
        Sleight of Hand: Look at the top two cards of your library. Put one into your 
        hand and the other on the bottom.
        Simplified: Draw a card.
        """
        state.log(f"  [SLEIGHT OF HAND] {caster.name} conjura Sleight of Hand")
        
        drawn = caster.draw_cards(1)
        if drawn:
            state.log(f"    Comprou {drawn[0].name}")
        
        # Sleight vai para o cemitério
        if card in caster.hand:
            caster.hand.remove(card)
        caster.graveyard.append(card)
    
    @staticmethod
    def resolve_spoils_of_the_vault(card: Card, caster: PlayerState, state: GameState):
        """
        Spoils of the Vault: Exile the top card of your library. You gain life equal 
        to its mana value. Draw a card.
        """
        state.log(f"  [SPOILS OF THE VAULT] {caster.name} conjura Spoils of the Vault")
        
        if len(caster.library) > 0:
            top_card = caster.library.pop(0)
            caster.exile.append(top_card)
            cmc = top_card.mana_value
            caster.life += cmc
            state.log(f"    Exilou {top_card.name} (CMC {cmc}), ganha {cmc} vida")
        
        drawn = caster.draw_cards(1)
        if drawn:
            state.log(f"    Comprou {drawn[0].name}")
        
        # Spoils vai para o cemitério
        if card in caster.hand:
            caster.hand.remove(card)
        caster.graveyard.append(card)
