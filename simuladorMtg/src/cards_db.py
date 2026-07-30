"""
MTG Match Simulator - Banco de Cartas
Cartas icônicas do Modern para simulação.
"""

from .card import Card, CardType, Color, ManaCost, Keyword, EffectType, SpellEffect, TargetType


# ─────────────────────────────────────────────
# Terrenos Básicos
# ─────────────────────────────────────────────

def _land(name: str, color: Color) -> Card:
    return Card(
        id=name.lower().replace(" ", "_"),
        name=name, mana_cost=ManaCost(),
        card_type=CardType.ARTIFACT,  # terreno tratado separadamente
        colors=set(), text=f"Tap: add {color.value}",
        is_land=True, land_mana={color}
    )

PLAINS = _land("Plains", Color.WHITE)
ISLAND = _land("Island", Color.BLUE)
SWAMP = _land("Swamp", Color.BLACK)
MOUNTAIN = _land("Mountain", Color.RED)
FOREST = _land("Forest", Color.GREEN)


# ─────────────────────────────────────────────
# Cartas Vermelhas (Red)
# ─────────────────────────────────────────────

LIGHTNING_BOLT = Card(
    id="lightning_bolt", name="Lightning Bolt",
    mana_cost=ManaCost(red=1), card_type=CardType.INSTANT,
    colors={Color.RED},
    text="Lightning Bolt deals 3 damage to any target.",
    effects=[SpellEffect(EffectType.DAMAGE, 3, target_type=TargetType.CREATURE_OR_PLAYER)]
)

LAVA_SPIKE = Card(
    id="lava_spike", name="Lava Spike",
    mana_cost=ManaCost(red=1), card_type=CardType.SORCERY,
    colors={Color.RED},
    text="Lava Spike deals 3 damage to target player or planeswalker.",
    effects=[SpellEffect(EffectType.DAMAGE, 3, target_type=TargetType.PLAYER)]
)

CHAIN_LIGHTNING = Card(
    id="chain_lightning", name="Chain Lightning",
    mana_cost=ManaCost(red=1), card_type=CardType.SORCERY,
    colors={Color.RED},
    text="Chain Lightning deals 3 damage to any target.",
    effects=[SpellEffect(EffectType.DAMAGE, 3, target_type=TargetType.CREATURE_OR_PLAYER)]
)

GOBLIN_GUIDE = Card(
    id="goblin_guide", name="Goblin Guide",
    mana_cost=ManaCost(red=1), card_type=CardType.CREATURE,
    colors={Color.RED}, text="Haste. When Goblin Guide enters, opponent reveals top card.",
    power=2, toughness=2,
    keywords=[Keyword.HASTE],
    effects=[SpellEffect(EffectType.DRAW_CARD, 1)]  # simplificado: oponente compra (simula reveal)
)

MONASTIC_MENTOR = Card(
    id="monastic_mentor", name="Monastic Mentor",
    mana_cost=ManaCost(red=1), card_type=CardType.CREATURE,
    colors={Color.RED}, text="First strike.",
    power=1, toughness=3,
    keywords=[Keyword.FIRST_STRIKE]
)

SAVAGE_TWIST = Card(
    id="savage_twist", name="Savage Twister",
    mana_cost=ManaCost(red=2, green=1), card_type=CardType.SORCERY,
    colors={Color.RED, Color.GREEN},
    text="Savage Twister deals 2 damage to each creature.",
    effects=[SpellEffect(EffectType.DAMAGE, 2, target_type=TargetType.CREATURE)]
)

SKULLRAID = Card(
    id="skullraid", name="Skullraid",
    mana_cost=ManaCost(red=1), card_type=CardType.SORCERY,
    colors={Color.RED},
    text="Skullraid deals 2 damage to any target.",
    effects=[SpellEffect(EffectType.DAMAGE, 2, target_type=TargetType.CREATURE_OR_PLAYER)]
)


# ─────────────────────────────────────────────
# Cartas Brancas (White)
# ─────────────────────────────────────────────

LLANOWAR_HEALBOT = Card(
    id="healing_salve", name="Healing Salve",
    mana_cost=ManaCost(white=1), card_type=CardType.INSTANT,
    colors={Color.WHITE},
    text="Target player gains 3 life.",
    effects=[SpellEffect(EffectType.GAIN_LIFE, 3, target_type=TargetType.PLAYER)]
)

