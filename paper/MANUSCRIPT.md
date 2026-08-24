---
title: 'Nonexistence of Simple Graphs with Laplacian Spectrum \(\{0,1,\ldots,n-1\}\) for \(n=16\) and \(20\): Exact Computer-Assisted Proofs'
title-meta: "Nonexistence of Simple Graphs with Laplacian Spectrum {0,1,...,n-1} for n=16 and 20: Exact Computer-Assisted Proofs"
subtitle: "Preprint, version 0.1.0 · DOI: 10.5281/zenodo.22082609"
author: "Jihun Kim (Independent Researcher)"
date: "24 August 2026"
lang: en
subject: "Exact certificate-based computer-assisted proofs in spectral graph theory"
keywords:
  - spectral graph theory
  - Laplacian spectrum
  - computer-assisted proof
  - Farkas certificate
  - exact computation
---

**MSC 2020:** 05C50, 05C85, 15A18.

---

## Abstract

We establish the \(n=16\) and \(n=20\) cases of the \(S_{n,n}\) conjecture.
There is no simple graph on \(16\) vertices with Laplacian spectrum
\(\{0,1,\ldots,15\}\), and no simple graph on \(20\) vertices with Laplacian
spectrum \(\{0,1,\ldots,19\}\). Both proofs combine exact enumeration of forced
degree data with linear relaxations derived from spectral moments, graph and
complement identities, and degree-class incidence constraints. The order-16
proof eliminates \(2{,}077\) candidate degree sequences with \(2{,}143\) exact
rational Farkas leaves organized into degree-reduction certificates and 42
integer branch trees. The order-20 proof enumerates \(160{,}244\)
degree-sequence/triangle-count pairs, reduces them to \(80{,}122\) complement
representatives, and eliminates them with \(80{,}124\) exact integer Farkas
certificates, including four exhaustive branch leaves. All certificate checks
use integer or rational arithmetic, and both coverage ledgers have zero
uncovered cases. These finite-order results do not settle the conjecture in
general.

\clearpage
\setcounter{tocdepth}{2}
\tableofcontents
\clearpage

## Introduction and relation to previous work

For \(1\le i\le n\), Fallat, Kirkland, Molitierno and Neumann introduced

\[
S_{i,n}=\{0,1,\ldots,n\}\setminus\{i\}
\]

and asked which such sets occur as the Laplacian spectrum of a simple graph
[1]. Their \(S_{n,n}\) conjecture states that

\[
S_{n,n}=\{0,1,\ldots,n-1\}
\]

is not Laplacian-realizable for any \(n\ge2\). Fallat et al. established the
conjecture for \(n\le11\), prime \(n\), and
\(n\equiv2,3\pmod4\) [1]. Das, Lee and Cheon derived additional diameter
restrictions on any realizing graph and its complement [2]. Goldberger and
Neumann proved the conjecture for all sufficiently large orders [3]. Hameed,
Khan and Tyaglov surveyed the remaining range and, among other structural
results, excluded Cartesian-product realizations [4]. Johnston, Plosker and
Varona subsequently established the unrestricted order-12 case and described
\(n=16\) as the smallest open order in July 2026 [5].

The present paper treats exactly two orders, \(16\) and \(20\). Within the
finite cases and order classes covered by the cited results, they are the two
smallest orders not covered: 17 and 19 are prime, while
\(18\equiv2\pmod4\). The least order not covered by that cited collection
after the present two theorems is 21. The proofs share a mathematical
architecture but not a single certificate corpus. The order-16 computation
uses rational Farkas certificates and complete integer branch trees for 42
final class models. The order-20 computation uses a complement quotient
followed by three continuous relaxations and a final two-root integer split.

A literature search completed on 24 August 2026 found no earlier public proof
of either case.

## 1. Main results and proof architecture

Let \(G\) be a finite simple undirected graph, let \(A\) be its adjacency
matrix, let \(D=\operatorname{diag}(d_v)\), and let \(L=D-A\) be its Laplacian.

