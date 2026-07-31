"""
MTG Match Simulator - Action Generator
Gera todas as acoes legais disponiveis para um jogador.

A IA nunca precisa "saber" como uma carta funciona.
Ela apenas escolhe entre as acoes legais apresentadas pelo motor.

Para cada carta, gera acoes diferentes dependendo do estado:
- Na mao: CAST, SUSPEND, PLAY_LAND
- Exilio com marcadores: Nenhuma (aguarda triggers)
- Exilio com 0 marcadores: CAST_FROM_SUSPEND
- No campo: ACTIVATE_ABILITY
"""

from typing import Any, Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum, auto
from .card import Color


# ─────────────────────────────────────────────
# Tipos de Acao
# ─────────────────────────────────────────────

class ActionType(Enum):
    """Todos os tipos de acao possiveis."""
    # Acoes basicas
    PASS = auto()
    PLAY_LAND = auto()
    CAST_SPELL = auto()
    ACTIVATE_ABILITY = auto()
    
    # Acoes de combate
    DECLARE_ATTACKERS = auto()
    DECLARE_BLOCKERS = auto()
    
    # Acoes especiais
    SUSPEND_CARD = auto()
    CAST_FROM_SUSPEND = auto()
    DISCARD_CARD = auto()
    SACRIFICE_PERMANENT = auto()
    
    # Acoes de mana (geradas pelo Mana Solver)
    TAP_FOR_MANA = auto()
    ACTIVATE_MANA_ABILITY = auto()
    
    # Acoes de resposta
    CAST_INSTANT = auto()
    ACTIVATE_INSTANT_ABILITY = auto()


@dataclass
class GameAction:
    """Uma acao legal disponivel para o jogador."""
    action_type: ActionType
    source: Any = None          # Carta ou permanente
    target: Any = None          # Alvo da acao
    parameters: Dict = field(default_factory=dict)  # Parametros adicionais
    description: str = ""       # Descricao legivel
    mana_cost: Dict = field(default_factory=dict)   # Custo de mana
    can_activate: bool = True   # Pode ser ativada agora?
    priority_required: bool = False  # Requer prioridade?
    
    def to_dict(self) -> Dict:
        """Converte para dicionario serializavel."""
        result = {
            'type': self.action_type.name,
            'description': self.description,
            'can_activate': self.can_activate,
            'parameters': self.parameters
        }
        
        if self.source:
            result['source'] = self.source.name if hasattr(self.source, 'name') else str(self.source)
        
        if self.target:
            if isinstance(self.target, list):
                result['target'] = [t.name if hasattr(t, 'name') else str(t) for t in self.target]
            else:
                result['target'] = self.target.name if hasattr(self.target, 'name') else str(self.target)
        
        if self.mana_cost:
            result['mana_cost'] = {k.value if hasattr(k, 'value') else k: v for k, v in self.mana_cost.items()}
        
        return result


# ─────────────────────────────────────────────
# Action Generator
# ─────────────────────────────────────────────

