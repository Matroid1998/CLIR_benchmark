#!/usr/bin/env python3
"""Plots for the human annotation review of question generation models.

Reads the annotation export and the slot->model mapping from the repo root and
regenerates every figure + summary table in this directory.

Scoring notes:
- Each question has 3 faithfulness criteria, 4 quality criteria (technical or
  semantic block), linguistic quality (all 1-5) and a keep/discard decision.
- On 18/180 questions the annotator filled the opposite mode's quality block
  (all 6 questions of one technical doc; scattered questions in 6 semantic
  docs). Quality is scored from whichever block was actually filled
  (`rubric_used`), and the switch is kept as a flag.
- composite = mean(faith_mean, quality_mean, linguistic), family-balanced.
"""

import json
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.path import Path as MplPath
from matplotlib.patches import PathPatch, Rectangle

ROOT = Path(__file__).resolve().parents[1]  # reports/qa_generation_model_comparison/
OUT = Path(__file__).resolve().parent

# ---------------------------------------------------------------- palette ---
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
BASELINE = "#c3c2b7"
BLUE = "#2a78d6"          # categorical slot 1 / sequential 450
BLUE_LIGHT = "#86b6ef"    # sequential 250 (ordinal-safe light end)
BLUE_150 = "#b7d3f6"
SEQ_RAMP = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]
# diverging Likert scale, arms validated as ordinal ramps (see analysis log)
LIKERT = {1: "#c93a39", 2: "#ec9791", 3: "#f0efec", 4: "#86b6ef", 5: "#2a78d6"}

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "figure.facecolor": SURFACE,
    "axes.facecolor": SURFACE,
    "savefig.facecolor": SURFACE,
    "axes.edgecolor": BASELINE,
    "axes.linewidth": 0.8,
    "xtick.color": MUTED,
    "ytick.color": INK2,
    "text.color": INK,
    "svg.fonttype": "none",
})

CMAP = LinearSegmentedColormap.from_list("seqblue", SEQ_RAMP)

FAITH = ["faith_grounding", "faith_precision", "faith_numerical_fidelity"]
TECH = ["qual_search_bar_realism", "qual_specificity", "qual_phrasing_economy", "qual_focus"]
SEM = ["qual_search_realism", "qual_lexical_distance", "qual_conceptual_framing", "qual_retrievability"]

MODEL_LABEL = {
    "gpt-5.4-mini": "GPT-5.4-mini",
    "gpt-5-mini": "GPT-5-mini",
    "gemini-3.5-flash": "Gemini 3.5 Flash",
    "qwen3.6-35b-a3b": "Qwen3.6-35B-A3B",
    "grok-4.3": "Grok 4.3",
    "sonnet-4.6": "Sonnet 4.6",
}

FOOTER = "Human annotation, single annotator, 30 patent documents × 6 models (180 questions) · export 2026-08-18"


# ------------------------------------------------------------------- data ---
def load_rows():
    with open(ROOT / "all-questions-by-model-review-annotations-2026-08-18.json") as f:
        ann = json.load(f)
    with open(ROOT / "model_slot_mapping.json") as f:
        mp = json.load(f)
    rows = []
    for rec in ann["records"]:
        eid = rec["external_id"]
        meta = rec["metadata"]
        slots = mp["records"][eid]["slots"]
        resp = {r["question_name"]: r["value"] for r in rec["responses"]}
        for slot in ["q1", "q2", "q3", "q4", "q5", "q6"]:
            tech_vals = {c: resp[f"{slot}_{c}"] for c in TECH if f"{slot}_{c}" in resp}
            sem_vals = {c: resp[f"{slot}_{c}"] for c in SEM if f"{slot}_{c}" in resp}
            rubric = "technical" if len(tech_vals) == 4 else "semantic"
            qvals = tech_vals if rubric == "technical" else sem_vals
            row = {
                "doc_id": eid,
                "model": slots[slot],
                "mode": meta["mode"],
                "lang": meta["question_language"],
                "rubric": rubric,
                "accept": resp[f"{slot}_accept"] == "yes",
                "linguistic": resp[f"{slot}_qual_linguistic_quality"],
                "faith_vals": [resp[f"{slot}_{c}"] for c in FAITH],
                "qual_vals": dict(qvals),
            }
            row["faith_mean"] = float(np.mean(row["faith_vals"]))
            row["quality_mean"] = float(np.mean(list(qvals.values())))
            row["composite"] = (row["faith_mean"] + row["quality_mean"] + row["linguistic"]) / 3
            rows.append(row)
    return rows


