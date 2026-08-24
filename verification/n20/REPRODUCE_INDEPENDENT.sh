#!/usr/bin/env -S -i PATH=/usr/bin:/bin:/usr/sbin:/sbin HOME=/tmp TMPDIR=/tmp TZ=UTC PYTHONNOUSERSITE=1 PYTHONHASHSEED=0 S20_CLEAN_ENTRY=1 /bin/bash --noprofile --norc
set -euo pipefail

# The supported entry point is direct execution (`./REPRODUCE_INDEPENDENT.sh`).
# Its env(1) shebang clears BASH_ENV, PYTHONPATH and all other inherited state
# before Bash or Python loads user-controlled startup code. `bash script.sh` is
# deliberately refused because Bash may already have executed BASH_ENV.
if [[ ${S20_CLEAN_ENTRY:-} != 1 ]]; then
  printf '%s\n' \
    'ERROR: invoke REPRODUCE_INDEPENDENT.sh directly; do not run it through bash.' \
    >&2
  exit 126
fi

unset BASH_ENV ENV CDPATH GLOBIGNORE
unset PYTHONPATH PYTHONHOME PYTHONSTARTUP PYTHONINSPECT PYTHONWARNINGS
unset TAR_OPTIONS GZIP BZIP2 BZIP XZ_DEFAULTS XZ_OPT
export PATH=/usr/bin:/bin:/usr/sbin:/sbin
export HOME=/tmp
export TMPDIR=/tmp
export LC_ALL=C
export PYTHONDONTWRITEBYTECODE=1
export PYTHONNOUSERSITE=1
export PYTHONHASHSEED=0
export TZ=UTC

PYTHON=/usr/bin/python3
TAR=/usr/bin/tar
CP=/bin/cp
CAT=/bin/cat
MKDIR=/bin/mkdir
MKTEMP=/usr/bin/mktemp
RM=/bin/rm
UNAME=/usr/bin/uname
ENV_TOOL=/usr/bin/env

usage() {
  printf 'Usage: %s /path/to/S20_RELEASE.tar.gz [canonical-result.json]\n' \
    "${0##*/}" >&2
  exit 2
}

fail() {
  printf 'ERROR: %s\n' "$*" >&2
  exit 1
}

script_name=${0##*/}
case $0 in
  */*) script_parent=${0%/*} ;;
  *) script_parent=. ;;
esac
script_dir=$(CDPATH= cd -- "$script_parent" && pwd -P)
script_path="$script_dir/$script_name"

# Enforce network denial for this process and all descendants. The clean-entry
# marker cannot be inherited from the caller because the shebang starts with
# env -i. On Linux, bwrap is preferred; unshare is a fail-closed fallback.
if [[ ${S20_NETWORK_SANDBOXED:-} != 1 ]]; then
  platform=$($UNAME -s)
  case $platform in
    Darwin)
      [[ -x /usr/bin/sandbox-exec ]] || fail 'sandbox-exec is required for offline replay on macOS'
      exec /usr/bin/sandbox-exec \
        -p '(version 1)(allow default)(deny network*)' \
        "$ENV_TOOL" -i \
        PATH=/usr/bin:/bin:/usr/sbin:/sbin HOME=/tmp TMPDIR=/tmp TZ=UTC \
        LC_ALL=C PYTHONDONTWRITEBYTECODE=1 PYTHONNOUSERSITE=1 PYTHONHASHSEED=0 \
        S20_CLEAN_ENTRY=1 S20_NETWORK_SANDBOXED=1 \
        S20_NETWORK_BACKEND=macos-sandbox-exec \
        /bin/bash --noprofile --norc "$script_path" "$@"
      ;;
    Linux)
      if [[ -x /usr/bin/bwrap ]]; then
        exec /usr/bin/bwrap --unshare-net --bind / / --dev-bind /dev /dev \
          --proc /proc -- \
          "$ENV_TOOL" -i \
          PATH=/usr/bin:/bin:/usr/sbin:/sbin HOME=/tmp TMPDIR=/tmp TZ=UTC \
          LC_ALL=C PYTHONDONTWRITEBYTECODE=1 PYTHONNOUSERSITE=1 PYTHONHASHSEED=0 \
          S20_CLEAN_ENTRY=1 S20_NETWORK_SANDBOXED=1 \
          S20_NETWORK_BACKEND=linux-bwrap \
          /bin/bash --noprofile --norc "$script_path" "$@"
      elif [[ -x /usr/bin/unshare ]]; then
        exec /usr/bin/unshare --net -- \
          "$ENV_TOOL" -i \
          PATH=/usr/bin:/bin:/usr/sbin:/sbin HOME=/tmp TMPDIR=/tmp TZ=UTC \
          LC_ALL=C PYTHONDONTWRITEBYTECODE=1 PYTHONNOUSERSITE=1 PYTHONHASHSEED=0 \
          S20_CLEAN_ENTRY=1 S20_NETWORK_SANDBOXED=1 \
          S20_NETWORK_BACKEND=linux-unshare \
          /bin/bash --noprofile --norc "$script_path" "$@"
      else
        fail 'bwrap or unshare is required for offline replay on Linux'
      fi
      ;;
    *) fail "unsupported platform for enforced offline replay: $platform" ;;
  esac
fi

printf 'Offline sandbox: %s\n' "${S20_NETWORK_BACKEND:-unknown}"

[[ $# -ge 1 && $# -le 2 ]] || usage
[[ -x $PYTHON ]] || fail "trusted Python is missing: $PYTHON"
[[ -x $TAR ]] || fail "trusted tar is missing: $TAR"

archive_arg=$1
canonical_output=${2:-}
[[ -f $archive_arg && ! -L $archive_arg ]] || \
  fail "archive is not a real regular file: $archive_arg"
archive_dir=$(CDPATH= cd -- "${archive_arg%/*}" 2>/dev/null && pwd -P) || {
  if [[ $archive_arg != */* ]]; then
    archive_dir=$PWD
  else
    fail "cannot resolve archive directory: $archive_arg"
  fi
}
archive="$archive_dir/${archive_arg##*/}"