class ActionGenerator:
    """
    Gera todas as acoes legais disponiveis para um jogador.
    
    Percorre todas as zonas (mao, campo, exilio, cemiterio) e gera
    acoes baseadas no estado de cada carta.
    """
    
    def __init__(self):
        self.special_cards = SPECIAL_CARD_ACTIONS
    
    def generate_all_actions(self, player, opponent, game_state) -> List[GameAction]:
        """
        Gera todas as acoes legais para o jogador atual.
        
        Returns:
            Lista de GameAction com todas as opcoes
        """
        actions = []
        
        # 1. Acoes da mao
        actions.extend(self._generate_hand_actions(player, game_state))
        
        # 2. Acoes do campo de batalha
        actions.extend(self._generate_battlefield_actions(player, opponent, game_state))
        
        # 3. Acoes do exilio
        actions.extend(self._generate_exile_actions(player, game_state))
        
        # 4. Acoes do cemiterio
        actions.extend(self._generate_graveyard_actions(player, game_state))
        
        # 5. Acoes de combate
        actions.extend(self._generate_combat_actions(player, opponent, game_state))
        
        # 6. Acao de passar (sempre disponivel)
        actions.append(GameAction(
            action_type=ActionType.PASS,
            description="Passar turno",
            can_activate=True
        ))
        
        return actions
    
    def _generate_hand_actions(self, player, game_state) -> List[GameAction]:
        """Gera acoes para cartas na mao."""
        actions = []
        
        for card in player.hand:
            card_name = card.name.lower()
            
            # Verifica se e um terreno
            if card.is_land:
                if player.lands_played == 0:
                    actions.append(GameAction(
                        action_type=ActionType.PLAY_LAND,
                        source=card,
                        description=f"Jogar {card.name}",
                        can_activate=True
                    ))
                continue
            
            # Verifica se tem acoes especiais (Suspend, etc.)
            if card_name in self.special_cards:
                special_actions = self.special_cards[card_name].get_actions(card, player, game_state, "hand")
                actions.extend(special_actions)
                continue
            
            # Verifica se pode ser conjurada
            cmc = getattr(card, 'cmc', 0)
            colors = getattr(card, 'colors', [])
            
            # Cartas sem custo de mana nao podem ser conjuradas normalmente
            if cmc == 0 and not colors:
                # Pode ter Suspend ou outra habilidade especial
                continue
            
            # Adiciona acao de conjurar
            actions.append(GameAction(
                action_type=ActionType.CAST_SPELL,
                source=card,
                description=f"Conjurar {card.name}",
                can_activate=True,
                mana_cost=self._calculate_mana_cost(card)
            ))
        
        return actions
    
    def _generate_battlefield_actions(self, player, opponent, game_state) -> List[GameAction]:
        """Gera acoes para permanentes no campo de batalha."""
        actions = []
        
        for permanent in player.battlefield:
            perm_name = permanent.name.lower()
            
            # Habilidades de mana
            mana_actions = self._generate_mana_actions(permanent, player)
            actions.extend(mana_actions)
            
            # Habilidades ativadas
            if perm_name in self.special_cards:
                special_actions = self.special_cards[perm_name].get_actions(permanent, player, game_state, "battlefield")
                actions.extend(special_actions)
            
            # Criaturas podem atacar (verificado em _generate_combat_actions)
            # Criaturas podem ser sacrificadas por efeitos
            if hasattr(permanent, 'is_creature') and permanent.is_creature:
                if not permanent.tapped and not getattr(permanent, 'summoning_sick', False):
                    # Pode ser declarada como atacante
                    pass  # Tratado em _generate_combat_actions
        
        return actions
    
    def _generate_mana_actions(self, permanent, player) -> List[GameAction]:
        """Gera acoes de mana para um permanente."""
        actions = []
        
        if not permanent.is_land:
            return actions
        
        # Verifica se pode virar para mana
        if hasattr(permanent, 'land_mana') and permanent.land_mana:
            if not permanent.tapped:
                for color in permanent.land_mana:
                    actions.append(GameAction(
                        action_type=ActionType.TAP_FOR_MANA,
                        source=permanent,
                        target=color,
                        description=f"Virar {permanent.name} para {color.name if hasattr(color, 'name') else color}",
                        can_activate=True
                    ))
        
        # Verifica habilidades especiais de mana (Lotus Bloom, Gemstone Mine, etc.)
        perm_name = permanent.name.lower()
        if perm_name in MANA_ABILITY_CARDS:
            mana_data = MANA_ABILITY_CARDS[perm_name]
            
            if mana_data.get('sacrifice_for_any'):
                # Lotus Bloom, Gemstone Mine, etc.
                for color in [Color.WHITE, Color.BLUE, Color.BLACK, Color.RED, Color.GREEN]:
                    actions.append(GameAction(
                        action_type=ActionType.ACTIVATE_MANA_ABILITY,
                        source=permanent,
                        target=color,
                        parameters={'sacrifice': True},
                        description=f"Ativar {permanent.name} para {color.name} (sacrificar)",
                        can_activate=True
                    ))
        
        return actions
    
    def _generate_exile_actions(self, player, game_state) -> List[GameAction]:
        """Gera acoes para cartas exiladas."""
        actions = []
        
        for card in player.exile:
            card_name = card.name.lower()
            
            # Verifica se pode ser conjurada do exilio
            if card_name in self.special_cards:
                special_actions = self.special_cards[card_name].get_actions(card, player, game_state, "exile")
                actions.extend(special_actions)
        
        return actions
    
    def _generate_graveyard_actions(self, player, game_state) -> List[GameAction]:
        """Gera acoes para cartas no cemiterio."""
        actions = []
        
        # Algumas cartas podem ser ativadas do cemiterio
        for card in player.graveyard:
            card_name = card.name.lower()
            
            if card_name in self.special_cards:
                special_actions = self.special_cards[card_name].get_actions(card, player, game_state, "graveyard")
                actions.extend(special_actions)
        
        return actions
    
    def _generate_combat_actions(self, player, opponent, game_state) -> List[GameAction]:
        """Gera acoes de combate."""
        actions = []
        
        # Verifica se esta na fase de combate
        phase = getattr(game_state, 'phase', '')
        if phase == 'declare_attackers':
            attackers = []
            for permanent in player.battlefield:
                if hasattr(permanent, 'is_creature') and permanent.is_creature:
                    if not permanent.tapped and not getattr(permanent, 'summoning_sick', False):
                        attackers.append(permanent)
            
            if attackers:
                actions.append(GameAction(
                    action_type=ActionType.DECLARE_ATTACKERS,
                    source=player,
                    target=attackers,
                    description=f"Atacar com {len(attackers)} criatura(s)",
                    can_activate=True
                ))
        
        return actions
    
    def _calculate_mana_cost(self, card) -> Dict:
        """Calcula o custo de mana de uma carta."""
        cmc = getattr(card, 'cmc', 0)
        colors = getattr(card, 'colors', [])
        
        cost = {}
        for color in colors:
            cost[color] = 1
        
        if cmc > len(colors):
            cost['generic'] = cmc - len(colors)
        
        return cost


