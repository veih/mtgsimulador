"""
MTG Match Simulator - Mana Ability Engine
Identifica habilidades de mana disponiveis seguindo o texto dos cards.

Cada terreno tem seu efeito exato:
- Basic Lands: {T}: Add {W}
- Shock Lands: {T}: Add {W/U} (pay 2 life: enters untapped)
- Fetch Lands: {T}, Pay 1 life, Sacrifice: Search...
- Pain Lands: {T}: Add {C}. {T}, Pay 1 life: Add {W/U}
- Lotus Bloom: {T}, Sacrifice: Add three mana of any one color
- Gemstone Mine: {T}, Remove counter: Add one mana of any color
"""

from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum, auto
from .card import Color


# ─────────────────────────────────────────────
# Tipos de Habilidade de Mana
# ─────────────────────────────────────────────

class ManaActionType(Enum):
    """Tipo de habilidade de mana."""
    TAP_FOR_MANA = auto()           # {T}: Add mana
    TAP_PAY_LIFE_FOR_MANA = auto()  # {T}, Pay life: Add mana
    TAP_SACRIFICE_FOR_MANA = auto() # {T}, Sacrifice: Add mana
    REMOVE_COUNTER_FOR_MANA = auto() # Remove counter: Add mana
    FETCH_LAND = auto()             # Sacrifice, pay life: Search land


@dataclass
class ManaAbility:
    """Uma habilidade de mana de um permanente."""
    source: Any                     # Carta/permanente
    ability_type: ManaActionType
    produces: Dict[Color, int]      # Cores que produz
    tap_required: bool = False      # Requer virar?
    sacrifice_required: bool = False # Requer sacrificar?
    life_cost: int = 0              # Custo de vida
    counter_cost: int = 0           # Custo de marcadores
    fetch_options: List[str] = field(default_factory=list)  # Opcoes de busca
    description: str = ""           # Descricao do efeito
    
    def can_activate(self, player) -> bool:
        """Verifica se a habilidade pode ser ativada."""
        # Verifica se esta virada
        if self.tap_required and hasattr(self.source, 'tapped') and self.source.tapped:
            return False
        
        # Verifica se esta no campo
        if self.source not in player.battlefield:
            return False
        
        # Verifica vida
        if self.life_cost > 0 and player.life <= self.life_cost:
            return False
        
        # Verifica marcadores
        if self.counter_cost > 0:
            counters = getattr(self.source, 'charge_counters', 0)
            if counters < self.counter_cost:
                return False
        
        return True
    
    def get_mana_text(self) -> str:
        """Retorna o texto da habilidade no formato MTG."""
        parts = []
        
        if self.tap_required:
            parts.append("{T}")
        
        if self.life_cost > 0:
            parts.append(f"Pay {self.life_cost} life")
        
        if self.sacrifice_required:
            parts.append("Sacrifice")
        
        if self.counter_cost > 0:
            parts.append(f"Remove {self.counter_cost} counter")
        
        cost = ", ".join(parts) if parts else "Activate"
        
        # Formata mana produzido
        if self.produces:
            if len(self.produces) == 1:
                color = list(self.produces.keys())[0]
                amount = self.produces[color]
                mana_text = f"{amount} {color.name}" if amount > 1 else color.name
            else:
                mana_text = " or ".join([c.name for c in self.produces.keys()])
        else:
            mana_text = "mana"
        
        return f"{cost}: Add {mana_text}"


# ─────────────────────────────────────────────
# Base de Dados de Habilidades de Mana
# ─────────────────────────────────────────────

