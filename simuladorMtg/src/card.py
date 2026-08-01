"""
MTG Match Simulator - Modelos de dados
Define cartas, efeitos, mecânicas e enums do simulador.
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional


# ─────────────────────────────────────────────
# Enums
# ─────────────────────────────────────────────

class CardType(Enum):
    CREATURE = auto()
    INSTANT = auto()
    SORCERY = auto()
    PLANESWALKER = auto()
    ARTIFACT = auto()
    ENCHANTMENT = auto()
    LAND = auto()


class Color(Enum):
    WHITE = "W"
    BLUE = "U"
    BLACK = "B"
    RED = "R"
    GREEN = "G"
    COLORLESS = "C"


class Zone(Enum):
    LIBRARY = auto()
    HAND = auto()
    BATTLEFIELD = auto()
    GRAVEYARD = auto()
    STACK = auto()
    EXILE = auto()


class Keyword(Enum):
    FLYING = "Flying"
    TRAMPLE = "Trample"
    LIFELINK = "Lifelink"
    HASTE = "Haste"
    VIGILANCE = "Vigilance"
    HEXPROOF = "Hexproof"
    INDESTRUCTIBLE = "Indestructible"
    MENACE = "Menace"
    FIRST_STRIKE = "First Strike"
    DOUBLE_STRIKE = "Double Strike"
    DEATHTOUCH = "Deathtouch"
    REACH = "Reach"
    FLASH = "Flash"
    WARD = "Ward"


class TargetType(Enum):
    ANY = "any"                 # qualquer alvo
    CREATURE = "creature"       # apenas criaturas
    PLAYER = "player"           # apenas jogadores
    CREATURE_OR_PLAYER = "creature_or_player"


# ─────────────────────────────────────────────
# Efeitos
# ─────────────────────────────────────────────

class EffectType(Enum):
    DAMAGE = auto()
    GAIN_LIFE = auto()
    DESTROY_CREATURE = auto()
    DRAW_CARD = auto()
    ADD_MANA = auto()
    PUMP = auto()              # +X/+Y
    EXILE = auto()
    COUNTER = auto()
    SACRIFICE = auto()
    MILL = auto()
    CREATE_TOKEN = auto()
    HEAL = auto()


@dataclass
class SpellEffect:
    """Define o efeito de uma magia quando resolve."""
    effect_type: EffectType
    value: int = 0
    value2: int = 0                     # para pump (+value/+value2)
    target_type: TargetType = TargetType.ANY
    duration: str = "instant"           # "instant" ou "turn" (para pump temporário)

    def __repr__(self):
        if self.effect_type == EffectType.DAMAGE:
            return f"Dano {self.value}"
        elif self.effect_type == EffectType.GAIN_LIFE:
            return f"Gain life {self.value}"
        elif self.effect_type == EffectType.PUMP:
            return f"+{self.value}/+{self.value2}"
        elif self.effect_type == EffectType.DESTROY_CREATURE:
            return "Destruir criatura"
        elif self.effect_type == EffectType.DRAW_CARD:
            return f"Comprar {self.value} carta(s)"
        elif self.effect_type == EffectType.ADD_MANA:
            return f"Adicionar {self.value} mana"
        return f"{self.effect_type.name} {self.value}"


# ─────────────────────────────────────────────
# Custo de Mana
# ─────────────────────────────────────────────

@dataclass
class ManaCost:
    """Representa o custo de mana de uma magia."""
    generic: int = 0
    white: int = 0
    blue: int = 0
    black: int = 0
    red: int = 0
    green: int = 0

    @property
    def total(self) -> int:
        return self.generic + self.white + self.blue + self.black + self.red + self.green

    @property
    def colors(self) -> set:
        c = set()
        if self.white: c.add(Color.WHITE)
        if self.blue: c.add(Color.BLUE)
        if self.black: c.add(Color.BLACK)
        if self.red: c.add(Color.RED)
        if self.green: c.add(Color.GREEN)
        return c

    def can_pay(self, mana_pool: dict) -> bool:
        """Verifica se o pool de mana consegue pagar o custo."""
        pool = dict(mana_pool)
        remaining_generic = self.generic

        # Paga custos coloridos primeiro
        for color, amount in [
            (Color.WHITE, self.white), (Color.BLUE, self.blue),
            (Color.BLACK, self.black), (Color.RED, self.red),
            (Color.GREEN, self.green)
        ]:
            available = pool.get(color, 0)
            if available < amount:
                return False
            pool[color] = available - amount

        # Paga custo genérico com o que sobrar
        remaining = sum(pool.values())
        return remaining >= remaining_generic

    def pay(self, mana_pool: dict) -> dict:
        """Paga o custo, retornando o pool restante."""
        pool = {k: v for k, v in mana_pool.items()}
        remaining_generic = self.generic

        for color, amount in [
            (Color.WHITE, self.white), (Color.BLUE, self.blue),
            (Color.BLACK, self.black), (Color.RED, self.red),
            (Color.GREEN, self.green)
        ]:
            pool[color] = pool.get(color, 0) - amount

        # Paga genérico
        for color in list(pool.keys()):
            if remaining_generic <= 0:
                break
            available = pool[color]
            use = min(available, remaining_generic)
            pool[color] -= use
            remaining_generic -= use

        return pool

    def __str__(self):
        parts = []
        if self.generic: parts.append(str(self.generic))
        if self.white: parts.append("W" * self.white)
        if self.blue: parts.append("U" * self.blue)
        if self.black: parts.append("B" * self.black)
        if self.red: parts.append("R" * self.red)
        if self.green: parts.append("G" * self.green)
        return "{" + "".join(parts) + "}" if parts else "{0}"


# ─────────────────────────────────────────────
# Carta
# ─────────────────────────────────────────────

@dataclass
class Card:
    """Modelo completo de uma carta MTG."""
    id: str
    name: str
    mana_cost: ManaCost
    card_type: CardType
    colors: set
    text: str
    power: int = 0
    toughness: int = 0
    keywords: list = field(default_factory=list)
    effects: list = field(default_factory=list)
    is_land: bool = False
    land_mana: set = field(default_factory=set)
    current_power: int = -1       # -1 significa "não modificado"
    current_toughness: int = -1
    tapped: bool = False
    summoning_sick: bool = True
    has_attacked: bool = False

    @property
    def mana_value(self) -> int:
        return self.mana_cost.total

    @property
    def effective_power(self) -> int:
        if self.current_power >= 0:
            return self.current_power
        return self.power

    @property
    def effective_toughness(self) -> int:
        if self.current_toughness >= 0:
            return self.current_toughness
        return self.toughness

    @property
    def is_creature(self) -> bool:
        return self.card_type == CardType.CREATURE

    @property
    def is_instant(self) -> bool:
        return self.card_type == CardType.INSTANT

    @property
    def is_sorcery(self) -> bool:
        return self.card_type == CardType.SORCERY

    @property
    def is_spell(self) -> bool:
        return not self.is_land

    @property
    def is_alive(self) -> bool:
        """Criatura com toughness > 0."""
        return self.effective_toughness > 0

    def has_keyword(self, kw: Keyword) -> bool:
        return kw in self.keywords

    def reset_temporary(self):
        """Reseta valores temporários (pump de turno, etc)."""
        self.current_power = -1
        self.current_toughness = -1

    def copy(self) -> 'Card':
        """Cria uma cópia independente da carta."""
        return Card(
            id=self.id, name=self.name, mana_cost=self.mana_cost,
            card_type=self.card_type, colors=set(self.colors),
            text=self.text, power=self.power, toughness=self.toughness,
            keywords=list(self.keywords), effects=list(self.effects),
            is_land=self.is_land, land_mana=set(self.land_mana),
        )

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name


# ─────────────────────────────────────────────
# Token
# ─────────────────────────────────────────────

def create_token(token_id: str, name: str, power: int, toughness: int,
                 colors: set = None, keywords: list = None) -> Card:
    """Cria uma ficha de criatura (token)."""
    return Card(
        id=token_id, name=name,
        mana_cost=ManaCost(),
        card_type=CardType.CREATURE,
        colors=colors or set(),
        text=f"Token {power}/{toughness}",
        power=power, toughness=toughness,
        keywords=keywords or []
    )
