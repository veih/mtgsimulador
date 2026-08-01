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
        card_type=CardType.LAND,
        colors=set(), text=f"Tap: add {color.value}",
        is_land=True, land_mana={color}
    )


def _dual_land(name: str, colors: set, text: str = "") -> Card:
    """Cria um terreno dual (entra virado ou paga vida)."""
    return Card(
        id=name.lower().replace(" ", "_").replace("'", "").replace(",", ""),
        name=name, mana_cost=ManaCost(),
        card_type=CardType.LAND,
        colors=set(), text=text or f"Tap: add one mana of {' or '.join(c.value for c in colors)}.",
        is_land=True, land_mana=colors
    )


def _utility_land(name: str, colors: set, card_id: str = "", text: str = "") -> Card:
    """Cria terreno utilitário (não-básico)."""
    cid = card_id or name.lower().replace(" ", "_").replace("'", "").replace(",", "").replace(".", "")
    return Card(
        id=cid,
        name=name, mana_cost=ManaCost(),
        card_type=CardType.LAND,
        colors=set(), text=text,
        is_land=True, land_mana=colors if colors else {Color.COLORLESS}
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


# ─────────────────────────────────────────────
# Cartas do Amulet Titan
# ─────────────────────────────────────────────

PRIMEVAL_TITAN = Card(
    id="primeval_titan", name="Primeval Titan",
    mana_cost=ManaCost(green=2, generic=4), card_type=CardType.CREATURE,
    colors={Color.GREEN},
    text="Trample. Whenever Primeval Titan enters or attacks, search your library for up to two land cards, put them onto the battlefield tapped, then shuffle.",
    power=6, toughness=6,
    keywords=[Keyword.TRAMPLE]
)

SIMIAN_SPIRIT_GUIDE = Card(
    id="simian_spirit_guide", name="Simian Spirit Guide",
    mana_cost=ManaCost(red=1, generic=2), card_type=CardType.CREATURE,
    colors={Color.RED},
    text="Exile Simian Spirit Guide from your hand: Add {R}.",
    power=2, toughness=2
)

GOBLIN_ENGINEER = Card(
    id="goblin_engineer", name="Goblin Engineer",
    mana_cost=ManaCost(red=1, generic=1), card_type=CardType.CREATURE,
    colors={Color.RED},
    text="When Goblin Engineer enters, you may search your library for an artifact card with mana value 3 or less, put it into your graveyard, then shuffle.",
    power=1, toughness=2
)

ANCIENT_STIRRINGS = Card(
    id="ancient_stirrings", name="Ancient Stirrings",
    mana_cost=ManaCost(green=1), card_type=CardType.SORCERY,
    colors={Color.GREEN},
    text="Look at the top five cards of your library. You may reveal a colorless card from among them and put it into your hand. Put the rest on the bottom in any order.",
    effects=[SpellEffect(EffectType.DRAW_CARD, 1)]
)

SYLVAN_SCRYING = Card(
    id="sylvan_scrying", name="Sylvan Scrying",
    mana_cost=ManaCost(green=1, generic=1), card_type=CardType.SORCERY,
    colors={Color.GREEN},
    text="Search your library for any land card, reveal it, put it into your hand, then shuffle.",
    effects=[SpellEffect(EffectType.DRAW_CARD, 1)]
)

EXPEDITION_MAP = Card(
    id="expedition_map", name="Expedition Map",
    mana_cost=ManaCost(generic=1), card_type=CardType.ARTIFACT,
    colors=set(),
    text="{2}, Tap, Sacrifice Expedition Map: Search your library for any land card, reveal it, put it into your hand, then shuffle.",
    effects=[SpellEffect(EffectType.DRAW_CARD, 1)]
)

AMULET_OF_VIGOR = Card(
    id="amulet_of_vigor", name="Amulet of Vigor",
    mana_cost=ManaCost(generic=1), card_type=CardType.ARTIFACT,
    colors=set(),
    text="Whenever a permanent enters the battlefield tapped and under your control, untap it."
)

URZAS_SAGA = Card(
    id="urzas_saga", name="Urza's Saga",
    mana_cost=ManaCost(), card_type=CardType.ENCHANTMENT,
    colors=set(),
    text="Enchantment — Saga. (As this Saga enters and after your draw step, add a lore counter. Sacrifice after III.) I — Add {C}{C}. II — You may search your library for an artifact card with mana value 0 or 1. III — Create a 0/0 colorless Construct token.",
    is_land=False
)

ELDRAZI_TEMPLE = _utility_land(
    "Eldrazi Temple", {Color.COLORLESS}, "eldrazi_temple",
    "Tap: Add {C}. Tap: Add {C}{C}. Spend this mana only to cast Eldrazi spells or activate abilities of Eldrazi."
)

CLOUDPOST = _utility_land(
    "Cloudpost", {Color.COLORLESS}, "cloudpost",
    "Tap: Add {C} for each Locus on the battlefield."
)

TOLARIA_WEST = _utility_land(
    "Tolaria West", {Color.BLUE}, "tolaria_west",
    "Tap: Add {U}. Transmute {1}{U}{U}."
)

VALAKUT = _utility_land(
    "Valakut, the Molten Pinnacle", {Color.RED}, "valakut_the_molten_pinnacle",
    "Valakut enters tapped. Tap: Add {R}. Whenever a Mountain enters under your control, if you control at least 5 other Mountains, Valakut deals 3 damage to any target."
)


# ─────────────────────────────────────────────
# Terrenos duais dos decks Modern
# ─────────────────────────────────────────────

SEACHROME_COAST = _dual_land("Seachrome Coast", {Color.WHITE, Color.BLUE})
WATERY_GRAVE = _dual_land("Watery Grave", {Color.BLUE, Color.BLACK})
HALLOWED_FOUNTAIN = _dual_land("Hallowed Fountain", {Color.WHITE, Color.BLUE})
GODLESS_SHRINE = _dual_land("Godless Shrine", {Color.WHITE, Color.BLACK})
DARKSLICK_SHORES = _dual_land("Darkslick Shores", {Color.BLUE, Color.BLACK})
GEMSTONE_MINE = _utility_land("Gemstone Mine", {Color.WHITE, Color.BLUE, Color.BLACK, Color.RED, Color.GREEN}, "gemstone_mine", "Tap: Add one mana of any color. Remove a mining counter.")
OTAWARA = _utility_land("Otawara, Soaring City", {Color.BLUE}, "otawara_soaring_city", "Tap: Add {U}. Channel — {X}{U}{U}: Return up to one target artifact, creature, enchantment, or planeswalker to its owner's hand.")


# ─────────────────────────────────────────────
# Cartas Ad Nauseam (já parcialmente definidas acima)
# ─────────────────────────────────────────────

AD_NAUSEAM = Card(
    id="ad_nauseam", name="Ad Nauseam",
    mana_cost=ManaCost(black=2, white=1, generic=2), card_type=CardType.INSTANT,
    colors={Color.BLACK, Color.WHITE},
    text="Reveal the top card of your library and put it into your hand. You lose life equal to its mana value. You may repeat this process any number of times.",
    effects=[]
)

ANGELS_GRACE = Card(
    id="angels_grace", name="Angel's Grace",
    mana_cost=ManaCost(white=1), card_type=CardType.INSTANT,
    colors={Color.WHITE},
    text="Split second. You can't lose the game this turn and your opponents can't win the game this turn. Until end of turn, damage that would reduce your life total to less than 1 reduces it to 1 instead.",
    effects=[]
)

PHYREXIAN_UNLIFE = Card(
    id="phyrexian_unlife", name="Phyrexian Unlife",
    mana_cost=ManaCost(white=2, generic=1), card_type=CardType.ENCHANTMENT,
    colors={Color.WHITE},
    text="You don't lose the game for having 0 or less life. As long as your life total is 0 or less, you're poisoned.",
    effects=[]
)

LOTUS_BLOOM = Card(
    id="lotus_bloom", name="Lotus Bloom",
    mana_cost=ManaCost(), card_type=CardType.ARTIFACT,
    colors=set(),
    text="Suspend 3 — {0}. Sacrifice Lotus Bloom: Add three mana of any one color.",
    effects=[]
)

PACT_OF_NEGATION = Card(
    id="pact_of_negation", name="Pact of Negation",
    mana_cost=ManaCost(), card_type=CardType.INSTANT,
    colors=set(),
    text="Counter target spell. At the beginning of your next upkeep, pay {3}{U}{U}. If you don't, you lose the game.",
    effects=[]
)

FORCE_OF_NEGATION = Card(
    id="force_of_negation", name="Force of Negation",
    mana_cost=ManaCost(blue=2, generic=1), card_type=CardType.INSTANT,
    colors={Color.BLUE},
    text="If it's not your turn, you may exile a blue card from your hand rather than pay this spell's mana cost. Counter target noncreature spell. If this spell was cast during your turn, draw a card.",
    effects=[]
)

PREORDAIN = Card(
    id="preordain", name="Preordain",
    mana_cost=ManaCost(blue=1), card_type=CardType.SORCERY,
    colors={Color.BLUE},
    text="Scry 2, then draw a card.",
    effects=[SpellEffect(EffectType.DRAW_CARD, 1)]
)

PROFANE_TUTOR = Card(
    id="profane_tutor", name="Profane Tutor",
    mana_cost=ManaCost(), card_type=CardType.SORCERY,
    colors=set(),
    text="Suspend 2 — {1}{B}. Search your library for a card and put it into your hand, then shuffle.",
    effects=[SpellEffect(EffectType.DRAW_CARD, 1)]
)

THASSAS_ORACLE = Card(
    id="thassas_oracle", name="Thassa's Oracle",
    mana_cost=ManaCost(blue=2), card_type=CardType.CREATURE,
    colors={Color.BLUE},
    text="When Thassa's Oracle enters, look at the top X cards of your library, where X is your devotion to blue. Put up to one of them on top and the rest on the bottom. If X is greater than or equal to the number of cards in your library, you win the game.",
    power=1, toughness=3
)

SPOILS_OF_THE_VAULT_CARD = Card(
    id="spoils_of_the_vault", name="Spoils of the Vault",
    mana_cost=ManaCost(black=1), card_type=CardType.INSTANT,
    colors={Color.BLACK},
    text="Name a card. Reveal cards from the top of your library until you reveal the named card, then put that card into your hand. You lose 1 life for each card revealed this way.",
    effects=[]
)

PATH_TO_EXILE = Card(
    id="path_to_exile", name="Path to Exile",
    mana_cost=ManaCost(white=1), card_type=CardType.INSTANT,
    colors={Color.WHITE},
    text="Exile target creature. Its controller may search their library for a basic land card, put it onto the battlefield tapped, then shuffle.",
    effects=[SpellEffect(EffectType.EXILE, target_type=TargetType.CREATURE)]
)

CONCEALED_COURTYARD_CARD = Card(
    id="concealed_courtyard", name="Concealed Courtyard",
    mana_cost=ManaCost(), card_type=CardType.LAND,
    colors=set(), text="Concealed Courtyard enters untapped if you control two or fewer other lands. Tap: Add W or B.",
    is_land=True, land_mana={Color.WHITE, Color.BLACK}
)


ALL_CARDS = {
    # Terrenos básicos
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
    "giant_growth": GIANT_GROWTH,
    # ── Amulet Titan ──
    "primeval_titan": PRIMEVAL_TITAN,
    "simian_spirit_guide": SIMIAN_SPIRIT_GUIDE,
    "goblin_engineer": GOBLIN_ENGINEER,
    "ancient_stirrings": ANCIENT_STIRRINGS,
    "sylvan_scrying": SYLVAN_SCRYING,
    "expedition_map": EXPEDITION_MAP,
    "amulet_of_vigor": AMULET_OF_VIGOR,
    "urzas_saga": URZAS_SAGA,
    "eldrazi_temple": ELDRAZI_TEMPLE,
    "cloudpost": CLOUDPOST,
    "tolaria_west": TOLARIA_WEST,
    "valakut_the_molten_pinnacle": VALAKUT,
    # ── Ad Nauseam ──
    "ad_nauseam": AD_NAUSEAM,
    "angels_grace": ANGELS_GRACE,
    "phyrexian_unlife": PHYREXIAN_UNLIFE,
    "lotus_bloom": LOTUS_BLOOM,
    "pact_of_negation": PACT_OF_NEGATION,
    "force_of_negation": FORCE_OF_NEGATION,
    "preordain": PREORDAIN,
    "profane_tutor": PROFANE_TUTOR,
    "thassas_oracle": THASSAS_ORACLE,
    "sleight_of_hand": Card(
        id="sleight_of_hand", name="Sleight of Hand",
        mana_cost=ManaCost(blue=1), card_type=CardType.SORCERY,
        colors={Color.BLUE},
        text="Look at the top two cards of your library. Put one into your hand and the other on the bottom.",
        effects=[SpellEffect(EffectType.DRAW_CARD, 1)]
    ),
    "spoils_of_the_vault": SPOILS_OF_THE_VAULT_CARD,
    "path_to_exile": PATH_TO_EXILE,
    # ── Terrenos duais / utilitários ──
    "seachrome_coast": SEACHROME_COAST,
    "concealed_courtyard": CONCEALED_COURTYARD_CARD,
    "darkslick_shores": DARKSLICK_SHORES,
    "hallowed_fountain": HALLOWED_FOUNTAIN,
    "watery_grave": WATERY_GRAVE,
    "godless_shrine": GODLESS_SHRINE,
    "gemstone_mine": GEMSTONE_MINE,
    "otawara_soaring_city": OTAWARA,
}


def get_card(card_id: str) -> Card:
    """Retorna uma cópia fresca da carta pelo ID."""
    if card_id in ALL_CARDS:
        return ALL_CARDS[card_id].copy()
    raise ValueError(f"Carta não encontrada: {card_id}")


# Mapeamento de nomes para IDs (para importação de decks)
CARD_NAME_TO_ID = {
    card.name: card_id for card_id, card in ALL_CARDS.items()
}
# Adiciona variações em minúsculo
for card_id, card in ALL_CARDS.items():
    CARD_NAME_TO_ID[card.name.lower()] = card_id