ROWS = load_rows()
MODELS = sorted(
    {r["model"] for r in ROWS},
    key=lambda m: (
        -np.mean([r["accept"] for r in ROWS if r["model"] == m]),
        -np.mean([r["composite"] for r in ROWS if r["model"] == m]),
    ),
)  # keep-rate order, composite tiebreak — reused by every figure


def sel(model, **kw):
    out = ROWS
    if model is not None:
        out = [r for r in out if r["model"] == model]
    for k, v in kw.items():
        out = [r for r in out if r[k] == v]
    return out


# ------------------------------------------------------------- primitives ---
def rounded_barh(ax, y, width, height, color, xmax):
    """Horizontal bar, square at the baseline, rounded at the data end."""
    ry = height * 0.30
    bbox = ax.get_window_extent()
    yrange = np.diff(ax.get_ylim())[0] or 1
    rx = abs(ry * (xmax / yrange) * (bbox.height / bbox.width))
    rx = min(rx, width * 0.5)
    k = 0.5523
    y0, y1 = y - height / 2, y + height / 2
    verts = [
        (0, y0), (width - rx, y0),
        (width - rx + k * rx, y0), (width, y0 + ry - k * ry), (width, y0 + ry),
        (width, y1 - ry),
        (width, y1 - ry + k * ry), (width - rx + k * rx, y1), (width - rx, y1),
        (0, y1), (0, y0),
    ]
    codes = [MplPath.MOVETO, MplPath.LINETO,
             MplPath.CURVE4, MplPath.CURVE4, MplPath.CURVE4,
             MplPath.LINETO,
             MplPath.CURVE4, MplPath.CURVE4, MplPath.CURVE4,
             MplPath.LINETO, MplPath.CLOSEPOLY]
    ax.add_patch(PathPatch(MplPath(verts, codes), facecolor=color, edgecolor="none", zorder=3))


def style_axes(ax, xgrid=True):
    for side in ["top", "right", "left"]:
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(BASELINE)
    ax.tick_params(length=0, labelsize=9)
    if xgrid:
        ax.grid(axis="x", color=GRID, linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)


def title_block(fig, title, subtitle, top=0.97):
    fig.text(0.06, top, title, fontsize=13.5, fontweight="bold", color=INK, va="top")
    fig.text(0.06, top - 0.062, subtitle, fontsize=9.5, color=INK2, va="top")


def footer(fig, extra=None, y=0.018):
    txt = FOOTER if extra is None else f"{extra}\n{FOOTER}"
    fig.text(0.06, y, txt, fontsize=8, color=MUTED, va="bottom")


def save(fig, name):
    fig.savefig(OUT / f"{name}.png", dpi=220)
    fig.savefig(OUT / f"{name}.pdf")
    plt.close(fig)
    print("wrote", name)


# ---------------------------------------------------------- fig1 keep rate --
def fig_keep_rate():
    fig, ax = plt.subplots(figsize=(8.2, 3.9))
    fig.subplots_adjust(left=0.20, right=0.90, top=0.80, bottom=0.17)
    ys = np.arange(len(MODELS))[::-1]
    ax.set_xlim(0, 100)
    ax.set_ylim(-0.6, len(MODELS) - 0.4)
    overall = 100 * np.mean([r["accept"] for r in ROWS])
    for y, m in zip(ys, MODELS):
        acc = [r["accept"] for r in sel(m)]
        pct = 100 * np.mean(acc)
        rounded_barh(ax, y, pct, 0.52, BLUE, 100)
        ax.text(pct + 1.5, y, f"{pct:.0f}%  ({sum(acc)}/{len(acc)})",
                va="center", fontsize=9.5, color=INK2)
    ax.axvline(overall, color=BASELINE, linewidth=0.8, zorder=1)
    ax.text(overall, len(MODELS) - 0.25, f"overall {overall:.0f}%",
            fontsize=8, color=MUTED, ha="center")
    ax.set_yticks(ys)
    ax.set_yticklabels([MODEL_LABEL[m] for m in MODELS], fontsize=10)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_xticklabels(["0%", "25%", "50%", "75%", "100%"])
    style_axes(ax)
    title_block(fig, "Share of questions the annotator would keep",
                "“Keep this question?” = yes, out of 30 questions per model (one per document)")
    footer(fig)
    save(fig, "fig1_keep_rate")


