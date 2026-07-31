"""
MTG Match Simulator - Sistema Avançado de Terrenos
Parseia terrenos não-básicos e seus efeitos automaticamente.
"""

import re
from typing import Optional, List, Dict
from .card import Card, Color, Keyword, CardType, ManaCost, SpellEffect, EffectType, TargetType


class LandEffectParser:
    """Parseia efeitos de terrenos não-básicos."""
    
    @staticmethod
    def parse_land_mana(land_name: str, oracle_text: str) -> set:
        """Determina quais cores de mana um terreno produz."""
        oracle_lower = oracle_text.lower() if oracle_text else ''
        name_lower = land_name.lower()
        land_mana = set()
        
        # Terrenos básicos
        if 'plains' in name_lower:
            return {Color.WHITE}
        elif 'island' in name_lower:
            return {Color.BLUE}
        elif 'swamp' in name_lower:
            return {Color.BLACK}
        elif 'mountain' in name_lower:
            return {Color.RED}
        elif 'forest' in name_lower:
            return {Color.GREEN}
        
        # Terrenos não-básicos - parseia o texto
        # Procura por padrões como "{W}", "{U}", "{B}", "{R}", "{G}"
        if '{w}' in oracle_lower or ': add w' in oracle_lower or 'add {w}' in oracle_lower:
            land_mana.add(Color.WHITE)
        if '{u}' in oracle_lower or ': add u' in oracle_lower or 'add {u}' in oracle_lower:
            land_mana.add(Color.BLUE)
        if '{b}' in oracle_lower or ': add b' in oracle_lower or 'add {b}' in oracle_lower:
            land_mana.add(Color.BLACK)
        if '{r}' in oracle_lower or ': add r' in oracle_lower or 'add {r}' in oracle_lower:
            land_mana.add(Color.RED)
        if '{g}' in oracle_lower or ': add g' in oracle_lower or 'add {g}' in oracle_lower:
            land_mana.add(Color.GREEN)
        
        # Procura por nomes de cores no texto
        if 'white' in oracle_lower and 'mana' in oracle_lower:
            land_mana.add(Color.WHITE)
        if 'blue' in oracle_lower and 'mana' in oracle_lower:
            land_mana.add(Color.BLUE)
        if 'black' in oracle_lower and 'mana' in oracle_lower:
            land_mana.add(Color.BLACK)
        if 'red' in oracle_lower and 'mana' in oracle_lower:
            land_mana.add(Color.RED)
        if 'green' in oracle_lower and 'mana' in oracle_lower:
            land_mana.add(Color.GREEN)
        
        # Procura por padrões como "add one mana of any color"
        if 'any color' in oracle_lower or 'any type' in oracle_lower:
            land_mana = {Color.WHITE, Color.BLUE, Color.BLACK, Color.RED, Color.GREEN}
        
        # Se não encontrou nada, assume qualquer cor (mana fixer genérico)
        if not land_mana:
            land_mana = {Color.WHITE, Color.BLUE, Color.BLACK, Color.RED, Color.GREEN}
        
        return land_mana
    
    @staticmethod
    def parse_land_effects(land_name: str, oracle_text: str) -> List[SpellEffect]:
        """Parseia efeitos especiais de terrenos (ETB, tap, etc)."""
        effects = []
        oracle_lower = oracle_text.lower() if oracle_text else ''
        
        # "enters the battlefield tapped"
        if 'enters the battlefield tapped' in oracle_lower or 'etb tapped' in oracle_lower:
            # Este efeito é tratado no momento que o terreno entra em campo
            pass
        
        # "tap: add [mana]"
        if 'tap:' in oracle_lower or '{tap}:' in oracle_lower:
            # Já tratado pelo land_mana
            pass
        
        # "sacrifice" effects
        if 'sacrifice' in oracle_lower:
            # Terrenos que sacrificam para dar algum efeito
            pass
        
        return effects


