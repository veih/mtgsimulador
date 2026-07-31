"""
MTG Match Simulator - Modern Card Abilities
Habilidades de todas as cartas dos decks Modern, seguindo as regras oficiais.

Cada carta tem suas habilidades definidas como dados:
- Habilidades ativadas: {type: "activated", cost: "...", effect: "..."}
- Habilidades desencadeadas: {type: "triggered", event: "...", effect: "..."}
- Habilidades estaticas: {type: "static", effect: "..."}
- Acoes especiais: {type: "special_action", effect: "..."}
"""

from typing import Dict, List, Any
from .card import Color
from .event_bus import GameEvent


# ─────────────────────────────────────────────
# Ad Nauseam Deck
# ─────────────────────────────────────────────

AD_NAUSEAM_ABILITIES = {
    "thassa's oracle": {
        "cmc": 2,
        "colors": [Color.BLUE],
        "type": "creature",
        "subtype": ["Merfolk", "Wizard"],
        "power": 1,
        "toughness": 1,
        "abilities": [
            {
                "type": "triggered",
                "event": GameEvent.PERMANENT_ENTERS,
                "text": "When Thassa's Oracle enters the battlefield, look at the top X cards of your library, where X is your devotion to blue. Put up to one of them on top of your library and the rest on the bottom in a random order. Then if X is greater than or equal to the number of cards in your library, hand, and graveyard, you win the game.",
                "effect": "thassas_oracle_etb",
                "params": {"look_at": "devotion_to_blue", "win_condition": True}
            }
        ]
    },
    
    "ad nauseam": {
        "cmc": 4,
        "colors": [Color.BLACK],
        "type": "sorcery",
        "abilities": [
            {
                "type": "special_action",
                "text": "Exile cards from the top of your library until you exile a nonland card, then put that card into your hand. You lose life equal to its converted mana cost.",
                "effect": "ad_nauseam_effect",
                "params": {"exile_until_nonland": True, "lose_life": "cmc"}
            }
        ]
    },
    
    "angel's grace": {
        "cmc": 2,
        "colors": [Color.WHITE],
        "type": "instant",
        "abilities": [
            {
                "type": "instant_effect",
                "text": "You can't lose the game this turn and your opponents can't win the game this turn.",
                "effect": "angels_grace_effect",
                "params": {"cant_lose_game": True, "opponents_cant_win": True, "duration": "this_turn"}
            }
        ]
    },
    
    "phyrexian unlife": {
        "cmc": 3,
        "colors": [],
        "type": "enchantment",
        "abilities": [
            {
                "type": "static",
                "text": "As long as you have no life, you don't lose the game and damage from sources with infect doesn't cause you to lose the game.",
                "effect": "phyrexian_unlife_effect",
                "params": {"cant_lose_game_at_zero_life": True, "infect_cant_kill": True}
            },
            {
                "type": "activated",
                "cost": "{2}{W/P}",
                "text": "{2}{W/P}: Exile target artifact or enchantment.",
                "effect": "exile_target",
                "params": {"target_type": ["artifact", "enchantment"]}
            }
        ]
    },
    
    "lotus bloom": {
        "cmc": 0,
        "colors": [],
        "type": "artifact",
        "abilities": [
            {
                "type": "special_action",
                "text": "Suspend 3—{0}",
                "effect": "suspend",
                "params": {"time_counters": 3, "cost": 0}
            },
            {
                "type": "activated",
                "cost": "{T}, Sacrifice Lotus Bloom",
                "text": "{T}, Sacrifice Lotus Bloom: Add three mana of any one color.",
                "effect": "add_three_mana_same_color",
                "params": {"tap": True, "sacrifice": True, "amount": 3, "same_color": True}
            }
        ]
    },
    
    "pact of negation": {
        "cmc": 0,
        "colors": [Color.BLUE],
        "type": "instant",
        "abilities": [
            {
                "type": "instant_effect",
                "text": "Counter target spell. At the beginning of your next upkeep, pay {3}{U}. If you don't, you lose the game.",
                "effect": "pact_of_negation_effect",
                "params": {"counter_target": True, "upkeep_payment": {"cost": "{3}{U}", "penalty": "lose_game"}}
            }
        ]
    },
    
    "force of negation": {
        "cmc": 2,
        "colors": [Color.BLUE],
        "type": "instant",
        "abilities": [
            {
                "type": "alternative_cost",
                "text": "You may pay {0} and exile a blue card from your hand rather than pay this spell's mana cost.",
                "effect": "alternative_cost_exile_blue",
                "params": {"alternative_cost": 0, "exile_from_hand": Color.BLUE}
            },
            {
                "type": "instant_effect",
                "text": "Counter target spell. If that spell is countered this way, exile it instead of putting it into its owner's graveyard.",
                "effect": "counter_and_exile",
                "params": {"counter_target": True, "exile_if_countered": True}
            }
        ]
    },
    
    "preordain": {
        "cmc": 1,
        "colors": [Color.BLUE],
        "type": "sorcery",
        "abilities": [
            {
                "type": "sorcery_effect",
                "text": "Scry 2, then draw a card.",
                "effect": "scry_and_draw",
                "params": {"scry": 2, "draw": 1}
            }
        ]
    },
    
    "profane tutor": {
        "cmc": 1,
        "colors": [Color.BLACK],
        "type": "sorcery",
        "abilities": [
            {
                "type": "sorcery_effect",
                "text": "Search your library for a card, put that card into your hand, discard a card, then shuffle.",
                "effect": "tutor_and_discard",
                "params": {"search_library": True, "discard": 1, "shuffle": True}
            }
        ]
    },
    
    "sleight of hand": {
        "cmc": 0,
        "colors": [Color.BLUE],
        "type": "sorcery",
        "abilities": [
            {
                "type": "sorcery_effect",
                "text": "Look at the top two cards of your library. Put one of them into your hand and the other on the bottom of your library.",
                "effect": "look_and_choose",
                "params": {"look_at": 2, "put_in_hand": 1, "put_on_bottom": 1}
            }
        ]
    },
    
    "spoils of the vault": {
        "cmc": 0,
        "colors": [Color.BLACK],
        "type": "instant",
        "abilities": [
            {
                "type": "instant_effect",
                "text": "Exile cards from the top of your library until you exile a card you can cast. Put that card into your hand, then put the rest on the bottom in a random order. You lose life equal to the number of cards exiled this way.",
                "effect": "spoils_of_the_vault_effect",
                "params": {"exile_until_castable": True, "lose_life": "cards_exiled"}
            }
        ]
    },
    
    "path to exile": {
        "cmc": 1,
        "colors": [Color.WHITE],
        "type": "instant",
        "abilities": [
            {
                "type": "instant_effect",
                "text": "Exile target creature. Its controller may search their library for a basic land card, put that card onto the battlefield tapped, then shuffle.",
                "effect": "exile_creature",
                "params": {"target_type": "creature", "opponent_searches_basic_land": True}
            }
        ]
    },
    
    "otawara, soaring city": {
        "cmc": 3,
        "colors": [Color.BLUE],
        "type": "legendary_land",
        "abilities": [
            {
                "type": "tap_for_mana",
                "text": "{T}: Add {U}.",
                "effect": "add_blue",
                "params": {"tap": True, "color": Color.BLUE}
            },
            {
                "type": "activated",
                "cost": "{T}",
                "text": "{T}: Return target nonland permanent to its owner's hand.",
                "effect": "bounce_permanent",
                "params": {"tap": True, "target_type": "nonland_permanent", "return_to_hand": True}
            }
        ]
    }
}