# ------------------------------------------------- fig2 keep rate by mode ---
def fig_keep_by_mode():
    fig, ax = plt.subplots(figsize=(8.2, 4.4))
    fig.subplots_adjust(left=0.20, right=0.94, top=0.78, bottom=0.16)
    order = sorted(MODELS, key=lambda m: -np.mean([r["accept"] for r in sel(m, mode="semantic")]))
    ys = np.arange(len(order))[::-1]
    ax.set_xlim(40, 102)
    ax.set_ylim(-0.7, len(order) - 0.3)
    for y, m in zip(ys, order):
        t = 100 * np.mean([r["accept"] for r in sel(m, mode="technical")])
        s = 100 * np.mean([r["accept"] for r in sel(m, mode="semantic")])
        ax.plot([s, t], [y, y], color=BLUE_150, linewidth=2, zorder=2, solid_capstyle="round")
        ax.plot(t, y, "o", color=BLUE, markersize=9, markeredgecolor=SURFACE,
                markeredgewidth=1.3, zorder=3)
        ax.plot(s, y, "o", color=BLUE_LIGHT, markersize=9, markeredgecolor=SURFACE,
                markeredgewidth=1.3, zorder=3)
        ax.annotate(f"{t:.0f}%", (t, y), xytext=(0, 8), textcoords="offset points",
                    ha="center", fontsize=8.5, color=INK2)
        ax.annotate(f"{s:.0f}%", (s, y), xytext=(0, -15), textcoords="offset points",
                    ha="center", fontsize=8.5, color=INK2)
    ax.set_yticks(ys)
    ax.set_yticklabels([MODEL_LABEL[m] for m in order], fontsize=10)
    ax.set_xticks([40, 50, 60, 70, 80, 90, 100])
    ax.set_xticklabels([f"{v}%" for v in [40, 50, 60, 70, 80, 90, 100]])
    style_axes(ax)
    ax.legend(handles=[
        plt.Line2D([], [], marker="o", linestyle="", color=BLUE, markersize=8,
                   markeredgecolor=SURFACE, label="technical mode (16 docs)"),
        plt.Line2D([], [], marker="o", linestyle="", color=BLUE_LIGHT, markersize=8,
                   markeredgecolor=SURFACE, label="semantic mode (14 docs)"),
    ], loc="lower left", frameon=False, fontsize=8.5, handletextpad=0.2,
        bbox_to_anchor=(0.0, 1.0), ncol=2, borderaxespad=0)
    title_block(fig, "Keep rate by document mode",
                "Semantic mode is what separates the models · sorted by semantic keep rate")
    footer(fig)
    save(fig, "fig2_keep_rate_by_mode")


# ------------------------------------------------- fig3 criterion heatmap ---
def fig_criteria_heatmap():
    groups = [
        ("Faithfulness", FAITH, None),
        ("Both", ["linguistic"], None),
        ("Technical quality", TECH, "technical"),
        ("Semantic quality", SEM, "semantic"),
    ]
    col_labels, col_defs = [], []
    for gname, crits, rubric in groups:
        for c in crits:
            col_labels.append(c.replace("faith_", "").replace("qual_", "").replace("_", " "))
            col_defs.append((c, rubric))

    def cell(m, c, rubric):
        if c == "linguistic":
            vals = [r["linguistic"] for r in sel(m)]
        elif c in FAITH:
            i = FAITH.index(c)
            vals = [r["faith_vals"][i] for r in sel(m)]
        else:
            vals = [r["qual_vals"][c] for r in sel(m, rubric=rubric) if c in r["qual_vals"]]
        return np.mean(vals), len(vals)

    M = np.zeros((len(MODELS), len(col_defs)))
    N = np.zeros_like(M, dtype=int)
    for i, m in enumerate(MODELS):
        for j, (c, rubric) in enumerate(col_defs):
            M[i, j], N[i, j] = cell(m, c, rubric)

    fig, ax = plt.subplots(figsize=(10.4, 4.6))
    fig.subplots_adjust(left=0.155, right=0.93, top=0.72, bottom=0.075)
    vmin, vmax = 3.8, 5.0
    ax.pcolormesh(M[::-1], cmap=CMAP, vmin=vmin, vmax=vmax,
                  edgecolors=SURFACE, linewidth=2)
    for i in range(len(MODELS)):
        for j in range(len(col_defs)):
            v = M[i, j]
            frac = (v - vmin) / (vmax - vmin)
            ink = "#ffffff" if frac > 0.55 else INK
            ax.text(j + 0.5, len(MODELS) - 1 - i + 0.5, f"{v:.2f}",
                    ha="center", va="center", fontsize=8.6, color=ink)
    ax.set_yticks(np.arange(len(MODELS)) + 0.5)
    ax.set_yticklabels([MODEL_LABEL[m] for m in MODELS[::-1]], fontsize=9.5)
    ax.set_xticks(np.arange(len(col_defs)) + 0.5)
    ax.set_xticklabels(col_labels, fontsize=8, rotation=28, ha="right", color=INK2)
    ax.tick_params(length=0)
    ax.xaxis.set_ticks_position("top")
    ax.xaxis.set_label_position("top")
    plt.setp(ax.get_xticklabels(), rotation=28, ha="left", rotation_mode="anchor")
    for side in ax.spines.values():
        side.set_visible(False)
    # group separators + headers
    xpos = 0
    for gname, crits, rubric in groups:
        w = len(crits)
        ax.text(xpos + w / 2, len(MODELS) + 1.28, gname, ha="center",
                fontsize=9, fontweight="bold", color=INK)
        if xpos > 0:
            ax.axvline(xpos, color=SURFACE, linewidth=6)
        xpos += w
    ax.set_xlim(0, len(col_defs))
    ax.set_ylim(0, len(MODELS))
    title_block(fig, "Mean rating per criterion (1–5)", "", top=0.965)
    footer(fig, extra="Faithfulness & linguistic pools: all 30 questions per model · technical / semantic quality pools: "
                      "questions scored with that rubric (56–64 / 36–56 ratings per cell)", y=0.012)
    save(fig, "fig3_criteria_heatmap")