### Theorem 1 (order 16)

There is no simple undirected graph \(G\) on \(16\) vertices such that

\[
\operatorname{spec}L(G)=\{0,1,2,\ldots,15\}.
\]

### Theorem 2 (order 20)

There is no simple undirected graph \(G\) on \(20\) vertices such that

\[
\operatorname{spec}L(G)=\{0,1,2,\ldots,19\}.
\]

Each proof has four logical components:

1. derive necessary spectral, degree and triangle conditions;
2. enumerate every discrete candidate satisfying those conditions;
3. map every hypothetical target graph to a feasible point of a sequence of
   necessary linear or mixed-integer relaxations;
4. verify exact Farkas certificates, together with exhaustive integer branch
   splits where required, that eliminate every candidate.

Floating-point optimization was used only during discovery. The proofs rely on
the analytic derivations, exact enumeration, certificate verification and
coverage ledgers described below.

Appendix A gives the complete enumeration and coverage ledgers. Appendices B
and C give the variables, rows, bounds, serialization and certificate
semantics used by the order-16 and order-20 verifiers.

## 2. Shared spectral and graph identities

Assume temporarily that \(G\) has \(n\) vertices and Laplacian spectrum
\(\{0,1,\ldots,n-1\}\). The zero eigenvalue is simple, so \(G\) is connected.
The first three spectral power sums give

\[
\sum_v d_v=\operatorname{tr}L=\frac{n(n-1)}2,
\tag{2.1}
\]

\[
\sum_v d_v^2
=\operatorname{tr}L^2-\operatorname{tr}L
=\frac{n(n-1)(n-2)}3,
\tag{2.2}
\]

and

\[
\sum_v d_v^3-6t(G)
=\operatorname{tr}L^3-3\sum_vd_v^2.
\tag{2.3}
\]

Here we used

\[
(L^2)_{vv}=d_v^2+d_v,
\qquad
\operatorname{tr}L^3=\sum_vd_v^3+3\sum_vd_v^2-6t(G).
\]

The complement satisfies

\[
L(\overline G)=nI-J-L(G).
\]

On \(\mathbf1^\perp\), eigenvalue \(k\) is sent to \(n-k\). Hence the target
spectrum is complement-invariant. Direct counting also gives

\[
t(G)+t(\overline G)
=\binom n3-\frac12\sum_vd_v(n-1-d_v)
=\frac{n(n-1)(n-5)}{12}.
\tag{2.4}
\]

For a local degree bound, choose an orthonormal Laplacian eigenbasis \(u_k\)
and put \(w_{v,k}=u_k(v)^2\). Connectedness gives \(w_{v,0}=1/n\), while

\[
\sum_kkw_{v,k}=d_v,
\qquad
\sum_kk^2w_{v,k}=d_v^2+d_v.
\tag{2.5}
\]

For \(1\le k\le n-1\),

\[
k^2\le nk-(n-1)
\]

because \((k-1)(n-1-k)\ge0\). Substitution in (2.5) gives

\[
nd_v^2-n(n-1)d_v+(n-1)^2\le0.
\tag{2.6}
\]

This proves the exact integer ranges used below:

\[
2\le d_v\le13\quad(n=16),
\qquad
2\le d_v\le17\quad(n=20).
\tag{2.7}
\]

Finally, every triangle contributes at each of its three vertices, so

\[
3t(G)\le\sum_v\binom{d_v}{2}.
\]

Combining this bound for \(G\) and \(\overline G\) with (2.4) yields

\[
54\le t(G)\le166\quad(n=16),
\qquad
127\le t(G)\le348\quad(n=20).
\tag{2.8}
\]

These bounds are consequences of the target spectrum, not imported pruning
assumptions.

## 3. Common relaxation variables

Let \(m_d\) be the multiplicity of degree \(d\). For an order-\(n\) candidate
define the nonnegative real spectral weights

