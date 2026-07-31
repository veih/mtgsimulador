"""
MTG Match Simulator - Land Planner & Strategic AI
Planeja terrenos e escolhe linha de jogo.
"""

from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from .card import Color
from .mana_engine import ManaAbilityEngine, LAND_MANA_ABILITIES
from .mana_solver import ManaSolver, ManaPlan


# ─────────────────────────────────────────────
# Land Planner
# Decide qual terreno baixar considerando futuro
# ─────────────────────────────────────────────

@dataclass
class LandPlan:
    """Plano de terrenos para os proximos turnos."""
    land_to_play: Any = None      # Terreno para jogar agora
    future_lands: List = field(default_factory=list)  # Terrenos para turnos futuros
    reasoning: str = ""


class LandPlanner:
    """
    Decide qual terreno baixar considerando:
    1. Magias na mao que quer conjurar
    2. Terrenos ja em campo
    3. Combinacoes de mana necessarias
    """
    
    def __init__(self):
        self.mana_solver = ManaSolver()
    
    def plan(self, player, hand: List, battlefield: List) -> LandPlan:
        """
        Planeja qual terreno jogar.
        
        Args:
            player: Estado do jogador
            hand: Mao do jogador
            battlefield: Campo de batalha
        
        Returns:
            LandPlan com o terreno escolhido
        """
        plan = LandPlan()
        
        # Filtra terrenos na mao
        lands_in_hand = [c for c in hand if c.is_land()]
        if not lands_in_hand:
            plan.reasoning = "Nenhum terreno na mao"
            return plan
        
        # Filtra magias na mao
        spells_in_hand = [c for c in hand if not c.is_land()]
        
        # Se nao tem magias, joga qualquer terreno
        if not spells_in_hand:
            plan.land_to_play = lands_in_hand[0]
            plan.reasoning = "Sem magias, jogando terreno qualquer"
            return plan
        
        # Analisa quais cores precisa
        needed_colors = self._analyze_needed_colors(spells_in_hand)
        
        # Analisa quais cores ja tem
        available_colors = self._analyze_available_colors(battlefield)
        
        # Escolhe o terreno que melhor complementa a base de mana
        best_land = None
        best_score = -1
        
        for land in lands_in_hand:
            score = self._score_land(land, needed_colors, available_colors, battlefield)
            if score > best_score:
                best_score = score
                best_land = land
        
        plan.land_to_play = best_land
        plan.reasoning = f"Melhor terreno (score: {best_score})"
        return plan
    
    def _analyze_needed_colors(self, spells: List) -> Dict:
        """Analisa quais cores as magias da mao precisam."""
        needed = {}
        for spell in spells:
            colors = getattr(spell, 'colors', [])
            for color in colors:
                needed[color] = needed.get(color, 0) + 1
        return needed
    
    def _analyze_available_colors(self, battlefield: List) -> Dict:
        """Analisa quais cores os terrenos em campo produzem."""
        available = {}
        for card in battlefield:
            if card.is_land() and hasattr(card, 'land_mana'):
                for color in card.land_mana:
                    available[color] = available.get(color, 0) + 1
        return available
    
    def _score_land(self, land, needed: Dict, available: Dict, battlefield: List) -> int:
        """
        Avalia quao bom e jogar este terreno.
        Score mais alto = melhor escolha.
        """
        score = 0
        land_name = land.name.lower()
        
        # Verifica mana que o terreno produz
        mana_data = LAND_MANA_ABILITIES.get(land_name, {})
        
        if hasattr(land, 'land_mana') and land.land_mana:
            for color in land.land_mana:
                if color in needed:
                    score += 10  # Cor necessaria
                if color not in available:
                    score += 5   # Cor nova
                if color in needed and color not in available:
                    score += 15  # Cor necessaria e ainda nao disponivel
        
        elif "any" in mana_data:
            score += 8  # Mana flexivel e sempre boa
        
        elif "fetch" in mana_data:
            score += 12  # Fetch lands sao muito fortes
        
        # Penaliza duplicatas
        existing_names = [c.name.lower() for c in battlefield if c.is_land()]
        if land_name in existing_names:
            score -= 3
        
        return score


# ─────────────────────────────────────────────
# Strategic AI
# Escolhe a linha de jogo
# ─────────────────────────────────────────────