# ─────────────────────────────────────────────
# Cartas com Habilidades Especiais
# ─────────────────────────────────────────────

class SpecialCardHandler:
    """Handler para cartas com acoes especiais."""
    
    def __init__(self, card_name, handlers):
        self.card_name = card_name
        self.handlers = handlers  # Dict: zone -> handler_function
    
    def get_actions(self, card, player, game_state, zone) -> List[GameAction]:
        """Retorna acoes especiais para esta carta."""
        if zone in self.handlers:
            return self.handlers[zone](card, player, game_state)
        return []


# ─────────────────────────────────────────────
# Handlers Especificos
# ─────────────────────────────────────────────

def lotus_bloom_hand(card, player, game_state) -> List[GameAction]:
    """Lotus Bloom na mao: pode ser suspensa."""
    return [GameAction(
        action_type=ActionType.SUSPEND_CARD,
        source=card,
        description=f"Suspender {card.name} (3 marcadores)",
        parameters={'suspend_cost': 0, 'time_counters': 3},
        can_activate=True
    )]


def lotus_bloom_exile(card, player, game_state) -> List[GameAction]:
    """Lotus Bloom exilada: verifica marcadores."""
    counters = getattr(card, 'time_counters', 0)
    
    if counters == 0:
        return [GameAction(
            action_type=ActionType.CAST_FROM_SUSPEND,
            source=card,
            description=f"Conjurar {card.name} do exilio (sem custo)",
            can_activate=True
        )]
    
    return []  # Aguarda triggers do upkeep


def lotus_bloom_battlefield(card, player, game_state) -> List[GameAction]:
    """Lotus Bloom no campo: {T}, Sacrifice Lotus Bloom: Add three mana of any one color."""
    actions = []
    
    # Nao pode ativar se ja estiver virada
    if hasattr(card, 'tapped') and card.tapped:
        return actions
    
    # Pode escolher UMA cor e produzir 3 manas dessa cor
    # WWW, UUU, BBB, RRR, ou GGG
    for color in [Color.WHITE, Color.BLUE, Color.BLACK, Color.RED, Color.GREEN]:
        actions.append(GameAction(
            action_type=ActionType.ACTIVATE_MANA_ABILITY,
            source=card,
            target=color,
            parameters={'sacrifice': True, 'tap': True, 'amount': 3, 'same_color': True},
            description=f"Virar e sacrificar {card.name} para 3 {color.name}",
            can_activate=True
        ))
    
    return actions