# ─────────────────────────────────────────────
# Izzet Murktide Deck
# ─────────────────────────────────────────────

IZZET_MURKTIDE_ABILITIES = {
    "murktide regent": {
        "cmc": 7,
        "colors": [Color.BLUE],
        "type": "creature",
        "subtype": ["Dragon"],
        "power": 8,
        "toughness": 8,
        "abilities": [
            {
                "type": "alternative_cost",
                "text": "You may pay {1} and exile a blue card from your graveyard rather than pay this spell's mana cost.",
                "effect": "alternative_cost_exile_blue_from_graveyard",
                "params": {"alternative_cost": 1, "exile_from_graveyard": Color.BLUE}
            },
            {
                "type": "triggered",
                "event": GameEvent.PERMANENT_ENTERS,
                "text": "Flying. Delve. When Murktide Regent enters the battlefield, draw a card.",
                "effect": "murktide_etb",
                "params": {"flying": True, "delve": True, "draw": 1}
            }
        ]
    },
    
    "ragavan, nimble pilferer": {
        "cmc": 1,
        "colors": [Color.RED],
        "type": "legendary_creature",
        "subtype": ["Monkey", "Pirate"],
        "power": 2,
        "toughness": 1,
        "abilities": [
            {
                "type": "triggered",
                "event": GameEvent.ATTACK,
                "text": "Whenever Ragavan, Nimble Pilferer attacks, create a Treasure token. Then exile the top card of target opponent's library. Until the end of your next turn, you may play that card.",
                "effect": "ragavan_attack",
                "params": {"create_treasure": True, "exile_top_card": True, "play_exiled": True}
            },
            {
                "type": "static",
                "text": "Haste",
                "effect": "haste",
                "params": {"haste": True}
            }
        ]
    },
    
    "dragon's rage channeler": {
        "cmc": 1,
        "colors": [Color.RED],
        "type": "creature",
        "subtype": ["Human", "Wizard"],
        "power": 1,
        "toughness": 3,
        "abilities": [
            {
                "type": "static",
                "text": "As long as there are four or more cards with delve in your graveyard, Dragon's Rage Channeler gets +3/+3, has flying, and has '{2}{R}: Dragon's Rage Channeler deals 2 damage to any target.'",
                "effect": "delve_threshold",
                "params": {"threshold": 4, "keyword": "delve", "bonus_pt": [3, 3], "flying": True, "activated_ability": True}
            }
        ]
    },
    
    "expressive iteration": {
        "cmc": 3,
        "colors": [Color.BLUE, Color.RED],
        "type": "sorcery",
        "abilities": [
            {
                "type": "sorcery_effect",
                "text": "Look at the top three cards of your library. Put one of them into your hand, put one of them on the bottom of your library, and exile one of them. You may play the exiled card until the end of your next turn.",
                "effect": "expressive_iteration_effect",
                "params": {"look_at": 3, "put_in_hand": 1, "put_on_bottom": 1, "exile_and_play": 1}
            }
        ]
    },
    
    "lightning bolt": {
        "cmc": 1,
        "colors": [Color.RED],
        "type": "instant",
        "abilities": [
            {
                "type": "instant_effect",
                "text": "Lightning Bolt deals 3 damage to any target.",
                "effect": "deal_damage",
                "params": {"damage": 3, "target": "any"}
            }
        ]
    },
    
    "spell snare": {
        "cmc": 0,
        "colors": [Color.BLUE],
        "type": "instant",
        "abilities": [
            {
                "type": "instant_effect",
                "text": "Counter target creature spell with converted mana cost 2 or less.",
                "effect": "counter_creature",
                "params": {"counter_target": True, "target_type": "creature_spell", "cmc_condition": "<=2"}
            }
        ]
    },
    
    "counterspell": {
        "cmc": 2,
        "colors": [Color.BLUE],
        "type": "instant",
        "abilities": [
            {
                "type": "instant_effect",
                "text": "Counter target spell.",
                "effect": "counter_spell",
                "params": {"counter_target": True}
            }
        ]
    },
    
    "unholy heat": {
        "cmc": 1,
        "colors": [Color.RED],
        "type": "instant",
        "abilities": [
            {
                "type": "instant_effect",
                "text": "Unholy Heat deals 2 damage to target creature or planeswalker. Delve. If there are four or more cards with delve in your graveyard, Unholy Heat deals 6 damage instead.",
                "effect": "unholy_heat_effect",
                "params": {"damage": 2, "delve_damage": 6, "threshold": 4, "target_type": ["creature", "planeswalker"]}
            }
        ]
    },
    
    "thought scour": {
        "cmc": 0,
        "colors": [Color.BLUE],
        "type": "instant",
        "abilities": [
            {
                "type": "instant_effect",
                "text": "Delve. Target player mills two cards.",
                "effect": "mill",
                "params": {"delve": True, "mill": 2, "target_player": True}
            }
        ]
    },
    
    "serum visions": {
        "cmc": 1,
        "colors": [Color.BLUE],
        "type": "sorcery",
        "abilities": [
            {
                "type": "sorcery_effect",
                "text": "Draw a card, scry 1, then put a card from your hand on the bottom of your library.",
                "effect": "serum_visions_effect",
                "params": {"draw": 1, "scry": 1, "put_on_bottom": 1}
            }
        ]
    }
}


