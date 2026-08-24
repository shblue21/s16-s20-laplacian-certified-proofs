# Zenodo upload instructions

These settings preserve the mixed-license boundary of the combined preprint
and its executable proof artifacts.

## Record settings

- Resource type: Publication / Preprint
- Access: Open
- Version: 0.1.0
- Record-level license: Creative Commons Attribution 4.0 International
- Metadata source: `.zenodo.json`
- Related repository: `https://github.com/shblue21/s16-s20-laplacian-certified-proofs`

The record-level CC BY 4.0 selection describes the manuscript, PDF and
documentation. It does not override the file-specific licenses inside the
release archive:

- verification software and replay scripts: MIT;
- certificates, ledgers, machine-readable results, manifests and logs: CC0
  1.0;
- manuscript and documentation: CC BY 4.0.

Paste or retain the following statement in Zenodo's additional-description or
notes field:

> The record-level CC BY 4.0 license applies to the manuscript and
> documentation. Verification software is MIT licensed, and certificate and
> machine-result data are released under CC0 1.0. See LICENSES.md in the
> archived release for the authoritative file-by-file scope.

## Files to upload

Upload only the prepared combined PDF, the allowlisted release tar.gz and its
checksum file from the local upload-preparation directory:

```text
S16_S20_EXACT_COMPUTER_ASSISTED_PROOFS_v0.1.0.pdf
S16_S20_LAPLACIAN_EXACT_PROOFS_0.1.0.tar.gz
S16_S20_UPLOAD_SHA256SUMS.txt
```

Do not upload the superseded order-20-only draft archive or working `tmp/`
directories.

## Pre-publish checks

1. Verify `S16_S20_UPLOAD_SHA256SUMS.txt` from the upload directory.
2. Extract the tar.gz into a new directory and verify its `MANIFEST.sha256`.
3. Run `./verification/REPRODUCE_BOTH.sh` from the extracted release and
   require `COMBINED_REPRODUCTION_PASS orders=16,20`.
4. Confirm that the UI still says Preprint, Open and CC BY 4.0, and that the
   mixed-license statement above is visible before pressing Publish.

The DOI is intentionally absent from the current PDF. If a DOI is reserved and
inserted into the PDF before publication, regenerate the LaTeX, PDF, manifest,
upload tar and checksum file, then repeat all checks above.
