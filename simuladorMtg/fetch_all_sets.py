#!/usr/bin/env python3
"""
MTG Card Collector - Baixa dados e imagens de todas as colecoes MTG.
Da 8a edicao ate as colecoes atuais, organizados por pasta.
Usa a API do Scryfall (gratuita).
"""

import os
import sys
import json
import time
import urllib.request
import urllib.error
import urllib.parse

# Encoding UTF-8 no Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Diretorios
BASE_DIR = os.path.join(os.path.expanduser('~'), 'Desktop', 'MTG_Cards')
DATA_DIR = os.path.join(BASE_DIR, 'data')
IMAGES_DIR = os.path.join(BASE_DIR, 'images')

# API Scryfall
API_BASE = 'https://api.scryfall.com'
HEADERS = {
    'User-Agent': 'MTGCardCollector/1.0',
    'Accept': 'application/json'
}

# 8a edicao foi lancada em 2003. Sets antes disso sao ignorados.
MIN_YEAR = 2003


def ensure_dirs():
    os.makedirs(BASE_DIR, exist_ok=True)
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(IMAGES_DIR, exist_ok=True)


def api_get(url, timeout=15):
    """Faz uma requisicao GET para a API do Scryfall."""
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='replace')[:200]
        print(f"    [ERRO] HTTP {e.code}: {body}")
        return None
    except Exception as e:
        print(f"    [ERRO] {e}")
        return None


def download_file(url, filepath, timeout=20):
    """Baixa um arquivo de uma URL."""
    try:
        headers = {
            'User-Agent': 'MTGCardCollector/1.0',
            'Accept': 'image/webp,image/*,*/*;q=0.8'
        }
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            with open(filepath, 'wb') as f:
                f.write(resp.read())
            return True
    except Exception as e:
        return False


def get_all_sets():
    """Lista todas as colecoes do Scryfall."""
    print("  Buscando lista de colecoes...")
    data = api_get(f"{API_BASE}/sets")
    if not data or 'data' not in data:
        print("  [ERRO] Nao foi possivel listar colecoes.")
        return []
    
    all_sets = data['data']
    
    # Filtra: apenas sets com carta (nao digitais/memorabilia) e a partir de 8a edicao
    valid_sets = []
    for s in all_sets:
        year = None
        if s.get('released_at'):
            try:
                year = int(s['released_at'][:4])
            except (ValueError, TypeError):
                pass
        
        if year and year >= MIN_YEAR:
            if s.get('set_type') in ('core', 'expansion', 'draft_innovation', 'commander', 'masters', 'starter'):
                valid_sets.append(s)
    
    # Ordena por data de lancamento (mais recente primeiro)
    valid_sets.sort(key=lambda x: x.get('released_at', ''), reverse=True)
    return valid_sets


def safe_filename(name):
    """Converte nome em filename seguro."""
    return name.replace('/', '_').replace('\\', '_').replace(':', '_').replace('*', '_').replace('?', '_').replace('"', '_').replace('<', '_').replace('>', '_').replace('|', '_').strip()


def get_set_cards(set_code):
    """Baixa todas as cartas de uma colecao."""
    cards = []
    page = 1
    url = f"{API_BASE}/cards/search?q=set:{set_code}&unique=prints&order=set"
    
    while url:
        data = api_get(url)
        if not data:
            break
        
        if 'data' in data:
            cards.extend(data['data'])
        
        # Paginacao
        url = data.get('next_page', None)
        page += 1
        
        # Rate limit: 100-150ms entre requisicoes
        time.sleep(0.15)
    
    return cards


