# Legal question generation and grading: complete call trace

Run status: **completed**. Recorded calls: **16**.

[Questions and grades](results.csv) · [Full provider responses and run data](llm_calls.json) · Resumable state: `run.sqlite`.

Every recorded call, including retries, appears in chronological order. API status describes transport; stage status describes final parsing and validation. The JSON export retains every recorded provider response field. Any candidates beyond a requested quota remain in the raw outcomes.

## Run configuration and source targets

````json
{
  "eurlex": 0,
  "generator": "gpt-5.6-luna",
  "jev_model": "~typesafe/jev-latest",
  "keep": 3,
  "language": "en",
  "max_per_document": 1,
  "meeting_modes": "all",
  "prompts_sha256": "8cacd25e5d2b773bd619f1f5923ea61f32ee5503f089f778541ee7ceb25d65b3",
  "retries": 3,
  "seed": 20260929,
  "targets_sha256": "4baabf5cf0c56603199a75e70b7b778b513b4be3bcc340b08004507177179cc3",
  "un": 50,
  "verifier": "anthropic/claude-sonnet-5.5"
}
````

## Run summary

````json
{}
````

## Input capacity and generation diagnostics

Character counts are not token counts. Missing token usage or capacity remains unknown; provider capacity errors are recorded separately from rate limits and timeouts.

````json
{
  "inputs_by_model": {
    "anthropic/claude-sonnet-5.5": {
      "calls": 16,
      "provider_errors": 0,
      "capacity_errors": 0,
      "max_input_characters": 38756,
      "max_reported_prompt_tokens": 12395,
      "reference_context_tokens": null,
      "reported_input_exceeds_reference_context": null
    }
  },
  "generation_overproduction": []
}
````

## Final stage results

| Task | Stage | Attempts | Final status | Error |
|---|---|---:|---|---|
| mode/un/1999/a/c_3/54/sr_31#11/lookup | faithfulness | 1 | completed |  |
| mode/un/1999/a/c_3/54/sr_31#11/lookup | quality | 1 | completed |  |
| mode/un/2000/cd/pv_844#0/practitioner | faithfulness | 3 | failed | JSONDecodeError: Expecting value: line 1 column 1 (char 0) |
| mode/un/2000/cd/pv_844#0/practitioner | faithfulness_json_recovery | 1 | completed |  |
| mode/un/2000/cd/pv_844#0/practitioner | quality | 1 | completed |  |
| mode/un/2002/cedaw/c/sr_560#20/lookup | faithfulness | 1 | completed |  |
| mode/un/2002/cedaw/c/sr_560#20/lookup | quality | 1 | completed |  |
| mode/un/2003/a/res/57/97#3/semantic | faithfulness | 1 | completed |  |
| mode/un/2003/a/res/57/97#3/semantic | quality | 1 | completed |  |
| mode/un/2005/a/59/pv_84#8/lookup | faithfulness | 1 | completed |  |
| mode/un/2005/a/59/pv_84#8/lookup | quality | 1 | completed |  |
| mode/un/2005/a/59/pv_84#8/semantic | faithfulness | 1 | completed |  |
| mode/un/2005/a/59/pv_84#8/semantic | quality | 1 | completed |  |
| mode/un/2007/a/cn_9/sr_841#21/semantic | faithfulness | 1 | completed |  |
| mode/un/2007/a/cn_9/sr_841#21/semantic | quality | 1 | completed |  |
| mode/un/2007/cd/pv_1063#7/semantic | faithfulness | 1 | completed |  |
| mode/un/2007/cd/pv_1063#7/semantic | quality | 1 | completed |  |
| mode/un/2008/s/res/1826_2008_#5/semantic | faithfulness | 1 | completed |  |
| mode/un/2008/s/res/1826_2008_#5/semantic | quality | 1 | completed |  |
| mode/un/2009/a/c_2/64/sr_16#3/practitioner | faithfulness | 1 | completed |  |
| mode/un/2009/a/c_2/64/sr_16#3/practitioner | quality | 1 | completed |  |
| mode/un/2009/a/c_2/64/sr_16#3/semantic | faithfulness | 1 | completed |  |
| mode/un/2009/a/c_2/64/sr_16#3/semantic | quality | 1 | completed |  |
| mode/un/2011/a/res/65/133#13/semantic | faithfulness | 1 | completed |  |
| mode/un/2011/a/res/65/133#13/semantic | quality | 1 | completed |  |
| mode/un/2011/a/res/65/141#10/lookup | faithfulness | 1 | completed |  |
| mode/un/2011/a/res/65/141#10/lookup | quality | 1 | completed |  |
| mode/un/2011/cd/pv_1222#13/lookup | faithfulness | 1 | completed |  |
| mode/un/2011/cd/pv_1222#13/lookup | quality | 1 | completed |  |

## Call 001: faithfulness

Request: `2548d1223e8342df8fc6c1141adef115`. Task: `mode/un/2003/a/res/57/97#3/semantic`.

Model: `anthropic/claude-sonnet-5.5`. UTC: 2026-09-30T17:48:41.759774+00:00.

API status: **response**. Duration: 3.138616 seconds.

### Request settings

````json
{
  "extra_body": {
    "thinking": {
      "budget_tokens": 16000,
      "type": "enabled"
    }
  },
  "max_tokens": 32000
}
````

### Input 1: system

````text
You are a strict faithfulness grader for legal and policy question-answer pairs built from United
  Nations documents.

You will receive a three-section context and THREE question-answer pairs.
The context is:
- "### TARGET BLOCK" — the passage the questions are supposed to be about, in one or more language
  versions.
- "### REFERENCED DOCUMENTS" — other documents CITED by the target block, each supplied as its
  symbol, title, and text — provided ONLY so the target block's citations can be understood, the way
  a footnote helps a reader.
- "### DOCUMENT CONTEXT" — surrounding text of the SAME document (its opening and neighbouring
  passages), supplied so that the target block can be understood: it resolves which mission "the
  Mission" is, which country "the Government" governs, what period a report covers, and similar
  referring expressions.
BOTH supporting sections are for UNDERSTANDING ONLY. Using them to resolve a referring expression in
  the question or answer (naming "the Mission" as UNAMIR, identifying what a cited resolution
  concerns) is legitimate and must NOT be penalised. Using either of them as a source of answer
  substance is a grounding failure — the answer's facts must come from the TARGET BLOCK itself,
  fully.

THREE question-answer pairs (questions may be in any language; each answer matches its question's
  language). Grade each pair on three sub-criteria, each 1–5. Do NOT evaluate query shape or
  retrieval quality — those are handled separately. Focus only on how faithfully each answer
  reflects the supplied text.

GRADING INSTRUCTIONS:
- Grade each of the three pairs independently and against the absolute rubric below — not relative
  to the other two.
- Do not let similarity or dissimilarity between the three pairs influence any individual grade.
- Evaluate each pair on its own merits before moving to the next.

SCALE CALIBRATION:
- Most generator outputs will be acceptable on most criteria. "Acceptable" is not the same as
  "excellent."
- 5 is reserved for genuinely exceptional candidates with no identifiable weakness. If you can point
  to any imperfection, it is not a 5. 5s should be uncommon.
- 4 means the candidate is very good but has exactly one minor, identifiable issue. You must be able
  to name the issue.
- 3 is the default grade for a candidate that is acceptable and does the job, with one clear
  weakness. It is not a punishment grade — most acceptable candidates will receive 3s.
- 2 and 1 are reserved for candidates with real, identifiable problems. Do not avoid using them when
  a candidate qualifies.
- Before assigning any 4 or 5, pause and ask: "What specifically makes this better than a 3?" If you
  cannot answer concretely, the grade is 3.

SUB-CRITERIA:

1. GROUNDING (1–5): Is the answer supported by a contiguous span of the TARGET BLOCK?
   The supporting text means the TARGET BLOCK alone. Resolving a referring expression through the
     REFERENCED DOCUMENTS, the DOCUMENT CONTEXT, or the metadata lines is legitimate disambiguation,
     not an inferential step. Anything more is.
   Cap the grade at 2 if any part of the answer's substance — a fact, figure, list, reason, or
     condition — is stated only in a REFERENCED DOCUMENT or only in the DOCUMENT CONTEXT and not in
     the target block. Cap at 1 if the answer's substance mainly comes from outside the target
     block.
   5 — Answer is taken directly from a single short contiguous span of the target block. Every word
     of the answer is explicitly present or is a trivial rewording of explicit content. No inference
     whatsoever. (Rare.)
   4 — Answer is fully supported but requires reading across two adjacent sentences, OR is from a
     single span with minor trivial rewording that a strict reader might flag.
   3 — Answer is grounded in the target block but requires one small, defensible inferential step —
     connecting a pronoun to its referent, combining a figure with its unit, or similar.
   2 — Answer is partially supported: some parts grounded in the target block, other parts not
     (including parts taken from a REFERENCED DOCUMENT or the DOCUMENT CONTEXT).
   1 — Answer requires significant inference, outside knowledge, or is not in the target block at
     all.
   CITATION RULE (UN): UN texts constantly cite other instruments ("the measures imposed by
     paragraph 20 of resolution 1493 (2003)"). If the answer's substance sits behind such a citation
     rather than in the target block's own words, score at most 2 (1 if the answer consists mainly
     of such content) — REGARDLESS of whether the cited document was supplied in the REFERENCED
     DOCUMENTS section. References exist for understanding, never as answer material.
   ATTRIBUTION RULE (UN): summary records report delegates' statements, letters convey a
     government's position, and reports state the reporting body's findings and estimates. If the
     target block attributes a claim, estimate, or assessment to a speaker or body and the answer
     (or the question it responds to) presents that claim as established fact with the attribution
     stripped, cap GROUNDING at 2 — the supplied text supports the attributed claim, not the bare
     assertion.

2. PRECISION (1–5): Does the answer add unsupported details or padding?
   5 — Answer is the shortest possible span that fully answers the question. Not one extra word. No
     surrounding context, no hedges, no elaboration. (Rare.)
   4 — Answer is grounded and tight but includes one short fragment of adjacent context that could
     have been cut.
   3 — Answer is grounded but includes one unsupported detail, generalization, or piece of padding.
   2 — Answer includes multiple unsupported details, or uses speculative framing ("likely,"
     "approximately," "it seems") where the passage is specific.
   1 — Answer is largely padded with content not in the passage, or is a rewrite rather than an
     extraction.

3. NUMERICAL & CITATIONAL FIDELITY (1–5): Are numbers, dates, amounts, and official identifiers
  reproduced exactly? (JSON key remains "numerical_fidelity".)
   5 — All numbers, dates, durations, monetary amounts, percentages, troop figures, and official
     identifiers (document symbols, resolution and paragraph numbers) match the passage
     character-for-character (e.g., "resolution 2374 (2017)" preserved as-is, not "Resolution 2374";
     "S/1994/565", not "S/1994/565/Rev.1"; "up to 5,500 troops", not "about 5,000 troops"; "within
     30 days", not "in about a month"). Dates rendered in the answer language's standard format
     count as exact if day, month, and year are unchanged ("15 July 1994" for "le 15 juillet 1994").
   4 — All values and identifiers are correct and preserved, but with a trivial formatting
     difference (e.g., "30-day period" vs. "within 30 days", or a spacing/punctuation variant of an
     identifier).
   3 — One number or date is rounded or approximated, one identifier is truncated (e.g., year
     dropped from a resolution number), or one duration is converted to a different unit.
   2 — Multiple values or identifiers rounded, reformatted, truncated, or partially dropped.
   1 — Numbers, dates, or identifiers invented, significantly changed, or contradicted by the
     passage.
   N/A — Answer contains no numerical or citational content. Score this sub-criterion as 5 if N/A.

Output valid JSON only — a list of three objects, one per candidate, in the order the candidates
  were provided (index 0, 1, 2):
[
  {
    "index": 0,
    "grounding": <1-5>,
    "precision": <1-5>,
    "numerical_fidelity": <1-5>,
    "reason": "one short sentence explaining the grades"
  },
  {
    "index": 1,
    "grounding": <1-5>,
    "precision": <1-5>,
    "numerical_fidelity": <1-5>,
    "reason": "..."
  },
  {
    "index": 2,
    "grounding": <1-5>,
    "precision": <1-5>,
    "numerical_fidelity": <1-5>,
    "reason": "..."
  }
]

ACTUAL BATCH SIZE: This request contains exactly 2 candidates. Return exactly 2 grade objects, using indices [0, 1]. Grade only supplied candidates. Any references above to THREE pairs or three example objects describe a typical batch; this actual batch size overrides those counts. All scoring criteria and calibration remain unchanged.
````

### Input 2: user

````text
### TARGET BLOCK — write the questions about THIS text

[EN] Document: A/RES/57/97
  Title: Resolution adopted by the General Assembly
Noting that one hundred and sixty-six States have signed the Comprehensive Nuclear-Test-Ban Treaty, including a number of States in the region,
1. Welcomes the conclusions on the Middle East of the 2000 Review Conference of the Parties to the Treaty on the Non-Proliferation of Nuclear Weapons;
2. Reaffirms the importance of Israel's accession to the Treaty on the Non-Proliferation of Nuclear Weapons5 and placement of all its nuclear facilities under comprehensive International Atomic Energy Agency safeguards, in realizing the goal of universal adherence to the Treaty in the Middle East;
3. Calls upon that State to accede to the Treaty on the Non-Proliferation of Nuclear Weapons without further delay and not to develop, produce, test or otherwise acquire nuclear weapons, and to renounce possession of nuclear weapons, and to place all its unsafeguarded nuclear facilities under full-scope International Atomic Energy Agency safeguards as an important confidence-building measure among all States of the region and as a step towards enhancing peace and security;
4. Requests the Secretary-General to report to the General Assembly at its fifty-eighth session on the implementation of the present resolution;
5. Decides to include in the provisional agenda of its fifty-eighth session the item entitled "The risk of nuclear proliferation in the Middle East". 57th plenary meeting

### REFERENCED DOCUMENTS — none. The target block cites no other document available in the corpus.

### DOCUMENT CONTEXT — surrounding text of the SAME document, supporting context only. It resolves what the target block leaves implicit; it is never a source of answers.

[EN] Document A/RES/57/97 — surrounding passages
Resolution adopted by the General Assembly
[on the report of the First Committee (A/57/513)]
57/97. The risk of nuclear proliferation in the Middle East
The General Assembly,
Bearing in mind its relevant resolutions,
Taking note of the relevant resolutions adopted by the General Conference of the International Atomic Energy Agency, the latest of which is resolution GC(46)/RES/16, adopted on 20 September 2002,
Cognizant that the proliferation of nuclear weapons in the region of the Middle East would pose a serious threat to international peace and security,
Mindful of the immediate need for placing all nuclear facilities in the region of the Middle East under full-scope safeguards of the International Atomic Energy Agency,
Recalling the decision on principles and objectives for nuclear non-proliferation and disarmament adopted by the 1995 Review and Extension Conference of the Parties to the Treaty on the Non-Proliferation of Nuclear Weapons on 11 May 1995, in which the Conference urged universal adherence to the Treaty as an urgent priority and called upon all States not yet parties to the Treaty to accede to it at the earliest date, particularly those States that operate unsafeguarded nuclear facilities,

Recognizing with satisfaction that, in the Final Document of the 2000 Review Conference of the Parties to the Treaty on the Non-Proliferation of Nuclear Weapons, the Conference undertook to make determined efforts towards the achievement of the goal of universality of the Treaty on the Non-Proliferation of Nuclear Weapons, and called upon those remaining States not parties to the Treaty to accede to it, thereby accepting an international legally binding commitment not to acquire nuclear weapons or nuclear explosive devices and to accept International Atomic Energy Agency safeguards on all their nuclear activities, and underlined the necessity of universal adherence to the Treaty and of strict compliance by all parties with their obligations under the Treaty,
Recalling the resolution on the Middle East adopted by the 1995 Review and Extension Conference of the Parties to the Treaty on the Non-Proliferation of Nuclear Weapons on 11 May 1995, in which the Conference noted with concern the continued existence in the Middle East of unsafeguarded nuclear facilities, reaffirmed the importance of the early realization of universal adherence to the Treaty and called upon all States in the Middle East that had not yet done so, without exception, to accede to the Treaty as soon as possible and to place all their nuclear facilities under full-scope International Atomic Energy Agency safeguards,

Noting that Israel remains the only State in the Middle East that has not yet become party to the Treaty on the Non-Proliferation of Nuclear Weapons,
Concerned about the threats posed by the proliferation of nuclear weapons to the security and stability of the Middle East region,
Stressing the importance of taking confidence-building measures, in particular the establishment of a nuclear-weapon-free zone in the Middle East, in order to enhance peace and security in the region and to consolidate the global non-proliferation regime,
Emphasizing the need for all parties directly concerned to consider seriously taking the practical and urgent steps required for the implementation of the proposal to establish a nuclear-weapon-free zone in the region of the Middle East in accordance with the relevant resolutions of the General Assembly and, as a means of promoting this objective, inviting the countries concerned to adhere to the Treaty on the Non-Proliferation of Nuclear Weapons and, pending the establishment of the zone, to agree to place all their nuclear activities under International Atomic Energy Agency safeguards,

[... the TARGET BLOCK appears here ...]

Candidate 0:
  Question: What nuclear non-proliferation steps did the General Assembly call for regarding Israel in 2002?
  Answer: Calls upon that State to accede to the Treaty on the Non-Proliferation of Nuclear Weapons without further delay and not to develop, produce, test or otherwise acquire nuclear weapons, and to renounce possession of nuclear weapons, and to place all its unsafeguarded nuclear facilities under full-scope International Atomic Energy Agency safeguards as an important confidence-building measure among all States of the region and as a step towards enhancing peace and security

Candidate 1:
  Question: How did the General Assembly seek to strengthen safeguards in the Middle East in 2002?
  Answer: Reaffirms the importance of Israel's accession to the Treaty on the Non-Proliferation of Nuclear Weapons5 and placement of all its nuclear facilities under comprehensive International Atomic Energy Agency safeguards, in realizing the goal of universal adherence to the Treaty in the Middle East
````

### Output: choice 0

Finish reason: `stop`.

````text
[
  {
    "index": 0,
    "grounding": 4,
    "precision": 4,
    "numerical_fidelity": 5,
    "reason": "The answer copies paragraph 3 of the target block almost verbatim. 'That State' is only resolved to Israel through paragraph 2 and the context, which is a minor disambiguation. The trailing purpose clause is slightly extra."
  },
  {
    "index": 1,
    "grounding": 4,
    "precision": 3,
    "numerical_fidelity": 4,
    "reason": "The answer is taken from paragraph 2 and is supported. It copies the footnote marker '5' attached to the Treaty name, which is stray padding, and it focuses on accession more than safeguards. The '5' is only a trivial formatting artifact."
  }
]
````

### Recorded usage

````json
{
  "cached_tokens": 0,
  "completion_tokens": 271,
  "prompt_tokens": 5264,
  "provider_cost": 0.013238,
  "reasoning_tokens": 0
}
````

### Input size diagnostics

````json
{
  "input_characters": 14958,
  "context_capacity_exceeded": null
}
````

## Call 002: faithfulness

Request: `7db46613ae694a6fb0ca9677c25f24b8`. Task: `mode/un/2011/a/res/65/133#13/semantic`.

Model: `anthropic/claude-sonnet-5.5`. UTC: 2026-09-30T17:48:41.761947+00:00.

API status: **response**. Duration: 3.568967 seconds.

### Request settings

````json
{
  "extra_body": {
    "thinking": {
      "budget_tokens": 16000,
      "type": "enabled"
    }
  },
  "max_tokens": 32000
}
````

### Input 1: system

````text
You are a strict faithfulness grader for legal and policy question-answer pairs built from United
  Nations documents.

You will receive a three-section context and THREE question-answer pairs.
The context is:
- "### TARGET BLOCK" — the passage the questions are supposed to be about, in one or more language
  versions.
- "### REFERENCED DOCUMENTS" — other documents CITED by the target block, each supplied as its
  symbol, title, and text — provided ONLY so the target block's citations can be understood, the way
  a footnote helps a reader.
- "### DOCUMENT CONTEXT" — surrounding text of the SAME document (its opening and neighbouring
  passages), supplied so that the target block can be understood: it resolves which mission "the
  Mission" is, which country "the Government" governs, what period a report covers, and similar
  referring expressions.
BOTH supporting sections are for UNDERSTANDING ONLY. Using them to resolve a referring expression in
  the question or answer (naming "the Mission" as UNAMIR, identifying what a cited resolution
  concerns) is legitimate and must NOT be penalised. Using either of them as a source of answer
  substance is a grounding failure — the answer's facts must come from the TARGET BLOCK itself,
  fully.

THREE question-answer pairs (questions may be in any language; each answer matches its question's
  language). Grade each pair on three sub-criteria, each 1–5. Do NOT evaluate query shape or
  retrieval quality — those are handled separately. Focus only on how faithfully each answer
  reflects the supplied text.

GRADING INSTRUCTIONS:
- Grade each of the three pairs independently and against the absolute rubric below — not relative
  to the other two.
- Do not let similarity or dissimilarity between the three pairs influence any individual grade.
- Evaluate each pair on its own merits before moving to the next.

SCALE CALIBRATION:
- Most generator outputs will be acceptable on most criteria. "Acceptable" is not the same as
  "excellent."
- 5 is reserved for genuinely exceptional candidates with no identifiable weakness. If you can point
  to any imperfection, it is not a 5. 5s should be uncommon.
- 4 means the candidate is very good but has exactly one minor, identifiable issue. You must be able
  to name the issue.
- 3 is the default grade for a candidate that is acceptable and does the job, with one clear
  weakness. It is not a punishment grade — most acceptable candidates will receive 3s.
- 2 and 1 are reserved for candidates with real, identifiable problems. Do not avoid using them when
  a candidate qualifies.
- Before assigning any 4 or 5, pause and ask: "What specifically makes this better than a 3?" If you
  cannot answer concretely, the grade is 3.

SUB-CRITERIA:

1. GROUNDING (1–5): Is the answer supported by a contiguous span of the TARGET BLOCK?
   The supporting text means the TARGET BLOCK alone. Resolving a referring expression through the
     REFERENCED DOCUMENTS, the DOCUMENT CONTEXT, or the metadata lines is legitimate disambiguation,
     not an inferential step. Anything more is.
   Cap the grade at 2 if any part of the answer's substance — a fact, figure, list, reason, or
     condition — is stated only in a REFERENCED DOCUMENT or only in the DOCUMENT CONTEXT and not in
     the target block. Cap at 1 if the answer's substance mainly comes from outside the target
     block.
   5 — Answer is taken directly from a single short contiguous span of the target block. Every word
     of the answer is explicitly present or is a trivial rewording of explicit content. No inference
     whatsoever. (Rare.)
   4 — Answer is fully supported but requires reading across two adjacent sentences, OR is from a
     single span with minor trivial rewording that a strict reader might flag.
   3 — Answer is grounded in the target block but requires one small, defensible inferential step —
     connecting a pronoun to its referent, combining a figure with its unit, or similar.
   2 — Answer is partially supported: some parts grounded in the target block, other parts not
     (including parts taken from a REFERENCED DOCUMENT or the DOCUMENT CONTEXT).
   1 — Answer requires significant inference, outside knowledge, or is not in the target block at
     all.
   CITATION RULE (UN): UN texts constantly cite other instruments ("the measures imposed by
     paragraph 20 of resolution 1493 (2003)"). If the answer's substance sits behind such a citation
     rather than in the target block's own words, score at most 2 (1 if the answer consists mainly
     of such content) — REGARDLESS of whether the cited document was supplied in the REFERENCED
     DOCUMENTS section. References exist for understanding, never as answer material.
   ATTRIBUTION RULE (UN): summary records report delegates' statements, letters convey a
     government's position, and reports state the reporting body's findings and estimates. If the
     target block attributes a claim, estimate, or assessment to a speaker or body and the answer
     (or the question it responds to) presents that claim as established fact with the attribution
     stripped, cap GROUNDING at 2 — the supplied text supports the attributed claim, not the bare
     assertion.

2. PRECISION (1–5): Does the answer add unsupported details or padding?
   5 — Answer is the shortest possible span that fully answers the question. Not one extra word. No
     surrounding context, no hedges, no elaboration. (Rare.)
   4 — Answer is grounded and tight but includes one short fragment of adjacent context that could
     have been cut.
   3 — Answer is grounded but includes one unsupported detail, generalization, or piece of padding.
   2 — Answer includes multiple unsupported details, or uses speculative framing ("likely,"
     "approximately," "it seems") where the passage is specific.
   1 — Answer is largely padded with content not in the passage, or is a rewrite rather than an
     extraction.

3. NUMERICAL & CITATIONAL FIDELITY (1–5): Are numbers, dates, amounts, and official identifiers
  reproduced exactly? (JSON key remains "numerical_fidelity".)
   5 — All numbers, dates, durations, monetary amounts, percentages, troop figures, and official
     identifiers (document symbols, resolution and paragraph numbers) match the passage
     character-for-character (e.g., "resolution 2374 (2017)" preserved as-is, not "Resolution 2374";
     "S/1994/565", not "S/1994/565/Rev.1"; "up to 5,500 troops", not "about 5,000 troops"; "within
     30 days", not "in about a month"). Dates rendered in the answer language's standard format
     count as exact if day, month, and year are unchanged ("15 July 1994" for "le 15 juillet 1994").
   4 — All values and identifiers are correct and preserved, but with a trivial formatting
     difference (e.g., "30-day period" vs. "within 30 days", or a spacing/punctuation variant of an
     identifier).
   3 — One number or date is rounded or approximated, one identifier is truncated (e.g., year
     dropped from a resolution number), or one duration is converted to a different unit.
   2 — Multiple values or identifiers rounded, reformatted, truncated, or partially dropped.
   1 — Numbers, dates, or identifiers invented, significantly changed, or contradicted by the
     passage.
   N/A — Answer contains no numerical or citational content. Score this sub-criterion as 5 if N/A.

Output valid JSON only — a list of three objects, one per candidate, in the order the candidates
  were provided (index 0, 1, 2):
[
  {
    "index": 0,
    "grounding": <1-5>,
    "precision": <1-5>,
    "numerical_fidelity": <1-5>,
    "reason": "one short sentence explaining the grades"
  },
  {
    "index": 1,
    "grounding": <1-5>,
    "precision": <1-5>,
    "numerical_fidelity": <1-5>,
    "reason": "..."
  },
  {
    "index": 2,
    "grounding": <1-5>,
    "precision": <1-5>,
    "numerical_fidelity": <1-5>,
    "reason": "..."
  }
]

ACTUAL BATCH SIZE: This request contains exactly 2 candidates. Return exactly 2 grade objects, using indices [0, 1]. Grade only supplied candidates. Any references above to THREE pairs or three example objects describe a typical batch; this actual batch size overrides those counts. All scoring criteria and calibration remain unchanged.
````

### Input 2: user

````text
### TARGET BLOCK — write the questions about THIS text

[EN] Document: A/RES/65/133
  Title: Resolution adopted by the General Assembly on 15 December 2010
27. Calls upon all States and parties in complex humanitarian emergencies, in particular in armed conflict and in post-conflict situations, in countries in which humanitarian personnel are operating, in conformity with the relevant provisions of international law and national laws, to cooperate fully with the United Nations and other humanitarian agencies and organizations and to ensure the safe and unhindered access of humanitarian personnel, as well as delivery of supplies and equipment, in order to allow such personnel to efficiently perform their task of assisting affected civilian populations, including refugees and internally displaced persons;
28. Welcomes the progress made towards further enhancing the United Nations security management system, and supports the approach taken by the Secretary-General to focus the security management system on enabling the United Nations system to deliver on its mandates, programmes and activities by effectively managing the risks to which personnel are exposed, including in the provision of humanitarian assistance;

### REFERENCED DOCUMENTS — none. The target block cites no other document available in the corpus.

### DOCUMENT CONTEXT — surrounding text of the SAME document, supporting context only. It resolves what the target block leaves implicit; it is never a source of answers.

[EN] Document A/RES/65/133 — surrounding passages
Resolution adopted by the General Assembly on 15 December 2010
[without reference to a Main Committee (A/65/L.45 and Add.1)]
The General Assembly,
Reaffirming its resolution 46/182 of 19 December 1991 and the guiding principles contained in the annex thereto, other relevant General Assembly and Economic and Social Council resolutions and agreed conclusions of the Council,
Noting the reports of the Secretary-General on the strengthening of the coordination of emergency humanitarian assistance of the United Nations and on the Central Emergency Response Fund,
Reaffirming the principles of neutrality, humanity, impartiality and independence for the provision of humanitarian assistance, and reaffirming also the need for all actors engaged in the provision of humanitarian assistance in situations of complex emergencies and natural disasters to promote and fully respect these principles,
Deeply concerned about the humanitarian impact of such global challenges as the global financial and economic crisis, the food crisis and continuing food insecurity, including their effect on the increasing vulnerability of populations and their negative impact on the effective delivery of humanitarian assistance,

Emphasizing the need to mobilize adequate, predictable, timely and flexible resources for humanitarian assistance based on and in proportion to assessed needs, with a view to ensuring fuller coverage of the needs in all sectors and across humanitarian emergencies, and recognizing, in this regard, the achievements of the Central Emergency Response Fund,
Reiterating the need for Member States, relevant United Nations organizations and other relevant actors to mainstream a gender perspective into humanitarian assistance, including by addressing the specific needs of women, girls, boys and men in a comprehensive and consistent manner,
Expressing its deep concern at the increasing challenges faced by Member States and the United Nations humanitarian response capacity as a result of the consequences of natural disasters, including those related to the continuing impact of climate change, and reaffirming the importance of implementing the Hyogo Framework for Action 2005 - 2015: Building the Resilience of Nations and Communities to Disasters, inter alia, by providing adequate resources for disaster risk reduction, including investment in disaster preparedness, and by working towards building back better in all phases from relief to development,

Concerned about the challenges posed by the magnitude of some humanitarian emergencies, including some of the most recent natural disasters, in particular to the capacity and coordination of the humanitarian response system,
Recognizing that building national and local preparedness and response capacity is critical to a more predictable and effective response,
Emphasizing that enhancing international cooperation on emergency humanitarian assistance is essential, and reaffirming its resolution 64/251 of 22 January 2010 on international cooperation on humanitarian assistance in the field of natural disasters, from relief to development,
Emphasizing also the fundamentally civilian character of humanitarian assistance, and reaffirming the need in situations in which military capacity and assets are used to support the implementation of humanitarian assistance, for their use to be undertaken with the consent of the affected State and in conformity with international law, including international humanitarian law, as well as humanitarian principles,
Condemning the increasing number of deliberate threats and violent attacks against humanitarian personnel and facilities and the negative implications for the provision of humanitarian assistance to populations in need,

Recognizing the high numbers of persons affected by humanitarian emergencies, including internally displaced persons, bearing in mind their particular needs, and welcoming in this regard the adoption and ongoing ratification process of the African Union Convention for the Protection and Assistance of Internally Displaced Persons in Africa, which marks a significant step towards strengthening the national and regional normative framework for the protection of and assistance to internally displaced persons in Africa,
Recognizing also the importance of the Geneva Conventions of 1949, which include a vital legal framework for the Protection of Civilian Persons in Time of War, including the provision of humanitarian assistance,
Noting with grave concern that violence, including gender-based violence, particularly sexual violence, and violence against children, continues to be deliberately directed against civilian populations in many emergency situations,
Noting with appreciation the efforts made by the United Nations to improve humanitarian response, including by strengthening humanitarian response capacities, improving humanitarian coordination, enhancing predictable and adequate funding and strengthening the accountability of all stakeholders, and recognizing the importance of strengthening emergency administrative procedures and funding to allow for an effective response to emergencies,

Recognizing that in strengthening the coordination of humanitarian assistance in the field, United Nations organizations should continue to work in close coordination with national Governments,
1. Welcomes the outcome of the thirteenth humanitarian affairs segment of the Economic and Social Council at its substantive session of 2010;
2. Requests the Emergency Relief Coordinator to continue her efforts to strengthen the coordination of humanitarian assistance, and calls upon relevant United Nations organizations and other relevant intergovernmental organizations, as well as other humanitarian and development actors, to continue to work with the Office for the Coordination of Humanitarian Affairs of the Secretariat to enhance the coordination, effectiveness and efficiency of humanitarian assistance;
3. Calls upon the relevant organizations of the United Nations system and, as appropriate, other relevant humanitarian actors to continue efforts to improve the humanitarian response to natural and man-made disasters and complex emergencies by further strengthening humanitarian response capacities at all levels, by continuing to strengthen the coordination of humanitarian assistance at the field level, including in support of national authorities of the affected State, as appropriate, and by further enhancing transparency, performance and accountability;

4. Recognizes the benefits of engagement and coordination with relevant humanitarian actors to the effectiveness of humanitarian response, and encourages the United Nations to continue to pursue efforts to strengthen partnerships at the global level with the International Red Cross and Red Crescent Movement, relevant humanitarian non-governmental organizations and other participants in the Inter-Agency Standing Committee;
5. Requests the Secretary-General to strengthen the support provided to United Nations resident/humanitarian coordinators and to United Nations country teams, including by providing necessary training, identifying resources and improving the identification of and the selection process for United Nations resident/humanitarian coordinators, and enhancing their performance accountability;
6. Reaffirms the importance of implementing the Hyogo Framework for Action 2005 - 2015: Building the Resilience of Nations and Communities to Disasters, and looks forward to the midterm review of the Hyogo Framework for Action, the third session of the Global Platform for Disaster Risk Reduction, to be held in Geneva from 8 to 13 May 2011, and the 2011 Global Assessment Report on Disaster Risk Reduction;

7. Calls upon Member States and the international community to increase resources for disaster risk reduction measures, including in the areas of prevention, mitigation and preparedness for effective response and contingency planning, in order to, inter alia, further strengthen national and local capacities to prepare for and respond to humanitarian emergencies, and encourages closer cooperation between national stakeholders and humanitarian and development actors in this regard;
8. Urges Member States, the United Nations and other relevant organizations to take further steps to provide a coordinated emergency response to the food and nutrition needs of affected populations, while aiming to ensure that such steps are supportive of national strategies and programmes aimed at improving food security;
9. Expresses concern at the challenges related to, inter alia, safe access to and use of fuel, firewood, alternative energy, water and sanitation, shelter and food and health-care services in humanitarian emergencies, and takes note with appreciation of initiatives at the national and international levels that promote effective cooperation in this regard;

10. Encourages the international community, including relevant United Nations organizations and the International Federation of Red Cross and Red Crescent Societies, to support efforts of Member States aimed at strengthening their capacity to prepare for and respond to disasters and to support efforts, as appropriate, to strengthen systems for identifying and monitoring disaster risk, including vulnerability and natural hazards;
11. Welcomes the initiatives at the regional and national levels related to the implementation of the Guidelines for the Domestic Facilitation and Regulation of International Disaster Relief and Initial Recovery Assistance, adopted at the Thirtieth International Conference of the Red Cross and Red Crescent, held in Geneva from 26 to 30 November 2007, and encourages Member States and, where applicable, regional organizations, to take further steps to strengthen operational and legal frameworks for international disaster relief, taking into account the Guidelines, as appropriate;

12. Encourages States to create an enabling environment for the capacity building of local authorities and of national and local non-governmental and community-based organizations in order to ensure better preparedness in providing timely, effective and predictable humanitarian assistance, and encourages the United Nations and humanitarian organizations to provide support to such efforts, including, as appropriate, through the transfer of technology and expertise to developing countries and through support to programmes aimed at enhancing the coordination capacities of affected States;
13. Calls upon United Nations humanitarian entities, other relevant humanitarian organizations, development partners, the private sector, donor countries and the affected State to enhance cooperation and coordination, with a view to planning and delivering humanitarian assistance in ways that are supportive of early recovery as well as of sustainable rehabilitation and reconstruction efforts;
14. Requests the Secretary-General, in consultation with the affected countries and relevant humanitarian and development actors, to carry out an assessment of steps taken by the United Nations and relevant partners to support efforts to strengthen local, national and regional humanitarian response capacity and to include his findings as well as recommendations for enhancing United Nations support in this regard in his report to the General Assembly at its sixty-sixth session;

15. Encourages efforts to provide education in humanitarian emergencies, including in order to contribute to a smooth transition from relief to development;
16. Calls upon relevant United Nations organizations to support the improvement of the consolidated appeals process, inter alia, by engaging in the preparation of needs analyses and common humanitarian action plans, including through a better analysis of gender-related allocations, in order to further the development of the process as an instrument for United Nations strategic planning and prioritization, and by involving other relevant humanitarian organizations in the process, while reiterating that consolidated appeals should be prepared in consultation with affected States;
17. Requests Member States, relevant humanitarian organizations of the United Nations system and other relevant humanitarian actors to ensure that all aspects of humanitarian response, including disaster preparedness and needs assessment, take into account the specific needs of the affected population, recognizing that giving appropriate consideration to, inter alia, gender, age and disability is part of a comprehensive and effective humanitarian response, and in this regard encourages efforts to ensure gender mainstreaming in the delivery of humanitarian assistance;

18. Calls upon United Nations humanitarian organizations, in consultation with Member States, as appropriate, to strengthen the evidence base for humanitarian assistance by further developing common mechanisms to improve the quality, transparency and reliability of, and make further progress towards, common humanitarian needs assessments, including through improved collection, analysis and reporting of sex-, age- and disability-disaggregated data, to assess their performance in assistance and to ensure the most effective use of humanitarian resources by these organizations;
19. Calls upon donors to provide adequate, timely, predictable and flexible resources based on and in proportion to assessed needs, including for underfunded emergencies, and to continue to support diverse humanitarian funding channels, and encourages efforts to adhere to the Principles and Good Practice of Humanitarian Donorship;
20. Welcomes the important achievements of the Central Emergency Response Fund in ensuring a more timely and predictable response to humanitarian emergencies, stresses the importance of continuing to improve the functioning of the Fund in order to ensure that resources are used in the most efficient, effective, accountable and transparent manner possible, and looks forward to reviewing the five-year evaluation of the Fund in 2011;

21. Calls upon all Member States and invites the private sector and all concerned individuals and institutions to consider increasing their voluntary contributions to the Central Emergency Response Fund, and emphasizes that contributions should be additional to current commitments to humanitarian programming and should not be to the detriment of resources made available for international cooperation for development;
22. Reiterates that the Office for the Coordination of Humanitarian Affairs should benefit from adequate and more predictable funding, and calls upon all Member States to consider increasing voluntary contributions;
23. Reaffirms the obligation of all States and parties to an armed conflict to protect civilians in armed conflicts in accordance with international humanitarian law, and invites States to promote a culture of protection, taking into account the particular needs of women, children, older persons and persons with disabilities;
24. Calls upon States to adopt preventive measures and effective responses to acts of violence committed against civilian populations in armed conflicts and to ensure that those responsible are promptly brought to justice, in accordance with national law and their obligations under international law;

25. Urges all Member States to address gender-based violence in humanitarian emergencies and to ensure that their laws and institutions are adequate to prevent, promptly investigate and prosecute acts of gender-based violence, and calls upon States, the United Nations and all relevant humanitarian organizations to improve coordination, harmonize response and strengthen capacity, with a view to reducing such violence, and in support services to victims of such violence;
26. Recognizes the Guiding Principles on Internal Displacement as an important international framework for the protection of internally displaced persons, encourages Member States and humanitarian agencies to continue to work together, in collaboration with host communities, in endeavours to provide a more predictable response to the needs of internally displaced persons, and in this regard calls for continued and enhanced international support, upon request, for capacity-building efforts of States;

[... the TARGET BLOCK appears here ...]

29. Requests the Secretary-General to report on action taken to further the efforts of the United Nations to strengthen its ability to recruit and deploy staff quickly and flexibly, procure emergency relief materials and services rapidly, cost-effectively and locally, where applicable, and quickly disburse funds in order to support Governments and United Nations country teams in the coordination of international humanitarian assistance;
30. Reaffirms the importance of humanitarian assistance of the United Nations system, and welcomes the upcoming twentieth anniversary, at its sixty-sixth session, of its resolution 46/182;
31. Requests the Secretary-General to report to the General Assembly at its sixty-sixth session, through the Economic and Social Council at its substantive session of 2011, on progress made in strengthening the coordination of emergency humanitarian assistance of the United Nations and to submit a report to the Assembly on the detailed use of the Central Emergency Response Fund. 67th plenary meeting

Candidate 0:
  Question: How were humanitarian workers to reach civilians safely during armed conflict in 2010?
  Answer: to cooperate fully with the United Nations and other humanitarian agencies and organizations and to ensure the safe and unhindered access of humanitarian personnel, as well as delivery of supplies and equipment

Candidate 1:
  Question: How was the United Nations security management system oriented to protect humanitarian personnel in 2010?
  Answer: to focus the security management system on enabling the United Nations system to deliver on its mandates, programmes and activities by effectively managing the risks to which personnel are exposed, including in the provision of humanitarian assistance
````

### Output: choice 0

Finish reason: `stop`.

````text
[
  {
    "index": 0,
    "grounding": 3,
    "precision": 3,
    "numerical_fidelity": 5,
    "reason": "The answer is a verbatim span of paragraph 27, but it is a call on States and parties to cooperate and ensure access, which the question frames loosely as how workers 'were to reach civilians'. It also includes the cooperation clause as mild padding."
  },
  {
    "index": 1,
    "grounding": 4,
    "precision": 4,
    "numerical_fidelity": 5,
    "reason": "The answer is a verbatim span of paragraph 28. The 'to protect humanitarian personnel' framing in the question is a slight reinterpretation, since the text concerns managing risks to enable mandate delivery. The answer also includes the trailing 'including in the provision of humanitarian assistance' clause."
  }
]
````

### Recorded usage

````json
{
  "cached_tokens": 0,
  "completion_tokens": 293,
  "prompt_tokens": 8844,
  "provider_cost": 0.020618,
  "reasoning_tokens": 0
}
````

### Input size diagnostics

````json
{
  "input_characters": 27964,
  "context_capacity_exceeded": null
}
````

## Call 003: faithfulness

Request: `a46d2417a72344d7895130d7d7961f30`. Task: `mode/un/2011/a/res/65/141#10/lookup`.

Model: `anthropic/claude-sonnet-5.5`. UTC: 2026-09-30T17:50:23.145802+00:00.

API status: **response**. Duration: 2.800943 seconds.

### Request settings

````json
{
  "extra_body": {
    "thinking": {
      "budget_tokens": 16000,
      "type": "enabled"
    }
  },
  "max_tokens": 32000
}
````

### Input 1: system

````text
You are a strict faithfulness grader for legal and policy question-answer pairs built from United
  Nations documents.

You will receive a three-section context and THREE question-answer pairs.
The context is:
- "### TARGET BLOCK" — the passage the questions are supposed to be about, in one or more language
  versions.
- "### REFERENCED DOCUMENTS" — other documents CITED by the target block, each supplied as its
  symbol, title, and text — provided ONLY so the target block's citations can be understood, the way
  a footnote helps a reader.
- "### DOCUMENT CONTEXT" — surrounding text of the SAME document (its opening and neighbouring
  passages), supplied so that the target block can be understood: it resolves which mission "the
  Mission" is, which country "the Government" governs, what period a report covers, and similar
  referring expressions.
BOTH supporting sections are for UNDERSTANDING ONLY. Using them to resolve a referring expression in
  the question or answer (naming "the Mission" as UNAMIR, identifying what a cited resolution
  concerns) is legitimate and must NOT be penalised. Using either of them as a source of answer
  substance is a grounding failure — the answer's facts must come from the TARGET BLOCK itself,
  fully.

THREE question-answer pairs (questions may be in any language; each answer matches its question's
  language). Grade each pair on three sub-criteria, each 1–5. Do NOT evaluate query shape or
  retrieval quality — those are handled separately. Focus only on how faithfully each answer
  reflects the supplied text.

GRADING INSTRUCTIONS:
- Grade each of the three pairs independently and against the absolute rubric below — not relative
  to the other two.
- Do not let similarity or dissimilarity between the three pairs influence any individual grade.
- Evaluate each pair on its own merits before moving to the next.

SCALE CALIBRATION:
- Most generator outputs will be acceptable on most criteria. "Acceptable" is not the same as
  "excellent."
- 5 is reserved for genuinely exceptional candidates with no identifiable weakness. If you can point
  to any imperfection, it is not a 5. 5s should be uncommon.
- 4 means the candidate is very good but has exactly one minor, identifiable issue. You must be able
  to name the issue.
- 3 is the default grade for a candidate that is acceptable and does the job, with one clear
  weakness. It is not a punishment grade — most acceptable candidates will receive 3s.
- 2 and 1 are reserved for candidates with real, identifiable problems. Do not avoid using them when
  a candidate qualifies.
- Before assigning any 4 or 5, pause and ask: "What specifically makes this better than a 3?" If you
  cannot answer concretely, the grade is 3.

SUB-CRITERIA:

1. GROUNDING (1–5): Is the answer supported by a contiguous span of the TARGET BLOCK?
   The supporting text means the TARGET BLOCK alone. Resolving a referring expression through the
     REFERENCED DOCUMENTS, the DOCUMENT CONTEXT, or the metadata lines is legitimate disambiguation,
     not an inferential step. Anything more is.
   Cap the grade at 2 if any part of the answer's substance — a fact, figure, list, reason, or
     condition — is stated only in a REFERENCED DOCUMENT or only in the DOCUMENT CONTEXT and not in
     the target block. Cap at 1 if the answer's substance mainly comes from outside the target
     block.
   5 — Answer is taken directly from a single short contiguous span of the target block. Every word
     of the answer is explicitly present or is a trivial rewording of explicit content. No inference
     whatsoever. (Rare.)
   4 — Answer is fully supported but requires reading across two adjacent sentences, OR is from a
     single span with minor trivial rewording that a strict reader might flag.
   3 — Answer is grounded in the target block but requires one small, defensible inferential step —
     connecting a pronoun to its referent, combining a figure with its unit, or similar.
   2 — Answer is partially supported: some parts grounded in the target block, other parts not
     (including parts taken from a REFERENCED DOCUMENT or the DOCUMENT CONTEXT).
   1 — Answer requires significant inference, outside knowledge, or is not in the target block at
     all.
   CITATION RULE (UN): UN texts constantly cite other instruments ("the measures imposed by
     paragraph 20 of resolution 1493 (2003)"). If the answer's substance sits behind such a citation
     rather than in the target block's own words, score at most 2 (1 if the answer consists mainly
     of such content) — REGARDLESS of whether the cited document was supplied in the REFERENCED
     DOCUMENTS section. References exist for understanding, never as answer material.
   ATTRIBUTION RULE (UN): summary records report delegates' statements, letters convey a
     government's position, and reports state the reporting body's findings and estimates. If the
     target block attributes a claim, estimate, or assessment to a speaker or body and the answer
     (or the question it responds to) presents that claim as established fact with the attribution
     stripped, cap GROUNDING at 2 — the supplied text supports the attributed claim, not the bare
     assertion.

2. PRECISION (1–5): Does the answer add unsupported details or padding?
   5 — Answer is the shortest possible span that fully answers the question. Not one extra word. No
     surrounding context, no hedges, no elaboration. (Rare.)
   4 — Answer is grounded and tight but includes one short fragment of adjacent context that could
     have been cut.
   3 — Answer is grounded but includes one unsupported detail, generalization, or piece of padding.
   2 — Answer includes multiple unsupported details, or uses speculative framing ("likely,"
     "approximately," "it seems") where the passage is specific.
   1 — Answer is largely padded with content not in the passage, or is a rewrite rather than an
     extraction.

3. NUMERICAL & CITATIONAL FIDELITY (1–5): Are numbers, dates, amounts, and official identifiers
  reproduced exactly? (JSON key remains "numerical_fidelity".)
   5 — All numbers, dates, durations, monetary amounts, percentages, troop figures, and official
     identifiers (document symbols, resolution and paragraph numbers) match the passage
     character-for-character (e.g., "resolution 2374 (2017)" preserved as-is, not "Resolution 2374";
     "S/1994/565", not "S/1994/565/Rev.1"; "up to 5,500 troops", not "about 5,000 troops"; "within
     30 days", not "in about a month"). Dates rendered in the answer language's standard format
     count as exact if day, month, and year are unchanged ("15 July 1994" for "le 15 juillet 1994").
   4 — All values and identifiers are correct and preserved, but with a trivial formatting
     difference (e.g., "30-day period" vs. "within 30 days", or a spacing/punctuation variant of an
     identifier).
   3 — One number or date is rounded or approximated, one identifier is truncated (e.g., year
     dropped from a resolution number), or one duration is converted to a different unit.
   2 — Multiple values or identifiers rounded, reformatted, truncated, or partially dropped.
   1 — Numbers, dates, or identifiers invented, significantly changed, or contradicted by the
     passage.
   N/A — Answer contains no numerical or citational content. Score this sub-criterion as 5 if N/A.

Output valid JSON only — a list of three objects, one per candidate, in the order the candidates
  were provided (index 0, 1, 2):
[
  {
    "index": 0,
    "grounding": <1-5>,
    "precision": <1-5>,
    "numerical_fidelity": <1-5>,
    "reason": "one short sentence explaining the grades"
  },
  {
    "index": 1,
    "grounding": <1-5>,
    "precision": <1-5>,
    "numerical_fidelity": <1-5>,
    "reason": "..."
  },
  {
    "index": 2,
    "grounding": <1-5>,
    "precision": <1-5>,
    "numerical_fidelity": <1-5>,
    "reason": "..."
  }
]

ACTUAL BATCH SIZE: This request contains exactly 2 candidates. Return exactly 2 grade objects, using indices [0, 1]. Grade only supplied candidates. Any references above to THREE pairs or three example objects describe a typical batch; this actual batch size overrides those counts. All scoring criteria and calibration remain unchanged.
````

### Input 2: user

````text
### TARGET BLOCK — write the questions about THIS text

[EN] Document: A/RES/65/141
  Title: Resolution adopted by the General Assembly on 20 December 2010
12. Encourages the United Nations funds and programmes and the specialized agencies, within their respective mandates, to contribute to the implementation of the outcomes of the World Summit on the Information Society, and emphasizes the need for resources in this regard;
13. Notes the organization of the World Summit on the Information Society Forum 2010 by the International Telecommunication Union, the United Nations Conference on Trade and Development, the United Nations Development Programme and the United Nations Educational, Scientific and Cultural Organization to facilitate interaction among actors implementing the Summit's action lines, and invites organizers to fully engage Governments, international organizations, civil society and the private sector in the preparations for the World Summit on the Information Society Forum 2011, to be held in Geneva from 16 to 20 May 2011;
14. Recognizes the urgent need to harness the potential of knowledge and technology, and in this regard encourages the United Nations development system to continue its effort to promote the use of information and communications technologies as a critical enabler of development and a catalyst for the achievement of the internationally agreed development goals, including the Millennium Development Goals;

### REFERENCED DOCUMENTS — none. The target block cites no other document available in the corpus.

### DOCUMENT CONTEXT — surrounding text of the SAME document, supporting context only. It resolves what the target block leaves implicit; it is never a source of answers.

[EN] Document A/RES/65/141 — surrounding passages
Resolution adopted by the General Assembly on 20 December 2010
[on the report of the Second Committee (A/65/433)]
The General Assembly,
Recalling its resolutions 56/183 of 21 December 2001, 57/238 of 20 December 2002, 57/270 B of 23 June 2003, 59/220 of 22 December 2004, 60/252 of 27 March 2006, 62/182 of 19 December 2007, 63/202 of 19 December 2008 and 64/187 of 21 December 2009, Economic and Social Council resolutions 2006/46 of 28 July 2006, 2008/3 of 18 July 2008 and 2009/7 of 24 July 2009 and other relevant resolutions,
Taking note of Economic and Social Council resolution 2010/2 of 19 July 2010 on the assessment of the progress made in the implementation of and follow-up to the outcomes of the World Summit on the Information Society,
Noting that cultural diversity is the common heritage of humankind and that the information society should be founded on and stimulate respect for cultural identity, cultural and linguistic diversity, traditions and religions and foster dialogue among cultures and civilizations, and noting also that the promotion, affirmation and preservation of diverse cultural identities and languages as reflected in relevant agreed United Nations documents, including the Universal Declaration on Cultural Diversity of the United Nations Educational, Scientific and Cultural Organization, will further enrich the information society,

Recalling also the 2005 World Summit Outcome,
Recalling further the High-level Plenary Meeting of the General Assembly on the Millennium Development Goals and its outcome document,
Taking note of the report of the Secretary-General on progress made in the implementation of and follow-up to the outcomes of the World Summit on the Information Society at the regional and international levels,
Noting the establishment of the Broadband Commission for Digital Development at the invitation of the Secretary-General of the International Telecommunication Union and the Director-General of the United Nations Educational, Scientific and Cultural Organization, and taking note of the report of the Commission prepared in cooperation with the International Telecommunication Union and the United Nations Educational, Scientific and Cultural Organization entitled "A 2010 Leadership Imperative: The Future Built on Broadband", which calls for broadband-friendly practice and policies towards the attainment of the internationally agreed development goals, including the Millennium Development Goals, to ensure that the potential of broadband connectivity and content are at the service of development,

Taking note of the report of the Secretary-General on enhanced cooperation on public policy issues pertaining to the Internet, and recognizing the need to promote the participation of intergovernmental organizations from developing countries in future consultations,
Taking note also of the note by the Secretary-General on the continuation of the Internet Governance Forum,
Recognizing the role of the Commission on Science and Technology for Development in assisting the Economic and Social Council as the focal point in the system-wide follow-up, in particular the review and assessment of the progress made in implementing the outcomes of the World Summit on the Information Society, while at the same time maintaining its original mandate on science and technology for development,
Noting the thirteenth session of the Commission on Science and Technology for Development, held in Geneva from 17 to 21 May 2010,

Recognizing that, while in recent years considerable progress has been made in access to information and communications technologies, including the steady increase in Internet access to nearly one quarter of the world's population, the expanding penetration of cellular telephony and the availability of multilingual content and Internet addresses, the need remains to reduce the digital divide and to ensure that the benefits of new technologies, especially information and communications technologies, are available to all, and recognizing in this regard that less than 18 per cent of the population in developing countries uses the Internet, compared to more than 60 per cent in developed countries,
Reaffirming the need to harness the potential of information and communications technologies to promote the achievement of the internationally agreed development goals, including the Millennium Development Goals, and sustainable economic growth,
Expressing concern about the impact of the world financial and economic crisis on the positive trends in the diffusion of information and communications technology and the investment needed to ensure universal access to information and communications technologies,

Stressing the need to reduce the digital divide, including with regard to such issues as international interconnection charges for Internet use, and to ensure that the benefits of new technologies, especially information and communications technologies, are available to all,
Acknowledging that the Internet, a central element of the infrastructure of the information society, has evolved from a research and academic facility into a global facility available to the public,
Recognizing that the international management of the Internet should be multilateral, transparent and democratic, with the full involvement of Governments, the private sector, civil society and international organizations, as stated in paragraph 29 of the Tunis Agenda,
Recognizing also the importance of the Internet Governance Forum and its mandate as a forum for multi-stakeholder dialogue on various matters, including public policy issues related to key elements of Internet governance, in order to foster the sustainability, robustness, security, stability and development of the Internet, as well as its role in building partnerships among different stakeholders so as to help in addressing the various issues of Internet governance, while acknowledging the calls for improvements in its working methods,

Emphasizing the significance and urgency of the process towards enhanced cooperation in full consistency with the mandate provided in paragraph 71 of the Tunis Agenda and the need for enhanced cooperation to enable Governments on an equal footing to carry out their roles and responsibilities in respect of international public policy issues pertaining to the Internet but not in respect of the day-to-day technical and operational matters that do not impact upon those issues,
Recalling the consultations, at the fourth meeting of the Internet Governance Forum, held in Sharm elSheikh, Egypt, from 15 to 18 November 2009, on the future of the Forum, which generally welcomed the renewal of its mandate and recognized the need for further discussion on the improvement of its working methods,
Welcoming the efforts undertaken by the host countries in organizing the first, second, third, fourth and fifth meetings of the Internet Governance Forum, held in Athens in 2006, in Rio de Janeiro, Brazil, in 2007, in Hyderabad, India, in 2008, in Sharm elSheikh, Egypt, in 2009 and in Vilnius in 2010, respectively,

Noting the contribution of the Global Alliance for Information and Communications Technologies and Development to the work of the Commission on Science and Technology for Development,
Recognizing the pivotal role of the United Nations system in promoting development, including with respect to enhancing access to information and communications technologies, inter alia, through partnerships with all relevant stakeholders,
Welcoming, in view of the existing gaps in information and communications technologies infrastructure, the Connect Africa summits held in Kigali in 2007 and in Cairo in 2008, the Connect the Commonwealth of Independent States summit held in Minsk in 2009 and the meeting of Commonwealth countries held in Colombo in 2010, which are regional initiatives aimed at mobilizing human, financial and technical resources to accelerate the implementation of the connectivity goals of the World Summit on the Information Society,
1. Recognizes that information and communications technologies have the potential to provide new solutions to development challenges, particularly in the context of globalization, and can foster economic growth, competitiveness, access to information and knowledge, poverty eradication and social inclusion that will help to expedite the integration of all countries, especially developing countries, in particular the least developed countries, into the global economy;

2. Expresses concern regarding the digital divide in access to information and communications technology tools and broadband connectivity between countries at different levels of development, which affects many economically and socially relevant applications in areas such as government, business, health and education, and further expresses concern with regard to the special challenges faced in the area of broadband connectivity by developing countries, including the least developed countries, small island developing States and landlocked developing countries;
3. Acknowledges that a gender divide exists as part of the digital divide, and encourages all stakeholders to ensure the full participation of women in the information society and women's access to the new technologies, especially information and communications technologies for development;
4. Stresses that, for the majority of the poor, the development promise of science and technology, including information and communications technologies, remains unfulfilled, and emphasizes the need to effectively harness technology, including information and communications technologies, to bridge the digital divide;

5. Also stresses the important role of Governments in the design of public policies and in the provision of public services responsive to national needs and priorities through, inter alia, the effective use of information and communications technologies, including on the basis of a multi-stakeholder approach, to support national development efforts;
6. Recognizes that, in addition to financing by the public sector, financing of information and communications technologies infrastructure by the private sector has come to play an important role in many countries and that domestic financing is being augmented by North-South flows and South-South cooperation;
7. Also recognizes that information and communications technologies present new opportunities and challenges and that there is a pressing need to address the major impediments that developing countries face in accessing the new technologies, such as insufficient resources, infrastructure, education, capacity, investment and connectivity and issues related to technology ownership, standards and flows, and in this regard calls upon all stakeholders to provide adequate resources, enhanced capacity-building and technology transfer, on mutually agreed terms, to developing countries, particularly the least developed countries;

8. Further recognizes the immense potential that information and communications technologies have in promoting the transfer of technologies in a wide spectrum of socio-economic activity;
9. Recognizes that South-South and triangular cooperation can be useful tools for promoting the development of information and communications technologies;
10. Encourages strengthened and continuing cooperation between and among stakeholders to ensure the effective implementation of the outcomes of the Geneva2 and Tunis4 phases of the World Summit on the Information Society through, inter alia, the promotion of national, regional and international multi-stakeholder partnerships, including public-private partnerships, and the promotion of national and regional multi-stakeholder thematic platforms, in a joint effort and dialogue with developing and least developed countries, development partners and actors in the information and communications technologies sector;
11. Welcomes the efforts undertaken by Tunisia, host of the second phase of the World Summit on the Information Society in collaboration with the United Nations Conference on Trade and Development, the International Telecommunication Union and other relevant international and regional organizations, for organizing annually the ICT 4 All Forum and technological exhibition as a platform within the framework of the follow-up to the Summit to promote a dynamic business environment for the information and communications technologies sector worldwide;

[... the TARGET BLOCK appears here ...]

15. Also recognizes the role of the United Nations Group on the Information Society as an inter-agency mechanism of the United Nations System Chief Executives Board for Coordination designed to coordinate United Nations implementation of the outcomes of the World Summit on the Information Society;
16. Further recognizes that the Internet governance-related outcomes of the World Summit on the Information Society, namely the process towards enhanced cooperation and the convening of the Internet Governance Forum, are to be pursued by the Secretary-General through two distinct processes, and recognizes that the two processes may be complementary;
17. Decides to extend the mandate of the Internet Governance Forum for a further five years, and in this regard invites the Secretary-General to continue to convene the Forum for multi-stakeholder policy dialogue on Internet governance issues according to its mandate as set out in paragraph 72 of the Tunis Agenda for the Information Society,4 while at the same time recognizing the need to improve the Forum, with a view to linking it to the broader dialogue on global Internet governance;

18. Welcomes the decision of the Economic and Social Council, in paragraph 30 of its resolution 2010/2, to invite the Chair of the Commission on Science and Technology for Development to establish, in an open and inclusive manner, a working group which would seek, compile and review inputs from all Member States and all other stakeholders on improvements to the Internet Governance Forum, in line with the mandate set out in the Tunis Agenda, and would make recommendations, as appropriate, to the Commission at its fourteenth session, in 2011, in a report that would constitute an input from the Commission to the General Assembly, through the Council;
19. Stresses that the consideration of improvements to the Internet Governance Forum should be based on the inputs to be provided to the working group by all Member States and all other stakeholders, including those comments received during the online consultation and the consultation undertaken by the Under-Secretary-General for Economic and Social Affairs during the fourth meeting of the Forum, held in Sharm elSheikh, Egypt, in November 2009, with particular consideration for, inter alia, enhancing the participation of developing countries, exploring further voluntary options for financing the Forum and improving the modalities of the preparation process and the work and functioning of the secretariat of the Forum;

20. Decides that the desirability of the continuation of the Internet Governance Forum will be considered again by Member States in the General Assembly in the context of a ten-year review of the implementation of the outcome of the World Summit on the Information Society in 2015;
21. Stresses the need for the enhanced participation of developing countries, in particular the least developed countries, in all Internet Governance Forum meetings, and in this regard invites Member States, as well as other stakeholders, to support the participation of Governments and other stakeholders from developing countries in the Forum itself, as well as in the preparatory meetings;

22. Welcomes the decision of the Economic and Social Council, in paragraph 24 of its resolution 2010/2, to invite the Secretary-General to convene open and inclusive consultations involving all Member States and all other stakeholders with a view to assisting the process towards enhanced cooperation in order to enable Governments on an equal footing to carry out their roles and responsibilities in respect of international public policy issues pertaining to the Internet but not in respect of the day-to-day technical and operational matters that do not impact upon those issues, through a balanced participation of all stakeholders, especially developing countries, in their respective roles and responsibilities, as stated in paragraph 35 of the Tunis Agenda, requests the Secretary-General to submit to the General Assembly for consideration at its sixty-sixth session, through the Council, a report on the outcome of those consultations, and takes note of the invitation circulated by the Under-Secretary-General for Economic and Social Affairs to participate in the open consultations on enhanced cooperation on international public policy issues pertaining to the Internet;

23. Requests the Secretary-General to submit to the General Assembly at its sixty-sixth session, through the Commission on Science and Technology for Development and the Economic and Social Council, a report on the status of the implementation of and follow-up to the present resolution, as part of his annual reporting on the progress made in the implementation of and follow-up to the outcomes of the World Summit on the Information Society at the regional and international levels;
24. Decides to include in the provisional agenda of its sixty-sixth session the item entitled "Information and communications technologies for development". 69th plenary meeting

Candidate 0:
  Question: What dates were set for the World Summit on the Information Society Forum 2011 in the 2010 General Assembly resolution on follow-up to the World Summit on the Information Society?
  Answer: from 16 to 20 May 2011

Candidate 1:
  Question: Where was the World Summit on the Information Society Forum 2011 to be held under the 2010 General Assembly resolution on follow-up to the World Summit on the Information Society?
  Answer: Geneva
````

### Output: choice 0

Finish reason: `stop`.

````text
[
  {
    "index": 0,
    "grounding": 5,
    "precision": 5,
    "numerical_fidelity": 5,
    "reason": "The answer is a verbatim span from paragraph 13 ('from 16 to 20 May 2011'), with nothing extra and the dates exact."
  },
  {
    "index": 1,
    "grounding": 5,
    "precision": 5,
    "numerical_fidelity": 5,
    "reason": "The answer 'Geneva' is taken directly from paragraph 13 ('to be held in Geneva'), with no extra content; there are no numbers to misstate."
  }
]
````

### Recorded usage

````json
{
  "cached_tokens": 0,
  "completion_tokens": 214,
  "prompt_tokens": 8828,
  "provider_cost": 0.019796,
  "reasoning_tokens": 0
}
````

### Input size diagnostics

````json
{
  "input_characters": 28122,
  "context_capacity_exceeded": null
}
````

## Call 004: faithfulness

Request: `1feb1db4b69e4409b62087f97a26016c`. Task: `mode/un/2008/s/res/1826_2008_#5/semantic`.

Model: `anthropic/claude-sonnet-5.5`. UTC: 2026-09-30T17:52:21.028432+00:00.

API status: **response**. Duration: 3.769076 seconds.

### Request settings

````json
{
  "extra_body": {
    "thinking": {
      "budget_tokens": 16000,
      "type": "enabled"
    }
  },
  "max_tokens": 32000
}
````

### Input 1: system

````text
You are a strict faithfulness grader for legal and policy question-answer pairs built from United
  Nations documents.

You will receive a three-section context and THREE question-answer pairs.
The context is:
- "### TARGET BLOCK" — the passage the questions are supposed to be about, in one or more language
  versions.
- "### REFERENCED DOCUMENTS" — other documents CITED by the target block, each supplied as its
  symbol, title, and text — provided ONLY so the target block's citations can be understood, the way
  a footnote helps a reader.
- "### DOCUMENT CONTEXT" — surrounding text of the SAME document (its opening and neighbouring
  passages), supplied so that the target block can be understood: it resolves which mission "the
  Mission" is, which country "the Government" governs, what period a report covers, and similar
  referring expressions.
BOTH supporting sections are for UNDERSTANDING ONLY. Using them to resolve a referring expression in
  the question or answer (naming "the Mission" as UNAMIR, identifying what a cited resolution
  concerns) is legitimate and must NOT be penalised. Using either of them as a source of answer
  substance is a grounding failure — the answer's facts must come from the TARGET BLOCK itself,
  fully.

THREE question-answer pairs (questions may be in any language; each answer matches its question's
  language). Grade each pair on three sub-criteria, each 1–5. Do NOT evaluate query shape or
  retrieval quality — those are handled separately. Focus only on how faithfully each answer
  reflects the supplied text.

GRADING INSTRUCTIONS:
- Grade each of the three pairs independently and against the absolute rubric below — not relative
  to the other two.
- Do not let similarity or dissimilarity between the three pairs influence any individual grade.
- Evaluate each pair on its own merits before moving to the next.

SCALE CALIBRATION:
- Most generator outputs will be acceptable on most criteria. "Acceptable" is not the same as
  "excellent."
- 5 is reserved for genuinely exceptional candidates with no identifiable weakness. If you can point
  to any imperfection, it is not a 5. 5s should be uncommon.
- 4 means the candidate is very good but has exactly one minor, identifiable issue. You must be able
  to name the issue.
- 3 is the default grade for a candidate that is acceptable and does the job, with one clear
  weakness. It is not a punishment grade — most acceptable candidates will receive 3s.
- 2 and 1 are reserved for candidates with real, identifiable problems. Do not avoid using them when
  a candidate qualifies.
- Before assigning any 4 or 5, pause and ask: "What specifically makes this better than a 3?" If you
  cannot answer concretely, the grade is 3.

SUB-CRITERIA:

1. GROUNDING (1–5): Is the answer supported by a contiguous span of the TARGET BLOCK?
   The supporting text means the TARGET BLOCK alone. Resolving a referring expression through the
     REFERENCED DOCUMENTS, the DOCUMENT CONTEXT, or the metadata lines is legitimate disambiguation,
     not an inferential step. Anything more is.
   Cap the grade at 2 if any part of the answer's substance — a fact, figure, list, reason, or
     condition — is stated only in a REFERENCED DOCUMENT or only in the DOCUMENT CONTEXT and not in
     the target block. Cap at 1 if the answer's substance mainly comes from outside the target
     block.
   5 — Answer is taken directly from a single short contiguous span of the target block. Every word
     of the answer is explicitly present or is a trivial rewording of explicit content. No inference
     whatsoever. (Rare.)
   4 — Answer is fully supported but requires reading across two adjacent sentences, OR is from a
     single span with minor trivial rewording that a strict reader might flag.
   3 — Answer is grounded in the target block but requires one small, defensible inferential step —
     connecting a pronoun to its referent, combining a figure with its unit, or similar.
   2 — Answer is partially supported: some parts grounded in the target block, other parts not
     (including parts taken from a REFERENCED DOCUMENT or the DOCUMENT CONTEXT).
   1 — Answer requires significant inference, outside knowledge, or is not in the target block at
     all.
   CITATION RULE (UN): UN texts constantly cite other instruments ("the measures imposed by
     paragraph 20 of resolution 1493 (2003)"). If the answer's substance sits behind such a citation
     rather than in the target block's own words, score at most 2 (1 if the answer consists mainly
     of such content) — REGARDLESS of whether the cited document was supplied in the REFERENCED
     DOCUMENTS section. References exist for understanding, never as answer material.
   ATTRIBUTION RULE (UN): summary records report delegates' statements, letters convey a
     government's position, and reports state the reporting body's findings and estimates. If the
     target block attributes a claim, estimate, or assessment to a speaker or body and the answer
     (or the question it responds to) presents that claim as established fact with the attribution
     stripped, cap GROUNDING at 2 — the supplied text supports the attributed claim, not the bare
     assertion.

2. PRECISION (1–5): Does the answer add unsupported details or padding?
   5 — Answer is the shortest possible span that fully answers the question. Not one extra word. No
     surrounding context, no hedges, no elaboration. (Rare.)
   4 — Answer is grounded and tight but includes one short fragment of adjacent context that could
     have been cut.
   3 — Answer is grounded but includes one unsupported detail, generalization, or piece of padding.
   2 — Answer includes multiple unsupported details, or uses speculative framing ("likely,"
     "approximately," "it seems") where the passage is specific.
   1 — Answer is largely padded with content not in the passage, or is a rewrite rather than an
     extraction.

3. NUMERICAL & CITATIONAL FIDELITY (1–5): Are numbers, dates, amounts, and official identifiers
  reproduced exactly? (JSON key remains "numerical_fidelity".)
   5 — All numbers, dates, durations, monetary amounts, percentages, troop figures, and official
     identifiers (document symbols, resolution and paragraph numbers) match the passage
     character-for-character (e.g., "resolution 2374 (2017)" preserved as-is, not "Resolution 2374";
     "S/1994/565", not "S/1994/565/Rev.1"; "up to 5,500 troops", not "about 5,000 troops"; "within
     30 days", not "in about a month"). Dates rendered in the answer language's standard format
     count as exact if day, month, and year are unchanged ("15 July 1994" for "le 15 juillet 1994").
   4 — All values and identifiers are correct and preserved, but with a trivial formatting
     difference (e.g., "30-day period" vs. "within 30 days", or a spacing/punctuation variant of an
     identifier).
   3 — One number or date is rounded or approximated, one identifier is truncated (e.g., year
     dropped from a resolution number), or one duration is converted to a different unit.
   2 — Multiple values or identifiers rounded, reformatted, truncated, or partially dropped.
   1 — Numbers, dates, or identifiers invented, significantly changed, or contradicted by the
     passage.
   N/A — Answer contains no numerical or citational content. Score this sub-criterion as 5 if N/A.

Output valid JSON only — a list of three objects, one per candidate, in the order the candidates
  were provided (index 0, 1, 2):
[
  {
    "index": 0,
    "grounding": <1-5>,
    "precision": <1-5>,
    "numerical_fidelity": <1-5>,
    "reason": "one short sentence explaining the grades"
  },
  {
    "index": 1,
    "grounding": <1-5>,
    "precision": <1-5>,
    "numerical_fidelity": <1-5>,
    "reason": "..."
  },
  {
    "index": 2,
    "grounding": <1-5>,
    "precision": <1-5>,
    "numerical_fidelity": <1-5>,
    "reason": "..."
  }
]

ACTUAL BATCH SIZE: This request contains exactly 2 candidates. Return exactly 2 grade objects, using indices [0, 1]. Grade only supplied candidates. Any references above to THREE pairs or three example objects describe a typical batch; this actual batch size overrides those counts. All scoring criteria and calibration remain unchanged.
````

### Input 2: user

````text
### TARGET BLOCK — write the questions about THIS text

[EN] Document: S/RES/1826(2008)
  Title: Resolution 1826 (2008)
8. Invites the signatories of the Ouagadougou political Agreement to take the necessary steps to protect vulnerable civilian populations, including by guaranteeing the voluntary return, reinstallation, reintegration and security of displaced persons, with the support of the United Nations system, and to fulfil in this regard their commitments in accordance with the Ouagadougou political Agreement and their obligations under international humanitarian law;
9. Expresses its intention to review by 31 January 2009 the mandates of UNOCI and the French forces which support it, as well as the level of troops of UNOCI, in the light of the progress achieved in the implementation of the key steps of the peace process and of the progress of the electoral process, and requests the Secretary-General to provide to it a report in this regard three weeks before this date, including some benchmarks for a possible phased drawdown of the troop levels of UNOCI, taking into consideration the electoral process and the situation on the ground and in particular the security conditions;

### REFERENCED DOCUMENTS — none. The target block cites no other document available in the corpus.

### DOCUMENT CONTEXT — surrounding text of the SAME document, supporting context only. It resolves what the target block leaves implicit; it is never a source of answers.

[EN] Document S/RES/1826(2008) — surrounding passages
Resolution 1826 (2008)
Adopted by the Security Council at its 5945th meeting, on 29 July 2008
The Security Council,
Recalling its previous resolutions, in particular resolutions 1739 (2007), 1765 (2007) and 1795 (2008), and the statements of its President relating to the situation in Côte d'Ivoire, and resolution 1777 (2007) on the situation in Liberia,
Reaffirming its strong commitment to the sovereignty, independence, territorial integrity and unity of Côte d'Ivoire, and recalling the importance of the principles of good-neighbourliness, non-interference and regional cooperation,
Recalling that it endorsed the Agreement signed by President Laurent Gbagbo and Mr. Guillaume Soro in Ouagadougou on 4 March 2007 ("the Ouagadougou political Agreement" S/2007/144), and the following Supplementary Agreements, as recommended by the African Union,
Recalling that it welcomed the announcement by the Ivorian authorities of the organization on 30 November 2008 of the first round of the presidential elections (S/PRST/2008/11) and that it encouraged the Ivorian parties to redouble their efforts to meet this commitment, and the international community to bring continued support to this effect,

Expressing again its appreciation to President Blaise Compaoré of Burkina Faso ("the Facilitator") for his continued efforts to support the peace process in Côte d'Ivoire, in particular through the Ouagadougou Political Agreement follow-up mechanisms, commending and encouraging the continued efforts of the African Union and the Economic Community of West African States ("ECOWAS") to promote peace and stability in Côte d'Ivoire, and reiterating its full support for them,
Stressing again the importance of the international consultative organ participating in the meetings of the evaluation and monitoring committee, as an observer, and recalling that it may be consulted at any time by the Facilitator,
Reiterating its strong condemnation of any attempt to destabilize the peace process by force, and expressing its intention to examine without delay the situation after any such attempt, on the basis of a report by the Secretary-General,
Having taken note of the report of the Secretary-General dated 10 July 2008 (S/2008/451),

Noting with concern, in spite of the sustained improvement of the overall human rights situation, the persistence of cases of human rights violations against civilians, including numerous acts of sexual violence, stressing that the perpetrators must be brought to justice, and reiterating its firm condemnation of all violations of human rights and international humanitarian law in Côte d'Ivoire,
Recalling its resolution 1612 (2005) on children and armed conflict and the subsequent conclusions of the Security Council Working Group on Children and Armed Conflict pertaining to parties in the armed conflict of Côte d'Ivoire (S/AC.51/2008/5),
Recalling also its resolutions 1325 (2000) and 1820 (2008) on women, peace and security, and its resolution 1674 (2006) on the protection of civilians in armed conflict, condemning any sexual violence and encouraging the Secretary-General to mainstream a gender perspective in the implementation of UNOCI's mandate,
Emphasizing the importance of the continuing support of the United Nations system and the international community for strengthening the capacity of the Government of Côte d'Ivoire and of the electoral bodies to organize the electoral process,

Determining that the situation in Côte d'Ivoire continues to pose a threat to international peace and security in the region,
Acting under Chapter VII of the Charter of the United Nations,
1. Decides to renew the mandates of the United Nations Operation in Côte d'Ivoire (UNOCI) and of the French forces which support it, as determined in resolution 1739 (2007), until 31 January 2009, in particular to support the organization in Côte d'Ivoire of free, open, fair and transparent elections;
2. Requests UNOCI, within its existing resources and mandate, to support the full implementation of the Ouagadougou political Agreement and its Supplementary Agreements, and in particular to contribute to bringing the security needed by the peace process and by the electoral process and to provide logistical support to the Independent Electoral Commission for the preparation and the holding of the elections;
3. Strongly encourages the Defense and Security Force of Côte d'Ivoire and the Forces nouvelles to jointly develop a comprehensive plan for the security of the elections, in close coordination with the Facilitator, with the technical and logistical support of UNOCI which is supported by the French forces;

4. Encourages the Ivorian parties to make further concrete progress, in particular in removing the remaining logistical obstacles that impede the identification of the population, the registration of voters, the disarmament and dismantling of militias, the cantonment and disarmament, demobilization and reintegration programme, the unification and restructuring of defence and security forces and the restoration of State authority throughout the country;
5. Urges the political parties to comply fully with the Code of Good Conduct for elections which they signed under the auspices of the Secretary-General, and in particular urges the Ivorian authorities to allow equitable access to public media;
6. Calls upon all concerned parties to ensure that the protection of women and children is addressed in the implementation of the Ouagadougou political Agreement as well as the post-conflict reconstruction and recovery phases, including continued monitoring and reporting of the situation of women and children;
7. Stresses the importance of ensuring the equal protection of and respect for human rights of every Ivorian as they relate to the electoral system, and in particular of removing obstacles and challenges to women's participation and full involvement in public life;

[... the TARGET BLOCK appears here ...]

10. Reiterates its full support to the efforts of the Special Representative of the Secretary-General in Côte d'Ivoire, recalls that he shall certify that all stages of the electoral process provide all the necessary guarantees for the holding of open, free, fair and transparent presidential and legislative elections in accordance with international standards and reaffirms its support to the five-criteria framework elaborated by the Special Representative and referred to in document S/2008/250;
11. Recalls that the publication of the electoral list is a crucial step in the electoral process, calls upon the Independent Electoral Commission, the technical operators, the authorities of Côte d'Ivoire and the political parties to redouble their efforts in this regard and requests the Special Representative of the Secretary-General to certify it explicitly;
12. Welcomes the financial assistance provided by donors to the Independent Electoral Commission, which made it possible to finance the electoral process;
13. Calls upon the donors to increase in particular their financial support to the cantonment, disarmament and reintegration of former combatants and militia and to the redeployment of State administration throughout the country;

14. Commends the Representative of the Secretary-General for his efforts to facilitate the reinsertion of former combatants through the launching of one thousand micro projects, and encourages donors to contribute to their financing;
15. Requests the Secretary-General to continue to take the necessary measures to ensure full compliance in UNOCI with the United Nations zero-tolerance policy on sexual exploitation and abuses and to keep the Council informed, and urges troop-contributing countries to take appropriate preventive action including predeployment awareness training, and other action to ensure full accountability in cases of such conduct involving their personnel;
16. Recalls the importance of the provisions of the Ouagadougou political Agreement and of the Supplementary Agreements, including paragraph 8.1 of the Ouagadougou political Agreement and paragraphs 8 and 9 of Supplementary Agreement number 3, and urges the Ivorian political forces to rely on the mediation by the Facilitator, for any major difficulty concerning the electoral process;

17. Commends the Facilitator for continuing to support the process to settle the crisis in Côte d'Ivoire, and requests UNOCI to continue to assist him and his Special Representative in Abidjan, Mr. Boureima Badini, in the conduct of the facilitation, including by helping the Facilitator, as appropriate and upon his request, to carry out his arbitration role according to the provisions of paragraph 8.1 of the Ouagadougou political Agreement and paragraphs 8 and 9 of Supplementary Agreement number 3;
18. Requests the Secretary-General to keep it regularly informed of the situation and of the preparation of the electoral process, including the process of the establishment of the electoral list, and notably by providing to it a report in this regard no later than 15 October 2008;
19. Decides to remain actively seized of the matter.

Candidate 0:
  Question: How were vulnerable civilians and displaced people to be protected under the Ouagadougou political Agreement in 2008?
  Answer: take the necessary steps to protect vulnerable civilian populations, including by guaranteeing the voluntary return, reinstallation, reintegration and security of displaced persons, with the support of the United Nations system

Candidate 1:
  Question: How was a possible UNOCI drawdown to be assessed as Côte d’Ivoire’s peace and electoral processes advanced in 2008?
  Answer: review by 31 January 2009 the mandates of UNOCI and the French forces which support it, as well as the level of troops of UNOCI, in the light of the progress achieved in the implementation of the key steps of the peace process and of the progress of the electoral process, and requests the Secretary-General to provide to it a report in this regard three weeks before this date, including some benchmarks for a possible phased drawdown of the troop levels of UNOCI, taking into consideration the electoral process and the situation on the ground and in particular the security conditions
````

### Output: choice 0

Finish reason: `stop`.

````text
[
  {
    "index": 0,
    "grounding": 4,
    "precision": 4,
    "numerical_fidelity": 5,
    "reason": "The answer is a verbatim span of paragraph 8 and fully supported. It omits the signatories' obligations under the Agreement and international humanitarian law, and the question's framing ('under the Agreement') is slightly loose. It also adds nothing extra, but includes the 'with the support of the UN system' fragment, which is minor."
  },
  {
    "index": 1,
    "grounding": 4,
    "precision": 4,
    "numerical_fidelity": 5,
    "reason": "The answer is a near-verbatim span of paragraph 9 with the dates and durations exact. It is long and includes the review of mandates, which goes slightly beyond the drawdown assessment the question asks about."
  }
]
````

### Recorded usage

````json
{
  "cached_tokens": 0,
  "completion_tokens": 287,
  "prompt_tokens": 6756,
  "provider_cost": 0.016382,
  "reasoning_tokens": 0
}
````

### Input size diagnostics

````json
{
  "input_characters": 20062,
  "context_capacity_exceeded": null
}
````

## Call 005: faithfulness

Request: `0a0e5fdfaa73451c94939f92a0fe3960`. Task: `mode/un/1999/a/c_3/54/sr_31#11/lookup`.

Model: `anthropic/claude-sonnet-5.5`. UTC: 2026-09-30T17:53:17.089417+00:00.

API status: **response**. Duration: 3.727171 seconds.

### Request settings

````json
{
  "extra_body": {
    "thinking": {
      "budget_tokens": 16000,
      "type": "enabled"
    }
  },
  "max_tokens": 32000
}
````

### Input 1: system

````text
You are a strict faithfulness grader for legal and policy question-answer pairs built from United
  Nations documents.

You will receive a three-section context and THREE question-answer pairs.
The context is:
- "### TARGET BLOCK" — the passage the questions are supposed to be about, in one or more language
  versions.
- "### REFERENCED DOCUMENTS" — other documents CITED by the target block, each supplied as its
  symbol, title, and text — provided ONLY so the target block's citations can be understood, the way
  a footnote helps a reader.
- "### DOCUMENT CONTEXT" — surrounding text of the SAME document (its opening and neighbouring
  passages), supplied so that the target block can be understood: it resolves which mission "the
  Mission" is, which country "the Government" governs, what period a report covers, and similar
  referring expressions.
BOTH supporting sections are for UNDERSTANDING ONLY. Using them to resolve a referring expression in
  the question or answer (naming "the Mission" as UNAMIR, identifying what a cited resolution
  concerns) is legitimate and must NOT be penalised. Using either of them as a source of answer
  substance is a grounding failure — the answer's facts must come from the TARGET BLOCK itself,
  fully.

THREE question-answer pairs (questions may be in any language; each answer matches its question's
  language). Grade each pair on three sub-criteria, each 1–5. Do NOT evaluate query shape or
  retrieval quality — those are handled separately. Focus only on how faithfully each answer
  reflects the supplied text.

GRADING INSTRUCTIONS:
- Grade each of the three pairs independently and against the absolute rubric below — not relative
  to the other two.
- Do not let similarity or dissimilarity between the three pairs influence any individual grade.
- Evaluate each pair on its own merits before moving to the next.

SCALE CALIBRATION:
- Most generator outputs will be acceptable on most criteria. "Acceptable" is not the same as
  "excellent."
- 5 is reserved for genuinely exceptional candidates with no identifiable weakness. If you can point
  to any imperfection, it is not a 5. 5s should be uncommon.
- 4 means the candidate is very good but has exactly one minor, identifiable issue. You must be able
  to name the issue.
- 3 is the default grade for a candidate that is acceptable and does the job, with one clear
  weakness. It is not a punishment grade — most acceptable candidates will receive 3s.
- 2 and 1 are reserved for candidates with real, identifiable problems. Do not avoid using them when
  a candidate qualifies.
- Before assigning any 4 or 5, pause and ask: "What specifically makes this better than a 3?" If you
  cannot answer concretely, the grade is 3.

SUB-CRITERIA:

1. GROUNDING (1–5): Is the answer supported by a contiguous span of the TARGET BLOCK?
   The supporting text means the TARGET BLOCK alone. Resolving a referring expression through the
     REFERENCED DOCUMENTS, the DOCUMENT CONTEXT, or the metadata lines is legitimate disambiguation,
     not an inferential step. Anything more is.
   Cap the grade at 2 if any part of the answer's substance — a fact, figure, list, reason, or
     condition — is stated only in a REFERENCED DOCUMENT or only in the DOCUMENT CONTEXT and not in
     the target block. Cap at 1 if the answer's substance mainly comes from outside the target
     block.
   5 — Answer is taken directly from a single short contiguous span of the target block. Every word
     of the answer is explicitly present or is a trivial rewording of explicit content. No inference
     whatsoever. (Rare.)
   4 — Answer is fully supported but requires reading across two adjacent sentences, OR is from a
     single span with minor trivial rewording that a strict reader might flag.
   3 — Answer is grounded in the target block but requires one small, defensible inferential step —
     connecting a pronoun to its referent, combining a figure with its unit, or similar.
   2 — Answer is partially supported: some parts grounded in the target block, other parts not
     (including parts taken from a REFERENCED DOCUMENT or the DOCUMENT CONTEXT).
   1 — Answer requires significant inference, outside knowledge, or is not in the target block at
     all.
   CITATION RULE (UN): UN texts constantly cite other instruments ("the measures imposed by
     paragraph 20 of resolution 1493 (2003)"). If the answer's substance sits behind such a citation
     rather than in the target block's own words, score at most 2 (1 if the answer consists mainly
     of such content) — REGARDLESS of whether the cited document was supplied in the REFERENCED
     DOCUMENTS section. References exist for understanding, never as answer material.
   ATTRIBUTION RULE (UN): summary records report delegates' statements, letters convey a
     government's position, and reports state the reporting body's findings and estimates. If the
     target block attributes a claim, estimate, or assessment to a speaker or body and the answer
     (or the question it responds to) presents that claim as established fact with the attribution
     stripped, cap GROUNDING at 2 — the supplied text supports the attributed claim, not the bare
     assertion.

2. PRECISION (1–5): Does the answer add unsupported details or padding?
   5 — Answer is the shortest possible span that fully answers the question. Not one extra word. No
     surrounding context, no hedges, no elaboration. (Rare.)
   4 — Answer is grounded and tight but includes one short fragment of adjacent context that could
     have been cut.
   3 — Answer is grounded but includes one unsupported detail, generalization, or piece of padding.
   2 — Answer includes multiple unsupported details, or uses speculative framing ("likely,"
     "approximately," "it seems") where the passage is specific.
   1 — Answer is largely padded with content not in the passage, or is a rewrite rather than an
     extraction.

3. NUMERICAL & CITATIONAL FIDELITY (1–5): Are numbers, dates, amounts, and official identifiers
  reproduced exactly? (JSON key remains "numerical_fidelity".)
   5 — All numbers, dates, durations, monetary amounts, percentages, troop figures, and official
     identifiers (document symbols, resolution and paragraph numbers) match the passage
     character-for-character (e.g., "resolution 2374 (2017)" preserved as-is, not "Resolution 2374";
     "S/1994/565", not "S/1994/565/Rev.1"; "up to 5,500 troops", not "about 5,000 troops"; "within
     30 days", not "in about a month"). Dates rendered in the answer language's standard format
     count as exact if day, month, and year are unchanged ("15 July 1994" for "le 15 juillet 1994").
   4 — All values and identifiers are correct and preserved, but with a trivial formatting
     difference (e.g., "30-day period" vs. "within 30 days", or a spacing/punctuation variant of an
     identifier).
   3 — One number or date is rounded or approximated, one identifier is truncated (e.g., year
     dropped from a resolution number), or one duration is converted to a different unit.
   2 — Multiple values or identifiers rounded, reformatted, truncated, or partially dropped.
   1 — Numbers, dates, or identifiers invented, significantly changed, or contradicted by the
     passage.
   N/A — Answer contains no numerical or citational content. Score this sub-criterion as 5 if N/A.

Output valid JSON only — a list of three objects, one per candidate, in the order the candidates
  were provided (index 0, 1, 2):
[
  {
    "index": 0,
    "grounding": <1-5>,
    "precision": <1-5>,
    "numerical_fidelity": <1-5>,
    "reason": "one short sentence explaining the grades"
  },
  {
    "index": 1,
    "grounding": <1-5>,
    "precision": <1-5>,
    "numerical_fidelity": <1-5>,
    "reason": "..."
  },
  {
    "index": 2,
    "grounding": <1-5>,
    "precision": <1-5>,
    "numerical_fidelity": <1-5>,
    "reason": "..."
  }
]

ACTUAL BATCH SIZE: This request contains exactly 2 candidates. Return exactly 2 grade objects, using indices [0, 1]. Grade only supplied candidates. Any references above to THREE pairs or three example objects describe a typical batch; this actual batch size overrides those counts. All scoring criteria and calibration remain unchanged.
````

### Input 2: user

````text
### TARGET BLOCK — write the questions about THIS text

[EN] Document: A/C.3/54/SR.31
  Title: (a) Implementation of human rights instruments (continued)
In exercise of its sovereign right, the United Republic of Tanzania had chosen to retain it because it served a useful purpose, although it was resorted to very sparingly.
If some States sought to impose on others a particular regime of laws, that would be tantamount to interference in their internal affairs and, in some cases, would ignore their religious traditions.
19. The United Republic of Tanzania respected the sovereign decision of those countries which had abolished the death penalty and proposed its elimination, but it believed that they should respect the decision of those countries which had chosen to retain it.
The real issue was not the death penalty, but whether States had the right to promulgate the kind of laws best suited to the needs of their societies.
In the view of her delegation, States had that right, which was established in the Charter of the United Nations and was one of the foundations of international law.
In order to respect the various choices countries had made, the European Union should withdraw the draft resolution on the death penalty, which only served to polarize the issue and undermine the smooth functioning of the Committee.

### REFERENCED DOCUMENTS — none. The target block cites no other document available in the corpus.

### DOCUMENT CONTEXT — surrounding text of the SAME document, supporting context only. It resolves what the target block leaves implicit; it is never a source of answers.

[EN] Document A/C.3/54/SR.31 — surrounding passages
(a) Implementation of human rights instruments (continued)

Draft resolution A/C.3/54/L.18/Rev.1: Violence against women migrant workers
1. Ms. Ramiro Lopez (Philippines) said that Belgium, Burkina Faso, Cape Verde, Colombia, Congo, Costa Rica, El Salvador, Ghana, Haiti, Indonesia, Ireland, Kenya, Liberia, Malawi, Mali, Morocco, Nicaragua, Pakistan, Paraguay, the former Yugoslav Republic of Macedonia and Togo had become sponsors of the draft resolution.
She hoped that it would be adopted by consensus.
2. The Chairman said that if he heard no objection, he would take it that the Committee wished to adopt draft resolution A/C.3/54/L.18/Rev.1.
3. Draft resolution A/C.3/54/L.18/Rev.1 was adopted.
(a) Implementation of human rights instruments (continued) (A/54/40, A/54/44, A/54/56, A/54/65, A/54/80, A/54/91, A/54/98, A/54/177, A/54/189, A/54/277, A/54/346, A/54/348, A/54/368, A/54/387 and A/54/426; A/C.3/54/5; A/C.3/54/L.8, A/C.3/54/L.31 and A/C.3/54/L.32)
4. Ms. Ramiro Lopez (Philippines) said that her Government could not support any resolution that called for the progressive abolition of the death penalty or for the establishment of a moratorium on executions.
The International Covenant on Civil and Political Rights established the manner in which the death penalty should be imposed in a criminal justice system and a democratic civil society.

As a State party to that Covenant, the Philippines imposed the death penalty only for heinous crimes and with full respect for due process and with safeguards for the rights of the accused, including the right to seek clemency or commutation of the sentence.
Furthermore, the Philippines did not impose the death penalty on anyone under the age of 18; it had set extremely strict requirements for the imposition of that penalty; and it ensured that only the most humane procedures were employed in carrying out the sentence.
It had established a Presidential Committee which reviewed the cases of those sentenced to death and the Constitution empowered the President to pardon individuals sentenced to death or to commute their sentences, a prerogative which he had used on four occasions.
5. While it was important to respect the opposition of other delegations to the death penalty and their right to seek its abolition, it was unfair for some States to impose their will on others.
Her delegation considered that a balance must be found between humanitarian concerns and the need for social justice; it therefore maintained its position, which reflected the sovereign will of the people of the Philippines.

6. Mr. Al-Dosari (Bahrain) said that in his country the death penalty was imposed only for the most serious crimes, such as murder, illicit drug trafficking and kidnapping.
The abolition of the death penalty would have serious consequences since its inclusion in a country's criminal code was a product of both the culture and the legal tradition of individual societies.
The death penalty could be abolished only under certain conditions, which were not the same in all countries, and, since it was an internal matter, it should not be subject to any outside interference.
It was also necessary to achieve a balance between the rights of victims, those of society and the interests of justice.
His Government considered that the death penalty was not a violation of human rights, but rather an effective means of protecting them and of guaranteeing respect for humanity and justice.
7. Mr. Donigi (Papua New Guinea) said that he endorsed the amendments proposed by the representative of Egypt to draft resolution A/C.3/54/L.8, which had been sponsored by some 80 Member States and appeared in documents A/C.3/54/L.31 and A/C.3/54/L.32.

8. The question of punishment was closely linked to issues such as the purpose and supremacy of law and the need to guarantee security and provide a deterrent against criminal conduct.
Therefore, any resolution dealing with the right to life must include a reference to the principle set forth in Article 2, paragraph 7, of the Charter of the United Nations. Otherwise a precedent would be set that might lead to an era in which States would be subject to the whims of a super-State or institution.
The international community must move with certainty, and the only certainty on the issue at hand was that an effort was being made to impose regulations on Member States and their institutions of government.
9. There had been a major outcry among the citizens of Western nations concerning the imposition of the death penalty in developing countries. Travellers entering a State must be aware that they would be bound by its laws; equality before the law was a basic democratic principle.
His country's domestic legislation was based on the right to freedom and, under the Constitution, everyone was free to do anything that did not interfere with the freedom of others.
An individual's freedom therefore also created obligations.

The death penalty was not in itself inconsistent with the freedoms guaranteed by the Constitution of Papua New Guinea; in fact, it strengthened them and provided a deterrent that protected them.
Any resolution which required the Parliament of Papua New Guinea to change its laws regarding the death penalty would constitute interference in the freedom, independence and discretion of the parliamentarians to promulgate such laws.
Because the imposition of the death penalty in Papua New Guinea was left to the discretion of the judge, the draft resolution also constituted interference with the functions of the judiciary since the Supreme Court of Papua New Guinea was the only body competent to strike down legislation enacted by Parliament.
His Government therefore opposed, and would continue to oppose, any move to impose such regulations on its highest legislative body or to limit the discretionary powers of its judiciary.
The international community should strive to attain universal ratification of, and strict compliance with, those instruments, a process that would entail an increasing need for control mechanisms.
His Government welcomed the opportunity for dialogue with the human rights treaty bodies and the Special Rapporteurs since it was of great assistance in promoting the implementation of those instruments at the national level.

11. In order to ensure the more effective implementation of human rights instruments, the Constitution of Slovakia established that the international conventions to which the State had acceded took precedence over national legislation. On 22 June 1999, the Slovak Republic had ratified the Second Optional Protocol to the International Covenant on Civil and Political Rights, aiming at the abolition of the death penalty.
International organizations had a very important role to play, and close cooperation between States parties and international organizations, both intergovernmental and non-governmental, was of paramount importance.
The creation of an effective mechanism to ensure respect for human rights was a function of the need to respond rapidly and adequately to violations of such rights, particularly those of children and other vulnerable groups.
That would require new standards, and his Government was following closely, and taking part in, the elaboration of the optional protocols to the Convention on the Rights of the Child.

12. Mr. Al-Absi (United Arab Emirates) said that the death penalty was one of the major issues on which States had a right to decide, bearing in mind the beliefs of their people and their sovereign right to choose a social system and model.
The death penalty was authorized under the legislation of many countries, including the United Arab Emirates, not by chance, but as a result of religious beliefs.
It was the product of a legal system that was centuries old and had stood up to the passage of time, and it provided a deterrent against murder and made it possible to limit the spread of social scourges to which the developing countries were particularly vulnerable, including vengeance and the temptation for people to take justice into their own hands, leading to a breakdown in society and fanning hatred and intolerance.
13. His Government respected the right of sovereign States to determine the legislation that governed the lives of their citizens, but it was opposed to some countries' claims to hegemony and efforts to interfere on the pretext of protecting human rights.
Furthermore, the International Covenant on Civil and Political Rights authorized the application of the death penalty in certain circumstances.

The legal system of the United Arab Emirates was based on Islamic law and on the values, standards, and virtues of human justice.
Although the death penalty was permitted by law, it was imposed only on rare occasions and by the Emir's decree. Justice was administered to all, equally and without exception.
14. Mr. Jemat (Brunei Darussalam) said that his country would have preferred that the question of the death penalty had been considered in a more balanced manner.
That issue had always been approached from the perspective of human rights, but focusing more on the right to life of the convicted person than on the rights of the victims and the community.
The issue touched on the sovereign right of a country to establish its own judicial system.
States had the right to impose the death penalty for the most serious crimes, in order to protect the country's peace and security, as stipulated in article 6, paragraph 2, of the International Covenant on Civil and Political Rights.

15. The system of capital punishment had long been used in Brunei Darussalam as a preventive mechanism and to punish very serious crimes, such as premeditated murder and drug trafficking.
The system had managed to contain serious crime and maintain peace and harmony in the country, and the death penalty would therefore be upheld as a necessary component of the judicial system.
Any change in a country's judicial system should be made in accordance with the will of the people; Brunei Darussalam would vote against the draft resolution on the death penalty.
16. Mr. Ferguson (Bahamas) said that the debate on the death penalty thus far clearly showed that there was no international consensus on the issue.
Many representatives had expressed their Governments' respect for the right of those countries which had abolished the death penalty to do so, as well as their understanding of the motivation for the call for others to do likewise.
However, they had also underscored that there should be equal respect and understanding for those countries which retained the death penalty.

The Bahamas recognized the sovereign and inalienable right of a State to determine the best way to maintain internal order and stability, and it retained the death penalty as one of the means of achieving those objectives, consistent with internationally agreed principles of good governance.
That sentence was, however, imposed only for the most serious offences and after due process of law.
17. It was inappropriate to introduce in a forum such as the Committee an issue as divisive as the abolition of the death penalty, not for a balanced exchange of views, but to seek to force countries to agree to its abolition.
Such action threatened the very principles on which the Organization had been established.
18. Ms. Kapalata (United Republic of Tanzania) said that the question of the death penalty should be considered under agenda item 107, "Crime prevention and criminal justice", as it was more closely related to that topic than to human rights.
The death penalty was useful as a means of curbing impunity.
International law provided for its use in special circumstances, and the International Covenant on Civil and Political Rights recognized the right of States to impose it.

[... the TARGET BLOCK appears here ...]

20. Mr. Shobokshi (Saudi Arabia) said that Islam, as a revealed religion, clearly guaranteed human rights, and that the Constitution of Saudi Arabia, which was immutable and based on the Koran, structured the lives of the people according to religious principles which established their duties and responsibilities.
Human life was a gift of God, and therefore no person could destroy it. That right was granted exclusively to the State, which could exercise it to protect society.
The Koran stated that whoever killed a human being without a reason deserved divine punishment.
It was impossible to say that it was a violation of human rights to follow a divine commandment.
21. The draft resolution submitted by Finland on behalf of the European Union showed that it had fallen into a trap.
The right of a victim to justice, in other words the need to impose a penalty commensurate with the crime, was a human right.
The human right which should be borne in mind was the right of society to security and to enjoy protection against such offences as murder, drug trafficking, terrorism and other heinous crimes.
Capital punishment and other severe penalties had no relationship to human rights and should be considered under the heading of crime prevention.

To abolish the death penalty or reduce its application would in practice deprive Governments of a means of meting out justice.
The international community was composed of sovereign States with different cultures, traditions and religions on which they based the measures they considered necessary for the protection of society.
International law recognized that capital punishment was a legitimate penalty which they could impose in accordance with their internal laws and in exercise of their sovereignty.
Article 6 of the International Covenant on Civil and Political Rights stipulated that, in accordance with its laws, a country could impose the death penalty for the most serious crimes.
22. The fact that some countries had signed treaties intended to abolish the death penalty did not mean that those instruments, including the second Optional Protocol to the Covenant, on the abolition of the death penalty, should be imposed on all Member States.
The countries of the European Union, like others, had the sovereign right to abolish the death penalty and also to retain it. But they did not have the right to impose their standards on other countries.
Certain values were universal, but others, for cultural or religious reasons, were not. Values could not be exported.
Societies adopted them if they were useful and did not contradict their cultural and religious traditions.

The diversity of the values which prevailed in each society should be respected.
It was to be hoped that, at the beginning of a new century marked by major changes, greater cooperation among States could be achieved on a basis of peace, equality, and brotherhood, and on respect for the values and traditions of all nations.
The European Union should therefore withdraw the draft resolution, in order to avoid confrontation and division and to maintain consensus.
23. Mr. Ajewole (Nigeria) said that his delegation recognized the importance of United Nations human rights treaty bodies and the work of the Organization in the promotion and protection of human rights, of which Nigeria had recently been a beneficiary through the participation of a United Nations monitoring team in the elections that had ushered in the current democratic Government.
Since independence, Nigeria's laws contained explicit provisions for the protection of fundamental human rights, which were in total accord with the Universal Declaration of Human Rights.
In October 1993, his country had acceded to the two major human rights instruments, the International Covenant on Economic, Social and Cultural Rights and the International Covenant on Civil and Political Rights and had accordingly established an independent National Commission on Human Rights.

Since the current democratic Government had taken over, concrete measures had been taken to investigate past human rights violations, all political prisoners had been released and appropriate judicial processes had been put into place to bring perpetrators of human rights abuses to justice.
Equal attention must be paid to all aspects of human rights, civil and political as well as social, economic and cultural.
In Nigeria, poverty, unemployment and inadequate funding were limitations on development, and the Government had therefore taken steps to improve the living standards of the people.
Furthermore, as a signatory to the Convention against Torture and Other Cruel, Inhuman or Degrading Treatment or Punishment, his country was committed to the total eradication of torture and other related practices, and had repealed all decrees that infringed on human rights.
24. The death penalty was essentially a matter of criminal justice and not a human rights issue; it was part of the policies applied by each State for the punishment of the most serious crimes which frequently reflected its values and culture.
The death penalty existed in Nigeria, but it was applied only after due process of law.
The rights of victims and of the community must be protected, and deprivation of life necessitated an appropriate penalty.

Candidate 0:
  Question: In 1999, what did Tanzania ask the European Union to do in the 1999 Third Committee meeting record on the death penalty?
  Answer: withdraw the draft resolution on the death penalty

Candidate 1:
  Question: In 1999, why did Tanzania retain the death penalty in the 1999 Third Committee meeting record on the death penalty?
  Answer: because it served a useful purpose, although it was resorted to very sparingly
````

### Output: choice 0

Finish reason: `stop`.

````text
[
  {
    "index": 0,
    "grounding": 4,
    "precision": 4,
    "numerical_fidelity": 5,
    "reason": "The answer is a near-verbatim span of the final sentence, but the speaker (Tanzania) has to be inferred from the paragraph 18 attribution. The answer is tight, with only a minor trailing phrase that could be cut, and it contains no numbers."
  },
  {
    "index": 1,
    "grounding": 4,
    "precision": 4,
    "numerical_fidelity": 5,
    "reason": "The answer is taken directly from the first sentence of the block, which says Tanzania retained the penalty because it served a useful purpose. The clause 'although it was resorted to very sparingly' is extra context, and the answer contains no numbers."
  }
]
````

### Recorded usage

````json
{
  "cached_tokens": 0,
  "completion_tokens": 273,
  "prompt_tokens": 8882,
  "provider_cost": 0.020494,
  "reasoning_tokens": 0
}
````

### Input size diagnostics

````json
{
  "input_characters": 27571,
  "context_capacity_exceeded": null
}
````

## Call 006: faithfulness

Request: `b604de05aaa84e92a3f88675b1f7a09e`. Task: `mode/un/2011/cd/pv_1222#13/lookup`.

Model: `anthropic/claude-sonnet-5.5`. UTC: 2026-09-30T17:53:17.092779+00:00.

API status: **response**. Duration: 3.492881 seconds.

### Request settings

````json
{
  "extra_body": {
    "thinking": {
      "budget_tokens": 16000,
      "type": "enabled"
    }
  },
  "max_tokens": 32000
}
````

### Input 1: system

````text
You are a strict faithfulness grader for legal and policy question-answer pairs built from United
  Nations documents.

You will receive a three-section context and THREE question-answer pairs.
The context is:
- "### TARGET BLOCK" — the passage the questions are supposed to be about, in one or more language
  versions.
- "### REFERENCED DOCUMENTS" — other documents CITED by the target block, each supplied as its
  symbol, title, and text — provided ONLY so the target block's citations can be understood, the way
  a footnote helps a reader.
- "### DOCUMENT CONTEXT" — surrounding text of the SAME document (its opening and neighbouring
  passages), supplied so that the target block can be understood: it resolves which mission "the
  Mission" is, which country "the Government" governs, what period a report covers, and similar
  referring expressions.
BOTH supporting sections are for UNDERSTANDING ONLY. Using them to resolve a referring expression in
  the question or answer (naming "the Mission" as UNAMIR, identifying what a cited resolution
  concerns) is legitimate and must NOT be penalised. Using either of them as a source of answer
  substance is a grounding failure — the answer's facts must come from the TARGET BLOCK itself,
  fully.

THREE question-answer pairs (questions may be in any language; each answer matches its question's
  language). Grade each pair on three sub-criteria, each 1–5. Do NOT evaluate query shape or
  retrieval quality — those are handled separately. Focus only on how faithfully each answer
  reflects the supplied text.

GRADING INSTRUCTIONS:
- Grade each of the three pairs independently and against the absolute rubric below — not relative
  to the other two.
- Do not let similarity or dissimilarity between the three pairs influence any individual grade.
- Evaluate each pair on its own merits before moving to the next.

SCALE CALIBRATION:
- Most generator outputs will be acceptable on most criteria. "Acceptable" is not the same as
  "excellent."
- 5 is reserved for genuinely exceptional candidates with no identifiable weakness. If you can point
  to any imperfection, it is not a 5. 5s should be uncommon.
- 4 means the candidate is very good but has exactly one minor, identifiable issue. You must be able
  to name the issue.
- 3 is the default grade for a candidate that is acceptable and does the job, with one clear
  weakness. It is not a punishment grade — most acceptable candidates will receive 3s.
- 2 and 1 are reserved for candidates with real, identifiable problems. Do not avoid using them when
  a candidate qualifies.
- Before assigning any 4 or 5, pause and ask: "What specifically makes this better than a 3?" If you
  cannot answer concretely, the grade is 3.

SUB-CRITERIA:

1. GROUNDING (1–5): Is the answer supported by a contiguous span of the TARGET BLOCK?
   The supporting text means the TARGET BLOCK alone. Resolving a referring expression through the
     REFERENCED DOCUMENTS, the DOCUMENT CONTEXT, or the metadata lines is legitimate disambiguation,
     not an inferential step. Anything more is.
   Cap the grade at 2 if any part of the answer's substance — a fact, figure, list, reason, or
     condition — is stated only in a REFERENCED DOCUMENT or only in the DOCUMENT CONTEXT and not in
     the target block. Cap at 1 if the answer's substance mainly comes from outside the target
     block.
   5 — Answer is taken directly from a single short contiguous span of the target block. Every word
     of the answer is explicitly present or is a trivial rewording of explicit content. No inference
     whatsoever. (Rare.)
   4 — Answer is fully supported but requires reading across two adjacent sentences, OR is from a
     single span with minor trivial rewording that a strict reader might flag.
   3 — Answer is grounded in the target block but requires one small, defensible inferential step —
     connecting a pronoun to its referent, combining a figure with its unit, or similar.
   2 — Answer is partially supported: some parts grounded in the target block, other parts not
     (including parts taken from a REFERENCED DOCUMENT or the DOCUMENT CONTEXT).
   1 — Answer requires significant inference, outside knowledge, or is not in the target block at
     all.
   CITATION RULE (UN): UN texts constantly cite other instruments ("the measures imposed by
     paragraph 20 of resolution 1493 (2003)"). If the answer's substance sits behind such a citation
     rather than in the target block's own words, score at most 2 (1 if the answer consists mainly
     of such content) — REGARDLESS of whether the cited document was supplied in the REFERENCED
     DOCUMENTS section. References exist for understanding, never as answer material.
   ATTRIBUTION RULE (UN): summary records report delegates' statements, letters convey a
     government's position, and reports state the reporting body's findings and estimates. If the
     target block attributes a claim, estimate, or assessment to a speaker or body and the answer
     (or the question it responds to) presents that claim as established fact with the attribution
     stripped, cap GROUNDING at 2 — the supplied text supports the attributed claim, not the bare
     assertion.

2. PRECISION (1–5): Does the answer add unsupported details or padding?
   5 — Answer is the shortest possible span that fully answers the question. Not one extra word. No
     surrounding context, no hedges, no elaboration. (Rare.)
   4 — Answer is grounded and tight but includes one short fragment of adjacent context that could
     have been cut.
   3 — Answer is grounded but includes one unsupported detail, generalization, or piece of padding.
   2 — Answer includes multiple unsupported details, or uses speculative framing ("likely,"
     "approximately," "it seems") where the passage is specific.
   1 — Answer is largely padded with content not in the passage, or is a rewrite rather than an
     extraction.

3. NUMERICAL & CITATIONAL FIDELITY (1–5): Are numbers, dates, amounts, and official identifiers
  reproduced exactly? (JSON key remains "numerical_fidelity".)
   5 — All numbers, dates, durations, monetary amounts, percentages, troop figures, and official
     identifiers (document symbols, resolution and paragraph numbers) match the passage
     character-for-character (e.g., "resolution 2374 (2017)" preserved as-is, not "Resolution 2374";
     "S/1994/565", not "S/1994/565/Rev.1"; "up to 5,500 troops", not "about 5,000 troops"; "within
     30 days", not "in about a month"). Dates rendered in the answer language's standard format
     count as exact if day, month, and year are unchanged ("15 July 1994" for "le 15 juillet 1994").
   4 — All values and identifiers are correct and preserved, but with a trivial formatting
     difference (e.g., "30-day period" vs. "within 30 days", or a spacing/punctuation variant of an
     identifier).
   3 — One number or date is rounded or approximated, one identifier is truncated (e.g., year
     dropped from a resolution number), or one duration is converted to a different unit.
   2 — Multiple values or identifiers rounded, reformatted, truncated, or partially dropped.
   1 — Numbers, dates, or identifiers invented, significantly changed, or contradicted by the
     passage.
   N/A — Answer contains no numerical or citational content. Score this sub-criterion as 5 if N/A.

Output valid JSON only — a list of three objects, one per candidate, in the order the candidates
  were provided (index 0, 1, 2):
[
  {
    "index": 0,
    "grounding": <1-5>,
    "precision": <1-5>,
    "numerical_fidelity": <1-5>,
    "reason": "one short sentence explaining the grades"
  },
  {
    "index": 1,
    "grounding": <1-5>,
    "precision": <1-5>,
    "numerical_fidelity": <1-5>,
    "reason": "..."
  },
  {
    "index": 2,
    "grounding": <1-5>,
    "precision": <1-5>,
    "numerical_fidelity": <1-5>,
    "reason": "..."
  }
]

ACTUAL BATCH SIZE: This request contains exactly 2 candidates. Return exactly 2 grade objects, using indices [0, 1]. Grade only supplied candidates. Any references above to THREE pairs or three example objects describe a typical batch; this actual batch size overrides those counts. All scoring criteria and calibration remain unchanged.
````

### Input 2: user

````text
### TARGET BLOCK — write the questions about THIS text

[EN] Document: CD/PV.1222
  Title: The President: I declare open the 1222nd plenary meeting of the Conference on Disarmament.
The President: I now give the floor to the distinguished Ambassador of Algeria.
You have the floor, Ambassador.
Mr. Idriss (Algeria) (spoke in Arabic): I have asked to take the floor in Arabic, a language that we have not heard yet today, in order to join previous speakers, especially the representative of Mexico who spoke on behalf of the Group of 21, in conveying on my own behalf and on behalf of my country's delegation our deep gratitude and appreciation to Mr. Sergei Ordzhonikidze, the Secretary-General of the Conference on Disarmament, who will leave us shortly, for his admirable efforts since taking office on 19 March 2002.
His performance is not surprising, since he spent his entire professional life in the diplomatic service, accumulating valuable experience during his years as a Russian diplomat.
He was thus well prepared for his move to the area of multilateral cooperation, in which he has occupied the exalted posts of Director-General of the United Nations Office at Geneva and Secretary-General of the Conference on Disarmament.

### REFERENCED DOCUMENTS — none. The target block cites no other document available in the corpus.

### DOCUMENT CONTEXT — surrounding text of the SAME document, supporting context only. It resolves what the target block leaves implicit; it is never a source of answers.

[EN] Document CD/PV.1222 — surrounding passages
The President: I declare open the 1222nd plenary meeting of the Conference on Disarmament.
As you are aware, Mr. Sergei Ordzhonikidze, Director-General of the United Nations Office at Geneva, Secretary-General of the Conference on Disarmament, completes his term of office at the end of this month.
Mr. Ordzhonikidze, a Russian national, was appointed to the post of Director-General by the Secretary-General of the United Nations, Mr. Kofi Annan, and took up his post on 1 March 2002. And he was also subsequently appointed by Mr. Kofi Annan as Secretary-General of the Conference on Disarmament.
A career diplomat, Mr. Ordzhonikidze joined the Soviet diplomatic service in 1969, and served primarily in the Permanent Mission of the Soviet Union and later the Russian Federation to the United Nations in New York and the Ministry of Foreign Affairs in Moscow.
Throughout his diplomatic career, Mr. Ordzhonikidze has served as head of the delegations of the Russian Federation to a great many international conferences and bilateral negotiations.
He has also had many works published on international and legal affairs.

In this capacity, he has discharged his duties with perseverance, authority and professionalism.
Indeed, the Conference on Disarmament has benefited greatly from his experience and skilfulness earned during his long-lasting career as an eminent diplomat of his country and then as a high-ranking official of the United Nations, as well as from his extensive knowledge of the intricacies of arms control and disarmament.
His tenacity and dedication in strengthening the role of the Conference as the sole multilateral negotiating body on disarmament and encouraging it to respond to new challenges with determination have earned him the respect of us all.
On behalf of the Conference on Disarmament and on my own behalf, I would like to wish Mr. Ordzhonikidze and his family much success and happiness in the future.
So I propose to give a round of applause to Mr. Ordzhonikidze.
Mr. Sirakov (France) (spoke in French): On behalf of Ambassador Danon and the delegations that are members of the Western Group, I would like to express our appreciation for the contribution made by Mr. Sergei Ordzhonikidze to the work of our Conference over the last nine years, and our regret at his departure.

Mr. Secretary-General, you took up this prestigious office on 1 March 2002 after being appointed Personal Representative of the Secretary-General of the United Nations in Geneva.
This appointment was a direct result of your knowledge of international law and your experience in multilateral diplomacy and the United Nations system.
After graduating from the Moscow Institute of International Relations, you completed your postgraduate studies in international law in 1978 at the Diplomatic Academy. You then entered the Ministry of Foreign Affairs and were appointed a number of times to the Permanent Mission of the Soviet Union, and then of the Russian Federation, to the United Nations in New York, where in particular you served as Deputy Permanent Representative.
You also worked in Moscow in the International Legal Department and the Department of International Organizations before being promoted to the role of Deputy Minister of Foreign Affairs.
You have therefore served as the head of your country's delegation on many occasions at international conferences and bilateral negotiations.
In addition, you have had a number of works published on legal affairs and major international issues.

Since arriving in Geneva as Secretary-General of the Conference on Disarmament, you have personified the continuity of the work of this forum and worked alongside more than 55 Presidents of the Conference, assisting them with your knowledge of the rules and procedures of the Conference, while offering member States your political sense and insight.
Encouraged by the declarations of the Secretary-General of the United Nations, you urged all member States to set aside their political differences and show flexibility so that the Conference could fulfil its role as the unique multilateral negotiating forum on disarmament.
You also quite rightly reminded us that any international institution has to produce results if it wishes to remain legitimate in the eyes of the international community.
Furthermore, you played a major role in the preparations for the high-level meeting on 24 September 2010 on revitalizing the work of the Conference.
We are very grateful for your committed service with us and for the encouragement you gave to stimulate our debates.
We are sorry to see you leave and we wish you and your family much happiness and success.

The President: I would now like to give the floor to the distinguished representative of Mexico, on behalf of the G-21.
Ms. Jáquez Huacuja (Mexico): The Group of 21 wishes to express its appreciation for the years that Mr. Sergei Ordzhonikidze served as Secretary-General of the Conference on Disarmament.
The Group recognizes Mr. Sergei Ordzhonikidze's assistance to the Conference and its Presidents in the organization of this body's work.
The Group of 21 wishes Mr. Ordzhonikidze the best of luck in his new endeavours, and takes this opportunity to extend its support to the new Secretary-General of the Conference and wish him success.
In this regard, the Group of 21 reiterates its commitment to the work of the Conference on Disarmament as the single multilateral negotiating disarmament body.
The President: I now give the floor to the distinguished Ambassador of Kazakhstan, on behalf of the Eastern European Group.
You have the floor.

Mr. Tileuberdi (Kazakhstan): It is a great honour for me to take the floor on behalf of the Eastern European Group at this special plenary meeting to bid farewell to His Excellency Mr. Sergei Ordzhonikidze.
First of all, let me convey deep gratitude and heartfelt appreciation from each distinguished delegation of our Group to Mr. Ordzhonikidze for his serious engagement, competent leadership and tireless efforts shown in his capacity as the United Nations Office at Geneva Director-General and the Secretary-General of the Conference on Disarmament.
I believe that all distinguished colleagues present here and many of our predecessors have good memories of the relationship that we have enjoyed with Mr. Ordzhonikidze over the last nine years.
We are especially grateful for his openness to listen to each of us and his efforts to reach out to all.
As we know, the Conference on Disarmament is the single multilateral disarmament negotiating forum. And the United Nations Office at Geneva Director-General, as Secretary-General of the Conference and Personal Representative of the United Nations Secretary-General to the Conference is responsible for overseeing the support and assistance provided to it.

In this regard, let me say that Mr. Ordzhonikidze has made every effort in generating political will towards that universal goal. He has served with a professionalism, loyalty and impartiality as a high official of the United Nations.
I have to commend Mr. Ordzhonikidze for his diplomatic skills and knowledge as well as constructive ideas to stimulate the work of this Conference. Our special thanks for his patience in that respect.
Finally, we would like to say that it was a great pleasure to work with Mr. Ordzhonikidze, and we wish him all the best in his further endeavours.
The President: I now give the floor to the distinguished representative of China.
Mr. Li Yang (China) (spoke in Chinese): Mr. President, the Chinese delegation endorses the comments just made by all our colleagues in praise of the distinguished Secretary-General of the Conference on Disarmament, Mr. Ordzhonikidze.
We are convinced that Mr. Ordzhonikidze should undoubtedly be proud of his abundant leadership abilities and a diplomatic career full of achievements.
As you all know, for a long time now Mr. Ordzhonikidze has consistently given full play to his outstanding leadership abilities with a spirit of professionalism, integrity and dedication, and has provided timely, effective and valuable support and assistance to the work of the Conference on Disarmament.

Relying on his extensive diplomatic experience, he has put forward many valuable suggestions for the work of the Conference, winning the respect of the member States and greatly benefiting us.
Whenever the Conference has faced difficulties, he has always worked in close cooperation with member States and made great joint efforts with them to promote the early start of substantive work by the Conference.
The Chinese delegation has had the honour of engaging in positive and pleasant cooperation with Mr. Ordzhonikidze and the Conference on Disarmament secretariat led by him.
During Mr. Ordzhonikidze's term of office, he and the secretariat gave the Chinese delegation a great deal of useful assistance and left many fond memories.
We are very sorry to see him leave office.
In conclusion, I would like to take this opportunity to wish Mr. Ordzhonikidze further success in his future career.
I wish him and his family health and happiness in the years to come.

The President: I now give the floor to the distinguished representative of the Russian Federation.
You have the floor, Ambassador.
Mr. Loshchinin (Russian Federation) (spoke in Russian): We extend a heartfelt welcome to our distinguished compatriot Sergei Alexandrovich Ordzhonikidze, the Director-General of the United Nations Office at Geneva, the Secretary-General of the Conference on Disarmament and the Personal Representative of the Secretary-General of the United Nations on disarmament matters.
We have every reason to be proud of your outstanding achievements.
You have been untiring in your efforts to bring the Conference on Disarmament out of its deadlock and in supporting the adoption of a balanced programme of work.
You have convincingly explained the nuances of the Conference's rules of procedure to us with patience and, where necessary, you managed to get us back on the right track when sometimes in this conference room our passions got the better of us.

Of course, I cannot fail to mention that Mr. Ordzhonikidze is a shining example of the Russian school of diplomacy.
As a highly qualified specialist on international law, he has been active and successful in so many international forums, undertaking to promote legal standards and principles in order to address the issues of our time, from the primacy of human rights to security in outer space.
As the Deputy Foreign Minister of the Russian Federation, Mr. Ordzhonikidze was in charge of and guided Russian delegations at many multilateral forums.
However, in the life of every diplomat and in the life of any high-ranking international civil servant, there comes a time when you have to bid farewell to colleagues, associates and friends.
Back in Moscow you have a large and loving family and many friends and comrades who are waiting for you to return.
I am sure that your wealth of experience and considerable knowledge will remain much sought after, not only back home but also internationally.

I wish you every success and until we meet again.
The President: Thank you, Ambassador.
And now I give the floor to the distinguished Ambassador of Switzerland.
Mr. Lauber (Switzerland) (spoke in French): On behalf of Switzerland, the host country today, I would like to express our sincere gratitude to Mr. Sergei Ordzhonikidze for the invaluable contribution that he has made to the Conference on Disarmament over the last nine years.
His dual role as Secretary-General of the Conference on the one hand, and Personal Representative of the Secretary-General of the United Nations to the Conference on the other, is entirely consistent with the sincere and sustained interest which he is known to have for disarmament.
Over the same period, that is to say since 2002, he has taken on additional important responsibilities in his position as Director-General of the United Nations Office in Geneva.
As the host country, we have particularly appreciated the way in which he has successfully carried out his various responsibilities.

Outside of the Conference on Disarmament, his support has been decisive in the progress that has been made here in Geneva in the areas of disarmament and non-proliferation.
We have particularly appreciated Mr. Ordzhonikidze's encouragement of delegations to agree on a programme of work, as well as the new impetus that he provided to the process of revitalizing disarmament mechanisms.
His approach has brought new value to our work and has reflected the long and valuable diplomatic experience which he acquired in the service of both his country and the United Nations.
We thank him warmly for his committed and constructive ideas which have helped to stimulate the work of this Conference.
Although there has been progress under his leadership, we regret the lack of results in the negotiations of the last few years and we are convinced that Mr. Ordzhonikidze shares this feeling.
We are sorry to see Mr. Ordzhonikidze leave us and we wish him every success in his future projects.

Immediately after this meeting, I have the pleasure to invite all the delegations, whether members of the Conference or not, and also Government and non-governmental representatives to a reception in honour of our Secretary-General.
Conference officers and interpreters are also cordially invited to come to the reception.
The President: I now give the floor to the distinguished Ambassador of Slovenia, on behalf of the informal group of observer States.
We applaud his leadership in guiding the secretariat in support of our work in the Conference and other disarmament processes.
We particularly appreciate his assistance and encouragement to our group in the cause of membership expansion.
We also look forward to his continuing engagement with the disarmament community and the work of the United Nations.
His experience and counsel can continue to guide us.
We, the representatives of the informal group, remain committed to our goal of expansion.
Our group would like to bid Mr. Ordzhonikidze a fond farewell, and to wish him every success in his future endeavours.

[... the TARGET BLOCK appears here ...]

Mr. Ordzhonikidze's wide-ranging experience, his qualifications and his personal qualities have been of immense importance and, as noted by the President of the Conference on Disarmament in 2002, the Conference has benefited from them.
I should be wanting in my duty if I failed to mention on this occasion that Mr. Ordzhonikidze has successfully performed the tasks entrusted to him. We have all witnessed his highly professional endeavours over the years to enable the Conference to achieve its lofty goals.
He has been an unstinting source of wise advice, and his pertinent guidance has been of great importance.
We are convinced that his efforts stemmed from his unwavering aspiration to enable the Conference to pursue and intensify its work as the sole multilateral forum for negotiations on disarmament issues.
The President: I now give the floor to the distinguished Ambassador of Sri Lanka.
You have the floor, Ambassador.
Ms. Senewiratne (Sri Lanka): Mr. President, at the outset, I wish to express our appreciation to you for convening the Conference on Disarmament in special session to pay tribute to Mr. Sergei Ordzhonikidze, Secretary-General of the Conference and Personal Representative of the United Nations Secretary-General, and associate myself with the statement of the representative of the G-21 delivered by the representative of Mexico.

Mr. Ordzhonikidze's long and distinguished diplomatic career representing the former Soviet Union and subsequently the Russian Federation is well known.
On the multilateral side, he served in missions both in New York and Geneva, subsequently being appointed as the Deputy Minister for Foreign Affairs of the Russian Federation.
Such experience bears ample testimony to his illustrious career in the diplomatic service.
We are of the view that the United Nations Office at Geneva in general, and the Conference on Disarmament in particular, are privileged to avail of his vast experience during the nine-year tenure of Mr. Ordzhonikidze here in Geneva.
My delegation welcomes and appreciates the contribution Mr. Ordzhonikidze has made to the Conference, especially in maintaining the subject at high priority to the United Nations Secretary-General.
Undoubtedly, this constructive approach of Mr. Ordzhonikidze to the work of the Conference at the highest level culminated in the United Nations Secretary-General's addressing this august body earlier this year.
His efforts in this regard were exemplified with the organizing of the High-level Meeting of all United Nations Member States in September last year on revitalizing the work of the Conference and taking forward the multilateral disarmament negotiations.

On a personal note, I have observed the humanness of Mr. Ordzhonikidze, which has been amply demonstrated through his subtle sense of humour.
He will be missed.
I take this opportunity to warmly felicitate Mr. Ordzhonikidze on a highly successful tenure and wish him the very best in his future endeavours.
The President: Thank you, Ambassador.
Also, we wish to thank you for the kind words you addressed to the Chair.
I now give the floor to the distinguished Ambassador of Iran.
Ambassador, you have the floor.
Mr. Sajjadi (Islamic Republic of Iran): At the outset, let me associate myself with the statement made by Mexico on behalf of the G-21.
I would like to take this opportunity to congratulate you, Mr. President, on the manner that you are conducting your presidency over the Conference on Disarmament.
I appreciate your efforts in convening this meeting outside the schedule of the meetings of the Conference to provide the opportunity for the delegations to express their appreciation for many years of hard work of His Excellency Mr. Ordzhonikidze.

We attach great importance to the Conference as the single multilateral negotiating body on disarmament.
We have to preserve the nature, role and purpose of this august body with the top priority of nuclear disarmament.
Mr. Sergei Ordzhonikidze served almost nine years as Secretary-General of the Conference.
During this period, he has provided much assistance to the Conference and its Presidents.
Due to the lack of political will for the resumption of nuclear disarmament, the Conference could not start its formal task of negotiation.
However, the valuable work and patience of Mr. Ordzhonikidze is commendable.
We wish Mr. Ordzhonikidze all the best in his new life, and take this opportunity to extend our support to the new Secretary-General of the Conference.
Would any other delegation like to take the floor? It does not seem to be the case.
It is now my privilege to give the floor to the Secretary-General of the Conference on Disarmament, Mr. Sergei Ordzhonikidze.

Mr. Sergei Ordzhonikidze (Secretary-General of the Conference on Disarmament): Thank you very much, Mr. President, for giving me the floor, and thank you very much for all those who spoke and all those who came here, and especially my colleagues and friends, Ambassadors from different countries, to support me in my tenure.
I am still there for a couple of weeks as Secretary-General, though I don't expect the Conference will create a miracle.
I appreciate all your help, assistance, your sympathy, your flexibility, your willingness.
I especially appreciate the Secretary-General who gave me this important job, a job as his representative to the CD and the Secretary-General of the Conference.
I believe that was one of the most difficult and challenging jobs in the United Nations.
Indeed, this is my final plenary meeting in my capacity as the Secretary-General of the Conference on Disarmament and Personal Representative of the United Nations Secretary-General to the Conference.
I value this opportunity to express to all of you my appreciation for your very professional collaboration.
I admit that I never felt myself distracted sitting here on the podium, distracted from you, from your positions, your preoccupations, your concerns, your willingness to do something.

I always felt that it is my duty to help you in a case that was permissible to me in that capacity that I have.
It has been a privilege to serve the Conference on Disarmament, the United Nations and the cause of multilateral disarmament over these nine years.
You all know that this is a cause in which I believe strongly and that I am passionate about.
That is why the Conference is both my passion and, of course, it is my pain.
It is a cause that I am committed to because it is essential for a safer and more prosperous world.
I will reveal something to you.
For a number of years, I was one of the top managers of the United Nations, according to unofficial estimates, and only this year I was not on the very top because in the part of my compact, which is about 50 pages, I said that I will try my best to promote the Conference on Disarmament.
The mark was negative.

I believe that multilateral disarmament is fundamental if the United Nations is to achieve its overall mission. And the Conference on Disarmament is a key to that effort.
The ambassadors in this room carry a tremendous responsibility on behalf of the international community and the human family.
It is as simple as that. And I understand why it is not that easy to have progress in the Conference on Disarmament, because we are not adopting the resolutions that other organs adopt, and the resolutions that nobody remembers in a couple of years.
But we are fighting for resolutions at the United Nations.
Here, we are not fighting for those resolutions.
Disarmament and non-proliferation bring stability, build confidence among States and can be part of establishing conditions conducive to development.
With annual military expenditures over $1.5 trillion, and in the wake of an economic and financial crisis that affected millions of vulnerable people around the world, we have an obligation to assess critically this spending, and our activity in particular.

The Conference on Disarmament has potential to be the driving force and the linchpin in multilateral disarmament.
The Conference has produced landmark treaties that have promoted international security while demonstrating that multilateral collaboration can serve the global and national interest alike.
It is a source of disappointment for me that this undisputed record of achievement is being overshadowed by the stalemate that we are experiencing today at the Conference.
I have to be blunt -- as I have been many times before from this podium and the podium in New York -- and say to you that not only the credibility of the Conference is at risk; its very future is at risk.
It is clear that the voices advocating taking some of the work of the Conference into other arenas are growing stronger, and they are increasingly being listened to.
This development is a reflection of the deep frustration and disappointment of the international community at the inability of the Conference to overcome its differences and show genuine political will.

This showed the unique potential of the Conference when the right balance of compromise and consensus had been found.
I commend the Conference for the political will and vision, leadership and sense of responsibility that the programme of work represented. And I most sincerely hope that the same can be found again to rejuvenate this achievement.
I have enjoyed working with you to further the cause of multilateral disarmament. It is our common cause.
I never felt somebody who is outside of this room, I felt as one of you.
I felt that your success is my success, and your lack of success is my problem.
Maybe the Secretary-General was right putting me a negative mark.
I encourage you -- as I have done many times over the past years -- to always keep in mind this vision of a more secure world and to find innovative ways to allow the Conference to take its work forward.

I remain convinced that the world needs the Conference on Disarmament.
People across the world look to the Conference to take its responsibility very seriously, and to use its potential to the full.
Ladies and gentlemen, dear ambassadors, dear colleagues, dear friends, I wish the Conference on Disarmament and its members all the best in taking forward this crucial work for international peace and security.
In our case, on 65 member States depends the success of the Conference.
I wish you all to be optimistic and don't lose sight that you are sitting here in Geneva in one of the most important organs of the United Nations system, and in general, one of the most important organs that we have in multilateral affairs.
I don't want to somehow denigrate other United Nations activities, but as I told you, disarmament is everything in this world. Disarmament is peace, disarmament is confidence, disarmament is friendly relations and disarmament is also development.

So you have on your shoulders an enormous burden.
You have to be up to this task before you.
I wish you very well, and I hope you will find a solution in this or another way.
Remember, I am retiring as Under-Secretary-General, as Director-General, as a Special Representative of the Secretary-General and the Secretary-General of this Conference, but your Director-General is watching you very carefully! And I'm going to write about my favourite passion and pain, the Conference on Disarmament -- some articles, do some lecturing -- because I am truly a believer in this disarmament process.
So I wish you very well in that.
The President: Thank you, Mr. Ordzhonikidze, for your farewell speech.
This concludes our business for today in this Council chamber.
This plenary session stands adjourned.

Candidate 0:
  Question: Which post did Algeria's ambassador identify Ordzhonikidze as holding in the 2011 Conference on Disarmament meeting record on his departure?
  Answer: Director-General of the United Nations Office at Geneva

Candidate 1:
  Question: Since what date did Algeria's ambassador associate Ordzhonikidze's efforts with taking office in the 2011 Conference on Disarmament meeting record?
  Answer: since taking office on 19 March 2002
````

### Output: choice 0

Finish reason: `stop`.

````text
[
  {
    "index": 0,
    "grounding": 3,
    "precision": 4,
    "numerical_fidelity": 5,
    "reason": "The target block names Director-General of the UN Office at Geneva among his posts, but also Secretary-General of the CD, so the question's singular 'which post' is ambiguous and the answer is only partial; '2011' comes from outside the block. The answer itself is a tight verbatim span."
  },
  {
    "index": 1,
    "grounding": 4,
    "precision": 4,
    "numerical_fidelity": 5,
    "reason": "The answer reproduces '19 March 2002' exactly as stated in the target block; 'since' is slightly redundant padding, and the question's '2011' is not in the block."
  }
]
````

### Recorded usage

````json
{
  "cached_tokens": 0,
  "completion_tokens": 259,
  "prompt_tokens": 11939,
  "provider_cost": 0.026468,
  "reasoning_tokens": 0
}
````

### Input size diagnostics

````json
{
  "input_characters": 36206,
  "context_capacity_exceeded": null
}
````

## Call 007: faithfulness

Request: `e2a48cdd23ba46d98fc1531c25815a1a`. Task: `mode/un/2000/cd/pv_844#0/practitioner`.

Model: `anthropic/claude-sonnet-5.5`. UTC: 2026-09-30T17:53:17.094108+00:00.

API status: **response**. Duration: 4.234322 seconds.

### Request settings

````json
{
  "extra_body": {
    "thinking": {
      "budget_tokens": 16000,
      "type": "enabled"
    }
  },
  "max_tokens": 32000
}
````

### Input 1: system

````text
You are a strict faithfulness grader for legal and policy question-answer pairs built from United
  Nations documents.

You will receive a three-section context and THREE question-answer pairs.
The context is:
- "### TARGET BLOCK" — the passage the questions are supposed to be about, in one or more language
  versions.
- "### REFERENCED DOCUMENTS" — other documents CITED by the target block, each supplied as its
  symbol, title, and text — provided ONLY so the target block's citations can be understood, the way
  a footnote helps a reader.
- "### DOCUMENT CONTEXT" — surrounding text of the SAME document (its opening and neighbouring
  passages), supplied so that the target block can be understood: it resolves which mission "the
  Mission" is, which country "the Government" governs, what period a report covers, and similar
  referring expressions.
BOTH supporting sections are for UNDERSTANDING ONLY. Using them to resolve a referring expression in
  the question or answer (naming "the Mission" as UNAMIR, identifying what a cited resolution
  concerns) is legitimate and must NOT be penalised. Using either of them as a source of answer
  substance is a grounding failure — the answer's facts must come from the TARGET BLOCK itself,
  fully.

THREE question-answer pairs (questions may be in any language; each answer matches its question's
  language). Grade each pair on three sub-criteria, each 1–5. Do NOT evaluate query shape or
  retrieval quality — those are handled separately. Focus only on how faithfully each answer
  reflects the supplied text.

GRADING INSTRUCTIONS:
- Grade each of the three pairs independently and against the absolute rubric below — not relative
  to the other two.
- Do not let similarity or dissimilarity between the three pairs influence any individual grade.
- Evaluate each pair on its own merits before moving to the next.

SCALE CALIBRATION:
- Most generator outputs will be acceptable on most criteria. "Acceptable" is not the same as
  "excellent."
- 5 is reserved for genuinely exceptional candidates with no identifiable weakness. If you can point
  to any imperfection, it is not a 5. 5s should be uncommon.
- 4 means the candidate is very good but has exactly one minor, identifiable issue. You must be able
  to name the issue.
- 3 is the default grade for a candidate that is acceptable and does the job, with one clear
  weakness. It is not a punishment grade — most acceptable candidates will receive 3s.
- 2 and 1 are reserved for candidates with real, identifiable problems. Do not avoid using them when
  a candidate qualifies.
- Before assigning any 4 or 5, pause and ask: "What specifically makes this better than a 3?" If you
  cannot answer concretely, the grade is 3.

SUB-CRITERIA:

1. GROUNDING (1–5): Is the answer supported by a contiguous span of the TARGET BLOCK?
   The supporting text means the TARGET BLOCK alone. Resolving a referring expression through the
     REFERENCED DOCUMENTS, the DOCUMENT CONTEXT, or the metadata lines is legitimate disambiguation,
     not an inferential step. Anything more is.
   Cap the grade at 2 if any part of the answer's substance — a fact, figure, list, reason, or
     condition — is stated only in a REFERENCED DOCUMENT or only in the DOCUMENT CONTEXT and not in
     the target block. Cap at 1 if the answer's substance mainly comes from outside the target
     block.
   5 — Answer is taken directly from a single short contiguous span of the target block. Every word
     of the answer is explicitly present or is a trivial rewording of explicit content. No inference
     whatsoever. (Rare.)
   4 — Answer is fully supported but requires reading across two adjacent sentences, OR is from a
     single span with minor trivial rewording that a strict reader might flag.
   3 — Answer is grounded in the target block but requires one small, defensible inferential step —
     connecting a pronoun to its referent, combining a figure with its unit, or similar.
   2 — Answer is partially supported: some parts grounded in the target block, other parts not
     (including parts taken from a REFERENCED DOCUMENT or the DOCUMENT CONTEXT).
   1 — Answer requires significant inference, outside knowledge, or is not in the target block at
     all.
   CITATION RULE (UN): UN texts constantly cite other instruments ("the measures imposed by
     paragraph 20 of resolution 1493 (2003)"). If the answer's substance sits behind such a citation
     rather than in the target block's own words, score at most 2 (1 if the answer consists mainly
     of such content) — REGARDLESS of whether the cited document was supplied in the REFERENCED
     DOCUMENTS section. References exist for understanding, never as answer material.
   ATTRIBUTION RULE (UN): summary records report delegates' statements, letters convey a
     government's position, and reports state the reporting body's findings and estimates. If the
     target block attributes a claim, estimate, or assessment to a speaker or body and the answer
     (or the question it responds to) presents that claim as established fact with the attribution
     stripped, cap GROUNDING at 2 — the supplied text supports the attributed claim, not the bare
     assertion.

2. PRECISION (1–5): Does the answer add unsupported details or padding?
   5 — Answer is the shortest possible span that fully answers the question. Not one extra word. No
     surrounding context, no hedges, no elaboration. (Rare.)
   4 — Answer is grounded and tight but includes one short fragment of adjacent context that could
     have been cut.
   3 — Answer is grounded but includes one unsupported detail, generalization, or piece of padding.
   2 — Answer includes multiple unsupported details, or uses speculative framing ("likely,"
     "approximately," "it seems") where the passage is specific.
   1 — Answer is largely padded with content not in the passage, or is a rewrite rather than an
     extraction.

3. NUMERICAL & CITATIONAL FIDELITY (1–5): Are numbers, dates, amounts, and official identifiers
  reproduced exactly? (JSON key remains "numerical_fidelity".)
   5 — All numbers, dates, durations, monetary amounts, percentages, troop figures, and official
     identifiers (document symbols, resolution and paragraph numbers) match the passage
     character-for-character (e.g., "resolution 2374 (2017)" preserved as-is, not "Resolution 2374";
     "S/1994/565", not "S/1994/565/Rev.1"; "up to 5,500 troops", not "about 5,000 troops"; "within
     30 days", not "in about a month"). Dates rendered in the answer language's standard format
     count as exact if day, month, and year are unchanged ("15 July 1994" for "le 15 juillet 1994").
   4 — All values and identifiers are correct and preserved, but with a trivial formatting
     difference (e.g., "30-day period" vs. "within 30 days", or a spacing/punctuation variant of an
     identifier).
   3 — One number or date is rounded or approximated, one identifier is truncated (e.g., year
     dropped from a resolution number), or one duration is converted to a different unit.
   2 — Multiple values or identifiers rounded, reformatted, truncated, or partially dropped.
   1 — Numbers, dates, or identifiers invented, significantly changed, or contradicted by the
     passage.
   N/A — Answer contains no numerical or citational content. Score this sub-criterion as 5 if N/A.

Output valid JSON only — a list of three objects, one per candidate, in the order the candidates
  were provided (index 0, 1, 2):
[
  {
    "index": 0,
    "grounding": <1-5>,
    "precision": <1-5>,
    "numerical_fidelity": <1-5>,
    "reason": "one short sentence explaining the grades"
  },
  {
    "index": 1,
    "grounding": <1-5>,
    "precision": <1-5>,
    "numerical_fidelity": <1-5>,
    "reason": "..."
  },
  {
    "index": 2,
    "grounding": <1-5>,
    "precision": <1-5>,
    "numerical_fidelity": <1-5>,
    "reason": "..."
  }
]

ACTUAL BATCH SIZE: This request contains exactly 1 candidates. Return exactly 1 grade objects, using indices [0]. Grade only supplied candidates. Any references above to THREE pairs or three example objects describe a typical batch; this actual batch size overrides those counts. All scoring criteria and calibration remain unchanged.
````

### Input 2: user

````text
### TARGET BLOCK — write the questions about THIS text

[EN] Document: CD/PV.844
  Title: I have on my list of speakers for today the representative of Japan.
I have on my list of speakers for today the representative of Japan.
As you are aware, our esteemed colleague and friend, Ambassador Akira Hayashi of Japan, will be leaving the Conference shortly, having been called to other important duties by his Government.
During his time here, he has presented the position of his Government with prodigious skills and talent.
His personal contribution to our collective efforts to bring about a consensus which would allow the start of substantive work of the Conference has been appreciated by all.
I am personally beholden to him for the friendship he has always shown me.
Mr. HAYASHI (Japan): Thank you very much, Mr. President, for your kind words to me and best wishes to me and to my family.
Mr. President, at the outset, I should like to congratulate you most warmly on your assumption of the presidency and wish you every success in discharging your important duties.
I am certain that your wisdom and diplomatic skills will help bring about in the CD the longawaited positive agreement on our work.
My delegation pledges its full cooperation in your endeavours.
I should also like to pay tribute to your predecessor, Ambassador Harald Kreid of Austria, for his initiative and strenuous efforts to promote the start of substantive work in the CD.

### REFERENCED DOCUMENTS — none. The target block cites no other document available in the corpus.

### DOCUMENT CONTEXT — surrounding text of the SAME document, supporting context only. It resolves what the target block leaves implicit; it is never a source of answers.

[EN] Document CD/PV.844 — surrounding passages
[... the TARGET BLOCK appears here ...]

It is unfortunate that my delegation has not yet been able to make a policy statement at this year's session.
I had been waiting for an opportunity conducive to doing so, possibly after the successful adoption of the work programme. Much to my regret, I now have missed that opportunity for good, because today I am speaking for the last time at the CD, while a prospective work programme is still under consideration or possibly even in long hibernation.
After my two and a half years of tenure here, I should today like to state some of my personal observations on the CD.
First of all, I would not be honest if I said, "I am satisfied with the work I have done here and I am leaving with a sense of achievement".
It is regrettable that I have not been able to participate in any substantive negotiations in the CD.

Before I came to Geneva in 1997, I was told that the situation at the CD was not very propitious for the commencement of negotiations on an FMCT, despite the fact that it had long been agreed as its next item for negotiation.
But, honestly, I did not anticipate that such a situation would continue during my entire tenure.
The report of the Tokyo Forum published last year stated as one of its recommendations: "The Tokyo Forum calls on the Conference on Disarmament to revise it procedures, update its work programme, and carry out purposeful work, or suspend its operations.
The consensus rule is causing perpetual deadlock. Consensus among members of the Conference on Disarmament should not be necessary to begin or conclude negotiations on a multilateral convention".
The frustration and the disappointment for those who are within the CD, including myself, are naturally much greater.
But I personally do not agree with this recommendation, since the existence of the consensus rule itself is not the only cause of the sorry state of the CD, and suspension of the CD's operations would certainly not change the situation for the better.

My predecessor, Ambassador Kurokochi, referred to the CD's consensus rule in her farewell speech. In it, while admitting that the consensus rule was indispensable to the CD, she stated: "When a point at issue is a procedural matter which does not prejudge the question of substance, every country should refrain as much as possible from exercising a veto".
This assertion apparently did not obtain much support at the CD.
Instead, I have frequently heard such words of caution as, "Procedure is substance" and "Devils are in detail".
I have to confess that my own experience here during these two and a half years, has made me more sympathetic to the argument of my predecessor.
Different views have been expressed on this famous consensus rule of the CD.
Some advocate adhering scrupulously to this rule in every nook and corner of the CD's operations. Some argue the necessity of a less rigorous application of the rule, especially to procedural matters.
The recent case of this difference is the interpretation of paragraph 5 (d) of CD/1036.

Despite all these disputes on that consensus rule, one thing I should like to stress is that the consensus rule should be taken as distinctly different from granting the right of veto to each member.
If this distinction is not properly made, the rule would inevitably turn out to be a recipe for indecision and no action.
What is essential to the consensus rule, in my view, is the common recognition of the prerequisite for employing the rule. That prerequisite is the fundamental orientation towards achieving compromises for the sake of agreements rather than a pursuit of individual positions by ultimately resorting to the right of veto.
This necessitates opportunities for thorough discussions through which differences among the participants are identified and efforts to narrow such differences are pursued based on self-restraint.
I have the impression - though I hope I am wrong - that the members of the CD have collectively become insensitive to the prerequisite that makes the consensus rule workable.
Such a sense of resignation as, "nothing to do because there is no consensus", is prevailing at the CD.
Clearly something must be done to redress the situation for the purpose of restoring normalcy to the Conference.

This would enhance the transparency of the work of the CD and increase awareness for progress, and would consequently create more chances for consensus to emerge in the CD.
It is my earnest hope that the CD will start its substantial work as soon as possible.
I was told when I arrived in Geneva that the CD was the best club in town. In fact, it is.
I have enjoyed immensely the company of my colleagues and have been tremendously stimulated intellectually.
But the CD should not be complacent with only good comradeship.
The PRESIDENT: I thank Ambassador Hayashi for his moving statement and for the kind words he addressed to me.
Ambassador Hayashi, once again, our very best to you.
I do share your hope that substantive negotiations may begin soon, and that normalcy, as you say, will soon be restored to the work of the Conference.
This concludes my list of speakers for today. Does any delegation wish to take the floor? That does not seem to be the case.

I should now like to take up for a decision the request from Albania to participate as observer in the work of the Conference during this session without first considering it at an informal plenary meeting.
This request is contained in document CD/WP.509, which is before you. May I take it that the Conference agrees to this request?
It was so decided.
The PRESIDENT: This concludes our business for today. Does any other delegation wish to take the floor at this stage? I recognize the distinguished representative of the United States.
Mr. GREY (United States of America): Mr. President, through you, I would like to extend an invitation to all the members and non-member participants of the Conference on Disarmament to attend a presentation by the United States on nuclear disarmament issues.
The presentation will take place here in the Council Chamber on Tuesday, 7 March, starting at 10 a.m. and will be given by Mr. Frank Miller, Principal Deputy Assistant Secretary of Defense for Strategy and Threat Reduction.
Following Mr. Miller's presentation, there will be an opportunity for questions and answers on issues relating to nuclear disarmament.

This presentation will be closed to the public and media in order to encourage condour and vigorous give-and-take.
I took forward to what I am sure will be an interesting and useful exchange of views.
The PRESIDENT: Distinguished colleagues, as you are aware, since I assumed the Presidency of the Conference, I have undertaken a round of intensive consultations with a number of delegations on the programme of work of the Conference. As a result of these efforts, I have circulated to all of you a non-paper containing possible steps towards a programme of work.
The preliminary reactions to my proposals indicate that further consultations will be needed, and I pledge to you that I will use the remaining days of my presidency in an effort to bring about agreement on the early start of our substantive work.
The next plenary meeting of the Conference will be held on Thursday, 9 March 2000, at 10 a.m.

Candidate 0:
  Question: According to the President of the Conference on Disarmament, why was Japan's Ambassador Hayashi leaving in March 2000?
  Answer: having been called to other important duties by his Government
````

### Output: choice 0

Finish reason: `stop`.

````text
The answer is a direct span from the target block: "having been called to other important duties by his Government." It is a single contiguous span, so the grounding is strong.

The question says "March 2000". The target block does not give that date, and it appears only in the document context, where the next plenary is set for 9 March 2000. The date sits in the question, not the answer, so it does not affect the answer's grounding. It is a minor issue at most.

The answer is a participial fragment and adds nothing unsupported. It is very tight, and the only flaw is that it is not a complete sentence. It has no numbers, so numerical fidelity is N/A and scores 5.

Grounding is 5 because the answer matches the text exactly. Precision is 4 or 5. The span is the shortest that answers the question, but it carries the "having been" participle, which could have been trimmed, so I give it 4.

[{"index":0,"grounding":5,"precision":4,"numerical_fidelity":5,"reason":"Answer is a verbatim contiguous span from the President's statement; it keeps the participle 'having been', which could be cut, and the question's March 2000 date comes from outside the block but does not affect the answer."}]
````

### Recorded usage

````json
{
  "cached_tokens": 0,
  "completion_tokens": 380,
  "prompt_tokens": 5898,
  "provider_cost": 0.015596,
  "reasoning_tokens": 0
}
````

### Input size diagnostics

````json
{
  "input_characters": 17584,
  "context_capacity_exceeded": null
}
````

## Call 008: faithfulness

Request: `633b5b7b71c3447793fb6511271901c5`. Task: `mode/un/2000/cd/pv_844#0/practitioner`.

Model: `anthropic/claude-sonnet-5.5`. UTC: 2026-09-30T17:53:22.346876+00:00.

API status: **response**. Duration: 3.563459 seconds.

### Request settings

````json
{
  "extra_body": {
    "thinking": {
      "budget_tokens": 16000,
      "type": "enabled"
    }
  },
  "max_tokens": 32000
}
````

### Input 1: system

````text
You are a strict faithfulness grader for legal and policy question-answer pairs built from United
  Nations documents.

You will receive a three-section context and THREE question-answer pairs.
The context is:
- "### TARGET BLOCK" — the passage the questions are supposed to be about, in one or more language
  versions.
- "### REFERENCED DOCUMENTS" — other documents CITED by the target block, each supplied as its
  symbol, title, and text — provided ONLY so the target block's citations can be understood, the way
  a footnote helps a reader.
- "### DOCUMENT CONTEXT" — surrounding text of the SAME document (its opening and neighbouring
  passages), supplied so that the target block can be understood: it resolves which mission "the
  Mission" is, which country "the Government" governs, what period a report covers, and similar
  referring expressions.
BOTH supporting sections are for UNDERSTANDING ONLY. Using them to resolve a referring expression in
  the question or answer (naming "the Mission" as UNAMIR, identifying what a cited resolution
  concerns) is legitimate and must NOT be penalised. Using either of them as a source of answer
  substance is a grounding failure — the answer's facts must come from the TARGET BLOCK itself,
  fully.

THREE question-answer pairs (questions may be in any language; each answer matches its question's
  language). Grade each pair on three sub-criteria, each 1–5. Do NOT evaluate query shape or
  retrieval quality — those are handled separately. Focus only on how faithfully each answer
  reflects the supplied text.

GRADING INSTRUCTIONS:
- Grade each of the three pairs independently and against the absolute rubric below — not relative
  to the other two.
- Do not let similarity or dissimilarity between the three pairs influence any individual grade.
- Evaluate each pair on its own merits before moving to the next.

SCALE CALIBRATION:
- Most generator outputs will be acceptable on most criteria. "Acceptable" is not the same as
  "excellent."
- 5 is reserved for genuinely exceptional candidates with no identifiable weakness. If you can point
  to any imperfection, it is not a 5. 5s should be uncommon.
- 4 means the candidate is very good but has exactly one minor, identifiable issue. You must be able
  to name the issue.
- 3 is the default grade for a candidate that is acceptable and does the job, with one clear
  weakness. It is not a punishment grade — most acceptable candidates will receive 3s.
- 2 and 1 are reserved for candidates with real, identifiable problems. Do not avoid using them when
  a candidate qualifies.
- Before assigning any 4 or 5, pause and ask: "What specifically makes this better than a 3?" If you
  cannot answer concretely, the grade is 3.

SUB-CRITERIA:

1. GROUNDING (1–5): Is the answer supported by a contiguous span of the TARGET BLOCK?
   The supporting text means the TARGET BLOCK alone. Resolving a referring expression through the
     REFERENCED DOCUMENTS, the DOCUMENT CONTEXT, or the metadata lines is legitimate disambiguation,
     not an inferential step. Anything more is.
   Cap the grade at 2 if any part of the answer's substance — a fact, figure, list, reason, or
     condition — is stated only in a REFERENCED DOCUMENT or only in the DOCUMENT CONTEXT and not in
     the target block. Cap at 1 if the answer's substance mainly comes from outside the target
     block.
   5 — Answer is taken directly from a single short contiguous span of the target block. Every word
     of the answer is explicitly present or is a trivial rewording of explicit content. No inference
     whatsoever. (Rare.)
   4 — Answer is fully supported but requires reading across two adjacent sentences, OR is from a
     single span with minor trivial rewording that a strict reader might flag.
   3 — Answer is grounded in the target block but requires one small, defensible inferential step —
     connecting a pronoun to its referent, combining a figure with its unit, or similar.
   2 — Answer is partially supported: some parts grounded in the target block, other parts not
     (including parts taken from a REFERENCED DOCUMENT or the DOCUMENT CONTEXT).
   1 — Answer requires significant inference, outside knowledge, or is not in the target block at
     all.
   CITATION RULE (UN): UN texts constantly cite other instruments ("the measures imposed by
     paragraph 20 of resolution 1493 (2003)"). If the answer's substance sits behind such a citation
     rather than in the target block's own words, score at most 2 (1 if the answer consists mainly
     of such content) — REGARDLESS of whether the cited document was supplied in the REFERENCED
     DOCUMENTS section. References exist for understanding, never as answer material.
   ATTRIBUTION RULE (UN): summary records report delegates' statements, letters convey a
     government's position, and reports state the reporting body's findings and estimates. If the
     target block attributes a claim, estimate, or assessment to a speaker or body and the answer
     (or the question it responds to) presents that claim as established fact with the attribution
     stripped, cap GROUNDING at 2 — the supplied text supports the attributed claim, not the bare
     assertion.

2. PRECISION (1–5): Does the answer add unsupported details or padding?
   5 — Answer is the shortest possible span that fully answers the question. Not one extra word. No
     surrounding context, no hedges, no elaboration. (Rare.)
   4 — Answer is grounded and tight but includes one short fragment of adjacent context that could
     have been cut.
   3 — Answer is grounded but includes one unsupported detail, generalization, or piece of padding.
   2 — Answer includes multiple unsupported details, or uses speculative framing ("likely,"
     "approximately," "it seems") where the passage is specific.
   1 — Answer is largely padded with content not in the passage, or is a rewrite rather than an
     extraction.

3. NUMERICAL & CITATIONAL FIDELITY (1–5): Are numbers, dates, amounts, and official identifiers
  reproduced exactly? (JSON key remains "numerical_fidelity".)
   5 — All numbers, dates, durations, monetary amounts, percentages, troop figures, and official
     identifiers (document symbols, resolution and paragraph numbers) match the passage
     character-for-character (e.g., "resolution 2374 (2017)" preserved as-is, not "Resolution 2374";
     "S/1994/565", not "S/1994/565/Rev.1"; "up to 5,500 troops", not "about 5,000 troops"; "within
     30 days", not "in about a month"). Dates rendered in the answer language's standard format
     count as exact if day, month, and year are unchanged ("15 July 1994" for "le 15 juillet 1994").
   4 — All values and identifiers are correct and preserved, but with a trivial formatting
     difference (e.g., "30-day period" vs. "within 30 days", or a spacing/punctuation variant of an
     identifier).
   3 — One number or date is rounded or approximated, one identifier is truncated (e.g., year
     dropped from a resolution number), or one duration is converted to a different unit.
   2 — Multiple values or identifiers rounded, reformatted, truncated, or partially dropped.
   1 — Numbers, dates, or identifiers invented, significantly changed, or contradicted by the
     passage.
   N/A — Answer contains no numerical or citational content. Score this sub-criterion as 5 if N/A.

Output valid JSON only — a list of three objects, one per candidate, in the order the candidates
  were provided (index 0, 1, 2):
[
  {
    "index": 0,
    "grounding": <1-5>,
    "precision": <1-5>,
    "numerical_fidelity": <1-5>,
    "reason": "one short sentence explaining the grades"
  },
  {
    "index": 1,
    "grounding": <1-5>,
    "precision": <1-5>,
    "numerical_fidelity": <1-5>,
    "reason": "..."
  },
  {
    "index": 2,
    "grounding": <1-5>,
    "precision": <1-5>,
    "numerical_fidelity": <1-5>,
    "reason": "..."
  }
]

ACTUAL BATCH SIZE: This request contains exactly 1 candidates. Return exactly 1 grade objects, using indices [0]. Grade only supplied candidates. Any references above to THREE pairs or three example objects describe a typical batch; this actual batch size overrides those counts. All scoring criteria and calibration remain unchanged.
````

### Input 2: user

````text
### TARGET BLOCK — write the questions about THIS text

[EN] Document: CD/PV.844
  Title: I have on my list of speakers for today the representative of Japan.
I have on my list of speakers for today the representative of Japan.
As you are aware, our esteemed colleague and friend, Ambassador Akira Hayashi of Japan, will be leaving the Conference shortly, having been called to other important duties by his Government.
During his time here, he has presented the position of his Government with prodigious skills and talent.
His personal contribution to our collective efforts to bring about a consensus which would allow the start of substantive work of the Conference has been appreciated by all.
I am personally beholden to him for the friendship he has always shown me.
Mr. HAYASHI (Japan): Thank you very much, Mr. President, for your kind words to me and best wishes to me and to my family.
Mr. President, at the outset, I should like to congratulate you most warmly on your assumption of the presidency and wish you every success in discharging your important duties.
I am certain that your wisdom and diplomatic skills will help bring about in the CD the longawaited positive agreement on our work.
My delegation pledges its full cooperation in your endeavours.
I should also like to pay tribute to your predecessor, Ambassador Harald Kreid of Austria, for his initiative and strenuous efforts to promote the start of substantive work in the CD.

### REFERENCED DOCUMENTS — none. The target block cites no other document available in the corpus.

### DOCUMENT CONTEXT — surrounding text of the SAME document, supporting context only. It resolves what the target block leaves implicit; it is never a source of answers.

[EN] Document CD/PV.844 — surrounding passages
[... the TARGET BLOCK appears here ...]

It is unfortunate that my delegation has not yet been able to make a policy statement at this year's session.
I had been waiting for an opportunity conducive to doing so, possibly after the successful adoption of the work programme. Much to my regret, I now have missed that opportunity for good, because today I am speaking for the last time at the CD, while a prospective work programme is still under consideration or possibly even in long hibernation.
After my two and a half years of tenure here, I should today like to state some of my personal observations on the CD.
First of all, I would not be honest if I said, "I am satisfied with the work I have done here and I am leaving with a sense of achievement".
It is regrettable that I have not been able to participate in any substantive negotiations in the CD.

Before I came to Geneva in 1997, I was told that the situation at the CD was not very propitious for the commencement of negotiations on an FMCT, despite the fact that it had long been agreed as its next item for negotiation.
But, honestly, I did not anticipate that such a situation would continue during my entire tenure.
The report of the Tokyo Forum published last year stated as one of its recommendations: "The Tokyo Forum calls on the Conference on Disarmament to revise it procedures, update its work programme, and carry out purposeful work, or suspend its operations.
The consensus rule is causing perpetual deadlock. Consensus among members of the Conference on Disarmament should not be necessary to begin or conclude negotiations on a multilateral convention".
The frustration and the disappointment for those who are within the CD, including myself, are naturally much greater.
But I personally do not agree with this recommendation, since the existence of the consensus rule itself is not the only cause of the sorry state of the CD, and suspension of the CD's operations would certainly not change the situation for the better.

My predecessor, Ambassador Kurokochi, referred to the CD's consensus rule in her farewell speech. In it, while admitting that the consensus rule was indispensable to the CD, she stated: "When a point at issue is a procedural matter which does not prejudge the question of substance, every country should refrain as much as possible from exercising a veto".
This assertion apparently did not obtain much support at the CD.
Instead, I have frequently heard such words of caution as, "Procedure is substance" and "Devils are in detail".
I have to confess that my own experience here during these two and a half years, has made me more sympathetic to the argument of my predecessor.
Different views have been expressed on this famous consensus rule of the CD.
Some advocate adhering scrupulously to this rule in every nook and corner of the CD's operations. Some argue the necessity of a less rigorous application of the rule, especially to procedural matters.
The recent case of this difference is the interpretation of paragraph 5 (d) of CD/1036.

Despite all these disputes on that consensus rule, one thing I should like to stress is that the consensus rule should be taken as distinctly different from granting the right of veto to each member.
If this distinction is not properly made, the rule would inevitably turn out to be a recipe for indecision and no action.
What is essential to the consensus rule, in my view, is the common recognition of the prerequisite for employing the rule. That prerequisite is the fundamental orientation towards achieving compromises for the sake of agreements rather than a pursuit of individual positions by ultimately resorting to the right of veto.
This necessitates opportunities for thorough discussions through which differences among the participants are identified and efforts to narrow such differences are pursued based on self-restraint.
I have the impression - though I hope I am wrong - that the members of the CD have collectively become insensitive to the prerequisite that makes the consensus rule workable.
Such a sense of resignation as, "nothing to do because there is no consensus", is prevailing at the CD.
Clearly something must be done to redress the situation for the purpose of restoring normalcy to the Conference.

This would enhance the transparency of the work of the CD and increase awareness for progress, and would consequently create more chances for consensus to emerge in the CD.
It is my earnest hope that the CD will start its substantial work as soon as possible.
I was told when I arrived in Geneva that the CD was the best club in town. In fact, it is.
I have enjoyed immensely the company of my colleagues and have been tremendously stimulated intellectually.
But the CD should not be complacent with only good comradeship.
The PRESIDENT: I thank Ambassador Hayashi for his moving statement and for the kind words he addressed to me.
Ambassador Hayashi, once again, our very best to you.
I do share your hope that substantive negotiations may begin soon, and that normalcy, as you say, will soon be restored to the work of the Conference.
This concludes my list of speakers for today. Does any delegation wish to take the floor? That does not seem to be the case.

I should now like to take up for a decision the request from Albania to participate as observer in the work of the Conference during this session without first considering it at an informal plenary meeting.
This request is contained in document CD/WP.509, which is before you. May I take it that the Conference agrees to this request?
It was so decided.
The PRESIDENT: This concludes our business for today. Does any other delegation wish to take the floor at this stage? I recognize the distinguished representative of the United States.
Mr. GREY (United States of America): Mr. President, through you, I would like to extend an invitation to all the members and non-member participants of the Conference on Disarmament to attend a presentation by the United States on nuclear disarmament issues.
The presentation will take place here in the Council Chamber on Tuesday, 7 March, starting at 10 a.m. and will be given by Mr. Frank Miller, Principal Deputy Assistant Secretary of Defense for Strategy and Threat Reduction.
Following Mr. Miller's presentation, there will be an opportunity for questions and answers on issues relating to nuclear disarmament.

This presentation will be closed to the public and media in order to encourage condour and vigorous give-and-take.
I took forward to what I am sure will be an interesting and useful exchange of views.
The PRESIDENT: Distinguished colleagues, as you are aware, since I assumed the Presidency of the Conference, I have undertaken a round of intensive consultations with a number of delegations on the programme of work of the Conference. As a result of these efforts, I have circulated to all of you a non-paper containing possible steps towards a programme of work.
The preliminary reactions to my proposals indicate that further consultations will be needed, and I pledge to you that I will use the remaining days of my presidency in an effort to bring about agreement on the early start of our substantive work.
The next plenary meeting of the Conference will be held on Thursday, 9 March 2000, at 10 a.m.

Candidate 0:
  Question: According to the President of the Conference on Disarmament, why was Japan's Ambassador Hayashi leaving in March 2000?
  Answer: having been called to other important duties by his Government
````

### Output: choice 0

Finish reason: `stop`.

````text
The answer is a verbatim span from the target block: "having been called to other important duties by his Government." It answers the question directly.

- **Grounding:** The span is contiguous and explicit. The question's "March 2000" comes from the document context, but it only frames the question and is not part of the answer, so the penalty is small. The answer is nearly verbatim, but it is a participial fragment, which is a minor issue.
- **Precision:** The answer is tight. It is a fragment that begins with "having been", and it could arguably be shortened to "called to other important duties by his Government".
- **Numerical fidelity:** The answer contains no numbers or identifiers, so this is N/A and scores 5.

[
  {
    "index": 0,
    "grounding": 4,
    "precision": 4,
    "numerical_fidelity": 5,
    "reason": "Answer is a verbatim span from the target block stating the reason; it is a participial fragment and could be trimmed slightly, and the question's date comes from context only."
  }
]
````

### Recorded usage

````json
{
  "cached_tokens": 0,
  "completion_tokens": 331,
  "prompt_tokens": 5898,
  "provider_cost": 0.015106,
  "reasoning_tokens": 0
}
````

### Input size diagnostics

````json
{
  "input_characters": 17584,
  "context_capacity_exceeded": null
}
````

## Call 009: faithfulness

Request: `fbc36aacc37242b593af1adaa0b9d809`. Task: `mode/un/2000/cd/pv_844#0/practitioner`.

Model: `anthropic/claude-sonnet-5.5`. UTC: 2026-09-30T17:53:27.928610+00:00.

API status: **response**. Duration: 3.550454 seconds.

### Request settings

````json
{
  "extra_body": {
    "thinking": {
      "budget_tokens": 16000,
      "type": "enabled"
    }
  },
  "max_tokens": 32000
}
````

### Input 1: system

````text
You are a strict faithfulness grader for legal and policy question-answer pairs built from United
  Nations documents.

You will receive a three-section context and THREE question-answer pairs.
The context is:
- "### TARGET BLOCK" — the passage the questions are supposed to be about, in one or more language
  versions.
- "### REFERENCED DOCUMENTS" — other documents CITED by the target block, each supplied as its
  symbol, title, and text — provided ONLY so the target block's citations can be understood, the way
  a footnote helps a reader.
- "### DOCUMENT CONTEXT" — surrounding text of the SAME document (its opening and neighbouring
  passages), supplied so that the target block can be understood: it resolves which mission "the
  Mission" is, which country "the Government" governs, what period a report covers, and similar
  referring expressions.
BOTH supporting sections are for UNDERSTANDING ONLY. Using them to resolve a referring expression in
  the question or answer (naming "the Mission" as UNAMIR, identifying what a cited resolution
  concerns) is legitimate and must NOT be penalised. Using either of them as a source of answer
  substance is a grounding failure — the answer's facts must come from the TARGET BLOCK itself,
  fully.

THREE question-answer pairs (questions may be in any language; each answer matches its question's
  language). Grade each pair on three sub-criteria, each 1–5. Do NOT evaluate query shape or
  retrieval quality — those are handled separately. Focus only on how faithfully each answer
  reflects the supplied text.

GRADING INSTRUCTIONS:
- Grade each of the three pairs independently and against the absolute rubric below — not relative
  to the other two.
- Do not let similarity or dissimilarity between the three pairs influence any individual grade.
- Evaluate each pair on its own merits before moving to the next.

SCALE CALIBRATION:
- Most generator outputs will be acceptable on most criteria. "Acceptable" is not the same as
  "excellent."
- 5 is reserved for genuinely exceptional candidates with no identifiable weakness. If you can point
  to any imperfection, it is not a 5. 5s should be uncommon.
- 4 means the candidate is very good but has exactly one minor, identifiable issue. You must be able
  to name the issue.
- 3 is the default grade for a candidate that is acceptable and does the job, with one clear
  weakness. It is not a punishment grade — most acceptable candidates will receive 3s.
- 2 and 1 are reserved for candidates with real, identifiable problems. Do not avoid using them when
  a candidate qualifies.
- Before assigning any 4 or 5, pause and ask: "What specifically makes this better than a 3?" If you
  cannot answer concretely, the grade is 3.

SUB-CRITERIA:

1. GROUNDING (1–5): Is the answer supported by a contiguous span of the TARGET BLOCK?
   The supporting text means the TARGET BLOCK alone. Resolving a referring expression through the
     REFERENCED DOCUMENTS, the DOCUMENT CONTEXT, or the metadata lines is legitimate disambiguation,
     not an inferential step. Anything more is.
   Cap the grade at 2 if any part of the answer's substance — a fact, figure, list, reason, or
     condition — is stated only in a REFERENCED DOCUMENT or only in the DOCUMENT CONTEXT and not in
     the target block. Cap at 1 if the answer's substance mainly comes from outside the target
     block.
   5 — Answer is taken directly from a single short contiguous span of the target block. Every word
     of the answer is explicitly present or is a trivial rewording of explicit content. No inference
     whatsoever. (Rare.)
   4 — Answer is fully supported but requires reading across two adjacent sentences, OR is from a
     single span with minor trivial rewording that a strict reader might flag.
   3 — Answer is grounded in the target block but requires one small, defensible inferential step —
     connecting a pronoun to its referent, combining a figure with its unit, or similar.
   2 — Answer is partially supported: some parts grounded in the target block, other parts not
     (including parts taken from a REFERENCED DOCUMENT or the DOCUMENT CONTEXT).
   1 — Answer requires significant inference, outside knowledge, or is not in the target block at
     all.
   CITATION RULE (UN): UN texts constantly cite other instruments ("the measures imposed by
     paragraph 20 of resolution 1493 (2003)"). If the answer's substance sits behind such a citation
     rather than in the target block's own words, score at most 2 (1 if the answer consists mainly
     of such content) — REGARDLESS of whether the cited document was supplied in the REFERENCED
     DOCUMENTS section. References exist for understanding, never as answer material.
   ATTRIBUTION RULE (UN): summary records report delegates' statements, letters convey a
     government's position, and reports state the reporting body's findings and estimates. If the
     target block attributes a claim, estimate, or assessment to a speaker or body and the answer
     (or the question it responds to) presents that claim as established fact with the attribution
     stripped, cap GROUNDING at 2 — the supplied text supports the attributed claim, not the bare
     assertion.

2. PRECISION (1–5): Does the answer add unsupported details or padding?
   5 — Answer is the shortest possible span that fully answers the question. Not one extra word. No
     surrounding context, no hedges, no elaboration. (Rare.)
   4 — Answer is grounded and tight but includes one short fragment of adjacent context that could
     have been cut.
   3 — Answer is grounded but includes one unsupported detail, generalization, or piece of padding.
   2 — Answer includes multiple unsupported details, or uses speculative framing ("likely,"
     "approximately," "it seems") where the passage is specific.
   1 — Answer is largely padded with content not in the passage, or is a rewrite rather than an
     extraction.

3. NUMERICAL & CITATIONAL FIDELITY (1–5): Are numbers, dates, amounts, and official identifiers
  reproduced exactly? (JSON key remains "numerical_fidelity".)
   5 — All numbers, dates, durations, monetary amounts, percentages, troop figures, and official
     identifiers (document symbols, resolution and paragraph numbers) match the passage
     character-for-character (e.g., "resolution 2374 (2017)" preserved as-is, not "Resolution 2374";
     "S/1994/565", not "S/1994/565/Rev.1"; "up to 5,500 troops", not "about 5,000 troops"; "within
     30 days", not "in about a month"). Dates rendered in the answer language's standard format
     count as exact if day, month, and year are unchanged ("15 July 1994" for "le 15 juillet 1994").
   4 — All values and identifiers are correct and preserved, but with a trivial formatting
     difference (e.g., "30-day period" vs. "within 30 days", or a spacing/punctuation variant of an
     identifier).
   3 — One number or date is rounded or approximated, one identifier is truncated (e.g., year
     dropped from a resolution number), or one duration is converted to a different unit.
   2 — Multiple values or identifiers rounded, reformatted, truncated, or partially dropped.
   1 — Numbers, dates, or identifiers invented, significantly changed, or contradicted by the
     passage.
   N/A — Answer contains no numerical or citational content. Score this sub-criterion as 5 if N/A.

Output valid JSON only — a list of three objects, one per candidate, in the order the candidates
  were provided (index 0, 1, 2):
[
  {
    "index": 0,
    "grounding": <1-5>,
    "precision": <1-5>,
    "numerical_fidelity": <1-5>,
    "reason": "one short sentence explaining the grades"
  },
  {
    "index": 1,
    "grounding": <1-5>,
    "precision": <1-5>,
    "numerical_fidelity": <1-5>,
    "reason": "..."
  },
  {
    "index": 2,
    "grounding": <1-5>,
    "precision": <1-5>,
    "numerical_fidelity": <1-5>,
    "reason": "..."
  }
]

ACTUAL BATCH SIZE: This request contains exactly 1 candidates. Return exactly 1 grade objects, using indices [0]. Grade only supplied candidates. Any references above to THREE pairs or three example objects describe a typical batch; this actual batch size overrides those counts. All scoring criteria and calibration remain unchanged.
````

### Input 2: user

````text
### TARGET BLOCK — write the questions about THIS text

[EN] Document: CD/PV.844
  Title: I have on my list of speakers for today the representative of Japan.
I have on my list of speakers for today the representative of Japan.
As you are aware, our esteemed colleague and friend, Ambassador Akira Hayashi of Japan, will be leaving the Conference shortly, having been called to other important duties by his Government.
During his time here, he has presented the position of his Government with prodigious skills and talent.
His personal contribution to our collective efforts to bring about a consensus which would allow the start of substantive work of the Conference has been appreciated by all.
I am personally beholden to him for the friendship he has always shown me.
Mr. HAYASHI (Japan): Thank you very much, Mr. President, for your kind words to me and best wishes to me and to my family.
Mr. President, at the outset, I should like to congratulate you most warmly on your assumption of the presidency and wish you every success in discharging your important duties.
I am certain that your wisdom and diplomatic skills will help bring about in the CD the longawaited positive agreement on our work.
My delegation pledges its full cooperation in your endeavours.
I should also like to pay tribute to your predecessor, Ambassador Harald Kreid of Austria, for his initiative and strenuous efforts to promote the start of substantive work in the CD.

### REFERENCED DOCUMENTS — none. The target block cites no other document available in the corpus.

### DOCUMENT CONTEXT — surrounding text of the SAME document, supporting context only. It resolves what the target block leaves implicit; it is never a source of answers.

[EN] Document CD/PV.844 — surrounding passages
[... the TARGET BLOCK appears here ...]

It is unfortunate that my delegation has not yet been able to make a policy statement at this year's session.
I had been waiting for an opportunity conducive to doing so, possibly after the successful adoption of the work programme. Much to my regret, I now have missed that opportunity for good, because today I am speaking for the last time at the CD, while a prospective work programme is still under consideration or possibly even in long hibernation.
After my two and a half years of tenure here, I should today like to state some of my personal observations on the CD.
First of all, I would not be honest if I said, "I am satisfied with the work I have done here and I am leaving with a sense of achievement".
It is regrettable that I have not been able to participate in any substantive negotiations in the CD.

Before I came to Geneva in 1997, I was told that the situation at the CD was not very propitious for the commencement of negotiations on an FMCT, despite the fact that it had long been agreed as its next item for negotiation.
But, honestly, I did not anticipate that such a situation would continue during my entire tenure.
The report of the Tokyo Forum published last year stated as one of its recommendations: "The Tokyo Forum calls on the Conference on Disarmament to revise it procedures, update its work programme, and carry out purposeful work, or suspend its operations.
The consensus rule is causing perpetual deadlock. Consensus among members of the Conference on Disarmament should not be necessary to begin or conclude negotiations on a multilateral convention".
The frustration and the disappointment for those who are within the CD, including myself, are naturally much greater.
But I personally do not agree with this recommendation, since the existence of the consensus rule itself is not the only cause of the sorry state of the CD, and suspension of the CD's operations would certainly not change the situation for the better.

My predecessor, Ambassador Kurokochi, referred to the CD's consensus rule in her farewell speech. In it, while admitting that the consensus rule was indispensable to the CD, she stated: "When a point at issue is a procedural matter which does not prejudge the question of substance, every country should refrain as much as possible from exercising a veto".
This assertion apparently did not obtain much support at the CD.
Instead, I have frequently heard such words of caution as, "Procedure is substance" and "Devils are in detail".
I have to confess that my own experience here during these two and a half years, has made me more sympathetic to the argument of my predecessor.
Different views have been expressed on this famous consensus rule of the CD.
Some advocate adhering scrupulously to this rule in every nook and corner of the CD's operations. Some argue the necessity of a less rigorous application of the rule, especially to procedural matters.
The recent case of this difference is the interpretation of paragraph 5 (d) of CD/1036.

Despite all these disputes on that consensus rule, one thing I should like to stress is that the consensus rule should be taken as distinctly different from granting the right of veto to each member.
If this distinction is not properly made, the rule would inevitably turn out to be a recipe for indecision and no action.
What is essential to the consensus rule, in my view, is the common recognition of the prerequisite for employing the rule. That prerequisite is the fundamental orientation towards achieving compromises for the sake of agreements rather than a pursuit of individual positions by ultimately resorting to the right of veto.
This necessitates opportunities for thorough discussions through which differences among the participants are identified and efforts to narrow such differences are pursued based on self-restraint.
I have the impression - though I hope I am wrong - that the members of the CD have collectively become insensitive to the prerequisite that makes the consensus rule workable.
Such a sense of resignation as, "nothing to do because there is no consensus", is prevailing at the CD.
Clearly something must be done to redress the situation for the purpose of restoring normalcy to the Conference.

This would enhance the transparency of the work of the CD and increase awareness for progress, and would consequently create more chances for consensus to emerge in the CD.
It is my earnest hope that the CD will start its substantial work as soon as possible.
I was told when I arrived in Geneva that the CD was the best club in town. In fact, it is.
I have enjoyed immensely the company of my colleagues and have been tremendously stimulated intellectually.
But the CD should not be complacent with only good comradeship.
The PRESIDENT: I thank Ambassador Hayashi for his moving statement and for the kind words he addressed to me.
Ambassador Hayashi, once again, our very best to you.
I do share your hope that substantive negotiations may begin soon, and that normalcy, as you say, will soon be restored to the work of the Conference.
This concludes my list of speakers for today. Does any delegation wish to take the floor? That does not seem to be the case.

I should now like to take up for a decision the request from Albania to participate as observer in the work of the Conference during this session without first considering it at an informal plenary meeting.
This request is contained in document CD/WP.509, which is before you. May I take it that the Conference agrees to this request?
It was so decided.
The PRESIDENT: This concludes our business for today. Does any other delegation wish to take the floor at this stage? I recognize the distinguished representative of the United States.
Mr. GREY (United States of America): Mr. President, through you, I would like to extend an invitation to all the members and non-member participants of the Conference on Disarmament to attend a presentation by the United States on nuclear disarmament issues.
The presentation will take place here in the Council Chamber on Tuesday, 7 March, starting at 10 a.m. and will be given by Mr. Frank Miller, Principal Deputy Assistant Secretary of Defense for Strategy and Threat Reduction.
Following Mr. Miller's presentation, there will be an opportunity for questions and answers on issues relating to nuclear disarmament.

This presentation will be closed to the public and media in order to encourage condour and vigorous give-and-take.
I took forward to what I am sure will be an interesting and useful exchange of views.
The PRESIDENT: Distinguished colleagues, as you are aware, since I assumed the Presidency of the Conference, I have undertaken a round of intensive consultations with a number of delegations on the programme of work of the Conference. As a result of these efforts, I have circulated to all of you a non-paper containing possible steps towards a programme of work.
The preliminary reactions to my proposals indicate that further consultations will be needed, and I pledge to you that I will use the remaining days of my presidency in an effort to bring about agreement on the early start of our substantive work.
The next plenary meeting of the Conference will be held on Thursday, 9 March 2000, at 10 a.m.

Candidate 0:
  Question: According to the President of the Conference on Disarmament, why was Japan's Ambassador Hayashi leaving in March 2000?
  Answer: having been called to other important duties by his Government
````

### Output: choice 0

Finish reason: `stop`.

````text
Grounding: the answer is a direct span from the target block ("having been called to other important duties by his Government"). The question's "March 2000" comes from the document context, which is legitimate for disambiguation, since the answer itself does not rely on it. The answer is an exact contiguous span.

Precision: the answer is tight, but it starts with a dangling participial phrase ("having been called...") rather than a clean reason. That is a minor wording issue. It contains no extra content.

Numerical fidelity: the answer has no numbers, so this is N/A and scores 5.

Grounding is 5 because the span is verbatim with no inference. A strict reader might flag "March 2000" in the question, but it does not affect the answer.

[
  {
    "index": 0,
    "grounding": 5,
    "precision": 4,
    "numerical_fidelity": 5,
    "reason": "The answer is a verbatim span from the target block. The only flaw is that it is a dangling participial fragment, though it adds nothing unsupported."
  }
]
````

### Recorded usage

````json
{
  "cached_tokens": 0,
  "completion_tokens": 336,
  "prompt_tokens": 5898,
  "provider_cost": 0.015156,
  "reasoning_tokens": 0
}
````

### Input size diagnostics

````json
{
  "input_characters": 17584,
  "context_capacity_exceeded": null
}
````

## Call 010: faithfulness

Request: `305a9282d09d43169834b47b66885c00`. Task: `mode/un/2005/a/59/pv_84#8/semantic`.

Model: `anthropic/claude-sonnet-5.5`. UTC: 2026-09-30T17:55:07.397055+00:00.

API status: **response**. Duration: 2.969987 seconds.

### Request settings

````json
{
  "extra_body": {
    "thinking": {
      "budget_tokens": 16000,
      "type": "enabled"
    }
  },
  "max_tokens": 32000
}
````

### Input 1: system

````text
You are a strict faithfulness grader for legal and policy question-answer pairs built from United
  Nations documents.

You will receive a three-section context and THREE question-answer pairs.
The context is:
- "### TARGET BLOCK" — the passage the questions are supposed to be about, in one or more language
  versions.
- "### REFERENCED DOCUMENTS" — other documents CITED by the target block, each supplied as its
  symbol, title, and text — provided ONLY so the target block's citations can be understood, the way
  a footnote helps a reader.
- "### DOCUMENT CONTEXT" — surrounding text of the SAME document (its opening and neighbouring
  passages), supplied so that the target block can be understood: it resolves which mission "the
  Mission" is, which country "the Government" governs, what period a report covers, and similar
  referring expressions.
BOTH supporting sections are for UNDERSTANDING ONLY. Using them to resolve a referring expression in
  the question or answer (naming "the Mission" as UNAMIR, identifying what a cited resolution
  concerns) is legitimate and must NOT be penalised. Using either of them as a source of answer
  substance is a grounding failure — the answer's facts must come from the TARGET BLOCK itself,
  fully.

THREE question-answer pairs (questions may be in any language; each answer matches its question's
  language). Grade each pair on three sub-criteria, each 1–5. Do NOT evaluate query shape or
  retrieval quality — those are handled separately. Focus only on how faithfully each answer
  reflects the supplied text.

GRADING INSTRUCTIONS:
- Grade each of the three pairs independently and against the absolute rubric below — not relative
  to the other two.
- Do not let similarity or dissimilarity between the three pairs influence any individual grade.
- Evaluate each pair on its own merits before moving to the next.

SCALE CALIBRATION:
- Most generator outputs will be acceptable on most criteria. "Acceptable" is not the same as
  "excellent."
- 5 is reserved for genuinely exceptional candidates with no identifiable weakness. If you can point
  to any imperfection, it is not a 5. 5s should be uncommon.
- 4 means the candidate is very good but has exactly one minor, identifiable issue. You must be able
  to name the issue.
- 3 is the default grade for a candidate that is acceptable and does the job, with one clear
  weakness. It is not a punishment grade — most acceptable candidates will receive 3s.
- 2 and 1 are reserved for candidates with real, identifiable problems. Do not avoid using them when
  a candidate qualifies.
- Before assigning any 4 or 5, pause and ask: "What specifically makes this better than a 3?" If you
  cannot answer concretely, the grade is 3.

SUB-CRITERIA:

1. GROUNDING (1–5): Is the answer supported by a contiguous span of the TARGET BLOCK?
   The supporting text means the TARGET BLOCK alone. Resolving a referring expression through the
     REFERENCED DOCUMENTS, the DOCUMENT CONTEXT, or the metadata lines is legitimate disambiguation,
     not an inferential step. Anything more is.
   Cap the grade at 2 if any part of the answer's substance — a fact, figure, list, reason, or
     condition — is stated only in a REFERENCED DOCUMENT or only in the DOCUMENT CONTEXT and not in
     the target block. Cap at 1 if the answer's substance mainly comes from outside the target
     block.
   5 — Answer is taken directly from a single short contiguous span of the target block. Every word
     of the answer is explicitly present or is a trivial rewording of explicit content. No inference
     whatsoever. (Rare.)
   4 — Answer is fully supported but requires reading across two adjacent sentences, OR is from a
     single span with minor trivial rewording that a strict reader might flag.
   3 — Answer is grounded in the target block but requires one small, defensible inferential step —
     connecting a pronoun to its referent, combining a figure with its unit, or similar.
   2 — Answer is partially supported: some parts grounded in the target block, other parts not
     (including parts taken from a REFERENCED DOCUMENT or the DOCUMENT CONTEXT).
   1 — Answer requires significant inference, outside knowledge, or is not in the target block at
     all.
   CITATION RULE (UN): UN texts constantly cite other instruments ("the measures imposed by
     paragraph 20 of resolution 1493 (2003)"). If the answer's substance sits behind such a citation
     rather than in the target block's own words, score at most 2 (1 if the answer consists mainly
     of such content) — REGARDLESS of whether the cited document was supplied in the REFERENCED
     DOCUMENTS section. References exist for understanding, never as answer material.
   ATTRIBUTION RULE (UN): summary records report delegates' statements, letters convey a
     government's position, and reports state the reporting body's findings and estimates. If the
     target block attributes a claim, estimate, or assessment to a speaker or body and the answer
     (or the question it responds to) presents that claim as established fact with the attribution
     stripped, cap GROUNDING at 2 — the supplied text supports the attributed claim, not the bare
     assertion.

2. PRECISION (1–5): Does the answer add unsupported details or padding?
   5 — Answer is the shortest possible span that fully answers the question. Not one extra word. No
     surrounding context, no hedges, no elaboration. (Rare.)
   4 — Answer is grounded and tight but includes one short fragment of adjacent context that could
     have been cut.
   3 — Answer is grounded but includes one unsupported detail, generalization, or piece of padding.
   2 — Answer includes multiple unsupported details, or uses speculative framing ("likely,"
     "approximately," "it seems") where the passage is specific.
   1 — Answer is largely padded with content not in the passage, or is a rewrite rather than an
     extraction.

3. NUMERICAL & CITATIONAL FIDELITY (1–5): Are numbers, dates, amounts, and official identifiers
  reproduced exactly? (JSON key remains "numerical_fidelity".)
   5 — All numbers, dates, durations, monetary amounts, percentages, troop figures, and official
     identifiers (document symbols, resolution and paragraph numbers) match the passage
     character-for-character (e.g., "resolution 2374 (2017)" preserved as-is, not "Resolution 2374";
     "S/1994/565", not "S/1994/565/Rev.1"; "up to 5,500 troops", not "about 5,000 troops"; "within
     30 days", not "in about a month"). Dates rendered in the answer language's standard format
     count as exact if day, month, and year are unchanged ("15 July 1994" for "le 15 juillet 1994").
   4 — All values and identifiers are correct and preserved, but with a trivial formatting
     difference (e.g., "30-day period" vs. "within 30 days", or a spacing/punctuation variant of an
     identifier).
   3 — One number or date is rounded or approximated, one identifier is truncated (e.g., year
     dropped from a resolution number), or one duration is converted to a different unit.
   2 — Multiple values or identifiers rounded, reformatted, truncated, or partially dropped.
   1 — Numbers, dates, or identifiers invented, significantly changed, or contradicted by the
     passage.
   N/A — Answer contains no numerical or citational content. Score this sub-criterion as 5 if N/A.

Output valid JSON only — a list of three objects, one per candidate, in the order the candidates
  were provided (index 0, 1, 2):
[
  {
    "index": 0,
    "grounding": <1-5>,
    "precision": <1-5>,
    "numerical_fidelity": <1-5>,
    "reason": "one short sentence explaining the grades"
  },
  {
    "index": 1,
    "grounding": <1-5>,
    "precision": <1-5>,
    "numerical_fidelity": <1-5>,
    "reason": "..."
  },
  {
    "index": 2,
    "grounding": <1-5>,
    "precision": <1-5>,
    "numerical_fidelity": <1-5>,
    "reason": "..."
  }
]

ACTUAL BATCH SIZE: This request contains exactly 2 candidates. Return exactly 2 grade objects, using indices [0, 1]. Grade only supplied candidates. Any references above to THREE pairs or three example objects describe a typical batch; this actual batch size overrides those counts. All scoring criteria and calibration remain unchanged.
````

### Input 2: user

````text
### TARGET BLOCK — write the questions about THIS text

[EN] Document: A/59/PV.84
  Title: Mr. Ping
Their disintegration, which presupposes the need for them to be rebuilt, can therefore more properly be attributed to their original lack of viability as States in the strict sense of the word.
It is therefore a fundamental mistake to think that the international community has the capacity, or is entitled, to determine what institutions must be put in place or created as alternatives to a failed, inoperative or inept State that cannot carry out its basic public functions.
To the contrary, we believe that -- as the Charter itself guarantees -- that power belongs solely to peoples exercising their collective and inalienable right to self-determination.
Peacekeeping operations whose goal is to rebuild a State, as appears to be the trend at the United Nations, therefore in fact curtail the right to self-determination of the people who are the object of such operations.
Moreover, by definition such operations are acts of intervention that contravene the Charter that governs the Organization.

### REFERENCED DOCUMENTS — none. The target block cites no other document available in the corpus.

### DOCUMENT CONTEXT — surrounding text of the SAME document, supporting context only. It resolves what the target block leaves implicit; it is never a source of answers.

[EN] Document A/59/PV.84 — surrounding passages
Mr. Ping
(Gabon)

Earthquake in the Indian Ocean
The President (spoke in French): I should like, on behalf of all members of the General Assembly, to extend our deepest sympathy to the Government and the people of Indonesia for the tragic loss of life and material damage that have, once again, resulted from the recent earthquake in the area.
May I also express the hope that the international community will show its solidarity and respond promptly and generously to any request for help from that country.
Agenda item 8 (continued)
Note by the Secretary-General (A/59/239)
The President (spoke in French): As indicated in his note, the Secretary-General has the honour to request, pursuant to rule 15 of the rules of procedure of the General Assembly, the inclusion in the agenda of the fifty-ninth session of the General Assembly of an additional item, entitled "Financing of the United Nations Mission in the Sudan".
It was so decided.

The President (spoke in French): May I take it that the General Assembly, on the proposal of the Secretary-General, wishes to include in the agenda of the current session an additional item, entitled "Financing of the United Nations Mission in the Sudan" under heading I, "Organizational, administrative and other matters"?
The President (spoke in French): The item is therefore included in the agenda as item 164.
In his note, the Secretary-General further requests that the item be allocated to the Fifth Committee. May I take it that the General Assembly, as requested by the Secretary-General, wishes to allocate this item to the Fifth Committee?
The President (spoke in French): The Chairman of the Fifth Committee will be informed of the decision just taken by the General Assembly.
Agenda item 77 (continued)
Comprehensive review of the whole question of peacekeeping operations in all their aspects
Report of the Special Political and Decolonization Committee (Fourth Committee) (A/59/472/Add.1)

The President (spoke in French): I request the Rapporteur of the Special Political and Decolonization Committee (Fourth Committee), Mr. Kais Kabtani of Tunisia, to introduce the report of the Committee.
Mr. Kabtani (Tunisia), Rapporteur of the Special Political and Decolonization Committee (Fourth Committee) (spoke in French): It is an honour for me to introduce to the General Assembly the report of the Special Political and Decolonization Committee (Fourth Committee), issued as document A/59/472/Add.1, submitted under agenda item 77, entitled "Comprehensive review of the whole question of peacekeeping operations in all their aspects".
The Special Political and Decolonization Committee considered this issue at its 15th to 18th meetings, held from 25 to 28 October 2004, during the first portion of the fifty-ninth session of the General Assembly.
At its 27th meeting, held on 23 March 2005, it resumed its consideration and examined the report of the Special Committee on Peacekeeping Operations (A/59/19).
At that same meeting, the Fourth Committee adopted a draft resolution without a vote.

The draft resolution submitted under agenda item 77 is contained in paragraph 7 of the report.
By the operative part of the draft resolution, the General Assembly would welcome the report of the Special Committee on Peacekeeping Operations. It would endorse the proposals, recommendations and conclusions of the Special Committee, contained in paragraphs 22 to 154 of its report, and would urge Member States to take all necessary steps to implement them. It would reiterate the conditions under which the countries that provide personnel can become members of the Special Committee and would decide that the Special Committee should continue its efforts. The Assembly would also request the Special Committee to submit a report on its work to the General Assembly at its sixtieth session.
It is my honour to submit to the General Assembly for consideration and adoption the draft resolution contained in paragraph 7 of document A/59/472/Add.1, entitled "Comprehensive review of the whole question of peacekeeping operations in all their aspects".

The President (spoke in French): If there is no proposal under rule 66 of the rules of procedure, I shall take it that the General Assembly decides not to discuss the report of the Special Political and Decolonization Committee (Fourth Committee) that is before the Assembly today.
The President (spoke in French): Statements will therefore be limited to explanations of vote or position.
The positions of delegations regarding the recommendation of the Special Political and Decolonization Committee have been made clear in the Committee and are reflected in the relevant official records.
May I remind members that, under paragraph 7 of decision 34/401, the General Assembly agreed that
"When the same draft resolution is considered in a Main Committee and in plenary meeting, a delegation should, as far as possible, explain its vote only once, i.e., either in the Committee or in plenary meeting, unless that delegation's vote in plenary meeting is different from its vote in the Committee."

I also wish to remind delegations that, also in accordance with General Assembly decision 34/401, explanations of vote are limited to 10 minutes and should be made by delegations from their seats.
Before we begin to take action on the draft resolution, I should like to inform representatives that we are going to proceed to take a decision in the same manner as was done in the Special Political and Decolonization Committee (Fourth Committee), unless notified to the contrary in advance.
I would like to take this opportunity, on behalf of the Government and the people of the Bolivarian Republic of Venezuela, to convey our most heartfelt condolences to the people of Indonesia in connection with the recent tragedy that has once again struck that country.
I would like to place on record before the Assembly that our delegation will not oppose the draft resolution endorsing the report of the Special Committee on Peacekeeping Operations (A/59/19) that was adopted by the Special Political and Decolonization Committee (Fourth Committee).
However, we would like to make the following explanations.

The Bolivarian Republic of Venezuela would once again like to make known in the Hall its opinion regarding peacekeeping operations as they are currently constituted in line with the provisions of the Charter of the United Nations.
We reaffirm that we have no objection whatever to peacekeeping operations whose provisions and strict purposes are the maintenance of peace, just as such operations have taken place historically.
A look into the ideological construct underpinning the new type of peacekeeping operations prompts us to make a few observations.
The fact is that the idea of a collapsed, failed or impotent State that is employed as the basis for those new operations is devoid of any historical perspective.
That idea tacitly implies that the collapse of a State is the responsibility of the people and Government that find themselves in that situation.
To the contrary, we know that many States that are today labelled as failed States have been failed States from their very beginnings, as they were in the main created as fronts for what in fact were dependent entities that were economically and politically subordinate neo-colonial foreign protectorates or quasi-protectorates.

[... the TARGET BLOCK appears here ...]

Nor do we accept the excuse of humanitarian intervention or the political use of human rights as grounds for the imposition on any State of enforcement measures falling outside the Charter.
A serious precedent in that regard is the recent proposal by the Secretary-General to grant powers to the Security Council, on the basis of the supposed principle of the responsibility to protect, to punish States for crimes stipulated in the Statute of the International Criminal Court.
We are sufficiently aware of the double standards employed by, and the undeclared goals of, those who have a monopoly on labelling such actions.
United Nations peacekeeping operations are solely a tool to carry out the provisions of the Charter.
In order for that to be a reality, peacekeeping operations must strictly adhere to the principles of the consent of the parties involved, impartiality and non-use of force except in cases strictly pertaining to legitimate self-defence.

The mandates of peacekeeping operations must therefore not be ambiguous, so as to avoid skewing the operation and making it possible for the powers it is given to be usurped by United Nations bodies that have no right to them.
Similarly, peacekeeping operations should have the necessary logistical resources to achieve the desired result of lasting and sustainable peace.
Moreover, peacekeeping operations must not take the place of resolving the real underlying causes of conflict.
They must therefore not be a substitute for addressing the root causes that are usually at the heart of major socio-economic problems.
The Bolivarian Republic of Venezuela therefore favours the prevention of conflicts by overcoming the serious problems that lead to instability and to conflict situations, as there can be neither lasting peace nor strengthened democratic institutions without development.
Every decision taken with regard to peacekeeping operations must abide by the fundamental principles of international law as enshrined in the Charter of the United Nations. In other words, there must be full respect for sovereignty, non-interference in internal affairs and self-determination for peoples.

That position is based upon the mandate enshrined in the Constitution of the Bolivarian Republic of Venezuela, whose preamble commits us to promoting peaceful cooperation between nations and the strengthening of Latin American integration in accordance with the principles of non-intervention, the self-determination of peoples, universal and inalienable guarantees of human rights, democratizing international society, nuclear disarmament, ecological balance and the preservation of legal and environmental well-being as humankind's common undeniable patrimony.
The peacekeeping operation in Haiti deserves special mention.
Venezuela does not support any action that could damage, infringe upon, alter or impair the ultimate right of the Haitian people to take decisions for itself with regard to its future, its social and political institutions and its path to development in order to overcome poverty.
Finally, we cannot fail to refer to the responsibility incumbent upon the Security Council when it decides to carry out a peacekeeping operation.
There will also be doubts as to whether it is possible to intervene in any State -- or just in weak ones.

The President (spoke in French): The Assembly will now take a decision on the draft resolution recommended by the Special Political and Decolonization Committee (Fourth Committee) in paragraph 7 of its report (A/59/472/Add.1).
The Special Political and Decolonization Committee (Fourth Committee) adopted the draft resolution without a vote. May take it that the Assembly wishes to do the same?
The draft resolution was adopted (resolution 59/281).
The President (spoke in French): The General Assembly has thus concluded this stage of its consideration of agenda item 77.

Candidate 0:
  Question: What consequence did Venezuela associate with UN peacekeeping missions rebuilding States for self-determination in 2005?
  Answer: therefore in fact curtail the right to self-determination of the people who are the object of such operations

Candidate 1:
  Question: Why did Venezuela consider state-rebuilding peacekeeping operations incompatible with the Charter in 2005?
  Answer: Moreover, by definition such operations are acts of intervention that contravene the Charter that governs the Organization
````

### Output: choice 0

Finish reason: `stop`.

````text
[
  {
    "index": 0,
    "grounding": 4,
    "precision": 4,
    "numerical_fidelity": 5,
    "reason": "The answer is a verbatim span, but it begins with the fragment 'therefore in fact' and the question attributes the view to Venezuela, which only the document context names. The 'in 2005' framing is also a minor point."
  },
  {
    "index": 1,
    "grounding": 4,
    "precision": 4,
    "numerical_fidelity": 5,
    "reason": "The answer is a verbatim sentence that gives the reason directly. It includes the padding 'Moreover,' and the question's attribution to Venezuela relies on context."
  }
]
````

### Recorded usage

````json
{
  "cached_tokens": 0,
  "completion_tokens": 236,
  "prompt_tokens": 7155,
  "provider_cost": 0.01667,
  "reasoning_tokens": 0
}
````

### Input size diagnostics

````json
{
  "input_characters": 21565,
  "context_capacity_exceeded": null
}
````

## Call 011: faithfulness

Request: `ceffea7ef7c948d8bcc664b91e31a884`. Task: `mode/un/2005/a/59/pv_84#8/lookup`.

Model: `anthropic/claude-sonnet-5.5`. UTC: 2026-09-30T17:55:07.397740+00:00.

API status: **response**. Duration: 8.290206 seconds.

### Request settings

````json
{
  "extra_body": {
    "thinking": {
      "budget_tokens": 16000,
      "type": "enabled"
    }
  },
  "max_tokens": 32000
}
````

### Input 1: system

````text
You are a strict faithfulness grader for legal and policy question-answer pairs built from United
  Nations documents.

You will receive a three-section context and THREE question-answer pairs.
The context is:
- "### TARGET BLOCK" — the passage the questions are supposed to be about, in one or more language
  versions.
- "### REFERENCED DOCUMENTS" — other documents CITED by the target block, each supplied as its
  symbol, title, and text — provided ONLY so the target block's citations can be understood, the way
  a footnote helps a reader.
- "### DOCUMENT CONTEXT" — surrounding text of the SAME document (its opening and neighbouring
  passages), supplied so that the target block can be understood: it resolves which mission "the
  Mission" is, which country "the Government" governs, what period a report covers, and similar
  referring expressions.
BOTH supporting sections are for UNDERSTANDING ONLY. Using them to resolve a referring expression in
  the question or answer (naming "the Mission" as UNAMIR, identifying what a cited resolution
  concerns) is legitimate and must NOT be penalised. Using either of them as a source of answer
  substance is a grounding failure — the answer's facts must come from the TARGET BLOCK itself,
  fully.

THREE question-answer pairs (questions may be in any language; each answer matches its question's
  language). Grade each pair on three sub-criteria, each 1–5. Do NOT evaluate query shape or
  retrieval quality — those are handled separately. Focus only on how faithfully each answer
  reflects the supplied text.

GRADING INSTRUCTIONS:
- Grade each of the three pairs independently and against the absolute rubric below — not relative
  to the other two.
- Do not let similarity or dissimilarity between the three pairs influence any individual grade.
- Evaluate each pair on its own merits before moving to the next.

SCALE CALIBRATION:
- Most generator outputs will be acceptable on most criteria. "Acceptable" is not the same as
  "excellent."
- 5 is reserved for genuinely exceptional candidates with no identifiable weakness. If you can point
  to any imperfection, it is not a 5. 5s should be uncommon.
- 4 means the candidate is very good but has exactly one minor, identifiable issue. You must be able
  to name the issue.
- 3 is the default grade for a candidate that is acceptable and does the job, with one clear
  weakness. It is not a punishment grade — most acceptable candidates will receive 3s.
- 2 and 1 are reserved for candidates with real, identifiable problems. Do not avoid using them when
  a candidate qualifies.
- Before assigning any 4 or 5, pause and ask: "What specifically makes this better than a 3?" If you
  cannot answer concretely, the grade is 3.

SUB-CRITERIA:

1. GROUNDING (1–5): Is the answer supported by a contiguous span of the TARGET BLOCK?
   The supporting text means the TARGET BLOCK alone. Resolving a referring expression through the
     REFERENCED DOCUMENTS, the DOCUMENT CONTEXT, or the metadata lines is legitimate disambiguation,
     not an inferential step. Anything more is.
   Cap the grade at 2 if any part of the answer's substance — a fact, figure, list, reason, or
     condition — is stated only in a REFERENCED DOCUMENT or only in the DOCUMENT CONTEXT and not in
     the target block. Cap at 1 if the answer's substance mainly comes from outside the target
     block.
   5 — Answer is taken directly from a single short contiguous span of the target block. Every word
     of the answer is explicitly present or is a trivial rewording of explicit content. No inference
     whatsoever. (Rare.)
   4 — Answer is fully supported but requires reading across two adjacent sentences, OR is from a
     single span with minor trivial rewording that a strict reader might flag.
   3 — Answer is grounded in the target block but requires one small, defensible inferential step —
     connecting a pronoun to its referent, combining a figure with its unit, or similar.
   2 — Answer is partially supported: some parts grounded in the target block, other parts not
     (including parts taken from a REFERENCED DOCUMENT or the DOCUMENT CONTEXT).
   1 — Answer requires significant inference, outside knowledge, or is not in the target block at
     all.
   CITATION RULE (UN): UN texts constantly cite other instruments ("the measures imposed by
     paragraph 20 of resolution 1493 (2003)"). If the answer's substance sits behind such a citation
     rather than in the target block's own words, score at most 2 (1 if the answer consists mainly
     of such content) — REGARDLESS of whether the cited document was supplied in the REFERENCED
     DOCUMENTS section. References exist for understanding, never as answer material.
   ATTRIBUTION RULE (UN): summary records report delegates' statements, letters convey a
     government's position, and reports state the reporting body's findings and estimates. If the
     target block attributes a claim, estimate, or assessment to a speaker or body and the answer
     (or the question it responds to) presents that claim as established fact with the attribution
     stripped, cap GROUNDING at 2 — the supplied text supports the attributed claim, not the bare
     assertion.

2. PRECISION (1–5): Does the answer add unsupported details or padding?
   5 — Answer is the shortest possible span that fully answers the question. Not one extra word. No
     surrounding context, no hedges, no elaboration. (Rare.)
   4 — Answer is grounded and tight but includes one short fragment of adjacent context that could
     have been cut.
   3 — Answer is grounded but includes one unsupported detail, generalization, or piece of padding.
   2 — Answer includes multiple unsupported details, or uses speculative framing ("likely,"
     "approximately," "it seems") where the passage is specific.
   1 — Answer is largely padded with content not in the passage, or is a rewrite rather than an
     extraction.

3. NUMERICAL & CITATIONAL FIDELITY (1–5): Are numbers, dates, amounts, and official identifiers
  reproduced exactly? (JSON key remains "numerical_fidelity".)
   5 — All numbers, dates, durations, monetary amounts, percentages, troop figures, and official
     identifiers (document symbols, resolution and paragraph numbers) match the passage
     character-for-character (e.g., "resolution 2374 (2017)" preserved as-is, not "Resolution 2374";
     "S/1994/565", not "S/1994/565/Rev.1"; "up to 5,500 troops", not "about 5,000 troops"; "within
     30 days", not "in about a month"). Dates rendered in the answer language's standard format
     count as exact if day, month, and year are unchanged ("15 July 1994" for "le 15 juillet 1994").
   4 — All values and identifiers are correct and preserved, but with a trivial formatting
     difference (e.g., "30-day period" vs. "within 30 days", or a spacing/punctuation variant of an
     identifier).
   3 — One number or date is rounded or approximated, one identifier is truncated (e.g., year
     dropped from a resolution number), or one duration is converted to a different unit.
   2 — Multiple values or identifiers rounded, reformatted, truncated, or partially dropped.
   1 — Numbers, dates, or identifiers invented, significantly changed, or contradicted by the
     passage.
   N/A — Answer contains no numerical or citational content. Score this sub-criterion as 5 if N/A.

Output valid JSON only — a list of three objects, one per candidate, in the order the candidates
  were provided (index 0, 1, 2):
[
  {
    "index": 0,
    "grounding": <1-5>,
    "precision": <1-5>,
    "numerical_fidelity": <1-5>,
    "reason": "one short sentence explaining the grades"
  },
  {
    "index": 1,
    "grounding": <1-5>,
    "precision": <1-5>,
    "numerical_fidelity": <1-5>,
    "reason": "..."
  },
  {
    "index": 2,
    "grounding": <1-5>,
    "precision": <1-5>,
    "numerical_fidelity": <1-5>,
    "reason": "..."
  }
]

ACTUAL BATCH SIZE: This request contains exactly 2 candidates. Return exactly 2 grade objects, using indices [0, 1]. Grade only supplied candidates. Any references above to THREE pairs or three example objects describe a typical batch; this actual batch size overrides those counts. All scoring criteria and calibration remain unchanged.
````

### Input 2: user

````text
### TARGET BLOCK — write the questions about THIS text

[EN] Document: A/59/PV.84
  Title: Mr. Ping
Their disintegration, which presupposes the need for them to be rebuilt, can therefore more properly be attributed to their original lack of viability as States in the strict sense of the word.
It is therefore a fundamental mistake to think that the international community has the capacity, or is entitled, to determine what institutions must be put in place or created as alternatives to a failed, inoperative or inept State that cannot carry out its basic public functions.
To the contrary, we believe that -- as the Charter itself guarantees -- that power belongs solely to peoples exercising their collective and inalienable right to self-determination.
Peacekeeping operations whose goal is to rebuild a State, as appears to be the trend at the United Nations, therefore in fact curtail the right to self-determination of the people who are the object of such operations.
Moreover, by definition such operations are acts of intervention that contravene the Charter that governs the Organization.

### REFERENCED DOCUMENTS — none. The target block cites no other document available in the corpus.

### DOCUMENT CONTEXT — surrounding text of the SAME document, supporting context only. It resolves what the target block leaves implicit; it is never a source of answers.

[EN] Document A/59/PV.84 — surrounding passages
Mr. Ping
(Gabon)

Earthquake in the Indian Ocean
The President (spoke in French): I should like, on behalf of all members of the General Assembly, to extend our deepest sympathy to the Government and the people of Indonesia for the tragic loss of life and material damage that have, once again, resulted from the recent earthquake in the area.
May I also express the hope that the international community will show its solidarity and respond promptly and generously to any request for help from that country.
Agenda item 8 (continued)
Note by the Secretary-General (A/59/239)
The President (spoke in French): As indicated in his note, the Secretary-General has the honour to request, pursuant to rule 15 of the rules of procedure of the General Assembly, the inclusion in the agenda of the fifty-ninth session of the General Assembly of an additional item, entitled "Financing of the United Nations Mission in the Sudan".
It was so decided.

The President (spoke in French): May I take it that the General Assembly, on the proposal of the Secretary-General, wishes to include in the agenda of the current session an additional item, entitled "Financing of the United Nations Mission in the Sudan" under heading I, "Organizational, administrative and other matters"?
The President (spoke in French): The item is therefore included in the agenda as item 164.
In his note, the Secretary-General further requests that the item be allocated to the Fifth Committee. May I take it that the General Assembly, as requested by the Secretary-General, wishes to allocate this item to the Fifth Committee?
The President (spoke in French): The Chairman of the Fifth Committee will be informed of the decision just taken by the General Assembly.
Agenda item 77 (continued)
Comprehensive review of the whole question of peacekeeping operations in all their aspects
Report of the Special Political and Decolonization Committee (Fourth Committee) (A/59/472/Add.1)

The President (spoke in French): I request the Rapporteur of the Special Political and Decolonization Committee (Fourth Committee), Mr. Kais Kabtani of Tunisia, to introduce the report of the Committee.
Mr. Kabtani (Tunisia), Rapporteur of the Special Political and Decolonization Committee (Fourth Committee) (spoke in French): It is an honour for me to introduce to the General Assembly the report of the Special Political and Decolonization Committee (Fourth Committee), issued as document A/59/472/Add.1, submitted under agenda item 77, entitled "Comprehensive review of the whole question of peacekeeping operations in all their aspects".
The Special Political and Decolonization Committee considered this issue at its 15th to 18th meetings, held from 25 to 28 October 2004, during the first portion of the fifty-ninth session of the General Assembly.
At its 27th meeting, held on 23 March 2005, it resumed its consideration and examined the report of the Special Committee on Peacekeeping Operations (A/59/19).
At that same meeting, the Fourth Committee adopted a draft resolution without a vote.

The draft resolution submitted under agenda item 77 is contained in paragraph 7 of the report.
By the operative part of the draft resolution, the General Assembly would welcome the report of the Special Committee on Peacekeeping Operations. It would endorse the proposals, recommendations and conclusions of the Special Committee, contained in paragraphs 22 to 154 of its report, and would urge Member States to take all necessary steps to implement them. It would reiterate the conditions under which the countries that provide personnel can become members of the Special Committee and would decide that the Special Committee should continue its efforts. The Assembly would also request the Special Committee to submit a report on its work to the General Assembly at its sixtieth session.
It is my honour to submit to the General Assembly for consideration and adoption the draft resolution contained in paragraph 7 of document A/59/472/Add.1, entitled "Comprehensive review of the whole question of peacekeeping operations in all their aspects".

The President (spoke in French): If there is no proposal under rule 66 of the rules of procedure, I shall take it that the General Assembly decides not to discuss the report of the Special Political and Decolonization Committee (Fourth Committee) that is before the Assembly today.
The President (spoke in French): Statements will therefore be limited to explanations of vote or position.
The positions of delegations regarding the recommendation of the Special Political and Decolonization Committee have been made clear in the Committee and are reflected in the relevant official records.
May I remind members that, under paragraph 7 of decision 34/401, the General Assembly agreed that
"When the same draft resolution is considered in a Main Committee and in plenary meeting, a delegation should, as far as possible, explain its vote only once, i.e., either in the Committee or in plenary meeting, unless that delegation's vote in plenary meeting is different from its vote in the Committee."

I also wish to remind delegations that, also in accordance with General Assembly decision 34/401, explanations of vote are limited to 10 minutes and should be made by delegations from their seats.
Before we begin to take action on the draft resolution, I should like to inform representatives that we are going to proceed to take a decision in the same manner as was done in the Special Political and Decolonization Committee (Fourth Committee), unless notified to the contrary in advance.
I would like to take this opportunity, on behalf of the Government and the people of the Bolivarian Republic of Venezuela, to convey our most heartfelt condolences to the people of Indonesia in connection with the recent tragedy that has once again struck that country.
I would like to place on record before the Assembly that our delegation will not oppose the draft resolution endorsing the report of the Special Committee on Peacekeeping Operations (A/59/19) that was adopted by the Special Political and Decolonization Committee (Fourth Committee).
However, we would like to make the following explanations.

The Bolivarian Republic of Venezuela would once again like to make known in the Hall its opinion regarding peacekeeping operations as they are currently constituted in line with the provisions of the Charter of the United Nations.
We reaffirm that we have no objection whatever to peacekeeping operations whose provisions and strict purposes are the maintenance of peace, just as such operations have taken place historically.
A look into the ideological construct underpinning the new type of peacekeeping operations prompts us to make a few observations.
The fact is that the idea of a collapsed, failed or impotent State that is employed as the basis for those new operations is devoid of any historical perspective.
That idea tacitly implies that the collapse of a State is the responsibility of the people and Government that find themselves in that situation.
To the contrary, we know that many States that are today labelled as failed States have been failed States from their very beginnings, as they were in the main created as fronts for what in fact were dependent entities that were economically and politically subordinate neo-colonial foreign protectorates or quasi-protectorates.

[... the TARGET BLOCK appears here ...]

Nor do we accept the excuse of humanitarian intervention or the political use of human rights as grounds for the imposition on any State of enforcement measures falling outside the Charter.
A serious precedent in that regard is the recent proposal by the Secretary-General to grant powers to the Security Council, on the basis of the supposed principle of the responsibility to protect, to punish States for crimes stipulated in the Statute of the International Criminal Court.
We are sufficiently aware of the double standards employed by, and the undeclared goals of, those who have a monopoly on labelling such actions.
United Nations peacekeeping operations are solely a tool to carry out the provisions of the Charter.
In order for that to be a reality, peacekeeping operations must strictly adhere to the principles of the consent of the parties involved, impartiality and non-use of force except in cases strictly pertaining to legitimate self-defence.

The mandates of peacekeeping operations must therefore not be ambiguous, so as to avoid skewing the operation and making it possible for the powers it is given to be usurped by United Nations bodies that have no right to them.
Similarly, peacekeeping operations should have the necessary logistical resources to achieve the desired result of lasting and sustainable peace.
Moreover, peacekeeping operations must not take the place of resolving the real underlying causes of conflict.
They must therefore not be a substitute for addressing the root causes that are usually at the heart of major socio-economic problems.
The Bolivarian Republic of Venezuela therefore favours the prevention of conflicts by overcoming the serious problems that lead to instability and to conflict situations, as there can be neither lasting peace nor strengthened democratic institutions without development.
Every decision taken with regard to peacekeeping operations must abide by the fundamental principles of international law as enshrined in the Charter of the United Nations. In other words, there must be full respect for sovereignty, non-interference in internal affairs and self-determination for peoples.

That position is based upon the mandate enshrined in the Constitution of the Bolivarian Republic of Venezuela, whose preamble commits us to promoting peaceful cooperation between nations and the strengthening of Latin American integration in accordance with the principles of non-intervention, the self-determination of peoples, universal and inalienable guarantees of human rights, democratizing international society, nuclear disarmament, ecological balance and the preservation of legal and environmental well-being as humankind's common undeniable patrimony.
The peacekeeping operation in Haiti deserves special mention.
Venezuela does not support any action that could damage, infringe upon, alter or impair the ultimate right of the Haitian people to take decisions for itself with regard to its future, its social and political institutions and its path to development in order to overcome poverty.
Finally, we cannot fail to refer to the responsibility incumbent upon the Security Council when it decides to carry out a peacekeeping operation.
There will also be doubts as to whether it is possible to intervene in any State -- or just in weak ones.

The President (spoke in French): The Assembly will now take a decision on the draft resolution recommended by the Special Political and Decolonization Committee (Fourth Committee) in paragraph 7 of its report (A/59/472/Add.1).
The Special Political and Decolonization Committee (Fourth Committee) adopted the draft resolution without a vote. May take it that the Assembly wishes to do the same?
The draft resolution was adopted (resolution 59/281).
The President (spoke in French): The General Assembly has thus concluded this stage of its consideration of agenda item 77.

Candidate 0:
  Question: What right did Mr. Ping of Gabon say state-rebuilding peacekeeping operations curtail in the 2005 General Assembly meeting record on peacekeeping operations?
  Answer: the right to self-determination

Candidate 1:
  Question: Who did Mr. Ping of Gabon identify as solely empowered to determine replacement institutions in the 2005 General Assembly meeting record on peacekeeping operations?
  Answer: peoples exercising their collective and inalienable right to self-determination
````

### Output: choice 0

Finish reason: `stop`.

````text
[
  {
    "index": 0,
    "grounding": 5,
    "precision": 5,
    "numerical_fidelity": 5,
    "reason": "The answer is a verbatim span from the sentence 'curtail the right to self-determination', and the question keeps the attribution to the speaker."
  },
  {
    "index": 1,
    "grounding": 4,
    "precision": 5,
    "numerical_fidelity": 5,
    "reason": "The answer is a verbatim phrase, but 'that power' must be linked to determining institutions through the preceding sentence, so two adjacent sentences are needed."
  }
]
````

### Recorded usage

````json
{
  "cached_tokens": 0,
  "completion_tokens": 722,
  "prompt_tokens": 7160,
  "provider_cost": 0.02154,
  "reasoning_tokens": 512
}
````

### Input size diagnostics

````json
{
  "input_characters": 21539,
  "context_capacity_exceeded": null
}
````

## Call 012: faithfulness

Request: `8db8a65f20c040bcb846074bb1e6e55c`. Task: `mode/un/2009/a/c_2/64/sr_16#3/semantic`.

Model: `anthropic/claude-sonnet-5.5`. UTC: 2026-09-30T17:56:01.385283+00:00.

API status: **response**. Duration: 3.285699 seconds.

### Request settings

````json
{
  "extra_body": {
    "thinking": {
      "budget_tokens": 16000,
      "type": "enabled"
    }
  },
  "max_tokens": 32000
}
````

### Input 1: system

````text
You are a strict faithfulness grader for legal and policy question-answer pairs built from United
  Nations documents.

You will receive a three-section context and THREE question-answer pairs.
The context is:
- "### TARGET BLOCK" — the passage the questions are supposed to be about, in one or more language
  versions.
- "### REFERENCED DOCUMENTS" — other documents CITED by the target block, each supplied as its
  symbol, title, and text — provided ONLY so the target block's citations can be understood, the way
  a footnote helps a reader.
- "### DOCUMENT CONTEXT" — surrounding text of the SAME document (its opening and neighbouring
  passages), supplied so that the target block can be understood: it resolves which mission "the
  Mission" is, which country "the Government" governs, what period a report covers, and similar
  referring expressions.
BOTH supporting sections are for UNDERSTANDING ONLY. Using them to resolve a referring expression in
  the question or answer (naming "the Mission" as UNAMIR, identifying what a cited resolution
  concerns) is legitimate and must NOT be penalised. Using either of them as a source of answer
  substance is a grounding failure — the answer's facts must come from the TARGET BLOCK itself,
  fully.

THREE question-answer pairs (questions may be in any language; each answer matches its question's
  language). Grade each pair on three sub-criteria, each 1–5. Do NOT evaluate query shape or
  retrieval quality — those are handled separately. Focus only on how faithfully each answer
  reflects the supplied text.

GRADING INSTRUCTIONS:
- Grade each of the three pairs independently and against the absolute rubric below — not relative
  to the other two.
- Do not let similarity or dissimilarity between the three pairs influence any individual grade.
- Evaluate each pair on its own merits before moving to the next.

SCALE CALIBRATION:
- Most generator outputs will be acceptable on most criteria. "Acceptable" is not the same as
  "excellent."
- 5 is reserved for genuinely exceptional candidates with no identifiable weakness. If you can point
  to any imperfection, it is not a 5. 5s should be uncommon.
- 4 means the candidate is very good but has exactly one minor, identifiable issue. You must be able
  to name the issue.
- 3 is the default grade for a candidate that is acceptable and does the job, with one clear
  weakness. It is not a punishment grade — most acceptable candidates will receive 3s.
- 2 and 1 are reserved for candidates with real, identifiable problems. Do not avoid using them when
  a candidate qualifies.
- Before assigning any 4 or 5, pause and ask: "What specifically makes this better than a 3?" If you
  cannot answer concretely, the grade is 3.

SUB-CRITERIA:

1. GROUNDING (1–5): Is the answer supported by a contiguous span of the TARGET BLOCK?
   The supporting text means the TARGET BLOCK alone. Resolving a referring expression through the
     REFERENCED DOCUMENTS, the DOCUMENT CONTEXT, or the metadata lines is legitimate disambiguation,
     not an inferential step. Anything more is.
   Cap the grade at 2 if any part of the answer's substance — a fact, figure, list, reason, or
     condition — is stated only in a REFERENCED DOCUMENT or only in the DOCUMENT CONTEXT and not in
     the target block. Cap at 1 if the answer's substance mainly comes from outside the target
     block.
   5 — Answer is taken directly from a single short contiguous span of the target block. Every word
     of the answer is explicitly present or is a trivial rewording of explicit content. No inference
     whatsoever. (Rare.)
   4 — Answer is fully supported but requires reading across two adjacent sentences, OR is from a
     single span with minor trivial rewording that a strict reader might flag.
   3 — Answer is grounded in the target block but requires one small, defensible inferential step —
     connecting a pronoun to its referent, combining a figure with its unit, or similar.
   2 — Answer is partially supported: some parts grounded in the target block, other parts not
     (including parts taken from a REFERENCED DOCUMENT or the DOCUMENT CONTEXT).
   1 — Answer requires significant inference, outside knowledge, or is not in the target block at
     all.
   CITATION RULE (UN): UN texts constantly cite other instruments ("the measures imposed by
     paragraph 20 of resolution 1493 (2003)"). If the answer's substance sits behind such a citation
     rather than in the target block's own words, score at most 2 (1 if the answer consists mainly
     of such content) — REGARDLESS of whether the cited document was supplied in the REFERENCED
     DOCUMENTS section. References exist for understanding, never as answer material.
   ATTRIBUTION RULE (UN): summary records report delegates' statements, letters convey a
     government's position, and reports state the reporting body's findings and estimates. If the
     target block attributes a claim, estimate, or assessment to a speaker or body and the answer
     (or the question it responds to) presents that claim as established fact with the attribution
     stripped, cap GROUNDING at 2 — the supplied text supports the attributed claim, not the bare
     assertion.

2. PRECISION (1–5): Does the answer add unsupported details or padding?
   5 — Answer is the shortest possible span that fully answers the question. Not one extra word. No
     surrounding context, no hedges, no elaboration. (Rare.)
   4 — Answer is grounded and tight but includes one short fragment of adjacent context that could
     have been cut.
   3 — Answer is grounded but includes one unsupported detail, generalization, or piece of padding.
   2 — Answer includes multiple unsupported details, or uses speculative framing ("likely,"
     "approximately," "it seems") where the passage is specific.
   1 — Answer is largely padded with content not in the passage, or is a rewrite rather than an
     extraction.

3. NUMERICAL & CITATIONAL FIDELITY (1–5): Are numbers, dates, amounts, and official identifiers
  reproduced exactly? (JSON key remains "numerical_fidelity".)
   5 — All numbers, dates, durations, monetary amounts, percentages, troop figures, and official
     identifiers (document symbols, resolution and paragraph numbers) match the passage
     character-for-character (e.g., "resolution 2374 (2017)" preserved as-is, not "Resolution 2374";
     "S/1994/565", not "S/1994/565/Rev.1"; "up to 5,500 troops", not "about 5,000 troops"; "within
     30 days", not "in about a month"). Dates rendered in the answer language's standard format
     count as exact if day, month, and year are unchanged ("15 July 1994" for "le 15 juillet 1994").
   4 — All values and identifiers are correct and preserved, but with a trivial formatting
     difference (e.g., "30-day period" vs. "within 30 days", or a spacing/punctuation variant of an
     identifier).
   3 — One number or date is rounded or approximated, one identifier is truncated (e.g., year
     dropped from a resolution number), or one duration is converted to a different unit.
   2 — Multiple values or identifiers rounded, reformatted, truncated, or partially dropped.
   1 — Numbers, dates, or identifiers invented, significantly changed, or contradicted by the
     passage.
   N/A — Answer contains no numerical or citational content. Score this sub-criterion as 5 if N/A.

Output valid JSON only — a list of three objects, one per candidate, in the order the candidates
  were provided (index 0, 1, 2):
[
  {
    "index": 0,
    "grounding": <1-5>,
    "precision": <1-5>,
    "numerical_fidelity": <1-5>,
    "reason": "one short sentence explaining the grades"
  },
  {
    "index": 1,
    "grounding": <1-5>,
    "precision": <1-5>,
    "numerical_fidelity": <1-5>,
    "reason": "..."
  },
  {
    "index": 2,
    "grounding": <1-5>,
    "precision": <1-5>,
    "numerical_fidelity": <1-5>,
    "reason": "..."
  }
]

ACTUAL BATCH SIZE: This request contains exactly 2 candidates. Return exactly 2 grade objects, using indices [0, 1]. Grade only supplied candidates. Any references above to THREE pairs or three example objects describe a typical batch; this actual batch size overrides those counts. All scoring criteria and calibration remain unchanged.
````

### Input 2: user

````text
### TARGET BLOCK — write the questions about THIS text

[EN] Document: A/C.2/64/SR.16
  Title: (b) Preventing and combating corrupt practices and transfer of assets of illicit origin and returning such assets, in particular to the countries of origin, consistent with the United Nations Convention against Corruption
UNODC also supported the creation and strengthening of regional networks of asset recovery focal points, which could further the dialogue between requesting and requested States.
In view of the growing size and work of the Conference of the States Parties, the Global Forum would then become a public/private partnership forum bringing together political and business leaders.
9. He called on States to continue to engage in constructive dialogue with a view to arriving at consensus decisions at the Conference of the States Parties, particularly with regard to the review mechanisms supported by the Group of Twenty (G-20).
The General Assembly could support the Conference by encouraging States that had not yet done so to ratify or accede to the Convention and encouraging its implementation by Member States.
The accomplishment of such tasks would be feasible only if Member States provided UNODC with strong support so that it would have the resources needed to make the Convention's provisions operational and fully effective.

### REFERENCED DOCUMENTS — none. The target block cites no other document available in the corpus.

### DOCUMENT CONTEXT — surrounding text of the SAME document, supporting context only. It resolves what the target block leaves implicit; it is never a source of answers.

[EN] Document A/C.2/64/SR.16 — surrounding passages
(b) Preventing and combating corrupt practices and transfer of assets of illicit origin and returning such assets, in particular to the countries of origin, consistent with the United Nations Convention against Corruption
(c) Science and technology for development
In the absence of Mr. Park In-kook (Republic of Korea), Mr. Mohamed Cherif Diallo (Guinea), Vice-Chairperson, took the Chair.

1. Ms. Miroux (United Nations Conference on Trade and Development (UNCTAD)), introducing the report of the Secretary-General on science and technology for development (A/64/168), drew attention to its salient points.
Science, technology and innovation had a crucial role to play in stimulating long-term social and economic development and in helping developing countries to meet the Millennium Development Goals (MDGs).
To that end, developing countries would require support to build their technological capacity.
3. Mr. Vlassis (United Nations Office on Drugs and Crime (UNODC)) introduced the report of the Secretary-General on preventing and combating corrupt practices and transfer of assets of illicit origin and returning such assets, in particular to the countries of origin, consistent with the United Nations Convention against Corruption (A/64/122).
Since July, when the report had been finalized, a further five States had ratified the Convention, bringing the number of parties up to 141.
At the third session of the Conference of the States Parties to the Convention, to be held in Doha in November 2009, the most important item for decision would be the establishment of a mechanism to review the implementation of the Convention.

Although a number of meetings had helped to advance the work of the open-ended Working Group on Review of the Implementation of the Convention, further meetings would be held in an effort to reach consensus on pending issues before the Doha session.
4. One matter on which the States parties were agreed was that the review should be based on their own self-assessments.
5. Asset recovery continued to enjoy high priority in the work of the Conference of the States Parties.
Moreover, it had stressed the need for practical tools and guides for the implementation of chapter V of the Convention and networks to build trust and had highlighted the importance of training and capacity-building.
The joint Stolen Asset Recovery initiative (StAR) of UNODC and the World Bank was the main medium through which UNODC acted on the Working Group's recommendations.
The initiative was further conducting a number of policy studies on related topics which would be presented in Doha.

[... the TARGET BLOCK appears here ...]

11. The Chairperson invited the Committee to engage in a general discussion on the item.
12. Mr. Daoud (Sudan), speaking on behalf of the Group of 77 and China, said that globalization posed special difficulties to developing countries and had left the least developed among them on the margins of the world economy.
The globalization of markets meant that economic meltdowns in developed country markets quickly spread to other markets.
Such internationalization of crises brought out the importance of global governance and sound regulatory frameworks that would enable developing countries to enjoy their right to development geared to their own realities.
13. Moreover, while each country bore primary responsibility for its own development, the benefits of globalization could not be shared equitably without strengthened international cooperation and a global partnership for development.
That meant giving developing countries greater voice and participation in international economic decision-making and norm-setting, in particular by reforming multilateral institutions and global governance.

14. In an increasingly knowledge-based world economy, access to technology was vital for development and should be made more available to developing countries; it was a major source of inequality between them and the developed world.
Such access would help them to advance significantly in agriculture, health, energy, trade, water management and environmental protection.
15. The Group of 77 and China invited the States parties to the Convention against Corruption to take further steps to implement it, notably through initiatives for asset recovery, technical assistance and capacity-building.
He stressed the need to continue seeking creative ways to increase collaboration between developing countries and developed countries and their financial institutions in uncovering illicit financial operations, locating the funds and arranging for their return.
Progress on trade and investment agreements and the participation of developing countries in international economic decision-making would be crucial to the global partnership for development.
In that context, he called on the international community to give special attention to the needs of the developing countries, the least developed countries, the landlocked developing countries and the small island developing States.

16. Ms. Ornbrant (Sweden), speaking on behalf of the European Union; the candidate countries Croatia, the former Yugoslav Republic of Macedonia and Turkey; the stabilization and association process countries Albania, Bosnia and Herzegovina, Montenegro and Serbia; and, in addition, Armenia, the Republic of Moldova and Ukraine, said that corruption was a fundamental obstacle to sustainable development.
Efforts to combat it must be predicated on the principles of good governance, integrity, transparency and accountability, which, in turn, called for strong legal and judicial institutions.
As the first global and legally binding instrument on the subject, the Convention against Corruption was an important step in that direction.
It likewise continued to support the further development of the StAR initiative.
17. The European Union also welcomed the joint undertakings of the Commission on Science and Technology for Development and UNCTAD and looked forward to further efforts to bridge the digital divide and promote access to technology for development.

18. The European Union would like to see a clear connection to the achievement of the Millennium Development Goals in future reports on science and technology, as well as on corruption.
19. Mr. Oemar (Indonesia), speaking on behalf of the Association of Southeast Asian Nations (ASEAN), said that the United Nations had an essential part to play in extending multilateralism and shaping comprehensive measures to address the multiple crises in a globalized world.
20. In its deliberations on globalization and interdependence, the Committee should not ignore the contribution of middle-income countries to global and regional development and economic stability.
The Association had included combating corruption in its Community Blueprint and would continue to resolutely pursue it.
Yet they were models of good governance, open borders and economic liberalization.
Although globalization took no account of the needs of their small populations, it played as critical a role in their development as the decisions and policies of their own Governments.
If the World Trade Organization and the Organization for Economic Cooperation and Development did not make allowances for banana production and the financial services sector in the CARICOM countries, those countries could cease to derive any benefit from globalization.

25. For globalization to be effective, it must be inclusive.
Responding to the global economic and financial crisis was not the exclusive preserve of the G-20 countries, no matter how well intentioned.
He reiterated the Community's endorsement of the conclusions of the United Nations Conference on the World Economic and Financial Crisis and Its Impact on Development and emphasized the importance of the follow-up process.
CARICOM also echoed the Secretary-General's call to maintain and indeed increase levels of official development assistance (ODA) in order to cushion the impact of the crisis, not only in the financial centres of the world but also throughout the developing countries.
26. The CARICOM States had been prematurely categorized as middle-income countries alongside other countries far more capable of weathering external economic shocks and combating the crisis unaided.
Their graduation had been based purely on economic development without taking into account their degree of integration at the international level.
CARICOM needed the assistance of the United Nations and of other global partners, as well as adequate support mechanisms in order to assume a leading role in the global knowledge-based economy.

27. Ms. Markoff (United States of America) said that in a globally networked world, cybersecurity was becoming an increasingly critical issue.
As threats to network security multiplied, Governments needed to take a leadership role in ensuring the safety and security of cyberspace.
Given the international nature of such threats, international cooperation would be indispensable.
28. In years past, her country had been a leader in drawing the attention of the General Assembly to threats to information technology security.
At the current session it intended, along with co-sponsors Australia, Israel, the Marshall Islands and Japan, to introduce a draft resolution commending successful regional and international cybersecurity efforts and offering a generic self-assessment tool to help States evaluate their national cybersecurity needs and strategies.
Such a tool would help identify the responsibilities of key stakeholders in society, encourage public/private partnerships at the national level, determine the readiness of the authorities to respond to criminal misuse of information technology, and measure the level of public awareness of the cybersecurity issue.
She looked forward to the cooperation of Member States in reaching a consensus on that draft resolution.

29. Mr. Chen Ming (China) said that the increasingly transnational nature of corruption had made confronting it all the more complicated and the need for effective international cooperation all the more crucial.
Domestically, his country had launched a national anti-corruption coordination mechanism, a national anti-corruption website, and several local anticorruption pilot projects.
Internationally, it took active part in the Conference of the State Parties to the United Nations Convention against Corruption and supported all implementation efforts, especially with regard to the recovery of stolen assets and their return to their countries of origin.
China would become even more involved in international cooperation to combat corruption through information sharing, judicial assistance, capacity-building and technical assistance and hoped that substantive progress would be achieved at the Conference's third session, to be held in Doha from 9 to 13 November 2009.
30. He applauded the work of UNCTAD and the Commission on Science and Technology for Development in helping developing countries to integrate science and technology into their development plans.
His country had been an early leader in promoting development through science and technology, and boasted numerous pathbreaking achievements.
Its 15-year plan for scientific and technological development, laid out in 2006, envisioned turning China into an innovation-oriented economy by 2020.

Nevertheless, while the Government's support of science and technology had helped to make his country's economy the third largest in the world, its per capita gross domestic product (GDP) was not even in the top 100.
It would continue to invest in poverty reduction at home while providing development assistance to other countries to the best of its ability.
Greater investment in science and technology, improved strategies for scientific innovation and increased technical assistance to developing countries were all vital to achieving the Millennium Development Goals.
UNCTAD must continue to provide support to that end.
Developing countries should have access to the markets of developed countries and capacity-building support to enable them to become competitive.
32. Mr. Yono (Iraq) said that there was international agreement that corruption was a major obstacle to development.
His country's Constitution had established an independent Commission on Public Integrity to root out corruption, and it had signed the United Nations Convention against Corruption in March 2008.
In September 2008, UNODC and UNDP had launched a five-year programme to fight corruption in Iraq.
His country would continue to promote good governance based on transparency and accountability in fulfilment of its commitments under the International Compact with Iraq.

The Open-ended International Working Group on Review of the Implementation of the Convention had made constructive progress on the terms of reference for a transparent and inclusive review mechanism.
Adoption of such a mechanism at the forthcoming session of the Conference of States Parties would ensure that provisions on asset recovery and international cooperation functioned as intended.
34. Illicit financial flows coming out of developing countries had been estimated at up to 10 times the amount of ODA flowing into them.
The Open-ended Intergovernmental Working Group on Asset Recovery and the Stolen Assets Recovery (StAR) initiative were both crucial to the development of best practices and training tools for asset recovery.
They must be given the broadest possible support.
States also needed to conform to Financial Action Task Force on Money Laundering (FATF) standards for identifying beneficial ownership of domiciled companies and customer due diligence to prevent company domiciliation from being used as a cover for illegal financial flows.

35. Mr. González Segura (Mexico), speaking on behalf of the Rio Group, said that the Rio Group hoped that the third session of the Conference of the State Parties to the United Nations Convention against Corruption would agree on a review mechanism that was acceptable to all States parties.
As the Convention gained strong and sustained political commitment, it was important for the General Assembly to express support for it.
The Rio Group urged those countries which had not already done so to become parties to the Convention.
Anti-corruption strategies should not shy away from targeting the private sector and the issue of bribery.
Asset recovery and technical assistance to developing countries should be priorities.
36. He commended the work of UNCTAD and the Commission on Science and Technology for Development.
Technological innovation in agriculture was essential for reducing poverty in the rural areas where the bulk of poverty in the developing world was found, and could also contribute to global food security.
For that reason, the Rio Group stressed the importance of establishing guidelines for technology transfer to developing countries.

38. Mr. Alahraf (Libyan Arab Jamahiriya) said that while globalization offered genuine opportunities to developing countries to acquire new capacities and technologies, it also threatened them with economic dependency.
Fairness and stability needed to be restored to the international financial system and efforts by developing countries to diversify their economies should be supported.
It was important to recognize that privatization and the free market alone would not produce development, and that conditional assistance made it difficult for developing countries to balance international commitments with national priorities.
39. Corruption, bribery and money-laundering deprived developing countries of resources needed for development.
The international community needed to take action against money-laundering havens that operated outside the reach of the law.
He commended the UNODC initiative to eliminate safe havens for the proceeds of corruption, and called on the forthcoming third session of the Conference of the States Parties to the United Nations Convention against Corruption to explore mechanisms to identify and recover illicit assets.

40. Science and technology had an important role to play in development, poverty reduction, food security, disease prevention, educational development and environmental protection.
Developing countries should have access to the technology and other tools needed to incorporate the benefits of science into their national economic plans, human resources development strategies and services sectors.
Intellectual property rights should not be allowed to stand in the way of closing the technology gap.
He expressed support for proposals calling on the Commission on Science and Technology for Development to assist the Economic and Social Council in following up the outcomes of the World Summit on the Information Society.

Candidate 0:
  Question: How did UNODC help States cooperate on recovering illicit assets in 2009?
  Answer: UNODC also supported the creation and strengthening of regional networks of asset recovery focal points, which could further the dialogue between requesting and requested States.

Candidate 1:
  Question: How was the Global Forum meant to connect political and business leaders on corruption issues in 2009?
  Answer: the Global Forum would then become a public/private partnership forum bringing together political and business leaders.
````

### Output: choice 0

Finish reason: `stop`.

````text
[
  {
    "index": 0,
    "grounding": 5,
    "precision": 4,
    "numerical_fidelity": 5,
    "reason": "The answer copies a single sentence from the target block verbatim; it includes the relative clause about dialogue, which is slightly extra, and the question's '2009' comes from the document context rather than the block."
  },
  {
    "index": 1,
    "grounding": 4,
    "precision": 4,
    "numerical_fidelity": 5,
    "reason": "The answer is a verbatim span, but 'then' and the Global Forum's connection to corruption depend on context not in the block, and 'in 2009' is not in the block. The 'then' is a minor fragment that could be cut."
  }
]
````

### Recorded usage

````json
{
  "cached_tokens": 0,
  "completion_tokens": 247,
  "prompt_tokens": 8518,
  "provider_cost": 0.019506,
  "reasoning_tokens": 0
}
````

### Input size diagnostics

````json
{
  "input_characters": 27378,
  "context_capacity_exceeded": null
}
````

## Call 013: faithfulness

Request: `1f2059d5e95c4e6faa15fa00b3c581e6`. Task: `mode/un/2007/cd/pv_1063#7/semantic`.

Model: `anthropic/claude-sonnet-5.5`. UTC: 2026-09-30T17:56:01.386124+00:00.

API status: **response**. Duration: 3.477128 seconds.

### Request settings

````json
{
  "extra_body": {
    "thinking": {
      "budget_tokens": 16000,
      "type": "enabled"
    }
  },
  "max_tokens": 32000
}
````

### Input 1: system

````text
You are a strict faithfulness grader for legal and policy question-answer pairs built from United
  Nations documents.

You will receive a three-section context and THREE question-answer pairs.
The context is:
- "### TARGET BLOCK" — the passage the questions are supposed to be about, in one or more language
  versions.
- "### REFERENCED DOCUMENTS" — other documents CITED by the target block, each supplied as its
  symbol, title, and text — provided ONLY so the target block's citations can be understood, the way
  a footnote helps a reader.
- "### DOCUMENT CONTEXT" — surrounding text of the SAME document (its opening and neighbouring
  passages), supplied so that the target block can be understood: it resolves which mission "the
  Mission" is, which country "the Government" governs, what period a report covers, and similar
  referring expressions.
BOTH supporting sections are for UNDERSTANDING ONLY. Using them to resolve a referring expression in
  the question or answer (naming "the Mission" as UNAMIR, identifying what a cited resolution
  concerns) is legitimate and must NOT be penalised. Using either of them as a source of answer
  substance is a grounding failure — the answer's facts must come from the TARGET BLOCK itself,
  fully.

THREE question-answer pairs (questions may be in any language; each answer matches its question's
  language). Grade each pair on three sub-criteria, each 1–5. Do NOT evaluate query shape or
  retrieval quality — those are handled separately. Focus only on how faithfully each answer
  reflects the supplied text.

GRADING INSTRUCTIONS:
- Grade each of the three pairs independently and against the absolute rubric below — not relative
  to the other two.
- Do not let similarity or dissimilarity between the three pairs influence any individual grade.
- Evaluate each pair on its own merits before moving to the next.

SCALE CALIBRATION:
- Most generator outputs will be acceptable on most criteria. "Acceptable" is not the same as
  "excellent."
- 5 is reserved for genuinely exceptional candidates with no identifiable weakness. If you can point
  to any imperfection, it is not a 5. 5s should be uncommon.
- 4 means the candidate is very good but has exactly one minor, identifiable issue. You must be able
  to name the issue.
- 3 is the default grade for a candidate that is acceptable and does the job, with one clear
  weakness. It is not a punishment grade — most acceptable candidates will receive 3s.
- 2 and 1 are reserved for candidates with real, identifiable problems. Do not avoid using them when
  a candidate qualifies.
- Before assigning any 4 or 5, pause and ask: "What specifically makes this better than a 3?" If you
  cannot answer concretely, the grade is 3.

SUB-CRITERIA:

1. GROUNDING (1–5): Is the answer supported by a contiguous span of the TARGET BLOCK?
   The supporting text means the TARGET BLOCK alone. Resolving a referring expression through the
     REFERENCED DOCUMENTS, the DOCUMENT CONTEXT, or the metadata lines is legitimate disambiguation,
     not an inferential step. Anything more is.
   Cap the grade at 2 if any part of the answer's substance — a fact, figure, list, reason, or
     condition — is stated only in a REFERENCED DOCUMENT or only in the DOCUMENT CONTEXT and not in
     the target block. Cap at 1 if the answer's substance mainly comes from outside the target
     block.
   5 — Answer is taken directly from a single short contiguous span of the target block. Every word
     of the answer is explicitly present or is a trivial rewording of explicit content. No inference
     whatsoever. (Rare.)
   4 — Answer is fully supported but requires reading across two adjacent sentences, OR is from a
     single span with minor trivial rewording that a strict reader might flag.
   3 — Answer is grounded in the target block but requires one small, defensible inferential step —
     connecting a pronoun to its referent, combining a figure with its unit, or similar.
   2 — Answer is partially supported: some parts grounded in the target block, other parts not
     (including parts taken from a REFERENCED DOCUMENT or the DOCUMENT CONTEXT).
   1 — Answer requires significant inference, outside knowledge, or is not in the target block at
     all.
   CITATION RULE (UN): UN texts constantly cite other instruments ("the measures imposed by
     paragraph 20 of resolution 1493 (2003)"). If the answer's substance sits behind such a citation
     rather than in the target block's own words, score at most 2 (1 if the answer consists mainly
     of such content) — REGARDLESS of whether the cited document was supplied in the REFERENCED
     DOCUMENTS section. References exist for understanding, never as answer material.
   ATTRIBUTION RULE (UN): summary records report delegates' statements, letters convey a
     government's position, and reports state the reporting body's findings and estimates. If the
     target block attributes a claim, estimate, or assessment to a speaker or body and the answer
     (or the question it responds to) presents that claim as established fact with the attribution
     stripped, cap GROUNDING at 2 — the supplied text supports the attributed claim, not the bare
     assertion.

2. PRECISION (1–5): Does the answer add unsupported details or padding?
   5 — Answer is the shortest possible span that fully answers the question. Not one extra word. No
     surrounding context, no hedges, no elaboration. (Rare.)
   4 — Answer is grounded and tight but includes one short fragment of adjacent context that could
     have been cut.
   3 — Answer is grounded but includes one unsupported detail, generalization, or piece of padding.
   2 — Answer includes multiple unsupported details, or uses speculative framing ("likely,"
     "approximately," "it seems") where the passage is specific.
   1 — Answer is largely padded with content not in the passage, or is a rewrite rather than an
     extraction.

3. NUMERICAL & CITATIONAL FIDELITY (1–5): Are numbers, dates, amounts, and official identifiers
  reproduced exactly? (JSON key remains "numerical_fidelity".)
   5 — All numbers, dates, durations, monetary amounts, percentages, troop figures, and official
     identifiers (document symbols, resolution and paragraph numbers) match the passage
     character-for-character (e.g., "resolution 2374 (2017)" preserved as-is, not "Resolution 2374";
     "S/1994/565", not "S/1994/565/Rev.1"; "up to 5,500 troops", not "about 5,000 troops"; "within
     30 days", not "in about a month"). Dates rendered in the answer language's standard format
     count as exact if day, month, and year are unchanged ("15 July 1994" for "le 15 juillet 1994").
   4 — All values and identifiers are correct and preserved, but with a trivial formatting
     difference (e.g., "30-day period" vs. "within 30 days", or a spacing/punctuation variant of an
     identifier).
   3 — One number or date is rounded or approximated, one identifier is truncated (e.g., year
     dropped from a resolution number), or one duration is converted to a different unit.
   2 — Multiple values or identifiers rounded, reformatted, truncated, or partially dropped.
   1 — Numbers, dates, or identifiers invented, significantly changed, or contradicted by the
     passage.
   N/A — Answer contains no numerical or citational content. Score this sub-criterion as 5 if N/A.

Output valid JSON only — a list of three objects, one per candidate, in the order the candidates
  were provided (index 0, 1, 2):
[
  {
    "index": 0,
    "grounding": <1-5>,
    "precision": <1-5>,
    "numerical_fidelity": <1-5>,
    "reason": "one short sentence explaining the grades"
  },
  {
    "index": 1,
    "grounding": <1-5>,
    "precision": <1-5>,
    "numerical_fidelity": <1-5>,
    "reason": "..."
  },
  {
    "index": 2,
    "grounding": <1-5>,
    "precision": <1-5>,
    "numerical_fidelity": <1-5>,
    "reason": "..."
  }
]

ACTUAL BATCH SIZE: This request contains exactly 2 candidates. Return exactly 2 grade objects, using indices [0, 1]. Grade only supplied candidates. Any references above to THREE pairs or three example objects describe a typical batch; this actual batch size overrides those counts. All scoring criteria and calibration remain unchanged.
````

### Input 2: user

````text
### TARGET BLOCK — write the questions about THIS text

[EN] Document: CD/PV.1063
  Title: The PRESIDENT: I declare open the 1063rd plenary meeting of the Conference on Disarmament.
Dr. Goldblat, as you know, follows assiduously our formal sessions from the gallery.
Unfortunately he has not been able to be with us today, but I wish to extend to him my warmest congratulations and deep appreciation for the precious role he has played throughout the years in favour of disarmament and non-proliferation.
The granting of this distinction to Dr. Goldblat reflects Italy's strong commitment in favour of disarmament and non-proliferation at all echelons of its institutions.
Let me recall that last month Deputy Prime Minister and Minister of Foreign Affairs Massimo D'Alema made a strong appeal in favour of nuclear disarmament and for non-proliferation on the occasion of his visit to Hiroshima, a city which has become a symbol of international striving for international peace through disarmament.
A few days later, during the high-level segment of our Conference, UnderSecretary of State Vittorio Craxi pleaded for the resumption of substantive work at the Conference and supported the six Presidents' initiative.

### REFERENCED DOCUMENTS — none. The target block cites no other document available in the corpus.

### DOCUMENT CONTEXT — surrounding text of the SAME document, supporting context only. It resolves what the target block leaves implicit; it is never a source of answers.

[EN] Document CD/PV.1063 — surrounding passages
The PRESIDENT: I declare open the 1063rd plenary meeting of the Conference on Disarmament.
I wish to begin with a statement on behalf of the P-6 with regard to the work of this week.
I would like to thank on behalf of the P-6 the many delegations across the regions who spoke both at informal and formal plenaries last Friday in support of the Presidential draft decision contained in document CD/2007/L.1.
At the same time, there were a few delegations who sought further clarification, mainly in relation to methods of work and procedures.
In a spirit of transparency, I would like to address these points in order to assist in assessing the proposal.
With regard to the question of balance, we firmly believe that the proposal has been carefully crafted to reach a compromise between different views, priorities and interests, and what is realistically achievable in relation to short-term and long-term objectives of member States.
I would like to stress once again that the proposal contained in document CD/2007/L.1 reflects the views of member States.
I would also like to refer to the chapeau of L.1, which states that the Conference will decide on the present draft decision without prejudice to future work and negotiations on its agenda items.

Further, it is our firm view that the proposal is fully compatible with the rules of procedure of the Conference.
The rules of procedure clearly state that the work of the Conference can be conducted under any arrangement agreed by the Conference.
The Conference is the master of its own rules of procedure, and their role is to facilitate our work.
At the informal plenary last Friday the SecretaryGeneral of the Conference, Mr. Ordzhonikidze, further underlined this position.
With regard to the timetable, we believe that there is a practical need for flexibility as regards the allocation of time.
Therefore, the P-6 will propose a suitable draft timetable in consultation with the Coordinators for the consideration of the Conference after a decision is taken on the present draft proposal.
With regard to the appointment of Coordinators for specific issues by the Conference, during our consultations the prevailing view was that the current method of working with coordinators had been useful and appropriate, and therefore it should be continued and further elaborated.
These Coordinators are accountable to the Conference, which will appoint them, and they will present their reports to the Conference for consideration.
The meetings chaired by the Coordinators will be informal in nature unless otherwise decided by the Conference.

Finally, in keeping with the undertaking given by the P-6 at the beginning of this year to the Conference as per the organizational framework presented in January, we intend to conduct a formal plenary on Thursday, 29 March, at 10 a.m. to take a decision on document L.1.
I now give the floor to the representative of Nigeria.
Mr. AWANEN (Nigeria): Madam President, I have the honour to deliver this statement on behalf of the Group of 21.
First of all, I would like to congratulate you on assuming the presidency of the Conference on Disarmament, and to assure you of the Group's full cooperation and support in the exercise of your responsibilities.
The Group of 21 reaffirms that the total elimination of nuclear weapons is the only absolute guarantee against the use or threat of use of nuclear weapons.
The Group remains convinced that as long as nuclear weapons exist, so also will the risk of their proliferation and possible use remain with us.

Recognizing this danger, the G-21 has consistently called for the conclusion of a legally binding international instrument providing security assurances for nonnuclearweapon States against the use or threat of use of nuclear weapons.
In this regard, the Group recalls paragraphs 32 and 59 of the Final Document of the Tenth Special Session of the General Assembly, the first special session devoted to disarmament, which underscored the need for effective arrangements, as appropriate, to assure nonnuclearweapons States against the use or threat of use of nuclear weapons.
The G-21 is convinced that these arrangements, once enshrined in a legally binding instrument, will not only build trust within their ranks, but also strengthen their security and the peace and security of the international community.
The G-21 welcomes the informal consultations that have been held under the framework of the CD on the issue of negative security assurances, as reflected in the P-6 initiatives, and notes with satisfaction that in the CD there is no objection, in principle, to the idea of an international convention to assure nonnuclearweapon States against the use or threat of use of nuclear weapons, although the difficulties with regard to evolving a common approach acceptable to all have also been pointed out.

Mr. BRASACK (Germany): Madam President, I have the honour to take the floor on behalf of the European Union.
I can assure you of the European Union's full support in your efforts to guide the work of this Conference, especially at this important moment.
The European Union is very much encouraged by the constructive, structured an substantive discussions during the sessions of the last weeks, brought about by the six 2007 CD Presidents' "organizational framework".
The momentum developed as a result of the initiative taken jointly by the six Presidents of the CD last year has clearly been taken up and brought to an even higher level.
I would go as far as to say that a new spirit is prevailing in the CD. This has fostered our hope that finally the deadlock in the work of the CD can be overcome and significant work be resumed.
The European Union will not object to the proposal presented by the P-6 in CD/2007/L.1 as is stands.

The PRESIDENT: Thank you. I would appeal to delegations with regard to your mobile phones because this is disturbing the technology. I find it very difficult to listen.
So kindly switch off your mobile phones.
I now give the floor to the next speaker, the Ambassador of Austria.
Mr. PETRITSCH (Austria): Madam President, since this is the first time I am taking the floor under you able guidance, allow me to congratulate you on the assumption of this important post.
At the same time, I would like to thank you as well as your fellow Presidents and the various coordinators for their tireless efforts and valuable work which we have witnessed during the last few weeks.
Austria is especially grateful for, and welcomes, the P-6 proposal, which was tabled in document CD/2007/L.1 last Friday.
We consider it a very balanced and fair approach and we believe that it has a real potential to break the current deadlock.
Austria would therefore like to extend its full support for the Presidential draft decision.

In this context, we would also like to welcome the working paper delivered by Canada called "an FMCT scope-verification arrangement".
We consider this working paper a valuable contribution to our future discussions - and hopefully negotiations - on an FMCT.
Mr. TREZZA (Italy): Madam President, I have the pleasure of informing you and the members of the Conference that the President of the Republic of Italy, Mr. Giorgio Napolitano, has bestowed upon Dr. Joseph Goldblat the title of Cavaliere dell' Ordine al merito della Repubblica Italiana, which in English is Knight of the Order of Merit of the Italian Republic.
The motivation is the following: "Dr. Goldblat is one of the major experts at the global level in the field of disarmament and non-proliferation.
As a government official and later as an expert and scholar, he has promoted international peace and security through disarmament, arms reduction and non-proliferation."
I believe that all those who are involved in disarmament and non-proliferation are familiar with the eminent merits of this distinguished scholar and respected expert in the fields relevant to the work of this Conference.

[... the TARGET BLOCK appears here ...]

Our Commitment is closely linked to the engagement of the European Union in the field of disarmament and non-proliferation, which has deep roots in the EU's history, in particular within the framework of its common foreign and security policy.
Some of the landmarks of this policy, like the EU Strategy against the Proliferation of Weapons of Mass Destruction and the EU Common Position on the Universalization and Reinforcement of Multilateral Agreements in the field of disarmament and non-proliferation, were crafted in 2003 under the Italian presidency of the European Union.
The developments I have mentioned take place at a special time.
Last November, results of substance were achieved at the CCW Review Conference under the French presidency.
A few weeks later similar positive results were reached at the Biological Weapons Review Conference under the presidency of Pakistan.
This year, for the first time ever, the six Presidents have submitted to the Conference on Disarmament a draft decision which would allow the Conference to resume its institutional task: to negotiate international disarmament treaties.
My delegation subscribes to the statement made this morning by Germany on behalf of the European Union.
This proposal cannot come as a surprise to the delegations that have followed all our deliberations and to capitals that have been briefed.

The Presidents have been working and consulting for a long time and have made all possible efforts to reach, well in advance, every delegation and every regional group.
We respect the necessity of consulting capitals on this important matter, but the time has come for a decision.
I believe that all CD members recognize that the NPT, whose review process will begin next month is the cornerstone of international peace and security.
That process would benefit enormously from a positive outcome of our deliberations here in Geneva.
The PRESIDENT: Thank you, and I avail of this opportunity to also extend to Dr. Goldblat our sincere congratulations.
He has been well known and close to the Sri Lankan delegation for many years.
I now give the floor to the next speaker on my list, the Ambassador of France.
Mr. DOBELLE (France) (spoke in French): Madam President, since I am taking the floor for the first time in this forum during your term, I would like first of all to extend to you my warmest congratulations.

If I did not speak on Friday afternoon, it was because we wanted to take time for serious thought in order to study the true worth of this proposal, which will at all events mark an important turning point in the work of the Conference on Disarmament.
In a spirit of compromise, France is prepared not to object to the consensus on this text.
In so doing, we are displaying our sincere commitment to the earliest possible launching of negotiations on the fissile material treaty (FMCT), which, as we have pointed out repeatedly in this forum, is as far as we are concerned an indispensable supplement to the CTBT as well as being the next tangible step forward to which the Conference on Disarmament can contribute in the field of nuclear disarmament.
In truth this is the only subject which at this stage is likely to meet with agreement on the part of the member States of the Conference with a view to starting negotiations.

I would also like to stress in this context that any amendment aimed at strengthening or amending the provisions of the President's compromise concerning nuclear disarmament or negative security assurances would put a complete end to any chances of a consensus.
We also regret the fact that this proposal gives excessive importance to nuclear disarmament and insufficient importance to conventional disarmament.
These topics are of prime relevance to national security.
However, despite the shortcomings that we have identified in this text, as I have already said, France will not block a consensus.
Bearing in mind what has just been said by the presidency of the European Union, if all delegations are able, showing the same flexibility that we are showing, to sign up to this compromise and thus enable the President's proposal to be adopted by consensus before the end of the first part of the work of the present session, we hope fervently that the President will ensure that the discussions during the second and third parts of the session will allocate the negotiations on the fissile material treaty the time they require and will take into account the importance of the issues related to conventional disarmament.

Madam President, the delegation of Algeria had not planned to take the floor, but given the clarifications that you have provided us with on behalf of the six Presidents, for which we would like to thank you, we have a few comments to make.
First of all, during the informal and formal meetings held last Friday, the Algerian delegation pointed out that the mandates concerning nuclear disarmament and negative security assurances could be improved upon by taking into account the wording adopted by consensus at the NPT review conferences in 1995 and 2000.
I can read out a proposal:
If we say "The Conference on Disarmament decides without prejudice to future work or negotiations on its agenda items to appoint for the duration of the current session ..." and then we nominate the Coordinators,
There is no problem for the balance of the documents, unless there is something we are not aware of.
The above relates to procedure.

Concerning the substance or the wording of the mandates, Madam President, we received your proposal very late on Friday evening and we did not hesitate to send it as soon as possible to our capital.
We are still awaiting responses from the Algerian authorities.
I hope to receive them by Thursday, but I can not tell you now.
But it is very important to mention in the decision the annual time frame for the programme of work, because once this phase is completed we will be referring much more to the decision than to the statement by these Presidents.
Mr. MOAIYERI (Islamic Republic of Iran): Madam President, since this is the first time I am speaking under your presidency, allow me to congratulate you on your assumption of the presidency of the Conference on Disarmament and wish you all success in discharging your important task to move the work of this august body forward.
I would also like to extend my appreciation to the six presidencies of the Conference and the coordinators, whose contributions to the work of the CD are admirable.

With regard to the proposal presented to the Conference on Friday, 23 March 2007, I wish to express some comments.
We immediately sent the proposal upon receipt to the capital in order to be studied in depth and to receive instructions.
Until now, my delegation has not received instructions from the capital. Therefore, my delegation deserves the right to make its final word in that regard at a later stage.
Since it is a very important proposal, it needs to be studied properly by different decisionmaking bodies within my capital.
In order to contribute to the discussion on this subject, some preliminary views of my delegation are as follows.
My delegation has always insisted on a balanced and comprehensive approach with regard to the programme of work of the CD.
The four core issues identified earlier by the Conference have their background, history and context.
My delegation is of the belief that nuclear disarmament and international legally binding arrangements to assure nonnuclearweapon States against the use or threat of use of nuclear weapons are the highest priorities in the work of the Conference.
Therefore, it is without affecting the balance between the four core issues in any programme of work of the CD.
The A-5 proposal has established a solid basis for any programme of work for this body.

Our expectation is that this proposal be consistent with that standard.
With regard to FMCT, my delegation on different occasions has expressed its position that negotiations on that subject should only be in the framework of the Shannon mandate.
Once again, I would like to put on record this principled position of my delegation.
Mr. SHOUKRY (Egypt) (spoke in Arabic): Madam President, may I congratulate you on your assumption of the presidency of the Conference and wish you every success in your important task? May I also thank you for the statement containing very important clarifications relating to the initiative proposed in document CRP.4?
Mr. PINTER (Slovakia): Madam President, to begin with, I would like to join the previous speakers in congratulating you on the assumption of your duties as President of the Conference and to wish you much success in your work.
At the same time, I want to add that we subscribe to the statement made by the Ambassador of Germany on behalf of the EU.

My delegation has been following the discussions during the first nine weeks of this year's session very carefully, and in particular last Friday's statement on the groundbreaking P-6 proposal on the future activities of the Conference.
I had the honour to support it on behalf of last year's CD presidencies during the informal CD plenary.
This proposal has been constructed along the lines expressed by all delegations during the intensive consultations conducted by the P-6.
This should serve as a guarantee that it meets the expectations of all member States to such a level that they would lend their support to it at this juncture.
Still, at some instances of last Friday's discussion, we experienced the sense of déjà vu.
I refer to the preparation of last year's CD report.
Without going into details, the dominant feeling we and the majority of colleagues acquired is that the lack of determination or the courage to go beyond the traditional or conservative concepts of behaviour still has its recurrent power.
Last Friday, the words of Mr. Ordzhonikidze reminded us that there was no reason not to break this vicious circle.

Ten years of non-action in terms of producing any concrete result with regard to negotiations on disarmament issues have left a negative impact on our perceptions of the primary role of this body.
Ten years of discussions, whatever objective has been invented in order to express movement forward, have brought us to a crossroads.
Each of these decisions contains risks we should be aware of.
This time, however, we should recall the words of Mr. Kofi Annan, the former United Nations SecretaryGeneral, who during his last visit to the Council chamber stressed that the time is ripe, the choice is clear.
Failing to accept the very carefully drafted proposal the P-6 submitted after having listened to each of us would mean seriously failing these words.
We do risk the very existence of this body.
It should not be taken for granted that another year of discussions would meet the expectations of our governments and indeed the international community.

Already now some people say that the CD, because of a lack of real work, is a body which requires the attention of junior diplomats only.
We may not be too distant from the moment when this negative assessment transforms even further and the CD becomes an irrelevant and informal body with no practical meaning and influence.
Some weeks ago I overheard a discussion within a tourist group visiting this chamber.
Mr. MISZTA (Poland): Madam President, let me begin by reiterating that Poland stands fully behind the EU statement delivered just a moment ago by the Ambassador of Germany.
Since it is the first time my delegation is taking the floor under the Sri Lankan presidency in a formal setting, let me extend our wholehearted congratulations to you on the assumption of this high post and reassure you of Poland's full support to your doings.
My delegation would also like to express words of great appreciation to the whole platform of this year's Presidents, especially to your predecessors of South Africa and Spain, for their enormous efforts invested in guiding the work of the CD.
We would also like to congratulate the coordinators appointed by the President for the excellent leadership in conducting substantive discussions carried out on the agenda items.

All these collective endeavours have undoubtedly contributed to building a positive momentum in the CD.
We would like to thank and commend you and all the P-6 on the Presidential draft decision presented in document CD/2007/L.1 of 23 March, which reflects the creative approach and application of thinking out of the box about the problems experienced by the CD.
In our view, they also seem to reflect upon our search for compromise solutions allowing for effectively accommodating the interests of all States represented in this august body.
Furthermore, we are of the opinion that the proposal adequately addresses expectations and appeals to overcome the existing stalemate repeatedly expressed by many for such a long time.
Hence, it is perceived by Poland as a step forward in our endeavours to revitalize the work of the Conference.
By focusing on setbacks rather than advantages at this stage, we put the entirety of efforts to get the CD back to work at risk.

Poland welcomes the Presidential draft decision and its assumptions.
We see it as a sound basis for a decision to be taken by the CD as we appeal to all States to extend their flexibility and constructive approach, indispensable in achieving this goal.
Mr. CHANG (Republic of Korea): Madam President, as this is the first time my delegation is taking the floor at a formal plenary during your presidency, I would like to convey my heartfelt congratulations to you on your assumption of the presidency of this body.
I would also like to thank this year's six Presidents for their dedicated efforts to move the work of the CD forward.
My delegation takes this opportunity to assure you of our full support and cooperation.
This year we have embarked on our discussion in the Conference on Disarmament with a sense of renewed purpose in the hope of finding a workable solution to getting the CD back to work after years of frustration, building upon the progress we made last year.
We have had intensified and structured debates on all the agenda items.
The focused in-depth debates during the course of the last nine weeks have produced a valuable P-6 proposal.

My delegation feels that the draft decision contained in CD/2007/L.1 is well balanced and duly reflective of the results of the bilateral consultations the P-6 have conducted with all member States.
In this event, I invite all the members to summon the necessary political will and exercise more flexibility in order not to lose the momentum.
Mr. BRASACK (Germany): Thank you, Madam President, for allowing Germany the floor in its national capacity.
Again, I would like to assure you, Madam, and the other members of the P-6 platform of Germany's fullest support in your efforts to guide the work of this Conference, especially at this crucially important moment.
We are confident that under your able guidance the Conference can finally achieve what it has been striving for nine years, namely bringing the CD back to substantial work.
It goes without saying - and no one will be surprised - that my delegation subscribes to the statement made this morning on behalf of the EU by Germany.

We are very much encouraged by the constructive, structured and substantive discussions during the sessions of the last weeks, brought about by the six 2007 CD Presidents' "organizational framework".
We therefore wholeheartedly welcome the Presidential draft decision tabled by this year's P-6 in document CD/2007/L.1 on 23 March 2007, and we are of the view that its elements indeed reflect the necessary decisions the CD will have to agree on to get back to work.
I am happy again, as I was already last Friday, to express Germany's full and unequivocal support for the P-6 proposal as it stands.
We very much welcome and encourage the efforts undertaken collectively by the six CD presidencies of 2007 to draw the appropriate conclusions from the discussions of the last weeks.
In particular, we highly commend the meticulous way in which the P-6 again gathered the views of every single CD member State and managed to merge all these views into a coherent layout proposal for the CD's activities in the remainder of the year - and hopefully beyond.

We also highly appreciate the work done by all the coordinators and are very grateful for their efforts under the respective agenda items.
Germany, through the EU and on a national basis, has made substantial contributions to the discussions on each agenda item and will continue to be actively involved in all future debates.
We therefore fully support the differentiated approach taken by the P-6 Presidential draft proposal.
Getting the CD back to fulfilling its function as the single multilateral forum at the disposal of the international community for disarmament negotiations is all the more important against the backdrop of the security challenges that we are facing today.
For now, therefore, it is of utmost importance that the CD adopts the fundamental decision to get back to work.
As regards procedural issues - and I would further elaborate on them - we fully subscribe to the views that you, Madam President, presented this morning to the room.
There is no realistic and viable alternative to this approach.

The Ambassador of China has the floor.
Mr. CHENG (China) (spoke in Chinese): I thank you, Madam President, for the introduction you have given to some of the issues.
The Chinese delegation, like all other parties, hopes to see the Conference on Disarmament commence its substantive work at the earliest possible stage.
First, rule 28 of the rules of procedure stipulates that, on the basis of its agenda, the Conference, at the beginning of its annual session, shall establish its programme of work, which will include a schedule of its activities for that session.
In my understanding of this rule, this has indeed been the past practice of the Conference on Disarmament, namely, that in order to conduct substantive work, the Conference should have a programme of work.
Fourth, in my view the mandates of the Coordinators on the three themes of nuclear disarmament, prevention of an arms race in outer space and negative security assurances to nonnuclear-weapon States, as formulated in the draft decision, do not differ from the mandates assigned to the coordinators on those three themes in the organizational framework put forward by the group of six Presidents during the first part of our session.

The PRESIDENT: I now give the floor to the next speaker on my list, the Ambassador of Bulgaria.
Mr. DRAGANOV (Bulgaria): Madam President, let me congratulate you on your assumption of this high office.
We wish you every success in your endeavours.
You can count on the full support and cooperation of my delegation.
Let me also thank all of the 2007 Presidents for their useful efforts.
It is my delegation's sincere hope that the continuity and the work of the 2006 and 2007 Presidents, combined with the good will of all member States, will bring success to the Conference and move it forward this year.
My delegation has been working over the years to help bring this Conference back to substantive work, and I can assure you that we will spare no further effort.
I subscribe to the EU joint statement made by Germany just now and join previous speakers who expressed their support for the P-6 proposal.
My delegation shares the view that while it may not be perfect, this formula seems to be the only one possible at this stage, and I wish to encourage all member States to grasp the chance and support it in the spirit of constructive cooperation and flexibility.

We should make no mistake about this.
The CD may not get a better opportunity any time soon.
To use the famous Mandela quote, "the time is now".
The PRESIDENT: I thank you, and I would like to thank all delegations for the kind words they have addressed to the Chair, to the P-6 and to the coordinators.
The P-6 has tried its best to address the questions of clarification which have been raised at the informal and formal plenaries.
If not, this concludes our plenary meeting.
The next plenary meeting will be held on Thursday, 29 March 2007 at 10 a.m.

Candidate 0:
  Question: What nuclear policy did Italy’s Deputy Prime Minister advocate during his Hiroshima visit in 2007?
  Answer: Deputy Prime Minister and Minister of Foreign Affairs Massimo D'Alema made a strong appeal in favour of nuclear disarmament and for non-proliferation

Candidate 1:
  Question: What institutional response did Italy support to restart substantive work at the Conference on Disarmament in 2007?
  Answer: UnderSecretary of State Vittorio Craxi pleaded for the resumption of substantive work at the Conference and supported the six Presidents' initiative
````

### Output: choice 0

Finish reason: `stop`.

````text
[
  {
    "index": 0,
    "grounding": 4,
    "precision": 3,
    "numerical_fidelity": 5,
    "reason": "The answer is taken from the target block's sentence about D'Alema's appeal. The question's 2007 date is not in the block, only in the document context, which is a minor resolution. The answer also includes his full title and name beyond what the question asked for."
  },
  {
    "index": 1,
    "grounding": 4,
    "precision": 3,
    "numerical_fidelity": 5,
    "reason": "The answer is directly supported by the final sentence of the block. It has a small mismatch: the question asks for an 'institutional response' whereas the answer reports an Under-Secretary's plea. It also includes the person's name and title, which adds padding."
  }
]
````

### Recorded usage

````json
{
  "cached_tokens": 0,
  "completion_tokens": 267,
  "prompt_tokens": 12395,
  "provider_cost": 0.02746,
  "reasoning_tokens": 0
}
````

### Input size diagnostics

````json
{
  "input_characters": 38756,
  "context_capacity_exceeded": null
}
````

## Call 014: faithfulness

Request: `be55e033d7ec40198cc2eb7dc20ceb7e`. Task: `mode/un/2007/a/cn_9/sr_841#21/semantic`.

Model: `anthropic/claude-sonnet-5.5`. UTC: 2026-09-30T17:56:01.390676+00:00.

API status: **response**. Duration: 4.189807 seconds.

### Request settings

````json
{
  "extra_body": {
    "thinking": {
      "budget_tokens": 16000,
      "type": "enabled"
    }
  },
  "max_tokens": 32000
}
````

### Input 1: system

````text
You are a strict faithfulness grader for legal and policy question-answer pairs built from United
  Nations documents.

You will receive a three-section context and THREE question-answer pairs.
The context is:
- "### TARGET BLOCK" — the passage the questions are supposed to be about, in one or more language
  versions.
- "### REFERENCED DOCUMENTS" — other documents CITED by the target block, each supplied as its
  symbol, title, and text — provided ONLY so the target block's citations can be understood, the way
  a footnote helps a reader.
- "### DOCUMENT CONTEXT" — surrounding text of the SAME document (its opening and neighbouring
  passages), supplied so that the target block can be understood: it resolves which mission "the
  Mission" is, which country "the Government" governs, what period a report covers, and similar
  referring expressions.
BOTH supporting sections are for UNDERSTANDING ONLY. Using them to resolve a referring expression in
  the question or answer (naming "the Mission" as UNAMIR, identifying what a cited resolution
  concerns) is legitimate and must NOT be penalised. Using either of them as a source of answer
  substance is a grounding failure — the answer's facts must come from the TARGET BLOCK itself,
  fully.

THREE question-answer pairs (questions may be in any language; each answer matches its question's
  language). Grade each pair on three sub-criteria, each 1–5. Do NOT evaluate query shape or
  retrieval quality — those are handled separately. Focus only on how faithfully each answer
  reflects the supplied text.

GRADING INSTRUCTIONS:
- Grade each of the three pairs independently and against the absolute rubric below — not relative
  to the other two.
- Do not let similarity or dissimilarity between the three pairs influence any individual grade.
- Evaluate each pair on its own merits before moving to the next.

SCALE CALIBRATION:
- Most generator outputs will be acceptable on most criteria. "Acceptable" is not the same as
  "excellent."
- 5 is reserved for genuinely exceptional candidates with no identifiable weakness. If you can point
  to any imperfection, it is not a 5. 5s should be uncommon.
- 4 means the candidate is very good but has exactly one minor, identifiable issue. You must be able
  to name the issue.
- 3 is the default grade for a candidate that is acceptable and does the job, with one clear
  weakness. It is not a punishment grade — most acceptable candidates will receive 3s.
- 2 and 1 are reserved for candidates with real, identifiable problems. Do not avoid using them when
  a candidate qualifies.
- Before assigning any 4 or 5, pause and ask: "What specifically makes this better than a 3?" If you
  cannot answer concretely, the grade is 3.

SUB-CRITERIA:

1. GROUNDING (1–5): Is the answer supported by a contiguous span of the TARGET BLOCK?
   The supporting text means the TARGET BLOCK alone. Resolving a referring expression through the
     REFERENCED DOCUMENTS, the DOCUMENT CONTEXT, or the metadata lines is legitimate disambiguation,
     not an inferential step. Anything more is.
   Cap the grade at 2 if any part of the answer's substance — a fact, figure, list, reason, or
     condition — is stated only in a REFERENCED DOCUMENT or only in the DOCUMENT CONTEXT and not in
     the target block. Cap at 1 if the answer's substance mainly comes from outside the target
     block.
   5 — Answer is taken directly from a single short contiguous span of the target block. Every word
     of the answer is explicitly present or is a trivial rewording of explicit content. No inference
     whatsoever. (Rare.)
   4 — Answer is fully supported but requires reading across two adjacent sentences, OR is from a
     single span with minor trivial rewording that a strict reader might flag.
   3 — Answer is grounded in the target block but requires one small, defensible inferential step —
     connecting a pronoun to its referent, combining a figure with its unit, or similar.
   2 — Answer is partially supported: some parts grounded in the target block, other parts not
     (including parts taken from a REFERENCED DOCUMENT or the DOCUMENT CONTEXT).
   1 — Answer requires significant inference, outside knowledge, or is not in the target block at
     all.
   CITATION RULE (UN): UN texts constantly cite other instruments ("the measures imposed by
     paragraph 20 of resolution 1493 (2003)"). If the answer's substance sits behind such a citation
     rather than in the target block's own words, score at most 2 (1 if the answer consists mainly
     of such content) — REGARDLESS of whether the cited document was supplied in the REFERENCED
     DOCUMENTS section. References exist for understanding, never as answer material.
   ATTRIBUTION RULE (UN): summary records report delegates' statements, letters convey a
     government's position, and reports state the reporting body's findings and estimates. If the
     target block attributes a claim, estimate, or assessment to a speaker or body and the answer
     (or the question it responds to) presents that claim as established fact with the attribution
     stripped, cap GROUNDING at 2 — the supplied text supports the attributed claim, not the bare
     assertion.

2. PRECISION (1–5): Does the answer add unsupported details or padding?
   5 — Answer is the shortest possible span that fully answers the question. Not one extra word. No
     surrounding context, no hedges, no elaboration. (Rare.)
   4 — Answer is grounded and tight but includes one short fragment of adjacent context that could
     have been cut.
   3 — Answer is grounded but includes one unsupported detail, generalization, or piece of padding.
   2 — Answer includes multiple unsupported details, or uses speculative framing ("likely,"
     "approximately," "it seems") where the passage is specific.
   1 — Answer is largely padded with content not in the passage, or is a rewrite rather than an
     extraction.

3. NUMERICAL & CITATIONAL FIDELITY (1–5): Are numbers, dates, amounts, and official identifiers
  reproduced exactly? (JSON key remains "numerical_fidelity".)
   5 — All numbers, dates, durations, monetary amounts, percentages, troop figures, and official
     identifiers (document symbols, resolution and paragraph numbers) match the passage
     character-for-character (e.g., "resolution 2374 (2017)" preserved as-is, not "Resolution 2374";
     "S/1994/565", not "S/1994/565/Rev.1"; "up to 5,500 troops", not "about 5,000 troops"; "within
     30 days", not "in about a month"). Dates rendered in the answer language's standard format
     count as exact if day, month, and year are unchanged ("15 July 1994" for "le 15 juillet 1994").
   4 — All values and identifiers are correct and preserved, but with a trivial formatting
     difference (e.g., "30-day period" vs. "within 30 days", or a spacing/punctuation variant of an
     identifier).
   3 — One number or date is rounded or approximated, one identifier is truncated (e.g., year
     dropped from a resolution number), or one duration is converted to a different unit.
   2 — Multiple values or identifiers rounded, reformatted, truncated, or partially dropped.
   1 — Numbers, dates, or identifiers invented, significantly changed, or contradicted by the
     passage.
   N/A — Answer contains no numerical or citational content. Score this sub-criterion as 5 if N/A.

Output valid JSON only — a list of three objects, one per candidate, in the order the candidates
  were provided (index 0, 1, 2):
[
  {
    "index": 0,
    "grounding": <1-5>,
    "precision": <1-5>,
    "numerical_fidelity": <1-5>,
    "reason": "one short sentence explaining the grades"
  },
  {
    "index": 1,
    "grounding": <1-5>,
    "precision": <1-5>,
    "numerical_fidelity": <1-5>,
    "reason": "..."
  },
  {
    "index": 2,
    "grounding": <1-5>,
    "precision": <1-5>,
    "numerical_fidelity": <1-5>,
    "reason": "..."
  }
]

ACTUAL BATCH SIZE: This request contains exactly 2 candidates. Return exactly 2 grade objects, using indices [0, 1]. Grade only supplied candidates. Any references above to THREE pairs or three example objects describe a typical batch; this actual batch size overrides those counts. All scoring criteria and calibration remain unchanged.
````

### Input 2: user

````text
### TARGET BLOCK — write the questions about THIS text

[EN] Document: A/CN.9/SR.841
  Title: United Nations Commission on International Trade Law
Mr. Burman (United States of America) expressed strong support for the wording of recommendation 204. He was unwilling to engage in any further discussion of the matter.
The Chairperson said that the Working Group had discussed the question at length and that the Commission had taken a decision.
Despite the concerns expressed by some delegations, there did not seem to be majority support for reopening the debate on the substance of recommendation 204.
Moreover, she trusted that the discussion of financial contracts would allay any remaining concerns.
Ms. McCreath (United Kingdom) said she disagreed with that conclusion.
A number of delegations had expressed valid concerns.
It was unhelpful and undermined consensus merely to state that the issue was closed.
She suggested, for example, that some form of cross-referencing should be included in recommendation 204.
At all events, the discussion should be deferred until the recommendations on financial contracts had been considered.

### REFERENCED DOCUMENTS — none. The target block cites no other document available in the corpus.

### DOCUMENT CONTEXT — surrounding text of the SAME document, supporting context only. It resolves what the target block leaves implicit; it is never a source of answers.

[EN] Document A/CN.9/SR.841 — surrounding passages
United Nations Commission on International Trade Law
Fortieth session
Summary record of the 841st meeting
Chairperson: Ms. Sabo (Chairperson of the Committee of the Whole). (Canada)

Adoption of a draft UNCITRAL Legislative Guide on Secured Transactions and possible future work (continued)

Recommendations 198 and 199
The Chairperson said that, if she heard no objection, she would take it that the Committee agreed on the substance of recommendations 198 and 199 and would leave it to the Secretariat to make the necessary editorial changes.
She also took it that the Committee wished to remove the square brackets from recommendation 199 and to retain the text they enclosed, as had been done in the case of recommendation 199 in the unitary approach section.
Recommendations 198 and 199 were adopted on that understanding.
Recommendations 200 and 201
Recommendations 200 and 201 were adopted.
The Chairperson said she took it that the Committee wished to approve the substance of the commentary to chapter XII, subject to any changes required to reflect the amendments to recommendations 184 to 201 (unitary and non-unitary approaches).
The substance of the commentary to chapter XII was adopted on that understanding.

XIII: Private international law (A/CN.9/631 and Add.10)
Mr. Deschamps (Canada), supported by Mr. Voulgaris (Greece) and Mr. Riffard (France), said that he was not convinced of the wisdom of changing the title of the chapter from "Conflicts of laws" to "Private international law".
While conflict-of-law rules certainly formed part of private international law, chapter XIII dealt exclusively with the rules governing the law applicable to security rights.
The scope of private international law was far broader and included rules that were unrelated to conflict-of-law issues, such as the jurisdiction of courts and the recognition and enforcement of foreign judgements.
It would therefore be preferable to retain the heading used in the past.
Mr. Marca Paco (Bolivia) said that neither the title "Private international law" nor the title "Conflicts of laws" was appropriate.
The purpose of the chapter was to determine the applicable law, regardless of whether a conflict of law existed.
The most appropriate title would therefore be "Applicable law".

The Chairperson said she took it that the Committee wished to replace the title "Private international law" by a more appropriate title, leaving the choice of the most suitable title for each language version to the terminology specialists.
It was so decided.
Mr. Wezenbeek (Observer for the European Union) suggested deleting the footnote referring to cooperation with the Hague Conference on Private International Law, which seemed inappropriate.
The Chairperson said that cooperation with the Permanent Bureau of the Hague Conference was an example of inter-agency cooperation that the Working Group felt should be encouraged by acknowledging it in a footnote.
Mr. Kemper (Germany) suggested inserting the words "Permanent Bureau of" before "the Hague Conference on Private International Law".
Recommendation 202
The Chairperson asked whether the Committee wished to include the text currently in square brackets in recommendation 202.
Ms. Okino Nakashima (Japan) proposed including the text.
In cases where movable assets were subject to a specialized registration system, the law of the State under the authority of which the registry was maintained should prevail.

Mr. Voulgaris (Greece), Mr. Sigman (United States of America) and Ms. McCreath (United Kingdom) concurred.
Mr. Wezenbeek (Observer for the European Union) said that the subject matter of chapter XIII was highly controversial.
The Convention on the Law Applicable to Certain Rights in respect of Securities Held with an Intermediary (the Hague Securities Convention) had been adopted quite speedily in 2002 but so far only two States had signed it.
Opinions within Europe were deeply divided on whether or not to sign. A proposed regulation on the law applicable to contractual arrangements (Rome I), which contained provisions on assignments of receivables and conflicts of law, was also currently the subject of heated debate in the European Union.
Chapter XIII was a crucial component of the draft Guide and, given the complexity of the underlying issues, should not be adopted hastily.
The Chairperson noted that the rule contained in recommendation 202 was consistent with the United Nations Convention on the Assignment of Receivables in International Trade (United Nations Assignment Convention).
The European Commission had in the past stated its willingness to work towards a solution that would be consistent with that instrument so that European Union member States could adopt it.

Mr. Rögner (Observer for the European Insurance and Reinsurance Federation) expressed support for the comments made by the observer for the European Commission and for the inclusion of the text in square brackets, which explained why lex situs should be the applicable law.
Mr. Marca Paco (Bolivia) asked whether the proposal contained in the note to the Commission had been inserted on the assumption that the text in square brackets would be retained as part of recommendation 202.
The question of whether the text was included would, in his view, influence the Committee's decision on whether to add a recommendation in the light of the note.
Mr. Bazinas (Secretariat) said that the note had not been intended to prejudge the Committee's decision on the text in square brackets.
The Chairperson said she took it that the Committee wished to include the text in square brackets in recommendation 202.
Recommendation 202, as amended, was adopted.

The Chairperson invited the Committee to consider the proposal contained in the note to the Commission following recommendation 202.
Mr. Bazinas (Secretariat) said that the Commission was invited to consider whether it wished to include a recommendation that would address the priority conflict between two creditors, one with a possessory security right in a negotiable document and the other with a non-possessory security right in the goods covered by the document.
The recommendation would state explicitly, in line with current practice, that the law of the location of the document should apply in order to preserve the negotiability of the negotiable document.
The matter could be clarified in the commentary to chapter XIII but the Committee might wish to address it in a separate recommendation.
Mr. Deschamps (Canada) expressed support in principle for the addition of a recommendation.
However, it might be best to defer a decision on the matter pending the outcome of the discussion of the revised version of recommendation 107, which concerned the question of whether a secured creditor that held a bill of lading had priority as against a competing claimant that held a right in the goods under another mechanism.

Mr. Pendón Meléndez (Spain) reiterated his dissatisfaction with the draft Guide's approach to negotiable instruments.
Before acting on the note to the Commission, the Committee should take a clear-cut decision on recommendation 107. He therefore endorsed the proposal made by the representative of Canada.
Mr. Bazinas (Secretariat) said that the Committee might also wish to consider situations in which there was a conflict of priority between a security right in a negotiable document and a security right in the goods covered by the document, where the latter security right was subject to a specialized registration system.
While he considered that the law of the location of the negotiable document should be applicable, the Committee might wish to discuss the matter in the light of the revised version of recommendation 107.
The Chairperson said she took it that the Committee wished to defer a decision regarding the note to the Commission until it had an opportunity to discuss the revised version of recommendation 107.

Recommendation 203
Mr. Pendón Meléndez (Spain) said he took it that recommendation 203 applied only to tangible property in transit for which no negotiable instrument or negotiable document had been issued.
If so, there should be a reference to that exclusion in the commentary to chapter XIII.
Mr. Bazinas (Secretariat) said that recommendation 203 applied irrespective of whether the goods were covered by a negotiable document or whether the document travelled with the goods.
The reference to tangible property other than negotiable instruments or negotiable documents referred to the goods only and had no bearing on the issue of whether a negotiable document existed.
Mr. Voulgaris (Greece) said he agreed that goods in transit should be considered separately from the documents by which they might be covered.
The recommendation should further specify that the transit must be completed within seven days.
Mr. Pendón Meléndez (Spain) said that, since the issue was related to the general regime applicable to negotiable documents and affected other recommendations, it would be useful to include a general explanatory note in the commentary.
There was a general unwritten rule in international transport that, once tangible property in transit was covered by a negotiable document, any action affecting the property, for example the exercise of security rights, must be taken on the basis of the negotiable document.

Mr. Voulgaris (Greece) called for a substantive discussion of the matter.
If, for example, a bill of lading had been issued in respect of goods in transit, the law governing bills of lading should clearly be applied.
The Chairperson suggested that the issue should be addressed once a decision had been taken on recommendation 107 and on the note following recommendation 202.
Mr. Riffard (France) said that the question of the applicable law in the case of transfer of a security right by way of assignment of a receivable had not been resolved.
He proposed inserting a recommendation to address that question, which had major practical implications.
The Chairperson expressed the view that the relevant rule in the United Nations Assignment Convention should apply.
Mr. Deschamps (Canada) said that it could be inferred from article 22 of the Assignment Convention concerning the law applicable to competing rights that the law governing priority would determine whether the assignee was entitled to benefit from the security right in a receivable.
The implicit rule was that the law of the grantor would determine whether formalities were required to enable the assignee to benefit from the security right in the receivable.
However, the issue was complex and required further in-depth consideration.

The Chairperson suggested deferring consideration of the issue and of recommendation 203 until all the recommendations in chapter XIII had been considered.
Recommendation 204
Ms. Perkins (United Kingdom) said that recommendation 204 was an inappropriate rule for intangible property, which was the currency of the financial markets.
Under certain circumstances, the recommendation would give rise to irreconcilable ambiguities for the forum court, and uncertainty was the very thing that the Commission was seeking to eliminate.
Some delegations considered that the practical advantages of recommendation 204 for regular transactions involving the bulk assignment of receivables or the assignment of future receivables outweighed the disadvantages of uncertainty in respect of irregular transactions.
However, it could be inferred from the comprehensive carve-out in the Assignment Convention for financial contracts and financial instruments, i.e. other intangibles, that recommendation 204 did not work for situations other than the bulk assignment of receivables or the assignment of future receivables.

By way of illustration, she described a situation in which an assignor granted a first security interest (interest A) in one location and then moved location and, retaining possession, granted a second security interest (interest B) in the second location.
The forum court could then be faced with a situation in which either both interests or neither interest had priority.
If, for example, interest A in the intangible had been created first but registered second and interest B had been created second but registered first, and if the law of the first location provided that priority was determined by the date of creation and the law of the second location provided that priority was determined by the date of registration, both security interests would take priority over one another under recommendation 204.
Similarly, if an assignment of a letter of credit by the assignor for security purposes in one location was followed by a reassignment by the assignee from a different location, and notice to the issuing bank was not required by the law of the first location in order to acquire priority but was required by the law of the second location, the forum court would again be faced with a situation in which both interests had priority.

It followed that recommendation 204 was inappropriate, possibly in all cases but certainly for intangibles other than the bulk assignment of receivables and the assignment of future receivables.
Mr. Deschamps (Canada) said that situations such as those just described potentially arose not only in respect of financial contracts but also in respect of other kinds of intangible property or trade receivables.
If an assignor located in one State granted an assignment to a first secured creditor, and the assignor's chief place of business was subsequently moved to a second State from which the assignor granted an assignment to a second secured creditor in respect of the same receivable, letter of credit or financial contract, it was unclear which law should apply to the competing claims of the two secured creditors, especially if the law of the first State gave priority to the first creditor and the law of the second State to the second creditor.
He submitted that the solution lay in recommendation 216, according to which, in the situations described by the representative of the United Kingdom, the law of the new location of the grantor would determine priority as between competing claimants.

Mr. Bazinas (Secretariat) said that the draft Guide treated assignments from assignor A to assignee B in different countries that were subsequently assigned to assignee C on the basis of the Assignment Convention as subsequent assignments that did not create a priority conflict because the first assignee took the position of the assignor.
It was thus not a matter of competing claims giving rise to a conflict of priority.

Ms. Perkins (United Kingdom) said that, while recommendation 216 might settle matters for the forum court, it did so in a manner that was largely arbitrary as between the assignees of the first and second security interests. In situations where there were competing assignments and the priority rules were different in the two locations of the assignments, the forum court was required to apply the priority rules of the second location.
Such a rule was disadvantageous for the first assignee who could not be sure that it was guaranteed priority at the time the security interest was granted, since future changes in the location of the grantor might affect the priority and effectiveness of its security interest vis-à-vis future assignees.
Hence, recommendation 216 did not provide an adequate solution to the issues arising from recommendation 204.
Her objection to recommendation 204 would perhaps have been better phrased as a concern about the position of the debtor, who was often a financial markets debtor, rather than about the dilemma for the forum court.

Where a security interest was created in a financial contract, it was important for the debtor under that contract, who could be an out-of-money party under a derivatives or foreign exchange contract or the issuer of a letter of credit, to know whom to pay if the debt was assigned.
If the law governing those issues was identified according to the location of the grantor or assignor and that location was subject to change, the financial markets debtor would be unable to identify with any certainty the law applicable to priority questions and vis-à-vis new assignees.
Mr. Bazinas (Secretariat) said that recommendation 216, which provided that the relevant location was that of the grantor at the time the priority conflict arose, might create the impression that the assignee in the original location would automatically lose priority.
However, under recommendation 46 the assignee in the initial location could preserve its third-party effectiveness and priority by meeting the requirements for third-party effectiveness of the new location within a grace period.

Ms. Kaller (Austria) said that she agreed with the comment of the representative of the European Commission on the complexity of the issues addressed in chapter XIII, which had been discussed in a number of forums.
While she was uneasy about its inclusion in the draft Guide, she respected the fact that decisions had already been taken, inter alia in the context of the United Nations Assignment Convention, which could not easily be reversed.
However, the solution provided in recommendation 204 was unsatisfactory.
In the context of the European Commission proposal for a regulation of the European Parliament and the Council on the law applicable to contractual obligations (Rome I), the law of the assignor's location and the law governing the assigned receivable were being discussed as the options for the law applicable to third-party effects of assignments.
Mr. Ghia (Italy) endorsed the statements by the representatives of the United Kingdom and Austria.
He expressed a preference for the application of the lex contractus chosen by the parties.

Ms. Walsh (Canada) said that recommendation 213 addressed the concern raised by the representative of the United Kingdom regarding the need for a debtor to know whom it must pay so as to be discharged from its obligation.
The recommendation confirmed that the applicable law was that governing the payment obligation, in other words the contract that gave rise to the obligation that had been the subject of an assignment or the creation of a security right.
Whether the person entitled to payment was also entitled to priority was a matter to be agreed among the competing assignees or secured creditors.
Account debtors that fulfilled their payment obligations in accordance with the law governing the contract out of which the obligation arose were always protected.
That law also governed the existence and extent of any right of set-off.
Mr. Weise (Observer for the American Bar Association) said that it should be borne in mind that the choice of applicable law also governed effectiveness against third parties.
If the law that governed the receivable also governed third-party effectiveness, there would potentially be multiple registrations in multiple States.

It should also be borne in mind that rules concerning applicable law were generally based on the assumption that other States had comparable laws, so that the hypothetical situation described by the representative of the United Kingdom in which effectiveness against third parties occurred upon creation would rarely arise.
Mr. Murray (United Kingdom) said that the structure of the draft Guide, which required legislators to refer to recommendations 204, 216 and 46 when addressing the issue under discussion, was inconvenient.
Moreover, recommendation 46 appeared to require a vigilance on the part of the assignee that was inconsistent with financial-market expectations.
While recommendation 213 stated the formal position with regard to debtor protection, debtors of financial claims were frequently not indifferent as to whether the ultimate owner of the debt was their relationship bank or a vulture fund.
They usually wished to be certain that the law which they had agreed should govern the debt they owed would also determine the question of the assignability of a claim.

The Chairperson reminded the Committee that the pending debate on financial contracts might help to resolve some of the issues raised.
She did not see any justification in the light of the discussion for amending recommendation 204.
Ms. McCreath (United Kingdom) reiterated her delegation's serious concern about recommendation 204, which she felt was shared by several other delegations.
She proposed deferring a final decision on the recommendation until after the discussion of financial contracts.
Mr. Kemper (Germany) expressed support for that proposal.
Mr. Deschamps (Canada), referring to the question of the debtor of a receivable under a financial contract that was opposed to having payment obligations to a vulture fund, said that the issue of whether the receivable was assignable was addressed in recommendation 213 (b).
If the contract giving rise to the receivable contained an anti-assignment clause, and if that clause was valid under the law governing the contract, the clause would be effective unless the receivable was a trade receivable.

[... the TARGET BLOCK appears here ...]

The Chairperson said that the decision on recommendation 204 had been based not only on the discussions in the Working Group and the Commission but also on six years of negotiations regarding the Assignment Convention, in which the United Kingdom had participated.
She took it, however, that the Committee agreed to include cross-references to the group of relevant recommendations.
Recommendation 204 was adopted on that understanding.
Mr. Voulgaris (Greece) drew attention to the issue of industrial and intellectual property rights, which were subject to registration.
In his view, registered industrial and intellectual property rights should be governed by the law of the State in which the registration took place.
Mr. Bazinas (Secretariat) said that the language that had been included in a previous version of recommendation 204 concerning the law that would determine the location of the registry for intangibles subject to registration had been deleted pending discussion of a project relating to security rights in intellectual property and the proposals emanating from the Colloquium on Security Interests in Intellectual Property Rights held in Vienna in January 2007 (A/CN.9/632).

The commentary would explain how the draft Guide should be applied in principle to security rights in intellectual property pending completion of any future project, on the understanding that some recommendations might prove to be inappropriate and that enacting States might need to adjust their legislation.
In cases of inconsistency, intellectual property law would prevail.
Recommendation 205
Mr. Bazinas (Secretariat) said that the note to the Commission following recommendation 205 related to the second sentence of that recommendation, which stipulated that in a priority conflict involving the rights of competing creditors that were registered in an immovable property registry, the law of the location of the registry should be applied.
The note suggested restricting the scope of that rule to situations in which registration in the immovable property registry had priority consequences.
If registration had no bearing on priority issues, the law of the location of the assignor would apply.

Mr. Sigman (United States of America) expressed support for the suggestion in the note to the Commission.
The same principle would be applicable to recommendation 202 and to any other provision relating to a registry.
He therefore proposed that each reference to an asset-based registry should be reviewed in order to determine whether registration had priority consequences, as opposed to tax or other consequences unrelated to priority.
The Chairperson said that, if she heard no objection, she would take it that the Committee concurred with the proposal made by the representative of the United States and wished to act on the suggestion contained in the note to the Commission.
Recommendation 205, as amended, was adopted.
Recommendation 206
The Chairperson reminded the Committee that the Working Group had decided, after extensive and inconclusive discussion, to present two alternatives, A and B, in the recommendation.
Mr. Wiegand (Switzerland) expressed strong support for alternative B, which effectively balanced the interests of the client and the bank on the basis of party autonomy.
He had so far failed to hear any convincing argument regarding the interests that alternative A was designed to protect.

Mr. Umarji (India) expressed support for alternative A, which established that the law of the State in which the bank maintaining the account had its place of business should be applied.
As banks were required to comply with a variety of rules concerning, inter alia, taxation, suspicious transactions and money laundering, it was only logical that matters relating to security rights in a bank account should be governed by the law of the location of the bank.
Mr. Riffard (France), supported by Ms. Kaller (Austria), said that alternative A did not seek to protect the interests of any particular party and was thus the most objective solution.
Mr. Sigman (United States of America), supported by Ms. McCreath (United Kingdom), said that although he strongly felt that alternative B was more neutral and easier to apply, he proposed, in the light of the persistent divergence of opinion, that both options should be retained.

Ms. Kolibabska (Poland) said that, in the light of an extensive debate in Poland on the subject matter of recommendation 206, she supported alternative A as the option that was more conducive to stability.
Mr. Cochard (Observer for the Association française des entreprises privées) expressed support for alternative A, which was preferable both on account of its consistency with other regulations applicable to banks and in the interests of legal certainty.
It was far easier to determine the applicable law on the basis of the location of a bank than by seeking to obtain access to an account agreement.
Mr. Patch (Australia) asked how alternative A would apply to a situation in which a bank account was not to be found in any physical location but was maintained by an Internet bank.
The Chairperson said that the issue had been discussed in the Working Group and had given rise to conflicting views.
Recommendation 205 was adopted.

Candidate 0:
  Question: How did United Nations Commission on International Trade Law delegates propose resolving a 2007 dispute over financial contracts?
  Answer: some form of cross-referencing should be included in recommendation 204

Candidate 1:
  Question: How were remaining concerns about financial contracts to be handled during United Nations Commission on International Trade Law discussions in 2007?
  Answer: the discussion should be deferred until the recommendations on financial contracts had been considered
````

### Output: choice 0

Finish reason: `stop`.

````text
[
  {
    "index": 0,
    "grounding": 3,
    "precision": 4,
    "numerical_fidelity": 5,
    "reason": "The answer is a verbatim span from Ms. McCreath's suggestion, but it is presented as resolving a 'dispute over financial contracts' when it concerns recommendation 204, so the question requires a small inferential step. The '2007' date is not in the target block, and the answer is tight with only a minor mismatch to the question framing."
  },
  {
    "index": 1,
    "grounding": 3,
    "precision": 4,
    "numerical_fidelity": 5,
    "reason": "The answer is a near-verbatim span of Ms. McCreath's statement that the discussion be deferred. The question's 'remaining concerns' framing loosely blends the Chairperson's remark with McCreath's proposal, and the proposal is not attributed to her, which calls for a small inference. The answer is tight, and the '2007' in the question is unsupported but does not affect the answer."
  }
]
````

### Recorded usage

````json
{
  "cached_tokens": 0,
  "completion_tokens": 345,
  "prompt_tokens": 11539,
  "provider_cost": 0.026528,
  "reasoning_tokens": 0
}
````

### Input size diagnostics

````json
{
  "input_characters": 36786,
  "context_capacity_exceeded": null
}
````

## Call 015: faithfulness

Request: `260c1d78d5d842d180b1adc1fb36e244`. Task: `mode/un/2002/cedaw/c/sr_560#20/lookup`.

Model: `anthropic/claude-sonnet-5.5`. UTC: 2026-09-30T17:56:01.391844+00:00.

API status: **response**. Duration: 3.678778 seconds.

### Request settings

````json
{
  "extra_body": {
    "thinking": {
      "budget_tokens": 16000,
      "type": "enabled"
    }
  },
  "max_tokens": 32000
}
````

### Input 1: system

````text
You are a strict faithfulness grader for legal and policy question-answer pairs built from United
  Nations documents.

You will receive a three-section context and THREE question-answer pairs.
The context is:
- "### TARGET BLOCK" — the passage the questions are supposed to be about, in one or more language
  versions.
- "### REFERENCED DOCUMENTS" — other documents CITED by the target block, each supplied as its
  symbol, title, and text — provided ONLY so the target block's citations can be understood, the way
  a footnote helps a reader.
- "### DOCUMENT CONTEXT" — surrounding text of the SAME document (its opening and neighbouring
  passages), supplied so that the target block can be understood: it resolves which mission "the
  Mission" is, which country "the Government" governs, what period a report covers, and similar
  referring expressions.
BOTH supporting sections are for UNDERSTANDING ONLY. Using them to resolve a referring expression in
  the question or answer (naming "the Mission" as UNAMIR, identifying what a cited resolution
  concerns) is legitimate and must NOT be penalised. Using either of them as a source of answer
  substance is a grounding failure — the answer's facts must come from the TARGET BLOCK itself,
  fully.

THREE question-answer pairs (questions may be in any language; each answer matches its question's
  language). Grade each pair on three sub-criteria, each 1–5. Do NOT evaluate query shape or
  retrieval quality — those are handled separately. Focus only on how faithfully each answer
  reflects the supplied text.

GRADING INSTRUCTIONS:
- Grade each of the three pairs independently and against the absolute rubric below — not relative
  to the other two.
- Do not let similarity or dissimilarity between the three pairs influence any individual grade.
- Evaluate each pair on its own merits before moving to the next.

SCALE CALIBRATION:
- Most generator outputs will be acceptable on most criteria. "Acceptable" is not the same as
  "excellent."
- 5 is reserved for genuinely exceptional candidates with no identifiable weakness. If you can point
  to any imperfection, it is not a 5. 5s should be uncommon.
- 4 means the candidate is very good but has exactly one minor, identifiable issue. You must be able
  to name the issue.
- 3 is the default grade for a candidate that is acceptable and does the job, with one clear
  weakness. It is not a punishment grade — most acceptable candidates will receive 3s.
- 2 and 1 are reserved for candidates with real, identifiable problems. Do not avoid using them when
  a candidate qualifies.
- Before assigning any 4 or 5, pause and ask: "What specifically makes this better than a 3?" If you
  cannot answer concretely, the grade is 3.

SUB-CRITERIA:

1. GROUNDING (1–5): Is the answer supported by a contiguous span of the TARGET BLOCK?
   The supporting text means the TARGET BLOCK alone. Resolving a referring expression through the
     REFERENCED DOCUMENTS, the DOCUMENT CONTEXT, or the metadata lines is legitimate disambiguation,
     not an inferential step. Anything more is.
   Cap the grade at 2 if any part of the answer's substance — a fact, figure, list, reason, or
     condition — is stated only in a REFERENCED DOCUMENT or only in the DOCUMENT CONTEXT and not in
     the target block. Cap at 1 if the answer's substance mainly comes from outside the target
     block.
   5 — Answer is taken directly from a single short contiguous span of the target block. Every word
     of the answer is explicitly present or is a trivial rewording of explicit content. No inference
     whatsoever. (Rare.)
   4 — Answer is fully supported but requires reading across two adjacent sentences, OR is from a
     single span with minor trivial rewording that a strict reader might flag.
   3 — Answer is grounded in the target block but requires one small, defensible inferential step —
     connecting a pronoun to its referent, combining a figure with its unit, or similar.
   2 — Answer is partially supported: some parts grounded in the target block, other parts not
     (including parts taken from a REFERENCED DOCUMENT or the DOCUMENT CONTEXT).
   1 — Answer requires significant inference, outside knowledge, or is not in the target block at
     all.
   CITATION RULE (UN): UN texts constantly cite other instruments ("the measures imposed by
     paragraph 20 of resolution 1493 (2003)"). If the answer's substance sits behind such a citation
     rather than in the target block's own words, score at most 2 (1 if the answer consists mainly
     of such content) — REGARDLESS of whether the cited document was supplied in the REFERENCED
     DOCUMENTS section. References exist for understanding, never as answer material.
   ATTRIBUTION RULE (UN): summary records report delegates' statements, letters convey a
     government's position, and reports state the reporting body's findings and estimates. If the
     target block attributes a claim, estimate, or assessment to a speaker or body and the answer
     (or the question it responds to) presents that claim as established fact with the attribution
     stripped, cap GROUNDING at 2 — the supplied text supports the attributed claim, not the bare
     assertion.

2. PRECISION (1–5): Does the answer add unsupported details or padding?
   5 — Answer is the shortest possible span that fully answers the question. Not one extra word. No
     surrounding context, no hedges, no elaboration. (Rare.)
   4 — Answer is grounded and tight but includes one short fragment of adjacent context that could
     have been cut.
   3 — Answer is grounded but includes one unsupported detail, generalization, or piece of padding.
   2 — Answer includes multiple unsupported details, or uses speculative framing ("likely,"
     "approximately," "it seems") where the passage is specific.
   1 — Answer is largely padded with content not in the passage, or is a rewrite rather than an
     extraction.

3. NUMERICAL & CITATIONAL FIDELITY (1–5): Are numbers, dates, amounts, and official identifiers
  reproduced exactly? (JSON key remains "numerical_fidelity".)
   5 — All numbers, dates, durations, monetary amounts, percentages, troop figures, and official
     identifiers (document symbols, resolution and paragraph numbers) match the passage
     character-for-character (e.g., "resolution 2374 (2017)" preserved as-is, not "Resolution 2374";
     "S/1994/565", not "S/1994/565/Rev.1"; "up to 5,500 troops", not "about 5,000 troops"; "within
     30 days", not "in about a month"). Dates rendered in the answer language's standard format
     count as exact if day, month, and year are unchanged ("15 July 1994" for "le 15 juillet 1994").
   4 — All values and identifiers are correct and preserved, but with a trivial formatting
     difference (e.g., "30-day period" vs. "within 30 days", or a spacing/punctuation variant of an
     identifier).
   3 — One number or date is rounded or approximated, one identifier is truncated (e.g., year
     dropped from a resolution number), or one duration is converted to a different unit.
   2 — Multiple values or identifiers rounded, reformatted, truncated, or partially dropped.
   1 — Numbers, dates, or identifiers invented, significantly changed, or contradicted by the
     passage.
   N/A — Answer contains no numerical or citational content. Score this sub-criterion as 5 if N/A.

Output valid JSON only — a list of three objects, one per candidate, in the order the candidates
  were provided (index 0, 1, 2):
[
  {
    "index": 0,
    "grounding": <1-5>,
    "precision": <1-5>,
    "numerical_fidelity": <1-5>,
    "reason": "one short sentence explaining the grades"
  },
  {
    "index": 1,
    "grounding": <1-5>,
    "precision": <1-5>,
    "numerical_fidelity": <1-5>,
    "reason": "..."
  },
  {
    "index": 2,
    "grounding": <1-5>,
    "precision": <1-5>,
    "numerical_fidelity": <1-5>,
    "reason": "..."
  }
]

ACTUAL BATCH SIZE: This request contains exactly 2 candidates. Return exactly 2 grade objects, using indices [0, 1]. Grade only supplied candidates. Any references above to THREE pairs or three example objects describe a typical batch; this actual batch size overrides those counts. All scoring criteria and calibration remain unchanged.
````

### Input 2: user

````text
### TARGET BLOCK — write the questions about THIS text

[EN] Document: CEDAW/C/SR.560
  Title: Committee on the Elimination of Discrimination against Women
44. The Government was concerned by the high unemployment rate among women.
To some extent the figures were skewed by the fact that the long-term unemployed were not dropped from the count.
There had been a reduction in some types of female unemployment over the past two years.
Like the other European countries, Belgium had a national employment plan that aimed at employment for all but placed special emphasis on quality jobs.
Many of the measures under that plan were particularly relevant to women, because they specifically targeted the long-term, the older and the low-skilled unemployed.
45. Ms. Verzele (Belgium) said that the project of removing inequalities from the tax system was still ongoing; the Ministry of Finance was studying the matter carefully and there would undoubtedly be more information to give in the next report.
With regard to development aid, Belgium was a staunch advocate of equality of opportunity.
The communities and regions had sole responsibility for education, but it should be understood that they, as well as the Federal Government, had to approve international treaties before they could be ratified by Belgium, so that they were also committed to implementing the treaty provisions.
Although no representative of the German-speaking community was present, it had contributed to the report.

### REFERENCED DOCUMENTS — none. The target block cites no other document available in the corpus.

### DOCUMENT CONTEXT — surrounding text of the SAME document, supporting context only. It resolves what the target block leaves implicit; it is never a source of answers.

[EN] Document CEDAW/C/SR.560 — surrounding passages
Committee on the Elimination of Discrimination against Women
Twenty-seventh session
Summary record of the 560th meeting
Held at Headquarters, New York, on Monday, 10 June 2002, at 3 p.m.
Chairperson: Ms. Acar (Vice-Chairperson)

Consideration of reports submitted by States parties under article 18 of the Convention (continued)
Combined third and fourth periodic reports of Belgium (continued)
In the absence of Ms. Abaka, Ms. Acar, Vice-Chairperson, took the Chair.

1. At the invitation of the Chairperson, Ms. Adriaenssens, Ms. Franken, Ms. Paternottre, Ms. Stevens and Ms. Verzele (Belgium) took places at the Committee table.
The position of the Minister for Equal Opportunities near the top of the federal hierarchy gave added impetus to the process.
Various initiatives by the regions and communities would be described later.
The Parliament elected in 1999 had established an inter-ministerial conference on literacy, which would deal with the literacy problems of migrant women.
In response to Ms. Manalo's question, she said that the French-speaking community was coordinating the gender equality activities of its various ministries, and had formulated a plan on equal opportunities and submitted proposals to the Government to that end.
The Equal Opportunities Service of the French-speaking community operated on a budget of 756,000 euros, but specific projects were financed by the ministries concerned.
The training of female executives would not happen overnight but was a long-term process.

4. She did not have figures available on the number of women in high-level posts in the press, or on female members of the Senior Audio-Visual Council.
She would provide that information in writing, together with statistical information on the implementation of the code of ethics adopted in 1994 by various French-speaking television stations.
She believed there had been a misunderstanding with regard to gender mainstreaming in the Flemish community, which had been the first to launch mainstreaming efforts following the Fourth World Conference on Women, held in Beijing.
The community had set up the Interdepartmental Commission on Equal Opportunities, and mainstreaming initiatives of the various departments were coordinated by the Equal Opportunities Unit in Flanders. It was not always an easy task; a delicate balance had to be struck between urging the various ministries to ensure mainstreaming within their own areas of competence and respecting their autonomy.
The budget had grown exponentially, from 120,000 euros in 1995 to 4.3 million euros in 2002.
The Equal Opportunities Unit in Flanders did not work with women exclusively but rather targeted a number of other vulnerable groups as well, including migrants, disabled persons and children.

6. Various mainstreaming instruments had been developed, including legislation establishing quotas and mandating implementation of the Beijing Platform for Action and a questionnaire which set out fundamental considerations for policy-making from a gender perspective.
A local gender impact assessment instrument had been developed two years later in 1999, on the basis of lessons learned from the original questionnaire.
7. She agreed that perhaps the report emphasized implementation of the Beijing Platform for Action at the expense of the Convention itself.
That was partly because of the legislation on implementing the Beijing Platform and partly because the Platform outlined clear and practical strategic goals for the Government, non-governmental organizations and other entities.
Her Unit would make every effort to compensate for giving insufficient coverage to the implementation of the Convention.
8. Turning to Committee members' questions on migrant women, she said that the Flemish community was responsible for receiving migrants, finding shelter for them and helping them adapt to their new life.
The Equal Opportunities Unit had established an organization to coordinate actions by all migrant women, from various ethnic groups.
Studies showed that second- and third-generation migrant girls performed better in school than boys but that many did not pursue a higher education.

In 1999, the Equal Opportunities Unit had launched a project, in conjunction with institutions of higher learning, to increase the number of migrant girls in higher education.
A separate hotline had been set up for migrant women in need of assistance.
9. Replying to the question concerning the Unit's relationship with non-governmental organizations, she said that the Women's Council, which coordinated the work of the various women's organizations in the Flemish community, was allocated resources from her Unit's annual budget.
The Unit had also conducted a workshop for the six existing Flemish women's organizations to obtain their input and offer them guidance where necessary.
Every effort was made to encourage the media to help transform mentalities without violating constitutional freedoms.
An impact assessment of gender mainstreaming in the media would be completed by the end of the year.
Zorra, an organization that acted as a watchdog for advertising and the media, had organized an e-mail forum for receiving complaints and attempted to discourage advertisers from publicizing sexist material.
She would give the Committee statistics on female journalists in a written response.

11. Ms. Verzele (Belgium) pointed out that communauté flamande should be translated as Flemish community, not Walloon community.
12. Ms. Livingstone Raday cautioned against using mediation to deal with violence against women, as it put pressure on the victims and perpetuated the problem by forcing all parties to compromise.
She wondered whether the State party recognized that danger and had taken measures to offset it, for example, by restricting mediation to first-time offenders, or to offences where physical violence or psychological abuse had not been serious.
She also wondered whether victims were provided with an independent advocate to represent them in proceedings.
13. Ms. Gaspard hailed the State party's introduction of legislation to increase the number of female candidates for elective office but noted that the number actually elected had not necessarily increased and that, in certain cases, even the minimum quota of candidates had not been met.
She would appreciate a progress report on the revision of the progressive 1994 law promoting parity in electoral lists and stressed that, beyond participation in political life, women must also be integrated into the civil service and the advisory bodies, which played a strategic role in government.

She wondered whether a 1990 law (revised in 1997) to increase the number of females on those advisory bodies was being properly implemented and what other measures the State party could take to that end.
14. Referring to article 8, she expressed concern at the decline in the number of women taking the foreign service entrance examination and wondered what action would be taken to remedy the situation.
15. Ms. Achmad said that she fully supported Ms. Gaspard's remarks and shared her concern.
She wondered how the Belgian Government would ensure the sustainability of its affirmative action policies to increase women's participation in political life.
Was it taking measures to ensure that leaders in Government, political parties and trade unions complied with the State party's obligations under the Convention?
She echoed previous speakers' concern that the report did not focus on the Convention as the primary instrument to promote equality.

Although such facilities constituted major support for female diplomats, she hoped that they would also be a means of encouraging men to shoulder a greater share of the responsibilities of family life.
She praised the State party's approach to dealing with the media through dialogue and suggestion; perhaps that same approach would be effective with the Ministry of Foreign Affairs and even non-governmental organizations and labour unions.
17. Ms. Kapalata agreed wholeheartedly with Ms. Gaspard's questions and comments concerning articles 7 and 8.
She welcomed the introduction of a quota system, which was a step in the right direction, and hoped that it would be extended to all levels of government. The report seemed to imply, under article 8, that it would take some time for female diplomats to attain the status necessary to become head of post.
She called for special measures to expedite the process and hoped to see tangible results in the State party's next report.

18. Ms. Tavares da Silva asked whether there had been any provisions in the former electoral law to ensure that women candidates were not relegated to the lower places on electoral lists, and whether there had been any investigation as to why the number of women taking part in entrance examinations for the diplomatic service had declined sharply in recent years and what barriers women might be facing in that regard.
19. She added that the Beijing Platform for Action and the Convention on the Elimination of All Forms of Discrimination against Women were complementary; the former was a legal text, and the latter a policy document.
20. Ms. Manalo asked what was the policy in relation to situations where spouses were employed in the career diplomatic service, whether both partners were encouraged to continue their careers, and what was the situation when one of them was required to take up a foreign posting.

21. Ms. Verzele (Belgium) said that her delegation agreed with Ms. Tavares da Silva as to the respective roles of the Beijing Platform for Action and the Convention.
22. Her Government was well aware that gender equality should be a concern for men as well as women, and awareness and involvement by men must be improved, particularly in respect of family activities.
23. The 1994 law on gender quotas on electoral lists applied to the composition of the lists themselves; it did not require that a particular result should be achieved. Given the functioning of the system of electoral lists under the Belgian system of proportional representation, candidates whose names appeared at the top of the list were more likely to be elected.
It was also true that, owing to regional peculiarities, it was more difficult for women candidates to be successful in the Walloon region.
24. On 30 May 2002, a new electoral law had been adopted.
It would require that 50 per cent of candidates should be women and that men and women candidates should alternate in the first and second places at the top of each list; furthermore, that legislation did not include any transitional provisions.

She drew the Committee's attention to the information on page 39 of the English-language text of her delegation's responses to the list of issues, concerning the composition of advisory bodies: about 28 per cent of the positions involved were now occupied by women.
As for the decline in the numbers of women seeking to enter the diplomatic service, plans were being prepared for information campaigns to improve awareness among young women of the opportunities available to them; the Government also planned to increase the proportion of women on the juries for the corresponding entrance examinations.
25. Ms. Stevens (Belgium) said that the measures taken by the Ministry of Foreign Affairs to improve the representation of women in the diplomatic service included a day-care centre and the availability of a Family Officer.
These services were available for use by both women and men.
Research was being undertaken to determine whether the fall in the numbers of women seeking to enter the diplomatic service might have been influenced by developments in the labour market as a whole.
As for the position of spouses in the diplomatic service, she was not aware that there had ever been an attempt to discourage the spouse of a diplomatic officer from remaining in employment.

A working group was looking into ways of helping the spouses of diplomatic officials posted abroad to continue to work; bilateral agreements with receiving States were one means of achieving that.
26. Ms. Paternottre (Belgium) said that steps had been taken to contact young women who had attended briefings on diplomatic careers but had decided not to take the entrance examinations, in order to determine the reasons for their decision.
One reason was that young women desiring a diplomatic career seldom had a spouse who did not work.
It would, however, be very difficult to explain why there were fewer women candidates in a specific year.
27. Responding to an earlier question relating to family mediation, she said that it was an experiment being conducted in the Brussels region.
When the police were called to deal with a problem of domestic violence, they asked the two partners whether they wished to avail themselves of a mediation service.
The mediation was offered not as an alternative to the usual investigation and prosecution but as a parallel, complementary service.

The first phase had involved invoking the federal legislation to increase the numbers of women candidates on electoral lists; the second phase had involved encouraging the public to vote for women candidates; and the third phase, implemented after the elections, had focused on political leaders, seeking to persuade them to give decision-making positions to women who had been elected.
The number of women candidates elected had increased to 27 per cent, an improvement of seven percentage points over the previous elections, and there had been an increase in the numbers of women given executive mandates.
29. To follow up those achievements, a strategic plan had been established, consisting of two tracks: the first to empower women who had been elected, so that they were not left out of decision-making processes, and the second to prepare more women to become candidates in future elections.
A project had been set up for the mentoring of women candidates who had been elected to the Community Councils, and a gender training course for politicians was being made available by a non-governmental organization.
The influence of the media was also being used: press conferences with political leaders in Flanders were being organized, at which they were asked to explain what they were doing to empower women and increase the numbers of women candidates.

An instrument known as the "family and business audit" was being developed to enable employers to determine how "family-friendly" their organizations were; it would be ready by the end of 2002, and it was hoped that it would help to improve awareness.
Articles 10 to14 30. Ms. Corti congratulated the reporting State on its health policies, particularly regarding HIV/AIDS.
Recalling that the Committee had been informed that the problems of elderly women were the object of much debate in Belgium, she asked which specific aspects were being considered; in particular, she wished to know what measures and institutions existed to deal with the problem of solitude among older women; with the increase in life expectancy, the scale of that problem was growing.
31. Ms. Abaka expressed concerned at the apparent lack of uniformity in compliance with obligations under the Convention, particularly in the area of health, in the country's different regions.
She also wondered who spoke for the inhabitants of the German-speaking area and of the Brussels region, and whether there was an independent body in Belgium which could coordinate all aspects of human rights throughout the country.

32. She expressed concern at the steady increase in teenage pregnancies.
Although the abortion statistics were not very high, she noted that some of the females undergoing abortions were between the ages of 14 and 16, and wondered whether some of those early pregnancies might be due to rape or incest.
In the case of 18-year-old women having abortions, she asked what proportion of them were single and married, how many were still studying and how many were employed.
She also asked what had been the impact of the campaign launched in the French community in 2000 to promote awareness of contraceptive methods among adolescents.
33. Ms. Kwaku asked what was the percentage of women with disabilities in Belgium, and what measures and provisions existed to assist and protect them.
34. Ms. Livingstone Raday said that the report showed considerable sensitivity to analysing the problem of gender discrimination in a sex-neutral manner, and included data on discrimination against men in certain areas such as employment. She wondered whether that sensitivity was not somewhat premature, since the overall picture showed that women were disadvantaged in what was still a patriarchally structured labour market, as well as in politics and in their subjection to violence.

35. Turning to the need to reform professional classifications and ensure equal pay for work of equal value, she asked the reporting State to specify whether it had pursued an aggressive legal policy on such matters, and whether any cases had been brought before the courts.
36. Ms. Goonesekere noted that, according to the State party's report, Belgium did not have a systematic compilation of jurisprudence on gender discrimination.
It appeared that some legal concepts implicit in Belgian law were not fully in conformity with the Convention.
For example, sexual abuse was treated as a problem of morals, whereas it should properly be treated as the infringement of the right to security of person; the crime of procuring was defined by the legal criterion of abnormal profit, suggesting that it was permissible to make a "normal profit" by exploiting the prostitution of others.
In many countries a body of feminist jurisprudence and an understanding of law in relation to gender discrimination had been the product of the efforts of women lawyers and academics.
She was therefore particularly interested in knowing what was being done to further women's access to legal education.

37. According to the report, in practice girls did not have the same educational opportunities as boys.
Since the Federal Government was party to the Convention but the Communities had responsibility for education, she wondered whether the Federal Government had a definite say in educational policy and a monitoring role to ensure that article 10 of the Convention and indeed article 24 of the national Constitution were respected.
38. She noted Belgium's valuable contribution to enhancing the status of women in developing countries through its Commission on Women and Development in the Ministry for Cooperation and Development.
She wondered what influence Belgium could bring to bear on the international financial institutions to make their policies more gender-sensitive.
39. Ms. Gaspard said, in regard to education, that in the next report the Committee would like to have aggregated statistics for the nation as a whole and comparable data across communities.
The Committee would also like to be told not just about the policies adopted but also about the results achieved.
Although women were doing well in terms of university attendance, there were still few women in higher posts and decision-making positions in education.

40. With regard to employment, she was disturbed by the high unemployment rate among women and hoped in the next report to see information about the results of remedial action taken.
She was greatly concerned about the high percentage of women in part-time work, which would have a serious impact on their retirement income.
In that regard, she would like to know whether any progress had been made with individualization of social security entitlements.
It was also disturbing that, despite considerable government efforts, the pay disparities between men and women still ranged from 25 to 30 per cent.
41. In the next report the Committee would appreciate information on the health situation of migrant women.
In view of the sweeping reform of the tax system in Belgium, studies should be done on the impact of the changes on women, especially on single women heads of household.
42. Ms. Paternottre (Belgium), in response to the questions about the health of older women, said that health care was the shared responsibility of the Federal Government and the communities.
One of the strategic goals of the Ministry of Health was to enable the handicapped and older persons to remain in their homes as long as possible and avoid institutionalization.

The aim of the Ministry's project was to coordinate and develop the structures that were already in place.
Although there were no government programmes specifically addressing the needs of older persons living alone, there were many non-governmental organizations with such programmes, including hot-lines for emergencies.
With regard to the handicapped, at the federal level assistance primarily took the form of disability payments under the social security system, but the regions had other assistance programmes to enable the handicapped to lead normal lives and if possible to rejoin the work force.
43. With regard to equal pay, Belgium had the proper laws, but de facto disparities existed, as the report had frankly stated.
Studies had been undertaken to find out why.
Pay disparity indicators had been developed, and it had been concluded that much of the problem lay in the classifications of job functions.
The Government was working with its social partners to correct the situation, and it was anticipated that by 2006 a new system of occupational classifications by industry would be in place; failing agreement in a given industry, new classifications could be imposed.
There were some court decisions on equal pay, but they tended to date back in time, since they had all been filed only after the person concerned had left the job.

[... the TARGET BLOCK appears here ...]

The delegation did not have a profile of the teenage girls who had opted for abortions, but the numbers were relatively small. For the next report the matter could be researched more thoroughly, and in general the delegation would try to provide the kind of statistics the Committee wanted.
46. Ms. Franken (Belgium), speaking for the Flemish community, said that the community's programmes for older women were chiefly targeted at the feminization of poverty.
The community had policies for the handicapped in general, although not specifically for women, and the emphasis was on integration into society.
With regard to fuller statistics, the Equal Opportunities Unit in Flanders was already working intensively to improve statistics and indicators and would be able to provide more in the next report.
She had some new statistical fact sheets with her which were available to any interested Committee members.
47. Ms. Adriaenssens (Belgium), speaking for the French-speaking community, said that the delegation would respond shortly in writing to the Committee's request for an evaluation of the results of the information campaign on contraception targeted at adolescents in 2000.
In the area of education, under the Belgian federal system the Federal Government did not have enforcement powers, since the communities had sole responsibility for education.

That said, the inter-ministerial body established in 2002 for gender mainstreaming was certainly concerned, among other things, with encouraging the elimination of stereotypes in the educational system.
She had brought with her some recent sex-disaggregated statistics on numbers of graduates and teaching staff.
In the French community some studies were nearing completion on access of women to decision-making posts in universities, and the information would be sent to the Committee.
48. Ms. Verzele (Belgium) said that the Belgian Government was indeed very concerned about the increase in part-time work but was making efforts to ensure that such workers were also covered by social insurance.
Her delegation could provide a fuller explanation in writing.
Articles 15 and 16
49. Ms. Goonesekere asked whether it was a matter of law or of custom for a child to bear the father's name if paternal filiation was established.
She was interested to know whether non-marital cohabitation was recognized for any legal purposes.
She would appreciate further clarification about the restrictions on recognition of repudiation under Muslim law and wondered if other provisions of traditional law, such as minimum age of marriage, were also recognized.

50. Ms. Gaspard said that she was concerned about the recognition of repudiation in Belgium.
Recognition of traditional law was a problem that faced many European countries. Some resolved it by applying the law of the country of residence and others by applying the law of the country of origin.
The latter put women at a considerable disadvantage.
51. Ms. Corti said that she seconded the question raised by Ms. Goonesekere and Ms. Gaspard.
52. Ms. Abaka said that she, too, wished to associate herself with the questions already raised.
In addition, she would like to know the reasons for the increase in divorce rates apparent in the statistics presented by the delegation.
53. The Chairperson, speaking in her personal capacity, said that she, too, would like to understand the thinking behind recognition of repudiation.
For migrant women, conservative community pressures added an additional layer of discrimination to that which all women faced, especially if they were supported by the authorities.

54. Ms. Schöpp-Schilling asked the delegation to clarify how the Belgian Constitution regulated the obligations of the Federal Government with regard to the implementation of international law and how that responsibility was to be reflected in its relations with the regions and communities.
55. Ms. Verzele (Belgium) said that the family name given to a child was prescribed by the Civil Code.
However, a proposal was under discussion in Parliament to allow a choice of father's or mother's name or both, hyphenated, although for practical reasons it was felt that all the children of a couple should have the same last name.
The Government sought to avoid "tourist" repudiation, whereby the husband would leave Belgium and on his return inform his wife that she had been repudiated.
However, there were situations, for example when a women who had been repudiated wished to remarry in Belgium, in which it was to a woman's advantage to have the Government recognize her divorced status.

57. The reasons for the increase in divorce had not, to her knowledge, been studied, but the introduction of consensual divorce might explain some of the increase.
58. Ms. Adriaenssens (Belgium) said that, in the case of the Optional Protocol to the Convention, for example, which related to mixed areas of responsibility, the ratification procedure required the Federal Government to submit to the communities and regions the text of the Protocol together with an explanation of the reasons for signing it.
After hearing the opinion of the Council of State, the communities and regions might approve the text and only then could it be ratified.
59. Ms. Paternottre (Belgium) said that cohabitation was recognized for all legal purposes, including social security and other taxation matters, if the two parties living together signed and filed a declaration of cohabitation with the municipality where they lived.
The Committee looked forward to Belgian ratification of the Optional Protocol and the amended article 20, paragraph 1, of the Convention.

Candidate 0:
  Question: What did Belgium's employment plan emphasize besides employment for all in the 2002 Committee on the Elimination of Discrimination against Women summary record on Belgium?
  Answer: quality jobs

Candidate 1:
  Question: What treaty-ratification role did Belgium's communities and regions have in the 2002 Committee on the Elimination of Discrimination against Women summary record on Belgium?
  Answer: had to approve international treaties before they could be ratified by Belgium
````

### Output: choice 0

Finish reason: `stop`.

````text
[
  {
    "index": 0,
    "grounding": 4,
    "precision": 5,
    "numerical_fidelity": 5,
    "reason": "The target says the plan aimed at employment for all 'but placed special emphasis on quality jobs'; the answer is directly supported, and the 'besides' framing requires reading across a clause, which is a small issue."
  },
  {
    "index": 1,
    "grounding": 4,
    "precision": 4,
    "numerical_fidelity": 5,
    "reason": "The answer is a verbatim span from the target, but it omits that the Federal Government must also approve, and the pronoun 'they' is left without a subject, so the fragment needs minor context."
  }
]
````

### Recorded usage

````json
{
  "cached_tokens": 0,
  "completion_tokens": 239,
  "prompt_tokens": 11868,
  "provider_cost": 0.026126,
  "reasoning_tokens": 0
}
````

### Input size diagnostics

````json
{
  "input_characters": 38197,
  "context_capacity_exceeded": null
}
````

## Call 016: faithfulness

Request: `4ab927c37fa34b9ea97e69dd99d66727`. Task: `mode/un/2009/a/c_2/64/sr_16#3/practitioner`.

Model: `anthropic/claude-sonnet-5.5`. UTC: 2026-09-30T17:57:22.922395+00:00.

API status: **response**. Duration: 3.67133 seconds.

### Request settings

````json
{
  "extra_body": {
    "thinking": {
      "budget_tokens": 16000,
      "type": "enabled"
    }
  },
  "max_tokens": 32000
}
````

### Input 1: system

````text
You are a strict faithfulness grader for legal and policy question-answer pairs built from United
  Nations documents.

You will receive a three-section context and THREE question-answer pairs.
The context is:
- "### TARGET BLOCK" — the passage the questions are supposed to be about, in one or more language
  versions.
- "### REFERENCED DOCUMENTS" — other documents CITED by the target block, each supplied as its
  symbol, title, and text — provided ONLY so the target block's citations can be understood, the way
  a footnote helps a reader.
- "### DOCUMENT CONTEXT" — surrounding text of the SAME document (its opening and neighbouring
  passages), supplied so that the target block can be understood: it resolves which mission "the
  Mission" is, which country "the Government" governs, what period a report covers, and similar
  referring expressions.
BOTH supporting sections are for UNDERSTANDING ONLY. Using them to resolve a referring expression in
  the question or answer (naming "the Mission" as UNAMIR, identifying what a cited resolution
  concerns) is legitimate and must NOT be penalised. Using either of them as a source of answer
  substance is a grounding failure — the answer's facts must come from the TARGET BLOCK itself,
  fully.

THREE question-answer pairs (questions may be in any language; each answer matches its question's
  language). Grade each pair on three sub-criteria, each 1–5. Do NOT evaluate query shape or
  retrieval quality — those are handled separately. Focus only on how faithfully each answer
  reflects the supplied text.

GRADING INSTRUCTIONS:
- Grade each of the three pairs independently and against the absolute rubric below — not relative
  to the other two.
- Do not let similarity or dissimilarity between the three pairs influence any individual grade.
- Evaluate each pair on its own merits before moving to the next.

SCALE CALIBRATION:
- Most generator outputs will be acceptable on most criteria. "Acceptable" is not the same as
  "excellent."
- 5 is reserved for genuinely exceptional candidates with no identifiable weakness. If you can point
  to any imperfection, it is not a 5. 5s should be uncommon.
- 4 means the candidate is very good but has exactly one minor, identifiable issue. You must be able
  to name the issue.
- 3 is the default grade for a candidate that is acceptable and does the job, with one clear
  weakness. It is not a punishment grade — most acceptable candidates will receive 3s.
- 2 and 1 are reserved for candidates with real, identifiable problems. Do not avoid using them when
  a candidate qualifies.
- Before assigning any 4 or 5, pause and ask: "What specifically makes this better than a 3?" If you
  cannot answer concretely, the grade is 3.

SUB-CRITERIA:

1. GROUNDING (1–5): Is the answer supported by a contiguous span of the TARGET BLOCK?
   The supporting text means the TARGET BLOCK alone. Resolving a referring expression through the
     REFERENCED DOCUMENTS, the DOCUMENT CONTEXT, or the metadata lines is legitimate disambiguation,
     not an inferential step. Anything more is.
   Cap the grade at 2 if any part of the answer's substance — a fact, figure, list, reason, or
     condition — is stated only in a REFERENCED DOCUMENT or only in the DOCUMENT CONTEXT and not in
     the target block. Cap at 1 if the answer's substance mainly comes from outside the target
     block.
   5 — Answer is taken directly from a single short contiguous span of the target block. Every word
     of the answer is explicitly present or is a trivial rewording of explicit content. No inference
     whatsoever. (Rare.)
   4 — Answer is fully supported but requires reading across two adjacent sentences, OR is from a
     single span with minor trivial rewording that a strict reader might flag.
   3 — Answer is grounded in the target block but requires one small, defensible inferential step —
     connecting a pronoun to its referent, combining a figure with its unit, or similar.
   2 — Answer is partially supported: some parts grounded in the target block, other parts not
     (including parts taken from a REFERENCED DOCUMENT or the DOCUMENT CONTEXT).
   1 — Answer requires significant inference, outside knowledge, or is not in the target block at
     all.
   CITATION RULE (UN): UN texts constantly cite other instruments ("the measures imposed by
     paragraph 20 of resolution 1493 (2003)"). If the answer's substance sits behind such a citation
     rather than in the target block's own words, score at most 2 (1 if the answer consists mainly
     of such content) — REGARDLESS of whether the cited document was supplied in the REFERENCED
     DOCUMENTS section. References exist for understanding, never as answer material.
   ATTRIBUTION RULE (UN): summary records report delegates' statements, letters convey a
     government's position, and reports state the reporting body's findings and estimates. If the
     target block attributes a claim, estimate, or assessment to a speaker or body and the answer
     (or the question it responds to) presents that claim as established fact with the attribution
     stripped, cap GROUNDING at 2 — the supplied text supports the attributed claim, not the bare
     assertion.

2. PRECISION (1–5): Does the answer add unsupported details or padding?
   5 — Answer is the shortest possible span that fully answers the question. Not one extra word. No
     surrounding context, no hedges, no elaboration. (Rare.)
   4 — Answer is grounded and tight but includes one short fragment of adjacent context that could
     have been cut.
   3 — Answer is grounded but includes one unsupported detail, generalization, or piece of padding.
   2 — Answer includes multiple unsupported details, or uses speculative framing ("likely,"
     "approximately," "it seems") where the passage is specific.
   1 — Answer is largely padded with content not in the passage, or is a rewrite rather than an
     extraction.

3. NUMERICAL & CITATIONAL FIDELITY (1–5): Are numbers, dates, amounts, and official identifiers
  reproduced exactly? (JSON key remains "numerical_fidelity".)
   5 — All numbers, dates, durations, monetary amounts, percentages, troop figures, and official
     identifiers (document symbols, resolution and paragraph numbers) match the passage
     character-for-character (e.g., "resolution 2374 (2017)" preserved as-is, not "Resolution 2374";
     "S/1994/565", not "S/1994/565/Rev.1"; "up to 5,500 troops", not "about 5,000 troops"; "within
     30 days", not "in about a month"). Dates rendered in the answer language's standard format
     count as exact if day, month, and year are unchanged ("15 July 1994" for "le 15 juillet 1994").
   4 — All values and identifiers are correct and preserved, but with a trivial formatting
     difference (e.g., "30-day period" vs. "within 30 days", or a spacing/punctuation variant of an
     identifier).
   3 — One number or date is rounded or approximated, one identifier is truncated (e.g., year
     dropped from a resolution number), or one duration is converted to a different unit.
   2 — Multiple values or identifiers rounded, reformatted, truncated, or partially dropped.
   1 — Numbers, dates, or identifiers invented, significantly changed, or contradicted by the
     passage.
   N/A — Answer contains no numerical or citational content. Score this sub-criterion as 5 if N/A.

Output valid JSON only — a list of three objects, one per candidate, in the order the candidates
  were provided (index 0, 1, 2):
[
  {
    "index": 0,
    "grounding": <1-5>,
    "precision": <1-5>,
    "numerical_fidelity": <1-5>,
    "reason": "one short sentence explaining the grades"
  },
  {
    "index": 1,
    "grounding": <1-5>,
    "precision": <1-5>,
    "numerical_fidelity": <1-5>,
    "reason": "..."
  },
  {
    "index": 2,
    "grounding": <1-5>,
    "precision": <1-5>,
    "numerical_fidelity": <1-5>,
    "reason": "..."
  }
]

ACTUAL BATCH SIZE: This request contains exactly 2 candidates. Return exactly 2 grade objects, using indices [0, 1]. Grade only supplied candidates. Any references above to THREE pairs or three example objects describe a typical batch; this actual batch size overrides those counts. All scoring criteria and calibration remain unchanged.
````

### Input 2: user

````text
### TARGET BLOCK — write the questions about THIS text

[EN] Document: A/C.2/64/SR.16
  Title: (b) Preventing and combating corrupt practices and transfer of assets of illicit origin and returning such assets, in particular to the countries of origin, consistent with the United Nations Convention against Corruption
UNODC also supported the creation and strengthening of regional networks of asset recovery focal points, which could further the dialogue between requesting and requested States.
In view of the growing size and work of the Conference of the States Parties, the Global Forum would then become a public/private partnership forum bringing together political and business leaders.
9. He called on States to continue to engage in constructive dialogue with a view to arriving at consensus decisions at the Conference of the States Parties, particularly with regard to the review mechanisms supported by the Group of Twenty (G-20).
The General Assembly could support the Conference by encouraging States that had not yet done so to ratify or accede to the Convention and encouraging its implementation by Member States.
The accomplishment of such tasks would be feasible only if Member States provided UNODC with strong support so that it would have the resources needed to make the Convention's provisions operational and fully effective.

### REFERENCED DOCUMENTS — none. The target block cites no other document available in the corpus.

### DOCUMENT CONTEXT — surrounding text of the SAME document, supporting context only. It resolves what the target block leaves implicit; it is never a source of answers.

[EN] Document A/C.2/64/SR.16 — surrounding passages
(b) Preventing and combating corrupt practices and transfer of assets of illicit origin and returning such assets, in particular to the countries of origin, consistent with the United Nations Convention against Corruption
(c) Science and technology for development
In the absence of Mr. Park In-kook (Republic of Korea), Mr. Mohamed Cherif Diallo (Guinea), Vice-Chairperson, took the Chair.

1. Ms. Miroux (United Nations Conference on Trade and Development (UNCTAD)), introducing the report of the Secretary-General on science and technology for development (A/64/168), drew attention to its salient points.
Science, technology and innovation had a crucial role to play in stimulating long-term social and economic development and in helping developing countries to meet the Millennium Development Goals (MDGs).
To that end, developing countries would require support to build their technological capacity.
3. Mr. Vlassis (United Nations Office on Drugs and Crime (UNODC)) introduced the report of the Secretary-General on preventing and combating corrupt practices and transfer of assets of illicit origin and returning such assets, in particular to the countries of origin, consistent with the United Nations Convention against Corruption (A/64/122).
Since July, when the report had been finalized, a further five States had ratified the Convention, bringing the number of parties up to 141.
At the third session of the Conference of the States Parties to the Convention, to be held in Doha in November 2009, the most important item for decision would be the establishment of a mechanism to review the implementation of the Convention.

Although a number of meetings had helped to advance the work of the open-ended Working Group on Review of the Implementation of the Convention, further meetings would be held in an effort to reach consensus on pending issues before the Doha session.
4. One matter on which the States parties were agreed was that the review should be based on their own self-assessments.
5. Asset recovery continued to enjoy high priority in the work of the Conference of the States Parties.
Moreover, it had stressed the need for practical tools and guides for the implementation of chapter V of the Convention and networks to build trust and had highlighted the importance of training and capacity-building.
The joint Stolen Asset Recovery initiative (StAR) of UNODC and the World Bank was the main medium through which UNODC acted on the Working Group's recommendations.
The initiative was further conducting a number of policy studies on related topics which would be presented in Doha.

[... the TARGET BLOCK appears here ...]

11. The Chairperson invited the Committee to engage in a general discussion on the item.
12. Mr. Daoud (Sudan), speaking on behalf of the Group of 77 and China, said that globalization posed special difficulties to developing countries and had left the least developed among them on the margins of the world economy.
The globalization of markets meant that economic meltdowns in developed country markets quickly spread to other markets.
Such internationalization of crises brought out the importance of global governance and sound regulatory frameworks that would enable developing countries to enjoy their right to development geared to their own realities.
13. Moreover, while each country bore primary responsibility for its own development, the benefits of globalization could not be shared equitably without strengthened international cooperation and a global partnership for development.
That meant giving developing countries greater voice and participation in international economic decision-making and norm-setting, in particular by reforming multilateral institutions and global governance.

14. In an increasingly knowledge-based world economy, access to technology was vital for development and should be made more available to developing countries; it was a major source of inequality between them and the developed world.
Such access would help them to advance significantly in agriculture, health, energy, trade, water management and environmental protection.
15. The Group of 77 and China invited the States parties to the Convention against Corruption to take further steps to implement it, notably through initiatives for asset recovery, technical assistance and capacity-building.
He stressed the need to continue seeking creative ways to increase collaboration between developing countries and developed countries and their financial institutions in uncovering illicit financial operations, locating the funds and arranging for their return.
Progress on trade and investment agreements and the participation of developing countries in international economic decision-making would be crucial to the global partnership for development.
In that context, he called on the international community to give special attention to the needs of the developing countries, the least developed countries, the landlocked developing countries and the small island developing States.

16. Ms. Ornbrant (Sweden), speaking on behalf of the European Union; the candidate countries Croatia, the former Yugoslav Republic of Macedonia and Turkey; the stabilization and association process countries Albania, Bosnia and Herzegovina, Montenegro and Serbia; and, in addition, Armenia, the Republic of Moldova and Ukraine, said that corruption was a fundamental obstacle to sustainable development.
Efforts to combat it must be predicated on the principles of good governance, integrity, transparency and accountability, which, in turn, called for strong legal and judicial institutions.
As the first global and legally binding instrument on the subject, the Convention against Corruption was an important step in that direction.
It likewise continued to support the further development of the StAR initiative.
17. The European Union also welcomed the joint undertakings of the Commission on Science and Technology for Development and UNCTAD and looked forward to further efforts to bridge the digital divide and promote access to technology for development.

18. The European Union would like to see a clear connection to the achievement of the Millennium Development Goals in future reports on science and technology, as well as on corruption.
19. Mr. Oemar (Indonesia), speaking on behalf of the Association of Southeast Asian Nations (ASEAN), said that the United Nations had an essential part to play in extending multilateralism and shaping comprehensive measures to address the multiple crises in a globalized world.
20. In its deliberations on globalization and interdependence, the Committee should not ignore the contribution of middle-income countries to global and regional development and economic stability.
The Association had included combating corruption in its Community Blueprint and would continue to resolutely pursue it.
Yet they were models of good governance, open borders and economic liberalization.
Although globalization took no account of the needs of their small populations, it played as critical a role in their development as the decisions and policies of their own Governments.
If the World Trade Organization and the Organization for Economic Cooperation and Development did not make allowances for banana production and the financial services sector in the CARICOM countries, those countries could cease to derive any benefit from globalization.

25. For globalization to be effective, it must be inclusive.
Responding to the global economic and financial crisis was not the exclusive preserve of the G-20 countries, no matter how well intentioned.
He reiterated the Community's endorsement of the conclusions of the United Nations Conference on the World Economic and Financial Crisis and Its Impact on Development and emphasized the importance of the follow-up process.
CARICOM also echoed the Secretary-General's call to maintain and indeed increase levels of official development assistance (ODA) in order to cushion the impact of the crisis, not only in the financial centres of the world but also throughout the developing countries.
26. The CARICOM States had been prematurely categorized as middle-income countries alongside other countries far more capable of weathering external economic shocks and combating the crisis unaided.
Their graduation had been based purely on economic development without taking into account their degree of integration at the international level.
CARICOM needed the assistance of the United Nations and of other global partners, as well as adequate support mechanisms in order to assume a leading role in the global knowledge-based economy.

27. Ms. Markoff (United States of America) said that in a globally networked world, cybersecurity was becoming an increasingly critical issue.
As threats to network security multiplied, Governments needed to take a leadership role in ensuring the safety and security of cyberspace.
Given the international nature of such threats, international cooperation would be indispensable.
28. In years past, her country had been a leader in drawing the attention of the General Assembly to threats to information technology security.
At the current session it intended, along with co-sponsors Australia, Israel, the Marshall Islands and Japan, to introduce a draft resolution commending successful regional and international cybersecurity efforts and offering a generic self-assessment tool to help States evaluate their national cybersecurity needs and strategies.
Such a tool would help identify the responsibilities of key stakeholders in society, encourage public/private partnerships at the national level, determine the readiness of the authorities to respond to criminal misuse of information technology, and measure the level of public awareness of the cybersecurity issue.
She looked forward to the cooperation of Member States in reaching a consensus on that draft resolution.

29. Mr. Chen Ming (China) said that the increasingly transnational nature of corruption had made confronting it all the more complicated and the need for effective international cooperation all the more crucial.
Domestically, his country had launched a national anti-corruption coordination mechanism, a national anti-corruption website, and several local anticorruption pilot projects.
Internationally, it took active part in the Conference of the State Parties to the United Nations Convention against Corruption and supported all implementation efforts, especially with regard to the recovery of stolen assets and their return to their countries of origin.
China would become even more involved in international cooperation to combat corruption through information sharing, judicial assistance, capacity-building and technical assistance and hoped that substantive progress would be achieved at the Conference's third session, to be held in Doha from 9 to 13 November 2009.
30. He applauded the work of UNCTAD and the Commission on Science and Technology for Development in helping developing countries to integrate science and technology into their development plans.
His country had been an early leader in promoting development through science and technology, and boasted numerous pathbreaking achievements.
Its 15-year plan for scientific and technological development, laid out in 2006, envisioned turning China into an innovation-oriented economy by 2020.

Nevertheless, while the Government's support of science and technology had helped to make his country's economy the third largest in the world, its per capita gross domestic product (GDP) was not even in the top 100.
It would continue to invest in poverty reduction at home while providing development assistance to other countries to the best of its ability.
Greater investment in science and technology, improved strategies for scientific innovation and increased technical assistance to developing countries were all vital to achieving the Millennium Development Goals.
UNCTAD must continue to provide support to that end.
Developing countries should have access to the markets of developed countries and capacity-building support to enable them to become competitive.
32. Mr. Yono (Iraq) said that there was international agreement that corruption was a major obstacle to development.
His country's Constitution had established an independent Commission on Public Integrity to root out corruption, and it had signed the United Nations Convention against Corruption in March 2008.
In September 2008, UNODC and UNDP had launched a five-year programme to fight corruption in Iraq.
His country would continue to promote good governance based on transparency and accountability in fulfilment of its commitments under the International Compact with Iraq.

The Open-ended International Working Group on Review of the Implementation of the Convention had made constructive progress on the terms of reference for a transparent and inclusive review mechanism.
Adoption of such a mechanism at the forthcoming session of the Conference of States Parties would ensure that provisions on asset recovery and international cooperation functioned as intended.
34. Illicit financial flows coming out of developing countries had been estimated at up to 10 times the amount of ODA flowing into them.
The Open-ended Intergovernmental Working Group on Asset Recovery and the Stolen Assets Recovery (StAR) initiative were both crucial to the development of best practices and training tools for asset recovery.
They must be given the broadest possible support.
States also needed to conform to Financial Action Task Force on Money Laundering (FATF) standards for identifying beneficial ownership of domiciled companies and customer due diligence to prevent company domiciliation from being used as a cover for illegal financial flows.

35. Mr. González Segura (Mexico), speaking on behalf of the Rio Group, said that the Rio Group hoped that the third session of the Conference of the State Parties to the United Nations Convention against Corruption would agree on a review mechanism that was acceptable to all States parties.
As the Convention gained strong and sustained political commitment, it was important for the General Assembly to express support for it.
The Rio Group urged those countries which had not already done so to become parties to the Convention.
Anti-corruption strategies should not shy away from targeting the private sector and the issue of bribery.
Asset recovery and technical assistance to developing countries should be priorities.
36. He commended the work of UNCTAD and the Commission on Science and Technology for Development.
Technological innovation in agriculture was essential for reducing poverty in the rural areas where the bulk of poverty in the developing world was found, and could also contribute to global food security.
For that reason, the Rio Group stressed the importance of establishing guidelines for technology transfer to developing countries.

38. Mr. Alahraf (Libyan Arab Jamahiriya) said that while globalization offered genuine opportunities to developing countries to acquire new capacities and technologies, it also threatened them with economic dependency.
Fairness and stability needed to be restored to the international financial system and efforts by developing countries to diversify their economies should be supported.
It was important to recognize that privatization and the free market alone would not produce development, and that conditional assistance made it difficult for developing countries to balance international commitments with national priorities.
39. Corruption, bribery and money-laundering deprived developing countries of resources needed for development.
The international community needed to take action against money-laundering havens that operated outside the reach of the law.
He commended the UNODC initiative to eliminate safe havens for the proceeds of corruption, and called on the forthcoming third session of the Conference of the States Parties to the United Nations Convention against Corruption to explore mechanisms to identify and recover illicit assets.

40. Science and technology had an important role to play in development, poverty reduction, food security, disease prevention, educational development and environmental protection.
Developing countries should have access to the technology and other tools needed to incorporate the benefits of science into their national economic plans, human resources development strategies and services sectors.
Intellectual property rights should not be allowed to stand in the way of closing the technology gap.
He expressed support for proposals calling on the Commission on Science and Technology for Development to assist the Economic and Social Council in following up the outcomes of the World Summit on the Information Society.

Candidate 0:
  Question: In 2009, which asset recovery mechanism under the United Nations Convention against Corruption could further dialogue between requesting and requested States?
  Answer: regional networks of asset recovery focal points

Candidate 1:
  Question: According to UNODC in 2009, what condition was needed to make the United Nations Convention against Corruption fully effective?
  Answer: Member States provided UNODC with strong support so that it would have the resources needed
````

### Output: choice 0

Finish reason: `stop`.

````text
[
  {
    "index": 0,
    "grounding": 4,
    "precision": 4,
    "numerical_fidelity": 5,
    "reason": "The answer is directly stated in the first sentence of the target block, but the question's framing ('mechanism under the Convention', '2009') adds slight inference, and the answer's 'regional networks of asset recovery focal points' omits the creation/strengthening support and leaves out 'UNODC supported'."
  },
  {
    "index": 1,
    "grounding": 4,
    "precision": 3,
    "numerical_fidelity": 5,
    "reason": "The answer is supported by the final sentence, but it is a grammatically fragmentary excerpt and omits the 'feasible only if' framing; it also attributes the statement to UNODC via the speaker context, and its tail 'so that it would have the resources needed' leaves out the purpose (making provisions operational and fully effective)."
  }
]
````

### Recorded usage

````json
{
  "cached_tokens": 0,
  "completion_tokens": 314,
  "prompt_tokens": 8503,
  "provider_cost": 0.020146,
  "reasoning_tokens": 0
}
````

### Input size diagnostics

````json
{
  "input_characters": 27330,
  "context_capacity_exceeded": null
}
````

## Parsed pipeline outputs

### mode/un/1999/a/c_3/54/sr_31#11/lookup: faithfulness — completed

````json
[
  {
    "_response": {
      "grounding": 4,
      "index": 0,
      "numerical_fidelity": 5,
      "precision": 4,
      "reason": "The answer is a near-verbatim span of the final sentence, but the speaker (Tanzania) has to be inferred from the paragraph 18 attribution. The answer is tight, with only a minor trailing phrase that could be cut, and it contains no numbers."
    },
    "grounding": 4,
    "numerical_fidelity": 5,
    "overall": 13,
    "precision": 4,
    "reason": "The answer is a near-verbatim span of the final sentence, but the speaker (Tanzania) has to be inferred from the paragraph 18 attribution. The answer is tight, with only a minor trailing phrase that could be cut, and it contains no numbers."
  },
  {
    "_response": {
      "grounding": 4,
      "index": 1,
      "numerical_fidelity": 5,
      "precision": 4,
      "reason": "The answer is taken directly from the first sentence of the block, which says Tanzania retained the penalty because it served a useful purpose. The clause 'although it was resorted to very sparingly' is extra context, and the answer contains no numbers."
    },
    "grounding": 4,
    "numerical_fidelity": 5,
    "overall": 13,
    "precision": 4,
    "reason": "The answer is taken directly from the first sentence of the block, which says Tanzania retained the penalty because it served a useful purpose. The clause 'although it was resorted to very sparingly' is extra context, and the answer contains no numbers."
  }
]
````

### mode/un/1999/a/c_3/54/sr_31#11/lookup: quality — completed

````json
[
  {
    "_batch_diversity": "pass",
    "_contract": "compact",
    "_keys": [
      "practitioner_realism",
      "anchoring",
      "consequence",
      "informativeness",
      "linguistic_quality"
    ],
    "_response": {
      "candidate_id": "q_1225a5193899ec3634d50d05",
      "checks": {
        "metadata": "pass",
        "mode": "pass",
        "support": "pass"
      },
      "index": 0,
      "problems": [
        "linguistic_quality: the year is repeated and the phrasing is clumsy.",
        "anchoring: the locator is vague, with no session or agenda item, and the attribution is to \"Tanzania\" loosely.",
        "metadata: the cited rendering is \"In 1999, what did Tanzania ask the European Union to do in A/C.3/54/SR.31?\" and works. The anchor \"the death penalty\" is a base substring outside the slot, and the slot is correctly replaced."
      ],
      "score_notes": {
        "anchoring": "\"The death penalty\" anchors the subject, and 1999 gives the time. But the meeting is identified only as a \"1999 Third Committee meeting record\", with no session or agenda item. The draft resolution's proponent is not tied to the Committee.",
        "consequence": "This is a delegation's call for withdrawal of a draft resolution, a political demand rather than a binding measure. It does identify the party (the EU) and a specific draft, so it is thin but not excluded.",
        "informativeness": "The answer \"withdraw the draft resolution on the death penalty\" is the exact span and resolves the ask. The question cues \"death penalty\" and \"European Union\", so the answer is partly predictable.",
        "linguistic_quality": "\"In 1999\" is repeated, and \"in the 1999 Third Committee meeting record on the death penalty\" is clumsy. It says \"Tanzania\" rather than the United Republic of Tanzania, and the question does not say that this was a delegation's statement.",
        "practitioner_realism": "One direct ask about a single requested action, but the base is awkward and the description of the record is redundant."
      },
      "scores": {
        "anchoring": 3,
        "consequence": 2,
        "informativeness": 3,
        "linguistic_quality": 2,
        "practitioner_realism": 3
      }
    },
    "anchoring": 3,
    "consequence": 2,
    "informativeness": 3,
    "linguistic_quality": 2,
    "overall": 13,
    "practitioner_realism": 3,
    "reason": "practitioner_realism: One direct ask about a single requested action, but the base is awkward and the description of the record is redundant.; anchoring: \"The death penalty\" anchors the subject, and 1999 gives the time. But the meeting is identified only as a \"1999 Third Committee meeting record\", with no session or agenda item. The draft resolution's proponent is not tied to the Committee.; consequence: This is a delegation's call for withdrawal of a draft resolution, a political demand rather than a binding measure. It does identify the party (the EU) and a specific draft, so it is thin but not excluded.; informativeness: The answer \"withdraw the draft resolution on the death penalty\" is the exact span and resolves the ask. The question cues \"death penalty\" and \"European Union\", so the answer is partly predictable.; linguistic_quality: \"In 1999\" is repeated, and \"in the 1999 Third Committee meeting record on the death penalty\" is clumsy. It says \"Tanzania\" rather than the United Republic of Tanzania, and the question does not say that this was a delegation's statement."
  },
  {
    "_batch_diversity": "pass",
    "_contract": "compact",
    "_keys": [
      "practitioner_realism",
      "anchoring",
      "consequence",
      "informativeness",
      "linguistic_quality"
    ],
    "_response": {
      "candidate_id": "q_e9e027fd590d9ae5bbe5eab3",
      "checks": {
        "metadata": "pass",
        "mode": "pass",
        "support": "pass"
      },
      "index": 1,
      "problems": [
        "linguistic_quality: the year is repeated and the phrasing is awkward.",
        "anchoring: the locator is vague, with no session or agenda item.",
        "consequence: this is a rationale for a national policy, given as a statement in debate, with little operational consequence.",
        "metadata: the cited rendering is correct. The anchor \"the death penalty\" is a base substring outside the slot."
      ],
      "score_notes": {
        "anchoring": "\"The death penalty\" and 1999 are anchors. The locator is a vague \"1999 Third Committee meeting record\", so the subject is only partly specified.",
        "consequence": "It asks for a delegation's stated rationale for retaining the death penalty. This is an attributed position on a national practice, not an operative or legal measure. It qualifies only thinly.",
        "informativeness": "The answer is the exact span: \"because it served a useful purpose, although it was resorted to very sparingly\". It resolves the ask, but the reason is generic, and \"it\" is unresolved when the answer is read alone.",
        "linguistic_quality": "\"In 1999\" is repeated and the phrasing is clumsy. \"Why did Tanzania retain...in [record]\" is awkward.",
        "practitioner_realism": "One direct ask, about a reason for retention, but the base is awkward."
      },
      "scores": {
        "anchoring": 3,
        "consequence": 2,
        "informativeness": 3,
        "linguistic_quality": 2,
        "practitioner_realism": 3
      }
    },
    "anchoring": 3,
    "consequence": 2,
    "informativeness": 3,
    "linguistic_quality": 2,
    "overall": 13,
    "practitioner_realism": 3,
    "reason": "practitioner_realism: One direct ask, about a reason for retention, but the base is awkward.; anchoring: \"The death penalty\" and 1999 are anchors. The locator is a vague \"1999 Third Committee meeting record\", so the subject is only partly specified.; consequence: It asks for a delegation's stated rationale for retaining the death penalty. This is an attributed position on a national practice, not an operative or legal measure. It qualifies only thinly.; informativeness: The answer is the exact span: \"because it served a useful purpose, although it was resorted to very sparingly\". It resolves the ask, but the reason is generic, and \"it\" is unresolved when the answer is read alone.; linguistic_quality: \"In 1999\" is repeated and the phrasing is clumsy. \"Why did Tanzania retain...in [record]\" is awkward."
  }
]
````

### mode/un/2000/cd/pv_844#0/practitioner: faithfulness — failed

````json
null
````

### mode/un/2000/cd/pv_844#0/practitioner: faithfulness_json_recovery — completed

````json
[
  {
    "_response": {
      "grounding": 5,
      "index": 0,
      "numerical_fidelity": 5,
      "precision": 4,
      "reason": "Answer is a verbatim contiguous span from the President's statement; it keeps the participle 'having been', which could be cut, and the question's March 2000 date comes from outside the block but does not affect the answer."
    },
    "grounding": 5,
    "numerical_fidelity": 5,
    "overall": 14,
    "precision": 4,
    "reason": "Answer is a verbatim contiguous span from the President's statement; it keeps the participle 'having been', which could be cut, and the question's March 2000 date comes from outside the block but does not affect the answer."
  }
]
````

### mode/un/2000/cd/pv_844#0/practitioner: quality — completed

````json
[
  {
    "_batch_diversity": "not_applicable",
    "_contract": "compact",
    "_keys": [
      "practitioner_realism",
      "anchoring_and_time",
      "consequence",
      "informativeness",
      "linguistic_quality"
    ],
    "_response": {
      "candidate_id": "q_72bba2d6554db17f7b4556ca",
      "checks": {
        "metadata": "pass",
        "mode": "fail",
        "support": "pass"
      },
      "index": 0,
      "problems": [
        "mode: Content is a farewell tribute/courtesy, an excluded ceremonial category, not a norm-state fact.",
        "mode: The question asks why a person left (speech-act/reason), not what applied or stood at a time.",
        "anchoring_and_time: 'March 2000' is not stated in the target block; the departure was only 'shortly', so the time pin is inferred from context.",
        "metadata: Anchors are verbatim and in order, but question_type 'finding_event_or_assessment' is a loose fit for a personnel departure reason."
      ],
      "score_notes": {
        "anchoring_and_time": "Names the CD President and Ambassador Hayashi, and 'March 2000' supplies a time pin. However, the departure date is not in the block and is only inferred. The anchors are a role and a person, not regime-specific.",
        "consequence": "The content is a farewell courtesy: a delegate called to other duties. It is ceremonial with no norm, measure or mandate value.",
        "informativeness": "The span does give the stated reason. But the question's 'why' invites a predictable answer (reassignment), and the substance is trivial.",
        "linguistic_quality": "Mostly fluent, but 'why was ... leaving in March 2000' wrongly implies a dated departure, and 'According to' attribution is slightly stiff.",
        "practitioner_realism": "Asks why a delegate was leaving, a biographical and farewell comprehension prompt rather than a norm-state need. It has no bounded specialist use."
      },
      "scores": {
        "anchoring_and_time": 3,
        "consequence": 1,
        "informativeness": 3,
        "linguistic_quality": 3,
        "practitioner_realism": 2
      }
    },
    "anchoring_and_time": 3,
    "consequence": 1,
    "informativeness": 3,
    "linguistic_quality": 3,
    "overall": 12,
    "practitioner_realism": 2,
    "reason": "practitioner_realism: Asks why a delegate was leaving, a biographical and farewell comprehension prompt rather than a norm-state need. It has no bounded specialist use.; anchoring_and_time: Names the CD President and Ambassador Hayashi, and 'March 2000' supplies a time pin. However, the departure date is not in the block and is only inferred. The anchors are a role and a person, not regime-specific.; consequence: The content is a farewell courtesy: a delegate called to other duties. It is ceremonial with no norm, measure or mandate value.; informativeness: The span does give the stated reason. But the question's 'why' invites a predictable answer (reassignment), and the substance is trivial.; linguistic_quality: Mostly fluent, but 'why was ... leaving in March 2000' wrongly implies a dated departure, and 'According to' attribution is slightly stiff."
  }
]
````

### mode/un/2002/cedaw/c/sr_560#20/lookup: faithfulness — completed

````json
[
  {
    "_response": {
      "grounding": 4,
      "index": 0,
      "numerical_fidelity": 5,
      "precision": 5,
      "reason": "The target says the plan aimed at employment for all 'but placed special emphasis on quality jobs'; the answer is directly supported, and the 'besides' framing requires reading across a clause, which is a small issue."
    },
    "grounding": 4,
    "numerical_fidelity": 5,
    "overall": 14,
    "precision": 5,
    "reason": "The target says the plan aimed at employment for all 'but placed special emphasis on quality jobs'; the answer is directly supported, and the 'besides' framing requires reading across a clause, which is a small issue."
  },
  {
    "_response": {
      "grounding": 4,
      "index": 1,
      "numerical_fidelity": 5,
      "precision": 4,
      "reason": "The answer is a verbatim span from the target, but it omits that the Federal Government must also approve, and the pronoun 'they' is left without a subject, so the fragment needs minor context."
    },
    "grounding": 4,
    "numerical_fidelity": 5,
    "overall": 13,
    "precision": 4,
    "reason": "The answer is a verbatim span from the target, but it omits that the Federal Government must also approve, and the pronoun 'they' is left without a subject, so the fragment needs minor context."
  }
]
````

### mode/un/2002/cedaw/c/sr_560#20/lookup: quality — completed

````json
[
  {
    "_batch_diversity": "pass",
    "_contract": "compact",
    "_keys": [
      "practitioner_realism",
      "anchoring",
      "consequence",
      "informativeness",
      "linguistic_quality"
    ],
    "_response": {
      "candidate_id": "q_b484a75c71a3490a44aafb94",
      "checks": {
        "metadata": "uncertain",
        "mode": "uncertain",
        "support": "pass"
      },
      "index": 0,
      "problems": [
        "mode: the content is a descriptive policy emphasis that is borderline generic, and the anchor is weak.",
        "anchoring: the anchor \"employment plan\" is generic and does not distinguish the instance.",
        "metadata: the question_type operative_action is a loose fit, since the span describes a policy emphasis and not an operative measure. The base and cited renderings differ only in the slot, which is fine. The base has a 2002 time pin, but the cited rendering has no year outside the slot; the CEDAW/C/SR.560 identifier does not give an absolute time."
      ],
      "score_notes": {
        "anchoring": "The anchor \"employment plan\" is generic, and the locator (2002 CEDAW summary record on Belgium) is usable but sits in a long, clunky description. Whether it is Belgium's national plan is fixed only by the question wording.",
        "consequence": "The span is a descriptive policy emphasis with no deadline, figure, or obligation. It is thin and close to generic policy language.",
        "informativeness": "\"quality jobs\" answers the question directly, but it is a two-word fragment and the question's phrasing (\"besides employment for all\") strongly cues the completion.",
        "linguistic_quality": "The description \"2002 Committee ... summary record on Belgium\" is long and awkward. The question also reads as a clumsy attribution, as if the record were itself the speaker.",
        "practitioner_realism": "One direct ask, but it is a narrow detail about a plan's emphasis in a summary record, and the question copies the block's wording closely (\"employment for all\")."
      },
      "scores": {
        "anchoring": 3,
        "consequence": 2,
        "informativeness": 3,
        "linguistic_quality": 3,
        "practitioner_realism": 3
      }
    },
    "anchoring": 3,
    "consequence": 2,
    "informativeness": 3,
    "linguistic_quality": 3,
    "overall": 14,
    "practitioner_realism": 3,
    "reason": "practitioner_realism: One direct ask, but it is a narrow detail about a plan's emphasis in a summary record, and the question copies the block's wording closely (\"employment for all\").; anchoring: The anchor \"employment plan\" is generic, and the locator (2002 CEDAW summary record on Belgium) is usable but sits in a long, clunky description. Whether it is Belgium's national plan is fixed only by the question wording.; consequence: The span is a descriptive policy emphasis with no deadline, figure, or obligation. It is thin and close to generic policy language.; informativeness: \"quality jobs\" answers the question directly, but it is a two-word fragment and the question's phrasing (\"besides employment for all\") strongly cues the completion.; linguistic_quality: The description \"2002 Committee ... summary record on Belgium\" is long and awkward. The question also reads as a clumsy attribution, as if the record were itself the speaker."
  },
  {
    "_batch_diversity": "pass",
    "_contract": "compact",
    "_keys": [
      "practitioner_realism",
      "anchoring",
      "consequence",
      "informativeness",
      "linguistic_quality"
    ],
    "_response": {
      "candidate_id": "q_3ad7caec7e882f89956d3ac3",
      "checks": {
        "metadata": "uncertain",
        "mode": "pass",
        "support": "pass"
      },
      "index": 1,
      "problems": [
        "anchoring: the anchor \"treaty-ratification\" is a topical phrase, not a named body or situation.",
        "metadata: the cited rendering has no year outside the slot; the identifier CEDAW/C/SR.560 does not supply absolute time. The anchor is a verbatim substring of the question and survives in the cited rendering."
      ],
      "score_notes": {
        "anchoring": "The anchor \"treaty-ratification\" is a topic word and not a strong independent anchor. Belgium's communities and regions do distinguish the subject, and the 2002 date is included.",
        "consequence": "The span states a concrete ratification procedure, namely that communities and regions must approve treaties before Belgium ratifies them. It is a legal-procedural fact, though it describes a constitutional arrangement and not a new measure.",
        "informativeness": "The answer is a full verbatim clause that resolves the ask, including the approval-before-ratification condition. The question cues are modest, and the answer adds the approval requirement.",
        "linguistic_quality": "The phrasing is clear but the description is wordy and awkward. \"Treaty-ratification role\" is a little vague.",
        "practitioner_realism": "A single direct procedural question about who must approve treaties before Belgium can ratify them. It is realistic for a practitioner and paraphrased reasonably."
      },
      "scores": {
        "anchoring": 3,
        "consequence": 3,
        "informativeness": 4,
        "linguistic_quality": 3,
        "practitioner_realism": 4
      }
    },
    "anchoring": 3,
    "consequence": 3,
    "informativeness": 4,
    "linguistic_quality": 3,
    "overall": 17,
    "practitioner_realism": 4,
    "reason": "practitioner_realism: A single direct procedural question about who must approve treaties before Belgium can ratify them. It is realistic for a practitioner and paraphrased reasonably.; anchoring: The anchor \"treaty-ratification\" is a topic word and not a strong independent anchor. Belgium's communities and regions do distinguish the subject, and the 2002 date is included.; consequence: The span states a concrete ratification procedure, namely that communities and regions must approve treaties before Belgium ratifies them. It is a legal-procedural fact, though it describes a constitutional arrangement and not a new measure.; informativeness: The answer is a full verbatim clause that resolves the ask, including the approval-before-ratification condition. The question cues are modest, and the answer adds the approval requirement.; linguistic_quality: The phrasing is clear but the description is wordy and awkward. \"Treaty-ratification role\" is a little vague."
  }
]
````

### mode/un/2003/a/res/57/97#3/semantic: faithfulness — completed

````json
[
  {
    "_response": {
      "grounding": 4,
      "index": 0,
      "numerical_fidelity": 5,
      "precision": 4,
      "reason": "The answer copies paragraph 3 of the target block almost verbatim. 'That State' is only resolved to Israel through paragraph 2 and the context, which is a minor disambiguation. The trailing purpose clause is slightly extra."
    },
    "grounding": 4,
    "numerical_fidelity": 5,
    "overall": 13,
    "precision": 4,
    "reason": "The answer copies paragraph 3 of the target block almost verbatim. 'That State' is only resolved to Israel through paragraph 2 and the context, which is a minor disambiguation. The trailing purpose clause is slightly extra."
  },
  {
    "_response": {
      "grounding": 4,
      "index": 1,
      "numerical_fidelity": 4,
      "precision": 3,
      "reason": "The answer is taken from paragraph 2 and is supported. It copies the footnote marker '5' attached to the Treaty name, which is stray padding, and it focuses on accession more than safeguards. The '5' is only a trivial formatting artifact."
    },
    "grounding": 4,
    "numerical_fidelity": 4,
    "overall": 11,
    "precision": 3,
    "reason": "The answer is taken from paragraph 2 and is supported. It copies the footnote marker '5' attached to the Treaty name, which is stray padding, and it focuses on accession more than safeguards. The '5' is only a trivial formatting artifact."
  }
]
````

### mode/un/2003/a/res/57/97#3/semantic: quality — completed

````json
[
  {
    "_batch_diversity": "fail",
    "_contract": "compact",
    "_keys": [
      "search_realism",
      "anchoring_and_time",
      "consequence",
      "lexical_distance",
      "linguistic_quality"
    ],
    "_response": {
      "candidate_id": "q_9aa3eb47dddf544f30d67f76",
      "checks": {
        "metadata": "pass",
        "mode": "pass",
        "support": "pass"
      },
      "index": 0,
      "problems": [
        "answer: the span is long, about 70 words. It is still a single contiguous paragraph and is necessary to cover the full request."
      ],
      "score_notes": {
        "anchoring_and_time": "Israel is a concrete anchor and 2002 is an absolute year. It is slightly broad because 2002 has other Assembly actions, but the nuclear non-proliferation scope narrows it. The 2002 date comes from document context, which is acceptable for the question's time pin.",
        "consequence": "The answer states the concrete demands: accede to the NPT, not develop or acquire nuclear weapons, and place facilities under safeguards. That matches the requested relationship. The span is long, but it is one contiguous operative paragraph.",
        "lexical_distance": "The question reuses 'nuclear non-proliferation' and 'General Assembly called'. The answer is a verbatim paragraph, and the question mirrors its predicate to a moderate degree. The terms are largely necessary, but some paraphrase was possible.",
        "linguistic_quality": "Clear, idiomatic and economical, at 14 words. Saying 'steps' is slightly loose for a call to accede and renounce weapons.",
        "search_realism": "Natural question about what the General Assembly asked of Israel, a bounded response need. The several steps form one connected call, so this is not a bundle of independent asks."
      },
      "scores": {
        "anchoring_and_time": 4,
        "consequence": 4,
        "lexical_distance": 3,
        "linguistic_quality": 4,
        "search_realism": 4
      }
    },
    "anchoring_and_time": 4,
    "consequence": 4,
    "lexical_distance": 3,
    "linguistic_quality": 4,
    "overall": 19,
    "reason": "search_realism: Natural question about what the General Assembly asked of Israel, a bounded response need. The several steps form one connected call, so this is not a bundle of independent asks.; anchoring_and_time: Israel is a concrete anchor and 2002 is an absolute year. It is slightly broad because 2002 has other Assembly actions, but the nuclear non-proliferation scope narrows it. The 2002 date comes from document context, which is acceptable for the question's time pin.; consequence: The answer states the concrete demands: accede to the NPT, not develop or acquire nuclear weapons, and place facilities under safeguards. That matches the requested relationship. The span is long, but it is one contiguous operative paragraph.; lexical_distance: The question reuses 'nuclear non-proliferation' and 'General Assembly called'. The answer is a verbatim paragraph, and the question mirrors its predicate to a moderate degree. The terms are largely necessary, but some paraphrase was possible.; linguistic_quality: Clear, idiomatic and economical, at 14 words. Saying 'steps' is slightly loose for a call to accede and renounce weapons.",
    "search_realism": 4
  },
  {
    "_batch_diversity": "fail",
    "_contract": "compact",
    "_keys": [
      "search_realism",
      "anchoring_and_time",
      "consequence",
      "lexical_distance",
      "linguistic_quality"
    ],
    "_response": {
      "candidate_id": "q_4545691372bb0c5713b84d31",
      "checks": {
        "metadata": "fail",
        "mode": "fail",
        "support": "fail"
      },
      "index": 1,
      "problems": [
        "mode: the answer is a reaffirmation of importance, which is excluded content and not a measure or mechanism.",
        "support: the answer does not show how the Assembly sought to strengthen safeguards. It only states importance and does not supply an action.",
        "metadata: framing 'stakeholder' does not fit, since the need is about an action or approach. The anchor 'the Middle East' is weak and too general."
      ],
      "score_notes": {
        "anchoring_and_time": "The Middle East and 2002 are given, but the anchor is a regional topic. The question does not name Israel or the NPT, so the episode is materially broad.",
        "consequence": "The answer is a reaffirmation of importance, which is a dataset-excluded 'reaffirmed commitment' type of content. It does not describe how the Assembly sought to strengthen safeguards, since it only says accession and safeguards matter for universality. The relationship 'how' is mismatched, and the answer is thin.",
        "lexical_distance": "'Safeguards' and 'Middle East' are carried over, but the wording is otherwise paraphrased. Overlap with the answer is moderate.",
        "linguistic_quality": "Fluent and concise, at 13 words. The 'seek to strengthen' phrasing is slightly loose relative to the answer.",
        "search_realism": "Plausible question, but 'seek to strengthen safeguards' is a vague framing. The actual target is a reaffirmation of the importance of Israel's accession."
      },
      "scores": {
        "anchoring_and_time": 3,
        "consequence": 2,
        "lexical_distance": 3,
        "linguistic_quality": 4,
        "search_realism": 3
      }
    },
    "anchoring_and_time": 3,
    "consequence": 2,
    "lexical_distance": 3,
    "linguistic_quality": 4,
    "overall": 15,
    "reason": "search_realism: Plausible question, but 'seek to strengthen safeguards' is a vague framing. The actual target is a reaffirmation of the importance of Israel's accession.; anchoring_and_time: The Middle East and 2002 are given, but the anchor is a regional topic. The question does not name Israel or the NPT, so the episode is materially broad.; consequence: The answer is a reaffirmation of importance, which is a dataset-excluded 'reaffirmed commitment' type of content. It does not describe how the Assembly sought to strengthen safeguards, since it only says accession and safeguards matter for universality. The relationship 'how' is mismatched, and the answer is thin.; lexical_distance: 'Safeguards' and 'Middle East' are carried over, but the wording is otherwise paraphrased. Overlap with the answer is moderate.; linguistic_quality: Fluent and concise, at 13 words. The 'seek to strengthen' phrasing is slightly loose relative to the answer.",
    "search_realism": 3
  }
]
````

### mode/un/2005/a/59/pv_84#8/lookup: faithfulness — completed

````json
[
  {
    "_response": {
      "grounding": 5,
      "index": 0,
      "numerical_fidelity": 5,
      "precision": 5,
      "reason": "The answer is a verbatim span from the sentence 'curtail the right to self-determination', and the question keeps the attribution to the speaker."
    },
    "grounding": 5,
    "numerical_fidelity": 5,
    "overall": 15,
    "precision": 5,
    "reason": "The answer is a verbatim span from the sentence 'curtail the right to self-determination', and the question keeps the attribution to the speaker."
  },
  {
    "_response": {
      "grounding": 4,
      "index": 1,
      "numerical_fidelity": 5,
      "precision": 5,
      "reason": "The answer is a verbatim phrase, but 'that power' must be linked to determining institutions through the preceding sentence, so two adjacent sentences are needed."
    },
    "grounding": 4,
    "numerical_fidelity": 5,
    "overall": 14,
    "precision": 5,
    "reason": "The answer is a verbatim phrase, but 'that power' must be linked to determining institutions through the preceding sentence, so two adjacent sentences are needed."
  }
]
````

### mode/un/2005/a/59/pv_84#8/lookup: quality — completed

````json
[
  {
    "_batch_diversity": "pass",
    "_contract": "compact",
    "_keys": [
      "practitioner_realism",
      "anchoring",
      "consequence",
      "informativeness",
      "linguistic_quality"
    ],
    "_response": {
      "candidate_id": "q_0bcc9929e6ee61264ebe2bf1",
      "checks": {
        "metadata": "pass",
        "mode": "fail",
        "support": "fail"
      },
      "index": 0,
      "problems": [
        "support: The claim is attributed to Mr. Ping of Gabon, who is the Assembly President. The target block is the Venezuelan delegate's statement, so this is an attribution shift and a false premise.",
        "mode: The locator names the wrong speaker, so it is invalid. The base is 22 words, over the 20-word target but within the 25-word limit."
      ],
      "score_notes": {
        "anchoring": "The block is spoken by the Venezuelan delegate ('we', 'the Bolivarian Republic of Venezuela'). 'Mr. Ping (Gabon)' is the heading for the President, who speaks elsewhere in the document. Attributing the claim to Mr. Ping of Gabon is a wrong locator. The anchor 'state-rebuilding peacekeeping operations' is a general class, not a specific measure.",
        "consequence": "It is an attributed position on the legal effect of peacekeeping operations. It concerns a general class of operations, not an identifiable instrument or measure, so the content is thin.",
        "informativeness": "The answer 'the right to self-determination' is the correct span, but the question's 'curtail' cue makes it fairly easy to guess. It also leaves out the qualifier that this applies to the people who are the object of the operations.",
        "linguistic_quality": "The wording is clear but wordy and repetitive ('peacekeeping operations' appears twice). At 22 words it exceeds the 20-word target.",
        "practitioner_realism": "One direct ask about a single right, but the scaffolding 'meeting record on peacekeeping operations' is bulky, and the attribution to a named person is wrong."
      },
      "scores": {
        "anchoring": 2,
        "consequence": 3,
        "informativeness": 3,
        "linguistic_quality": 3,
        "practitioner_realism": 3
      }
    },
    "anchoring": 2,
    "consequence": 3,
    "informativeness": 3,
    "linguistic_quality": 3,
    "overall": 14,
    "practitioner_realism": 3,
    "reason": "practitioner_realism: One direct ask about a single right, but the scaffolding 'meeting record on peacekeeping operations' is bulky, and the attribution to a named person is wrong.; anchoring: The block is spoken by the Venezuelan delegate ('we', 'the Bolivarian Republic of Venezuela'). 'Mr. Ping (Gabon)' is the heading for the President, who speaks elsewhere in the document. Attributing the claim to Mr. Ping of Gabon is a wrong locator. The anchor 'state-rebuilding peacekeeping operations' is a general class, not a specific measure.; consequence: It is an attributed position on the legal effect of peacekeeping operations. It concerns a general class of operations, not an identifiable instrument or measure, so the content is thin.; informativeness: The answer 'the right to self-determination' is the correct span, but the question's 'curtail' cue makes it fairly easy to guess. It also leaves out the qualifier that this applies to the people who are the object of the operations.; linguistic_quality: The wording is clear but wordy and repetitive ('peacekeeping operations' appears twice). At 22 words it exceeds the 20-word target."
  },
  {
    "_batch_diversity": "pass",
    "_contract": "compact",
    "_keys": [
      "practitioner_realism",
      "anchoring",
      "consequence",
      "informativeness",
      "linguistic_quality"
    ],
    "_response": {
      "candidate_id": "q_8c2f7643cfb84f24bf2f3454",
      "checks": {
        "metadata": "pass",
        "mode": "fail",
        "support": "fail"
      },
      "index": 1,
      "problems": [
        "support: The claim is attributed to Mr. Ping of Gabon, but the block is the Venezuelan delegate's statement; Ping is the heading for the President.",
        "mode: The locator names the wrong speaker, so it is invalid. The base is 24 words, over the 20-word target but within the 25-word limit.",
        "anchoring: The anchor 'replacement institutions' is weak and generic."
      ],
      "score_notes": {
        "anchoring": "The wrong speaker (Mr. Ping of Gabon instead of the Venezuelan delegate) makes the locator inaccurate. The anchor 'replacement institutions' is vague and not tied to a specific measure.",
        "consequence": "It is an attributed position on who holds authority to decide post-failure institutions. The content is general and non-operational, so it is thin but qualifying.",
        "informativeness": "The answer span names the actor completely, including the 'collective and inalienable right to self-determination' qualifier. The question does not expose it.",
        "linguistic_quality": "The phrasing 'solely empowered to determine replacement institutions' is slightly awkward. At 24 words it is long, with heavy locator padding.",
        "practitioner_realism": "One clear 'who' ask, but the scaffolding is lengthy and the speaker is misidentified."
      },
      "scores": {
        "anchoring": 2,
        "consequence": 3,
        "informativeness": 4,
        "linguistic_quality": 3,
        "practitioner_realism": 3
      }
    },
    "anchoring": 2,
    "consequence": 3,
    "informativeness": 4,
    "linguistic_quality": 3,
    "overall": 15,
    "practitioner_realism": 3,
    "reason": "practitioner_realism: One clear 'who' ask, but the scaffolding is lengthy and the speaker is misidentified.; anchoring: The wrong speaker (Mr. Ping of Gabon instead of the Venezuelan delegate) makes the locator inaccurate. The anchor 'replacement institutions' is vague and not tied to a specific measure.; consequence: It is an attributed position on who holds authority to decide post-failure institutions. The content is general and non-operational, so it is thin but qualifying.; informativeness: The answer span names the actor completely, including the 'collective and inalienable right to self-determination' qualifier. The question does not expose it.; linguistic_quality: The phrasing 'solely empowered to determine replacement institutions' is slightly awkward. At 24 words it is long, with heavy locator padding."
  }
]
````

### mode/un/2005/a/59/pv_84#8/semantic: faithfulness — completed

````json
[
  {
    "_response": {
      "grounding": 4,
      "index": 0,
      "numerical_fidelity": 5,
      "precision": 4,
      "reason": "The answer is a verbatim span, but it begins with the fragment 'therefore in fact' and the question attributes the view to Venezuela, which only the document context names. The 'in 2005' framing is also a minor point."
    },
    "grounding": 4,
    "numerical_fidelity": 5,
    "overall": 13,
    "precision": 4,
    "reason": "The answer is a verbatim span, but it begins with the fragment 'therefore in fact' and the question attributes the view to Venezuela, which only the document context names. The 'in 2005' framing is also a minor point."
  },
  {
    "_response": {
      "grounding": 4,
      "index": 1,
      "numerical_fidelity": 5,
      "precision": 4,
      "reason": "The answer is a verbatim sentence that gives the reason directly. It includes the padding 'Moreover,' and the question's attribution to Venezuela relies on context."
    },
    "grounding": 4,
    "numerical_fidelity": 5,
    "overall": 13,
    "precision": 4,
    "reason": "The answer is a verbatim sentence that gives the reason directly. It includes the padding 'Moreover,' and the question's attribution to Venezuela relies on context."
  }
]
````

### mode/un/2005/a/59/pv_84#8/semantic: quality — completed

````json
[
  {
    "_batch_diversity": "pass",
    "_contract": "compact",
    "_keys": [
      "search_realism",
      "anchoring_and_time",
      "consequence",
      "lexical_distance",
      "linguistic_quality"
    ],
    "_response": {
      "candidate_id": "q_1a1290caeef608ed2d46e705",
      "checks": {
        "metadata": "pass",
        "mode": "pass",
        "support": "pass"
      },
      "index": 0,
      "problems": [
        "lexical_distance: the question mirrors the source's 'rebuild a State' and 'self-determination' construction.",
        "linguistic_quality: the phrase 'consequence ... associate with ... for self-determination' is awkward."
      ],
      "score_notes": {
        "anchoring_and_time": "Venezuela, peacekeeping missions rebuilding States and 2005 are concrete. The year comes from context (the 23 March 2005 Committee meeting), and the plenary date is plausible. The anchor is reasonably specific.",
        "consequence": "The answer states the claimed effect on self-determination, which is substantive and attributed to Venezuela by the question. The attribution is about an alleged effect, so it is slightly hedged.",
        "lexical_distance": "'rebuilding States' and 'self-determination' are close to the source, and the predicate 'curtail the right to self-determination' is copied in the answer. The question itself is only moderately paraphrased.",
        "linguistic_quality": "Understandable but clunky: 'associate with ... for self-determination' is awkward, and the noun-stacked phrasing reads stiffly. The word count is fine.",
        "search_realism": "Bounded conceptual need about a State's stated view of an effect. Somewhat slot-like, and the asker would already know the answer is a curtailment of self-determination, so it is not a fully natural outsider query."
      },
      "scores": {
        "anchoring_and_time": 4,
        "consequence": 4,
        "lexical_distance": 3,
        "linguistic_quality": 3,
        "search_realism": 3
      }
    },
    "anchoring_and_time": 4,
    "consequence": 4,
    "lexical_distance": 3,
    "linguistic_quality": 3,
    "overall": 17,
    "reason": "search_realism: Bounded conceptual need about a State's stated view of an effect. Somewhat slot-like, and the asker would already know the answer is a curtailment of self-determination, so it is not a fully natural outsider query.; anchoring_and_time: Venezuela, peacekeeping missions rebuilding States and 2005 are concrete. The year comes from context (the 23 March 2005 Committee meeting), and the plenary date is plausible. The anchor is reasonably specific.; consequence: The answer states the claimed effect on self-determination, which is substantive and attributed to Venezuela by the question. The attribution is about an alleged effect, so it is slightly hedged.; lexical_distance: 'rebuilding States' and 'self-determination' are close to the source, and the predicate 'curtail the right to self-determination' is copied in the answer. The question itself is only moderately paraphrased.; linguistic_quality: Understandable but clunky: 'associate with ... for self-determination' is awkward, and the noun-stacked phrasing reads stiffly. The word count is fine.",
    "search_realism": 3
  },
  {
    "_batch_diversity": "pass",
    "_contract": "compact",
    "_keys": [
      "search_realism",
      "anchoring_and_time",
      "consequence",
      "lexical_distance",
      "linguistic_quality"
    ],
    "_response": {
      "candidate_id": "q_362d2d04670357e3fd282341",
      "checks": {
        "metadata": "pass",
        "mode": "pass",
        "support": "pass"
      },
      "index": 1,
      "problems": [],
      "score_notes": {
        "anchoring_and_time": "Venezuela, state-rebuilding peacekeeping operations and 2005 are concrete. The year comes from context, and the Charter reference is resolvable.",
        "consequence": "The answer gives the stated rationale, that such operations are acts of intervention contravening the Charter. It matches the 'why incompatible' relationship. The answer is partly a restatement of the question's premise, but it does add the intervention reasoning.",
        "lexical_distance": "'Charter' and 'operations' are necessary terms. 'Incompatible with' paraphrases 'contravene', but the question still follows the source's predicate structure.",
        "linguistic_quality": "Clear, idiomatic and economical.",
        "search_realism": "A natural 'why' question about a State's stated rationale for its position on a concrete type of operation. It is bounded and conceptual."
      },
      "scores": {
        "anchoring_and_time": 4,
        "consequence": 4,
        "lexical_distance": 3,
        "linguistic_quality": 4,
        "search_realism": 4
      }
    },
    "anchoring_and_time": 4,
    "consequence": 4,
    "lexical_distance": 3,
    "linguistic_quality": 4,
    "overall": 19,
    "reason": "search_realism: A natural 'why' question about a State's stated rationale for its position on a concrete type of operation. It is bounded and conceptual.; anchoring_and_time: Venezuela, state-rebuilding peacekeeping operations and 2005 are concrete. The year comes from context, and the Charter reference is resolvable.; consequence: The answer gives the stated rationale, that such operations are acts of intervention contravening the Charter. It matches the 'why incompatible' relationship. The answer is partly a restatement of the question's premise, but it does add the intervention reasoning.; lexical_distance: 'Charter' and 'operations' are necessary terms. 'Incompatible with' paraphrases 'contravene', but the question still follows the source's predicate structure.; linguistic_quality: Clear, idiomatic and economical.",
    "search_realism": 4
  }
]
````

### mode/un/2007/a/cn_9/sr_841#21/semantic: faithfulness — completed

````json
[
  {
    "_response": {
      "grounding": 3,
      "index": 0,
      "numerical_fidelity": 5,
      "precision": 4,
      "reason": "The answer is a verbatim span from Ms. McCreath's suggestion, but it is presented as resolving a 'dispute over financial contracts' when it concerns recommendation 204, so the question requires a small inferential step. The '2007' date is not in the target block, and the answer is tight with only a minor mismatch to the question framing."
    },
    "grounding": 3,
    "numerical_fidelity": 5,
    "overall": 12,
    "precision": 4,
    "reason": "The answer is a verbatim span from Ms. McCreath's suggestion, but it is presented as resolving a 'dispute over financial contracts' when it concerns recommendation 204, so the question requires a small inferential step. The '2007' date is not in the target block, and the answer is tight with only a minor mismatch to the question framing."
  },
  {
    "_response": {
      "grounding": 3,
      "index": 1,
      "numerical_fidelity": 5,
      "precision": 4,
      "reason": "The answer is a near-verbatim span of Ms. McCreath's statement that the discussion be deferred. The question's 'remaining concerns' framing loosely blends the Chairperson's remark with McCreath's proposal, and the proposal is not attributed to her, which calls for a small inference. The answer is tight, and the '2007' in the question is unsupported but does not affect the answer."
    },
    "grounding": 3,
    "numerical_fidelity": 5,
    "overall": 12,
    "precision": 4,
    "reason": "The answer is a near-verbatim span of Ms. McCreath's statement that the discussion be deferred. The question's 'remaining concerns' framing loosely blends the Chairperson's remark with McCreath's proposal, and the proposal is not attributed to her, which calls for a small inference. The answer is tight, and the '2007' in the question is unsupported but does not affect the answer."
  }
]
````

### mode/un/2007/a/cn_9/sr_841#21/semantic: quality — completed

````json
[
  {
    "_batch_diversity": "fail",
    "_contract": "compact",
    "_keys": [
      "search_realism",
      "anchoring_and_time",
      "consequence",
      "lexical_distance",
      "linguistic_quality"
    ],
    "_response": {
      "candidate_id": "q_91e7de54b8f3f2c8ad40f18f",
      "checks": {
        "metadata": "pass",
        "mode": "fail",
        "support": "fail"
      },
      "index": 0,
      "problems": [
        "mode: Anchor is too weak, since only the body name and a vague 'dispute' are given, and the subject is mischaracterized.",
        "support: The premise is wrong. The dispute concerned recommendation 204, not financial contracts. 'Delegates' plural overstates what was a single UK delegate's suggestion.",
        "search_realism: The 'dispute' is undefined and the intent is hard to bound.",
        "anchoring_and_time: There is no concrete situation-linked subject, and 2007 is taken only from context.",
        "consequence: The answer names 'recommendation 204', which the question does not identify, and it is a proposal, not a resolution."
      ],
      "score_notes": {
        "anchoring_and_time": "The year 2007 comes only from context. The only anchor is the commission's name, and the real subject (the secured-transactions guide, recommendation 204, priority law for intangibles) is missing. The topic is materially broad.",
        "consequence": "The answer is a single delegate's suggestion, not a resolution or agreement, yet the question says 'delegates proposed'. It also does not fit a dispute 'over financial contracts', and the answer names the recommendation, which the question never identified.",
        "lexical_distance": "'Financial contracts' is copied from the block. The rest is loosely paraphrased, but the paraphrase is vague rather than precise.",
        "linguistic_quality": "The question is grammatical, but 'dispute over financial contracts' is imprecise and the name of the commission is heavy in a short question.",
        "search_realism": "'A 2007 dispute over financial contracts' is vague and mislabels the issue, so an outsider could not tell which concrete problem is meant. The dispute was about recommendation 204 and intangibles."
      },
      "scores": {
        "anchoring_and_time": 2,
        "consequence": 2,
        "lexical_distance": 3,
        "linguistic_quality": 3,
        "search_realism": 2
      }
    },
    "anchoring_and_time": 2,
    "consequence": 2,
    "lexical_distance": 3,
    "linguistic_quality": 3,
    "overall": 12,
    "reason": "search_realism: 'A 2007 dispute over financial contracts' is vague and mislabels the issue, so an outsider could not tell which concrete problem is meant. The dispute was about recommendation 204 and intangibles.; anchoring_and_time: The year 2007 comes only from context. The only anchor is the commission's name, and the real subject (the secured-transactions guide, recommendation 204, priority law for intangibles) is missing. The topic is materially broad.; consequence: The answer is a single delegate's suggestion, not a resolution or agreement, yet the question says 'delegates proposed'. It also does not fit a dispute 'over financial contracts', and the answer names the recommendation, which the question never identified.; lexical_distance: 'Financial contracts' is copied from the block. The rest is loosely paraphrased, but the paraphrase is vague rather than precise.; linguistic_quality: The question is grammatical, but 'dispute over financial contracts' is imprecise and the name of the commission is heavy in a short question.",
    "search_realism": 2
  },
  {
    "_batch_diversity": "fail",
    "_contract": "compact",
    "_keys": [
      "search_realism",
      "anchoring_and_time",
      "consequence",
      "lexical_distance",
      "linguistic_quality"
    ],
    "_response": {
      "candidate_id": "q_afdea353607b1c4cf58ffb54",
      "checks": {
        "metadata": "pass",
        "mode": "fail",
        "support": "fail"
      },
      "index": 1,
      "problems": [
        "mode: 'Remaining concerns about financial contracts' is unresolved and misframed, and the subject of the concerns (recommendation 204) is not identified.",
        "support: The premise is wrong, since the concerns were about recommendation 204, not financial contracts. The deferral is one delegate's suggestion, not how the concerns were actually handled.",
        "anchoring_and_time: The body name and a context-derived year are the only anchor; the actual situation is missing.",
        "consequence: The answer is partly circular on 'financial contracts' and omits what was deferred."
      ],
      "score_notes": {
        "anchoring_and_time": "It has the commission's name and 2007 from context, but no concrete subject such as the secured-transactions guide or the priority-law rule. The 'remaining concerns' have no resolvable referent.",
        "consequence": "Deferral is a stated proposal by the UK delegate, but the question implies a settled handling ('were to be handled'). The Chairperson's actual outcome was to add cross-references. The answer also echoes 'financial contracts' and leaves out what was being deferred.",
        "lexical_distance": "The question and answer both reuse 'financial contracts' and 'discussion', with limited reformulation.",
        "linguistic_quality": "The sentence is understandable but wordy and somewhat awkward ('were to be handled during ... discussions').",
        "search_realism": "The question is vague and its premise is misleading. The concerns were about recommendation 204, not about 'financial contracts'. A searcher would not plausibly frame the need this way."
      },
      "scores": {
        "anchoring_and_time": 2,
        "consequence": 2,
        "lexical_distance": 3,
        "linguistic_quality": 3,
        "search_realism": 2
      }
    },
    "anchoring_and_time": 2,
    "consequence": 2,
    "lexical_distance": 3,
    "linguistic_quality": 3,
    "overall": 12,
    "reason": "search_realism: The question is vague and its premise is misleading. The concerns were about recommendation 204, not about 'financial contracts'. A searcher would not plausibly frame the need this way.; anchoring_and_time: It has the commission's name and 2007 from context, but no concrete subject such as the secured-transactions guide or the priority-law rule. The 'remaining concerns' have no resolvable referent.; consequence: Deferral is a stated proposal by the UK delegate, but the question implies a settled handling ('were to be handled'). The Chairperson's actual outcome was to add cross-references. The answer also echoes 'financial contracts' and leaves out what was being deferred.; lexical_distance: The question and answer both reuse 'financial contracts' and 'discussion', with limited reformulation.; linguistic_quality: The sentence is understandable but wordy and somewhat awkward ('were to be handled during ... discussions').",
    "search_realism": 2
  }
]
````

### mode/un/2007/cd/pv_1063#7/semantic: faithfulness — completed

````json
[
  {
    "_response": {
      "grounding": 4,
      "index": 0,
      "numerical_fidelity": 5,
      "precision": 3,
      "reason": "The answer is taken from the target block's sentence about D'Alema's appeal. The question's 2007 date is not in the block, only in the document context, which is a minor resolution. The answer also includes his full title and name beyond what the question asked for."
    },
    "grounding": 4,
    "numerical_fidelity": 5,
    "overall": 12,
    "precision": 3,
    "reason": "The answer is taken from the target block's sentence about D'Alema's appeal. The question's 2007 date is not in the block, only in the document context, which is a minor resolution. The answer also includes his full title and name beyond what the question asked for."
  },
  {
    "_response": {
      "grounding": 4,
      "index": 1,
      "numerical_fidelity": 5,
      "precision": 3,
      "reason": "The answer is directly supported by the final sentence of the block. It has a small mismatch: the question asks for an 'institutional response' whereas the answer reports an Under-Secretary's plea. It also includes the person's name and title, which adds padding."
    },
    "grounding": 4,
    "numerical_fidelity": 5,
    "overall": 12,
    "precision": 3,
    "reason": "The answer is directly supported by the final sentence of the block. It has a small mismatch: the question asks for an 'institutional response' whereas the answer reports an Under-Secretary's plea. It also includes the person's name and title, which adds padding."
  }
]
````

### mode/un/2007/cd/pv_1063#7/semantic: quality — completed

````json
[
  {
    "_batch_diversity": "fail",
    "_contract": "compact",
    "_keys": [
      "search_realism",
      "anchoring_and_time",
      "consequence",
      "lexical_distance",
      "linguistic_quality"
    ],
    "_response": {
      "candidate_id": "q_99c0bd64f033d8a0a7747ef3",
      "checks": {
        "metadata": "pass",
        "mode": "fail",
        "support": "pass"
      },
      "index": 0,
      "problems": [
        "mode: Framed as a speech report (what the minister advocated), with only a generic appeal as the answer; no qualifying concrete content.",
        "anchoring_and_time: The 2007 date is inferred from the meeting context (\"last month\") rather than stated in the block.",
        "consequence: The answer is an exhortation-type appeal, which falls under the exclusions for generic emphasis.",
        "metadata: The anchor is a verbatim question substring, but the framing \"response\" is questionable for a speech-report question, where stakeholder or situation would fit better."
      ],
      "score_notes": {
        "anchoring_and_time": "The anchor is concrete: Italy, the Deputy Prime Minister and Hiroshima. However, \"2007\" is inferred from the meeting date; the block says only \"last month\", so the event's date rests on context. The episode is also narrow.",
        "consequence": "The answer is a generic appeal for nuclear disarmament and non-proliferation, which is close to an exhortation with little concrete substance. It also repeats the question's terms and restates \"nuclear policy\".",
        "lexical_distance": "\"Nuclear policy\" and \"advocate\" paraphrase the appeal. The Hiroshima visit, Deputy Prime Minister and Italy are copied from the source, but they are needed for identification.",
        "linguistic_quality": "The question is clear, idiomatic and 16 words long. \"Nuclear policy\" is slightly vague.",
        "search_realism": "This is effectively a speech-report question: it asks what position an official advocated during a visit. The need is thin, and the answer is a generic appeal rather than a conceptual problem or mechanism."
      },
      "scores": {
        "anchoring_and_time": 3,
        "consequence": 2,
        "lexical_distance": 3,
        "linguistic_quality": 4,
        "search_realism": 2
      }
    },
    "anchoring_and_time": 3,
    "consequence": 2,
    "lexical_distance": 3,
    "linguistic_quality": 4,
    "overall": 14,
    "reason": "search_realism: This is effectively a speech-report question: it asks what position an official advocated during a visit. The need is thin, and the answer is a generic appeal rather than a conceptual problem or mechanism.; anchoring_and_time: The anchor is concrete: Italy, the Deputy Prime Minister and Hiroshima. However, \"2007\" is inferred from the meeting date; the block says only \"last month\", so the event's date rests on context. The episode is also narrow.; consequence: The answer is a generic appeal for nuclear disarmament and non-proliferation, which is close to an exhortation with little concrete substance. It also repeats the question's terms and restates \"nuclear policy\".; lexical_distance: \"Nuclear policy\" and \"advocate\" paraphrase the appeal. The Hiroshima visit, Deputy Prime Minister and Italy are copied from the source, but they are needed for identification.; linguistic_quality: The question is clear, idiomatic and 16 words long. \"Nuclear policy\" is slightly vague.",
    "search_realism": 2
  },
  {
    "_batch_diversity": "fail",
    "_contract": "compact",
    "_keys": [
      "search_realism",
      "anchoring_and_time",
      "consequence",
      "lexical_distance",
      "linguistic_quality"
    ],
    "_response": {
      "candidate_id": "q_a3dff04d7508f9b1a007bc84",
      "checks": {
        "metadata": "pass",
        "mode": "fail",
        "support": "pass"
      },
      "index": 1,
      "problems": [
        "mode: Speech-report framing of a plea, and the answer is hortatory without concrete content about the initiative.",
        "anchoring_and_time: The year 2007 is supplied from context; the actor (Italy's Under-Secretary) is not named in the question.",
        "consequence: The initiative is not explained in the block, so the answer adds little and the requested \"institutional response\" is not actually described.",
        "support: The answer is a verbatim span from the block. It names Craxi as the actor while the question says \"Italy\", which is acceptable, but the answer does not establish an institutional response."
      ],
      "score_notes": {
        "anchoring_and_time": "The Conference on Disarmament is a concrete anchor, but \"2007\" is not stated in the block. The question also does not identify the six Presidents' initiative or the plenary context, so it is broad.",
        "consequence": "The answer only says Craxi pleaded for resumption and supported the six Presidents' initiative. It gives no mechanism detail, so the \"institutional response\" is unexplained. It is thin, hortatory and partly restates the question.",
        "lexical_distance": "The question reuses \"substantive work\", \"Conference\" and \"restart/resumption\", which mirrors the source predicate. \"Institutional response\" is a paraphrase but not a precise one.",
        "linguistic_quality": "Clear and grammatical at 16 words. \"Institutional response\" is a slightly awkward label for the initiative.",
        "search_realism": "This asks what Italy supported, which is a speech-report or position ask. The answer is a plea for resumed work plus support for an initiative that is not described in the block, so the question is not a real conceptual need."
      },
      "scores": {
        "anchoring_and_time": 3,
        "consequence": 2,
        "lexical_distance": 3,
        "linguistic_quality": 4,
        "search_realism": 2
      }
    },
    "anchoring_and_time": 3,
    "consequence": 2,
    "lexical_distance": 3,
    "linguistic_quality": 4,
    "overall": 14,
    "reason": "search_realism: This asks what Italy supported, which is a speech-report or position ask. The answer is a plea for resumed work plus support for an initiative that is not described in the block, so the question is not a real conceptual need.; anchoring_and_time: The Conference on Disarmament is a concrete anchor, but \"2007\" is not stated in the block. The question also does not identify the six Presidents' initiative or the plenary context, so it is broad.; consequence: The answer only says Craxi pleaded for resumption and supported the six Presidents' initiative. It gives no mechanism detail, so the \"institutional response\" is unexplained. It is thin, hortatory and partly restates the question.; lexical_distance: The question reuses \"substantive work\", \"Conference\" and \"restart/resumption\", which mirrors the source predicate. \"Institutional response\" is a paraphrase but not a precise one.; linguistic_quality: Clear and grammatical at 16 words. \"Institutional response\" is a slightly awkward label for the initiative.",
    "search_realism": 2
  }
]
````

### mode/un/2008/s/res/1826_2008_#5/semantic: faithfulness — completed

````json
[
  {
    "_response": {
      "grounding": 4,
      "index": 0,
      "numerical_fidelity": 5,
      "precision": 4,
      "reason": "The answer is a verbatim span of paragraph 8 and fully supported. It omits the signatories' obligations under the Agreement and international humanitarian law, and the question's framing ('under the Agreement') is slightly loose. It also adds nothing extra, but includes the 'with the support of the UN system' fragment, which is minor."
    },
    "grounding": 4,
    "numerical_fidelity": 5,
    "overall": 13,
    "precision": 4,
    "reason": "The answer is a verbatim span of paragraph 8 and fully supported. It omits the signatories' obligations under the Agreement and international humanitarian law, and the question's framing ('under the Agreement') is slightly loose. It also adds nothing extra, but includes the 'with the support of the UN system' fragment, which is minor."
  },
  {
    "_response": {
      "grounding": 4,
      "index": 1,
      "numerical_fidelity": 5,
      "precision": 4,
      "reason": "The answer is a near-verbatim span of paragraph 9 with the dates and durations exact. It is long and includes the review of mandates, which goes slightly beyond the drawdown assessment the question asks about."
    },
    "grounding": 4,
    "numerical_fidelity": 5,
    "overall": 13,
    "precision": 4,
    "reason": "The answer is a near-verbatim span of paragraph 9 with the dates and durations exact. It is long and includes the review of mandates, which goes slightly beyond the drawdown assessment the question asks about."
  }
]
````

### mode/un/2008/s/res/1826_2008_#5/semantic: quality — completed

````json
[
  {
    "_batch_diversity": "pass",
    "_contract": "compact",
    "_keys": [
      "search_realism",
      "anchoring_and_time",
      "consequence",
      "lexical_distance",
      "linguistic_quality"
    ],
    "_response": {
      "candidate_id": "q_89bce6108944ecd692e26b6f",
      "checks": {
        "metadata": "pass",
        "mode": "pass",
        "support": "fail"
      },
      "index": 0,
      "problems": [
        "support: The question says protection was \"under the Ouagadougou political Agreement\", but the block is a Council invitation to signatories, and the Agreement's own provisions are not in the block. This misattributes the source of the measure.",
        "consequence: The answer mostly restates the invitation and does not state the actor (the signatories), so it is only partly responsive.",
        "lexical_distance: The question leans on source wording.",
        "anchoring_and_time: Côte d'Ivoire is not named, and the year 2008 is the resolution's date rather than an event date."
      ],
      "score_notes": {
        "anchoring_and_time": "Has the Ouagadougou Agreement and 2008, but it does not name Côte d'Ivoire and \"vulnerable civilians\" is fairly broad. The year 2008 is only the resolution date.",
        "consequence": "The answer says what steps are to be taken, but it is mostly a restatement of the invitation. It is thin on mechanism and mislabels the source: the protection steps come from the Council's invitation, not from the Agreement.",
        "lexical_distance": "The answer and question copy \"vulnerable civilian populations\", \"displaced persons\" and \"Ouagadougou political Agreement\". The phrasing is only lightly reworded from the source.",
        "linguistic_quality": "Understandable, but \"vulnerable civilians and displaced people to be protected under the Agreement\" is slightly awkward and imprecise.",
        "search_realism": "Stakeholder need about protection of displaced people is natural, but it is framed as a measure under the Agreement, which is slightly off: the Council invites signatories to act."
      },
      "scores": {
        "anchoring_and_time": 3,
        "consequence": 3,
        "lexical_distance": 2,
        "linguistic_quality": 3,
        "search_realism": 3
      }
    },
    "anchoring_and_time": 3,
    "consequence": 3,
    "lexical_distance": 2,
    "linguistic_quality": 3,
    "overall": 14,
    "reason": "search_realism: Stakeholder need about protection of displaced people is natural, but it is framed as a measure under the Agreement, which is slightly off: the Council invites signatories to act.; anchoring_and_time: Has the Ouagadougou Agreement and 2008, but it does not name Côte d'Ivoire and \"vulnerable civilians\" is fairly broad. The year 2008 is only the resolution date.; consequence: The answer says what steps are to be taken, but it is mostly a restatement of the invitation. It is thin on mechanism and mislabels the source: the protection steps come from the Council's invitation, not from the Agreement.; lexical_distance: The answer and question copy \"vulnerable civilian populations\", \"displaced persons\" and \"Ouagadougou political Agreement\". The phrasing is only lightly reworded from the source.; linguistic_quality: Understandable, but \"vulnerable civilians and displaced people to be protected under the Agreement\" is slightly awkward and imprecise.",
    "search_realism": 3
  },
  {
    "_batch_diversity": "pass",
    "_contract": "compact",
    "_keys": [
      "search_realism",
      "anchoring_and_time",
      "consequence",
      "lexical_distance",
      "linguistic_quality"
    ],
    "_response": {
      "candidate_id": "q_eebe92182113807eee48e4f7",
      "checks": {
        "metadata": "pass",
        "mode": "fail",
        "support": "pass"
      },
      "index": 1,
      "problems": [
        "mode: The answer span is about 100 words, well beyond a short span, and it bundles the review, the report and the benchmarks.",
        "consequence: The long answer includes timing and report details that the question does not ask for."
      ],
      "score_notes": {
        "anchoring_and_time": "Names UNOCI, Côte d'Ivoire and 2008, so it is concrete and time-pinned. The anchor \"UNOCI\" is short but valid.",
        "consequence": "The answer does supply the review criteria, the report and the benchmarks. It is long, though, and includes the review date and the report timing, which goes beyond the question.",
        "lexical_distance": "The question reuses \"UNOCI\", \"drawdown\", \"peace\" and \"electoral processes\" and \"advanced\" (from \"progress\"), so there is moderate overlap. The names are necessary, but \"drawdown\" and \"progress\" are avoidable.",
        "linguistic_quality": "Fluent and clear. \"was to be assessed as ... advanced\" is slightly stiff.",
        "search_realism": "A natural question about how the UN operation's drawdown would be judged, with one bounded need, the mechanism and criteria."
      },
      "scores": {
        "anchoring_and_time": 4,
        "consequence": 3,
        "lexical_distance": 3,
        "linguistic_quality": 4,
        "search_realism": 4
      }
    },
    "anchoring_and_time": 4,
    "consequence": 3,
    "lexical_distance": 3,
    "linguistic_quality": 4,
    "overall": 18,
    "reason": "search_realism: A natural question about how the UN operation's drawdown would be judged, with one bounded need, the mechanism and criteria.; anchoring_and_time: Names UNOCI, Côte d'Ivoire and 2008, so it is concrete and time-pinned. The anchor \"UNOCI\" is short but valid.; consequence: The answer does supply the review criteria, the report and the benchmarks. It is long, though, and includes the review date and the report timing, which goes beyond the question.; lexical_distance: The question reuses \"UNOCI\", \"drawdown\", \"peace\" and \"electoral processes\" and \"advanced\" (from \"progress\"), so there is moderate overlap. The names are necessary, but \"drawdown\" and \"progress\" are avoidable.; linguistic_quality: Fluent and clear. \"was to be assessed as ... advanced\" is slightly stiff.",
    "search_realism": 4
  }
]
````

### mode/un/2009/a/c_2/64/sr_16#3/practitioner: faithfulness — completed

````json
[
  {
    "_response": {
      "grounding": 4,
      "index": 0,
      "numerical_fidelity": 5,
      "precision": 4,
      "reason": "The answer is directly stated in the first sentence of the target block, but the question's framing ('mechanism under the Convention', '2009') adds slight inference, and the answer's 'regional networks of asset recovery focal points' omits the creation/strengthening support and leaves out 'UNODC supported'."
    },
    "grounding": 4,
    "numerical_fidelity": 5,
    "overall": 13,
    "precision": 4,
    "reason": "The answer is directly stated in the first sentence of the target block, but the question's framing ('mechanism under the Convention', '2009') adds slight inference, and the answer's 'regional networks of asset recovery focal points' omits the creation/strengthening support and leaves out 'UNODC supported'."
  },
  {
    "_response": {
      "grounding": 4,
      "index": 1,
      "numerical_fidelity": 5,
      "precision": 3,
      "reason": "The answer is supported by the final sentence, but it is a grammatically fragmentary excerpt and omits the 'feasible only if' framing; it also attributes the statement to UNODC via the speaker context, and its tail 'so that it would have the resources needed' leaves out the purpose (making provisions operational and fully effective)."
    },
    "grounding": 4,
    "numerical_fidelity": 5,
    "overall": 12,
    "precision": 3,
    "reason": "The answer is supported by the final sentence, but it is a grammatically fragmentary excerpt and omits the 'feasible only if' framing; it also attributes the statement to UNODC via the speaker context, and its tail 'so that it would have the resources needed' leaves out the purpose (making provisions operational and fully effective)."
  }
]
````

### mode/un/2009/a/c_2/64/sr_16#3/practitioner: quality — completed

````json
[
  {
    "_batch_diversity": "pass",
    "_contract": "compact",
    "_keys": [
      "practitioner_realism",
      "anchoring_and_time",
      "consequence",
      "informativeness",
      "linguistic_quality"
    ],
    "_response": {
      "candidate_id": "q_1feaa757514ab1e72b72abf3",
      "checks": {
        "metadata": "pass",
        "mode": "fail",
        "support": "pass"
      },
      "index": 0,
      "problems": [
        "mode: it asks about a descriptive, aspirational statement ('could further the dialogue'), not a norm-state. The content is weak and close to the excluded generic/aspirational category.",
        "mode: the time pin '2009' is tied to no event or act, and the question includes no UNODC attribution.",
        "anchoring_and_time: 'asset recovery mechanism' is partly circular with the answer, so it is a weak anchor.",
        "metadata: the anchors are verbatim and ordered, and the type actor_body_or_procedure is tolerable."
      ],
      "score_notes": {
        "anchoring_and_time": "It names the Convention and 'requesting and requested States' and gives 2009. However, 'In 2009' attaches to no event, and the anchors are thin: 'asset recovery mechanism' mostly restates the answer. UNODC's role is not stated in the question.",
        "consequence": "The content is a UNODC-supported description of networks that 'could' further dialogue. This is a soft, aspirational statement with no concrete norm, task or figure.",
        "informativeness": "The span names the networks, which is the requested item. The question's cue 'could further dialogue' makes the answer largely predictable. 'Mechanism' also overstates the networks' status.",
        "linguistic_quality": "The English is understandable but slightly awkward. 'Mechanism' is imprecise and the modal phrasing is loose.",
        "practitioner_realism": "The need is bounded, but it is a comprehension-style prompt about what 'could further dialogue'. It also does not ask about an applicable norm. The wording 'asset recovery mechanism' is a loose slot."
      },
      "scores": {
        "anchoring_and_time": 3,
        "consequence": 2,
        "informativeness": 3,
        "linguistic_quality": 3,
        "practitioner_realism": 3
      }
    },
    "anchoring_and_time": 3,
    "consequence": 2,
    "informativeness": 3,
    "linguistic_quality": 3,
    "overall": 14,
    "practitioner_realism": 3,
    "reason": "practitioner_realism: The need is bounded, but it is a comprehension-style prompt about what 'could further dialogue'. It also does not ask about an applicable norm. The wording 'asset recovery mechanism' is a loose slot.; anchoring_and_time: It names the Convention and 'requesting and requested States' and gives 2009. However, 'In 2009' attaches to no event, and the anchors are thin: 'asset recovery mechanism' mostly restates the answer. UNODC's role is not stated in the question.; consequence: The content is a UNODC-supported description of networks that 'could' further dialogue. This is a soft, aspirational statement with no concrete norm, task or figure.; informativeness: The span names the networks, which is the requested item. The question's cue 'could further dialogue' makes the answer largely predictable. 'Mechanism' also overstates the networks' status.; linguistic_quality: The English is understandable but slightly awkward. 'Mechanism' is imprecise and the modal phrasing is loose."
  },
  {
    "_batch_diversity": "pass",
    "_contract": "compact",
    "_keys": [
      "practitioner_realism",
      "anchoring_and_time",
      "consequence",
      "informativeness",
      "linguistic_quality"
    ],
    "_response": {
      "candidate_id": "q_0bb843999b921663a07be1d9",
      "checks": {
        "metadata": "pass",
        "mode": "fail",
        "support": "pass"
      },
      "index": 1,
      "problems": [
        "mode: the content is a generic resource appeal, an exhortation rather than a norm-state.",
        "mode: the stance is an 'according to UNODC' assessment, close to a speech act.",
        "support: the answer is supported by the block, and the 'feasible only if' condition is preserved only partially.",
        "metadata: the anchors UNODC and the Convention are verbatim and ordered, and the type finding_event_or_assessment is acceptable."
      ],
      "score_notes": {
        "anchoring_and_time": "UNODC and the Convention are two anchors, and 2009 is given as the time. The time is only the year of the meeting, with no dated act. UNODC's attribution is shaky, since the speaker is a UNODC representative but the statement is in his own words.",
        "consequence": "The content is an appeal for strong Member State support and resources. It is hortatory and has no specific measure, figure or deadline.",
        "informativeness": "The answer supplies the requested condition, but the span is a truncated clause that begins mid-sentence ('provided UNODC with strong support'). The question's cue 'condition... fully effective' makes the answer predictable.",
        "linguistic_quality": "The question is acceptable but vague ('what condition was needed'). The answer is ungrammatical as a stand-alone span.",
        "practitioner_realism": "'According to UNODC... what condition' is a speech-act/assessment framing. The condition is essentially a resource appeal, not a norm-state, and the question is vague."
      },
      "scores": {
        "anchoring_and_time": 3,
        "consequence": 2,
        "informativeness": 3,
        "linguistic_quality": 3,
        "practitioner_realism": 2
      }
    },
    "anchoring_and_time": 3,
    "consequence": 2,
    "informativeness": 3,
    "linguistic_quality": 3,
    "overall": 13,
    "practitioner_realism": 2,
    "reason": "practitioner_realism: 'According to UNODC... what condition' is a speech-act/assessment framing. The condition is essentially a resource appeal, not a norm-state, and the question is vague.; anchoring_and_time: UNODC and the Convention are two anchors, and 2009 is given as the time. The time is only the year of the meeting, with no dated act. UNODC's attribution is shaky, since the speaker is a UNODC representative but the statement is in his own words.; consequence: The content is an appeal for strong Member State support and resources. It is hortatory and has no specific measure, figure or deadline.; informativeness: The answer supplies the requested condition, but the span is a truncated clause that begins mid-sentence ('provided UNODC with strong support'). The question's cue 'condition... fully effective' makes the answer predictable.; linguistic_quality: The question is acceptable but vague ('what condition was needed'). The answer is ungrammatical as a stand-alone span."
  }
]
````

### mode/un/2009/a/c_2/64/sr_16#3/semantic: faithfulness — completed

````json
[
  {
    "_response": {
      "grounding": 5,
      "index": 0,
      "numerical_fidelity": 5,
      "precision": 4,
      "reason": "The answer copies a single sentence from the target block verbatim; it includes the relative clause about dialogue, which is slightly extra, and the question's '2009' comes from the document context rather than the block."
    },
    "grounding": 5,
    "numerical_fidelity": 5,
    "overall": 14,
    "precision": 4,
    "reason": "The answer copies a single sentence from the target block verbatim; it includes the relative clause about dialogue, which is slightly extra, and the question's '2009' comes from the document context rather than the block."
  },
  {
    "_response": {
      "grounding": 4,
      "index": 1,
      "numerical_fidelity": 5,
      "precision": 4,
      "reason": "The answer is a verbatim span, but 'then' and the Global Forum's connection to corruption depend on context not in the block, and 'in 2009' is not in the block. The 'then' is a minor fragment that could be cut."
    },
    "grounding": 4,
    "numerical_fidelity": 5,
    "overall": 13,
    "precision": 4,
    "reason": "The answer is a verbatim span, but 'then' and the Global Forum's connection to corruption depend on context not in the block, and 'in 2009' is not in the block. The 'then' is a minor fragment that could be cut."
  }
]
````

### mode/un/2009/a/c_2/64/sr_16#3/semantic: quality — completed

````json
[
  {
    "_batch_diversity": "pass",
    "_contract": "compact",
    "_keys": [
      "search_realism",
      "anchoring_and_time",
      "consequence",
      "lexical_distance",
      "linguistic_quality"
    ],
    "_response": {
      "candidate_id": "q_c452d1c0af793b841e86e4b5",
      "checks": {
        "metadata": "pass",
        "mode": "pass",
        "support": "pass"
      },
      "index": 0,
      "problems": [
        "anchoring_and_time: The anchor is only the bare organization name 'UNODC' and the question is broad. The year 2009 comes from context, not the target. Acceptable, but thin."
      ],
      "score_notes": {
        "anchoring_and_time": "Names UNODC, asset recovery and 2009, which is supported by context. The need is fairly broad, with no mention of the Convention against Corruption or of regional networks.",
        "consequence": "The answer states a concrete mechanism (regional networks of focal points) and its purpose (dialogue between requesting and requested States), which fits the 'how' relationship. The question's 'cooperate' partly pre-frames the answer.",
        "lexical_distance": "The question reuses 'asset recovery' and 'UNODC', which are necessary terms. The answer is a verbatim sentence, but the question itself paraphrases 'requesting/requested States' as 'cooperate'. Moderate mirroring.",
        "linguistic_quality": "Clear and idiomatic, 12 words.",
        "search_realism": "Natural outsider question about a UN body's mechanism for asset-recovery cooperation; one bounded intent, though a bit broad."
      },
      "scores": {
        "anchoring_and_time": 3,
        "consequence": 4,
        "lexical_distance": 3,
        "linguistic_quality": 4,
        "search_realism": 4
      }
    },
    "anchoring_and_time": 3,
    "consequence": 4,
    "lexical_distance": 3,
    "linguistic_quality": 4,
    "overall": 18,
    "reason": "search_realism: Natural outsider question about a UN body's mechanism for asset-recovery cooperation; one bounded intent, though a bit broad.; anchoring_and_time: Names UNODC, asset recovery and 2009, which is supported by context. The need is fairly broad, with no mention of the Convention against Corruption or of regional networks.; consequence: The answer states a concrete mechanism (regional networks of focal points) and its purpose (dialogue between requesting and requested States), which fits the 'how' relationship. The question's 'cooperate' partly pre-frames the answer.; lexical_distance: The question reuses 'asset recovery' and 'UNODC', which are necessary terms. The answer is a verbatim sentence, but the question itself paraphrases 'requesting/requested States' as 'cooperate'. Moderate mirroring.; linguistic_quality: Clear and idiomatic, 12 words.",
    "search_realism": 4
  },
  {
    "_batch_diversity": "pass",
    "_contract": "compact",
    "_keys": [
      "search_realism",
      "anchoring_and_time",
      "consequence",
      "lexical_distance",
      "linguistic_quality"
    ],
    "_response": {
      "candidate_id": "q_cf32f8000da79bd78afc6970",
      "checks": {
        "metadata": "pass",
        "mode": "fail",
        "support": "uncertain"
      },
      "index": 1,
      "problems": [
        "mode: 'The Global Forum' is an unresolved definite reference, and the 2009 time pin is not established for the forum.",
        "support: The answer depends on an unstated condition ('would then become'), and 'meant to' changes the modality. Whether the forum relates to corruption is not shown in the block.",
        "anchoring_and_time: The essential referent (which Global Forum) is not resolved from the question itself.",
        "lexical_distance: 'political and business leaders' is copied directly from the answer span."
      ],
      "score_notes": {
        "anchoring_and_time": "'The Global Forum' is unresolved: the target block never says which forum, and the block only says it 'would then become' something. The question adds 'on corruption issues' and '2009', which the block does not supply for the forum. The anchor is not concrete.",
        "consequence": "The answer is a speculative future evolution of the forum. It describes a planned format rather than a mechanism, and it restates the question's 'political and business leaders'. The 'then' depends on a missing preceding condition, so the answer is thin and partly unresolved.",
        "lexical_distance": "The question copies 'political and business leaders', which is nearly the whole answer. The 'connect' predicate mirrors 'bringing together'. Heavy overlap.",
        "linguistic_quality": "Understandable but slightly awkward ('was meant to connect ... on corruption issues'). 'Meant' misstates the conditional 'would then become'.",
        "search_realism": "A searcher would not know about a 'Global Forum' without the source text. The question is tied to a document-internal entity and is mostly passage comprehension."
      },
      "scores": {
        "anchoring_and_time": 2,
        "consequence": 2,
        "lexical_distance": 2,
        "linguistic_quality": 3,
        "search_realism": 2
      }
    },
    "anchoring_and_time": 2,
    "consequence": 2,
    "lexical_distance": 2,
    "linguistic_quality": 3,
    "overall": 11,
    "reason": "search_realism: A searcher would not know about a 'Global Forum' without the source text. The question is tied to a document-internal entity and is mostly passage comprehension.; anchoring_and_time: 'The Global Forum' is unresolved: the target block never says which forum, and the block only says it 'would then become' something. The question adds 'on corruption issues' and '2009', which the block does not supply for the forum. The anchor is not concrete.; consequence: The answer is a speculative future evolution of the forum. It describes a planned format rather than a mechanism, and it restates the question's 'political and business leaders'. The 'then' depends on a missing preceding condition, so the answer is thin and partly unresolved.; lexical_distance: The question copies 'political and business leaders', which is nearly the whole answer. The 'connect' predicate mirrors 'bringing together'. Heavy overlap.; linguistic_quality: Understandable but slightly awkward ('was meant to connect ... on corruption issues'). 'Meant' misstates the conditional 'would then become'.",
    "search_realism": 2
  }
]
````

### mode/un/2011/a/res/65/133#13/semantic: faithfulness — completed

````json
[
  {
    "_response": {
      "grounding": 3,
      "index": 0,
      "numerical_fidelity": 5,
      "precision": 3,
      "reason": "The answer is a verbatim span of paragraph 27, but it is a call on States and parties to cooperate and ensure access, which the question frames loosely as how workers 'were to reach civilians'. It also includes the cooperation clause as mild padding."
    },
    "grounding": 3,
    "numerical_fidelity": 5,
    "overall": 11,
    "precision": 3,
    "reason": "The answer is a verbatim span of paragraph 27, but it is a call on States and parties to cooperate and ensure access, which the question frames loosely as how workers 'were to reach civilians'. It also includes the cooperation clause as mild padding."
  },
  {
    "_response": {
      "grounding": 4,
      "index": 1,
      "numerical_fidelity": 5,
      "precision": 4,
      "reason": "The answer is a verbatim span of paragraph 28. The 'to protect humanitarian personnel' framing in the question is a slight reinterpretation, since the text concerns managing risks to enable mandate delivery. The answer also includes the trailing 'including in the provision of humanitarian assistance' clause."
    },
    "grounding": 4,
    "numerical_fidelity": 5,
    "overall": 13,
    "precision": 4,
    "reason": "The answer is a verbatim span of paragraph 28. The 'to protect humanitarian personnel' framing in the question is a slight reinterpretation, since the text concerns managing risks to enable mandate delivery. The answer also includes the trailing 'including in the provision of humanitarian assistance' clause."
  }
]
````

### mode/un/2011/a/res/65/133#13/semantic: quality — completed

````json
[
  {
    "_batch_diversity": "pass",
    "_contract": "compact",
    "_keys": [
      "search_realism",
      "anchoring_and_time",
      "consequence",
      "lexical_distance",
      "linguistic_quality"
    ],
    "_response": {
      "candidate_id": "q_7956709851e4a341325f8534",
      "checks": {
        "metadata": "pass",
        "mode": "fail",
        "support": "pass"
      },
      "index": 0,
      "problems": [
        "mode: The anchor is a bare topic (\"armed conflict\") with no concrete country, situation or actor, so the anchoring requirement is not met.",
        "anchoring_and_time: \"In 2010\" is a resolution year with no specific situation, so the question is too generic.",
        "mode: The question does not name who is called upon (States and parties). The answer is also a fragment that begins with \"to cooperate\"."
      ],
      "score_notes": {
        "anchoring_and_time": "\"Armed conflict\" is a bare topic with no country, situation or named body. The question gives 2010 only as a year and no concrete actor, so the anchor is materially broad.",
        "consequence": "The answer states the duty to cooperate fully and to ensure safe and unhindered access, plus delivery of supplies. That matches the \"how reach safely\" ask. The span is not cut at the stated purpose, but it is adequate.",
        "lexical_distance": "\"Safe\" and \"humanitarian\" are mirrored, and the answer span copies the target closely. Elsewhere the question is paraphrased (\"reach civilians\" for \"access\"), so the overlap is moderate.",
        "linguistic_quality": "The question is clear and idiomatic. The phrase \"were to reach\" is slightly awkward.",
        "search_realism": "There is a real conceptual need (how aid workers get safe access), but it is broad. \"In 2010\" makes it read like a generic topic query rather than a situation-specific one."
      },
      "scores": {
        "anchoring_and_time": 2,
        "consequence": 4,
        "lexical_distance": 3,
        "linguistic_quality": 4,
        "search_realism": 3
      }
    },
    "anchoring_and_time": 2,
    "consequence": 4,
    "lexical_distance": 3,
    "linguistic_quality": 4,
    "overall": 16,
    "reason": "search_realism: There is a real conceptual need (how aid workers get safe access), but it is broad. \"In 2010\" makes it read like a generic topic query rather than a situation-specific one.; anchoring_and_time: \"Armed conflict\" is a bare topic with no country, situation or named body. The question gives 2010 only as a year and no concrete actor, so the anchor is materially broad.; consequence: The answer states the duty to cooperate fully and to ensure safe and unhindered access, plus delivery of supplies. That matches the \"how reach safely\" ask. The span is not cut at the stated purpose, but it is adequate.; lexical_distance: \"Safe\" and \"humanitarian\" are mirrored, and the answer span copies the target closely. Elsewhere the question is paraphrased (\"reach civilians\" for \"access\"), so the overlap is moderate.; linguistic_quality: The question is clear and idiomatic. The phrase \"were to reach\" is slightly awkward.",
    "search_realism": 3
  },
  {
    "_batch_diversity": "pass",
    "_contract": "compact",
    "_keys": [
      "search_realism",
      "anchoring_and_time",
      "consequence",
      "lexical_distance",
      "linguistic_quality"
    ],
    "_response": {
      "candidate_id": "q_5594029f89d12738b1ca74e8",
      "checks": {
        "metadata": "pass",
        "mode": "pass",
        "support": "pass"
      },
      "index": 1,
      "problems": [
        "consequence: The question says \"to protect humanitarian personnel\", but the target says the approach is to enable delivery of mandates by managing risks. This is a slight mismatch in relationship.",
        "anchoring_and_time: The question does not attribute the approach to the Secretary-General, who is the actor in the target."
      ],
      "score_notes": {
        "anchoring_and_time": "The named body (the UN security management system) is a concrete anchor, and 2010 is given. The question does not say whose approach it was, and the year comes only from the resolution date.",
        "consequence": "The answer states the Secretary-General's approach: focus on enabling delivery of mandates by managing risks to personnel. It fits the \"oriented\" ask and adds real content. The question's \"to protect\" framing slightly shifts the stated focus on enabling delivery.",
        "lexical_distance": "The question copies \"United Nations security management system\", which is an official name and not penalized. \"Humanitarian personnel\" and \"oriented\" are lightly paraphrased. The answer repeats the target's wording.",
        "linguistic_quality": "The question is clear and grammatical. \"Oriented to protect\" is a little stiff.",
        "search_realism": "This asks about the orientation of the UN security management system. It is a bounded conceptual question about an approach and rationale, and it is natural."
      },
      "scores": {
        "anchoring_and_time": 3,
        "consequence": 4,
        "lexical_distance": 3,
        "linguistic_quality": 4,
        "search_realism": 4
      }
    },
    "anchoring_and_time": 3,
    "consequence": 4,
    "lexical_distance": 3,
    "linguistic_quality": 4,
    "overall": 18,
    "reason": "search_realism: This asks about the orientation of the UN security management system. It is a bounded conceptual question about an approach and rationale, and it is natural.; anchoring_and_time: The named body (the UN security management system) is a concrete anchor, and 2010 is given. The question does not say whose approach it was, and the year comes only from the resolution date.; consequence: The answer states the Secretary-General's approach: focus on enabling delivery of mandates by managing risks to personnel. It fits the \"oriented\" ask and adds real content. The question's \"to protect\" framing slightly shifts the stated focus on enabling delivery.; lexical_distance: The question copies \"United Nations security management system\", which is an official name and not penalized. \"Humanitarian personnel\" and \"oriented\" are lightly paraphrased. The answer repeats the target's wording.; linguistic_quality: The question is clear and grammatical. \"Oriented to protect\" is a little stiff.",
    "search_realism": 4
  }
]
````

### mode/un/2011/a/res/65/141#10/lookup: faithfulness — completed

````json
[
  {
    "_response": {
      "grounding": 5,
      "index": 0,
      "numerical_fidelity": 5,
      "precision": 5,
      "reason": "The answer is a verbatim span from paragraph 13 ('from 16 to 20 May 2011'), with nothing extra and the dates exact."
    },
    "grounding": 5,
    "numerical_fidelity": 5,
    "overall": 15,
    "precision": 5,
    "reason": "The answer is a verbatim span from paragraph 13 ('from 16 to 20 May 2011'), with nothing extra and the dates exact."
  },
  {
    "_response": {
      "grounding": 5,
      "index": 1,
      "numerical_fidelity": 5,
      "precision": 5,
      "reason": "The answer 'Geneva' is taken directly from paragraph 13 ('to be held in Geneva'), with no extra content; there are no numbers to misstate."
    },
    "grounding": 5,
    "numerical_fidelity": 5,
    "overall": 15,
    "precision": 5,
    "reason": "The answer 'Geneva' is taken directly from paragraph 13 ('to be held in Geneva'), with no extra content; there are no numbers to misstate."
  }
]
````

### mode/un/2011/a/res/65/141#10/lookup: quality — completed

````json
[
  {
    "_batch_diversity": "fail",
    "_contract": "compact",
    "_keys": [
      "practitioner_realism",
      "anchoring",
      "consequence",
      "informativeness",
      "linguistic_quality"
    ],
    "_response": {
      "candidate_id": "q_80512106be20047a831a8e85",
      "checks": {
        "metadata": "pass",
        "mode": "fail",
        "support": "fail"
      },
      "index": 0,
      "problems": [
        "mode: the base question is about 28 words, over the 25-word limit.",
        "support: 'dates were set ... in the resolution' attributes the scheduling to the GA, but the block only mentions the forum is 'to be held' and the GA did not set the dates.",
        "anchoring: the description 'resolution on follow-up to the World Summit' does not distinguish this resolution from others.",
        "consequence: the content is a scheduled event, with minimal legal or operational significance."
      ],
      "score_notes": {
        "anchoring": "The forum name is a substantive anchor and the year 2010 gives time, but the description 'resolution on follow-up to the World Summit' is vague and not distinguishing among several 2010 GA resolutions.",
        "consequence": "A scheduled event date for a forum; it is a reported event fact but has low operational weight. The GA only notes the forum and invites organizers, it did not set the dates.",
        "informativeness": "The span 'from 16 to 20 May 2011' fully answers the date ask, and the question does not give it away. Minor limit: the year is shared with the question's cues.",
        "linguistic_quality": "'What dates were set ... in the resolution' misattributes scheduling to the resolution and is slightly clumsy. The description is wordy, at about 27 words.",
        "practitioner_realism": "One direct date lookup, but the question is about a forum's dates and is mostly a logistics detail; the phrasing 'were set for ... in the resolution' implies the resolution set them."
      },
      "scores": {
        "anchoring": 3,
        "consequence": 2,
        "informativeness": 4,
        "linguistic_quality": 3,
        "practitioner_realism": 3
      }
    },
    "anchoring": 3,
    "consequence": 2,
    "informativeness": 4,
    "linguistic_quality": 3,
    "overall": 15,
    "practitioner_realism": 3,
    "reason": "practitioner_realism: One direct date lookup, but the question is about a forum's dates and is mostly a logistics detail; the phrasing 'were set for ... in the resolution' implies the resolution set them.; anchoring: The forum name is a substantive anchor and the year 2010 gives time, but the description 'resolution on follow-up to the World Summit' is vague and not distinguishing among several 2010 GA resolutions.; consequence: A scheduled event date for a forum; it is a reported event fact but has low operational weight. The GA only notes the forum and invites organizers, it did not set the dates.; informativeness: The span 'from 16 to 20 May 2011' fully answers the date ask, and the question does not give it away. Minor limit: the year is shared with the question's cues.; linguistic_quality: 'What dates were set ... in the resolution' misattributes scheduling to the resolution and is slightly clumsy. The description is wordy, at about 27 words."
  },
  {
    "_batch_diversity": "fail",
    "_contract": "compact",
    "_keys": [
      "practitioner_realism",
      "anchoring",
      "consequence",
      "informativeness",
      "linguistic_quality"
    ],
    "_response": {
      "candidate_id": "q_ab38b56c437dad9f5c68eab1",
      "checks": {
        "metadata": "pass",
        "mode": "fail",
        "support": "fail"
      },
      "index": 1,
      "problems": [
        "mode: the base question is about 29 words, over the 25-word limit.",
        "support: 'to be held under the resolution' implies the GA determined the venue, but the block only reports where the forum will be held.",
        "consequence: the content is a venue detail for an event, with minimal operational weight.",
        "informativeness: the one-word answer 'Geneva' is thin and partly guessable from the Summit's association with Geneva."
      ],
      "score_notes": {
        "anchoring": "The forum name anchors and the year 2010 gives time, but the resolution description is generic and does not identify the target among similar resolutions.",
        "consequence": "A venue for an event; thin operational content and not a decision by the GA.",
        "informativeness": "The answer 'Geneva' is a bare one-word answer; it is correct but very thin, and the question's Summit context makes Geneva guessable.",
        "linguistic_quality": "'to be held under the resolution' is awkward and implies the GA decided the venue; the description is wordy, at about 28 words.",
        "practitioner_realism": "A direct single-fact lookup (venue), but a trivial logistics question with low professional need."
      },
      "scores": {
        "anchoring": 3,
        "consequence": 2,
        "informativeness": 3,
        "linguistic_quality": 3,
        "practitioner_realism": 3
      }
    },
    "anchoring": 3,
    "consequence": 2,
    "informativeness": 3,
    "linguistic_quality": 3,
    "overall": 14,
    "practitioner_realism": 3,
    "reason": "practitioner_realism: A direct single-fact lookup (venue), but a trivial logistics question with low professional need.; anchoring: The forum name anchors and the year 2010 gives time, but the resolution description is generic and does not identify the target among similar resolutions.; consequence: A venue for an event; thin operational content and not a decision by the GA.; informativeness: The answer 'Geneva' is a bare one-word answer; it is correct but very thin, and the question's Summit context makes Geneva guessable.; linguistic_quality: 'to be held under the resolution' is awkward and implies the GA decided the venue; the description is wordy, at about 28 words."
  }
]
````

### mode/un/2011/cd/pv_1222#13/lookup: faithfulness — completed

````json
[
  {
    "_response": {
      "grounding": 3,
      "index": 0,
      "numerical_fidelity": 5,
      "precision": 4,
      "reason": "The target block names Director-General of the UN Office at Geneva among his posts, but also Secretary-General of the CD, so the question's singular 'which post' is ambiguous and the answer is only partial; '2011' comes from outside the block. The answer itself is a tight verbatim span."
    },
    "grounding": 3,
    "numerical_fidelity": 5,
    "overall": 12,
    "precision": 4,
    "reason": "The target block names Director-General of the UN Office at Geneva among his posts, but also Secretary-General of the CD, so the question's singular 'which post' is ambiguous and the answer is only partial; '2011' comes from outside the block. The answer itself is a tight verbatim span."
  },
  {
    "_response": {
      "grounding": 4,
      "index": 1,
      "numerical_fidelity": 5,
      "precision": 4,
      "reason": "The answer reproduces '19 March 2002' exactly as stated in the target block; 'since' is slightly redundant padding, and the question's '2011' is not in the block."
    },
    "grounding": 4,
    "numerical_fidelity": 5,
    "overall": 13,
    "precision": 4,
    "reason": "The answer reproduces '19 March 2002' exactly as stated in the target block; 'since' is slightly redundant padding, and the question's '2011' is not in the block."
  }
]
````

### mode/un/2011/cd/pv_1222#13/lookup: quality — completed

````json
[
  {
    "_batch_diversity": "pass",
    "_contract": "compact",
    "_keys": [
      "practitioner_realism",
      "anchoring",
      "consequence",
      "informativeness",
      "linguistic_quality"
    ],
    "_response": {
      "candidate_id": "q_ba4aa113c3fbb46fb96f16dd",
      "checks": {
        "metadata": "pass",
        "mode": "fail",
        "support": "uncertain"
      },
      "index": 0,
      "problems": [
        "mode: content is a tribute/appreciation statement and speaker biography trivia, which are excluded.",
        "mode: the base question is about 'Ordzhonikidze' only and lacks a distinguishing subject. The base renders a bare title lookup.",
        "anchoring: the year 2011 does not appear in the target block, so the time pin is unverified. The description is generic.",
        "support: the answer gives only one of two posts he is said to hold (Director-General of UNOG and Secretary-General of the CD), so it is incomplete. The block says 'posts' plural.",
        "informativeness: ambiguous question with multiple valid answers.",
        "metadata: the question_type actor_body_or_procedure is acceptable, but the anchor is merely a person's name."
      ],
      "score_notes": {
        "anchoring": "The anchor is only the person's name. The description 'the 2011 Conference on Disarmament meeting record' does not separate this meeting from others, and there is no substantive subject. The year 2011 is not in the block and is inferred. The question is ambiguous about which of two posts is meant.",
        "consequence": "The content is a farewell tribute and a biographical description, not an operational or legal fact. It falls under the excluded praise/appreciation category.",
        "informativeness": "The answer names one of two posts mentioned, so it is incomplete and ambiguous. The Secretary-General of the Conference post is also stated in the block. It is a trivial title lookup, and the question does not say which post.",
        "linguistic_quality": "The phrasing is clunky: 'in the 2011 ... meeting record on his departure'. The referents are understandable.",
        "practitioner_realism": "The ask is biographical trivia about a speaker's title drawn from a farewell tribute. The wording is a bit of an instrument-speaking frame, and the question is ambiguous because he held two posts."
      },
      "scores": {
        "anchoring": 2,
        "consequence": 1,
        "informativeness": 2,
        "linguistic_quality": 3,
        "practitioner_realism": 2
      }
    },
    "anchoring": 2,
    "consequence": 1,
    "informativeness": 2,
    "linguistic_quality": 3,
    "overall": 10,
    "practitioner_realism": 2,
    "reason": "practitioner_realism: The ask is biographical trivia about a speaker's title drawn from a farewell tribute. The wording is a bit of an instrument-speaking frame, and the question is ambiguous because he held two posts.; anchoring: The anchor is only the person's name. The description 'the 2011 Conference on Disarmament meeting record' does not separate this meeting from others, and there is no substantive subject. The year 2011 is not in the block and is inferred. The question is ambiguous about which of two posts is meant.; consequence: The content is a farewell tribute and a biographical description, not an operational or legal fact. It falls under the excluded praise/appreciation category.; informativeness: The answer names one of two posts mentioned, so it is incomplete and ambiguous. The Secretary-General of the Conference post is also stated in the block. It is a trivial title lookup, and the question does not say which post.; linguistic_quality: The phrasing is clunky: 'in the 2011 ... meeting record on his departure'. The referents are understandable."
  },
  {
    "_batch_diversity": "pass",
    "_contract": "compact",
    "_keys": [
      "practitioner_realism",
      "anchoring",
      "consequence",
      "informativeness",
      "linguistic_quality"
    ],
    "_response": {
      "candidate_id": "q_cfa274adfb67804c30c15f48",
      "checks": {
        "metadata": "pass",
        "mode": "fail",
        "support": "pass"
      },
      "index": 1,
      "problems": [
        "mode: content is a tribute/appreciation statement, which is excluded.",
        "mode: the question concerns biographical trivia rather than a measure, deadline or mandate task.",
        "anchoring: the anchor is a name only. The year 2011 is not stated in the block, and the description of the document is generic.",
        "linguistic_quality: awkward, confusing phrasing ('associate ... efforts with taking office').",
        "informativeness: the answer is a stitched partial phrase and echoes the question wording."
      ],
      "score_notes": {
        "anchoring": "The anchor is only a personal name, and the description is a generic 'meeting record' with an unverified year. There is no substantive subject.",
        "consequence": "The content is praise of a departing official, and the date is an appointment date in a tribute. It is excluded appreciation content with no operational consequence.",
        "informativeness": "The date 19 March 2002 is in the block and the answer is specific. However, the answer wording 'since taking office on ...' partly echoes the question, and the question's premise is odd.",
        "linguistic_quality": "The phrasing is convoluted and unnatural, and 'associate ... efforts with taking office' is confusing.",
        "practitioner_realism": "The question is awkwardly phrased ('associate ... efforts with taking office') and asks for a date from a eulogy. It is not a natural information need."
      },
      "scores": {
        "anchoring": 2,
        "consequence": 1,
        "informativeness": 3,
        "linguistic_quality": 2,
        "practitioner_realism": 2
      }
    },
    "anchoring": 2,
    "consequence": 1,
    "informativeness": 3,
    "linguistic_quality": 2,
    "overall": 10,
    "practitioner_realism": 2,
    "reason": "practitioner_realism: The question is awkwardly phrased ('associate ... efforts with taking office') and asks for a date from a eulogy. It is not a natural information need.; anchoring: The anchor is only a personal name, and the description is a generic 'meeting record' with an unverified year. There is no substantive subject.; consequence: The content is praise of a departing official, and the date is an appointment date in a tribute. It is excluded appreciation content with no operational consequence.; informativeness: The date 19 March 2002 is in the block and the answer is specific. However, the answer wording 'since taking office on ...' partly echoes the question, and the question's premise is odd.; linguistic_quality: The phrasing is convoluted and unnatural, and 'associate ... efforts with taking office' is confusing."
  }
]
````
