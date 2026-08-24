## Appendix B: Complete computational specification for the order-16 proof

This appendix specifies the finite computation contained in the frozen
order-16 archive `snn16-certified-nonexistence-20260821.zip`. The
mathematical implication used throughout is

\[
\text{target graph}
\Longrightarrow
\text{feasible point of a necessary relaxation}.
\]

Consequently, exact infeasibility of a relaxation rules out the graph. The
converse implication is never assumed.

### B.1 Frozen identities and candidate enumeration

Let \(G\) be a simple graph on 16 vertices with hypothetical Laplacian spectrum
\(\{0,1,\ldots,15\}\). The spectral trace identities, the local degree bound,
and the graph/complement triangle identity give

\[
\sum_v d_v=120,\qquad
\sum_v d_v^2=1120,\qquad
\sum_v d_v^3-6t=11040,
\tag{B.1}
\]

\[
2\le d_v\le13,\qquad
54\le t\le166,\qquad
t(G)+t(\overline G)=220.
\tag{B.2}
\]

The strict verifier enumerates every nondecreasing tuple in the lexicographic
order induced by the Python standard-library combinations-with-replacement
iterator over degrees \(2,\ldots,13\),
\(s=(d_1,\ldots,d_{16})\) satisfying the first two equations in (B.1). It then
applies the Erdős--Gallai inequalities, and finally retains a tuple precisely
when

\[
t=\frac{\sum_i d_i^3-11040}{6}
\tag{B.3}
\]

is an integer in \([54,166]\). The exact ledger is

| Enumeration layer | Exact count |
|---|---:|
| moment tuples | \(2{,}249\) |
| Erdős--Gallai graphical tuples | \(2{,}233\) |
| graphical tuples with admissible integral \(t\) | \(2{,}077\) |

The certificate records occur in exactly this final enumeration order. A
separate internal semantic audit enumerates the moment solutions by degree
multiplicities and tests graphicality by Havel--Hakimi. It reproduces all three
counts and the complete ordered list of 2,077 pairs \((s,t)\). This is an
internal cross-check using a different enumeration organization, not an
external replication.

For the remainder fix one candidate \((s,t)\). Let

\[
m_d=|\{i:d_i=d\}|,\qquad
D=\{d:m_d>0\},
\tag{B.4}
\]

with \(D\) always traversed in increasing order.

### B.2 Stage 1: spectral-weight relaxation

Choose an orthonormal Laplacian eigenbasis \(u_0,\ldots,u_{15}\), where \(u_k\)
has eigenvalue \(k\), and define

\[
Y_{d,k}=16\sum_{v:d_v=d}u_k(v)^2,
\qquad d\in D,\quad 1\le k\le15.
\tag{B.5}
\]

The \(Y_{d,k}\) are nonnegative **real** variables. No integrality,
orthostochasticity, or integral-eigenvector condition is imposed. Every target
graph satisfies

\[
\sum_{k=1}^{15}Y_{d,k}=15m_d,
\tag{B.6}
\]

\[
\sum_{k=1}^{15}kY_{d,k}=16m_dd,
\tag{B.7}
\]

\[
\sum_{k=1}^{15}k^2Y_{d,k}=16m_d(d^2+d)
\tag{B.8}
\]

for every \(d\in D\), and

\[
\sum_{d\in D}Y_{d,k}=16
\tag{B.9}
\]

for every \(1\le k\le15\). Stage 1 consists exactly of (B.6)--(B.9) and
\(Y_{d,k}\ge0\). Exact rational Farkas certificates eliminate 1,359 of the
2,077 candidates, leaving 718.

### B.3 Stage 2: local-third-moment relaxation

Stage 2 retains all Stage-1 variables and equations and adds one nonnegative
real variable \(S_d\) for each \(d\in D\). Semantically,

\[
S_d=\sum_{v:d_v=d}\sum_{u\sim v}d_u.
\tag{B.10}
\]

For one occurrence of \(d\), delete that occurrence from \(s\). Let \(\ell_d\)
and \(u_d\) be the sums of the \(d\) smallest and \(d\) largest entries of the
remaining 15-tuple. Then

