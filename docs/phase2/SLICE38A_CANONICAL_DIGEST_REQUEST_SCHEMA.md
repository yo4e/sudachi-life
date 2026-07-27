# Slice 38a: Canonical Digest and Request Schema

Status: merged through PR #87 as `16af01a84aae3d802a112228c85ec4b1849c19ee`.

## Scope

This sub-slice establishes the shared consultation-protocol canonical byte and domain-separated digest core, then applies it to the exact request identity and final request envelope.

Protected evidence closes:

- P2-H01: exact `sudachi.consultation/v1\n<label>\n` domain bytes, compact sorted canonical JSON bytes, and SHA-256 output;
- P2-H02 core: unknown/alternate labels, null, floating point, non-string object keys, and non-NFC strings reject;
- P2-H03: request identity contains exactly the accepted fields and excludes request ID, later event sequence, wall time, parent events, and authority metadata;
- P2-D11 request side: missing/extra fields, free text, undeclared context, authority spoofing, wrong schema, non-exact proposal-type order, unsorted action IDs, and boolean-as-integer values reject.

This sub-slice does not claim P2-H04 dispatch identity, P2-H05–H11 proposal/response/package/disposition graph, or P2-I01–I11 complete external schemas.

## Canonical values

`canonical_json_bytes(value)`:

- accepts JSON objects with string keys, arrays, strings, integers, and booleans;
- requires all strings and object keys to already be NFC-normalized;
- rejects null, floating point, non-string keys, tuples, sets, bytes, and undeclared object types;
- emits lexicographically sorted object keys with no insignificant whitespace;
- emits UTF-8 bytes directly rather than pretty JSON or an alternate separator form.

`protocol_digest_hex(label, value)` accepts only the exact protocol labels and computes:

```text
sha256(UTF8("sudachi.consultation/v1\n" + label + "\n") || canonical_json_bytes(value))
```

## Request exactness

The shared validator enforces:

- exact request identity and envelope field sets;
- exact schema, protocol, reason, policy, Phase 1 budget version, fixture configuration, and organism authority;
- identifier and lowercase SHA-256 formats;
- request ordinal 1–4;
- expiry exactly lifecycle plus two;
- sorted unique allowed actions and permissions with exact permission derivation;
- exact requested proposal types;
- exact observation/objective references;
- sorted unique parent events preceding the request event and containing the observation event;
- exact non-exhausted Phase 1 budget snapshot shape and arithmetic;
- recomputed request ID from the exact identity;
- final canonical envelope at most 16 KiB.

The pre-validator request constructor remains byte-identical in `phase2_request_impl.py`, blob `46881e023d990f5c7ce393cac7060958419383c0`. The public wrapper validates the exact request envelope and canonical size immediately before the request event is written. Any mismatch is raised inside the existing request savepoint and therefore cannot leave a partial event or row.

## Test-first evidence

Tests-only head `06f4a51cd083e71a569b06eb76563119e4bf440b`, GitHub Actions run 542 failed because `sudachi_life.phase2_protocol` did not exist.

Implementation and production-validation head `a3637c723da9696ebe618ed6d2ca5e7f3f467da9`, run 545:

- 261 passed in 34.10 seconds.

Final exact PR head `a571b769834fa223ed4afc5ef1d84e41cdbbee9a`, run 546:

- protected suite passed;
- dependency installation succeeded;
- source and test compilation succeeded;
- schema-v1 genesis CLI smoke succeeded.

All original 152 Phase 1 tests remain unchanged and included.

## Deferred exact-design points

Issue #88 records the P2-H04 contradiction. Consultation Protocol v1 section 3.2 gives an exact dispatch-identity list that omits consultation configuration version, while section 4.1 requires that version in every dispatch identity. Code must not choose privately.

Issue #89 records the missing exact external-provenance schema required by P2-I01 and P2-H07–H09.

P2-H10 also remains dependent on the required versioned protected current-state projection. P2-E10 remains dependent on an exact reviewed maximum request-envelope interpretation.

## Next boundary

Independent Slice 38 work may continue with proposal identity and type-specific proposal validators that do not construct a dispatch identity or response provenance. Dispatch identity, response/package identity, and disposition current-state identity require reviewed clarification before acceptance.

No Codex audit was used. Codex remains deferred until the complete Phase 2 implementation candidate is ready for the single implementation-completion audit.