@dataclass
class GameDecision:
    """Uma decisao da IA."""
    action: str           # "CAST", "PLAY_LAND", "ATTACK", "PASS"
    target: Any = None    # Carta ou alvo
    plan: Any = None      # Plano de mana (se aplicavel)
    reasoning: str = ""


class StrategicAI:
    """
    IA estrategica que escolhe a linha de jogo.
    Usa o Mana Solver para saber o que pode conjurar.
    Usa o Land Planner para decidir qual terreno jogar.
    """
    
    def __init__(self):
        self.mana_solver = ManaSolver()
        self.land_planner = LandPlanner()
    
    def decide(self, player, opponent, game_state) -> GameDecision:
        """
        Toma uma decisao para o turno atual.
        
        Ordem de prioridade:
        1. Jogar terreno (se ainda nao jogou)
        2. Conjurar magias (se possivel)
        3. Atacar (se tiver criaturas)
        4. Passar turno
        """
        
        # 1. Jogar terreno?
        if player.lands_played == 0:
            land_plan = self.land_planner.plan(player, player.hand, player.battlefield)
            if land_plan.land_to_play:
                return GameDecision(
                    action="PLAY_LAND",
                    target=land_plan.land_to_play,
                    reasoning=land_plan.reasoning
                )
        
        # 2. Conjurar magias?
        castable = self.mana_solver.get_all_castable(player, player.hand)
        if castable:
            # Escolhe a melhor magia para conjurar
            best_spell, best_plan = self._choose_best_spell(castable, player, opponent)
            if best_spell:
                return GameDecision(
                    action="CAST",
                    target=best_spell,
                    plan=best_plan,
                    reasoning=f"Melhor magia: {best_spell.name}"
                )
        
        # 3. Atacar?
        attackers = [c for c in player.battlefield 
                     if hasattr(c, 'is_creature') and c.is_creature 
                     and not c.tapped and not getattr(c, 'summoning_sick', False)]
        if attackers:
            return GameDecision(
                action="ATTACK",
                target=attackers,
                reasoning=f"Atacando com {len(attackers)} criatura(s)"
            )
        
        # 4. Passar
        return GameDecision(
            action="PASS",
            reasoning="Nenhuma acao disponivel"
        )
    
    def _choose_best_spell(self, castable: List, player, opponent) -> Tuple:
        """Escolhe a melhor magia para conjurar."""
        if not castable:
            return None, None
        
        # Prioridade para Ad Nauseam (combo)
        for spell, plan in castable:
            if "ad nauseam" in spell.name.lower():
                return spell, plan
        
        # Prioridade para tutor effects
        for spell, plan in castable:
            if "tutor" in spell.name.lower() or "profane" in spell.name.lower():
                return spell, plan
        
        # Prioridade para protecao
        for spell, plan in castable:
            if "grace" in spell.name.lower() or "pact" in spell.name.lower():
                return spell, plan
        
        # Prioridade para win condition
        for spell, plan in castable:
            if "oracle" in spell.name.lower():
                return spell, plan
        
        # Prioridade por CMC (menor primeiro)
        castable.sort(key=lambda x: getattr(x[0], 'cmc', 99))
        return castable[0]
    
    def get_available_actions(self, player, opponent) -> List[GameDecision]:
        """
        Retorna todas as acoes disponiveis para a IA escolher.
        Esta e a lista que o motor oferece para a IA.
        """
        actions = []
        
        # Acoes de terreno
        lands_in_hand = [c for c in player.hand if c.is_land()]
        if lands_in_hand and player.lands_played == 0:
            for land in lands_in_hand:
                actions.append(GameDecision(
                    action="PLAY_LAND",
                    target=land,
                    reasoning=f"Jogar {land.name}"
                ))
        
        # Acoes de magia
        castable = self.mana_solver.get_all_castable(player, player.hand)
        for spell, plan in castable:
            actions.append(GameDecision(
                action="CAST",
                target=spell,
                plan=plan,
                reasoning=f"Conjurar {spell.name}"
            ))
        
        # Acoes de ataque
        attackers = [c for c in player.battlefield 
                     if hasattr(c, 'is_creature') and c.is_creature 
                     and not c.tapped and not getattr(c, 'summoning_sick', False)]
        if attackers:
            actions.append(GameDecision(
                action="ATTACK",
                target=attackers,
                reasoning=f"Atacar com {len(attackers)}"
            ))
        
        # Acao de passar
        actions.append(GameDecision(
            action="PASS",
            reasoning="Passar turno"
        ))
        
        return actions