\[
Y_{d,k}=n\sum_{v:d_v=d}u_k(v)^2,
\qquad 1\le k\le n-1.
\tag{3.1}
\]

Every target graph satisfies

\[
\sum_kY_{d,k}=(n-1)m_d,
\quad
\sum_kkY_{d,k}=nm_dd,
\quad
\sum_kk^2Y_{d,k}=nm_d(d^2+d),
\tag{3.2}
\]

and, for each \(k\),

\[
\sum_dY_{d,k}=n.
\tag{3.3}
\]

For a vertex \(v\) of degree \(d\), put

\[
s_v=\sum_{u\sim v}d_u,
\qquad
q_v=\#\{\text{triangles containing }v\},
\qquad
h_v=s_v-2q_v.
\]

Direct multiplication gives

\[
(L^3)_{vv}=d^3+2d^2+h_v.
\tag{3.4}
\]

If \(R_v=V\setminus(N(v)\cup\{v\})\), then

\[
h_v=d+e(N(v),R_v),
\qquad d\le h_v\le d(n-d).
\tag{3.5}
\]

For a degree class define

\[
S_d=\sum_{v:d_v=d}s_v,
\qquad
H_d=\sum_{v:d_v=d}h_v.
\]

Equations (3.1) and (3.4) imply

\[
\sum_kk^3Y_{d,k}=n\{m_d(d^3+2d^2)+H_d\}.
\tag{3.6}
\]

Summing (3.5) over the degree-\(d\) class gives the two necessary Stage-2
inequalities

\[
m_dd\le H_d\le m_dd(n-d).
\tag{3.7}
\]

In both serialized Stage-2 models, \(H_d\) is not a separate variable. It is
the affine abbreviation

\[
H_d=\frac1n\sum_k k^3Y_{d,k}-m_d(d^3+2d^2)
\]

obtained from (3.6). The variables \(S_d\) are allowed to be real in the
relaxation, even though the values supplied by an actual graph are integers.
After eliminating \(H_d\), (3.7) and the bounds below are linear rows in
\(Y,S\).

The neighbor-degree order bounds, triangle capacities, complement-triangle
identity and \(\sum_dS_d=\sum_vd_v^2\) complete the Stage-2 relaxation. If
\(\ell_d,u_d\) are the sums of the \(d\) smallest and largest entries after
removing one occurrence of \(d\), then

\[
m_d\ell_d\le S_d\le m_du_d,
\tag{3.8}
\]

while

\[
H_d\le S_d\le H_d+2m_d\binom d2.
\tag{3.9}
\]

Writing \(M=n(n-1)/4\) for the forced edge count, the local complement formula

\[
\overline q_v=\binom{n-1-d}{2}-M+s_v-q_v
\tag{3.10}
\]

gives

\[
m_d\left(2M-2\binom{n-1-d}{2}\right)
\le S_d+H_d\le2Mm_d.
\tag{3.11}
\]

All these rows are necessary conditions. The models deliberately omit several
nonlinear graph-realizability constraints; infeasibility of a relaxation is
therefore sufficient for nonexistence, whereas feasibility is not evidence of
a graph.

## 4. The order-16 certified exhaustion

### 4.1 Forced data and exact enumeration

For \(n=16\), (2.1)--(2.3) specialize to

\[
\sum_vd_v=120,
\qquad
\sum_vd_v^2=1120,
\qquad
\sum_vd_v^3-6t=11040.
\tag{4.1}
\]

The complement triangle total is \(220\), the degree range is \([2,13]\), and
the triangle range is \([54,166]\). Exact nondecreasing-sequence enumeration
has the following ledger.

| Order-16 layer | Source | Eliminated | Survivors |
|---|---:|---:|---:|
| moment equations | -- | -- | \(2{,}249\) |
| Erdős--Gallai graphicality | \(2{,}249\) | \(16\) | \(2{,}233\) |
| integral triangle count and bounds | \(2{,}233\) | \(156\) | \(2{,}077\) |
| Stage 1 spectral weights | \(2{,}077\) | \(1{,}359\) | \(718\) |
| Stage 2 local third moments | \(718\) | \(676\) | \(42\) |
| integer class branch trees | \(42\) | \(42\) | \(0\) |

