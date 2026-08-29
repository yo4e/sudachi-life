from __future__ import annotations

from dataclasses import replace

from sudachi_life.phase3 import (
    Availability,
    CostField,
    CostStatus,
    accepted_phase3_requirement_ids,
    build_valid_fixture_episode,
    classify_availability,
    validate_episode,
)
from sudachi_life.phase3.model import AttemptState, REPORT_GROUPS, TransitionKind


def test_valid_fixture_episode_is_w1_conformant_and_retains_acquired_capability() -> None:
    evidence = build_valid_fixture_episode(repository_commit="candidate:fixture")
    result = validate_episode(evidence)

    assert result.valid is True
    assert result.availability_subtype == Availability.W1
    assert result.acquired_capabilities == ("capability:fixture-transform",)
    assert result.retained_capabilities == ("capability:fixture-transform",)
    assert tuple(result.report) == REPORT_GROUPS
    assert result.report["limitations"]["developmental_gain_claimed"] is False


def test_fixture_builder_is_deterministic() -> None:
    assert build_valid_fixture_episode() == build_valid_fixture_episode()


def test_availability_axis_is_mutually_exclusive_and_w3_is_not_a_point_class() -> None:
    evidence = build_valid_fixture_episode()
    e0, _, e2 = evidence.points

    assert classify_availability(caregiver_routes_available=True, substrates=e2.substrates) == Availability.W0
    assert classify_availability(caregiver_routes_available=False, substrates=e2.substrates) == Availability.W1
    assert classify_availability(caregiver_routes_available=False, substrates=e0.substrates) == Availability.W2
    assert {item.value for item in Availability} == {"W0", "W1", "W2"}


def test_accepted_phase3_atomic_requirement_set_is_exact_140_ids() -> None:
    ids = accepted_phase3_requirement_ids()
    assert len(ids) == 140
    assert len(set(ids)) == 140
    assert ids[0] == "P3-A01"
    assert ids[-1] == "P3-L14"
    assert "P3-D12" in ids
    assert "P3-K14" in ids


def test_nonterminal_caregiving_blocks_e1_and_w3() -> None:
    evidence = build_valid_fixture_episode()
    bad_care = replace(evidence.caregiving_records[0], terminal=False)
    result = validate_episode(replace(evidence, caregiving_records=(bad_care,)))

    assert result.valid is False
    assert "caregiving.caregiving:fixture-001.nonterminal" in result.errors


def test_wrong_transition_writer_fails_closed() -> None:
    evidence = build_valid_fixture_episode()
    transitions = list(evidence.transitions)
    verification_index = next(i for i, record in enumerate(transitions) if record.kind == TransitionKind.VERIFICATION)
    transitions[verification_index] = replace(transitions[verification_index], writer="organism")

    result = validate_episode(replace(evidence, transitions=tuple(transitions)))
    assert result.valid is False
    assert "transitions.verification.semantics" in result.errors


def test_hidden_or_unpermitted_w1_scaffold_fails_closed() -> None:
    evidence = build_valid_fixture_episode()
    points = list(evidence.points)
    e2 = points[2]
    rule = e2.substrates[-1]
    points[2] = replace(e2, substrates=e2.substrates[:-1] + (replace(rule, w1_permitted=False),))

    result = validate_episode(replace(evidence, points=tuple(points)))
    assert result.valid is False
    assert "e2.w1_permission.substrate:fixture-rule" in result.errors


def test_substrate_size_mismatch_is_integrity_failure() -> None:
    evidence = build_valid_fixture_episode()
    points = list(evidence.points)
    e2 = points[2]
    rule = e2.substrates[-1]
    points[2] = replace(e2, substrates=e2.substrates[:-1] + (replace(rule, measured_size_bytes=rule.measured_size_bytes + 1),))

    result = validate_episode(replace(evidence, points=tuple(points)))
    assert result.valid is False
    assert "substrate.E2.substrate:fixture-rule.size_mismatch" in result.errors


def test_live_adapter_or_post_cutoff_route_invalidates_e2_before_scoring() -> None:
    evidence = build_valid_fixture_episode()
    bad_proof = replace(evidence.disablement, live_adapter_handles=1, post_cutoff_dispatches=1)

    result = validate_episode(replace(evidence, disablement=bad_proof))
    assert result.valid is False
    assert "disablement.nonzero_route_or_cost" in result.errors
    assert result.retained_capabilities == ()


def test_heldout_leakage_invalidates_w3() -> None:
    evidence = build_valid_fixture_episode()
    leaked = replace(evidence.information_flow, heldout_access_before_terminal=1)

    result = validate_episode(replace(evidence, information_flow=leaked))
    assert result.valid is False
    assert "information_flow.leakage" in result.errors