def extract_card_info(card):
    """Extrai informacoes relevantes de uma carta."""
    # Face frontal
    if card.get('layout') in ('transform', 'modal_dfc', 'meld') and card.get('card_faces'):
        face = card['card_faces'][0]
        name = face.get('name', card.get('name', ''))
        mana_cost = face.get('mana_cost', '')
        type_line = face.get('type_line', '')
        oracle_text = face.get('oracle_text', '')
        power = face.get('power', '')
        toughness = face.get('toughness', '')
        colors = face.get('colors', card.get('colors', []))
        img_uris = face.get('image_uris', card.get('image_uris', {}))
    else:
        name = card.get('name', '')
        mana_cost = card.get('mana_cost', '')
        type_line = card.get('type_line', '')
        oracle_text = card.get('oracle_text', '')
        power = card.get('power', '')
        toughness = card.get('toughness', '')
        colors = card.get('colors', [])
        img_uris = card.get('image_uris', {})

    return {
        'id': card.get('id', ''),
        'name': name,
        'mana_cost': mana_cost,
        'type_line': type_line,
        'oracle_text': oracle_text,
        'power': power,
        'toughness': toughness,
        'colors': colors,
        'rarity': card.get('rarity', ''),
        'set': card.get('set', ''),
        'set_name': card.get('set_name', ''),
        'artist': card.get('artist', ''),
        'number': card.get('collector_number', ''),
        'keywords': card.get('keywords', []),
        'legalities': card.get('legalities', {}),
        'image_uris': {
            'small': img_uris.get('small', ''),
            'normal': img_uris.get('normal', ''),
            'large': img_uris.get('large', ''),
            'png': img_uris.get('png', ''),
            'art_crop': img_uris.get('art_crop', ''),
        },
        'scryfall_uri': card.get('scryfall_uri', ''),
        'released_at': card.get('released_at', ''),
    }


def download_card_images(card_info, set_dir):
    """Baixa imagens de uma carta para a pasta da colecao."""
    img_uris = card_info.get('image_uris', {})
    downloaded = {}
    
    # Nome seguro para o arquivo
    card_name = safe_filename(card_info.get('name', 'unknown'))
    card_num = safe_filename(card_info.get('number', ''))
    base_name = f"{card_num}_{card_name}" if card_num else card_name
    
    for size in ['normal', 'art_crop']:
        url = img_uris.get(size, '')
        if not url:
            continue
        
        ext = 'jpg'
        filename = f"{base_name}_{size}.{ext}"
        filepath = os.path.join(set_dir, filename)
        
        if not os.path.exists(filepath):
            if download_file(url, filepath):
                downloaded[size] = filename
        else:
            downloaded[size] = filename
    
    return downloaded


def process_set(set_info, download_images=True):
    """Processa uma colecao: baixa dados e imagens."""
    set_code = set_info['code']
    set_name = set_info['name']
    set_year = set_info.get('released_at', '')[:4]
    
    print(f"\n  [{set_code}] {set_name} ({set_year})")
    
    # Pasta da colecao
    set_dir_name = safe_filename(f"{set_code}_{set_name}_{set_year}")
    set_data_dir = os.path.join(DATA_DIR, set_dir_name)
    set_img_dir = os.path.join(IMAGES_DIR, set_dir_name)
    os.makedirs(set_data_dir, exist_ok=True)
    if download_images:
        os.makedirs(set_img_dir, exist_ok=True)
    
    # Busca cartas
    print(f"    Buscando cartas...", end=' ', flush=True)
    cards = get_set_cards(set_code)
    print(f"{len(cards)} cartas encontradas")
    
    if not cards:
        return 0
    
    # Extrai informacoes
    cards_info = []
    for card in cards:
        info = extract_card_info(card)
        
        # Baixa imagens
        if download_images:
            local_imgs = download_card_images(info, set_img_dir)
            info['local_images'] = local_imgs
        
        cards_info.append(info)
        
        # Rate limit
        if download_images:
            time.sleep(0.1)
    
    # Salva dados da colecao
    data_file = os.path.join(set_data_dir, 'cards.json')
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(cards_info, f, ensure_ascii=False, indent=2)
    
    # Salva info do set
    set_meta = {
        'code': set_code,
        'name': set_name,
        'released_at': set_info.get('released_at', ''),
        'set_type': set_info.get('set_type', ''),
        'card_count': len(cards_info),
        'total_cards_in_set': set_info.get('card_count', 0),
    }
    meta_file = os.path.join(set_data_dir, 'set_info.json')
    with open(meta_file, 'w', encoding='utf-8') as f:
        json.dump(set_meta, f, ensure_ascii=False, indent=2)
    
    img_count = sum(1 for c in cards_info if c.get('local_images'))
    print(f"    Salvo: {data_file}")
    if download_images:
        print(f"    Imagens: {img_count} cartas com imagens em {set_img_dir}")
    
    return len(cards_info)


