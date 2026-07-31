import json
import os

# Carrega o mapping
mapping_file = os.path.join('cards_data', 'cards_mapping.json')
with open(mapping_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Total de cartas no mapping: {len(data)}")

# Procura cartas do deck Ad Nauseam
target_cards = [
    'ad nauseam', "angel's grace", 'phyrexian unlife', 'lotus bloom',
    'pact of negation', 'force of negation', 'preordain', 'profane tutor',
    'sleight of hand', 'spoils of the vault', 'path to exile',
    'thassa\'s oracle', 'seachrome coast', 'concealed courtyard',
    'darkslick shores', 'hallowed fountain', 'watery grave',
    'godless shrine', 'gemstone mine', 'otawara'
]

print("\nProcurando cartas do deck Ad Nauseam:")
for target in target_cards:
    found = False
    for k, v in data.items():
        if target in v.get('name', '').lower():
            has_image = 'local_images' in v and 'art_crop' in v.get('local_images', {})
            print(f"  ✓ {v.get('name')}: imagem={has_image}")
            found = True
            break
    if not found:
        print(f"  ✗ {target}: NÃO ENCONTRADA")