# ─────────────────────────────────────────────
# Amulet Titan Deck
# ─────────────────────────────────────────────

AMULET_TITAN_ABILITIES = {
    "primeval titan": {
        "cmc": 8,
        "colors": [Color.GREEN],
        "type": "creature",
        "subtype": ["Titan"],
        "power": 6,
        "toughness": 6,
        "abilities": [
            {
                "type": "static",
                "text": "Trample",
                "effect": "trample",
                "params": {"trample": True}
            },
            {
                "type": "triggered",
                "event": GameEvent.PERMANENT_ENTERS,
                "text": "When Primeval Titan enters the battlefield, you may search your library for up to two land cards, put them onto the battlefield, then shuffle.",
                "effect": "titan_etb",
                "params": {"search_library": True, "target_type": "land", "max_lands": 2, "put_onto_battlefield": True}
            }
        ]
    },
    
    "simian spirit guide": {
        "cmc": 2,
        "colors": [Color.RED],
        "type": "creature",
        "subtype": ["Ape"],
        "power": 3,
        "toughness": 2,
        "abilities": [
            {
                "type": "alternative_cost",
                "text": "You may exile Simian Spirit Guide from your hand rather than pay its mana cost.",
                "effect": "alternative_cost_exile_from_hand",
                "params": {"exile_from_hand": True}
            },
            {
                "type": "static",
                "text": "Haste",
                "effect": "haste",
                "params": {"haste": True}
            }
        ]
    },
    
    "ancient stirrings": {
        "cmc": 1,
        "colors": [Color.GREEN],
        "type": "sorcery",
        "abilities": [
            {
                "type": "sorcery_effect",
                "text": "Look at the top five cards of your library. You may reveal a basic land card or a card with delve from among them and put it into your hand. Put the rest on the bottom of your library in a random order.",
                "effect": "ancient_stirrings_effect",
                "params": {"look_at": 5, "reveal_basic_or_delve": True, "put_in_hand": 1}
            }
        ]
    },
    
    "sylvan scrying": {
        "cmc": 2,
        "colors": [Color.GREEN],
        "type": "sorcery",
        "abilities": [
            {
                "type": "sorcery_effect",
                "text": "Search your library for a land card, put it onto the battlefield, then shuffle.",
                "effect": "search_and_put_onto_battlefield",
                "params": {"search_library": True, "target_type": "land", "put_onto_battlefield": True}
            }
        ]
    },
    
    "expedition map": {
        "cmc": 1,
        "colors": [],
        "type": "artifact",
        "abilities": [
            {
                "type": "activated",
                "cost": "{1}, {T}, Sacrifice Expedition Map",
                "text": "{1}, {T}, Sacrifice Expedition Map: Search your library for a land card, exile it, then shuffle. You may play that card this turn.",
                "effect": "expedition_map_effect",
                "params": {"tap": True, "sacrifice": True, "search_library": True, "target_type": "land", "exile_and_play": True}
            }
        ]
    },
    
    "amulet of vigor": {
        "cmc": 2,
        "colors": [],
        "type": "artifact",
        "abilities": [
            {
                "type": "triggered",
                "event": GameEvent.PERMANENT_ENTERS,
                "text": "Whenever a land enters the battlefield under your control, if it has the tap ability to produce mana of any color, untap it.",
                "effect": "amulet_etb_trigger",
                "params": {"untap_lands_with_mana_abilities": True}
            }
        ]
    },
    
    "urza's saga": {
        "cmc": 1,
        "colors": [],
        "type": "legendary_enchantment",
        "subtype": ["Urza's", "Saga"],
        "abilities": [
            {
                "type": "triggered",
                "event": GameEvent.PERMANENT_ENTERS,
                "text": "When Urza's Saga enters the battlefield, search your library for an artifact card with converted mana cost 1 or less, put it onto the battlefield, then shuffle.",
                "effect": "urzas_saga_chapter_1",
                "params": {"search_library": True, "target_type": "artifact", "cmc_condition": "<=1"}
            },
            {
                "type": "triggered",
                "event": GameEvent.UPKEEP,
                "text": "At the beginning of your second main phase, search your library for an artifact card with converted mana cost 4 or less, put it onto the battlefield, then shuffle. Then sacrifice Urza's Saga.",
                "effect": "urzas_saga_chapter_2",
                "params": {"search_library": True, "target_type": "artifact", "cmc_condition": "<=4", "sacrifice_self": True}
            }
        ]
    },
    
    "valakut, the molten pinnacle": {
        "cmc": 0,
        "colors": [],
        "type": "land",
        "abilities": [
            {
                "type": "tap_for_mana",
                "text": "{T}: Add {R}.",
                "effect": "add_red",
                "params": {"tap": True, "color": Color.RED}
            },
            {
                "type": "triggered",
                "event": GameEvent.PERMANENT_ENTERS,
                "text": "Whenever a Mountain enters the battlefield under your control, if you control at least five other Mountains, Valakut, the Molten Pinnacle deals 3 damage to any target.",
                "effect": "valakut_trigger",
                "params": {"trigger_on_mountain": True, "condition": "5_other_mountains", "damage": 3}
            }
        ]
    }
}


