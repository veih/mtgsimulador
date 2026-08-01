import sys
sys.path.insert(0, '.')
from modern_meta_decks import load_modern_decks
from src.cards_db import get_card, CARD_NAME_TO_ID

def build_deck(deck_name, all_decks):
    cards = []
    missing = []
    deck = next(d for d in all_decks if d['name'] == deck_name)
    for entry in deck['cards']:
        cname = entry['name']
        qty = entry.get('quantity', 1)
        cid = cname.lower().replace(" ", "_").replace("'", "").replace(",", "").replace(".", "")
        try:
            card = get_card(cid)
        except ValueError:
            cid2 = CARD_NAME_TO_ID.get(cname) or CARD_NAME_TO_ID.get(cname.lower())
            if cid2:
                card = get_card(cid2)
            else:
                missing.append(cname)
                continue
        for _ in range(qty):
            cards.append(card.copy())
    return cards, missing

all_decks = load_modern_decks()
print()
all_ok = True
for d in all_decks:
    total = sum(e.get('quantity', 1) for e in d['cards'])
    cards, missing = build_deck(d['name'], all_decks)
    if missing:
        all_ok = False
        print(f"  {d['name']}: {len(cards)}/{total} | MISSING: {missing}")
    else:
        print(f"  {d['name']}: {len(cards)}/{total} cards | OK")

print()
if all_ok:
    print("ALL DECKS COMPLETE - no missing cards!")
else:
    print("Some cards still missing.")
