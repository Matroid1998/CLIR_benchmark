#!/usr/bin/env python3
"""Cross-annotator analysis: human vs two blind LLM annotators on the same 30 docs x 6 models.

Inputs (all under reports/qa_generation_model_comparison/):
  human  : all-questions-by-model-review-annotations-2026-08-18.json + model_slot_mapping.json
  claude : llm_annotation/results_claude/<doc>.json + <private>/pass_claude_slot_mapping.json
  gpt    : llm_annotation/results_gpt/<doc>.json    + <private>/pass_gpt_slot_mapping.json
Each LLM pass saw its own fresh slot randomisation, so slots are resolved per annotator.
Outputs go to llm_annotation/analysis/.
"""
import argparse, csv, json, itertools
from collections import defaultdict
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = HERE / "analysis"; OUT.mkdir(exist_ok=True)

ap = argparse.ArgumentParser()
ap.add_argument("--private-dir", default=str(HERE))
args = ap.parse_args()
PRIV = Path(args.private_dir)

FAITH = ["faith_grounding", "faith_precision", "faith_numerical_fidelity"]
TECH = ["qual_search_bar_realism", "qual_specificity", "qual_phrasing_economy", "qual_focus"]
SEM = ["qual_search_realism", "qual_lexical_distance", "qual_conceptual_framing", "qual_retrievability"]
CRITERIA = FAITH + TECH + SEM + ["linguistic"]
HSLOTS = ["q1", "q2", "q3", "q4", "q5", "q6"]
ANN = ["human", "claude", "gpt"]
ANN_LABEL = {"human": "Human (amirreza)", "claude": "Claude Fable 5", "gpt": "GPT-5.6 Sol"}
MODEL_LABEL = {"gpt-5.4-mini": "GPT-5.4-mini", "gpt-5-mini": "GPT-5-mini", "gemini-3.5-flash": "Gemini 3.5 Flash",
               "qwen3.6-35b-a3b": "Qwen3.6-35B-A3B", "grok-4.3": "Grok 4.3", "sonnet-4.6": "Sonnet 4.6"}

# ------------------------------------------------------------------ palette (dataviz reference, validated) ---
SURFACE, INK, INK2, MUTED, GRID, BASELINE = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"
SERIES = {"human": "#2a78d6", "claude": "#eb6834", "gpt": "#1baf7a"}   # categorical slots 1-3 (all-pairs safe)
SEQ_RAMP = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]
CMAP = LinearSegmentedColormap.from_list("seqblue", SEQ_RAMP)
LIKERT = {1: "#c93a39", 2: "#ec9791", 3: "#f0efec", 4: "#86b6ef", 5: "#2a78d6"}
plt.rcParams.update({"font.family": "DejaVu Sans", "figure.facecolor": SURFACE, "axes.facecolor": SURFACE,
                     "savefig.facecolor": SURFACE, "axes.edgecolor": BASELINE, "axes.linewidth": 0.8,
                     "xtick.color": MUTED, "ytick.color": INK2, "text.color": INK, "svg.fonttype": "none"})
FOOTER = "30 chemistry patent documents × 6 generators = 180 questions; same rubric for all three annotators; slot order re-randomised per annotator"


# ------------------------------------------------------------------------------------------------- loading ---
def finish(row):
    qv = row["qual_vals"]
    row["faith_mean"] = float(np.mean(row["faith_vals"]))
    row["quality_mean"] = float(np.mean(list(qv.values())))
    row["composite"] = (row["faith_mean"] + row["quality_mean"] + row["linguistic"]) / 3
    return row


def load_human():
    ann = json.load(open(ROOT / "all-questions-by-model-review-annotations-2026-08-18.json"))
    mp = json.load(open(ROOT / "model_slot_mapping.json"))
    rows, notes, qa = [], {}, {}
    for rec in ann["records"]:
        eid, meta = rec["external_id"], rec["metadata"]
        slots = mp["records"][eid]["slots"]
        resp = {r["question_name"]: r["value"] for r in rec["responses"]}
        if resp.get("shared_notes"):
            notes[eid] = resp["shared_notes"]
        for i, slot in enumerate(HSLOTS, 1):
            tech = {c: resp[f"{slot}_{c}"] for c in TECH if f"{slot}_{c}" in resp}
            sem = {c: resp[f"{slot}_{c}"] for c in SEM if f"{slot}_{c}" in resp}
            rubric = "technical" if len(tech) == 4 else "semantic"
            qa[(eid, slots[slot])] = (rec["fields"][f"question_{i}"], rec["fields"][f"answer_{i}"])
            rows.append(finish({"annotator": "human", "doc_id": eid, "slot": slot.upper(), "model": slots[slot], "mode": meta["mode"],
                                "lang": meta["question_language"], "rubric": rubric, "rubric_switched": int(rubric != meta["mode"]),
                                "accept": resp[f"{slot}_accept"] == "yes", "linguistic": resp[f"{slot}_qual_linguistic_quality"],
                                "faith_vals": [resp[f"{slot}_{c}"] for c in FAITH], "qual_vals": tech if rubric == "technical" else sem,
                                "reason": ""}))
    return rows, notes, qa


