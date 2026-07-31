"""
MTG Match Simulator - Modern Meta Decks
Decklists competitivos do formato Modern pré-definidos.
"""

import json
import os
from typing import Dict, List


# Diretório local
DECKLISTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'decklists')
os.makedirs(DECKLISTS_DIR, exist_ok=True)


# Top Modern Decks (baseado em meta atual)
MODERN_META_DECKS = {
    "Ad Nauseam": {
        "format": "modern",
        "cards": [
            {"name": "Thassa's Oracle", "quantity": 4},
            {"name": "Ad Nauseam", "quantity": 4},
            {"name": "Angel's Grace", "quantity": 4},
            {"name": "Phyrexian Unlife", "quantity": 4},
            {"name": "Lotus Bloom", "quantity": 4},
            {"name": "Pact of Negation", "quantity": 4},
            {"name": "Force of Negation", "quantity": 4},
            {"name": "Preordain", "quantity": 4},
            {"name": "Profane Tutor", "quantity": 4},
            {"name": "Sleight of Hand", "quantity": 2},
            {"name": "Spoils of the Vault", "quantity": 2},
            {"name": "Path to Exile", "quantity": 2},
            {"name": "Seachrome Coast", "quantity": 4},
            {"name": "Concealed Courtyard", "quantity": 4},
            {"name": "Darkslick Shores", "quantity": 2},
            {"name": "Hallowed Fountain", "quantity": 2},
            {"name": "Watery Grave", "quantity": 2},
            {"name": "Godless Shrine", "quantity": 1},
            {"name": "Gemstone Mine", "quantity": 2},
            {"name": "Otawara, Soaring City", "quantity": 1}
        ]
    },
    
    "Izzet Murktide": {
        "format": "modern",
        "cards": [
            {"name": "Murktide Regent", "quantity": 4},
            {"name": "Ragavan, Nimble Pilferer", "quantity": 4},
            {"name": "Dragon's Rage Channeler", "quantity": 4},
            {"name": "Expressive Iteration", "quantity": 4},
            {"name": "Lightning Bolt", "quantity": 4},
            {"name": "Spell Snare", "quantity": 2},
            {"name": "Counterspell", "quantity": 2},
            {"name": "Unholy Heat", "quantity": 4},
            {"name": "Thought Scour", "quantity": 4},
            {"name": "Serum Visions", "quantity": 4},
            {"name": "Steam Vents", "quantity": 4},
            {"name": "Scalding Tarn", "quantity": 4},
            {"name": "Spirebluff Canal", "quantity": 2},
            {"name": "Island", "quantity": 5},
            {"name": "Mountain", "quantity": 3}
        ]
    },
    
    "Amulet Titan": {
        "format": "modern",
        "cards": [
            {"name": "Primeval Titan", "quantity": 4},
            {"name": "Simian Spirit Guide", "quantity": 4},
            {"name": "Goblin Engineer", "quantity": 2},
            {"name": "Ancient Stirrings", "quantity": 4},
            {"name": "Sylvan Scrying", "quantity": 4},
            {"name": "Expedition Map", "quantity": 4},
            {"name": "Amulet of Vigor", "quantity": 4},
            {"name": "Urza's Saga", "quantity": 2},
            {"name": "Eldrazi Temple", "quantity": 2},
            {"name": "Cloudpost", "quantity": 2},
            {"name": "Tolaria West", "quantity": 2},
            {"name": "Valakut, the Molten Pinnacle", "quantity": 4},
            {"name": "Forest", "quantity": 6},
            {"name": "Mountain", "quantity": 4}
        ]
    },
    
    "Hollow One": {
        "format": "modern",
        "cards": [
            {"name": "Hollow One", "quantity": 4},
            {"name": "Goblin Charbelcher", "quantity": 2},
            {"name": "Flame Slash", "quantity": 4},
            {"name": "Faithless Looting", "quantity": 4},
            {"name": "Gurmag Angler", "quantity": 4},
            {"name": "Merciless Executioner", "quantity": 2},
            {"name": "Dread Return", "quantity": 3},
            {"name": "Vengevine", "quantity": 4},
            {"name": "Bazaar of Baghdad", "quantity": 4},
            {"name": "Bloodghast", "quantity": 4},
            {"name": "Bridge from Below", "quantity": 4},
            {"name": "Stirling Castle", "quantity": 4},
            {"name": "Blackcleave Cliffs", "quantity": 2},
            {"name": "Bloodstained Mire", "quantity": 4},
            {"name": "Swamp", "quantity": 3},
            {"name": "Mountain", "quantity": 2}
        ]
    },
    
    "Prowess": {
        "format": "modern",
        "cards": [
            {"name": "Monastery Swiftspear", "quantity": 4},
            {"name": "Soul-Scar Mage", "quantity": 4},
            {"name": "Goblin Guide", "quantity": 4},
            {"name": "Eidolon of the Great Revel", "quantity": 4},
            {"name": "Lava Dart", "quantity": 2},
            {"name": "Lightning Bolt", "quantity": 4},
            {"name": "Lava Spike", "quantity": 4},
            {"name": "Rift Bolt", "quantity": 2},
            {"name": "Burst Lightning", "quantity": 2},
            {"name": "Mishra's Bauble", "quantity": 4},
            {"name": "Mountain", "quantity": 18},
            {"name": "Sacred Foundry", "quantity": 2}
        ]
    },
    
    "Jund": {
        "format": "modern",
        "cards": [
            {"name": "Bloodbraid Elf", "quantity": 4},
            {"name": "Dark Confidant", "quantity": 3},
            {"name": "Kolaghan's Command", "quantity": 4},
            {"name": "Lightning Bolt", "quantity": 4},
            {"name": "Fatal Push", "quantity": 4},
            {"name": "Inquisition of Kozilek", "quantity": 4},
            {"name": "Thoughtseize", "quantity": 3},
            {"name": "Tarmogoyf", "quantity": 4},
            {"name": "Wrenn and Six", "quantity": 2},
            {"name": "Liliana of the Veil", "quantity": 2},
            {"name": "Blood Crypt", "quantity": 3},
            {"name": "Overgrown Tomb", "quantity": 2},
            {"name": "Stomping Ground", "quantity": 2},
            {"name": "Forest", "quantity": 3},
            {"name": "Mountain", "quantity": 3},
            {"name": "Swamp", "quantity": 2}
        ]
    },
    
    "Death's Shadow": {
        "format": "modern",
        "cards": [
            {"name": "Death's Shadow", "quantity": 4},
            {"name": "Temur Battle Rage", "quantity": 4},
            {"name": "Ragavan, Nimble Pilferer", "quantity": 4},
            {"name": "Lightning Bolt", "quantity": 4},
            {"name": "Fatal Push", "quantity": 4},
            {"name": "Daze", "quantity": 2},
            {"name": "Counterspell", "quantity": 2},
            {"name": "Delirium Skeins", "quantity": 4},
            {"name": "Thought Scour", "quantity": 4},
            {"name": "Street Wraith", "quantity": 4},
            {"name": "Watery Grave", "quantity": 3},
            {"name": "Steam Vents", "quantity": 2},
            {"name": "Scalding Tarn", "quantity": 4},
            {"name": "Island", "quantity": 3},
            {"name": "Swamp", "quantity": 3},
            {"name": "Mountain", "quantity": 2}
        ]
    },
    
    "Urza's Saga Tron": {
        "format": "modern",
        "cards": [
            {"name": "Karn Liberated", "quantity": 4},
            {"name": "Expedition Map", "quantity": 4},
            {"name": "Chromatic Star", "quantity": 4},
            {"name": "Chromatic Sphere", "quantity": 4},
            {"name": "Sylvan Scrying", "quantity": 4},
            {"name": "Urza's Mine", "quantity": 4},
            {"name": "Urza's Power Plant", "quantity": 4},
            {"name": "Urza's Tower", "quantity": 4},
            {"name": "Urza's Saga", "quantity": 4},
            {"name": "Oblivion Stone", "quantity": 2},
            {"name": "Mindslaver", "quantity": 1},
            {"name": "Forest", "quantity": 6},
            {"name": "Wastes", "quantity": 3}
        ]
    }
}