# ─────────────────────────────────────────────
# Hollow One Deck
# ─────────────────────────────────────────────

HOLLOW_ONE_ABILITIES = {
    "hollow one": {
        "cmc": 5,
        "colors": [Color.BLACK],
        "type": "artifact_creature",
        "subtype": ["Golem"],
        "power": 4,
        "toughness": 4,
        "abilities": [
            {
                "type": "alternative_cost",
                "text": "You may pay {3}{B} and discard a card rather than pay Hollow One's mana cost.",
                "effect": "alternative_cost_discard",
                "params": {"alternative_cost": "{3}{B}", "discard": 1}
            }
        ]
    },
    
    "goblin charbelcher": {
        "cmc": 4,
        "colors": [Color.RED],
        "type": "artifact",
        "abilities": [
            {
                "type": "activated",
                "cost": "{4}, {T}",
                "text": "{4}, {T}: Reveal cards from the top of your library until you reveal a land card. Goblin Charbelcher deals damage equal to the number of nonland cards revealed this way to any target. Put the revealed cards on the bottom of your library in a random order.",
                "effect": "charbelcher_effect",
                "params": {"tap": True, "reveal_until_land": True, "damage": "nonland_revealed"}
            }
        ]
    },
    
    "flame slash": {
        "cmc": 1,
        "colors": [Color.RED],
        "type": "sorcery",
        "abilities": [
            {
                "type": "sorcery_effect",
                "text": "Flame Slash deals 2 damage to target creature.",
                "effect": "deal_damage",
                "params": {"damage": 2, "target_type": "creature"}
            }
        ]
    },
    
    "faithless looting": {
        "cmc": 1,
        "colors": [Color.RED],
        "type": "sorcery",
        "abilities": [
            {
                "type": "sorcery_effect",
                "text": "Draw two cards, then discard two cards. Flashback {2}{R}.",
                "effect": "draw_and_discard",
                "params": {"draw": 2, "discard": 2, "flashback": "{2}{R}"}
            }
        ]
    },
    
    "gurmag angler": {
        "cmc": 5,
        "colors": [Color.BLACK],
        "type": "creature",
        "subtype": ["Zombie", "Fish"],
        "power": 5,
        "toughness": 4,
        "abilities": [
            {
                "type": "static",
                "text": "Delve",
                "effect": "delve",
                "params": {"delve": True}
            }
        ]
    },
    
    "bloodghast": {
        "cmc": 1,
        "colors": [Color.BLACK],
        "type": "creature",
        "subtype": ["Zombie"],
        "power": 2,
        "toughness": 1,
        "abilities": [
            {
                "type": "triggered",
                "event": GameEvent.PERMANENT_ENTERS,
                "text": "Bloodghast can't block. Whenever a land enters the battlefield under your control, you may return Bloodghast from your graveyard to the battlefield.",
                "effect": "bloodghast_return",
                "params": {"cant_block": True, "return_from_graveyard_on_land": True}
            }
        ]
    },
    
    "bridge from below": {
        "cmc": 0,
        "colors": [Color.BLACK],
        "type": "enchantment",
        "abilities": [
            {
                "type": "triggered",
                "event": GameEvent.CREATURE_DIED,
                "text": "Whenever another creature is put into your graveyard from the battlefield, if Bridge from Below is in your graveyard, create a 2/2 black Zombie creature token.",
                "effect": "bridge_from_below_trigger",
                "params": {"trigger_on_creature_death": True, "create_zombie_token": True}
            }
        ]
    },
    
    "dread return": {
        "cmc": 3,
        "colors": [Color.BLACK],
        "type": "sorcery",
        "abilities": [
            {
                "type": "sorcery_effect",
                "text": "Return target creature card from your graveyard to the battlefield. Flashback—Sacrifice three creatures.",
                "effect": "return_creature",
                "params": {"return_from_graveyard": True, "target_type": "creature", "flashback": "sacrifice_three_creatures"}
            }
        ]
    },
    
    "vengevine": {
        "cmc": 3,
        "colors": [Color.GREEN],
        "type": "creature",
        "subtype": ["Plant", "Elemental"],
        "power": 0,
        "toughness": 2,
        "abilities": [
            {
                "type": "triggered",
                "event": GameEvent.CREATURE_DIED,
                "text": "Whenever another creature is put into your graveyard from the battlefield, you may discard a card. If you do, return Vengevine from your graveyard to the battlefield.",
                "effect": "vengevine_return",
                "params": {"trigger_on_creature_death": True, "discard_to_return": True}
            }
        ]
    },
    
    "bazaar of baghdad": {
        "cmc": 0,
        "colors": [],
        "type": "land",
        "abilities": [
            {
                "type": "activated",
                "cost": "{T}",
                "text": "{T}: Draw two cards, then discard three cards.",
                "effect": "bazaar_effect",
                "params": {"tap": True, "draw": 2, "discard": 3}
            }
        ]
    }
}


