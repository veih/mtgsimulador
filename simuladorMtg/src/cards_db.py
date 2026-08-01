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

# Shocklands — Jund
BLOOD_CRYPT = _dual_land("Blood Crypt", {Color.BLACK, Color.RED}, "As this land enters, you may pay 2 life. If you don't, it enters tapped. {T}: Add {B} or {R}.")
OVERGROWN_TOMB = _dual_land("Overgrown Tomb", {Color.BLACK, Color.GREEN}, "As this land enters, you may pay 2 life. If you don't, it enters tapped. {T}: Add {B} or {G}.")
STOMPING_GROUND = _dual_land("Stomping Ground", {Color.RED, Color.GREEN}, "As this land enters, you may pay 2 life. If you don't, it enters tapped. {T}: Add {R} or {G}.")
# Shocklands — Izzet Murktide
STEAM_VENTS = _dual_land("Steam Vents", {Color.BLUE, Color.RED}, "As this land enters, you may pay 2 life. If you don't, it enters tapped. {T}: Add {U} or {R}.")
SACRED_FOUNDRY = _dual_land("Sacred Foundry", {Color.RED, Color.WHITE}, "As this land enters, you may pay 2 life. If you don't, it enters tapped. {T}: Add {R} or {W}.")
# Fetchlands
SCALDING_TARN = _utility_land("Scalding Tarn", {Color.BLUE, Color.RED}, "scalding_tarn", "{T}, Pay 1 life, Sacrifice: Search library for Island or Mountain, put it onto battlefield, then shuffle.")
BLOODSTAINED_MIRE = _utility_land("Bloodstained Mire", {Color.BLACK, Color.RED}, "bloodstained_mire", "{T}, Pay 1 life, Sacrifice: Search library for Swamp or Mountain, put it onto battlefield, then shuffle.")
# Fast lands
SPIREBLUFF_CANAL = _dual_land("Spirebluff Canal", {Color.BLUE, Color.RED}, "Enters tapped unless you control two or fewer other lands. {T}: Add {U} or {R}.")
BLACKCLEAVE_CLIFFS = _dual_land("Blackcleave Cliffs", {Color.BLACK, Color.RED}, "Enters tapped unless you control two or fewer other lands. {T}: Add {B} or {R}.")
# Utility lands
BAZAAR_OF_BAGHDAD = _utility_land("Bazaar of Baghdad", {Color.COLORLESS}, "bazaar_of_baghdad", "{T}: Draw two cards, then discard three cards.")
WASTES = _utility_land("Wastes", {Color.COLORLESS}, "wastes", "{T}: Add {C}.")
# Tron lands
URZAS_MINE = _utility_land("Urza's Mine", {Color.COLORLESS}, "urzas_mine", "{T}: Add {C}. If you control Urza's Power-Plant and Urza's Tower, add {C}{C} instead.")
URZAS_POWER_PLANT = _utility_land("Urza's Power Plant", {Color.COLORLESS}, "urzas_power_plant", "{T}: Add {C}. If you control Urza's Mine and Urza's Tower, add {C}{C} instead.")
URZAS_TOWER = _utility_land("Urza's Tower", {Color.COLORLESS}, "urzas_tower", "{T}: Add {C}. If you control Urza's Mine and Urza's Power-Plant, add {C}{C}{C} instead.")


# ─────────────────────────────────────────────
# Jund
# ─────────────────────────────────────────────

BLOODBRAID_ELF = Card(
    id="bloodbraid_elf", name="Bloodbraid Elf",
    mana_cost=ManaCost(red=1, green=1, generic=2), card_type=CardType.CREATURE,
    colors={Color.RED, Color.GREEN},
    text="Haste. Cascade.",
    power=3, toughness=2, keywords=[Keyword.HASTE]
)

DARK_CONFIDANT = Card(
    id="dark_confidant", name="Dark Confidant",
    mana_cost=ManaCost(black=1, generic=1), card_type=CardType.CREATURE,
    colors={Color.BLACK},
    text="At the beginning of your upkeep, reveal the top card of your library and put that card into your hand. You lose life equal to its mana value.",
    power=2, toughness=1
)

