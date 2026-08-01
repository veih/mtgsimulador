#!/usr/bin/env python3
"""
======================================================
       MTG Match Simulator v1.0
       Simulador de Partidas de Magic: The Gathering
======================================================

Simula N partidas entre dois decks e analisa qual deck e superior.

Uso:
    python main.py                          # Modo interativo
    python main.py --deck-a "Red Deck Wins" --deck-b "Green Stompy" --matches 100
    python main.py --all-matchups --matches 50
"""

import sys
import os
import argparse
import random
from datetime import datetime

# Forca encoding UTF-8 no Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Diretório de replays na Área de Trabalho
DESKTOP_PATH = os.path.join(os.path.expanduser('~'), 'Desktop')
REPLAY_DIR = os.path.join(DESKTOP_PATH, 'MTG_Replays')

from decks import ALL_DECKS, get_deck, list_decks
from src.simulator import MatchSimulator, MatchupStats


# ─────────────────────────────────────────────
# Formatação de Saída
# ─────────────────────────────────────────────

def print_header():
    print()
    print("=" * 58)
    print("          MTG MATCH SIMULATOR v1.0")
    print("   Simulador de Partidas de Magic: The Gathering")
    print("=" * 58)
    print()


def print_available_decks():
    print("  Decks disponíveis:")
    for i, name in enumerate(ALL_DECKS.keys(), 1):
        deck = ALL_DECKS[name]
        lands = sum(1 for c in deck if c.is_land)
        creatures = sum(1 for c in deck if c.is_creature)
        spells = len(deck) - lands - creatures
        print(f"    {i}. {name:20s} ({len(deck)} cartas: "
              f"{lands} terrenos, {creatures} criaturas, {spells} magias)")
    print()


def print_stats(stats: MatchupStats):
    """Exibe estatísticas detalhadas do matchup."""
    print()
    print("=" * 60)
    print(f"  RESULTADO: {stats.deck_a_name} vs {stats.deck_b_name}")
    print("=" * 60)
    print()

    # Win rate
    print(f"  Total de partidas: {stats.total_matches}")
    print()
    bar_width = 40
    a_w = int(stats.deck_a_winrate / 100 * bar_width)
    b_w = int(stats.deck_b_winrate / 100 * bar_width)

    print(f"  {stats.deck_a_name}:")
    print(f"    Vitórias: {stats.deck_a_wins}/{stats.total_matches} "
          f"({stats.deck_a_winrate:.1f}%)")
    print(f"    [{'#' * a_w}{'.' * (bar_width - a_w)}] {stats.deck_a_winrate:.1f}%")
    print()
    print(f"  {stats.deck_b_name}:")
    print(f"    Vitórias: {stats.deck_b_wins}/{stats.total_matches} "
          f"({stats.deck_b_winrate:.1f}%)")
    print(f"    [{'#' * b_w}{'.' * (bar_width - b_w)}] {stats.deck_b_winrate:.1f}%")
    print()

    if stats.draws > 0:
        print(f"  Empates: {stats.draws} ({stats.draws / stats.total_matches * 100:.1f}%)")
        print()

    # Deck superior
    print("-" * 60)
    if stats.superior_deck != "Empate":
        print(f"  [WINNER] DECK SUPERIOR: {stats.superior_deck}")
        print(f"     Diferenca de win rate: {stats.winrate_difference:.1f} pontos")
    else:
        print(f"  [TIE] MATCHUP EQUILIBRADO")
    print("-" * 60)
    print()

    # Estatísticas detalhadas
    print("  ESTATÍSTICAS DETALHADAS:")
    print(f"    {'Métrica':<30s} {stats.deck_a_name:>15s} {stats.deck_b_name:>15s}")
    print(f"    {'-' * 30} {'-' * 15} {'-' * 15}")
    print(f"    {'Win Rate':<30s} {stats.deck_a_winrate:>14.1f}% {stats.deck_b_winrate:>14.1f}%")
    print(f"    {'Vida média (quando vence)':<30s} {stats.deck_a_avg_life:>15.1f} {stats.deck_b_avg_life:>15.1f}")
    print(f"    {'Dano médio por partida':<30s} {stats.deck_a_avg_damage:>15.1f} {stats.deck_b_avg_damage:>15.1f}")
    print(f"    {'Magias conjuradas (média)':<30s} {stats.deck_a_avg_spells:>15.1f} {stats.deck_b_avg_spells:>15.1f}")
    print(f"    {'Duração média (turnos)':<30s} {stats.avg_game_length:>15.1f} {'':>15s}")
    print()

    # Analise
    print("  ANALISE:")
    if stats.deck_a_winrate > 60:
        print(f"    -> {stats.deck_a_name} domina o matchup com {stats.deck_a_winrate:.1f}% de win rate.")
    elif stats.deck_a_winrate > 55:
        print(f"    -> {stats.deck_a_name} tem vantagem no matchup ({stats.deck_a_winrate:.1f}%).")
    elif stats.deck_b_winrate > 60:
        print(f"    -> {stats.deck_b_name} domina o matchup com {stats.deck_b_winrate:.1f}% de win rate.")
    elif stats.deck_b_winrate > 55:
        print(f"    -> {stats.deck_b_name} tem vantagem no matchup ({stats.deck_b_winrate:.1f}%).")
    else:
        print(f"    -> Matchup muito equilibrado, nenhum deck claramente superior.")

    if stats.avg_game_length < 6:
        print(f"    -> Partidas rapidas (media {stats.avg_game_length:.1f} turnos) - deck agressivo.")
    elif stats.avg_game_length < 10:
        print(f"    -> Partidas de duracao media ({stats.avg_game_length:.1f} turnos).")
    else:
        print(f"    -> Partidas longas ({stats.avg_game_length:.1f} turnos) - matchup controlado.")
    print()


