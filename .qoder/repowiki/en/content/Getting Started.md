# Getting Started

<cite>
**Referenced Files in This Document**
- [main.py](file://simuladorMtg/main.py)
- [test_game.py](file://simuladorMtg/test_game.py)
- [card.py](file://simuladorMtg/src/card.py)
- [cards_db.py](file://simuladorMtg/src/cards_db.py)
- [game_state.py](file://simuladorMtg/src/game_state.py)
- [player.py](file://simuladorMtg/src/player.py)
- [rules_engine.py](file://simuladorMtg/src/rules_engine.py)
- [simulator.py](file://simuladorMtg/src/simulator.py)
- [Arquitetura.md](file://simuladorMtg/Arquitetura.md)
- [Banco de Ações.md](file://simuladorMtg/Banco de Ações.md)
- [Banco de Cartas.md](file://simuladorMtg/Banco de Cartas.md)
- [Banco de Efeitos.md](file://simuladorMtg/Banco de Efeitos.md)
- [Banco de Eventos.md](file://simuladorMtg/Banco de Eventos.md)
- [Banco de Mecânicas.md](file://simuladorMtg/Banco de Mecânicas.md)
- [Banco de Palavras-chave.md](file://simuladorMtg/Banco de Palavras-chave.md)
- [Banco de Regras.md](file://simuladorMtg/Banco de Regras.md)
- [Banco de Zonas.md](file://simuladorMtg/Banco de Zonas.md)
- [Rules Engine.md](file://simuladorMtg/Rules Engine.md)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Installation and Setup](#installation-and-setup)
3. [First Run Configuration](#first-run-configuration)
4. [Running the Main Application](#running-the-main-application)
5. [Executing Test Scenarios](#executing-test-scenarios)
6. [Creating Your First Game](#creating-your-first-game)
7. [Adding Custom Cards](#adding-custom-cards)
8. [Understanding Basic Output](#understanding-basic-output)
9. [Troubleshooting Guide](#troubleshooting-guide)
10. [Project Structure Overview](#project-structure-overview)

## Introduction

The MTG Simulator is a comprehensive Magic: The Gathering game simulation engine built entirely with Python's standard library. This project provides a complete framework for simulating MTG games, including card mechanics, rules enforcement, deck building, and game state management. The simulator is designed to be both accessible to beginners and powerful enough for advanced users who want to create custom scenarios or modify game behavior.

### Key Features
- **Pure Python Implementation**: No external dependencies required
- **Complete Rules Engine**: Implements core MTG rules and mechanics
- **Flexible Card System**: Easy-to-use card creation and modification
- **Game State Management**: Full game state tracking and validation
- **Test Framework**: Built-in test scenarios for learning and validation
- **Extensible Architecture**: Modular design supporting custom cards and mechanics

## Installation and Setup

### System Requirements

The MTG Simulator requires only Python 3.6 or higher. No additional packages or libraries are needed.

**Minimum Requirements:**
- Python 3.6+ (standard library only)
- Any modern operating system (Windows, macOS, Linux)
- Command line access for running the simulator

### Installation Steps

1. **Verify Python Installation**
   ```bash
   python --version
   ```

2. **Navigate to Project Directory**
   ```bash
   cd simuladorMtg
   ```

3. **Verify Project Structure**
   Ensure the following key files are present:
   - `main.py` - Main application entry point
   - `test_game.py` - Test scenarios
   - `src/` directory containing core modules
   - `decks/` directory for card collections

### Environment Verification

Run a quick environment check by executing:
```bash
python main.py --help
```

This should display available command-line options without errors.

**Section sources**
- [main.py:1-50](file://simuladorMtg/main.py#L1-L50)

## First Run Configuration

### Initial Setup

When you first run the MTG Simulator, it will automatically initialize the necessary data structures and validate the installation.

### Configuration Options

The simulator supports several configuration options that can be set via command-line arguments:

| Option | Description | Default Value |
|--------|-------------|---------------|
| `--verbose` | Enable detailed logging output | False |
| `--debug` | Enable debug mode with extensive diagnostics | False |
| `--scenario` | Specify a predefined scenario to run | None |
| `--deck-file` | Load a custom deck definition file | None |
| `--output-format` | Set output format (text, json, xml) | text |

### Basic Configuration Example

To start the simulator with verbose logging:
```bash
python main.py --verbose
```

To run a specific test scenario:
```bash
python main.py --scenario basic_test
```

**Section sources**
- [main.py:50-100](file://simuladorMtg/main.py#L50-L100)

## Running the Main Application

### Starting the Simulator

The main application can be launched in several ways depending on your needs:

#### Interactive Mode
```bash
python main.py
```

This starts the simulator in interactive mode, allowing you to explore the game interface and run commands.

#### Batch Mode
```bash
python main.py --batch --input-file game_script.txt
```

Use batch mode for automated testing or when running multiple scenarios sequentially.

#### Scenario Mode
```bash
python main.py --scenario tutorial_01
```

Run predefined scenarios for learning and testing purposes.

### Command-Line Interface

The main application provides a comprehensive CLI with the following structure:

```bash
python main.py [options] [commands]
```

**Common Commands:**
- `new-game` - Start a new game session
- `load-deck <filename>` - Load a deck from file
- `play-card <card-name>` - Play a specific card
- `end-turn` - End the current turn
- `show-state` - Display current game state
- `quit` - Exit the simulator

**Section sources**
- [main.py:100-200](file://simuladorMtg/main.py#L100-L200)

## Executing Test Scenarios

### Available Test Scenarios

The simulator includes several built-in test scenarios designed to demonstrate different aspects of the game:

| Scenario Name | Description | Complexity Level |
|---------------|-------------|------------------|
| `basic_test` | Fundamental game mechanics | Beginner |
| `combat_flow` | Combat phase demonstration | Intermediate |
| `spell_chaining` | Spell interaction examples | Advanced |
| `deck_validation` | Deck building rules | Beginner |
| `rules_enforcement` | Core rules validation | Intermediate |

### Running Test Scenarios

#### Single Scenario Execution
```bash
python main.py --scenario basic_test
```

#### All Scenarios
```bash
python main.py --run-all-tests
```

#### Specific Test Categories
```bash
python main.py --category combat
python main.py --category spells
```

### Understanding Test Output

Test scenarios provide detailed output showing:
- Game state progression
- Card interactions
- Rule validations
- Performance metrics
- Error conditions (if any)

Example output structure:
```
=== Test Scenario: basic_test ===
Starting game setup...
Player 1: Red Mage
Player 2: Blue Wizard

Turn 1:
- Player 1 draws card: Lightning Bolt
- Player 1 casts Lightning Bolt targeting Player 2
- Damage dealt: 3
- Player 2 life total: 17

Test Result: PASSED ✓
```

**Section sources**
- [test_game.py:1-100](file://simuladorMtg/test_game.py#L1-L100)

## Creating Your First Game

### Basic Game Setup

Creating a simple MTG game involves these fundamental steps:

#### Step 1: Initialize Players
```python
from src.simulator import GameSimulator

simulator = GameSimulator()
player1 = simulator.create_player("Player 1", "Red")
player2 = simulator.create_player("Player 2", "Blue")
```

#### Step 2: Create Decks
```python
deck1 = simulator.create_deck(player1, "Basic Red Deck")
deck2 = simulator.create_deck(player2, "Basic Blue Deck")
```

#### Step 3: Add Cards to Decks
```python
deck1.add_card("Lightning Bolt")
deck1.add_card("Fireball")
deck2.add_card("Counterspell")
deck2.add_card("Brainstorm")
```

#### Step 4: Start the Game
```python
game = simulator.start_game([player1, player2])
```

### Playing Cards

Once the game is running, you can play cards using the following approach:

```python
# Cast a spell
game.cast_spell("Lightning Bolt", target="Player 2")

# Attack with creatures
game.attack(creature="Grizzly Bears", target="Player 2")

# End turn
game.end_turn()
```

### Game Flow Control

The game follows standard MTG turn structure:
1. **Untap Phase**: Untap all permanents owned by active player
2. **Upkeep Phase**: Handle upkeep triggers
3. **Draw Phase**: Draw a card
4. **Main Phase**: Play lands, cast spells, activate abilities
5. **Combat Phase**: Declare attackers and blockers
6. **End Phase**: Handle end-of-turn effects

**Section sources**
- [simulator.py:1-150](file://simuladorMtg/src/simulator.py#L1-L150)
- [game_state.py:1-100](file://simuladorMtg/src/game_state.py#L1-L100)

## Adding Custom Cards

### Card Creation Process

The MTG Simulator provides a flexible system for creating custom cards. Each card has several components that define its behavior and properties.

#### Basic Card Structure

Every card consists of these essential elements:

| Component | Description | Example |
|-----------|-------------|---------|
| **Name** | Unique card identifier | "Lightning Bolt" |
| **Mana Cost** | Resources required to cast | "{R}" |
| **Card Type** | Classification (Creature, Instant, etc.) | "Instant" |
| **Text Box** | Card abilities and effects | "Deal 3 damage to any target" |
| **Power/Toughness** | For creatures only | "2/1" |
| **Rarity** | Common, Uncommon, Rare, Mythic | "Common" |

#### Creating a Simple Creature Card

```python
from src.card import Card

my_card = Card(
    name="Custom Dragon",
    mana_cost="{3}{R}",
    card_type="Creature - Dragon",
    power=4,
    toughness=4,
    text="Flying, Trample"
)
```

#### Creating a Spell Card

```python
fireball = Card(
    name="Fireball",
    mana_cost="{3}{R}",
    card_type="Instant",
    text="Deal 3 damage to any target"
)
```

### Card Abilities and Effects

Cards can have various abilities that trigger under specific conditions:

#### Static Abilities
Always active while the card is on the battlefield:
- Flying
- Haste
- Trample
- First Strike

#### Triggered Abilities
Activate when specific events occur:
- "Whenever this creature attacks..."
- "When this creature dies..."
- "At the beginning of your upkeep..."

#### Activated Abilities
Cost-based abilities players can use:
- "{T}: Draw a card"
- "{1}{R}: Deal 1 damage"

### Card Database Integration

Custom cards can be added to the card database for reuse:

```python
from src.cards_db import CardDatabase

db = CardDatabase()
db.register_card(my_card)
db.register_card(fireball)
```

### Advanced Card Mechanics

For complex cards, you can implement custom logic:

```python
class ConditionalCard(Card):
    def __init__(self, name, mana_cost, card_type, text, condition_func):
        super().__init__(name, mana_cost, card_type, text)
        self.condition = condition_func
    
    def can_be_played(self, game_state):
        return self.condition(game_state)
```

**Section sources**
- [card.py:1-200](file://simuladorMtg/src/card.py#L1-L200)
- [cards_db.py:1-150](file://simuladorMtg/src/cards_db.py#L1-L150)

## Understanding Basic Output

### Console Output Format

The MTG Simulator provides structured console output to help you understand game flow and debugging information.

#### Game State Output

When you request game state information, you'll see:

```
=== GAME STATE ===
Current Turn: 3
Active Player: Player 1
Phase: Main Phase

Player 1 (Red)
  Life Total: 20
  Hand: 3 cards
  Library: 25 cards
  Graveyard: 2 cards
  Battlefield: 
    - Grizzly Bears (2/1)
  
Player 2 (Blue)
  Life Total: 17
  Hand: 2 cards
  Library: 26 cards
  Graveyard: 1 card
  Battlefield: 
    - Island
```

#### Card Interaction Log

Each card interaction generates detailed logs:

```
[Turn 3, Main Phase]
Player 1 casts Lightning Bolt targeting Player 2
  Mana paid: {R}
  Target validated: Player 2
  Effect resolved: 3 damage dealt
  Player 2 life total updated: 17 -> 14
```

#### Error Messages

Error messages follow a consistent format:

```
ERROR: Invalid target for Lightning Bolt
  Card: Lightning Bolt
  Attempted Target: Player 1
  Reason: Lightning Bolt targets any target, but Player 1 is not a valid target in this context
  Suggestion: Try targeting an opponent or their permanent
```

### Debug Information

Enable debug mode for detailed diagnostic information:

```bash
python main.py --debug
```

Debug output includes:
- Memory usage statistics
- Performance metrics
- Rule validation details
- Card resolution traces
- Stack operations

**Section sources**
- [game_state.py:100-200](file://simuladorMtg/src/game_state.py#L100-L200)
- [rules_engine.py:1-100](file://simuladorMtg/src/rules_engine.py#L1-L100)

## Troubleshooting Guide

### Common Setup Issues

#### Python Version Compatibility

**Problem**: ImportError or syntax errors when running the simulator
**Solution**: Ensure you're using Python 3.6 or higher
```bash
python --version
```

#### File Path Issues

**Problem**: Cannot find card definitions or deck files
**Solution**: Verify file paths are correct and relative to the project root
```bash
cd simuladorMtg
python main.py --deck-file ./decks/my_deck.txt
```

#### Permission Errors

**Problem**: Permission denied when accessing certain directories
**Solution**: Check file permissions and ensure proper read/write access
```bash
chmod +x main.py
ls -la
```

### Runtime Errors

#### Card Validation Errors

**Problem**: Cards fail validation during game setup
**Solution**: Check card format and ensure all required fields are present
- Card names must be unique
- Mana costs must be properly formatted
- Card types must be valid MTG card types

#### Memory Issues

**Problem**: Out of memory errors with large decks or complex scenarios
**Solution**: Reduce deck size or enable garbage collection optimization
```bash
python -X faulthandler main.py
```

#### Performance Problems

**Problem**: Slow performance with many cards or complex interactions
**Solution**: 
- Use batch processing for large datasets
- Enable caching for frequently accessed cards
- Optimize card search algorithms

### Debugging Techniques

#### Enable Verbose Logging

```bash
python main.py --verbose --debug
```

#### Isolate Problem Areas

Create minimal test cases to identify specific issues:
```python
# Minimal reproduction case
from src.simulator import GameSimulator

sim = GameSimulator()
# Add only the problematic cards
# Test specific interactions
```

#### Check Card Database Integrity

```bash
python main.py --validate-cards
```

### Environment-Specific Issues

#### Windows Users

**Issue**: Line ending problems
**Solution**: Convert files to Unix line endings if needed
```bash
dos2unix *.py
```

#### macOS/Linux Users

**Issue**: Script execution permissions
**Solution**: Make scripts executable
```bash
chmod +x main.py
./main.py
```

**Section sources**
- [test_game.py:100-200](file://simuladorMtg/test_game.py#L100-L200)

## Project Structure Overview

### Directory Organization

The MTG Simulator follows a modular architecture with clear separation of concerns:

```
simuladorMtg/
├── main.py                 # Application entry point
├── test_game.py           # Test scenarios and examples
├── src/                   # Core source code
│   ├── card.py           # Card class and functionality
│   ├── cards_db.py       # Card database management
│   ├── game_state.py     # Game state management
│   ├── player.py         # Player class and logic
│   ├── rules_engine.py   # Rules validation and enforcement
│   └── simulator.py      # Main simulation engine
├── decks/                # Card deck definitions
└── Documentation files   # Various reference documents
```

### Core Modules

#### Card System (`card.py`)
Defines the fundamental card structure and behavior, including:
- Card properties and attributes
- Ability systems
- Card interactions
- Validation rules

#### Game State Management (`game_state.py`)
Handles the complete game state including:
- Player information and resources
- Battlefield state
- Card zones (hand, library, graveyard, etc.)
- Turn structure and phases

#### Rules Engine (`rules_engine.py`)
Implements MTG rules including:
- Legal move validation
- Target restrictions
- Timing rules
- Priority system

#### Simulation Engine (`simulator.py`)
Coordinates all game components:
- Game lifecycle management
- Event handling
- State synchronization
- Output generation

### Documentation Files

The project includes comprehensive documentation in Portuguese covering various aspects of the MTG rules and mechanics:

- **Arquitetura.md**: Architecture overview
- **Banco de Cartas.md**: Card database reference
- **Banco de Regras.md**: Rules database
- **Rules Engine.md**: Technical rules implementation

**Section sources**
- [Arquitetura.md:1-100](file://simuladorMtg/Arquitetura.md#L1-L100)
- [Rules Engine.md:1-50](file://simuladorMtg/Rules Engine.md#L1-L50)

## Conclusion

The MTG Simulator provides a robust, extensible platform for Magic: The Gathering simulation. With its pure Python implementation and comprehensive feature set, it serves both as a learning tool for understanding MTG mechanics and as a foundation for developing custom game scenarios.

### Key Takeaways

1. **Easy Setup**: No external dependencies required, just Python 3.6+
2. **Comprehensive Testing**: Built-in scenarios for learning and validation
3. **Extensible Design**: Modular architecture supporting custom cards and mechanics
4. **Rich Documentation**: Extensive reference materials and examples
5. **Cross-Platform**: Works on Windows, macOS, and Linux

### Next Steps

After completing this getting started guide, consider exploring:
- Advanced card creation with custom abilities
- Complex game scenarios and tournaments
- Performance optimization techniques
- Integration with external card databases
- Custom UI development

The MTG Simulator's flexible architecture makes it suitable for both casual experimentation and serious game development projects.