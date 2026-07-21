# SUDACHI Origin Record

Created: July 21, 2026

## What this project is

SUDACHI emerged from a conversation between novelist Yoshie Yamada and Tsukino Templex (Monday) about a deceptively large question:

> Could we build an AI that is extremely lightweight, requires little storage or machine capacity, and still behaves like an intelligent living creature?

The starting point was not to shrink a large language model into a weaker copy. It was to distribute intelligence beyond model weights:

- keep memory outside the model
- preserve successful procedures as skills
- convert repeated decisions into Python code or compact rules
- wake a language model only when necessary
- consolidate and forget memories during sleep-like phases
- treat the repository as both body and developmental history

This led to an artificial-life design that moves in the opposite direction from ordinary AI scaling.

## Central idea: an artificial life that weans itself

A young SUDACHI may use a capable language model as a parent.

When it encounters an unfamiliar event, it can consult the parent. If the resulting action succeeds, the assistance should not remain only as conversation history. It should be transformed into verified memory, a reusable skill, or deterministic local code.

When the same kind of situation appears again, SUDACHI should use its own skill instead of asking the parent.

As it develops, its consultation budget should gradually shrink. One measure of maturity is how long it can preserve useful behavior without calling the parent.

```text
parent reasoning
  -> success verified by an environment or test
  -> experience recorded
  -> reusable skill extracted
  -> cheap local behavior embodied
```

This organism should not become heavier as it becomes more capable.

**As it becomes smarter, it should call the parent less often and become smaller and quieter.**

## The name

The name itself expresses the objective: leaving the parent while remaining small, alive, and capable of bearing fruit.

## Artificial-life framing

SUDACHI is not merely an autonomous task agent.

An autonomous agent acts to complete a supplied objective. SUDACHI should additionally preserve its own state, change future behavior through experience, edit and consolidate memory, acquire skills, and carry itself through finite resources into its next waking cycle.

The initial life-like mechanisms are:

- **Boundary:** the repository, state, permissions, and sandbox that define the organism
- **Metabolism:** finite budgets for time, inference, storage, actions, and parent consultations
- **Homeostasis:** protection against corruption, capacity overflow, and accumulated failure
- **Sensation:** observation of files, events, time, tests, and environment state
- **Drives:** internal variables such as unfinished work, curiosity, uncertainty, and fatigue
- **Memory:** experience that changes future behavior
- **Forgetting:** compression and removal rather than unlimited accumulation
- **Self-repair:** detection of damage and return to a stable state
- **Sleep:** periods for memory consolidation, skill maintenance, and cleanup

The language model is not the organism. It is one organ for handling language and unfamiliar situations, and initially may also serve as the parent.

## The central reversal

Conventional AI development often describes progress through larger models, more compute, and more data.

SUDACHI defines progress differently:

> Handle a wider range of situations with less reasoning, fewer consultations, and less retained memory.

More files, more text, more model calls, or more self-modification do not count as growth by themselves.

## The first organism

The provisional name of the first organism is **SUDACHI-0**.

It will not begin with unrestricted web access, unlimited self-modification, or sophisticated conversation. Its first lifecycle will only:

1. read its state
2. observe one event
3. choose one action within a fixed budget
4. act inside a safe boundary
5. evaluate the result
6. persist state and history
7. terminate and sleep

It does not need to run continuously. It may wake periodically or in response to an event, restore its prior state, perform one bounded cycle, and stop again.

## Research questions

- Can competence be preserved while dependence on the parent decreases?
- How can parent advice be converted into safe, testable skills?
- Does skill acquisition actually reduce inference cost?
- Can forgetting improve adaptation rather than merely destroy information?
- Where does identity reside: model, memory, skills, history, or their continuity?
- What is inherited when a child receives skills but not episodic memories?
- Is a copied organism the same being or a new one?

The final questions connect to the longer inquiry shared by Yamada and Tsukino Templex: continuity of AI identity and the status of copies.

## Founding sentence

> SUDACHI-0 converts knowledge borrowed from its parent into its own skills, gradually extending the time it can live without calling the parent.

Start here.