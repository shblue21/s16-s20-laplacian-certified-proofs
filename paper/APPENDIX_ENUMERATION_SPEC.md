\newpage

## Appendix A: Exact enumeration and finite-coverage specification

This appendix specifies the discrete enumeration and coverage obligations used
in the order-16 and order-20 proofs. The counts and hashes below were checked
against the frozen inputs
identified in Section A.1. All arithmetic in the trusted enumeration and
coverage checks is integer arithmetic.

### A.1 Frozen inputs and derived parameters

The two proof archives are logically separate.

```text
snn16-certified-nonexistence-20260821.zip
SHA-256: f7f127da4fd6227bd66eadfc22847da270caf2d29b8bedbc16aabee548c8c847

S20_CERTIFIED_EXHAUSTION_RELEASE_20260821.tar.gz
SHA-256: 1eeda59a36dc835ec0efd3dc741d985145054af0d72e77f59e84f9cb63461206
```

For a target graph of order $n$, write its nondecreasing degree sequence as
$s=(d_1,\ldots,d_n)$. The analytic part of the proof gives the following
enumeration parameters.

| Parameter | $n=16$ | $n=20$ |
|---|---:|---:|
| allowed degree interval | $2,\ldots,13$ | $2,\ldots,17$ |
| sequence length | 16 | 20 |
| forced degree sum | 120 | 190 |
| forced square sum | 1120 | 2280 |
| constant $C_n$ in $\sum_i d_i^3-6t=C_n$ | 11040 | 29260 |
| allowed triangle interval | $54,\ldots,166$ | $127,\ldots,348$ |
| $t(G)+t(\overline G)$ | 220 | 475 |

Consequently, if the allowed degree alphabet is
$D_n=\{a,a+1,\ldots,b\}$, every admissible sorted sequence corresponds
bijectively to a nonnegative integer multiplicity vector
$(m_a,\ldots,m_b)$ satisfying

\[
\sum_{d=a}^{b}m_d=n,
\qquad
\sum_{d=a}^{b}d m_d=\sigma_1,
\qquad
\sum_{d=a}^{b}d^2m_d=\sigma_2.
\tag{A.1}
\]

No graph-isomorphism reduction or heuristic symmetry breaking is used in this
enumeration.

### A.2 Complete multiplicity recursion

The following pseudocode is a mathematical specification of a complete
multiplicity enumeration. The frozen order-20 verifier implements its
memoized exact-completion version. The separately structured order-16
audit implements the same multiplicity principle with endpoint pruning; the
order-16 strict verifier instead traverses every sorted tuple directly.

```text
ENUM(d, r, S, Q, multiplicities):
    # d is the smallest still available degree.
    # A completion must use r entries, with residual sum S
    # and residual square sum Q, all drawn from {d,...,b}.

    if r < 0 or S < 0 or Q < 0:
        return

    if d = b:
        if S = r*b and Q = r*b^2:
            set m_b = r
            output the sorted sequence encoded by m_a,...,m_b
        return

    if S < r*d or S > r*b:
        return
    if Q < r*d^2 or Q > r*b^2:
        return
    if r > 0 and r*Q < S^2:
        return
    if r = 0:
        output only if S = Q = 0
        return

    for c = 0,...,r:
        set m_d = c
        ENUM(d+1, r-c, S-c*d, Q-c*d^2, multiplicities)
```

The initial call is

\[
\operatorname{ENUM}(a,n,\sigma_1,\sigma_2,()).
\tag{A.2}
\]

The pruning invariant is the following: at a call
$\operatorname{ENUM}(d,r,S,Q)$, a completion, if one exists, consists of
exactly $r$ values in $[d,b]$, with sum $S$ and square sum $Q$.
Therefore it necessarily satisfies

\[
rd\le S\le rb,
\qquad
rd^2\le Q\le rb^2,
\qquad
rQ\ge S^2.
\tag{A.3}
\]

The last inequality is Cauchy--Schwarz. Hence every endpoint or
Cauchy--Schwarz rejection is necessary and cannot discard a completion. At an
unpruned node, the loop tries every possible value of $m_d$. Induction on
the number of remaining degree values proves that every solution of (A.1) is
output exactly once. The order-20 verifier additionally memoizes the exact
Boolean recurrence

\[
P(d,r,S,Q)
=\bigvee_{c=0}^{r}P(d+1,r-c,S-cd,Q-cd^2),
\tag{A.4}
\]

with the evident terminal condition. This can prune more nodes than (A.3),
but it is an exact restatement of the same exhaustive case split.

### A.3 Graphicality and forced triangle filtering

Every sequence output by (A.2) is tested for simple-graph graphicality. The
strict paths use the Erdős--Gallai inequalities. If
$e_1\ge\cdots\ge e_n$ is the sequence in decreasing order, the test is

