import urllib.request, urllib.parse, json, time, os

# Load existing partial results if available
existing = {}
if os.path.exists("mtgjson_cards.json"):
    with open("mtgjson_cards.json", encoding="utf-8") as f:
        existing = json.load(f)

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
    "Bloodstained Mire", "Stirling Castle",
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
]

results = {}
for name in missing:
    if name in existing and existing[name] is not None:
        print(f"SKIP: {name} (already fetched)")
        results[name] = existing[name]
        continue
    encoded = urllib.parse.quote(name)
    url = f"https://api.scryfall.com/cards/named?fuzzy={encoded}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "mtg-sim/1.0", "Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read())
        results[name] = {
            "mana_cost": data.get("mana_cost", ""),
            "type_line": data.get("type_line", ""),
            "oracle_text": data.get("oracle_text", ""),
            "power": data.get("power"),
            "toughness": data.get("toughness"),
            "keywords": data.get("keywords", []),
            "cmc": data.get("cmc", 0),
            "colors": data.get("colors", []),
        }
        print(f"OK: {name} | {data.get('mana_cost','')} | {data.get('type_line','')}")
    except Exception as e:
        print(f"ERR: {name}: {e}")
        # retry once after 5s on 429
        if '429' in str(e):
            print(f"  Waiting 5s and retrying {name}...")
            time.sleep(5)
            try:
                req2 = urllib.request.Request(url, headers={"User-Agent": "mtg-sim/1.0", "Accept": "application/json"})
                with urllib.request.urlopen(req2, timeout=10) as r2:
                    data2 = json.loads(r2.read())
                results[name] = {
                    "mana_cost": data2.get("mana_cost", ""),
                    "type_line": data2.get("type_line", ""),
                    "oracle_text": data2.get("oracle_text", ""),
                    "power": data2.get("power"),
                    "toughness": data2.get("toughness"),
                    "keywords": data2.get("keywords", []),
                    "cmc": data2.get("cmc", 0),
                    "colors": data2.get("colors", []),
                }
                print(f"  RETRY OK: {name}")
            except Exception as e2:
                print(f"  RETRY FAIL: {e2}")
                results[name] = None
        else:
            results[name] = None
    time.sleep(0.5)  # Scryfall: max 10 req/sec, we do 2/sec to be safe

with open("mtgjson_cards.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print(f"\nDone. {sum(1 for v in results.values() if v)} cards fetched.")