LAND_MANA_ABILITIES = {
    # ─── Terrenos Basicos ───
    # {T}: Add {W}
    "plains": {
        "type": "tap_for_mana",
        "produces": {Color.WHITE: 1},
        "text": "{T}: Add {W}"
    },
    "island": {
        "type": "tap_for_mana",
        "produces": {Color.BLUE: 1},
        "text": "{T}: Add {U}"
    },
    "swamp": {
        "type": "tap_for_mana",
        "produces": {Color.BLACK: 1},
        "text": "{T}: Add {B}"
    },
    "mountain": {
        "type": "tap_for_mana",
        "produces": {Color.RED: 1},
        "text": "{T}: Add {R}"
    },
    "forest": {
        "type": "tap_for_mana",
        "produces": {Color.GREEN: 1},
        "text": "{T}: Add {G}"
    },
    
    # ─── Shock Lands ───
    # {T}: Add {W} or {U}
    "hallowed fountain": {
        "type": "tap_for_mana",
        "produces": {Color.WHITE: 1, Color.BLUE: 1},
        "text": "{T}: Add {W} or {U}"
    },
    "watery grave": {
        "type": "tap_for_mana",
        "produces": {Color.BLUE: 1, Color.BLACK: 1},
        "text": "{T}: Add {U} or {B}"
    },
    "blood crypt": {
        "type": "tap_for_mana",
        "produces": {Color.BLACK: 1, Color.RED: 1},
        "text": "{T}: Add {B} or {R}"
    },
    "stomping ground": {
        "type": "tap_for_mana",
        "produces": {Color.RED: 1, Color.GREEN: 1},
        "text": "{T}: Add {R} or {G}"
    },
    "temple garden": {
        "type": "tap_for_mana",
        "produces": {Color.GREEN: 1, Color.WHITE: 1},
        "text": "{T}: Add {G} or {W}"
    },
    "godless shrine": {
        "type": "tap_for_mana",
        "produces": {Color.WHITE: 1, Color.BLACK: 1},
        "text": "{T}: Add {W} or {B}"
    },
    "overgrown tomb": {
        "type": "tap_for_mana",
        "produces": {Color.BLACK: 1, Color.GREEN: 1},
        "text": "{T}: Add {B} or {G}"
    },
    "steam vents": {
        "type": "tap_for_mana",
        "produces": {Color.BLUE: 1, Color.RED: 1},
        "text": "{T}: Add {U} or {R}"
    },
    "breeding pool": {
        "type": "tap_for_mana",
        "produces": {Color.GREEN: 1, Color.BLUE: 1},
        "text": "{T}: Add {G} or {U}"
    },
    "sacred foundry": {
        "type": "tap_for_mana",
        "produces": {Color.RED: 1, Color.WHITE: 1},
        "text": "{T}: Add {R} or {W}"
    },
    
    # ─── Pain Lands ───
    # {T}: Add {C}. {T}, Pay 1 life: Add {W} or {U}
    "adarkar wastes": {
        "type": "pain_land",
        "colorless": 1,
        "colors": {Color.WHITE: 1, Color.BLUE: 1},
        "life_cost": 1,
        "text": "{T}: Add {C}. {T}, Pay 1 life: Add {W} or {U}"
    },
    "underground river": {
        "type": "pain_land",
        "colorless": 1,
        "colors": {Color.BLUE: 1, Color.BLACK: 1},
        "life_cost": 1,
        "text": "{T}: Add {C}. {T}, Pay 1 life: Add {U} or {B}"
    },
    "caves of koilos": {
        "type": "pain_land",
        "colorless": 1,
        "colors": {Color.WHITE: 1, Color.BLACK: 1},
        "life_cost": 1,
        "text": "{T}: Add {C}. {T}, Pay 1 life: Add {W} or {B}"
    },
    "karplusan forest": {
        "type": "pain_land",
        "colorless": 1,
        "colors": {Color.RED: 1, Color.GREEN: 1},
        "life_cost": 1,
        "text": "{T}: Add {C}. {T}, Pay 1 life: Add {R} or {G}"
    },
    "brushland": {
        "type": "pain_land",
        "colorless": 1,
        "colors": {Color.GREEN: 1, Color.WHITE: 1},
        "life_cost": 1,
        "text": "{T}: Add {C}. {T}, Pay 1 life: Add {G} or {W}"
    },
    "shivan reef": {
        "type": "pain_land",
        "colorless": 1,
        "colors": {Color.BLUE: 1, Color.RED: 1},
        "life_cost": 1,
        "text": "{T}: Add {C}. {T}, Pay 1 life: Add {U} or {R}"
    },
    "llanowar wastes": {
        "type": "pain_land",
        "colorless": 1,
        "colors": {Color.BLACK: 1, Color.GREEN: 1},
        "life_cost": 1,
        "text": "{T}: Add {C}. {T}, Pay 1 life: Add {B} or {G}"
    },
    
    # ─── Fetch Lands ───
    # {T}, Pay 1 life, Sacrifice: Search land
    "flooded strand": {
        "type": "fetch_land",
        "life_cost": 1,
        "fetch_options": ["plains", "island", "tundra", "hallowed fountain", "godless shrine", "watery grave"],
        "text": "{T}, Pay 1 life, Sacrifice ~: Search your library for a Plains or Island card..."
    },
    "bloodstained mire": {
        "type": "fetch_land",
        "life_cost": 1,
        "fetch_options": ["swamp", "mountain", "badlands", "blood crypt", "godless shrine", "stomping ground"],
        "text": "{T}, Pay 1 life, Sacrifice ~: Search your library for a Swamp or Mountain card..."
    },
    "wooded foothills": {
        "type": "fetch_land",
        "life_cost": 1,
        "fetch_options": ["mountain", "forest", "taiga", "stomping ground", "blood crypt", "rootbound crag"],
        "text": "{T}, Pay 1 life, Sacrifice ~: Search your library for a Mountain or Forest card..."
    },
    "polluted delta": {
        "type": "fetch_land",
        "life_cost": 1,
        "fetch_options": ["island", "swamp", "underground sea", "watery grave", "drowned catacomb", "steam vents"],
        "text": "{T}, Pay 1 life, Sacrifice ~: Search your library for an Island or Swamp card..."
    },
    "windswept heath": {
        "type": "fetch_land",
        "life_cost": 1,
        "fetch_options": ["forest", "plains", "savannah", "temple garden", "stomping ground", "rootbound crag"],
        "text": "{T}, Pay 1 life, Sacrifice ~: Search your library for a Forest or Plains card..."
    },
    "marsh flats": {
        "type": "fetch_land",
        "life_cost": 1,
        "fetch_options": ["plains", "swamp", "scrubland", "godless shrine", "temple of silence", "caves of koilos"],
        "text": "{T}, Pay 1 life, Sacrifice ~: Search your library for a Plains or Swamp card..."
    },
    "arid mesa": {
        "type": "fetch_land",
        "life_cost": 1,
        "fetch_options": ["mountain", "plains", "plateau", "sacred foundry", "clifftop retreat", "nomad outpost"],
        "text": "{T}, Pay 1 life, Sacrifice ~: Search your library for a Mountain or Plains card..."
    },
    "verdant catacombs": {
        "type": "fetch_land",
        "life_cost": 1,
        "fetch_options": ["swamp", "forest", "bayou", "overgrown tomb", "woodland cemetery", "twilight mire"],
        "text": "{T}, Pay 1 life, Sacrifice ~: Search your library for a Swamp or Forest card..."
    },
    "misty rainforest": {
        "type": "fetch_land",
        "life_cost": 1,
        "fetch_options": ["island", "forest", "tropical island", "breeding pool", "hinterland harbor", "yalam grotto"],
        "text": "{T}, Pay 1 life, Sacrifice ~: Search your library for an Island or Forest card..."
    },
    "scalding tarn": {
        "type": "fetch_land",
        "life_cost": 1,
        "fetch_options": ["island", "mountain", "volcanic island", "steam vents", "sulphur falls", "shivan reef"],
        "text": "{T}, Pay 1 life, Sacrifice ~: Search your library for an Island or Mountain card..."
    },
    
    # ─── Special Lands ───
    # Lotus Bloom: {T}, Sacrifice ~: Add three mana of any one color
    "lotus bloom": {
        "type": "sacrifice_for_any",
        "amount": 3,
        "same_color": True,
        "text": "{T}, Sacrifice ~: Add three mana of any one color"
    },
    
    # Gemstone Mine: {T}, Remove a mining counter: Add one mana of any color
    "gemstone mine": {
        "type": "remove_counter_for_any",
        "amount": 1,
        "text": "{T}, Remove a mining counter from ~: Add one mana of any color"
    },
    
    # City of Brass: {T}: Add one mana of any color. Whenever City of Brass becomes tapped, you lose 1 life
    "city of brass": {
        "type": "tap_for_any",
        "amount": 1,
        "life_cost": 1,  # Perde 1 vida ao virar
        "text": "{T}: Add one mana of any color. Whenever ~ becomes tapped, you lose 1 life"
    },
    
    # Mana Confluence: {T}, Pay 1 life: Add one mana of any color
    "mana confluence": {
        "type": "tap_pay_life_for_any",
        "amount": 1,
        "life_cost": 1,
        "text": "{T}, Pay 1 life: Add one mana of any color"
    },
}