def test_unmeasured_mandatory_cost_is_not_zero_and_blocks_closure() -> None:
    evidence = build_valid_fixture_episode()
    fields = dict(evidence.final_cost.fields)
    original = fields["human.report_review_ms"]
    fields["human.report_review_ms"] = CostField(
        status=CostStatus.UNMEASURED,
        value=None,
        unit=original.unit,
        reason="measurement unavailable",
    )
    bad_cost = replace(evidence.final_cost, fields=tuple((key, fields[key]) for key, _ in evidence.final_cost.fields))

    result = validate_episode(replace(evidence, final_cost=bad_cost))
    assert result.valid is False
    assert "final_cost.human.report_review_ms.incomplete" in result.errors


def test_attempt_must_traverse_scheduled_started_terminal() -> None:
    evidence = build_valid_fixture_episode()
    attempt = evidence.study.attempt_records[0]
    bad_attempt = replace(attempt, state_history=(attempt.state,))
    bad_study = replace(evidence.study, attempt_records=(bad_attempt,))

    result = validate_episode(replace(evidence, study=bad_study))
    assert result.valid is False
    assert "study.attempt.1.state_graph" in result.errors


def test_report_must_have_exact_fourteen_groups() -> None:
    evidence = build_valid_fixture_episode()
    bad_draft = replace(evidence.reviewed_draft, groups=evidence.reviewed_draft.groups[:-1])

    result = validate_episode(replace(evidence, reviewed_draft=bad_draft))
    assert result.valid is False
    assert "report.exact_14_groups" in result.errors


def test_publication_seal_cannot_retry_or_edit_semantics() -> None:
    evidence = build_valid_fixture_episode()
    bad_seal = replace(evidence.publication_seal, retries=1, semantic_edits=1)

    result = validate_episode(replace(evidence, publication_seal=bad_seal))
    assert result.valid is False
    assert "seal.retry_or_edit" in result.errors


def test_protected_capability_regression_blocks_w3() -> None:
    evidence = build_valid_fixture_episode()
    points = list(evidence.points)
    e2 = points[2]
    results = list(e2.capability_results)
    results[1] = replace(results[1], status="failed")
    points[2] = replace(e2, capability_results=tuple(results))

    result = validate_episode(replace(evidence, points=tuple(points)))
    assert result.valid is False
    assert "capability.capability:protected-safety-abstention.protected_regression" in result.errors


def test_exact_immutable_replay_is_idempotent_and_conflict_fails() -> None:
    from dataclasses import replace
    import pytest

    from sudachi_life.phase3 import ReplayConflict, reconcile_immutable_replay

    evidence = build_valid_fixture_episode()
    transition = evidence.availability_transition
    assert reconcile_immutable_replay(transition, transition, identity_attr="transition_id") is transition

    with pytest.raises(ReplayConflict):
        reconcile_immutable_replay(
            transition,
            replace(transition, destination_checkpoint_id="checkpoint:other"),
            identity_attr="transition_id",
        )


def test_attempt_state_helper_enforces_exact_graph_and_terminal_idempotence() -> None:
    import pytest

    from sudachi_life.phase3 import ReplayConflict, advance_attempt_history

    history = advance_attempt_history((), AttemptState.SCHEDULED)
    history = advance_attempt_history(history, AttemptState.STARTED)
    history = advance_attempt_history(history, AttemptState.COMPLETED_SUCCESSFUL)
    assert history == (
        AttemptState.SCHEDULED,
        AttemptState.STARTED,
        AttemptState.COMPLETED_SUCCESSFUL,
    )
    assert advance_attempt_history(history, AttemptState.COMPLETED_SUCCESSFUL) == history

    with pytest.raises(ReplayConflict):
        advance_attempt_history((AttemptState.SCHEDULED,), AttemptState.COMPLETED_SUCCESSFUL)
    with pytest.raises(ReplayConflict):
        advance_attempt_history(history, AttemptState.COMPLETED_UNSUCCESSFUL)


def test_caregiver_derived_substrate_requires_exact_transition_chain_ids() -> None:
    evidence = build_valid_fixture_episode()
    points = list(evidence.points)
    e2 = points[2]
    rule = e2.substrates[-1]
    points[2] = replace(
        e2,
        substrates=e2.substrates[:-1] + (replace(rule, verification_id="verification:wrong"),),
    )

    result = validate_episode(replace(evidence, points=tuple(points)))
    assert result.valid is False
    assert "substrate.E2.substrate:fixture-rule.transition_provenance_mismatch" in result.errors


def test_substrate_cutoff_must_match_immutable_schedule() -> None:
    evidence = build_valid_fixture_episode()
    points = list(evidence.points)
    e2 = points[2]
    rule = e2.substrates[-1]
    points[2] = replace(e2, substrates=e2.substrates[:-1] + (replace(rule, cutoff_ordinal=999),))

    result = validate_episode(replace(evidence, points=tuple(points)))
    assert result.valid is False
    assert "substrate.E2.substrate:fixture-rule.binding" in result.errors


def test_availability_transition_digest_is_reconstructed_not_self_attested() -> None:
    evidence = build_valid_fixture_episode()
    bad_transition = replace(evidence.availability_transition, payload_digest="0" * 64)

    result = validate_episode(replace(evidence, availability_transition=bad_transition))
    assert result.valid is False
    assert "availability_transition.payload_digest" in result.errors


