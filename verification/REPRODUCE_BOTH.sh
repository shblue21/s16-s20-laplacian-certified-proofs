#!/bin/bash
set -euo pipefail

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)
root_dir=$(CDPATH= cd -- "$script_dir/.." && pwd -P)
python_bin=/usr/bin/python3
[[ -x $python_bin ]] || python_bin=$(command -v python3)

n16_archive="$root_dir/artifacts/snn16-certified-nonexistence-20260821.zip"
n20_archive="$root_dir/artifacts/S20_CERTIFIED_EXHAUSTION_RELEASE_20260821.tar.gz"
n16_expected="$root_dir/results/ORDER16_RESULT_FINAL.json"
n20_expected="$root_dir/results/S20_CANONICAL_RESULT_FINAL.json"
n20_reproduced="$root_dir/tmp/reproduced-n20-canonical.json"

[[ -f $n16_archive && ! -L $n16_archive ]] || {
  echo "missing n=16 archive: $n16_archive" >&2
  exit 1
}
[[ -f $n20_archive && ! -L $n20_archive ]] || {
  echo "missing n=20 archive: $n20_archive" >&2
  exit 1
}

"$python_bin" -I - "$root_dir/MANIFEST.sha256" "$root_dir" <<'PY'
import hashlib
import pathlib
import sys

manifest = pathlib.Path(sys.argv[1])
root = pathlib.Path(sys.argv[2])
for line_number, raw in enumerate(manifest.read_text(encoding="utf-8").splitlines(), 1):
    if not raw:
        continue
    digest, relative = raw.split("  ", 1)
    relative = relative.removeprefix("./")
    path = root / relative
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual != digest:
        raise SystemExit(
            f"manifest mismatch at line {line_number}: {relative}: "
            f"expected {digest}, got {actual}"
        )
print("COMBINED_MANIFEST_PASS")
PY

work_dir=$(mktemp -d /tmp/s16-s20-replay.XXXXXX)
cleanup() {
  case $work_dir in
    /tmp/s16-s20-replay.*) rm -rf -- "$work_dir" ;;
    *) echo "refusing unsafe cleanup path: $work_dir" >&2 ;;
  esac
}
trap cleanup EXIT

"$python_bin" -I - "$n16_archive" "$work_dir" <<'PY'
import pathlib
import sys
import zipfile

archive = pathlib.Path(sys.argv[1])
target = pathlib.Path(sys.argv[2])
top = set()
seen = set()
with zipfile.ZipFile(archive) as bundle:
    for info in bundle.infolist():
        raw = info.filename.rstrip("/")
        if not raw:
            continue
        parts = pathlib.PurePosixPath(raw).parts
        if raw.startswith("/") or any(part in ("", ".", "..") for part in parts):
            raise SystemExit(f"unsafe ZIP path: {info.filename!r}")
        if raw in seen:
            raise SystemExit(f"duplicate ZIP path: {raw!r}")
        seen.add(raw)
        top.add(parts[0])
    if top != {"snn16-certified-nonexistence"}:
        raise SystemExit(f"unexpected ZIP top level: {sorted(top)!r}")
    bundle.extractall(target)
PY

echo "===== ORDER 16 CLEAN REPLAY ====="
n16_log="$work_dir/order16.log"
(
  cd "$work_dir/snn16-certified-nonexistence"
  PATH="$root_dir/verification:$PATH" /bin/bash ./REPRODUCE.sh
  echo "===== ORDER 16 OPTIMIZED VERIFIER ====="
  "$python_bin" -O code/verify_certificates.py
) | /usr/bin/tee "$n16_log"

"$python_bin" -I - "$n16_archive" "$n16_expected" "$n16_log" <<'PY'
import hashlib
import json
import pathlib
import sys

archive = pathlib.Path(sys.argv[1])
expected_path = pathlib.Path(sys.argv[2])
log_path = pathlib.Path(sys.argv[3])

records = []
for line in log_path.read_text(encoding="utf-8").splitlines():
    if line.startswith("{"):
        records.append(json.loads(line))

verification = [value for value in records if value.get("status") == "VERIFIED_UNSAT"]
semantic = [value for value in records if value.get("status") == "SEMANTIC_AUDIT_PASSED"]
if len(verification) != 2:
    raise SystemExit(
        f"expected normal and optimized order-16 verifier records, got {len(verification)}"
    )
if len(semantic) != 1:
    raise SystemExit(
        f"expected one order-16 semantic-audit record, got {len(semantic)}"
    )

def normalized(value):
    value = dict(value)
    value.pop("elapsed_seconds", None)
    return value

normal = normalized(verification[0])
optimized = normalized(verification[1])
if normal != optimized:
    raise SystemExit("order-16 normal and optimized verifier results differ")

digest = hashlib.sha256(archive.read_bytes()).hexdigest()
result = {
    "archive_sha256": digest,
    "semantic_audit": semantic[0],
    "status": "ORDER16_REPRODUCTION_PASS",
    "verification": normal,
}
payload = (json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n").encode()
if payload != expected_path.read_bytes():
    raise SystemExit("order-16 reproduced summary differs from frozen expected bytes")
print("N16_CANONICAL_BYTE_MATCH")
PY

echo "===== ORDER 20 HARDENED REPLAY ====="
mkdir -p "$root_dir/tmp"
"$root_dir/verification/n20/REPRODUCE_INDEPENDENT.sh" \
  "$n20_archive" \
  "$n20_reproduced"

"$python_bin" -I - "$n20_expected" "$n20_reproduced" <<'PY'
import pathlib
import sys

expected = pathlib.Path(sys.argv[1]).read_bytes()
actual = pathlib.Path(sys.argv[2]).read_bytes()
if actual != expected:
    raise SystemExit("n=20 reproduced canonical JSON differs from frozen expected result")
print("N20_CANONICAL_BYTE_MATCH")
PY

echo "COMBINED_REPRODUCTION_PASS orders=16,20"
