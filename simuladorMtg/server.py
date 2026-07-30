#!/usr/bin/env python3
"""
MTG Match Simulator - Servidor Web
Permite rodar simulações e assistir replays pelo navegador.
"""

import sys
import os
import json
import random
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from datetime import datetime

# Forca encoding UTF-8 no Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Adiciona o diretorio raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from decks import get_deck, list_decks, ALL_DECKS
from src.simulator import MatchSimulator
from src.replay import ReplayRecorder, ReplayManager

# Diretorio de replays na Area de Trabalho
DESKTOP_PATH = os.path.join(os.path.expanduser('~'), 'Desktop')
REPLAY_DIR = os.path.join(DESKTOP_PATH, 'MTG_Replays')

# Diretorio de dados das cartas
CARDS_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cards_data')
CARDS_IMAGES_DIR = os.path.join(CARDS_DATA_DIR, 'images')
CARDS_MAPPING = os.path.join(CARDS_DATA_DIR, 'cards_mapping.json')

# Garante que o diretorio existe
os.makedirs(REPLAY_DIR, exist_ok=True)


class MTGHandler(SimpleHTTPRequestHandler):
    """Handler para o servidor MTG."""

    def do_GET(self):
        """Trata requisicoes GET."""
        parsed = urlparse(self.path)
        
        if parsed.path == '/' or parsed.path == '/index.html':
            self.serve_viewer()
        elif parsed.path == '/api/decks':
            self.serve_decks()
        elif parsed.path == '/api/replays':
            self.serve_replays()
        elif parsed.path == '/api/cards':
            self.serve_cards_data()
        elif parsed.path.startswith('/replays/'):
            self.serve_replay_file(parsed.path)
        elif parsed.path.startswith('/card-images/'):
            self.serve_card_image(parsed.path)
        else:
            # Tenta servir arquivos estaticos
            super().do_GET()

    def do_POST(self):
        """Trata requisicoes POST."""
        parsed = urlparse(self.path)
        
        if parsed.path == '/api/simulate':
            self.handle_simulate()
        else:
            self.send_error(404)

    def serve_viewer(self):
        """Serve o viewer.html."""
        viewer_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'viewer.html')
        try:
            with open(viewer_path, 'rb') as f:
                content = f.read()
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        except FileNotFoundError:
            self.send_error(404, "viewer.html nao encontrado")

    def serve_decks(self):
        """Retorna lista de decks disponiveis."""
        decks = list_decks()
        self.send_json({'decks': decks})

    def serve_replays(self):
        """Retorna lista de replays salvos."""
        replay_manager = ReplayManager(REPLAY_DIR)
        replays = []
        for filename in replay_manager.list_replays():
            try:
                data = replay_manager.load_replay(filename)
                replays.append({
                    'filename': filename,
                    'deck_a': data.get('deck_a', '?'),
                    'deck_b': data.get('deck_b', '?'),
                    'winner': data.get('winner', '?'),
                    'turns': data.get('turns', 0),
                    'frames': len(data.get('frames', [])),
                    'timestamp': data.get('timestamp', ''),
                    'match_number': data.get('match_number', 0),
                })
            except Exception:
                continue
        # Ordena por timestamp (mais recente primeiro)
        replays.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        self.send_json({'replays': replays})

    def serve_replay_file(self, path):
        """Serve um arquivo de replay especifico."""
        filename = path.replace('/replays/', '')
        filepath = os.path.join(REPLAY_DIR, filename)
        try:
            with open(filepath, 'rb') as f:
                content = f.read()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        except FileNotFoundError:
            self.send_error(404, "Replay nao encontrado")

    def serve_cards_data(self):
        """Serve o mapeamento de cartas com dados e imagens."""
        try:
            with open(CARDS_MAPPING, 'rb') as f:
                content = f.read()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        except FileNotFoundError:
            self.send_json({'error': 'Dados de cartas nao encontrados. Rode fetch_cards.py primeiro.'}, 404)

    def serve_card_image(self, path):
        """Serve uma imagem de carta."""
        filename = path.replace('/card-images/', '')
        filepath = os.path.join(CARDS_IMAGES_DIR, filename)
        try:
            with open(filepath, 'rb') as f:
                content = f.read()
            self.send_response(200)
            self.send_header('Content-Type', 'image/jpeg')
            self.send_header('Content-Length', len(content))
            self.send_header('Cache-Control', 'public, max-age=86400')
            self.end_headers()
            self.wfile.write(content)
        except FileNotFoundError:
            self.send_error(404, "Imagem nao encontrada")

    def handle_simulate(self):
        """Processa uma requisicao de simulacao."""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body.decode('utf-8'))
            
            deck_a_name = data.get('deck_a')
            deck_b_name = data.get('deck_b')
            num_matches = int(data.get('matches', 5))
            
            # Valida
            if deck_a_name not in ALL_DECKS or deck_b_name not in ALL_DECKS:
                self.send_json({'error': 'Deck invalido'}, 400)
                return
            
            if num_matches < 1 or num_matches > 100:
                self.send_json({'error': 'Numero de partidas deve ser entre 1 e 100'}, 400)
                return
            
            # Executa simulacao
            deck_a = get_deck(deck_a_name)
            deck_b = get_deck(deck_b_name)
            
            sim = MatchSimulator(deck_a, deck_b, deck_a_name, deck_b_name, verbosity=0)
            replay_manager = ReplayManager(REPLAY_DIR)
            
            saved_replays = []
            results = []
            
            for i in range(1, num_matches + 1):
                recorder = ReplayRecorder()
                result = sim.simulate_match(match_number=i, recorder=recorder)
                replay_path = replay_manager.save_replay(recorder)
                saved_replays.append(os.path.basename(replay_path))
                results.append({
                    'winner': result.winner_name,
                    'turns': result.turns,
                    'winner_life': result.winner_life,
                })
            
            # Calcula estatisticas
            deck_a_wins = sum(1 for r in results if r['winner'] == deck_a_name)
            deck_b_wins = sum(1 for r in results if r['winner'] == deck_b_name)
            
            response = {
                'success': True,
                'deck_a': deck_a_name,
                'deck_b': deck_b_name,
                'matches': num_matches,
                'deck_a_wins': deck_a_wins,
                'deck_b_wins': deck_b_wins,
                'replays': saved_replays,
                'results': results,
            }
            
            self.send_json(response)
            
        except Exception as e:
            self.send_json({'error': str(e)}, 500)

    def send_json(self, data, status=200):
        """Envia resposta JSON."""
        content = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', len(content))
        self.end_headers()
        self.wfile.write(content)

    def log_message(self, format, *args):
        """Customiza log para ser mais limpo."""
        msg = format % args
        if '/api/' in msg:
            print(f"  [API] {msg}")


def run_server(port=8080):
    """Inicia o servidor web."""
    server = HTTPServer(('localhost', port), MTGHandler)
    print(f"""
==========================================================
       MTG Match Simulator - Servidor Web
==========================================================

  Servidor iniciado em: http://localhost:{port}
  
  Abra no navegador para comecar!
  
  Pressione Ctrl+C para parar o servidor.
==========================================================
""")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n  Servidor parado.")
        server.shutdown()


if __name__ == '__main__':
    port = 8080
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            pass
    run_server(port)