\[
m_d\ell_d\le S_d\le m_du_d.
\tag{B.11}
\]

Put

\[
b_d=d^3+2d^2,\qquad
K_d=\sum_{k=1}^{15}k^3Y_{d,k}.
\tag{B.12}
\]

There is no separately serialized \(H_d\) variable. It is the derived real
quantity

\[
H_d=\frac{K_d}{16}-m_db_d
=\sum_{v:d_v=d}(s_v-2q_v).
\tag{B.13}
\]

The exact Stage-2 inequalities are

\[
m_dd\le H_d\le m_dd(16-d),
\tag{B.14}
\]

\[
H_d\le S_d\le H_d+2m_d\binom d2,
\tag{B.15}
\]

and, from the local complement-triangle identity,

\[
m_d\left(120-2\binom{15-d}{2}\right)
\le S_d+H_d\le120m_d.
\tag{B.16}
\]

The final Stage-2 equality is

\[
\sum_{d\in D}S_d=1120.
\tag{B.17}
\]

For avoidance of sign or scaling ambiguity, the verifier serializes the six
base inequality rows for each increasing \(d\) in this order:

\[
-K_d\le-16m_d(b_d+d),
\tag{B.18}
\]

\[
K_d\le16m_d\{b_d+d(16-d)\},
\tag{B.19}
\]

\[
K_d-16S_d\le16m_db_d,
\tag{B.20}
\]

\[
-K_d+16S_d\le32m_d\binom d2-16m_db_d,
\tag{B.21}
\]

\[
-K_d-16S_d
\le-16m_d\left\{b_d+120-2\binom{15-d}{2}\right\},
\tag{B.22}
\]

\[
K_d+16S_d\le16m_d(b_d+120).
\tag{B.23}
\]

Variable-bound rows are appended later as specified in Section B.7. Exact
rational Farkas certificates eliminate 676 of the 718 Stage-1 survivors. The
remaining 42 candidates are the ordered records in
data/survivors42_exact.json.

### B.4 Final degree-class model

For \(a,b\in D\), \(a\le b\), define the available unordered vertex-pair
capacity

\[
P_{a,b}=
\begin{cases}
\binom{m_a}{2},&a=b,\\
m_am_b,&a<b.
\end{cases}
\tag{B.24}
\]

For a nondecreasing degree triple \(z=(a,b,c)\), let \(\mu_d(z)\) be the
multiplicity of \(d\) in \(z\) and define

\[
P_z=\prod_{d\in D}\binom{m_d}{\mu_d(z)}.
\tag{B.25}
\]

Only triples with \(P_z>0\) are included. The model contains:

- the nonnegative real variables \(Y_{d,k}\) from Stage 1;
- \(E_{a,b}\), semantically the integer number of graph edges joining degree
  classes \(a,b\);
- \(T_z\), semantically the integer number of graph triangles with original
  degree multiset \(z\);
- \(C_z\), semantically the integer number of complement triangles whose
  vertices have original graph-degree multiset \(z\).

Thus \(Y\) is real, whereas actual graph values of \(E,T,C\) are integers. The
model declares every \(E,T,C\) variable integer and imposes

\[
0\le E_{a,b}\le P_{a,b},\qquad
0\le T_z\le P_z,\qquad
0\le C_z\le P_z.
\tag{B.26}
\]

#### B.4.1 Stub and total-triangle equations

For every \(d\in D\),

\[
2E_{d,d}+\sum_{b\in D\setminus\{d\}}
E_{\min(d,b),\max(d,b)}=m_dd.
\tag{B.27}
\]

The graph and complement totals are

\[
\sum_zT_z=t,\qquad
\sum_zC_z=220-t.
\tag{B.28}
\]

#### B.4.2 Graph classwise third moments

Define

\[
S_d^G=2dE_{d,d}
+\sum_{b\in D\setminus\{d\}}
bE_{\min(d,b),\max(d,b)},
\tag{B.29}
\]

\[
R_d^G=\sum_z\mu_d(z)T_z.
\tag{B.30}
\]

For each \(d\in D\), the graph classwise \(L^3\) equation is