# --------------------------------------------- fig4 rating distributions ----
def fig_rating_distribution():
    fig, axes = plt.subplots(1, 2, figsize=(10.4, 4.3), sharey=True)
    fig.subplots_adjust(left=0.155, right=0.98, top=0.72, bottom=0.20, wspace=0.08)
    panels = [
        ("Faithfulness ratings", lambda r: r["faith_vals"], "3 criteria × 30 questions = 90 ratings per model"),
        ("Quality ratings", lambda r: list(r["qual_vals"].values()), "4 criteria × 30 questions = 120 ratings per model"),
    ]
    ys = np.arange(len(MODELS))[::-1]
    for ax, (name, get, sub) in zip(axes, panels):
        for y, m in zip(ys, MODELS):
            vals = [v for r in sel(m) for v in get(r)]
            n = len(vals)
            pct = {k: 100 * sum(v == k for v in vals) / n for k in range(1, 6)}
            left = -(pct[1] + pct[2] + pct[3] / 2)
            x = left
            for k in range(1, 6):
                ax.add_patch(Rectangle((x, y - 0.28), pct[k], 0.56, facecolor=LIKERT[k],
                                       edgecolor=SURFACE, linewidth=1.6, zorder=3))
                x += pct[k]
            neg, pos = pct[1] + pct[2], pct[4] + pct[5]
            ax.text(left - 2, y, f"{neg:.0f}%", ha="right", va="center", fontsize=8.3, color=INK2)
            ax.text(x + 2, y, f"{pos:.0f}%", ha="left", va="center", fontsize=8.3, color=INK2)
        ax.axvline(0, color=BASELINE, linewidth=0.8, zorder=2)
        ax.set_xlim(-40, 105)
        ax.set_ylim(-0.6, len(MODELS) - 0.4)
        ax.set_xticks([-25, 0, 25, 50, 75, 100])
        ax.set_xticklabels(["25%", "0", "25%", "50%", "75%", "100%"])
        style_axes(ax, xgrid=False)
        ax.set_title(name, fontsize=10.5, fontweight="bold", color=INK, pad=26)
        ax.text(0.5, 1.10, sub, transform=ax.transAxes, ha="center", fontsize=8, color=MUTED)
    axes[0].set_yticks(ys)
    axes[0].set_yticklabels([MODEL_LABEL[m] for m in MODELS], fontsize=9.5)
    handles = [Rectangle((0, 0), 1, 1, facecolor=LIKERT[k],
                         edgecolor=GRID if k == 3 else "none", linewidth=0.5,
                         label=f"{k}") for k in range(1, 6)]
    fig.legend(handles=handles, loc="lower right", bbox_to_anchor=(0.98, 0.035),
               frameon=False, fontsize=8.5, ncol=5, title="rating", title_fontsize=8.5,
               handlelength=1.1, handletextpad=0.4, columnspacing=0.9)
    title_block(fig, "How often each rating was given",
                "Centered on the neutral rating 3 — left of the axis: ratings 1–2, right: ratings 4–5")
    footer(fig)
    save(fig, "fig4_rating_distribution")