def print_all_matchups_summary(all_stats: list):
    """Exibe resumo de todos os matchups."""
    print()
    print("=" * 70)
    print("  RESUMO GERAL - TODOS OS MATCHUPS")
    print("=" * 70)
    print()

    # Ranking de decks por win rate geral
    deck_stats = {}
    for stats in all_stats:
        for deck_name in [stats.deck_a_name, stats.deck_b_name]:
            if deck_name not in deck_stats:
                deck_stats[deck_name] = {"wins": 0, "total": 0, "total_life": 0}

        if stats.deck_a_wins > 0:
            deck_stats[stats.deck_a_name]["wins"] += stats.deck_a_wins
            deck_stats[stats.deck_a_name]["total"] += stats.total_matches
        if stats.deck_b_wins > 0:
            deck_stats[stats.deck_b_name]["wins"] += stats.deck_b_wins
            deck_stats[stats.deck_b_name]["total"] += stats.total_matches

    print(f"  {'Deck':<20s} {'Vitórias':>10s} {'Partidas':>10s} {'Win Rate':>10s}")
    print(f"  {'-' * 20} {'-' * 10} {'-' * 10} {'-' * 10}")

    ranking = []
    for deck_name, data in deck_stats.items():
        wr = (data["wins"] / data["total"] * 100) if data["total"] > 0 else 0
        ranking.append((deck_name, data["wins"], data["total"], wr))

    ranking.sort(key=lambda x: x[3], reverse=True)

    for i, (name, wins, total, wr) in enumerate(ranking, 1):
        medal = ["#1", "#2", "#3"][i - 1] if i <= 3 else f" {i}"
        print(f"  {medal} {name:<18s} {wins:>10d} {total:>10d} {wr:>9.1f}%")

    print()
    if ranking:
        print(f"  [WINNER] DECK MAIS FORTE: {ranking[0][0]} ({ranking[0][3]:.1f}% win rate)")
    print()


