import json

with open('cards_data/cards_mapping.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

missing = ['sleight_of_hand', 'spoils_of_the_vault', 'concealed_courtyard']
for m in missing:
    status = "OK" if m in data else "FALTANDO"
    print(f"{m}: {status}")

print(f"\nTotal de cartas no mapping: {len(data)}")