class CardEffectParserAdvanced:
    """Parser avançado de efeitos de cartas."""
    
    @staticmethod
    def parse_all_effects(card_name: str, oracle_text: str, card_type: CardType) -> List[SpellEffect]:
        """Parseia todos os efeitos de uma carta."""
        effects = []
        text_lower = oracle_text.lower() if oracle_text else ''
        
        # DANO
        dmg_match = re.search(r'deals?\s+(\d+)\s+damage', text_lower)
        if dmg_match:
            dmg = int(dmg_match.group(1))
            if 'any target' in text_lower or 'target creature or player' in text_lower:
                effects.append(SpellEffect(EffectType.DAMAGE, dmg, target_type=TargetType.CREATURE_OR_PLAYER))
            elif 'target player' in text_lower or 'target opponent' in text_lower:
                effects.append(SpellEffect(EffectType.DAMAGE, dmg, target_type=TargetType.PLAYER))
            elif 'target creature' in text_lower:
                effects.append(SpellEffect(EffectType.DAMAGE, dmg, target_type=TargetType.CREATURE))
            else:
                effects.append(SpellEffect(EffectType.DAMAGE, dmg, target_type=TargetType.CREATURE_OR_PLAYER))
        
        # COMPRAR CARTAS
        draw_match = re.search(r'draw\s+(\d+)\s+card', text_lower)
        if draw_match:
            effects.append(SpellEffect(EffectType.DRAW_CARD, int(draw_match.group(1))))
        
        # GANHAR VIDA
        life_match = re.search(r'gain\s+(\d+)\s+life', text_lower)
        if life_match:
            effects.append(SpellEffect(EffectType.GAIN_LIFE, int(life_match.group(1))))
        
        # DESTRUIR CRIATURA
        if 'destroy target creature' in text_lower:
            effects.append(SpellEffect(EffectType.DESTROY_CREATURE, target_type=TargetType.CREATURE))
        
        # EXILAR CRIATURA
        if 'exile target creature' in text_lower:
            effects.append(SpellEffect(EffectType.EXILE, target_type=TargetType.CREATURE))
        
        # +X/+Y (PUMP)
        pump_match = re.search(r'gets?\s+\+?(\d+)/\+?(\d+)', text_lower)
        if pump_match:
            effects.append(SpellEffect(EffectType.PUMP, int(pump_match.group(1)), int(pump_match.group(2))))
        
        # MILL
        mill_match = re.search(r'mill\s+(\d+)', text_lower)
        if mill_match:
            effects.append(SpellEffect(EffectType.MILL, int(mill_match.group(1))))
        
        # ADICIONAR MANA
        if 'add' in text_lower and 'mana' in text_lower:
            mana_match = re.search(r'add\s+(\d+)', text_lower)
            if mana_match:
                effects.append(SpellEffect(EffectType.ADD_MANA, int(mana_match.group(1))))
            else:
                effects.append(SpellEffect(EffectType.ADD_MANA, 1))
        
        # CONTRA-MÁGICA
        if 'counter target spell' in text_lower or 'counter target' in text_lower:
            effects.append(SpellEffect(EffectType.COUNTER, target_type=TargetType.ANY))
        
        # SACRIFÍCIO
        if 'sacrifice' in text_lower and 'creature' in text_lower:
            effects.append(SpellEffect(EffectType.SACRIFICE, target_type=TargetType.CREATURE))
        
        return effects


