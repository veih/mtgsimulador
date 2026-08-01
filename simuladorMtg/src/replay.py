"""
MTG Match Simulator - Sistema de Replay
Grava o estado de cada turno para visualização posterior.
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any
from .game_state import GameState, PlayerState
from .card import Card


class ReplayRecorder:
    """Grava o estado do jogo a cada turno para replay."""

    def __init__(self):
        self.frames: List[Dict[str, Any]] = []
        self.match_info: Dict[str, Any] = {}

    def start_match(self, deck_a_name: str, deck_b_name: str, match_number: int):
        """Inicia a gravação de uma partida."""
        self.match_info = {
            "deck_a": deck_a_name,
            "deck_b": deck_b_name,
            "match_number": match_number,
            "timestamp": datetime.now().isoformat(),
        }
        self.frames = []

    def record_frame(self, state: GameState, phase: str = ""):
        """Grava um frame do estado atual do jogo."""
        frame = {
            "turn": state.turn_number,
            "phase": phase or state.phase,
            "active_player": state.active_player_index,
            "player1": self._serialize_player(state.player1),
            "player2": self._serialize_player(state.player2),
            "log": state.game_log[-5:] if state.game_log else [],  # Últimas 5 mensagens
        }
        self.frames.append(frame)

    def _serialize_player(self, player: PlayerState) -> Dict[str, Any]:
        """Serializa o estado de um jogador."""
        return {
            "name": player.name,
            "life": player.life,
            "hand_count": len(player.hand),
            "hand_cards": [self._serialize_card(c) for c in player.hand],
            "library_count": len(player.library),
            "battlefield": [self._serialize_card(c) for c in player.battlefield],
            "graveyard": [self._serialize_card(c) for c in player.graveyard],
            "graveyard_count": len(player.graveyard),
            "exile": [self._serialize_card(c) for c in player.exile],
        }

    def _serialize_card(self, card: Card) -> Dict[str, Any]:
        """Serializa uma carta."""
        if card.is_land:
            card_type_str = "LAND"
        else:
            card_type_str = card.card_type.name
        return {
            "name": card.name,
            "mana_cost": str(card.mana_cost),
            "type": card_type_str,
            "power": card.effective_power if card.is_creature else None,
            "toughness": card.effective_toughness if card.is_creature else None,
            "tapped": card.tapped,
            "is_land": card.is_land,
            "keywords": [kw.value for kw in card.keywords],
        }

    def end_match(self, winner_name: str, turns: int):
        """Finaliza a gravação da partida."""
        self.match_info["winner"] = winner_name
        self.match_info["turns"] = turns
        self.match_info["frames"] = self.frames

    def to_dict(self) -> Dict[str, Any]:
        """Retorna o replay completo como dicionário."""
        return self.match_info

    def save_to_file(self, filepath: str):
        """Salva o replay em um arquivo JSON."""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.match_info, f, ensure_ascii=False, indent=2)


class ReplayManager:
    """Gerencia múltiplos replays salvos."""

    def __init__(self, replay_dir: str = "replays"):
        self.replay_dir = replay_dir
        if not os.path.exists(replay_dir):
            os.makedirs(replay_dir)

    def save_replay(self, replay: ReplayRecorder, filename: str = None):
        """Salva um replay no diretório de replays."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"match_{replay.match_info.get('match_number', 0)}_{timestamp}.json"

        filepath = os.path.join(self.replay_dir, filename)
        replay.save_to_file(filepath)
        return filepath

    def list_replays(self) -> List[str]:
        """Lista todos os replays salvos."""
        if not os.path.exists(self.replay_dir):
            return []
        return [f for f in os.listdir(self.replay_dir) if f.endswith('.json')]

    def load_replay(self, filename: str) -> Dict[str, Any]:
        """Carrega um replay do arquivo."""
        filepath = os.path.join(self.replay_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)

    def get_all_replays(self) -> List[Dict[str, Any]]:
        """Carrega todos os replays."""
        replays = []
        for filename in self.list_replays():
            try:
                replay = self.load_replay(filename)
                replays.append(replay)
            except Exception:
                continue
        return replays