A second implementation enumerates the moment solutions by degree
multiplicities and checks graphicality by Havel-Hakimi instead of reusing the
main combinations/Erdős--Gallai route. It reproduces \(2{,}249\), \(2{,}233\)
and \(2{,}077\) exactly.

The recurrence, pruning invariant, graphicality test, triangle filter,
deterministic record order and exact ledger-partition obligations for this
enumeration are specified in Appendix A.

### 4.2 Spectral and local-third-moment leaves

The Stage-1 system consists of (3.2)--(3.3) at \(n=16\). Exact rational Farkas
certificates eliminate \(1{,}359\) candidates. Stage 2 appends the real
variables \(S_d\), uses the aggregate bounds (3.7)--(3.9) and (3.11) with
\(H_d\) eliminated by the affine expression obtained from (3.6), and adds

\[
\sum_dS_d=1120.
\]

Exact rational Farkas certificates eliminate another \(676\) candidates,
leaving 42 sequences.

### 4.3 Integer degree-class model

For a surviving degree multiset let \(D\) be its distinct degrees and put

\[
P_{a,b}=\begin{cases}
\binom{m_a}{2},&a=b,\\
m_am_b,&a<b.
\end{cases}
\]

The model retains the real variables \(Y_{d,k}\) and adds integer graph counts:

- \(E_{a,b}\), the number of graph edges with endpoint degree multiset
  \(\{a,b\}\);
- \(T_{a,b,c}\), the number of graph triangles with degree multiset
  \(\{a,b,c\}\);
- \(C_{a,b,c}\), the analogous complement-triangle count indexed by original
  degrees.

Their bounds are the elementary pair and triple capacities. Stub equations,
graph and complement triangle totals, classwise third-moment equations,
edge-triangle incidence bounds and degree-class wedge bounds are imposed. For
example,

\[
2E_{d,d}+\sum_{b\ne d}E_{\min(d,b),\max(d,b)}=m_dd,
\tag{4.2}
\]

\[
\sum T_{a,b,c}=t,
\qquad
\sum C_{a,b,c}=220-t,
\tag{4.3}
\]

and, with \(\nu_d(a,b,c)\) the multiplicity of \(d\) in a triple,

\[
\sum_kk^3Y_{d,k}
=16\left[m_d(d^3+2d^2)+S_d^G-2R_d^G\right],
\tag{4.4}
\]

where

\[
S_d^G=2dE_{d,d}+\sum_{b\ne d}bE_{\min(d,b),\max(d,b)},
\qquad
R_d^G=\sum_{a\le b\le c}\nu_d(a,b,c)T_{a,b,c}.
\]

The complement uses \(P_{a,b}-E_{a,b}\), original degree \(d\) maps to
\(15-d\), and spectral weights satisfy

\[
\overline Y_{15-d,k}=Y_{d,16-k}.
\tag{4.5}
\]

Any graph with the prescribed spectrum determines a feasible mixed point:
\(Y\) is generally real, whereas \(E,T,C\) are integer. The converse is not
asserted.
The complete triple set, capacities, graph and complement rows, wedge and
incidence inequalities, variable order and branch-tree serialization are given
in Appendix B; that appendix is the formal definition of the model
whose certificates are checked here.

### 4.4 Exact branch-and-Farkas proof

At an order-16 branch-tree node, the model has rational rows

\[
Ax\le b,
\qquad
Cx=e.
\]

A leaf stores rational multipliers \(y,z\) satisfying

\[
y\ge0,
\qquad
y^{\mathsf T}A+z^{\mathsf T}C=0,
\qquad
y^{\mathsf T}b+z^{\mathsf T}e=-1.
\tag{4.6}
\]