def save_modern_decks():
    """Salva decklists Modern em arquivos."""
    print("Salvando Modern Meta Decks...")
    
    decklists = []
    
    for deck_name, deck_data in MODERN_META_DECKS.items():
        decklist = {
            'name': deck_name,
            'format': deck_data['format'],
            'cards': deck_data['cards']
        }
        decklists.append(decklist)
        
        # Salva individualmente
        safe_name = deck_name.replace(' ', '_').replace("'", '')
        filepath = os.path.join(DECKLISTS_DIR, f"modern_{safe_name}.json")
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(decklist, f, ensure_ascii=False, indent=2)
        
        print(f"  [OK] {deck_name} ({len(deck_data['cards'])} tipos)")
    
    # Salva índice
    index_filepath = os.path.join(DECKLISTS_DIR, "modern_index.json")
    with open(index_filepath, 'w', encoding='utf-8') as f:
        json.dump(decklists, f, ensure_ascii=False, indent=2)
    
    print(f"\nTotal: {len(decklists)} decklists salvos")
    return decklists


def load_modern_decks() -> List[Dict]:
    """Carrega decklists Modern."""
    index_filepath = os.path.join(DECKLISTS_DIR, "modern_index.json")
    
    if not os.path.exists(index_filepath):
        return save_modern_decks()
    
    try:
        with open(index_filepath, 'r', encoding='utf-8') as f:
            decklists = json.load(f)
        
        print(f"Decklists Modern carregados: {len(decklists)}")
        return decklists
        
    except Exception as e:
        print(f"Erro ao carregar decklists: {e}")
        return []


if __name__ == '__main__':
    print("=" * 60)
    print("MTG Match Simulator - Modern Meta Decks")
    print("=" * 60)
    
    decklists = save_modern_decks()
    
    print(f"\nDecks disponíveis:")
    for deck in decklists:
        total_cards = sum(card['quantity'] for card in deck['cards'])
        print(f"  - {deck['name']} ({total_cards} cartas)")
