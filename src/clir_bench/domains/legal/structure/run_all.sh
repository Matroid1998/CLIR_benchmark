#!/usr/bin/env bash
# Full-corpus run: fetch -> segment -> extract references -> join -> resolve.
#
# Detached and resumable. Every stage is cache-first and skips work already on
# disk, so re-running after an interruption picks up where it stopped rather
# than starting over. Launch with:
#
#   setsid nohup src/clir_bench/domains/legal/structure/run_all.sh \
#       > data/legal/eurlex/structure/run_all.log 2>&1 &
set -uo pipefail

cd "$(dirname "$0")/../../../../.." || exit 1
PY=.venv/bin/python
M=clir_bench.domains.legal.structure
OUT=data/legal/eurlex/structure

stamp() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }
say()   { echo "[$(stamp)] $*"; }

say "=== stage 1/5: fetch from CELLAR ==="
$PY -m $M.cellar --all --workers 8 --rate 8 || { say "FETCH FAILED"; exit 1; }

say "=== stage 2/5: segment ==="
$PY -m $M.segment --all --workers 12 || { say "SEGMENT FAILED"; exit 1; }

say "=== stage 3/5: extract references (English) ==="
$PY -m $M.references || { say "REFERENCES FAILED"; exit 1; }

say "=== stage 4/5: cross-language join ==="
$PY -m $M.project || { say "PROJECT FAILED"; exit 1; }

say "=== stage 5/5: resolve cross-act references ==="
$PY -m $M.resolve_external || { say "RESOLVE FAILED"; exit 1; }

say "=== done ==="
wc -l "$OUT"/articles.jsonl "$OUT"/internal_edges.jsonl \
      "$OUT"/external_references.jsonl "$OUT"/dropped_references.jsonl \
      "$OUT"/external_edges.jsonl "$OUT"/unresolved_external.jsonl \
      "$OUT"/reference_status.jsonl "$OUT"/quarantine.jsonl 2>/dev/null
du -sh "$OUT"
say "ALL STAGES COMPLETE"
