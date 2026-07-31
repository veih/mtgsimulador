#!/usr/bin/env python3
"""
MTG Match Simulator - Download de Coleções do Scryfall
Baixa dados de cartas de coleções específicas do Scryfall.
"""

import json
import os
import sys
import time
import urllib.request
import urllib.error
from typing import List, Dict, Optional

# Pasta base para dados de cartas
BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cards_data')
os.makedirs(BASE_DIR, exist_ok=True)

# API do Scryfall
SCRYFALL_API_SETS = 'https://api.scryfall.com/sets'
SCRYFALL_API_SEARCH = 'https://api.scryfall.com/cards/search'
SCRYFALL_API_SET_QUERY = 'https://api.scryfall.com/cards/search?q=set:{set_code}'


def download_with_retry(url: str, retries: int = 3, delay: int = 2) -> Optional[dict]:
    """Baixa JSON com retry."""
    headers = {
        'User-Agent': 'MTGSimulator/1.0',
        'Accept': 'application/json'
    }
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as response:
                return json.loads(response.read().decode('utf-8'))
        except Exception as e:
            print(f"  Tentativa {attempt+1} falhou: {e}")
            if attempt < retries - 1:
                time.sleep(delay)
    return None


def list_available_sets() -> List[Dict]:
    """Lista todas as coleções disponíveis no Scryfall."""
    print("Buscando lista de coleções...")
    data = download_with_retry(SCRYFALL_API_SETS)
    if not data:
        print("Erro ao buscar coleções!")
        return []
    
    sets = data.get('data', [])
    # Filtra apenas coleções relevantes
    relevant = []
    for s in sets:
        if s.get('set_type') in ['core', 'expansion', 'masters', 'draft_innovation']:
            relevant.append({
                'code': s['code'],
                'name': s['name'],
                'year': s.get('released_at', '')[:4],
                'card_count': s.get('card_count', 0),
                'set_type': s.get('set_type', '')
            })
    
    return sorted(relevant, key=lambda x: x['year'], reverse=True)


def download_set(set_code: str) -> bool:
    """Baixa todas as cartas de uma coleção específica."""
    set_code = set_code.lower().strip()
    
    # Verifica se já foi baixada
    set_dir = os.path.join(BASE_DIR, set_code)
    if os.path.exists(set_dir):
        print(f"Coleção {set_code} já foi baixada!")
        return True
    
    os.makedirs(set_dir, exist_ok=True)
    
    print(f"\nBaixando coleção: {set_code.upper()}")
    print("-" * 40)
    
    all_cards = []
    page = 1
    url = SCRYFALL_API_SET_QUERY.format(set_code=set_code)
    
    while url:
        print(f"  Página {page}...", end=' ', flush=True)
        
        data = download_with_retry(url)
        if not data:
            print("ERRO!")
            return False
        
        cards = data.get('data', [])
        all_cards.extend(cards)
        print(f"{len(cards)} cartas")
        
        # Usa next_page se disponível
        url = data.get('next_page', None)
        page += 1
        
        # Delay para não sobrecarregar a API
        time.sleep(0.1)
    
    # Salva as cartas
    cards_file = os.path.join(set_dir, 'cards.json')
    with open(cards_file, 'w', encoding='utf-8') as f:
        json.dump(all_cards, f, ensure_ascii=False, indent=2)
    
    print(f"\nTotal: {len(all_cards)} cartas salvas em {cards_file}")
    return True


def download_multiple_sets(set_codes: List[str]):
    """Baixa múltiplas coleções."""
    print(f"Baixando {len(set_codes)} coleções...")
    
    success = 0
    for code in set_codes:
        if download_set(code):
            success += 1
        time.sleep(1)  # Delay entre coleções
    
    print(f"\n{'='*40}")
    print(f"Concluído: {success}/{len(set_codes)} coleções baixadas")


