"""Bounded command-line interface for SUDACHI-0."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Sequence

from .checkpoint_repair import repair_pending_checkpoint_registration
from .errors import SudachiError
from .event_export import export_stable_events
from .inbox import GARDEN_TICK_EVENT_TYPE, enqueue_garden_tick
from .lifecycle import perform_garden_wake
from .maintenance import inspect_maintenance
from .maintenance_recovery import clear_maintenance
from .organism import get_status, initialize_organism
from .paths import OrganismPaths
from .rollback import prepare_rollback_archive
from .rollback_candidate import build_restore_candidate
from .rollback_intent import begin_rollback
from .rollback_transform import transform_restore_candidate


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

    enqueue_parser = subparsers.add_parser("enqueue", help="enqueue one synthetic input")
    enqueue_parser.add_argument("organism_id")
    enqueue_parser.add_argument("event_type", choices=[GARDEN_TICK_EVENT_TYPE])
    enqueue_parser.add_argument("--id", required=True, dest="external_event_id")
    enqueue_parser.add_argument("--json", action="store_true", dest="as_json")

    wake_parser = subparsers.add_parser("wake", help="perform one bounded Phase 1 wake")
    wake_parser.add_argument("organism_id")
    wake_parser.add_argument("--seed", type=int, required=True)
    wake_parser.add_argument("--json", action="store_true", dest="as_json")

    status_parser = subparsers.add_parser("status", help="read canonical organism status")
    status_parser.add_argument("organism_id")
    status_parser.add_argument("--json", action="store_true", dest="as_json")

    maintenance_parser = subparsers.add_parser(
        "maintenance", help="perform explicit administrative maintenance operations"
    )
    maintenance_subparsers = maintenance_parser.add_subparsers(
        dest="maintenance_command", required=True
    )
    inspect_parser = maintenance_subparsers.add_parser(
        "inspect", help="inspect stable maintenance state without mutation"
    )
    inspect_parser.add_argument("organism_id")
    inspect_parser.add_argument("--json", action="store_true", dest="as_json")

    clear_parser = maintenance_subparsers.add_parser(
        "clear", help="clear protected maintenance through an audited transaction"
    )
    clear_parser.add_argument("organism_id")
    clear_parser.add_argument("--reason", required=True, dest="recovery_reason")
    clear_parser.add_argument("--json", action="store_true", dest="as_json")

    checkpoint_parser = subparsers.add_parser(
        "checkpoint", help="perform explicit administrative checkpoint operations"
    )
    checkpoint_subparsers = checkpoint_parser.add_subparsers(
        dest="checkpoint_command", required=True
    )
    repair_pending_parser = checkpoint_subparsers.add_parser(
        "repair-pending",
        help="register exactly one valid published pending checkpoint",
    )
    repair_pending_parser.add_argument("organism_id")
    repair_pending_parser.add_argument(
        "--json", action="store_true", dest="as_json"
    )

    export_parser = subparsers.add_parser(
        "export", help="create explicit non-canonical administrative exports"
    )
    export_subparsers = export_parser.add_subparsers(
        dest="export_command", required=True
    )
    export_events_parser = export_subparsers.add_parser(
        "events", help="export events through one registered stable boundary"
    )
    export_events_parser.add_argument("organism_id")
    export_events_parser.add_argument(
        "--event-sequence", type=int, required=True, dest="event_sequence"
    )
    export_events_parser.add_argument(
        "--json", action="store_true", dest="as_json"
    )

    rollback_parser = subparsers.add_parser(
        "rollback", help="perform explicit offline rollback administration"
    )
    rollback_subparsers = rollback_parser.add_subparsers(
        dest="rollback_command", required=True
    )
    rollback_prepare_parser = rollback_subparsers.add_parser(
        "prepare",
        help="validate one stable rollback source and archive the active database",
    )
    rollback_prepare_parser.add_argument("organism_id")
    rollback_prepare_parser.add_argument(
        "--event-sequence", type=int, required=True, dest="event_sequence"
    )
    rollback_prepare_parser.add_argument(
        "--json", action="store_true", dest="as_json"
    )

    rollback_begin_parser = rollback_subparsers.add_parser(
        "begin",
        help="adopt one verified pre-rollback archive as durable rollback intent",
    )
    rollback_begin_parser.add_argument("organism_id")
    rollback_begin_parser.add_argument(
        "--archive-id", required=True, dest="archive_id"
    )
    rollback_begin_parser.add_argument(
        "--json", action="store_true", dest="as_json"
    )

    rollback_candidate_parser = rollback_subparsers.add_parser(
        "build-candidate",
        help="construct one verified restore candidate from durable rollback intent",
    )
    rollback_candidate_parser.add_argument("organism_id")
    rollback_candidate_parser.add_argument(
        "--json", action="store_true", dest="as_json"
    )

    rollback_transform_parser = rollback_subparsers.add_parser(
        "transform-candidate",
        help="transform one verified restore candidate into a new-lineage candidate",
    )
    rollback_transform_parser.add_argument("organism_id")
    rollback_transform_parser.add_argument(
        "--candidate-id", required=True, dest="candidate_id"
    )
    rollback_transform_parser.add_argument(
        "--reason", required=True, dest="administrative_reason"
    )
    rollback_transform_parser.add_argument(
        "--json", action="store_true", dest="as_json"
    )

    return parser


def _format_human(payload: dict[str, object]) -> str:
    return "\n".join(f"{key}: {value}" for key, value in payload.items())


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "init":
            status, checkpoint = initialize_organism(args.runtime_dir, args.organism_id)
            payload = status.as_dict()
            payload["genesis_checkpoint_id"] = checkpoint.checkpoint_id
        elif args.command == "enqueue":
            paths = OrganismPaths.build(args.runtime_dir, args.organism_id)
            payload = enqueue_garden_tick(paths, args.external_event_id).as_dict()
        elif args.command == "wake":
            payload = perform_garden_wake(
                args.runtime_dir,
                args.organism_id,
                seed=args.seed,
            ).as_dict()
        elif args.command == "status":
            payload = get_status(args.runtime_dir, args.organism_id).as_dict()
        elif args.command == "maintenance" and args.maintenance_command == "inspect":
            payload = inspect_maintenance(args.runtime_dir, args.organism_id).as_dict()
        elif args.command == "maintenance" and args.maintenance_command == "clear":
            payload = clear_maintenance(
                args.runtime_dir,
                args.organism_id,
                args.recovery_reason,
            ).as_dict()
        elif (
            args.command == "checkpoint"
            and args.checkpoint_command == "repair-pending"
        ):
            payload = repair_pending_checkpoint_registration(
                args.runtime_dir,
                args.organism_id,
            ).as_dict()
        elif args.command == "export" and args.export_command == "events":
            payload = export_stable_events(
                args.runtime_dir,
                args.organism_id,
                args.event_sequence,
            ).as_dict()
        elif args.command == "rollback" and args.rollback_command == "prepare":
            payload = prepare_rollback_archive(
                args.runtime_dir,
                args.organism_id,
                args.event_sequence,
            ).as_dict()
        elif args.command == "rollback" and args.rollback_command == "begin":
            payload = begin_rollback(
                args.runtime_dir,
                args.organism_id,
                args.archive_id,
            ).as_dict()
        elif (
            args.command == "rollback"
            and args.rollback_command == "build-candidate"
        ):
            payload = build_restore_candidate(
                args.runtime_dir,
                args.organism_id,
            ).as_dict()
        elif (
            args.command == "rollback"
            and args.rollback_command == "transform-candidate"
        ):
            payload = transform_restore_candidate(
                args.runtime_dir,
                args.organism_id,
                args.candidate_id,
                args.administrative_reason,
            ).as_dict()
        else:
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
