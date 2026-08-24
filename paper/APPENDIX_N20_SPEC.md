## Appendix C: Complete order-20 model and certificate specification

### C.1 Purpose, scope and frozen artifact

This appendix gives the complete mathematical and serialization specification
for the order-\(20\) theorem in the combined manuscript. It makes the
graph-to-model implication and the correspondence with the exact verifier
auditable without treating generated matrices or floating-point solver output
as trusted evidence.

The theorem addressed here is

\[
\text{there is no simple graph }G\text{ on }20\text{ vertices with }
\operatorname{spec}L(G)=\{0,1,\ldots,19\}.
\]

The frozen certificate artifact is

~~~text
S20_CERTIFIED_EXHAUSTION_RELEASE_20260821.tar.gz
SHA-256: 1eeda59a36dc835ec0efd3dc741d985145054af0d72e77f59e84f9cb63461206
~~~

Throughout, \(G\) is a finite simple undirected graph, \(A\) is its adjacency
matrix, \(D=\operatorname{diag}(d_v)\), and \(L=D-A\). Every model below
contains necessary conditions only. A feasible relaxation point need not come
from a graph; soundness requires the other direction: every hypothetical target
graph supplies a feasible point.

### C.2 Global necessities, enumeration and complement quotient

The prescribed spectrum has a simple zero, so \(G\) is connected. Its first
three Laplacian moments give

\[
\sum_vd_v=190,\qquad
\sum_vd_v^2=2280,\qquad
\sum_vd_v^3-6t(G)=29260.
\tag{C.1}
\]

Thus \(|E(G)|=95\), and the only possible triangle count for a degree sequence
is

\[
t(G)=\frac{\sum_vd_v^3-29260}{6}.
\tag{C.2}
\]

For an orthonormal eigenbasis \(Lu_k=ku_k\), put
\(w_{v,k}=u_k(v)^2\). Since \(w_{v,0}=1/20\),

\[
\sum_{k=1}^{19}kw_{v,k}=d_v,\qquad
\sum_{k=1}^{19}k^2w_{v,k}=d_v^2+d_v,\qquad
\sum_{k=1}^{19}w_{v,k}=\frac{19}{20}.
\]

The pointwise inequality \(k^2\le20k-19\), valid for \(1\le k\le19\),
implies

\[
20d_v^2-380d_v+361\le0.
\]

Its integral solutions in the simple-graph range are exactly

\[
2\le d_v\le17.
\tag{C.3}
\]

For an edge \(uv\), the number \(c_{uv}\) of common neighbors satisfies
\(c_{uv}\ge d_u+d_v-20\). Hence

\[
3t(G)=\sum_{uv\in E(G)}c_{uv}
\ge\sum_{uv\in E(G)}(d_u+d_v-20)
=2280-20(95)=380,
\]

so \(t(G)\ge127\). The identity

\[
L(\overline G)=20I-J-L(G)
\]

shows that the target spectrum is complement-invariant. Also,

\[
t(G)+t(\overline G)
=\binom{20}{3}-\frac12\sum_vd_v(19-d_v)=475.
\tag{C.4}
\]

Applying the same lower bound to \(\overline G\) yields

\[
127\le t(G)\le348.
\tag{C.5}
\]

Exact enumeration lists every nondecreasing \(20\)-tuple in \([2,17]\)
satisfying the degree moments, tests graphicality, and imposes the integrality
and range in (C.2) and (C.5). The counts are

\[
209{,}932\longrightarrow200{,}108\longrightarrow160{,}244
\tag{C.6}
\]

for moment sequences, graphical sequences, and graphical
degree-sequence/triangle-count pairs.

For \(s=(d_1,\ldots,d_{20})\) nondecreasing, define

\[
\kappa(s,t)=
\left(\operatorname{sort}(19-d_1,\ldots,19-d_{20}),475-t\right).
\tag{C.7}
\]

