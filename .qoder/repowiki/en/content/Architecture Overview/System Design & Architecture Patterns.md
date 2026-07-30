# System Design & Architecture Patterns

<cite>
**Referenced Files in This Document**
- [main.py](file://simuladorMtg/main.py)
- [simulator.py](file://simuladorMtg/src/simulator.py)
- [game_state.py](file://simuladorMtg/src/game_state.py)
- [rules_engine.py](file://simuladorMtg/src/rules_engine.py)
- [card.py](file://simuladorMtg/src/card.py)
- [player.py](file://simuladorMtg/src/player.py)
- [cards_db.py](file://simuladorMtg/src/cards_db.py)
- [Arquitetura.md](file://simuladorMtg/Arquitetura.md)
- [Rules Engine.md](file://simuladorMtg/Rules Engine.md)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Project Structure](#project-structure)
3. [Core Components](#core-components)
4. [Architecture Overview](#architecture-overview)
5. [Detailed Component Analysis](#detailed-component-analysis)
6. [Dependency Analysis](#dependency-analysis)
7. [Performance Considerations](#performance-considerations)
8. [Troubleshooting Guide](#troubleshooting-guide)
9. [Conclusion](#conclusion)

## Introduction

The MTG Simulator is a comprehensive implementation of Magic: The Gathering game mechanics using Python's object-oriented programming paradigm. The system follows established design patterns including Model-View-Controller (MVC), Observer pattern for event handling, Factory pattern for card creation, and State pattern for turn management. This architecture ensures maintainability, extensibility, and clear separation of concerns across all game components.

The simulator provides a complete game engine that handles card interactions, player actions, rule enforcement, and state transitions while maintaining high performance and code organization through modular design principles.

## Project Structure

The MTG Simulator follows a well-organized modular architecture with clear separation between core game logic, data management, and user interface components:

```mermaid
graph TB
subgraph "Application Layer"
Main[main.py]
Test[test_game.py]
end
subgraph "Core Game Logic"
Simulator[simulator.py]
GameState[game_state.py]
RulesEngine[rules_engine.py]
end
subgraph "Game Entities"
Card[card.py]
Player[player.py]
CardsDB[cards_db.py]
end
subgraph "Data Management"
Decks[decks/]
Docs[Documentation/]
end
Main --> Simulator
Simulator --> GameState
Simulator --> RulesEngine
Simulator --> CardsDB
GameState --> Card
GameState --> Player
RulesEngine --> Card
CardsDB --> Card
```

**Diagram sources**
- [main.py:1-50](file://simuladorMtg/main.py#L1-L50)
- [simulator.py:1-100](file://simuladorMtg/src/simulator.py#L1-L100)
- [game_state.py:1-100](file://simuladorMtg/src/game_state.py#L1-L100)

**Section sources**
- [Arquitetura.md](file://simuladorMtg/Arquitetura.md)
- [Rules Engine.md](file://simuladorMtg/Rules Engine.md)

## Core Components

### Model-View-Controller Architecture

The system implements a clean MVC separation where:

- **Model Layer**: Handles game state, card definitions, and data persistence
- **View Layer**: Manages user interface and display logic  
- **Controller Layer**: Orchestrates game flow and user interactions

### Key Architectural Patterns

#### Observer Pattern Implementation
Event-driven architecture enables loose coupling between components through publish-subscribe messaging:

```mermaid
sequenceDiagram
participant Game as Game State
participant Rules as Rules Engine
participant Players as Player System
participant Events as Event System
Game->>Events : Publish CardPlayed(card)
Events->>Rules : Notify Rules Engine
Rules->>Rules : Validate Card Play
Rules-->>Events : Return Validation Result
Events->>Players : Notify All Players
Players-->>Events : Acknowledge Event
Events-->>Game : Complete Event Cycle
```

**Diagram sources**
- [game_state.py:1-150](file://simuladorMtg/src/game_state.py#L1-L150)
- [rules_engine.py:1-100](file://simuladorMtg/src/rules_engine.py#L1-L100)

#### Factory Pattern for Card Creation
Card instantiation follows the Factory pattern to handle different card types and abilities:

```mermaid
classDiagram
class CardFactory {
+createCard(cardType, properties) Card
+validateCardProperties(properties) bool
+getCardTemplate(cardType) dict
}
class Card {
+string name
+string type
+int manaCost
+list abilities
+activateAbility() void
+resolveEffect() void
}
class CreatureCard {
+int power
+int toughness
+list creatureAbilities
}
class SpellCard {
+string target
+list spellEffects
}
CardFactory --> Card : creates
Card <|-- CreatureCard
Card <|-- SpellCard
```

**Diagram sources**
- [card.py:1-200](file://simuladorMtg/src/card.py#L1-L200)
- [cards_db.py:1-100](file://simuladorMtg/src/cards_db.py#L1-L100)

#### State Pattern for Turn Management
Turn progression uses the State pattern to manage game phases and player turns:

```mermaid
stateDiagram-v2
[*] --> UntapPhase
UntapPhase --> UpkeepPhase : "untap complete"
UpkeepPhase --> DrawPhase : "upkeep complete"
DrawPhase --> MainPhase : "draw complete"
MainPhase --> CombatPhase : "attack declared"
CombatPhase --> MainPhase : "combat complete"
MainPhase --> EndPhase : "end turn"
EndPhase --> UntapPhase : "turn complete"
UntapPhase --> [*] : "game over"
UpkeepPhase --> [*] : "game over"
DrawPhase --> [*] : "game over"
MainPhase --> [*] : "game over"
CombatPhase --> [*] : "game over"
EndPhase --> [*] : "game over"
```

**Diagram sources**
- [game_state.py:1-200](file://simuladorMtg/src/game_state.py#L1-L200)

**Section sources**
- [simulator.py:1-150](file://simuladorMtg/src/simulator.py#L1-L150)
- [game_state.py:1-200](file://simuladorMtg/src/game_state.py#L1-L200)
- [card.py:1-200](file://simuladorMtg/src/card.py#L1-L200)

## Architecture Overview

The MTG Simulator employs a layered architecture with clear separation of responsibilities:

```mermaid
graph TD
subgraph "Presentation Layer"
UI[User Interface]
CLI[Command Line Interface]
end
subgraph "Application Layer"
Controller[Game Controller]
Validator[Input Validator]
Formatter[Output Formatter]
end
subgraph "Domain Layer"
GameState[Game State Manager]
RulesEngine[Rules Engine]
CardSystem[Card System]
PlayerSystem[Player System]
end
subgraph "Infrastructure Layer"
Database[Card Database]
EventSystem[Event System]
Logger[System Logger]
end
UI --> Controller
CLI --> Controller
Controller --> GameState
Controller --> RulesEngine
Controller --> CardSystem
Controller --> PlayerSystem
GameState --> EventSystem
RulesEngine --> Database
CardSystem --> Database
PlayerSystem --> EventSystem
```

**Diagram sources**
- [main.py:1-100](file://simuladorMtg/main.py#L1-L100)
- [simulator.py:1-200](file://simuladorMtg/src/simulator.py#L1-L200)

### Technical Decisions

#### Python Standard Library Usage
The system leverages Python's standard library for maximum portability:
- `collections` for data structures and containers
- `enum` for type-safe enumerations
- `dataclasses` for immutable data objects
- `logging` for system diagnostics
- `json` for configuration and save files

#### Modular File Organization
Each component resides in dedicated modules following single responsibility principle:
- Separation of concerns between game logic and presentation
- Clear interfaces between components
- Dependency injection for testability

**Section sources**
- [Arquitetura.md](file://simuladorMtg/Arquitetura.md)
- [Rules Engine.md](file://simuladorMtg/Rules Engine.md)

## Detailed Component Analysis

### Game State Manager

The Game State Manager serves as the central coordinator for all game operations, maintaining consistency across the entire game session:

```mermaid
classDiagram
class GameStateManager {
-dict players
-dict board
-dict graveyard
-dict stack
-CurrentTurn currentTurn
-GamePhase currentPhase
+initializeGame(players) void
+processTurn() void
+executeAction(action) bool
+checkWinConditions() bool
+saveGameState() dict
+loadGameState(data) void
}
class Player {
+string id
+int lifeTotal
+list hand
+list deck
+list graveyard
+list library
+playCard(card) bool
+castSpell(spell) bool
+attack(target) bool
}
class Board {
+list creatures
+list enchantments
+list artifacts
+list lands
+placeCard(card, zone) bool
+removeCard(cardId) bool
+searchCards(query) list
}
GameStateManager --> Player : manages
GameStateManager --> Board : maintains
Player --> Board : interacts with
```

**Diagram sources**
- [game_state.py:1-300](file://simuladorMtg/src/game_state.py#L1-L300)
- [player.py:1-200](file://simuladorMtg/src/player.py#L1-L200)

### Rules Engine

The Rules Engine enforces Magic: The Gathering rules and validates all game actions:

```mermaid
flowchart TD
Start([Action Received]) --> Parse["Parse Action"]
Parse --> ValidateContext["Validate Context"]
ValidateContext --> CheckRules["Check Game Rules"]
CheckRules --> RuleValid{"Rules Valid?"}
RuleValid --> |No| Reject["Reject Action"]
RuleValid --> |Yes| Execute["Execute Action"]
Execute --> UpdateState["Update Game State"]
UpdateState --> TriggerEffects["Trigger Effects"]
TriggerEffects --> ResolveStack["Resolve Stack"]
ResolveStack --> CheckWin["Check Win Conditions"]
CheckWin --> Success{"Win Condition Met?"}
Success --> |Yes| EndGame["End Game"]
Success --> |No| Complete["Complete Action"]
Reject --> End([Action Rejected])
EndGame --> End
Complete --> End
```

**Diagram sources**
- [rules_engine.py:1-250](file://simuladorMtg/src/rules_engine.py#L1-L250)

### Card System

The Card System implements the Factory pattern for creating and managing different card types:

```mermaid
classDiagram
class Card {
<<abstract>>
+string name
+string cardType
+int manaCost
+list keywords
+activateAbility() bool
+resolveEffect() void
+canBePlayed() bool
}
class CreatureCard {
+int power
+int toughness
+list creatureAbilities
+declareAttack() bool
+block(attacker) bool
}
class InstantSpell {
+string targetType
+list effects
+targetSelection() list
}
class SorcerySpell {
+string effectType
+list targets
+resolve() void
}
class LandCard {
+list manaTypes
+tapMana(manaType) void
+untap() void
}
Card <|-- CreatureCard
Card <|-- InstantSpell
Card <|-- SorcerySpell
Card <|-- LandCard
```

**Diagram sources**
- [card.py:1-300](file://simuladorMtg/src/card.py#L1-L300)

### Event System

The Event System implements the Observer pattern for decoupled communication:

```mermaid
sequenceDiagram
participant Source as Event Source
participant Bus as Event Bus
participant Handler1 as Handler 1
participant Handler2 as Handler 2
participant Handler3 as Handler 3
Source->>Bus : Emit(event, data)
Bus->>Handler1 : Handle(event, data)
Handler1-->>Bus : Processed
Bus->>Handler2 : Handle(event, data)
Handler2-->>Bus : Processed
Bus->>Handler3 : Handle(event, data)
Handler3-->>Bus : Processed
Bus-->>Source : Event Complete
```

**Diagram sources**
- [game_state.py:1-200](file://simuladorMtg/src/game_state.py#L1-L200)

**Section sources**
- [game_state.py:1-300](file://simuladorMtg/src/game_state.py#L1-L300)
- [rules_engine.py:1-250](file://simuladorMtg/src/rules_engine.py#L1-L250)
- [card.py:1-300](file://simuladorMtg/src/card.py#L1-L300)

## Dependency Analysis

The system exhibits low coupling and high cohesion through careful dependency management:

```mermaid
graph LR
subgraph "High Cohesion Modules"
A[GameState] --> B[Player]
A --> C[Board]
D[RulesEngine] --> E[Card]
F[CardFactory] --> E
end
subgraph "Low Coupling Interfaces"
G[EventBus] -.-> H[All Components]
I[Database] -.-> J[Card System]
K[Logger] -.-> L[All Components]
end
M[Main] --> N[Simulator]
N --> A
N --> D
N --> F
```

**Diagram sources**
- [simulator.py:1-150](file://simuladorMtg/src/simulator.py#L1-L150)
- [game_state.py:1-200](file://simuladorMtg/src/game_state.py#L1-L200)

### Dependency Relationships

- **Loose Coupling**: Components communicate through well-defined interfaces
- **Single Responsibility**: Each module has one clear purpose
- **Dependency Inversion**: High-level modules depend on abstractions
- **Interface Segregation**: Small, focused interfaces per component

**Section sources**
- [simulator.py:1-200](file://simuladorMtg/src/simulator.py#L1-L200)

## Performance Considerations

### Memory Management
- Efficient card object pooling to reduce garbage collection overhead
- Lazy loading of card database entries
- Optimized board state representation using hash maps

### Algorithmic Efficiency
- O(1) card lookup using dictionary-based indexing
- Amortized O(log n) sorting for priority queues
- Constant-time ability resolution through pre-computed tables

### Scalability Features
- Asynchronous event processing for large games
- Incremental state updates to minimize memory allocation
- Configurable simulation speed for different use cases

## Troubleshooting Guide

### Common Issues and Solutions

#### Game State Inconsistencies
- Verify all state transitions are atomic
- Implement state validation hooks at critical points
- Use snapshot testing for complex scenarios

#### Performance Bottlenecks
- Profile card ability resolution paths
- Monitor memory usage during long games
- Optimize frequently called methods

#### Event Handling Problems
- Ensure proper event listener registration
- Implement dead letter queues for failed events
- Add comprehensive event logging

### Debugging Tools
- Built-in game state inspection utilities
- Step-by-step action execution mode
- Comprehensive logging framework

## Conclusion

The MTG Simulator demonstrates effective application of object-oriented design patterns to create a maintainable and extensible game engine. The combination of MVC architecture, Observer pattern for events, Factory pattern for card creation, and State pattern for turn management results in a system that is both powerful and easy to understand.

The modular design allows for easy extension of game mechanics, while the clear separation of concerns ensures that changes in one area don't inadvertently affect others. The use of Python's standard library provides excellent portability and reduces external dependencies.

This architecture serves as a solid foundation for future enhancements, including network multiplayer support, advanced AI opponents, and integration with external card databases.