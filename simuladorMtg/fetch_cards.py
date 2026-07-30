#!/usr/bin/env python3
"""
MTG Match Simulator - Busca dados e imagens das cartas via Scryfall API.
Baixa fotos e textos de todas as cartas usadas no simulador.
"""

import os
import sys
import json
import time
import urllib.request
import urllib.error

# Forca encoding UTF-8 no Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Pasta para salvar os dados e imagens
CARDS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cards_data')
IMAGES_DIR = os.path.join(CARDS_DIR, 'images')
DATA_FILE = os.path.join(CARDS_DIR, 'cards.json')

# Cartas usadas no simulador (nomes exatos do Scryfall)
SIMULATOR_CARDS = [
    # Terrenos Basicos
    "Plains", "Island", "Swamp", "Mountain", "Forest",
    # Red
    "Lightning Bolt", "Lava Spike", "Chain Lightning", "Goblin Guide",
    "Monastic Mentor", "Skullraid",
    # White
    "Healing Salve", "Swords to Plowshares", "Day of Judgment",
    "Guardian of Solitude", "Samite Healer", "Thraben Inspector",
    "Knight of the White Orchid",
    # Green
    "Grizzly Bears", "Tarmogoyf", "Bird of Paradise", "Llanowar Elves",
    "Collective Unconscious", "Overcome", "Wood Elephant", "Baloth Gorger",
    "Giant Growth", "Harmonize",
    # Black
    "Thoughtseize", "Doom Blade", "Vampire Nobile", "Dark Imp",
    "Shadow Slayer", "Bone Picker", "Drain Life",
    # Blue
    "Counterspell", "Air Elemental", "Phantasmal Bear", "Mind Rot",
    # Multi/Other
    "Barktooth Warbeard",
]

# Mapeamento de IDs do simulador para nomes do Scryfall
CARD_ID_TO_SCRYFALL = {
    "plains": "Plains",
    "island": "Island",
    "swamp": "Swamp",
    "mountain": "Mountain",
    "forest": "Forest",
    "lightning_bolt": "Lightning Bolt",
    "lava_spike": "Lava Spike",
    "chain_lightning": "Chain Lightning",
    "goblin_guide": "Goblin Guide",
    "monastic_mentor": "Monastic Mentor",
    "skullraid": "Skullraid",
    "healing_salve": "Healing Salve",
    "swords_to_plowshares": "Swords to Plowshares",
    "day_of_judgment": "Day of Judgment",
    "guardian_of_solitude": "Guardian of Solitude",
    "samite_healer": "Samite Healer",
    "thraben_banner": "Thraben Inspector",
    "knight_of_white": "Knight of the White Orchid",
    "grizzly_bears": "Grizzly Bears",
    "tarmogoyf": "Tarmogoyf",
    "bird_of_paradise": "Bird of Paradise",
    "elves": "Llanowar Elves",
    "collective_unconscious": "Collective Unconscious",
    "overcome": "Overcome",
    "wood_elephant": "Wood Elephant",
    "baloth": "Baloth Gorger",
    "giant_growth": "Giant Growth",
    "harmonize": "Harmonize",
    "thoughtseize": "Thoughtseize",
    "doom_blade": "Doom Blade",
    "vampire_noble": "Vampire Nobile",
    "dark_imp": "Dark Imp",
    "shadow_slayer": "Shadow Slayer",
    "bone_picker": "Bone Picker",
    "drain_life": "Drain Life",
    "counterspell": "Counterspell",
    "air_elemental": "Air Elemental",
    "phantasmal_bear": "Phantasmal Bear",
    "mind_rotate": "Mind Rot",
    "barktooth": "Barktooth Warbeard",
}


def ensure_dirs():
    """Cria diretorios necessarios."""
    os.makedirs(CARDS_DIR, exist_ok=True)
    os.makedirs(IMAGES_DIR, exist_ok=True)


def search_card(card_name):
    """Busca dados de uma carta na API do Scryfall."""
    encoded = urllib.request.quote(card_name)
    url = f"https://api.scryfall.com/cards/named?fuzzy={encoded}"
    try:
        headers = {
            'User-Agent': 'MTGSimulator/1.0',
            'Accept': 'application/json'
        }
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='replace')[:200]
        print(f"  [ERRO] HTTP {e.code} para '{card_name}': {body}")
        return None
    except Exception as e:
        print(f"  [ERRO] {e} para '{card_name}'")
        return None


def download_image(url, filepath):
    """Baixa uma imagem de uma URL."""
    try:
        headers = {
            'User-Agent': 'MTGSimulator/1.0',
            'Accept': 'image/webp,image/*,*/*;q=0.8'
        }
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as response:
            with open(filepath, 'wb') as f:
                f.write(response.read())
            return True
    except Exception as e:
        print(f"  [ERRO] Download imagem: {e}")
        return False


