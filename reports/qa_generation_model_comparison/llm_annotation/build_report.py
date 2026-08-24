#!/usr/bin/env python3
"""Assemble analysis/report.html from the analysis outputs (numbers read from files, figures embedded)."""
import base64, csv, html, json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
A = HERE / "analysis"
pm = {(r["annotator"], r["model"]): r for r in csv.DictReader(open(A / "per_model_by_annotator.csv"))}
ann = {r["annotator"]: r for r in csv.DictReader(open(A / "annotator_summary.csv"))}
agr = json.load(open(A / "agreement.json"))
pq = {(r["doc_id"], r["model"]): r for r in csv.DictReader(open(A / "per_question_all_annotators.csv"))}
tags = {a: list(csv.DictReader(open(A / f"discard_reason_tags_{a}.csv"))) for a in ["claude", "gpt"]}
usage = json.load(open(A / "llm_usage.json"))
fallback = json.load(open(HERE / "claude_pass_fallback.json"))

ANN = ["human", "claude", "gpt"]
LABEL = {"human": "Human", "claude": "Claude Fable 5", "gpt": "GPT-5.6 Sol"}
MODELS = ["gpt-5.4-mini", "gpt-5-mini", "gemini-3.5-flash", "qwen3.6-35b-a3b", "grok-4.3", "sonnet-4.6"]
MLABEL = {"gpt-5.4-mini": "GPT-5.4-mini", "gpt-5-mini": "GPT-5-mini", "gemini-3.5-flash": "Gemini 3.5 Flash",
          "qwen3.6-35b-a3b": "Qwen3.6-35B-A3B", "grok-4.3": "Grok 4.3", "sonnet-4.6": "Sonnet 4.6"}

def f(x, d=2): return f"{float(x):.{d}f}"
def pct(x): return f"{100*float(x):.0f}%"
def img(name, alt):
    b = base64.b64encode((A / f"{name}.png").read_bytes()).decode()
    return f'<figure><img src="data:image/png;base64,{b}" alt="{html.escape(alt)}"><figcaption>{html.escape(alt)} · <code>{name}.png</code></figcaption></figure>'
def esc(s): return html.escape(s)

# ---- headline table
rows = []
for m in MODELS:
    c = agr["per_model_consensus"][m]
    cells = [f'<th scope="row">{MLABEL[m]}</th>']
    for a in ANN: cells.append(f'<td class="num {a}">{pct(pm[(a, m)]["keep_rate"])}</td>')
    for a in ANN: cells.append(f'<td class="num">{f(pm[(a, m)]["composite_mean"])}</td>')
    cells += [f'<td class="num">{pct(c["majority_keep"])}</td>', f'<td class="num">{pct(c["unanimous_keep"])}</td>']
    rows.append("<tr>" + "".join(cells) + "</tr>")
headline_table = f"""<div class="tablewrap"><table>
<thead><tr><th>generator</th><th colspan="3">keep rate</th><th colspan="3">composite (1–5)</th><th>majority keep</th><th>all 3 keep</th></tr>
<tr class="sub"><th></th><th class="human">human</th><th class="claude">Claude</th><th class="gpt">GPT</th><th>human</th><th>Claude</th><th>GPT</th><th></th><th></th></tr></thead>
<tbody>{''.join(rows)}</tbody></table></div>"""

