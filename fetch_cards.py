import urllib.request, json, sys

# Collect all missing cards from all 8 decks
missing = [
    # Jund
    "Bloodbraid Elf", "Dark Confidant", "Kolaghan's Command",
    "Fatal Push", "Inquisition of Kozilek", "Wrenn and Six",
    "Liliana of the Veil", "Blood Crypt", "Overgrown Tomb", "Stomping Ground",
    # Izzet Murktide
    "Murktide Regent", "Ragavan, Nimble Pilferer", "Dragon's Rage Channeler",
    "Expressive Iteration", "Spell Snare", "Unholy Heat", "Thought Scour",
    "Steam Vents", "Scalding Tarn", "Spirebluff Canal",
    # Hollow One
    "Hollow One", "Goblin Charbelcher", "Flame Slash", "Faithless Looting",
    "Gurmag Angler", "Merciless Executioner", "Dread Return", "Vengevine",
    "Bazaar of Baghdad", "Bloodghast", "Bridge from Below", "Blackcleave Cliffs",
    "Bloodstained Mire",
    # Prowess
    "Monastery Swiftspear", "Soul-Scar Mage", "Eidolon of the Great Revel",
    "Lava Dart", "Rift Bolt", "Burst Lightning", "Mishra's Bauble", "Sacred Foundry",
    # Death's Shadow
    "Death's Shadow", "Temur Battle Rage", "Daze",
    "Delirium Skeins", "Street Wraith",
    # Tron
    "Karn Liberated", "Chromatic Star", "Chromatic Sphere",
    "Oblivion Stone", "Mindslaver", "Urza's Mine", "Urza's Power Plant", "Urza's Tower",
    "Wastes",
    # Prowess lands
    # Already have: Mountain, Lightning Bolt, Lava Spike, Goblin Guide
    # Hollow One lands already have swamp/mountain
]

results = {}
for name in missing:
    encoded = urllib.parse.quote(name) if hasattr(urllib, 'parse') else name.replace(" ","%20").replace("'","%27").replace(",","%2C")
    url = f"https://api.scryfall.com/cards/named?exact={encoded}"
    try:
        with urllib.request.urlopen(url, timeout=8) as r:
            data = json.loads(r.read())
        results[name] = {
            "mana_cost": data.get("mana_cost",""),
            "type_line": data.get("type_line",""),
            "oracle_text": data.get("oracle_text",""),
            "power": data.get("power"),
            "toughness": data.get("toughness"),
            "keywords": data.get("keywords",[]),
            "cmc": data.get("cmc",0),
            "colors": data.get("colors",[]),
        }
        print(f"OK: {name} | {data.get('mana_cost','')} | {data.get('type_line','')}")
    except Exception as e:
        print(f"ERR: {name}: {e}")
        results[name] = None

import urllib.parse
with open("mtgjson_cards.json","w",encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print("Done. Saved mtgjson_cards.json")
