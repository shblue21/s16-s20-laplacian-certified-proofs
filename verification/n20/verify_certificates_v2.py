#!/usr/bin/env python3
"""Independent, standard-library verifier for the S20 certificate release.

Usage:

    python3 verify_certificates_v2.py EXTRACTED_RELEASE_ROOT

This program treats the release as untrusted data.  In particular, it never
imports or executes a Python or shell file from the release.  It derives the
global constants and the degree/triangle bounds, independently enumerates the
candidate ledger, rebuilds every relaxation from the mathematical definitions,
and checks all sparse Farkas multipliers with Python integers.

The certificate convention is the following.  After finite lower bounds have
been shifted and a nonnegative slack has been added to each <= row and each
finite upper bound, a model has the form B*x=h, x>=0.  A sparse integer vector
z proves infeasibility when B^T*z>=0 and h^T*z<0.

Every trusted check is explicit, so ``python -O`` does not weaken verification.
"""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass, field
from functools import lru_cache
import gzip
import hashlib
from itertools import combinations_with_replacement
import json
import math
from pathlib import Path
import re
import sys
import time
from typing import Callable, Iterable, Optional


N = 20
NONZERO_EIGENVALUES = tuple(range(1, N))
CERT_FORMAT = "s20-standard-form-farkas-z-v1"
MAX_COMPRESSED_BYTES = 64 * 1024 * 1024
MAX_DECOMPRESSED_BYTES = 512 * 1024 * 1024
MAX_PLAIN_JSON_BYTES = 64 * 1024 * 1024
FINAL_ROOT_KEYS = {
    "branch_variable_index", "branch_variable_name", "floor", "left_bound",
    "right_bound", "root_index", "sequence", "triangles",
}
BRANCH_ROOT_KEYS = {
    "floor", "left_cert", "right_cert", "root_index", "sequence",
    "triangles", "variable_index", "variable_name",
}


class Rejection(RuntimeError):
    """Raised whenever untrusted input or an exact proof check fails."""


def demand(condition: bool, message: object) -> None:
    if not condition:
        raise Rejection(str(message))


def no_duplicate_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        demand(key not in result, f"duplicate JSON key: {key!r}")
        result[key] = value
    return result


def reject_json_constant(token: str) -> object:
    raise Rejection(f"non-standard JSON constant is forbidden: {token}")


def decode_json(text: str, label: str) -> object:
    try:
        return json.loads(
            text,
            object_pairs_hook=no_duplicate_object,
            parse_constant=reject_json_constant,
        )
    except (UnicodeError, json.JSONDecodeError, Rejection) as exc:
        raise Rejection(f"invalid JSON in {label}: {exc}") from exc


def read_json(path: Path, compressed: bool = False) -> object:
    demand(path.is_file(), f"missing file: {path}")
    demand(not path.is_symlink(), f"symbolic links are not accepted: {path}")
    try:
        if compressed:
            text = limited_gzip_payload(path).decode("utf-8")
        else:
            demand(path.stat().st_size <= MAX_PLAIN_JSON_BYTES,
                   f"plain JSON exceeds size limit: {path}")
            text = path.read_text(encoding="utf-8")
    except (OSError, EOFError, UnicodeError) as exc:
        raise Rejection(f"cannot read {path}: {exc}") from exc
    return decode_json(text, str(path))


def digest_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def digest_file(path: Path) -> str:
    demand(path.is_file() and not path.is_symlink(), f"cannot hash non-regular release file: {path}")
    h = hashlib.sha256()
    try:
        with path.open("rb") as handle:
            for block in iter(lambda: handle.read(1024 * 1024), b""):
                h.update(block)
    except OSError as exc:
        raise Rejection(f"cannot hash {path}: {exc}") from exc
    return h.hexdigest()


def integer(value: object, label: str) -> int:
    demand(type(value) is int, f"{label} must be an integer")
    return value


def dictionary(value: object, label: str) -> dict[str, object]:
    demand(isinstance(value, dict), f"{label} must be an object")
    return value


def array(value: object, label: str) -> list[object]:
    demand(isinstance(value, list), f"{label} must be an array")
    return value


def exact_integer_table(value: object, expected: dict[str, int], label: str) -> dict[str, object]:
    """Require an exact-key JSON object whose values are canonical integers."""
    table = dictionary(value, label)
    demand(set(table) == set(expected), f"{label}: missing or unexpected fields")
    for key, wanted in expected.items():
        got = integer(table.get(key), f"{label}.{key}")
        demand(got == wanted, f"{label}.{key}: {got} != {wanted}")
    return table


def exact_sha256_table(value: object, expected: dict[str, str], label: str) -> dict[str, object]:
    """Require an exact-key table of canonical lowercase SHA-256 strings."""
    table = dictionary(value, label)
    demand(set(table) == set(expected), f"{label}: missing or unexpected fields")
    for key, wanted in expected.items():
        got = table.get(key)
        demand(type(got) is str and re.fullmatch(r"[0-9a-f]{64}", got) is not None,
               f"{label}.{key}: noncanonical SHA-256")
        demand(got == wanted, f"{label}.{key}: digest mismatch")
    return table


@dataclass(frozen=True)
class DerivedConstants:
    spectrum: tuple[int, ...]
    edge_count: int
    degree_sum: int
    degree_square_sum: int
    triangle_offset: int
    trace_l4: int
    spanning_trees: int
    degree_min: int
    degree_max: int
    triangle_min: int
    triangle_max: int
    complement_triangle_total: int


