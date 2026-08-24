# Literature and novelty search record

**Cutoff:** 24 August 2026

**Scope:** the conjectured non-realizability of
\(S_{n,n}=\{0,1,\ldots,n-1\}\) as the Laplacian spectrum of a finite
simple graph, with particular attention to \(n=16\) and \(n=20\).

**Purpose:** record what was actually checked before release of the combined
preprint. This is a reproducible search log, not a guarantee that inaccessible,
unindexed or unpublished work does not exist.

## 1. Sources and services actually checked

| Source or service | Queries or identifiers checked | Access and result |
|---|---|---|
| arXiv official record | `2607.06336`; web searches including `site:arxiv.org/abs/2607.06336 Johnston Plosker Varona Laplacian integral diagonalizable graphs n=16` | The official abstract and v1 record were accessible. A local copy of the v1 PDF and extracted text was also inspected. The paper explicitly says that it proves the \(n=12\) case and thereby makes \(n=16\) the smallest open case. |
| Wiley Online Library | DOI `10.1002/jgt.20412` and DOI `10.1002/jgt.21638`; title- and DOI-specific web searches | The official abstracts and bibliographic records for Das--Lee--Cheon and Goldberger--Neumann were accessible. The Goldberger--Neumann full PDF was not accessible through the checked Wiley PDF URL (HTTP 403), so its exact numerical threshold was not independently read from the primary theorem text. |
| Sacred Heart University Digital Commons | DOI `10.1002/jgt.20102`; exact title search for Fallat--Kirkland--Molitierno--Neumann | The institutional bibliographic page and abstract were accessible. They confirm the definition of \(S_{i,n}\), the realizability question and the \(S_{n,n}\) conjecture. The full journal PDF was not inspected in this review. |
| Sciendo official article PDF | DOI `10.2478/auom-2022-0023` | The complete 28-page publisher PDF was downloaded and text-extracted. Its SHA-256 in this review was `88350098a834cbb84187e88f899182d8f51bd1e853a69e40ba5e53f25e4d84e8`. |
| General web search | Exact and near-exact queries including `2026 "n=16" "S_{n,n}" Laplacian graph`, `2026 "order 16" "consecutive Laplacian" graph`, `2026 "order 20" "consecutive Laplacian" graph`, `"Laplacian spectrum" "0,1,...,15" graph`, and the analogous order-20 query | The searches located the papers listed below and no earlier public proof specifically resolving order 16 or order 20. Search-engine non-retrieval is not conclusive evidence of nonexistence. |
| Zenodo public Records API and direct record lookup | Broad queries involving `Laplacian`, `consecutive Laplacian`, `Laplacian spectrum n=16`, and `certified nonexistence Laplacian`; direct inspection of records `21772560` and `21777218` | The two directly inspected records concern unrelated CAT(0) and phase-retrieval problems. The broad API queries had noisy tokenized results and are not sufficient by themselves to certify novelty. No matching public order-16 or order-20 proof was identified in the returned records. |

The local arXiv v1 PDF inspected for Johnston--Plosker--Varona has SHA-256
`5d93de6d6de13ecb33b533309145741fd3ac704faf27f9b5b15f14dacc7ef5e0`.

### Services not claimed as checked

This review did **not** directly search MathSciNet, zbMATH Open, Scopus, Web
of Science, ProQuest, or a logged-in Google Scholar session. Crossref was not
queried as an independent database; DOI landing pages were reached through
publisher or general web results. No claim in the manuscript should imply
otherwise.

## 2. Primary and official-source findings

### 2.1 Fallat--Kirkland--Molitierno--Neumann (2005)

S. M. Fallat, S. J. Kirkland, J. J. Molitierno and M. Neumann,
"On graphs whose Laplacian matrices have distinct integer eigenvalues,"
*Journal of Graph Theory* **50** (2005), 162--174,
DOI `10.1002/jgt.20102`.

