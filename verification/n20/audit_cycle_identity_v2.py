#!/usr/bin/env python3
"""Independent regression for the C20 fixture omitted by the bundled audit."""

from __future__ import annotations

import json
from math import comb


class AuditFailure(RuntimeError):
    pass


def require(condition: bool, message: object) -> None:
    if not condition:
        raise AuditFailure(str(message))


def multiply(left: list[list[int]], right: list[list[int]]) -> list[list[int]]:
    n = len(left)
    return [
        [sum(left[i][k] * right[k][j] for k in range(n)) for j in range(n)]
        for i in range(n)
    ]


def main() -> int:
    n = 20
    adjacency = [[0] * n for _ in range(n)]
    for vertex in range(n):
        neighbor = (vertex + 1) % n
        i, j = sorted((vertex, neighbor))
        adjacency[i][j] = adjacency[j][i] = 1

    degrees = [sum(row) for row in adjacency]
    require(degrees == [2] * n, "fixture is not the 20-cycle")
    edge_count = sum(degrees) // 2
    require(edge_count == 20, "cycle edge count differs")

    laplacian = [
        [degrees[i] if i == j else -adjacency[i][j] for j in range(n)]
        for i in range(n)
    ]
    laplacian2 = multiply(laplacian, laplacian)
    laplacian3 = multiply(laplacian2, laplacian)
    laplacian4 = multiply(laplacian2, laplacian2)
    common = [
        [sum(adjacency[i][k] * adjacency[j][k] for k in range(n)) for j in range(n)]
        for i in range(n)
    ]

    incident_triangles: list[int] = []
    neighbor_degree_sums: list[int] = []
    for vertex in range(n):
        triangles = sum(
            adjacency[vertex][i] * adjacency[vertex][j] * adjacency[i][j]
            for i in range(n)
            for j in range(i + 1, n)
        )
        incident_triangles.append(triangles)
        neighbor_sum = sum(adjacency[vertex][other] * degrees[other] for other in range(n))
        neighbor_degree_sums.append(neighbor_sum)
        degree = degrees[vertex]
        require(laplacian2[vertex][vertex] == degree * degree + degree,
                ("L2 diagonal", vertex))
        require(
            laplacian3[vertex][vertex]
            == degree ** 3 + 2 * degree * degree + neighbor_sum - 2 * triangles,
            ("L3 diagonal", vertex),
        )

    triangle_count = sum(incident_triangles) // 3
    require(triangle_count == 0, "C20 unexpectedly has a triangle")
    trace4 = sum(laplacian4[i][i] for i in range(n))
    trace4_formula = sum((degree * degree + degree) ** 2 for degree in degrees)
    trace4_formula += 2 * sum(
        (common[i][j] - adjacency[i][j] * (degrees[i] + degrees[j])) ** 2
        for i in range(n)
        for j in range(i + 1, n)
    )
    require(trace4 == trace4_formula == 1400, "C20 L4 identity differs")
    require(
        sum(common[i][j] for i in range(n) for j in range(i + 1, n))
        == sum(comb(degree, 2) for degree in degrees),
        "all-pair common-neighbor identity differs",
    )
    require(
        sum(
            common[i][j]
            for i in range(n)
            for j in range(i + 1, n)
            if adjacency[i][j]
        )
        == 3 * triangle_count,
        "edge common-neighbor identity differs",
    )

    complement = [
        [0 if i == j else 1 - adjacency[i][j] for j in range(n)]
        for i in range(n)
    ]
    complement_degrees = [19 - degree for degree in degrees]
    complement_common = [
        [sum(complement[i][k] * complement[j][k] for k in range(n)) for j in range(n)]
        for i in range(n)
    ]
    complement_incident_triangles: list[int] = []
    for vertex in range(n):
        count = sum(
            complement[vertex][i] * complement[vertex][j] * complement[i][j]
            for i in range(n)
            for j in range(i + 1, n)
        )
        complement_incident_triangles.append(count)
        require(
            count
            == comb(19 - degrees[vertex], 2)
            - edge_count
            + neighbor_degree_sums[vertex]
            - incident_triangles[vertex],
            ("local complement triangle", vertex),
        )
    for i in range(n):
        for j in range(i + 1, n):
            require(
                complement_common[i][j]
                == 18 - degrees[i] - degrees[j] + 2 * adjacency[i][j] + common[i][j],
                ("complement common neighbors", i, j),
            )
    complement_triangles = sum(complement_incident_triangles) // 3
    require(
        triangle_count + complement_triangles
        == comb(n, 3) - sum(degrees[i] * complement_degrees[i] for i in range(n)) // 2,
        "Goodman identity differs",
    )

    print(json.dumps({
        "status": "GRAPH_IDENTITY_CYCLE_V2_PASS",
        "vertices": n,
        "edges": edge_count,
        "triangles": triangle_count,
        "trace_L4": trace4,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(json.dumps({
            "status": "GRAPH_IDENTITY_CYCLE_V2_FAILED",
            "error": str(exc),
        }, sort_keys=True))
        raise SystemExit(2)
