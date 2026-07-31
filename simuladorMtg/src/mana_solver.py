"""
MTG Match Simulator - Mana Solver
Encontra a melhor sequencia de ativacoes de terrenos para pagar um custo.

A carta so pode ser baixada no campo se paga seu custo de conjuracao.
Ex: Custo de 1 incolor e 1 azul (1U):
  1. Vira terreno gerando 1 incolor
  2. Vira terreno gerando 1 azul

O Mana Solver resolve:
  Entrada: Custo da magia (ex: 1U = 1 generico + 1 azul)
  Saida: Plano de ativacoes dos terrenos
"""

from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from .card import Color
from .mana_engine import ManaAbilityEngine, ManaAbility, ManaActionType


@dataclass
class ManaPlan:
    """Um plano de como gerar mana para pagar um custo."""
    steps: List['ManaStep'] = field(default_factory=list)
    total_produced: Dict = field(default_factory=dict)
    can_pay: bool = False
    description: str = ""
    cost_breakdown: str = ""  # Ex: "1U = 1 generic + 1 blue"


@dataclass
class ManaStep:
    """Um passo no plano de mana."""
    action: str           # "Tap Seachrome Coast for W"
    source: Any = None    # Carta
    color: Any = None     # Cor produzida
    amount: int = 1
    pays_for: str = ""    # O que esta pagando (generic, blue, etc.)


