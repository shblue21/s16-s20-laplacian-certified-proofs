# Publication status

Last updated: 24 August 2026.

## Claim and release identity

- Working title: *Nonexistence of Simple Graphs with Laplacian Spectrum
  {0,1,...,n-1} for n=16 and 20: Exact Computer-Assisted Proofs*.
- Version: `0.1.0`.
- Author: Jihun Kim, Independent Researcher.
- Publication type: open, AI-assisted, non-peer-reviewed preprint.
- DOI: pending; none is asserted in the current metadata.
- Repository URL: `https://github.com/shblue21/s16-s20-laplacian-certified-proofs`.
  The repository remains private until coordinated release.
- ORCID: not supplied and therefore omitted.

## Mathematical artifact status

- Order 16: the frozen archive has SHA-256
  `f7f127da4fd6227bd66eadfc22847da270caf2d29b8bedbc16aabee548c8c847`.
  A fresh local replay produced `VERIFIED_UNSAT` and
  `SEMANTIC_AUDIT_PASSED`, followed by a passing internal manifest check.
- Order 20: the frozen archive has SHA-256
  `1eeda59a36dc835ec0efd3dc741d985145054af0d72e77f59e84f9cb63461206`.
  A fresh local native replay produced `VERIFIED_UNSAT` with 80,124 exact
  leaves, zero uncovered cases and passing enumeration, graph-identity,
  mutation and manifest audits in both normal and optimized Python modes.
- These are two logically separate finite-order results. They do not prove the
  `S_n,n` conjecture for every graph order.

The replays above were internal runs on one macOS ARM64 system with system
Python 3.9.6. They are not external institutional or different-language
replications. The frozen artifacts record Linux x86_64 generation/verification
environments, but additional independent clean-room replay remains desirable.

## Publication preparation

- Combined Markdown, three complete computational appendices, standalone
  LaTeX and rendered PDF: prepared.
- Zenodo metadata, citation metadata, file-specific license notices, build
  instructions, mixed-license UI instructions and AI disclosure: prepared
  locally.
- Both frozen archives and detached sidecars: included.
- Hardened order-20 wrapper, current helper programs, expected canonical JSON
  and two fresh exit-0 replay transcripts: included.
- Canonical combined replay command: `./verification/REPRODUCE_BOTH.sh`.
- Latest combined replay: exit 0 with `N16_CANONICAL_BYTE_MATCH`,
  `N20_CANONICAL_BYTE_MATCH` and
  `COMBINED_REPRODUCTION_PASS orders=16,20`.
- External human mathematical peer review: absent.
- External independent replication: absent.
- Different-language verifier: absent.
- Proof-assistant formalization: absent.

The final top-level manifest covers the complete prepared upload. Publication
must still use these exact files and must remain on hold if a final pre-upload
execution of `./verification/REPRODUCE_BOTH.sh` does not emit
`COMBINED_REPRODUCTION_PASS orders=16,20`.
