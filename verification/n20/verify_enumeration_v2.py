#!/usr/bin/env python3
"""Separately structured internal enumeration audit for the S20 release.

Usage::

    python3 verify_enumeration_v2.py EXTRACTED_RELEASE_ROOT

This file deliberately does not import or execute any code from the release.
Its enumeration is also structurally different from both implementations in
the release:

* the release verifier recurses over degree multiplicities;
* its auxiliary auditor uses a position-by-position feasibility DP;
* this auditor splits the degree alphabet in two, enumerates each half with
  ``itertools.combinations_with_replacement``, and hash-joins the two moment
  keys (a meet-in-the-middle construction).

Graphicality is checked by repeatedly laying off the *smallest* positive
degree and reducing the largest remaining degrees (the Kleitman--Wang layoff
theorem).  Thus it uses neither the release verifier's Erdos--Gallai scan nor
the auxiliary auditor's largest-degree Havel--Hakimi implementation.

Only Python's standard library is used.  All checks raise explicit failures,
so running with ``python -O`` does not disable any verification.
"""

from __future__ import annotations

from collections import defaultdict
from itertools import combinations_with_replacement
from pathlib import Path
import gzip
import hashlib
import json
import math
import sys
import time
from typing import Iterable


TARGET_N = 20


class AuditFailure(RuntimeError):
    """A failed proof-artifact check, as opposed to a Python assertion."""


