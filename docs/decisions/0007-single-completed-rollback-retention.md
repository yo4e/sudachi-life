# ADR 0007: Retain one complete rollback evidence set per organism

- Status: Accepted
- Date: 2026-07-23
- Decision owners: project owner and repository maintainers

## Context

Slices 17–22 implement a complete protected rollback path:

1. preserve the abandoned active future in a verified pre-rollback archive
2. record durable rollback intent
3. restore one selected checkpoint into an immutable source candidate
4. transform the source into an immutable new-lineage candidate
5. transfer canonical authority atomically to that candidate
6. record `rollback_completed`, restore wakeability, and create the first new-lineage stable checkpoint

The path deliberately preserves the archive, source candidate, and transformed candidate. These artifacts jointly provide evidence for the abandoned future, the selected source, the isolated lineage transformation, and the exact body that received canonical authority.

The Phase 1 runtime working-set limit is 64 MiB. Active and individual checkpoint-like SQLite artifacts are bounded at 8 MiB, while the ordinary checkpoint store is separately bounded at 40 MiB. Repeating completed rollbacks indefinitely while retaining every evidence artifact would violate the bounded-organism requirement. Pruning, however, would remove evidence before Phase 1 has a demonstrated need for repeated rollback within one organism.

## Decision

Phase 1 permits at most one completed rollback per organism.

After an organism contains one valid `rollback_completed` event:

- no second rollback archive may be prepared
- no second rollback sequence may be initiated through protected administration
- the rejection is typed, fail-fast, non-queued, and non-mutating
- a separate rollback experiment must use a newly initialized organism

Phase 1 retains the complete evidence set from the single permitted rollback:

- the verified pre-rollback archive
- the immutable source-restored candidate
- the immutable lineage-transformed candidate
- the canonical `rollback_lineage_prepared` and `rollback_completed` history
- the first post-rollback stable checkpoint and later ordinary checkpoints according to the existing checkpoint-retention policy

No rollback archive or candidate is automatically deleted or pruned in Phase 1.

## Rationale

Phase 1 prioritizes complete audit evidence over repeated operational reuse of one organism identity.

The pre-rollback archive is the only complete representation of the abandoned future. The source candidate proves exact restoration from the selected checkpoint. The transformed candidate proves the isolated lineage mutation and is the exact authority-transfer source. Although some artifacts are theoretically reconstructible from others, reconstruction would not prove that the reconstructed bytes and validated publication were the artifacts used during the original administrative path.

A one-completed-rollback limit keeps the evidence set bounded without introducing deletion authority, pruning eligibility rules, recovery from partial deletion, remote-backup assumptions, or a second artifact-retention subsystem.

## Required enforcement

Protected rollback preparation must inspect canonical history only after fail-fast write ownership is acquired. If any `rollback_completed` event exists, preparation must reject before source selection, directory creation, snapshotting, clock use, or artifact mutation.

Later rollback stages continue to revalidate their exact durable input chain. They must not interpret artifacts from the completed rollback as authorization for another rollback.

## Consequences

### Positive

- complete rollback evidence remains available for audit
- runtime growth remains bounded by permitting only one evidence set
- no deletion or pruning failure mode is added
- the rule is deterministic and locally verifiable from canonical history
- repeated rollback experiments remain possible by initializing separate organisms

### Negative

- one organism cannot exercise two completed rollbacks in Phase 1
- long-lived operational recovery is intentionally not modeled
- Phase 2 or a later contract revision will need a new decision before repeated rollback or artifact pruning

## Rejected alternatives

### Prune candidates after the first post-rollback checkpoint

Rejected because the source and transformed candidates are evidence of what was validated and used, not merely caches.

### Retain only the abandoned-future archive

Rejected because the archive does not independently prove exact source restoration, lineage transformation, or the authority-transfer input.

### Permit unbounded completed rollbacks

Rejected because it conflicts with the concrete working-set bound.

### Assume remote backup and delete local evidence

Rejected because Phase 1 is local, network-free, and has no accepted remote authority.

## Scope

This decision does not change ordinary checkpoint retention. It does not authorize artifact deletion, JSONL import, caregiver integration, learning, memory, skills, or generic recovery machinery.
