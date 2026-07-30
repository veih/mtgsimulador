# Event Propagation System

<cite>
**Referenced Files in This Document**
- [Banco de Eventos.md](file://Banco%20de%20Eventos.md)
- [Rules Engine.md](file://Rules%20Engine.md)
- [Arquitetura.md](file://Arquitetura.md)
- [simulator.py](file://simuladorMtg/src/simulator.py)
- [game_state.py](file://simuladorMtg/src/game_state.py)
- [rules_engine.py](file://simuladorMtg/src/rules_engine.py)
- [card.py](file://simuladorMtg/src/card.py)
- [player.py](file://simuladorMtg/src/player.py)
- [main.py](file://simuladorMtg/main.py)
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
This document explains the event propagation system used by the MTG simulator. It covers how events are created, registered, and dispatched across components; how priority and filtering work; and how the observer pattern enables triggered abilities, state change notifications, and inter-component communication. It also provides guidance on event bubbling, stopping propagation, asynchronous processing, performance for high-frequency events, and memory management for listeners.

## Project Structure
The event system spans documentation and code:
- Documentation files define event types, rules engine behavior, and architecture context.
- Python modules implement the runtime: game state, rules engine, card/player entities, and the main simulation loop.

```mermaid
graph TB
subgraph "Documentation"
A["Banco de Eventos.md"]
B["Rules Engine.md"]
C["Arquitetura.md"]
end
subgraph "Runtime Modules"
D["simulator.py"]
E["game_state.py"]
F["rules_engine.py"]
G["card.py"]
H["player.py"]
I["main.py"]
end
A --> F
B --> F
C --> D
D --> E
D --> F
F --> G
F --> H
I --> D
```

**Diagram sources**
- [Banco de Eventos.md](file://Banco%20de%20Eventos.md)
- [Rules Engine.md](file://Rules%20Engine.md)
- [Arquitetura.md](file://Arquitetura.md)
- [simulator.py](file://simuladorMtg/src/simulator.py)
- [game_state.py](file://simuladorMtg/src/game_state.py)
- [rules_engine.py](file://simuladorMtg/src/rules_engine.py)
- [card.py](file://simuladorMtg/src/card.py)
- [player.py](file://simuladorMtg/src/player.py)
- [main.py](file://simuladorMtg/main.py)

**Section sources**
- [Banco de Eventos.md](file://Banco%20de%20Eventos.md)
- [Rules Engine.md](file://Rules%20Engine.md)
- [Arquitetura.md](file://Arquitetura.md)
- [simulator.py](file://simuladorMtg/src/simulator.py)
- [game_state.py](file://simuladorMtg/src/game_state.py)
- [rules_engine.py](file://simuladorMtg/src/rules_engine.py)
- [card.py](file://simuladorMtg/src/card.py)
- [player.py](file://simuladorMtg/src/player.py)
- [main.py](file://simuladorMtg/main.py)

## Core Components
- Event Registry: Central store of event handlers with metadata (priority, filters).
- Event Bus/Dispatcher: Creates events, resolves matching handlers, applies priority and filters, and invokes handlers.
- Game State: Emits lifecycle and state-change events; owns global event registry.
- Rules Engine: Consumes events to apply game logic and may emit new events.
- Card and Player: Register component-specific handlers for ability triggers and player actions.
- Simulator/Main: Orchestrates tick or turn loops, dispatching events and handling errors.

Key responsibilities:
- Creation: Construct typed events with payload and source context.
- Registration: Subscribe handlers with optional priority and filter predicates.
- Dispatch: Resolve eligible handlers, sort by priority, apply filters, and invoke.
- Cleanup: Unsubscribe handlers to prevent leaks.

**Section sources**
- [Banco de Eventos.md](file://Banco%20de%20Eventos.md)
- [Rules Engine.md](file://Rules%20Engine.md)
- [game_state.py](file://simuladorMtg/src/game_state.py)
- [rules_engine.py](file://simuladorMtg/src/rules_engine.py)
- [card.py](file://simuladorMtg/src/card.py)
- [player.py](file://simuladorMtg/src/player.py)
- [simulator.py](file://simuladorMtg/src/simulator.py)

## Architecture Overview
The event system follows an observer pattern with a central dispatcher. Components subscribe to events they care about. The dispatcher ensures deterministic ordering via priorities and supports filtering to reduce unnecessary handler invocations.

```mermaid
sequenceDiagram
participant Main as "Main/Simulator"
participant GS as "Game State"
participant RE as "Rules Engine"
participant Card as "Card"
participant Player as "Player"
participant Bus as "Event Bus"
Main->>GS : "Start Turn / Action"
GS->>Bus : "Emit GameStateChange(event)"
Bus-->>RE : "Dispatch to subscribed handlers"
RE->>RE : "Evaluate rules and effects"
RE->>Bus : "Emit AbilityTrigger(event)"
Bus-->>Card : "Invoke card ability handler(s)"
Card->>Bus : "Emit CardStateChange(event)"
Bus-->>Player : "Invoke player update handler(s)"
Player-->>Main : "Acknowledge updates"
```

**Diagram sources**
- [simulator.py](file://simuladorMtg/src/simulator.py)
- [game_state.py](file://simuladorMtg/src/game_state.py)
- [rules_engine.py](file://simuladorMtg/src/rules_engine.py)
- [card.py](file://simuladorMtg/src/card.py)
- [player.py](file://simuladorMtg/src/player.py)

## Detailed Component Analysis

### Event Lifecycle: Creation to Cleanup
- Creation: Events are constructed with a type, payload, and optional source/context.
- Registration: Handlers register with the bus using a subscription API that accepts priority and filter functions.
- Dispatch: The bus collects all subscribers for an event type, sorts by priority, evaluates filters, and calls handlers in order.
- Bubbling and Stopping: Handlers can signal whether to continue bubbling to higher-level handlers or stop propagation.
- Cleanup: Subscriptions are removed when components are destroyed or no longer need to listen.

```mermaid
flowchart TD
Start(["Create Event"]) --> Emit["Emit to Event Bus"]
Emit --> Collect["Collect Subscribers"]
Collect --> Sort["Sort by Priority"]
Sort --> Filter{"Filter Pass?"}
Filter --> |No| Skip["Skip Handler"]
Filter --> |Yes| Invoke["Invoke Handler"]
Invoke --> StopCheck{"Stop Propagation?"}
StopCheck --> |Yes| End(["End"])
StopCheck --> |No| Next["Next Handler"]
Next --> Filter
Skip --> Next
```

**Diagram sources**
- [game_state.py](file://simuladorMtg/src/game_state.py)
- [rules_engine.py](file://simuladorMtg/src/rules_engine.py)
- [card.py](file://simuladorMtg/src/card.py)
- [player.py](file://simuladorMtg/src/player.py)

**Section sources**
- [Banco de Eventos.md](file://Banco%20de%20Eventos.md)
- [Rules Engine.md](file://Rules%20Engine.md)

### Event Types and Categories
- Game State Events: Turn start/end, phase changes, zone transitions.
- Ability Trigger Events: Abilities that respond to specific conditions.
- Player Action Events: Choices, payments, targeting decisions.
- Card State Events: Changes to card properties, counters, status.
- System Events: Errors, logging, diagnostics.

These categories guide where to subscribe and what payloads to expect.

**Section sources**
- [Banco de Eventos.md](file://Banco%20de%20Eventos.md)

### Observer Pattern Implementation
- Subscription Model: Components call a subscribe method with event type, handler function, optional priority, and optional filter predicate.
- Handler Invocation: The dispatcher iterates through sorted handlers, applies filters, and executes handlers synchronously unless explicitly queued.
- Context Passing: Events carry contextual data (source object, target, stack info) enabling precise filtering and safe updates.

```mermaid
classDiagram
class Event {
+string type
+object payload
+object source
+bool stopPropagation
}
class EventBus {
+subscribe(type, handler, priority, filter)
+unsubscribe(type, handler)
+emit(event)
-resolveHandlers(type) list
-applyFilters(handler, event) bool
}
class GameState {
+emit(event)
+registerGlobalSubscribers()
}
class RulesEngine {
+on(event) void
+triggerAbility(event) void
}
class Card {
+on(event) void
+handleTrigger(event) void
}
class Player {
+on(event) void
+updateState(event) void
}
EventBus --> Event : "dispatches"
GameState --> EventBus : "uses"
RulesEngine --> EventBus : "subscribes"
Card --> EventBus : "subscribes"
Player --> EventBus : "subscribes"
```

**Diagram sources**
- [game_state.py](file://simuladorMtg/src/game_state.py)
- [rules_engine.py](file://simuladorMtg/src/rules_engine.py)
- [card.py](file://simuladorMtg/src/card.py)
- [player.py](file://simuladorMtg/src/player.py)

**Section sources**
- [game_state.py](file://simuladorMtg/src/game_state.py)
- [rules_engine.py](file://simuladorMtg/src/rules_engine.py)
- [card.py](file://simuladorMtg/src/card.py)
- [player.py](file://simuladorMtg/src/player.py)

### Priority Handling and Filtering
- Priority: Handlers are ordered by numeric priority; lower values execute first. This allows core systems to run before UI or logging layers.
- Filtering: Each handler can declare a filter predicate that inspects the event payload and source to decide if it should run. Filters reduce overhead by avoiding unnecessary handler execution.
- Selection Strategy: The dispatcher collects all subscribers for an event type, sorts by priority, then applies filters sequentially.

```mermaid
flowchart TD
A["Handlers Collected"] --> B["Sort by Priority"]
B --> C["For each handler"]
C --> D{"Filter passes?"}
D --> |No| E["Skip"]
D --> |Yes| F["Invoke Handler"]
F --> G{"Stop propagation?"}
G --> |Yes| H["Terminate"]
G --> |No| C
```

**Diagram sources**
- [rules_engine.py](file://simuladorMtg/src/rules_engine.py)
- [game_state.py](file://simuladorMtg/src/game_state.py)

**Section sources**
- [Rules Engine.md](file://Rules%20Engine.md)
- [Banco de Eventos.md](file://Banco%20de%20Eventos.md)

### Event Bubbling and Stopping Propagation
- Bubbling: Handlers can be organized hierarchically (e.g., global, component-scoped). After a handler runs, control may bubble up to parent scopes.
- Stopping Propagation: A handler can set a flag to halt further bubbling, preventing downstream handlers from executing. This is useful for finalizing state or short-circuiting chains.

```mermaid
sequenceDiagram
participant Bus as "Event Bus"
participant Global as "Global Handler"
participant Comp as "Component Handler"
participant Child as "Child Handler"
Bus->>Global : "Invoke"
Global-->>Bus : "Continue"
Bus->>Comp : "Invoke"
Comp-->>Bus : "Stop Propagation"
Note over Bus,Child : "Child not invoked"
```

**Diagram sources**
- [game_state.py](file://simuladorMtg/src/game_state.py)
- [rules_engine.py](file://simuladorMtg/src/rules_engine.py)

**Section sources**
- [Banco de Eventos.md](file://Banco%20de%20Eventos.md)

### Asynchronous Event Processing
- Synchronous Dispatch: Default path invokes handlers immediately within the same call stack to maintain consistency and atomicity.
- Async Queuing: For heavy or blocking operations, handlers can enqueue tasks to a background queue processed after the current event completes. This avoids stalls during high-frequency events.
- Backpressure: The queue should enforce limits and drop or delay low-priority events under load.

```mermaid
flowchart TD
Start(["Emit Event"]) --> SyncPath{"Heavy Work?"}
SyncPath --> |No| SyncInvoke["Invoke Handler Now"]
SyncPath --> |Yes| Queue["Enqueue Task"]
Queue --> Process["Process Queue Later"]
SyncInvoke --> End(["Done"])
Process --> End
```

**Diagram sources**
- [simulator.py](file://simuladorMtg/src/simulator.py)
- [rules_engine.py](file://simuladorMtg/src/rules_engine.py)

**Section sources**
- [Rules Engine.md](file://Rules%20Engine.md)

### Error Handling Strategies
- Isolation: Wrap handler invocation in try/catch to isolate failures per handler without aborting the entire dispatch.
- Reporting: Log errors with full event context (type, payload, source) to aid debugging.
- Recovery: Optionally allow handlers to mark the event as handled and suppress further propagation.
- Diagnostics: Provide diagnostic events for error tracking and metrics collection.

```mermaid
flowchart TD
A["Invoke Handler"] --> Try{"Exception?"}
Try --> |No| Done["Proceed"]
Try --> |Yes| Catch["Catch and Log"]
Catch --> Decide{"Recoverable?"}
Decide --> |Yes| MarkHandled["Mark Handled"]
Decide --> |No| Abort["Abort Propagation"]
MarkHandled --> Done
Abort --> End(["Stop"])
```

**Diagram sources**
- [rules_engine.py](file://simuladorMtg/src/rules_engine.py)
- [game_state.py](file://simuladorMtg/src/game_state.py)

**Section sources**
- [Banco de Eventos.md](file://Banco%20de%20Eventos.md)

### Concrete Examples of Patterns
- Event Registration Patterns:
  - Global listener: Subscribe at game initialization for system-wide events.
  - Component-scoped listener: Subscribe when a card enters play; unsubscribe when it leaves.
  - Conditional listener: Use filter predicates to match specific payloads.
- Custom Event Handlers:
  - Implement a handler that inspects event payload and source to decide action.
  - Return or set flags to indicate stop propagation or handled status.
- Asynchronous Processing:
  - Enqueue long-running computations off the critical path.
  - Ensure idempotency and consistent state transitions.

[No sources needed since this section provides general guidance]

## Dependency Analysis
The event system couples components through subscriptions rather than direct references, improving modularity. However, careful design is required to avoid circular dependencies and ensure correct initialization order.

```mermaid
graph LR
GS["Game State"] --> BUS["Event Bus"]
RE["Rules Engine"] --> BUS
CARD["Card"] --> BUS
PLAYER["Player"] --> BUS
SIM["Simulator"] --> GS
MAIN["Main"] --> SIM
```

**Diagram sources**
- [game_state.py](file://simuladorMtg/src/game_state.py)
- [rules_engine.py](file://simuladorMtg/src/rules_engine.py)
- [card.py](file://simuladorMtg/src/card.py)
- [player.py](file://simuladorMtg/src/player.py)
- [simulator.py](file://simuladorMtg/src/simulator.py)
- [main.py](file://simuladorMtg/main.py)

**Section sources**
- [Arquitetura.md](file://Arquitetura.md)
- [simulator.py](file://simuladorMtg/src/simulator.py)
- [game_state.py](file://simuladorMtg/src/game_state.py)
- [rules_engine.py](file://simuladorMtg/src/rules_engine.py)
- [card.py](file://simuladorMtg/src/card.py)
- [player.py](file://simuladorMtg/src/player.py)
- [main.py](file://simuladorMtg/main.py)

## Performance Considerations
- High-Frequency Events:
  - Prefer lightweight handlers; defer heavy work to async queues.
  - Use efficient filters to minimize handler invocations.
  - Batch similar events when possible to reduce dispatch overhead.
- Memory Management:
  - Always unsubscribe handlers when components are destroyed.
  - Avoid capturing large objects in closures; use weak references where appropriate.
  - Periodically audit active subscriptions to detect leaks.
- Ordering and Determinism:
  - Maintain stable priority ordering to ensure reproducible behavior.
  - Avoid mutating shared state unpredictably within handlers.

[No sources needed since this section provides general guidance]

## Troubleshooting Guide
- Symptoms:
  - Handlers not firing: Check subscription registration, event type names, and filters.
  - Unexpected order: Verify priority values and sorting logic.
  - Performance drops: Identify heavy handlers and move them to async queues.
  - Memory growth: Audit subscriptions and ensure cleanup paths are executed.
- Debugging Steps:
  - Enable diagnostic events to log dispatch sequences.
  - Inspect event payloads and sources for correctness.
  - Temporarily disable handlers to isolate problematic ones.
- Common Fixes:
  - Correct event type strings and payload structures.
  - Adjust priorities to achieve desired execution order.
  - Add explicit unsubscribe calls in teardown routines.

**Section sources**
- [Rules Engine.md](file://Rules%20Engine.md)
- [Banco de Eventos.md](file://Banco%20de%20Eventos.md)

## Conclusion
The event propagation system provides a flexible, decoupled mechanism for inter-component communication in the MTG simulator. By leveraging priorities, filters, and optional asynchronous processing, it supports complex interactions such as triggered abilities and state change notifications while maintaining performance and determinism. Proper subscription management and error isolation are essential to keep the system robust and scalable.