def require(condition: bool, message: object) -> None:
    if not condition:
        raise AuditFailure(str(message))


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def derive_parameters(n: int, spectrum: tuple[int, ...]) -> dict[str, object]:
    """Derive every release parameter used by the enumeration.

    No numerical moment, degree, or triangle bound is taken from PARAMS.json.
    The degree interval follows from the local spectral-measure identities

        sum k*w_k = d,       sum k^2*w_k = d^2+d,

    and k^2 <= n*k-(n-1) for 1 <= k <= n-1.  The triangle lower bound follows
    by summing c_uv >= d_u+d_v-n over edges; the upper bound applies the same
    inequality to the complement.
    """
    require(n >= 2, "n must be at least two")
    require(spectrum == tuple(range(n)), "target spectrum is not range(n)")
    require(spectrum.count(0) == 1, "target must have a simple zero eigenvalue")

    trace1 = sum(spectrum)
    trace2 = sum(k * k for k in spectrum)
    trace3 = sum(k**3 for k in spectrum)
    trace4 = sum(k**4 for k in spectrum)
    require(trace1 % 2 == 0, "trace(L) is not even")
    edge_count = trace1 // 2
    degree_square_sum = trace2 - trace1
    triangle_offset = trace3 - 3 * degree_square_sum

    # Pointwise inequality used in the spectral-measure degree bound.
    require(
        all(k * k <= n * k - (n - 1) for k in spectrum[1:]),
        "spectral degree-bound inequality failed",
    )
    allowed_degrees = tuple(
        d
        for d in range(n)
        if n * d * d - n * (n - 1) * d + (n - 1) ** 2 <= 0
    )
    require(allowed_degrees, "derived degree interval is empty")
    require(
        allowed_degrees == tuple(range(allowed_degrees[0], allowed_degrees[-1] + 1)),
        "derived degree values do not form an interval",
    )
    degree_min = allowed_degrees[0]
    degree_max = allowed_degrees[-1]

    triangle_lower_numerator = degree_square_sum - n * edge_count
    triangle_min = -(-triangle_lower_numerator // 3)
    complement_wedge_twice = (n - 1) * trace1 - degree_square_sum
    require(complement_wedge_twice % 2 == 0, "complement wedge total is nonintegral")
    triangle_complement_total = (
        math.comb(n, 3) - complement_wedge_twice // 2
    )
    triangle_max = triangle_complement_total - triangle_min

    complement_spectrum = tuple(sorted((0,) + tuple(n - k for k in spectrum[1:])))
    require(complement_spectrum == spectrum, "target spectrum is not complement invariant")
    nonzero_product = math.prod(spectrum[1:])
    require(nonzero_product % n == 0, "Matrix--Tree quotient is nonintegral")

    return {
        "n": n,
        "spectrum": list(spectrum),
        "edge_count": edge_count,
        "degree_sum": trace1,
        "degree_square_sum": degree_square_sum,
        "triangle_offset": triangle_offset,
        "trace_L4": trace4,
        "spanning_tree_count": nonzero_product // n,
        "degree_min": degree_min,
        "degree_max": degree_max,
        "triangle_min": triangle_min,
        "triangle_max": triangle_max,
        "triangle_complement_total": triangle_complement_total,
    }


def viable_other_half(
    count: int,
    total: int,
    squares: int,
    smallest: int,
    largest: int,
) -> bool:
    """Cheap necessary conditions for a half-multiset moment key."""
    if count == 0:
        return total == 0 and squares == 0
    if total < count * smallest or total > count * largest:
        return False
    if squares < count * smallest * smallest or squares > count * largest * largest:
        return False
    # Cauchy--Schwarz is exact integer arithmetic here.
    return squares * count >= total * total


def enumerate_moment_sequences(params: dict[str, object]) -> tuple[list[tuple[int, ...]], dict[str, int]]:
    """Meet-in-the-middle enumeration of sorted sequences with two moments."""
    n = int(params["n"])
    degree_min = int(params["degree_min"])
    degree_max = int(params["degree_max"])
    degree_sum = int(params["degree_sum"])
    degree_square_sum = int(params["degree_square_sum"])

    split = (degree_min + degree_max + 1) // 2
    low_values = tuple(range(degree_min, split))
    high_values = tuple(range(split, degree_max + 1))
    require(low_values and high_values, "degree alphabet split is degenerate")

    # Each high tuple is indexed by (length, sum, square sum).  Conditions on
    # the complementary low tuple reduce the hash table substantially but do
    # not discard any possible full sequence.
    high_by_key: dict[tuple[int, int, int], list[tuple[int, ...]]] = defaultdict(list)
    retained_high = 0
    for high_count in range(n + 1):
        low_count = n - high_count
        for high in combinations_with_replacement(high_values, high_count):
            high_sum = sum(high)
            needed_low_sum = degree_sum - high_sum
            high_squares = sum(d * d for d in high)
            needed_low_squares = degree_square_sum - high_squares
            if not viable_other_half(
                low_count,
                needed_low_sum,
                needed_low_squares,
                low_values[0],
                low_values[-1],
            ):
                continue
            high_by_key[(high_count, high_sum, high_squares)].append(high)
            retained_high += 1

    sequences: list[tuple[int, ...]] = []
    matched_low = 0
    for low_count in range(n + 1):
        high_count = n - low_count
        for low in combinations_with_replacement(low_values, low_count):
            low_sum = sum(low)
            low_squares = sum(d * d for d in low)
            key = (
                high_count,
                degree_sum - low_sum,
                degree_square_sum - low_squares,
            )
            matches = high_by_key.get(key)
            if matches is None:
                continue
            matched_low += 1
            sequences.extend(low + high for high in matches)

    sequences.sort()
    require(
        all(sequences[i - 1] < sequences[i] for i in range(1, len(sequences))),
        "meet-in-the-middle enumeration produced a duplicate or ordering error",
    )
    for sequence in sequences:
        require(len(sequence) == n, f"wrong sequence length: {sequence}")
        require(tuple(sorted(sequence)) == sequence, f"nonmonotone sequence: {sequence}")
        require(sum(sequence) == degree_sum, f"first-moment failure: {sequence}")
        require(
            sum(d * d for d in sequence) == degree_square_sum,
            f"second-moment failure: {sequence}",
        )
    return sequences, {
        "alphabet_split": split,
        "retained_high_tuples": retained_high,
        "high_hash_keys": len(high_by_key),
        "matched_low_tuples": matched_low,
    }


def is_graphical_kleitman_wang(sequence: tuple[int, ...]) -> bool:
    """Test graphicality by smallest-degree Kleitman--Wang layoff."""
    if sum(sequence) % 2:
        return False
    work = list(sequence)
    while work:
        first_positive = 0
        while first_positive < len(work) and work[first_positive] == 0:
            first_positive += 1
        if first_positive:
            del work[:first_positive]
        if not work:
            return True
        degree = work.pop(0)  # deliberately select the smallest positive term
        if degree < 0 or degree > len(work):
            return False
        start = len(work) - degree
        for index in range(start, len(work)):
            work[index] -= 1
            if work[index] < 0:
                return False
        work.sort()
    return True


def sequence_bytes(sequences: Iterable[tuple[int, ...]]) -> bytes:
    output = bytearray()
    for sequence in sequences:
        output.extend(" ".join(map(str, sequence)).encode("ascii"))
        output.append(10)
    return bytes(output)


def sequence_triangle_bytes(items: Iterable[tuple[tuple[int, ...], int]]) -> bytes:
    output = bytearray()
    for sequence, triangles in items:
        output.extend(" ".join(map(str, sequence)).encode("ascii"))
        output.extend(b"|")
        output.extend(str(triangles).encode("ascii"))
        output.append(10)
    return bytes(output)


def complement_pair_bytes(
    representatives: Iterable[tuple[tuple[int, ...], int]],
    n: int,
    triangle_total: int,
) -> bytes:
    output = bytearray()
    for sequence, triangles in representatives:
        mate = (
            tuple(sorted(n - 1 - degree for degree in sequence)),
            triangle_total - triangles,
        )
        output.extend(" ".join(map(str, sequence)).encode("ascii"))
        output.extend(b"|")
        output.extend(str(triangles).encode("ascii"))
        output.extend(b"||")
        output.extend(" ".join(map(str, mate[0])).encode("ascii"))
        output.extend(b"|")
        output.extend(str(mate[1]).encode("ascii"))
        output.append(10)
    return bytes(output)


def load_json(path: Path) -> object:
    require(path.is_file() and not path.is_symlink(), f"missing/unsafe JSON file: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise AuditFailure(f"cannot read JSON {path}: {exc}") from exc


def read_gzip(path: Path) -> bytes:
    require(path.is_file() and not path.is_symlink(), f"missing/unsafe gzip file: {path}")
    try:
        with gzip.open(path, "rb") as stream:
            return stream.read()
    except (OSError, EOFError) as exc:
        raise AuditFailure(f"cannot read gzip file {path}: {exc}") from exc


def verify_exact_data_file(
    data_dir: Path,
    coverage_files: dict[str, object],
    name: str,
    generated: bytes,
) -> dict[str, object]:
    path = data_dir / name
    actual = read_gzip(path)
    require(actual == generated, f"exact uncompressed byte mismatch: data/{name}")
    metadata = coverage_files.get(name)
    require(isinstance(metadata, dict), f"coverage metadata absent for {name}")
    require(metadata.get("count") == generated.count(b"\n"), f"coverage count mismatch: {name}")
    require(metadata.get("uncompressed_bytes") == len(generated), f"coverage size mismatch: {name}")
    require(metadata.get("sha256_uncompressed") == sha256(generated), f"coverage raw hash mismatch: {name}")
    require(metadata.get("sha256_compressed") == sha256_file(path), f"coverage gzip hash mismatch: {name}")
    return {
        "count": generated.count(b"\n"),
        "uncompressed_bytes": len(generated),
        "sha256_uncompressed": sha256(generated),
        "sha256_compressed": sha256_file(path),
    }


def audit(release_root: Path) -> dict[str, object]:
    started = time.monotonic()
    require(release_root.is_dir() and not release_root.is_symlink(), f"not a safe release root: {release_root}")
    data_dir = release_root / "data"
    require(data_dir.is_dir() and not data_dir.is_symlink(), f"missing/unsafe data directory: {data_dir}")

    spectrum = tuple(range(TARGET_N))
    params = derive_parameters(TARGET_N, spectrum)
    released_params = load_json(release_root / "PARAMS.json")
    require(released_params == params, f"PARAMS.json differs from independent derivation: {released_params!r}")

    moment, enumeration_stats = enumerate_moment_sequences(params)
    graphical = [sequence for sequence in moment if is_graphical_kleitman_wang(sequence)]

    triangle_offset = int(params["triangle_offset"])
    triangle_min = int(params["triangle_min"])
    triangle_max = int(params["triangle_max"])
    base: list[tuple[tuple[int, ...], int]] = []
    for sequence in graphical:
        six_triangles = sum(degree**3 for degree in sequence) - triangle_offset
        if six_triangles % 6 != 0:
            continue
        triangles = six_triangles // 6
        if triangle_min <= triangles <= triangle_max:
            base.append((sequence, triangles))

    base_set = set(base)
    triangle_total = int(params["triangle_complement_total"])
    representatives: list[tuple[tuple[int, ...], int]] = []
    fixed_points: list[tuple[tuple[int, ...], int]] = []
    for item in base:
        sequence, triangles = item
        mate = (
            tuple(sorted(TARGET_N - 1 - degree for degree in sequence)),
            triangle_total - triangles,
        )
        require(mate in base_set, f"complement mate missing: {item!r} -> {mate!r}")
        require(
            (
                tuple(sorted(TARGET_N - 1 - degree for degree in mate[0])),
                triangle_total - mate[1],
            )
            == item,
            f"complement map is not an involution at {item!r}",
        )
        if item == mate:
            fixed_points.append(item)
        elif item < mate:
            representatives.append(item)
    require(not fixed_points, f"unexpected complement fixed point: {fixed_points[:3]!r}")
    require(2 * len(representatives) == len(base), "complement orbits do not partition the base list into pairs")

    generated = {
        "moment_sequences.txt.gz": sequence_bytes(moment),
        "graphical_sequences.txt.gz": sequence_bytes(graphical),
        "base_sequences.txt.gz": sequence_triangle_bytes(base),
        "complement_representatives.txt.gz": sequence_triangle_bytes(representatives),
        "complement_pairs.txt.gz": complement_pair_bytes(
            representatives, TARGET_N, triangle_total
        ),
    }
    coverage = load_json(data_dir / "coverage.json")
    require(isinstance(coverage, dict), "coverage.json is not an object")
    require(coverage.get("format") == "s20-coverage-v1", "unexpected coverage format")
    coverage_files = coverage.get("files")
    require(isinstance(coverage_files, dict), "coverage files table is absent")
    file_results = {
        name: verify_exact_data_file(data_dir, coverage_files, name, content)
        for name, content in generated.items()
    }

    # These byte-identical aliases connect the independently reconstructed
    # enumeration to the first certified-elimination stage.
    alias_targets = {
        "stage1_source.txt.gz": generated["complement_representatives.txt.gz"],
        "stage2_source.txt.gz": read_gzip(data_dir / "stage1_survivors.txt.gz"),
        "class_source.txt.gz": read_gzip(data_dir / "stage2_survivors.txt.gz"),
    }
    for name, expected in alias_targets.items():
        file_results[name] = verify_exact_data_file(
            data_dir, coverage_files, name, expected
        )

    summary = load_json(release_root / "RESULT_SUMMARY.json")
    require(isinstance(summary, dict), "RESULT_SUMMARY.json is not an object")
    require(summary.get("n") == TARGET_N, "summary n mismatch")
    require(summary.get("spectrum") == list(spectrum), "summary spectrum mismatch")
    summary_counts = summary.get("counts")
    require(isinstance(summary_counts, dict), "summary counts table is absent")
    independently_counted = {
        "moment": len(moment),
        "graphical": len(graphical),
        "base": len(base),
        "complement_representatives": len(representatives),
        "complement_fixed_points": len(fixed_points),
    }
    for name, count in independently_counted.items():
        require(summary_counts.get(name) == count, f"summary count mismatch for {name}")

    return {
        "status": "INDEPENDENT_ENUMERATION_V2_PASS",
        "release_root": str(release_root),
        "implementation": {
            "enumeration": "degree-alphabet meet-in-the-middle hash join",
            "graphicality": "smallest-degree Kleitman-Wang layoff",
            "release_code_imported_or_executed": False,
        },
        "derived_parameters": params,
        "counts": independently_counted,
        "enumeration_stats": enumeration_stats,
        "verified_files": file_results,
        "elapsed_seconds": round(time.monotonic() - started, 6),
    }


def main(argv: list[str]) -> int:
    try:
        require(len(argv) == 2, "usage: verify_enumeration_v2.py EXTRACTED_RELEASE_ROOT")
        root = Path(argv[1]).expanduser().resolve(strict=True)
        result = audit(root)
        print(json.dumps(result, sort_keys=True))
        return 0
    except (AuditFailure, OSError, ValueError) as exc:
        print(
            json.dumps(
                {"status": "INDEPENDENT_ENUMERATION_V2_FAILED", "error": str(exc)},
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