\[
\sum_{k=1}^{15}k^3Y_{d,k}
=16\left\{m_d(d^3+2d^2)+S_d^G-2R_d^G\right\}.
\tag{B.31}
\]

#### B.4.3 Complement classwise third moments

An original degree-\(d\) vertex has complement degree \(15-d\), and

\[
\overline Y_{15-d,k}=Y_{d,16-k}.
\tag{B.32}
\]

There are \(P_{a,b}-E_{a,b}\) complement edges between original degree classes
\(a,b\). Therefore define

\[
S_d^{\overline G}
=2(15-d)(P_{d,d}-E_{d,d})
+\sum_{b\in D\setminus\{d\}}
(15-b)\left(
P_{\min(d,b),\max(d,b)}
-E_{\min(d,b),\max(d,b)}
\right),
\tag{B.33}
\]

\[
R_d^{\overline G}=\sum_z\mu_d(z)C_z.
\tag{B.34}
\]

The complement classwise \(L^3\) equation is

\[
\sum_{k=1}^{15}k^3Y_{d,16-k}
=16\left\{
m_d\bigl((15-d)^3+2(15-d)^2\bigr)
+S_d^{\overline G}-2R_d^{\overline G}
\right\}.
\tag{B.35}
\]

#### B.4.4 Pair-incidence inequalities

For \(a\le b\), set

\[
\kappa_{a,b}(z)=
\begin{cases}
\binom{\mu_a(z)}2,&a=b,\\
\mu_a(z)\mu_b(z),&a<b.
\end{cases}
\tag{B.36}
\]

This is the number of degree-\((a,b)\) vertex pairs in a triple of type \(z\).
Every graph edge of endpoint degrees \(a,b\) lies in at most
\(\min(a,b)-1\) graph triangles. Every complement edge between the same original
classes has complement endpoint degrees \(15-a,15-b\), and hence lies in at
most \(14-\max(a,b)\) complement triangles. The exact inequalities are

\[
\sum_z\kappa_{a,b}(z)T_z
\le(\min(a,b)-1)E_{a,b},
\tag{B.37}
\]

\[
\sum_z\kappa_{a,b}(z)C_z
\le(14-\max(a,b))(P_{a,b}-E_{a,b}).
\tag{B.38}
\]

#### B.4.5 Degree-class wedge inequalities

Counting triangle incidences at vertices in one degree class gives

\[
\sum_z\mu_d(z)T_z\le m_d\binom d2,
\tag{B.39}
\]

\[
\sum_z\mu_d(z)C_z\le m_d\binom{15-d}{2}.
\tag{B.40}
\]

Equations (B.6)--(B.9), (B.27)--(B.28), (B.31), and (B.35), together with
(B.26) and (B.37)--(B.40), are the complete final class model. No graph
isomorphism quotient or symmetry-breaking constraint is present.

### B.5 Why every target graph maps into the models

For a target graph, (B.5) supplies nonnegative real \(Y\) and the spectral
projector identities give (B.6)--(B.9). Actual neighbor-degree sums supply
\(S_d\); the diagonal identity

\[
(L^3)_{vv}=d_v^3+2d_v^2+s_v-2q_v
\tag{B.41}
\]

and \(s_v-2q_v=d_v+e(N(v),R_v)\) give (B.13)--(B.15). The local
complement-triangle identity gives (B.16). Actual degree-class edge and triangle
counts supply integer \(E,T,C\). Their pair and triple capacities, stub counts,
triangle totals, classwise third moments, edge-triangle incidences, and wedge
counts give every row in Section B.4. Complement equations follow from

\[
L(\overline G)=16I-J-L(G).
\tag{B.42}
\]

Thus every target graph gives a feasible mixed point. The relaxations may also
contain points that do not come from graphs; that enlargement is harmless for
an infeasibility proof.

### B.6 Integer branching and leaf semantics

At the root of each of the 42 final models, \(Y\) is real and \(E,T,C\) have the
integer semantics and bounds in (B.26). A branch node stores a variable index
\(j\) belonging to the declared integer-variable set and an integer \(a\). Its
children impose