def load_llm(name):
    mp = json.load(open(PRIV / f"pass_{name}_slot_mapping.json"))
    meta = {r["doc_id"]: r for r in json.load(open(HERE / f"pass_{name}_records.json"))}
    rows, notes, usage, models_seen = [], {}, defaultdict(int), set()
    for path in sorted((HERE / f"results_{name}").glob("*.json")):
        res = json.load(open(path)); eid = res["doc_id"]; m = meta[eid]
        slots = mp["records"][eid]["slots"]; assert mp["records"][eid]["mode"] == m["mode"]
        models_seen.add(res.get("model"))
        for k, v in (res.get("usage") or {}).items():
            if isinstance(v, (int, float)): usage[k] += v
        if res["output"]["shared_notes"].strip():
            notes[eid] = res["output"]["shared_notes"].strip()
        keys = TECH if m["mode"] == "technical" else SEM
        for r in res["output"]["ratings"]:
            slot = r["slot"].lower()
            rows.append(finish({"annotator": name, "doc_id": eid, "slot": r["slot"], "model": slots[slot], "mode": m["mode"],
                                "lang": m["question_language"], "rubric": m["mode"], "rubric_switched": 0,
                                "accept": r["accept"] == "yes", "linguistic": r["linguistic_quality"],
                                "faith_vals": [r[c] for c in FAITH], "qual_vals": {c: r[c] for c in keys}, "reason": r["reason"]}))
    return rows, notes, dict(usage), models_seen


H_ROWS, H_NOTES, QA = load_human()
C_ROWS, C_NOTES, C_USAGE, C_MODELS = load_llm("claude")
G_ROWS, G_NOTES, G_USAGE, G_MODELS = load_llm("gpt")
ROWS = H_ROWS + C_ROWS + G_ROWS
NOTES = {"human": H_NOTES, "claude": C_NOTES, "gpt": G_NOTES}
BY = {(r["annotator"], r["doc_id"], r["model"]): r for r in ROWS}
DOCS = sorted({r["doc_id"] for r in H_ROWS})
MODELS_ALL = sorted({r["model"] for r in H_ROWS})
present = {a: sorted({r["doc_id"] for r in ROWS if r["annotator"] == a}) for a in ANN}
print({a: len(v) for a, v in present.items()}, "docs per annotator; claude models:", C_MODELS, "gpt models:", G_MODELS)
COMMON = [d for d in DOCS if all(d in present[a] for a in ANN)]
print(len(COMMON), "docs annotated by all three")


def sel(annotator=None, model=None, **kw):
    out = ROWS
    if annotator: out = [r for r in out if r["annotator"] == annotator]
    if model: out = [r for r in out if r["model"] == model]
    for k, v in kw.items(): out = [r for r in out if r[k] == v]
    return out


def mean(xs): return float(np.mean(xs)) if len(xs) else float("nan")
def pct(xs): return 100 * mean([bool(x) for x in xs])


# ------------------------------------------------------------------------------------------------- stats -----
def rankdata(x):
    x = np.asarray(x, float); n = len(x); order = np.argsort(x, kind="mergesort"); ranks = np.empty(n)
    i = 0
    while i < n:
        j = i
        while j + 1 < n and x[order[j + 1]] == x[order[i]]: j += 1
        ranks[order[i:j + 1]] = (i + j) / 2 + 1; i = j + 1
    return ranks


def spearman(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    if len(a) < 3 or np.std(a) == 0 or np.std(b) == 0: return float("nan")
    return float(np.corrcoef(rankdata(a), rankdata(b))[0, 1])


def pearson(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    if len(a) < 3 or np.std(a) == 0 or np.std(b) == 0: return float("nan")
    return float(np.corrcoef(a, b)[0, 1])


def cohen_kappa(a, b):
    a, b = np.asarray(a, bool), np.asarray(b, bool)
    po = np.mean(a == b); pe = np.mean(a) * np.mean(b) + (1 - np.mean(a)) * (1 - np.mean(b))
    return float((po - pe) / (1 - pe)) if pe < 1 else float("nan")


def fleiss_kappa(matrix):
    """matrix: items x raters of booleans."""
    m = np.asarray(matrix, bool); n_r = m.shape[1]
    yes = m.sum(1); no = n_r - yes
    p_i = (yes * (yes - 1) + no * (no - 1)) / (n_r * (n_r - 1))
    p_bar = p_i.mean(); pj = np.array([yes.sum(), no.sum()]) / (m.size); pe = (pj ** 2).sum()
    return float((p_bar - pe) / (1 - pe)) if pe < 1 else float("nan")


def bootstrap_ci(vals, fn=np.mean, n=4000, seed=0):
    rng = np.random.default_rng(seed); vals = np.asarray(vals, float)
    if len(vals) == 0: return (float("nan"), float("nan"))
    bs = [fn(rng.choice(vals, len(vals))) for _ in range(n)]
    return (float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5)))