KOLAGHANS_COMMAND = Card(
    id="kolahans_command", name="Kolaghan's Command",
    mana_cost=ManaCost(black=1, red=1, generic=1), card_type=CardType.INSTANT,
    colors={Color.BLACK, Color.RED},
    text="Choose two — Return target creature from graveyard to hand; target player discards a card; destroy target artifact; deal 2 damage to any target.",
    effects=[SpellEffect(EffectType.DAMAGE, 2, target_type=TargetType.CREATURE_OR_PLAYER)]
)

FATAL_PUSH = Card(
    id="fatal_push", name="Fatal Push",
    mana_cost=ManaCost(black=1), card_type=CardType.INSTANT,
    colors={Color.BLACK},
    text="Destroy target creature if it has mana value 2 or less. Revolt — Destroy that creature if it has mana value 4 or less instead.",
    effects=[SpellEffect(EffectType.DESTROY_CREATURE, target_type=TargetType.CREATURE)]
)

INQUISITION_OF_KOZILEK = Card(
    id="inquisition_of_kozilek", name="Inquisition of Kozilek",
    mana_cost=ManaCost(black=1), card_type=CardType.SORCERY,
    colors={Color.BLACK},
    text="Target player reveals their hand. You choose a nonland card from it with mana value 3 or less. That player discards that card.",
    effects=[]
)

WRENN_AND_SIX = Card(
    id="wrenn_and_six", name="Wrenn and Six",
    mana_cost=ManaCost(red=1, green=1), card_type=CardType.PLANESWALKER,
    colors={Color.RED, Color.GREEN},
    text="+1: Return up to one target land card from your graveyard to your hand. −1: Deals 1 damage to any target. −7: Instant and sorcery cards in your graveyard have retrace.",
    effects=[]
)

LILIANA_OF_THE_VEIL = Card(
    id="liliana_of_the_veil", name="Liliana of the Veil",
    mana_cost=ManaCost(black=2, generic=1), card_type=CardType.PLANESWALKER,
    colors={Color.BLACK},
    text="+1: Each player discards a card. −2: Target player sacrifices a creature. −6: Separate all permanents target player controls into two piles. That player sacrifices all permanents in the pile of their choice.",
    effects=[]
)


# ─────────────────────────────────────────────
# Izzet Murktide
# ─────────────────────────────────────────────

MURKTIDE_REGENT = Card(
    id="murktide_regent", name="Murktide Regent",
    mana_cost=ManaCost(blue=2, generic=5), card_type=CardType.CREATURE,
    colors={Color.BLUE},
    text="Delve. Flying. Enters with a +1/+1 counter for each instant/sorcery exiled with it. Whenever an instant or sorcery leaves your graveyard, put a +1/+1 counter on this.",
    power=3, toughness=3, keywords=[Keyword.FLYING]
)

RAGAVAN = Card(
    id="ragavan_nimble_pilferer", name="Ragavan, Nimble Pilferer",
    mana_cost=ManaCost(red=1), card_type=CardType.CREATURE,
    colors={Color.RED},
    text="Whenever Ragavan deals combat damage to a player, create a Treasure token and exile the top card of that player's library. Dash {1}{R}.",
    power=2, toughness=1, keywords=[Keyword.HASTE]
)

DRAGONS_RAGE_CHANNELER = Card(
    id="dragons_rage_channeler", name="Dragon's Rage Channeler",
    mana_cost=ManaCost(red=1), card_type=CardType.CREATURE,
    colors={Color.RED},
    text="Whenever you cast a noncreature spell, surveil 1. Delirium — As long as there are four or more card types in your graveyard, gets +2/+2, has flying, and attacks each combat if able.",
    power=1, toughness=1
)

EXPRESSIVE_ITERATION = Card(
    id="expressive_iteration", name="Expressive Iteration",
    mana_cost=ManaCost(blue=1, red=1), card_type=CardType.SORCERY,
    colors={Color.BLUE, Color.RED},
    text="Look at the top three cards of your library. Put one into your hand, one on the bottom, and exile one. You may play the exiled card this turn.",
    effects=[SpellEffect(EffectType.DRAW_CARD, 1)]
)