expected_archive_digest='1eeda59a36dc835ec0efd3dc741d985145054af0d72e77f59e84f9cb63461206'
expected_enum_digest='4df5db86179076364561689d8a4e62cba67890ded650ecc354f53949492bdbd9'
expected_cert_digest='b12dfe89fa5b8562844da9f963fdc9782336a3ef29219f6d481dea71170d385e'
expected_cycle_digest='c59c0255ba40f7b311c614b7493b760460a622ceb09fca08ce1669230248f956'

sha256_file() {
  "$PYTHON" -I - "$1" <<'PY'
import hashlib
import pathlib
import sys

digest = hashlib.sha256()
with pathlib.Path(sys.argv[1]).open("rb") as stream:
    for block in iter(lambda: stream.read(1024 * 1024), b""):
        digest.update(block)
print(digest.hexdigest())
PY
}

sidecar_digest() {
  "$PYTHON" -I - "$1" <<'PY'
import pathlib
import re
import sys

text = pathlib.Path(sys.argv[1]).read_text(encoding="utf-8")
matches = re.findall(r"(?i)(?<![0-9a-f])[0-9a-f]{64}(?![0-9a-f])", text)
if len(matches) != 1:
    raise SystemExit(f"expected exactly one SHA-256 digest in sidecar, found {len(matches)}")
print(matches[0].lower())
PY
}

work_dir=$($MKTEMP -d /tmp/s20-independent.XXXXXX)
cleanup() {
  case $work_dir in
    /tmp/s20-independent.*) "$RM" -rf -- "$work_dir" ;;
    *) printf 'Refusing to remove unexpected temporary path: %s\n' "$work_dir" >&2 ;;
  esac
}
trap cleanup EXIT
trap 'exit 129' HUP
trap 'exit 130' INT
trap 'exit 143' TERM

# Privately snapshot and pin every project-internal executable before the long
# bundled replay. Only these immutable copies are executed later.
helper_dir="$work_dir/helpers"
"$MKDIR" -m 700 "$helper_dir"
snapshot_helper() {
  local name=$1
  local expected=$2
  local source="$script_dir/$name"
  local target="$helper_dir/$name"
  [[ -f $source && ! -L $source ]] || fail "helper is missing or unsafe: $source"
  "$CP" -p "$source" "$target"
  local actual
  actual=$(sha256_file "$target")
  [[ $actual == "$expected" ]] || \
    fail "helper digest mismatch for $name: expected $expected, got $actual"
  printf 'Pinned helper: %s SHA-256=%s\n' "$name" "$actual"
}
snapshot_helper verify_enumeration_v2.py "$expected_enum_digest"
snapshot_helper verify_certificates_v2.py "$expected_cert_digest"
snapshot_helper audit_cycle_identity_v2.py "$expected_cycle_digest"

# Work only with a private archive copy so caller-side replacement cannot race
# validation and extraction.
local_archive="$work_dir/release.tar.gz"
"$CP" -p "$archive" "$local_archive"
actual_digest=$(sha256_file "$local_archive")
printf 'Archive SHA-256: %s\n' "$actual_digest"
[[ $actual_digest == "$expected_archive_digest" ]] || \
  fail "archive is not the frozen S20 release: expected $expected_archive_digest, got $actual_digest"

sidecars=("$archive.sha256")
case $archive in
  *.tar.gz) sidecars+=("${archive%.tar.gz}.sha256") ;;
  *.tgz) sidecars+=("${archive%.tgz}.sha256") ;;