def derive_constants() -> DerivedConstants:
    """Derive, rather than trust, every global constant used in elimination."""
    spectrum = tuple(range(N))
    trace1 = sum(spectrum)
    trace2 = sum(k * k for k in spectrum)
    trace3 = sum(k * k * k for k in spectrum)
    trace4 = sum(k ** 4 for k in spectrum)
    demand(trace1 % 2 == 0, "odd Laplacian trace")
    edges = trace1 // 2
    degree_squares = trace2 - trace1
    third_offset = trace3 - 3 * degree_squares

    # For a vertex of degree d, spectral projector weights give
    # sum k*w_k=d and sum k^2*w_k=d^2+d with w_0=1/20.  Since
    # k^2 <= 20k-19 for 1<=k<=19, necessarily
    #     20*d^2 - 380*d + 361 <= 0.
    # Enumerate all simple-graph degrees to avoid trusting stated roots.
    allowed_degrees = tuple(
        d for d in range(N) if N * d * d - N * (N - 1) * d + (N - 1) ** 2 <= 0
    )
    demand(allowed_degrees == tuple(range(2, 18)), f"derived degree range is {allowed_degrees}")

    # Every edge uv has at least d(u)+d(v)-N common neighbors.  Summing gives
    # 3t >= sum d(v)^2 - N|E|.  The ceiling is computed exactly.
    triangle_numerator = degree_squares - N * edges
    triangle_lower = (triangle_numerator + 2) // 3

    # The two-colour count of vertex triples gives
    # t(G)+t(Gbar)=C(n,3)-1/2 sum_v d_v(n-1-d_v).
    mixed_twice = (N - 1) * trace1 - degree_squares
    demand(mixed_twice % 2 == 0, "nonintegral mixed-triple count")
    complement_total = math.comb(N, 3) - mixed_twice // 2
    triangle_upper = complement_total - triangle_lower

    demand(triangle_lower == 127, f"derived triangle lower bound is {triangle_lower}")
    demand(complement_total == 475, f"derived complement triangle sum is {complement_total}")
    demand(triangle_upper == 348, f"derived triangle upper bound is {triangle_upper}")

    return DerivedConstants(
        spectrum=spectrum,
        edge_count=edges,
        degree_sum=trace1,
        degree_square_sum=degree_squares,
        triangle_offset=third_offset,
        trace_l4=trace4,
        spanning_trees=math.factorial(N - 1) // N,
        degree_min=allowed_degrees[0],
        degree_max=allowed_degrees[-1],
        triangle_min=triangle_lower,
        triangle_max=triangle_upper,
        complement_triangle_total=complement_total,
    )


def check_params(root: Path, constants: DerivedConstants) -> dict[str, int]:
    params = dictionary(read_json(root / "PARAMS.json"), "PARAMS.json")
    expected: dict[str, object] = {
        "n": N,
        "spectrum": list(constants.spectrum),
        "edge_count": constants.edge_count,
        "degree_sum": constants.degree_sum,
        "degree_square_sum": constants.degree_square_sum,
        "triangle_offset": constants.triangle_offset,
        "trace_L4": constants.trace_l4,
        "spanning_tree_count": constants.spanning_trees,
        "degree_min": constants.degree_min,
        "degree_max": constants.degree_max,
        "triangle_min": constants.triangle_min,
        "triangle_max": constants.triangle_max,
        "triangle_complement_total": constants.complement_triangle_total,
    }
    demand(set(params) == set(expected), "PARAMS.json has missing or unexpected fields")
    spectrum_value = array(params.get("spectrum"), "PARAMS.spectrum")
    for position, value in enumerate(spectrum_value):
        integer(value, f"PARAMS.spectrum[{position}]")
    for key in expected:
        if key != "spectrum":
            integer(params.get(key), f"PARAMS.{key}")
    demand(params == expected, {"PARAMS_mismatch": params, "derived": expected})
    return {
        "degree_min": constants.degree_min,
        "degree_max": constants.degree_max,
        "triangle_min": constants.triangle_min,
        "triangle_max": constants.triangle_max,
    }


def limited_gzip_payload(path: Path) -> bytes:
    demand(path.is_file(), f"missing data file: {path}")
    demand(not path.is_symlink(), f"symbolic links are not accepted: {path}")
    demand(path.stat().st_size <= MAX_COMPRESSED_BYTES,
           f"compressed input exceeds size limit: {path}")
    try:
        chunks: list[bytes] = []
        total = 0
        with gzip.open(path, "rb") as handle:
            while True:
                chunk = handle.read(1024 * 1024)
                if not chunk:
                    break
                total += len(chunk)
                demand(total <= MAX_DECOMPRESSED_BYTES,
                       f"decompressed input exceeds size limit: {path}")
                chunks.append(chunk)
        return b"".join(chunks)
    except (OSError, EOFError) as exc:
        raise Rejection(f"invalid gzip file {path}: {exc}") from exc


def gzip_payload(path: Path) -> bytes:
    return limited_gzip_payload(path)


def validate_sequence(seq: tuple[int, ...], label: str, lo: int = 0, hi: int = 19) -> None:
    demand(len(seq) == N, f"{label}: expected {N} degrees, got {len(seq)}")
    demand(tuple(sorted(seq)) == seq, f"{label}: degree sequence is not sorted")
    demand(all(lo <= d <= hi for d in seq), f"{label}: degree outside [{lo},{hi}]")


def parse_edge_variable_name(value: object, label: str) -> tuple[object, ...]:
    pieces = array(value, label)
    demand(len(pieces) == 3, f"{label}: expected ['E',degree,degree]")
    demand(type(pieces[0]) is str and pieces[0] == "E", f"{label}: expected edge-count variable")
    return (
        pieces[0],
        integer(pieces[1], f"{label}[1]"),
        integer(pieces[2], f"{label}[2]"),
    )


def parse_final_root(value: object, position: int) -> tuple[tuple[int, ...], int]:
    """Strictly type-check one final-root record before using its values."""
    item = dictionary(value, f"root[{position}]")
    demand(set(item) == FINAL_ROOT_KEYS,
           f"root[{position}]: missing or unexpected fields")
    root_index = integer(item.get("root_index"), f"root[{position}].root_index")
    demand(root_index == position, f"root[{position}]: noncanonical root index {root_index}")
    floor = integer(item.get("floor"), f"root[{position}].floor")
    variable_index = integer(
        item.get("branch_variable_index"),
        f"root[{position}].branch_variable_index",
    )
    parse_edge_variable_name(item.get("branch_variable_name"), f"root[{position}].branch_variable_name")
    demand(item.get("left_bound") == f"x[{variable_index}] <= {floor}",
           f"root[{position}]: left-bound display metadata mismatch")
    demand(item.get("right_bound") == f"x[{variable_index}] >= {floor + 1}",
           f"root[{position}]: right-bound display metadata mismatch")
    seq_raw = array(item.get("sequence"), f"root[{position}].sequence")
    seq = tuple(integer(x, f"root[{position}].sequence[{j}]") for j, x in enumerate(seq_raw))
    validate_sequence(seq, f"root[{position}]")
    triangles = integer(item.get("triangles"), f"root[{position}].triangles")
    return seq, triangles


def parse_sequences(payload: bytes, with_triangles: bool, label: str) -> list[object]:
    try:
        text = payload.decode("ascii")
    except UnicodeDecodeError as exc:
        raise Rejection(f"{label}: non-ASCII data") from exc
    demand(not text or text.endswith("\n"), f"{label}: missing final newline")
    result: list[object] = []
    seen: set[object] = set()
    for line_number, line in enumerate(text.splitlines(), 1):
        demand(line != "", f"{label}:{line_number}: blank line")
        if with_triangles:
            pieces = line.split("|")
            demand(len(pieces) == 2, f"{label}:{line_number}: malformed sequence/triangle pair")
            degree_text, triangle_text = pieces
        else:
            degree_text, triangle_text = line, ""
        tokens = degree_text.split(" ")
        demand(len(tokens) == N and all(re.fullmatch(r"0|[1-9][0-9]*", x) for x in tokens),
               f"{label}:{line_number}: noncanonical degree text")
        seq = tuple(int(x) for x in tokens)
        validate_sequence(seq, f"{label}:{line_number}")
        if with_triangles:
            demand(re.fullmatch(r"0|[1-9][0-9]*", triangle_text) is not None,
                   f"{label}:{line_number}: noncanonical triangle count")
            item: object = (seq, int(triangle_text))
        else:
            item = seq
        demand(item not in seen, f"{label}:{line_number}: duplicate record")
        seen.add(item)
        result.append(item)
    return result


