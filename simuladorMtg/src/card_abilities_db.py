"""
MTG Match Simulator - Card Abilities Database
Habilidades das cartas definidas como dados, nao codigo.
O motor de regras usa esses dados para resolver efeitos automaticamente.
"""

from .event_bus import GameEvent


# ─────────────────────────────────────────────
# Formato das habilidades:
# {
#   "card_name": {
#     "abilities": [
#       {
#         "type": "triggered" | "activated" | "static" | "replacement",
#         "event": GameEvent.XXX,         (para triggered)
#         "condition": lambda,            (opcional)
#         "effect": "description",        (para resolucao)
#         "cost": "description",          (para activated)
#         "target": "description",
#       }
#     ]
#   }
# }
# ─────────────────────────────────────────────


CARD_ABILITIES = {
    
    # ─── Ad Nauseam ───
    "ad nauseam": {
        "abilities": [
            {
                "type": "special_action",
                "description": "Exile cards from top of library until a nonland card is exiled. Put that card into your hand. Lose life equal to its converted mana cost.",
                "effect": "ad_nauseam_effect"
            }
        ]
    },
    
    # ─── Angel's Grace ───
    "angel's grace": {
        "abilities": [
            {
                "type": "replacement",
                "event": GameEvent.GAME_LOST,
                "description": "You can't lose the game this turn and your opponents can't win the game this turn.",
                "effect": "angels_grace_effect"
            }
        ]
    },
    
    # ─── Phyrexian Unlife ───
    "phyrexian unlife": {
        "abilities": [
            {
                "type": "static",
                "description": "As long as you have 0 or less life, you don't lose the game and your opponents can't win the game.",
                "effect": "phyrexian_unlife_effect"
            },
            {
                "type": "triggered",
                "event": GameEvent.PERMANENT_ENTERS,
                "condition": "self",
                "description": "When Phyrexian Unlife enters the battlefield, you lose life equal to your life total.",
                "effect": "phyrexian_unlife_etb"
            }
        ]
    },
    
    # ─── Thassa's Oracle ───
    "thassa's oracle": {
        "abilities": [
            {
                "type": "triggered",
                "event": GameEvent.PERMANENT_ENTERS,
                "condition": "self",
                "description": "When Thassa's Oracle enters the battlefield, look at the top X cards of your library, where X is your devotion to blue. Put up to one of them into your hand and the rest on the bottom of your library in a random order. If your devotion to blue is 20 or more, you win the game.",
                "effect": "thassas_oracle_etb"
            }
        ]
    },
    
    # ─── Preordain ───
    "preordain": {
        "abilities": [
            {
                "type": "special_action",
                "description": "Scry 2, then draw a card.",
                "effect": "preordain_effect"
            }
        ]
    },
    
    # ─── Profane Tutor ───
    "profane tutor": {
        "abilities": [
            {
                "type": "special_action",
                "description": "Search your library for a card, put it into your hand, then shuffle. You lose 2 life.",
                "effect": "profane_tutor_effect"
            }
        ]
    },
    
    # ─── Lotus Bloom ───
    "lotus bloom": {
        "abilities": [
            {
                "type": "activated",
                "cost": "Suspend 3, Sacrifice Lotus Bloom",
                "description": "Add three mana of any one color.",
                "effect": "lotus_bloom_mana"
            }
        ]
    },
    
    # ─── Pact of Negation ───
    "pact of negation": {
        "abilities": [
            {
                "type": "counter_spell",
                "description": "Counter target spell. At the beginning of your next upkeep, pay 3BBB. If you don't, you lose the game.",
                "effect": "pact_of_negation_effect"
            }
        ]
    },
    
    # ─── Force of Negation ───
    "force of negation": {
        "abilities": [
            {
                "type": "counter_spell",
                "description": "Counter target spell. If you cast this spell during your main phase, pay 3 life and exile a blue card from your hand rather than pay its mana cost.",
                "effect": "force_of_negation_effect"
            }
        ]
    },
    
    # ─── Path to Exile ───
    "path to exile": {
        "abilities": [
            {
                "type": "special_action",
                "description": "Exile target creature. Its controller searches their library for a basic land card, puts that card onto the battlefield tapped, then shuffles.",
                "effect": "path_to_exile_effect"
            }
        ]
    },
    
    # ─── Sleight of Hand ───
    "sleight of hand": {
        "abilities": [
            {
                "type": "special_action",
                "description": "Draw a card.",
                "effect": "sleight_of_hand_effect"
            }
        ]
    },
    
    # ─── Spoils of the Vault ───
    "spoils of the vault": {
        "abilities": [
            {
                "type": "special_action",
                "description": "Exile cards from the top of your library until you exile a land card. Put that land card onto the battlefield tapped. You gain life equal to the converted mana cost of the last card exiled this way. Draw a card.",
                "effect": "spoils_of_the_vault_effect"
            }
        ]
    },
}


def get_card_abilities(card_name: str) -> dict:
    """Retorna as habilidades de uma carta."""
    name_lower = card_name.lower()
    return CARD_ABILITIES.get(name_lower, {"abilities": []})


def has_ability(card_name: str, ability_type: str) -> bool:
    """Verifica se uma carta tem um tipo de habilidade."""
    abilities = get_card_abilities(card_name)
    for ability in abilities.get("abilities", []):
        if ability.get("type") == ability_type:
            return True
    return False


def get_effect_name(card_name: str) -> str:
    """Retorna o nome do efeito de uma carta."""
    abilities = get_card_abilities(card_name)
    for ability in abilities.get("abilities", []):
        if "effect" in ability:
            return ability["effect"]
    return ""