\[
\sum_{i=1}^{k}e_i
\le k(k-1)+\sum_{i=k+1}^{n}\min(e_i,k)
\quad(1\le k\le n).
\tag{A.5}
\]

Only graphical sequences are retained. For each such sequence, the triangle
count required by the third spectral moment is computed, rather than searched,
as

\[
t=\frac{\sum_i d_i^3-C_n}{6}.
\tag{A.6}
\]

The numerator must be divisible by 6, and the resulting integer must lie
in the interval in Section A.1. These are necessary conditions for a target
graph. Thus the moment recursion, graphicality test, divisibility test and
triangle-range test cannot remove the degree data of a target graph.

### A.4 Order-16 enumeration and coverage

The order-16 strict verifier enumerates all

\[
d_1,\ldots,d_{16}\in\{2,\ldots,13\},
\qquad d_1\le\cdots\le d_{16},
\]

by a direct combinations-with-repetition traversal. It then applies the two
moment equalities, Erdős--Gallai, and (A.6). Its exact ledger is:

| Order-16 layer | Source | Certified leaves | Survivors |
|---|---:|---:|---:|
| two degree moments | all sorted tuples | -- | 2,249 |
| Erdős--Gallai | 2,249 | -- | 2,233 |
| triangle integrality and range | 2,233 | -- | 2,077 |
| Stage 1 spectral model | 2,077 | 1,359 | 718 |
| Stage 2 local model | 718 | 676 | 42 |
| integer class trees | 42 roots | 108 branch-tree leaves | 0 |

The file `certs/degree_reduction.json.gz` has one record, in exact base-list
order, for each of the 2,077 candidates. Each record has exactly one of
the mutually exclusive kinds `stage1_farkas`, `stage2_farkas`, or `survivor`.
Writing $B_{16}$ for the ordered base list, $L_{16,1}$ and $L_{16,2}$
for the two certified subsets, and $R_{16}$ for the final survivors, the
verifier checks

\[
B_{16}=L_{16,1}\mathbin{\dot\cup}L_{16,2}
              \mathbin{\dot\cup}R_{16},
\quad
(|L_{16,1}|,|L_{16,2}|,|R_{16}|)=(1359,676,42).
\tag{A.7}
\]

Equivalently, the Stage-1 survivor set has size $676+42=718$, and is the
disjoint union of the Stage-2 leaves and the 42 class roots. The class
certificate contains exactly those 42 roots, in the same order. Its
integer branch trees have 174 nodes: 66 branch nodes and 108
exact Farkas leaves, with maximum depth 10. At each branch, adjacent
integer bounds $x_j\le q$ and $x_j\ge q+1$ are disjoint and exhaustive.

The frozen order-16 certificate identities are:

```text
certs/degree_reduction.json.gz
SHA-256: 950d05274bf8e7234c0c72efa78927feeeacadc33ba5274f42c738ff3e8562c9

certs/class_exhaustion.json.gz
SHA-256: 51cc5417f922f6bfceb3704c81a1691d813f76550517397269404b35225cc9bd
```

The semantic audit follows a structurally different route: it enumerates
multiplicities by the residual recursion of Section A.2 and uses
largest-degree Havel--Hakimi instead of the strict verifier's sorted-tuple
traversal and Erdős--Gallai test. It reproduces 2,249, 2,233 and
2,077, compares the complete ordered base list with all certificate
records, and checks that the class items equal the 42 survivors. This is a
separately structured internal audit, not external replication.

### A.5 Order-20 complement quotient

Before certificate elimination, the order-20 computation applies a
complement quotient. For a candidate $(s,t)$, define

\[
\kappa(s,t)=
\left(\operatorname{sort}(19-d_1,\ldots,19-d_{20}),475-t\right).
\tag{A.8}
\]

This map preserves the complete candidate set. Indeed, complementing a simple
graph realizing a graphical degree sequence gives a simple graph with degree
sequence $\operatorname{sort}(19-d_i)$. Substitution in the first two moment
equations preserves $\sum d_i=190$ and $\sum d_i^2=2280$. Expanding
$\sum_i(19-d_i)^3$, and using those two moments, gives

\[
\sum_i(19-d_i)^3
=20\cdot19^3-3\cdot19^2\cdot190+3\cdot19\cdot2280-\sum_i d_i^3
=61370-\sum_i d_i^3.
\]

Therefore (A.6) gives

\[
\overline t
=\frac{61370-\sum_i d_i^3-29260}{6}
=475-\frac{\sum_i d_i^3-29260}{6}
=475-t.
\]

The interval
$[127,348]$ is invariant under $t\mapsto475-t$. Therefore the complement
mate passes the same moment, graphicality, divisibility and range predicates.

