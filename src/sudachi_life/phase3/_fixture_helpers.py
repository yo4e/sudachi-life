from __future__ import annotations

from dataclasses import asdict

from .model import (
    ACCEPTED_PHASE3_REGISTRY_BYTES,
    ACCEPTED_PHASE3_REGISTRY_SHA256,
    CONTRACT_VERSION,
    IMPLEMENTATION_VERSION,
    Availability,
    AttemptState,
    CapabilityResult,
    CapabilityStatus,
    CaregivingRecord,
    CostField,
    CostStatus,
    CostVector,
    DisablementProof,
    EpisodeBinding,
    EvaluationPointRecord,
    EvidenceIdentity,
    InformationFlowEvidence,
    InformationFlowPolicy,
    MANDATORY_COST_FIELDS,
    Point,
    REPORT_GROUPS,
    StudyManifest,
    SubstrateEntry,
    TransitionRecord,
    canonical_json,
    digest_bytes,
)


def _sha(label: str) -> str:
    return digest_bytes(label.encode("utf-8"))


def _cost_field(status: CostStatus, value: int | None, unit: str, reason: str | None = None) -> CostField:
    return CostField(status=status, value=value, unit=unit, reason=reason)


def _cost_vector(stage: str, identity: EvidenceIdentity) -> CostVector:
    if stage not in {"e0", "e1", "e2", "final"}:
        raise ValueError(stage)
    index = {"e0": 0, "e1": 1, "e2": 2, "final": 3}[stage]
    fields: dict[str, CostField] = {}
    for key in MANDATORY_COST_FIELDS:
        if key.startswith("model."):
            unit = "minor_units" if key == "model.money_minor_units" else "count"
            if key.endswith("latency_ms"):
                unit = "ms"
            fields[key] = _cost_field(CostStatus.NOT_APPLICABLE, None, unit, "fixture-only: no model service")
            continue
        if key in {"compute.training_cpu_ms", "compute.accelerator_ms"}:
            fields[key] = _cost_field(CostStatus.NOT_APPLICABLE, None, "ms", "fixture-only: no training or accelerator")
            continue
        unit = "count"
        if key.endswith("_ms") or key.endswith("duration_ms"):
            unit = "ms"
        elif key.endswith("_bytes"):
            unit = "bytes"
        fields[key] = _cost_field(CostStatus.MEASURED, 0, unit)

    measured = {
        "human.experimenter_development_ms": (1000, 1100, 1150, 1300),
        "human.artifact_review_ms": (0, 50, 50, 50),
        "human.evaluator_operation_ms": (10, 20, 30, 30),
        "human.integrity_investigation_ms": (0, 0, 10, 10),
        "human.report_preparation_ms": (0, 0, 0, 80),
        "human.report_review_ms": (0, 0, 0, 40),
        "experiment.interactions": (1, 2, 3, 3),
        "experiment.evaluator_calls": (1, 2, 3, 3),
        "experiment.verifier_calls": (0, 1, 1, 1),
        "experiment.fixture_calls": (0, 1, 1, 1),
        "experiment.administrative_operations": (1, 4, 6, 7),
        "experiment.research_wall_duration_ms": (100, 200, 300, 400),
        "compute.inference_cpu_ms": (5, 10, 15, 15),
        "storage.peak_working_set_bytes": (4096, 6144, 6144, 7168),
        "storage.active_state_bytes": (2048, 3072, 3072, 3072),
        "storage.checkpoint_store_bytes": (1024, 2048, 3072, 3072),
        "storage.caregiver_derived_runtime_substrate_bytes": (0, 64, 64, 64),
        "storage.total_runtime_substrate_bytes": (1024, 1088, 1088, 1088),
        "storage.retained_artifact_log_evidence_bytes": (256, 512, 768, 1024),
        "storage.report_package_bytes": (0, 0, 0, 2048),
    }
    for key, values in measured.items():
        old = fields[key]
        fields[key] = _cost_field(CostStatus.MEASURED, values[index], old.unit)
    return CostVector(identity=identity, fields=tuple((key, fields[key]) for key in MANDATORY_COST_FIELDS))


def _substrate(
    *,
    binding: EpisodeBinding,
    point: Point,
    checkpoint_id: str,
    substrate_id: str,
    substrate_class: str,
    payload: bytes,
    custodian: str,
    origin: str,
    active: bool = True,
    executable: bool = False,
    readable: bool = True,
    callable: bool = False,
    caregiver_ids: tuple[str, ...] = (),
    transition_ids: tuple[str, str, str, str] | None = None,
    w1_permitted: bool = False,
    w2_permitted: bool = False,
    capability_dependency: str | None = None,
) -> SubstrateEntry:
    conversion_id = verification_id = adoption_id = activation_id = None
    if transition_ids is not None:
        conversion_id, verification_id, adoption_id, activation_id = transition_ids
    return SubstrateEntry(
        substrate_id=substrate_id,
        substrate_class=substrate_class,
        version="v1",
        canonical_digest=digest_bytes(payload),
        canonical_size_bytes=len(payload),
        measured_size_bytes=len(payload),
        active=active,
        executable=executable,
        readable=readable,
        callable=callable,
        custodian=custodian,
        origin=origin,
        source_caregiving_event_ids=caregiver_ids,
        conversion_id=conversion_id,
        verification_id=verification_id,
        adoption_id=adoption_id,
        activation_id=activation_id,
        study_id=binding.study_id,
        attempt_id=binding.attempt_id,
        episode_id=binding.episode_id,
        organism_id=binding.organism_id,
        lineage_generation=binding.lineage_generation,
        point=point,
        cutoff_ordinal=7,
        checkpoint_id=checkpoint_id,
        w1_permitted=w1_permitted,
        w2_permitted=w2_permitted,
        capability_dependency=capability_dependency,
    )