\[
x_j\le a
\qquad\text{and}\qquad
x_j\ge a+1.
\tag{B.43}
\]

These children are disjoint and cover every integer value allowed at the
parent. The verifier propagates current lower and upper bounds recursively and,
for current bounds \(\ell_j,u_j\), requires \(\ell_j\le a<u_j\).

In the frozen forest all 66 branch nodes happen to branch on \(E\)-variables.
This does not assume that \(T\) or \(C\) is continuous in an actual graph. At a
leaf the stored Farkas certificate proves infeasibility of the **continuous**
linear relaxation under the accumulated branch bounds. Hence it also excludes
the smaller set in which all \(E,T,C\) are integral; no further branch is
needed.

The 42 rooted trees contain

| Quantity | Exact value |
|---|---:|
| roots / final class models | \(42\) |
| all tree nodes | \(174\) |
| branch nodes | \(66\) |
| Farkas leaves | \(108\) |
| maximum depth | \(10\) |

The full-binary-forest identity \(108=66+42\) is an additional elementary check
on the tree ledger.

### B.7 Farkas certificates and deterministic serialization

Every model is represented as

\[
Ax\le b,\qquad Cx=e.
\tag{B.44}
\]

Finite lower bounds are appended as rows \(-x_j\le-\ell_j\); finite upper
bounds are appended as \(x_j\le u_j\). A certificate consists of rational
multipliers \(y,z\) such that

\[
y\ge0,\qquad
y^{\mathsf T}A+z^{\mathsf T}C=0,\qquad
y^{\mathsf T}b+z^{\mathsf T}e<0.
\tag{B.45}
\]

The frozen 2,143 certificates are normalized so that the last quantity is
exactly \(-1\). The verifier checks cancellation and negativity over
fractions.Fraction, without a floating tolerance. Equation (B.45) contradicts
feasibility because a feasible \(x\) would give \(0\le-1\).

The deterministic variable order is:

1. \(Y_{d,k}\), with \(d\) increasing and then \(k=1,\ldots,15\);
2. in Stage 2 only, \(S_d\) with \(d\) increasing;
3. in a class model, \(E_{a,b}\) for lexicographically ordered pairs
   \(a\le b\);
4. \(T_z\) for lexicographically ordered nondecreasing triples with \(P_z>0\);
5. \(C_z\) in the same triple order.

The deterministic equality-row order is:

1. for each increasing \(d\), the three rows (B.6)--(B.8);
2. for \(k=1,\ldots,15\), row (B.9);
3. in Stage 2, the single final row (B.17);
4. in a class model instead: stub rows (B.27) by increasing \(d\), the graph
   and complement totals (B.28), graph \(L^3\) rows (B.31) by increasing \(d\),
   and complement \(L^3\) rows (B.35) by increasing original \(d\).

The deterministic base-inequality order is:

1. in Stage 2, rows (B.18)--(B.23) for each increasing \(d\);
2. in a class model, for each lexicographic pair \(a\le b\), graph row (B.37)
   followed by complement row (B.38);
3. for each increasing \(d\), graph row (B.39) followed by complement row
   (B.40).

After those base inequalities, every finite lower bound is appended in variable
index order, followed by every finite upper bound in variable index order. This
order determines the row indices referenced by a Farkas certificate.

#### B.7.1 Degree-reduction JSON

certs/degree_reduction.json.gz has top-level format
snn16-degree-reduction-v1 and fields

    base_count, counts, format, records

There are exactly 2,077 ordered records. Each record contains sequence,
triangles, and one of the kinds stage1_farkas, stage2_farkas, or survivor. The
first two kinds additionally contain cert; a survivor contains no certificate.
The exact kind counts are

    stage1_farkas  1359
    stage2_farkas   676
    survivor         42

#### B.7.2 Certificate JSON

A certificate is an object with arrays y and z. A nonzero rational multiplier
is encoded as

    [row_index, numerator, denominator]

with nonzero denominator. Omitted row indices mean multiplier zero. The y array
indexes the complete inequality list, including bounds, and must be
nonnegative. The z array indexes the equality list and is unrestricted in sign.
Duplicate or out-of-range indices are rejected by the strict verifier.