The verifier checks that \(\kappa\) is an involution on the complete
\(160{,}244\)-candidate set. It has no fixed pair because a fixed pair would
require the integer equation \(2t=475\). Retaining the lexicographically
smaller member of each orbit gives \(80{,}122\) representatives. If a target
graph realizes a discarded member, its complement realizes the retained mate.

### C.3 Stage 1: degree-class spectral weights

Let \(m_d=|\{v:d_v=d\}|\), let \(D_s\) be the increasing set of degrees in
a candidate \(s\), and define nonnegative real variables

\[
Y_{d,k}=20\sum_{v:d_v=d}u_k(v)^2,
\qquad d\in D_s,\quad1\le k\le19.
\tag{C.8}
\]

Every target graph satisfies, for each \(d\in D_s\),

\[
\sum_{k=1}^{19}Y_{d,k}=19m_d,
\tag{C.9}
\]

\[
\sum_{k=1}^{19}kY_{d,k}=20m_dd,
\tag{C.10}
\]

\[
\sum_{k=1}^{19}k^2Y_{d,k}=20m_d(d^2+d),
\tag{C.11}
\]

and, for every \(1\le k\le19\),

\[
\sum_{d\in D_s}Y_{d,k}=20.
\tag{C.12}
\]

Equations (C.9)--(C.12), together with \(Y_{d,k}\ge0\), are exactly the
Stage-1 model. Orthostochasticity, eigenvector signs, and other nonlinear
conditions are omitted, so this is a relaxation. Exact Farkas certificates
eliminate \(63{,}235\) of the \(80{,}122\) representatives and leave
\(16{,}887\).

### C.4 Stage 2: local third moments and all serialized rows

For a vertex \(v\) of degree \(d\), define

\[
s_v=\sum_{u\sim v}d_u,\qquad
q_v=\#\{\text{triangles of }G\text{ containing }v\},\qquad
h_v=s_v-2q_v.
\tag{C.13}
\]

Direct multiplication gives

\[
(L^3)_{vv}=d^3+2d^2+s_v-2q_v=d^3+2d^2+h_v.
\tag{C.14}
\]

If \(R_v=V\setminus(N(v)\cup\{v\})\), then

\[
h_v=d+e(N(v),R_v),\qquad
d\le h_v\le d(20-d).
\tag{C.15}
\]

For a degree class put

\[
S_d=\sum_{v:d_v=d}s_v,\qquad
Q_d=\sum_{v:d_v=d}q_v,\qquad
H_d=S_d-2Q_d.
\tag{C.16}
\]

Also put

\[
A_d=\sum_{k=1}^{19}k^3Y_{d,k},\qquad
b_d=d^3+2d^2.
\tag{C.17}
\]

Summing (C.14) over the class gives the elimination identity

\[
A_d=20(m_db_d+H_d),\qquad
H_d=\frac{A_d}{20}-m_db_d.
\tag{C.18}
\]

The serialized Stage-2 model contains \(S_d\), but it does **not** contain
\(H_d\) or \(Q_d\) as variables and does not serialize (C.18) as an extra row.
Those symbols only derive the six necessary inequalities below.

The graph-triangle bounds give

\[
m_dd\le H_d\le m_dd(20-d),\qquad
H_d\le S_d\le H_d+2m_d\binom d2.
\tag{C.19}
\]

For a degree-\(d\) vertex, the number of complement triangles through it is

\[
\overline q_v=\binom{19-d}{2}-95+s_v-q_v.
\tag{C.20}
\]

Consequently,

\[
m_d\left(190-2\binom{19-d}{2}\right)
\le S_d+H_d\le190m_d.
\tag{C.21}
\]

Let

\[
R_d^*=190-2\binom{19-d}{2}.
\]

After substituting (C.18), the exact six serialized inequalities are

\[
\begin{aligned}
A_d &\ge20m_d(b_d+d),\\
A_d &\le20m_d\bigl(b_d+d(20-d)\bigr),\\
A_d-20S_d &\le20m_db_d,\\
-A_d+20S_d &\le40m_d\binom d2-20m_db_d,\\
-A_d-20S_d &\le-20m_d(b_d+R_d^*),\\
A_d+20S_d &\le20m_d(b_d+190).
\end{aligned}
\tag{C.22}
\]