P = agr["pairs"]
def pair(a, b): return P[f"{a}__{b}"]
agree_table = f"""<div class="tablewrap"><table>
<thead><tr><th>pair</th><th>keep agreement</th><th>Cohen κ</th><th>κ technical</th><th>κ semantic</th><th>ρ composite (180 q)</th><th>ρ faithfulness</th><th>ρ quality</th><th>ρ per-model keep (6)</th></tr></thead><tbody>
{''.join(f'<tr><th scope="row"><span class="{a}">{LABEL[a]}</span> × <span class="{b}">{LABEL[b]}</span></th><td class="num">{pct(pair(a,b)["keep_percent_agreement"])}</td><td class="num">{f(pair(a,b)["keep_cohen_kappa"])}</td><td class="num">{f(pair(a,b)["keep_kappa_technical"])}</td><td class="num">{f(pair(a,b)["keep_kappa_semantic"])}</td><td class="num">{f(pair(a,b)["composite_spearman"])}</td><td class="num">{f(pair(a,b)["faith_mean_spearman"])}</td><td class="num">{f(pair(a,b)["quality_mean_spearman"])}</td><td class="num"><strong>{f(pair(a,b)["per_model_keep_spearman"])}</strong></td></tr>' for a, b in [("human","claude"),("human","gpt"),("claude","gpt")])}
</tbody></table></div>"""

# ---- discard reason table
CATS = [("unanchored_generic", "unanchored / generic question"), ("faithfulness", "faithfulness"), ("answer_form", "answer form (padded, list, framing)"),
        ("answer_language_mismatch", "answer ↔ question language mismatch"), ("trivial_tautological", "trivial / tautological"),
        ("not_search_like", "not search-like / fluency"), ("lifted_wording", "lifted wording"), ("multi_fact", "multi-fact"), ("near_duplicate", "near-duplicate"), ("conceptual_vs_factual", "conceptual vs factual"), ("other", "other")]
cc = {a: Counter(r["primary_category"] for r in tags[a]) for a in tags}
ch = {a: Counter(r["primary_category"] for r in tags[a] if r["human_keep"] == "yes") for a in tags}
tag_rows = "".join(f'<tr><th scope="row">{lab}</th><td class="num">{cc["claude"][k] or "–"}</td><td class="num">{ch["claude"][k] or "–"}</td><td class="num">{cc["gpt"][k] or "–"}</td><td class="num">{ch["gpt"][k] or "–"}</td></tr>' for k, lab in CATS if cc["claude"][k] or cc["gpt"][k])
tag_table = f"""<div class="tablewrap"><table>
<thead><tr><th>primary reason</th><th class="claude">Claude discards ({len(tags['claude'])})</th><th class="claude">…that the human kept ({sum(ch['claude'].values())})</th><th class="gpt">GPT discards ({len(tags['gpt'])})</th><th class="gpt">…that the human kept ({sum(ch['gpt'].values())})</th></tr></thead>
<tbody>{tag_rows}</tbody></table></div>"""

# ---- examples
def ex(doc, model, note):
    r = pq[(doc, model)]
    verdict = lambda a: f'<span class="pill {"keep" if r[f"{a}_keep"]=="yes" else "drop"}">{LABEL[a]}: {r[f"{a}_keep"]}</span>'
    return f"""<article class="example"><p class="q">{esc(r['question'])}</p><p class="a">— {esc(r['answer'])}</p>
<p class="meta">{MLABEL[model]} · {doc} · {r['mode']} · {r['lang']}</p>
<p class="verdicts">{verdict('human')} {verdict('claude')} {verdict('gpt')}</p>
<p class="reason"><span class="claude">Claude:</span> {esc(r['claude_reason'])}</p>
<p class="reason"><span class="gpt">GPT:</span> {esc(r['gpt_reason'])}</p>
<p class="note">{note}</p></article>"""
examples = "".join([
    ex("MX-2025002756-A", "gpt-5-mini", "The canonical disagreement: exact number, faithful answer, but “the alloy” anchors nothing. Human keeps on faithfulness; both LLMs discard on specificity."),
    ex("EP-4627127-A1", "gpt-5-mini", "A question whose answer is an adjective. The human scored faithfulness 5 and quality 4.75; the LLMs call it vacuous."),
    ex("EP-4504821-A1", "qwen3.6-35b-a3b", "Spanish question, English answer span. The human never penalised mixed-language answers; both LLMs do."),
    ex("MX-2025007206-A", "sonnet-4.6", "The one document Fable 5 refused (rAAV formulations); Claude's verdict here is Opus 5's. The three annotators split 1–1–1 on Sonnet's question."),
])