esac
sidecar_count=0
checked_sidecar=''
for sidecar in "${sidecars[@]}"; do
  [[ -f $sidecar && ! -L $sidecar ]] || continue
  [[ $sidecar != "$checked_sidecar" ]] || continue
  checked_sidecar=$sidecar
  sidecar_count=$((sidecar_count + 1))
  sidecar_value=$(sidecar_digest "$sidecar") || fail "invalid SHA-256 sidecar: $sidecar"
  [[ $sidecar_value == "$actual_digest" ]] || \
    fail "sidecar hash mismatch ($sidecar): expected $sidecar_value, got $actual_digest"
  printf 'Sidecar verified: %s\n' "$sidecar"
done
[[ $sidecar_count -gt 0 ]] || fail 'the detached archive SHA-256 sidecar is required'

# Validate members with Python before extracting with tar. The hard outer pin
# and private copy are checked first.
release_top=$(
  "$PYTHON" -I - "$local_archive" <<'PY'
import pathlib
import sys
import tarfile

archive = pathlib.Path(sys.argv[1])
max_members = 1_000_000
max_bytes = 20 * 1024**3
seen = set()
top_levels = set()
directory_entries = set()
total_bytes = 0

with tarfile.open(archive, mode="r:*") as bundle:
    members = bundle.getmembers()
    if not members:
        raise SystemExit("archive is empty")
    if len(members) > max_members:
        raise SystemExit(f"archive has too many members: {len(members)}")
    for member in members:
        raw = member.name
        if "\x00" in raw or raw.startswith("/"):
            raise SystemExit(f"unsafe archive path: {raw!r}")
        trimmed = raw[:-1] if raw.endswith("/") else raw
        parts = trimmed.split("/")
        if not trimmed or any(part in ("", ".", "..") for part in parts):
            raise SystemExit(f"unsafe/noncanonical archive path: {raw!r}")
        canonical = "/".join(parts)
        if canonical in seen:
            raise SystemExit(f"duplicate archive path: {canonical!r}")
        seen.add(canonical)
        top_levels.add(parts[0])
        if member.issym() or member.islnk():
            raise SystemExit(f"links are forbidden in archive: {raw!r}")
        if not (member.isfile() or member.isdir()):
            raise SystemExit(f"special archive entry is forbidden: {raw!r}")
        if member.isdir():
            directory_entries.add(canonical)
        if member.isfile():
            total_bytes += member.size
            if member.size < 0 or total_bytes > max_bytes:
                raise SystemExit("archive expansion limit exceeded")

if len(top_levels) != 1:
    raise SystemExit(f"archive must contain one top-level directory: {sorted(top_levels)!r}")
top = next(iter(top_levels))
if top not in directory_entries:
    raise SystemExit(f"top-level directory entry is missing: {top!r}")
print(top)
PY
) || fail 'archive safety validation failed'

extract_dir="$work_dir/extracted"
"$MKDIR" -m 700 "$extract_dir"
"$TAR" -xzf "$local_archive" -C "$extract_dir"
release_dir="$extract_dir/$release_top"
[[ -d $release_dir && ! -L $release_dir ]] || fail "release root was not safely extracted: $release_dir"
[[ -f $release_dir/REPRODUCE_FINAL.sh && ! -L $release_dir/REPRODUCE_FINAL.sh ]] || \
  fail 'bundled REPRODUCE_FINAL.sh is missing or unsafe'

printf '\n===== BUNDLED CLEAN REPLAY =====\n'
bundled_log="$work_dir/bundled.log"
set +e
(
  cd "$release_dir"
  /bin/bash --noprofile --norc ./REPRODUCE_FINAL.sh
) >"$bundled_log" 2>&1
bundled_rc=$?
set -e
"$CAT" "$bundled_log"
[[ $bundled_rc -eq 0 ]] || fail "bundled replay failed with exit $bundled_rc"

printf '\n===== INDEPENDENT ENUMERATION V2 (normal) =====\n'
enum_normal="$work_dir/enum-normal.json"
"$PYTHON" -I "$helper_dir/verify_enumeration_v2.py" "$release_dir" >"$enum_normal"
"$CAT" "$enum_normal"

printf '\n===== INDEPENDENT ENUMERATION V2 (-O) =====\n'
enum_optimized="$work_dir/enum-optimized.json"
"$PYTHON" -I -O "$helper_dir/verify_enumeration_v2.py" "$release_dir" >"$enum_optimized"
"$CAT" "$enum_optimized"

printf '\n===== INDEPENDENT CERTIFICATE VERIFIER V2 (normal) =====\n'
cert_normal="$work_dir/cert-normal.json"
"$PYTHON" -I "$helper_dir/verify_certificates_v2.py" "$release_dir" >"$cert_normal"
"$CAT" "$cert_normal"

