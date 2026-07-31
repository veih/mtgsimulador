"""
Baixa as 3 cartas faltantes diretamente da API do Scryfall
"""
import json
import os
import urllib.request

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
        'scryfall_url': 'https://api.scryfall.com/cards/named?fuzzy=Sleight+of+Hand'
    },
    {
        'id': 'spoils_of_the_vault',
        'name': 'Spoils of the Vault',
        'scryfall_url': 'https://api.scryfall.com/cards/named?fuzzy=Spoils+of+the+Vault'
    },
    {
        'id': 'concealed_courtyard',
        'name': 'Concealed Courtyard',
        'scryfall_url': 'https://api.scryfall.com/cards/named?fuzzy=Concealed+Courtyard'
    }
]

headers = {
    'User-Agent': 'MTGSimulator/1.0',
    'Accept': 'application/json'
}

# Adiciona as cartas ao mapping
for card_info in missing_cards:
    card_id = card_info['id']
    if card_id not in cards_mapping:
        print(f"Buscando: {card_info['name']}")
        
        try:
            # Faz request para a API do Scryfall
            req = urllib.request.Request(card_info['scryfall_url'], headers=headers)
            with urllib.request.urlopen(req) as response:
                card_data = json.loads(response.read().decode('utf-8'))
            
            # Extrai URLs de imagem
            image_uris = card_data.get('image_uris', {})
            if not image_uris and 'card_faces' in card_data:
                image_uris = card_data['card_faces'][0].get('image_uris', {})
            
            # Cria entrada no mapping
            entry = {
                'name': card_data.get('name', card_info['name']),
                'type_line': card_data.get('type_line', ''),
                'oracle_text': card_data.get('oracle_text', ''),
                'mana_cost': card_data.get('mana_cost', ''),
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
                        print(f"    Erro ao baixar imagem: {e}")
                
                entry['local_images']['art_crop'] = filename
            
            cards_mapping[card_id] = entry
            print(f"  Adicionado: {card_info['name']}")
            
        except Exception as e:
            print(f"  ERRO ao buscar {card_info['name']}: {e}")

print(f"\nCartas no mapping depois: {len(cards_mapping)}")

# Salva o mapping atualizado
with open(mapping_file, 'w', encoding='utf-8') as f:
    json.dump(cards_mapping, f, ensure_ascii=False, indent=2)

print("Mapping atualizado com sucesso!")