Applying (A.8) twice returns the original sorted pair, so $\kappa$ is an
involution. It has no fixed point: a fixed pair would require
$t=475-t$, or $2t=475$, which is impossible for integer $t$. Hence all
160,244 candidates lie in two-element orbits. Retaining the
lexicographically smaller member of every orbit leaves exactly 80,122
representatives and loses no hypothetical target graph, because the graph or
its complement realizes the retained member.

### A.6 Order-20 enumeration, hashes and coverage

The order-20 strict route uses the exact memoized multiplicity recurrence
(A.4), Erdős--Gallai, (A.6), and the complement quotient (A.8). Its ledger is:

| Order-20 layer | Source | Certified leaves | Survivors |
|---|---:|---:|---:|
| two degree moments | multiplicity recursion | -- | 209,932 |
| Erdős--Gallai | 209,932 | -- | 200,108 |
| triangle integrality and range | 200,108 | -- | 160,244 |
| complement quotient | 160,244 | symmetry pairing | 80,122 |
| Stage 1 spectral model | 80,122 | 63,235 | 16,887 |
| Stage 2 local model | 16,887 | 16,542 | 345 |
| Stage 3 class model | 345 | 343 | 2 roots |
| final integer split | 2 roots | 4 child leaves | 0 |

The following SHA-256 values hash the complete **uncompressed canonical
ledger bytes** named immediately above them. They are not hashes of individual
certificates.

```text
moment_sequences.txt (209,932)
c60854d47d7c6492577999103aba99f00e50d076f38c3f4d3ad486e25c557856

graphical_sequences.txt (200,108)
7b7cc252551d8e0afdf76e9b47df007ac292b192c3474031201f4026936ef731

base_sequences.txt (160,244)
8523a5c0c0bc1c4f2d6e76be0979f984954b393393e483f4047529b0d48245e2

complement_representatives.txt / Stage-1 source (80,122)
851b058e4c5f933e22bbd61051293342e5788fd3a524fa295266dcde4633e0d4

Stage-1 survivors / Stage-2 source (16,887)
a325883c2b1d7919f70ac82d2460733f1fe9b3e373f633b42a1b6ae512fc3ad4

Stage-2 survivors / class source (345)
dd39bed2528cea440158a0161451dc29dbbb2b36fde0f91ae6558ee7424d8798

class survivors / final roots (2)
b3b6352252492f17517e00f25307f8370daec1eb50786d598218c8f540859ecc
```

For each certificate stage $i$, let $S_i$ be its ordered source ledger,
$R_i$ its ordered survivor ledger, and $L_i$ the source indices carrying
certificates. The verifier checks more than the counts: every certificate
index is in range and globally strictly increasing, every survivor is unique,
the survivor list is the source-induced order, and

\[
S_i=L_i\mathbin{\dot\cup}R_i,
\qquad
L_i=S_i\setminus R_i.
\tag{A.9}
\]

It also compares the bytes of each next-stage source with the preceding
survivor ledger:

\[
S_1=\text{complement representatives},
\quad S_2=R_1,
\quad S_3=R_2.
\tag{A.10}
\]

The two Stage-3 survivors are byte-identical to the two roots in the final
branch metadata. Each root is split on the actual integer graph count
$E_{2,2}$ into $E_{2,2}\le0$ and $E_{2,2}\ge1$. These children are
disjoint and exhaustive, and all four child models have exact certificates.
Thus the certificate-leaf total is

\[
63235+16542+343+4=80124,
\]

with zero uncovered candidates.

### A.7 Structurally different internal audit paths

The agreement checks deliberately change both enumeration and graphicality
algorithms.

| Order | Main exact path | Structurally different internal path |
|---|---|---|
| 16 | sorted tuples by combinations with repetition; Erdős--Gallai | degree-multiplicity residual recursion; largest-degree Havel--Hakimi |
| 20, bundled | degree-multiplicity exact-completion recursion; Erdős--Gallai | nondecreasing position-by-position feasibility dynamic program; largest-degree Havel--Hakimi |
| 20, second verifier | does not import or execute release code | degree-alphabet meet-in-the-middle hash join; smallest-degree Kleitman--Wang layoff |

The order-20 meet-in-the-middle audit splits the degree alphabet, indexes
high-half multisets by `(length, sum, square sum)`, joins complementary low-half
keys, and reconstructs the complete canonical bytes. It therefore does not
reuse the multiplicity recursion. Its smallest-degree Kleitman--Wang layoff
also differs from both Erdős--Gallai and the bundled largest-degree
Havel--Hakimi path.

These checks reduce the risk of a shared algorithmic mistake, but they remain
internal Python implementations using the same frozen mathematical
specification and data. Section 7.3 states the corresponding trust boundary.
