import sys
sys.path.insert(0, '.')
from src.simulator_v2 import MatchSimulatorV2
from modern_meta_decks import load_modern_decks
from src.cards_db import get_card

def build_deck(deck_name):
    modern_decks = {d['name']: d for d in load_modern_decks()}
    if deck_name not in modern_decks:
        raise ValueError(f'Deck {deck_name!r} nao encontrado. Disponiveis: {list(modern_decks.keys())}')
    cards = []
    for entry in modern_decks[deck_name]['cards']:
        cname = entry['name']
        qty = entry.get('quantity', entry.get('count', 1))
        try:
            card = get_card(cname.lower().replace(" ","_").replace("'","").replace(",","").replace(".",""))
        except ValueError:
            # Tenta pelo nome direto
            try:
                from src.cards_db import CARD_NAME_TO_ID
                cid = CARD_NAME_TO_ID.get(cname) or CARD_NAME_TO_ID.get(cname.lower())
                if cid:
                    card = get_card(cid)
                else:
                    print(f'  AVISO: Carta nao encontrada: {cname}')
                    continue
            except Exception as e:
                print(f'  ERRO: {cname}: {e}')
                continue
        for _ in range(qty):
            cards.append(card.copy())
    return cards

deck_an = build_deck('Ad Nauseam')
deck_jund = build_deck('Jund')
print(f'Ad Nauseam: {len(deck_an)} cartas | Jund: {len(deck_jund)} cartas')

sim = MatchSimulatorV2(deck_an, deck_jund, 'Ad Nauseam', 'Jund', verbosity=1)
an_wins = 0
jund_wins = 0
draws = 0
turns_list = []

for i in range(1, 11):
    r = sim.simulate_match(i)
    turns_list.append(r.turns)
    if r.winner_name == 'Ad Nauseam':
        an_wins += 1
    elif r.winner_name == 'Jund':
        jund_wins += 1
    else:
        draws += 1

print('--- RESULTADOS ---')
print(f'Ad Nauseam: {an_wins} | Jund: {jund_wins} | Empate: {draws}')
print(f'Turnos: {turns_list}')

# Mostra o log da ultima partida para verificar o combo
print('\n--- LOG DA ULTIMA PARTIDA (fragmento) ---')
log = sim.last_log if hasattr(sim, 'last_log') else []
for line in log[-60:]:
    if any(kw in line for kw in ['Ad Nauseam', 'Thassa', 'Spoils', 'Lotus Bloom', 'Angel', 'Oracle',
                                   'Suspend', 'Phyrexian', 'combo', 'VENCE', 'venceu', 'library']):
        print(line)