# ─────────────────────────────────────────────
# Prowess Deck
# ─────────────────────────────────────────────

PROWESS_ABILITIES = {
    "monastery swiftspear": {
        "cmc": 1,
        "colors": [Color.RED],
        "type": "creature",
        "subtype": ["Human", "Monk"],
        "power": 1,
        "toughness": 2,
        "abilities": [
            {
                "type": "static",
                "text": "Haste. Prowess",
                "effect": "haste_prowess",
                "params": {"haste": True, "prowess": True}
            }
        ]
    },
    
    "soul-scar mage": {
        "cmc": 1,
        "colors": [Color.RED],
        "type": "creature",
        "subtype": ["Human", "Wizard"],
        "power": 1,
        "toughness": 2,
        "abilities": [
            {
                "type": "triggered",
                "event": GameEvent.DAMAGE_DEALT,
                "text": "Prowess. Whenever you deal noncombat damage to an opponent or a planeswalker they control, put that many -1/-1 counters on target creature an opponent controls.",
                "effect": "soul_scar_trigger",
                "params": {"prowess": True, "trigger_on_noncombat_damage": True, "add_counters": "-1/-1"}
            }
        ]
    },
    
    "goblin guide": {
        "cmc": 1,
        "colors": [Color.RED],
        "type": "creature",
        "subtype": ["Goblin", "Scout"],
        "power": 2,
        "toughness": 2,
        "abilities": [
            {
                "type": "triggered",
                "event": GameEvent.ATTACK,
                "text": "Haste. Whenever Goblin Guide attacks, defending player reveals the top card of their library. If it's a land card, that player puts it into their hand. Otherwise, you may look at that card until end of turn, and you may spend mana as though it were mana of any type to cast that spell.",
                "effect": "goblin_guide_attack",
                "params": {"haste": True, "reveal_top_card": True, "may_play_if_nonland": True}
            }
        ]
    },
    
    "eidolon of the great revel": {
        "cmc": 2,
        "colors": [Color.RED],
        "type": "creature",
        "subtype": ["Spirit"],
        "power": 2,
        "toughness": 2,
        "abilities": [
            {
                "type": "triggered",
                "event": GameEvent.CAST_SPELL,
                "text": "Whenever a player casts a spell with converted mana cost 3 or less, Eidolon of the Great Revel deals 2 damage to that player.",
                "effect": "eidolon_trigger",
                "params": {"trigger_on_low_cmc_spell": True, "cmc_condition": "<=3", "damage": 2}
            }
        ]
    },
    
    "lava spike": {
        "cmc": 1,
        "colors": [Color.RED],
        "type": "sorcery",
        "abilities": [
            {
                "type": "sorcery_effect",
                "text": "Lava Spike deals 3 damage to target player or planeswalker.",
                "effect": "deal_damage",
                "params": {"damage": 3, "target_type": ["player", "planeswalker"]}
            }
        ]
    },
    
    "rift bolt": {
        "cmc": 2,
        "colors": [Color.RED],
        "type": "sorcery",
        "abilities": [
            {
                "type": "sorcery_effect",
                "text": "Rift Bolt deals 3 damage to any target. Suspend 2—{R}.",
                "effect": "deal_damage_suspend",
                "params": {"damage": 3, "target": "any", "suspend": {"time_counters": 2, "cost": "{R}"}}
            }
        ]
    },
    
    "burst lightning": {
        "cmc": 1,
        "colors": [Color.RED],
        "type": "instant",
        "abilities": [
            {
                "type": "instant_effect",
                "text": "Kicker {2}. Burst Lightning deals 2 damage to any target. If it was kicked, it deals 4 damage instead.",
                "effect": "burst_lightning_effect",
                "params": {"damage": 2, "kicked_damage": 4, "kicker": "{2}", "target": "any"}
            }
        ]
    },
    
    "mishra's bauble": {
        "cmc": 0,
        "colors": [],
        "type": "artifact",
        "abilities": [
            {
                "type": "activated",
                "cost": "{T}, Sacrifice Mishra's Bauble",
                "text": "{T}, Sacrifice Mishra's Bauble: Draw a card.",
                "effect": "sacrifice_draw",
                "params": {"tap": True, "sacrifice": True, "draw": 1}
            }
        ]
    }
}