def rank_in_doc(annotator):
    """mean within-document rank of each model by composite (1 = best), averaged over docs."""
    out = defaultdict(list)
    for d in present[annotator]:
        rs = [BY[(annotator, d, m)] for m in MODELS_ALL]
        ranks = rankdata([-r["composite"] for r in rs])
        for m, rk in zip(MODELS_ALL, ranks): out[m].append(rk)
    return {m: mean(v) for m, v in out.items()}


# ------------------------------------------------------------------------------------------------ tables -----
def per_model_table():
    rows = []
    for a in ANN:
        rk = rank_in_doc(a)
        for m in MODELS_ALL:
            rs = sel(a, m)
            if not rs: continue
            keep = [r["accept"] for r in rs]
            lo, hi = bootstrap_ci(keep)
            rows.append({"annotator": a, "model": m, "n": len(rs), "keep_rate": mean(keep), "keep_ci_lo": lo, "keep_ci_hi": hi,
                         "keep_rate_technical": mean([r["accept"] for r in rs if r["mode"] == "technical"]),
                         "keep_rate_semantic": mean([r["accept"] for r in rs if r["mode"] == "semantic"]),
                         "faith_mean": mean([r["faith_mean"] for r in rs]), "quality_mean": mean([r["quality_mean"] for r in rs]),
                         "linguistic_mean": mean([r["linguistic"] for r in rs]), "composite_mean": mean([r["composite"] for r in rs]),
                         "composite_median": float(np.median([r["composite"] for r in rs])), "mean_rank_in_doc": rk[m]})
    with open(OUT / "per_model_by_annotator.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); [w.writerow({k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items()}) for r in rows]
    return rows


def annotator_table():
    rows = []
    for a in ANN:
        rs = sel(a)
        allv = [v for r in rs for v in r["faith_vals"] + list(r["qual_vals"].values()) + [r["linguistic"]]]
        rows.append({"annotator": a, "n_docs": len(present[a]), "n_questions": len(rs), "keep_rate": mean([r["accept"] for r in rs]),
                     "keep_rate_technical": mean([r["accept"] for r in rs if r["mode"] == "technical"]),
                     "keep_rate_semantic": mean([r["accept"] for r in rs if r["mode"] == "semantic"]),
                     "faith_mean": mean([r["faith_mean"] for r in rs]), "quality_mean": mean([r["quality_mean"] for r in rs]),
                     "linguistic_mean": mean([r["linguistic"] for r in rs]), "composite_mean": mean([r["composite"] for r in rs]),
                     "share_of_5s": mean([v == 5 for v in allv]), "share_le_2": mean([v <= 2 for v in allv]),
                     "docs_with_notes": len(NOTES[a]), "rubric_switched": sum(r["rubric_switched"] for r in rs)})
    with open(OUT / "annotator_summary.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); [w.writerow({k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items()}) for r in rows]
    return rows


def criteria_table():
    rows = []
    for a in ANN:
        for m in MODELS_ALL:
            rs = sel(a, m)
            row = {"annotator": a, "model": m}
            for i, c in enumerate(FAITH): row[c] = mean([r["faith_vals"][i] for r in rs])
            for c in TECH + SEM: row[c] = mean([r["qual_vals"][c] for r in rs if c in r["qual_vals"]])
            row["linguistic"] = mean([r["linguistic"] for r in rs])
            rows.append(row)
    with open(OUT / "criteria_by_model_annotator.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); [w.writerow({k: (round(v, 3) if isinstance(v, float) else v) for k, v in r.items()}) for r in rows]
    return rows


def agreement():
    out = {"pairs": {}, "three_way": {}}
    keys = [(d, m) for d in COMMON for m in MODELS_ALL]
    for a, b in itertools.combinations(ANN, 2):
        ra = [BY[(a, d, m)] for d, m in keys]; rb = [BY[(b, d, m)] for d, m in keys]
        ka = [r["accept"] for r in ra]; kb = [r["accept"] for r in rb]
        pm_a = {m: mean([r["accept"] for r in ra if r["model"] == m]) for m in MODELS_ALL}
        pm_b = {m: mean([r["accept"] for r in rb if r["model"] == m]) for m in MODELS_ALL}
        pc_a = {m: mean([r["composite"] for r in ra if r["model"] == m]) for m in MODELS_ALL}
        pc_b = {m: mean([r["composite"] for r in rb if r["model"] == m]) for m in MODELS_ALL}
        res = {"n": len(keys), "keep_percent_agreement": mean([x == y for x, y in zip(ka, kb)]), "keep_cohen_kappa": cohen_kappa(ka, kb),
               "both_keep": int(sum(x and y for x, y in zip(ka, kb))), "both_discard": int(sum((not x) and (not y) for x, y in zip(ka, kb))),
               f"{a}_keep_{b}_discard": int(sum(x and not y for x, y in zip(ka, kb))), f"{a}_discard_{b}_keep": int(sum((not x) and y for x, y in zip(ka, kb)))}
        for crit in ["faith_mean", "quality_mean", "linguistic", "composite"]:
            xa = [r[crit] for r in ra]; xb = [r[crit] for r in rb]
            res[f"{crit}_spearman"] = spearman(xa, xb); res[f"{crit}_pearson"] = pearson(xa, xb)
            res[f"{crit}_mean_abs_diff"] = mean([abs(x - y) for x, y in zip(xa, xb)])
            res[f"{crit}_mean_diff_{a}_minus_{b}"] = mean([x - y for x, y in zip(xa, xb)])
        # individual criteria (faith criteria + linguistic; quality criteria pooled by rubric-in-common)
        for i, c in enumerate(FAITH):
            res[f"{c}_spearman"] = spearman([r["faith_vals"][i] for r in ra], [r["faith_vals"][i] for r in rb])
        for c in TECH + SEM:
            pairs = [(x["qual_vals"][c], y["qual_vals"][c]) for x, y in zip(ra, rb) if c in x["qual_vals"] and c in y["qual_vals"]]
            res[f"{c}_spearman"] = spearman([p[0] for p in pairs], [p[1] for p in pairs]) if len(pairs) >= 3 else float("nan")
            res[f"{c}_n"] = len(pairs)
        res["per_model_keep_spearman"] = spearman([pm_a[m] for m in MODELS_ALL], [pm_b[m] for m in MODELS_ALL])
        res["per_model_composite_spearman"] = spearman([pc_a[m] for m in MODELS_ALL], [pc_b[m] for m in MODELS_ALL])
        # mode-split kappa
        for mode in ["technical", "semantic"]:
            idx = [i for i, (d, m) in enumerate(keys) if ra[i]["mode"] == mode]
            res[f"keep_kappa_{mode}"] = cohen_kappa([ka[i] for i in idx], [kb[i] for i in idx])
            res[f"keep_agreement_{mode}"] = mean([ka[i] == kb[i] for i in idx])
        out["pairs"][f"{a}__{b}"] = res
    mat = [[BY[(a, d, m)]["accept"] for a in ANN] for d, m in keys]
    votes = np.asarray(mat, int).sum(1)
    out["three_way"] = {"n": len(keys), "keep_fleiss_kappa": fleiss_kappa(mat), "unanimous_keep": int((votes == 3).sum()),
                        "unanimous_discard": int((votes == 0).sum()), "split_2_1": int(((votes == 2) | (votes == 1)).sum()),
                        "majority_keep_rate": float((votes >= 2).mean())}
    # per-model majority / unanimous keep
    out["per_model_consensus"] = {}
    for m in MODELS_ALL:
        v = np.array([sum(BY[(a, d, m)]["accept"] for a in ANN) for d in COMMON])
        out["per_model_consensus"][m] = {"majority_keep": float((v >= 2).mean()), "unanimous_keep": float((v == 3).mean()),
                                         "any_discard": float((v < 3).mean()), "llm_both_keep": float(np.mean([BY[("claude", d, m)]["accept"] and BY[("gpt", d, m)]["accept"] for d in COMMON]))}
    json.dump(out, open(OUT / "agreement.json", "w"), indent=1)
    with open(OUT / "agreement_pairs.csv", "w", newline="") as f:
        ks = sorted({k for v in out["pairs"].values() for k in v})
        w = csv.writer(f); w.writerow(["pair"] + ks)
        for p, v in out["pairs"].items(): w.writerow([p] + [round(v.get(k, float("nan")), 4) if isinstance(v.get(k), float) else v.get(k, "") for k in ks])
    return out


def per_question_table():
    rows = []
    for d in DOCS:
        for m in MODELS_ALL:
            q, a = QA[(d, m)]
            row = {"doc_id": d, "model": m, "mode": BY[("human", d, m)]["mode"], "lang": BY[("human", d, m)]["lang"], "question": q, "answer": a}
            for an in ANN:
                r = BY.get((an, d, m))
                row[f"{an}_slot"] = r["slot"] if r else ""
                row[f"{an}_keep"] = ("yes" if r["accept"] else "no") if r else ""
                row[f"{an}_faith"] = round(r["faith_mean"], 2) if r else ""
                row[f"{an}_quality"] = round(r["quality_mean"], 2) if r else ""
                row[f"{an}_linguistic"] = r["linguistic"] if r else ""
                row[f"{an}_composite"] = round(r["composite"], 2) if r else ""
                row[f"{an}_reason"] = r["reason"] if r else ""
            votes = [BY[(an, d, m)]["accept"] for an in ANN if (an, d, m) in BY]
            row["n_keep_votes"] = sum(votes); row["majority_keep"] = "yes" if sum(votes) >= 2 and len(votes) == 3 else ("" if len(votes) < 3 else "no")
            rows.append(row)
    with open(OUT / "per_question_all_annotators.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    return rows


def write_disagreements(pq):
    lines = ["# Keep/discard disagreements between the human and the LLM annotators", "",
             "One entry per question where at least one LLM annotator disagrees with the human keep decision. LLM one-sentence reasons are quoted verbatim.", ""]
    groups = {"human keeps, both LLMs discard": [], "human discards, both LLMs keep": [], "human keeps, one LLM discards": [], "human discards, one LLM keeps": []}
    for r in pq:
        if not all(r[f"{a}_keep"] for a in ANN): continue
        h, c, g = (r[f"{a}_keep"] == "yes" for a in ANN)
        if h and not c and not g: groups["human keeps, both LLMs discard"].append(r)
        elif not h and c and g: groups["human discards, both LLMs keep"].append(r)
        elif h and (c != g): groups["human keeps, one LLM discards"].append(r)
        elif not h and (c != g): groups["human discards, one LLM keeps"].append(r)
    for g, rs in groups.items():
        lines += [f"## {g} ({len(rs)})", ""]
        for r in rs:
            lines += [f"- **{r['doc_id']} · {r['model']}** ({r['mode']}, {r['lang']}): {r['question']}  ", f"  — *{r['answer']}*  ",
                      f"  human: faith {r['human_faith']}, quality {r['human_quality']} · Claude: {r['claude_keep']} (faith {r['claude_faith']}, quality {r['claude_quality']}) — {r['claude_reason']}  ",
                      f"  GPT: {r['gpt_keep']} (faith {r['gpt_faith']}, quality {r['gpt_quality']}) — {r['gpt_reason']}", ""]
    (OUT / "disagreements.md").write_text("\n".join(lines))
    return {g: len(rs) for g, rs in groups.items()}


def write_notes(name):
    mp = json.load(open(PRIV / f"pass_{name}_slot_mapping.json")) if name != "human" else json.load(open(ROOT / "model_slot_mapping.json"))
    lines = [f"# {ANN_LABEL[name]} — document notes and per-question reasons", "",
             f"{len(NOTES[name])} of {len(present[name])} documents carry a shared note. Q1–Q6 refer to the randomised slots this annotator saw; resolved to models below.", ""]
    for d in present[name]:
        rs = sorted(sel(name, doc_id=d), key=lambda r: r["slot"])
        lines += [f"## {d}  ·  {rs[0]['mode']} mode  ·  question language: {rs[0]['lang']}", ""]
        if d in NOTES[name]: lines += [f"> {NOTES[name][d]}", ""]
        for r in rs:
            q, a = QA[(d, r["model"])]
            lines.append(f"- **{r['slot']} · {r['model']}** ({'kept' if r['accept'] else 'DISCARDED'}, faith {r['faith_mean']:.2f}, quality {r['quality_mean']:.2f}, ling {r['linguistic']}): {q}  \n  — *{a}*" + (f"  \n  reason: {r['reason']}" if r["reason"] else ""))
        lines.append("")
    (OUT / f"notes_{name}.md").write_text("\n".join(lines))


def write_long():
    with open(OUT / "scores_long_all_annotators.csv", "w", newline="") as f:
        cols = ["annotator", "doc_id", "slot", "model", "mode", "rubric_used", "rubric_switched", "question_language"] + FAITH + TECH + SEM + ["linguistic", "accept", "faith_mean", "quality_mean", "composite", "reason"]
        w = csv.writer(f); w.writerow(cols)
        for r in ROWS:
            w.writerow([r["annotator"], r["doc_id"], r["slot"], r["model"], r["mode"], r["rubric"], r["rubric_switched"], r["lang"]] + r["faith_vals"] +
                       [r["qual_vals"].get(c, "") for c in TECH + SEM] + [r["linguistic"], "yes" if r["accept"] else "no", round(r["faith_mean"], 4), round(r["quality_mean"], 4), round(r["composite"], 4), r["reason"]])


def position_table():
    rows = []
    for a in ANN:
        for s in ["Q1", "Q2", "Q3", "Q4", "Q5", "Q6"]:
            rs = sel(a, slot=s)
            rows.append({"annotator": a, "slot": s, "n": len(rs), "keep_rate": mean([r["accept"] for r in rs]), "composite_mean": mean([r["composite"] for r in rs])})
    with open(OUT / "keep_by_slot_position.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); [w.writerow({k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items()}) for r in rows]
    return rows


# ------------------------------------------------------------------------------------------------ figures ---
def style(ax, xgrid=True, ygrid=False):
    for side in ["top", "right", "left"]: ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(BASELINE); ax.tick_params(length=0, labelsize=9)
    if xgrid: ax.grid(axis="x", color=GRID, linewidth=0.8, zorder=0)
    if ygrid: ax.grid(axis="y", color=GRID, linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)


def title_block(fig, title, subtitle, top=0.97):
    fig.text(0.06, top, title, fontsize=13.5, fontweight="bold", color=INK, va="top")
    fig.text(0.06, top - 0.055, subtitle, fontsize=9.5, color=INK2, va="top")


def footer(fig, y=0.015): fig.text(0.06, y, FOOTER, fontsize=7.5, color=MUTED, va="bottom")


def legend(ax, loc="lower right"):
    """Annotator legend in one row above the plot area, never over the data."""
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(color=SERIES[a], label=ANN_LABEL[a]) for a in ANN], loc="lower left", bbox_to_anchor=(0, 1.0),
              ncol=3, frameon=False, fontsize=8.5, handlelength=1.2, columnspacing=1.4, borderaxespad=0)


def save(fig, name):
    fig.savefig(OUT / f"{name}.png", dpi=220); fig.savefig(OUT / f"{name}.pdf"); plt.close(fig); print("wrote", name)


ORDER = sorted(MODELS_ALL, key=lambda m: -mean([r["accept"] for r in sel("human", m)]))  # human keep-rate order, reused


def fig_keep_rate():
    fig, ax = plt.subplots(figsize=(8.6, 5.4)); fig.subplots_adjust(left=0.20, right=0.95, top=0.78, bottom=0.13)
    h = 0.25; ys = np.arange(len(ORDER))[::-1]
    for j, a in enumerate(ANN):
        for y, m in zip(ys, ORDER):
            rs = sel(a, m); p = pct([r["accept"] for r in rs]) if rs else 0
            yy = y + (1 - j) * (h + 0.02)
            ax.barh(yy, p, height=h, color=SERIES[a], zorder=3)
            ax.text(p + 1, yy, f"{p:.0f}%", va="center", fontsize=8, color=INK2)
    ax.set_yticks(ys); ax.set_yticklabels([MODEL_LABEL[m] for m in ORDER], fontsize=9.5); ax.set_xlim(0, 108)
    ax.set_xticks([0, 25, 50, 75, 100]); ax.set_xticklabels(["0%", "25%", "50%", "75%", "100%"]); style(ax); legend(ax)
    title_block(fig, "Keep rate by generator and annotator", "Share of each generator's 30 questions the annotator would keep in the benchmark (models in human keep-rate order)")
    footer(fig); save(fig, "fig1_keep_rate_by_annotator")


def fig_keep_by_mode():
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 5.3), sharey=True); fig.subplots_adjust(left=0.17, right=0.97, top=0.76, bottom=0.14, wspace=0.12)
    h = 0.25; ys = np.arange(len(ORDER))[::-1]
    for ax, mode in zip(axes, ["technical", "semantic"]):
        for j, a in enumerate(ANN):
            for y, m in zip(ys, ORDER):
                rs = sel(a, m, mode=mode); p = pct([r["accept"] for r in rs]) if rs else 0
                yy = y + (1 - j) * (h + 0.02); ax.barh(yy, p, height=h, color=SERIES[a], zorder=3)
                ax.text(p + 1, yy, f"{p:.0f}", va="center", fontsize=7.5, color=INK2)
        n = len({r["doc_id"] for r in sel("human", mode=mode)})
        ax.text(0, 1.085, f"{mode} mode · {n} documents", fontsize=10, color=INK2, transform=ax.transAxes, va="bottom")
        ax.set_xlim(0, 110); ax.set_xticks([0, 50, 100]); ax.set_xticklabels(["0%", "50%", "100%"]); style(ax)
    axes[0].set_yticks(ys); axes[0].set_yticklabels([MODEL_LABEL[m] for m in ORDER], fontsize=9.5); legend(axes[0])
    title_block(fig, "Keep rate by mode", "Technical-mode keyword questions vs semantic-mode conceptual questions, per annotator")
    footer(fig); save(fig, "fig2_keep_by_mode_annotator")


def fig_criteria_heatmap(crit_rows):
    crits = FAITH + ["linguistic"] + TECH + SEM
    labels = {"faith_grounding": "grounding", "faith_precision": "precision", "faith_numerical_fidelity": "numerical fidelity", "linguistic": "linguistic quality",
              "qual_search_bar_realism": "[T] search-bar realism", "qual_specificity": "[T] specificity", "qual_phrasing_economy": "[T] phrasing economy", "qual_focus": "[T] focus",
              "qual_search_realism": "[S] search realism", "qual_lexical_distance": "[S] lexical distance", "qual_conceptual_framing": "[S] conceptual framing", "qual_retrievability": "[S] retrievability"}
    fig, axes = plt.subplots(1, 3, figsize=(12.5, 6.8), sharey=True); fig.subplots_adjust(left=0.16, right=0.985, top=0.82, bottom=0.17, wspace=0.06)
    lut = {(r["annotator"], r["model"]): r for r in crit_rows}
    vmin, vmax = 2.5, 5.0
    for ax, a in zip(axes, ANN):
        mat = np.array([[lut[(a, m)][c] for m in ORDER] for c in crits])
        ax.imshow(mat, cmap=CMAP, vmin=vmin, vmax=vmax, aspect="auto")
        for i in range(len(crits)):
            for j in range(len(ORDER)):
                v = mat[i, j]; ax.text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=7.5, color="white" if v > 4.1 else INK)
        ax.set_xticks(range(len(ORDER))); ax.set_xticklabels([MODEL_LABEL[m] for m in ORDER], fontsize=8, rotation=35, ha="right", rotation_mode="anchor")
        ax.set_title(ANN_LABEL[a], fontsize=10, color=SERIES[a], loc="left", fontweight="bold"); ax.tick_params(length=0)
        for s in ax.spines.values(): s.set_visible(False)
        ax.axhline(3.5, color=SURFACE, linewidth=2); ax.axhline(7.5, color=SURFACE, linewidth=2)
    axes[0].set_yticks(range(len(crits))); axes[0].set_yticklabels([labels[c] for c in crits], fontsize=8.5)
    title_block(fig, "Mean criterion score by generator, per annotator", "1–5 scale; technical criteria over the 16 technical docs, semantic over the 14 semantic docs (human: by rubric actually filled)")
    footer(fig); save(fig, "fig3_criteria_heatmap_by_annotator")