def encode_sequences(items: Iterable[object], with_triangles: bool) -> bytes:
    lines: list[str] = []
    if with_triangles:
        for raw in items:
            seq, triangles = raw  # type: ignore[misc]
            lines.append(" ".join(str(d) for d in seq) + "|" + str(triangles) + "\n")
    else:
        for seq in items:
            lines.append(" ".join(str(d) for d in seq) + "\n")  # type: ignore[union-attr]
    return "".join(lines).encode("ascii")


@lru_cache(maxsize=None)
def moment_completion_possible(degree: int, slots: int, total: int, squares: int) -> bool:
    if slots < 0 or total < 0 or squares < 0:
        return False
    if degree == 18:
        return slots == total == squares == 0
    if slots == 0:
        return total == squares == 0
    if total < degree * slots or total > 17 * slots:
        return False
    if squares < degree * degree * slots or squares > 17 * 17 * slots:
        return False
    if squares * slots < total * total:
        return False
    return any(
        moment_completion_possible(
            degree + 1,
            slots - multiplicity,
            total - multiplicity * degree,
            squares - multiplicity * degree * degree,
        )
        for multiplicity in range(slots + 1)
    )


def enumerate_moment_sequences(constants: DerivedConstants) -> list[tuple[int, ...]]:
    multiplicities = [0] * 18
    output: list[tuple[int, ...]] = []

    def visit(degree: int, slots: int, total: int, squares: int) -> None:
        if degree == 18:
            if slots == total == squares == 0:
                output.append(tuple(d for d in range(2, 18) for _ in range(multiplicities[d])))
            return
        for count in range(slots + 1):
            next_state = (
                degree + 1,
                slots - count,
                total - count * degree,
                squares - count * degree * degree,
            )
            if moment_completion_possible(*next_state):
                multiplicities[degree] = count
                visit(*next_state)
        multiplicities[degree] = 0

    initial = (2, N, constants.degree_sum, constants.degree_square_sum)
    demand(moment_completion_possible(*initial), "moment recurrence has no initial completion")
    visit(*initial)
    output.sort()
    demand(len(output) == len(set(output)), "moment recurrence produced duplicates")
    return output


def erdos_gallai_ascending(seq: tuple[int, ...]) -> bool:
    descending = seq[::-1]
    left = 0
    for k in range(1, N + 1):
        left += descending[k - 1]
        right = k * (k - 1) + sum(min(k, d) for d in descending[k:])
        if left > right:
            return False
    return True


@dataclass
class CoverageLedger:
    representatives: list[tuple[tuple[int, ...], int]]
    stage1_survivors: list[tuple[tuple[int, ...], int]]
    stage2_survivors: list[tuple[tuple[int, ...], int]]
    class_survivors: list[tuple[tuple[int, ...], int]]
    raw: dict[str, bytes]
    counts: dict[str, int]


DATA_FILES = {
    "moment_sequences.txt.gz": False,
    "graphical_sequences.txt.gz": False,
    "base_sequences.txt.gz": True,
    "complement_representatives.txt.gz": True,
    "complement_pairs.txt.gz": None,
    "stage1_source.txt.gz": True,
    "stage1_survivors.txt.gz": True,
    "stage2_source.txt.gz": True,
    "stage2_survivors.txt.gz": True,
    "class_source.txt.gz": True,
    "class_survivors.txt.gz": True,
}


