import json, os

base = 'cards_data'
missing = ['Preordain', 'Concealed Courtyard', 'Hallowed Fountain', 'Godless Shrine', 
           'Gemstone Mine', 'Sleight of Hand', 'Spoils of the Vault']

for card_name in missing:
    found = False
    for d in os.listdir(base):
        cards_file = os.path.join(base, d, 'cards.json')
        if not os.path.isfile(cards_file):
            continue
        with open(cards_file, 'r', encoding='utf-8') as f:
            cards = json.load(f)
        for card in cards:
            if card.get('name', '').lower() == card_name.lower():
                print(f"  FOUND: {card_name} in {d} (name: {card['name']})")
                found = True
                break
        if found:
            break
    if not found:
        # Busca parcial
        for d in os.listdir(base):
            cards_file = os.path.join(base, d, 'cards.json')
            if not os.path.isfile(cards_file):
                continue
            with open(cards_file, 'r', encoding='utf-8') as f:
                cards = json.load(f)
            for card in cards:
                if card_name.lower() in card.get('name', '').lower():
                    print(f"  PARTIAL: '{card_name}' ~ '{card['name']}' in {d}")
                    found = True
                    break
            if found:
                break
        if not found:
            print(f"  NOT FOUND: {card_name}")