def extract_card_data(scryfall_data):
    """Extrai dados relevantes do JSON do Scryfall."""
    # Pega a face frontal
    if scryfall_data.get('layout') == 'transform' and scryfall_data.get('card_faces'):
        face = scryfall_data['card_faces'][0]
        name = face.get('name', scryfall_data.get('name', ''))
        mana_cost = face.get('mana_cost', '')
        type_line = face.get('type_line', '')
        oracle_text = face.get('oracle_text', '')
        power = face.get('power', '')
        toughness = face.get('toughness', '')
        colors = face.get('colors', scryfall_data.get('colors', []))
    else:
        name = scryfall_data.get('name', '')
        mana_cost = scryfall_data.get('mana_cost', '')
        type_line = scryfall_data.get('type_line', '')
        oracle_text = scryfall_data.get('oracle_text', '')
        power = scryfall_data.get('power', '')
        toughness = scryfall_data.get('toughness', '')
        colors = scryfall_data.get('colors', [])

    # Imagens
    images = {}
    img_data = scryfall_data.get('image_uris', {})
    if not img_data and scryfall_data.get('card_faces'):
        img_data = scryfall_data['card_faces'][0].get('image_uris', {})

    images['small'] = img_data.get('small', '')
    images['normal'] = img_data.get('normal', '')
    images['large'] = img_data.get('large', '')
    images['png'] = img_data.get('png', '')
    images['art_crop'] = img_data.get('art_crop', '')

    # Keywords
    keywords = scryfall_data.get('keywords', [])

    # Legalidades
    legalities = scryfall_data.get('legalities', {})

    # Raridade
    rarity = scryfall_data.get('rarity', '')

    # Set
    set_name = scryfall_data.get('set_name', '')
    set_code = scryfall_data.get('set', '')

    # Artista
    artist = scryfall_data.get('artist', '')

    # Scryfall ID
    scryfall_id = scryfall_data.get('id', '')

    return {
        'name': name,
        'mana_cost': mana_cost,
        'type_line': type_line,
        'oracle_text': oracle_text,
        'power': power,
        'toughness': toughness,
        'colors': colors,
        'keywords': keywords,
        'rarity': rarity,
        'set_name': set_name,
        'set_code': set_code,
        'artist': artist,
        'scryfall_id': scryfall_id,
        'legalities': legalities,
        'images': images,
    }


def download_card_images(card_data, card_id):
    """Baixa as imagens da carta."""
    images = card_data.get('images', {})
    downloaded = {}

    # Baixa apenas normal e art_crop para economiar espaco
    for size in ['normal', 'art_crop']:
        url = images.get(size, '')
        if url:
            ext = 'jpg'
            filename = f"{card_id}_{size}.{ext}"
            filepath = os.path.join(IMAGES_DIR, filename)
            if not os.path.exists(filepath):
                print(f"    Baixando {size}...", end=' ', flush=True)
                if download_image(url, filepath):
                    print("OK")
                    downloaded[size] = filename
                else:
                    print("FALHOU")
            else:
                downloaded[size] = filename

    return downloaded


def fetch_all_cards():
    """Busca todas as cartas do simulador."""
    ensure_dirs()

    print("=" * 60)
    print("  MTG Card Data Fetcher")
    print("  Buscando dados e imagens via Scryfall API")
    print("=" * 60)
    print()

    all_cards = {}
    total = len(SIMULATOR_CARDS)

    for i, card_name in enumerate(SIMULATOR_CARDS):
        print(f"  [{i+1}/{total}] Buscando: {card_name}")

        # Busca dados no Scryfall
        scryfall_data = search_card(card_name)
        if not scryfall_data:
            print(f"    Carta nao encontrada, pulando...")
            time.sleep(0.5)
            continue

        # Extrai dados relevantes
        card_data = extract_card_data(scryfall_data)

        # Gera um ID seguro para o arquivo
        card_id = card_name.lower().replace(' ', '_').replace("'", "").replace(",", "").replace(":", "")

        # Baixa imagens
        local_images = download_card_images(card_data, card_id)

        # Salva caminhos locais das imagens
        card_data['local_images'] = local_images

        # Salva dados completos
        all_cards[card_name] = card_data

        # Respeita o rate limit do Scryfall (100ms entre requisicoes)
        time.sleep(0.15)

    # Salva tudo em JSON
    print(f"\n  Salvando dados em: {DATA_FILE}")
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_cards, f, ensure_ascii=False, indent=2)

    # Tambem salva um mapeamento ID do simulador -> dados
    mapping = {}
    for sim_id, scryfall_name in CARD_ID_TO_SCRYFALL.items():
        if scryfall_name in all_cards:
            mapping[sim_id] = all_cards[scryfall_name]

    mapping_file = os.path.join(CARDS_DIR, 'cards_mapping.json')
    with open(mapping_file, 'w', encoding='utf-8') as f:
        json.dump(mapping, f, ensure_ascii=False, indent=2)

    print(f"  Mapeamento salvo em: {mapping_file}")
    print()
    print(f"  Concluido!")
    print(f"  {len(all_cards)} cartas processadas")
    print(f"  Dados: {DATA_FILE}")
    print(f"  Imagens: {IMAGES_DIR}/")
    print(f"  Mapeamento: {mapping_file}")
    print("=" * 60)

    return all_cards


if __name__ == '__main__':
    fetch_all_cards()