# ─────────────────────────────────────────────
# Modo Interativo
# ─────────────────────────────────────────────

def interactive_mode():
    """Modo interativo do simulador."""
    print_header()
    print_available_decks()

    deck_names = list(ALL_DECKS.keys())

    # Escolhe Deck A
    while True:
        try:
            choice = input("  Escolha o Deck A (número): ").strip()
            idx = int(choice) - 1
            if 0 <= idx < len(deck_names):
                deck_a_name = deck_names[idx]
                break
            print("  Número inválido. Tente novamente.")
        except (ValueError, EOFError):
            print("  Entrada inválida.")
            return

    # Escolhe Deck B
    while True:
        try:
            choice = input("  Escolha o Deck B (número): ").strip()
            idx = int(choice) - 1
            if 0 <= idx < len(deck_names) and idx != (int(deck_a_name != deck_names[idx - 1]) if False else -1):
                deck_b_name = deck_names[idx]
                if deck_b_name == deck_a_name:
                    print("  Escolha um deck diferente do Deck A.")
                    continue
                break
            print("  Número inválido. Tente novamente.")
        except (ValueError, EOFError):
            print("  Entrada inválida.")
            return

    # Número de partidas
    while True:
        try:
            choice = input("  Número de partidas (padrão 100): ").strip()
            if not choice:
                num_matches = 100
                break
            num_matches = int(choice)
            if num_matches > 0:
                break
            print("  Número deve ser positivo.")
        except (ValueError, EOFError):
            num_matches = 100
            break

    # Executa simulação
    print(f"\n  Simulando {num_matches} partidas: {deck_a_name} vs {deck_b_name}...")
    print()

    deck_a = get_deck(deck_a_name)
    deck_b = get_deck(deck_b_name)

    sim = MatchSimulator(deck_a, deck_b, deck_a_name, deck_b_name, verbosity=1)
    
    # Grava replays na Area de Trabalho
    os.makedirs(REPLAY_DIR, exist_ok=True)
    # Copia viewer.html, viewer.css e viewer.js para a pasta de replays
    import shutil
    base_dir = os.path.dirname(os.path.abspath(__file__))
    for viewer_file in ('viewer.html', 'viewer.css', 'viewer.js'):
        src = os.path.join(base_dir, viewer_file)
        dst = os.path.join(REPLAY_DIR, viewer_file)
        if os.path.exists(src) and not os.path.exists(dst):
            shutil.copy(src, dst)
    stats, saved_replays = sim.simulate_and_record(num_matches, REPLAY_DIR)
    print(f"\n  {len(saved_replays)} replays salvos em: {REPLAY_DIR}")
    print(f"  Para assistir, abra viewer.html na pasta MTG_Replays na Area de Trabalho")

    print_stats(stats)


# ─────────────────────────────────────────────
# Modo All Matchups
# ─────────────────────────────────────────────

def all_matchups_mode(num_matches: int):
    """Simula todos os matchups possíveis."""
    print_header()
    deck_names = list(ALL_DECKS.keys())
    print(f"  Simulando todos os matchups ({len(deck_names)} decks)...")
    print(f"  {num_matches} partidas por matchup")
    print()

    all_stats = []

    for i in range(len(deck_names)):
        for j in range(i + 1, len(deck_names)):
            name_a = deck_names[i]
            name_b = deck_names[j]
            print(f"  > {name_a} vs {name_b}...")

            deck_a = get_deck(name_a)
            deck_b = get_deck(name_b)

            sim = MatchSimulator(deck_a, deck_b, name_a, name_b, verbosity=0)
            stats = sim.simulate_matches(num_matches)
            all_stats.append(stats)

            print(f"    {name_a}: {stats.deck_a_winrate:.1f}% | "
                  f"{name_b}: {stats.deck_b_winrate:.1f}%")

    print_all_matchups_summary(all_stats)

    # Detalhes de cada matchup
    for stats in all_stats:
        print_stats(stats)