# ------------------------------------------- fig5 composite distribution ----
def fig_composite_strip():
    fig, ax = plt.subplots(figsize=(8.6, 4.6))
    fig.subplots_adjust(left=0.19, right=0.96, top=0.80, bottom=0.15)
    rng = np.random.default_rng(7)
    ys = np.arange(len(MODELS))[::-1]
    for y, m in zip(ys, MODELS):
        vals = np.array([r["composite"] for r in sel(m)])
        jitter = rng.uniform(-0.16, 0.16, len(vals))
        ax.plot(vals, y + jitter, "o", color=BLUE_LIGHT, markersize=6.5, alpha=0.85,
                markeredgecolor=SURFACE, markeredgewidth=0.9, zorder=3)
        med = np.median(vals)
        ax.plot([med, med], [y - 0.30, y + 0.30], color=BLUE, linewidth=2.5,
                solid_capstyle="round", zorder=4)
        ax.text(med, y + 0.40, f"{med:.2f}", ha="center", fontsize=8.3, color=INK2)
    ax.set_yticks(ys)
    ax.set_yticklabels([MODEL_LABEL[m] for m in MODELS], fontsize=10)
    ax.set_xlim(2.4, 5.15)
    ax.set_ylim(-0.75, len(MODELS) - 0.15)
    style_axes(ax)
    ax.legend(handles=[
        plt.Line2D([], [], marker="o", linestyle="", color=BLUE_LIGHT, markersize=7,
                   markeredgecolor=SURFACE, label="one document"),
        plt.Line2D([], [], color=BLUE, linewidth=2.5, label="median"),
    ], loc="lower left", frameon=False, fontsize=8.5, handletextpad=0.4,
        bbox_to_anchor=(0.0, 1.0), ncol=2, borderaxespad=0)
    title_block(fig, "Per-document composite score",
                "composite = mean of faithfulness, quality and linguistic sub-scores (1–5) · one dot per document")
    footer(fig)
    save(fig, "fig5_composite_distribution")


# ----------------------------------------------------- fig6 by language -----
def fig_language():
    langs = ["en", "de", "fr", "es", "zh"]
    lang_n = {l: len({r["doc_id"] for r in ROWS if r["lang"] == l}) for l in langs}
    M = np.zeros((len(MODELS), len(langs)))
    K = {}
    for i, m in enumerate(MODELS):
        for j, l in enumerate(langs):
            rs = sel(m, lang=l)
            kept = sum(r["accept"] for r in rs)
            M[i, j] = kept / len(rs)
            K[i, j] = (kept, len(rs))
    fig, ax = plt.subplots(figsize=(7.6, 4.2))
    fig.subplots_adjust(left=0.21, right=0.97, top=0.76, bottom=0.06)
    ax.pcolormesh(M[::-1], cmap=CMAP, vmin=0.2, vmax=1.0, edgecolors=SURFACE, linewidth=2)
    for i in range(len(MODELS)):
        for j in range(len(langs)):
            kept, n = K[i, j]
            frac = (M[i, j] - 0.2) / 0.8
            ink = "#ffffff" if frac > 0.55 else INK
            ax.text(j + 0.5, len(MODELS) - 1 - i + 0.5, f"{kept}/{n}",
                    ha="center", va="center", fontsize=9, color=ink)
    ax.set_yticks(np.arange(len(MODELS)) + 0.5)
    ax.set_yticklabels([MODEL_LABEL[m] for m in MODELS[::-1]], fontsize=9.5)
    ax.set_xticks(np.arange(len(langs)) + 0.5)
    ax.set_xticklabels([f"{l}\n({lang_n[l]} docs)" for l in langs], fontsize=9, color=INK2)
    ax.xaxis.set_ticks_position("top")
    ax.tick_params(length=0)
    for side in ax.spines.values():
        side.set_visible(False)
    ax.set_xlim(0, len(langs))
    ax.set_ylim(0, len(MODELS))
    title_block(fig, "Questions kept, by question language",
                "Cell = kept / judged · darker = higher keep rate · small per-cell samples")
    footer(fig, y=0.012)
    save(fig, "fig6_keep_by_language")


# ------------------------------------------------ fig7 overall mean score ---
def fig_overall_score():
    fig, ax = plt.subplots(figsize=(8.2, 4.0))
    fig.subplots_adjust(left=0.20, right=0.93, top=0.76, bottom=0.16)
    order = sorted(MODELS, key=lambda m: -np.mean([r["composite"] for r in sel(m)]))
    ys = np.arange(len(order))[::-1]
    for y, m in zip(ys, order):
        vals = np.array([r["composite"] for r in sel(m)])
        mean = vals.mean()
        half = 1.96 * vals.std(ddof=1) / np.sqrt(len(vals))
        ax.plot([mean - half, mean + half], [y, y], color=BLUE_150, linewidth=2,
                solid_capstyle="round", zorder=2)
        ax.plot(mean, y, "o", color=BLUE, markersize=9, markeredgecolor=SURFACE,
                markeredgewidth=1.3, zorder=3)
        ax.annotate(f"{mean:.2f}", (mean, y), xytext=(0, 9), textcoords="offset points",
                    ha="center", fontsize=8.8, color=INK2)
    ax.set_yticks(ys)
    ax.set_yticklabels([MODEL_LABEL[m] for m in order], fontsize=10)
    ax.set_xlim(4.15, 4.85)
    ax.set_ylim(-0.6, len(order) - 0.4)
    ax.set_xticks(np.arange(4.2, 4.81, 0.1))
    ax.set_xticklabels([f"{v:.1f}" for v in np.arange(4.2, 4.81, 0.1)])
    style_axes(ax)
    ax.legend(handles=[
        plt.Line2D([], [], marker="o", linestyle="", color=BLUE, markersize=8,
                   markeredgecolor=SURFACE, label="mean over 30 documents"),
        plt.Line2D([], [], color=BLUE_150, linewidth=2, label="95% CI"),
    ], loc="lower left", frameon=False, fontsize=8.5, handletextpad=0.4,
        bbox_to_anchor=(0.0, 1.0), ncol=2, borderaxespad=0)
    title_block(fig, "Overall average score",
                "composite = mean of faithfulness, quality and linguistic sub-scores (1–5 scale, axis zoomed to 4.2–4.8)")
    footer(fig, extra="Confidence intervals overlap heavily — average-score differences between the models are not statistically meaningful at n=30")
    save(fig, "fig7_overall_score")


