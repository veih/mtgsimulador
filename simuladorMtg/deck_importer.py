"""
MTG Match Simulator - Importador de Decks
Permite importar decks de arquivos externos (JSON, TXT, MTG Arena format).
"""

import json
import os
import re
from typing import List, Dict, Optional, Tuple
from src.cards_db import get_card, CARD_NAME_TO_ID, ALL_CARDS
from src.card import Card, Color, CardType, ManaCost, Keyword, EffectType, SpellEffect, TargetType
from src.land_effects import get_land_mana_from_known, LandEffectParser

# Pasta para decks customizados
CUSTOM_DECKS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'custom_decks')
os.makedirs(CUSTOM_DECKS_DIR, exist_ok=True)

# Pasta de dados do Scryfall (Desktop)
SCRYFALL_DATA_DIR = os.path.join(os.path.expanduser('~'), 'Desktop', 'MTG_Cards', 'data')
# Pasta local de dados do projeto (coleções baixadas pelo download_sets.py)
LOCAL_CARDS_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cards_data')

# Cache de cartas do Scryfall
_scryfall_cache: Dict[str, Dict] = {}


def _load_scryfall_cards():
    """Carrega cartas dos dados do Scryfall (Desktop + pasta local do projeto)."""
    global _scryfall_cache
    if _scryfall_cache:
        return
    
    # Carrega de ambas as pastas
    for data_dir in [SCRYFALL_DATA_DIR, LOCAL_CARDS_DATA_DIR]:
        if not os.path.exists(data_dir):
            continue
        
        for set_folder in os.listdir(data_dir):
            cards_file = os.path.join(data_dir, set_folder, 'cards.json')
            if os.path.exists(cards_file):
                try:
                    with open(cards_file, 'r', encoding='utf-8') as f:
                        cards = json.load(f)
                        for card in cards:
                            name = card.get('name', '')
                            if name and name not in _scryfall_cache:
                                _scryfall_cache[name] = card
                                _scryfall_cache[name.lower()] = card
                except Exception as e:
                    print(f"Erro ao carregar {cards_file}: {e}")
    
    print(f"Cache do Scryfall: {len(_scryfall_cache)//2} cartas carregadas")


def _parse_mana_cost(mana_str: str) -> ManaCost:
    """Parseia uma string de mana no formato {1}{R}{G} em ManaCost."""
    cost = ManaCost()
    if not mana_str:
        return cost
    
    # Remove chaves e parseia
    symbols = re.findall(r'\{([^}]+)\}', mana_str)
    for sym in symbols:
        sym = sym.upper()
        if sym.isdigit():
            cost.generic += int(sym)
        elif sym == 'W':
            cost.white += 1
        elif sym == 'U':
            cost.blue += 1
        elif sym == 'B':
            cost.black += 1
        elif sym == 'R':
            cost.red += 1
        elif sym == 'G':
            cost.green += 1
    
    return cost


def _parse_card_type(type_line: str) -> CardType:
    """Determina o CardType a partir da type line."""
    type_lower = type_line.lower()
    if 'creature' in type_lower:
        return CardType.CREATURE
    elif 'instant' in type_lower:
        return CardType.INSTANT
    elif 'sorcery' in type_lower:
        return CardType.SORCERY
    elif 'planeswalker' in type_lower:
        return CardType.PLANESWALKER
    elif 'artifact' in type_lower:
        return CardType.ARTIFACT
    elif 'enchantment' in type_lower:
        return CardType.ENCHANTMENT
    return CardType.ARTIFACT  # default


def _parse_colors(type_line: str, colors: list) -> set:
    """Determina as cores a partir da type line e cores do Scryfall."""
    color_set = set()
    color_map = {'W': Color.WHITE, 'U': Color.BLUE, 'B': Color.BLACK, 'R': Color.RED, 'G': Color.GREEN}
    for c in colors:
        if c in color_map:
            color_set.add(color_map[c])
    return color_set


def _parse_keywords(oracle_text: str) -> list:
    """Extrai keywords do texto da carta."""
    keywords = []
    keyword_map = {
        'haste': Keyword.HASTE,
        'flying': Keyword.FLYING,
        'trample': Keyword.TRAMPLE,
        'deathtouch': Keyword.DEATHTOUCH,
        'lifelink': Keyword.LIFELINK,
        'first strike': Keyword.FIRST_STRIKE,
        'vigilance': Keyword.VIGILANCE,
        'hexproof': Keyword.HEXPROOF,
        'indestructible': Keyword.INDESTRUCTIBLE,
        'reach': Keyword.REACH,
        'menace': Keyword.MENACE,
    }
    text_lower = oracle_text.lower() if oracle_text else ''
    for kw_str, kw_enum in keyword_map.items():
        if kw_str in text_lower:
            keywords.append(kw_enum)
    return keywords