Any feasible \(x\) would yield \(0\le-1\), a contradiction. An internal node
branches on an explicitly integer variable \(x_j\) using

\[
x_j\le a
\qquad\text{or}\qquad
x_j\ge a+1.
\tag{4.7}
\]

The cases are disjoint and exhaustive for every integer value in the parent
interval. The 42 trees contain 174 nodes, 66 branch nodes and 108 exact Farkas
leaves, with maximum depth 10. Together with the \(1{,}359+676\) earlier leaves,
the order-16 proof verifies \(2{,}143\) exact Farkas certificates. No target
candidate survives the certified computation. Lemma 3 below supplies the
graph-to-model implication that completes the proof of Theorem 1.

### Computational Proposition 1 (order-16 exact coverage)

The order-16 ledger partitions all \(2{,}077\) candidates into \(1{,}359\)
Stage-1 leaves, \(676\) Stage-2 leaves and \(42\) class roots. The branch
forest replaces those roots by \(108\) certified leaves, so \(2{,}143\)
rational Farkas certificates cover every candidate.

## 5. The order-20 certified exhaustion

### 5.1 Forced data, enumeration and complement quotient

For \(n=20\), the shared identities specialize to

\[
\sum_vd_v=190,
\qquad
\sum_vd_v^2=2280,
\qquad
\sum_vd_v^3-6t=29260.
\tag{5.1}
\]

The complement triangle total is \(475\), the degree range is \([2,17]\), and
the triangle range is \([127,348]\). Exact enumeration gives

\[
209{,}932\longrightarrow200{,}108\longrightarrow160{,}244
\tag{5.2}
\]

moment sequences, graphical sequences, and graphical
degree-sequence/triangle-count pairs. The primary enumerator lists degree
multiplicities and uses Erdős--Gallai. A position-by-position/Havel--Hakimi audit
and a degree-alphabet meet-in-the-middle/Kleitman-Wang audit reproduce the same
counts and complete uncompressed candidate bytes.

The exact enumeration recurrences, pruning invariants, record serialization,
complement-orbit checks and ledger partitions are specified in Appendix A.

For a pair \((s,t)\), where \(s=(d_1,\ldots,d_{20})\) is nondecreasing, define

\[
\kappa(s,t)
=\left(\operatorname{sort}(19-d_1,\ldots,19-d_{20}),475-t\right).
\tag{5.3}
\]

The map is a fixed-point-free involution on the 160,244 candidates: a fixed
point would require \(2t=475\). Retaining the lexicographically smaller member
of each orbit leaves exactly \(80{,}122\) representatives. If a target graph
realizes either member, it or its complement realizes the retained one.

### 5.2 Three necessary relaxation layers

Stage 1 is (3.2)--(3.3) at \(n=20\). Stage 2 appends the real variables \(S_d\),
uses the aggregate bounds (3.7)--(3.9) and (3.11) with \(H_d\) eliminated by
the affine expression obtained from (3.6), and adds \(\sum_dS_d=2280\). Stage 3 uses the real spectral weights
together with degree-pair and degree-triple variables \(E_{a,b},T_z,C_z\).
For a nondecreasing triple \(z\) with degree multiplicities \(\nu_d(z)\), put

\[
P_z=\prod_d\binom{m_d}{\nu_d(z)}.
\]

Only triples with \(P_z>0\) are serialized. Define the pair multiplicity in a
triple by

\[
\pi_{a,b}(z)=
\begin{cases}
\binom{\nu_a(z)}2,&a=b,\\
\nu_a(z)\nu_b(z),&a<b.
\end{cases}
\tag{5.4a}
\]

The elementary capacities are

\[
0\le E_{a,b}\le P_{a,b},
\qquad
0\le T_z,C_z\le P_z.
\tag{5.4}
\]

The model imposes stub equations, graph and complement triangle totals, graph
and complement classwise \(L^3\) equations, pair-incidence bounds and wedge
bounds. For a pair \((a,b)\), graph triangles incident with that pair satisfy