Delete one occurrence of \(d\) from the degree multiset and sort the remaining
entries as \(r_1\le\cdots\le r_{19}\). A degree-\(d\) neighbor set selects
\(d\) distinct entries, so

\[
m_d\sum_{i=1}^{d}r_i
\le S_d\le
m_d\sum_{i=20-d}^{19}r_i.
\tag{C.23}
\]

Oriented-edge double counting gives

\[
\sum_{d\in D_s}S_d=2280.
\tag{C.24}
\]

Stage 2 consists of Stage 1, real \(S_d\) variables with bounds (C.23), the
six inequalities (C.22), and equality (C.24). It eliminates \(16{,}542\) of
the \(16{,}887\) Stage-1 survivors and leaves \(345\).

### C.5 Stage 3: degree-pair and degree-triple class model

Fix one of the \(345\) Stage-2 survivors. For \(a\le b\) in \(D_s\), define

\[
P_{a,b}=
\begin{cases}
\binom{m_a}{2},&a=b,\\
m_am_b,&a<b.
\end{cases}
\tag{C.25}
\]

For a nondecreasing triple \(z=(a,b,c)\), let \(\nu_d(z)\) be the
multiplicity of \(d\) in \(z\), and define

\[
P_z=\prod_d\binom{m_d}{\nu_d(z)}.
\tag{C.26}
\]

Triples with \(P_z=0\) are omitted. For an actual graph define:

- \(E_{a,b}\): the number of graph edges whose endpoint-degree multiset is
  \(\{a,b\}\);
- \(T_z\): the number of graph triangles whose vertex-degree multiset is \(z\);
- \(C_z\): the number of complement triangles whose vertices have
  original-graph degree multiset \(z\).

Their elementary capacities are

\[
0\le E_{a,b}\le P_{a,b},\qquad
0\le T_z,C_z\le P_z.
\tag{C.27}
\]

#### C.5.1 Stub and triangle totals

Counting degree-\(d\) edge ends gives

\[
2E_{d,d}+\sum_{b\ne d}E_{\min(d,b),\max(d,b)}=m_dd.
\tag{C.28}
\]

The graph and complement triangle totals are

\[
\sum_zT_z=t,\qquad
\sum_zC_z=475-t.
\tag{C.29}
\]

#### C.5.2 Graph classwise third moments

Define

\[
S_d^G
=2dE_{d,d}
+\sum_{b\ne d}bE_{\min(d,b),\max(d,b)},
\tag{C.30}
\]

and

\[
Q_d^G=\sum_z\nu_d(z)T_z.
\tag{C.31}
\]

The graph classwise \(L^3\) equation is

\[
\sum_{k=1}^{19}k^3Y_{d,k}
=20\left[m_d(d^3+2d^2)+S_d^G-2Q_d^G\right].
\tag{C.32}
\]

The verifier serializes (C.32) after substituting (C.30)--(C.31); those
definitions are not additional rows.

#### C.5.3 Complement classwise third moments

An original degree-\(d\) vertex has complement degree \(19-d\), and

\[
\overline Y_{19-d,k}=Y_{d,20-k}.
\tag{C.33}
\]

For \(a\le b\), define

\[
\gamma_d(a,b)=
\begin{cases}
2(19-d),&a=b=d,\\
19-b,&a=d<b,\\
19-a,&a<d=b,\\
0,&d\notin\{a,b\}.
\end{cases}
\tag{C.34}
\]

There are \(P_{a,b}-E_{a,b}\) complement edges of original class pair
\((a,b)\). Hence

\[
S_d^{\overline G}
=\sum_{a\le b}\gamma_d(a,b)(P_{a,b}-E_{a,b}),
\tag{C.35}
\]

and

\[
Q_d^{\overline G}=\sum_z\nu_d(z)C_z.
\tag{C.36}
\]

Put \(\overline b_d=(19-d)^3+2(19-d)^2\). Applying the local \(L^3\)
identity to the complement and moving the \(-E_{a,b}\) terms to the left gives
the exact verifier row