def create_card_from_scryfall(card_name: str) -> Optional[Card]:
    """Cria uma Card a partir dos dados do Scryfall."""
    _load_scryfall_cards()
    
    card_data = _scryfall_cache.get(card_name) or _scryfall_cache.get(card_name.lower())
    if not card_data:
        return None
    
    try:
        name = card_data.get('name', card_name)
        mana_str = card_data.get('mana_cost', '')
        mana_cost = _parse_mana_cost(mana_str)
        type_line = card_data.get('type_line', '')
        card_type = _parse_card_type(type_line)
        colors = _parse_colors(type_line, card_data.get('colors', []))
        oracle_text = card_data.get('oracle_text', '')
        keywords = _parse_keywords(oracle_text)
        
        # Power/Toughness para criaturas
        power = None
        toughness = None
        pt_match = re.search(r'(\d+)\s*/\s*(\d+)', card_data.get('power', '') + '/' + card_data.get('toughness', ''))
        if pt_match:
            power = int(pt_match.group(1))
            toughness = int(pt_match.group(2))
        
        # Efeitos simplificados
        effects = []
        if 'damage' in oracle_text.lower():
            dmg_match = re.search(r'(\d+) damage', oracle_text.lower())
            if dmg_match:
                effects.append(SpellEffect(EffectType.DAMAGE, int(dmg_match.group(1)), 
                                          target_type=TargetType.CREATURE_OR_PLAYER))
        
        # Land detection
        is_land = 'land' in type_line.lower()
        land_mana = set()
        if is_land:
            # Primeiro tenta buscar no dicionário de terrenos conhecidos
            known_mana = get_land_mana_from_known(name)
            if known_mana:
                land_mana = known_mana
            else:
                oracle_lower = oracle_text.lower() if oracle_text else ''
                # Terrenos básicos
                if 'plains' in name.lower():
                    land_mana = {Color.WHITE}
                elif 'island' in name.lower():
                    land_mana = {Color.BLUE}
                elif 'swamp' in name.lower():
                    land_mana = {Color.BLACK}
                elif 'mountain' in name.lower():
                    land_mana = {Color.RED}
                elif 'forest' in name.lower():
                    land_mana = {Color.GREEN}
                # Terrenos não-básicos - parseia o texto
                else:
                    # Usa o parser avançado
                    land_mana = LandEffectParser.parse_land_mana(name, oracle_text)
        
        card_id = re.sub(r'[^a-z0-9]', '_', name.lower()).strip('_')
        
        card = Card(
            id=card_id,
            name=name,
            mana_cost=mana_cost,
            card_type=card_type,
            colors=colors,
            text=oracle_text[:200],
            keywords=keywords,
            effects=effects,
            is_land=is_land,
            land_mana=land_mana,
            power=power or 0,
            toughness=toughness or 0,
        )
        
        # Registra no cache para uso futuro
        ALL_CARDS[card_id] = card
        CARD_NAME_TO_ID[name] = card_id
        CARD_NAME_TO_ID[name.lower()] = card_id
        
        return card
        
    except Exception as e:
        print(f"Erro ao criar carta {card_name}: {e}")
        return None


def parse_mtg_arena_format(text: str) -> Tuple[List[Tuple[str, int]], Optional[str], int]:
    """
    Parseia o formato de exportação do MTG Arena.
    
    Formato exemplo:
    4 Lightning Bolt (M21) 123
    20 Mountain (M21) 254
    
    Retorna: (lista de (card_name, qty), land_name, land_count)
    """
    cards = []
    lands = []
    land_name = None
    land_count = 0
    
    # Regex para linhas do formato Arena: "4 Card Name (SET) 123"
    pattern = r'^(\d+)\s+(.+?)(?:\s+\((\w+)\)\s+(\d+))?$'
    
    for line in text.strip().split('\n'):
        line = line.strip()
        if not line or line.startswith('//') or line.startswith('Deck'):
            continue
        
        match = re.match(pattern, line)
        if match:
            qty = int(match.group(1))
            card_name = match.group(2).strip()
            
            # Verifica se é terreno básico
            if card_name.lower() in ['plains', 'island', 'swamp', 'mountain', 'forest',
                                      'planicie', 'ilha', 'pantano', 'montanha', 'floresta']:
                land_name = card_name.lower()
                land_count = qty
            else:
                cards.append((card_name, qty))
    
    return cards, land_name, land_count