SWORDS_TO_PLOWSHARES = Card(
    id="swords_to_plowshares", name="Swords to Plowshares",
    mana_cost=ManaCost(white=1), card_type=CardType.INSTANT,
    colors={Color.WHITE},
    text="Exile target creature. Its controller gains life equal to its power.",
    effects=[SpellEffect(EffectType.EXILE, target_type=TargetType.CREATURE),
             SpellEffect(EffectType.GAIN_LIFE, 0, target_type=TargetType.PLAYER)]
)

GIANT_GROWTH = Card(
    id="giant_growth", name="Giant Growth",
    mana_cost=ManaCost(green=1), card_type=CardType.INSTANT,
    colors={Color.GREEN},
    text="Target creature gets +3/+3 until end of turn.",
    effects=[SpellEffect(EffectType.PUMP, 3, 3, target_type=TargetType.CREATURE, duration="turn")]
)

ELSPETH_TALENT = Card(
    id="day_of_judgment", name="Day of Judgment",
    mana_cost=ManaCost(white=2, generic=2), card_type=CardType.SORCERY,
    colors={Color.WHITE},
    text="Destroy all creatures.",
    effects=[SpellEffect(EffectType.DESTROY_CREATURE, target_type=TargetType.CREATURE)]
)

GUARDIAN_OF_SOLITUDE = Card(
    id="guardian_of_solitude", name="Guardian of Solitude",
    mana_cost=ManaCost(white=3), card_type=CardType.CREATURE,
    colors={Color.WHITE}, text="Vigilance.",
    power=2, toughness=5,
    keywords=[Keyword.VIGILANCE]
)

SAMITE_HEALER = Card(
    id="samite_healer", name="Samite Healer",
    mana_cost=ManaCost(white=2), card_type=CardType.CREATURE,
    colors={Color.WHITE},
    text="Tap: Prevent 1 damage.",
    power=1, toughness=3,
    effects=[SpellEffect(EffectType.GAIN_LIFE, 2)]
)

THRaben_BENCH = Card(
    id="thrabens_banner", name="Thraben Banner",
    mana_cost=ManaCost(white=1), card_type=CardType.SORCERY,
    colors={Color.WHITE},
    text="Target player gains 2 life.",
    effects=[SpellEffect(EffectType.GAIN_LIFE, 2, target_type=TargetType.PLAYER)]
)


# ─────────────────────────────────────────────
# Cartas Verdes (Green)
# ─────────────────────────────────────────────

GRIZZLY_BEARS = Card(
    id="grizzly_bears", name="Grizzly Bears",
    mana_cost=ManaCost(green=1, generic=1), card_type=CardType.CREATURE,
    colors={Color.GREEN},
    text="Vanilla 2/2.",
    power=2, toughness=2
)

TARMAGOID = Card(
    id="tarmogoyf", name="Tarmogoyf",
    mana_cost=ManaCost(green=1, generic=1), card_type=CardType.CREATURE,
    colors={Color.GREEN},
    text="Tarmogoyf's power is equal to the number of card types among cards in all graveyards +1, toughness +2.",
    power=2, toughness=3,  # valor médio simplificado
)

BIRD_OF_PARADISE = Card(
    id="bird_of_paradise", name="Bird of Paradise",
    mana_cost=ManaCost(green=1), card_type=CardType.CREATURE,
    colors={Color.GREEN},
    text="Tap: Add one mana of any color.",
    power=1, toughness=1,
    keywords=[Keyword.FLYING],
    effects=[SpellEffect(EffectType.ADD_MANA, 1)]
)

ELVES_OF_DEEPENING = Card(
    id="elves", name="Llanowar Elves",
    mana_cost=ManaCost(green=1), card_type=CardType.CREATURE,
    colors={Color.GREEN},
    text="Tap: Add G.",
    power=1, toughness=1,
    effects=[SpellEffect(EffectType.ADD_MANA, 1)]
)

COLLECTIVE_UNCONSCIOUS = Card(
    id="harmonize", name="Harmonize",
    mana_cost=ManaCost(green=2, generic=1), card_type=CardType.SORCERY,
    colors={Color.GREEN},
    text="Draw three cards.",
    effects=[SpellEffect(EffectType.DRAW_CARD, 3)]
)

OVERCOME = Card(
    id="overcome", name="Overcome",
    mana_cost=ManaCost(green=2, generic=1), card_type=CardType.SORCERY,
    colors={Color.GREEN},
    text="Target creature gets +4/+4 until end of turn.",
    effects=[SpellEffect(EffectType.PUMP, 4, 4, target_type=TargetType.CREATURE, duration="turn")]
)