# ─────────────────────────────────────────────
# Jund Deck
# ─────────────────────────────────────────────

JUND_ABILITIES = {
    "bloodbraid elf": {
        "cmc": 3,
        "colors": [Color.GREEN, Color.RED],
        "type": "creature",
        "subtype": ["Elf", "Berserker"],
        "power": 3,
        "toughness": 2,
        "abilities": [
            {
                "type": "triggered",
                "event": GameEvent.PERMANENT_ENTERS,
                "text": "Haste. When Bloodbraid Elf enters the battlefield, reveal the top two cards of your library. You may put a nonland card from among them into your hand. Put the rest on the bottom of your library in a random order.",
                "effect": "bloodbraid_etb",
                "params": {"haste": True, "reveal_top": 2, "may_put_nonland_in_hand": True}
            }
        ]
    },
    
    "dark confidant": {
        "cmc": 3,
        "colors": [Color.BLACK],
        "type": "creature",
        "subtype": ["Human", "Wizard"],
        "power": 2,
        "toughness": 2,
        "abilities": [
            {
                "type": "triggered",
                "event": GameEvent.UPKEEP,
                "text": "At the beginning of your upkeep, reveal the top card of your library and put that card into your hand. You lose life equal to its converted mana cost.",
                "effect": "dark_confidant_trigger",
                "params": {"reveal_and_draw_top": True, "lose_life": "cmc"}
            }
        ]
    },
    
    "kolaghan's command": {
        "cmc": 2,
        "colors": [Color.BLACK, Color.RED],
        "type": "instant",
        "abilities": [
            {
                "type": "instant_effect",
                "text": "Choose two — • Return target creature card from your graveyard to your hand; • Kolaghan's Command deals 2 damage to any target; • Discard target player's hand; • Counter target spell.",
                "effect": "kolaghan_command_modes",
                "params": {"modes": 2, "options": ["return_creature", "deal_damage", "discard_hand", "counter_spell"]}
            }
        ]
    },
    
    "fatal push": {
        "cmc": 1,
        "colors": [Color.BLACK],
        "type": "instant",
        "abilities": [
            {
                "type": "instant_effect",
                "text": "Destroy target creature with converted mana cost 2 or less. Revolt — Destroy that creature instead if a permanent returned to the battlefield under your control this turn.",
                "effect": "fatal_push_effect",
                "params": {"destroy_creature": True, "cmc_condition": "<=2", "revolt": True}
            }
        ]
    },
    
    "inquisition of kozilek": {
        "cmc": 1,
        "colors": [Color.BLACK],
        "type": "sorcery",
        "abilities": [
            {
                "type": "sorcery_effect",
                "text": "Target player reveals their hand. You choose a nonland card from it with converted mana cost 3 or less. That player discards that card.",
                "effect": "inquisition_effect",
                "params": {"reveal_hand": True, "choose_nonland": True, "cmc_condition": "<=3", "discard": 1}
            }
        ]
    },
    
    "thoughtseize": {
        "cmc": 1,
        "colors": [Color.BLACK],
        "type": "sorcery",
        "abilities": [
            {
                "type": "sorcery_effect",
                "text": "Target player reveals their hand. You choose a nonland card from it. That player discards that card. You lose 2 life.",
                "effect": "thoughtseize_effect",
                "params": {"reveal_hand": True, "choose_nonland": True, "discard": 1, "lose_life": 2}
            }
        ]
    },
    
    "tarmogoyf": {
        "cmc": 2,
        "colors": [Color.GREEN],
        "type": "creature",
        "subtype": ["Lhurgoyf"],
        "power": 1,
        "toughness": 2,
        "abilities": [
            {
                "type": "static",
                "text": "Tarmogoyf's power is equal to the number of card types among cards in all graveyards and its toughness is equal to that number plus 1.",
                "effect": "tarmogoyf_stats",
                "params": {"power": "card_types_in_graveyards", "toughness": "card_types_plus_1"}
            }
        ]
    },
    
    "wrenn and six": {
        "cmc": 2,
        "colors": [Color.GREEN, Color.RED],
        "type": "legendary_planeswalker",
        "subtype": ["Wrenn"],
        "loyalty": 3,
        "abilities": [
            {
                "type": "activated",
                "cost": "+1",
                "text": "+1: Return up to one target land card from your graveyard to your hand.",
                "effect": "wrenn_plus_one",
                "params": {"loyalty": "+1", "return_land_from_graveyard": True}
            },
            {
                "type": "activated",
                "cost": "0",
                "text": "0: Wrenn and Six deals 1 damage to any target.",
                "effect": "wrenn_zero",
                "params": {"loyalty": "0", "damage": 1, "target": "any"}
            },
            {
                "type": "activated",
                "cost": "-7",
                "text": "-7: You get an emblem with 'Instant and sorcery cards in your graveyard have retrace.'",
                "effect": "wrenn_minus_seven",
                "params": {"loyalty": "-7", "create_emblem": "retrace"}
            }
        ]
    },
    
    "liliana of the veil": {
        "cmc": 4,
        "colors": [Color.BLACK],
        "type": "legendary_planeswalker",
        "subtype": ["Liliana"],
        "loyalty": 3,
        "abilities": [
            {
                "type": "activated",
                "cost": "+1",
                "text": "+1: Each player discards a card.",
                "effect": "liliana_plus_one",
                "params": {"loyalty": "+1", "each_player_discards": 1}
            },
            {
                "type": "activated",
                "cost": "-2",
                "text": "-2: Destroy target creature. That creature's controller reveals cards from the top of their library until they reveal a creature card. That player puts that card into their hand and the rest on the bottom of their library.",
                "effect": "liliana_minus_two",
                "params": {"loyalty": "-2", "destroy_creature": True, "reveal_until_creature": True}
            },
            {
                "type": "activated",
                "cost": "-6",
                "text": "-6: Each player sacrifices all but the top three creatures of their choice from their graveyard.",
                "effect": "liliana_minus_six",
                "params": {"loyalty": "-6", "sacrifice_from_graveyard": True}
            }
        ]
    }
}