def gemstone_mine_battlefield(card, player, game_state) -> List[GameAction]:
    """Gemstone Mine no campo: remove marcador para mana."""
    counters = getattr(card, 'charge_counters', 3)
    
    if counters > 0:
        actions = []
        for color in [Color.WHITE, Color.BLUE, Color.BLACK, Color.RED, Color.GREEN]:
            actions.append(GameAction(
                action_type=ActionType.ACTIVATE_MANA_ABILITY,
                source=card,
                target=color,
                parameters={'remove_counter': True},
                description=f"Remover marcador de {card.name} para {color.name}",
                can_activate=True
            ))
        return actions
    
    return []


def fetch_land_battlefield(card, player, game_state) -> List[GameAction]:
    """Fetch lands: sacrificar para buscar terreno."""
    from .mana_engine import LAND_MANA_ABILITIES
    
    card_name = card.name.lower()
    mana_data = LAND_MANA_ABILITIES.get(card_name, {})
    
    if 'fetch' in mana_data:
        actions = []
        for land_name in mana_data['fetch']:
            actions.append(GameAction(
                action_type=ActionType.ACTIVATE_ABILITY,
                source=card,
                target=land_name,
                parameters={'sacrifice': True, 'fetch': land_name},
                description=f"Sacrificar {card.name}, buscar {land_name}",
                can_activate=True
            ))
        return actions
    
    return []


# ─────────────────────────────────────────────
# Registro de Cartas Especiais
# ─────────────────────────────────────────────

SPECIAL_CARD_ACTIONS = {
    "lotus bloom": SpecialCardHandler("lotus bloom", {
        "hand": lotus_bloom_hand,
        "exile": lotus_bloom_exile,
        "battlefield": lotus_bloom_battlefield
    }),
    "gemstone mine": SpecialCardHandler("gemstone mine", {
        "battlefield": gemstone_mine_battlefield
    }),
    "city of brass": SpecialCardHandler("city of brass", {
        "battlefield": gemstone_mine_battlefield  # Mesma logica
    }),
    "mana confluence": SpecialCardHandler("mana confluence", {
        "battlefield": gemstone_mine_battlefield  # Mesma logica
    }),
    # Fetch lands
    "flooded strand": SpecialCardHandler("flooded strand", {
        "battlefield": fetch_land_battlefield
    }),
    "bloodstained mire": SpecialCardHandler("bloodstained mire", {
        "battlefield": fetch_land_battlefield
    }),
    "wooded foothills": SpecialCardHandler("wooded foothills", {
        "battlefield": fetch_land_battlefield
    }),
    "polluted delta": SpecialCardHandler("polluted delta", {
        "battlefield": fetch_land_battlefield
    }),
    "windswept heath": SpecialCardHandler("windswept heath", {
        "battlefield": fetch_land_battlefield
    }),
    "marsh flats": SpecialCardHandler("marsh flats", {
        "battlefield": fetch_land_battlefield
    }),
    "arid mesa": SpecialCardHandler("arid mesa", {
        "battlefield": fetch_land_battlefield
    }),
    "verdant catacombs": SpecialCardHandler("verdant catacombs", {
        "battlefield": fetch_land_battlefield
    }),
    "misty rainforest": SpecialCardHandler("misty rainforest", {
        "battlefield": fetch_land_battlefield
    }),
    "scalding tarn": SpecialCardHandler("scalding tarn", {
        "battlefield": fetch_land_battlefield
    }),
}

# Cartas com habilidades de mana especiais
MANA_ABILITY_CARDS = {
    "lotus bloom": {"sacrifice_for_any": 3},
    "gemstone mine": {"remove_counter_for_any": 1},
    "city of brass": {"sacrifice_for_any": 1},
    "mana confluence": {"sacrifice_for_any": 1},
}