SPELL_SNARE = Card(
    id="spell_snare", name="Spell Snare",
    mana_cost=ManaCost(blue=1), card_type=CardType.INSTANT,
    colors={Color.BLUE},
    text="Counter target spell with mana value 2.",
    effects=[SpellEffect(EffectType.COUNTER)]
)

UNHOLY_HEAT = Card(
    id="unholy_heat", name="Unholy Heat",
    mana_cost=ManaCost(red=1), card_type=CardType.INSTANT,
    colors={Color.RED},
    text="Unholy Heat deals 2 damage to target creature or planeswalker. Delirium — 6 damage instead.",
    effects=[SpellEffect(EffectType.DAMAGE, 2, target_type=TargetType.CREATURE)]
)

THOUGHT_SCOUR = Card(
    id="thought_scour", name="Thought Scour",
    mana_cost=ManaCost(blue=1), card_type=CardType.INSTANT,
    colors={Color.BLUE},
    text="Target player mills two cards. Draw a card.",
    effects=[SpellEffect(EffectType.DRAW_CARD, 1)]
)


# ─────────────────────────────────────────────
# Hollow One
# ─────────────────────────────────────────────

HOLLOW_ONE = Card(
    id="hollow_one", name="Hollow One",
    mana_cost=ManaCost(generic=5), card_type=CardType.CREATURE,
    colors=set(),
    text="Costs {2} less for each card you've cycled or discarded this turn. Cycling {2}.",
    power=4, toughness=4
)

GOBLIN_CHARBELCHER = Card(
    id="goblin_charbelcher", name="Goblin Charbelcher",
    mana_cost=ManaCost(generic=4), card_type=CardType.ARTIFACT,
    colors=set(),
    text="{3}, {T}: Reveal cards from the top of your library until you reveal a land. Deal damage equal to nonland cards revealed. Put them on the bottom.",
    effects=[SpellEffect(EffectType.DAMAGE, 5, target_type=TargetType.CREATURE_OR_PLAYER)]
)

FLAME_SLASH = Card(
    id="flame_slash", name="Flame Slash",
    mana_cost=ManaCost(red=1), card_type=CardType.SORCERY,
    colors={Color.RED},
    text="Flame Slash deals 4 damage to target creature.",
    effects=[SpellEffect(EffectType.DAMAGE, 4, target_type=TargetType.CREATURE)]
)

FAITHLESS_LOOTING = Card(
    id="faithless_looting", name="Faithless Looting",
    mana_cost=ManaCost(red=1), card_type=CardType.SORCERY,
    colors={Color.RED},
    text="Draw two cards, then discard two cards. Flashback {2}{R}.",
    effects=[SpellEffect(EffectType.DRAW_CARD, 2)]
)

GURMAG_ANGLER = Card(
    id="gurmag_angler", name="Gurmag Angler",
    mana_cost=ManaCost(black=1, generic=6), card_type=CardType.CREATURE,
    colors={Color.BLACK},
    text="Delve.",
    power=5, toughness=5
)

MERCILESS_EXECUTIONER = Card(
    id="merciless_executioner", name="Merciless Executioner",
    mana_cost=ManaCost(black=1, generic=2), card_type=CardType.CREATURE,
    colors={Color.BLACK},
    text="When this creature enters, each player sacrifices a creature.",
    power=3, toughness=1
)

DREAD_RETURN = Card(
    id="dread_return", name="Dread Return",
    mana_cost=ManaCost(black=2, generic=2), card_type=CardType.SORCERY,
    colors={Color.BLACK},
    text="Return target creature card from your graveyard to the battlefield. Flashback — Sacrifice three creatures.",
    effects=[]
)

VENGEVINE = Card(
    id="vengevine", name="Vengevine",
    mana_cost=ManaCost(green=2, generic=2), card_type=CardType.CREATURE,
    colors={Color.GREEN},
    text="Haste. Whenever you cast a spell, if it's the second creature spell you cast this turn, you may return this from your graveyard to the battlefield.",
    power=4, toughness=3, keywords=[Keyword.HASTE]
)