def verify_data(root: Path, constants: DerivedConstants) -> CoverageLedger:
    data_dir = root / "data"
    coverage = dictionary(read_json(data_dir / "coverage.json"), "coverage.json")
    demand(coverage.get("format") == "s20-coverage-v1", "wrong coverage format")
    file_meta = dictionary(coverage.get("files"), "coverage.files")
    demand(set(file_meta) == set(DATA_FILES), "coverage file set is not exact")

    raw: dict[str, bytes] = {}
    parsed: dict[str, list[object]] = {}
    for name, pair_mode in DATA_FILES.items():
        meta = dictionary(file_meta[name], f"coverage.files.{name}")
        path = data_dir / name
        demand(meta.get("path") == f"data/{name}", f"bad coverage path for {name}")
        demand(meta.get("sha256_compressed") == digest_file(path), f"compressed hash mismatch: {name}")
        payload = gzip_payload(path)
        demand(meta.get("sha256_uncompressed") == digest_bytes(payload), f"payload hash mismatch: {name}")
        demand(integer(meta.get("compressed_bytes"), f"{name}.compressed_bytes") == path.stat().st_size,
               f"compressed byte count mismatch: {name}")
        demand(integer(meta.get("uncompressed_bytes"), f"{name}.uncompressed_bytes") == len(payload),
               f"payload byte count mismatch: {name}")
        demand(integer(meta.get("count"), f"{name}.count") == payload.count(b"\n"),
               f"line count mismatch: {name}")
        raw[name] = payload
        if pair_mode is not None:
            parsed[name] = parse_sequences(payload, pair_mode, name)

    moment = enumerate_moment_sequences(constants)
    demand(encode_sequences(moment, False) == raw["moment_sequences.txt.gz"],
           "independent moment enumeration differs from ledger")
    graphical = [seq for seq in moment if erdos_gallai_ascending(seq)]
    demand(encode_sequences(graphical, False) == raw["graphical_sequences.txt.gz"],
           "independent Erdos-Gallai filtering differs from ledger")

    base: list[tuple[tuple[int, ...], int]] = []
    for seq in graphical:
        numerator = sum(d ** 3 for d in seq) - constants.triangle_offset
        if numerator % 6 == 0:
            triangles = numerator // 6
            if constants.triangle_min <= triangles <= constants.triangle_max:
                base.append((seq, triangles))
    base.sort()
    demand(encode_sequences(base, True) == raw["base_sequences.txt.gz"],
           "independent triangle filtering differs from ledger")

    base_set = set(base)
    representatives: list[tuple[tuple[int, ...], int]] = []
    fixed: list[object] = []
    consumed: set[tuple[tuple[int, ...], int]] = set()
    for item in base:
        if item in consumed:
            continue
        seq, triangles = item
        mate = (tuple(sorted(N - 1 - d for d in seq)), constants.complement_triangle_total - triangles)
        demand(mate in base_set, f"complement candidate absent: {item}")
        if mate == item:
            fixed.append(item)
        representatives.append(min(item, mate))
        consumed.add(item)
        consumed.add(mate)
    representatives.sort()
    demand(not fixed, f"unexpected complement fixed point: {fixed[:1]}")
    demand(len(consumed) == len(base), "complement pairing failed to cover base ledger")
    demand(encode_sequences(representatives, True) == raw["complement_representatives.txt.gz"],
           "canonical complement representatives differ")

    pair_lines: list[str] = []
    for representative in representatives:
        seq, triangles = representative
        mate = (tuple(sorted(N - 1 - d for d in seq)), constants.complement_triangle_total - triangles)
        demand(representative < mate, f"non-strict complement representative: {representative}")
        pair_lines.append(
            " ".join(map(str, seq)) + "|" + str(triangles) + "||" +
            " ".join(map(str, mate[0])) + "|" + str(mate[1]) + "\n"
        )
    demand("".join(pair_lines).encode("ascii") == raw["complement_pairs.txt.gz"],
           "complement pair ledger differs")

    demand(raw["stage1_source.txt.gz"] == raw["complement_representatives.txt.gz"],
           "Stage 1 source is not the representative ledger")
    demand(raw["stage2_source.txt.gz"] == raw["stage1_survivors.txt.gz"],
           "Stage 2 source does not equal Stage 1 survivors")
    demand(raw["class_source.txt.gz"] == raw["stage2_survivors.txt.gz"],
           "class source does not equal Stage 2 survivors")

    stage1_survivors = parsed["stage1_survivors.txt.gz"]
    stage2_survivors = parsed["stage2_survivors.txt.gz"]
    class_survivors = parsed["class_survivors.txt.gz"]
    demand(parsed["stage1_source.txt.gz"] == representatives, "parsed Stage 1 source mismatch")
    demand(parsed["stage2_source.txt.gz"] == stage1_survivors, "parsed Stage 2 source mismatch")
    demand(parsed["class_source.txt.gz"] == stage2_survivors, "parsed class source mismatch")

    def require_ordered_subsequence(source: list[object], survivor: list[object], label: str) -> None:
        survivor_set = set(survivor)
        demand(len(survivor_set) == len(survivor), f"{label}: duplicate survivor")
        demand(survivor == [item for item in source if item in survivor_set],
               f"{label}: survivors are not an ordered subset of the source")

    require_ordered_subsequence(representatives, stage1_survivors, "Stage 1")
    require_ordered_subsequence(stage1_survivors, stage2_survivors, "Stage 2")
    require_ordered_subsequence(stage2_survivors, class_survivors, "class")

    roots_doc = dictionary(read_json(data_dir / "final_integer_roots.json"), "final_integer_roots.json")
    demand(set(roots_doc) == {"format", "roots"},
           "final_integer_roots.json has missing or unexpected fields")
    demand(roots_doc.get("format") == "s20-final-integer-roots-v1", "wrong root metadata format")
    roots_array = array(roots_doc.get("roots"), "final_integer_roots.roots")
    roots_from_metadata: list[tuple[tuple[int, ...], int]] = []
    for position, raw_root in enumerate(roots_array):
        roots_from_metadata.append(parse_final_root(raw_root, position))
    demand(roots_from_metadata == class_survivors, "root metadata differs from class survivors")

    expected_counts = {
        "moment": len(moment),
        "graphical": len(graphical),
        "base": len(base),
        "complement_representatives": len(representatives),
        "complement_fixed_points": len(fixed),
        "stage1_source": len(representatives),
        "stage1_survivors": len(stage1_survivors),
        "stage1_leaves": len(representatives) - len(stage1_survivors),
        "stage2_source": len(stage1_survivors),
        "stage2_survivors": len(stage2_survivors),
        "stage2_leaves": len(stage1_survivors) - len(stage2_survivors),
        "class_source": len(stage2_survivors),
        "class_roots": len(class_survivors),
        "class_root_leaves": len(stage2_survivors) - len(class_survivors),
        "branch_roots": len(class_survivors),
        "branch_leaves": 2 * len(class_survivors),
        "total_leaves": (
            len(representatives) - len(stage1_survivors)
            + len(stage1_survivors) - len(stage2_survivors)
            + len(stage2_survivors) - len(class_survivors)
            + 2 * len(class_survivors)
        ),
    }
    exact_integer_table(coverage.get("counts"), expected_counts, "coverage.counts")
    demand(expected_counts == {
        "moment": 209932, "graphical": 200108, "base": 160244,
        "complement_representatives": 80122, "complement_fixed_points": 0,
        "stage1_source": 80122, "stage1_survivors": 16887, "stage1_leaves": 63235,
        "stage2_source": 16887, "stage2_survivors": 345, "stage2_leaves": 16542,
        "class_source": 345, "class_roots": 2, "class_root_leaves": 343,
        "branch_roots": 2, "branch_leaves": 4, "total_leaves": 80124,
    }, f"unexpected independently derived coverage counts: {expected_counts}")

    expected_mapping = {
        "stage1_source": digest_bytes(raw["stage1_source.txt.gz"]),
        "stage1_survivor": digest_bytes(raw["stage1_survivors.txt.gz"]),
        "stage2_source": digest_bytes(raw["stage2_source.txt.gz"]),
        "stage2_survivor": digest_bytes(raw["stage2_survivors.txt.gz"]),
        "class_source": digest_bytes(raw["class_source.txt.gz"]),
        "class_survivor": digest_bytes(raw["class_survivors.txt.gz"]),
    }
    exact_sha256_table(coverage.get("source_survivor_sha256"), expected_mapping,
                       "coverage.source_survivor_sha256")
    return CoverageLedger(
        representatives=representatives,
        stage1_survivors=stage1_survivors,  # type: ignore[arg-type]
        stage2_survivors=stage2_survivors,  # type: ignore[arg-type]
        class_survivors=class_survivors,  # type: ignore[arg-type]
        raw=raw,
        counts=expected_counts,
    )


@dataclass
class Variable:
    name: tuple[object, ...]
    lower: int = 0
    upper: Optional[int] = None
    integral: bool = False