# ---------------------------------------------------- fig8 notes scoreboard -
# Hand-tagged from the 17 shared_notes, de-anonymised via the slot mapping
# (see annotator_notes.md). Categories:
#   S strongest/clearest mention        P other praise (strong/specific/good/useful)
#   U adds or alters content (incl. numerical-condition changes)
#   V vague / thin context / imprecise phrasing
#   M answer does not actually answer the question
#   L language mixing / weaker language quality
# Remarks about overlap between questions are not tagged.
NOTES_TAGS = [
    # (doc_id, model, category)
    ("MX-2025009666-A", "sonnet-4.6", "S"), ("MX-2025009666-A", "gpt-5-mini", "P"),
    ("MX-2025009666-A", "qwen3.6-35b-a3b", "P"), ("MX-2025009666-A", "gemini-3.5-flash", "P"),
    ("MX-2025009666-A", "grok-4.3", "P"), ("MX-2025009666-A", "gpt-5.4-mini", "V"),
    ("WO-2023149795-A1", "qwen3.6-35b-a3b", "S"), ("WO-2023149795-A1", "sonnet-4.6", "S"),
    ("WO-2025211128-A1", "qwen3.6-35b-a3b", "S"), ("WO-2025211128-A1", "sonnet-4.6", "S"),
    ("WO-2025211128-A1", "gemini-3.5-flash", "P"), ("WO-2025211128-A1", "grok-4.3", "P"),
    ("WO-2025211128-A1", "gpt-5-mini", "V"), ("WO-2025211128-A1", "gpt-5.4-mini", "V"),
    ("MX-2025002756-A", "gemini-3.5-flash", "S"), ("MX-2025002756-A", "grok-4.3", "P"),
    ("MX-2025002756-A", "qwen3.6-35b-a3b", "V"), ("MX-2025002756-A", "sonnet-4.6", "V"),
    ("MX-2025002756-A", "gpt-5-mini", "V"),
    ("EP-4504821-A1", "sonnet-4.6", "S"), ("EP-4504821-A1", "gemini-3.5-flash", "S"),
    ("EP-4504821-A1", "gpt-5-mini", "V"), ("EP-4504821-A1", "grok-4.3", "V"),
    ("EP-4504821-A1", "gpt-5.4-mini", "V"), ("EP-4504821-A1", "gpt-5.4-mini", "L"),
    ("EP-4504821-A1", "qwen3.6-35b-a3b", "V"), ("EP-4504821-A1", "qwen3.6-35b-a3b", "L"),
    ("WO-2025211336-A1", "gpt-5-mini", "S"),
    ("WO-2025211336-A1", "gemini-3.5-flash", "P"), ("WO-2025211336-A1", "gemini-3.5-flash", "U"),
    ("WO-2025211336-A1", "sonnet-4.6", "P"), ("WO-2025211336-A1", "sonnet-4.6", "U"),
    ("WO-2025211336-A1", "gpt-5.4-mini", "M"), ("WO-2025211336-A1", "grok-4.3", "U"),
    ("WO-2025211336-A1", "qwen3.6-35b-a3b", "U"),
    ("EP-4584229-A1", "sonnet-4.6", "S"), ("EP-4584229-A1", "qwen3.6-35b-a3b", "P"),
    ("WO-2025054647-A1", "gpt-5-mini", "S"),
    ("EP-4630021-A1", "gpt-5-mini", "S"), ("EP-4630021-A1", "sonnet-4.6", "S"),
    ("EP-4630021-A1", "qwen3.6-35b-a3b", "S"), ("EP-4630021-A1", "gemini-3.5-flash", "V"),
    ("EP-4627881-A1", "gpt-5.4-mini", "S"),
    ("MX-2025007206-A", "qwen3.6-35b-a3b", "S"), ("MX-2025007206-A", "gpt-5.4-mini", "S"),
    ("MX-2025007206-A", "grok-4.3", "S"), ("MX-2025007206-A", "gpt-5-mini", "V"),
    ("MX-2025007206-A", "gemini-3.5-flash", "U"), ("MX-2025007206-A", "sonnet-4.6", "U"),
    ("MX-2025010190-A", "grok-4.3", "S"),
    ("WO-2025207810-A1", "gpt-5-mini", "S"), ("WO-2025207810-A1", "qwen3.6-35b-a3b", "S"),
    ("WO-2025207810-A1", "sonnet-4.6", "L"),
    ("EP-4577789-A1", "gpt-5.4-mini", "S"), ("EP-4577789-A1", "qwen3.6-35b-a3b", "S"),
    ("EP-4577789-A1", "gemini-3.5-flash", "P"), ("EP-4577789-A1", "sonnet-4.6", "P"),
    ("WO-2025212655-A1", "sonnet-4.6", "S"), ("WO-2025212655-A1", "gpt-5-mini", "S"),
    ("WO-2025212655-A1", "gpt-5.4-mini", "S"),
    ("MX-2025006624-A", "gpt-5-mini", "S"), ("MX-2025006624-A", "gemini-3.5-flash", "S"),
    ("WO-2025187661-A8", "gpt-5-mini", "S"),
    ("WO-2025187661-A8", "sonnet-4.6", "P"), ("WO-2025187661-A8", "sonnet-4.6", "V"),
    ("WO-2025187661-A8", "gemini-3.5-flash", "M"), ("WO-2025187661-A8", "grok-4.3", "M"),
    ("WO-2025187661-A8", "gpt-5.4-mini", "M"),
    ("WO-2025187661-A8", "qwen3.6-35b-a3b", "U"), ("WO-2025187661-A8", "qwen3.6-35b-a3b", "M"),
]