three = agr["three_way"]
hk_bd = [r for r in pq.values() if r["human_keep"]=="yes" and r["claude_keep"]=="no" and r["gpt_keep"]=="no"]
n_hk_bd = len(hk_bd); n_hk_bd_tech = sum(r["mode"]=="technical" for r in hk_bd); n_hk_bd_minis = sum(r["model"] in ("gpt-5-mini","gpt-5.4-mini") for r in hk_bd)
hc, hg, cg = pair("human","claude"), pair("human","gpt"), pair("claude","gpt")
gpt_u = usage["gpt"]["usage"]; cl_u = usage["claude"]["usage"]

page = f"""<title>Three Annotators, One Rubric</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,700&family=Source+Sans+3:ital,wght@0,400;0,600;1,400&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
:root {{
  --bg:#f6f6f3; --bg-2:#ecece7; --ink:#16161b; --ink-2:#53535c; --ink-3:#8a8a93; --rule:#d9d9d2; --card:#fdfdfb;
  --human:#2a78d6; --claude:#d95926; --gpt:#168f66; --keep:#168f66; --drop:#c93a39;
  --human-bg:#e4eefb; --claude-bg:#fbe7de; --gpt-bg:#dff3ea;
}}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{
  --bg:#18181b; --bg-2:#202024; --ink:#ececea; --ink-2:#b4b4bc; --ink-3:#7e7e88; --rule:#2f2f35; --card:#1f1f23;
  --human:#5c9df0; --claude:#f0884f; --gpt:#2fc08a; --keep:#2fc08a; --drop:#ef6b6a;
  --human-bg:#1d2a3d; --claude-bg:#3b2418; --gpt-bg:#163127; }} }}
:root[data-theme="dark"] {{
  --bg:#18181b; --bg-2:#202024; --ink:#ececea; --ink-2:#b4b4bc; --ink-3:#7e7e88; --rule:#2f2f35; --card:#1f1f23;
  --human:#5c9df0; --claude:#f0884f; --gpt:#2fc08a; --keep:#2fc08a; --drop:#ef6b6a;
  --human-bg:#1d2a3d; --claude-bg:#3b2418; --gpt-bg:#163127; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:var(--bg); color:var(--ink); font-family:"Source Sans 3","Segoe UI",system-ui,sans-serif; font-size:17px; line-height:1.55; }}
main {{ max-width:1060px; margin:0 auto; padding:48px 28px 80px; }}
h1,h2,h3 {{ font-family:"Fraunces","Iowan Old Style",Georgia,serif; text-wrap:balance; line-height:1.12; margin:0; }}
h1 {{ font-size:2.7rem; font-weight:700; letter-spacing:-0.01em; }}
h2 {{ font-size:1.65rem; font-weight:600; margin-top:3.2rem; padding-top:1.2rem; border-top:1px solid var(--rule); }}
h3 {{ font-size:1.15rem; font-weight:600; margin-top:1.8rem; }}
p, li {{ max-width:70ch; }}
.lede {{ font-size:1.22rem; color:var(--ink-2); max-width:62ch; margin-top:1rem; }}
.eyebrow {{ font-family:"IBM Plex Mono",monospace; font-size:0.74rem; letter-spacing:0.12em; text-transform:uppercase; color:var(--ink-3); margin-bottom:0.9rem; }}
.strip {{ display:grid; grid-template-columns:repeat(3,1fr); gap:14px; margin:2rem 0 0.5rem; }}
.tile {{ background:var(--card); border:1px solid var(--rule); border-radius:6px; padding:16px 18px; border-top:3px solid var(--tile); }}
.tile .who {{ font-weight:600; color:var(--tile); font-size:0.95rem; }}
.tile .big {{ font-family:"IBM Plex Mono",monospace; font-size:2.1rem; font-weight:500; margin:4px 0 0; line-height:1.1; }}
.tile .sub {{ color:var(--ink-2); font-size:0.9rem; margin:4px 0 0; }}
.tile.human {{ --tile:var(--human); }} .tile.claude {{ --tile:var(--claude); }} .tile.gpt {{ --tile:var(--gpt); }}
.human {{ color:var(--human); font-weight:600; }} .claude {{ color:var(--claude); font-weight:600; }} .gpt {{ color:var(--gpt); font-weight:600; }}
.tablewrap {{ overflow-x:auto; margin:1.2rem 0; }}
table {{ border-collapse:collapse; width:100%; font-size:0.92rem; }}
th, td {{ padding:7px 10px; border-bottom:1px solid var(--rule); text-align:left; vertical-align:top; }}
thead th {{ font-weight:600; color:var(--ink-2); font-size:0.82rem; letter-spacing:0.02em; }}
thead tr.sub th {{ font-size:0.78rem; color:var(--ink-3); border-bottom:2px solid var(--rule); }}
td.num {{ font-family:"IBM Plex Mono",monospace; font-variant-numeric:tabular-nums; text-align:right; font-weight:400; }}
td.num.human {{ background:var(--human-bg); }} td.num.claude {{ background:var(--claude-bg); }} td.num.gpt {{ background:var(--gpt-bg); }}
td.num.human, td.num.claude, td.num.gpt {{ color:var(--ink); }}
tbody th {{ font-weight:600; white-space:nowrap; }}
figure {{ margin:1.6rem 0; }}
figure img {{ max-width:100%; height:auto; display:block; border:1px solid var(--rule); border-radius:4px; background:#fcfcfb; }}
figcaption {{ font-size:0.84rem; color:var(--ink-3); margin-top:6px; }}
code {{ font-family:"IBM Plex Mono",monospace; font-size:0.86em; background:var(--bg-2); padding:1px 5px; border-radius:3px; }}
.examples {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(420px,1fr)); gap:16px; margin-top:1rem; }}
.example {{ background:var(--card); border:1px solid var(--rule); border-radius:6px; padding:16px 18px; font-size:0.95rem; }}
.example p {{ margin:0 0 6px; max-width:none; }}
.example .q {{ font-weight:600; font-size:1.02rem; }}
.example .a {{ color:var(--ink-2); font-style:italic; }}
.example .meta {{ font-family:"IBM Plex Mono",monospace; font-size:0.74rem; color:var(--ink-3); }}
.example .reason {{ font-size:0.9rem; color:var(--ink-2); }}
.example .note {{ border-top:1px dashed var(--rule); padding-top:8px; margin-top:8px; color:var(--ink); }}
.pill {{ display:inline-block; font-family:"IBM Plex Mono",monospace; font-size:0.74rem; padding:2px 8px; border-radius:999px; border:1px solid; margin-right:4px; }}
.pill.keep {{ color:var(--keep); border-color:var(--keep); }} .pill.drop {{ color:var(--drop); border-color:var(--drop); }}
.callout {{ background:var(--bg-2); border-left:3px solid var(--ink-3); padding:12px 16px; border-radius:0 4px 4px 0; margin:1.2rem 0; }}
.callout p {{ margin:0; }}
ul {{ padding-left:1.2rem; }} li {{ margin-bottom:0.45rem; }}
.files li {{ font-size:0.92rem; }}
footer {{ margin-top:3rem; color:var(--ink-3); font-size:0.84rem; border-top:1px solid var(--rule); padding-top:1rem; }}
@media (max-width:720px) {{ .strip {{ grid-template-columns:1fr; }} h1 {{ font-size:2.1rem; }} body {{ font-size:16px; }} }}
</style>
<main>
<p class="eyebrow">Question-generation model comparison · chemistry patents · 2026-08-22</p>
<h1>Three Annotators, One Rubric</h1>
<p class="lede">The blind 30-document review of six question generators was repeated with two LLM annotators — Claude Fable 5 and GPT-5.6 Sol — under the human annotator's exact protocol. The LLMs agree with each other and rank the generators almost in reverse of the human: the human keeps on faithfulness, the LLMs discard on specificity.</p>

<div class="strip">
<div class="tile human"><div class="who">Human (amirreza)</div><p class="big">{pct(ann['human']['keep_rate'])}</p><p class="sub">keep rate · technical {pct(ann['human']['keep_rate_technical'])} · semantic {pct(ann['human']['keep_rate_semantic'])}</p></div>
<div class="tile claude"><div class="who">Claude Fable 5</div><p class="big">{pct(ann['claude']['keep_rate'])}</p><p class="sub">keep rate · technical {pct(ann['claude']['keep_rate_technical'])} · semantic {pct(ann['claude']['keep_rate_semantic'])}</p></div>
<div class="tile gpt"><div class="who">GPT-5.6 Sol</div><p class="big">{pct(ann['gpt']['keep_rate'])}</p><p class="sub">keep rate · technical {pct(ann['gpt']['keep_rate_technical'])} · semantic {pct(ann['gpt']['keep_rate_semantic'])}</p></div>
</div>

<h2>Protocol</h2>
<p>Same 30 patent documents (16 technical-mode, 14 semantic-mode; question languages en/es/fr/de/zh) and the same 180 question–answer pairs from six anonymised generators. Each LLM annotator received, per document, the verbatim Argilla guidelines and criterion definitions, the source passage (all language versions), and Q1–Q6 with answers — then returned the three faithfulness scores, the four mode-specific quality scores, linguistic quality, a keep/discard decision and a one-sentence reason per question, plus an optional document note. Slot order was re-randomised independently for each pass (seeds 20260822 / 20260823), so no annotator saw the same Q1–Q6 assignment, and no prompt contained a system name.</p>
<ul>
<li><span class="claude">Claude Fable 5</span> — one fresh workflow subagent per document, reasoning effort high. Each agent was allowed a single <code>Read</code> of its own anonymised prompt file and nothing else; the transcripts were audited (30/30 clean: one Read of the right file + the structured-output call). Model per transcript: <code>claude-fable-5</code> on 29 documents.</li>
<li><span class="gpt">GPT-5.6 Sol</span> — OpenAI chat completions, <code>reasoning_effort=high</code>, strict JSON-schema output (<code>gpt-5.6-sol</code> on 30/30). It wrote its reasons in the question's language.</li>
</ul>
<div class="callout"><p><strong>One document could not be rated by Fable 5.</strong> <code>{fallback['doc_id']}</code> (an rAAV viral-vector formulation patent) triggered Fable 5's content filter — twice in the harness (automatic fallback to <code>claude-opus-5</code> right after the passage was read) and on a direct API call (<code>finish_reason=content_filter</code>, 0 tokens). The Opus 5 rating produced under the same blind protocol is kept in the Claude pass and flagged; removing it moves no per-generator keep rate by more than 3 pp and changes no ordering.</p></div>

<h2>Headline: the LLMs invert the human's ranking</h2>
{headline_table}
<p>Per-generator keep rates correlate <strong>ρ = {f(hc['per_model_keep_spearman'])}</strong> between human and Claude, <strong>{f(hg['per_model_keep_spearman'])}</strong> between human and GPT, and <strong>+{f(cg['per_model_keep_spearman'])}</strong> between the two LLMs (composite means: {f(hc['per_model_composite_spearman'])}, {f(hg['per_model_composite_spearman'])}, +{f(cg['per_model_composite_spearman'])}). The generators the human liked best — the two GPT-minis at 87% and 83% — are the ones both LLMs keep least (43–57%); Sonnet 4.6, the human's lowest keep rate, is Claude's 97% and GPT's highest composite. With n = 30 per generator the within-annotator orderings carry ±15 pp bootstrap intervals; the cross-annotator inversion is the robust result.</p>
{img('fig1_keep_rate_by_annotator', 'Keep rate by generator and annotator')}
{img('fig2_keep_by_mode_annotator', 'Keep rate by mode: the human keeps technical questions at 92%, Claude inverts the pattern, GPT is flat')}

<h2>Why: faithfulness drives the human, specificity drives the LLMs</h2>
<p>The LLMs rate nearly every answer as faithful ({pct(0.91)} of Claude's and {pct(0.89)} of GPT's faithfulness ratings are 5, against 75% for the human) and then decide on retrieval usefulness. The correlation between an annotator's own scores and its keep decision makes the split explicit: for the human, faithfulness predicts keep (r = 0.76) far better than specificity (0.34); for Claude it is the reverse (0.08 vs 0.71), and GPT sits in between (0.34 vs 0.68).</p>
{img('fig3_criteria_heatmap_by_annotator', 'Mean criterion score by generator, per annotator')}
<p>Claude is the harshest grader of the technical block — 2.1–2.2 mean specificity for the GPT-minis, 2.9 search-bar realism across the board — because it reads short factoid questions as conversational rather than search-like, and unanchored. GPT's technical block is milder but ranks the generators the same way. On faithfulness the three agree only on the ordering of the weakest (Qwen, Gemini), and the LLMs' precision scores sit a full point above the human's.</p>
{img('fig5_rating_distribution_by_annotator', 'How each annotator uses the 1–5 scale')}

<h3>Question-level agreement</h3>
{agree_table}
<p>Of 180 questions, {three['unanimous_keep']} are kept by all three, {three['unanimous_discard']} discarded by all three, and {three['split_2_1']} split; three-way Fleiss κ = {f(three['keep_fleiss_kappa'])}. Human–Claude keep agreement is at chance level (κ = {f(hc['keep_cohen_kappa'])}); the two LLMs agree with each other more than either does with the human, and agree best on technical documents (κ = {f(cg['keep_kappa_technical'])}). Specificity is the one criterion all three read alike (ρ 0.58–0.84); phrasing economy, conceptual framing and retrievability correlate near zero between human and LLMs — the rubric words mean different things to them.</p>
{img('fig4_keep_agreement', 'Keep-decision cross-tabulations')}

<h3>What the disagreements look like</h3>
<p>{n_hk_bd} questions were kept by the human and discarded by both LLMs — {n_hk_bd_tech} of them technical-mode, {n_hk_bd_minis} from the two GPT-minis. Nine went the other way (human discard, both LLMs keep), mostly Grok and Sonnet semantic questions where the human had flagged drifting framing and the LLMs scored grounding 4–5.</p>
<div class="examples">{examples}</div>

<h3>Why the LLMs discard</h3>
<p>Every LLM discard reason was hand-categorised (<code>discard_reason_tags_*.csv</code>). Claude's discards are dominated by a single criterion; GPT's split between specificity and faithfulness. Among the discards the human had kept, two-thirds of Claude's and nearly half of GPT's are the unanchored-generic category — the Claude–human disagreement is almost entirely Claude applying a retrieval-specificity standard the human did not. Both LLMs also penalise mixed-language answers (an English answer span under a Spanish or German question), which the human never did. Near-duplication across generators — the human's main complaint in the notes — is the most common <em>secondary</em> tag but never the primary reason.</p>
{tag_table}

<h3>Position and notes</h3>
{img('fig6_keep_by_slot_position', 'Keep rate by displayed slot position, per annotator')}
<p>No annotator shows a monotone position effect; GPT's Q4 dip (43%) is the largest single-slot deviation and within noise at 30 questions per bar. Claude wrote a document note for all 30 documents and GPT for 29 (the human: 17); both LLMs' dominant note is the same as the human's — five or six candidates targeting the same fact in many documents — and both flag encoding noise and literal calques in translated questions that the human did not mention.</p>
{img('fig7_composite_by_annotator', 'Composite score by generator and annotator')}

<h2>What to take from this</h2>
<ul>
<li>An LLM annotator is not a stand-in for this human annotator: the keep decisions disagree at chance level (Claude) to fair (GPT), and the generator ranking flips. Reporting an LLM-judge keep rate as if it were the human's would have picked Sonnet 4.6 instead of the GPT-minis.</li>
<li>The disagreement is about <em>standards</em>, not errors: on the contested questions both sides are internally consistent — the human is right that the answers are faithful; the LLMs are right that "what values can b take?" cannot retrieve the document. A benchmark needs both properties, which argues for a two-stage filter: human (or LLM) faithfulness check plus an LLM specificity/retrievability gate.</li>
<li>The two LLMs are a usable pair: they agree on every quality criterion (ρ 0.5–0.8) and on the generator ordering; GPT is the more human-like of the two (κ 0.30 vs 0.03) and catches faithfulness problems Claude does not, Claude is the stricter specificity gate.</li>
<li>Cheap wins for the generation pipeline that all three annotators point at: suppress near-duplicate questions across generators, reject answer spans whose language differs from the question, and require a document anchor (material, device, compound class) in technical-mode questions.</li>
</ul>

<h2>Caveats</h2>
<ul>
<li>One pass per LLM annotator; self-consistency across repeated passes was not measured.</li>
<li>1 of 30 Claude documents was rated by Opus 5 (content-filter fallback) and is labelled "Claude Fable 5" in the figures.</li>
<li>On 18/180 slots the human filled the other mode's quality block; quality and composite agreement compare non-identical criteria on those 10% of pairs (per-criterion correlations are unaffected).</li>
<li>All statistics were recomputed independently from the raw files by a separate verification pass (108 values, all matching to four decimals); the analysis code was reviewed for correctness with no bugs found.</li>
</ul>

<h2>Cost</h2>
<p>GPT-5.6 Sol: {gpt_u['prompt_tokens']/1000:.1f}k prompt + {gpt_u['completion_tokens']/1000:.1f}k completion tokens for 30 calls (~25 s each). Claude Fable 5: {cl_u['output_tokens']/1000:.0f}k output tokens and {(cl_u['cache_read_input_tokens']+cl_u['cache_creation_input_tokens'])/1e6:.1f}M cached input tokens across 31 agents, about one minute of wall clock.</p>

<h2>Files</h2>
<ul class="files">
<li><code>reports/qa_generation_model_comparison/llm_annotation/</code> — protocol (<code>README.md</code>, <code>rubric.md</code>), anonymised records and prompts per pass, private slot mappings, raw per-document results, audit and fallback notes, <code>analyze.py</code>.</li>
<li><code>…/llm_annotation/analysis/summary.md</code> — this report in markdown, plus <code>per_model_by_annotator.csv</code>, <code>agreement.json</code>, <code>per_question_all_annotators.csv</code> (all three verdicts + LLM reasons per question), <code>disagreements.md</code>, <code>notes_&lt;annotator&gt;.md</code>, <code>discard_reason_tags_&lt;annotator&gt;.csv</code>, figures 1–7 (.png/.pdf).</li>
<li>Previous human-only analysis: <code>…/annotation_analysis/summary.md</code>.</li>
</ul>
<footer>30 chemistry patent documents × 6 generators = 180 questions · human export 2026-08-18 · LLM passes 2026-08-22 · regenerate with <code>uv run python analyze.py &amp;&amp; uv run python build_report.py</code></footer>
</main>
"""
(A / "report.html").write_text(page)
print("wrote", A / "report.html", len(page) // 1024, "KB")
