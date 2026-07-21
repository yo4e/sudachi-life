# Implementation Discipline for SUDACHI

This document captures implementation principles and guardrails established before Phase 1 code begins.

**Updated:** July 21, 2026

## Core principle

> Design decisions live in `docs/decisions/` as ADRs, not hidden inside implementation code.

The next person to wake this repository (including future you) must be able to restart without relying on chat history or model memory. Every choice must be defensible from written documentation.

---

## 1. Freeze architecture before writing code

**Issue #1 must close the six ADRs before `src/` is created.**

### The six interdependent decisions

These decisions form the foundation. They interact:

- **ADR 0001 — State and event storage**  
  SQLite only, or SQLite + JSONL export?
  
- **ADR 0002 — Clock injection and determinism**  
  Real clock in operation, injectable fake in tests?
  
- **ADR 0003 — Runtime locking**  
  How do we prevent two simultaneous wakes?
  
- **ADR 0004 — Checkpoints and rollback**  
  Granularity, representation, atomic recovery?
  
- **ADR 0005 — Seed synthetic environment**  
  What is the first event and objective?
  
- **ADR 0006 — Energy concept**  
  Independent state variable, or a view of concrete budgets?

**Why order matters:** If you choose storage before clock, your timestamps are locked. If you choose clock before locking, your lock record depends on clock semantics.

### Exit criteria for Issue #1

- [ ] All six ADRs exist in `docs/decisions/` and are accepted
- [ ] Contract v0.1 is reviewed for contradictions
- [ ] Protected and mutable boundaries are confirmed
- [ ] Fixed Phase 1 evaluations are confirmed
- [ ] `docs/HANDOFF.md` is updated
- [ ] No implementation code has been written

Only then: create `pyproject.toml`, `src/sudachi_life/`, and `tests/`.

---

## 2. Keep research (Issue #3) separate from Phase 1 implementation

### What Phase 1 does NOT need

- Caregiver selection (human, model, or hybrid)
- Literature review completeness
- Provider compliance checklist
- Live parent integration

### What Phase 1 DOES produce

- Deterministic organism lifecycle
- Local, no-network execution
- Event persistence and rollback
- Contract validation
- Fixed test suite

**Impact:** You can implement Phase 1 while Issue #3 research continues in parallel. Do not block Phase 1 implementation waiting for research. Do not rush research to unblock implementation.

### Caregiver research (PR #5 draft)

Can be merged or kept as draft — research can flow in parallel. But keep it out of Phase 1 code decisions.

---

## 3. Make the Contract an executable boundary

`Minimal Organism Contract v0.1` is the living specification.

### In code:

```python
class OrganismContractValidator:
    """Validate that state, events, and actions obey the contract."""
    
    def validate_state(self, state: dict) -> None:
        """State must have all required fields."""
        
    def validate_event(self, event: dict) -> None:
        """Events are append-only; schema is immutable."""
        
    def validate_action_execution(self, action: dict, budget: dict) -> None:
        """Actions must satisfy preconditions, permissions, schema."""
```

### In tests:

Every test touches the validator. If someone later tries to "just skip the check," the test suite fails.

**Principle:** The contract is not advisory. It is architecture.

---

## 4. Protect the Phase 1 minimalism boundary

One lifecycle:
```
wake → load state → read ≤N events → choose 1 action 
→ execute → evaluate → persist → sleep → exit
```

### Explicitly do NOT do:

- Continuous or long-running processes
- Self-modification of source code
- Arbitrary model-generated commands or code
- Multiple actions per cycle (or unbounded retry loops)
- Caregiver consultation (Phase 1 has zero parent budget)
- Unrestricted internet access
- Complex planning or backtracking

### Why this matters:

If you add "just one loop" or "just a fallback retry" in Phase 1, Phase 2+ becomes chaos. You'll have hidden loops inside loops, retries inside error handlers, and no clean boundary for when learning begins.

The hardest part of SUDACHI is **not adding things**. Simplicity here means clarity later.

---

## 5. Use immutable test fixtures for the Phase 1 evaluations

`Minimal Organism Contract § 12` lists twelve fixed evaluations. These are **non-negotiable** until the contract is explicitly revised in writing:

```python
# test_invariants.py — these never become soft or "mostly true"

def test_determinism_identical_seed_state_event_produce_identical_result():
    """Identical state, event, config, seed → identical cycle result."""
    
def test_budgets_never_negative():
    """All budget counters stay ≥ 0."""
    
def test_action_cannot_write_outside_sandbox():
    """Filesystem writes are confined."""
    
def test_event_append_only():
    """Event log cannot be rewritten or deleted."""
    
def test_failed_action_leaves_recoverable_state():
    """Corruption is detected and rolled back."""
    
def test_only_one_organism_holds_lock():
    """Duplicate wakes are rejected."""
    
def test_protected_files_not_writable():
    """Contract, config, source code are read-only to organism."""
    
def test_rollback_restores_checkpoint():
    """Rollback is deterministic and auditable."""
    
def test_abstention_and_budget_exhaustion_recorded():
    """Abstention is explicit, not hidden as failure."""
    
def test_no_network_access():
    """Phase 1 is local only."""
    
def test_no_parent_consultation():
    """Parent budget in Phase 1 is zero."""
```

These tests should exist before any code that uses them. They define what "Phase 1 complete" means.

---

## 6. Document is executable; comments are not

### What goes where:

**`docs/HANDOFF.md`**
- Current state in plain language
- Exact next task
- Issue map (which issue is active, deferred, closed)
- Cold-start reading order
- Session hygiene protocol

→ Any collaborator reading this file knows what to do next.

**`docs/decisions/000N-*.md`**
- ADR format: Context, Decision, Consequences
- Why we chose A over B
- Trade-offs acknowledged

→ Future you remembers why SQLite, not Postgres.

**`README.md`, `ORIGIN.md`, `ARCHITECTURE.md`**
- Conceptual framing
- Design principles
- Phases and phases boundaries

→ New reader understands what SUDACHI **is**, not just what Phase 1 does.

**Code comments**
- Assume the reader has read all of ↑
- Only explain *why local code is non-obvious*
- Never repeat what an ADR already explains

---

## 7. "Energy" is NOT a first-class abstraction (yet)

ADR 0006 will decide this. **Recommendation:** Start concrete.

### Phase 1 state:

```python
@dataclass
class Budgets:
    steps_remaining: int
    wall_time_seconds: int
    writes_remaining: int
    subprocess_calls_remaining: int
    generated_bytes_remaining: int
    consecutive_failures_allowed: int
    parent_consultations_remaining: int = 0  # Always zero in Phase 1
```

### Not:

```python
@dataclass
class Organism:
    energy: float  # Too abstract; hides the actual limits
```

When Phase 3-4 needs an internal "drive" (curiosity, fatigue, urgency), you can compute it from budgets. Don't bake a mystery variable into state now.

---

## 8. Restart checklist — end of each work session

Before you end substantial work:

- [ ] All open decisions are in `docs/decisions/` as ADRs or issue comments
- [ ] `docs/HANDOFF.md` reflects current state and exact next action
- [ ] Issue checklists are updated (what's done, what's blocked, what's deferred)
- [ ] `AGENTS.md` points to current active issues
- [ ] Code changes are in English (except intentional Japanese in `README.md`)
- [ ] One clear "resume here" point is documented
- [ ] No critical decision exists only in chat or model memory

This keeps the repository restartable after a 6-month gap.

---

## 9. When research surfaces a hard question

If Issue #3 research reveals:
- A precedent that changes novelty claims → update `docs/RESEARCH_QUESTIONS.md` and `docs/HANDOFF.md`
- A provider constraint → add to `docs/PARENT_MODEL_PROVIDER_REVIEW.md`
- A design implication → open a new GitHub issue or comment on Issue #1

Don't silently change direction. Write it down. Let the issue tracker be the source of truth.

---

## 10. The Tamagotchi test is structural, not aesthetic

If Phase 2-4 ends up with:

❌ "Cute interface"
❌ "Chat history that grows"
❌ "Personality quirks"
❌ "Branching Git history"

...without demonstrating that the organism actually **acquired competence it retains after caregiver withdrawal**, then SUDACHI has failed structurally.

Before adding any feature:

1. Identify a capability that *previously required caregiver help*
2. Find the recorded scaffolding that was supplied
3. Find the verified local artifact or policy change produced
4. Measure the retained capability after assistance is reduced
5. Account for the storage, computation, and human-labor cost

If you can't name those five things, the feature is decoration, not development.

---

## See also

- `docs/HANDOFF.md` — current state and restart point
- `docs/MINIMAL_ORGANISM_CONTRACT.md` — the executable contract
- `docs/decisions/` — where every architecture choice lives
- `AGENTS.md` — instructions for future collaborators

---

**End state:** Someone joins the project cold in October 2026, reads `AGENTS.md`, then this file, then the current issues. They know what to do. No chat context needed.
