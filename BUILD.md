# Building the combined preprint

Run all commands from the repository root. The publication source is the
ordered set

1. paper/MANUSCRIPT.md,
2. paper/APPENDIX_ENUMERATION_SPEC.md,
3. paper/APPENDIX_N16_SPEC.md,
4. paper/APPENDIX_N20_SPEC.md,
5. paper/BACK_MATTER.md.

The checked-in standalone LaTeX file is generated from those Markdown files;
it is not a separately edited authoritative source.

## Tested toolchain

- Pandoc 3.9
- XeLaTeX / xdvipdfmx from the TeX distribution available on 24 August 2026
- Bash (the replay scripts use Bash arrays, `[[ ... ]]` tests and
  `set -o pipefail`)

Other recent versions may produce a semantically identical PDF whose binary
hash differs because of tool versions, font versions or embedded timestamps.

## Generate the standalone LaTeX source

~~~bash
pandoc \
  paper/MANUSCRIPT.md \
  paper/APPENDIX_ENUMERATION_SPEC.md \
  paper/APPENDIX_N16_SPEC.md \
  paper/APPENDIX_N20_SPEC.md \
  paper/BACK_MATTER.md \
  --from=markdown+tex_math_dollars+tex_math_single_backslash+pipe_tables+fenced_code_blocks \
  --standalone \
  --pdf-engine=xelatex \
  --include-in-header=paper/latex-header.tex \
  --syntax-highlighting=none \
  -V papersize=a4 \
  -V geometry:margin=25mm \
  -V fontsize=11pt \
  -V colorlinks=true \
  -V linkcolor=blue \
  -V urlcolor=blue \
  -o paper/S16_S20_PREPRINT_v0.1.0.tex
~~~

Before publication, regenerate the file above and confirm that it has no
unexpected difference from the checked-in LaTeX source.

## Compile the PDF

Three XeLaTeX passes stabilize the table of contents and cross-references.

~~~bash
mkdir -p tmp/tex-build output/pdf

xelatex -interaction=nonstopmode -halt-on-error \
  -output-directory=tmp/tex-build \
  paper/S16_S20_PREPRINT_v0.1.0.tex
xelatex -interaction=nonstopmode -halt-on-error \
  -output-directory=tmp/tex-build \
  paper/S16_S20_PREPRINT_v0.1.0.tex
xelatex -interaction=nonstopmode -halt-on-error \
  -output-directory=tmp/tex-build \
  paper/S16_S20_PREPRINT_v0.1.0.tex

cp tmp/tex-build/S16_S20_PREPRINT_v0.1.0.pdf \
  output/pdf/S16_S20_EXACT_COMPUTER_ASSISTED_PROOFS_v0.1.0.pdf
~~~

Inspect the final log for unresolved references and layout warnings:

~~~bash
rg 'Warning|Overfull|Underfull|Undefined|Error|Missing' \
  tmp/tex-build/S16_S20_PREPRINT_v0.1.0.log
~~~

Treat errors, unresolved references and overfull boxes as release blockers;
inspect any underfull-box warning at the cited line before deciding whether it
is harmless. A publication build must also render every PDF page to images and
inspect it for clipping, overlap, broken tables and unreadable hashes or
commands.

## Release integrity

Calculate the built file's digest with either of the following equivalent
commands:

~~~bash
shasum -a 256 \
  output/pdf/S16_S20_EXACT_COMPUTER_ASSISTED_PROOFS_v0.1.0.pdf

sha256sum \
  output/pdf/S16_S20_EXACT_COMPUTER_ASSISTED_PROOFS_v0.1.0.pdf
~~~

The final archival upload must carry a top-level checksum manifest generated
after all manuscript, metadata, license and frozen proof-artifact files are in
their final locations. Do not infer that the checked-in manifest is current
after editing or packaging; verify it explicitly before publication.
