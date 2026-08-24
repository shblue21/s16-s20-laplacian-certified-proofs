# Nonexistence of Simple Graphs with Laplacian Spectrum {0,1,...,n-1} for n=16 and 20: Exact Computer-Assisted Proofs

This release contains exact computer-assisted proofs for the order-16 and
order-20 cases, together with their separate certificate archives, hashes and
reproduction paths. The two finite-order results do not settle the conjecture
in general and have not undergone external peer review.

## Reproduce both results

Run from the repository root:

```bash
./verification/REPRODUCE_BOTH.sh
```

The command verifies the complete release manifest, extracts and replays the
order-16 archive in normal and optimized Python modes, requires its normalized
summary to match the frozen expected bytes, performs the hardened offline
order-20 replay, and requires the reproduced order-20 canonical JSON to match
the frozen expected bytes.
The final marker is:

```text
COMBINED_REPRODUCTION_PASS orders=16,20
```

## Main files

- paper/MANUSCRIPT.md - combined manuscript source;
- paper/APPENDIX_ENUMERATION_SPEC.md - exact enumeration and coverage;
- paper/APPENDIX_N16_SPEC.md - complete order-16 model specification;
- paper/APPENDIX_N20_SPEC.md - complete order-20 model specification;
- paper/BACK_MATTER.md - availability, disclosures and references;
- paper/S16_S20_PREPRINT_v0.1.0.tex - generated standalone LaTeX;
- output/pdf/S16_S20_EXACT_COMPUTER_ASSISTED_PROOFS_v0.1.0.pdf - rendered
  combined preprint;
- artifacts/ - both frozen exact-certificate archives and sidecars;
- verification/ - combined replay entry point and hardened order-20 helpers;
- results/ - frozen and reproduced canonical machine-readable results;
- logs/ - complete publication-candidate replay transcripts.

See BUILD.md for the exact Pandoc/XeLaTeX command, LITERATURE_SEARCH.md for the
dated novelty search, LICENSES.md for file-specific rights,
ZENODO_UPLOAD_INSTRUCTIONS.md for the mixed-license upload settings, and
STATUS.md for the release status.