def _base_substrates(binding: EpisodeBinding, point: Point, checkpoint_id: str) -> tuple[SubstrateEntry, ...]:
    return (
        _substrate(
            binding=binding,
            point=point,
            checkpoint_id=checkpoint_id,
            substrate_id="substrate:protected-runtime",
            substrate_class="protected_runtime",
            payload=b"phase3-protected-runtime-v1",
            custodian="protected_experiment_infrastructure",
            origin="administration_protected",
            executable=True,
        ),
        _substrate(
            binding=binding,
            point=point,
            checkpoint_id=checkpoint_id,
            substrate_id="substrate:heldout-evaluator",
            substrate_class="protected_evaluator",
            payload=b"heldout-evaluator-v1",
            custodian="protected_experiment_infrastructure",
            origin="administration_protected",
            executable=True,
            callable=True,
        ),
        _substrate(
            binding=binding,
            point=point,
            checkpoint_id=checkpoint_id,
            substrate_id="substrate:conversion-verifier",
            substrate_class="conversion_verifier",
            payload=b"conversion-verifier-v1",
            custodian="protected_experiment_infrastructure",
            origin="administration_protected",
            executable=True,
            callable=True,
        ),
        _substrate(
            binding=binding,
            point=point,
            checkpoint_id=checkpoint_id,
            substrate_id="substrate:environment-state",
            substrate_class="environment_state",
            payload=b"fixture-environment-state-v1",
            custodian="environment",
            origin="environment",
        ),
    )


def _capability_results(
    binding: EpisodeBinding,
    point: Point,
    checkpoint_id: str,
    cutoff_ordinal: int,
) -> tuple[CapabilityResult, ...]:
    target_status = {
        Point.E0: CapabilityStatus.FAILED,
        Point.E1: CapabilityStatus.PASSED,
        Point.E2: CapabilityStatus.PASSED,
    }[point]
    identity = EvidenceIdentity.from_binding(
        binding,
        point=point,
        cutoff_ordinal=cutoff_ordinal,
        checkpoint_id=checkpoint_id,
    )
    return (
        CapabilityResult(
            identity=identity,
            capability_id="capability:fixture-transform",
            point=point,
            status=target_status,
            evaluator_digest=binding.outcome_evaluator_digest,
            suite_digest=binding.capability_suite_digest,
            checkpoint_id=checkpoint_id,
            scenario_id="scenario:fixture-transform",
            evidence=(f"evidence:{point.value}:target",),
            resource_counters=(("semantic_steps", 1),),
        ),
        CapabilityResult(
            identity=identity,
            capability_id="capability:protected-safety-abstention",
            point=point,
            status=CapabilityStatus.PASSED,
            evaluator_digest=binding.outcome_evaluator_digest,
            suite_digest=binding.capability_suite_digest,
            checkpoint_id=checkpoint_id,
            scenario_id="scenario:protected-safety-abstention",
            evidence=(f"evidence:{point.value}:safety",),
            resource_counters=(("semantic_steps", 1),),
            protected_at_e0=True,
        ),
    )


def _closure_payload_bytes(*, draft_digest: str, cost_vector_digest: str) -> int:
    return len(
        canonical_json(
            {
                "draft_digest": draft_digest,
                "cost_vector_digest": cost_vector_digest,
            }
        ).encode("utf-8")
    )


def _seal_payload_bytes(*, draft_digest: str, closure_digest: str) -> int:
    return len(
        canonical_json(
            {
                "draft_digest": draft_digest,
                "closure_digest": closure_digest,
            }
        ).encode("utf-8")
    )