# ─────────────────────────────────────────────
# Mana Ability Engine
# ─────────────────────────────────────────────

class ManaAbilityEngine:
    """
    Identifica todas as habilidades de mana disponiveis no campo de batalha.
    Segue o texto exato dos cards.
    """
    
    def __init__(self):
        self.land_abilities = LAND_MANA_ABILITIES
    
    def get_mana_abilities(self, player) -> List[ManaAbility]:
        """Retorna todas as habilidades de mana disponiveis para um jogador."""
        abilities = []
        
        for card in player.battlefield:
            if not card.is_land():
                continue
            
            card_name = card.name.lower()
            mana_data = self.land_abilities.get(card_name, {})
            
            if not mana_data:
                continue
            
            ability_type = mana_data.get("type", "")
            
            # Terreno basico ou shock land
            if ability_type == "tap_for_mana":
                produces = mana_data.get("produces", {})
                ability = ManaAbility(
                    source=card,
                    ability_type=ManaActionType.TAP_FOR_MANA,
                    produces=produces,
                    tap_required=True,
                    description=mana_data.get("text", "")
                )
                abilities.append(ability)
            
            # Pain land
            elif ability_type == "pain_land":
                # Primeira habilidade: {T}: Add {C}
                colorless_ability = ManaAbility(
                    source=card,
                    ability_type=ManaActionType.TAP_FOR_MANA,
                    produces={"colorless": 1},
                    tap_required=True,
                    description=f"{{T}}: Add {{C}}"
                )
                abilities.append(colorless_ability)
                
                # Segunda habilidade: {T}, Pay 1 life: Add {W/U}
                colors = mana_data.get("colors", {})
                life_cost = mana_data.get("life_cost", 1)
                colored_ability = ManaAbility(
                    source=card,
                    ability_type=ManaActionType.TAP_PAY_LIFE_FOR_MANA,
                    produces=colors,
                    tap_required=True,
                    life_cost=life_cost,
                    description=mana_data.get("text", "").split(". ")[1] if ". " in mana_data.get("text", "") else ""
                )
                abilities.append(colored_ability)
            
            # Fetch land
            elif ability_type == "fetch_land":
                life_cost = mana_data.get("life_cost", 1)
                fetch_options = mana_data.get("fetch_options", [])
                ability = ManaAbility(
                    source=card,
                    ability_type=ManaActionType.FETCH_LAND,
                    produces={},
                    tap_required=True,
                    sacrifice_required=True,
                    life_cost=life_cost,
                    fetch_options=fetch_options,
                    description=mana_data.get("text", "")
                )
                abilities.append(ability)
            
            # Sacrifice for any (Lotus Bloom)
            elif ability_type == "sacrifice_for_any":
                amount = mana_data.get("amount", 1)
                ability = ManaAbility(
                    source=card,
                    ability_type=ManaActionType.TAP_SACRIFICE_FOR_MANA,
                    produces={Color.WHITE: amount, Color.BLUE: amount, Color.BLACK: amount, Color.RED: amount, Color.GREEN: amount},
                    tap_required=True,
                    sacrifice_required=True,
                    description=mana_data.get("text", "")
                )
                # Marca que e 3 da mesma cor
                ability.same_color = mana_data.get("same_color", False)
                abilities.append(ability)
            
            # Remove counter for any (Gemstone Mine)
            elif ability_type == "remove_counter_for_any":
                amount = mana_data.get("amount", 1)
                ability = ManaAbility(
                    source=card,
                    ability_type=ManaActionType.REMOVE_COUNTER_FOR_MANA,
                    produces={Color.WHITE: amount, Color.BLUE: amount, Color.BLACK: amount, Color.RED: amount, Color.GREEN: amount},
                    tap_required=True,
                    counter_cost=1,
                    description=mana_data.get("text", "")
                )
                abilities.append(ability)
            
            # Tap for any (City of Brass)
            elif ability_type == "tap_for_any":
                amount = mana_data.get("amount", 1)
                life_cost = mana_data.get("life_cost", 1)
                ability = ManaAbility(
                    source=card,
                    ability_type=ManaActionType.TAP_FOR_MANA,
                    produces={Color.WHITE: amount, Color.BLUE: amount, Color.BLACK: amount, Color.RED: amount, Color.GREEN: amount},
                    tap_required=True,
                    life_cost=life_cost,
                    description=mana_data.get("text", "")
                )
                abilities.append(ability)
            
            # Tap pay life for any (Mana Confluence)
            elif ability_type == "tap_pay_life_for_any":
                amount = mana_data.get("amount", 1)
                life_cost = mana_data.get("life_cost", 1)
                ability = ManaAbility(
                    source=card,
                    ability_type=ManaActionType.TAP_PAY_LIFE_FOR_MANA,
                    produces={Color.WHITE: amount, Color.BLUE: amount, Color.BLACK: amount, Color.RED: amount, Color.GREEN: amount},
                    tap_required=True,
                    life_cost=life_cost,
                    description=mana_data.get("text", "")
                )
                abilities.append(ability)
        
        return abilities
    
    def get_available_actions(self, player) -> List[str]:
        """
        Retorna todas as acoes disponiveis relacionadas a mana.
        """
        actions = []
        abilities = self.get_mana_abilities(player)
        
        for ability in abilities:
            if not ability.can_activate(player):
                continue
            
            actions.append(ability.get_mana_text())
        
        return actions