# ─────────────────────────────────────────────
# Death's Shadow Deck
# ─────────────────────────────────────────────

DEATHS_SHADOW_ABILITIES = {
    "death's shadow": {
        "cmc": 1,
        "colors": [Color.BLACK],
        "type": "creature",
        "subtype": ["Avatar"],
        "power": 13,
        "toughness": 13,
        "abilities": [
            {
                "type": "static",
                "text": "Death's Shadow gets -X/-X, where X is the difference between your starting life total and your life total.",
                "effect": "deaths_shadow_stats",
                "params": {"power_modifier": "-life_lost", "toughness_modifier": "-life_lost"}
            }
        ]
    },
    
    "temur battle rage": {
        "cmc": 2,
        "colors": [Color.GREEN, Color.BLUE, Color.RED],
        "type": "instant",
        "abilities": [
            {
                "type": "instant_effect",
                "text": "Target creature gets +2/+0 and gains trample and double strike until end of turn. Draw a card.",
                "effect": "temur_battle_rage_effect",
                "params": {"bonus_pt": [2, 0], "grant_trample": True, "grant_double_strike": True, "draw": 1}
            }
        ]
    },
    
    "daze": {
        "cmc": 1,
        "colors": [Color.BLUE],
        "type": "instant",
        "abilities": [
            {
                "type": "instant_effect",
                "text": "You may return an island you control to its owner's hand rather than pay Daze's mana cost. Counter target spell unless its controller pays {2}.",
                "effect": "daze_effect",
                "params": {"alternative_cost": "return_island", "counter_unless_pay": 2}
            }
        ]
    },
    
    "delirium skeins": {
        "cmc": 1,
        "colors": [Color.BLACK],
        "type": "sorcery",
        "abilities": [
            {
                "type": "sorcery_effect",
                "text": "Target player discards three cards. If that player has delirium, they discard four cards instead.",
                "effect": "delirium_skeins_effect",
                "params": {"discard": 3, "delirium_discard": 4}
            }
        ]
    },
    
    "street wraith": {
        "cmc": 2,
        "colors": [Color.BLACK],
        "type": "creature",
        "subtype": ["Wraith"],
        "power": 3,
        "toughness": 3,
        "abilities": [
            {
                "type": "activated",
                "cost": "{T}, Pay 2 life",
                "text": "{T}, Pay 2 life: Draw a card.",
                "effect": "street_wraith_draw",
                "params": {"tap": True, "pay_life": 2, "draw": 1}
            }
        ]
    }
}


# ─────────────────────────────────────────────
# Urza's Saga Tron Deck
# ─────────────────────────────────────────────