@dataclass
class LinearRelaxation:
    variables: list[Variable] = field(default_factory=list)
    equations: list[tuple[dict[int, int], int]] = field(default_factory=list)
    inequalities: list[tuple[dict[int, int], int]] = field(default_factory=list)

    def variable(self, name: tuple[object, ...], lower: int = 0,
                 upper: Optional[int] = None, integral: bool = False) -> int:
        demand(type(lower) is int, f"noninteger lower bound for {name}")
        demand(upper is None or type(upper) is int, f"noninteger upper bound for {name}")
        demand(upper is None or lower <= upper, f"inconsistent bounds for {name}")
        index = len(self.variables)
        self.variables.append(Variable(name, lower, upper, integral))
        return index

    def equal(self, coefficients: dict[int, int], rhs: int) -> None:
        self.equations.append((clean_row(coefficients, len(self.variables)), integer(rhs, "equation rhs")))

    def at_most(self, coefficients: dict[int, int], rhs: int) -> None:
        self.inequalities.append((clean_row(coefficients, len(self.variables)), integer(rhs, "inequality rhs")))

    def standard_rows(self) -> tuple[list[dict[int, int]], list[int], list[bool]]:
        rows: list[dict[int, int]] = []
        right: list[int] = []
        has_slack: list[bool] = []
        for coefficients, rhs in self.equations:
            rows.append(coefficients)
            right.append(rhs - sum(a * self.variables[j].lower for j, a in coefficients.items()))
            has_slack.append(False)
        for coefficients, rhs in self.inequalities:
            rows.append(coefficients)
            right.append(rhs - sum(a * self.variables[j].lower for j, a in coefficients.items()))
            has_slack.append(True)
        for j, variable in enumerate(self.variables):
            if variable.upper is not None:
                demand(variable.lower <= variable.upper, f"empty bound interval for {variable.name}")
                rows.append({j: 1})
                right.append(variable.upper - variable.lower)
                has_slack.append(True)
        return rows, right, has_slack

    def branched(self, variable_index: int, floor: int, left: bool) -> "LinearRelaxation":
        demand(0 <= variable_index < len(self.variables), "branch variable index out of range")
        copied = LinearRelaxation(
            variables=[Variable(v.name, v.lower, v.upper, v.integral) for v in self.variables],
            equations=list(self.equations),
            inequalities=list(self.inequalities),
        )
        target = copied.variables[variable_index]
        if left:
            target.upper = floor if target.upper is None else min(target.upper, floor)
        else:
            target.lower = max(target.lower, floor + 1)
        demand(target.upper is None or target.lower <= target.upper, "branch creates empty encoded interval")
        return copied


def clean_row(coefficients: dict[int, int], variable_count: int) -> dict[int, int]:
    result: dict[int, int] = {}
    for index, coefficient in coefficients.items():
        demand(type(index) is int and 0 <= index < variable_count, f"row variable index out of range: {index}")
        demand(type(coefficient) is int, f"noninteger row coefficient at {index}")
        if coefficient:
            result[index] = result.get(index, 0) + coefficient
            if result[index] == 0:
                del result[index]
    return result


def increment(row: dict[int, int], index: int, amount: int) -> None:
    if amount:
        row[index] = row.get(index, 0) + amount
        if row[index] == 0:
            del row[index]


def degree_classes(seq: tuple[int, ...]) -> tuple[Counter[int], list[int]]:
    validate_sequence(seq, "model sequence", 2, 17)
    demand(sum(seq) == 190 and sum(d * d for d in seq) == 2280, "model sequence violates degree moments")
    counts: Counter[int] = Counter(seq)
    return counts, sorted(counts)


def install_spectral_block(model: LinearRelaxation, counts: Counter[int], degrees: list[int]) -> dict[tuple[int, int], int]:
    weights: dict[tuple[int, int], int] = {}
    for degree in degrees:
        for eigenvalue in NONZERO_EIGENVALUES:
            weights[degree, eigenvalue] = model.variable(("Y", degree, eigenvalue))
    for degree in degrees:
        multiplicity = counts[degree]
        model.equal({weights[degree, k]: 1 for k in NONZERO_EIGENVALUES}, 19 * multiplicity)
        model.equal({weights[degree, k]: k for k in NONZERO_EIGENVALUES}, 20 * multiplicity * degree)
        model.equal({weights[degree, k]: k * k for k in NONZERO_EIGENVALUES},
                    20 * multiplicity * (degree * degree + degree))
    for eigenvalue in NONZERO_EIGENVALUES:
        model.equal({weights[degree, eigenvalue]: 1 for degree in degrees}, 20)
    return weights


def build_stage_model(seq: tuple[int, ...], include_local_third_moments: bool) -> LinearRelaxation:
    counts, degrees = degree_classes(seq)
    model = LinearRelaxation()
    weights = install_spectral_block(model, counts, degrees)
    neighbor_sums: dict[int, int] = {}
    if include_local_third_moments:
        # These variables must follow all Y variables to reproduce the declared
        # standard-form row/column convention used by the certificate format.
        # Rebuild the variable block, because install_spectral_block has already
        # installed equations but variable order remains available for extension.
        for degree in degrees:
            remaining = list(seq)
            remaining.remove(degree)
            remaining.sort()
            multiplicity = counts[degree]
            neighbor_sums[degree] = model.variable(
                ("S", degree),
                multiplicity * sum(remaining[:degree]),
                multiplicity * sum(remaining[-degree:]),
            )

        for degree in degrees:
            multiplicity = counts[degree]
            base = degree ** 3 + 2 * degree * degree
            cube = {weights[degree, k]: k ** 3 for k in NONZERO_EIGENVALUES}
            s_index = neighbor_sums[degree]

            model.at_most({j: -a for j, a in cube.items()}, -20 * multiplicity * (base + degree))
            model.at_most(dict(cube), 20 * multiplicity * (base + degree * (20 - degree)))
            row = dict(cube)
            increment(row, s_index, -20)
            model.at_most(row, 20 * multiplicity * base)
            row = {j: -a for j, a in cube.items()}
            increment(row, s_index, 20)
            model.at_most(row, 40 * multiplicity * math.comb(degree, 2) - 20 * multiplicity * base)

            complement_crossing_floor = 190 - 2 * math.comb(19 - degree, 2)
            row = {j: -a for j, a in cube.items()}
            increment(row, s_index, -20)
            model.at_most(row, -20 * multiplicity * (complement_crossing_floor + base))
            row = dict(cube)
            increment(row, s_index, 20)
            model.at_most(row, 20 * multiplicity * (190 + base))

        model.equal({neighbor_sums[d]: 1 for d in degrees}, 2280)
    return model


def triple_capacity(triple: tuple[int, int, int], counts: Counter[int]) -> int:
    capacity = 1
    for degree, requested in Counter(triple).items():
        if requested > counts[degree]:
            return 0
        capacity *= math.comb(counts[degree], requested)
    return capacity