# ─────────────────────────────────────────────
# CLI Arguments
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="MTG Match Simulator - Simula partidas de Magic: The Gathering"
    )
    parser.add_argument(
        "--deck-a", type=str, help="Nome do Deck A"
    )
    parser.add_argument(
        "--deck-b", type=str, help="Nome do Deck B"
    )
    parser.add_argument(
        "--matches", "-m", type=int, default=100,
        help="Número de partidas para simular (padrão: 100)"
    )
    parser.add_argument(
        "--all-matchups", action="store_true",
        help="Simula todos os matchups possíveis"
    )
    parser.add_argument(
        "--list-decks", action="store_true",
        help="Lista todos os decks disponíveis"
    )
    parser.add_argument(
        "--seed", type=int, help="Seed para reprodutibilidade"
    )
    parser.add_argument(
        "--no-record", action="store_true",
        help="Desativa gravação de replays (por padrao grava na Area de Trabalho)"
    )
    parser.add_argument(
        "--replay-dir", type=str, default=None,
        help="Diretorio para salvar replays (padrao: ~/Desktop/MTG_Replays/)"
    )
    parser.add_argument(
        "--viewer", action="store_true",
        help="Abre o visualizador de replays no navegador"
    )

    args = parser.parse_args()

    # Seed
    if args.seed is not None:
        random.seed(args.seed)

    # Lista decks
    if args.list_decks:
        print_header()
        print_available_decks()
        return

    # Abre o viewer
    if args.viewer:
        import webbrowser
        viewer_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'viewer.html')
        webbrowser.open(f'file://{viewer_path}')
        print("  Visualizador aberto no navegador.")
        return

    # All matchups
    if args.all_matchups:
        all_matchups_mode(args.matches)
        return

    # Modo com argumentos
    if args.deck_a and args.deck_b:
        print_header()

        if args.deck_a not in ALL_DECKS:
            print(f"  Erro: Deck '{args.deck_a}' nao encontrado.")
            print_available_decks()
            return
        if args.deck_b not in ALL_DECKS:
            print(f"  Erro: Deck '{args.deck_b}' nao encontrado.")
            print_available_decks()
            return

        print(f"  Simulando {args.matches} partidas: "
              f"{args.deck_a} vs {args.deck_b}...")
        print()

        deck_a = get_deck(args.deck_a)
        deck_b = get_deck(args.deck_b)

        sim = MatchSimulator(deck_a, deck_b, args.deck_a, args.deck_b, verbosity=1)
        
        # Determina diretorio de replays
        replay_dir = args.replay_dir if args.replay_dir else REPLAY_DIR
        
        # Sempre grava replays a menos que --no-record seja especificado
        if not args.no_record:
            # Cria diretorio se nao existir
            os.makedirs(replay_dir, exist_ok=True)
            # Copia viewer.html, viewer.css e viewer.js para a pasta de replays
            import shutil
            base_dir = os.path.dirname(os.path.abspath(__file__))
            for viewer_file in ('viewer.html', 'viewer.css', 'viewer.js'):
                src = os.path.join(base_dir, viewer_file)
                dst = os.path.join(replay_dir, viewer_file)
                if os.path.exists(src) and not os.path.exists(dst):
                    shutil.copy(src, dst)
            # Simula e grava replays
            stats, saved_replays = sim.simulate_and_record(args.matches, replay_dir)
            print(f"\n  {len(saved_replays)} replays salvos em: {replay_dir}")
            print(f"  Para assistir, abra viewer.html na pasta MTG_Replays na Area de Trabalho")
        else:
            stats = sim.simulate_matches(args.matches)

        print_stats(stats)
        return

    # Modo interativo
    try:
        interactive_mode()
    except KeyboardInterrupt:
        print("\n\n  Simulação cancelada.")
        sys.exit(0)


if __name__ == "__main__":
    main()