def fig_keep_confusion(agr):
    fig, axes = plt.subplots(1, 3, figsize=(11, 3.9)); fig.subplots_adjust(left=0.07, right=0.98, top=0.74, bottom=0.16, wspace=0.5)
    for ax, (a, b) in zip(axes, itertools.combinations(ANN, 2)):
        v = agr["pairs"][f"{a}__{b}"]
        grid = np.array([[v["both_keep"], v[f"{a}_keep_{b}_discard"]], [v[f"{a}_discard_{b}_keep"], v["both_discard"]]])
        ax.imshow(grid, cmap=CMAP, vmin=0, vmax=grid.max() * 1.15, aspect="equal")
        for i in range(2):
            for j in range(2):
                ax.text(j, i, str(grid[i, j]), ha="center", va="center", fontsize=13, fontweight="bold", color="white" if grid[i, j] > grid.max() * 0.6 else INK)
        ax.set_xticks([0, 1]); ax.set_xticklabels(["keep", "discard"], fontsize=8.5); ax.set_yticks([0, 1]); ax.set_yticklabels(["keep", "discard"], fontsize=8.5)
        ax.set_xlabel(ANN_LABEL[b], fontsize=9, color=SERIES[b]); ax.set_ylabel(ANN_LABEL[a], fontsize=9, color=SERIES[a]); ax.tick_params(length=0)
        for s in ax.spines.values(): s.set_visible(False)
        ax.set_title(f"agreement {100*v['keep_percent_agreement']:.0f}% · κ = {v['keep_cohen_kappa']:.2f}", fontsize=9.5, color=INK2, loc="left")
    title_block(fig, "Keep-decision agreement between annotators", f"Question-level cross-tabulation over the {agr['pairs']['human__claude']['n']} questions scored by all three · Fleiss κ (3-way) = {agr['three_way']['keep_fleiss_kappa']:.2f}", top=0.96)
    footer(fig); save(fig, "fig4_keep_agreement")