WOOD_ELEPHANT = Card(
    id="wood_elephant", name="Wood Elephant",
    mana_cost=ManaCost(green=2), card_type=CardType.CREATURE,
    colors={Color.GREEN},
    text="Trample.",
    power=3, toughness=3,
    keywords=[Keyword.TRAMPLE]
)

BALOTH = Card(
    id="baloth", name="Balloth Wurm",
    mana_cost=ManaCost(green=3, generic=2), card_type=CardType.CREATURE,
    colors={Color.GREEN},
    text="Trample.",
    power=6, toughness=6,
    keywords=[Keyword.TRAMPLE]
)


# ─────────────────────────────────────────────
# Cartas Pretas (Black)
# ─────────────────────────────────────────────

THOUGHTSEIZE = Card(
    id="thoughtseize", name="Thoughtseize",
    mana_cost=ManaCost(black=1), card_type=CardType.SORCERY,
    colors={Color.BLACK},
    text="Target player discards a non-land card.",
    effects=[SpellEffect(EffectType.DAMAGE, 2, target_type=TargetType.PLAYER)]  # simplificado como dano
)

DOOM_BLADE = Card(
    id="doom_blade", name="Doom Blade",
    mana_cost=ManaCost(black=1, generic=1), card_type=CardType.INSTANT,
    colors={Color.BLACK},
    text="Destroy target nonblack creature.",
    effects=[SpellEffect(EffectType.DESTROY_CREATURE, target_type=TargetType.CREATURE)]
)

VAMPIRE_NOBLE = Card(
    id="vampire_noble", name="Vampire Noble",
    mana_cost=ManaCost(black=2, generic=1), card_type=CardType.CREATURE,
    colors={Color.BLACK},
    text="Lifelink.",
    power=3, toughness=3,
    keywords=[Keyword.LIFELINK]
)

DARK_IMP = Card(
    id="dark_imp", name="Dark Imp",
    mana_cost=ManaCost(black=1), card_type=CardType.CREATURE,
    colors={Color.BLACK},
    text="Menace.",
    power=2, toughness=1,
    keywords=[Keyword.MENACE]
)

SHADOW_SLAYER = Card(
    id="shadow_slayer", name="Shadow Slayer",
    mana_cost=ManaCost(black=2), card_type=CardType.CREATURE,
    colors={Color.BLACK},
    text="Deathtouch.",
    power=2, toughness=2,
    keywords=[Keyword.DEATHTOUCH]
)

BONE_PICKER = Card(
    id="bone_picker", name="Bone Picker",
    mana_cost=ManaCost(black=3, generic=1), card_type=CardType.CREATURE,
    colors={Color.BLACK},
    text="Flying. When Bone Picker enters, target opponent discards a card.",
    power=3, toughness=2,
    keywords=[Keyword.FLYING],
    effects=[SpellEffect(EffectType.DAMAGE, 1, target_type=TargetType.PLAYER)]
)

DRAIN_LIFE = Card(
    id="drain_life", name="Drain Life",
    mana_cost=ManaCost(black=1, generic=1), card_type=CardType.SORCERY,
    colors={Color.BLACK},
    text="Drain Life deals 3 damage to any target. You gain life equal to the damage dealt.",
    effects=[SpellEffect(EffectType.DAMAGE, 3, target_type=TargetType.CREATURE_OR_PLAYER),
             SpellEffect(EffectType.GAIN_LIFE, 3)]
)


# ─────────────────────────────────────────────
# Cartas Azuis (Blue)
# ─────────────────────────────────────────────

COUNTERSPELL = Card(
    id="counterspell", name="Counterspell",
    mana_cost=ManaCost(blue=2), card_type=CardType.INSTANT,
    colors={Color.BLUE},
    text="Counter target spell.",
    effects=[SpellEffect(EffectType.COUNTER)]
)

AIR_ELEMENTAL = Card(
    id="air_elemental", name="Air Elemental",
    mana_cost=ManaCost(blue=3, generic=1), card_type=CardType.CREATURE,
    colors={Color.BLUE},
    text="Flying.",
    power=4, toughness=4,
    keywords=[Keyword.FLYING]
)