def build_class_model(seq: tuple[int, ...], triangles: int) -> LinearRelaxation:
    counts, degrees = degree_classes(seq)
    demand(type(triangles) is int and 127 <= triangles <= 348, "class triangle count out of derived range")
    demand(sum(d ** 3 for d in seq) - 6 * triangles == 29260, "class triangle identity fails")
    model = LinearRelaxation()

    # Install variables in certificate-format order: Y, E, T, C.
    weights: dict[tuple[int, int], int] = {}
    for degree in degrees:
        for eigenvalue in NONZERO_EIGENVALUES:
            weights[degree, eigenvalue] = model.variable(("Y", degree, eigenvalue))
    pairs = [(a, b) for i, a in enumerate(degrees) for b in degrees[i:]]
    edge_count: dict[tuple[int, int], int] = {}
    for a, b in pairs:
        capacity = math.comb(counts[a], 2) if a == b else counts[a] * counts[b]
        edge_count[a, b] = model.variable(("E", a, b), 0, capacity, True)
    triples = [
        triple for triple in combinations_with_replacement(degrees, 3)
        if triple_capacity(triple, counts) > 0
    ]
    graph_triangles: dict[tuple[int, int, int], int] = {}
    complement_triangles: dict[tuple[int, int, int], int] = {}
    for triple in triples:
        graph_triangles[triple] = model.variable(("T",) + triple, 0, triple_capacity(triple, counts), True)
    for triple in triples:
        complement_triangles[triple] = model.variable(("C",) + triple, 0, triple_capacity(triple, counts), True)

    # Spectral-weight equalities, written separately so variable layout is not
    # coupled to the Stage builders.
    for degree in degrees:
        multiplicity = counts[degree]
        model.equal({weights[degree, k]: 1 for k in NONZERO_EIGENVALUES}, 19 * multiplicity)
        model.equal({weights[degree, k]: k for k in NONZERO_EIGENVALUES}, 20 * multiplicity * degree)
        model.equal({weights[degree, k]: k * k for k in NONZERO_EIGENVALUES},
                    20 * multiplicity * (degree * degree + degree))
    for eigenvalue in NONZERO_EIGENVALUES:
        model.equal({weights[d, eigenvalue]: 1 for d in degrees}, 20)

    # Degree-class stub counts.
    for degree in degrees:
        row: dict[int, int] = {}
        for a, b in pairs:
            if a == degree and b == degree:
                increment(row, edge_count[a, b], 2)
            elif a == degree or b == degree:
                increment(row, edge_count[a, b], 1)
        model.equal(row, counts[degree] * degree)

    model.equal({graph_triangles[z]: 1 for z in triples}, triangles)
    model.equal({complement_triangles[z]: 1 for z in triples}, 475 - triangles)

    # Classwise diagonal L^3 identity for G.
    for degree in degrees:
        multiplicity = counts[degree]
        base = degree ** 3 + 2 * degree * degree
        row = {weights[degree, k]: k ** 3 for k in NONZERO_EIGENVALUES}
        for a, b in pairs:
            neighbor_degree_contribution = (
                2 * degree if a == b == degree
                else b if a == degree
                else a if b == degree
                else 0
            )
            increment(row, edge_count[a, b], -20 * neighbor_degree_contribution)
        for triple in triples:
            increment(row, graph_triangles[triple], 40 * triple.count(degree))
        model.equal(row, 20 * multiplicity * base)

    # The same identity in the complement, expressed using original classes.
    for degree in degrees:
        multiplicity = counts[degree]
        complement_degree = 19 - degree
        base = complement_degree ** 3 + 2 * complement_degree * complement_degree
        row = {weights[degree, 20 - k]: k ** 3 for k in NONZERO_EIGENVALUES}
        constant = 0
        for a, b in pairs:
            capacity = math.comb(counts[a], 2) if a == b else counts[a] * counts[b]
            contribution = (
                2 * (19 - degree) if a == b == degree
                else 19 - b if a == degree
                else 19 - a if b == degree
                else 0
            )
            if contribution:
                constant += contribution * capacity
                increment(row, edge_count[a, b], 20 * contribution)
        for triple in triples:
            increment(row, complement_triangles[triple], 40 * triple.count(degree))
        model.equal(row, 20 * multiplicity * base + 20 * constant)

    # Edge/common-neighbor and complement-nonedge/common-neighbor capacities.
    for a, b in pairs:
        capacity = math.comb(counts[a], 2) if a == b else counts[a] * counts[b]
        graph_row: dict[int, int] = {}
        complement_row: dict[int, int] = {}
        for triple in triples:
            multiplicity = Counter(triple)
            incidences = math.comb(multiplicity[a], 2) if a == b else multiplicity[a] * multiplicity[b]
            increment(graph_row, graph_triangles[triple], incidences)
            increment(complement_row, complement_triangles[triple], incidences)
        increment(graph_row, edge_count[a, b], -(min(a, b) - 1))
        model.at_most(graph_row, 0)
        complement_limit = 18 - max(a, b)
        increment(complement_row, edge_count[a, b], complement_limit)
        model.at_most(complement_row, complement_limit * capacity)

    # Wedge capacities within each degree class.
    for degree in degrees:
        graph_row: dict[int, int] = {}
        complement_row: dict[int, int] = {}
        for triple in triples:
            incidences = triple.count(degree)
            increment(graph_row, graph_triangles[triple], incidences)
            increment(complement_row, complement_triangles[triple], incidences)
        model.at_most(graph_row, counts[degree] * math.comb(degree, 2))
        model.at_most(complement_row, counts[degree] * math.comb(19 - degree, 2))
    return model


def audit_sparse_farkas(model: LinearRelaxation, raw_certificate: object, label: str) -> int:
    certificate = array(raw_certificate, f"{label}.certificate")
    rows, right, has_slack = model.standard_rows()
    column_sums = [0] * len(model.variables)
    scalar = 0
    previous_index = -1
    for position, raw_term in enumerate(certificate):
        term = array(raw_term, f"{label}.term[{position}]")
        demand(len(term) == 2, f"{label}.term[{position}]: expected [row,coefficient]")
        row_index = integer(term[0], f"{label}.term[{position}].row")
        multiplier = integer(term[1], f"{label}.term[{position}].coefficient")
        demand(previous_index < row_index < len(rows),
               f"{label}: row indices must be unique, strictly increasing, and in range: {row_index}")
        demand(multiplier != 0, f"{label}: zero multiplier is not canonical")
        if has_slack[row_index]:
            demand(multiplier >= 0, f"{label}: negative multiplier on a +slack row {row_index}")
        scalar += multiplier * right[row_index]
        for variable_index, coefficient in rows[row_index].items():
            column_sums[variable_index] += multiplier * coefficient
        previous_index = row_index
    bad = next(
        ((j, value, model.variables[j].name) for j, value in enumerate(column_sums) if value < 0),
        None,
    )
    demand(bad is None, f"{label}: negative entry in B^T z: {bad}")
    demand(scalar < 0, f"{label}: h^T z is not negative: {scalar}")
    return len(certificate)