def parse_simple_format(text: str) -> Tuple[List[Tuple[str, int]], Optional[str], int]:
    """
    Parseia formato simples: "4 Lightning Bolt" por linha.
    """
    cards = []
    land_name = None
    land_count = 0
    
    basic_lands = ['plains', 'island', 'swamp', 'mountain', 'forest',
                   'planicie', 'ilha', 'pantano', 'montanha', 'floresta']
    
    for line in text.strip().split('\n'):
        line = line.strip()
        if not line or line.startswith('#') or line.startswith('//'):
            continue
        
        # Tenta extrair quantidade e nome
        match = re.match(r'^(\d+)x?\s+(.+)$', line, re.IGNORECASE)
        if match:
            qty = int(match.group(1))
            card_name = match.group(2).strip()
            
            if card_name.lower() in basic_lands:
                land_name = card_name.lower()
                land_count = qty
            else:
                cards.append((card_name, qty))
        else:
            # Linha sem quantidade, assume 1
            card_name = line.strip()
            if card_name.lower() in basic_lands:
                land_name = card_name.lower()
                land_count += 1
            else:
                cards.append((card_name, 1))
    
    return cards, land_name, land_count


def find_card_id(card_name: str) -> Optional[str]:
    """
    Tenta encontrar o ID de uma carta pelo nome.
    Busca no mapeamento local, depois no Scryfall.
    """
    # Busca direta no cache local
    if card_name in CARD_NAME_TO_ID:
        return CARD_NAME_TO_ID[card_name]
    
    # Busca case-insensitive no cache local
    name_lower = card_name.lower()
    for name, card_id in CARD_NAME_TO_ID.items():
        if name.lower() == name_lower:
            return card_id
    
    # Busca parcial no cache local
    for name, card_id in CARD_NAME_TO_ID.items():
        if name_lower in name.lower() or name.lower() in name_lower:
            return card_id
    
    # Tenta criar a carta a partir do Scryfall
    card = create_card_from_scryfall(card_name)
    if card:
        return card.id
    
    return None


def build_deck_from_names(card_names: List[Tuple[str, int]], land_name: str = None, 
                          land_count: int = 0) -> Dict:
    """
    Constroi um deck a partir de nomes de cartas.
    
    Retorna dict com estrutura do deck ou erro.
    """
    deck_cards = []
    missing_cards = []
    
    for card_name, qty in card_names:
        card_id = find_card_id(card_name)
        if card_id:
            deck_cards.append((card_id, qty))
        else:
            missing_cards.append(card_name)
    
    # Resolve terreno
    actual_land_name = land_name
    if land_name:
        land_id = find_card_id(land_name)
        if land_id:
            actual_land_name = land_id
        else:
            # Mapeia nomes em português
            land_map = {
                'planicie': 'plains', 'ilha': 'island', 'pantano': 'swamp',
                'montanha': 'mountain', 'floresta': 'forest',
                'plains': 'plains', 'island': 'island', 'swamp': 'swamp',
                'mountain': 'mountain', 'forest': 'forest'
            }
            actual_land_name = land_map.get(land_name.lower(), 'plains')
    
    return {
        'cards': deck_cards,
        'land': actual_land_name,
        'land_count': land_count if land_count > 0 else 20,
        'missing': missing_cards
    }


def import_deck_from_text(text: str, deck_name: str = "Custom Deck") -> Dict:
    """
    Importa um deck a partir de texto (formato Arena ou simples).
    """
    # Tenta formato Arena primeiro
    cards, land_name, land_count = parse_mtg_arena_format(text)
    
    # Se não encontrou nada, tenta formato simples
    if not cards:
        cards, land_name, land_count = parse_simple_format(text)
    
    if not cards:
        return {'error': 'Nenhuma carta encontrada no texto'}
    
    deck_data = build_deck_from_names(cards, land_name, land_count)
    deck_data['name'] = deck_name
    
    return deck_data


def import_deck_from_json(json_data: Dict) -> Dict:
    """
    Importa um deck a partir de JSON.
    
    Formato esperado:
    {
        "name": "Nome do Deck",
        "cards": [
            {"name": "Lightning Bolt", "qty": 4},
            ...
        ],
        "land": "mountain",
        "land_count": 20
    }
    """
    name = json_data.get('name', 'Custom Deck')
    cards_data = json_data.get('cards', [])
    
    cards = []
    for card in cards_data:
        if isinstance(card, dict):
            card_name = card.get('name', '')
            qty = card.get('qty', card.get('quantity', 1))
            cards.append((card_name, qty))
        elif isinstance(card, (list, tuple)) and len(card) >= 2:
            cards.append((card[0], card[1]))
    
    land_name = json_data.get('land', json_data.get('land_type', None))
    land_count = json_data.get('land_count', 20)
    
    deck_data = build_deck_from_names(cards, land_name, land_count)
    deck_data['name'] = name
    
    return deck_data


