"""
Adiciona as cartas do deck Ad Nauseam ao cards_mapping.json
"""
import json
import os
import sys

sys.path.insert(0, '.')
from deck_importer import load_custom_decks, get_custom_deck_as_cards

# Carrega o mapping existente
mapping_file = os.path.join('cards_data', 'cards_mapping.json')
with open(mapping_file, 'r', encoding='utf-8') as f:
    cards_mapping = json.load(f)

print(f"Cartas no mapping antes: {len(cards_mapping)}")

# Carrega o deck Ad Nauseam
decks = load_custom_decks()
ad_deck = None
for d in decks:
    if d['name'] == 'Ad Nauseam':
        ad_deck = d
        break

if not ad_deck:
    print("ERRO: Deck 'Ad Nauseam' não encontrado!")
    sys.exit(1)

cards = get_custom_deck_as_cards(ad_deck)
print(f"Cartas no deck: {len(cards)}")

# Adiciona as cartas ao mapping
for card in cards:
    card_id = card.id
    if card_id not in cards_mapping:
        # Busca dados da carta no cache do Scryfall
        from deck_importer import _scryfall_cache, _load_scryfall_cards
        _load_scryfall_cards()
        
        card_data = _scryfall_cache.get(card.name) or _scryfall_cache.get(card.name.lower())
        
        if card_data:
            # Extrai URLs de imagem
            image_uris = card_data.get('image_uris', {})
            if not image_uris and 'card_faces' in card_data:
                image_uris = card_data['card_faces'][0].get('image_uris', {})
            
            # Cria entrada no mapping
            entry = {
                'name': card.name,
                'type_line': card_data.get('type_line', ''),
                'oracle_text': card_data.get('oracle_text', ''),
                'mana_cost': card_data.get('mana_cost', ''),
                'local_images': {}
            }
            
            # Adiciona URLs de imagem
            if 'art_crop' in image_uris:
                # Baixa a imagem se não existir
                art_crop_url = image_uris['art_crop']
                filename = f"{card_id}_art_crop.jpg"
                filepath = os.path.join('cards_data', 'images', filename)
                
                if not os.path.exists(filepath):
                    print(f"  Baixando imagem: {card.name}")
                    try:
                        import urllib.request
                        urllib.request.urlretrieve(art_crop_url, filepath)
                    except Exception as e:
                        print(f"    Erro ao baixar: {e}")
                        continue
                
                entry['local_images']['art_crop'] = filename
            
            cards_mapping[card_id] = entry
            print(f"  Adicionado: {card.name}")

print(f"\nCartas no mapping depois: {len(cards_mapping)}")

# Salva o mapping atualizado
with open(mapping_file, 'w', encoding='utf-8') as f:
    json.dump(cards_mapping, f, ensure_ascii=False, indent=2)

print("Mapping atualizado com sucesso!")