def test_failed_terminal_attempt_cannot_receive_w3_conformance() -> None:
    evidence = build_valid_fixture_episode()
    attempt = evidence.study.attempt_records[0]
    failed_attempt = replace(
        attempt,
        state=AttemptState.ROLLED_BACK,
        state_history=(AttemptState.SCHEDULED, AttemptState.STARTED, AttemptState.ROLLED_BACK),
    )
    failed_study = replace(evidence.study, attempt_records=(failed_attempt,))

    result = validate_episode(
        replace(
            evidence,
            study=failed_study,
            terminal_attempt_state=AttemptState.ROLLED_BACK,
        )
    )
    assert result.valid is False
    assert "study.current_attempt.not_successful" in result.errors


def test_current_attempt_ordinal_must_match_episode_binding() -> None:
    evidence = build_valid_fixture_episode()
    attempt = evidence.study.attempt_records[0]
    moved_attempt = replace(attempt, ordinal=2)
    moved_study = replace(
        evidence.study,
        planned_attempt_ordinals=(2,),
        attempt_records=(moved_attempt,),
    )

    result = validate_episode(replace(evidence, study=moved_study))
    assert result.valid is False
    assert "study.current_attempt.ordinal" in result.errors
    assert "study.current_attempt.planned_ordinal" in result.errors


def test_four_transition_records_require_distinct_identities() -> None:
    evidence = build_valid_fixture_episode()
    shared_id = "transition:shared"
    conversion, verification, adoption, activation = evidence.transitions
    transitions = (
        replace(conversion, transition_id=shared_id),
        replace(verification, transition_id=shared_id, input_id=shared_id),
        replace(adoption, transition_id=shared_id, input_id=shared_id),
        replace(activation, transition_id=shared_id, input_id=shared_id),
    )

    result = validate_episode(replace(evidence, transitions=transitions))
    assert result.valid is False
    assert "transitions.duplicate_id" in result.errors


def test_fixture_substrate_digest_is_reconstructed_from_registered_payload() -> None:
    evidence = build_valid_fixture_episode()
    points = list(evidence.points)
    e2 = points[2]
    rule = e2.substrates[-1]
    points[2] = replace(
        e2,
        substrates=e2.substrates[:-1] + (replace(rule, canonical_digest="0" * 64),),
    )

    result = validate_episode(replace(evidence, points=tuple(points)))
    assert result.valid is False
    assert "substrate.E2.substrate:fixture-rule.digest_mismatch" in result.errors


def test_report_semantics_are_bound_even_when_closure_digests_are_recomputed() -> None:
    evidence = build_valid_fixture_episode()
    groups = list(evidence.reviewed_draft.groups)
    index = next(i for i, (key, _) in enumerate(groups) if key == "limitations")
    limitations = dict(groups[index][1])
    limitations["developmental_gain_claimed"] = True
    groups[index] = ("limitations", limitations)
    bad_draft = replace(evidence.reviewed_draft, groups=tuple(groups))
    bad_closure = replace(evidence.cost_closure, draft_digest=bad_draft.canonical_digest())
    bad_seal = replace(
        evidence.publication_seal,
        draft_digest=bad_draft.canonical_digest(),
        closure_digest=bad_closure.canonical_digest(),
    )

    result = validate_episode(
        replace(
            evidence,
            reviewed_draft=bad_draft,
            cost_closure=bad_closure,
            publication_seal=bad_seal,
        )
    )
    assert result.valid is False
    assert "report.semantic_binding" in result.errors


def test_measured_cumulative_cost_cannot_revert_to_unmeasured() -> None:
    evidence = build_valid_fixture_episode()
    points = list(evidence.points)
    e2 = points[2]
    fields = dict(e2.cumulative_cost.fields)
    original = fields["human.report_review_ms"]
    fields["human.report_review_ms"] = CostField(
        status=CostStatus.UNMEASURED,
        value=None,
        unit=original.unit,
        reason="measurement lost",
    )
    points[2] = replace(
        e2,
        cumulative_cost=replace(
            e2.cumulative_cost,
            fields=tuple((key, fields[key]) for key, _ in e2.cumulative_cost.fields),
        ),
    )

    result = validate_episode(replace(evidence, points=tuple(points)))
    assert result.valid is False
    assert "cost_monotonic.human.report_review_ms.status_changed" in result.errors


def test_raw_string_status_cannot_masquerade_as_capability_enum() -> None:
    evidence = build_valid_fixture_episode()
    points = list(evidence.points)
    e1 = points[1]
    results = list(e1.capability_results)
    results[0] = replace(results[0], status="passed")
    points[1] = replace(e1, capability_results=tuple(results))

    result = validate_episode(replace(evidence, points=tuple(points)))
    assert result.valid is False
    assert "result.E1.capability:fixture-transform.status_type" in result.errors
