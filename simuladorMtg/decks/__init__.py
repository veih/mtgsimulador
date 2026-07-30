"""
MTG Match Simulator - Decks Pre-Construidos
Decks exemplo para testar o simulador.
Usa lazy loading - decks so sao construidos quando solicitados.
"""

from src.cards_db import get_card
from src.card import Color

# ─────────────────────────────────────────────
# Receitas dos decks (so construidos sob demanda)
# ─────────────────────────────────────────────

_DECK_RECIPES = {
    "Red Deck Wins": {
        "cards": [
            ("lightning_bolt", 4), ("lava_spike", 4), ("chain_lightning", 4),
            ("goblin_guide", 4), ("monastic_mentor", 4), ("skullraid", 4),
            ("grizzly_bears", 4), ("dark_imp", 4), ("phantasmal_bear", 4),
        ],
        "land": "mountain", "land_count": 24,
    },
    "White Weenie": {
        "cards": [
            ("goblin_guide", 4), ("monastic_mentor", 4), ("guardian_of_solitude", 4),
            ("samite_healer", 4), ("knight_of_white", 4), ("healing_salve", 4),
            ("swords_to_plowshares", 4), ("day_of_judgment", 2), ("thraben_banner", 4),
            ("grizzly_bears", 4),
        ],
        "land": "plains", "land_count": 20,
    },
    "Green Stompy": {
        "cards": [
            ("grizzly_bears", 4), ("tarmogoyf", 4), ("bird_of_paradise", 4),
            ("elves", 4), ("wood_elephant", 4), ("baloth", 4),
            ("giant_growth", 4), ("overcome", 4), ("harmonize", 2), ("barktooth", 4),
        ],
        "land": "forest", "land_count": 22,
    },
    "Black Control": {
        "cards": [
            ("thoughtseize", 4), ("doom_blade", 4), ("vampire_noble", 4),
            ("dark_imp", 4), ("shadow_slayer", 4), ("bone_picker", 4),
            ("drain_life", 4), ("monastic_mentor", 4), ("goblin_guide", 4),
        ],
        "land": "swamp", "land_count": 22,
    },
    "Blue Tempo": {
        "cards": [
            ("counterspell", 4), ("air_elemental", 4), ("phantasmal_bear", 4),
            ("mind_rotate", 4), ("monastic_mentor", 4), ("goblin_guide", 4),
            ("grizzly_bears", 4), ("giant_growth", 4), ("healing_salve", 4),
        ],
        "land": "island", "land_count": 22,
    },
    "Gruul Aggro": {
        "cards": [
            ("lightning_bolt", 4), ("grizzly_bears", 4), ("tarmogoyf", 4),
            ("wood_elephant", 4), ("baloth", 4), ("barktooth", 4),
            ("giant_growth", 4), ("goblin_guide", 4), ("lava_spike", 4),
            ("chain_lightning", 4),
        ],
        "land": None, "land_count": 0,  # calculado dinamicamente
        "lands": [("mountain", 10), ("forest", 12)],
    },
}

# Cache dos decks construidos
_deck_cache = {}


def _build_deck(recipe: dict) -> list:
    """Constroi um deck a partir de uma receita."""
    deck = []
    for card_id, qty in recipe["cards"]:
        for _ in range(qty):
            deck.append(get_card(card_id))

    # Adiciona terrenos
    if recipe.get("lands"):
        for land_id, qty in recipe["lands"]:
            for _ in range(qty):
                deck.append(get_card(land_id))
    elif recipe.get("land"):
        for _ in range(recipe["land_count"]):
            deck.append(get_card(recipe["land"]))

    # Preenche se necessario
    while len(deck) < 60:
        deck.append(get_card(recipe.get("land", "forest")))

    return deck[:60]


def get_deck(name: str) -> list:
    """Retorna um deck pelo nome (com cache)."""
    if name not in _DECK_RECIPES:
        available = ', '.join(_DECK_RECIPES.keys())
        raise ValueError(f"Deck nao encontrado: {name}. Decks: {available}")

    if name not in _deck_cache:
        _deck_cache[name] = _build_deck(_DECK_RECIPES[name])

    return [c.copy() for c in _deck_cache[name]]


def list_decks() -> list:
    """Lista todos os decks disponiveis."""
    return list(_DECK_RECIPES.keys())


class _LazyDeckDict:
    """Dicionario lazy que so carrega decks quando acessados."""

    def __contains__(self, key):
        return key in _DECK_RECIPES

    def __getitem__(self, key):
        if key not in _DECK_RECIPES:
            raise KeyError(key)
        return get_deck(key)

    def keys(self):
        return _DECK_RECIPES.keys()

    def items(self):
        for name in _DECK_RECIPES:
            yield name, get_deck(name)

    def values(self):
        for name in _DECK_RECIPES:
            yield get_deck(name)

    def __iter__(self):
        return iter(_DECK_RECIPES)

    def __len__(self):
        return len(_DECK_RECIPES)


ALL_DECKS = _LazyDeckDict()
