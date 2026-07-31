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
from deck_importer import (import_deck_from_text, import_deck_from_json, 
                           save_custom_deck, load_custom_decks, delete_custom_deck,
                           get_custom_deck_as_cards, CUSTOM_DECKS_DIR)
from src.learning_system import learning_system, GameState, GameAction, ActionType
from modern_meta_decks import load_modern_decks

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
        elif parsed.path == '/api/custom-decks':
            self.serve_custom_decks()
        elif parsed.path == '/api/replays':
            self.serve_replays()
        elif parsed.path == '/api/cards':
            self.serve_cards_data()
        elif parsed.path == '/api/learning/stats':
            self.serve_learning_stats()
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
        elif parsed.path == '/api/import-deck':
            self.handle_import_deck()
        elif parsed.path == '/api/delete-deck':
            self.handle_delete_deck()
        elif parsed.path == '/api/learning/start':
            self.handle_learning_start()
        elif parsed.path == '/api/learning/action':
            self.handle_learning_action()
        elif parsed.path == '/api/learning/end':
            self.handle_learning_end()
        elif parsed.path == '/api/learning/train':
            self.handle_learning_train()
        elif parsed.path == '/api/interactive/start':
            self.handle_interactive_start()
        elif parsed.path == '/api/interactive/action':
            self.handle_interactive_action()
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
        """Retorna lista de decks disponiveis (built-in + customizados + Modern)."""
        built_in = list_decks()
        custom = [d['name'] for d in load_custom_decks()]
        modern = [d['name'] for d in load_modern_decks()]
        self.send_json({'decks': built_in, 'custom_decks': custom, 'modern_decks': modern})

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
            
            # Carrega decks customizados e Modern
            custom_decks = {d['name']: d for d in load_custom_decks()}
            modern_decks = {d['name']: d for d in load_modern_decks()}
            
            # Valida e carrega deck A
            if deck_a_name in ALL_DECKS:
                deck_a = get_deck(deck_a_name)
            elif deck_a_name in custom_decks:
                deck_a = get_custom_deck_as_cards(custom_decks[deck_a_name])
            elif deck_a_name in modern_decks:
                # Converte decklist Modern para formato de cartas
                from deck_importer import find_card_id
                deck_a = []
                for card_entry in modern_decks[deck_a_name]['cards']:
                    card_id = find_card_id(card_entry['name'])
                    if card_id:
                        from src.cards_db import get_card
                        try:
                            card = get_card(card_id)
                            for _ in range(card_entry['quantity']):
                                deck_a.append(card)
                        except:
                            pass
            else:
                self.send_json({'error': f'Deck A "{deck_a_name}" nao encontrado'}, 400)
                return
            
            # Valida e carrega deck B
            if deck_b_name in ALL_DECKS:
                deck_b = get_deck(deck_b_name)
            elif deck_b_name in custom_decks:
                deck_b = get_custom_deck_as_cards(custom_decks[deck_b_name])
            elif deck_b_name in modern_decks:
                # Converte decklist Modern para formato de cartas
                from deck_importer import find_card_id
                deck_b = []
                for card_entry in modern_decks[deck_b_name]['cards']:
                    card_id = find_card_id(card_entry['name'])
                    if card_id:
                        from src.cards_db import get_card
                        try:
                            card = get_card(card_id)
                            for _ in range(card_entry['quantity']):
                                deck_b.append(card)
                        except:
                            pass
            else:
                self.send_json({'error': f'Deck B "{deck_b_name}" nao encontrado'}, 400)
                return
            
            if num_matches < 1 or num_matches > 100:
                self.send_json({'error': 'Numero de partidas deve ser entre 1 e 100'}, 400)
                return
            
            from src.simulator_v2 import MatchSimulatorV2
            sim = MatchSimulatorV2(deck_a, deck_b, deck_a_name, deck_b_name, verbosity=1)
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
            import traceback
            error_detail = traceback.format_exc()
            print(f"[ERROR] Simulacao falhou: {error_detail}")
            self.send_json({'error': str(e), 'detail': error_detail}, 500)

    def serve_custom_decks(self):
        """Retorna lista de decks customizados."""
        decks = load_custom_decks()
        self.send_json({'decks': decks})

    def handle_import_deck(self):
        """Processa importacao de deck."""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body.decode('utf-8'))
            
            deck_name = data.get('name', 'Custom Deck')
            deck_text = data.get('text', '')
            deck_json = data.get('json', None)
            
            # Importa do texto ou JSON
            if deck_json:
                deck_data = import_deck_from_json(deck_json)
            elif deck_text:
                deck_data = import_deck_from_text(deck_text, deck_name)
            else:
                self.send_json({'error': 'Nenhum deck fornecido'}, 400)
                return
            
            if 'error' in deck_data:
                self.send_json(deck_data, 400)
                return
            
            # Salva o deck
            deck_data['name'] = deck_name
            filepath = save_custom_deck(deck_data)
            
            response = {
                'success': True,
                'deck': deck_data,
                'filename': os.path.basename(filepath),
                'missing_cards': deck_data.get('missing', []),
                'card_count': sum(qty for _, qty in deck_data.get('cards', [])),
                'land_count': deck_data.get('land_count', 0),
            }
            
            self.send_json(response)
            
        except Exception as e:
            self.send_json({'error': str(e)}, 500)

    def handle_delete_deck(self):
        """Deleta um deck customizado."""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body.decode('utf-8'))
            
            filename = data.get('filename', '')
            if not filename:
                self.send_json({'error': 'Nome do arquivo nao fornecido'}, 400)
                return
            
            if delete_custom_deck(filename):
                self.send_json({'success': True})
            else:
                self.send_json({'error': 'Deck nao encontrado'}, 404)
                
        except Exception as e:
            self.send_json({'error': str(e)}, 500)

    def serve_learning_stats(self):
        """Retorna estatisticas do sistema de aprendizado."""
        stats = learning_system.get_stats()
        self.send_json(stats)

    def handle_learning_start(self):
        """Inicia a gravacao de uma partida."""
        learning_system.start_recording()
        self.send_json({'success': True, 'message': 'Gravacao iniciada'})

    def handle_learning_action(self):
        """Grava uma acao durante a partida."""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body.decode('utf-8'))
            
            state = GameState(
                life=data.get('life', 20),
                hand_size=data.get('hand_size', 0),
                library_size=data.get('library_size', 0),
                battlefield_creatures=data.get('battlefield_creatures', 0),
                battlefield_lands=data.get('battlefield_lands', 0),
                opponent_life=data.get('opponent_life', 20),
                opponent_creatures=data.get('opponent_creatures', 0),
                turn_number=data.get('turn_number', 1),
                mana_available=data.get('mana_available', 0),
                has_card_draw=data.get('has_card_draw', False),
                opponent_threat_level=data.get('opponent_threat_level', 0)
            )
            
            action = GameAction(
                action_type=ActionType(data.get('action_type', 'play_land')),
                card_name=data.get('card_name', ''),
                card_id=data.get('card_id', ''),
                target=data.get('target', ''),
                context=data.get('context', {})
            )
            
            reward = data.get('reward', 0.0)
            
            learning_system.record_action(state, action, reward)
            self.send_json({'success': True})
            
        except Exception as e:
            self.send_json({'error': str(e)}, 500)

    def handle_learning_end(self):
        """Finaliza a gravacao da partida."""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body.decode('utf-8'))
            
            won = data.get('won', False)
            final_reward = data.get('final_reward', 0.0)
            
            learning_system.end_game(won, final_reward)
            self.send_json({'success': True, 'message': 'Gravacao finalizada'})
            
        except Exception as e:
            self.send_json({'error': str(e)}, 500)

    def handle_learning_train(self):
        """Executa um passo de treinamento."""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body.decode('utf-8'))
            
            batch_size = data.get('batch_size', 32)
            learning_system.train_step(batch_size)
            
            stats = learning_system.get_stats()
            self.send_json({'success': True, 'stats': stats})
            
        except Exception as e:
            self.send_json({'error': str(e)}, 500)

    def handle_interactive_start(self):
        """Inicia um jogo interativo onde o usuario joga."""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body.decode('utf-8'))
            
            player_deck_name = data.get('player_deck')
            opponent_deck_name = data.get('opponent_deck')
            
            # Carrega decks
            custom_decks = {d['name']: d for d in load_custom_decks()}
            modern_decks = {d['name']: d for d in load_modern_decks()}
            
            # Carrega deck do jogador
            if player_deck_name in ALL_DECKS:
                player_deck = get_deck(player_deck_name)
            elif player_deck_name in custom_decks:
                player_deck = get_custom_deck_as_cards(custom_decks[player_deck_name])
            elif player_deck_name in modern_decks:
                from deck_importer import find_card_id
                player_deck = []
                for card_entry in modern_decks[player_deck_name]['cards']:
                    card_id = find_card_id(card_entry['name'])
                    if card_id:
                        from src.cards_db import get_card
                        try:
                            card = get_card(card_id)
                            for _ in range(card_entry['quantity']):
                                player_deck.append(card)
                        except:
                            pass
            else:
                self.send_json({'error': f'Deck do jogador nao encontrado'}, 400)
                return
            
            # Carrega deck do oponente
            if opponent_deck_name in ALL_DECKS:
                opponent_deck = get_deck(opponent_deck_name)
            elif opponent_deck_name in custom_decks:
                opponent_deck = get_custom_deck_as_cards(custom_decks[opponent_deck_name])
            elif opponent_deck_name in modern_decks:
                from deck_importer import find_card_id
                opponent_deck = []
                for card_entry in modern_decks[opponent_deck_name]['cards']:
                    card_id = find_card_id(card_entry['name'])
                    if card_id:
                        from src.cards_db import get_card
                        try:
                            card = get_card(card_id)
                            for _ in range(card_entry['quantity']):
                                opponent_deck.append(card)
                        except:
                            pass
            else:
                self.send_json({'error': f'Deck do oponente nao encontrado'}, 400)
                return
            
            # Cria estado do jogo
            from src.game_state import GameState, PlayerState
            from src.rules_engine_v2 import RulesEngineV2
            import random
            
            # Prepara decks frescos
            deck_a_cards = [c.copy() for c in player_deck]
            deck_b_cards = [c.copy() for c in opponent_deck]
            
            random.shuffle(deck_a_cards)
            random.shuffle(deck_b_cards)
            
            # Cria estados dos jogadores
            p1 = PlayerState(name="VOCÊ", life=20, library=deck_a_cards)
            p2 = PlayerState(name=opponent_deck_name, life=20, library=deck_b_cards)
            
            # Mao inicial (7 cartas)
            p1.draw_cards(7)
            p2.draw_cards(7)
            
            # Cria estado do jogo
            game_state = GameState(player1=p1, player2=p2, logging_enabled=True)
            
            # Cria rules engine V2 com o state
            rules_engine = RulesEngineV2(game_state)
            
            # Salva referencia do engine no state para acesso ao log
            game_state._engine = rules_engine
            
            # Salva estado na sessao
            if not hasattr(self.server, 'interactive_games'):
                self.server.interactive_games = {}
            
            game_id = str(len(self.server.interactive_games))
            self.server.interactive_games[game_id] = {
                'state': game_state,
                'engine': rules_engine,
                'player_deck': player_deck_name,
                'opponent_deck': opponent_deck_name
            }
            
            # Retorna estado inicial
            self.send_json({
                'success': True,
                'game_id': game_id,
                'state': self.get_game_state_dict(game_state)
            })
            
        except Exception as e:
            self.send_json({'error': str(e)}, 500)

    def handle_interactive_action(self):
        """Processa uma jogada do usuario."""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body.decode('utf-8'))
            
            game_id = data.get('game_id')
            action = data.get('action')
            params = data.get('params', {})
            
            if not hasattr(self.server, 'interactive_games') or game_id not in self.server.interactive_games:
                self.send_json({'error': 'Jogo nao encontrado'}, 400)
                return
            
            game_data = self.server.interactive_games[game_id]
            state = game_data['state']
            engine = game_data['engine']
            
            # Processa acao
            result = self.process_player_action(state, engine, action, params)
            
            # Registra no sistema de aprendizado
            from src.learning_system import GameAction, ActionType
            learning_system.record_experience(
                GameAction(ActionType.PLAY_CARD, {'action': action, 'params': params}),
                result.get('reward', 0)
            )
            
            # IA faz jogada
            if not state.is_game_over:
                self.ai_take_turn(state, engine)
            
            # Verifica se jogo acabou
            game_over = state.is_game_over
            winner = state.winner
            
            self.send_json({
                'success': True,
                'state': self.get_game_state_dict(state),
                'game_over': game_over,
                'winner': winner,
                'result': result
            })
            
        except Exception as e:
            self.send_json({'error': str(e)}, 500)

    def get_game_state_dict(self, state):
        """Converte estado do jogo para dicionario."""
        # Obter log do engine se disponivel
        game_log = []
        if hasattr(state, '_engine') and hasattr(state._engine, 'get_log'):
            game_log = state._engine.get_log()[-20:]
        
        # Obter acoes disponiveis usando Action Generator
        available_actions = []
        try:
            from src.action_generator import ActionGenerator
            
            action_gen = ActionGenerator()
            actions = action_gen.generate_all_actions(state.player1, state.player2, state)
            
            for action in actions:
                available_actions.append(action.to_dict())
        except Exception as e:
            available_actions = [{'type': 'ERROR', 'description': str(e)}]
        
        return {
            'turn': state.turn_number,
            'phase': state.phase,
            'player1': {
                'name': state.player1.name,
                'life': state.player1.life,
                'hand': [c.name for c in state.player1.hand],
                'battlefield': [c.name for c in state.player1.battlefield],
                'graveyard': [c.name for c in state.player1.graveyard],
                'library_count': len(state.player1.library),
                'mana_pool': {k.value: v for k, v in state.player1.mana_pool.items()}
            },
            'player2': {
                'name': state.player2.name,
                'life': state.player2.life,
                'hand_count': len(state.player2.hand),
                'battlefield': [c.name for c in state.player2.battlefield],
                'graveyard_count': len(state.player2.graveyard),
                'library_count': len(state.player2.library)
            },
            'log': game_log,
            'available_actions': available_actions
        }

    def process_player_action(self, state, engine, action, params):
        """Processa uma acao do jogador usando o RulesEngineV2."""
        result = {'reward': 0, 'message': ''}
        
        if action == 'play_land':
            card_index = params.get('card_index', 0)
            if card_index < len(state.player1.hand):
                card = state.player1.hand[card_index]
                if card.is_land():
                    success = engine.play_land(state.player1, card)
                    if success:
                        result['message'] = f'Terreno jogado: {card.name}'
                        result['reward'] = 1
                    else:
                        result['message'] = 'Não foi possível jogar o terreno'
        
        elif action == 'cast_spell':
            card_index = params.get('card_index', 0)
            if card_index < len(state.player1.hand):
                card = state.player1.hand[card_index]
                if not card.is_land():
                    success = engine.cast_spell(state.player1, card)
                    if success:
                        result['message'] = f'Magia conjurada: {card.name}'
                        result['reward'] = 2
                    else:
                        result['message'] = 'Não foi possível conjurar a magia'
        
        elif action == 'suspend':
            card_index = params.get('card_index', 0)
            if card_index < len(state.player1.hand):
                card = state.player1.hand[card_index]
                success = engine.suspend_card(state.player1, card)
                if success:
                    result['message'] = f'Carta suspensa: {card.name}'
                    result['reward'] = 1
                else:
                    result['message'] = 'Não foi possível suspender a carta'
        
        elif action == 'process_upkeep':
            engine.process_upkeep(state.player1)
            result['message'] = 'Upkeep processado'
            result['reward'] = 0
        
        elif action == 'attack':
            # Ataca com todas as criaturas
            attackers = [c for c in state.player1.battlefield if c.is_creature() and not c.tapped]
            if attackers:
                engine.declare_attackers(state.player1, attackers)
                result['message'] = f'Atacando com {len(attackers)} criatura(s)'
                result['reward'] = 1
            else:
                result['message'] = 'Nenhuma criatura disponível para atacar'
        
        elif action == 'end_turn':
            engine.execute_turn()  # Usa o motor V2
            result['message'] = 'Turno encerrado'
            result['reward'] = 0
        
        return result

    def ai_take_turn(self, state, engine):
        """IA faz seu turno usando o RulesEngineV2."""
        # Joga terrenos
        for card in state.player2.hand[:]:
            if card.is_land() and len(state.player2.battlefield) < 8:
                engine.play_land(state.player2, card)
                break
        
        # Conjura magias simples
        for card in state.player2.hand[:]:
            if not card.is_land():
                total_mana = sum(state.player2.mana_pool.values())
                cmc = getattr(card, 'cmc', 0)
                if cmc <= total_mana:
                    engine.cast_spell(state.player2, card)
                    break

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