def fig_rating_distribution():
    fig, axes = plt.subplots(1, 3, figsize=(11.5, 4.0), sharey=True); fig.subplots_adjust(left=0.12, right=0.97, top=0.72, bottom=0.16, wspace=0.1)
    blocks = [("faithfulness (3 criteria)", lambda r: r["faith_vals"]), ("mode quality (4 criteria)", lambda r: list(r["qual_vals"].values())), ("linguistic quality", lambda r: [r["linguistic"]])]
    for ax, (name, fn) in zip(axes, blocks):
        for j, a in enumerate(ANN):
            vals = [v for r in sel(a) for v in fn(r)]; tot = len(vals); left = 0
            for lv in [1, 2, 3, 4, 5]:
                share = 100 * sum(v == lv for v in vals) / tot
                ax.barh(2 - j, share, left=left, height=0.6, color=LIKERT[lv], edgecolor=SURFACE, linewidth=1.5, zorder=3)
                if share >= 7: ax.text(left + share / 2, 2 - j, f"{share:.0f}", ha="center", va="center", fontsize=7.5, color="white" if lv in (1, 5) else INK)
                left += share
        ax.set_xlim(0, 100); ax.set_xticks([0, 50, 100]); ax.set_xticklabels(["0%", "50%", "100%"]); ax.set_title(name, fontsize=9.5, color=INK2, loc="left"); style(ax, xgrid=False)
    axes[0].set_yticks([2, 1, 0]); axes[0].set_yticklabels([ANN_LABEL[a] for a in ANN], fontsize=9)
    from matplotlib.patches import Patch
    fig.legend(handles=[Patch(color=LIKERT[v], label=str(v)) for v in [1, 2, 3, 4, 5]], title="rating", loc="upper right", bbox_to_anchor=(0.97, 0.985), ncol=5, frameon=False, fontsize=8, title_fontsize=8)
    title_block(fig, "How the annotators use the 1–5 scale", "Share of ratings at each level, pooled over all generators — a leniency / severity profile per annotator", top=0.96)
    footer(fig, y=0.01); save(fig, "fig5_rating_distribution_by_annotator")