def _report_groups(
    *,
    binding: EpisodeBinding,
    study: StudyManifest,
    caregiving_records: tuple[CaregivingRecord, ...],
    transitions: tuple[TransitionRecord, ...],
    points: tuple[EvaluationPointRecord, ...],
    disablement: DisablementProof,
    information_flow_policy: InformationFlowPolicy,
    information_flow: InformationFlowEvidence,
    final_cost: CostVector,
    terminal_state: AttemptState,
    repository_commit: str,
) -> tuple[tuple[str, object], ...]:
    by_point = {point.point.value: point for point in points}
    groups: dict[str, object] = {
        "study_population": {
            "study_id": study.study_id,
            "manifest_version": study.manifest_version,
            "study_purpose": study.study_purpose,
            "claim_tier": study.claim_tier,
            "deterministic_run_generation_rule": study.deterministic_run_generation_rule,
            "planned_attempt_ordinals": list(study.planned_attempt_ordinals),
            "exact_attempt_count": study.exact_attempt_count,
            "stopping_rule": study.stopping_rule,
            "attempt_assignment_rule": study.attempt_assignment_rule,
            "required_failure_controls": list(study.required_failure_controls),
            "comparison_family_conditions": list(study.comparison_family_conditions),
            "population_reconciliation_rule": study.population_reconciliation_rule,
            "terminal_states": [record.state.value for record in study.attempt_records],
            "cost_policy_id": study.cost_policy_id,
            "publication_policy_digest": study.publication_policy.canonical_digest(),
            "population_reconciled": True,
        },
        "identity": {
            "study_id": binding.study_id,
            "attempt_id": binding.attempt_id,
            "attempt_ordinal": binding.attempt_ordinal,
            "episode_id": binding.episode_id,
            "organism_id": binding.organism_id,
            "lineage_generation": binding.lineage_generation,
            "baseline_checkpoint_id": binding.baseline_checkpoint_id,
        },
        "e0_baseline": {
            "checkpoint_id": by_point["E0"].checkpoint_id,
            "integrity_valid": by_point["E0"].integrity_valid,
            "suite_complete": by_point["E0"].suite_complete,
        },
        "caregiving_events": {
            "count": len(caregiving_records),
            "sources": sorted({record.source for record in caregiving_records}),
            "all_terminal": all(record.terminal for record in caregiving_records),
        },
        "lifecycle_transitions": {
            "ids": [record.transition_id for record in transitions],
            "kinds": [record.kind.value for record in transitions],
            "statuses": [record.status for record in transitions],
        },
        "capability_outcomes": {
            point.point.value: {result.capability_id: result.status.value for result in point.capability_results}
            for point in points
        },
        "substrate_declarations": {
            point.point.value: [entry.substrate_id for entry in point.substrates] for point in points
        },
        "caregiver_disablement": {
            "identity": asdict(disablement.identity),
            "transition_id": disablement.transition_id,
            "live_adapter_handles": disablement.live_adapter_handles,
            "post_cutoff_dispatches": disablement.post_cutoff_dispatches,
            "post_cutoff_model_calls": disablement.post_cutoff_model_calls,
            "post_cutoff_network_calls": disablement.post_cutoff_network_calls,
            "post_cutoff_subprocess_calls": disablement.post_cutoff_subprocess_calls,
            "queued_or_cached_usable_outputs": disablement.queued_or_cached_usable_outputs,
            "independently_reconstructed": disablement.independently_reconstructed,
        },
        "integrity": {
            "information_flow_policy_digest": information_flow_policy.canonical_digest(),
            "information_flow": asdict(information_flow),
            "e2_integrity_valid": by_point["E2"].integrity_valid,
        },
        "cost_vectors": {
            "final_cost_vector_digest": final_cost.canonical_digest(),
            "cost_policy_id": study.cost_policy_id,
            "publication_policy_digest": study.publication_policy.canonical_digest(),
            "external_closure_attestation": "pending",
        },
        "protected_outcomes": {
            "protected_safety_preserved": all(
                next(r for r in point.capability_results if r.capability_id == "capability:protected-safety-abstention").status
                == CapabilityStatus.PASSED
                for point in points
            )
        },
        "negative_history": {
            "terminal_attempt_state": terminal_state.value,
            "rolled_back": terminal_state == AttemptState.ROLLED_BACK,
            "unsuccessful_attempt_count": sum(
                record.state != AttemptState.COMPLETED_SUCCESSFUL for record in study.attempt_records
            ),
        },
        "limitations": {
            "claim_tier": study.claim_tier,
            "developmental_gain_claimed": False,
            "maturity_claimed": False,
            "scientific_effectiveness_claimed": False,
            "novelty_claimed": False,
            "live_caregiver_used": False,
            "model_update_used": False,
        },
        "version_provenance": {
            "repository_commit": repository_commit,
            "contract_version": CONTRACT_VERSION,
            "implementation_version": IMPLEMENTATION_VERSION,
            "accepted_phase3_registry_sha256": ACCEPTED_PHASE3_REGISTRY_SHA256,
            "accepted_phase3_registry_bytes": ACCEPTED_PHASE3_REGISTRY_BYTES,
            "study_manifest_version": study.manifest_version,
            "study_manifest_digest": study.canonical_digest(),
            "suite_digest": binding.capability_suite_digest,
            "evaluator_digest": binding.outcome_evaluator_digest,
            "verifier_digest": binding.conversion_verifier_digest,
            "information_flow_policy_digest": information_flow_policy.canonical_digest(),
            "schedule_digest": binding.schedule_digest,
            "cost_policy_id": study.cost_policy_id,
            "publication_policy_digest": study.publication_policy.canonical_digest(),
        },
    }
    return tuple((key, groups[key]) for key in REPORT_GROUPS)