\[
\sum_{k=1}^{19}k^3Y_{d,20-k}
+20\sum_{a\le b}\gamma_d(a,b)E_{a,b}
+40\sum_z\nu_d(z)C_z
=20m_d\overline b_d
+20\sum_{a\le b}\gamma_d(a,b)P_{a,b}.
\tag{C.37}
\]

The \(E_{a,b}\) coefficient is positive because the complement uses
\(P_{a,b}-E_{a,b}\).

#### C.5.4 Pair-incidence and wedge inequalities

For \(a\le b\), define

\[
\pi_{a,b}(z)=
\begin{cases}
\binom{\nu_a(z)}2,&a=b,\\
\nu_a(z)\nu_b(z),&a<b.
\end{cases}
\tag{C.38}
\]

The graph edge--triangle incidence bound is

\[
\sum_z\pi_{a,b}(z)T_z
\le(\min(a,b)-1)E_{a,b}.
\tag{C.39}
\]

An original nonedge of class \((a,b)\) is a complement edge with endpoint
degrees \(19-a,19-b\), so

\[
\sum_z\pi_{a,b}(z)C_z
\le(18-\max(a,b))(P_{a,b}-E_{a,b}).
\tag{C.40}
\]

The graph and complement wedge bounds are

\[
\sum_z\nu_d(z)T_z\le m_d\binom d2,\qquad
\sum_z\nu_d(z)C_z\le m_d\binom{19-d}{2}.
\tag{C.41}
\]

Stage 3 comprises spectral rows (C.9)--(C.12), bounds (C.27), equations
(C.28)--(C.29), the substituted classwise rows (C.32) and (C.37), and
inequalities (C.39)--(C.41).

#### C.5.5 Continuous-relaxation and integrality semantics

For an actual graph, \(Y\) is generally real, whereas \(E,T,C\) are integer
graph counts. In each of the \(343\) ordinary Stage-3 leaves, the verifier
allows \(E,T,C\) to be real. Each ordinary certificate therefore proves
infeasibility of a continuous relaxation containing every actual mixed graph
point. Integrality metadata is not imposed in those root LPs. It is consulted
only to validate the final branch variable. Root certificates eliminate
\(343\) of the \(345\) models and leave two roots.

### C.6 Exact Farkas convention

Before standardization, write a model as

\[
A_{\rm eq}x=b_{\rm eq},\qquad
A_{\rm ub}x\le b_{\rm ub},\qquad
\ell_j\le x_j\le u_j,
\tag{C.42}
\]

where every lower bound is finite. Substitute \(x=\ell+x'\), \(x'\ge0\).
For each inequality add a nonnegative slack \(s\); for each finite upper bound
add a nonnegative slack \(r\):

\[
\begin{aligned}
A_{\rm eq}x'&=b_{\rm eq}-A_{\rm eq}\ell,\\
A_{\rm ub}x'+s&=b_{\rm ub}-A_{\rm ub}\ell,\\
x'_j+r_j&=u_j-\ell_j.
\end{aligned}
\tag{C.43}
\]

This gives an integer standard form

\[
Bw=h,\qquad w\ge0.
\tag{C.44}
\]

A sparse integer row multiplier \(z\) is a contradiction certificate when

\[
B^{\mathsf T}z\ge0,\qquad h^{\mathsf T}z<0.
\tag{C.45}
\]

A feasible \(w\) would instead give
\(h^{\mathsf T}z=w^{\mathsf T}B^{\mathsf T}z\ge0\). Equality-row
multipliers may have either sign. Every model-inequality and upper-bound row
has its own \(+1\) slack column, so its multiplier must be nonnegative. The
checker verifies lower-bound shifts, sparse indices, integer coefficients,
slack-row signs, every component of \(B^{\mathsf T}z\), and the strict
inequality \(h^{\mathsf T}z<0\). It reconstructs the model from candidate data
and trusts neither serialized matrices nor floating-point solver verdicts.

### C.7 Deterministic variable, row and certificate serialization