\[
\sum_z\pi_{a,b}(z)T_z
\le(\min(a,b)-1)E_{a,b},
\tag{5.5}
\]

while complement triangles satisfy

\[
\sum_z\pi_{a,b}(z)C_z
\le(18-\max(a,b))(P_{a,b}-E_{a,b}).
\tag{5.6}
\]

In the 343 ordinary Stage-3 leaves, \(E,T,C\) are allowed to be real. Thus each
certificate proves infeasibility of a continuous relaxation containing every
actual graph point. Integrality metadata is consulted only for the final
branch variable described below.

Appendix C states the full graph and complement classwise equations, stub and
triangle-total rows, pair-incidence and wedge inequalities, standard-form
conversion, deterministic row order and sparse-certificate serialization
reconstructed by the verifier.

### 5.3 Exact standard-form certificates

For each order-20 leaf, finite lower bounds are shifted away, inequalities and
finite upper bounds receive nonnegative slack variables, and the verifier
obtains

\[
Bw=h,
\qquad
w\ge0,
\tag{5.7}
\]

with integer \(B,h\). A stored integer multiplier \(z\) is a contradiction if

\[
B^{\mathsf T}z\ge0,
\qquad
h^{\mathsf T}z<0.
\tag{5.8}
\]

Indeed, a feasible \(w\) would imply

\[
h^{\mathsf T}z=w^{\mathsf T}B^{\mathsf T}z\ge0.
\]

The dedicated slack columns force the multipliers of inequality and
upper-bound rows to be nonnegative. The verifier checks integer arithmetic,
row signs, row order and every sparse multiplier exactly.

### 5.4 Coverage and final integer split

The exact order-20 coverage ledger is:

| Order-20 layer | Source | Exact Farkas leaves | Survivors |
|---|---:|---:|---:|
| complement representatives | \(80{,}122\) | -- | \(80{,}122\) |
| Stage 1 spectral weights | \(80{,}122\) | \(63{,}235\) | \(16{,}887\) |
| Stage 2 local third moments | \(16{,}887\) | \(16{,}542\) | \(345\) |
| Stage 3 class model | \(345\) | \(343\) | \(2\) roots |
| integer split | \(2\) roots | \(4\) | \(0\) |

The two parent roots are

\[
s^{(0)}=(2,2,2,4,6,6,7,7,9,9,9,10,12,12,14,14,15,16,17,17),
\qquad t^{(0)}=229,
\tag{5.9}
\]

and

\[
s^{(1)}=(2,2,2,5,5,6,6,8,9,9,9,10,12,12,14,14,15,16,17,17),
\qquad t^{(1)}=231.
\tag{5.10}
\]

Both have exactly three degree-2 vertices. Variable \(E_{2,2}\) is an actual
integer graph-edge count with parent interval \([0,3]\). The two children

\[
E_{2,2}\le0
\qquad\text{and}\qquad
E_{2,2}\ge1
\tag{5.11}
\]

are disjoint and cover every possible integer value. All four child
relaxations have exact Farkas certificates. Hence the number of exact
order-20 leaves is

\[
63{,}235+16{,}542+343+4=80{,}124.
\tag{5.12}
\]

Every source at each layer is the disjoint union of the certified leaves and
the next survivor ledger. The verifier checks exact set difference, uniqueness,
source order, shard hashes and zero uncovered cases. Therefore no retained
candidate survives the certified computation. Lemma 4 below supplies the
canonical complement and graph-to-model implications that complete the proof
of Theorem 2.

### Computational Proposition 2 (order-20 exact coverage)

The order-20 ledgers partition all \(80{,}122\) complement representatives
into \(63{,}235\) Stage-1 leaves, \(16{,}542\) Stage-2 leaves, \(343\)
Stage-3 leaves and two final roots. The four certified children of those roots
complete the \(80{,}124\)-leaf exhaustion.

## 6. Order-specific graph-to-model soundness and theorem proofs

