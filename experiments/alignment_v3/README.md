# Right to Intervene V3

**Which LLM solutions should a human review first?**

Imagine an assistant submits a derivation that ends with the expected answer. A final-answer check lets it through, even if a step is wrong. V3 studies where to spend scarce human review by replaying a release queue on archived LLM solutions with human step-level annotations. It extends Right to Intervene's work on allocating oversight to generated reasoning.

At a 20% review budget, the process verifier surfaced **403 of 1,643** human-flagged solutions, compared with **381** for answer agreement. This improvement fell short of the study's practical target. Among flagged solutions whose answer text matched the key, the verifier surfaced **30 of 80**, compared with **9** for agreement. The larger gain in that group persisted when we changed the answer formatting rules and checked the underlying step ratings.

[How the test works](docs/MECHANISM.md) · [Methods](docs/METHODS.md) · [Results](docs/RESULTS.md) · [Accuracy checks](docs/AUDIT.md)

## Reproduce the study

Use Python 3.12, Git, and Git LFS. The metrics runner uses only the Python standard library. From `experiments/alignment_v3`, fetch the pinned input from OpenAI's PRM800K repository. The runner verifies the dataset's SHA-256 against the pinned Git LFS object.

```bash
(
  set -eu
  mkdir -p results-local
  source_dir=$(mktemp -d)
  trap 'rm -rf -- "$source_dir"' EXIT
  revision=7ecc794703b2877f63226f2477a49b34f9b25163
  remote=https://github.com/openai/prm800k.git
  data=prm800k/data/phase2_test.jsonl

  git init -q "$source_dir"
  git -C "$source_dir" fetch -q --depth 1 "$remote" "$revision"
  GIT_LFS_SKIP_SMUDGE=1 git -C "$source_dir" checkout -q --detach FETCH_HEAD
  git -C "$source_dir" lfs install --local
  git -C "$source_dir" lfs fetch --include="$data" "$remote" "$revision"
  git -C "$source_dir" lfs checkout "$data"
  cp "$source_dir/$data" results-local/phase2_test.jsonl
)
```

```bash
python3.12 -m unittest discover -s tests -v
python3.12 experiment.py --input results-local/phase2_test.jsonl \
  --split pilot --out results-local/pilot
python3.12 experiment.py --input results-local/phase2_test.jsonl \
  --split evaluation --out results-local/evaluation
```

Use `--plot` with Matplotlib installed to also generate the recall figure. The repository-root virtual environment from V2 already provides Matplotlib. The evaluation pass takes a few seconds on a CPU and uses archived outputs and scores.

The accuracy checks use the same input and Python's standard library:

```bash
python3.12 audit.py --input results-local/phase2_test.jsonl --out results-local/audit.json

curl -fsS https://raw.githubusercontent.com/openai/prm800k/7ecc794703b2877f63226f2477a49b34f9b25163/prm800k/grading/math_normalize.py \
  -o results-local/math_normalize.py
python3.12 robustness.py --input results-local/phase2_test.jsonl \
  --normalizer results-local/math_normalize.py --out results-local/robustness.json
```

The normalization script verifies the upstream source against a pinned SHA-256 before loading it.

## Data files

| File | Contents |
| --- | --- |
| [Candidate table](results/candidates.csv) · [Download CSV](results/candidates.csv?raw=1) | One row per unique model solution, with source line numbers, annotation status, answer-match flag, verifier score, answer agreement, and queue ranks. |
| [`results/summary.csv`](results/summary.csv) | Held-out counts and metrics by policy and budget. The runner writes a fresh copy alongside the candidate data. |
| [`results/manifest.json`](results/manifest.json) | Dataset and runner hashes, evaluation-partition counts, score and label accounting, and paired bootstrap intervals. |
| [`results/review_recall.png`](results/review_recall.png) | Recall curves for all flagged candidates and for flagged candidates that match the answer key. |
| [`results/audit.json`](results/audit.json) | Tie-break distributions, label checks, and bounds for unresolved labels. |
| [`results/robustness.json`](results/robustness.json) | Metrics and paired intervals under different answer string normalization rules. |

The published candidate table contains derived fields and source row numbers. The download and reproduction steps use the pinned PRM800K source archive. Source attribution and the study's scope are in the methods. [PRM800K archive and license](https://github.com/openai/prm800k/tree/7ecc794703b2877f63226f2477a49b34f9b25163)
