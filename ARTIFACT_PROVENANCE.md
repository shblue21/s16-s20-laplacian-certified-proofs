# Artifact provenance and terminology

This release preserves two previously frozen proof archives byte-for-byte.
Release-level documentation controls the interpretation of their historical
status labels.

## Order 16

`snn16-certified-nonexistence-20260821.zip` has SHA-256
`f7f127da4fd6227bd66eadfc22847da270caf2d29b8bedbc16aabee548c8c847`.
Some files inside the frozen ZIP use the phrase `independent verifier`. In this
release that phrase means a separately implemented internal exact verifier. It
does not mean external authorship, institutional independence, a different
language implementation or external replication. The ZIP is not rewritten
because changing prose inside it would destroy its audited identity.

## Order 20

`S20_CERTIFIED_EXHAUSTION_RELEASE_20260821.tar.gz` has SHA-256
`1eeda59a36dc835ec0efd3dc741d985145054af0d72e77f59e84f9cb63461206`.
The publication wrapper pins enumeration helper SHA-256
`4df5db86179076364561689d8a4e62cba67890ded650ecc354f53949492bdbd9`
and emits canonical JSON SHA-256
`ebc3d8065c3f0c2e869e940f2d50c572292c45646a5ee6ac658a3f805b1ccbac`.
Earlier project logs used a pre-publication helper label and therefore produced
a different wrapper-envelope digest. They are not used as the provenance logs
for this combined release. The mathematical archive, certificate counts,
coverage and theorem result did not change.

## Machine labels

Labels containing `INDEPENDENT` are retained for compatibility with the
verification programs. Throughout this release they denote separately
implemented internal checks. No external peer review, external institutional
replication, different-language verification or proof-assistant formalization
is claimed.

## Combined release replay

`logs/combined-current.log` records the current top-level replay. It verifies
the complete manifest, reproduces the order-16 normal and optimized summaries,
matches the frozen order-16 result bytes, performs the hardened offline
order-20 replay, matches the current canonical JSON bytes and terminates with
`COMBINED_REPRODUCTION_PASS orders=16,20`.
