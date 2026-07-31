"""
Teste completo do deck Ad Nauseam
"""
import sys
sys.path.insert(0, '.')

from deck_importer import load_custom_decks, get_custom_deck_as_cards
from src.game_state import GameState, PlayerState
from src.rules_engine import RulesEngine
from src.player import AIPlayer

# Carrega o deck Ad Nauseam
print("=" * 60)
print("CARREGANDO DECK AD NAUSEAM")
print("=" * 60)

decks = load_custom_decks()
ad_deck = None
for d in decks:
    if d['name'] == 'Ad Nauseam':
        ad_deck = d
        break

if not ad_deck:
    print("ERRO: Deck 'Ad Nauseam' não encontrado!")
    sys.exit(1)

print(f"Deck encontrado: {ad_deck['name']}")
cards = get_custom_deck_as_cards(ad_deck)
print(f"Total de cartas: {len(cards)}")

# Mostra as cartas do deck
print("\nCartas do deck:")
card_names = {}
for card in cards:
    if card.name not in card_names:
        card_names[card.name] = 0
    card_names[card.name] += 1

for name, qty in sorted(card_names.items()):
    print(f"  {qty}x {name}")

# Cria os jogadores
print("\n" + "=" * 60)
print("INICIANDO PARTIDA")
print("=" * 60)

p1 = PlayerState('Jogador 1 (Ad Nauseam)')
p1.library = cards.copy()
p1.shuffle_library()
p1.hand = p1.library[:7]
p1.library = p1.library[7:]

p2 = PlayerState('Jogador 2 (Red Deck Wins)')
# Usa um deck simples para o oponente
from src.cards_db import ALL_CARDS
p2.library = [ALL_CARDS['lightning_bolt'].copy() for _ in range(20)]
p2.library += [ALL_CARDS['goblin_guide'].copy() for _ in range(20)]
p2.library += [ALL_CARDS['mountain'].copy() for _ in range(20)]
p2.shuffle_library()
p2.hand = p2.library[:7]
p2.library = p2.library[7:]

# Cria o estado do jogo
state = GameState(p1, p2)
state.logging_enabled = True
state._log_max = 1000  # Aumenta o limite do log

# Cria o motor de regras
engine = RulesEngine(state)

# Cria o controlador de IA
ai = AIPlayer()

# Simula alguns turnos
print("\nSimulando partida...\n")
max_turns = 10

for turn in range(1, max_turns + 1):
    if state.is_game_over:
        print(f"\n*** JOGO TERMINOU no turno {turn}! ***")
        break
    
    print(f"\n{'='*60}")
    print(f"TURNO {turn}")
    print(f"{'='*60}")
    
    # Mostra o estado antes do turno
    print(f"\nEstado antes do turno:")
    print(f"  {p1.name}: {p1.life} vida, {len(p1.hand)} cartas na mão, {len(p1.library)} na biblioteca")
    print(f"  {p2.name}: {p2.life} vida, {len(p2.hand)} cartas na mão, {len(p2.library)} na biblioteca")
    
    # Executa o turno
    engine.execute_turn(ai_controller=ai)
    
    # Mostra o log do turno
    if state.game_log:
        print(f"\nLog do turno:")
        for log_entry in state.game_log[-20:]:
            print(f"  {log_entry}")

# Mostra o resultado final
print("\n" + "=" * 60)
print("RESULTADO FINAL")
print("=" * 60)

if state.winner is not None:
    if state.winner == 0:
        print(f"VENCEDOR: {p1.name} (Ad Nauseam)!")
    elif state.winner == 1:
        print(f"VENCEDOR: {p2.name}")
    else:
        print("EMPATE!")
else:
    print("Jogo não terminou")

print(f"\nEstatísticas finais:")
print(f"  {p1.name}:")
print(f"    Vida: {p1.life}")
print(f"    Cartas na mão: {len(p1.hand)}")
print(f"    Cartas na biblioteca: {len(p1.library)}")
print(f"    Cartas no cemitério: {len(p1.graveyard)}")
print(f"    Cartas no exílio: {len(p1.exile)}")
print(f"    Magias conjuradas: {p1.spells_cast}")
print(f"    Dano causado: {p1.damage_dealt}")

print(f"\n  {p2.name}:")
print(f"    Vida: {p2.life}")
print(f"    Cartas na mão: {len(p2.hand)}")
print(f"    Cartas na biblioteca: {len(p2.library)}")
print(f"    Cartas no cemitério: {len(p2.graveyard)}")
print(f"    Cartas no exílio: {len(p2.exile)}")
print(f"    Magias conjuradas: {p2.spells_cast}")
print(f"    Dano causado: {p2.damage_dealt}")

print("\n" + "=" * 60)