def fig_position(pos_rows):
    fig, ax = plt.subplots(figsize=(8, 4.2)); fig.subplots_adjust(left=0.12, right=0.95, top=0.74, bottom=0.15)
    xs = np.arange(6); w = 0.26
    for j, a in enumerate(ANN):
        ks = [100 * r["keep_rate"] for r in pos_rows if r["annotator"] == a]
        ax.bar(xs + (j - 1) * (w + 0.01), ks, width=w, color=SERIES[a], zorder=3)
    ax.set_xticks(xs); ax.set_xticklabels([f"Q{i}" for i in range(1, 7)]); ax.set_ylim(0, 100); ax.set_yticks([0, 25, 50, 75, 100]); ax.set_yticklabels(["0%", "25%", "50%", "75%", "100%"])
    style(ax, xgrid=False, ygrid=True); legend(ax)
    title_block(fig, "Keep rate by displayed slot position", "Each annotator saw a different random slot order; a flat profile means no position bias (30 questions per bar)")
    footer(fig); save(fig, "fig6_keep_by_slot_position")


def fig_model_rank(pm_rows):
    fig, ax = plt.subplots(figsize=(8.6, 4.9)); fig.subplots_adjust(left=0.20, right=0.95, top=0.77, bottom=0.13)
    h = 0.25; ys = np.arange(len(ORDER))[::-1]; lut = {(r["annotator"], r["model"]): r for r in pm_rows}
    for j, a in enumerate(ANN):
        for y, m in zip(ys, ORDER):
            v = lut[(a, m)]["composite_mean"]; yy = y + (1 - j) * (h + 0.02)
            ax.barh(yy, v, height=h, color=SERIES[a], zorder=3); ax.text(v + 0.03, yy, f"{v:.2f}", va="center", fontsize=8, color=INK2)
    ax.set_yticks(ys); ax.set_yticklabels([MODEL_LABEL[m] for m in ORDER], fontsize=9.5); ax.set_xlim(3, 5.2); ax.set_xticks([3, 3.5, 4, 4.5, 5]); style(ax); legend(ax, "lower right")
    title_block(fig, "Composite score by generator and annotator", "mean of (faithfulness mean, mode-quality mean, linguistic quality); axis starts at 3")
    footer(fig); save(fig, "fig7_composite_by_annotator")