printf '\n===== INDEPENDENT CERTIFICATE VERIFIER V2 (-O) =====\n'
cert_optimized="$work_dir/cert-optimized.json"
"$PYTHON" -I -O "$helper_dir/verify_certificates_v2.py" "$release_dir" >"$cert_optimized"
"$CAT" "$cert_optimized"

printf '\n===== CORRECTED C20 SEMANTIC REGRESSION =====\n'
cycle_result="$work_dir/cycle.json"
"$PYTHON" -I "$helper_dir/audit_cycle_identity_v2.py" >"$cycle_result"
"$CAT" "$cycle_result"

# Generate a telemetry-free canonical attestation. It also requires normal and
# optimized outputs to match after removal of elapsed time and private paths.
canonical_result="$work_dir/S20_CANONICAL_RESULT.json"
"$PYTHON" -I - \
  "$actual_digest" "$release_top" \
  "$expected_enum_digest" "$expected_cert_digest" "$expected_cycle_digest" \
  "$bundled_log" "$enum_normal" "$enum_optimized" \
  "$cert_normal" "$cert_optimized" "$cycle_result" "$canonical_result" <<'PY'
import hashlib
import json
import pathlib
import sys

(
    archive_digest,
    release_top,
    enum_digest,
    cert_digest,
    cycle_digest,
    bundled_log_path,
    enum_normal_path,
    enum_optimized_path,
    cert_normal_path,
    cert_optimized_path,
    cycle_path,
    result_path,
) = sys.argv[1:]

volatile = {"elapsed_seconds", "release_root"}

def normalized(value):
    if isinstance(value, dict):
        return {
            key: normalized(item)
            for key, item in value.items()
            if key not in volatile
        }
    if isinstance(value, list):
        return [normalized(item) for item in value]
    return value

def load(path):
    return json.loads(pathlib.Path(path).read_text(encoding="utf-8"))

enum_normal = normalized(load(enum_normal_path))
enum_optimized = normalized(load(enum_optimized_path))
if enum_normal != enum_optimized:
    raise SystemExit("normal and optimized enumeration results differ")

cert_normal = normalized(load(cert_normal_path))
cert_optimized = normalized(load(cert_optimized_path))
if cert_normal != cert_optimized:
    raise SystemExit("normal and optimized certificate results differ")

bundled_results = []
for line in pathlib.Path(bundled_log_path).read_text(encoding="utf-8").splitlines():
    try:
        value = json.loads(line)
    except json.JSONDecodeError:
        continue
    if isinstance(value, dict) and value.get("status") == "VERIFIED_UNSAT":
        bundled_results.append(normalized(value))
if len(bundled_results) != 2 or bundled_results[0] != bundled_results[1]:
    raise SystemExit("bundled normal/-O semantic results are absent or differ")

cycle = normalized(load(cycle_path))
if cycle.get("status") != "GRAPH_IDENTITY_CYCLE_V2_PASS":
    raise SystemExit("corrected C20 semantic regression did not pass")

result = {
    "archive_sha256": archive_digest,
    "bundled": bundled_results[0],
    "certificates_v2": cert_normal,
    "enumeration_v2": enum_normal,
    "helpers": {
        "audit_cycle_identity_v2.py": cycle_digest,
        "verify_certificates_v2.py": cert_digest,
        "verify_enumeration_v2.py": enum_digest,
    },
    "release": release_top,
    "schema": "s20-canonical-reproduction-v2",
    "semantic_cycle_regression": cycle,
    "status": "INDEPENDENT_REPRODUCTION_PASS",
}
payload = (json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
pathlib.Path(result_path).write_bytes(payload)
print(hashlib.sha256(payload).hexdigest())
PY
canonical_digest=$(sha256_file "$canonical_result")

printf '\n===== CANONICAL RESULT =====\n'
"$CAT" "$canonical_result"
printf 'CANONICAL_RESULT_SHA256=%s\n' "$canonical_digest"
printf 'OFFLINE_SANDBOX=ENFORCED\n'
printf 'INDEPENDENT_REPRODUCTION_PASS archive_sha256=%s release=%s canonical_sha256=%s\n' \
  "$actual_digest" "$release_top" "$canonical_digest"

if [[ -n $canonical_output ]]; then
  output_parent=${canonical_output%/*}
  if [[ $output_parent == "$canonical_output" ]]; then
    output_parent=.
  fi
  [[ -d $output_parent && ! -L $output_parent ]] || \
    fail "canonical result parent is not a real directory: $output_parent"
  "$CP" -p "$canonical_result" "$canonical_output"
  printf 'Canonical result copied to: %s\n' "$canonical_output"
fi