- The accessible institutional abstract confirms that the paper defines
  \(S_{i,n}=\{0,1,\ldots,n\}\setminus\{i\}\), investigates which such sets
  are Laplacian-realizable, and conjectures that \(S_{n,n}\) is not
  realizable for every \(n\ge2\).
- The exact coverage commonly attributed to this paper--\(n\le11\), prime
  \(n\), and \(n\equiv2,3\pmod4\)--was confirmed in the official abstract of
  Das--Lee--Cheon and in the primary full text of Johnston--Plosker--Varona.
  Because the Fallat journal PDF itself was not inspected here, the combined
  manuscript should not cite an unverified Fallat theorem or page number.

Official/institutional record:
<https://digitalcommons.sacredheart.edu/math_fac/21/>

### 2.2 Das--Lee--Cheon (2010)

K. Ch. Das, S.-G. Lee and G.-S. Cheon, "On the conjecture for certain
Laplacian integral spectrum of graphs," *Journal of Graph Theory* **63**
(2010), 106--113, DOI `10.1002/jgt.20412`.

The official abstract states the earlier coverage \(n\le11\), prime \(n\),
and \(n\equiv2,3\pmod4\). Its own stated contributions are structural:

- if the graph is connected and its largest Laplacian eigenvalue is
  \(n-1\), then its diameter is 2 or 3;
- if the largest and smallest positive Laplacian eigenvalues are \(n-1\)
  and 1, respectively, then both the graph and its complement have diameter
  3.

This paper does not, on the accessible abstract, resolve order 16 or order 20.

Official record:
<https://onlinelibrary.wiley.com/doi/abs/10.1002/jgt.20412>

### 2.3 Goldberger--Neumann (2013)

A. Goldberger and M. Neumann, "On a conjecture on a Laplacian matrix with
distinct integral spectrum," *Journal of Graph Theory* **72** (2013),
178--208, DOI `10.1002/jgt.21638`.

- The official abstract supports the statement that the conjecture holds for
  all sufficiently large \(n\), and that the paper treats more general spectra
  under trace conditions.
- The checked official abstract did not render the numerical bound legibly,
  and the primary PDF was unavailable from the checked Wiley endpoint.
- Hameed--Khan--Tyaglov restate the threshold as
  \(n\ge6{,}649{,}688{,}933\). That is a useful secondary confirmation, but
  this review did not independently verify the number in the primary
  Goldberger--Neumann theorem. The combined paper may safely say
  "sufficiently large orders." It should state the numerical threshold only
  if it labels Hameed et al. as the immediate source or after the primary
  theorem text is obtained and checked.
- Either formulation leaves 16 and 20 far below the large-order range.

Official record:
<https://onlinelibrary.wiley.com/doi/abs/10.1002/jgt.21638>

### 2.4 Hameed--Khan--Tyaglov (2022): citation-scope ruling

A. Hameed, Z. U. Khan and M. Tyaglov, "Laplacian energy and first Zagreb
index of Laplacian integral graphs," *Analele Științifice ale Universității
Ovidius Constanța* **30** (2022), 133--160,
DOI `10.2478/auom-2022-0023`.

**Ruling: relevant, but only for explicitly limited background and structural
claims.** The citation is appropriate for the following statements:

- it surveys the \(S_{n,n}\) conjecture and restates the known small- and
  large-order bounds;
- it reports a computation that self-complementary graphs through order 12 do
  not realize \(S_{n,n}\) (printed page 154);
- Proposition 5.7 proves that a graph realizing \(S_{n,n}\), if one exists,
  cannot be a Cartesian product of graphs (printed pages 154--155);
- it derives Laplacian-energy and Zagreb-index identities for the broader
  \(S_{i,n}\) setting.

It is **not** appropriate support for a claim that the authors proved a broad
new family of graph orders, resolved order 16 or order 20, or independently
verified the present certificate computations. The manuscript should split
the previous-work paragraph by source rather than attaching the vague phrase
"structural restrictions and broad classes of orders" jointly to references
[2--4].

