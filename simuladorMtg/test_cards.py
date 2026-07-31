from deck_importer import create_card_from_scryfall, _load_scryfall_cards, _scryfall_cache

_load_scryfall_cards()
print(f"Total no cache: {len(_scryfall_cache)//2} cartas\n")

test_cards = [
    "Thassa's Oracle",
    "Ad Nauseam",
    "Preordain",
    "Force of Negation",
    "Path to Exile",
    "Seachrome Coast",
    "Concealed Courtyard",
    "Darkslick Shores",
    "Hallowed Fountain",
    "Watery Grave",
    "Godless Shrine",
    "Gemstone Mine",
    "Profane Tutor",
    "Sleight of Hand",
    "Spoils of the Vault",
    "Lotus Bloom",
    "Angel's Grace",
    "Phyrexian Unlife",
]

for name in test_cards:
    card = create_card_from_scryfall(name)
    status = "OK" if card else "NOT FOUND"
    print(f"  {status:10} {name}")
