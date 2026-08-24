#!/bin/bash
set -euo pipefail

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)
root_dir=$(CDPATH= cd -- "$script_dir/.." && pwd -P)
output="$root_dir/MANIFEST.sha256"
temporary="$root_dir/tmp/MANIFEST.sha256.new"

files=(
  .gitattributes
  .gitignore
  .zenodo.json
  AI_DISCLOSURE.md
  ARTIFACT_PROVENANCE.md
  BUILD.md
  CITATION.cff
  LICENSE-CC-BY-4.0.txt
  LICENSE-CC0-1.0.txt
  LICENSE-MIT.txt
  LICENSES.md
  LITERATURE_SEARCH.md
  README.md
  RELEASE_NOTES.md
  STATUS.md
  ZENODO_UPLOAD_INSTRUCTIONS.md
  artifacts/S20_CERTIFIED_EXHAUSTION_RELEASE_20260821.tar.gz
  artifacts/S20_CERTIFIED_EXHAUSTION_RELEASE_20260821.tar.gz.sha256
  artifacts/snn16-certified-nonexistence-20260821.zip
  artifacts/snn16-certified-nonexistence-20260821.zip.sha256
  logs/combined-current.log
  logs/n16-current.log
  logs/n20-current-run1.log
  logs/n20-current-run2.log
  output/pdf/S16_S20_EXACT_COMPUTER_ASSISTED_PROOFS_v0.1.0.pdf
  paper/APPENDIX_ENUMERATION_SPEC.md
  paper/APPENDIX_N16_SPEC.md
  paper/APPENDIX_N20_SPEC.md
  paper/BACK_MATTER.md
  paper/MANUSCRIPT.md
  paper/S16_S20_PREPRINT_v0.1.0.tex
  paper/latex-header.tex
  results/ORDER16_RESULT_FINAL.json
  results/ORDER16_RESULT_FINAL.json.sha256
  results/S20_CANONICAL_RESULT_FINAL.json
  results/S20_CANONICAL_RESULT_FINAL.json.sha256
  results/reproduced-n20-run1.json
  results/reproduced-n20-run2.json
  verification/REPRODUCE_BOTH.sh
  verification/n20/REPRODUCE_INDEPENDENT.sh
  verification/n20/audit_cycle_identity_v2.py
  verification/n20/verify_certificates_v2.py
  verification/n20/verify_enumeration_v2.py
  verification/sha256sum
  verification/update_manifest.sh
)

mkdir -p "$root_dir/tmp"
: >"$temporary"
for relative in "${files[@]}"; do
  [[ -f "$root_dir/$relative" && ! -L "$root_dir/$relative" ]] || {
    echo "missing or unsafe manifest input: $relative" >&2
    exit 1
  }
  (
    cd "$root_dir"
    shasum -a 256 "./$relative"
  ) >>"$temporary"
done
mv "$temporary" "$output"
echo "WROTE_MANIFEST entries=${#files[@]} path=$output"