# ------------------------------------------------------------------------------------------------- main -----
if __name__ == "__main__":
    write_long()
    pm = per_model_table(); at = annotator_table(); cr = criteria_table(); agr = agreement(); pq = per_question_table()
    dis = write_disagreements(pq); pos = position_table()
    for a in ANN: write_notes(a)
    json.dump({"claude": {"models_seen": sorted(x for x in C_MODELS if x), "usage": C_USAGE}, "gpt": {"models_seen": sorted(x for x in G_MODELS if x), "usage": G_USAGE}}, open(OUT / "llm_usage.json", "w"), indent=1)
    fig_keep_rate(); fig_keep_by_mode(); fig_criteria_heatmap(cr); fig_keep_confusion(agr); fig_rating_distribution(); fig_position(pos); fig_model_rank(pm)
    print("\nANNOTATOR SUMMARY"); [print({k: (round(v, 3) if isinstance(v, float) else v) for k, v in r.items()}) for r in at]
    print("\nPER MODEL (keep / faith / quality / ling / composite / rank)")
    for a in ANN:
        print(a); [print(f"  {r['model']:18s} keep {r['keep_rate']:.3f} (T {r['keep_rate_technical']:.2f} S {r['keep_rate_semantic']:.2f}) faith {r['faith_mean']:.2f} qual {r['quality_mean']:.2f} ling {r['linguistic_mean']:.2f} comp {r['composite_mean']:.2f} rank {r['mean_rank_in_doc']:.2f}") for r in pm if r["annotator"] == a]
    print("\nAGREEMENT"); [print(p, {k: (round(v, 3) if isinstance(v, float) else v) for k, v in d.items() if "spearman" in k or "kappa" in k or "agreement" in k or k == "n"}) for p, d in agr["pairs"].items()]
    print("three-way", agr["three_way"]); print("consensus", {m: {k: round(v, 3) for k, v in d.items()} for m, d in agr["per_model_consensus"].items()})
    print("disagreement groups", dis)
