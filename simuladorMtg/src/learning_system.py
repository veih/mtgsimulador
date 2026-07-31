"""
MTG Match Simulator - Sistema de Aprendizado por Reforço
Aprende com as jogadas do jogador para melhorar a IA.
"""

import json
import os
import random
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum


class ActionType(Enum):
    PLAY_LAND = "play_land"
    CAST_CREATURE = "cast_creature"
    CAST_SPELL = "cast_spell"
    CAST_INSTANT = "cast_instant"
    DECLARE_ATTACKERS = "declare_attackers"
    DECLARE_BLOCKERS = "declare_blockers"
    MULLIGAN = "mulligan"
    KEEP_HAND = "keep_hand"


@dataclass
class GameState:
    """Estado do jogo para o sistema de aprendizado."""
    life: int = 20
    hand_size: int = 0
    library_size: int = 0
    battlefield_creatures: int = 0
    battlefield_lands: int = 0
    opponent_life: int = 20
    opponent_creatures: int = 0
    turn_number: int = 1
    mana_available: int = 0
    has_card_draw: bool = False
    opponent_threat_level: int = 0  # 0-10


@dataclass
class GameAction:
    """Ação tomada pelo jogador."""
    action_type: ActionType
    card_name: str = ""
    card_id: str = ""
    target: str = ""
    context: Dict = field(default_factory=dict)


@dataclass
class GameExperience:
    """Experiência de uma jogada."""
    state: GameState
    action: GameAction
    reward: float = 0.0
    next_state: Optional[GameState] = None
    done: bool = False


class ReplayMemory:
    """Memória de replay para aprendizado."""
    
    def __init__(self, capacity: int = 10000):
        self.capacity = capacity
        self.memory: List[GameExperience] = []
        self.position = 0
    
    def push(self, experience: GameExperience):
        """Adiciona uma experiência à memória."""
        if len(self.memory) < self.capacity:
            self.memory.append(experience)
        else:
            self.memory[self.position] = experience
        self.position = (self.position + 1) % self.capacity
    
    def sample(self, batch_size: int) -> List[GameExperience]:
        """Amostra um batch de experiências."""
        return random.sample(self.memory, min(batch_size, len(self.memory)))
    
    def __len__(self):
        return len(self.memory)
    
    def save(self, filepath: str):
        """Salva a memória em um arquivo."""
        data = []
        for exp in self.memory:
            data.append({
                'state': {
                    'life': exp.state.life,
                    'hand_size': exp.state.hand_size,
                    'library_size': exp.state.library_size,
                    'battlefield_creatures': exp.state.battlefield_creatures,
                    'battlefield_lands': exp.state.battlefield_lands,
                    'opponent_life': exp.state.opponent_life,
                    'opponent_creatures': exp.state.opponent_creatures,
                    'turn_number': exp.state.turn_number,
                    'mana_available': exp.state.mana_available,
                    'has_card_draw': exp.state.has_card_draw,
                    'opponent_threat_level': exp.state.opponent_threat_level
                },
                'action': {
                    'action_type': exp.action.action_type.value,
                    'card_name': exp.action.card_name,
                    'card_id': exp.action.card_id,
                    'target': exp.action.target,
                    'context': exp.action.context
                },
                'reward': exp.reward,
                'done': exp.done
            })
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    def load(self, filepath: str):
        """Carrega a memória de um arquivo."""
        if not os.path.exists(filepath):
            return
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.memory = []
        for item in data:
            state = GameState(
                life=item['state']['life'],
                hand_size=item['state']['hand_size'],
                library_size=item['state']['library_size'],
                battlefield_creatures=item['state']['battlefield_creatures'],
                battlefield_lands=item['state']['battlefield_lands'],
                opponent_life=item['state']['opponent_life'],
                opponent_creatures=item['state']['opponent_creatures'],
                turn_number=item['state']['turn_number'],
                mana_available=item['state']['mana_available'],
                has_card_draw=item['state']['has_card_draw'],
                opponent_threat_level=item['state']['opponent_threat_level']
            )
            
            action = GameAction(
                action_type=ActionType(item['action']['action_type']),
                card_name=item['action']['card_name'],
                card_id=item['action']['card_id'],
                target=item['action']['target'],
                context=item['action']['context']
            )
            
            exp = GameExperience(
                state=state,
                action=action,
                reward=item['reward'],
                done=item['done']
            )
            
            self.memory.append(exp)