def generate_index(all_sets_info):
    """Gera um arquivo indice com todas as colecoes."""
    index_file = os.path.join(BASE_DIR, 'index.json')
    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(all_sets_info, f, ensure_ascii=False, indent=2)
    print(f"\n  Indice salvo em: {index_file}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Baixa colecoes MTG da 8a edicao ate hoje')
    parser.add_argument('--sets', type=str, help='Codigos das colecoes separados por virgula (ex: M21,KHM,MID)')
    parser.add_argument('--recent', type=int, help='Baixa apenas as N mais recentes')
    parser.add_argument('--all', action='store_true', help='Baixa TODAS as colecoes')
    parser.add_argument('--no-images', action='store_true', help='Nao baixa imagens (so dados)')
    parser.add_argument('--list', action='store_true', help='Lista colecoes disponiveis e sai')
    args = parser.parse_args()
    
    ensure_dirs()
    
    print("=" * 60)
    print("  MTG Card Collector")
    print("  Baixando colecoes da 8a edicao ate hoje")
    print(f"  Dados: {DATA_DIR}")
    print(f"  Imagens: {IMAGES_DIR}")
    print("=" * 60)
    
    # Lista todas as colecoes
    all_sets = get_all_sets()
    if not all_sets:
        print("  Nenhuma colecao encontrada!")
        return
    
    print(f"\n  {len(all_sets)} colecoes encontradas (de {MIN_YEAR} ate hoje)")
    
    # Modo lista
    if args.list:
        print()
        for i, s in enumerate(all_sets):
            print(f"    {i+1:3d}. [{s['code']}] {s['name']} ({s.get('released_at','')[:4]}) - {s.get('set_type','')}")
        return
    
    # Determina quais colecoes baixar
    if args.sets:
        codes = [c.strip().upper() for c in args.sets.split(',')]
        selected_sets = [s for s in all_sets if s['code'].upper() in codes]
        if not selected_sets:
            print(f"  Nenhuma colecao encontrada com codigos: {args.sets}")
            return
    elif args.recent:
        selected_sets = all_sets[:args.recent]
    elif args.all:
        selected_sets = all_sets
    else:
        # Modo interativo
        print()
        for i, s in enumerate(all_sets[:30]):
            print(f"    {i+1:3d}. [{s['code']}] {s['name']} ({s.get('released_at','')[:4]})")
        if len(all_sets) > 30:
            print(f"    ... e mais {len(all_sets)-30} colecoes")
        
        print()
        print("  Opcoes:")
        print("    1. Baixar TODAS as colecoes (pode demorar muito)")
        print("    2. Selecionar colecoes especificas")
        print("    3. Baixar apenas as 10 mais recentes")
        print("    4. Sair")
        print()
        
        choice = input("  Escolha (1-4): ").strip()
        
        if choice == '4':
            print("  Saindo...")
            return
        elif choice == '1':
            selected_sets = all_sets
        elif choice == '3':
            selected_sets = all_sets[:10]
        elif choice == '2':
            print("\n  Digite os codigos separados por virgula (ex: M21,KHM,MID)")
            codes = input("  Codigos: ").strip().split(',')
            codes = [c.strip().upper() for c in codes]
            selected_sets = [s for s in all_sets if s['code'].upper() in codes]
            if not selected_sets:
                print("  Nenhuma colecao encontrada!")
                return
        else:
            selected_sets = all_sets[:10]
    
    download_images = not args.no_images
    
    if not args.sets and not args.recent and not args.all:
        img_choice = input("  Baixar imagens tambem? (s/n): ").strip().lower()
        download_images = img_choice != 'n'
    
    print(f"\n  {len(selected_sets)} colecoes selecionadas")
    print(f"  Imagens: {'sim' if download_images else 'nao'}")
    
    # Processa cada colecao
    total_cards = 0
    all_sets_info = []
    
    for i, set_info in enumerate(selected_sets):
        print(f"\n  Processando {i+1}/{len(selected_sets)}...")
        card_count = process_set(set_info, download_images)
        total_cards += card_count
        
        all_sets_info.append({
            'code': set_info['code'],
            'name': set_info['name'],
            'released_at': set_info.get('released_at', ''),
            'set_type': set_info.get('set_type', ''),
            'cards_downloaded': card_count,
        })
    
    # Gera indice
    generate_index(all_sets_info)
    
    print()
    print("=" * 60)
    print(f"  CONCLUIDO!")
    print(f"  {len(selected_sets)} colecoes processadas")
    print(f"  {total_cards} cartas baixadas")
    print(f"  Dados em: {DATA_DIR}")
    if download_images:
        print(f"  Imagens em: {IMAGES_DIR}")
    print("=" * 60)


if __name__ == '__main__':
    main()