# Dicionário de terrenos não-básicos conhecidos com suas cores de mana
KNOWN_LANDS = {
    # Dual Lands (Original)
    'tundra': {Color.WHITE, Color.BLUE},
    'underground sea': {Color.BLUE, Color.BLACK},
    'badlands': {Color.BLACK, Color.RED},
    'bayou': {Color.BLACK, Color.GREEN},
    'savannah': {Color.WHITE, Color.GREEN},
    'scrubland': {Color.WHITE, Color.BLACK},
    'tropical island': {Color.BLUE, Color.GREEN},
    'volcanic island': {Color.BLUE, Color.RED},
    'taiga': {Color.RED, Color.GREEN},
    
    # Fetch Lands
    'flooded strand': {Color.WHITE, Color.BLUE},
    'bloodstained mire': {Color.RED, Color.BLACK},
    'wooded foothills': {Color.RED, Color.GREEN},
    'polluted delta': {Color.BLUE, Color.BLACK},
    'windswept heath': {Color.WHITE, Color.GREEN},
    'marsh flats': {Color.WHITE, Color.BLACK},
    'arid mesa': {Color.RED, Color.WHITE},
    'scalding tarn': {Color.BLUE, Color.RED},
    'verdant catacombs': {Color.BLACK, Color.GREEN},
    'misty rainforest': {Color.BLUE, Color.GREEN},
    
    # Shock Lands
    'hallowed fountain': {Color.WHITE, Color.BLUE},
    'watery grave': {Color.BLUE, Color.BLACK},
    'blood crypt': {Color.BLACK, Color.RED},
    'stomping ground': {Color.RED, Color.GREEN},
    'temple garden': {Color.WHITE, Color.GREEN},
    'godless shrine': {Color.WHITE, Color.BLACK},
    'overgrown tomb': {Color.BLACK, Color.GREEN},
    'steam vents': {Color.BLUE, Color.RED},
    'breeding pool': {Color.BLUE, Color.GREEN},
    'sacred foundry': {Color.WHITE, Color.RED},
    
    # Check Lands
    'glacial fortress': {Color.WHITE, Color.BLUE},
    'drowned catacomb': {Color.BLUE, Color.BLACK},
    'dragonskull summit': {Color.BLACK, Color.RED},
    'rootbound crag': {Color.RED, Color.GREEN},
    'sunpetal grove': {Color.WHITE, Color.GREEN},
    'isolated chapel': {Color.WHITE, Color.BLACK},
    'woodland cemetery': {Color.BLACK, Color.GREEN},
    'sulfur falls': {Color.BLUE, Color.RED},
    'breeding pool': {Color.BLUE, Color.GREEN},
    'clifftop retreat': {Color.WHITE, Color.RED},
    
    # Pain Lands
    'adarkar wastes': {Color.WHITE, Color.BLUE},
    'underground river': {Color.BLUE, Color.BLACK},
    'lava tubes': {Color.BLACK, Color.RED},
    'brushland': {Color.WHITE, Color.GREEN},
    'karplusan forest': {Color.RED, Color.GREEN},
    'shivan reef': {Color.BLUE, Color.RED},
    'llanowar wastes': {Color.BLACK, Color.GREEN},
    'yawgmoth cemetery': {Color.BLACK, Color.GREEN},
    'city of brass': {Color.WHITE, Color.BLUE, Color.BLACK, Color.RED, Color.GREEN},
    'gemstone mine': {Color.WHITE, Color.BLUE, Color.BLACK, Color.RED, Color.GREEN},
    
    # Filter Lands
    'seachrome coast': {Color.WHITE, Color.BLUE},
    'darkslick shores': {Color.BLUE, Color.BLACK},
    'blackcleave cliffs': {Color.BLACK, Color.RED},
    'copperline gorge': {Color.RED, Color.GREEN},
    'raging ravine': {Color.WHITE, Color.GREEN},
    'sungrass prairie': {Color.WHITE, Color.BLACK},
    'twilight mire': {Color.BLACK, Color.GREEN},
    'river of tears': {Color.WHITE, Color.BLUE},
    'valley of the dead': {Color.BLUE, Color.BLACK},
    'fire-lit thicket': {Color.BLACK, Color.RED},
    'mossfire valley': {Color.RED, Color.GREEN},
    'fertile thicket': {Color.WHITE, Color.GREEN},
    
    # Scry Lands
    'temple of enlightenment': {Color.WHITE, Color.BLUE},
    'temple of deception': {Color.BLUE, Color.BLACK},
    'temple of malice': {Color.BLACK, Color.RED},
    'temple of abandon': {Color.RED, Color.GREEN},
    'temple of triumph': {Color.WHITE, Color.GREEN},
    'temple of silence': {Color.WHITE, Color.BLACK},
    'temple of epiphany': {Color.BLUE, Color.RED},
    'temple of malady': {Color.BLACK, Color.GREEN},
    'temple of mystery': {Color.BLUE, Color.GREEN},
    'temple of plenty': {Color.WHITE, Color.RED},
    
    # Special Lands
    'concealed courtyard': {Color.WHITE, Color.RED},
    'otawara, soaring city': {Color.BLUE},
    'bojuka bog': {Color.BLACK},
    'ghost quarter': {Color.COLORLESS},
    'field of ruin': {Color.COLORLESS},
    'tectonic edge': {Color.COLORLESS},
    'creeping tar pit': {Color.BLUE, Color.BLACK},
    'inkmoth nexus': {Color.BLUE},
    'celestial coliseum': {Color.WHITE, Color.BLUE},
    'hinterland harbor': {Color.BLUE, Color.GREEN},
    'prairie stream': {Color.WHITE, Color.BLUE},
    'sunken hollow': {Color.BLUE, Color.BLACK},
    'smoldering marsh': {Color.BLACK, Color.RED},
    'cinder glade': {Color.RED, Color.GREEN},
    'canopy vista': {Color.WHITE, Color.GREEN},
    'mystic monastery': {Color.WHITE, Color.RED},
    'opulent palace': {Color.BLUE, Color.BLACK, Color.GREEN},
    'nomad outpost': {Color.WHITE, Color.BLACK, Color.RED},
    'sandsteppe citadel': {Color.WHITE, Color.BLUE, Color.GREEN},
}


def get_land_mana_from_known(land_name: str) -> Optional[set]:
    """Busca as cores de mana de um terreno conhecido."""
    name_lower = land_name.lower()
    return KNOWN_LANDS.get(name_lower)