def certificate_shards(certs_dir: Path, stage: str) -> list[Path]:
    pattern = re.compile(re.escape(stage) + r"_[0-9]{4}\.json\.gz\Z")
    shards = sorted(path for path in certs_dir.iterdir() if path.is_file() and pattern.fullmatch(path.name))
    expected = [f"{stage}_{i:04d}.json.gz" for i in range(len(shards))]
    demand([path.name for path in shards] == expected, f"{stage}: shard numbering is not contiguous")
    demand(shards, f"{stage}: no certificate shards")
    return shards


@dataclass
class StageResult:
    source_count: int
    survivor_count: int
    leaf_count: int
    support_sum: int
    support_min: int
    support_max: int


def verify_certificate_stage(
    root: Path,
    stage: str,
    source: list[tuple[tuple[int, ...], int]],
    survivors: list[tuple[tuple[int, ...], int]],
    model_factory: Callable[[tuple[int, ...], int], LinearRelaxation],
) -> StageResult:
    certs_dir = root / "certs"
    shards = certificate_shards(certs_dir, stage)
    survivor_set = set(survivors)
    expected_indices = [index for index, item in enumerate(source) if item not in survivor_set]
    seen_indices: list[int] = []
    support_sum = 0
    support_min: Optional[int] = None
    support_max = 0

    for shard in shards:
        document = dictionary(read_json(shard, compressed=True), shard.name)
        demand(set(document) == {"format", "stage", "records"}, f"{shard.name}: unexpected object keys")
        demand(document.get("format") == CERT_FORMAT, f"{shard.name}: wrong certificate format")
        demand(document.get("stage") == stage, f"{shard.name}: wrong stage label")
        records = array(document.get("records"), f"{shard.name}.records")
        for record_number, raw_record in enumerate(records):
            record = array(raw_record, f"{shard.name}.record[{record_number}]")
            demand(len(record) == 2, f"{shard.name}.record[{record_number}]: expected [source_index,certificate]")
            source_index = integer(record[0], f"{shard.name}.record[{record_number}].source_index")
            demand(0 <= source_index < len(source), f"{stage}: source index out of range: {source_index}")
            demand(not seen_indices or source_index > seen_indices[-1],
                   f"{stage}: duplicate or non-increasing source index: {source_index}")
            seq, triangles = source[source_index]
            model = model_factory(seq, triangles)
            support = audit_sparse_farkas(model, record[1], f"{stage}[{source_index}]")
            support_sum += support
            support_max = max(support_max, support)
            support_min = support if support_min is None else min(support_min, support)
            seen_indices.append(source_index)

    demand(seen_indices == expected_indices,
           f"{stage}: exact leaf coverage differs: got {len(seen_indices)}, expected {len(expected_indices)}")
    demand(support_min is not None, f"{stage}: empty certificate stage")
    result = StageResult(
        source_count=len(source),
        survivor_count=len(survivors),
        leaf_count=len(seen_indices),
        support_sum=support_sum,
        support_min=support_min,
        support_max=support_max,
    )

    summary = dictionary(read_json(certs_dir / f"{stage}_summary.json"), f"{stage}_summary.json")
    master = dictionary(read_json(certs_dir / "SUMMARY.json"), "SUMMARY.json")
    demand(summary == master.get(stage), f"{stage}: stage and master summaries differ")
    demanded_summary = {
        "stage": stage,
        "source_count": result.source_count,
        "survivor_count": result.survivor_count,
        "leaf_count": result.leaf_count,
        "support_sum": result.support_sum,
        "support_min": result.support_min,
        "support_max": result.support_max,
        "shards": [path.name for path in shards],
    }
    for key, expected in demanded_summary.items():
        if type(expected) is int:
            integer(summary.get(key), f"{stage}_summary.{key}")
        demand(summary.get(key) == expected, f"{stage}: summary field {key} differs")
    expected_summary_fields = {
        "stage", "source_count", "survivor_count", "leaf_count", "support_sum",
        "support_min", "support_max", "shards", "mode_counts", "elapsed_seconds",
    }
    demand(set(summary) == expected_summary_fields, f"{stage}: missing or unexpected summary fields")
    shard_values = array(summary.get("shards"), f"{stage}_summary.shards")
    demand(all(type(name) is str for name in shard_values), f"{stage}: non-string shard name")
    modes = dictionary(summary.get("mode_counts"), f"{stage}_summary.mode_counts")
    demand(modes, f"{stage}: empty mode-count table")
    mode_total = 0
    for mode, value in modes.items():
        demand(type(mode) is str and mode != "", f"{stage}: noncanonical mode name")
        count = integer(value, f"{stage}_summary.mode_counts.{mode}")
        demand(count >= 0, f"{stage}: negative mode count for {mode}")
        mode_total += count
    demand(mode_total == result.leaf_count, f"{stage}: mode counts do not sum to leaf count")
    elapsed = summary.get("elapsed_seconds")
    demand(type(elapsed) in (int, float) and math.isfinite(elapsed) and elapsed >= 0,
           f"{stage}: noncanonical elapsed_seconds")
    return result