class QLearningAgent:
    """Agente de aprendizado por Q-Learning."""
    
    def __init__(self, learning_rate: float = 0.1, discount_factor: float = 0.95,
                 epsilon: float = 0.1):
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = epsilon  # Exploração vs exploração
        
        # Q-table: state_hash -> action -> value
        self.q_table: Dict[str, Dict[str, float]] = {}
        
        # Estatísticas
        self.games_played = 0
        self.total_reward = 0.0
    
    def _state_to_hash(self, state: GameState) -> str:
        """Converte o estado em um hash para a Q-table."""
        # Discretiza o estado para reduzir o espaço
        life_bucket = state.life // 5
        hand_bucket = state.hand_size // 2
        creatures_bucket = state.battlefield_creatures // 2
        lands_bucket = state.battlefield_lands // 2
        turn_bucket = min(state.turn_number // 5, 10)
        mana_bucket = state.mana_available // 2
        threat_bucket = state.opponent_threat_level // 2
        
        return f"{life_bucket}_{hand_bucket}_{creatures_bucket}_{lands_bucket}_{turn_bucket}_{mana_bucket}_{threat_bucket}"
    
    def _action_to_hash(self, action: GameAction) -> str:
        """Converte a ação em um hash."""
        return f"{action.action_type.value}_{action.card_id}"
    
    def get_q_value(self, state: GameState, action: GameAction) -> float:
        """Retorna o valor Q de um estado-ação."""
        state_hash = self._state_to_hash(state)
        action_hash = self._action_to_hash(action)
        
        if state_hash not in self.q_table:
            return 0.0
        
        return self.q_table[state_hash].get(action_hash, 0.0)
    
    def update_q_value(self, state: GameState, action: GameAction, reward: float,
                       next_state: Optional[GameState]):
        """Atualiza o valor Q usando a equação de Bellman."""
        state_hash = self._state_to_hash(state)
        action_hash = self._action_to_hash(action)
        
        current_q = self.get_q_value(state, action)
        
        if next_state is None:
            target = reward
        else:
            # Max Q para o próximo estado
            next_state_hash = self._state_to_hash(next_state)
            if next_state_hash in self.q_table and self.q_table[next_state_hash]:
                max_next_q = max(self.q_table[next_state_hash].values())
            else:
                max_next_q = 0.0
            target = reward + self.discount_factor * max_next_q
        
        # Atualiza Q-value
        new_q = current_q + self.learning_rate * (target - current_q)
        
        if state_hash not in self.q_table:
            self.q_table[state_hash] = {}
        
        self.q_table[state_hash][action_hash] = new_q
    
    def choose_action(self, state: GameState, available_actions: List[GameAction]) -> GameAction:
        """Escolhe uma ação usando epsilon-greedy."""
        if random.random() < self.epsilon:
            # Exploração: ação aleatória
            return random.choice(available_actions)
        else:
            # Exploração: melhor ação conhecida
            best_action = None
            best_q = float('-inf')
            
            for action in available_actions:
                q = self.get_q_value(state, action)
                if q > best_q:
                    best_q = q
                    best_action = action
            
            return best_action if best_action else random.choice(available_actions)
    
    def save(self, filepath: str):
        """Salva o agente em um arquivo."""
        data = {
            'q_table': self.q_table,
            'games_played': self.games_played,
            'total_reward': self.total_reward,
            'learning_rate': self.learning_rate,
            'discount_factor': self.discount_factor,
            'epsilon': self.epsilon
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    def load(self, filepath: str):
        """Carrega o agente de um arquivo."""
        if not os.path.exists(filepath):
            return
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.q_table = data.get('q_table', {})
        self.games_played = data.get('games_played', 0)
        self.total_reward = data.get('total_reward', 0.0)
        self.learning_rate = data.get('learning_rate', 0.1)
        self.discount_factor = data.get('discount_factor', 0.95)
        self.epsilon = data.get('epsilon', 0.1)


class LearningSystem:
    """Sistema de aprendizado completo."""
    
    def __init__(self, data_dir: str = None):
        if data_dir is None:
            data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'learning_data')
        
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.memory = ReplayMemory(capacity=10000)
        self.agent = QLearningAgent()
        
        # Carrega dados existentes
        self.memory_file = os.path.join(self.data_dir, 'replay_memory.json')
        self.agent_file = os.path.join(self.data_dir, 'q_agent.json')
        
        self.memory.load(self.memory_file)
        self.agent.load(self.agent_file)
        
        # Sessão atual
        self.current_game_experiences: List[GameExperience] = []
        self.is_recording = False
    
    def start_recording(self):
        """Inicia a gravação de uma partida."""
        self.current_game_experiences = []
        self.is_recording = True
    
    def record_action(self, state: GameState, action: GameAction, reward: float = 0.0):
        """Grava uma ação durante a partida."""
        if not self.is_recording:
            return
        
        exp = GameExperience(
            state=state,
            action=action,
            reward=reward
        )
        
        self.current_game_experiences.append(exp)
    
    def end_game(self, won: bool, final_reward: float = 0.0):
        """Finaliza a gravação da partida."""
        if not self.is_recording:
            return
        
        # Aplica recompensa final
        if self.current_game_experiences:
            self.current_game_experiences[-1].reward = final_reward
            self.current_game_experiences[-1].done = True
        
        # Adiciona à memória
        for exp in self.current_game_experiences:
            self.memory.push(exp)
        
        # Atualiza agente
        self.agent.games_played += 1
        self.agent.total_reward += final_reward
        
        # Salva dados
        self.memory.save(self.memory_file)
        self.agent.save(self.agent_file)
        
        self.is_recording = False
        self.current_game_experiences = []
    
    def get_stats(self) -> Dict:
        """Retorna estatísticas do aprendizado."""
        return {
            'games_played': self.agent.games_played,
            'total_reward': self.agent.total_reward,
            'average_reward': self.agent.total_reward / max(1, self.agent.games_played),
            'memory_size': len(self.memory),
            'q_table_size': len(self.agent.q_table),
            'epsilon': self.agent.epsilon
        }
    
    def train_step(self, batch_size: int = 32):
        """Executa um passo de treinamento."""
        if len(self.memory) < batch_size:
            return
        
        batch = self.memory.sample(batch_size)
        
        for exp in batch:
            self.agent.update_q_value(
                exp.state,
                exp.action,
                exp.reward,
                exp.next_state
            )
    
    def get_best_action(self, state: GameState, available_actions: List[GameAction]) -> GameAction:
        """Retorna a melhor ação conhecida pelo agente."""
        return self.agent.choose_action(state, available_actions)


# Instância global do sistema de aprendizado
learning_system = LearningSystem()