# Where the note equates a question with another question, it inherits that
# question's verdict. Not applied where the annotator distinguishes on
# substance (WO-2023149795: Q6 "better because it gives more context";
# EP-4577789: Q1/Q2 ask one leg of the route, the strongest ask both ends).
NOTES_TAGS_INHERITED = [
    # Q3 equated with Q1 = "clear and specific"
    ("MX-2025002756-A", "gpt-5.4-mini", "P"),
    # Q1/Q2 equated with Q3 = "also strong, clearly asks the carbon range"
    ("EP-4584229-A1", "gpt-5.4-mini", "P"), ("EP-4584229-A1", "gemini-3.5-flash", "P"),
    # Q1/Q2 equated with Q6 (same Hamming-code question) = strongest
    ("WO-2025207810-A1", "gpt-5.4-mini", "S"), ("WO-2025207810-A1", "grok-4.3", "S"),
]

NOTES_CATS = [
    ("S", "called\nstrongest", "praise"),
    ("P", "other\npraise", "praise"),
    ("U", "adds / alters\ncontent", "crit"),
    ("V", "vague /\nthin context", "crit"),
    ("M", "answer doesn't\nanswer", "crit"),
    ("L", "language\nmixing", "crit"),
]


def fig_notes_scoreboard():
    import csv as _csv
    with open(OUT / "notes_feedback_tags.csv", "w", newline="") as f:
        w = _csv.writer(f)
        w.writerow(["doc_id", "model", "category", "inherited"])
        w.writerows([*t, 0] for t in NOTES_TAGS)
        w.writerows([*t, 1] for t in NOTES_TAGS_INHERITED)
    print("wrote notes_feedback_tags.csv")

    counts = {(m, c): 0 for m in MODELS for c, _, _ in NOTES_CATS}
    for doc, m, c in NOTES_TAGS + NOTES_TAGS_INHERITED:
        counts[(m, c)] += 1
    order = sorted(MODELS, key=lambda m: (-(counts[(m, "S")] + counts[(m, "P")]), -counts[(m, "S")]))

    red_ramp = LinearSegmentedColormap.from_list("crit", ["#fdf0ef", "#ec9791", "#c93a39"])
    blue_ramp = LinearSegmentedColormap.from_list("praise", ["#eff5fd", "#86b6ef", "#2a78d6"])
    VMAX = {"praise": 8, "crit": 4}
    RAMP = {"praise": blue_ramp, "crit": red_ramp}

    fig, ax = plt.subplots(figsize=(9.0, 4.6))
    fig.subplots_adjust(left=0.18, right=0.97, top=0.70, bottom=0.10)
    ncols, nrows = len(NOTES_CATS), len(order)
    for i, m in enumerate(order):
        y = nrows - 1 - i
        for j, (c, _, grp) in enumerate(NOTES_CATS):
            v = counts[(m, c)]
            frac = v / VMAX[grp]
            color = RAMP[grp](frac) if v else "#f5f4f1"
            ax.add_patch(Rectangle((j, y), 1, 1, facecolor=color, edgecolor=SURFACE, linewidth=2))
            if v == 0:
                ax.text(j + 0.5, y + 0.5, "–", ha="center", va="center", fontsize=9, color=MUTED)
            else:
                ink = "#ffffff" if frac > 0.62 else INK
                ax.text(j + 0.5, y + 0.5, str(v), ha="center", va="center",
                        fontsize=10, color=ink, fontweight="bold" if c == "S" else "normal")
    ax.set_yticks(np.arange(nrows) + 0.5)
    ax.set_yticklabels([MODEL_LABEL[m] for m in order[::-1]], fontsize=9.5)
    ax.set_xticks(np.arange(ncols) + 0.5)
    ax.set_xticklabels([lab for _, lab, _ in NOTES_CATS], fontsize=8.4, color=INK2)
    ax.xaxis.set_ticks_position("top")
    ax.tick_params(length=0)
    for side in ax.spines.values():
        side.set_visible(False)
    # group headers + separators
    spans = [("Praise", 0, 2), ("Criticism", 2, 6)]
    for name, a, b in spans:
        if name:
            ax.text((a + b) / 2, nrows + 0.95, name, ha="center", fontsize=9,
                    fontweight="bold", color=INK)
        if a > 0:
            ax.axvline(a, color=SURFACE, linewidth=6)
    ax.set_xlim(0, ncols)
    ax.set_ylim(0, nrows + 0.05)
    title_block(fig, "What the notes say, model by model",
                "Documents whose note praises or criticises the model's question, out of 17 noted documents · sorted by praise")
    footer(fig, y=0.012)
    save(fig, "fig8_notes_scoreboard")


