"""Narrow Phase 1 authority provenance for canonical sources and reports."""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Mapping

from .errors import SudachiError

ORGANISM = "organism"
ADMINISTRATION = "administration"

_AUTHORITY_SOURCE_RE = re.compile(
    r"^(?P<category>organism|administration):"
    r"(?P<name>[a-z0-9][a-z0-9._-]{0,127})$"
)
_PROTECTED_REPORT_KEYS = frozenset({"authority_category", "authority_source"})


class AuthorityProvenanceError(SudachiError):
    """An authority source or report attempted to cross or hide its category."""


@dataclass(frozen=True, slots=True)
class AuthorityProvenance:
    category: str
    source: str


def classify_authority_source(
    source: str,
    *,
    expected_category: str | None = None,
) -> AuthorityProvenance:
    """Validate one exact Phase 1 authority source and optional expected category."""

    if expected_category not in {None, ORGANISM, ADMINISTRATION}:
        raise AuthorityProvenanceError(
            f"unknown expected authority category: {expected_category!r}"
        )
    if not isinstance(source, str):
        raise AuthorityProvenanceError("authority source must be a string")
    match = _AUTHORITY_SOURCE_RE.fullmatch(source)
    if match is None:
        raise AuthorityProvenanceError(
            "authority source must use a protected organism: or administration: namespace"
        )
    category = match.group("category")
    if expected_category is not None and category != expected_category:
        raise AuthorityProvenanceError(
            f"authority source category mismatch: expected {expected_category}, found {category}"
        )
    return AuthorityProvenance(category=category, source=source)


def build_authority_report(
    payload: Mapping[str, object],
    *,
    source: str,
    expected_category: str,
) -> dict[str, object]:
    """Add validated, non-spoofable authority provenance to one published report."""

    overlap = _PROTECTED_REPORT_KEYS.intersection(payload)
    if overlap:
        raise AuthorityProvenanceError(
            "report payload attempted to supply protected authority fields: "
            + ", ".join(sorted(overlap))
        )
    provenance = classify_authority_source(
        source,
        expected_category=expected_category,
    )
    return {
        "authority_category": provenance.category,
        "authority_source": provenance.source,
        **dict(payload),
    }
