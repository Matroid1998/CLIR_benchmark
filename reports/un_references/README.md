# UN reference resolution — tracked stats

Produced by `python -m clir_bench.domains.legal.un.references_status`, the
stage that classifies every citation in every target block of the UN corpus
(external document / internal part / unmodelled family), resolves each one
only when the surface pins exactly one target, and persists the verdict.

Artifacts (data side, under `data/legal/un_parallel/blocks/`):

| file | contents |
|---|---|
| `reference_status_en.jsonl` | one row per **citing** target block: counts, reasons, `complete`. A target block absent from the file cites nothing and is complete by definition. |
| `un_citation_edges.jsonl` | every cleanly resolved external citation (block → document, with the anchored paragraph / annex part when the citation named one) |
| `un_unresolved.jsonl` | every citation carrying a reason — blocking and merely-recorded alike |

`un_reference_stats.json` in this directory is the tracked summary: per-kind
found/resolved table, per-reason counts, symbol-map health (collisions,
special-session overlaps), and the gate pools that
`qac/un_batch.select(require_complete=True)` draws from.

Safety rules (the whole point — see `qac/un_references.py` for the measured
justification of each):

- a lettered citation ("resolution 51/153 B") resolves only to the lettered
  symbol, never the plain twin;
- un-pinned special sessions that exist in both the GA and HRC spaces
  (sessions 20, 21) are `ambiguous_candidates`, never guessed;
- internal "paragraph N" anchors only to a unique same-part sibling block, and
  a bare "paragraph N" is anchored only inside resolutions/decisions;
- annex citations resolve against the document's annex inventory
  (`blocks.py` part model), unique match or a named miss;
- treaty articles, rules of procedure and general comments are detected and
  block completeness; agenda items and coarse structural pointers are
  recorded without blocking.

Regeneration order after touching `un/blocks.py`:
`blocks` rebuild → `references_status` → (`--sample 400` for the manual
review file in `data/legal/un_parallel/`).
