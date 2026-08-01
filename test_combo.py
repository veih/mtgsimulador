import sys
sys.path.insert(0, '.')
from src.simulator_v2 import MatchSimulatorV2
sim = MatchSimulatorV2('modern_Ad_Nauseam', 'modern_Jund', verbosity=1)
an_wins = 0; jund_wins = 0; draws = 0; turns_list = []
for i in range(1, 11):
    r = sim.simulate_match(i)
    turns_list.append(r.turns)
    if r.winner_name == 'modern_Ad_Nauseam': an_wins += 1
    elif r.winner_name == 'modern_Jund': jund_wins += 1
    else: draws += 1
print('--- RESULTADOS ---')
print(f'Ad Nauseam: {an_wins} | Jund: {jund_wins} | Empate: {draws}')
print(f'Turnos: {turns_list}')