def verify_roots_and_branches(
    root: Path,
    class_source: list[tuple[tuple[int, ...], int]],
    roots: list[tuple[tuple[int, ...], int]],
) -> tuple[StageResult, int]:
    class_result = verify_certificate_stage(root, "class", class_source, roots, build_class_model)
    roots_doc = dictionary(read_json(root / "data" / "final_integer_roots.json"), "final_integer_roots.json")
    demand(set(roots_doc) == {"format", "roots"},
           "final_integer_roots.json has missing or unexpected fields")
    demand(roots_doc.get("format") == "s20-final-integer-roots-v1",
           "wrong root metadata format")
    metadata = array(roots_doc.get("roots"), "final_integer_roots.roots")
    branch_doc = dictionary(read_json(root / "certs" / "branch_leaves.json.gz", compressed=True),
                            "branch_leaves.json.gz")
    demand(set(branch_doc) == {"format", "leaf_count", "roots"}, "unexpected branch document keys")
    demand(branch_doc.get("format") == "s20-branch-farkas-v1", "wrong branch certificate format")
    branch_roots = array(branch_doc.get("roots"), "branch.roots")
    demand(len(branch_roots) == len(metadata) == len(roots) == 2, "branch/root count differs from two")
    branch_leaves = 0
    seen_root_indices: set[int] = set()

    for position, (root_item, raw_meta, raw_branch) in enumerate(zip(roots, metadata, branch_roots)):
        meta = dictionary(raw_meta, f"root metadata[{position}]")
        demand(parse_final_root(meta, position) == root_item, f"root {position}: strict metadata target mismatch")
        branch = dictionary(raw_branch, f"branch root[{position}]")
        demand(set(branch) == BRANCH_ROOT_KEYS,
               f"branch root[{position}]: missing or unexpected fields")
        root_index = integer(branch.get("root_index"), f"branch[{position}].root_index")
        demand(root_index == position and root_index not in seen_root_indices,
               f"duplicate or misplaced branch root index: {root_index}")
        seen_root_indices.add(root_index)
        demand(meta.get("root_index") == root_index, f"root {position}: metadata index mismatch")

        seq, triangles = root_item
        branch_seq = tuple(integer(x, f"branch[{position}].degree") for x in array(branch.get("sequence"), "branch.sequence"))
        branch_triangles = integer(branch.get("triangles"), f"branch[{position}].triangles")
        demand((branch_seq, branch_triangles) == (seq, triangles), f"root {position}: branch target mismatch")
        model = build_class_model(seq, triangles)
        variable_index = integer(branch.get("variable_index"), f"branch[{position}].variable_index")
        floor = integer(branch.get("floor"), f"branch[{position}].floor")
        demand(0 <= variable_index < len(model.variables), f"root {position}: branch variable out of range")
        variable = model.variables[variable_index]
        demand(variable.integral, f"root {position}: branch variable is not integral")
        declared_name = parse_edge_variable_name(branch.get("variable_name"), f"branch[{position}].variable_name")
        demand(variable.name == declared_name, f"root {position}: variable name/index mismatch")
        demand(meta.get("branch_variable_index") == variable_index, f"root {position}: metadata variable index mismatch")
        demand(parse_edge_variable_name(meta.get("branch_variable_name"), "metadata variable name") == variable.name,
               f"root {position}: metadata variable name mismatch")
        demand(meta.get("floor") == floor, f"root {position}: metadata floor mismatch")
        demand(variable.lower <= floor and (variable.upper is None or floor < variable.upper),
               f"root {position}: split is outside the parent integer interval")

        left = model.branched(variable_index, floor, True)
        right = model.branched(variable_index, floor, False)
        demand(left.variables[variable_index].upper == floor, f"root {position}: bad left child")
        demand(right.variables[variable_index].lower == floor + 1, f"root {position}: bad right child")
        audit_sparse_farkas(left, branch.get("left_cert"), f"branch[{position}].left")
        audit_sparse_farkas(right, branch.get("right_cert"), f"branch[{position}].right")
        branch_leaves += 2

    branch_declared_leaves = integer(branch_doc.get("leaf_count"), "branch.leaf_count")
    demand(branch_declared_leaves == branch_leaves == 4, "branch leaf count mismatch")
    return class_result, branch_leaves


def audit_certificate_directory(root: Path) -> None:
    certs = root / "certs"
    demand(certs.is_dir(), "missing certs directory")
    allowed_fixed = {
        "SUMMARY.json", "stage1_summary.json", "stage2_summary.json", "class_summary.json",
        "branch_leaves.json.gz",
    }
    shard_pattern = re.compile(r"(?:stage1|stage2|class)_[0-9]{4}\.json\.gz\Z")
    unexpected = sorted(
        path.name for path in certs.iterdir()
        if path.is_symlink() or not path.is_file()
        or (path.name not in allowed_fixed and shard_pattern.fullmatch(path.name) is None)
    )
    demand(not unexpected, f"unexpected certificate-directory entries: {unexpected}")


def run_verification(root: Path) -> dict[str, object]:
    started = time.monotonic()
    demand(root.is_dir(), f"release root is not a directory: {root}")
    demand(not root.is_symlink(), "release root must not be a symlink")
    data_dir = root / "data"
    certs_dir = root / "certs"
    demand(data_dir.is_dir() and not data_dir.is_symlink(),
           "release data directory must be a real directory")
    demand(certs_dir.is_dir() and not certs_dir.is_symlink(),
           "release certs directory must be a real directory")
    audit_certificate_directory(root)
    constants = derive_constants()
    bounds = check_params(root, constants)
    ledger = verify_data(root, constants)

    stage1 = verify_certificate_stage(
        root, "stage1", ledger.representatives, ledger.stage1_survivors,
        lambda seq, unused_triangles: build_stage_model(seq, False),
    )
    stage2 = verify_certificate_stage(
        root, "stage2", ledger.stage1_survivors, ledger.stage2_survivors,
        lambda seq, unused_triangles: build_stage_model(seq, True),
    )
    class_result, branch_leaves = verify_roots_and_branches(
        root, ledger.stage2_survivors, ledger.class_survivors,
    )
    total = stage1.leaf_count + stage2.leaf_count + class_result.leaf_count + branch_leaves
    demand(total == ledger.counts["total_leaves"] == 80124, f"total exact leaf count mismatch: {total}")

    master = dictionary(read_json(root / "certs" / "SUMMARY.json"), "SUMMARY.json")
    demand(set(master) == {"format", "stage1", "stage2", "class", "branch", "total_leaf_count"},
           "master summary has missing or unexpected fields")
    demand(master.get("format") == "s20-certificate-generation-summary-v1", "wrong master summary format")
    demand(integer(master.get("total_leaf_count"), "SUMMARY.total_leaf_count") == total,
           "master total leaf count differs")
    exact_integer_table(master.get("branch"), {"roots": 2, "leaves": 4}, "SUMMARY.branch")

    def stage_json(value: StageResult) -> dict[str, int]:
        return {
            "source": value.source_count,
            "survivors": value.survivor_count,
            "leaves": value.leaf_count,
            "support_sum": value.support_sum,
            "support_min": value.support_min,
            "support_max": value.support_max,
        }

    return {
        "status": "INDEPENDENTLY_VERIFIED_UNSAT",
        "n": N,
        "spectrum": list(constants.spectrum),
        "derived_bounds": bounds,
        "moment_sequences": ledger.counts["moment"],
        "graphical_sequences": ledger.counts["graphical"],
        "base_sequences": ledger.counts["base"],
        "complement_representatives": ledger.counts["complement_representatives"],
        "stage1": stage_json(stage1),
        "stage2": stage_json(stage2),
        "class": stage_json(class_result),
        "branch_roots": 2,
        "branch_leaves": branch_leaves,
        "total_farkas_leaves": total,
        "uncovered": 0,
        "elapsed_seconds": round(time.monotonic() - started, 6),
    }


def parse_arguments(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("release_root", type=Path, help="path to an extracted S20 release root")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_arguments(argv)
    try:
        root = args.release_root.expanduser()
        if not root.is_absolute():
            root = Path.cwd() / root
        result = run_verification(root)
    except Rejection as exc:
        print(f"INDEPENDENT_VERIFICATION_FAILED: {exc}", file=sys.stderr)
        return 1
    except (OSError, EOFError, ValueError, TypeError, KeyError, OverflowError) as exc:
        print(f"INDEPENDENT_VERIFICATION_FAILED: malformed input: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