MAHAMILI = Card(
    id="mahamili", name="Mahamili Djinn",
    mana_cost=ManaCost(blue=3), card_type=CardType.CREATURE,
    colors={Color.BLUE},
    text="Flash. Flying.",
    power=2, toughness=3,
    keywords=[Keyword.FLASH, Keyword.FLYING]
)

MIND_ROTATE = Card(
    id="mind_rotate", name="Mind Rotate",
    mana_cost=ManaCost(blue=2, generic=1), card_type=CardType.SORCERY,
    colors={Color.BLUE},
    text="Target player puts the top 3 cards of their library into their graveyard.",
    effects=[SpellEffect(EffectType.MILL, 3, target_type=TargetType.PLAYER)]
)

PHANTASMAL_BEAR = Card(
    id="phantasmal_bear", name="Phantasmal Bear",
    mana_cost=ManaCost(blue=1), card_type=CardType.CREATURE,
    colors={Color.BLUE},
    text="A simple 1/1 flyer.",
    power=1, toughness=1,
    keywords=[Keyword.FLYING]
)


# ─────────────────────────────────────────────
# Cartas Multicoloridas
# ─────────────────────────────────────────────

KNIGHT_OF_THE_WHITE = Card(
    id="knight_of_white", name="Knight of the White Orchid",
    mana_cost=ManaCost(white=2), card_type=CardType.CREATURE,
    colors={Color.WHITE},
    text="First strike. When enters, search for a basic land.",
    power=2, toughness=2,
    keywords=[Keyword.FIRST_STRIKE],
    effects=[SpellEffect(EffectType.ADD_MANA, 1)]
)

BARKTOOTH = Card(
    id="barktooth", name="Barktooth Warbeard",
    mana_cost=ManaCost(green=1, red=1), card_type=CardType.CREATURE,
    colors={Color.GREEN, Color.RED},
    text="Haste. Trample.",
    power=3, toughness=2,
    keywords=[Keyword.HASTE, Keyword.TRAMPLE]
)


# ─────────────────────────────────────────────
# Dicionário de todas as cartas
# ─────────────────────────────────────────────

ALL_CARDS = {
    # Terrenos
    "plains": PLAINS, "island": ISLAND, "swamp": SWAMP,
    "mountain": MOUNTAIN, "forest": FOREST,
    # Red
    "lightning_bolt": LIGHTNING_BOLT, "lava_spike": LAVA_SPIKE,
    "chain_lightning": CHAIN_LIGHTNING, "goblin_guide": GOBLIN_GUIDE,
    "monastic_mentor": MONASTIC_MENTOR, "savage_twist": SAVAGE_TWIST,
    "skullraid": SKULLRAID,
    # White
    "healing_salve": LLANOWAR_HEALBOT, "swords_to_plowshares": SWORDS_TO_PLOWSHARES,
    "day_of_judgment": ELSPETH_TALENT, "guardian_of_solitude": GUARDIAN_OF_SOLITUDE,
    "samite_healer": SAMITE_HEALER, "thraben_banner": THRaben_BENCH,
    # Green
    "grizzly_bears": GRIZZLY_BEARS, "tarmogoyf": TARMAGOID,
    "bird_of_paradise": BIRD_OF_PARADISE, "elves": ELVES_OF_DEEPENING,
    "harmonize": COLLECTIVE_UNCONSCIOUS, "overcome": OVERCOME,
    "wood_elephant": WOOD_ELEPHANT, "baloth": BALOTH,
    # Black
    "thoughtseize": THOUGHTSEIZE, "doom_blade": DOOM_BLADE,
    "vampire_noble": VAMPIRE_NOBLE, "dark_imp": DARK_IMP,
    "shadow_slayer": SHADOW_SLAYER, "bone_picker": BONE_PICKER,
    "drain_life": DRAIN_LIFE,
    # Blue
    "counterspell": COUNTERSPELL, "air_elemental": AIR_ELEMENTAL,
    "mahamili": MAHAMILI, "mind_rotate": MIND_ROTATE,
    "phantasmal_bear": PHANTASMAL_BEAR,
    # Multi
    "knight_of_white": KNIGHT_OF_THE_WHITE, "barktooth": BARKTOOTH,
    # Green pump (Giant Growth é verde na verdade, vamos corrigir)
    "giant_growth": GIANT_GROWTH,
}


def get_card(card_id: str) -> Card:
    """Retorna uma cópia fresca da carta pelo ID."""
    if card_id in ALL_CARDS:
        return ALL_CARDS[card_id].copy()
    raise ValueError(f"Carta não encontrada: {card_id}")