#### B.7.3 Class-exhaustion JSON

certs/class_exhaustion.json.gz has top-level format
snn16-class-exhaustion-v1, count 42, and an ordered items array. Every item
records its index, sequence, triangle count, statistics and root tree. A tree
node has one of the forms

    {"type":"leaf","cert":{"y":[],"z":[]}}

or

    {
      "type":"branch",
      "var":143,
      "floor":4,
      "left":{},
      "right":{}
    }

Both displays are schema illustrations: actual leaf multiplier arrays are
populated, and the empty child objects are placeholders for recursively encoded
nodes. The verifier reconstructs the model from the sequence and triangle
count; no matrix stored in the certificate is trusted.

### B.8 Exact coverage and frozen identities

The degree-reduction records and class forest give the disjoint coverage ledger

\[
2077=1359+676+42,
\tag{B.46}
\]

\[
2143=1359+676+108.
\tag{B.47}
\]

The strict verifier matches every degree record to the freshly enumerated
\((s,t)\) at the same position, matches the 42 class items to exactly the 42
survivors, checks every branch recursively, and verifies all 2,143 rational
contradictions. The semantic audit independently reorganizes the finite
degree-sequence enumeration, checks the survivor and complement ledgers, tests
selected non-spectral graph-to-model identities on structured and deterministic
random graphs, and confirms that a one-unit certificate mutation is rejected.

The frozen artifact identities are:

    snn16-certified-nonexistence-20260821.zip
    f7f127da4fd6227bd66eadfc22847da270caf2d29b8bedbc16aabee548c8c847

    certs/degree_reduction.json.gz
    950d05274bf8e7234c0c72efa78927feeeacadc33ba5274f42c738ff3e8562c9

    certs/class_exhaustion.json.gz
    51cc5417f922f6bfceb3704c81a1691d813f76550517397269404b35225cc9bd

    data/survivors42_exact.json
    ca899c72bf4e17c18663ee5b0d58a044347dcaad078c1a37f02bf551c1a09fa7

    code/verify_certificates.py
    7fdc4932f8f6a50b7bef06db8537c3eb621ae5cea9ad6910c53ea455a0458d61

    code/audit_semantics.py
    a6908f2f844c35cc806e356cef121ff2984662c022905276a6b910d7dcaf026c

A clean replay from the extracted ZIP is

    ./REPRODUCE.sh

and has expected terminal statuses VERIFIED_UNSAT and SEMANTIC_AUDIT_PASSED.
The strict verifier uses Python standard-library arithmetic only. The archive
records successful normal and optimized Python verification; certificate
regeneration is not part of the trusted replay.

The combined release additionally stores a current normal/optimized transcript:

~~~text
logs/n16-current.log
~~~

The combined replay normalizes away elapsed time, requires the two verifier
records to agree exactly, and requires the resulting summary bytes to equal:

~~~text
results/ORDER16_RESULT_FINAL.json
~~~

### B.9 Generator/verifier lineage and limits of independence

The untrusted generator uses code/exact_models.py, SciPy/HiGHS and SymPy.
Floating-point optimization is used only to discover supports and branch
choices; proposed multipliers are exactified before storage. None of the solver
success or infeasibility flags is a premise of the theorem.

The trusted strict verifier is a separately implemented **internal** Python
program. It uses only the standard library, re-enumerates the candidate list,
reconstructs every row from the mathematical definitions, and checks the
stored rational multipliers and integer branches. It does not import the
generator's exact_models.py or farkas_tools.py.

The semantic audit supplies another enumeration organization, Havel--Hakimi
graphicality, selected graph-identity tests, coverage comparisons and mutation
rejection. Its mutation test loads the strict verifier. Both programs are
internal Python implementations; Section 7.3 states their trust boundary.

The remaining trusted boundary consists of the analytic graph-to-model mapping
in Section B.5, the correctness of the internal Python verifier and runtime,
and integrity of the frozen hashes. Those limitations affect the validation
status of the computer-assisted proof but do not turn floating-point discovery
output into a trusted premise.