Official PDF:
<https://sciendo.com/2/v2/download/article/10.2478/auom-2022-0023.pdf>

### 2.5 Johnston--Plosker--Varona (2026)

N. Johnston, S. Plosker and L. M. B. Varona, "Enumeration of Laplacian
integral and \(\{-1,0,1\}\)-diagonalizable graphs," arXiv:2607.06336v1
(submitted 7 July 2026), DOI `10.48550/arXiv.2607.06336`.

- The official abstract and v1 full text state that their enumeration proves
  the unrestricted \(n=12\) case of the \(S_{n,n}\) conjecture.
- They explicitly describe \(n=16\) as the smallest open case.
- Their text summarizes the earlier order coverage and says their result
  extends the verified finite range to \(n\le15\).
- They do not claim to resolve \(n=16\) or \(n=20\).

Official record:
<https://arxiv.org/abs/2607.06336>

## 3. Position of orders 16 and 20

The following conclusion uses only the coverage stated in the sources above:

1. the conjecture is covered through order 15;
2. Johnston--Plosker--Varona therefore identify 16 as the smallest open order;
3. order 17 is prime, order 18 is \(2\pmod4\), and order 19 is prime, so they
   fall in previously established classes;
4. order 20 is composite and \(0\pmod4\), and is the next order after 16 not
   covered by those standard classes;
5. if the two theorems in the combined manuscript are accepted, then 21 is
   the least order not covered by the **cited collection of results**.

The last wording is deliberately narrower than "21 is now the smallest open
case," which would require an exhaustive, continuously updated novelty search
including sources not accessed in this review.

## 4. Novelty language

### Supported strongest formulation

> Johnston, Plosker and Varona identified \(n=16\) as the smallest open case
> in July 2026. Within the order classes and finite cases covered by the
> results cited above, 16 and 20 are the two smallest orders not covered. The
> present paper establishes these two finite cases by separately checkable
> exact certificate-based computer-assisted proofs. The least order not
> covered by that cited collection of results is then 21.

A dated search statement may additionally say:

> The searches recorded in `LITERATURE_SEARCH.md`, completed on 24 August
> 2026, did not identify an earlier public proof resolving order 16 or order
> 20.

This must remain a report of search outcome, not an unconditional priority
claim.

### Expressions that require qualification or should be avoided

- Do not write "the \(S_{n,n}\) conjecture is proved/solved"; only two finite
  cases are proved.
- Do not write "all composite orders" or "all orders
  \(n\equiv0\pmod4\)."
- Do not describe the result as one uniform or simultaneous proof. The paper
  contains two logically separate theorem packages with related architecture.
- Do not write unqualified "first-ever," "world first," or "first public
  proof." At most write "no earlier public proof was identified in the
  recorded searches" or "to the author's knowledge," with the cutoff date.
- Do not write unqualified "\(n=21\) is now the smallest open case." Prefer
  "the least order not covered by the cited results is 21."
- Do not call internal separately implemented verifiers "independent
  verification" without the modifier "internal"; there is no external
  institutional replication.
- Do not call the work proof-assistant formalized, formally verified,
  peer-reviewed or externally validated.
- Do not say that all graphs on 16 or 20 vertices were enumerated. The
  computations enumerate all necessary degree/triangle candidates and map
  every hypothetical target graph into that exhaustion.
- Do not claim that order 20 is mathematically stronger merely because 20 is
  larger. Its importance is that it is the next order not covered by the cited
  general classes and that it supplies a second, substantially larger exact
  certificate exhaustion.

## 5. AI-assistance wording

The title need not mention AI. The manuscript should state, outside the title,
that it is an AI-assisted, non-peer-reviewed preprint presenting two exact
computer-assisted proofs. It should continue to identify the AI systems'
substantial contributions to planning, drafting, code, tests and adversarial
review; deny AI authorship; and assign responsibility to the named human
author. A DOI records identity and preservation and must not be described as
peer review or mathematical endorsement.
