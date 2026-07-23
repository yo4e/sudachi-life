# Slice 35 — Authority provenance

Status: **Implemented and verified**

Contract evaluation: **41 — administrative actions are distinguishable from organism actions**

## Boundary

Phase 1 already stored a `source` string on canonical events and used operation-specific result types and immutable artifact manifests for administrative work. The remaining gap was that:

- the externally callable administrative enqueue API accepted a caller-supplied source without validating its authority category
- CLI reports, including reports for read-only or intentionally event-free administrative operations, did not carry one uniform protected authority category and source

Slice 35 closes those gaps without changing the event schema, action registry, evaluator, checkpoint semantics, rollback semantics, or lifecycle transaction.

## Production correction

`src/sudachi_life/authority.py` defines the only Phase 1 authority categories:

- `organism`
- `administration`

A valid source has one exact namespace form:

```text
organism:<protected-name>
administration:<protected-name>
```

`classify_authority_source(...)` rejects empty, unknown, malformed, and cross-category values. `build_authority_report(...)` adds non-spoofable `authority_category` and `authority_source` fields and rejects payloads that attempt to supply those protected fields themselves.

`enqueue_garden_tick(...)` now validates its administrative source before database ownership, canonical reads, clock use, inbox insertion, or event append. The validation is repeated at the event append helper.

The CLI maps each current operation to one exact authority source. The bounded wake report is organism provenance. Initialization, enqueue, status, maintenance, checkpoint repair, event export, and every rollback stage are administrative provenance.

## Event and non-event distinction

Canonical organism lifecycle records remain sourced from:

```text
organism:phase1-fixed-policy
```

Administrative canonical records retain their operation-specific `administration:*` sources.

Operations that intentionally create no canonical event remain event-free. This includes read-only inspection and reporting, rollback archive preparation, source-candidate publication, active replacement, duplicate/idempotent report paths, and pre-authority rejection. Their CLI reports now identify the administrative authority category and exact operation source without inventing false canonical history.

Python operation result types remain unchanged and operation-specific. Authority report decoration occurs at the public CLI report boundary.

## Protected proof

`tests/test_authority_provenance.py` proves:

- empty, unknown, and organism-category enqueue sources reject before clock use and preserve exact canonical authority rows and status
- a real genesis, administrative enqueue, organism wake, and administrative checkpoint path produces both protected categories in canonical history
- every observed event and inbox source classifies under an exact protected namespace
- all fourteen current CLI paths have one exact protected category and source
- read-only status CLI output carries administrative provenance without canonical mutation
- all literal production `organism:*` and `administration:*` sources are syntactically valid and classifiable
- report publication rejects unknown, cross-category, and payload-spoofed authority

Existing exact CLI report tests for maintenance inspection, rollback preparation, source-candidate publication, and candidate transformation now require the new provenance fields.

## Validation history

GitHub Actions run 313 compiled and ran the suite, then failed four existing exact CLI JSON assertions because the intended authority fields were new. All other protected tests passed. No production behavior failed.

The four assertions were strengthened to require the operation-specific authority fields. GitHub Actions run 317 then passed:

- clean Python 3.12 editable installation
- source and test compilation
- **142 protected tests in 7.25 seconds**
- genesis CLI smoke test

## Result

All 41 fixed Minimal Organism Contract v0.2 evaluations now have complete protected coverage. Slice 35 is the final Phase 1 implementation slice.

Phase 2 is not authorized by this completion. Caregiver-neutral consultation plumbing requires a new explicit reviewed scope and must preserve the complete Phase 1 zero-caregiver baseline.
