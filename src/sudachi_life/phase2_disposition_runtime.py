"""Public disposition-wake runtime with exact row-link validation."""

from __future__ import annotations

from . import phase2_disposition_runtime_impl as _impl


class _RowLinkedEnvelope(dict):
    def __init__(
        self,
        value: dict[str, object],
        *,
        organism_id: object,
        lineage_generation: object,
    ) -> None:
        super().__init__(value)
        self._organism_id = organism_id
        self._lineage_generation = lineage_generation

    def __missing__(self, key: str):
        if key == "organism_id":
            return self._organism_id
        if key == "lineage_generation":
            return self._lineage_generation
        raise KeyError(key)


_original_validate_proposal_envelope = _impl.validate_proposal_envelope
_original_validate_response_envelope = _impl.validate_response_envelope


def _validate_proposal_envelope(value, *, request_envelope, fixture_case_id):
    envelope = _original_validate_proposal_envelope(
        value,
        request_envelope=request_envelope,
        fixture_case_id=fixture_case_id,
    )
    return _RowLinkedEnvelope(
        envelope,
        organism_id=request_envelope["organism_id"],
        lineage_generation=request_envelope["lineage_generation"],
    )


def _validate_response_envelope(
    value,
    *,
    request_envelope,
    dispatch_envelope,
    proposal_envelopes,
):
    envelope = _original_validate_response_envelope(
        value,
        request_envelope=request_envelope,
        dispatch_envelope=dispatch_envelope,
        proposal_envelopes=proposal_envelopes,
    )
    return _RowLinkedEnvelope(
        envelope,
        organism_id=request_envelope["organism_id"],
        lineage_generation=request_envelope["lineage_generation"],
    )


_impl.validate_proposal_envelope = _validate_proposal_envelope
_impl.validate_response_envelope = _validate_response_envelope

for _name, _value in vars(_impl).items():
    if not _name.startswith("__"):
        globals()[_name] = _value

__all__ = list(_impl.__all__)
