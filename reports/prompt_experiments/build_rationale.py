"""Build an evidence-linked rationale from frozen prompt snapshots, without editing them."""

import argparse
import csv
import hashlib
import html
import json
from pathlib import Path


def build(root):
    mappings = {version: json.loads((root / version / "prompts.json").read_text())
                for version in ("baseline", "debiased", "simple")}

    def quote(version, key, start, stop=None):
        text = mappings[version][key]
        position = text.index(start)
        end = text.index(stop, position) + len(stop) if stop else position + len(start)
        return {"version": version, "key": key, "quote": text[position:end],
                "prompt_line": text[:position].count("\n") + 1,
                "snapshot": f"{version}/prompts.json"}

    def jev(version, corpus, field, index=None):
        key = corpus + "/decider/jev"
        prompt = json.loads(mappings[version][key])["questions"]["mode"]
        text = prompt["instructions"]["selection"][index] if field == "selection" else prompt["criteria"][field]
        return {"version": version, "key": key, "quote": text,
                "json_pointer": f"questions.mode.instructions.selection[{index}]" if field == "selection"
                                else f"questions.mode.criteria.{field}",
                "snapshot": f"{version}/prompts.json"}

    entries = [
        {"title": "EUR-Lex: broad lookup eligibility competes with a narrower case test",
         "kind": "Routing policy intervention",
         "before": [jev("baseline", "eurlex", "selection", 0), jev("baseline", "eurlex", "selection", 1)],
         "after": [jev("debiased", "eurlex", "selection", 3)],
         "mechanism": "A direct lookup can describe almost every legal rule, while a scenario must clear additional factual conditions. The original prompts already supported fact patterns, included positive examples and preferred a case when meaningful particulars fit; the baseline standard GPT selected 37/50 fact patterns while Jev selected 0/50. The revised tie rule strengthens that preference. It does not remove an explicit original lookup priority, and it does not establish that fact patterns are better.",
         "simple": "The simplified router preserves this same tie policy; it is not an independent neutral policy."},
        {"title": "EUR-Lex: routine application was easy to classify as penalized inference",
         "kind": "Faithfulness rubric correction",
         "before": [quote("baseline", "eurlex/faithfulness", "No inference\n     whatsoever. (Rare.)"),
                    quote("baseline", "eurlex/faithfulness", "3 — Answer is grounded", "or similar.")],
         "after": [quote("debiased", "eurlex/faithfulness", "Hypothetical facts belong to the question", "reduce grounding.")],
         "mechanism": "Fact patterns necessarily connect supplied hypothetical facts with a rule. The old scale could penalize that operation, or even pronoun resolution, despite correct evidence. The revised rule allows explicit condition/category matching while still excluding missing facts, converse rules and outside law.",
         "simple": "Retains direct application and context resolution as permitted operations."},
        {"title": "Both corpora: extreme brevity and rarity of 5s can distort faithfulness",
         "kind": "Shared grading calibration",
         "before": [quote("baseline", "eurlex/faithfulness", "5 is reserved", "5s should be uncommon."),
                    quote("baseline", "un/faithfulness", "5 — Answer is the shortest possible span", "(Rare.)")],
         "after": [quote("debiased", "un/faithfulness", "Completeness outranks minimum word count.", "multi-clause span.")],
         "mechanism": "Necessary qualifiers, governing clauses and attribution can make a complete answer longer. A rarity prior also moves scores without a candidate defect. Revised grading rewards complete, appropriately concise evidence and requires a specific reason for deductions.",
         "simple": "Preserves completeness, necessary context and criterion-based scoring without a rarity quota."},
        {"title": "EUR-Lex: case evidence need not repeat the whole legal conclusion",
         "kind": "Clarification of an ambiguous contract",
         "before": [quote("baseline", "eurlex/quality/fact_pattern", "Matching stated", "restriction are allowed."),
                    quote("baseline", "eurlex/quality/fact_pattern", "Require outcome-changing qualifications", "requested.")],
         "after": [quote("debiased", "eurlex/quality/fact_pattern", "The answer is an evidence span", "being absent from legislation.")],
         "mechanism": "The baseline quality verifier already permitted condition matching, rejected an added yes/no answer and waived unrelated entitlement conditions for category-only asks. The revision reinforces existing permissions and aligns them with the conflicting faithfulness rubric; it also addresses observed over-strict grading. It is not new permission for case application. A case still needs two relevant particulars and every fact decisive for its actual ask.",
         "simple": "Keeps ordinary case application valid without demanding extra drama or an added yes/no conclusion."},
        {"title": "UN: the practitioner stance excluded concrete requests and authorizations",
         "kind": "Generation/verifier eligibility correction",
         "before": [quote("baseline", "un/quality/practitioner", "1. NORM-STATE STANCE.", "“What troop ceiling applied?” can pass.")],
         "after": [quote("debiased", "un/quality/practitioner", "Questions may ask what applied", "binding law.")],
         "mechanism": "The baseline already allowed attributed findings, figures and concrete events. Its norm-state rule nevertheless excluded specific speech/request framings, such as asking what an organ requested or authorized. That can reject a useful request/proposal question or encourage a stronger legal status than the evidence supports. The revision expands those framings while preserving their status; it does not newly introduce all reported facts.",
         "simple": "Allows concrete requests, proposals, tasks and reported facts; it does not convert them into binding duties."},
        {"title": "UN: anchor quotas plus a hard word ceiling create conflicting demands",
         "kind": "Generation/verifier eligibility correction",
         "before": [quote("baseline", "un/quality/practitioner", "The question supplies the named regime", "at most 2."),
                    quote("baseline", "un/generation/practitioner", "Wording & Length: direct interrogative, 8–20 words, hard maximum 25.")],
         "after": [quote("debiased", "un/quality/practitioner", "Require sufficient substantive context", "additional generic institutions."),
                   quote("debiased", "un/generation/practitioner", "Prefer concise natural questions", "even when longer.")],
         "mechanism": "A single distinctive operational phrase can identify a need, while adding a second separately counted anchor, date and attribution can force awkward or truncated wording. Revised prompts test actual identification and concision rather than independent counts.",
         "simple": "Preserves one sufficient composite anchor and a soft 8–25-word guideline."},
        {"title": "UN: recurring wording was required to contain yearly novelty",
         "kind": "Generation/verifier eligibility correction",
         "before": [quote("baseline", "un/generation/practitioner", "For these, the year alone is not enough", "a named event.")],
         "after": [quote("debiased", "un/generation/practitioner", "Recurring wording is not automatically unusable", "what applied then.")],
         "mechanism": "A useful dated question about an unchanged norm can fail an instance-novelty test even when the regime and period are identified. The revision keeps specificity requirements but does not assume unseen duplicate passages or demand that a norm change annually.",
         "simple": "Retains concrete recurring content and rejects unsupported assumptions about duplicates."},
        {"title": "UN: guessed reader knowledge can suppress short, useful answers",
         "kind": "Generation/verifier informativeness correction",
         "before": [quote("baseline", "un/generation/practitioner", "Guessability: a specialist could complete the answer", '"in writing" for the form of a request).')],
         "after": [quote("debiased", "un/quality/practitioner", "A yes/no condition can genuinely be unknown.", "reduce informativeness.")],
         "mechanism": "The old better-than-even-odds test is an unmeasured prior about specialists, rather than evidence of an exposed answer. Revised grading penalizes actual circularity and answer disclosure, while permitting a short deciding span or genuine yes/no need.",
         "simple": "Keeps actual unknown information as the test; familiar-looking facts are not automatically uninformative."},
        {"title": "UN semantic grading: clarify that extraction is an answer contract",
         "kind": "Clarification, not a relaxation of answer support",
         "before": [quote("baseline", "un/quality/semantic", "lexical_distance:\nNatural conceptual reformulation", "near-verbatim question conversion: 1.")],
         "after": [quote("debiased", "un/quality/semantic", "The answer is intentionally extractive", "lexical-distance defect.")],
         "mechanism": "The baseline criterion already referred to question conversion, but observed notes sometimes criticized answer overlap. The revision explicitly restricts lexical-distance deductions to question scaffolding. It still rejects unsupported mechanisms, implementation claims and missing qualifications.",
         "simple": "Explicitly says QUESTION scaffolding only and never penalizes copied ANSWER text."},
        {"title": "UN routing still has an unresolved source-intent distinction",
         "kind": "Remaining identification problem",
         "before": [jev("baseline", "un", "selection", 1)],
         "after": [jev("debiased", "un", "selection", 1)],
         "mechanism": "Lookup and practitioner can ask about the same fact with different source-locator wording. The decider receives a passage, not an actual searcher or their source knowledge. Broader practitioner eligibility can therefore reverse the routing preference without proving greater question quality. Both prompts retain this overlap.",
         "simple": "Retains the known-source versus source-free specialist distinction; shorter wording cannot by itself identify unobserved user intent."},
    ]
    routing = []
    paths = {"baseline": root.parents[1] / "decider_screening/fresh100_20260930_examples/decisions.csv",
             "debiased": root / "debiased/run/decisions.csv"}
    for version, path in paths.items():
        if path.exists():
            with path.open(encoding="utf-8-sig", newline="") as stream:
                rows = [r for r in csv.DictReader(stream) if r["corpus"] == "un" and r["backend"] == "jev"]
            routing.append({"version": version, "decisions_present": len(rows),
                            "completed": sum(r["status"] == "completed" for r in rows),
                            "practitioner": sum(r.get("mode") == "practitioner" for r in rows)})
    data = {"status": "Rationale and routing diagnostic only; no common-evaluation result claim.",
            "snapshot_sha256": {version: hashlib.sha256((root / version / "prompts.json").read_bytes()).hexdigest()
                                for version in mappings},
            "entries": entries, "un_jev_routing_checkpoint": routing,
            "caveats": [
                "Native quality criteria differ by mode and are edited between versions; higher native /40 scores are not independent cross-version quality evidence.",
                "The frozen, blinded common evaluator uses the same five criteria and usability gate across all versions. Its results are required before any claim that a version improves quality.",
                "The fixed diagnostic sample is English only: 50 EUR-Lex articles and 50 UN passages, with 25 UN resolutions, 20 meeting passages and 5 letters. It is stratified, not a representative estimate of full-corpus or multilingual routing frequencies.",
                "There is one generation draw per target/mode/version. Routing counts are not a success criterion, and best-of-batch score comparisons must show candidate availability and usable coverage.",
                "The revised bundle changes several generation, routing and grading rules together. The simplified bundle compresses that contract; this is not a single-clause causal ablation."]}
    (root / "rationale.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")

    def citation(item):
        location = item.get("json_pointer") or f"prompt line {item['prompt_line']}"
        return ('<blockquote>' + html.escape(item["quote"]) + '</blockquote><p class="source"><a href="'
                + item["snapshot"] + '">' + html.escape(item["version"] + ": " + item["key"])
                + "</a> · " + html.escape(location) + "</p>")

    rows = []
    for entry in entries:
        rows.append('<section><h2>' + html.escape(entry["title"]) + '</h2><p class="kind">'
                    + html.escape(entry["kind"]) + '</p><div class="pair"><div><h3>Original clause</h3>'
                    + "".join(citation(q) for q in entry["before"]) + '</div><div><h3>Revised clause</h3>'
                    + "".join(citation(q) for q in entry["after"]) + "</div></div><p>"
                    + html.escape(entry["mechanism"]) + '</p><p class="simple"><strong>Simplified version:</strong> '
                    + html.escape(entry["simple"]) + "</p></section>")
    checkpoint = "; ".join(f"{r['version']}: {r['practitioner']}/{r['completed']} completed Jev decisions"
                           for r in routing)
    body = ('<h1>Why the legal prompts changed</h1><p class="intro">Exact excerpts from frozen snapshots, '
            'paired with the revised rule. These are documented mechanisms and hypotheses under test—not '
            'a claim that the revised questions are already better.</p><p><a href="experiment_design.json">Experiment design</a> '
            '· <a href="rationale.json">Structured rationale and snapshot hashes</a></p>'
            '<aside><strong>Routing is not quality.</strong> UN practitioner routing at this checkpoint: '
            + html.escape(checkpoint) + '. The 6→44 shift is a warning about overlapping mode definitions '
            'and backend sensitivity, not evidence that bias has been eliminated.</aside>'
            + "".join(rows) + '<h2>What the experiment can establish</h2><ul>'
            + "".join("<li>" + html.escape(item) + "</li>" for item in data["caveats"]) + '</ul>')
    css = "body{font:15px system-ui,sans-serif;color:#192330;max-width:1180px;margin:40px auto;padding:0 24px;line-height:1.6}h1{font-size:32px}h2{font-size:20px;margin-bottom:3px}h3{font-size:14px;color:#526477}section{border-top:1px solid #dbe2ea;margin-top:28px;padding-top:10px}.pair{display:grid;grid-template-columns:1fr 1fr;gap:24px}blockquote{margin:0;padding:14px;background:#f1f5f9;white-space:pre-wrap;font-size:13px}.source,.kind{font-size:12px;color:#526477}.simple{font-size:13px}.intro,aside{max-width:1050px}aside{padding:18px;background:#fff4d8;margin:24px 0}a{color:#215a93}li{margin:10px 0}@media(max-width:750px){.pair{display:block}}"
    (root / "rationale.html").write_text('<!doctype html><html lang="en"><meta charset="utf-8"><title>Legal prompt rationale</title><style>'
                                         + css + "</style><main>" + body + "</main></html>", encoding="utf-8")
    return data


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    result = build(args.directory)
    print(json.dumps({"entries": len(result["entries"]), "routing": result["un_jev_routing_checkpoint"]}))
