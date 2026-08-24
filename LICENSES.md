# File-specific licenses

Copyright (c) 2026 Jihun Kim.

This research compendium contains prose, software and exact certificate/result
data. It therefore does not use one license for every file. The following
file-specific licenses apply to material for which Jihun Kim holds the relevant
rights.

## Manuscript and documentation - CC BY 4.0

The following are licensed under Creative Commons Attribution 4.0
International (`CC-BY-4.0`):

- `paper/`, including the Markdown and LaTeX sources;
- the combined preprint PDF under `output/pdf/`;
- root documentation, including `README.md`, `BUILD.md`, `STATUS.md` and
  `AI_DISCLOSURE.md`;
- publication metadata, including `CITATION.cff` and `.zenodo.json`;
- prose documentation inside either frozen proof archive, including README,
  REPORT, audit and environment documents.

See `LICENSE-CC-BY-4.0.txt`.

## Verification software - MIT

Python and shell source files supplied for enumeration, model reconstruction,
certificate verification, replay and testing are licensed under the MIT
License (`MIT`). This includes such files under root verification directories
and under `code/` inside each frozen proof archive, together with the replay and
regeneration shell scripts.

See `LICENSE-MIT.txt`.

## Certificate and result data - CC0 1.0

Factual and machine-generated proof data are dedicated to the public domain
under CC0 1.0 Universal (`CC0-1.0`). This includes certificate files,
enumerated candidate data, coverage ledgers, canonical JSON outputs, replay
logs, checksum manifests and machine-readable result summaries, whether
distributed directly or inside either frozen proof archive.

See `LICENSE-CC0-1.0.txt`.

## Archive containers and boundaries

The two frozen archive files are byte-preserving containers whose contents
fall under the file-specific rules above; the containers themselves are not
assigned a conflicting single license. The license notices do not change the
frozen archive bytes or their SHA-256 identities.

No license is granted for third-party works merely cited by the manuscript.
Third-party dependencies retain their own licenses. Trademarks and other rights
not held by the author are unaffected. If a file contains an explicit
third-party notice, that notice takes precedence for the covered material.
