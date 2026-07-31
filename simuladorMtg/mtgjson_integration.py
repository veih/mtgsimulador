"""
MTG Match Simulator - MTGJSON Integration (Versão Otimizada)
Baixa dados em arquivos menores para evitar MemoryError.
"""

import json
import os
import urllib.request
from typing import Dict, List


# URLs do MTGJSON (arquivos menores)
MTGJSON_URLS = {
    'AtomicCards': 'https://mtgjson.com/api/v5/AtomicCards.json',
    'CardTypes': 'https://mtgjson.com/api/v5/CardTypes.json',
    'CompRules': 'https://mtgjson.com/api/v5/CompRules.json',
    'Decklists': 'https://mtgjson.com/api/v5/Decklists.json',
    'EnumValues': 'https://mtgjson.com/api/v5/EnumValues.json',
    'Keywords': 'https://mtgjson.com/api/v5/Keywords.json',
}

# Diretório local
MTGJSON_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mtgjson_data')
os.makedirs(MTGJSON_DIR, exist_ok=True)


def download_file(url: str, filename: str) -> bool:
    """Baixa um arquivo individual do MTGJSON."""
    filepath = os.path.join(MTGJSON_DIR, filename)
    
    if os.path.exists(filepath):
        print(f"  [OK] {filename} ja existe")
        return True
    
    try:
        print(f"  [..] Baixando {filename}...")
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'MTGSimulator/1.0'}
        )
        
        with urllib.request.urlopen(req) as response:
            data = response.read().decode('utf-8')
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(data)
        
        print(f"  [OK] {filename} baixado")
        return True
        
    except Exception as e:
        print(f"  [ERRO] {filename}: {e}")
        return False


def download_mtgjson_optimized():
    """Baixa arquivos individuais do MTGJSON (menor uso de memoria)."""
    print("Baixando MTGJSON (arquivos individuais)...")
    
    success_count = 0
    for name, url in MTGJSON_URLS.items():
        filename = f"{name}.json"
        if download_file(url, filename):
            success_count += 1
    
    print(f"\nConcluido: {success_count}/{len(MTGJSON_URLS)} arquivos baixados")
    return success_count > 0


def load_atomic_cards() -> Dict:
    """Carrega AtomicCards (cartas unificadas)."""
    filepath = os.path.join(MTGJSON_DIR, 'AtomicCards.json')
    
    if not os.path.exists(filepath):
        return {}
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"AtomicCards carregado: {len(data.get('data', {}))} cartas")
        return data.get('data', {})
    
    except Exception as e:
        print(f"Erro ao carregar AtomicCards: {e}")
        return {}


def load_keywords() -> List:
    """Carrega lista de keywords."""
    filepath = os.path.join(MTGJSON_DIR, 'Keywords.json')
    
    if not os.path.exists(filepath):
        return []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        keywords = data.get('data', [])
        print(f"Keywords carregadas: {len(keywords)}")
        return keywords
    
    except Exception as e:
        print(f"Erro ao carregar Keywords: {e}")
        return []


def load_comp_rules() -> Dict:
    """Carrega regras completas."""
    filepath = os.path.join(MTGJSON_DIR, 'CompRules.json')
    
    if not os.path.exists(filepath):
        return {}
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        rules = data.get('data', {})
        print(f"Regras carregadas: {len(rules)} regras")
        return rules
    
    except Exception as e:
        print(f"Erro ao carregar CompRules: {e}")
        return {}


def integrate_with_local_db():
    """Integra dados do MTGJSON com o banco local."""
    print("\nIntegrando com banco local...")
    
    atomic_cards = load_atomic_cards()
    if not atomic_cards:
        print("Nenhuma carta encontrada para integrar")
        return
    
    # Salva cartas integradas
    integrated_filepath = os.path.join(MTGJSON_DIR, 'integrated_cards.json')
    
    integrated_data = {}
    for card_name, card_versions in atomic_cards.items():
        # Pega a versao mais recente
        if isinstance(card_versions, list) and len(card_versions) > 0:
            latest = card_versions[0]
            integrated_data[card_name] = {
                'name': latest.get('name'),
                'mana_cost': latest.get('manaCost', ''),
                'cmc': latest.get('convertedManaCost', 0),
                'types': latest.get('types', []),
                'text': latest.get('text', ''),
                'power': latest.get('power'),
                'toughness': latest.get('toughness'),
                'colors': latest.get('colors', []),
                'keywords': latest.get('keywords', []),
                'legalities': latest.get('legalities', {}),
            }
    
    with open(integrated_filepath, 'w', encoding='utf-8') as f:
        json.dump(integrated_data, f, ensure_ascii=False, indent=2)
    
    print(f"Cartas integradas salvas: {len(integrated_data)} cartas")
    return integrated_data


if __name__ == '__main__':
    print("=" * 60)
    print("MTG Match Simulator - MTGJSON Integration (Otimizado)")
    print("=" * 60)
    
    # Baixa arquivos individuais
    if download_mtgjson_optimized():
        # Integra com banco local
        integrate_with_local_db()
        
        # Carrega keywords
        keywords = load_keywords()
        
        # Carrega regras
        rules = load_comp_rules()
        
        print("\n" + "=" * 60)
        print("Integracao concluida!")
        print("=" * 60)