The shared identities do not make the two finite computations identical. The
order-16 proof branches through complete mixed-integer class trees, whereas the
order-20 proof first selects one complement representative, uses continuous
class relaxations, and consults integrality only for its final split. We
therefore state the two mapping lemmas separately.

### Lemma 3 (order-16 graph-to-model mapping)

Suppose that a simple graph \(G\) on \(16\) vertices has Laplacian spectrum
\(\{0,1,\ldots,15\}\). Its sorted degree sequence and forced triangle count
occur in the complete order-16 enumeration. Its projector-diagonal weights
\(Y\) satisfy the Stage-1 equations, and the same weights together with the
actual neighbor-degree sums \(S_d\) satisfy every Stage-2 row. If the candidate
reaches one of the 42 class models, the same \(Y\) together with the actual
integer degree-class counts \(E,T,C\) gives a feasible mixed point of that
model. At each branch node, the actual integer count lies in exactly one child.

#### Proof

Equations (2.1)--(2.8) and the order-16 specialization (4.1) put the sorted
degree sequence and its forced integral triangle count in the initial list;
the completeness and filtering statement is the order-16 part of Appendix A.
Equations (3.1)--(3.3) follow by summing squared
eigenvector coordinates over each degree class. Equations (3.4)--(3.11), after
the stated elimination of \(H_d\), follow from the diagonal of \(L^3\), actual
neighbor sums, triangle capacities and complement counting. For a final model,
take \(E,T,C\) to be the actual edge and graph/complement triangle counts by
degree class. Every row in Appendix B is then a capacity bound,
double-counting identity, local third-moment identity or incidence upper bound.
Finally, every branch is on an integer graph count and uses adjacent bounds
\(x_j\le a\) and \(x_j\ge a+1\), so the children are disjoint and exhaustive.
Thus an actual target graph remains feasible until it reaches one certified
leaf. \(\square\)

### Proof of Theorem 1

Assume that a target graph of order 16 exists. Lemma 3 maps it to an enumerated
candidate and preserves a feasible point through every applicable relaxation
and integer branch. Computational Proposition 1 says that the exact coverage
ledger sends every such candidate to a verified Farkas leaf. The contradiction
at that leaf rules out the feasible point. Hence no target graph exists.
\(\square\)

### Lemma 4 (order-20 canonical graph-to-model mapping)

Suppose that a simple graph \(G\) on \(20\) vertices has Laplacian spectrum
\(\{0,1,\ldots,19\}\). Let \(G^{\ast}\) be \(G\) if the pair consisting of its
sorted degree sequence and triangle count is the retained representative of
its \(\kappa\)-orbit, and let \(G^{\ast}=\overline G\) otherwise. Then
\(G^{\ast}\) realizes exactly one of the \(80{,}122\) retained representatives.
Its projector-diagonal weights and actual neighbor-degree sums give feasible
points of its Stage-1 and Stage-2 models. If it reaches Stage 3, its actual
degree-class counts \(E,T,C\), viewed in the continuous relaxation, give a
feasible point of the class model. If it is one of the final two roots, its
integer \(E_{2,2}\) lies in exactly one of the two children in (5.11).

#### Proof

The target spectrum is invariant under complementation, and (5.3) is a
fixed-point-free involution of the complete \(160{,}244\)-candidate set.
Consequently exactly one of \(G,\overline G\) realizes the retained member of
its orbit; this is the complement-coverage statement formalized in Appendix A.
Applying (3.1)--(3.11) to \(G^{\ast}\) proves
the Stage-1 and Stage-2 claims exactly as above. At Stage 3 take \(E,T,C\) to be
the actual graph and complement counts by original degree class. The complete
rows in Appendix C are satisfied by the corresponding capacity,
stub, triangle-total, graph/complement third-moment, incidence and wedge
counts. Although these counts are integers for \(G^{\ast}\), the 343 ordinary
class certificates discard their integrality and prove infeasibility of the
larger continuous relaxation. For either final root, \(E_{2,2}\) is an integer
in \([0,3]\), so it satisfies exactly one of \(E_{2,2}\le0\) and
\(E_{2,2}\ge1\). Thus \(G^{\ast}\) remains feasible until it reaches one
certified leaf. \(\square\)