BLOODGHAST = Card(
    id="bloodghast", name="Bloodghast",
    mana_cost=ManaCost(black=2), card_type=CardType.CREATURE,
    colors={Color.BLACK},
    text="Can't block. Has haste if opponent has 10 or less life. Landfall — Return from graveyard to battlefield.",
    power=2, toughness=1
)

BRIDGE_FROM_BELOW = Card(
    id="bridge_from_below", name="Bridge from Below",
    mana_cost=ManaCost(black=3), card_type=CardType.ENCHANTMENT,
    colors={Color.BLACK},
    text="Whenever a nontoken creature is put into your graveyard from the battlefield, if this card is in your graveyard, create a 2/2 black Zombie token.",
    effects=[]
)


# ─────────────────────────────────────────────
# Prowess
# ─────────────────────────────────────────────

MONASTERY_SWIFTSPEAR = Card(
    id="monastery_swiftspear", name="Monastery Swiftspear",
    mana_cost=ManaCost(red=1), card_type=CardType.CREATURE,
    colors={Color.RED},
    text="Haste. Prowess (whenever you cast a noncreature spell, +1/+1 until end of turn).",
    power=1, toughness=2, keywords=[Keyword.HASTE]
)

SOUL_SCAR_MAGE = Card(
    id="soulscar_mage", name="Soul-Scar Mage",
    mana_cost=ManaCost(red=1), card_type=CardType.CREATURE,
    colors={Color.RED},
    text="Prowess. If a source you control would deal noncombat damage to a creature an opponent controls, put that many -1/-1 counters on it instead.",
    power=1, toughness=2
)

EIDOLON_OF_THE_GREAT_REVEL = Card(
    id="eidolon_of_the_great_revel", name="Eidolon of the Great Revel",
    mana_cost=ManaCost(red=2), card_type=CardType.CREATURE,
    colors={Color.RED},
    text="Whenever a player casts a spell with mana value 3 or less, this creature deals 2 damage to that player.",
    power=2, toughness=2
)

LAVA_DART = Card(
    id="lava_dart", name="Lava Dart",
    mana_cost=ManaCost(red=1), card_type=CardType.INSTANT,
    colors={Color.RED},
    text="Lava Dart deals 1 damage to any target. Flashback — Sacrifice a Mountain.",
    effects=[SpellEffect(EffectType.DAMAGE, 1, target_type=TargetType.CREATURE_OR_PLAYER)]
)

RIFT_BOLT = Card(
    id="rift_bolt", name="Rift Bolt",
    mana_cost=ManaCost(red=1, generic=2), card_type=CardType.SORCERY,
    colors={Color.RED},
    text="Rift Bolt deals 3 damage to any target. Suspend 1 — {R}.",
    effects=[SpellEffect(EffectType.DAMAGE, 3, target_type=TargetType.CREATURE_OR_PLAYER)]
)

BURST_LIGHTNING = Card(
    id="burst_lightning", name="Burst Lightning",
    mana_cost=ManaCost(red=1), card_type=CardType.INSTANT,
    colors={Color.RED},
    text="Burst Lightning deals 2 damage to any target. Kicker {4} — 4 damage instead.",
    effects=[SpellEffect(EffectType.DAMAGE, 2, target_type=TargetType.CREATURE_OR_PLAYER)]
)

MISHRAS_BAUBLE = Card(
    id="mishras_bauble", name="Mishra's Bauble",
    mana_cost=ManaCost(), card_type=CardType.ARTIFACT,
    colors=set(),
    text="{T}, Sacrifice: Look at the top card of target player's library. Draw a card at the beginning of the next turn's upkeep.",
    effects=[]
)


# ─────────────────────────────────────────────
# Death's Shadow
# ─────────────────────────────────────────────

DEATHS_SHADOW = Card(
    id="deaths_shadow", name="Death's Shadow",
    mana_cost=ManaCost(black=1), card_type=CardType.CREATURE,
    colors={Color.BLACK},
    text="This creature gets -X/-X, where X is your life total.",
    power=13, toughness=13
)

