"""
MTG Match Simulator - MTGGoldfish Decklist Scraper
Baixa decklists competitivos do MTGGoldfish.
"""

import json
import os
import re
import urllib.request
from typing import Dict, List
from html.parser import HTMLParser


# Diretório local
DECKLISTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'decklists')
os.makedirs(DECKLISTS_DIR, exist_ok=True)


class MTGGoldfishParser(HTMLParser):
    """Parser HTML para decklists do MTGGoldfish."""
    
    def __init__(self):
        super().__init__()
        self.decks = []
        self.current_deck = {}
        self.in_deck_link = False
        self.in_deck_author = False
    
    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == 'a' and 'href' in attrs_dict:
            href = attrs_dict['href']
            if '/deck/' in href and href.endswith('#minimize'):
                self.in_deck_link = True
                self.current_deck = {'url': href}
    
    def handle_data(self, data):
        if self.in_deck_link:
            data = data.strip()
            if data and not self.current_deck.get('name'):
                self.current_deck['name'] = data
    
    def handle_endtag(self, tag):
        if tag == 'a' and self.in_deck_link:
            if self.current_deck.get('name') and self.current_deck.get('url'):
                self.decks.append(self.current_deck)
            self.in_deck_link = False
            self.current_deck = {}


def scrape_mtggoldfish_modern() -> List[Dict]:
    """Scrape decklists Modern do MTGGoldfish."""
    url = 'https://www.mtggoldfish.com/decks/modern'
    
    print(f"Scraping: {url}")
    
    try:
        req = urllib.request.Request(
            url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        )
        
        with urllib.request.urlopen(req) as response:
            html = response.read().decode('utf-8')
        
        parser = MTGGoldfishParser()
        parser.feed(html)
        
        print(f"  Encontrados {len(parser.decks)} decks")
        return parser.decks
        
    except Exception as e:
        print(f"  Erro ao scraping: {e}")
        return []


def scrape_deck_details(deck_url: str) -> Dict:
    """Scrape detalhes de um deck específico."""
    full_url = f"https://www.mtggoldfish.com{deck_url}"
    
    try:
        req = urllib.request.Request(
            full_url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        )
        
        with urllib.request.urlopen(req) as response:
            html = response.read().decode('utf-8')
        
        # Extrai lista de cartas do HTML
        # Padrão: <td class="deck-card-name">Card Name</td><td class="deck-card-qty">4</td>
        cards = []
        name_pattern = re.compile(r'<td class="deck-card-name">(.*?)</td>')
        qty_pattern = re.compile(r'<td class="deck-card-qty">(\d+)</td>')
        
        names = name_pattern.findall(html)
        qtys = qty_pattern.findall(html)
        
        for name, qty in zip(names, qtys):
            cards.append({
                'name': name.strip(),
                'quantity': int(qty)
            })
        
        return {'cards': cards, 'url': full_url}
        
    except Exception as e:
        print(f"  Erro ao scraping {full_url}: {e}")
        return {}


def download_top_decks(format_code: str = 'modern', max_decks: int = 50):
    """Baixa os top decks de um formato."""
    print(f"\nBaixando top {max_decks} decks {format_code}...")
    
    # Scrape lista de decks
    decks = scrape_mtggoldfish_modern()
    
    if not decks:
        print("  Nenhum deck encontrado")
        return
    
    # Limita quantidade
    decks = decks[:max_decks]
    
    # Baixa detalhes de cada deck
    decklists = []
    for i, deck in enumerate(decks):
        print(f"  [{i+1}/{len(decks)}] {deck.get('name', 'Unknown')}")
        
        details = scrape_deck_details(deck['url'])
        if details:
            decklist = {
                'name': deck.get('name', 'Unknown'),
                'format': format_code,
                'url': deck['url'],
                'cards': details.get('cards', [])
            }
            decklists.append(decklist)
            
            # Salva individualmente
            safe_name = re.sub(r'[^\w\s-]', '', deck.get('name', 'unknown'))[:50]
            filepath = os.path.join(DECKLISTS_DIR, f"{format_code}_{safe_name}.json")
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(decklist, f, ensure_ascii=False, indent=2)
    
    # Salva índice
    index_filepath = os.path.join(DECKLISTS_DIR, f"{format_code}_index.json")
    with open(index_filepath, 'w', encoding='utf-8') as f:
        json.dump(decklists, f, ensure_ascii=False, indent=2)
    
    print(f"\n  Total: {len(decklists)} decklists salvos")
    return decklists


def load_decklists(format_code: str = 'modern') -> List[Dict]:
    """Carrega decklists salvos."""
    index_filepath = os.path.join(DECKLISTS_DIR, f"{format_code}_index.json")
    
    if not os.path.exists(index_filepath):
        return []
    
    try:
        with open(index_filepath, 'r', encoding='utf-8') as f:
            decklists = json.load(f)
        
        print(f"Decklists carregados: {len(decklists)}")
        return decklists
        
    except Exception as e:
        print(f"Erro ao carregar decklists: {e}")
        return []


if __name__ == '__main__':
    print("=" * 60)
    print("MTG Match Simulator - MTGGoldfish Scraper")
    print("=" * 60)
    
    # Baixa top decks Modern
    decklists = download_top_decks('modern', max_decks=20)
    
    if decklists:
        print(f"\nPrimeiros 5 decks:")
        for deck in decklists[:5]:
            print(f"  - {deck['name']} ({len(deck['cards'])} tipos)")