### Proof of Theorem 2

Assume that a target graph of order 20 exists and form \(G^{\ast}\) as in
Lemma 4. Computational Proposition 2 and the exact set-partition ledger place
its retained candidate in a Stage-1, Stage-2 or Stage-3 Farkas leaf, or in one
of the four certified children of the final two roots. Lemma 4 supplies a
feasible point in that same leaf, contradicting its exact certificate. Hence no
target graph exists. \(\square\)

## 7. Artifacts, hashes and reproduction

The theorem claims depend on two frozen proof artifacts. The canonical
self-contained reproduction command from the combined release root is

~~~bash
./verification/REPRODUCE_BOTH.sh
~~~

It checks the top-level manifest, replays order 16, performs the hardened
offline order-20 replay, and requires the reproduced order-20 canonical JSON
to match the frozen expected bytes.

A successful run terminates with

~~~text
COMBINED_REPRODUCTION_PASS orders=16,20
~~~

### 7.1 Order-16 artifact

~~~text
snn16-certified-nonexistence-20260821.zip
SHA-256: f7f127da4fd6227bd66eadfc22847da270caf2d29b8bedbc16aabee548c8c847
~~~

From the extracted package root, run:

~~~bash
./REPRODUCE.sh
~~~

The two primary certificate files have SHA-256 identities:

~~~text
certs/degree_reduction.json.gz
950d05274bf8e7234c0c72efa78927feeeacadc33ba5274f42c738ff3e8562c9

certs/class_exhaustion.json.gz
51cc5417f922f6bfceb3704c81a1691d813f76550517397269404b35225cc9bd
~~~

Expected statuses are VERIFIED_UNSAT and SEMANTIC_AUDIT_PASSED.

### 7.2 Order-20 artifact

~~~text
S20_CERTIFIED_EXHAUSTION_RELEASE_20260821.tar.gz
SHA-256: 1eeda59a36dc835ec0efd3dc741d985145054af0d72e77f59e84f9cb63461206
~~~

To replay order 20 alone from the combined release root, run:

~~~bash
./verification/n20/REPRODUCE_INDEPENDENT.sh \
  artifacts/S20_CERTIFIED_EXHAUSTION_RELEASE_20260821.tar.gz \
  tmp/reproduced-n20-canonical.json
~~~

The publication-revision canonical JSON has SHA-256:

~~~text
ebc3d8065c3f0c2e869e940f2d50c572292c45646a5ee6ac658a3f805b1ccbac
~~~

Expected statuses include:

~~~text
VERIFIED_UNSAT
INDEPENDENT_ENUMERATION_V2_PASS
INDEPENDENTLY_VERIFIED_UNSAT
GRAPH_IDENTITY_CYCLE_V2_PASS
INDEPENDENT_REPRODUCTION_PASS
~~~

The strings beginning with INDEPENDENT are retained machine labels for
separately implemented internal checks. They do not claim external replication.

### 7.3 Trust boundary

| Component | Trust role |
|---|---|
| floating-point LP and generators | untrusted discovery only |
| analytic identities and mapping lemma | trusted mathematics |
| exact enumerators | trusted internal implementation |
| exact certificate verifiers | trusted internal implementation |
| coverage and branch audits | trusted internal implementation |
| external or different-language checker | not yet available; not claimed |

The two theorem packages use different constants, candidate ledgers and final
certificate structures. Passing one verifier is not treated as evidence for
the other theorem.

## 8. Limitations and external validation

Theorems 1 and 2 concern only the two stated orders and do not settle the
conjecture in general. External specialist review, independently written
verifiers, clean-room reproduction on additional platforms and eventual
proof-assistant formalization would provide further assurance and remain
future work.