TEMUR_BATTLE_RAGE = Card(
    id="temur_battle_rage", name="Temur Battle Rage",
    mana_cost=ManaCost(red=1, generic=1), card_type=CardType.INSTANT,
    colors={Color.RED},
    text="Target creature gains double strike until end of turn. Ferocious — also gains trample if you control a creature with power 4 or greater.",
    effects=[]
)

DAZE = Card(
    id="daze", name="Daze",
    mana_cost=ManaCost(blue=1, generic=1), card_type=CardType.INSTANT,
    colors={Color.BLUE},
    text="You may return an Island you control to its owner's hand rather than pay this spell's mana cost. Counter target spell unless its controller pays {1}.",
    effects=[SpellEffect(EffectType.COUNTER)]
)

DELIRIUM_SKEINS = Card(
    id="delirium_skeins", name="Delirium Skeins",
    mana_cost=ManaCost(black=1, generic=2), card_type=CardType.SORCERY,
    colors={Color.BLACK},
    text="Each player discards three cards.",
    effects=[]
)

STREET_WRAITH = Card(
    id="street_wraith", name="Street Wraith",
    mana_cost=ManaCost(black=2, generic=3), card_type=CardType.CREATURE,
    colors={Color.BLACK},
    text="Swampwalk. Cycling — Pay 2 life.",
    power=3, toughness=4
)


# ─────────────────────────────────────────────
# Tron
# ─────────────────────────────────────────────

KARN_LIBERATED = Card(
    id="karn_liberated", name="Karn Liberated",
    mana_cost=ManaCost(generic=7), card_type=CardType.PLANESWALKER,
    colors=set(),
    text="+4: Target player exiles a card from their hand. −3: Exile target permanent. −14: Restart the game, putting exiled Karn permanents onto the battlefield.",
    effects=[]
)

CHROMATIC_STAR = Card(
    id="chromatic_star", name="Chromatic Star",
    mana_cost=ManaCost(generic=1), card_type=CardType.ARTIFACT,
    colors=set(),
    text="{1}, {T}, Sacrifice: Add one mana of any color. When this goes to graveyard, draw a card.",
    effects=[]
)

CHROMATIC_SPHERE = Card(
    id="chromatic_sphere", name="Chromatic Sphere",
    mana_cost=ManaCost(generic=1), card_type=CardType.ARTIFACT,
    colors=set(),
    text="{1}, {T}, Sacrifice: Add one mana of any color. Draw a card.",
    effects=[SpellEffect(EffectType.DRAW_CARD, 1)]
)

OBLIVION_STONE = Card(
    id="oblivion_stone", name="Oblivion Stone",
    mana_cost=ManaCost(generic=3), card_type=CardType.ARTIFACT,
    colors=set(),
    text="{4}, {T}: Put a fate counter on target permanent. {5}, {T}, Sacrifice: Destroy each nonland permanent without a fate counter.",
    effects=[]
)

MINDSLAVER = Card(
    id="mindslaver", name="Mindslaver",
    mana_cost=ManaCost(generic=6), card_type=CardType.ARTIFACT,
    colors=set(),
    text="{4}, {T}, Sacrifice: You control target player during their next turn.",
    effects=[]
)

# Hollow One: Stirling Castle is not a real MTG card — replaced with a generic placeholder
STIRLING_CASTLE = _utility_land("Stirling Castle", {Color.COLORLESS}, "stirling_castle",
    "(Placeholder — not a real MTG card.) {T}: Add {C}.")



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

PENTAD_PRISM = Card(
    id="pentad_prism", name="Pentad Prism",
    mana_cost=ManaCost(generic=2), card_type=CardType.ARTIFACT,
    colors=set(),
    text="Pentad Prism enters the battlefield with two charge counters on it. Remove a charge counter from Pentad Prism: Add one mana of any color.",
    effects=[]
)

