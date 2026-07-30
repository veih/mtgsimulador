#!/usr/bin/env python3
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import random
random.seed(42)

from decks import get_deck
from src.game_state import GameState, PlayerState
from src.rules_engine import RulesEngine
from src.player import AIPlayer

d1 = [c.copy() for c in get_deck('Red Deck Wins')]
d2 = [c.copy() for c in get_deck('Green Stompy')]
random.shuffle(d1)
random.shuffle(d2)

p1 = PlayerState(name='Red', life=20, library=d1)
p2 = PlayerState(name='Green', life=20, library=d2)
p1.draw_cards(7)
p2.draw_cards(7)

state = GameState(player1=p1, player2=p2)
engine = RulesEngine(state)
ai1 = AIPlayer()
ai2 = AIPlayer()

# Run 7 turns successfully
for i in range(7):
    ai = ai1 if state.active_player_index == 0 else ai2
    engine.execute_turn(ai)

print(f"Before turn 8: Turn={state.turn_number} Active={state.active_player_index}", flush=True)
print(f"  P1: life={p1.life} hand={len(p1.hand)} bf={len(p1.battlefield)} lib={len(p1.library)}", flush=True)
print(f"  P2: life={p2.life} hand={len(p2.hand)} bf={len(p2.battlefield)} lib={len(p2.library)}", flush=True)

# Show battlefield
for c in p1.battlefield:
    print(f"  P1 bf: {c.name} ({c.power}/{c.toughness}) tapped={c.tapped} sick={c.summoning_sick}", flush=True)
for c in p2.battlefield:
    print(f"  P2 bf: {c.name} ({c.power}/{c.toughness}) tapped={c.tapped} sick={c.summoning_sick}", flush=True)

# Now manually execute turn 8 step by step
active = state.active_player
inactive = state.non_active_player
ai = ai2 if state.active_player_index == 1 else ai1

print(f"\nExecuting turn 8 step by step...", flush=True)

print("  Untap...", flush=True)
engine._untap_step(active)
print("  Upkeep...", flush=True)
engine._upkeep_step(active)
print("  Draw...", flush=True)
engine._draw_step(active)
print(f"  After draw: active hand={len(active.hand)}", flush=True)

print("  Pre-combat main phase...", flush=True)
state.phase = "precombat_main"
ai.main_phase(active, inactive, state)
print(f"  After pre-combat: active hand={len(active.hand)} bf={len(active.battlefield)}", flush=True)

print("  Combat phase...", flush=True)
state.phase = "combat_begin"
attackers = ai.declare_attackers(active, inactive, state) if state.active_player_index == 0 else ai.declare_attackers(active, inactive, state)
print(f"  Attackers: {len(attackers)}", flush=True)
for a in attackers:
    print(f"    {a.name} ({a.effective_power}/{a.effective_toughness})", flush=True)

if attackers:
    print("  Declare blockers...", flush=True)
    blockers = ai.declare_blockers(inactive, active, attackers, state)
    print(f"  Blockers: {len(blockers)}", flush=True)
    for target, blk in blockers:
        print(f"    {blk.name} blocks {target.name}", flush=True)
    
    print("  Damage step...", flush=True)
    engine._combat_damage_step(active, inactive, attackers, blockers, first_strike_only=False)
    print(f"  After damage: P1={p1.life} P2={p2.life}", flush=True)
    
    print("  SBA check...", flush=True)
    engine.check_state_based_actions()
    print(f"  After SBA: P1 bf={len(p1.battlefield)} P2 bf={len(p2.battlefield)}", flush=True)

print("\nTurn 8 completed!", flush=True)