class ManaSolver:
    """
    Resolve a melhor sequencia de ativacoes de terrenos para pagar um custo.
    
    Entrada:
      - Campo de batalha
      - Custo da magia (ex: 1U = 1 generico + 1 azul)
    
    Saida:
      - Plano de ativacoes
      - Pode pagar? Sim/Nao
    """
    
    def __init__(self):
        self.mana_engine = ManaAbilityEngine()
    
    def solve(self, player, required_mana: Dict) -> ManaPlan:
        """
        Resolve a melhor combinacao de mana.
        
        Args:
            player: Estado do jogador
            required_mana: Dict de mana necessaria
                          ex: {"generic": 1, Color.BLUE: 1}
        
        Returns:
            ManaPlan com os passos para gerar a mana
        """
        plan = ManaPlan()
        
        # Obtem todas as habilidades de mana disponiveis
        abilities = self.mana_engine.get_mana_abilities(player)
        
        # Filtra apenas as que podem ser ativadas
        available = [a for a in abilities if a.can_activate(player)]
        
        # Calcula mana ja disponivel no pool
        current_pool = dict(player.mana_pool)
        
        # Verifica se ja tem mana suficiente
        if self._has_enough_mana(current_pool, required_mana):
            plan.can_pay = True
            plan.description = "Mana ja disponivel no pool"
            return plan
        
        # Tenta encontrar uma combinacao
        remaining = dict(required_mana)
        used_sources = set()
        
        # 1. Primeiro paga as cores especificas (nao-genericas)
        for color in list(remaining.keys()):
            if color == "generic":
                continue
            if not isinstance(color, Color):
                continue
            
            amount_needed = remaining[color]
            if amount_needed <= 0:
                continue
            
            # Tenta encontrar terrenos que produzem essa cor
            for ability in available:
                if ability.source in used_sources:
                    continue
                if ability.ability_type not in [ManaActionType.TAP_FOR_MANA, ManaActionType.TAP_PAY_LIFE_FOR_MANA]:
                    continue
                
                # Verifica se produz essa cor
                if color in ability.produces:
                    produces = ability.produces[color]
                    use = min(produces, amount_needed)
                    
                    step = ManaStep(
                        action=f"Tap {ability.source.name} for {color.name}",
                        source=ability.source,
                        color=color,
                        amount=use,
                        pays_for=color.name
                    )
                    plan.steps.append(step)
                    
                    remaining[color] -= use
                    used_sources.add(ability.source)
                    
                    if remaining[color] <= 0:
                        del remaining[color]
                    
                    amount_needed -= use
                    if amount_needed <= 0:
                        break
        
        # 2. Depois paga o generico com qualquer mana
        if "generic" in remaining and remaining["generic"] > 0:
            generic_needed = remaining["generic"]
            
            for ability in available:
                if ability.source in used_sources:
                    continue
                if ability.ability_type not in [ManaActionType.TAP_FOR_MANA, ManaActionType.TAP_PAY_LIFE_FOR_MANA]:
                    continue
                
                # Pega qualquer cor que o terreno produz
                for color in ability.produces:
                    if generic_needed <= 0:
                        break
                    
                    step = ManaStep(
                        action=f"Tap {ability.source.name} for {color.name if hasattr(color, 'name') else color} (generic)",
                        source=ability.source,
                        color=color,
                        amount=1,
                        pays_for="generic"
                    )
                    plan.steps.append(step)
                    
                    generic_needed -= 1
                    used_sources.add(ability.source)
                    
                    if generic_needed <= 0:
                        break
            
            remaining["generic"] = generic_needed
            if remaining["generic"] <= 0:
                del remaining["generic"]
        
        # 3. Tenta terrenos de qualquer cor (Gemstone Mine, Lotus Bloom, etc.)
        for ability in available:
            if ability.source in used_sources:
                continue
            
            # Terrenos que produzem qualquer cor (5 cores no produces)
            if len(ability.produces) >= 5:
                # Paga cores especificas primeiro
                for color in list(remaining.keys()):
                    if color == "generic":
                        continue
                    if not isinstance(color, Color):
                        continue
                    
                    amount_needed = remaining[color]
                    if amount_needed > 0:
                        step = ManaStep(
                            action=f"Activate {ability.source.name} for {color.name}",
                            source=ability.source,
                            color=color,
                            amount=1,
                            pays_for=color.name
                        )
                        plan.steps.append(step)
                        remaining[color] -= 1
                        used_sources.add(ability.source)
                        
                        if remaining[color] <= 0:
                            del remaining[color]
                        break
                
                # Depois paga generico
                if "generic" in remaining and remaining["generic"] > 0:
                    for color in ability.produces:
                        if remaining["generic"] <= 0:
                            break
                        
                        step = ManaStep(
                            action=f"Activate {ability.source.name} for {color.name if hasattr(color, 'name') else color} (generic)",
                            source=ability.source,
                            color=color,
                            amount=1,
                            pays_for="generic"
                        )
                        plan.steps.append(step)
                        remaining["generic"] -= 1
                        used_sources.add(ability.source)
                    
                    if remaining["generic"] <= 0:
                        del remaining["generic"]
        
        # 4. Tenta fetch lands se ainda precisa de mana
        for ability in available:
            if ability.ability_type != ManaActionType.FETCH_LAND:
                continue
            if ability.source in used_sources:
                continue
            
            # Verifica se pode buscar um terreno que produza a cor necessaria
            for color in list(remaining.keys()):
                if color == "generic":
                    continue
                if not isinstance(color, Color):
                    continue
                
                amount_needed = remaining[color]
                if amount_needed > 0:
                    fetch_target = self._find_best_fetch_target(ability, color, player)
                    if fetch_target:
                        step = ManaStep(
                            action=f"Sacrifice {ability.source.name}, fetch {fetch_target}",
                            source=ability.source,
                            color=color,
                            amount=1,
                            pays_for=color.name
                        )
                        plan.steps.append(step)
                        remaining[color] -= 1
                        used_sources.add(ability.source)
                        
                        if remaining[color] <= 0:
                            del remaining[color]
                        break
        
        # Verifica se conseguiu pagar tudo
        plan.can_pay = len(remaining) == 0
        plan.total_produced = {k: required_mana[k] - remaining.get(k, 0) for k in required_mana}
        
        if plan.can_pay:
            plan.description = f"Plano: {len(plan.steps)} ativacoes"
        else:
            plan.description = f"Mana insuficiente. Falta: {remaining}"
        
        return plan
    
    def _has_enough_mana(self, pool: Dict, required: Dict) -> bool:
        """Verifica se o pool tem mana suficiente."""
        # Verifica cores especificas
        for color, amount in required.items():
            if color == "generic":
                continue
            available = pool.get(color, 0)
            if available < amount:
                return False
        
        # Verifica generico (pode ser pago com qualquer cor)
        if "generic" in required:
            generic_needed = required["generic"]
            total_available = sum(pool.values())
            # Subtrai as cores especificas ja alocadas
            for color, amount in required.items():
                if color != "generic":
                    total_available -= min(pool.get(color, 0), amount)
            
            if total_available < generic_needed:
                return False
        
        return True
    
    def _find_best_fetch_target(self, fetch_ability, color, player) -> Optional[str]:
        """Encontra o melhor terreno para buscar com uma fetch land."""
        if not hasattr(fetch_ability, 'fetch_options'):
            return None
        
        # Filtra opcoes que produzem a cor necessaria
        from .mana_engine import LAND_MANA_ABILITIES
        for land_name in fetch_ability.fetch_options:
            land_data = LAND_MANA_ABILITIES.get(land_name, {})
            produces = land_data.get("produces", {})
            if color in produces:
                return land_name
        
        return None
    
    def can_cast(self, player, card) -> Tuple[bool, Optional[ManaPlan]]:
        """
        Verifica se o jogador pode conjurar uma carta.
        Retorna (pode_conjurar, plano_de_mana).
        """
        # Calcula o custo de mana da carta
        required = self._calculate_mana_cost(card)
        
        plan = self.solve(player, required)
        plan.cost_breakdown = self._format_cost(required)
        
        return plan.can_pay, plan
    
    def _calculate_mana_cost(self, card) -> Dict:
        """
        Calcula o custo de mana de uma carta.
        Retorna dict com cores e generico.
        Ex: {Color.BLUE: 1, "generic": 1} para custo 1U
        """
        cmc = getattr(card, 'cmc', 0)
        colors = getattr(card, 'colors', [])
        
        required = {}
        
        # Adiciona cores especificas
        for color in colors:
            required[color] = required.get(color, 0) + 1
        
        # Adiciona generico (CMC - cores)
        generic = cmc - len(colors)
        if generic > 0:
            required["generic"] = generic
        
        return required
    
    def _format_cost(self, required: Dict) -> str:
        """Formata o custo para exibicao."""
        parts = []
        generic = required.get("generic", 0)
        if generic > 0:
            parts.append(f"{generic} generic")
        
        for color, amount in required.items():
            if color == "generic":
                continue
            color_name = color.name if hasattr(color, 'name') else str(color)
            parts.append(f"{amount} {color_name}")
        
        return " + ".join(parts) if parts else "0"
    
    def get_all_castable(self, player, hand) -> List[Tuple[Any, ManaPlan]]:
        """
        Retorna todas as cartas da mao que o jogador pode conjurar.
        """
        castable = []
        
        for card in hand:
            if card.is_land:
                continue
            
            can_cast, plan = self.can_cast(player, card)
            if can_cast:
                castable.append((card, plan))
        
        return castable
