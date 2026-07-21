"""Minimal command-line interface for the Phase 1 foundation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Sequence

from .errors import SudachiError
from .organism import get_status, initialize_organism


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="sudachi")
    parser.add_argument(
        "--runtime-dir",
        type=Path,
        default=Path("runtime"),
        help="root directory containing organism runtime state",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="initialize one SUDACHI-0 organism")
    init_parser.add_argument("organism_id")
    init_parser.add_argument("--json", action="store_true", dest="as_json")

    status_parser = subparsers.add_parser("status", help="read canonical organism status")
    status_parser.add_argument("organism_id")
    status_parser.add_argument("--json", action="store_true", dest="as_json")

    return parser


def _format_human(status: dict[str, object]) -> str:
    lines = [
        f"organism_id: {status['organism_id']}",
        f"status: {status['status']}",
        f"contract_version: {status['contract_version']}",
        f"schema_version: {status['schema_version']}",
        f"environment_version: {status['environment_version']}",
        f"lineage_generation: {status['lineage_generation']}",
        f"lifecycle_number: {status['lifecycle_number']}",
        f"checkpoint_pending: {str(status['checkpoint_pending']).lower()}",
        f"latest_stable_checkpoint_id: {status['latest_stable_checkpoint_id']}",
        f"latest_stable_event_sequence: {status['latest_stable_event_sequence']}",
        f"event_count: {status['event_count']}",
        f"environment_step: {status['environment_step']}",
        f"objective_complete: {str(status['objective_complete']).lower()}",
        f"water_units: {status['water_units']}",
        f"harvested_fruit: {status['harvested_fruit']}",
    ]
    for plot in status["plots"]:  # type: ignore[index]
        lines.append(
            "plot: "
            f"{plot['plot_id']} stage={plot['stage']} moisture={plot['moisture']} fruit={plot['fruit']}"
        )
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "init":
            status, checkpoint = initialize_organism(args.runtime_dir, args.organism_id)
            payload = status.as_dict()
            payload["genesis_checkpoint_id"] = checkpoint.checkpoint_id
        elif args.command == "status":
            payload = get_status(args.runtime_dir, args.organism_id).as_dict()
        else:  # pragma: no cover - argparse enforces the command set.
            parser.error(f"unknown command: {args.command}")
            return 2
    except SudachiError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.as_json:
        print(json.dumps(payload, sort_keys=True, separators=(",", ":")))
    else:
        print(_format_human(payload))
    return 0
