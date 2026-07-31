"""
Adiciona as 3 cartas faltantes ao cards_mapping.json
"""
import json
import os
import sys
import urllib.request

sys.path.insert(0, '.')

# Carrega o mapping existente
mapping_file = os.path.join('cards_data', 'cards_mapping.json')
with open(mapping_file, 'r', encoding='utf-8') as f:
    cards_mapping = json.load(f)

print(f"Cartas no mapping antes: {len(cards_mapping)}")

# Cartas faltantes
missing_cards = [
    {
        'id': 'sleight_of_hand',
        'name': 'Sleight of Hand',
        'type_line': 'Sorcery',
        'oracle_text': 'Look at the top two cards of your library. Put one into your hand and the other on the bottom of your library.',
        'mana_cost': '{U}',
        'scryfall_search': 'Sleight of Hand'
    },
    {
        'id': 'spoils_of_the_vault',
        'name': 'Spoils of the Vault',
        'type_line': 'Sorcery',
        'oracle_text': 'Exile the top card of your library. You gain life equal to its mana value. Draw a card.',
        'mana_cost': '{B}',
        'scryfall_search': 'Spoils of the Vault'
    },
    {
        'id': 'concealed_courtyard',
        'name': 'Concealed Courtyard',
        'type_line': 'Land',
        'oracle_text': 'Concealed Courtyard enters the battlefield tapped unless you control two or fewer other lands. Tap: Add W or R.',
        'mana_cost': '',
        'scryfall_search': 'Concealed Courtyard'
    }
]

# Adiciona as cartas ao mapping
for card_info in missing_cards:
    card_id = card_info['id']
    if card_id not in cards_mapping:
        print(f"Buscando: {card_info['name']}")
        
        # Busca no cache do Scryfall
        from deck_importer import _scryfall_cache, _load_scryfall_cards
        _load_scryfall_cards()
        
        card_data = _scryfall_cache.get(card_info['name']) or _scryfall_cache.get(card_info['name'].lower())
        
        if card_data:
            # Extrai URLs de imagem
            image_uris = card_data.get('image_uris', {})
            if not image_uris and 'card_faces' in card_data:
                image_uris = card_data['card_faces'][0].get('image_uris', {})
            
            # Cria entrada no mapping
            entry = {
                'name': card_info['name'],
                'type_line': card_info['type_line'],
                'oracle_text': card_info['oracle_text'],
                'mana_cost': card_info['mana_cost'],
                'local_images': {}
            }
            
            # Adiciona URLs de imagem
            if 'art_crop' in image_uris:
                art_crop_url = image_uris['art_crop']
                filename = f"{card_id}_art_crop.jpg"
                filepath = os.path.join('cards_data', 'images', filename)
                
                if not os.path.exists(filepath):
                    print(f"  Baixando imagem: {card_info['name']}")
                    try:
                        urllib.request.urlretrieve(art_crop_url, filepath)
                    except Exception as e:
                        print(f"    Erro ao baixar: {e}")
                        continue
                
                entry['local_images']['art_crop'] = filename
            
            cards_mapping[card_id] = entry
            print(f"  Adicionado: {card_info['name']}")
        else:
            print(f"  ERRO: {card_info['name']} não encontrado no cache do Scryfall")

print(f"\nCartas no mapping depois: {len(cards_mapping)}")

# Salva o mapping atualizado
with open(mapping_file, 'w', encoding='utf-8') as f:
    json.dump(cards_mapping, f, ensure_ascii=False, indent=2)

print("Mapping atualizado com sucesso!")