SERUM_VISIONS = Card(
    id="serum_visions", name="Serum Visions",
    mana_cost=ManaCost(blue=1), card_type=CardType.SORCERY,
    colors={Color.BLUE},
    text="Draw a card. Scry 2.",
    effects=[SpellEffect(EffectType.DRAW_CARD, 1)]
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
    "pentad_prism": PENTAD_PRISM,
    "serum_visions": SERUM_VISIONS,
    # ── Terrenos duais / utilitários ──
    "seachrome_coast": SEACHROME_COAST,
    "concealed_courtyard": CONCEALED_COURTYARD_CARD,
    "darkslick_shores": DARKSLICK_SHORES,
    "hallowed_fountain": HALLOWED_FOUNTAIN,
    "watery_grave": WATERY_GRAVE,
    "godless_shrine": GODLESS_SHRINE,
    "gemstone_mine": GEMSTONE_MINE,
    "otawara_soaring_city": OTAWARA,
    # ── Terrenos shocklands / fetchlands / fastlands ──
    "blood_crypt": BLOOD_CRYPT,
    "overgrown_tomb": OVERGROWN_TOMB,
    "stomping_ground": STOMPING_GROUND,
    "steam_vents": STEAM_VENTS,
    "sacred_foundry": SACRED_FOUNDRY,
    "scalding_tarn": SCALDING_TARN,
    "bloodstained_mire": BLOODSTAINED_MIRE,
    "spirebluff_canal": SPIREBLUFF_CANAL,
    "blackcleave_cliffs": BLACKCLEAVE_CLIFFS,
    "bazaar_of_baghdad": BAZAAR_OF_BAGHDAD,
    "wastes": WASTES,
    "urzas_mine": URZAS_MINE,
    "urzas_power_plant": URZAS_POWER_PLANT,
    "urzas_tower": URZAS_TOWER,
    "stirling_castle": STIRLING_CASTLE,
    # ── Jund ──
    "bloodbraid_elf": BLOODBRAID_ELF,
    "dark_confidant": DARK_CONFIDANT,
    "kolahans_command": KOLAGHANS_COMMAND,
    "fatal_push": FATAL_PUSH,
    "inquisition_of_kozilek": INQUISITION_OF_KOZILEK,
    "wrenn_and_six": WRENN_AND_SIX,
    "liliana_of_the_veil": LILIANA_OF_THE_VEIL,
    # ── Izzet Murktide ──
    "murktide_regent": MURKTIDE_REGENT,
    "ragavan_nimble_pilferer": RAGAVAN,
    "dragons_rage_channeler": DRAGONS_RAGE_CHANNELER,
    "expressive_iteration": EXPRESSIVE_ITERATION,
    "spell_snare": SPELL_SNARE,
    "unholy_heat": UNHOLY_HEAT,
    "thought_scour": THOUGHT_SCOUR,
    # ── Hollow One ──
    "hollow_one": HOLLOW_ONE,
    "goblin_charbelcher": GOBLIN_CHARBELCHER,
    "flame_slash": FLAME_SLASH,
    "faithless_looting": FAITHLESS_LOOTING,
    "gurmag_angler": GURMAG_ANGLER,
    "merciless_executioner": MERCILESS_EXECUTIONER,
    "dread_return": DREAD_RETURN,
    "vengevine": VENGEVINE,
    "bloodghast": BLOODGHAST,
    "bridge_from_below": BRIDGE_FROM_BELOW,
    # ── Prowess ──
    "monastery_swiftspear": MONASTERY_SWIFTSPEAR,
    "soulscar_mage": SOUL_SCAR_MAGE,
    "eidolon_of_the_great_revel": EIDOLON_OF_THE_GREAT_REVEL,
    "lava_dart": LAVA_DART,
    "rift_bolt": RIFT_BOLT,
    "burst_lightning": BURST_LIGHTNING,
    "mishras_bauble": MISHRAS_BAUBLE,
    # ── Death's Shadow ──
    "deaths_shadow": DEATHS_SHADOW,
    "temur_battle_rage": TEMUR_BATTLE_RAGE,
    "daze": DAZE,
    "delirium_skeins": DELIRIUM_SKEINS,
    "street_wraith": STREET_WRAITH,
    # ── Tron ──
    "karn_liberated": KARN_LIBERATED,
    "chromatic_star": CHROMATIC_STAR,
    "chromatic_sphere": CHROMATIC_SPHERE,
    "oblivion_stone": OBLIVION_STONE,
    "mindslaver": MINDSLAVER,
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