def save_custom_deck(deck_data: Dict, filename: str = None) -> str:
    """
    Salva um deck customizado na pasta de decks customizados.
    Retorna o caminho do arquivo salvo.
    """
    if filename is None:
        name = deck_data.get('name', 'custom_deck')
        filename = re.sub(r'[^\w\-]', '_', name) + '.json'
    
    filepath = os.path.join(CUSTOM_DECKS_DIR, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(deck_data, f, ensure_ascii=False, indent=2)
    
    return filepath


def load_custom_decks() -> List[Dict]:
    """
    Carrega todos os decks customizados salvos.
    """
    decks = []
    
    if not os.path.exists(CUSTOM_DECKS_DIR):
        return decks
    
    for filename in os.listdir(CUSTOM_DECKS_DIR):
        if filename.endswith('.json'):
            filepath = os.path.join(CUSTOM_DECKS_DIR, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    deck_data = json.load(f)
                    deck_data['filename'] = filename
                    decks.append(deck_data)
            except Exception as e:
                print(f"Erro ao carregar deck {filename}: {e}")
    
    return decks


def delete_custom_deck(filename: str) -> bool:
    """
    Deleta um deck customizado.
    """
    filepath = os.path.join(CUSTOM_DECKS_DIR, filename)
    if os.path.exists(filepath):
        os.remove(filepath)
        return True
    return False


def get_custom_deck_as_cards(deck_data: Dict) -> List[Card]:
    """
    Converte um deck customizado em lista de Cards para usar no simulador.
    Busca no Scryfall se a carta não for encontrada localmente.
    """
    deck = []
    
    for card_id, qty in deck_data.get('cards', []):
        try:
            # Tenta buscar localmente primeiro
            try:
                card = get_card(card_id)
            except ValueError:
                # Se não encontrar, busca pelo nome no Scryfall
                card = None
                _load_scryfall_cards()
                
                # Tenta várias variações do nome
                variations = [
                    card_id,
                    card_id.lower(),
                    card_id.replace('_', ' ').title(),
                    card_id.replace('__', ', ').replace('_', ' ').title(),  # otawara__soaring_city -> Otawara, Soaring City
                    card_id.replace('_s_', "'s ").replace('_', ' ').title(),  # angel_s_grace -> Angel's Grace
                    card_id.replace('__', ', ').replace('_s_', "'s ").replace('_', ' ').title(),
                ]
                
                for name in variations:
                    if name in _scryfall_cache:
                        card = create_card_from_scryfall(_scryfall_cache[name]['name'])
                        if card:
                            break
                    elif name.lower() in _scryfall_cache:
                        card = create_card_from_scryfall(_scryfall_cache[name.lower()]['name'])
                        if card:
                            break
                
                if card is None:
                    print(f"Carta não encontrada: {card_id}")
                    continue
            
            for _ in range(qty):
                deck.append(card)
        except Exception as e:
            print(f"Erro ao adicionar carta {card_id}: {e}")
    
    # Adiciona terrenos
    # Verifica se tem múltiplos tipos de terrenos
    lands_list = deck_data.get('lands', [])
    if lands_list:
        # Múltiplos tipos de terrenos
        for land_id, land_qty in lands_list:
            try:
                try:
                    land_card = get_card(land_id)
                except ValueError:
                    # Busca no Scryfall
                    _load_scryfall_cards()
                    land_card = None
                    variations = [
                        land_id,
                        land_id.lower(),
                        land_id.replace('_', ' ').title(),
                        land_id.replace('__', ', ').replace('_', ' ').title(),
                    ]
                    for name in variations:
                        if name in _scryfall_cache:
                            land_card = create_card_from_scryfall(_scryfall_cache[name]['name'])
                            if land_card:
                                break
                        elif name.lower() in _scryfall_cache:
                            land_card = create_card_from_scryfall(_scryfall_cache[name.lower()]['name'])
                            if land_card:
                                break
                    
                    if land_card is None:
                        print(f"Terreno não encontrado: {land_id}")
                        continue
                
                for _ in range(land_qty):
                    deck.append(land_card)
            except Exception as e:
                print(f"Erro ao adicionar terreno {land_id}: {e}")
    else:
        # Terreno único
        land_name = deck_data.get('land', 'plains')
        land_count = deck_data.get('land_count', 20)
        
        if land_name and land_count > 0:
            try:
                land_card = get_card(land_name)
                for _ in range(land_count):
                    deck.append(land_card)
            except Exception as e:
                print(f"Erro ao adicionar terreno {land_name}: {e}")
                # Fallback para terrenos básicos
                for land in ['plains', 'island', 'swamp', 'mountain', 'forest']:
                    try:
                        land_card = get_card(land)
                        for _ in range(land_count // 5):
                            deck.append(land_card)
                    except:
                        pass
    
    return deck