# ------------------------------------------------------- summary tables -----
def write_summaries():
    per_model = []
    for m in MODELS:
        rs = sel(m)
        row = {
            "model": m,
            "n": len(rs),
            "keep_rate": round(float(np.mean([r["accept"] for r in rs])), 4),
            "keep_rate_technical": round(float(np.mean([r["accept"] for r in sel(m, mode="technical")])), 4),
            "keep_rate_semantic": round(float(np.mean([r["accept"] for r in sel(m, mode="semantic")])), 4),
            "faith_mean": round(float(np.mean([r["faith_mean"] for r in rs])), 4),
            "quality_mean": round(float(np.mean([r["quality_mean"] for r in rs])), 4),
            "linguistic_mean": round(float(np.mean([r["linguistic"] for r in rs])), 4),
            "composite_mean": round(float(np.mean([r["composite"] for r in rs])), 4),
            "composite_median": round(float(np.median([r["composite"] for r in rs])), 4),
            "rubric_switched": int(sum(r["rubric"] != r["mode"] for r in rs)),
        }
        per_model.append(row)

    # within-document head-to-head on composite
    by_doc = defaultdict(dict)
    for r in ROWS:
        by_doc[r["doc_id"]][r["model"]] = r["composite"]
    ranks = defaultdict(list)
    best = defaultdict(int)
    worst = defaultdict(int)
    for doc, scores in by_doc.items():
        vals = sorted(scores.values(), reverse=True)
        top, bottom = max(scores.values()), min(scores.values())
        for m, v in scores.items():
            rank = 1 + sum(1 for o in scores.values() if o > v)  # ties share best rank
            ranks[m].append(rank)
            if v == top:
                best[m] += 1
            if v == bottom:
                worst[m] += 1
    for row in per_model:
        m = row["model"]
        row["mean_rank_in_doc"] = round(float(np.mean(ranks[m])), 3)
        row["times_co_best"] = best[m]
        row["times_co_worst"] = worst[m]

    import csv
    with open(OUT / "per_model_summary.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(per_model[0].keys()))
        w.writeheader()
        w.writerows(per_model)
    with open(OUT / "per_model_summary.json", "w") as f:
        json.dump(per_model, f, indent=2)
    print("wrote per_model_summary.{csv,json}")
    for row in per_model:
        print(row)


if __name__ == "__main__":
    fig_keep_rate()
    fig_keep_by_mode()
    fig_criteria_heatmap()
    fig_rating_distribution()
    fig_composite_strip()
    fig_language()
    fig_overall_score()
    fig_notes_scoreboard()
    write_summaries()