def show_popular_sets():
    """Mostra coleções populares para Modern."""
    print("\n" + "="*60)
    print("COLEÇÕES POPULARES PARA MODERN")
    print("="*60)
    print("\nFormato: código - nome (ano)")
    print("\n--- Core Sets ---")
    print("  m21 - Core Set 2021 (2020)")
    print("  m20 - Core Set 2020 (2019)")
    print("  m19 - Core Set 2019 (2018)")
    print("\n--- Expansões Recentes ---")
    print("  neo - Kamigawa: Neon Dynasty (2022)")
    print("  mid - Innistrad: Midnight Hunt (2021)")
    print("  vow - Innistrad: Crimson Vow (2021)")
    print("  khm - Kaldheim (2021)")
    print("  stx - Strixhaven (2021)")
    print("  thb - Theros Beyond Death (2020)")
    print("  ikO - Ikoria: Lair of Behemoths (2020)")
    print("  znr - Zendikar Rising (2020)")
    print("  znt - Zendikar Rising Commander (2020)")
    print("\n--- Masters ---")
    print("  a25 - Masters 25 (2018)")
    print("  2xm - Double Masters (2020)")
    print("  3xm - Triple Masters (2021)")
    print("  mma - Modern Masters 2017 (2017)")
    print("  mm2 - Modern Masters 2015 (2015)")
    print("  mm3 - Modern Masters 2017 (2017)")
    print("\n--- Clássicos Modern ---")
    print("  rtr - Return to Ravnica (2012)")
    print("  gtC - Gatecrash (2013)")
    print("  dgm - Dragon's Maze (2013)")
    print("  ths - Theros (2013)")
    print("  bng - Born of the Gods (2014)")
    print("  jou - Journey into Nyx (2014)")
    print("  khn - Khans of Tarkir (2014)")
    print("  frf - Fate Reforged (2015)")
    print("  dtk - Dragons of Tarkir (2015)")
    print("  bfz - Battle for Zendikar (2015)")
    print("  ogw - Oath of the Gatewatch (2016)")
    print("  soI - Shadows over Innistrad (2016)")
    print("  emn - Eldritch Moon (2016)")
    print("  kld - Kaladesh (2016)")
    print("  aer - Aether Revolt (2017)")
    print("  A25 - Amonkhet (2017)")
    print("  hou - Hour of Devastation (2017)")
    print("  xln - Ixalan (2017)")
    print("  rix - Rivals of Ixalan (2018)")
    print("  dom - Dominaria (2018)")
    print("  grn - Guilds of Ravnica (2018)")
    print("  rna - Ravnica Allegiance (2019)")
    print("  war - War of the Spark (2019)")
    print("  eld - Throne of Eldraine (2019)")
    print("  thb - Theros Beyond Death (2020)")
    print("\n--- Commander/Outros ---")
    print("  cmr - Commander Legends (2020)")
    print("  c21 - Commander 2021 (2021)")
    print("  mic - MIC (2021)")
    print("="*60)


def main():
    """Função principal."""
    if len(sys.argv) < 2:
        print("Uso: python download_sets.py <comando> [args]")
        print("\nComandos:")
        print("  list          - Lista todas as coleções disponíveis")
        print("  popular       - Mostra coleções populares para Modern")
        print("  download <código> [código2 ...] - Baixa coleções específicas")
        print("  download-all  - Baixa todas as coleções populares")
        print("\nExemplos:")
        print("  python download_sets.py download m21 neo")
        print("  python download_sets.py download thb ikO znr")
        print("  python download_sets.py download-all")
        return
    
    command = sys.argv[1].lower()
    
    if command == 'list':
        sets = list_available_sets()
        print(f"\nEncontradas {len(sets)} coleções:")
        for s in sets[:30]:  # Mostra apenas 30
            print(f"  {s['code']:5} - {s['name'][:40]:40} ({s['year']}) [{s['set_type']}]")
        if len(sets) > 30:
            print(f"  ... e mais {len(sets)-30} coleções")
    
    elif command == 'popular':
        show_popular_sets()
    
    elif command == 'download':
        if len(sys.argv) < 3:
            print("Erro: Especifique pelo menos uma coleção!")
            print("Exemplo: python download_sets.py download m21 neo")
            return
        set_codes = sys.argv[2:]
        download_multiple_sets(set_codes)
    
    elif command == 'download-all':
        # Coleções populares para Modern
        popular = [
            'm21', 'm20', 'm19',  # Core sets
            'neo', 'mid', 'vow', 'khm', 'stx',  # Recentes
            'thb', 'iko', 'znr', 'eld', 'war',  # 2019-2020
            'rna', 'grn', 'dom', 'a25',  # 2017-2018
            '2xm', '3xm',  # Masters
        ]
        download_multiple_sets(popular)
    
    else:
        print(f"Comando desconhecido: {command}")
        print("Use 'list', 'popular', 'download' ou 'download-all'")


if __name__ == '__main__':
    main()