URZA_TRON_ABILITIES = {
    "karn liberated": {
        "cmc": 6,
        "colors": [],
        "type": "legendary_planeswalker",
        "subtype": ["Karn"],
        "loyalty": 5,
        "abilities": [
            {
                "type": "activated",
                "cost": "+1",
                "text": "+1: Add one mana of any color.",
                "effect": "karn_plus_one",
                "params": {"loyalty": "+1", "add_mana_any_color": 1}
            },
            {
                "type": "activated",
                "cost": "-3",
                "text": "-3: Target opponent exiles a card from their hand at random. You exile cards from the top of your library until you exile a nonland card. Put that card into your hand and the rest on the bottom in a random order.",
                "effect": "karn_minus_three",
                "params": {"loyalty": "-3", "opponent_discards": 1, "search_library": True}
            },
            {
                "type": "activated",
                "cost": "-10",
                "text": "-10: Target player gains control of Karn Liberated. That player exiles all cards from their graveyard, then shuffles those cards into their library.",
                "effect": "karn_minus_ten",
                "params": {"loyalty": "-10", "change_control": True, "shuffle_graveyard": True}
            }
        ]
    },
    
    "chromatic star": {
        "cmc": 1,
        "colors": [],
        "type": "artifact",
        "abilities": [
            {
                "type": "activated",
                "cost": "{1}, {T}, Sacrifice Chromatic Star",
                "text": "{1}, {T}, Sacrifice Chromatic Star: Add one mana of any color. Draw a card.",
                "effect": "chromatic_star_effect",
                "params": {"tap": True, "sacrifice": True, "add_mana_any_color": 1, "draw": 1}
            }
        ]
    },
    
    "chromatic sphere": {
        "cmc": 1,
        "colors": [],
        "type": "artifact",
        "abilities": [
            {
                "type": "activated",
                "cost": "{T}, Sacrifice Chromatic Sphere",
                "text": "{T}, Sacrifice Chromatic Sphere: Add one mana of any color. Draw a card.",
                "effect": "chromatic_sphere_effect",
                "params": {"tap": True, "sacrifice": True, "add_mana_any_color": 1, "draw": 1}
            }
        ]
    },
    
    "oblivia stone": {
        "cmc": 6,
        "colors": [],
        "type": "artifact",
        "abilities": [
            {
                "type": "activated",
                "cost": "{7}, {T}",
                "text": "{7}, {T}: Each player exiles all permanents they control, then each player reveals their hand and exiles all nonland cards from it. Each player shuffles all cards exiled this way into their library, then draws seven cards.",
                "effect": "oblivia_stone_effect",
                "params": {"tap": True, "exile_all": True, "reset_game": True}
            }
        ]
    },
    
    "mindslaver": {
        "cmc": 8,
        "colors": [],
        "type": "legendary_artifact",
        "abilities": [
            {
                "type": "activated",
                "cost": "{4}, {T}, Sacrifice Mindslaver",
                "text": "{4}, {T}, Sacrifice Mindslaver: You control target player during that player's next turn.",
                "effect": "mindslaver_effect",
                "params": {"tap": True, "sacrifice": True, "control_player": True, "duration": "next_turn"}
            }
        ]
    },
    
    "urza's mine": {
        "cmc": 0,
        "colors": [],
        "type": "land",
        "abilities": [
            {
                "type": "tap_for_mana",
                "text": "{T}: Add {C}. If you control both Urza's Mine and Urza's Tower, add {C}{C} instead.",
                "effect": "urza_mine_mana",
                "params": {"tap": True, "color": "colorless", "bonus_if_with_tower": True}
            }
        ]
    },
    
    "urza's power plant": {
        "cmc": 0,
        "colors": [],
        "type": "land",
        "abilities": [
            {
                "type": "tap_for_mana",
                "text": "{T}: Add {C}. If you control both Urza's Power Plant and Urza's Tower, add {C}{C} instead.",
                "effect": "urza_plant_mana",
                "params": {"tap": True, "color": "colorless", "bonus_if_with_tower": True}
            }
        ]
    },
    
    "urza's tower": {
        "cmc": 0,
        "colors": [],
        "type": "land",
        "abilities": [
            {
                "type": "tap_for_mana",
                "text": "{T}: Add {C}. If you control both Urza's Mine and Urza's Power Plant, add {C}{C}{C} instead.",
                "effect": "urza_tower_mana",
                "params": {"tap": True, "color": "colorless", "bonus_if_complete_tron": True}
            }
        ]
    }
}


# ─────────────────────────────────────────────
# Consolidated Card Database
# ─────────────────────────────────────────────

MODERN_CARD_ABILITIES = {
    **AD_NAUSEAM_ABILITIES,
    **IZZET_MURKTIDE_ABILITIES,
    **AMULET_TITAN_ABILITIES,
    **HOLLOW_ONE_ABILITIES,
    **PROWESS_ABILITIES,
    **JUND_ABILITIES,
    **DEATHS_SHADOW_ABILITIES,
    **URZA_TRON_ABILITIES,
}


def get_card_abilities(card_name: str) -> Dict:
    """Retorna as habilidades de uma carta."""
    return MODERN_CARD_ABILITIES.get(card_name.lower(), {})


def has_ability(card_name: str, ability_type: str) -> bool:
    """Verifica se uma carta tem um tipo de habilidade."""
    abilities = get_card_abilities(card_name)
    if not abilities:
        return False
    
    for ability in abilities.get("abilities", []):
        if ability.get("type") == ability_type:
            return True
    return False


def get_effect_name(card_name: str) -> str:
    """Retorna o nome do efeito principal de uma carta."""
    abilities = get_card_abilities(card_name)
    if not abilities:
        return ""
    
    for ability in abilities.get("abilities", []):
        if "effect" in ability:
            return ability["effect"]
    return ""