For every candidate, \(D_s\) is increasing. Stage-1 variables are
\(Y_{d,k}\), first by increasing \(d\), then by \(k=1,\ldots,19\). Stage 2
uses the same block and appends \(S_d\) in increasing degree order. The class
model orders variables as:

1. \(Y_{d,k}\), first by increasing \(d\), then \(k\);
2. \(E_{a,b}\) for lexicographically ordered pairs \(a\le b\);
3. \(T_z\) for lexicographically ordered nondecreasing triples with \(P_z>0\);
4. \(C_z\) in the same triple order.

Standard-form rows are ordered as:

1. equality rows in construction order;
2. model inequalities in construction order;
3. finite variable upper bounds in variable order.

For Stage 1 and Stage 2, equality order is the three class moments
(C.9)--(C.11) for increasing \(d\), the spectral-column equations (C.12) for
increasing \(k\), and, in Stage 2, (C.24). Stage-2 inequalities are the six
rows (C.22) for each increasing \(d\). Finite \(S_d\) upper bounds from
(C.23) appear later with the variable upper-bound rows; their lower bounds are
handled by the shift in (C.43).

For the class model, equality order is:

1. spectral class moments for increasing \(d\);
2. spectral-column equations for increasing \(k\);
3. stub equations for increasing \(d\);
4. graph and complement triangle totals;
5. graph classwise \(L^3\) rows for increasing \(d\);
6. complement classwise \(L^3\) rows for increasing \(d\).

Class inequalities are the graph and complement pair-incidence rows for each
lexicographically ordered pair, followed by graph and complement wedge rows
for increasing \(d\). Upper-bound rows then follow the \(E,T,C\) order.

Each Stage-1, Stage-2, or class certificate shard has schema

~~~json
{
  "format": "s20-standard-form-farkas-z-v1",
  "stage": "stage1 | stage2 | class",
  "records": [
    ["source_index", [["row_index", "integer_multiplier"]]]
  ]
}
~~~

The quoted field values in this display denote types, not literal values in an
actual shard. Within each certificate, nonzero row indices are strictly
increasing, unique, and in range. Across consecutively numbered shards, source
indices are globally increasing and equal the exact source-minus-survivor
index list. Zero multipliers and noninteger coefficients are rejected.

The final branch file is certs/branch_leaves.json.gz. For each root it binds
the source sequence and triangle count to a verified variable index and name,
the integer split floor, and one sparse certificate for each child. Its
metadata must agree with data/final_integer_roots.json.

### C.8 Set partition, ledger identities and exact coverage

At every certified layer,

\[
S_i=L_i\mathbin{\dot\cup}S_{i+1},\qquad
L_i=S_i\setminus S_{i+1}.
\tag{C.46}
\]

The exact coverage ledger is:

| Layer | Source | Exact Farkas leaves | Survivors |
|---|---:|---:|---:|
| complement representatives | \(80{,}122\) | -- | \(80{,}122\) |
| Stage 1 | \(80{,}122\) | \(63{,}235\) | \(16{,}887\) |
| Stage 2 | \(16{,}887\) | \(16{,}542\) | \(345\) |
| Stage 3 | \(345\) | \(343\) | \(2\) roots |
| integer split | \(2\) roots | \(4\) | \(0\) |

The five complete uncompressed ledger-byte identities are

~~~text
base candidates (160,244)
8523a5c0c0bc1c4f2d6e76be0979f984954b393393e483f4047529b0d48245e2

complement representatives / Stage-1 source (80,122)
851b058e4c5f933e22bbd61051293342e5788fd3a524fa295266dcde4633e0d4

Stage-1 survivors / Stage-2 source (16,887)
a325883c2b1d7919f70ac82d2460733f1fe9b3e373f633b42a1b6ae512fc3ad4

Stage-2 survivors / class source (345)
dd39bed2528cea440158a0161451dc29dbbb2b36fde0f91ae6558ee7424d8798

class survivors / final roots (2)
b3b6352252492f17517e00f25307f8370daec1eb50786d598218c8f540859ecc
~~~

