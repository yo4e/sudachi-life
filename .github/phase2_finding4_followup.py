from pathlib import Path

path = Path('src/sudachi_life/phase2_dispatch_runtime.py')
text = path.read_text(encoding='utf-8')
old = '''        snapshot_row, snapshot_envelope = _load_request(snapshot, request_id)
'''
new = '''        try:
            snapshot_row, snapshot_envelope = _load_request(snapshot, request_id)
        except DispatchAdmissionRejectedError as exc:
            raise DispatchAdmissionRejectedError(
                f"dispatch checkpoint request is invalid: {exc}"
            ) from exc
'''
if text.count(old) != 1:
    raise SystemExit(f'expected one snapshot request load, found {text.count(old)}')
path.write_text(text.replace(old, new, 1), encoding='utf-8')