The checker verifies ordered subset membership, uniqueness, exact set
difference, source order, shard numbering, and shard hashes. It records zero
uncovered cases, unknown outcomes, timeouts, or crashes.

### C.9 Final \(E_{2,2}\) split

The two surviving roots are

\[
\begin{aligned}
s^{(0)}={}&(2,2,2,4,6,6,7,7,9,9,9,10,12,12,14,14,15,16,17,17),\\
t^{(0)}={}&229,
\end{aligned}
\tag{C.47}
\]

and

\[
\begin{aligned}
s^{(1)}={}&(2,2,2,5,5,6,6,8,9,9,9,10,12,12,14,14,15,16,17,17),\\
t^{(1)}={}&231.
\end{aligned}
\tag{C.48}
\]

Each has eleven degree classes and hence \(11\cdot19=209\) spectral
variables. The checker verifies by name, not merely by position, that
class-model variable index \(209\) is \(E_{2,2}\). Both sequences have three
degree-\(2\) vertices, so for an actual graph

\[
E_{2,2}\in\{0,1,2,3\}.
\tag{C.49}
\]

For each root, the adjacent children are

\[
E_{2,2}\le0\qquad\text{and}\qquad E_{2,2}\ge1.
\tag{C.50}
\]

The left child fixes \(E_{2,2}=0\); the right contains \(1,2,3\). The
children are disjoint and exhaustive for the actual integer count. Each of
the four child continuous relaxations has an exact Farkas certificate. Thus

\[
63{,}235+16{,}542+343+4=80{,}124
\tag{C.51}
\]

exact leaves cover all complement representatives, with each final
representative replaced by two branch leaves.

### C.10 Universal graph-to-model implication

Suppose a target graph existed. Equations (C.1)--(C.5) put its degree
sequence and triangle count in the complete enumeration. After complementing
if necessary, it realizes a retained representative. Its eigenprojector
diagonals give \(Y\) satisfying Stage 1. Its actual neighbor-degree sums give
\(S\) satisfying Stage 2. Its actual edge, graph-triangle, and
complement-triangle counts give \(E,T,C\) satisfying every Stage-3 equation,
capacity, and incidence inequality. If it reaches a final root, its integer
\(E_{2,2}\) lies in exactly one child of (C.50).

The exact certificate at the corresponding leaf contradicts feasibility by
(C.45), and the verified set partition ensures that no candidate avoids a
leaf. Therefore no target graph exists.

### C.11 Reproduction identities and provenance note

The release launcher pins the following internal helper files:

~~~text
verification/n20/verify_enumeration_v2.py
4df5db86179076364561689d8a4e62cba67890ded650ecc354f53949492bdbd9

verification/n20/verify_certificates_v2.py
b12dfe89fa5b8562844da9f963fdc9782336a3ef29219f6d481dea71170d385e

verification/n20/audit_cycle_identity_v2.py
c59c0255ba40f7b311c614b7493b760460a622ceb09fca08ce1669230248f956
~~~

With those helpers, the telemetry-free canonical JSON has SHA-256

~~~text
ebc3d8065c3f0c2e869e940f2d50c572292c45646a5ee6ac658a3f805b1ccbac
~~~

The combined release retains two fresh full macOS replay transcripts for this
current helper set:

~~~text
logs/n20-current-run1.log
9b7ad79994af963e0ba8acfce70d2c3f29c451fb914eae4d57a4d98010989688

logs/n20-current-run2.log
f85d291f862188b2f9b653f512ea458b971f9a4910f79cddf275a2b8f302b3ec
~~~

Both runs exit 0 and reproduce the canonical bytes under the offline sandbox.
The expected terminal statuses are:

~~~text
INDEPENDENT_ENUMERATION_V2_PASS
INDEPENDENTLY_VERIFIED_UNSAT
INDEPENDENT_REPRODUCTION_PASS
~~~

These are internal cross-check status labels; Section 7.3 states their trust
boundary. Earlier wrapper identities are recorded in
`ARTIFACT_PROVENANCE.md`.
