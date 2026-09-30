# Legal question generation and grading: complete call trace

Run status: **completed**. Recorded calls: **14**.

[Questions and grades](results.csv) · [Full provider responses and run data](llm_calls.json) · Resumable state: `run.sqlite`.

Every recorded call, including retries, appears in chronological order. API status describes transport; stage status describes final parsing and validation. The JSON export retains every recorded provider response field. Any candidates beyond a requested quota remain in the raw outcomes.

## Run configuration and source targets

````json
{
  "eurlex": 50,
  "excluded_documents_sha256": "609cd74c9b991e34b4ff5fbfcc527e28f666112d55585f0ae53d840a92f76a54",
  "generator": "gpt-5.6-luna",
  "jev_model": "~typesafe/jev-latest",
  "keep": 3,
  "language": "en",
  "max_per_document": 1,
  "meeting_modes": "all",
  "prompts_sha256": "2c9325f4dfd320d4e5fdb9efffb94430f98f19474495a07fd3120000cf2f72cb",
  "retries": 3,
  "seed": 20260930,
  "targets_sha256": "4cbc8590864a2234cbb839290bd836d84b57c4bde5b3b87b4764a82437e2c8d0",
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
      "calls": 14,
      "provider_errors": 0,
      "capacity_errors": 0,
      "max_input_characters": 38380,
      "max_reported_prompt_tokens": 12535,
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
| mode/eurlex/http://data.europa.eu/eli/reg/2010/1031/art_48/oj/lookup | faithfulness | 1 | completed |  |
| mode/eurlex/http://data.europa.eu/eli/reg/2010/1031/art_48/oj/lookup | quality | 1 | completed |  |
| mode/un/1999/cedaw/c/sr_434#16/practitioner | faithfulness | 1 | completed |  |
| mode/un/1999/cedaw/c/sr_434#16/practitioner | quality | 1 | completed |  |
| mode/un/2000/cd/pv_841#11/practitioner | faithfulness | 1 | completed |  |
| mode/un/2000/cd/pv_841#11/practitioner | quality | 1 | completed |  |
| mode/un/2001/s/res/1376_2001_#2/semantic | faithfulness | 1 | completed |  |
| mode/un/2001/s/res/1376_2001_#2/semantic | quality | 1 | completed |  |
| mode/un/2003/a/res/57/300#10/lookup | faithfulness | 1 | completed |  |
| mode/un/2003/a/res/57/300#10/lookup | quality | 1 | completed |  |
| mode/un/2004/s/2004/505#15/practitioner | faithfulness | 1 | completed |  |
| mode/un/2004/s/2004/505#15/practitioner | quality | 1 | completed |  |
| mode/un/2004/s/res/1565_2004_#11/semantic | faithfulness | 1 | completed |  |
| mode/un/2004/s/res/1565_2004_#11/semantic | quality | 1 | completed |  |
| mode/un/2007/a/res/62/137#12/lookup | faithfulness | 1 | completed |  |
| mode/un/2007/a/res/62/137#12/lookup | quality | 1 | completed |  |
| mode/un/2007/gc_12/c_1/sr_1#10/practitioner | faithfulness | 1 | completed |  |
| mode/un/2007/gc_12/c_1/sr_1#10/practitioner | quality | 1 | completed |  |
| mode/un/2007/gc_12/c_1/sr_1#10/semantic | faithfulness | 1 | completed |  |
| mode/un/2007/gc_12/c_1/sr_1#10/semantic | quality | 1 | completed |  |
| mode/un/2010/ccpr/c/sr_2695#25/practitioner | faithfulness | 1 | completed |  |
| mode/un/2010/ccpr/c/sr_2695#25/practitioner | quality | 1 | completed |  |
| mode/un/2013/a/res/68/18#1/practitioner | faithfulness | 3 | failed | JSONDecodeError: Expecting value: line 1 column 1 (char 0) |
| mode/un/2013/a/res/68/18#1/practitioner | faithfulness_json_recovery | 1 | completed |  |
| mode/un/2013/a/res/68/18#1/practitioner | quality | 1 | completed |  |

## Call 001: faithfulness

Request: `25a5d70207524ca0b43521fb7502b65a`. Task: `mode/un/2013/a/res/68/18#1/practitioner`.

Model: `anthropic/claude-sonnet-5.5`. UTC: 2026-09-30T18:27:30.099600+00:00.

API status: **response**. Duration: 4.661468 seconds.

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

[EN] Document: A/RES/68/18
  Title: 68/18. Graduation of countries from the least developed country category
1. Reaffirms that graduating from the category of least developed countries should not result in a disruption of development plans, programmes and projects;
2. Takes note of the endorsement by the Economic and Social Council of the recommendation of the Committee for Development Policy that Equatorial Guinea be graduated from the least developed country category, and decides to provide Equatorial Guinea, on an exceptional basis, with an additional preparatory period of six months before the start of the three-year preparatory period leading to graduation;
3. Invites Equatorial Guinea to prepare, during the three and a half year period between the adoption of the present resolution and its graduation from the least developed country category, its national smooth-transition strategy, with the support of the United Nations system and in cooperation with its bilateral and multilateral development and trading partners;
4. Takes note of the endorsement by the Council of the recommendation of the Committee that Vanuatu be graduated from the least developed country category, and decides to provide Vanuatu, on an exceptional basis, with an additional preparatory period of one year before the start of the three-year preparatory period leading to graduation;

### REFERENCED DOCUMENTS — none. The target block cites no other document available in the corpus.

### DOCUMENT CONTEXT — surrounding text of the SAME document, supporting context only. It resolves what the target block leaves implicit; it is never a source of answers.

[EN] Document A/RES/68/18 — surrounding passages
68/18. Graduation of countries from the least developed country category
The General Assembly,
Recalling Economic and Social Council resolution 2012/32 of 27 July 2012 on the report of the Committee for Development Policy on its fourteenth session,
Taking into account its resolutions 59/209 of 20 December 2004, 65/286 of 29 June 2011 and 67/221 of 21 December 2012 on a smooth transition for countries graduating from the list of least developed countries,
Recalling paragraph 10 of its resolution 67/221, in which the General Assembly decided to take note of the decisions of the Economic and Social Council regarding the graduation of countries from the least developed country category, as well as the inclusion of countries in that category, at the first session of the Assembly following the adoption of the decisions,
Emphasizing that graduation from the least developed country category is a major milestone for the country involved as it means that significant progress has been made towards reaching at least some of its development goals,

[... the TARGET BLOCK appears here ...]

Candidate 0:
  Question: In 2013, how long was Equatorial Guinea's exceptional preparation before the three-year preparatory period for graduation?
  Answer: six months

Candidate 1:
  Question: In 2013, how long was Vanuatu's exceptional preparation before the three-year preparatory period for graduation?
  Answer: one year
````

### Output: choice 0

Finish reason: `stop`.

````text
Both answers are short spans taken directly from the target block.

Candidate 0: "six months" appears in paragraph 2 as the additional preparatory period for Equatorial Guinea. The question's "In 2013" is not in the target block, which only mentions "the adoption of the present resolution". The year comes from the resolution number or metadata, so it is a minor disambiguation point that does not affect the answer itself. The answer is an exact span, so grounding is 5 or 4. The question is phrased as "exceptional preparation", which is fine. I give grounding 4 because the answer needs a slight mapping to the question's wording. Precision is 5 because the answer is minimal. Numerical fidelity is 5 because "six months" matches exactly.

Candidate 1: "one year" is taken directly from paragraph 4, with the same considerations as Candidate 0. Grounding is 4, precision is 5, and numerical fidelity is 5.

[
{"index":0,"grounding":4,"precision":5,"numerical_fidelity":5,"reason":"'six months' is stated directly in paragraph 2; the question's '2013' is not in the target block, which is a minor flaw."},
{"index":1,"grounding":4,"precision":5,"numerical_fidelity":5,"reason":"'one year' is stated directly in paragraph 4; the question's '2013' is not in the target block, which is a minor flaw."}
]
````

### Recorded usage

````json
{
  "cached_tokens": 0,
  "completion_tokens": 465,
  "prompt_tokens": 3997,
  "provider_cost": 0.012644,
  "reasoning_tokens": 0
}
````

### Input size diagnostics

````json
{
  "input_characters": 11457,
  "context_capacity_exceeded": null
}
````

## Call 002: faithfulness

Request: `3cbf2853bbd4490d99155b56cc20eca5`. Task: `mode/un/2007/a/res/62/137#12/lookup`.

Model: `anthropic/claude-sonnet-5.5`. UTC: 2026-09-30T18:27:30.100863+00:00.

API status: **response**. Duration: 3.024508 seconds.

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

[EN] Document: A/RES/62/137
  Title: Resolution adopted by the General Assembly on 18 December 2007
12. Urges Governments and all entities of the United Nations system, including United Nations agencies, funds and programmes, and all relevant actors of civil society, to ensure the integration of gender perspectives in the implementation of and follow-up to all United Nations summits, conferences and special sessions and to give attention to gender perspectives in preparation for such events, including the commemorative high-level plenary meeting devoted to the follow-up to the outcome of the special session of the General Assembly on children in 2007, the thirteenth session of the Conference of the Parties to the United Nations Framework Convention on Climate Change, and the third session of the Conference of the Parties serving as the Meeting of the Parties to the Kyoto Protocol, in Bali, Indonesia, in 2007, the Follow-up International Conference on Financing for Development to Review the Implementation of the Monterey Consensus in Doha in 2008, and the Third High-level Forum on Aid Effectiveness in Accra in 2008;

### REFERENCED DOCUMENTS — none. The target block cites no other document available in the corpus.

### DOCUMENT CONTEXT — surrounding text of the SAME document, supporting context only. It resolves what the target block leaves implicit; it is never a source of answers.

[EN] Document A/RES/62/137 — surrounding passages
Resolution adopted by the General Assembly on 18 December 2007
[on the report of the Third Committee (A/62/433 (Part II))]
62/137. Follow-up to the Fourth World Conference on Women and full implementation of the Beijing Declaration and Platform for Action and the outcome of the twenty-third special session of the General Assembly
The General Assembly,
Recalling its previous resolutions on the question, including resolution 61/145 of 19 December 2006,
Reaffirming the commitments to gender equality and the advancement of women made at the Millennium Summit, the 2005 World Summit and other major United Nations summits, conferences and special sessions, and reaffirming also that their full, effective and accelerated implementation are integral to achieving the internationally agreed development goals, including the Millennium Development Goals,
Welcoming progress made towards achieving gender equality, but stressing that challenges and obstacles remain in the implementation of the Beijing Declaration and Platform for Action and the outcome of the twenty-third special session,

Recognizing that the responsibility for the implementation of the Beijing Declaration and Platform for Action and the outcome of the twenty-third special session rests primarily at the national level and that strengthened efforts are necessary in this respect, and reiterating that enhanced international cooperation is essential for full, effective and accelerated implementation,
Reaffirming that gender mainstreaming is a globally accepted strategy for promoting the empowerment of women and achieving gender equality by transforming structures of inequality, and reaffirming also the commitment to actively promote the mainstreaming of a gender perspective in the design, implementation, monitoring and evaluation of policies and programmes in all political, economic and social spheres, as well as the commitment to strengthen the capabilities of the United Nations system in the area of gender equality,
Bearing in mind the challenges and obstacles to changing discriminatory attitudes and gender stereotypes, and stressing that challenges and obstacles remain in the implementation of international standards and norms to address the inequality between men and women,

Reaffirming the important role of women in the prevention and resolution of conflicts and in peacebuilding,
Reaffirming also the Declaration of Commitment on HIV/AIDS and the Political Declaration on HIV/AIDS adopted at the High-level Meeting on HIV/AIDS, held from 31 May to 2 June 2006, which, inter alia, acknowledged the feminization of the pandemic,
Noting with appreciation the report of the Secretary-General on mainstreaming a gender perspective into all policies and programmes of the United Nations system,
1. Takes note with appreciation of the report of the Secretary-General on the measures taken and progress achieved in follow-up to the implementation of the Beijing Declaration and Platform for Action and the outcome of the twenty-third special session of the General Assembly;
2. Reaffirms the Beijing Declaration and Platform for Action adopted at the Fourth World Conference on Women,1 the outcome of the twenty-third special session of the General Assembly,2 and the declaration adopted on the occasion of the ten-year review and appraisal of the Beijing Declaration and Platform for Action at the forty-ninth session of the Commission on the Status of Women, and also reaffirms its commitment to their full, effective and accelerated implementation;

3. Recognizes that the implementation of the Beijing Declaration and Platform for Action and the fulfilment of the obligations of States parties under the Convention on the Elimination of All Forms of Discrimination against Women are mutually reinforcing in achieving gender equality and the empowerment of women, and in this regard welcomes the contributions of the Committee on the Elimination of Discrimination against Women to promoting the implementation of the Platform for Action and the outcome of the twenty-third special session, and invites States parties to the Convention to include information on measures taken to enhance implementation at the national level in their reports to the Committee under article 18 of the Convention;
4. Calls upon Governments, the United Nations system and other international and regional organizations, and all sectors of civil society, including non-governmental organizations, as well as all women and men, to fully commit themselves and to intensify their contributions to the implementation of the Beijing Declaration and Platform for Action and the outcome of the twenty-third special session;

5. Calls upon States parties to comply fully with their obligations under the Convention on the Elimination of All Forms of Discrimination against Women and the Optional Protocol thereto and to take into consideration the concluding comments as well as the general recommendations of the Committee, urges States parties to consider limiting the extent of any reservations that they lodge to the Convention, to formulate any reservations as precisely and narrowly as possible, and to regularly review such reservations with a view to withdrawing them so as to ensure that no reservation is incompatible with the object and purpose of the Convention, also urges all Member States that have not yet ratified or acceded to the Convention to consider doing so, and calls upon those Member States that have not yet done so to consider signing, ratifying or acceding to the Optional Protocol;

6. Encourages all actors, inter alia, Governments, the United Nations system, other international organizations and civil society, to continue to support the work of the Commission on the Status of Women in fulfilling its central role in the follow-up to and review of the implementation of the Beijing Declaration and Platform for Action and the outcome of the twenty-third special session, and, as applicable, to carry out its recommendations, and welcomes in this regard the revised programme and methods of work of the Commission adopted at its fiftieth session, which give particular attention to the sharing of experiences, lessons learned and good practices in overcoming challenges to full implementation at the national and international levels as well as to the evaluation of progress in the implementation of priority themes;
7. Calls upon Governments, and the relevant funds and programmes, organs and specialized agencies of the United Nations system, within their respective mandates, and invites the international financial institutions and all relevant actors of civil society, including non-governmental organizations, to intensify action to achieve the full and effective implementation of the Beijing Declaration and Platform for Action and the outcome of the twenty-third special session, through, inter alia:

(a) Sustained political will and commitment at the national, regional and international levels to take further action, inter alia, through the mainstreaming of gender perspectives, including through the development and use of gender equality indicators, as applicable, in all policies and programmes and the promotion of full and equal participation and empowerment of women, and enhanced international cooperation;
(b) Promotion and protection of, and respect for, the full enjoyment of human rights and fundamental freedoms by women and girls, including through the full implementation by States of their obligations under all human rights instruments, especially the Convention on the Elimination of All Forms of Discrimination against Women;
(c) Ensuring full representation and full and equal participation of women in political, social and economic decision-making as an essential condition for gender equality, and the empowerment of women and girls as a critical factor in the eradication of poverty;
(d) Involving women actively in environmental decision-making at all levels, integrating gender concerns and perspectives in policies and programmes for sustainable development, and strengthening or establishing mechanisms at the national, regional and international levels to assess the impact of development and environmental policies on women;

(e) Providing technical assistance to women, particularly in developing countries, to ensure the continuing promotion of human resources development and the development of environmentally sound technologies and of women's entrepreneurship;
(f) Respect for the rule of law, including legislation, and continued efforts to repeal laws and eradicate policies and practices that discriminate against women and girls, and to adopt laws and promote practices that protect their rights;
(g) Strengthening the role of national institutional mechanisms for gender equality and the advancement of women, including through financial and other appropriate assistance, to increase their direct impact on women;
(h) Undertaking socio-economic policies that promote sustainable development and ensure poverty eradication programmes, especially for women and girls, and strengthening the provision of and ensuring equal access to adequate, affordable and accessible public and social services, including education and training at all levels, as well as to all types of permanent and sustainable social protection/social security systems for women throughout their life cycle, and supporting national efforts in this regard;

(i) Taking further steps to ensure that the education system and the media, to the extent consistent with freedom of expression, support the use of nonstereotypic, balanced and diverse images of women presenting them as key actors of the process of development as well as promoting non-discriminatory roles of women and men in their private and public life;
(j) Incorporating gender perspectives and human rights in health-sector policies, programmes and research activities, paying attention to women's and girls' specific needs and priorities, ensuring women's right to the highest attainable standards of health and their access to affordable and adequate health-care services, including sexual, reproductive and maternal health care and lifesaving obstetric care, in accordance with the Programme of Action of the International Conference on Population and Development, and recognizing that the lack of economic empowerment and independence has increased women's vulnerability to a range of negative consequences, involving the risk of contracting HIV/AIDS, malaria, tuberculosis and other poverty-related diseases;

(k) Eliminating gender inequalities, gender-based abuse and violence; increasing the capacity of women and adolescent girls to protect themselves from the risk of HIV infection, principally through the provision of health care and services, including sexual and reproductive health, and the provision of full access to comprehensive information and education; ensuring that women can exercise their right to have control over, and decide freely and responsibly on, matters related to their sexuality in order to increase their ability to protect themselves from HIV infection, including their sexual and reproductive health, free of coercion, discrimination and violence; and taking all necessary measures to create an enabling environment for the empowerment of women and to strengthen their economic independence, while, in this context, reiterating the importance of the role of men and boys in achieving gender equality;
(l) Strengthening national health and social infrastructures to reinforce measures to promote women's access to public health and taking action at the national level to address shortages of human resources for health, by, inter alia, developing, financing and implementing policies, within national development strategies, to improve training and management and effectively govern the recruitment, retention and deployment of health workers, including through international cooperation in this area;

(m) Adequate mobilization of resources at the national and international levels, as well as new and additional resources for the developing countries, including the least developed countries and countries with economies in transition, from all available funding mechanisms, including multilateral, bilateral and private sources;
(n) Increased partnerships among Governments, civil society and the private sector;
(o) Encouraging joint responsibility of men and boys with women and girls in the promotion of gender equality, based on the conviction that this is essential to the achievement of the goals of gender equality, development and peace;
(p) Removing structural and legal barriers, as well as eliminating stereotypic attitudes, to gender equality at work, promoting equal pay for equal work, and promoting the recognition of the value of women's unremunerated work, as well as developing and promoting policies that facilitate the reconciliation of employment and family responsibilities;
8. Reaffirms that States have an obligation to exercise due diligence to prevent violence against women and girls, provide protection to the victims and investigate, prosecute and punish the perpetrators of violence against women and girls, and that failure to do so violates and impairs or nullifies the enjoyment of their human rights and fundamental freedoms, and calls upon Governments to elaborate and implement laws and strategies to eliminate violence against women and girls;

9. Strongly encourages Governments to continue to support the role and contribution of civil society, in particular non-governmental organizations and women's organizations, in the implementation of the Beijing Declaration and Platform for Action and the outcome of the twenty-third special session;
10. Resolves to intensify the efforts of its Main Committees and subsidiary bodies to fully mainstream a gender perspective in their work, including by paying more attention to issues related to the status of women under their consideration and within their mandates, as well as in all United Nations summits, conferences and special sessions and in their follow-up processes;
11. Requests that reports of the Secretary-General submitted to the General Assembly and its subsidiary bodies systematically address gender perspectives through qualitative gender analysis and, where available, quantitative data, in particular through concrete conclusions and recommendations for further action on gender equality and the advancement of women, in order to facilitate gender-sensitive policy development;

[... the TARGET BLOCK appears here ...]

13. Reaffirms its call to include a gender perspective in the consideration of all issues in the agenda and activities of the Peacebuilding Commission and the Human Rights Council;
14. Encourages the Economic and Social Council to continue its efforts to ensure that gender mainstreaming is an integral part of its work and that of its subsidiary bodies, through, inter alia, implementation of its agreed conclusions 1997/2 of 18 July 1997 and its resolution 2004/4 of 7 July 2004;
15. Welcomes the ministerial declaration of the high-level segment of the substantive session of 2007 of the Economic and Social Council, which, inter alia, reaffirmed that gender equality and the promotion and protection of the full enjoyment of all human rights and fundamental freedoms for all are essential to eradicating poverty and hunger and that all countries should promote gender equality and the empowerment of women and, as called for, inter alia, in the Beijing Declaration and Platform for Action and the outcome of the twenty-third special session, identify and accelerate actions towards that end;

16. Requests all bodies that deal with programme and budgetary matters, including the Committee for Programme and Coordination, to ensure that programmes, plans and budgets visibly mainstream gender perspectives;
17. Reaffirms the primary and essential role of the General Assembly and the Economic and Social Council, as well as the central role of the Commission on the Status of Women, in promoting the advancement of women and gender equality;
18. Requests the Economic and Social Council to continue to encourage its functional commissions to mainstream a gender perspective in their respective follow-up actions to major United Nations conferences and summits and to develop more effective means to ensure the implementation of outcomes on gender equality at the national level;
19. Underlines the catalytic role played by the Commission on the Status of Women, as well as the important role played by the Economic and Social Council and the General Assembly, in promoting and monitoring gender mainstreaming within the United Nations system;

20. Requests that entities of the United Nations system systematically incorporate the outcomes of the Commission on the Status of Women into their work within their mandates;
21. Reaffirms the commitment made at the 2005 World Summit to the full and effective implementation of Security Council resolution 1325 (2000) of 31 October 2000, while noting the seventh anniversary of its adoption and the open debates in the Council on women and peace and security;
22. Urges Governments and the United Nations system to take further steps to ensure the integration of a gender perspective and the full and equal participation of women in all efforts to promote peace and security, including in peace negotiations, peacekeeping, peacebuilding and post-conflict situations, as well as to increase their role in decision-making at all levels, including through the development of national action plans and strategies;

23. Calls upon all parts of the United Nations system to continue to play an active role in ensuring the full, effective and accelerated implementation of the Beijing Platform for Action and the outcome of the twenty-third special session, through, inter alia, the work of the Office of the Special Adviser on Gender Issues and Advancement of Women and the Division for the Advancement of Women and the maintenance of gender specialists in all entities of the United Nations system, as well as by ensuring that all personnel, especially in the field, receive training and appropriate follow-up, including tools, guidance and support, for accelerated gender mainstreaming, and reaffirms the need to strengthen the capabilities of the United Nations system in the area of gender;

24. Requests the Secretary-General to review and redouble his efforts to make progress towards achieving the goal of 50/50 gender balance at all levels in the Secretariat and throughout the United Nations system, with full respect for the principle of equitable geographical distribution, in conformity with Article 101, paragraph 3, of the Charter of the United Nations, considering, in particular, women from developing and least developed countries, from countries with economies in transition and from unrepresented or largely underrepresented Member States, and to ensure managerial and departmental accountability with respect to gender balance targets, and strongly encourages Member States to identify and regularly submit more women candidates for appointment to positions in the United Nations system, especially at more senior and policymaking levels;
25. Encourages the subsidiary bodies of the General Assembly to incorporate gender-equality perspectives systematically in their discussions and outcomes, including through effective use of the analysis, data and recommendations contained in reports of the Secretary-General, and to follow up on the outcomes;

26. Requests that reports of the Secretary-General submitted to the General Assembly facilitate gender-sensitive policy development by more systematically including qualitative gender analysis, data and recommendations for further action;
27. Calls upon the United Nations system to continue its efforts towards achieving the goal of gender balance, including with the active support of gender focal points, and requests the Secretary-General to provide an oral report to the Commission on the Status of Women at its fifty-second session, to report to the General Assembly at its sixty-third session, under the item entitled "Advancement of women", and to include in his report on human resources management information on the status of women in the United Nations system, including on progress made and obstacles encountered in achieving gender balance, recommendations for accelerating progress, and up-to-date statistics, including the number and percentage of women and their functions and nationalities throughout the United Nations system, and information on the responsibility and accountability of the Office of Human Resources Management of the Secretariat and the secretariat of the United Nations System Chief Executives Board for Coordination for promoting gender balance;

28. Requests the Secretary-General to continue to report annually to the General Assembly under the item entitled "Advancement of women", as well as to the Commission on the Status of Women and the Economic and Social Council, on the follow-up to and progress made in the implementation of the Beijing Declaration and Platform for Action and the outcome of the twenty-third special session, with an assessment of progress in gender mainstreaming, including information on key achievements, lessons learned and good practices, and recommendations on further measures to enhance implementation. 76th plenary meeting

Candidate 0:
  Question: Which 2008 development-financing event did the 2007 General Assembly resolution on Beijing follow-up identify for attention to gender perspectives?
  Answer: the Follow-up International Conference on Financing for Development to Review the Implementation of the Monterey Consensus in Doha in 2008
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
    "reason": "The answer is a verbatim span from the target block (the Doha 2008 conference name); the question requires a small inference to identify it as the 'development-financing' event among two 2008 events. It includes the location and year as adjacent context that is fairly necessary but not strictly needed, and all identifiers match exactly."
  }
]
````

### Recorded usage

````json
{
  "cached_tokens": 0,
  "completion_tokens": 157,
  "prompt_tokens": 9819,
  "provider_cost": 0.021208,
  "reasoning_tokens": 0
}
````

### Input size diagnostics

````json
{
  "input_characters": 31665,
  "context_capacity_exceeded": null
}
````

## Call 003: faithfulness

Request: `0cf2f4aada4a4345bb4c0555aabe4f6a`. Task: `mode/un/2013/a/res/68/18#1/practitioner`.

Model: `anthropic/claude-sonnet-5.5`. UTC: 2026-09-30T18:27:35.775727+00:00.

API status: **response**. Duration: 4.28195 seconds.

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

[EN] Document: A/RES/68/18
  Title: 68/18. Graduation of countries from the least developed country category
1. Reaffirms that graduating from the category of least developed countries should not result in a disruption of development plans, programmes and projects;
2. Takes note of the endorsement by the Economic and Social Council of the recommendation of the Committee for Development Policy that Equatorial Guinea be graduated from the least developed country category, and decides to provide Equatorial Guinea, on an exceptional basis, with an additional preparatory period of six months before the start of the three-year preparatory period leading to graduation;
3. Invites Equatorial Guinea to prepare, during the three and a half year period between the adoption of the present resolution and its graduation from the least developed country category, its national smooth-transition strategy, with the support of the United Nations system and in cooperation with its bilateral and multilateral development and trading partners;
4. Takes note of the endorsement by the Council of the recommendation of the Committee that Vanuatu be graduated from the least developed country category, and decides to provide Vanuatu, on an exceptional basis, with an additional preparatory period of one year before the start of the three-year preparatory period leading to graduation;

### REFERENCED DOCUMENTS — none. The target block cites no other document available in the corpus.

### DOCUMENT CONTEXT — surrounding text of the SAME document, supporting context only. It resolves what the target block leaves implicit; it is never a source of answers.

[EN] Document A/RES/68/18 — surrounding passages
68/18. Graduation of countries from the least developed country category
The General Assembly,
Recalling Economic and Social Council resolution 2012/32 of 27 July 2012 on the report of the Committee for Development Policy on its fourteenth session,
Taking into account its resolutions 59/209 of 20 December 2004, 65/286 of 29 June 2011 and 67/221 of 21 December 2012 on a smooth transition for countries graduating from the list of least developed countries,
Recalling paragraph 10 of its resolution 67/221, in which the General Assembly decided to take note of the decisions of the Economic and Social Council regarding the graduation of countries from the least developed country category, as well as the inclusion of countries in that category, at the first session of the Assembly following the adoption of the decisions,
Emphasizing that graduation from the least developed country category is a major milestone for the country involved as it means that significant progress has been made towards reaching at least some of its development goals,

[... the TARGET BLOCK appears here ...]

Candidate 0:
  Question: In 2013, how long was Equatorial Guinea's exceptional preparation before the three-year preparatory period for graduation?
  Answer: six months

Candidate 1:
  Question: In 2013, how long was Vanuatu's exceptional preparation before the three-year preparatory period for graduation?
  Answer: one year
````

### Output: choice 0

Finish reason: `stop`.

````text
Both answers come from a single short span of the target block.

Candidate 0: paragraph 2 gives Equatorial Guinea "an additional preparatory period of six months before the start of the three-year preparatory period." The answer "six months" matches exactly. The question's "In 2013" is not in the target block, but it is the question's framing rather than part of the answer. The resolution number 68/18 would put it in 2013, so it is a minor, defensible inference. Grounding gets 4 because the question's date is not stated in the target and the answer needs only a small inferential step. Precision is 5 because the answer is minimal. Numerical fidelity is 5 because "six months" is exact.

Candidate 1: paragraph 4 gives Vanuatu "an additional preparatory period of one year." The answer "one year" is exact. The grades mirror Candidate 0. Grounding is 4 and precision is 5. Numerical fidelity is 5.

[
{"index":0,"grounding":4,"precision":5,"numerical_fidelity":5,"reason":"Answer 'six months' is directly stated in paragraph 2; only the question's '2013' framing is not in the target block."},
{"index":1,"grounding":4,"precision":5,"numerical_fidelity":5,"reason":"Answer 'one year' is directly stated in paragraph 4; only the question's '2013' framing is not in the target block."}
]
````

### Recorded usage

````json
{
  "cached_tokens": 0,
  "completion_tokens": 461,
  "prompt_tokens": 3997,
  "provider_cost": 0.012604,
  "reasoning_tokens": 0
}
````

### Input size diagnostics

````json
{
  "input_characters": 11457,
  "context_capacity_exceeded": null
}
````

## Call 004: faithfulness

Request: `d4cdc32ef2914c109a4cb9ea482f29f4`. Task: `mode/un/2013/a/res/68/18#1/practitioner`.

Model: `anthropic/claude-sonnet-5.5`. UTC: 2026-09-30T18:27:42.072028+00:00.

API status: **response**. Duration: 3.748498 seconds.

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

[EN] Document: A/RES/68/18
  Title: 68/18. Graduation of countries from the least developed country category
1. Reaffirms that graduating from the category of least developed countries should not result in a disruption of development plans, programmes and projects;
2. Takes note of the endorsement by the Economic and Social Council of the recommendation of the Committee for Development Policy that Equatorial Guinea be graduated from the least developed country category, and decides to provide Equatorial Guinea, on an exceptional basis, with an additional preparatory period of six months before the start of the three-year preparatory period leading to graduation;
3. Invites Equatorial Guinea to prepare, during the three and a half year period between the adoption of the present resolution and its graduation from the least developed country category, its national smooth-transition strategy, with the support of the United Nations system and in cooperation with its bilateral and multilateral development and trading partners;
4. Takes note of the endorsement by the Council of the recommendation of the Committee that Vanuatu be graduated from the least developed country category, and decides to provide Vanuatu, on an exceptional basis, with an additional preparatory period of one year before the start of the three-year preparatory period leading to graduation;

### REFERENCED DOCUMENTS — none. The target block cites no other document available in the corpus.

### DOCUMENT CONTEXT — surrounding text of the SAME document, supporting context only. It resolves what the target block leaves implicit; it is never a source of answers.

[EN] Document A/RES/68/18 — surrounding passages
68/18. Graduation of countries from the least developed country category
The General Assembly,
Recalling Economic and Social Council resolution 2012/32 of 27 July 2012 on the report of the Committee for Development Policy on its fourteenth session,
Taking into account its resolutions 59/209 of 20 December 2004, 65/286 of 29 June 2011 and 67/221 of 21 December 2012 on a smooth transition for countries graduating from the list of least developed countries,
Recalling paragraph 10 of its resolution 67/221, in which the General Assembly decided to take note of the decisions of the Economic and Social Council regarding the graduation of countries from the least developed country category, as well as the inclusion of countries in that category, at the first session of the Assembly following the adoption of the decisions,
Emphasizing that graduation from the least developed country category is a major milestone for the country involved as it means that significant progress has been made towards reaching at least some of its development goals,

[... the TARGET BLOCK appears here ...]

Candidate 0:
  Question: In 2013, how long was Equatorial Guinea's exceptional preparation before the three-year preparatory period for graduation?
  Answer: six months

Candidate 1:
  Question: In 2013, how long was Vanuatu's exceptional preparation before the three-year preparatory period for graduation?
  Answer: one year
````

### Output: choice 0

Finish reason: `stop`.

````text
Both questions add "In 2013," which does not appear in the target block. It is a question detail, not answer content, and the answer itself is unaffected.

Candidate 0: "six months" comes directly from paragraph 2. The answer is minimal. The number is exact.

Candidate 1: "one year" comes directly from paragraph 4. The answer is minimal. The number is exact.

Grounding is a 4 for both, not a 5. The answer words are explicit in the text. But the question's "2013" is not supported by the target block, and the answer must be matched to the right country through the paragraph structure. Precision is 5 for both because each answer is the shortest possible span, and numerical fidelity is 5 for both.

[
{"index":0,"grounding":4,"precision":5,"numerical_fidelity":5,"reason":"'Six months' is taken verbatim from paragraph 2 for Equatorial Guinea; the question's '2013' is not in the target block, so grounding is a 4 rather than a 5."},
{"index":1,"grounding":4,"precision":5,"numerical_fidelity":5,"reason":"'One year' is taken verbatim from paragraph 4 for Vanuatu; the question's '2013' is not in the target block, so grounding is a 4 rather than a 5."}
]
````

### Recorded usage

````json
{
  "cached_tokens": 0,
  "completion_tokens": 426,
  "prompt_tokens": 3997,
  "provider_cost": 0.012254,
  "reasoning_tokens": 0
}
````

### Input size diagnostics

````json
{
  "input_characters": 11457,
  "context_capacity_exceeded": null
}
````

## Call 005: faithfulness

Request: `0c94f77f4e834507a239348633dc8122`. Task: `mode/un/2001/s/res/1376_2001_#2/semantic`.

Model: `anthropic/claude-sonnet-5.5`. UTC: 2026-09-30T18:28:33.355531+00:00.

API status: **response**. Duration: 3.851199 seconds.

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

[EN] Document: S/RES/1376(2001)
  Title: Resolution 1376 (2001)
4. Expresses its support for the inter-Congolese dialogue, one of the key elements of the peace process, and for all efforts to promote this process, calls on the Congolese parties to work together for the success of the dialogue, and expresses its support for the Facilitator and his call on the parties to make the dialogue fully inclusive;
6. Expresses its serious concern with regard to the humanitarian situation in the DRC and calls on the international community to increase, without delay, its support for humanitarian activities;
7. Expresses its serious concern with regard to the economic difficulties facing the Democratic Republic of the Congo, stresses that progress in the peace process and the economic recovery and development of the country are interdependent, and in this regard underlines the urgent need for increased international economic assistance in support of the peace process;
8. Reiterates its condemnation of all illegal exploitation of the natural resources of the Democratic Republic of the Congo, demands that such exploitation cease and stresses that the natural resources of the Democratic Republic of the Congo should not be exploited to finance the conflict in that country;

### REFERENCED DOCUMENTS — none. The target block cites no other document available in the corpus.

### DOCUMENT CONTEXT — surrounding text of the SAME document, supporting context only. It resolves what the target block leaves implicit; it is never a source of answers.

[EN] Document S/RES/1376(2001) — surrounding passages
Resolution 1376 (2001)
Adopted by the Security Council at its 4412th meeting, on 9 November 2001
The Security Council,
Recalling its previous resolutions and statements by its President,
Reaffirming the obligation of all States to refrain from the use of force against the territorial integrity and political independence of any State, or in any other manner inconsistent with the purposes of the United Nations, and reaffirming also the political independence, the territorial integrity and the sovereignty of the Democratic Republic of the Congo, including over its natural resources,
Taking note of the Secretary-General's report of 16 October 2001 (S/2001/970) and its recommendations,
Welcoming the participation of the Political Committee for the implementation of the Lusaka Ceasefire Agreement (S/1999/818) in joint meetings held on 9 November 2001,
Determining that the situation in the Democratic Republic of the Congo continues to pose a threat to international peace and security in the region,

1. Welcomes the general respect for the ceasefire among the parties to the Lusaka Ceasefire Agreement, expresses nonetheless its concern at the hostilities in areas of the eastern Democratic Republic of the Congo and calls on the parties to cease any form of support to the armed groups, particularly in the east of the country;
2. Welcomes the withdrawal of some foreign forces from the Democratic Republic of the Congo, including the full Namibian contingent, as a positive step towards the full withdrawal of all foreign forces, and requests all States that have not yet done so to begin to implement, without delay, their full withdrawal in accordance with resolution 1304 (2000) of 16 June 2000;
3. Demands once again that Kisangani be demilitarized rapidly and unconditionally in accordance with Security Council resolution 1304 (2000), takes note of the pledge by the RCD-Goma during the 4411th meeting of 9 November 2001 fully to demilitarize the city, welcomes the decision of the Secretary-General to further deploy MONUC personnel in this city, notably to contribute to the training of police, stresses that, once demilitarized, no party will be permitted to reoccupy the city militarily and welcomes in this regard the pledge by the Government of the DRC, during the same meeting, to respect this provision;

[... the TARGET BLOCK appears here ...]

9. Emphasizes that there are links between the peace processes in Burundi and in the Democratic Republic of the Congo and, welcoming the recent progress in the Burundi process, invites the parties to the Lusaka Ceasefire Agreement to work with the Burundian authorities to advance these two processes;
10. Supports the launching of phase III of the deployment of the United Nations Organization Mission in the Democratic Republic of the Congo (MONUC) on the basis of the concept of operations detailed in paragraphs 59 to 87 of the Secretary-General's report (S/2001/970) and stresses, in this regard, the importance it attaches to the deployment of MONUC in the east of the Democratic Republic of the Congo, in conformity with the new concept of operation and within the overall ceiling, including in the cities of Kindu and Kisangani;
11. Notes with concern the joint communiqué issued on 4 November 2001 by the Secretaries General of the Mouvement de Libération du Congo and of the Rassemblement Congolais pour la Démocratie concerning the deployment of a joint special force in Kindu, and stresses that appropriate conditions will be necessary to allow MONUC to fulfil its role in Kindu and to ensure that discussions on the voluntary disarmament and demobilization of concerned armed groups take place in a neutral environment;

12. Affirms that the implementation of phase III of the deployment of MONUC requires the following steps from the parties and requests the Secretary-General to report on progress thereon:
(i) The transmission to MONUC, as soon as possible and in accordance with its resolution 1355 (2001) of 15 June 2001, of the necessary operational information for the planning of MONUC support for the process of total withdrawal of foreign troops present in the territory of the Democratic Republic of the Congo, including the number of foreign military personnel in the territory of the DRC, their equipment and armament, their exit routes, and a precise timetable for implementation;
(ii) The transmission to MONUC, as soon as possible and in accordance with its resolution 1355 (2001), of the necessary operational information for the planning of MONUC's mandated role in the process of disarmament, demobilization, repatriation, resettlement and reintegration (DDRRR) programme for the armed groups referred to in annex A, chapter 9.1 of the Lusaka Ceasefire Agreement, including the number of persons concerned, their equipment and armament, their location, their intentions, as well as a precise timetable for implementation;

(iii) The establishment of a direct dialogue between the governments of the Democratic Republic of the Congo and Rwanda leading to confidence building and a joint mechanism for coordination, and exchanges of information regarding the DDRRR process;
(iv) The establishment by the governments of the countries concerned, in particular Rwanda, and noting steps taken so far, of conditions conducive to voluntary DDRRR of the members of the armed groups concerned, in particular, by assuring the protection of the personal safety of the members of these armed groups, their civil rights and their economic reintegration including with the assistance of the donor community;
(v) The demilitarization of Kisangani;
(vi) The full restoration of freedom of movement for persons and goods between Kinshasa and Kisangani and throughout the country;
(vii) The full cooperation by the parties with MONUC military and logistical operations, as well as its humanitarian, human rights, and child protection activities, including by permitting unrestricted access to ports and airports, and by refraining from introducing administrative and other impediments;

13. Expresses its satisfaction at the partnership established with the parties to the Lusaka Ceasefire Agreement, strengthened by regular contacts between the Political Committee for the implementation of that Agreement and the Council, and reiterates its firm determination to continue to provide assistance to the parties in their efforts to achieve peace;
14. Commends the outstanding work of MONUC personnel in challenging conditions, and pays tribute in particular to the efforts of the Special Representative of the Secretary-General;
15. Decides to remain actively seized of the matter.

Candidate 0:
  Question: Why was international economic assistance considered urgent for the Democratic Republic of the Congo peace process in 2001?
  Answer: progress in the peace process and the economic recovery and development of the country are interdependent

Candidate 1:
  Question: How were natural resources in the Democratic Republic of the Congo prevented from fueling conflict in 2001?
  Answer: demands that such exploitation cease and stresses that the natural resources of the Democratic Republic of the Congo should not be exploited to finance the conflict in that country
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
    "reason": "The answer is a verbatim span from paragraph 7, but the reason for urgency is only implied by the 'in this regard' link, and the span is slightly narrower than the full reasoning (it omits economic difficulties and the assistance need)."
  },
  {
    "index": 1,
    "grounding": 3,
    "precision": 4,
    "numerical_fidelity": 5,
    "reason": "The answer is verbatim from paragraph 8, but the question asks how resources were 'prevented' from fueling conflict while the text only demands cessation and states a principle, so the answer presents a demand as if it were an outcome; the span also carries a redundant trailing clause."
  }
]
````

### Recorded usage

````json
{
  "cached_tokens": 0,
  "completion_tokens": 277,
  "prompt_tokens": 5851,
  "provider_cost": 0.014472,
  "reasoning_tokens": 0
}
````

### Input size diagnostics

````json
{
  "input_characters": 17197,
  "context_capacity_exceeded": null
}
````

## Call 006: faithfulness

Request: `3ed05012ceb0438bab28f3661c3423b0`. Task: `mode/un/2004/s/res/1565_2004_#11/semantic`.

Model: `anthropic/claude-sonnet-5.5`. UTC: 2026-09-30T18:28:33.355655+00:00.

API status: **response**. Duration: 3.808261 seconds.

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

[EN] Document: S/RES/1565(2004)
  Title: Resolution 1565 (2004)
19. Strongly condemns violence and other violations of international humanitarian law and human rights, in particular those perpetrated against civilians, in the Democratic Republic of the Congo, and demands that all parties and Governments concerned in the region, including the Government of National Unity and Transition, take without delay all necessary steps to bring to justice those responsible for these violations and to ensure respect for human rights and international humanitarian law, as appropriate with relevant international assistance, as well as to guarantee the security and well-being of the civilian population;
20. Demands that all parties cooperate fully with the operations of MONUC and that they ensure the safety of as well as unhindered and immediate access for United Nations and associated personnel in carrying out their mandate, throughout the territory of the Democratic Republic of the Congo, demands in particular that all parties provide full access to MONUC military observers, including in all ports, airports, airfields, military bases and border crossings, and requests the Secretary-General to report without delay any failure to comply with these demands;

### REFERENCED DOCUMENTS — none. The target block cites no other document available in the corpus.

### DOCUMENT CONTEXT — surrounding text of the SAME document, supporting context only. It resolves what the target block leaves implicit; it is never a source of answers.

[EN] Document S/RES/1565(2004) — surrounding passages
Resolution 1565 (2004)
Adopted by the Security Council at its 5048th meeting, on 1 October 2004
The Security Council,
Recalling its previous resolutions and the statements by its President concerning the Democratic Republic of the Congo,
Reaffirming its commitment to respect the sovereignty, territorial integrity and political independence of the Democratic Republic of the Congo and all the States of the region,
Reaffirming its support for the process of the Global and All Inclusive Agreement on the Transition in the Democratic Republic of the Congo (signed in Pretoria on 17 December 2002), welcoming the efforts made to date for its implementation by the Government of National Unity and Transition, and calling on all the Congolese parties to honour their commitments in this regard, in particular so that free, fair and peaceful elections can take place within the agreed time frame,
Deeply concerned by the continuation of hostilities in the eastern part of the Democratic Republic of the Congo, particularly in the provinces of North and South Kivu and in the Ituri district, and by the grave violations of human rights and of international humanitarian law that accompany them,

Recalling that all the parties bear responsibility for ensuring security with respect to the civilian populations, and recalling in particular in this regard its resolutions 1325 (2000) on women, peace and security, 1379 (2001), 1460 (2003) and 1539 (2004) on children in armed conflict, and 1265 (1999) and 1296 (2000) on the protection of civilians in armed conflict,
Taking note of the third special report of the Secretary-General on the United Nations Organization Mission in the Democratic Republic of the Congo (MONUC), dated 16 August 2004 (S/2004/650), and of its recommendations,
Taking note of the letter of the Secretary-General dated 3 September 2004 (S/2004/715),
Noting that the situation in the Democratic Republic of the Congo continues to constitute a threat to international peace and security in the region,
Acting under Chapter VII of the Charter of the United Nations,
1. Decides to extend the deployment of MONUC until 31 March 2005;

2. Requests the Secretary-General to arrange the rapid deployment of additional military capabilities for MONUC in accordance with the recommendation contained in his letter dated 3 September 2004, and, beyond, to deploy as soon as possible in the provinces of North and South Kivu all the brigades and appropriate force enablers;
3. Authorizes the increase of MONUC's strength by 5,900 personnel, including up to 341 civilian police personnel, as well as the deployment of appropriate civilian personnel, appropriate and proportionate air mobility assets and other force enablers, and expresses its determination to keep MONUC's strength and structure under regular review, taking into account the evolution of the situation on the ground;
4. Decides that MONUC will have the following mandate:
(a) to deploy and maintain a presence in the key areas of potential volatility in order to promote the re-establishment of confidence, to discourage violence, in particular by deterring the use of force to threaten the political process, and to allow United Nations personnel to operate freely, particularly in the Eastern part of the Democratic Republic of the Congo,

(b) to ensure the protection of civilians, including humanitarian personnel, under imminent threat of physical violence,
(c) to ensure the protection of United Nations personnel, facilities, installations and equipment,
(d) to ensure the security and freedom of movement of its personnel,
(e) to establish the necessary operational links with the United Nations Operation in Burundi (ONUB), and with the Governments of the Democratic Republic of the Congo and Burundi, in order to coordinate efforts towards monitoring and discouraging cross-border movements of combatants between the two countries,
(f) to monitor the implementation of the measures imposed by paragraph 20 of resolution 1493 of 28 July 2003, including on the lakes, in cooperation with ONUB and, as appropriate, with the Governments concerned and with the group of experts referred to in paragraph 10 of resolution 1533 of 12 March 2004, including by inspecting, as it deems it necessary and without notice, the cargo of aircraft and of any transport vehicle using the ports, airports, airfields, military bases and border crossings in North and South Kivu and in Ituri,

(g) to seize or collect, as appropriate, arms and any related materiel whose presence in the territory of the Democratic Republic of the Congo violates the measures imposed by paragraph 20 of resolution 1493, and dispose of such arms and related materiel as appropriate,
(h) to observe and report in a timely manner, on the position of armed movements and groups, and the presence of foreign military forces in the key areas of volatility, especially by monitoring the use of landing strips and the borders, in particular on the lakes;
5. Decides that MONUC will also have the following mandate, in support of the Government of National Unity and Transition:
(a) to contribute to arrangements taken for the security of the institutions and the protection of officials of the Transition in Kinshasa until the integrated police unit for Kinshasa is ready to take on this responsibility and assist the Congolese authorities in the maintenance of order in other strategic areas, as recommended in paragraph 103 (c) of the Secretary-General's third special report,

(b) to contribute to the improvement of the security conditions in which humanitarian assistance is provided, and assist in the voluntary return of refugees and internally displaced persons,
(c) to support operations to disarm foreign combatants led by the Armed Forces of the Democratic Republic of the Congo, including by undertaking the steps listed in paragraph 75, subparagraphs (b), (c), (d) and (e) of the Secretary-General's third special report,
(d) to facilitate the demobilization and voluntary repatriation of the disarmed foreign combatants and their dependants,
(e) to contribute to the disarmament portion of the national programme of disarmament, demobilization and reintegration (DDR) of Congolese combatants and their dependants, in monitoring the process and providing as appropriate security in some sensitive locations,
(f) to contribute to the successful completion of the electoral process stipulated in the Global and All Inclusive Agreement, by assisting in the establishment of a secure environment for free, transparent and peaceful elections to take place,

(g) to assist in the promotion and protection of human rights, with particular attention to women, children and vulnerable persons, investigate human rights violations to put an end to impunity, and continue to cooperate with efforts to ensure that those responsible for serious violations of human rights and international humanitarian law are brought to justice, while working closely with the relevant agencies of the United Nations;
6. Authorizes MONUC to use all necessary means, within its capacity and in the areas where its armed units are deployed, to carry out the tasks listed in paragraph 4, subparagraphs (a) to (g) above, and in paragraph 5, subparagraphs (a), (b), (c), (e) and (f) above;
7. Decides that MONUC will also have the mandate, within its capacity and without prejudice to carrying out tasks stipulated in paragraphs 4 and 5 above, to provide advice and assistance to the transitional government and authorities, in accordance with the commitments of the Global and All Inclusive Agreement, including by supporting the three joint commissions outlined in paragraph 62 of the Secretary-General's third special report, in order to contribute to their efforts, with a view to take forward:

(a) Essential legislation, including the future constitution,
(b) Security sector reform, including the integration of national defence and internal security forces together with disarmament, demobilization and reintegration and, in particular, the training and monitoring of the police, while ensuring that they are democratic and fully respect human rights and fundamental freedoms,
(c) The electoral process;
8. Requests the Secretary-General to report to the Council within one month of the adoption of this resolution, on reforms necessary to improve the structures of command and control and the management of military information within MONUC, and to rationalize the civilian and police components of MONUC;
9. Requests the Secretary-General, through his Special Representative for the Democratic Republic of the Congo, to coordinate all the activities of the United Nations system in the Democratic Republic of the Congo;
10. Requests the Secretary-General to ensure that his Special Representatives for the Democratic Republic of the Congo and for Burundi coordinate the activities of MONUC and ONUB, in particular:

- by sharing military information at their disposal, especially those concerning cross-border movements of armed elements and arms trafficking,
- by pooling their logistic and administrative resources, to an extent that does not prejudice the ability of these missions to carry out their respective mandates, in order to ensure their maximum efficiency and cost-effectiveness,
- and by coordinating, as appropriate, implementation of the national programmes for disarmament and demobilization and repatriation, reintegration and resettlement;
11. Stresses the need for the Government of National Unity and Transition to carry out the process provided for by the Global and All Inclusive Agreement, and in particular to implement the recommendations listed in paragraph 54 of the Secretary-General's third special report, including by producing, with the support of MONUC, precise plans and timelines in each of the fields identified;
12. Calls upon the Government of National Unity and Transition to cooperate closely with MONUC in establishing three joint commissions on essential legislation, security sector reform and elections, and in implementing the security sector reform, in accordance with paragraph 7 above;

13. Urges the Government of National Unity and Transition to continue with determination and rapidity the integration of the security forces, in particular the integration of the armed forces, and underlines the importance of regular meetings of the Supreme Defence Council and of its cooperation with the international partners of the Democratic Republic of the Congo, especially with MONUC, as positive signals of the commitment of the Government of National Unity and Transition in this regard;
14. Urges the Government of National Unity and Transition to develop without further delay a plan for the disarmament of foreign combatants, and to entrust its implementation to the Armed Forces of the Democratic Republic of the Congo, with the support of MONUC;
15. Urges each of the Governments of the Democratic Republic of the Congo, Burundi, Rwanda and Uganda, to ensure that its territory is not used to infringe the sovereignty of the others, to realize without further delay the complete normalization of their bilateral relations, and to cooperate actively in assuring security along their common borders, in particular by implementing agreements they have signed for the establishment of joint verification mechanisms with the active participation of MONUC, and exhorts them to comply in this regard with the recommendations listed in paragraph 55 of the Secretary-General's third special report;

16. Urges in particular, the Governments of the Democratic Republic of the Congo and Rwanda to work together and with MONUC and the African Union, with a view to removing the threat posed by foreign armed groups, as they have agreed to in the Agreement signed in Pretoria on 30 July 2002 and the Declaration signed in Pretoria on 27 November 2003 and in accordance with the "Terms of Reference" signed in New York on 22 September 2004;
17. Calls upon the Government of National Unity and Transition and Congolese officials at all levels to take all necessary steps, while respecting freedom of expression and of the press, to prevent the use of the media to incite hatred or tensions among communities;
18. Calls upon the Member States, the international organizations concerned and the community of donors to provide their full support to the transitional process, the extension of State authority throughout the territory and long-term social and economic development, in the Democratic Republic of the Congo, and encourages them in this regard to respond positively to the recommendations listed in paragraph 57 of the Secretary-General's third special report;

[... the TARGET BLOCK appears here ...]

21. Recalling its resolution 1502 of 26 August 2003, reaffirms the obligation of all parties to comply fully with the rules and principles of international humanitarian law applicable to them related to the protection of humanitarian and United Nations personnel, and also urges all those concerned to allow immediate, full and unimpeded access by humanitarian personnel to all people in need of assistance as set forth in applicable international humanitarian law;
22. Recalls the link between the illicit exploitation and trade of natural resources in certain regions and the fuelling of armed conflicts and, in line with its resolutions 1493 (2003), 1533 (2004) and 1552 (2004), condemns categorically the illegal exploitation of the natural resources and other sources of wealth of the Democratic Republic of the Congo, urges all States, especially those in the region including the Democratic Republic of the Congo itself, to take appropriate steps in order to end these illegal activities, including if necessary through judicial means, and to report to the Council as appropriate, and exhorts the international financial institutions to assist the Government of National Unity and Transition in establishing efficient and transparent control of the exploitation of natural resources;

23. Welcomes the convening of the international conference on peace, security, democracy and development in the Great Lakes region of Africa, with inclusive participation by all the Governments concerned, under the aegis of the African Union and the United Nations, with a view to strengthening stability in the region and working out conditions that will enable each State to enjoy the right to live in peace;
24. Encourages all Member States to increase international political engagement in the peace process in the region, as requested in paragraph 57 of the Secretary-General's third report;
25. Expressing grave concern at the allegations of sexual exploitation and misconduct by civilian and military personnel of MONUC, requests the Secretary-General to continue to fully investigate these allegations to take the appropriate action in accordance with the Secretary-General's Bulletin on special measures for protection from sexual exploitation and sexual abuse (ST/SGB/2003/13) and to keep the Council informed, further encourages MONUC to conduct training for personnel targeted to ensure full compliance with its code of conduct regarding sexual misconduct, and urges troop-contributing countries to take appropriate disciplinary and other action to ensure full accountability in cases of such misconduct involving their personnel;

26. Requests the Secretary-General to keep it informed regularly of developments in the situation in the Democratic Republic of the Congo, and to submit to the Council before 28 February 2005 a report on the execution of MONUC's mandate, including an evaluation of the structure and strength of its military, civilian and police components, with a view to their adjustment according to the progress made on the ground and the tasks remaining to be accomplished;
27. Reiterates its strong support for the Special Representative of the Secretary-General and MONUC, and for the efforts they continue to make to assist the parties in the Democratic Republic of the Congo and in the region to advance the peace process;
28. Decides to remain actively seized of the matter.

Candidate 0:
  Question: How did the Security Council seek accountability for abuses against civilians in the Democratic Republic of the Congo in 2004?
  Answer: demands that all parties and Governments concerned in the region, including the Government of National Unity and Transition, take without delay all necessary steps to bring to justice those responsible for these violations

Candidate 1:
  Question: How were parties expected to enable MONUC's field operations throughout the Democratic Republic of the Congo in 2004?
  Answer: Demands that all parties cooperate fully with the operations of MONUC and that they ensure the safety of as well as unhindered and immediate access for United Nations and associated personnel in carrying out their mandate, throughout the territory of the Democratic Republic of the Congo
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
    "reason": "The answer is a near-verbatim span from paragraph 19, but 'these violations' needs the preceding sentence to be understood and the span has a trailing referent; it also omits 'as appropriate with relevant international assistance', which is minor."
  },
  {
    "index": 1,
    "grounding": 5,
    "precision": 4,
    "numerical_fidelity": 5,
    "reason": "The answer is a verbatim contiguous span from paragraph 20 that fully answers the question; it includes the fairly long 'safety of as well as unhindered...' clause, which is slightly more than the minimum."
  }
]
````

### Recorded usage

````json
{
  "cached_tokens": 0,
  "completion_tokens": 258,
  "prompt_tokens": 8736,
  "provider_cost": 0.020052,
  "reasoning_tokens": 0
}
````

### Input size diagnostics

````json
{
  "input_characters": 26933,
  "context_capacity_exceeded": null
}
````

## Call 007: faithfulness

Request: `a194862fd9e4449bbaed69621a91e0fe`. Task: `mode/un/2010/ccpr/c/sr_2695#25/practitioner`.

Model: `anthropic/claude-sonnet-5.5`. UTC: 2026-09-30T18:30:21.402878+00:00.

API status: **response**. Duration: 4.094283 seconds.

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

[EN] Document: CCPR/C/SR.2695
  Title: Human Rights Committee
79. Mr. Rivas Posada agreed that paragraph 57 should be deleted.
80. Ms. Keller said that she endorsed the suggestion to delete paragraph 57 and add a fourth bullet in paragraph 54.
However, given that the document was addressed not just to human rights experts, in her view the phrase "such as abduction of women and children" should not be deleted.
Perhaps it could be included in parentheses, after the word "servitude".
81. The Chair said that just a few days earlier, Uzbekistan had referred to alternative military service under article 8.
Therefore, for the purpose of informing States how the issue was to be dealt with, perhaps paragraph 57 should contain a reference to article 18, and the present paragraph 57 should be moved to the section covering article 18.
It appeared that the members of the Committee agreed with that approach, as they did with the new version of paragraph 54.

### REFERENCED DOCUMENTS — none. The target block cites no other document available in the corpus.

### DOCUMENT CONTEXT — surrounding text of the SAME document, supporting context only. It resolves what the target block leaves implicit; it is never a source of answers.

[EN] Document CCPR/C/SR.2695 — surrounding passages
Human Rights Committee
Ninety-eighth session
Summary record of the 2695th meeting
Held at Headquarters, New York, on Monday, 15 March 2010, at 10 a.m.
Chair: Sir Nigel Rodley (Vice-Chair)

Organizational and other matters (continued)
Working methods (continued)

1. The Chair, speaking on behalf of the Committee, expressed his deepest condolences to Mr. Iwasawa, whose mother had passed away.
Working methods (continued) (CCPR/C/2009/1/CRP.2; HRI/GEN/2/Rev.5)
3. Ms. Keller, recalling the discussions of the Committee at its ninety-seventh session on the draft revised guidelines, drew attention to those paragraphs in which approved changes had been incorporated, namely, paragraphs 14 and 15 on focused reports based on replies to lists of issues, and paragraph 25, which now included a proposal made by Ms. Wedgwood for the consideration of the Committee.
She suggested that the Committee might wish to discuss paragraph 17 in light of its recent meeting with representatives of the Department for General Assembly and Conference Management (DGACM) and the Programme Planning and Budget Division (PPBD); as currently drafted, the paragraph imposed no page limits on reports of States parties.
4. Mr. Thelin said he was in favour of setting page limits for States parties' reports.

5. Mr. Lallah said that while he, too, generally supported setting page limits, it was difficult to determine an appropriate limit, as some questions on a list of issues required detailed responses, whereas other, more general ones could be covered in the core document submitted by a State party.
In that connection, he wondered whether the Committee might consider asking States to cover some of the questions normally asked on a list of issues in their core document.
6. Mr. Pérez Sánchez-Cerro said that it was clear from the Committee's meeting with DGACM and PPBD representatives that, rather than seek additional funding for document processing, the Committee should strive to reduce the documentation produced by and for its meetings.
He therefore supported setting page limits on reports submitted by States parties; such limits would furthermore guide them in providing the focused responses sought by the Committee.
The importance of the timely submission of States parties' reports should also be emphasized.

7. Mr. O'Flaherty said that he questioned the usefulness of discussing page limits before more substantive issues, such as the content and format of the list of issues.
8. Mr. Amor said that he supported streamlining the reporting process, on the understanding that the Committee would explore issues that remained unclear in more detail during its constructive dialogues with States parties.
Furthermore, the Committee must cease treating States parties unequally with regard to the amount of time allocated to the consideration of their reports: one rule should apply to all.
9. Ms. Motoc said that it was difficult to determine a page limit that was appropriate to all States parties.
Moreover, imposing additional rules on States parties would not necessarily facilitate the Committee's work.
She supported the statement made by Mr. Amor regarding the need to allocate every State party the same number of hours for consideration of their report.
However, it was also the Chair's responsibility to guide the constructive dialogue with the State party in order to cover the issues raised by the Committee in a satisfactory manner.

10. Ms. Chanet said that she agreed that the issue of page limits would resolve itself once the Committee had adopted guidelines on the content and format of the list of issues.
The Committee was aware of the types of questions that were likely to lead to lengthy responses by States parties and should refrain from asking for additional details where possible.
Furthermore, some questions could be covered in the core document, as proposed by Mr. Lallah.
As for the equal treatment of States parties, she pointed out that some States parties were treated differently because they interacted differently with the Committee.
While such situations needed to be dealt with promptly by the Chair, the Committee as a whole should not be criticized for unequal treatment of States parties if the number of hours originally allocated for consideration of a report needed to be increased.
11. Mr. Thelin said that while he agreed that all States parties should receive equal consideration by the Committee, it was important to note that not all States parties adhered equally to the Covenant and that consideration of their reports might therefore require more time.

That did not mean, however, that the Committee should not institute a cap on the number of pages in a report, which helped States parties focus more narrowly on the questions put to them.
He would therefore be in favour of the shortest possible page limit.
12. Mr. O'Flaherty said that information on the page limits currently being imposed by other treaty bodies would be useful.
13. The Chair said that, according to the harmonized guidelines on reporting under the international human rights treaties including guidelines on a core document and treaty-specific documents (HRI/GEN/2/Rev.5), common core documents should not exceed 60 to 80 pages, initial treaty-specific documents should not exceed 60 pages and subsequent periodic documents should be limited to 40 pages.
Speaking in his capacity as an expert, he said that he was in favour of setting page limits.
While the Committee could not countermand the harmonized guidelines, it could decide whether or not to refer to them in its own reporting guidelines.

14. Ms. Motoc, noting that the words "if possible" preceded the page limits indicated in the harmonized guidelines, said that the Committee's own guidelines currently left it significantly more flexibility.
If the Committee decided to impose a streamlined, more focused report on States parties, the latter might feel the need to express themselves at greater length during the constructive dialogue and thus increase the Committee's workload.
15. Mr. O'Flaherty, pointing out that the suggested page limits referred to in the harmonized guidelines had in fact been drafted by the Secretariat, proposed that the limits should simply be referred to in the Committee's revised guidelines.
16. Ms. Keller said, in reply to Mr. Amor, that the question of a page limit had been dictated by a concern to provide guidelines applicable to all countries.
Concerning Mr. Lallah's suggestion that some issues might be transferred to the core document, she pointed out that the Committee was not competent to determine what went into that document.

17. The Chair said that he had understood Mr. Lallah to mean that in cases where an issue was already addressed in the core document, it could be omitted from the focused report. He proposed that paragraph 19 should remain pending in the absence of a consensus and that the Committee should proceed on an article-by-article basis.
18. Mr. Lallah said that his concern had been to reduce the number of questions, which took up more than 70 paragraphs in the draft revised guidelines, either by transferring or eliminating some of them. Furthermore, it would be useful to make it clear whether initial reports or focused reports were being referred to: some questions seemed to concern the initial report and others to relate to both.
19. The Chair said that there was indeed no need to repeat what was already in the core document.
The guidelines related to some extent to the initial report, but they remained relevant to subsequent reports, including the focused report option.

20. Ms. Chanet said that the most important issues should be addressed in the initial report and that an effort should be made to eliminate any duplication.
21. Mr. Fathalla noted that paragraph 27 of the draft referred to "the most urgent problems arising in the reporting period": that was clearly applicable to both types of reports.
22. Ms. Keller said that paragraph 16 clearly indicated that States not subject to the procedure described in paragraph 15 should follow the guidance provided in paragraphs 18 to 103.
In the new procedure, those paragraphs would not be applicable: questions would be chosen according to their importance for the State party concerned.
Detailed questions would apply to initial or to full reports.
23. Turning to the chapeau provision in paragraph 27, she stressed that the questions were only possible ones and that States parties would not be required to answer every one of them; they might, however, serve to guide officials in preparing the report.
On the possible elimination of questions addressed in the core document, it had to be carefully checked that they were indeed covered in that document, bearing in mind its non-specific character.

24. The Chair noted that the document under consideration was not designed to provide strict rules but merely guidelines.
25. Ms. Majodina asked when it had been agreed that the new procedure would not apply to the initial report, as stated in paragraph 15.
26. Ms. Keller said that the Committee had so decided in October 2009 and that no changes had been made to the draft guidelines, which were based on the Committee's practice, since that time.
She also recalled that the criteria for selecting countries to be discussed in closed meeting were intended for the use of the Committee, not of States parties.
Reverting to the question of the relationship to the core document, she cited paragraph 34 as an example of that document being taken into account.
27. The Chair noted that the wording of the draft guidelines was, however, completely new in relation to the original guidelines, which were still in force.

28. Mr. O'Flaherty said that it might be useful to request in paragraph 27 that, when a State had already provided relevant information in its core document, it should refer thereto in its treaty-specific report; a simple cross-reference would suffice.
That paragraph might also refer to all relevant General Comments, but in general terms, as new ones were constantly being adopted by the Committee.
29. Ms. Keller said that Mr. O'Flaherty's first suggestion could easily be accommodated; as for the second, it was already covered by paragraph 18.
30. Mr. O'Flaherty noted the omission of any reference to a General Comment in paragraph 85; that was no doubt due to the fact that a new one was currently being drafted on article 19, to which it related.
Once the new General Comment was adopted, however, it would be appropriate to refer to it in that paragraph.
Since the Committee could not revisit the guidelines each time a new General Comment was adopted, the solution would be to insert a chapeau provision in section IV.

31. Mr. Thelin said that he agreed on the need for a clear reference to all relevant General Comments.
Paragraph 13, which identified the various types of reporting scenarios, might be a good place to insert such a chapeau provision.
32. The Chair, speaking in his capacity as an expert, said that it would be useful to refer as appropriate to General Comments under each article; it would then be necessary to amend the reporting guidelines each time a new one was adopted.
That question would need to be taken up at a later stage.
In his capacity as Chair, he invited the Committee members to consider the draft guidelines article by article.
Articles 1-2
33. Paragraph 28, relating to article 1, and paragraphs 29-33, relating to article 2, were approved.
Articles 2 (1), 3 and 26
34. Ms. Majodina proposed the inclusion in the last bullet of paragraph 35 of a request for information about the mechanisms for reporting such cases, in addition to information about steps taken to eliminate such discrimination.

35. Mr. O'Flaherty wished to know why article 26, which was so important in itself, had been grouped with articles 2 (1) and 3.
He also wondered whether there was a sufficiently clear indication of the need for disaggregated data regarding discrimination.
Paragraph 38 adequately addressed the various forms of discrimination against women, but paragraph 35 did not cover all possible grounds of discrimination.
The first bullet of that paragraph might usefully stipulate "other status, as well as on any other grounds identified by the Committee", so as to make it clear that the Committee's concerns were not limited to the grounds listed in articles 2 and 26.
36. Ms. Keller said that she could accept Ms. Majodina's suggestion.
In reply to Mr. O'Flaherty's question, she said that the three articles had, exceptionally, been grouped together in line with the Committee's current practice regarding lists of issues.
She could also accept his suggestion to include a reference in paragraph 35 to other grounds of discrimination identified by the Committee.

38. Mr. O'Flaherty suggested the following amended new wording: "other status, such as those identified in the practice of the Committee".
He continued to wonder whether the need for disaggregated data regarding all grounds of discrimination was adequately covered.
Specific language was not required, but merely a mention of the importance of disaggregated data across all grounds of discrimination.
39. Paragraphs 34 to 38, relating to Articles 2 (1), 3 and 26, were approved, subject to drafting changes.
Article 4
Paragraphs 39 to 43
40. Mr. Fathalla, referring to paragraph 41, wondered what the words "correct exercise" meant, when it came to the use of extraordinary powers during a period of emergency.
41. Ms. Keller said that the phrase meant "in conformity with the Covenant".
42. The Chair suggested the following wording: "to ensure that measures taken under a state of emergency are consistent with the requirements of the Covenant".

43. Mr. O'Flaherty said that paragraph 42 should include a requirement for the State party to inform the United Nations Secretary-General.
44. Ms. Keller said that she agreed, but added that if the Committee continued along those lines, the list could become longer than before, as the previous text had excluded items that had already been spelled out in the Covenant.
45. The Chair reminded the Committee that a notification requirement was already in the table of ratifications, reservations and notifications, and that it was not necessary to include it in paragraph 42.
46. Mr. O'Flaherty said that it was better to include the requirement.
It was not just an incidental detail, but an important provision that was often ignored and violated, even though it could serve as a pedagogical tool and a control element for the States.
By being reminded of that notification obligation, States might just end up informing the Secretary-General in the process.

47. Mr. Lallah said that other bodies, including the Human Rights Committee, were also more likely to be notified.
48. Ms. Chanet suggested moving paragraph 33 on terrorism from article 2 to article 4, where it belonged logically.
49. Paragraphs 39 to 43 relating to article 4 of the Covenant were approved, as amended.
Article 6
Paragraphs 44 to 47
50. Mr. O'Flaherty, turning to paragraph 47, said that he regretted that little reference was made to nondeath penalty-related elements.
In addition, the reference in the second bullet to measures taken to help women prevent unwanted pregnancies was unrelated to article 6 as drafted.
Given the very narrow basis on which abortion was dealt with by the Committee, the reference should be nuanced.
According to the jurisprudence and practice of the Committee, article 6 did not include a generic entitlement to prevent unwanted pregnancies.
Accordingly, the text should be redrafted to refer, for example, to measures taken to help women avoid practices that would put their lives at risk.

51. With regard to the last bullet of paragraph 47, General Comment No. 14 referred to nuclear proliferation and hence the reference to nuclear disasters was acceptable.
However, including other items such as environmental pollution and malnutrition went too far and was not consonant with the Committee's practice.
52. Ms. Keller noted that equal access to information and medical care concerning pregnancy had already been covered in several State reports.
Nevertheless, if her understanding was incorrect, then maybe the wording could be amended.
53. Ms. Chanet said that the Committee should simply ask States what they did in cases of unwanted pregnancies and in situations where the mother's life was at risk.
54. Mr. Thelin said that parts of the bullet were straying too far into the area of positive rights; he suggested deleting it altogether and adding language to the penultimate bullet to capture the idea of risk to the mother's life.

55. The Chair suggested that paragraph 47 could simply borrow from the language of General Comment No. 28, paragraph 10, which stated that: "States parties should give information on any measures taken by the State to help women prevent unwanted pregnancies, and to ensure that they do not have to undergo life-threatening clandestine abortions".
56. Mr. O'Flaherty said that he failed to see how the generic issue of unwanted pregnancies fell within the ambit of the Covenant.
The solution of deleting the last bullet of paragraph 47 was not ideal; instead, the language could be amended to capture social risks to life and life expectancy, without going into economic, social and cultural areas.
Wording to the effect of "measures taken to increase life expectancy, including through addressing the risk to life to be found in society", could be included in the text.
57. The Chair suggested that the first clause could read "measures taken to increase life expectancy through reduction of infant mortality", or the reference to the reduction of infant mortality could simply be removed.

58. Ms. Motoc suggested that if social and economic rights were indivisible from civil and political rights, they should be included.
59. The Chair suggested a compromise solution of keeping only the first six words of the bullet point "measures taken to increase life expectancy".
60. Mr. Salvioli said that he supported the proposed text as drafted and did not feel that it strayed into areas beyond the Committee's mandate.
61. Ms. Chanet said that those rights were already in the core document and did not need to be repeated in the proposed text, because it would only give States parties another excuse to digress and to inundate the Committee with information about countless programmes and plans of action.
She suggested deleting the bullet to limit the number of pages that States parties would produce.
62. Mr. O'Flaherty said that he agreed that the bullet should be deleted.
63. The Chair, speaking in his capacity as an expert, suggested that in the first bullet of paragraph 45, the Committee should guide States parties as to the approaches to be followed in the use of force and firearms by the police and security forces.

He preferred making reference to a soft law from another body, typically the United Nations Principles on the Use of Force and Firearms by Law Enforcement Officials, as other treaty bodies and international courts often did.
At the very least, the use of force and firearms should reflect the principle of necessity, meaning that minimum reasonable force should be used, or of proportionality, meaning that such force should be commensurate with the objective to be obtained.
Indeed, the Committee itself had already made reference to such soft law in some of its concluding observations and in individual cases.
64. Mr. Amor, in reference to paragraph 47, suggested adding the notion of honour crimes to the points listed in the penultimate bullet.
65. Mr. Thelin suggested that the word "honour" should be put in quotation marks, or that the qualifier "so-called" should be added to reflect the fact that those crimes had nothing to do with real honour.

66. Paragraphs 44 to 47, pertaining to article 6 of the Covenant, were approved, as amended.
Article 7
Paragraphs 48 to 53
67. Ms. Chanet, referring to paragraph 48, welcomed the clear and precise language of the first four bullets and requested that the fifth and sixth bullets should be revised to bring them in line with the first four.
In paragraph 49, the reference to "detailed information" should be removed and States parties should simply be asked to "indicate" the measures taken to ensure dissemination of information to the population, to prohibit torture, to provide training to law enforcement officials, and to compensate victims.
68. Mr. Amor expressed concern about the end of paragraph 53, which referred to practices governing experimentation on human beings and mechanisms to ensure that experimentation on individuals not capable of expressing free consent was made impossible.
In difficult circumstances where the life of a person depended on the use of medication that had not been fully tested, it would be reasonable to allow parents or legal guardians to be able to give such consent, especially in cases of road accidents, albeit within legal limits.

69. Ms. Chanet said that the Committee had already taken a position on the issue of experimentation in its concluding observations on the Netherlands.
Reference could be made to the measures taken to ensure consent in the case of experimentation, and perhaps a question could be asked regarding what happened to people who could not give such consent.
70. The Chair suggested simply asking what measures States had taken to ensure that consent was given, without being as peremptory as the paragraph would suggest.
Article 8
Paragraphs 54 to 57
71. Mr. O'Flaherty said that in paragraph 54, the phrase "any resurgent form of slavery" should be replaced by "contemporary forms of slavery".
The word "prostitution" should be deleted, as the Committee had never stated that it fell under article 8.
The phrase "prostitution and human trafficking" should be replaced with "all forms of human trafficking".
The phrase "in this regard" should be deleted.

72. A bullet should be added to paragraph 54 regarding training for all public officials involved in addressing trafficking.
While many States had excellent laws against trafficking, officials lacked understanding of the issue.
Paragraph 57 should be deleted.
Compulsory military service had been dealt with under article 18, not as an issue related to slavery or servitude.
73. Ms. Motoc said that since the reference to slavery covered servitude as well, the word "servitude" in paragraph 54 was unnecessary.
In many cases, prostitution was quite close to trafficking in persons.
Consent was sometimes weak.
While in some countries work permits were issued to prostitutes, the trend in human rights was away from legalizing prostitution.
The issue of demand for trafficking must be addressed directly: trafficking existed because there was a demand for it.
74. Mr. Amor said that many forms of servitude were not new, for example, slavery.
He therefore preferred the phrase "all forms of servitude and trafficking", without reference to prostitution and the abduction of women and children.
The phrase "measures to eradicate definitively all forms of servitude" could also be included.

75. Mr. O'Flaherty noted that the purpose of his drafting comments was not to express a personal position, but rather to achieve a document which best expressed the practice of the Committee.
He had not expressed a personal view on the relationship of prostitution to human rights.
76. Ms. Chanet said that she agreed that paragraph 57 should be deleted.
She also agreed with Mr. O'Flaherty's comments on prostitution and with those of Mr. Amor in reference to paragraph 54.
77. Ms. Motoc said that she had not expressed a personal view on prostitution. Rather, her comments reflected a position which was widely held and which had been voiced by the Special Rapporteur on violence against women, its causes and consequences and by the Special Rapporteur on trafficking in persons, especially in women and children.
78. The Chair said that the present meeting was not the forum for establishing new policy.

[... the TARGET BLOCK appears here ...]

82. Mr. Amor noted that there should be mention of domestic labour.
In some cases, it amounted to a form of slavery, often involving little girls.
83. Ms. Chanet expressed concern about the risks involved in making lists.
In her view, forced marriage was worse than prostitution.
If a list was compiled, something would surely be left out.
It was better to use more generic terms.
84. The Chair said that, paradoxically, the more inclusive the Committee was, the more implicitly exclusive it would be.
However, the purpose was to give guidance to States, and generic language added little to what was already in the Covenant.
Two approaches had taken shape in the course of the discussion, one of which was to mention slavery, contemporary forms of slavery and all other forms of servitude and to stop there.
The other approach was to include the abduction of women and children, all forms of human trafficking, enforced domestic work and forced marriage.
He saw the inclusive route as more helpful to States.
The purpose of the current exercise was to provide guidance to States, and it was therefore necessary to make the guidelines reflect the current Committee practice.

85. Mr. Lallah said that bonded labour should be mentioned, as well.
The Committee had dealt with the issue in the case of India.
86. The Chair said that as bonded labour was a contemporary form of slavery, he had no objection to including it.
87. Ms. Motoc said that bonded labour was not new.
88. Mr. Amor said that it was best to use generic terms in the text and raise specific issues with States.
89. The Chair said that if generic terms were used rather than a list, those terms would include contemporary forms of slavery and all forms of servitude. There should also be mention of trafficking.
90. After requesting the members of the Committee to indicate by a show of hands which of the two approaches they supported, he noted that the room was evenly divided in its opinions.
91. Ms. Majodina said that there should be a list.
In many countries, such forms of servitude as abduction of women and children and forced marriages were traditional practices, and even government officials saw nothing wrong with them.
It would be useful to draw the attention of States parties to the fact that such practices were wrong and in violation of article 8 of the Covenant.

In many African countries, people saw nothing wrong with a child of 5 years of age working in a huge household.
92. Mr. O'Flaherty said that he favoured generic references because the guidelines must be applicable to all countries, regardless of their human rights situation.
A list would be imperfect because it would encompass only certain phenomena.
The term "contemporary forms of slavery" was inclusive, covering all types of abuse.
He would prefer the reference to trafficking to be retained, but was prepared to join a consensus in the interest of saving time.
93. Ms. Motoc said that certain issues should be emphasized to avoid a situation in which States thought that change was not necessary.
Because generic terms would let them avoid the issue, she favoured a list.
94. Mr. Amor said that the positions of the Committee members were in fact quite close to each other.
95. Ms. Chanet said that although she had previously held the position that it was better not to be too specific, she could see that States would gain a better understanding of their violations if certain types of violations were explicitly named.
The whole world must be treated with complete equality.

96. The Chair said that it was his understanding that a consensus had been achieved: rather than generic terms, there would be a list of specific violations in paragraph 54.
97. Mr. Fathalla requested clarification as to why the three bullet points in paragraph 54 referred only to trafficking rather than to all the issues in the chapeau, given that trafficking was already referred to in the chapeau.
98. Ms. Keller said that it would be necessary to look at the revised text.
She suggested that the Committee should study the new version and determine if it wished to retain paragraph 55 as written.
99. The Chair said that that issue could be considered at a later date.

Candidate 0:
  Question: On 15 March 2010, what article reference was paragraph 57 to contain in the Human Rights Committee's guidance to States?
  Answer: a reference to article 18

Candidate 1:
  Question: Where was paragraph 57 to be moved in the Human Rights Committee's guidance on 15 March 2010?
  Answer: the section covering article 18
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
    "reason": "The Chair said 'perhaps paragraph 57 should contain a reference to article 18', so the answer is a direct span. It is a tentative suggestion ('perhaps'), which the answer presents as settled, though the block adds that members seemed to agree. The answer includes a minor 'a reference to' phrase, and 'article 18' is exact."
  },
  {
    "index": 1,
    "grounding": 4,
    "precision": 4,
    "numerical_fidelity": 5,
    "reason": "The span 'the present paragraph 57 should be moved to the section covering article 18' is directly supported. Like the first pair, it presents a tentative proposal as settled, though the members' apparent agreement is noted. The identifier 'article 18' is exact."
  }
]
````

### Recorded usage

````json
{
  "cached_tokens": 0,
  "completion_tokens": 307,
  "prompt_tokens": 12535,
  "provider_cost": 0.02814,
  "reasoning_tokens": 0
}
````

### Input size diagnostics

````json
{
  "input_characters": 38380,
  "context_capacity_exceeded": null
}
````

## Call 008: faithfulness

Request: `ea446d1a66b548fc873ee0d5da9e1da4`. Task: `mode/un/2007/gc_12/c_1/sr_1#10/semantic`.

Model: `anthropic/claude-sonnet-5.5`. UTC: 2026-09-30T18:30:21.405101+00:00.

API status: **response**. Duration: 3.14066 seconds.

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

[EN] Document: GC.12/C.1/SR.1
  Title: General Conference
"9. The emergence of Aid for Trade, to assist least developed countries in developing their trade-related productive capacity and for meeting other trade-related needs, is a landmark development.
The Enhanced Integrated Framework is a promising tool for analysis and identification of needs in the area of trade capacity-building, and for implementation of projects identified.
"10. UNIDO's core mandate is to support industrial development, including in least developed countries.
Aid for Trade and the Enhanced Integrated Framework emphasize development of supply capacity and trade-related infrastructure.
We call upon UNIDO to work closely with countries engaged in the Framework process and, wherever possible, to act as an implementing agency, particularly concentrating in developing industrial capacity and standards and conformity related infrastructure.
"11. In enhancing productive capacity, donors should also utilize the services of UNIDO.
We call upon UNIDO to create a special Trust Fund for least developed countries, and urge donors to contribute generously to the Fund.

### REFERENCED DOCUMENTS — none. The target block cites no other document available in the corpus.

### DOCUMENT CONTEXT — surrounding text of the SAME document, supporting context only. It resolves what the target block leaves implicit; it is never a source of answers.

[EN] Document GC.12/C.1/SR.1 — surrounding passages
General Conference
Twelfth session
Main Committee
Summary record of the 1st meeting
Held at the Austria Center Vienna on Tuesday, 4 December 2007, at 10.30 a.m.
Chair: Mr. Lundby .(Norway)

Agenda item
Organization of work
Election of officers
Financial matters
Programme and budgets, 2008-2009
Strategic Approach to International Chemicals Management
UNIDO Staff Pension Committee
Financial matters (continued)
Medium-term programme framework, 2008-2011

The Chair said that the Committee would be discussing items 7-18 of the Conference agenda.
A set of other texts had been circulated informally without a symbol; they consisted of various proposals that had been submitted and would need to be considered by the Committee.
He requested delegates not to make statements of principle and only to comment on the specific texts under consideration by the Committee.
Mr. Mogadingwane (South Africa), speaking on behalf of the African Group, nominated Mr. Gumbi (South Africa).
Mr. Idris (Indonesia), speaking on behalf of the Asian Group, nominated Mr. Shaghaghi (Islamic Republic of Iran).
Mr. Gumbi (South Africa), Mr. Shaghaghi (Islamic Republic of Iran), Mrs. Noriega Urizar (Guatemala) and Ms. Brdovčak (Croatia) were elected Vice-Chairs of the Committee by acclamation.
(GC.12/4; GC.12/CRP.3; IDB.33/3)
The draft decision on agenda item 10 (a) in document GC.12/CRP.3 was adopted for recommendation to the plenary.
The Chair invited comments on the draft decision on item 10 (c) contained in document GC.12/CRP.3.

The draft decision on item 10 (c) in document GC.12/CRP.3 was adopted for recommendation to the plenary.
The Chair invited comments on the draft decision on item 10 (d) contained in document GC.12/CRP.3.
The draft decision on item 10 (d) in document GC.12/CRP.3 was adopted for recommendation to the plenary.
(GC.12/4, GC.12/8; GC.12/CRP.3)
The Chair invited comments on the draft decision on agenda item 13 contained in document GC.12/CRP.3.
The draft decision on item 13 in document GC.12/CRP.3 was adopted for recommendation to the plenary. Strategic Approach to International Chemicals Management (GC.12/4; GC.12/CRP.3; IDB.33/20)
The Chair invited comments on the draft decision on item 15 contained in document GC.12/CRP.3.
The draft decision on item 15 in document GC.12/CRP.3 was adopted for recommendation to the plenary.
UNIDO Staff Pension Committee (GC.12/CRP.3; IDB.33/Dec.8)
The Chair said he understood that it was proposed that the alternate member of the Staff Pension Committee whose name had been left blank in the draft decision on item 16 in document GC.12/CRP.3 should be Mr. Bilal Kabalan (Lebanon).

On that understanding, the draft decision on item 16 in document GC.12/CRP.3 was adopted for recommendation to the plenary.
The Chair said it had come to his attention that there was some interest in addressing once again the matter of unencumbered balances of appropriations.
Taking into account experience at previous sessions, he suggested that the matter should be postponed pending the preparation, in consultation with the Secretariat, of a possible text on unencumbered balances of appropriations to be combined with the text on item 10 (b) in document GC.12/CRP.3 and submitted to the Committee as a draft of the Chair.
It was so agreed.
The Chair invited comments on the draft decision on the restoration of the voting rights of Costa Rica suggested in paragraph 4 of document GC.12/14.
The draft decision was adopted for recommendation to the plenary.
The Chair invited comments on the draft decision contained in chapter II.B of document GC.12/CRP.3, entitled "Payment plan and request for restoration of voting rights - Moldova".

(IDB.32/8 and Add.1)
The Chair drew attention to the following draft resolution submitted by the Ministerial Conference of the Least Developed Countries (LDCs), held at Vienna on 29 and 30 November 2007, and contained in the set of texts circulated without a symbol:
"The General Conference,
"Taking note of the Ministerial Conference of the Least Developed Countries convened in Vienna on 29 and 30 November 2007,
"Also taking note of the Vienna Ministerial Declaration of the Least Developed Countries adopted by the Ministerial Conference and contained in the annex to the present resolution,
"Invites the Director-General, in implementing the medium-term programme framework, 2008-2011, to take special account of the needs of the least developed countries.
"Annex
"We, the Ministers and Heads of Delegation of the least developed countries participating in the Ministerial Conference held in Vienna, Austria on 2930 November 2007, reiterating our commitment to strengthen the role of the United Nations Industrial Development Organization in promoting the industrial development of the least developed countries as a means to accelerate their development and integration into the multilateral trading system, particularly in the context of the new opportunities being created by aid for trade and the Enhanced Integrated Framework,

"Recalling the Declaration and Programme of Action for the Least Developed Countries for the Decade 2001-2010, adopted in Brussels in 2001,
"Appreciating the particular focus by UNIDO, within its mandate, on two essential commitments of the Brussels Programme of Action:
"`Commitment 4: Building productive capacities to make globalization work for LDCs;
"`Commitment 5: Enhancing the role of trade in development'".
"Being aware of the importance that foreign trade can play in the industrialization and economic development of a least developed country, and also aware that trade is an opportunity and not a guarantee, and therefore requires policy intervention to be successful,
"Recalling that within the framework of the Millennium Development Goal (MDG) 8, Indicator 40 is aimed at increasing the proportion of Official Development Assistance provided to help build trade capacity,
"Recalling also that the Sixth World Trade Organization Ministerial Conference, held in Hong Kong in 2005, called for the expansion of Aid For Trade to help developing countries, particularly least developed countries, to benefit from WTO agreements, expand their trade and enhance their ability to take full advantage of new trade opportunities,

"Recognizing that new opportunities are being created by Aid For Trade and the Enhanced Integrated Framework,
"Deeply appreciating the efforts of the United Nations Industrial Development Organization to assist the least developed countries to take the path to sustainable economic development, using manufacturing as a dynamic force, and to export more value added products complying with international standards,
"Declare that:
"1. The Millennium Development Goals, as well as the other internationally agreed development goals, can most effectively be achieved in the least developed countries through a process that also emphasizes industrial growth, diversification and export of manufactured products.
"3. The commitments made in the 2005 World Summit to address the special needs of the least developed countries should be implemented fully.
In this regard, all countries, the United Nations system, the Bretton Woods institutions and other organizations should make concerted efforts and adopt speedy measures to meet in a timely manner the goals and targets of the Brussels Programme of Action and the World Summit.

"4. The beneficial and meaningful integration of the least developed countries into the multilateral trading system is an important objective of the Doha Development Agenda and the 2005 Sixth Ministerial Conference of the World Trade Organization.
It is vital that the LDCs be able to enter the global value chains with manufactured products and processed foods, apart from other contributions in services, with the aid of targeted technical assistance from UNIDO.
"5. In order to enable the least developed countries to benefit from the opportunities of the multilateral trading system, their manufacturing supply-side needs must be addressed. This requires the enhancement of their productive capacity, as stated in Commitment 4 of the Brussels Programme of Action. This will enable the least developed countries to enhance the role of trade in their development (Commitment 5).
"6. Considering the limited opportunities available to least developed countries, we call upon UNIDO to play a pioneering role in developing industrial productive capacity in those countries in a manner that ensures that products conform to acceptable international standards.

Depending on the needs of specific LDCs this may, inter alia, entail efforts to develop entrepreneurship, creating an enabling business environment, developing domestic research capacity, investment facilitation, development of agro business, along with delivery of targeted technical assistance and capacity-building for developing standards, testing, certification and accreditation capabilities accepted in international markets, and integration of the local with the global value chains, lending support in finding markets.
"7. Given the increasing importance of the South as a destination for least developed country exports and the potential for these countries to benefit from their increasing collaboration with the South, UNIDO should promote mutually beneficial least developed countries-South cooperation in areas within its mandate.
"8. UNIDO should help least developed countries with commodity-specific interventions, wherever required by those countries, including in the development of technology, enhancing research, moving up the value chain and improving the welfare of those employed in, or dependent on, those commodities in the least developed countries.
This is particularly needed for cotton.

[... the TARGET BLOCK appears here ...]

"12. UNIDO is hosting an LDC Ministerial Conference after more than a decade.
"The Ministers and Heads of Delegation of the least developed countries are deeply grateful to UNIDO for hosting the Ministerial Conference and for the excellent arrangements made for it.
We thank the G-77 and China for co-sponsoring this event.
Mr. Nyaphisi (Lesotho), supported by Ms. Espinoza Patiño (Bolivia), introducing the draft resolution, said that it represented the outcome of the Ministerial Conference.
Since 90 per cent of world trade was in manufactured goods, the real, sustained benefits could come only from the export of such goods.
The LDCs were primarily raw material and primary commodity exporters, and while their share of world exports had been more than 3 per cent in the 1960s it had now dwindled to about 0.5 per cent.
Unless some remedial action was taken, their fate would be uncertain.
The world community had recognized the problem, and the "Aid for Trade" programme had been launched.
Many countries and groups had offered help under the programme, but the only organization of the United Nations system to deal with productive capacity enhancement was UNIDO, and the LDCs had been delighted that the Organization had taken the initiative to convene the Ministerial Conference.

At its conclusion, ministers had adopted a Ministerial Declaration which outlined what they would like UNIDO to do with its mandate.
The LDCs hoped that the draft resolution submitted by them would be endorsed by the Committee and adopted unanimously by the Conference.
The draft resolution submitted by the Ministerial Conference of the LDCs was adopted for recommendation to the plenary.
Mrs. Noriega Urizar (Guatemala) introduced the following draft resolution submitted by the Group of 77 and China entitled "Regional programme for Latin America and the Caribbean": "The General Conference:
"Recalling resolution GC.11/Res.1, entitled "Regional programme for Latin America and the Caribbean", in which the Director-General was requested to establish a regional programme for Latin America and the Caribbean,
"Recognizing the joint work that has been carried out to date by Member States and the Secretariat with the aim of defining that regional programme and, in particular, the conclusions set out in the final document of the Latin America and the Caribbean Second Expert Group Meeting, held in Vienna in November 2007,

"Considering that resolution GC.11/Res.1 requested inter alia the Secretariat of UNIDO to identify and mobilize financial resources which would permit the implementation of the regional programme for Latin America and the Caribbean,
"Requests the Director-General:
"(a) To adopt the necessary measures so that the activities in execution of the regional programme for Latin America and the Caribbean are duly reflected in the medium-term programme framework, 2008-2011, in order to sustain the work initiated;
"(b) To continue his efforts, in consultation with the Member States of the region, to identify and mobilize further financial resources required for its full implementation, at the same time calling upon the international community to provide financial support to the programme;
She said that, following the adoption of resolution GC.11/Res.1 in 2005, the first steps had been taken to set up a regional programme for Latin America and the Caribbean; UNIDO had assisted the region in establishing a strategy and defining priorities.
The proposed draft resolution was intended to provide continuity and to ensure that the programme activities were reflected in the medium-term programme framework, 2008-2011.

In the second preambular paragraph, the term "approved document" might be preferable to "final document".
In operative paragraph (b), the words "and mobilize further financial resources" might be amended to read "and mobilize additional voluntary resources ...".
Mr. Roselló (Spain), speaking on behalf of the Western European and Others Group, suggested that in the second preambular paragraph, "adopted" might be used instead of "approved".
The exact dates of the Second Expert Group Meeting mentioned in the same paragraph might also be added.
Mrs. Noriega Urizar (Guatemala) agreed.
The exact dates of the Second Expert Group Meeting were 28-30 November 2007.
The Chair said that, if he heard no objection, he would take it that the second preambular paragraph and operative paragraph (b) should be amended as proposed.
Mr. Quesada (Mexico) wondered whether the word "additional" should be added before the words "financial resources" in the second line of the third preambular paragraph to make the text consistent with operative paragraph (b).

The Chair noted that the General Conference resolution referred to in the third preambular paragraph did not in fact contain the word "additional".
Mr. Duarte (Portugal) thought that it would be better in that case to leave the text as it stood.
Mr. Quesada (Mexico) agreed.
The draft resolution entitled "Regional programme for Latin America and the Caribbean", as amended, was adopted for recommendation to the plenary.
Mr. Duarte (Portugal), speaking on behalf of the European Union, introduced the following draft resolution entitled "Results-based management":
"Welcoming the introduction of results-based management principles and practices at UNIDO,
"Further welcoming the establishment of the Results-based Management Steering Committee at UNIDO to carry out a base-line self-assessment of the status of results-based management implementation in UNIDO, draft a conceptual framework for further development of results-based management in the Organization, and define a time-bound results-based management implementation strategy with milestones,
"Cognizant of the need to further refine and harmonize results-based management within the United Nations system,

"(a) To continue to give priority to the comprehensive adoption of results-based management principles by UNIDO, and the full integration of results-based management approaches methods in all spheres of its activities;
"(b) To continue to provide the governing bodies with regular updates on the implementation of results-based management in UNIDO;
He said that the European Union welcomed the fact that UNIDO had established a sound basis for the implementation of results-based management principles and practices in all spheres of its activities and wished to encourage the Organization to continue to give priority to their implementation and provide updates thereon.
The draft resolution was also sponsored by Croatia, Norway, Serbia and Turkey.
Mr. Bougacha (Tunisia) welcomed the draft resolution but thought that it might be better to delete the reference in the first preambular paragraph to an informal document which might not have been translated into all the official languages.
He also questioned the appropriateness in a resolution concerned with UNIDO of speaking of harmonizing work "within the United Nations system".

Mr. Duarte (Portugal) said that he could accept the deletion of the reference in the first preambular paragraph, which would not affect the substance of the draft resolution.
The Chair said he took it that it was agreed to delete the documentary reference in the first preambular paragraph.
Mr. Duarte (Portugal), referring to the question of harmonization within the United Nations system, said that it seemed important to stress the involvement of UNIDO in the work of the wider United Nations system, ensuring coherence with other agencies, and to mention the need for harmonization with the United Nations system as a whole.
Mr. Bougacha (Tunisia) said that, while the United Nations system certainly needed to continue to strengthen results-based management, UNIDO should focus on development and not on strengthening results-based management within the United Nations system.
He could accept the reference to the United Nations system in the fourth preambular paragraph, but would prefer to see operative paragraph (c) deleted.

Ms. Permanyer (Cuba) supported the remarks of the representative of Tunisia, believing that the draft should confine itself to results-based management in UNIDO.
Mr. Duarte (Portugal) thought that the intention of operative paragraph (c) might be made clearer by amending the phrase "harmonize the approach" to read "harmonize its approach".
Mr. Kim Sung-hwan (Republic of Korea) supported that suggestion.
However, it was a good idea to set the topic within the wider perspective of the United Nations system and to urge UNIDO to continue to work with other organizations.
Mr. Bougacha (Tunisia) agreed with the suggestion to change "the" to "its" but said he would still prefer the deletion of the phrase "within the United Nations system" at the end of operative paragraph (c).
Ms. Leucuta (Romania) suggested that the phrase "within the United Nations system" be moved from the end of the paragraph to after the words "with other organizations", to make the meaning still clearer.
The draft resolution entitled "Results-based management", as amended, was adopted for recommendation to the plenary.

Candidate 0:
  Question: How was UNIDO expected to support least developed countries through Aid for Trade and the Enhanced Integrated Framework in 2007?
  Answer: We call upon UNIDO to work closely with countries engaged in the Framework process and, wherever possible, to act as an implementing agency, particularly concentrating in developing industrial capacity and standards and conformity related infrastructure.

Candidate 1:
  Question: What dedicated financing arrangement was proposed for least developed countries through UNIDO in 2007?
  Answer: We call upon UNIDO to create a special Trust Fund for least developed countries, and urge donors to contribute generously to the Fund.
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
    "reason": "The answer quotes one sentence of the target block almost verbatim and is well grounded; the question's '2007' comes from the document context, and the answer keeps the 'We call upon' phrasing, which adds slight extra wording."
  },
  {
    "index": 1,
    "grounding": 5,
    "precision": 4,
    "numerical_fidelity": 5,
    "reason": "The answer is a direct verbatim sentence from the target block; the clause about urging donors to contribute is a small extra beyond the 'financing arrangement' asked."
  }
]
````

### Recorded usage

````json
{
  "cached_tokens": 0,
  "completion_tokens": 238,
  "prompt_tokens": 9916,
  "provider_cost": 0.022212,
  "reasoning_tokens": 0
}
````

### Input size diagnostics

````json
{
  "input_characters": 29440,
  "context_capacity_exceeded": null
}
````

## Call 009: faithfulness

Request: `88e47ef713a6441a80312a0cf3963a18`. Task: `mode/un/2003/a/res/57/300#10/lookup`.

Model: `anthropic/claude-sonnet-5.5`. UTC: 2026-09-30T18:30:21.407083+00:00.

API status: **response**. Duration: 3.140246 seconds.

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

[EN] Document: A/RES/57/300
  Title: Resolution adopted by the General Assembly
27. Concurs with the intention of the Secretary-General to establish a panel of eminent persons, reflecting a diversity of views, to review the relationship between the United Nations and civil society, stresses that the terms of reference of such a panel should underscore the intergovernmental character of the United Nations, and decides to consider the recommendations of the panel through the respective intergovernmental process;
28. Decides that the creation of a partnership office as part of the effort to enhance cooperation in the work of the Organization with the private sector, taking into account the outcome of the major United Nations conferences and summits, should be subject to its resolutions 55/215 of 21 December 2000 and 56/76 of 11 December 2001;
29. Recognizes the need to continue to improve and streamline the planning, programming and budgetary cycle of the Organization;
30. Notes the reference to sunset provisions in the report of the Secretary-General, and recalls that no decision has been taken in this regard;

### REFERENCED DOCUMENTS — other documents CITED by the target block, supplied so you can UNDERSTAND those citations. Context only: never a source of answers, never the subject of a question.

[EN] Reference: A/RES/55/215 — Resolution adopted by the General Assembly
Resolution adopted by the General Assembly
[without reference to a Main Committee (A/55/L.71 and Add.1)]
55/215. Towards global partnerships
The General Assembly,
Reaffirming the central role of the United Nations, in particular the General Assembly, in the promotion of partnerships in the context of globalization,
Underlining the intergovernmental nature of the United Nations,
Recalling the priorities and objectives formulated in the United Nations Millennium Declaration, particularly in regard to developing strong partnerships in pursuit of development and poverty eradication,
Stressing that efforts to meet the challenges of globalization could benefit from enhanced cooperation between the United Nations and all relevant partners, in particular the private sector, in order to ensure that globalization becomes a positive force for all,
Taking into account ideas expressed in the report of the Secretary-General entitled "We the peoples: the role of the United Nations in the twenty-first century" of 27 March 2000 with regard to enhanced cooperation with the private sector,

1. Stresses the need for Member States further to discuss partnerships and consider, in appropriate intergovernmental consultations, ways and means to enhance cooperation between the United Nations and all relevant partners, inter alia, from the developing countries, to give them greater opportunities to contribute to the realization of the goals and programmes of the Organization;
2. Requests the Secretary-General in this regard to seek the views of all Member States on ways and means to enhance cooperation between the United Nations and all relevant partners, in particular the private sector;
3. Invites the Secretary-General also to seek the views of relevant partners, in particular the private sector, on how to enhance their cooperation with the United Nations;
4. Requests the Secretary-General to submit a comprehensive report on this matter, containing a compilation of views of Member States, views of other relevant partners, and his recommendations in this regard, for consideration by the General Assembly at its fifty-sixth session;
5. Decides to include in the agenda of its fifty-sixth session the item entitled "Towards global partnerships". 88th plenary meeting

### DOCUMENT CONTEXT — surrounding text of the SAME document, supporting context only. It resolves what the target block leaves implicit; it is never a source of answers.

[EN] Document A/RES/57/300 — surrounding passages
Resolution adopted by the General Assembly
[without reference to a Main Committee (A/57/L.74 )]
57/300. Strengthening of the United Nations: an agenda for further change
The General Assembly,
Reaffirming its determination to strengthen further the role, capacity, effectiveness and efficiency of the United Nations and thus improve its performance in order to realize the full potential of the Organization, in accordance with the purposes and principles of the Charter of the United Nations, and to respond more effectively to the needs of Member States and existing and new global challenges facing the United Nations in the twenty-first century,
Recalling all the previous reform efforts, including those based on the report of the Secretary-General and its resolutions 52/12 A of 12 November 1997 and 52/12 B of 19 December 1997, entitled "Renewing the United Nations: a programme for reform",
Recalling also Article 97 of the Charter, the rules of procedure of the General Assembly and the Financial Regulations and Rules of the United Nations,

Recalling further the respective mandates of various treaty bodies,
Having in mind the necessity to pursue the process of revitalization of the General Assembly, reform of the Security Council, restructuring of the Economic and Social Council and modernization of the Secretariat,
Bearing in mind that notable political, economic and social developments, particularly in Africa, call for continued strong and focused cooperation between the United Nations system and the Member States,
1. Welcomes the efforts and initiatives of the Secretary-General aimed at further reforming the United Nations to cope with contemporary challenges and address new priorities facing the Organization in the twenty-first century;
2. Stresses that the strengthening of the United Nations encompasses the revitalization, reform and restructuring of the principal organs of the United Nations;
3. Requests the Secretary-General, while implementing the provisions of the present resolution, to continue to take into account the views and comments expressed by Member States and to respect fully the Charter of the United Nations and the relevant decisions and resolutions of the General Assembly;

4. Welcomes the intention of the Secretary-General to submit a shorter proposed programme budget for the biennium 2004 - 2005 that fully justifies the resource requirements and better reflects the priorities of the medium-term plan for the period 2002 - 2005, the United Nations Millennium Declaration and the outcomes of the major international conferences, taking into account the full scope of the Regulations and Rules Governing Programme Planning, the Programme Aspects of the Budget, the Monitoring of Implementation and the Methods of Evaluation, while emphasizing that reform should not be seen as a budget-cutting exercise;
5. Emphasizes the need to further strengthen the efforts of the United Nations in implementing the development goals through enhanced mechanisms, adequate resources and effective follow-up activities;
6. Takes note of the proposal of the Secretary-General to develop and present plans for strengthening inter-agency coordination in respect of human rights technical assistance, which are carried out at the country level, at the request of interested countries;

7. Stresses the importance of the country-driven approach in the operational activities of the United Nations funds and programmes, bearing in mind their existing mandates;
8. Encourages States parties to the human rights treaties and the respective treaty bodies to review the reporting procedures of treaty bodies with a view to developing a more coordinated approach and to streamlining the reporting requirements under these treaties, and requests the United Nations High Commissioner for Human Rights to support this exercise, including through submission of recommendations, as appropriate;
9. Requests the Commission on Human Rights and the relevant intergovernmental bodies to review the human rights special procedures in order to rationalize their work and enhance their effectiveness, consistent with their mandates, and also requests the United Nations High Commissioner for Human Rights to support this exercise, including through submission of recommendations, as appropriate, and by providing adequate administrative support to each of these special procedures;

10. Encourages the efforts of the Secretary-General to improve the effectiveness and management of the Office of the United Nations High Commissioner for Human Rights, in accordance with the relevant resolutions and decisions and taking into account, as appropriate, the report of the Office of Internal Oversight Services of the Secretariat;
11. Welcomes the proposals of the Secretary-General to improve the effective and targeted delivery of public information activities, including the restructuring of the Department of Public Information of the Secretariat, in accordance with the relevant resolutions and decisions of the General Assembly;
12. Reaffirms the role of the Committee on Information in guiding the process of restructuring the Department of Public Information, and therefore invites the Committee on Information to engage actively in the process;
13. Welcomes the continuing efforts to enhance the use of information technology within the Department of Public Information, bearing in mind the constraints experienced by developing countries in terms of access to information;

14. Takes note of the proposals of the Secretary-General contained in action 9 of his report,3 which are intended to improve the management of the libraries, and requests the Secretary-General to submit a report for further consideration by the relevant United Nations bodies, including the Committee on Information at its twenty-fifth session, with a view to taking a decision on the proposals of the Secretary-General in this regard at its fifty-eighth session;
15. Also takes note of the proposal of the Secretary-General contained in action 8 of his report,3 to rationalize the network of United Nations information centres around regional hubs, where appropriate, in consultation with concerned Member States, starting with the creation of a Western European hub, followed by a similar approach in other high-cost developed countries, and requests the Secretary-General to submit a progress report on the implementation of the proposal with the objective of applying this initiative in other regions, in consultation with Member States, where this initiative will strengthen the flow and exchange of information in developing countries;

16. Notes the proposal of the Secretary-General to transfer the functions and resources of the Cartographic Section from the Department of Public Information to the Department of Peacekeeping Operations of the Secretariat, while maintaining the service currently provided to users outside the Department of Peacekeeping Operations, and decides to consider the proposal in the context of the proposed programme budget for the biennium 2004 - 2005;
17. Welcomes the intention of the Secretary-General to conduct a systematic evaluation of the impact, efficiency and cost-effectiveness of all activities of the Department of Public Information, and requests the Secretary-General, with assistance from the Office of Internal Oversight Services, to proceed as quickly as possible in this regard and to report on progress made to the General Assembly at its fifty-eighth session, through the Committee on Information at its twenty-fifth session;
18. Notes the proposal to improve the electronic access to United Nations collections, publications and parliamentary documents, and requests the Secretary-General to keep the internal capacity for the provision of hard copies at the request of Member States, subject to the relevant provisions of its resolution 56/242 of 24 December 2001;

19. Welcomes the proposals of the Secretary-General to improve the efficiency and effectiveness of the conference-servicing function of the United Nations, and requests the Secretary-General to continue to consult Member States, including relevant groups, on how best to accomplish this goal with due attention to their needs, and in this regard emphasizes the need for Member States to take well-informed decisions, and decides that the measures pertinent to it will be decided upon in the context of its consideration of the report of the Secretary-General on improving the performance of the Department of General Assembly Affairs and Conference Services;
20. Requests the Secretary-General to start, on a trial basis, a consultative process with the President of the General Assembly and the Chairmen of the Main Committees of the Assembly at the end of the main part of each session of the Assembly, with a view to consolidating reports on related subjects, if decided by the Main Committees;

21. Also requests the Secretary-General to submit proposals on recurring reporting requirements to the General Assembly at its fifty-eighth session for consideration and decision;
22. Welcomes the intention of the Secretary-General to develop an implementation plan to strengthen the effectiveness of the United Nations presence for developmental and humanitarian activities in developing countries by September 2003, and requests the Secretary-General to submit a report for the consideration of the General Assembly through the relevant intergovernmental bodies;
23. Also welcomes the intention of the Secretary-General to issue a document clarifying the roles and responsibilities of the various United Nations entities in the area of technical cooperation by September 2003 and to submit a report thereon to the relevant intergovernmental bodies for their consideration;
24. Further welcomes the efforts of the Secretary-General to strengthen the management capacities of the Department of Economic and Social Affairs of the Secretariat, inter alia, by establishing a policy planning unit, and notes in this regard his intention to submit, in the context of the proposed programme budget for the biennium 2004 - 2005, proposals for a new position of Assistant Secretary-General for its consideration;

25. Endorses the decision of the Secretary-General to entrust the Under-Secretary-General and Special Adviser on Africa, who will report directly to him, with the responsibilities of:
(a) Coordinating and guiding the preparation of Africa-related reports and inputs, in particular support for the New Partnership for Africa's Development by the United Nations system and the international community, and the coordination of global advocacy in support of the New Partnership;
(b) Coordinating the interdepartmental task force on African affairs to ensure coherence and an integrated approach for United Nations support to Africa, including following up the implementation of all summit and conference outcomes related to Africa and addressing gaps and initiating reports on critical issues affecting Africa;
26. Approves the transfer of resources allocated to the Office of the Special Coordinator for Africa and the Least Developed Countries and those from the current Office of the Adviser for Special Assignments in Africa, to the new Office of the Under-Secretary-General and Special Adviser on Africa, and requests the Secretary-General to ensure that the new Office is reflected in the proposed programme budget for the biennium 2004 - 2005 with the allocation of adequate resources for its expanded mandate;

[... the TARGET BLOCK appears here ...]

31. Requests the Secretary-General to implement regulation 5.6 and rule 105.6 of the Regulations and Rules Governing Programme Planning, the Programme Aspects of the Budget, the Monitoring of Implementation and the Methods of Evaluation;
32. Takes note of the proposal of the Secretary-General, contained in action 21 of his report,3 for a shorter, more strategic medium-term plan that is linked to the budget outline, and requests the Secretary-General to submit a more detailed proposal to the General Assembly, through the Advisory Committee on Administrative and Budgetary Questions, for consideration at its fifty-eighth session;
33. Reaffirms the roles of the Fifth Committee of the General Assembly, the Committee for Programme and Coordination and the Advisory Committee on Administrative and Budgetary Questions in the intergovernmental consideration of the planning, programming and budgeting process;
34. Invites the Committee for Programme and Coordination to continue to improve its working methods;

35. Takes note of the request of the Secretary-General for a degree of flexibility to reallocate resources between programmes and between allocations for personnel and other allocations within a single budget period and in exceptional circumstances, notes the relevant General Assembly resolutions, and in this regard requests the Secretary-General to develop criteria for the use of any such authorization, proposed modalities for reporting the duration and programmatic impacts of reallocations, including specification of the exceptional circumstances in which it would be used, and to report thereon to the Assembly, through the Advisory Committee on Administrative and Budgetary Questions, for its consideration at its fifty-eighth session;
36. Welcomes the efforts of the Secretary-General to strengthen the system of evaluation and monitoring that underlines the importance of assessing programme impacts;
37. Notes the proposal of the Secretary-General for a single-stage intergovernmental review of the programme budget and medium-term plan, contained in action 22 of his report,3 and requests the Secretary-General to submit a report clarifying his proposal for consideration by the General Assembly at its resumed fifty-seventh session;

38. Shares the vision of the Secretary-General to foster excellence among United Nations staff, inter alia, by rejuvenation, while ensuring the highest standards of efficiency, competence and integrity, as well as equitable geographical representation and gender balance;
39. Requests the Secretary-General to submit, as soon as possible, but not later than at the fifty-ninth session of the General Assembly, for consideration in the context of human resources management, a study on ways to promote General Service staff to Professional posts, analysing the effects on non-represented and underrepresented countries, while ensuring the implementation of equitable geographic representation and aligning the procedures and qualifications of the General Service to Professional category examinations to those of the national competitive recruitment examinations;
40. Welcomes the intention of the Secretary-General, as set out in action 32 of his report,3 to continue to improve management, and requests the Secretary-General to continue to improve accountability and responsibility as well as monitoring and control mechanisms and procedures;
41. Requests the Secretary-General to submit a progress report on the implementation of the reform measures as considered in the present resolution to the General Assembly at its fifty-eighth session. 79th plenary meeting

Candidate 0:
  Question: What institutional character should the panel’s terms of reference underscore under the 2002 General Assembly resolution on strengthening the United Nations?
  Answer: the intergovernmental character of the United Nations

Candidate 1:
  Question: Which earlier General Assembly resolutions was creation of the partnership office subject to under the 2002 General Assembly resolution on strengthening the United Nations?
  Answer: resolutions 55/215 of 21 December 2000 and 56/76 of 11 December 2001
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
    "reason": "The answer is a verbatim short span from paragraph 27 of the target block, with no extra words. The '2002' in the question is metadata-level disambiguation and does not affect the answer."
  },
  {
    "index": 1,
    "grounding": 5,
    "precision": 5,
    "numerical_fidelity": 5,
    "reason": "The answer copies the resolution numbers and dates exactly from paragraph 28 as a single contiguous span, with nothing added."
  }
]
````

### Recorded usage

````json
{
  "cached_tokens": 0,
  "completion_tokens": 214,
  "prompt_tokens": 8985,
  "provider_cost": 0.02011,
  "reasoning_tokens": 0
}
````

### Input size diagnostics

````json
{
  "input_characters": 27972,
  "context_capacity_exceeded": null
}
````

## Call 010: faithfulness

Request: `2a02923c69204efe96c46309f82a7047`. Task: `mode/un/2007/gc_12/c_1/sr_1#10/practitioner`.

Model: `anthropic/claude-sonnet-5.5`. UTC: 2026-09-30T18:30:21.409978+00:00.

API status: **response**. Duration: 3.227837 seconds.

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

[EN] Document: GC.12/C.1/SR.1
  Title: General Conference
"9. The emergence of Aid for Trade, to assist least developed countries in developing their trade-related productive capacity and for meeting other trade-related needs, is a landmark development.
The Enhanced Integrated Framework is a promising tool for analysis and identification of needs in the area of trade capacity-building, and for implementation of projects identified.
"10. UNIDO's core mandate is to support industrial development, including in least developed countries.
Aid for Trade and the Enhanced Integrated Framework emphasize development of supply capacity and trade-related infrastructure.
We call upon UNIDO to work closely with countries engaged in the Framework process and, wherever possible, to act as an implementing agency, particularly concentrating in developing industrial capacity and standards and conformity related infrastructure.
"11. In enhancing productive capacity, donors should also utilize the services of UNIDO.
We call upon UNIDO to create a special Trust Fund for least developed countries, and urge donors to contribute generously to the Fund.

### REFERENCED DOCUMENTS — none. The target block cites no other document available in the corpus.

### DOCUMENT CONTEXT — surrounding text of the SAME document, supporting context only. It resolves what the target block leaves implicit; it is never a source of answers.

[EN] Document GC.12/C.1/SR.1 — surrounding passages
General Conference
Twelfth session
Main Committee
Summary record of the 1st meeting
Held at the Austria Center Vienna on Tuesday, 4 December 2007, at 10.30 a.m.
Chair: Mr. Lundby .(Norway)

Agenda item
Organization of work
Election of officers
Financial matters
Programme and budgets, 2008-2009
Strategic Approach to International Chemicals Management
UNIDO Staff Pension Committee
Financial matters (continued)
Medium-term programme framework, 2008-2011

The Chair said that the Committee would be discussing items 7-18 of the Conference agenda.
A set of other texts had been circulated informally without a symbol; they consisted of various proposals that had been submitted and would need to be considered by the Committee.
He requested delegates not to make statements of principle and only to comment on the specific texts under consideration by the Committee.
Mr. Mogadingwane (South Africa), speaking on behalf of the African Group, nominated Mr. Gumbi (South Africa).
Mr. Idris (Indonesia), speaking on behalf of the Asian Group, nominated Mr. Shaghaghi (Islamic Republic of Iran).
Mr. Gumbi (South Africa), Mr. Shaghaghi (Islamic Republic of Iran), Mrs. Noriega Urizar (Guatemala) and Ms. Brdovčak (Croatia) were elected Vice-Chairs of the Committee by acclamation.
(GC.12/4; GC.12/CRP.3; IDB.33/3)
The draft decision on agenda item 10 (a) in document GC.12/CRP.3 was adopted for recommendation to the plenary.
The Chair invited comments on the draft decision on item 10 (c) contained in document GC.12/CRP.3.

The draft decision on item 10 (c) in document GC.12/CRP.3 was adopted for recommendation to the plenary.
The Chair invited comments on the draft decision on item 10 (d) contained in document GC.12/CRP.3.
The draft decision on item 10 (d) in document GC.12/CRP.3 was adopted for recommendation to the plenary.
(GC.12/4, GC.12/8; GC.12/CRP.3)
The Chair invited comments on the draft decision on agenda item 13 contained in document GC.12/CRP.3.
The draft decision on item 13 in document GC.12/CRP.3 was adopted for recommendation to the plenary. Strategic Approach to International Chemicals Management (GC.12/4; GC.12/CRP.3; IDB.33/20)
The Chair invited comments on the draft decision on item 15 contained in document GC.12/CRP.3.
The draft decision on item 15 in document GC.12/CRP.3 was adopted for recommendation to the plenary.
UNIDO Staff Pension Committee (GC.12/CRP.3; IDB.33/Dec.8)
The Chair said he understood that it was proposed that the alternate member of the Staff Pension Committee whose name had been left blank in the draft decision on item 16 in document GC.12/CRP.3 should be Mr. Bilal Kabalan (Lebanon).

On that understanding, the draft decision on item 16 in document GC.12/CRP.3 was adopted for recommendation to the plenary.
The Chair said it had come to his attention that there was some interest in addressing once again the matter of unencumbered balances of appropriations.
Taking into account experience at previous sessions, he suggested that the matter should be postponed pending the preparation, in consultation with the Secretariat, of a possible text on unencumbered balances of appropriations to be combined with the text on item 10 (b) in document GC.12/CRP.3 and submitted to the Committee as a draft of the Chair.
It was so agreed.
The Chair invited comments on the draft decision on the restoration of the voting rights of Costa Rica suggested in paragraph 4 of document GC.12/14.
The draft decision was adopted for recommendation to the plenary.
The Chair invited comments on the draft decision contained in chapter II.B of document GC.12/CRP.3, entitled "Payment plan and request for restoration of voting rights - Moldova".

(IDB.32/8 and Add.1)
The Chair drew attention to the following draft resolution submitted by the Ministerial Conference of the Least Developed Countries (LDCs), held at Vienna on 29 and 30 November 2007, and contained in the set of texts circulated without a symbol:
"The General Conference,
"Taking note of the Ministerial Conference of the Least Developed Countries convened in Vienna on 29 and 30 November 2007,
"Also taking note of the Vienna Ministerial Declaration of the Least Developed Countries adopted by the Ministerial Conference and contained in the annex to the present resolution,
"Invites the Director-General, in implementing the medium-term programme framework, 2008-2011, to take special account of the needs of the least developed countries.
"Annex
"We, the Ministers and Heads of Delegation of the least developed countries participating in the Ministerial Conference held in Vienna, Austria on 2930 November 2007, reiterating our commitment to strengthen the role of the United Nations Industrial Development Organization in promoting the industrial development of the least developed countries as a means to accelerate their development and integration into the multilateral trading system, particularly in the context of the new opportunities being created by aid for trade and the Enhanced Integrated Framework,

"Recalling the Declaration and Programme of Action for the Least Developed Countries for the Decade 2001-2010, adopted in Brussels in 2001,
"Appreciating the particular focus by UNIDO, within its mandate, on two essential commitments of the Brussels Programme of Action:
"`Commitment 4: Building productive capacities to make globalization work for LDCs;
"`Commitment 5: Enhancing the role of trade in development'".
"Being aware of the importance that foreign trade can play in the industrialization and economic development of a least developed country, and also aware that trade is an opportunity and not a guarantee, and therefore requires policy intervention to be successful,
"Recalling that within the framework of the Millennium Development Goal (MDG) 8, Indicator 40 is aimed at increasing the proportion of Official Development Assistance provided to help build trade capacity,
"Recalling also that the Sixth World Trade Organization Ministerial Conference, held in Hong Kong in 2005, called for the expansion of Aid For Trade to help developing countries, particularly least developed countries, to benefit from WTO agreements, expand their trade and enhance their ability to take full advantage of new trade opportunities,

"Recognizing that new opportunities are being created by Aid For Trade and the Enhanced Integrated Framework,
"Deeply appreciating the efforts of the United Nations Industrial Development Organization to assist the least developed countries to take the path to sustainable economic development, using manufacturing as a dynamic force, and to export more value added products complying with international standards,
"Declare that:
"1. The Millennium Development Goals, as well as the other internationally agreed development goals, can most effectively be achieved in the least developed countries through a process that also emphasizes industrial growth, diversification and export of manufactured products.
"3. The commitments made in the 2005 World Summit to address the special needs of the least developed countries should be implemented fully.
In this regard, all countries, the United Nations system, the Bretton Woods institutions and other organizations should make concerted efforts and adopt speedy measures to meet in a timely manner the goals and targets of the Brussels Programme of Action and the World Summit.

"4. The beneficial and meaningful integration of the least developed countries into the multilateral trading system is an important objective of the Doha Development Agenda and the 2005 Sixth Ministerial Conference of the World Trade Organization.
It is vital that the LDCs be able to enter the global value chains with manufactured products and processed foods, apart from other contributions in services, with the aid of targeted technical assistance from UNIDO.
"5. In order to enable the least developed countries to benefit from the opportunities of the multilateral trading system, their manufacturing supply-side needs must be addressed. This requires the enhancement of their productive capacity, as stated in Commitment 4 of the Brussels Programme of Action. This will enable the least developed countries to enhance the role of trade in their development (Commitment 5).
"6. Considering the limited opportunities available to least developed countries, we call upon UNIDO to play a pioneering role in developing industrial productive capacity in those countries in a manner that ensures that products conform to acceptable international standards.

Depending on the needs of specific LDCs this may, inter alia, entail efforts to develop entrepreneurship, creating an enabling business environment, developing domestic research capacity, investment facilitation, development of agro business, along with delivery of targeted technical assistance and capacity-building for developing standards, testing, certification and accreditation capabilities accepted in international markets, and integration of the local with the global value chains, lending support in finding markets.
"7. Given the increasing importance of the South as a destination for least developed country exports and the potential for these countries to benefit from their increasing collaboration with the South, UNIDO should promote mutually beneficial least developed countries-South cooperation in areas within its mandate.
"8. UNIDO should help least developed countries with commodity-specific interventions, wherever required by those countries, including in the development of technology, enhancing research, moving up the value chain and improving the welfare of those employed in, or dependent on, those commodities in the least developed countries.
This is particularly needed for cotton.

[... the TARGET BLOCK appears here ...]

"12. UNIDO is hosting an LDC Ministerial Conference after more than a decade.
"The Ministers and Heads of Delegation of the least developed countries are deeply grateful to UNIDO for hosting the Ministerial Conference and for the excellent arrangements made for it.
We thank the G-77 and China for co-sponsoring this event.
Mr. Nyaphisi (Lesotho), supported by Ms. Espinoza Patiño (Bolivia), introducing the draft resolution, said that it represented the outcome of the Ministerial Conference.
Since 90 per cent of world trade was in manufactured goods, the real, sustained benefits could come only from the export of such goods.
The LDCs were primarily raw material and primary commodity exporters, and while their share of world exports had been more than 3 per cent in the 1960s it had now dwindled to about 0.5 per cent.
Unless some remedial action was taken, their fate would be uncertain.
The world community had recognized the problem, and the "Aid for Trade" programme had been launched.
Many countries and groups had offered help under the programme, but the only organization of the United Nations system to deal with productive capacity enhancement was UNIDO, and the LDCs had been delighted that the Organization had taken the initiative to convene the Ministerial Conference.

At its conclusion, ministers had adopted a Ministerial Declaration which outlined what they would like UNIDO to do with its mandate.
The LDCs hoped that the draft resolution submitted by them would be endorsed by the Committee and adopted unanimously by the Conference.
The draft resolution submitted by the Ministerial Conference of the LDCs was adopted for recommendation to the plenary.
Mrs. Noriega Urizar (Guatemala) introduced the following draft resolution submitted by the Group of 77 and China entitled "Regional programme for Latin America and the Caribbean": "The General Conference:
"Recalling resolution GC.11/Res.1, entitled "Regional programme for Latin America and the Caribbean", in which the Director-General was requested to establish a regional programme for Latin America and the Caribbean,
"Recognizing the joint work that has been carried out to date by Member States and the Secretariat with the aim of defining that regional programme and, in particular, the conclusions set out in the final document of the Latin America and the Caribbean Second Expert Group Meeting, held in Vienna in November 2007,

"Considering that resolution GC.11/Res.1 requested inter alia the Secretariat of UNIDO to identify and mobilize financial resources which would permit the implementation of the regional programme for Latin America and the Caribbean,
"Requests the Director-General:
"(a) To adopt the necessary measures so that the activities in execution of the regional programme for Latin America and the Caribbean are duly reflected in the medium-term programme framework, 2008-2011, in order to sustain the work initiated;
"(b) To continue his efforts, in consultation with the Member States of the region, to identify and mobilize further financial resources required for its full implementation, at the same time calling upon the international community to provide financial support to the programme;
She said that, following the adoption of resolution GC.11/Res.1 in 2005, the first steps had been taken to set up a regional programme for Latin America and the Caribbean; UNIDO had assisted the region in establishing a strategy and defining priorities.
The proposed draft resolution was intended to provide continuity and to ensure that the programme activities were reflected in the medium-term programme framework, 2008-2011.

In the second preambular paragraph, the term "approved document" might be preferable to "final document".
In operative paragraph (b), the words "and mobilize further financial resources" might be amended to read "and mobilize additional voluntary resources ...".
Mr. Roselló (Spain), speaking on behalf of the Western European and Others Group, suggested that in the second preambular paragraph, "adopted" might be used instead of "approved".
The exact dates of the Second Expert Group Meeting mentioned in the same paragraph might also be added.
Mrs. Noriega Urizar (Guatemala) agreed.
The exact dates of the Second Expert Group Meeting were 28-30 November 2007.
The Chair said that, if he heard no objection, he would take it that the second preambular paragraph and operative paragraph (b) should be amended as proposed.
Mr. Quesada (Mexico) wondered whether the word "additional" should be added before the words "financial resources" in the second line of the third preambular paragraph to make the text consistent with operative paragraph (b).

The Chair noted that the General Conference resolution referred to in the third preambular paragraph did not in fact contain the word "additional".
Mr. Duarte (Portugal) thought that it would be better in that case to leave the text as it stood.
Mr. Quesada (Mexico) agreed.
The draft resolution entitled "Regional programme for Latin America and the Caribbean", as amended, was adopted for recommendation to the plenary.
Mr. Duarte (Portugal), speaking on behalf of the European Union, introduced the following draft resolution entitled "Results-based management":
"Welcoming the introduction of results-based management principles and practices at UNIDO,
"Further welcoming the establishment of the Results-based Management Steering Committee at UNIDO to carry out a base-line self-assessment of the status of results-based management implementation in UNIDO, draft a conceptual framework for further development of results-based management in the Organization, and define a time-bound results-based management implementation strategy with milestones,
"Cognizant of the need to further refine and harmonize results-based management within the United Nations system,

"(a) To continue to give priority to the comprehensive adoption of results-based management principles by UNIDO, and the full integration of results-based management approaches methods in all spheres of its activities;
"(b) To continue to provide the governing bodies with regular updates on the implementation of results-based management in UNIDO;
He said that the European Union welcomed the fact that UNIDO had established a sound basis for the implementation of results-based management principles and practices in all spheres of its activities and wished to encourage the Organization to continue to give priority to their implementation and provide updates thereon.
The draft resolution was also sponsored by Croatia, Norway, Serbia and Turkey.
Mr. Bougacha (Tunisia) welcomed the draft resolution but thought that it might be better to delete the reference in the first preambular paragraph to an informal document which might not have been translated into all the official languages.
He also questioned the appropriateness in a resolution concerned with UNIDO of speaking of harmonizing work "within the United Nations system".

Mr. Duarte (Portugal) said that he could accept the deletion of the reference in the first preambular paragraph, which would not affect the substance of the draft resolution.
The Chair said he took it that it was agreed to delete the documentary reference in the first preambular paragraph.
Mr. Duarte (Portugal), referring to the question of harmonization within the United Nations system, said that it seemed important to stress the involvement of UNIDO in the work of the wider United Nations system, ensuring coherence with other agencies, and to mention the need for harmonization with the United Nations system as a whole.
Mr. Bougacha (Tunisia) said that, while the United Nations system certainly needed to continue to strengthen results-based management, UNIDO should focus on development and not on strengthening results-based management within the United Nations system.
He could accept the reference to the United Nations system in the fourth preambular paragraph, but would prefer to see operative paragraph (c) deleted.

Ms. Permanyer (Cuba) supported the remarks of the representative of Tunisia, believing that the draft should confine itself to results-based management in UNIDO.
Mr. Duarte (Portugal) thought that the intention of operative paragraph (c) might be made clearer by amending the phrase "harmonize the approach" to read "harmonize its approach".
Mr. Kim Sung-hwan (Republic of Korea) supported that suggestion.
However, it was a good idea to set the topic within the wider perspective of the United Nations system and to urge UNIDO to continue to work with other organizations.
Mr. Bougacha (Tunisia) agreed with the suggestion to change "the" to "its" but said he would still prefer the deletion of the phrase "within the United Nations system" at the end of operative paragraph (c).
Ms. Leucuta (Romania) suggested that the phrase "within the United Nations system" be moved from the end of the paragraph to after the words "with other organizations", to make the meaning still clearer.
The draft resolution entitled "Results-based management", as amended, was adopted for recommendation to the plenary.

Candidate 0:
  Question: In December 2007, what did UNIDO's core mandate cover in least developed countries?
  Answer: support industrial development

Candidate 1:
  Question: In December 2007, what infrastructure did Aid for Trade and the Enhanced Integrated Framework emphasize?
  Answer: trade-related infrastructure
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
    "reason": "The target says the core mandate is to support industrial development, including in LDCs, so the answer is directly supported; the 'December 2007' framing is a minor metadata-based addition, and the answer omits the LDC clause."
  },
  {
    "index": 1,
    "grounding": 3,
    "precision": 3,
    "numerical_fidelity": 5,
    "reason": "The text says they emphasize 'development of supply capacity and trade-related infrastructure'; the answer is a correct fragment but is slightly incomplete, because supply capacity is left out, and the question's 'what infrastructure' wording is imprecise."
  }
]
````

### Recorded usage

````json
{
  "cached_tokens": 0,
  "completion_tokens": 263,
  "prompt_tokens": 9805,
  "provider_cost": 0.02224,
  "reasoning_tokens": 0
}
````

### Input size diagnostics

````json
{
  "input_characters": 29067,
  "context_capacity_exceeded": null
}
````

## Call 011: faithfulness

Request: `4cef9d06ef76442f9e01aa9e2db0ade8`. Task: `mode/un/1999/cedaw/c/sr_434#16/practitioner`.

Model: `anthropic/claude-sonnet-5.5`. UTC: 2026-09-30T18:31:33.097931+00:00.

API status: **response**. Duration: 4.049069 seconds.

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

[EN] Document: CEDAW/C/SR.434
  Title: Committee on the Elimination of Discrimination against Women
She would also like to know why the 1997 Human Rights Commission Act had not been implemented; whether the Government had developed any gender management plan and, if so, how the various institutions would coordinate action under the plan; and would appreciate a specific breakdown of the budget for women's issues.
27. Poverty alleviation had to be the main goal, but if women were not brought into the process, it would not happen.
Although no Nepalese woman had yet done so, the option of appealing for international redress under the Optional Protocol to the International Covenant on Civil and Political Rights, after the exhaustion of domestic remedies -- and soon under an Optional Protocol to the Convention -- was a distinct possibility unless the Government acted quickly to remedy the situation of women in the country.
Article 5
She asked how the Government planned to convey a serious message that it intended to enforce the prohibitions.

### REFERENCED DOCUMENTS — none. The target block cites no other document available in the corpus.

### DOCUMENT CONTEXT — surrounding text of the SAME document, supporting context only. It resolves what the target block leaves implicit; it is never a source of answers.

[EN] Document CEDAW/C/SR.434 — surrounding passages
Committee on the Elimination of Discrimination against Women
Twenty-first session
Summary record of the 434th meeting
Held at Headquarters, New York, on Tuesday, 15 June 1999, at 10 a.m.
Chairperson: Ms. Ouedraogo (Vice-Chairperson)

Initial report of Nepal

Initial report of Nepal (CEDAW/C/NPL/1)
1. At the invitation of the Chairperson, Mr. Shakya (Nepal) took a place at the Committee table.
2. Mr. Shakya (Nepal), introducing the initial report of Nepal (CEDAW/C/NPL/1), said that Nepal had recently become party to a number of international human rights instruments, including the Convention on the Elimination of All Forms of Discrimination against Women (CEDAW).
He was also pleased to report that, with the adoption of the new Constitution in 1990, the death penalty had been completely abolished.
But poverty was a major obstacle to the implementation of many international instruments: an estimated fifty per cent of the people of Nepal lived in absolute poverty, with urban poverty increasing swiftly over the past decade.
The Government believed that human rights should be an integral part of all poverty alleviation strategies and efforts.
3. On the eve of the twenty-first century, Nepalese women were still suppressed, exploited, neglected and had little security because of illiteracy, poverty, tradition and a discriminatory legal system.
Since women constituted just over half the population, their development contributed to the country's overall development.
Thus, a "women in development" approach had been national policy since the sixth five-year development plan.

In the eighth plan, several policies had been adopted to involve women in the development mainstream in order to ensure their participation in every sector, improve their social, economic, educational, political and legal status, increase capacity by providing skills for employment generation and create an appropriate environment for access to decision-making from the national to the local level.
In accordance with the commitments made at the Fourth World Conference on Women in Beijing, a National Work Plan for Gender Equality and Women's Empowerment had been formulated and the Ministry of Women and Social Welfare established.
4. Challenges to be met in improving the status of women included a legal and social system which denied them access to property, employment and other economic resources.
Because of their low educational level, women were still denied access to political and administrative decision-making.
The maternal mortality rate of 53.9 per 10,000 live births was very high, and contributed to the lower life expectancy for women than for men.
Women's literacy was only 30 per cent compared to 66 per cent for men.

5. The ninth five-year development plan targeted women to achieve its overall aim of poverty alleviation and human resources development. Its implementation strategies and policies would involve women in the national development mainstream.
Women's contributions to household labour would be evaluated and incorporated into the national accounting system.
The existing institutional structure would be strengthened and appropriate gender disaggregated indicators would be developed for monitoring and evaluation.
In order to eliminate gender inequalities, a review of legislation would be conducted to remove discriminatory laws, and existing discrimination would gradually be reduced with the adoption of positive policies and programmes.
Governmental and non-governmental organizations and local bodies would be mobilized to combat violence against women through prevention and rehabilitation.
6. The National Work Plan for Gender Equity and Women's Empowerment encompassed 11 sectors requiring serious attention: poverty, education, health, violence, armed insurgency, economy, policy-making, institutional structure, human rights, the environment and children.
A number of programmes in those sectors would be implemented in the context of the ninth development plan.
In the education sector, the goal was to increase women's literacy to 67 per cent and the proportion of women teachers and participants in vocational training to 50 per cent.
In the health sector, programmes would emphasize safe motherhood and care of elderly women.

The family planning programme would also be expanded significantly.
To increase women's productivity in agriculture, programmes to ensure their access to production technology and credit were planned.
Programmes to increase women's entry into the economy would emphasize microcredit schemes and training.
In the legal sector, a family court would be established, and legal provisions made to reduce the economic disparities between men and women.
The legal approach to preventing violence against women would be reviewed and strengthened as well.
To raise consciousness about gender equality at the political, administrative and local levels, training seminars and publicity campaigns would be carried out.
7. The issue of trafficking in women and girls and prostitution was becoming more serious.
In response, a "self-reliance and rehabilitation home" had been established to provide a residential six-month job skills training programme for women engaged in prostitution. It would also provide rehabilitation services for victims of trafficking.
The Ministry of Women and Social Welfare had formed a national coordination committee to coordinate all programmes being implemented by Government agencies in order to avoid duplication and provide effective monitoring and evaluation.
Secretaries of the main ministries were members of the committee.
It had also formulated a National Plan of Action as a follow-up to the Beijing Platform for Action.

8. The Ministry had formed a task force to review all laws which discriminated against women and recommended amendments to those laws to the Ministry of Law and Justice.
Women were still under-represented in the country's civil service, making up less than 8 per cent of the total workforce, and only 3 per cent of the highest employment grades.
9. Referring to the participation of women in the political process, he noted that in the May 1999 general election, 13 out of 142 women candidates had been elected to the House of Representatives.
That figure was double the total of the previous election.
His delegation would welcome any suggestions by members of the Committee on how to improve its subsequent periodic reports and the status of women in Nepal in general.
10. The Chairperson congratulated the Government of Nepal for having ratified the Convention without any reservations and for its efforts to promote equality of opportunities for both men and women.
She commended the delegation for the objectivity and frankness of its report.
The report had complied with the guidelines of the Committee and that would not only facilitate its assessment but would also favour constructive dialogue.

General comments
11. Ms. Taya hailed Nepal's efforts to strengthen democracy since 1990, particularly its effort to improve girls' education and promote grass-roots democracy.
12. Ms. Abaka said that the equal rights laws were not being enforced.
She was particularly concerned about the trafficking in children for commercial sexual exploitation and child labour, despite legislation dating as far back as 1950.
The relevant penal provisions should be strictly enforced.
Fourteen-year-old children, who were at particularly high risk, must be adequately protected by the Government.
She was also concerned that women's reproductive health rights were not being recognized as a basic human right.
13. Ms. Corti said that she would have preferred to have had the report introduced by a woman, since, when it came to their own rights and realities, women were more sensitive.
Noting the considerable number of ethnic groups, languages and religions in Nepal, she wondered how difficult it would be for the Government to develop a policy that enjoyed the support of such a diverse population.
In her view, maintaining the cultures of different groups could sometimes be an obstacle to the advancement of women and equality.
State mechanisms in Nepal seemed to be controlled by patriarchal norms, beliefs and values, resulting in a very low status of women.

In that regard, she enquired whether the Minister for Women and Social Welfare was a woman or a man.
She also wondered who had prepared Nepal's report and to what extent non-governmental organizations had been involved in its preparation.
14. Patriarchal values dominated laws in Nepal.
For example, a single mother could not register the birth of her child, and women were discriminated against under the adoption law.
Indeed, the so-called son preference was very deeply rooted in Nepal and its legislation.
The very high rate of prostitution, especially among girl children, together with the lack of any explicit measures to stamp out that criminal phenomenon, demonstrated a lack of political will to overcome discrimination against women.
Moreover, as the recent figures for parliamentary elections showed, women's political participation was virtually non-existent.
Patriarchal attitudes and norms appeared to be the main obstacles to the advancement of women in Nepal and to implementing Nepal's commitments under the Convention. Very little was being done to eliminate stereotypes.

15. Ms. Aouij said that, while Nepal had abolished the death penalty, it still criminalized abortion, which killed women daily and denied them their right to life -- a fundamental right.
Indeed, abortion-related complications were the main cause of the maternal mortality rate of 1,500 per 100,000 births, the highest in south Asia. That was also the reason for the lower life expectancy of women.
Even under the bill before Parliament which sought to revise existing laws abortion would be legal only for married women, with the consent of their husbands, which meant that women still did not have control over their own bodies.
The bill needed to be revised and adopted as soon as possible by Parliament, because the progress of women and their health were linked directly to the development of the country and its well-being.
Articles 1 and 2
She also wished to know what actions had been taken by the Government to amend the apparent discriminatory laws, such as those on marriage and bigamy, besides submitting the bill to Parliament.

17. Ms. Cartwright said that, while she welcomed the ratification of the Convention by the Government of Nepal without reservations, compliance with its provisions was a much more difficult task.
Nepal had considerable problems concerning poverty and health, and there was an enormous gap between law and practice.
There was great significance in ensuring that laws were not only promulgated but enforced, since that would demonstrate that the Government would not discriminate against any of its citizens.
18. There was an urgent need to amend legislation to ensure that women had the same right to inherit property as men did.
She was seriously concerned that while the Supreme Court had wide powers to direct the amendment of legislation and policy, the House of Representatives had introduced a bill which had been allowed to lapse.
She was equally concerned that, although the court had taken action on the inheritance laws, it had nonetheless asked the House of Representatives to ensure that men were not discriminated against.
The Supreme Court's comments and the inaction of the House of Representatives demonstrated deep-seated and damaging discrimination against women.
The Nepalese Government had firmly indicated that it wanted to bring women into the development process equally with men.

If the Government was serious about ensuring women's participation in development, then women had to have access to land and other assets on the same basis as men.
19. As for other laws needing amendment or implementation, the marriage laws should establish the same marriageable age for women as for men.
She drew attention to the Committee's general recommendation No. 21 setting out the reasons why both spouses should attain the age of 18 before marriage, among them physical maturity and the ability to shoulder adult responsibilities.
In any case, the marriage of children under 16 -- a serious infringement of their bodily integrity and their right to a childhood -- must be prohibited and punished severely.
The laws of nationality should be amended to allow the children of naturalized women as well as men to obtain citizenship.
The Government should also amend the divorce laws to allow equal access to divorce and should do away with dowry payments, which fostered discrimination.

20. The criminal law also needed broad revision to ensure equal treatment.
Apparently there was no law on violence against women, a major problem.
The Committee's general recommendation No. 19 and the General Assembly Declaration on the Elimination of Violence against Women provided useful definitions that could be starting points for legislation and policy.
Lastly, the Government should be applauded for the preliminary steps that it had taken to stem trafficking in women, another serious problem in Nepal.
21. Ms. Shalev said that the situation of women in Nepal was distressing.
In facing the formidable tasks before it, the first and easiest step for the Government would be to adopt legal measures.
The poverty and the cultural or social stereotyping were indeed daunting, but it was in the hands of the Government to legislate with regard to the family.
Thus, it should amend as soon as possible the discriminatory provisions in the divorce laws which denied custody of children to the mother after divorce.
Abortion must also be immediately given legal status for, as indicated in the Committee's general recommendation No. 24 on women and health, it was discriminatory for a State party to refuse to legally provide for the performance of certain reproductive health services for women.

The report (paras. 45 and 50) indicated that the Supreme Court had the right -- which it had on occasion exercised -- to abrogate, under extraordinary powers of judicial review, any law that unreasonably restricted the enjoyment of fundamental rights.
She wondered if the Government was planning to avail itself of that existing procedure.
23. Ms. Khan commended Nepal for being one of the few south Asian States to have ratified all the major human rights instruments and incorporated the Convention into its domestic legislation.
The Government was clearly aware of its obligations, in view of the constitutional provisions outlined in the report (paras. 34 et seq.). Nevertheless, as Ms. Cartwright had pointed out, it was very disappointing that there were so many discriminatory laws in effect that restricted women in so many spheres.
With regard to the inheritance laws, complex social and legal mechanisms reinforced each other to deprive women of their rights.
Poverty, a lack of social awareness and deep-rooted prejudices were at the heart of the problem.
Yet how could the Government raise social awareness if it countenanced discrimination by not putting anti-discrimination laws in place?
Public authorities must be the first to act if social and behavioural patterns were to change.

She therefore would like to know what action the Government had taken to abolish laws that violated both the Convention and article 11 of Nepal's Constitution; and also whether there was any likelihood of the early reintroduction and adoption of the bill establishing the inheritance rights of daughters (addendum to report, p. 18).
24. Ms. Acar said that de jure equality, though not sufficient in itself, was the fundamental to any further progress.
The Government must therefore act immediately to nullify laws contrary to the Convention and the Constitution.
She was disturbed by the Government's resigned attitude betrayed in the statement in the addendum to the report (p. 4, para. 2) that from a long-term perspective, it could be visualized that Nepal could be one of the countries giving more value to sons rather than daughters, unless political, administrative, socio-economic and legal affirmative policies were formulated and implemented.
Especially in patriarchal, authoritarian societies, where political action was an effective tool, bold, radical steps had to be taken.
Egalitarian juridical policies had to precede affirmative action.
A recent Supreme Court directive for the immediate adoption of remedial legislation had been thwarted in Parliament, and it would be interesting to know what the Government intended to do to deal with that situation, and to take more urgent action in general.

Article 3
25. Ms. Goonesekere said that she agreed with Ms. Cartwright that the Government had an obligation to make a comprehensive effort to achieve equality for women.
Nepal stood out in south Asia as a country in which the people's power had led to the creation of a democratic Government, and therefore its people's expectations were correspondingly high.
Yet there was a contradictory situation which the laws were at odds with and a Constitution proclaiming equality and international human rights norms. The promise of democratization had not yet reached the women in Nepal.
The Government should set goals and target dates for the advancement of women and identify the indicators of progress.
26. She would like to know if the Government had in fact done so, and also if it had any long-term plan and target dates for law reform, which had to be done consistently, across the board.
How, for instance, was the Government planning to enforce the Supreme Court order for the adoption of non-discriminatory inheritance laws, which Parliament had failed to pass? The issue had to be addressed, because a government was seriously undermined when judicial decisions were not followed by executive and legislative action.

[... the TARGET BLOCK appears here ...]

29. Regarding the grounds for the dissolution of marriage and the statement in the report (para. 62 (ii)) that a woman could not obtain a divorce if she simply found that marriage was detrimental to her person, mentally, physically or emotionally, it should be pointed out that there was nothing innocuous about gender-based violence.
Such abuse threatened the very life of a woman.
30. Ms. Ferrer said that the Government would require strong political will to alter the deeply rooted traditions that subjugated Nepalese women, among them such aberrant practices as giving prepubescent children in marriage, marrying girl children to older men, and the tradition of "temple prostitutes".
It would be useful to know whether the Ministry of Education provided training and awareness courses in those matters to teachers, professionals and the general community, and whether it disseminated relevant educational information through the mass media.
31. In several instances, the report cited minor changes to legislation that was clearly discriminatory.
A law which permitted women to divorce their husbands for such actions as keeping another wife or refusing support was described as a provision that freed women from subjugation by their husbands.

But a woman should be free to divorce her husband simply because she no longer loved him. Did the Government envisage a radical revision of legislation in order to guarantee women their rights under the Covenant?
Lastly, it would be useful to know what the incidence of violence against women was in Nepal, how such acts were handled under the law, and what treatment was available to battered women.
32. Ms. Goonesekere said that, regrettably, the report made no reference to the issue of violence against women.
33. Ms. Khan enquired whether the Government had considered reviewing the provisions of the Muluki Ain, which, according to the report, were based on the caste system and a tradition of male domination.
She too regretted that the report contained no reference to domestic violence, which according to non-governmental organizations was widely prevalent. The Muluki Ain condoned polygamy despite the constitutional and legal prohibitions against it.

34. Although the Nepalese tourist industry was booming, the report made no mention of tourism, which exposed women and girls to sexual exploitation. The next report should take up that matter.
It would be useful to know whether the Government had a comprehensive plan of action to address trafficking in human beings, whether steps had been taken to enforce the relevant provisions of the Muluki Ain, and whether law enforcement personnel were trained to deal with that issue.
She would like to know whether Nepal had engaged in any regional cooperation efforts with a view to implementing the Convention for the Suppression of the Traffic in Persons and of the Exploitation of the Prostitution of Others, and whether it intended immediately to ratify the convention on the suppression of prostitution recently concluded by the South Asian Association for Regional Cooperation (SAARC).
It would also be useful to know the principal features of the plan of action to combat trafficking in women and children, what recommendations had been put forward by the national task force, and whether any mechanisms had been established to eliminate that scourge.

35. Likewise unmentioned in the report was the vast diversity of ethnic groups living in Nepal.
The Terai women of Southern Nepal were not only bonded labourers, but also considered the sexual property of landowners.
Their children became bonded at birth, and the system of exploitation thus passed from generation to generation.
Dalit women, who belonged to the lowest caste, were not only extremely poor, but also dominated by the higher castes.
Although the national female literacy rate was 25 per cent, among Dalits it was only 4 per cent.
The national contraception prevalence rate was 30 per cent; among Dalits it was 7.
36. Maternal mortality was much higher among Dalits than among other Nepalese women.
Their extreme social and economic isolation precluded any possibility of upward mobility.
It would be useful to know whether the Government planned to enact measures to redress their situation, whether laws had been enacted to prohibit discrimination on the basis of caste, and whether Government officials were subject to punishment for denying mandatory services to persons of a lower caste.

As a person from a traditional culture, she profoundly believed that the only way to effect change was to challenge those justifications.
But it must, above all, honour its commitment to establishing the rights of women.
Article 6
38. Ms. Taya observed that the Ministry of Women and Social Welfare had drafted national plans and policies to combat trafficking in girls, which included, inter alia, alleviating poverty, empowering women, and establishing international cooperation to halt such trafficking. What measures had been taken to implement those plans immediately?
39. Ms. Regazzoli said that although Nepal had endorsed all the major international initiatives designed to combat trafficking in children, very few traffickers had been reported.
It was therefore unclear whether any practical measures had been taken to eliminate that problem.
She enquired whether the Government had arranged to report such incidents to the International Criminal Police Organization (INTERPOL), and whether it had taken measures to facilitate the rehabilitation of children who were rescued and brought home.
In her view, training women to engage in productive work could prove an effective means of combating sexual exploitation of both women and children.

40. Ms. Corti enquired what plans had been made to tackle immediately the alarming phenomenon of the prostitution of Nepalese women.
She would like to know whether the Government had commenced talks with India and other countries regarding trafficking in women and children; whether it had begun the process of reviewing and reforming relevant legislation; whether it envisaged the establishment of centres for the rehabilitation of girls traumatized by prostitution and the payment of compensation to victims; and whether free legal counselling for victims of violence was available.

Candidate 0:
  Question: As of June 1999, had any Nepalese woman yet appealed for international redress under the Optional Protocol?
  Answer: Although no Nepalese woman had yet done so

Candidate 1:
  Question: In June 1999, what condition made international redress a distinct possibility for Nepalese women?
  Answer: unless the Government acted quickly to remedy the situation of women in the country
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
    "reason": "The answer is a verbatim fragment of the target sentence, but the pronoun 'done so' has to be resolved to the appeal; the answer also does not explicitly say 'no' and keeps a dependent-clause opener ('Although')."
  },
  {
    "index": 1,
    "grounding": 4,
    "precision": 4,
    "numerical_fidelity": 5,
    "reason": "The answer is a verbatim span from the target sentence and is well supported, though 'condition' is a slight framing of 'unless' and the clause is left as a fragment; it contains no numerical content."
  }
]
````

### Recorded usage

````json
{
  "cached_tokens": 0,
  "completion_tokens": 252,
  "prompt_tokens": 10912,
  "provider_cost": 0.024344,
  "reasoning_tokens": 0
}
````

### Input size diagnostics

````json
{
  "input_characters": 34425,
  "context_capacity_exceeded": null
}
````

## Call 012: faithfulness

Request: `8d7b156fa8564ce892fdb8a14b65badc`. Task: `mode/un/2000/cd/pv_841#11/practitioner`.

Model: `anthropic/claude-sonnet-5.5`. UTC: 2026-09-30T18:31:33.099609+00:00.

API status: **response**. Duration: 4.304809 seconds.

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

[EN] Document: CD/PV.841
  Title: on Thursday, 10 February 2000, at 10.15 a.m. President: Mr. Harald Kreid (Austria)
In your subsequent consultations, you were to bring forward for consideration a number of options, one of which would have permitted the appointment of special coordinators to deal with the issues of nuclear disarmament and the prevention of an arms race in outer space, while allowing the Conference to agree on a work programme, including the establishment of an ad hoc committee for negotiations on an FMCT.
Five years on, that common objective remains unfulfilled. The importance of an FMCT has not diminished in the intervening period. Indeed, events in the closing years of the last century have underlined its necessity.
In our view, it remains the case that before there can be an effective and verifiable ban on nuclear weapons globally, there must be confidence that no new fissile material for such weapons can be produced.
An FMCT would deliver such an assurance, and in so doing, put in place a vital foundation for the achievement of global nuclear disarmament.

### REFERENCED DOCUMENTS — none. The target block cites no other document available in the corpus.

### DOCUMENT CONTEXT — surrounding text of the SAME document, supporting context only. It resolves what the target block leaves implicit; it is never a source of answers.

[EN] Document CD/PV.841 — surrounding passages
on Thursday, 10 February 2000, at 10.15 a.m. President: Mr. Harald Kreid (Austria)
I have two speakers inscribed on my list today.
I give the floor to the first speaker, who is the Ambassador of Cuba, Ambassador Carlos Amat Fores.
I would also like to thank the secretariat staff and the team of translators and interpreters for the irreplaceable support they give us in accomplishing our work.
We are beginning a new session of the Conference on Disarmament in an international situation that bears no relation to the one which was generated by the most optimistic ideas in the field of disarmament at the beginning of the last decade, ideas which proliferated at the end of the cold war and, following elementary logic, held out, among other things, the possibility of achieving the final and complete elimination of nuclear weapons.
I speak of elementary logic because with the end of the cold war it appeared that the cause of the uncontrolled buildup of nuclear arsenals in the world would disappear.
Though I must confess that in Cuba we always viewed that optimism with some reservations.

Now everything appears clearer.
I could cite other examples which illustrate that dangerous reality, but I prefer to refer to a few of them later.
In the international situation to which I referred earlier, the role of the Conference on Disarmament is increasing.
It is becoming imperative to heed the calls from the international community expressed through the resolutions adopted by the United Nations General Assembly, among other forums.
For several years resolutions have been adopted in that body requesting the Conference to establish an ad hoc committee on the issue of nuclear disarmament.
Last year this Conference was once again asked, in resolution 54/54 P, to establish such a mechanism on a priority basis.
Cuba, as a member of the Group of 21, to which it has the honour to belong, has set out its ideas on the programme of work in documents CD/1570 and CD/1571, which contain the Group's position on the matter.
These proposals are clear and express the will of the Group of 21 to begin negotiations immediately to eliminate for ever the latent danger represented by the possession of nuclear weapons by certain Powers.
Some believe that that position is not realistic, and have even stated that it is out of step with the present.

The General Assembly of the United Nations, in resolution 54/53, entitled "Prevention of the arms race in outer space", which was adopted with the support of almost all the Members of the United Nations, and, even more significantly, without opposition from any of them, also reiterates "that the Conference on Disarmament, as the single multilateral disarmament negotiating forum, has the primary role in the negotiation of a multilateral agreement or agreements, as appropriate, on the prevention of an arms race in outer space in all its aspects", and invites the Conference to reestablish an ad hoc committee for this purpose.
Of course, it is implicit in my analysis that in order to begin any negotiating exercise it is vital that we should all display the necessary political will and spirit of flexibility if we are to achieve the noble objectives and goals that are urged upon us.
Cuba has always advocated nuclear disarmament and the peaceful uses of nuclear energy.
This is why all our programmes for the use of nuclear energy are directed to its peaceful exploitation and are placed under safeguards agreements with IAEA.
This is the expression shown of our country's and our Government's vocation for peace.

Following that vocation, we have recently signed an additional protocol to our safeguards agreements with IAEA, based on the model protocol adopted by that agency.
This represents a concrete contribution to a strengthened, efficient and effective international safeguards regime.
In so doing Cuba became the first country with INFCIRC/66type safeguards agreements to sign a protocol of this nature with IAEA.
We would also like to take this opportunity to refer to other important topics in the field of disarmament and arms control which are currently on the table.
Our country is following those negotiations with great interest and is taking an active part in the work of the Ad Hoc Group.
We appreciate the progress reached in that forum and stand ready to continue contributing to those negotiations in a positive and constructive manner, so that we can conclude a protocol which is universal and effective before the Fifth Review Conference on the Convention, as decided at the previous Conference.

Secondly, while emphasizing that we attach the highest priority to the issue of nuclear disarmament, Cuba shares the concerns related to the illicit traffic in small arms and supports the initiatives that are being pursued at the bilateral, regional and multilateral level in search of negotiated solutions to this phenomenon.
The Preparatory Committee for the conference will begin its work very soon, and my country is preparing to participate actively in its work in the hope of reaching fruitful results.
The PRESIDENT: I thank the representative of Cuba for his statement and for the kind words addressed to the Chair.
I now give the floor to the representative of China, Ambassador Hu Xiaodi.
Mr. HU (China) (translated from Chinese): The Chinese delegation attaches great importance to the prevention of an arms race in outer space, and maintains that the CD should reestablish an ad hoc committee under this agenda item to commence substantive negotiations.
Today, upon the instructions from the Chinese Government, I submit a working paper entitled "China's position on and suggestions for ways to address the issue of prevention of an arms race in outer space at the Conference on Disarmament".
Yesterday, I requested the SecretaryGeneral to circulate it as an official document of the CD.

I shall briefly outline the main elements of the working paper.
There are four parts: our views on how to address the issue of PAROS at the CD, our views on the existing international legal instruments concerning PAROS, China's position on PAROS and tentative ideas on the new international legal instruments.
First, our views on how to address PAROS at the CD.
The fact that no country voted against the resolution amply reflects the common aspiration and strong desire of the international community to prevent an arms race in outer space.
In a related move, the General Assembly last year adopted, again by an overwhelming majority, a resolution on preservation of and compliance with the Treaty on the Limitation of AntiBallistic Missile Systems.
Thus the Chinese delegation maintains that as proposed: in CD/1576, the CD should reestablish an ad hoc committee under agenda item 3, "Prevention of an arms race in outer space", to negotiate and conclude an international legal instrument banning the testing, deployment and use of any weapons, weapon systems and their components in outer space, with a view to preventing the weaponization of outer space.

In carrying out its mandate, the ad hoc committee should take into consideration all relevant present and future developments and specific proposals tabled by all sides.
The Chinese delegation has taken note of the many ideas and suggestions on PAROS put to the Conference by various parties.
We are of the view that the new ad hoc committee should be an open-ended all-embracing mechanism within which all sides can freely express their views.
It should be given the negotiation and conclusion of an international legal instrument or instruments on the prevention of the weaponization of and an arms race in outer space as a clear direction and ultimate goal.
Secondly, the issue of the existing international legal instruments.
However, they have been ineffective in preventing the weaponization of outer space or an arms race in outer space.
Some have provided for limited prohibitions and contain many loopholes and ambiguities. Some have not been fully complied with or risk being violated, amended or abrogated.
Therefore the Chinese delegation believes that the international community, while making efforts to strengthen the existing international legal instruments, also needs to negotiate new international legal instruments to achieve the goal of non-weaponization of and prevention of an arms race in outer space.

The new international legal instrument to be concluded should include as basic elements a ban on the testing, deployment and use of any weapon system or components thereof in outer space, and limits on the use of satellites for military purposes.
Thirdly, China's basic position on PAROS.
As long ago as in 1985, China submitted to the first ad hoc committee on PAROS a position paper (CD/579) which outlined its basic positions in this regard.
This principled position remains unchanged.
We emphasize that the Powers with the greatest space capabilities bear a special responsibility for preventing an arms race in outer space.
Countries must undertake not to test, deploy or use any weapon systems or components in space.
Fourthly, tentative ideas on new international legal instruments.
For the moment the Chinese delegation believes that the new international legal instruments to prevent the weaponization of, and an arms race in outer space ought to include purposes, basic obligations, definitions, national implementation measures, international cooperation in the peaceful uses of outer space, verification measures, appropriate measures for the resolution of disputes, transparency measures, and the procedural articles commonly found in international instruments such as articles on amendment, signature, ratification and entry into force.
Our working paper gives the main features of these articles, so I will not repeat them here.

My delegation will actively participate in such discussions and negotiations.
The PRESIDENT: I thank the representative of China for his statement.
This concludes the list of speakers for today. Does any delegation want to take the floor? That does not seem to be the case.
I would therefore now turn to the question of our programme of work.
I regret to have to inform you that none of the three options which I submitted in an informal context to the Conference gained unanimous support.
The draft declaration which I circulated yesterday morning with regard to the appointment of two special coordinators under decision CD/1036, paragraph 5 (d), did not, for technical reasons, reach all groups in time to be discussed in yesterday's group meetings.
In the Presidential consultations held yesterday afternoon, the Coordinator of the G-21 informed me that his group, while maintaining its formal position presented in its statement made in the plenary meeting of 27 January, could accept the appointment of the two special coordinators as a stand-alone decision.
In addition, the group made a number of changes to the text, which in the meantime should have been brought to the attention of all delegations.

Under these circumstances, I am not in a position to carry the matter any further at this point.
Much as I deplore it, I have no choice but to leave it for consideration at a later stage.
Although the rule quoted in decision CD/1036 stipulates, or implies, that a decision on the appointment of the special coordinator or coordinators should be taken in the second half of the first presidency of each session, in the one case on record when this rule was applied, in 1991, the appointment was made by the second President of the year's session.
My successor, provided that he intends to follow this course and provided he can obtain the support of the Conference, would thus be able to take up, based on this precedent, the same question during his term of office.
The PRESIDENT: I thank the Ambassador of Mexico and I appreciate his clarification.
It was not my intention to create the impression that the problem rests with the Group of 21. I was just pointing out that from them we had received a reply - a positive reply, as I said - with some text amendments which, however, need time to be studied.

Mr. SOUTAR (United Kingdom of Great Britain and Northern Ireland): Mr. President, as this is the first time I have asked for the floor during your presidency, may I begin by expressing the appreciation of my delegation for the energy and determination with which you have performed your crucial role at a particularly challenging time?
May I also, with regret, offer the commiseration of my delegation that your efforts on our behalf have not been translated into agreement on a substantive work programme for the Conference?
The United Kingdom finds this state of affairs deeply disappointing.
We approached this year's session with the same key objective we have held for a number of years: the immediate commencement and early conclusion of negotiations on a fissile material cut-off treaty (FMCT).
I was therefore heartened by the report which Ambassador Luck made to the Conference at our first meeting on 18 January, describing the outcome of the inter-sessional consultations he had conducted jointly with you, Mr. President.
In that report, he spoke of a strongly dominant sentiment among delegations that the Conference should commence forthwith on a programme of work, and that the informal proposals outlined by Ambassador Dembri last year remained our

[... the TARGET BLOCK appears here ...]

The United Kingdom was therefore dismayed when informal consultations revealed that one delegation was no longer prepared to be bound by a commitment solemnly entered into five years ago, making the achievement of consensus on this particular option impossible.
Those who try to place obstacles in the way of an FMCT negotiation do nothing to advance the cause of nuclear disarmament, and only call into question the sincerity of their commitment to nuclear disarmament.
Another unfortunate victim of this development is that the Conference has been unable to reappoint a special coordinator or coordinators on the reform issues: review of the agenda, expansion of its membership, and improved and effective functioning.
In informal consultations last week, I made the point that the consensus rule provides an essential safeguard for the interests of individual delegations.
But I also said that the consensus rule should not be allowed to become a straitjacket, choking off the possibility of substantive work where there is a real demand for it.
Like our distinguished former colleague, Ambassador Péter Náray of Hungary, I begin to fear that the word "consensus" may get a new meaning if the Conference continues the practices we have seen established over the past two years.

The United Kingdom would therefore like to lend its voice to the increasing chorus of delegations who have called for reform of our procedures.
I am not so naive as to believe that mere reform of procedures would necessarily of itself lead to accelerated progress on the substantive items of our agenda.
But I would recall the words of the distinguished Ambassador of Chile who told us last year that even in unpromising external circumstances, the Conference could emerge from its state of paralysis.
He went on to suggest some simple modifications to our operating procedures which, without altering the current procedural framework, would nonetheless allow the Conference to carry out some ground-breaking work to prepare for eventual negotiations.
The regrettable failure of the consultative process which you had launched on the work programme, Mr. President, strongly suggests to my delegation that there would be merit in taking up the ideas put forward by the Ambassador of Chile, and my delegation would be prepared to work on these and other ideas with like-minded delegations, even if for the time being progress on the substantive items of our work programme remains blocked.

I would suggest that this would be a modest but unmistakable signal that some members of the Conference at least are prepared to try to live up to the responsibilities laid upon the Conference by the international community.
The PRESIDENT: I thank Ambassador Soutar for his statement and the kind words addressed to the Chair.
The next speaker on my list is the Ambassador of Romania, Ambassador Maxim.
Thanks to the secretariat we were able to catch up, and yesterday evening we were in a position to send to our colleagues who are members of the Eastern European group the text which you distributed yesterday as well as the text that was prepared by the Group of 21.
This morning we were able to discuss these two texts briefly.
I am in a position to tell you that the Eastern European group is in principle in agreement with the two proposals.

I would like to take this opportunity, Sir, to thank you yet again for the efforts which you have been making during your term of offfice to arrive at a solution, and I would also like to assure the incoming President of cooperation on the part of the members of our group.
The PRESIDENT: I thank Ambassador Maxim for his statement.
I congratulate you on the manner in which you caught up with the information and conveyed it to your group and came to a very positive reaction, for which I also want to thank the Group through its Coordinator.
I now have on my list the Ambassador of France.
My delegation is all the sorrier, then, to see that it is highly likely that these efforts will lead nowhere.
Adopting what might be called option 4, involving simply the appointment of two special coordinators on nuclear disarmament and space, is far from ideal, and far from satisfactory to my delegation, because, as a previous speaker said, that option takes no account of the priority attached to the FMCT.
Maybe this could still offer a way out - I very much hope so, and in any event I thank you once again and convey to you every good wish until the last day of your term of office.

The PRESIDENT: I thank Ambassador de la Fortelle for his statement and I interpret it as support to the presidency, for which I am very grateful.
Unfortunately, I have had to accept that the trend of the Conference is not exactly to expand the role and the competence of the President but to limit them as much as possible by an interpretation of the rules which is going in favour of the Conference as such and the consensus rule.
I think Ambassador Soutar in his statement before pointed out the situation, which I personally also believe is very unfortunate because the little movement and headway we could make with the help of the presidency is hampered to a large extent by these developments.
I now give the floor to the Ambassador of Germany.
Mr. SEIBERT (Germany): In the course of the first plenary session this year, in conjunction with the adoption of the agenda, my delegation already expressed misgivings and concern about the manner in which the Conference is conducting its business.
Our protracted procedural squabbles have contributed nothing to dispelling these misgivings.
While it is legitimate that delegations may have different interpretations of the rules of procedure, we must nevertheless not forget that rules of procedure are there to facilitate our work and not to complicate it.

Against this backdrop, we appreciate and commend your efforts, Mr. President, to overcome differences and to move us forward to substantive work.
I think the first step we should be able to take is at least to reappoint the special coordinators and all of them on which agreement already existed last year.
As I mentioned earlier and other delegations as well, these are, among others, on transparency in armaments, on APMs, but also on the reform of the Conference and on the agenda.
We have in our decision on the agenda a reference to consultations on review, and I wonder when these consultations will take place if we do not have the instruments to carry out these consultations.
So I would hope that at our next meeting we will be able to reestablish the special coordinators as a first step - and this would be perfectly in harmony with paragraph 5 (d) of CD/1036 - and then move on to further substantive discussions.

My delegation, like the United Kingdom delegation, is strongly committed to the purposes of this Conference and also to the "Principles and objectives" and the programme established therein, and I would do everything in order fulfil this commitment.
I hope that we will muster the political will and determination to move this Conference out of the existing stalemate.
Since this is an official meeting, my comments are for the record.
First of all, China considers that the CD should respond to the demands placed upon it by the General Assembly and respond to the hope and aspirations of the international community. In other words, it should embark on negotiations on PAROS and nuclear disarmament.
Under the circumstances, we also need to begin negotiations on the FMCT. The Chinese delegation considers it regrettable that because some delegations refuse to negotiate on PAROS and nuclear disarmament we cannot agree on the programme of work.

If we are obliged to designate special coordinators, then after thorough consideration of your proposal of 9 February for a draft declaration, and the text and model put forward by the Group of 21 the same afternoon, my delegation finds the latter the more reasonable.
Consequently, the delegation of China supports the text and wording proposed on the afternoon of 9 February by the Group of 21.
I would like to emphasize that this does not mean that the Chinese delegation has changed its basic position on item 1.
Thirdly, I would like to clarify an issue to avoid any misunderstanding.
The Chinese delegation considers that within the CD a variety of parties regard PAROS, nuclear disarmament and FMCT as priority issues on the programme of work.
The only way of dealing with the three issues is to treat them, thoroughly and comprehensively.
Even if we accept the designation of two special coordinators to work on the organizational and jurisdictional aspects of PAROSand nuclear disarmament, our delegation still feels that FMCT must be a component of a complete solution to the matter.

The PRESIDENT: I thank the representative of China for his statement.
Maybe it opens up perspectives to my successor, if I listened carefully.
I now have on my list the representative of the Russian Federation. Ambassador Sidorov, you have the floor.
Mr. SIDOROV (Russian Federation) (translated from Russian): Since we are in the final days of your tenure as President, Sir, I would to express our delegation's gratitude to you for your recent attempts to find a way out of the deadlock in which the Conference on Disarmament has regrettably found itself for so long.
At this meeting I would like to indicate Russia's priorities in the work of the Conference on Disarmament to ensure that the participants in the Conference have a better understanding.
I wish to say that our main priority in the work of the Conference has recently been and still remains work to prevent an arms race in outer space.
We have always considered that life itself, the very circumstances, the very events of recent times should bring home to the Conference on Disarmament the urgent need to tackle this problem.
We have frequently had an opportunity, in this room, in the General Assembly and elsewhere, to set out our concerns on the state of affairs in this area.

I wish to remind you that on the initiative of Russia and a number of other delegations, a resolution was adopted at the last session of the General Assembly on the situation with regard to the ABM Treaty.
Events in the last few months have not only not diminished the urgency of this topic, but have made it even more topical.
In one of the forthcoming formal meetings of the Conference on Disarmament, the Russian Federation intends to make a special statement of that issue.
Another of our priorities will certainly remain the reestablishment of the committee on the prohibition of the production of fissile material, which, as we know, was created in 1998.
We regret that to date, despite fairly intensive consultations, negotiations, the CD has not yet managed to get down to work, substantive work, on these two issues.
We understand the difficulties experienced by individual delegations on particular issues.
The Russian delegation has been trying to ease the task of the President, in seeking consensus.
In the same spirit, pursuing the aim of seeking and finding a way out of the deadlock, we are ready to support your proposal to designate two special coordinators in accordance with decision 1036 of the Conference on Disarmament.

We would like to express the hope, Sir, that the future Presidents of the Conference will continue those consultations, and we wish you in the days remaining and the Ambassador of Bangladesh in the days to come success in those efforts.
The PRESIDENT: I thank Ambassador Sidorov for his statement, for the kind words addressed to me and for the flexibility and constructive cooperation of his delegation during my tenure.
I think the list of speakers is exhausted. Does any other delegation wish to take the floor? That does not seem to be the case.
I would therefore, with your permission, come to a few concluding remarks.
We are now in the fourth year of blockade, yet the situation this year is not identical with previous years.
I will refrain from trying to evaluate whether it is more difficult than before or not.
Once again, the Conference has been the seismograph of events in the global context.
Nobody could have expected anything else.
We are not operating in an ivory tower; we reflect in this setting here the wider issues and stakes, and we should not complain about it because it is our raison d'être.

I was under no illusion when I assumed the presidency that we would overcome the existing obstacles.
My expectations were quite modest and muted.
Well, now we know where we stand.
I believe this is a prerequisite for further work. What could that further work consist of? This is a more difficult question to answer. The Conference, for its own good reasons, has disdained secondbest solutions which would indeed have been available in the form of a reduced programme of work. In deciding against the adoption of such a reduced or lean programme of work which would not have contained any of the three items each of which is essential to a number of delegations, we would not have achieved much, but at least we would have been able to take up work in some areas.
We would not have negotiated an arms control treaty, that is true, but I still believe that we would have been able to do some useful work.
The Conference preferred to bide its time until the current situation changes, waiting for a breakthrough at a later date.
It is a perfectly respectable decision, but, of course, one could not have expected the President himself to adopt such a position of wait-and-see at the very outset.

For the President, the task consists in pointing out avenues of compromise, both substantive and procedural ones.
I take it with equanimity that not everybody agreed with the way in which I proceeded. It s the inevitable risk you run in this position.
Yet I have not represented the interests of any articular group.
The overriding motive of my efforts was to get the Conference out of the mpasse in which it has found itself for some time already, for too much time indeed.
The end f he road which we have now reached is heavily barrricaded.
To break through this barricade is ot within the power of the presidency. It is only possible by the concerted effort of all of us.
At this point I should like to thank all of you, those who accepted my proposals but also those who rejected them, those who supported me in my efforts and those who could find little merit in them, because they all spent much time in meetings and consultations on the initiatives of the presidency.
The next plenary meeting therefore will take place, as usual, on Thursday, 17 February, at 10 a.m. in this room.

Candidate 0:
  Question: According to the United Kingdom's February 2000 statement, what assurance did an FMCT offer before an effective and verifiable global ban on nuclear weapons?
  Answer: that no new fissile material for such weapons can be produced

Candidate 1:
  Question: According to the United Kingdom's February 2000 statement, had the importance of an FMCT diminished during the intervening period?
  Answer: The importance of an FMCT has not diminished in the intervening period
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
    "reason": "The answer is supported by the target block, but it spans two adjacent sentences (confidence that no new fissile material can be produced, and the FMCT delivering that assurance). The answer also reads as 'confidence' rather than an assurance, and the extracted fragment is slightly awkward as a standalone answer. The speaker attribution to the UK comes from the document context, which is legitimate."
  },
  {
    "index": 1,
    "grounding": 5,
    "precision": 4,
    "numerical_fidelity": 5,
    "reason": "The answer is a verbatim single sentence from the target block. It is a full sentence restating the question rather than a bare 'No', which is minor padding. There are no numbers to check."
  }
]
````

### Recorded usage

````json
{
  "cached_tokens": 0,
  "completion_tokens": 292,
  "prompt_tokens": 12120,
  "provider_cost": 0.02716,
  "reasoning_tokens": 0
}
````

### Input size diagnostics

````json
{
  "input_characters": 38358,
  "context_capacity_exceeded": null
}
````

## Call 013: faithfulness

Request: `15be68e2f06e4cb78056fb4a18e6c62c`. Task: `mode/eurlex/http://data.europa.eu/eli/reg/2010/1031/art_48/oj/lookup`.

Model: `anthropic/claude-sonnet-5.5`. UTC: 2026-09-30T18:32:37.293400+00:00.

API status: **response**. Duration: 3.342314 seconds.

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
You are a strict faithfulness grader for legal and regulatory question-answer pairs.

You will receive a context of four labelled blocks (an empty block says so explicitly) and THREE
  question-answer pairs.
The context is:
- "### TARGET ARTICLE" — the article the questions are supposed to be about, in several language
  versions.
- "### REFERENCED ARTICLES" — other articles of the SAME act, cited by the target article and
  supplied so that an answer can be complete.
- "### REFERENCED ARTICLES FROM OTHER ACTS" — articles of OTHER acts that the target article cites
  by name, supplied for the same purpose. Each carries a "Cite as:" key of the form CELEX:number
  (e.g. 32004R0021:5). A block that is empty says so.
- "### REFERENCED ANNEXES" — annexes the target article cites, of its own act or of another act,
  each with its own "Act:" line and a "Cite as:" key of the form CELEX:anx_<id> (e.g.
  32019R0904:anx_1).
An answer MAY legitimately draw on a referenced article or annex — of the same act or of another act
  — when the target article's own text points to it. That is by design and must NOT be penalised as
  ungrounded.

Each candidate also carries an "articles_involved" list: the articles the generator says are needed
  to answer it — bare numbers for the target's own act's articles, "Cite as" keys for articles of
  other acts and for all annexes. Verify it. An answer whose substance comes partly from a
  referenced article that is NOT declared is mis-attributed; an answer that declares an article it
  did not use is over-declared. Both are grounding failures — see the GROUNDING rubric.

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

1. GROUNDING (1–5): Is the answer supported by a contiguous span of the supplied text, and is its
  provenance declared correctly?
   The supplied text means the TARGET ARTICLE plus any REFERENCED ARTICLES or REFERENCED ANNEXES —
     of the same act or of other acts. Following an explicit cross-reference from the target into
     any supplied referenced unit is legitimate and is not an inferential step.
   Cap the grade at 2 if "articles_involved" is wrong in either direction: an article whose content
     the answer uses is missing from the list, or an article is listed whose content the answer
     never used. Cap at 1 if the answer's substance comes from an article that was never supplied at
     all.
   5 — Answer is taken directly from a single short contiguous span of the supplied text. Every word
     of the answer is explicitly present or is a trivial rewording of explicit content. No inference
     whatsoever. (Rare.)
   4 — Answer is fully supported but requires reading across two adjacent sentences, OR is from a
     single span with minor trivial rewording that a strict reader might flag.
   3 — Answer is grounded in the supplied text but requires one small, defensible inferential step —
     combining a definition with a value, or connecting a pronoun to its referent, or similar.
   2 — Answer is partially supported: some parts grounded in the supplied text, other parts not.
   1 — Answer requires significant inference, outside knowledge, or is not in the supplied text at
     all.
   CROSS-REFERENCE RULE (EUR-Lex): legal text constantly cites other provisions ("the articles
     listed in Article 3", "subject to Article 5(2)", "the checks provided for in Article 5 of
     Regulation (EC) No 21/2004"). Here the cited provision is often SUPPLIED — in the REFERENCED
     ARTICLES block, the REFERENCED ARTICLES FROM OTHER ACTS block, or the REFERENCED ANNEXES block.
     Distinguish two cases:
     (a) the cited provision IS supplied (in any of the three reference blocks) — following the
       citation is legitimate support, not inference. Grade the answer on its merits, and check that
       the cited provision appears in "articles_involved" (by its "Cite as" key when it belongs to
       another act or is an annex).
     (b) the cited article is NOT supplied — the substance sits behind a pointer with nothing behind
       it. Score at most 2 (1 if the answer consists mainly of such unstated content).

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
   5 — All numbers, dates, durations, monetary amounts, percentages, and official identifiers
     (instrument, article, paragraph, and annex numbers) match the passage character-for-character
     (e.g., "resolution 2374 (2017)" preserved as-is, not "Resolution 2374"; "Article 5(2)", not
     "Article 5.2"; "100 000 EUR", not "€100,000"; "within 90 days", not "in about three months").
     Dates rendered in the answer language's standard format count as exact if day, month, and year
     are unchanged ("15 July 2027" for "el 15 de julio de 2027").
   4 — All values and identifiers are correct and preserved, but with a trivial formatting
     difference (e.g., "90-day period" vs. "within 90 days", or a spacing/punctuation variant of an
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
### TARGET ARTICLE — write the questions about THIS article

[EN] Article 48 — Late delivery of the auctioned allowances
  Act: Commission Regulation (EU) No 1031/2010 of 12 November 2010 on the timing, administration and other aspects of auctioning of greenhouse gas emission allowances pursuant to Directive 2003/87/EC of the European Parliament and of the Council establishing a scheme for greenhouse gas emission allowances trading within the Community (Text with EEA relevance)
  Location: CHAPTER XII DELIVERY OF THE AUCTIONED ALLOWANCES
Late delivery of the auctioned allowances

1. Where the clearing system or settlement system fails to deliver the whole or part of the auctioned allowances due to circumstances outside its control, the clearing system or settlement system shall deliver the allowances at the earliest opportunity and the successful bidders or their successors in title shall accept delivery at that later date.

2. The remedy provided for in paragraph 1 shall be the sole remedy to which a successful bidder or its successors in title shall be entitled to in case of any failure to deliver auctioned allowances, due to circumstances outside the control of the clearing system or settlement system concerned.

### REFERENCED ARTICLES — none. The target article cites no other article of this act.

### REFERENCED ARTICLES FROM OTHER ACTS — none. The target article cites no article of another act in the corpus.

### REFERENCED ANNEXES — none. The target article cites no resolvable annex.

Candidate 0:
  Question: What must the clearing or settlement system do when it cannot deliver auctioned allowances because of circumstances outside its control?
  Answer: shall deliver the allowances at the earliest opportunity
  Articles involved (declared): 48

Candidate 1:
  Question: May a successful bidder or its successor in title claim any remedy other than the remedy specified for late delivery of auctioned allowances caused by circumstances outside the system's control?
  Answer: The remedy provided for in paragraph 1 shall be the sole remedy to which a successful bidder or its successors in title shall be entitled to in case of any failure to deliver auctioned allowances, due to circumstances outside the control of the clearing system or settlement system concerned.
  Articles involved (declared): 48
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
    "reason": "The answer is a verbatim short span from Article 48(1), and the declared article is correct. It is tight and contains no numbers to get wrong."
  },
  {
    "index": 1,
    "grounding": 4,
    "precision": 3,
    "numerical_fidelity": 5,
    "reason": "The answer copies paragraph 2 verbatim and declares the right article, but the question is yes/no and the answer never says so directly. It is also a full-sentence copy where a shorter span would do, and it needs a small inference to read as 'no'. The 'paragraph 1' reference is preserved exactly."
  }
]
````

### Recorded usage

````json
{
  "cached_tokens": 0,
  "completion_tokens": 257,
  "prompt_tokens": 3920,
  "provider_cost": 0.01041,
  "reasoning_tokens": 0
}
````

### Input size diagnostics

````json
{
  "input_characters": 10934,
  "context_capacity_exceeded": null
}
````

## Call 014: faithfulness

Request: `6c5bd9ad3a7c4e1f8cb7f4573a9f57a4`. Task: `mode/un/2004/s/2004/505#15/practitioner`.

Model: `anthropic/claude-sonnet-5.5`. UTC: 2026-09-30T18:32:37.295269+00:00.

API status: **response**. Duration: 3.567723 seconds.

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

[EN] Document: S/2004/505
  Title: Letter dated 18 June 2004 from the Permanent Representative of Germany to the United Nations addressed to the Secretary-General I have the honour to enclose the assessment of the work of the Security Council during the presidency of Germany in April 2004 (see annex).
There was agreement that the resolution does not alter existing treaties or arrangements on disarmament, arms control, non-proliferation and verification, which retain their full importance and must be further developed, and that it does not constitute a basis for unilateral enforcement action.
38. Under the terms of the resolution, all Member States are to submit, within the next six months, a first report on steps they have taken or intend to take to implement it.
39. On 15 April, the Council met to discuss the role of business in conflict prevention, peacekeeping and post-conflict peace-building.
Guests speakers in the public meeting were the Secretary-General Kofi Annan, the World Bank President, the President and CEO of Siemens, Heinrich von Pierer, the President of the Economic and Social Council, Ambassador Marjatta Rasi, and the Chairman of the Advisory Groups of the Economic and Social Council for African countries emerging from conflict, Ambassador Dumisani Shadrak Kumalo.

### REFERENCED DOCUMENTS — none. The target block cites no other document available in the corpus.

### DOCUMENT CONTEXT — surrounding text of the SAME document, supporting context only. It resolves what the target block leaves implicit; it is never a source of answers.

[EN] Document S/2004/505 — surrounding passages
Letter dated 18 June 2004 from the Permanent Representative of Germany to the United Nations addressed to the Secretary-General I have the honour to enclose the assessment of the work of the Security Council during the presidency of Germany in April 2004 (see annex).
This assessment has been prepared under my own responsibility following consultations with other members of the Council.
Introduction 1. The work of the Security Council during the month of April 2004 was characterized in particular by discussions about the non-proliferation of weapons of mass destruction, the question of Cyprus, Iraq and the Middle East.
The Security Council also discussed the serious humanitarian crises in the Sudan (Darfur) and in northern Uganda.
A Council debate on the role of business in conflict prevention, peacekeeping and peace-building highlighted the important role the private sector can play in mitigating the consequences of conflict, and the possible contribution of private business to re-establishing peace and security.
The results of the Berlin Conference on Afghanistan were welcomed by the Security Council which reaffirmed its support for the long-term commitment by the international community in Afghanistan.
The Security Council adopted a resolution on children in armed conflict with a view to further increase the protection of the rights of children associated with armed conflict.

2. The Council held 18 informal consultations and one private meeting, nine open briefings and public meetings as well as two open debates (on the Middle East and weapons of mass destruction).
It adopted five resolutions (oil-for-food inquiry, children in armed conflict, non-proliferation of weapons of mass destruction, Western Sahara, Haiti) and five presidential statements (Afghanistan, Libyan Arab Jamahiriya, Iraq/Kuwait, Kosovo, Côte d'Ivoire).
The mandate of the United Nations Mission in Western Sahara (MINURSO) was renewed for six months.
Africa
Guinea-Bissau 3. In informal consultations on 6 April 2004, the representative of the Secretary-General and head of the United Nations Peace-Building Office in Guinea-Bissau (UNOGBIS), David Stephen, updated the Council on the situation in Guinea-Bissau.
Members of the Council welcomed the holding of the legislative elections on 2830 March 2004 and commended the people of Guinea-Bissau for their democratic maturity.
They urged the political parties to continue to work together for national reconciliation and the return to constitutional order.
They commended the coordinating roles of the United Nations Development Programme and UNOGBIS with regard to the assistance provided to Guinea-Bissau during the electoral process and the observation of the elections, respectively.
They expressed their continued support for the Representative of the Secretary-General as well as for UNOGBIS.

In a press statement (SC/8054), members of the Council expressed concern at the persistence of serious economic difficulties in Guinea-Bissau and made a strong appeal to the international community, to continue considering the situation in Guinea-Bissau as a matter of emergency.
Sudan (Darfur)
4. In consultations on 2 April, under "other matters", the Security Council heard a briefing by the Under-Secretary-General for Humanitarian Affairs and Emergency Relief Coordinator about the humanitarian situation in the Darfur region of Sudan.
He described the continued attacks of the Janjaweed militias against the local population in Darfur as acts comparable to ethnic cleansing.
More than a million people had been forced from their homes by the armed conflict to date.
Without immediately improved security as well as access for humanitarian agencies, the crisis would worsen dramatically.
5. In a press statement (SC/8050), members of the Council subsequently expressed their deep concern about the massive humanitarian crisis in Darfur and called on the parties concerned to fully cooperate in order to address the grave situation, to ensure the protection of civilians and to facilitate humanitarian access to the affected population.
The Council also called for the conclusion of a humanitarian ceasefire and a political settlement to the dispute.

Uganda (northern Uganda)
6. In consultations on 14 April, under "other matters", the Security Council heard a briefing by the Under-Secretary-General for Humanitarian Affairs and Emergency Relief Coordinator on the humanitarian situation in northern Uganda.
More than 1.5 million people had been forced from their homes and over 20,000 children had been abducted since the beginning of the conflict between the Government in Kampala and the Lord's Resistance Army in the north of the country 18 years ago.
7. In a press statement (SC/8057), the Security Council strongly condemned the appalling atrocities and expressed its deep concern about the humanitarian crisis, in particular the abduction, forced recruitment and sexual violence against children.
The Security Council stressed that such crimes should not remain unpunished.
Council members called for an immediate end to all acts of violence against civilians and for unimpeded humanitarian access to the civilian population. Côte d'Ivoire
9. On 27 April, the Under-Secretary-General briefed the Council on the high-level mission to Côte d'Ivoire he led from 15 to 20 April.
The mission was comprised of the Executive Secretary of ECOWAS, senior officials from France, the United Kingdom and the United States and a representative of the African Union.

The purpose of the mission was to impress upon all Ivorian parties the urgent need to resolve the stalemate in the peace process.
Members of the Council expressed their support for the mission.
10. On 30 April, the Security Council authorized its President to make a statement, emphasizing the individual responsibility of each of the Ivorian actors in the settlement of the crisis.
The statement also expressed the Council's readiness to consider further steps to encourage full implementation of the Linas-Marcoussis agreement and to promote the process of national reconciliation, including actions that might be taken, if necessary, against individuals whose activities are an obstacle to the full implementation of the agreement.
Western Sahara 11. On 27 April, the Security Council in informal consultations heard a briefing by the Assistant Secretary-General for Peacekeeping Operations on the situation concerning Western Sahara. The Assistant Secretary-General made reference to the report of the Secretary-General dated 23 April (S/2004/325), in which the Secretary-General had recommended a further extension of MINURSO's mandate.

12. The Council, on 29 April, unanimously adopted resolution 1541 (2004) reaffirming its support for the peace plan for self-determination of the people of Western Sahara as an optimum political solution on the basis of agreement between the two parties.
The resolution provides for an extension of the mandate of MINURSO for a period of six months until 31 October 2004 and requests that the Secretary-General provide a report on the situation before the end of the mandate, including an evaluation of the mission size necessary for MINURSO with a view towards its possible reduction.
Libyan Arab Jamahiriya
13. On 22 April, the Security Council authorized the President to make a statement, welcoming the decision by the Libyan Arab Jamahiriya to abandon its programmes for developing weapons of mass destruction and expressing the hope that resolution 2004/18 of the Board of Governors of the International Atomic Energy Agency would be implemented in the spirit of continued cooperation.

Iraq
14. On 16 April, in an open briefing, the United States, on behalf of the multinational force, reported to the Security Council pursuant to paragraph 25 of resolution 1511 (2003) on the efforts and progress of this force.
In the subsequent closed consultations on Iraq discussion focused on the current security situation in Iraq, on the tentative ideas regarding interim structures as of 30 June presented by the Special Adviser of the Secretary-General, Lakhdar Brahimi, at a press conference held in Baghdad on 14 April, concerning a new mandate for the multinational force in Iraq and possible elements for a future Security Council resolution.
15. Following the appointment by the Secretary-General of an independent high-level inquiry on 21 April 2004, the Security Council adopted unanimously resolution 1538 (2004), in which it welcomed the appointment and called on the Coalition Provisional Authority, Iraq and all other member States to cooperate fully with the inquiry using all appropriate means.
The Security Council looks forward to receiving the final report of the investigation into the administration and management of the oil-for-food programme.

16. On 27 April, the Security Council held an open briefing followed by closed consultations on Iraq with the Secretary-General's Special Adviser.
In the open briefing, Mr. Brahimi further elaborated his ideas presented at a press conference in Baghdad on 14 April about interim structures following the 30 June transfer of sovereignty.
He informed the Council about his plans to return to Baghdad to facilitate agreement on the proposed structures and specific personalities for the interim government.
The Security Council adopted a presidential statement supporting Mr. Brahimi (S/PRST/2004/11).
17. In consultations, member States asked many questions concerning the balance of power among the multinational force, the Iraqi government and the United Nations.
They also expressed concern about the very difficult security situation.
18. In informal consultations on 21 April, the Council heard a briefing from Ambassador Yuli Vorontsov, the Secretary-General's High-Level Coordinator, on the fifteenth report of the Secretary-General (S/2004/301), in accordance with paragraph 14 of Security Council resolution 1284 (1999).
Council members expressed their continued support for the work of Ambassador Vorontsov and extended their condolences to the families of missing persons now identified.
They expressed their hope that those responsible for the executions of Kuwaiti and third country nationals in violation of human rights and international humanitarian law will be brought to justice.

19. In a press statement (SC/8067), members of the Council also called on all parties concerned to continue to work towards a satisfactory solution of all humanitarian aspects under Ambassador Vorontsov's mandate and recalled that Iraq will continue to have international obligations, as set out in paragraph 14 of resolution 1284 (1999), after 30 June 2004.
Middle East (including the question of Palestine)
20. The Council held an open debate on 19 April regarding the situation in the Middle East, including the Palestinian question.
The meeting followed the targeted killing of Hamas leader Abdel Aziz al-Rantisi on 17 April by Israel.
In the meeting, delegations in general expressed their serious concern about the recent developments on the ground.
21. On 23 April, the Council held its monthly open briefing on the situation in the Middle East.
The Special Coordinator for the Middle East Peace Process and Personal Representative of the Secretary-General, Terje Roed-Larsen, shared with the Council his assessment of the latest political developments, concentrating primarily on the Government of Israel's announced Gaza withdrawal initiative.
He said that he believed that the Gaza withdrawal, if carried out in the right way, could usher in a new era of peace-making in the Middle East.

For this to happen, two main elements were necessary. First, the withdrawal should constitute an end of the occupation of the Gaza Strip, not merely a military redeployment. Second, the withdrawal would have to be accompanied by the implementation of other Palestinian and Israeli obligations under the road map.
He appealed to the parties to take advantage of the opportunity provided by the withdrawal initiative, and to the international community to assist the parties therein.
In informal consultations following the briefing, members of the Council agreed in general with the assessment of the situation given by the Special Coordinator.
22. Following prior informal consultations, a draft resolution demanding inter alia the cessation of extrajudicial killings was tabled as document S/2004/322 on 23 April.
No action was taken.
Afghanistan
23. The Security Council held a public meeting on the situation in Afghanistan on 6 April.
The Council heard briefings by Under-Secretary-General for Peacekeeping Operations and Ambassador Pleuger of Germany on the Berlin Conference on Afghanistan.
Both outlined the achievements of the Conference: reform commitments by the Afghan Government, notably in the field of disarmament, demobilization and reintegration of armed forces, significant donor pledges and increased regional cooperation in counter-narcotics efforts.
They welcomed President Karzai's announcement to hold elections in September 2004.

Furthermore, they highlighted the continuing security problems that threatened the holding of credible elections, as well as the increasing challenge from narcotics.
Georgia
Council members expressed their support for the work of the Special Representative of the Secretary-General in Georgia as well as for the efforts of the Group of Friends, and stated their hope that the peace process will be carried forward despite the recent stalemate.
Europe
Cyprus
27. On 2 April, in an open meeting, the Council heard a briefing from the Secretary-General's Special Adviser on Cyprus, Alvaro de Soto, about the latest developments in the Cyprus talks.
28. He described the different phases of negotiations since the resumption of the Cyprus talks on 13 February 2003. He commended in particular the work of the technical experts, who had finalized 131 laws and cooperation agreements on 9,000 pages of text.
However, the political level had not been able to agree on the proposed changes.
In informal consultations following the open briefing, Council members expressed their appreciation for the good offices of the Secretary-General and the work of the Special Adviser and his team, and expressed hope for a solution of the Cyprus problem.

In a press statement following the meeting (SC/8050), Council members noted that it was now for the Cypriots to decide their future at this important juncture.
Council members expressed their readiness to take further actions as provided for in the plan, including by establishing a new United Nations operation in support of its swift and full implementation by all parties and by helping ensure that the parties fully met their commitments under the settlement.
Several Council members gave an explanation of vote (see S/PV.4947).
31. In a press statement on 29 April, members of the Security Council noted the outcome of the referenda held in Cyprus on 24 April 2004 on the comprehensive settlement of the Cyprus problem and shared the Secretary-General's disappointment that efforts since 1999 to reunify the island had not succeeded.
They expressed their regret that an extraordinary and historic opportunity to resolve the Cyprus issue had been missed, reiterated their strong support for an overall political settlement in Cyprus and looked forward to the Secretary-General's forthcoming report.

UNMIK 32. On 13 April, the Council held a regular public meeting on Kosovo. It heard a briefing by the Under-Secretary-General for Peacekeeping Operations, who focused his briefing on the violence in Kosovo from 17 to 20 March.
He warned that although the current situation was quiet, a potential for new violence continued to exist.
The violent attacks mainly by Kosovo Albanians against Kosovo Serbs following a series of events, including the shooting of a Kosovo Serb youth and the drowning of two Kosovo Albanian children had been an organized, widespread, and targeted campaign.
The violence had completely reverted the returns process, which prior to the events had shown signs of limited but encouraging progress.
In the subsequent debate, members of the Council widely condemned ethnic violence in Kosovo, called on the provisional institutions of self-government in Kosovo to take responsibility and compensate for the losses, and reiterated their support for the "standards before status" policy. On 30 April, the Council authorized the President to make a statement on Kosovo that was issued in document S/PRST/2004/13.

Haiti
33. In informal consultations on 30 April, the United Nations Secretariat introduced the report of the Secretary-General on Haiti (S/2004/300), including proposals for the mandate, structure and competencies of the multidimensional peacekeeping and nation-building mission that is to take over from the current multinational interim force, which was mandated by resolution 1529 (2004) for a period of three months.
The Special Adviser of the Secretary-General for Haiti, Reginald Dumas, briefed Council members about his most recent trip to the region. He pointed out the expectation of an improvement of the cooperation between the Transitional Government of Haiti and the regional organizations.
Council members welcomed the long-term comprehensive approach of the proposed United Nations-engagement in Haiti.
They also requested that information on the financial implications be made available as soon as possible.
34. The Council then unanimously adopted resolution 1542 (2004) and established the Mission des Nations Unies pour la stabilisation en Haiti (MINUSTAH) for a period of six months, beginning on 1 June 2004.
MINUSTAH will comprise up to 6,700 troops, up to 1,622 police officers and a number of multidimensional peace-building components.
A secure and stable environment, the political process and human rights are given equal importance under the mission's mandate.

Other issues
Non-proliferation of weapons of mass destruction
35. On 28 April, the Council adopted resolution 1540 (2004) on the non-proliferation of weapons of mass destruction.
This was the first time that the Council passed a resolution on this subject.
36. Its aim is to prevent proliferation of weapons of mass destruction, related materials and means of delivery to non-state actors.
Such acts of proliferation are to be criminalized; controls, including export controls, are to be strengthened, and the respective legislation and administrative provisions improved.
The adoption of this resolution was preceded by intensive discussions in consultations of the Security Council on 8 April, 20 April and 28 April, as well as in an open debate on 22 April.
37. Resolution 1540 (2004) imposes binding far-reaching obligations on all United Nations Member States to take legal and administrative action.
Many members therefore called for an open debate to discuss the draft before its finalization.
The great majority of delegates expressed support for the goals of the resolution, i.e., to address a dangerous gap in the international security framework, and affirmed their commitment to fully implement this important new instrument.

[... the TARGET BLOCK appears here ...]

40. There was a general view among speakers that business has an important role to play in conflict prevention and conflict resolution.
Private business could fuel conflicts just as it could help to overcome conflicts.
Business' role in providing employment, particularly in countries emerging from conflict, was emphasized.
The Stability Pact for South Eastern Europe was referred to by some speakers as a good example for a comprehensive approach towards economic and political stabilization.
The Kimberly Process for Certification of Rough Diamonds was frequently cited as a good example of partnership with the private sector to reduce the role of trade in diamonds to fund conflicts.
41. The meeting signalled the need felt for a more coherent approach by all respective institutions both inside and outside the United Nations to better use the potential of entrepreneurial initiative in stabilization efforts after a conflict.
Children in armed conflict
42. On 22 April, the Council adopted resolution 1539 (2004) on children and armed conflict.
The resolution imposes strict time-bound goals on parties that recruit or use child soldiers in contravention of their international obligations.
It also gives a much needed fresh impetus to the improvement of monitoring and reporting, both at United Nations Headquarters and in the field.

Other important areas of focus are the protection of children, especially girls, from sexual exploitation, the curbing of the sale of small arms as well as education as a means to halt and prevent the recruitment and re-recruitment of child soldiers.
The Council has also broadened the scope of the resolution by taking into account other egregious violations aside from the recruitment of child soldiers.
The resolution, therefore, brings important advances in the struggle for the protection of the rights of children associated with armed conflict.
43. In addition, in resolution 1539 (2004), the Council, for the first time, announced its intention to consider imposing targeted measures against parties that persist in illegal practices pertaining to the recruitment of child soldiers.
44. On 7 April, the Security Council working group on peacekeeping discussed the configuration and mandate of the planned peacekeeping mission for Burundi.
Major stakeholders in the future mission also participated in the discussion.
The Secretariat briefed the working group about the situation in Burundi and plans for the peacekeeping mission.

Participants subsequently exchanged views on the accomplishments of the African Mission in Burundi, contributions and support for the future United Nations peacekeeping mission, security of peacekeeping personnel, exit strategy, sustainability of United Nations peacekeeping efforts in Burundi through early linkage with peace-building measures, and benchmarks for the peacekeeping mission's mandate.
45. On 27 April, the Chairman of the Al Qaida/Taliban Sanctions Committee, Heraldo Munoz, briefed the Council on specific aspects concerning the implementation of the sanctions.
Pursuant to resolution 1526 (2004), he presented a list of 68 member States which had not yet submitted reports due under resolution 1455 (2003).
Underlining the importance of States' reports as invaluable tools in evaluating the level of implementation of the sanctions measures, the Chairman announced that non-reporting States will be contacted by Committee experts to discuss the reasons for their non-reporting and will be offered assistance if needed.

Candidate 0:
  Question: As of April 2004, how soon were Member States to submit a first report on non-proliferation measures for weapons of mass destruction?
  Answer: within the next six months

Candidate 1:
  Question: When in April 2004 did the Security Council discuss business in conflict prevention, peacekeeping and post-conflict peace-building?
  Answer: 15 April
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
    "reason": "The target block says 'within the next six months' for a first report on steps taken to implement 'the resolution', but the link to WMD non-proliferation (resolution 1540) comes only from the document context, which is legitimate disambiguation, while 'as of April 2004' adds a small inference; the answer is a short exact span with correct figures."
  },
  {
    "index": 1,
    "grounding": 5,
    "precision": 5,
    "numerical_fidelity": 5,
    "reason": "Paragraph 39 states 'On 15 April, the Council met to discuss the role of business in conflict prevention, peacekeeping and post-conflict peace-building,' and the answer is exactly that date."
  }
]
````

### Recorded usage

````json
{
  "cached_tokens": 0,
  "completion_tokens": 285,
  "prompt_tokens": 10898,
  "provider_cost": 0.024646,
  "reasoning_tokens": 0
}
````

### Input size diagnostics

````json
{
  "input_characters": 33075,
  "context_capacity_exceeded": null
}
````

## Parsed pipeline outputs

### mode/eurlex/http://data.europa.eu/eli/reg/2010/1031/art_48/oj/lookup: faithfulness — completed

````json
[
  {
    "_response": {
      "grounding": 5,
      "index": 0,
      "numerical_fidelity": 5,
      "precision": 5,
      "reason": "The answer is a verbatim short span from Article 48(1), and the declared article is correct. It is tight and contains no numbers to get wrong."
    },
    "grounding": 5,
    "numerical_fidelity": 5,
    "overall": 15,
    "precision": 5,
    "reason": "The answer is a verbatim short span from Article 48(1), and the declared article is correct. It is tight and contains no numbers to get wrong."
  },
  {
    "_response": {
      "grounding": 4,
      "index": 1,
      "numerical_fidelity": 5,
      "precision": 3,
      "reason": "The answer copies paragraph 2 verbatim and declares the right article, but the question is yes/no and the answer never says so directly. It is also a full-sentence copy where a shorter span would do, and it needs a small inference to read as 'no'. The 'paragraph 1' reference is preserved exactly."
    },
    "grounding": 4,
    "numerical_fidelity": 5,
    "overall": 12,
    "precision": 3,
    "reason": "The answer copies paragraph 2 verbatim and declares the right article, but the question is yes/no and the answer never says so directly. It is also a full-sentence copy where a shorter span would do, and it needs a small inference to read as 'no'. The 'paragraph 1' reference is preserved exactly."
  }
]
````

### mode/eurlex/http://data.europa.eu/eli/reg/2010/1031/art_48/oj/lookup: quality — completed

````json
[
  {
    "_batch_diversity": "pass",
    "_contract": "compact",
    "_keys": [
      "practitioner_realism",
      "anchoring",
      "informativeness",
      "focus",
      "linguistic_quality"
    ],
    "_response": {
      "candidate_id": "q_c402f3b7c825c41027988365",
      "checks": {
        "metadata": "pass",
        "mode": "pass",
        "support": "pass"
      },
      "index": 0,
      "problems": [],
      "score_notes": {
        "anchoring": "\"auctioned allowances\" together with \"clearing or settlement system\" identifies the auctioning regime under the EU ETS. A minor gap is that it does not say which auction or scheme, but the regime is identifiable.",
        "focus": "One bounded need: the system's obligation upon non-delivery.",
        "informativeness": "The answer (deliver at the earliest opportunity) gives the core obligation. It omits that successful bidders must accept later delivery, but the question asks only what the system must do.",
        "linguistic_quality": "Clear, natural and economical English.",
        "practitioner_realism": "Direct, plausible request, but wording closely tracks the article's scaffolding (\"fails to deliver ... due to circumstances outside its control\"), so it reads close to a reading-comprehension slot."
      },
      "scores": {
        "anchoring": 4,
        "focus": 5,
        "informativeness": 4,
        "linguistic_quality": 4,
        "practitioner_realism": 3
      }
    },
    "anchoring": 4,
    "focus": 5,
    "informativeness": 4,
    "linguistic_quality": 4,
    "overall": 20,
    "practitioner_realism": 3,
    "reason": "practitioner_realism: Direct, plausible request, but wording closely tracks the article's scaffolding (\"fails to deliver ... due to circumstances outside its control\"), so it reads close to a reading-comprehension slot.; anchoring: \"auctioned allowances\" together with \"clearing or settlement system\" identifies the auctioning regime under the EU ETS. A minor gap is that it does not say which auction or scheme, but the regime is identifiable.; informativeness: The answer (deliver at the earliest opportunity) gives the core obligation. It omits that successful bidders must accept later delivery, but the question asks only what the system must do.; focus: One bounded need: the system's obligation upon non-delivery.; linguistic_quality: Clear, natural and economical English."
  },
  {
    "_batch_diversity": "pass",
    "_contract": "compact",
    "_keys": [
      "practitioner_realism",
      "anchoring",
      "informativeness",
      "focus",
      "linguistic_quality"
    ],
    "_response": {
      "candidate_id": "q_96db71273e55c8f91ba9d22e",
      "checks": {
        "metadata": "pass",
        "mode": "pass",
        "support": "pass"
      },
      "index": 1,
      "problems": [
        "informativeness: the answer span includes the unresolved pointer \"paragraph 1\" and is longer than needed to answer the yes/no question.",
        "anchoring: \"the system's control\" lacks an antecedent in the base question."
      ],
      "score_notes": {
        "anchoring": "\"auctioned allowances\", \"successful bidder\" and \"clearing/settlement system\" identify the regime. \"the remedy specified for late delivery\" is a somewhat vague referent, and \"the system\" is used without an antecedent.",
        "focus": "A single yes/no question about whether other remedies are available.",
        "informativeness": "The answer is a verbatim copy of paragraph 2 and begins with \"The remedy provided for in paragraph 1\", which is a dangling pointer. It does answer the yes/no point (no, sole remedy) but is not the shortest span and is partly a restatement.",
        "linguistic_quality": "Understandable but clumsy: \"the remedy other than the remedy specified\" is repetitive, and \"the system's\" has no antecedent.",
        "practitioner_realism": "A realistic yes/no question about exclusivity of remedy, but it is phrased with heavy copying from the article."
      },
      "scores": {
        "anchoring": 3,
        "focus": 5,
        "informativeness": 3,
        "linguistic_quality": 3,
        "practitioner_realism": 3
      }
    },
    "anchoring": 3,
    "focus": 5,
    "informativeness": 3,
    "linguistic_quality": 3,
    "overall": 17,
    "practitioner_realism": 3,
    "reason": "practitioner_realism: A realistic yes/no question about exclusivity of remedy, but it is phrased with heavy copying from the article.; anchoring: \"auctioned allowances\", \"successful bidder\" and \"clearing/settlement system\" identify the regime. \"the remedy specified for late delivery\" is a somewhat vague referent, and \"the system\" is used without an antecedent.; informativeness: The answer is a verbatim copy of paragraph 2 and begins with \"The remedy provided for in paragraph 1\", which is a dangling pointer. It does answer the yes/no point (no, sole remedy) but is not the shortest span and is partly a restatement.; focus: A single yes/no question about whether other remedies are available.; linguistic_quality: Understandable but clumsy: \"the remedy other than the remedy specified\" is repetitive, and \"the system's\" has no antecedent."
  }
]
````

### mode/un/1999/cedaw/c/sr_434#16/practitioner: faithfulness — completed

````json
[
  {
    "_response": {
      "grounding": 4,
      "index": 0,
      "numerical_fidelity": 5,
      "precision": 4,
      "reason": "The answer is a verbatim fragment of the target sentence, but the pronoun 'done so' has to be resolved to the appeal; the answer also does not explicitly say 'no' and keeps a dependent-clause opener ('Although')."
    },
    "grounding": 4,
    "numerical_fidelity": 5,
    "overall": 13,
    "precision": 4,
    "reason": "The answer is a verbatim fragment of the target sentence, but the pronoun 'done so' has to be resolved to the appeal; the answer also does not explicitly say 'no' and keeps a dependent-clause opener ('Although')."
  },
  {
    "_response": {
      "grounding": 4,
      "index": 1,
      "numerical_fidelity": 5,
      "precision": 4,
      "reason": "The answer is a verbatim span from the target sentence and is well supported, though 'condition' is a slight framing of 'unless' and the clause is left as a fragment; it contains no numerical content."
    },
    "grounding": 4,
    "numerical_fidelity": 5,
    "overall": 13,
    "precision": 4,
    "reason": "The answer is a verbatim span from the target sentence and is well supported, though 'condition' is a slight framing of 'unless' and the clause is left as a fragment; it contains no numerical content."
  }
]
````

### mode/un/1999/cedaw/c/sr_434#16/practitioner: quality — completed

````json
[
  {
    "_batch_diversity": "fail",
    "_contract": "compact",
    "_keys": [
      "practitioner_realism",
      "anchoring_and_time",
      "consequence",
      "informativeness",
      "linguistic_quality"
    ],
    "_response": {
      "candidate_id": "q_b738cdc8418f9b9cc0ce0d69",
      "checks": {
        "metadata": "fail",
        "mode": "fail",
        "support": "fail"
      },
      "index": 0,
      "problems": [
        "mode: the content is a committee member's remark, not a norm-state or a specific dated fact. The regime is not named and the Optional Protocol is ambiguous, so the question lacks two resolved substantive anchors.",
        "support: the deciding span is a bare fragment, and the claim is not attributed to the Committee member. The question asks about 'the Optional Protocol', which the block gives as the ICCPR protocol; the Convention's protocol is only prospective.",
        "metadata: 'Nepalese woman', 'international redress' and 'Optional Protocol' are verbatim, but 'Nepalese woman' is an affected-actor anchor of weak specificity. The regime is not anchored, and the finding_event_or_assessment type is marginal."
      ],
      "score_notes": {
        "anchoring_and_time": "June 1999 is usable as a time pin. The 'Optional Protocol' is unnamed: the block refers to the ICCPR protocol and a future Convention protocol, so an essential reference is unresolved. The regime (CEDAW/Nepal) is not named in the question, and only 'Nepalese woman' and 'international redress' are otherwise present.",
        "consequence": "The content is a thin fact: no woman had yet used the complaint route. It is a committee member's remark, not a norm, task or measure.",
        "informativeness": "The answer is 'Although no Nepalese woman had yet done so', which is essentially a bare yes/no restatement. It does not say which protocol, and the question already presupposes the answer's content.",
        "linguistic_quality": "The English is readable but vague ('the Optional Protocol', 'yet appealed'), and the question is slightly redundant.",
        "practitioner_realism": "Asks about a committee member's remark on whether anyone has used the complaint route. It is a narrow factual probe with little practitioner use, and the 'Optional Protocol' is ambiguous because the block names two protocols."
      },
      "scores": {
        "anchoring_and_time": 2,
        "consequence": 2,
        "informativeness": 2,
        "linguistic_quality": 3,
        "practitioner_realism": 2
      }
    },
    "anchoring_and_time": 2,
    "consequence": 2,
    "informativeness": 2,
    "linguistic_quality": 3,
    "overall": 11,
    "practitioner_realism": 2,
    "reason": "practitioner_realism: Asks about a committee member's remark on whether anyone has used the complaint route. It is a narrow factual probe with little practitioner use, and the 'Optional Protocol' is ambiguous because the block names two protocols.; anchoring_and_time: June 1999 is usable as a time pin. The 'Optional Protocol' is unnamed: the block refers to the ICCPR protocol and a future Convention protocol, so an essential reference is unresolved. The regime (CEDAW/Nepal) is not named in the question, and only 'Nepalese woman' and 'international redress' are otherwise present.; consequence: The content is a thin fact: no woman had yet used the complaint route. It is a committee member's remark, not a norm, task or measure.; informativeness: The answer is 'Although no Nepalese woman had yet done so', which is essentially a bare yes/no restatement. It does not say which protocol, and the question already presupposes the answer's content.; linguistic_quality: The English is readable but vague ('the Optional Protocol', 'yet appealed'), and the question is slightly redundant."
  },
  {
    "_batch_diversity": "fail",
    "_contract": "compact",
    "_keys": [
      "practitioner_realism",
      "anchoring_and_time",
      "consequence",
      "informativeness",
      "linguistic_quality"
    ],
    "_response": {
      "candidate_id": "q_7efc48073fe0fcb9b5fdcaef",
      "checks": {
        "metadata": "fail",
        "mode": "fail",
        "support": "fail"
      },
      "index": 1,
      "problems": [
        "mode: not a norm-state. It asks about a Committee member's rhetorical warning, and the regime is not named.",
        "support: the premise 'a condition made redress possible' misstates a speaker's rhetorical caveat as a fact. The unattributed claim is presented as established, and the mechanism (the Optional Protocol) is not identified.",
        "metadata: only two weak anchors ('international redress', 'Nepalese women'), neither naming a regime, body or measure. The finding_event_or_assessment type is poorly suited."
      ],
      "score_notes": {
        "anchoring_and_time": "June 1999 is given, but the question does not name the regime (CEDAW, Nepal's initial report) and has only two weak anchors: 'international redress' and 'Nepalese women'. 'Made international redress a distinct possibility' relies on the source wording, and no mechanism is specified.",
        "consequence": "It concerns a member's political warning that is not a norm or measure. It is a rhetorical rationale, not a qualifying norm element.",
        "informativeness": "The answer 'unless the Government acted quickly...' restates the question's premise and is vague. It gives no concrete norm information.",
        "linguistic_quality": "The phrasing 'what condition made international redress a distinct possibility' is stiff and partly a calque of the source wording.",
        "practitioner_realism": "Asks for the condition under which a Committee member said redress was possible. This is a comprehension-style prompt about a rhetorical warning, not a real practitioner need."
      },
      "scores": {
        "anchoring_and_time": 2,
        "consequence": 1,
        "informativeness": 2,
        "linguistic_quality": 3,
        "practitioner_realism": 1
      }
    },
    "anchoring_and_time": 2,
    "consequence": 1,
    "informativeness": 2,
    "linguistic_quality": 3,
    "overall": 9,
    "practitioner_realism": 1,
    "reason": "practitioner_realism: Asks for the condition under which a Committee member said redress was possible. This is a comprehension-style prompt about a rhetorical warning, not a real practitioner need.; anchoring_and_time: June 1999 is given, but the question does not name the regime (CEDAW, Nepal's initial report) and has only two weak anchors: 'international redress' and 'Nepalese women'. 'Made international redress a distinct possibility' relies on the source wording, and no mechanism is specified.; consequence: It concerns a member's political warning that is not a norm or measure. It is a rhetorical rationale, not a qualifying norm element.; informativeness: The answer 'unless the Government acted quickly...' restates the question's premise and is vague. It gives no concrete norm information.; linguistic_quality: The phrasing 'what condition made international redress a distinct possibility' is stiff and partly a calque of the source wording."
  }
]
````

### mode/un/2000/cd/pv_841#11/practitioner: faithfulness — completed

````json
[
  {
    "_response": {
      "grounding": 4,
      "index": 0,
      "numerical_fidelity": 5,
      "precision": 4,
      "reason": "The answer is supported by the target block, but it spans two adjacent sentences (confidence that no new fissile material can be produced, and the FMCT delivering that assurance). The answer also reads as 'confidence' rather than an assurance, and the extracted fragment is slightly awkward as a standalone answer. The speaker attribution to the UK comes from the document context, which is legitimate."
    },
    "grounding": 4,
    "numerical_fidelity": 5,
    "overall": 13,
    "precision": 4,
    "reason": "The answer is supported by the target block, but it spans two adjacent sentences (confidence that no new fissile material can be produced, and the FMCT delivering that assurance). The answer also reads as 'confidence' rather than an assurance, and the extracted fragment is slightly awkward as a standalone answer. The speaker attribution to the UK comes from the document context, which is legitimate."
  },
  {
    "_response": {
      "grounding": 5,
      "index": 1,
      "numerical_fidelity": 5,
      "precision": 4,
      "reason": "The answer is a verbatim single sentence from the target block. It is a full sentence restating the question rather than a bare 'No', which is minor padding. There are no numbers to check."
    },
    "grounding": 5,
    "numerical_fidelity": 5,
    "overall": 14,
    "precision": 4,
    "reason": "The answer is a verbatim single sentence from the target block. It is a full sentence restating the question rather than a bare 'No', which is minor padding. There are no numbers to check."
  }
]
````

### mode/un/2000/cd/pv_841#11/practitioner: quality — completed

````json
[
  {
    "_batch_diversity": "fail",
    "_contract": "compact",
    "_keys": [
      "practitioner_realism",
      "anchoring_and_time",
      "consequence",
      "informativeness",
      "linguistic_quality"
    ],
    "_response": {
      "candidate_id": "q_2daf7c750ce7d62d29109d8a",
      "checks": {
        "metadata": "pass",
        "mode": "fail",
        "support": "pass"
      },
      "index": 0,
      "problems": [
        "mode: \"what assurance did an FMCT offer\" is a speech-act or opinion framing, not a norm-state question.",
        "mode: Content is advocacy or rationale, not a specific measure or dated fact.",
        "mode: Regime (Conference on Disarmament) is not named, and the UK is the only strong anchor."
      ],
      "score_notes": {
        "anchoring_and_time": "\"United Kingdom's February 2000 statement\" gives a date and attribution, and \"FMCT\" and \"global ban on nuclear weapons\" are further anchors. The regime is not fully named, since the Conference on Disarmament is absent. The FMCT acronym is also unexpanded.",
        "consequence": "The span is an argumentative rationale in a national statement about why an FMCT matters. It states no measure, deadline or obligation, so it is generic advocacy.",
        "informativeness": "The span \"no new fissile material ... can be produced\" answers the question. It is fairly predictable from the question's own cues and only restates the UK's reasoning, and \"before\" is slightly off as a framing.",
        "linguistic_quality": "The phrase \"offer before an effective and verifiable global ban\" is clumsy and imprecise. The original says confidence must exist before a ban, and the question compresses that awkwardly.",
        "practitioner_realism": "It asks for a UK position (\"what assurance did an FMCT offer\") rather than a norm-state, and the wording is somewhat awkward. The need is a single bounded fact, though."
      },
      "scores": {
        "anchoring_and_time": 4,
        "consequence": 2,
        "informativeness": 3,
        "linguistic_quality": 3,
        "practitioner_realism": 3
      }
    },
    "anchoring_and_time": 4,
    "consequence": 2,
    "informativeness": 3,
    "linguistic_quality": 3,
    "overall": 15,
    "practitioner_realism": 3,
    "reason": "practitioner_realism: It asks for a UK position (\"what assurance did an FMCT offer\") rather than a norm-state, and the wording is somewhat awkward. The need is a single bounded fact, though.; anchoring_and_time: \"United Kingdom's February 2000 statement\" gives a date and attribution, and \"FMCT\" and \"global ban on nuclear weapons\" are further anchors. The regime is not fully named, since the Conference on Disarmament is absent. The FMCT acronym is also unexpanded.; consequence: The span is an argumentative rationale in a national statement about why an FMCT matters. It states no measure, deadline or obligation, so it is generic advocacy.; informativeness: The span \"no new fissile material ... can be produced\" answers the question. It is fairly predictable from the question's own cues and only restates the UK's reasoning, and \"before\" is slightly off as a framing.; linguistic_quality: The phrase \"offer before an effective and verifiable global ban\" is clumsy and imprecise. The original says confidence must exist before a ban, and the question compresses that awkwardly."
  },
  {
    "_batch_diversity": "fail",
    "_contract": "compact",
    "_keys": [
      "practitioner_realism",
      "anchoring_and_time",
      "consequence",
      "informativeness",
      "linguistic_quality"
    ],
    "_response": {
      "candidate_id": "q_383a353519c639e583665b37",
      "checks": {
        "metadata": "pass",
        "mode": "fail",
        "support": "pass"
      },
      "index": 1,
      "problems": [
        "mode: Yes/no speech-act style question about stressed importance, which is an excluded content type.",
        "mode: \"intervening period\" is an unresolved reference, and only one substantive anchor is present.",
        "informativeness: The answer merely restates the question.",
        "metadata: Two listed anchors are present as substrings; \"FMCT\" is substantive and \"United Kingdom\" is an actor. This is marginal but passes."
      ],
      "score_notes": {
        "anchoring_and_time": "\"United Kingdom's February 2000 statement\" supplies time and attribution, but the only other anchor is \"FMCT\". The regime is unnamed, and \"intervening period\" is an unresolved reference.",
        "consequence": "The span is an importance-stressing rhetorical statement that states no measure or fact, which falls under the excluded mode.",
        "informativeness": "The answer just restates the question, and the yes/no is predictable from the phrasing. It is mostly restatement.",
        "linguistic_quality": "The English is grammatical, but \"during the intervening period\" is vague and the question is leading.",
        "practitioner_realism": "This is a bare yes/no comprehension prompt about a delegation's opinion, not a practitioner need."
      },
      "scores": {
        "anchoring_and_time": 3,
        "consequence": 1,
        "informativeness": 1,
        "linguistic_quality": 3,
        "practitioner_realism": 1
      }
    },
    "anchoring_and_time": 3,
    "consequence": 1,
    "informativeness": 1,
    "linguistic_quality": 3,
    "overall": 9,
    "practitioner_realism": 1,
    "reason": "practitioner_realism: This is a bare yes/no comprehension prompt about a delegation's opinion, not a practitioner need.; anchoring_and_time: \"United Kingdom's February 2000 statement\" supplies time and attribution, but the only other anchor is \"FMCT\". The regime is unnamed, and \"intervening period\" is an unresolved reference.; consequence: The span is an importance-stressing rhetorical statement that states no measure or fact, which falls under the excluded mode.; informativeness: The answer just restates the question, and the yes/no is predictable from the phrasing. It is mostly restatement.; linguistic_quality: The English is grammatical, but \"during the intervening period\" is vague and the question is leading."
  }
]
````

### mode/un/2001/s/res/1376_2001_#2/semantic: faithfulness — completed

````json
[
  {
    "_response": {
      "grounding": 4,
      "index": 0,
      "numerical_fidelity": 5,
      "precision": 4,
      "reason": "The answer is a verbatim span from paragraph 7, but the reason for urgency is only implied by the 'in this regard' link, and the span is slightly narrower than the full reasoning (it omits economic difficulties and the assistance need)."
    },
    "grounding": 4,
    "numerical_fidelity": 5,
    "overall": 13,
    "precision": 4,
    "reason": "The answer is a verbatim span from paragraph 7, but the reason for urgency is only implied by the 'in this regard' link, and the span is slightly narrower than the full reasoning (it omits economic difficulties and the assistance need)."
  },
  {
    "_response": {
      "grounding": 3,
      "index": 1,
      "numerical_fidelity": 5,
      "precision": 4,
      "reason": "The answer is verbatim from paragraph 8, but the question asks how resources were 'prevented' from fueling conflict while the text only demands cessation and states a principle, so the answer presents a demand as if it were an outcome; the span also carries a redundant trailing clause."
    },
    "grounding": 3,
    "numerical_fidelity": 5,
    "overall": 12,
    "precision": 4,
    "reason": "The answer is verbatim from paragraph 8, but the question asks how resources were 'prevented' from fueling conflict while the text only demands cessation and states a principle, so the answer presents a demand as if it were an outcome; the span also carries a redundant trailing clause."
  }
]
````

### mode/un/2001/s/res/1376_2001_#2/semantic: quality — completed

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
      "candidate_id": "q_82c5ddb7916535f4778311d9",
      "checks": {
        "metadata": "pass",
        "mode": "pass",
        "support": "pass"
      },
      "index": 0,
      "problems": [
        "linguistic_quality: no actor is named for \"considered urgent\" (the Security Council), a minor attribution gap."
      ],
      "score_notes": {
        "anchoring_and_time": "Names the DRC peace process and the year 2001. The anchor is concrete and the time is supported by the resolution date, though the question is fairly broad.",
        "consequence": "The span gives the stated rationale (interdependence of peace progress and economic recovery), which matches the \"why\" relationship. It is a concrete rationale, though thin.",
        "lexical_distance": "Copies \"international economic assistance\", \"peace process\" and \"Democratic Republic of the Congo\" from the block. Official names are exempt, but \"economic assistance\" and \"peace process\" are mirrored phrasing.",
        "linguistic_quality": "Clear and idiomatic. \"Considered urgent\" is slightly stiff, and the question does not say who considered it urgent.",
        "search_realism": "Natural conceptual question asking for the rationale behind the urgent need for economic assistance. One bounded intent and a realistic outsider query."
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
    "reason": "search_realism: Natural conceptual question asking for the rationale behind the urgent need for economic assistance. One bounded intent and a realistic outsider query.; anchoring_and_time: Names the DRC peace process and the year 2001. The anchor is concrete and the time is supported by the resolution date, though the question is fairly broad.; consequence: The span gives the stated rationale (interdependence of peace progress and economic recovery), which matches the \"why\" relationship. It is a concrete rationale, though thin.; lexical_distance: Copies \"international economic assistance\", \"peace process\" and \"Democratic Republic of the Congo\" from the block. Official names are exempt, but \"economic assistance\" and \"peace process\" are mirrored phrasing.; linguistic_quality: Clear and idiomatic. \"Considered urgent\" is slightly stiff, and the question does not say who considered it urgent.",
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
      "candidate_id": "q_8c8600b6497f79db6b0e1090",
      "checks": {
        "metadata": "pass",
        "mode": "pass",
        "support": "fail"
      },
      "index": 1,
      "problems": [
        "consequence: the question asks how prevention was achieved, but the answer is only a demand and a stated principle, which is a wrong relationship.",
        "support: the premise that the resources were in fact prevented from fueling conflict is not established by the block, which only demands cessation.",
        "mode: the answer span is long and appears to include two clauses, which is a mild over-length concern."
      ],
      "score_notes": {
        "anchoring_and_time": "Names the DRC, natural resources and 2001, so it is concrete and time-pinned.",
        "consequence": "The answer is a demand and a statement, not a mechanism of prevention. The question's presupposition that resources were prevented from fueling conflict is unsupported, so the relationship is wrong.",
        "lexical_distance": "Reuses \"natural resources\", \"conflict\" and the DRC name. Fairly close to the block, though the verbs are paraphrased (\"fueling\" for \"finance\").",
        "linguistic_quality": "The passive \"were prevented\" is awkward and misleading. The answer is a long span that repeats the country name.",
        "search_realism": "A natural topic, but the \"how were they prevented\" framing presumes a prevention that occurred. The block only demands cessation and does not describe one."
      },
      "scores": {
        "anchoring_and_time": 4,
        "consequence": 2,
        "lexical_distance": 3,
        "linguistic_quality": 3,
        "search_realism": 3
      }
    },
    "anchoring_and_time": 4,
    "consequence": 2,
    "lexical_distance": 3,
    "linguistic_quality": 3,
    "overall": 15,
    "reason": "search_realism: A natural topic, but the \"how were they prevented\" framing presumes a prevention that occurred. The block only demands cessation and does not describe one.; anchoring_and_time: Names the DRC, natural resources and 2001, so it is concrete and time-pinned.; consequence: The answer is a demand and a statement, not a mechanism of prevention. The question's presupposition that resources were prevented from fueling conflict is unsupported, so the relationship is wrong.; lexical_distance: Reuses \"natural resources\", \"conflict\" and the DRC name. Fairly close to the block, though the verbs are paraphrased (\"fueling\" for \"finance\").; linguistic_quality: The passive \"were prevented\" is awkward and misleading. The answer is a long span that repeats the country name.",
    "search_realism": 3
  }
]
````

### mode/un/2003/a/res/57/300#10/lookup: faithfulness — completed

````json
[
  {
    "_response": {
      "grounding": 5,
      "index": 0,
      "numerical_fidelity": 5,
      "precision": 5,
      "reason": "The answer is a verbatim short span from paragraph 27 of the target block, with no extra words. The '2002' in the question is metadata-level disambiguation and does not affect the answer."
    },
    "grounding": 5,
    "numerical_fidelity": 5,
    "overall": 15,
    "precision": 5,
    "reason": "The answer is a verbatim short span from paragraph 27 of the target block, with no extra words. The '2002' in the question is metadata-level disambiguation and does not affect the answer."
  },
  {
    "_response": {
      "grounding": 5,
      "index": 1,
      "numerical_fidelity": 5,
      "precision": 5,
      "reason": "The answer copies the resolution numbers and dates exactly from paragraph 28 as a single contiguous span, with nothing added."
    },
    "grounding": 5,
    "numerical_fidelity": 5,
    "overall": 15,
    "precision": 5,
    "reason": "The answer copies the resolution numbers and dates exactly from paragraph 28 as a single contiguous span, with nothing added."
  }
]
````

### mode/un/2003/a/res/57/300#10/lookup: quality — completed

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
      "candidate_id": "q_0138c66c13ba89d646510fdd",
      "checks": {
        "metadata": "pass",
        "mode": "fail",
        "support": "pass"
      },
      "index": 0,
      "problems": [
        "mode: the anchor 'the panel' is generic and the referent is unresolved, since the eminent persons panel on civil society is not named.",
        "anchoring: no distinguishing subject such as civil society or eminent persons appears outside the slot.",
        "mode: the base is 21 words, over the 20-word target but within the 25-word limit.",
        "metadata: the cited rendering has no year or date outside the slot. The 57/300 symbol supplies only a session number, so absolute time is weak in that rendering."
      ],
      "score_notes": {
        "anchoring": "'The panel' is a generic anchor. The question never says it is a panel of eminent persons on UN–civil society relations, so the referent is unresolved. The 2002 date and the resolution description locate the document but do not identify the subject.",
        "consequence": "It concerns a specific non-binding direction on how the terms of reference should be framed. That content is usable but thin.",
        "informativeness": "The span 'the intergovernmental character of the United Nations' answers the question. Because the panel is unidentified, the question is ambiguous, and 'character' plus the UN context makes the answer fairly guessable.",
        "linguistic_quality": "The wording is grammatical but clumsy: 'institutional character', 'under the 2002 ... resolution' and an unresolved 'the panel'. At 21 words it is over the 20-word target.",
        "practitioner_realism": "It asks one direct question about a single feature of the panel's terms of reference. However, the phrase 'institutional character' is vague, and the wording mirrors the resolution's 'underscore'."
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
    "reason": "practitioner_realism: It asks one direct question about a single feature of the panel's terms of reference. However, the phrase 'institutional character' is vague, and the wording mirrors the resolution's 'underscore'.; anchoring: 'The panel' is a generic anchor. The question never says it is a panel of eminent persons on UN–civil society relations, so the referent is unresolved. The 2002 date and the resolution description locate the document but do not identify the subject.; consequence: It concerns a specific non-binding direction on how the terms of reference should be framed. That content is usable but thin.; informativeness: The span 'the intergovernmental character of the United Nations' answers the question. Because the panel is unidentified, the question is ambiguous, and 'character' plus the UN context makes the answer fairly guessable.; linguistic_quality: The wording is grammatical but clumsy: 'institutional character', 'under the 2002 ... resolution' and an unresolved 'the panel'. At 21 words it is over the 20-word target."
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
      "candidate_id": "q_3c51eb8d20f6a1beead7334e",
      "checks": {
        "metadata": "fail",
        "mode": "pass",
        "support": "pass"
      },
      "index": 1,
      "problems": [
        "metadata: question_type 'sanction_condition_or_consequence' does not fit. There is no sanction or consequence; the block makes the office subject to earlier resolutions, which is closer to operative_action or actor_body_or_procedure.",
        "mode: the base is 24 words, over the 20-word target but within the 25-word limit.",
        "metadata: the cited rendering has no year or date outside the slot, so absolute time is weak there."
      ],
      "score_notes": {
        "anchoring": "'The partnership office' is a substantive anchor outside the slot, and 2002 pins the time. The description of the resolution is accurate, though the private-sector context is not stated.",
        "consequence": "It identifies a concrete legal constraint, namely the existing resolutions the office creation is subject to. The content is moderately specific, but the answer is essentially a pair of resolution numbers.",
        "informativeness": "The span gives both resolutions with dates, completely resolving the question. 'Earlier' is a mild cue, but it does not expose the answer.",
        "linguistic_quality": "The sentence is understandable but long and heavy at 24 words, over the 20-word target. 'Subject to under the ... resolution' is awkward, and the repeated 'General Assembly' adds redundancy.",
        "practitioner_realism": "It asks one direct question about which prior resolutions govern the partnership office. This is a plausible professional lookup, and the wording is paraphrased rather than copied."
      },
      "scores": {
        "anchoring": 4,
        "consequence": 3,
        "informativeness": 4,
        "linguistic_quality": 3,
        "practitioner_realism": 4
      }
    },
    "anchoring": 4,
    "consequence": 3,
    "informativeness": 4,
    "linguistic_quality": 3,
    "overall": 18,
    "practitioner_realism": 4,
    "reason": "practitioner_realism: It asks one direct question about which prior resolutions govern the partnership office. This is a plausible professional lookup, and the wording is paraphrased rather than copied.; anchoring: 'The partnership office' is a substantive anchor outside the slot, and 2002 pins the time. The description of the resolution is accurate, though the private-sector context is not stated.; consequence: It identifies a concrete legal constraint, namely the existing resolutions the office creation is subject to. The content is moderately specific, but the answer is essentially a pair of resolution numbers.; informativeness: The span gives both resolutions with dates, completely resolving the question. 'Earlier' is a mild cue, but it does not expose the answer.; linguistic_quality: The sentence is understandable but long and heavy at 24 words, over the 20-word target. 'Subject to under the ... resolution' is awkward, and the repeated 'General Assembly' adds redundancy."
  }
]
````

### mode/un/2004/s/2004/505#15/practitioner: faithfulness — completed

````json
[
  {
    "_response": {
      "grounding": 3,
      "index": 0,
      "numerical_fidelity": 5,
      "precision": 4,
      "reason": "The target block says 'within the next six months' for a first report on steps taken to implement 'the resolution', but the link to WMD non-proliferation (resolution 1540) comes only from the document context, which is legitimate disambiguation, while 'as of April 2004' adds a small inference; the answer is a short exact span with correct figures."
    },
    "grounding": 3,
    "numerical_fidelity": 5,
    "overall": 12,
    "precision": 4,
    "reason": "The target block says 'within the next six months' for a first report on steps taken to implement 'the resolution', but the link to WMD non-proliferation (resolution 1540) comes only from the document context, which is legitimate disambiguation, while 'as of April 2004' adds a small inference; the answer is a short exact span with correct figures."
  },
  {
    "_response": {
      "grounding": 5,
      "index": 1,
      "numerical_fidelity": 5,
      "precision": 5,
      "reason": "Paragraph 39 states 'On 15 April, the Council met to discuss the role of business in conflict prevention, peacekeeping and post-conflict peace-building,' and the answer is exactly that date."
    },
    "grounding": 5,
    "numerical_fidelity": 5,
    "overall": 15,
    "precision": 5,
    "reason": "Paragraph 39 states 'On 15 April, the Council met to discuss the role of business in conflict prevention, peacekeeping and post-conflict peace-building,' and the answer is exactly that date."
  }
]
````

### mode/un/2004/s/2004/505#15/practitioner: quality — completed

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
      "candidate_id": "q_02c35f2dbd505a5f5b966e6b",
      "checks": {
        "metadata": "pass",
        "mode": "pass",
        "support": "pass"
      },
      "index": 0,
      "problems": [
        "anchoring_and_time: the resolution is not named and \"within six months\" has no stated start date. The anchors are mostly generic topic terms, which makes the scope of the question somewhat ambiguous."
      ],
      "score_notes": {
        "anchoring_and_time": "\"April 2004\" is a usable time pin, and \"non-proliferation ... weapons of mass destruction\" and \"first report\" are anchors. However, the question names no specific body or measure, and the resolution that created the duty is left unresolved. \"Within the next six months\" is relative to the resolution's adoption on 28 April, which the question never gives, so the scope is somewhat ambiguous.",
        "consequence": "A concrete reporting deadline binding all Member States under the non-proliferation resolution, and useful to practitioners. The content is the author's summary of the resolution, but it is specific.",
        "informativeness": "The answer gives the six-month period, which is the requested fact. It is relative (\"within the next six months\") and the start date is not stated in the span. Still, it is a short, complete answer to the question.",
        "linguistic_quality": "Clear and precise English. \"How soon were ... to submit\" is slightly awkward, and \"non-proliferation measures\" is slightly loose, but both are acceptable.",
        "practitioner_realism": "Natural norm-state request about a reporting deadline. The unknown is the period, a single bounded fact. It is slightly indirect because the resolution is not named."
      },
      "scores": {
        "anchoring_and_time": 3,
        "consequence": 4,
        "informativeness": 4,
        "linguistic_quality": 4,
        "practitioner_realism": 4
      }
    },
    "anchoring_and_time": 3,
    "consequence": 4,
    "informativeness": 4,
    "linguistic_quality": 4,
    "overall": 19,
    "practitioner_realism": 4,
    "reason": "practitioner_realism: Natural norm-state request about a reporting deadline. The unknown is the period, a single bounded fact. It is slightly indirect because the resolution is not named.; anchoring_and_time: \"April 2004\" is a usable time pin, and \"non-proliferation ... weapons of mass destruction\" and \"first report\" are anchors. However, the question names no specific body or measure, and the resolution that created the duty is left unresolved. \"Within the next six months\" is relative to the resolution's adoption on 28 April, which the question never gives, so the scope is somewhat ambiguous.; consequence: A concrete reporting deadline binding all Member States under the non-proliferation resolution, and useful to practitioners. The content is the author's summary of the resolution, but it is specific.; informativeness: The answer gives the six-month period, which is the requested fact. It is relative (\"within the next six months\") and the start date is not stated in the span. Still, it is a short, complete answer to the question.; linguistic_quality: Clear and precise English. \"How soon were ... to submit\" is slightly awkward, and \"non-proliferation measures\" is slightly loose, but both are acceptable."
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
      "candidate_id": "q_f751a5b7fa31d7746c576080",
      "checks": {
        "metadata": "pass",
        "mode": "fail",
        "support": "pass"
      },
      "index": 1,
      "problems": [
        "mode: the question asks when the Council discussed a topic, which is a speech-act or event question, not a norm-state question.",
        "consequence: the content is a meeting date with no norm, measure or task."
      ],
      "score_notes": {
        "anchoring_and_time": "\"April 2004\" is the time pin, and the Security Council plus the business/peacebuilding topic give two anchors. The regime is generic, and \"business\" is a vague term.",
        "consequence": "A meeting date for a thematic debate. It is a dated event, but it has no norm content, and the debate produced no measure. It is close to procedural record-keeping.",
        "informativeness": "The answer \"15 April\" is correct and is in the block. It is a thin answer, and the question already fixes the month.",
        "linguistic_quality": "Fluent and concise English. \"Business\" is slightly vague.",
        "practitioner_realism": "This is an event-date lookup, essentially a comprehension prompt about when a meeting occurred, not a norm-state request. A practitioner would rarely need it."
      },
      "scores": {
        "anchoring_and_time": 3,
        "consequence": 1,
        "informativeness": 3,
        "linguistic_quality": 4,
        "practitioner_realism": 2
      }
    },
    "anchoring_and_time": 3,
    "consequence": 1,
    "informativeness": 3,
    "linguistic_quality": 4,
    "overall": 13,
    "practitioner_realism": 2,
    "reason": "practitioner_realism: This is an event-date lookup, essentially a comprehension prompt about when a meeting occurred, not a norm-state request. A practitioner would rarely need it.; anchoring_and_time: \"April 2004\" is the time pin, and the Security Council plus the business/peacebuilding topic give two anchors. The regime is generic, and \"business\" is a vague term.; consequence: A meeting date for a thematic debate. It is a dated event, but it has no norm content, and the debate produced no measure. It is close to procedural record-keeping.; informativeness: The answer \"15 April\" is correct and is in the block. It is a thin answer, and the question already fixes the month.; linguistic_quality: Fluent and concise English. \"Business\" is slightly vague."
  }
]
````

### mode/un/2004/s/res/1565_2004_#11/semantic: faithfulness — completed

````json
[
  {
    "_response": {
      "grounding": 4,
      "index": 0,
      "numerical_fidelity": 5,
      "precision": 4,
      "reason": "The answer is a near-verbatim span from paragraph 19, but 'these violations' needs the preceding sentence to be understood and the span has a trailing referent; it also omits 'as appropriate with relevant international assistance', which is minor."
    },
    "grounding": 4,
    "numerical_fidelity": 5,
    "overall": 13,
    "precision": 4,
    "reason": "The answer is a near-verbatim span from paragraph 19, but 'these violations' needs the preceding sentence to be understood and the span has a trailing referent; it also omits 'as appropriate with relevant international assistance', which is minor."
  },
  {
    "_response": {
      "grounding": 5,
      "index": 1,
      "numerical_fidelity": 5,
      "precision": 4,
      "reason": "The answer is a verbatim contiguous span from paragraph 20 that fully answers the question; it includes the fairly long 'safety of as well as unhindered...' clause, which is slightly more than the minimum."
    },
    "grounding": 5,
    "numerical_fidelity": 5,
    "overall": 14,
    "precision": 4,
    "reason": "The answer is a verbatim contiguous span from paragraph 20 that fully answers the question; it includes the fairly long 'safety of as well as unhindered...' clause, which is slightly more than the minimum."
  }
]
````

### mode/un/2004/s/res/1565_2004_#11/semantic: quality — completed

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
      "candidate_id": "q_a32e1a7923c7db5e292f3d63",
      "checks": {
        "metadata": "pass",
        "mode": "pass",
        "support": "pass"
      },
      "index": 0,
      "problems": [
        "lexical_distance: \"violations\" became \"abuses\", but the predicate structure still follows paragraph 19 closely.",
        "anchoring_and_time: the question omits MONUC and the specific violations, which leaves the episode somewhat broad."
      ],
      "score_notes": {
        "anchoring_and_time": "The DRC is a concrete anchor and 2004 is an absolute year that matches the resolution. The question does not name MONUC or the specific violations, so the episode is somewhat broad.",
        "consequence": "The answer states the demand that all parties and governments take all necessary steps to bring perpetrators to justice. This directly matches accountability and is concrete. It omits the \"with international assistance\" qualifier, and the demand is somewhat generic.",
        "lexical_distance": "The question reuses \"abuses against civilians\" and \"Democratic Republic of the Congo\" (a necessary name). \"Accountability\" for \"bring to justice\" is a fair paraphrase. The answer is a verbatim span, which is expected.",
        "linguistic_quality": "Clear and idiomatic. \"Seek accountability\" is slightly loose but acceptable.",
        "search_realism": "A natural outsider question about the accountability response to abuses against civilians in the DRC. One bounded intent. The phrase \"the Security Council\" is slightly loose, since the demand is in a resolution."
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
    "reason": "search_realism: A natural outsider question about the accountability response to abuses against civilians in the DRC. One bounded intent. The phrase \"the Security Council\" is slightly loose, since the demand is in a resolution.; anchoring_and_time: The DRC is a concrete anchor and 2004 is an absolute year that matches the resolution. The question does not name MONUC or the specific violations, so the episode is somewhat broad.; consequence: The answer states the demand that all parties and governments take all necessary steps to bring perpetrators to justice. This directly matches accountability and is concrete. It omits the \"with international assistance\" qualifier, and the demand is somewhat generic.; lexical_distance: The question reuses \"abuses against civilians\" and \"Democratic Republic of the Congo\" (a necessary name). \"Accountability\" for \"bring to justice\" is a fair paraphrase. The answer is a verbatim span, which is expected.; linguistic_quality: Clear and idiomatic. \"Seek accountability\" is slightly loose but acceptable.",
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
      "candidate_id": "q_f7adce56a22a9efe6adbc44d",
      "checks": {
        "metadata": "pass",
        "mode": "pass",
        "support": "pass"
      },
      "index": 1,
      "problems": [
        "mode: the answer span is about 40 words, which is long for a short span, though it is contiguous and needed for the conditions.",
        "lexical_distance: \"throughout the Democratic Republic of the Congo\" is copied directly from the target block."
      ],
      "score_notes": {
        "anchoring_and_time": "MONUC, the DRC and 2004 give a concrete, well-resolved anchor with a clear time pin.",
        "consequence": "The answer states the duties to cooperate fully, to ensure safety, and to give unhindered, immediate access throughout the territory. This matches the expected relationship and is informative. It is a long paraphrase-free span, but it stays contiguous.",
        "lexical_distance": "The question reuses \"MONUC\", \"throughout the Democratic Republic of the Congo\" and \"operations\" (as \"field operations\"). \"Enable\" is a paraphrase of \"cooperate/access\". Some copied scaffolding remains.",
        "linguistic_quality": "Fluent and clear. \"How were parties expected to enable\" is a little stiff.",
        "search_realism": "A natural question about what parties must do to let MONUC operate. It has a single bounded intent and is a good response/stakeholder need."
      },
      "scores": {
        "anchoring_and_time": 5,
        "consequence": 4,
        "lexical_distance": 3,
        "linguistic_quality": 4,
        "search_realism": 4
      }
    },
    "anchoring_and_time": 5,
    "consequence": 4,
    "lexical_distance": 3,
    "linguistic_quality": 4,
    "overall": 20,
    "reason": "search_realism: A natural question about what parties must do to let MONUC operate. It has a single bounded intent and is a good response/stakeholder need.; anchoring_and_time: MONUC, the DRC and 2004 give a concrete, well-resolved anchor with a clear time pin.; consequence: The answer states the duties to cooperate fully, to ensure safety, and to give unhindered, immediate access throughout the territory. This matches the expected relationship and is informative. It is a long paraphrase-free span, but it stays contiguous.; lexical_distance: The question reuses \"MONUC\", \"throughout the Democratic Republic of the Congo\" and \"operations\" (as \"field operations\"). \"Enable\" is a paraphrase of \"cooperate/access\". Some copied scaffolding remains.; linguistic_quality: Fluent and clear. \"How were parties expected to enable\" is a little stiff.",
    "search_realism": 4
  }
]
````

### mode/un/2007/a/res/62/137#12/lookup: faithfulness — completed

````json
[
  {
    "_response": {
      "grounding": 4,
      "index": 0,
      "numerical_fidelity": 5,
      "precision": 4,
      "reason": "The answer is a verbatim span from the target block (the Doha 2008 conference name); the question requires a small inference to identify it as the 'development-financing' event among two 2008 events. It includes the location and year as adjacent context that is fairly necessary but not strictly needed, and all identifiers match exactly."
    },
    "grounding": 4,
    "numerical_fidelity": 5,
    "overall": 13,
    "precision": 4,
    "reason": "The answer is a verbatim span from the target block (the Doha 2008 conference name); the question requires a small inference to identify it as the 'development-financing' event among two 2008 events. It includes the location and year as adjacent context that is fairly necessary but not strictly needed, and all identifiers match exactly."
  }
]
````

### mode/un/2007/a/res/62/137#12/lookup: quality — completed

````json
[
  {
    "_batch_diversity": "not_applicable",
    "_contract": "compact",
    "_keys": [
      "practitioner_realism",
      "anchoring",
      "consequence",
      "informativeness",
      "linguistic_quality"
    ],
    "_response": {
      "candidate_id": "q_01aec55607b5106b2c10b347",
      "checks": {
        "metadata": "uncertain",
        "mode": "fail",
        "support": "pass"
      },
      "index": 0,
      "problems": [
        "mode: The content is an urging to pay attention to gender perspectives, which is a generic encouragement. The question targets a list item rather than a concrete measure.",
        "mode: The '2008 development-financing' cue is ambiguous between Doha and the Accra aid effectiveness forum.",
        "anchoring: 'gender perspectives' is a weak, generic anchor. The substantive subject is only the loosely described resolution.",
        "metadata: The anchor 'gender perspectives' appears in both renderings outside the slot, but it is a weak anchor. The type 'situation_scope_or_coverage' is plausible.",
        "informativeness: The question cue does not uniquely identify the event."
      ],
      "score_notes": {
        "anchoring": "The base description is 'the 2007 General Assembly resolution on Beijing follow-up'. It is fairly distinctive but loose, and the only other anchor is the generic 'gender perspectives'. The '2008 development-financing' cue fits both Doha and arguably Accra, so the subject is only partly specified.",
        "consequence": "The content is an urging to give attention to gender perspectives in preparation for events. It is a generic exhortation whose only specific element is a list of event names, with no concrete deliverable or deadline.",
        "informativeness": "The answer is a verbatim span naming the Doha conference and is correct. However, the question cues ('2008', 'development-financing') do not exclude the Accra forum, so the ask is not fully resolved. The answer also includes the full event title, which is fine.",
        "linguistic_quality": "The English is readable. 'Identify for attention to gender perspectives' is awkward and imprecise, and the resolution's urging is not reflected. The base is about 19 words.",
        "practitioner_realism": "The question is a narrow lookup of a list item. It is ambiguous because two 2008 events (Doha and Accra) fit the cue, and the Accra forum is also about aid, so the ask is not a single clear need."
      },
      "scores": {
        "anchoring": 2,
        "consequence": 2,
        "informativeness": 3,
        "linguistic_quality": 3,
        "practitioner_realism": 2
      }
    },
    "anchoring": 2,
    "consequence": 2,
    "informativeness": 3,
    "linguistic_quality": 3,
    "overall": 12,
    "practitioner_realism": 2,
    "reason": "practitioner_realism: The question is a narrow lookup of a list item. It is ambiguous because two 2008 events (Doha and Accra) fit the cue, and the Accra forum is also about aid, so the ask is not a single clear need.; anchoring: The base description is 'the 2007 General Assembly resolution on Beijing follow-up'. It is fairly distinctive but loose, and the only other anchor is the generic 'gender perspectives'. The '2008 development-financing' cue fits both Doha and arguably Accra, so the subject is only partly specified.; consequence: The content is an urging to give attention to gender perspectives in preparation for events. It is a generic exhortation whose only specific element is a list of event names, with no concrete deliverable or deadline.; informativeness: The answer is a verbatim span naming the Doha conference and is correct. However, the question cues ('2008', 'development-financing') do not exclude the Accra forum, so the ask is not fully resolved. The answer also includes the full event title, which is fine.; linguistic_quality: The English is readable. 'Identify for attention to gender perspectives' is awkward and imprecise, and the resolution's urging is not reflected. The base is about 19 words."
  }
]
````

### mode/un/2007/gc_12/c_1/sr_1#10/practitioner: faithfulness — completed

````json
[
  {
    "_response": {
      "grounding": 4,
      "index": 0,
      "numerical_fidelity": 5,
      "precision": 4,
      "reason": "The target says the core mandate is to support industrial development, including in LDCs, so the answer is directly supported; the 'December 2007' framing is a minor metadata-based addition, and the answer omits the LDC clause."
    },
    "grounding": 4,
    "numerical_fidelity": 5,
    "overall": 13,
    "precision": 4,
    "reason": "The target says the core mandate is to support industrial development, including in LDCs, so the answer is directly supported; the 'December 2007' framing is a minor metadata-based addition, and the answer omits the LDC clause."
  },
  {
    "_response": {
      "grounding": 3,
      "index": 1,
      "numerical_fidelity": 5,
      "precision": 3,
      "reason": "The text says they emphasize 'development of supply capacity and trade-related infrastructure'; the answer is a correct fragment but is slightly incomplete, because supply capacity is left out, and the question's 'what infrastructure' wording is imprecise."
    },
    "grounding": 3,
    "numerical_fidelity": 5,
    "overall": 11,
    "precision": 3,
    "reason": "The text says they emphasize 'development of supply capacity and trade-related infrastructure'; the answer is a correct fragment but is slightly incomplete, because supply capacity is left out, and the question's 'what infrastructure' wording is imprecise."
  }
]
````

### mode/un/2007/gc_12/c_1/sr_1#10/practitioner: quality — completed

````json
[
  {
    "_batch_diversity": "fail",
    "_contract": "compact",
    "_keys": [
      "practitioner_realism",
      "anchoring_and_time",
      "consequence",
      "informativeness",
      "linguistic_quality"
    ],
    "_response": {
      "candidate_id": "q_0569d21e0332cb31bac20191",
      "checks": {
        "metadata": "pass",
        "mode": "fail",
        "support": "pass"
      },
      "index": 0,
      "problems": [
        "mode: the content is a generic restatement of UNIDO's mandate, not a specific norm element.",
        "mode: the time pin is the meeting date, and the question does not attribute the statement to the LDC ministers, so the source is unclear.",
        "informativeness: the answer is essentially a restatement of the question's terms."
      ],
      "score_notes": {
        "anchoring_and_time": "Anchors are UNIDO's core mandate and least developed countries, and 'December 2007' is the meeting date. The regime is implied by UNIDO. The date is the statement's date rather than a norm date, and the speaker/body is unidentified, so scope is slightly ambiguous.",
        "consequence": "The content is a generic statement of UNIDO's core mandate in a statement by the LDC ministers. It gives no specific measure, task or figure, so it is thin and generic.",
        "informativeness": "The answer 'support industrial development' largely restates the question's terms ('core mandate'). It is a predictable default completion, and 'including in least developed countries' is already in the question.",
        "linguistic_quality": "The English is grammatical, but 'what did ... mandate cover' is slightly awkward and imprecise.",
        "practitioner_realism": "It asks a bounded scope question, but it reads like a comprehension prompt. The answer is a generic mandate statement, and 'cover' is a vague slot."
      },
      "scores": {
        "anchoring_and_time": 3,
        "consequence": 2,
        "informativeness": 2,
        "linguistic_quality": 3,
        "practitioner_realism": 3
      }
    },
    "anchoring_and_time": 3,
    "consequence": 2,
    "informativeness": 2,
    "linguistic_quality": 3,
    "overall": 13,
    "practitioner_realism": 3,
    "reason": "practitioner_realism: It asks a bounded scope question, but it reads like a comprehension prompt. The answer is a generic mandate statement, and 'cover' is a vague slot.; anchoring_and_time: Anchors are UNIDO's core mandate and least developed countries, and 'December 2007' is the meeting date. The regime is implied by UNIDO. The date is the statement's date rather than a norm date, and the speaker/body is unidentified, so scope is slightly ambiguous.; consequence: The content is a generic statement of UNIDO's core mandate in a statement by the LDC ministers. It gives no specific measure, task or figure, so it is thin and generic.; informativeness: The answer 'support industrial development' largely restates the question's terms ('core mandate'). It is a predictable default completion, and 'including in least developed countries' is already in the question.; linguistic_quality: The English is grammatical, but 'what did ... mandate cover' is slightly awkward and imprecise."
  },
  {
    "_batch_diversity": "fail",
    "_contract": "compact",
    "_keys": [
      "practitioner_realism",
      "anchoring_and_time",
      "consequence",
      "informativeness",
      "linguistic_quality"
    ],
    "_response": {
      "candidate_id": "q_b59897075876974a207fe978",
      "checks": {
        "metadata": "pass",
        "mode": "fail",
        "support": "pass"
      },
      "index": 1,
      "problems": [
        "mode: the question asks what the frameworks 'emphasized', which is a speech-act stance, not a norm-state.",
        "mode: the content is a descriptive characterization, not a specific norm element.",
        "informativeness: the answer omits 'supply capacity', which the source pairs with infrastructure, so it is partial."
      ],
      "score_notes": {
        "anchoring_and_time": "Aid for Trade and the Enhanced Integrated Framework are two anchors, and 'December 2007' is given. The date is the meeting date, not an event date. The statement is unattributed, since the LDC ministers' declaration is not named.",
        "consequence": "The content is a descriptive characterization of the frameworks' emphasis, not a norm, task or figure. It has low operational value.",
        "informativeness": "The answer 'trade-related infrastructure' is correct, but the source also names supply capacity, so the answer is incomplete. The question asks for 'what infrastructure', which suggests a narrower fact than the source gives.",
        "linguistic_quality": "The English is clear and natural, though 'emphasize' is a speech-act verb and the question is slightly stiff.",
        "practitioner_realism": "It is a bounded single-fact question, but it asks what the frameworks 'emphasized', which is a speech-act stance. It reads like a comprehension prompt."
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
    "reason": "practitioner_realism: It is a bounded single-fact question, but it asks what the frameworks 'emphasized', which is a speech-act stance. It reads like a comprehension prompt.; anchoring_and_time: Aid for Trade and the Enhanced Integrated Framework are two anchors, and 'December 2007' is given. The date is the meeting date, not an event date. The statement is unattributed, since the LDC ministers' declaration is not named.; consequence: The content is a descriptive characterization of the frameworks' emphasis, not a norm, task or figure. It has low operational value.; informativeness: The answer 'trade-related infrastructure' is correct, but the source also names supply capacity, so the answer is incomplete. The question asks for 'what infrastructure', which suggests a narrower fact than the source gives.; linguistic_quality: The English is clear and natural, though 'emphasize' is a speech-act verb and the question is slightly stiff."
  }
]
````

### mode/un/2007/gc_12/c_1/sr_1#10/semantic: faithfulness — completed

````json
[
  {
    "_response": {
      "grounding": 4,
      "index": 0,
      "numerical_fidelity": 5,
      "precision": 4,
      "reason": "The answer quotes one sentence of the target block almost verbatim and is well grounded; the question's '2007' comes from the document context, and the answer keeps the 'We call upon' phrasing, which adds slight extra wording."
    },
    "grounding": 4,
    "numerical_fidelity": 5,
    "overall": 13,
    "precision": 4,
    "reason": "The answer quotes one sentence of the target block almost verbatim and is well grounded; the question's '2007' comes from the document context, and the answer keeps the 'We call upon' phrasing, which adds slight extra wording."
  },
  {
    "_response": {
      "grounding": 5,
      "index": 1,
      "numerical_fidelity": 5,
      "precision": 4,
      "reason": "The answer is a direct verbatim sentence from the target block; the clause about urging donors to contribute is a small extra beyond the 'financing arrangement' asked."
    },
    "grounding": 5,
    "numerical_fidelity": 5,
    "overall": 14,
    "precision": 4,
    "reason": "The answer is a direct verbatim sentence from the target block; the clause about urging donors to contribute is a small extra beyond the 'financing arrangement' asked."
  }
]
````

### mode/un/2007/gc_12/c_1/sr_1#10/semantic: quality — completed

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
      "candidate_id": "q_9315369173b771e117dc87f5",
      "checks": {
        "metadata": "pass",
        "mode": "pass",
        "support": "pass"
      },
      "index": 0,
      "problems": [
        "anchoring_and_time: \"expected\" lacks a named attributing party, so the claim is not attributed to the LDC Ministerial Conference."
      ],
      "score_notes": {
        "anchoring_and_time": "Names UNIDO, Aid for Trade, the Enhanced Integrated Framework and 2007, which is supported by the context (Ministerial Conference, November 2007). The anchor is concrete. \"Expected\" does not say who expected it (the LDC ministers).",
        "consequence": "The answer states the concrete role: work closely with Framework countries, act as implementing agency, and focus on industrial capacity and standards/conformity infrastructure. It matches the role question, though the question omits the LDC ministers who made the call.",
        "lexical_distance": "The question copies the phrases \"Aid for Trade and the Enhanced Integrated Framework\" and \"least developed countries\" from the block. These are largely names and official terms. The predicate is reworded, but the answer mirrors the question's scaffolding.",
        "linguistic_quality": "Clear, idiomatic and economical at 20 words. The passive \"was expected to support\" is slightly vague.",
        "search_realism": "A natural, bounded question about UNIDO's expected role in the LDC trade-capacity framework, asking for duties rather than a datum. The LDC declaration's authorship is not attributed."
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
    "reason": "search_realism: A natural, bounded question about UNIDO's expected role in the LDC trade-capacity framework, asking for duties rather than a datum. The LDC declaration's authorship is not attributed.; anchoring_and_time: Names UNIDO, Aid for Trade, the Enhanced Integrated Framework and 2007, which is supported by the context (Ministerial Conference, November 2007). The anchor is concrete. \"Expected\" does not say who expected it (the LDC ministers).; consequence: The answer states the concrete role: work closely with Framework countries, act as implementing agency, and focus on industrial capacity and standards/conformity infrastructure. It matches the role question, though the question omits the LDC ministers who made the call.; lexical_distance: The question copies the phrases \"Aid for Trade and the Enhanced Integrated Framework\" and \"least developed countries\" from the block. These are largely names and official terms. The predicate is reworded, but the answer mirrors the question's scaffolding.; linguistic_quality: Clear, idiomatic and economical at 20 words. The passive \"was expected to support\" is slightly vague.",
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
      "candidate_id": "q_6d53c089534e390a01000b2d",
      "checks": {
        "metadata": "pass",
        "mode": "pass",
        "support": "pass"
      },
      "index": 1,
      "problems": [
        "anchoring_and_time: The proposer is not named and the anchor \"least developed countries\" is broad, so the question is underspecified against other LDC-related UNIDO proposals."
      ],
      "score_notes": {
        "anchoring_and_time": "Has UNIDO, LDCs and 2007, but the issue is generic: it does not say who proposed the arrangement or the context of the LDC ministerial declaration, so the episode is materially broad. The anchor \"least developed countries\" is a broad topic term.",
        "consequence": "The answer states the concrete proposal: a special Trust Fund for LDCs, with donors urged to contribute. It fits \"what arrangement was proposed\". The added donor appeal is partly exhortation but is a concrete part of the mechanism.",
        "lexical_distance": "\"Least developed countries\" and \"UNIDO\" are copied, which is acceptable. \"Dedicated financing arrangement\" paraphrases \"special Trust Fund\" well, but the answer itself mirrors the source sentence.",
        "linguistic_quality": "Fluent and concise at 14 words. \"Proposed ... through UNIDO\" is slightly loose.",
        "search_realism": "A plausible search for a specific proposed financing mechanism. It borders on asking for a named item (\"what arrangement\"), though the need is still conceptual."
      },
      "scores": {
        "anchoring_and_time": 3,
        "consequence": 4,
        "lexical_distance": 3,
        "linguistic_quality": 4,
        "search_realism": 3
      }
    },
    "anchoring_and_time": 3,
    "consequence": 4,
    "lexical_distance": 3,
    "linguistic_quality": 4,
    "overall": 17,
    "reason": "search_realism: A plausible search for a specific proposed financing mechanism. It borders on asking for a named item (\"what arrangement\"), though the need is still conceptual.; anchoring_and_time: Has UNIDO, LDCs and 2007, but the issue is generic: it does not say who proposed the arrangement or the context of the LDC ministerial declaration, so the episode is materially broad. The anchor \"least developed countries\" is a broad topic term.; consequence: The answer states the concrete proposal: a special Trust Fund for LDCs, with donors urged to contribute. It fits \"what arrangement was proposed\". The added donor appeal is partly exhortation but is a concrete part of the mechanism.; lexical_distance: \"Least developed countries\" and \"UNIDO\" are copied, which is acceptable. \"Dedicated financing arrangement\" paraphrases \"special Trust Fund\" well, but the answer itself mirrors the source sentence.; linguistic_quality: Fluent and concise at 14 words. \"Proposed ... through UNIDO\" is slightly loose.",
    "search_realism": 3
  }
]
````

### mode/un/2010/ccpr/c/sr_2695#25/practitioner: faithfulness — completed

````json
[
  {
    "_response": {
      "grounding": 4,
      "index": 0,
      "numerical_fidelity": 5,
      "precision": 4,
      "reason": "The Chair said 'perhaps paragraph 57 should contain a reference to article 18', so the answer is a direct span. It is a tentative suggestion ('perhaps'), which the answer presents as settled, though the block adds that members seemed to agree. The answer includes a minor 'a reference to' phrase, and 'article 18' is exact."
    },
    "grounding": 4,
    "numerical_fidelity": 5,
    "overall": 13,
    "precision": 4,
    "reason": "The Chair said 'perhaps paragraph 57 should contain a reference to article 18', so the answer is a direct span. It is a tentative suggestion ('perhaps'), which the answer presents as settled, though the block adds that members seemed to agree. The answer includes a minor 'a reference to' phrase, and 'article 18' is exact."
  },
  {
    "_response": {
      "grounding": 4,
      "index": 1,
      "numerical_fidelity": 5,
      "precision": 4,
      "reason": "The span 'the present paragraph 57 should be moved to the section covering article 18' is directly supported. Like the first pair, it presents a tentative proposal as settled, though the members' apparent agreement is noted. The identifier 'article 18' is exact."
    },
    "grounding": 4,
    "numerical_fidelity": 5,
    "overall": 13,
    "precision": 4,
    "reason": "The span 'the present paragraph 57 should be moved to the section covering article 18' is directly supported. Like the first pair, it presents a tentative proposal as settled, though the members' apparent agreement is noted. The identifier 'article 18' is exact."
  }
]
````

### mode/un/2010/ccpr/c/sr_2695#25/practitioner: quality — completed

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
      "candidate_id": "q_a1239c01971b70bd5c6a4488",
      "checks": {
        "metadata": "fail",
        "mode": "fail",
        "support": "pass"
      },
      "index": 0,
      "problems": [
        "mode: the question uses the paragraph number \"paragraph 57\" as a document locator, which is forbidden.",
        "mode: the regime (the Covenant, reporting guidelines) is unnamed and there are not two genuine substantive anchors.",
        "mode: the stance is a drafting-history question about what a paragraph was to contain, not a norm in force.",
        "metadata: the anchors \"paragraph 57\" (a locator) and \"guidance to States\" (generic) are not genuine substantive anchors."
      ],
      "score_notes": {
        "anchoring_and_time": "The date 15 March 2010 gives a usable time pin. \"Paragraph 57\" is a locator, not a substantive anchor. No document is named (draft reporting guidelines), nor the Covenant or the military-service subject, so \"paragraph 57\" cannot be resolved from the question. Only \"Human Rights Committee\" is substantive.",
        "consequence": "The content is a tentative drafting proposal about a cross-reference in internal reporting guidelines. It is thin and procedural, with little professional use as a norm or task.",
        "informativeness": "The answer, a reference to article 18, is in the block. However, the question does not fix the topic (alternative military service), so the answer is a bare article number. The Chair's \"perhaps\" makes the status tentative, although members agreed.",
        "linguistic_quality": "The question is understandable but awkward: \"what article reference was paragraph 57 to contain\" is stiff, and \"guidance to States\" is vague.",
        "practitioner_realism": "It asks about the drafting of an internal guideline paragraph identified only by its number. That is an editing-history question, not a natural norm-state need, and \"what article reference\" is a vague slot."
      },
      "scores": {
        "anchoring_and_time": 2,
        "consequence": 2,
        "informativeness": 3,
        "linguistic_quality": 3,
        "practitioner_realism": 2
      }
    },
    "anchoring_and_time": 2,
    "consequence": 2,
    "informativeness": 3,
    "linguistic_quality": 3,
    "overall": 12,
    "practitioner_realism": 2,
    "reason": "practitioner_realism: It asks about the drafting of an internal guideline paragraph identified only by its number. That is an editing-history question, not a natural norm-state need, and \"what article reference\" is a vague slot.; anchoring_and_time: The date 15 March 2010 gives a usable time pin. \"Paragraph 57\" is a locator, not a substantive anchor. No document is named (draft reporting guidelines), nor the Covenant or the military-service subject, so \"paragraph 57\" cannot be resolved from the question. Only \"Human Rights Committee\" is substantive.; consequence: The content is a tentative drafting proposal about a cross-reference in internal reporting guidelines. It is thin and procedural, with little professional use as a norm or task.; informativeness: The answer, a reference to article 18, is in the block. However, the question does not fix the topic (alternative military service), so the answer is a bare article number. The Chair's \"perhaps\" makes the status tentative, although members agreed.; linguistic_quality: The question is understandable but awkward: \"what article reference was paragraph 57 to contain\" is stiff, and \"guidance to States\" is vague."
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
      "candidate_id": "q_6949f73b9ea14b91da17373c",
      "checks": {
        "metadata": "fail",
        "mode": "fail",
        "support": "pass"
      },
      "index": 1,
      "problems": [
        "mode: the question uses the paragraph number \"paragraph 57\" as a forbidden locator.",
        "mode: there are fewer than two substantive anchors and the regime is unnamed.",
        "mode: it targets a drafting relocation, not an applicable norm.",
        "metadata: only one genuine anchor, \"Human Rights Committee\", is present; \"paragraph 57\" is a locator. The type actor_body_or_procedure is marginally compatible."
      ],
      "score_notes": {
        "anchoring_and_time": "The date 15 March 2010 is given. \"Paragraph 57\" is a locator and unresolved, since no document or subject is named. Apart from \"Human Rights Committee\" there is no substantive anchor, and the regime is not identified.",
        "consequence": "The content is a procedural relocation of a paragraph within guidelines, with minimal substantive value.",
        "informativeness": "The answer, the section covering article 18, is in the block. It is a short placement detail that the question does not make meaningful. The Chair said \"perhaps\", and agreement was only implied.",
        "linguistic_quality": "The question is clear but sparse and slightly awkward (\"in the Human Rights Committee's guidance on 15 March 2010\").",
        "practitioner_realism": "It asks where a numbered paragraph was to be moved within internal guidelines. That is a drafting-mechanics question, not a practitioner norm-state need."
      },
      "scores": {
        "anchoring_and_time": 2,
        "consequence": 2,
        "informativeness": 3,
        "linguistic_quality": 3,
        "practitioner_realism": 2
      }
    },
    "anchoring_and_time": 2,
    "consequence": 2,
    "informativeness": 3,
    "linguistic_quality": 3,
    "overall": 12,
    "practitioner_realism": 2,
    "reason": "practitioner_realism: It asks where a numbered paragraph was to be moved within internal guidelines. That is a drafting-mechanics question, not a practitioner norm-state need.; anchoring_and_time: The date 15 March 2010 is given. \"Paragraph 57\" is a locator and unresolved, since no document or subject is named. Apart from \"Human Rights Committee\" there is no substantive anchor, and the regime is not identified.; consequence: The content is a procedural relocation of a paragraph within guidelines, with minimal substantive value.; informativeness: The answer, the section covering article 18, is in the block. It is a short placement detail that the question does not make meaningful. The Chair said \"perhaps\", and agreement was only implied.; linguistic_quality: The question is clear but sparse and slightly awkward (\"in the Human Rights Committee's guidance on 15 March 2010\")."
  }
]
````

### mode/un/2013/a/res/68/18#1/practitioner: faithfulness — failed

````json
null
````

### mode/un/2013/a/res/68/18#1/practitioner: faithfulness_json_recovery — completed

````json
[
  {
    "_response": {
      "grounding": 4,
      "index": 0,
      "numerical_fidelity": 5,
      "precision": 5,
      "reason": "'six months' is stated directly in paragraph 2; the question's '2013' is not in the target block, which is a minor flaw."
    },
    "grounding": 4,
    "numerical_fidelity": 5,
    "overall": 14,
    "precision": 5,
    "reason": "'six months' is stated directly in paragraph 2; the question's '2013' is not in the target block, which is a minor flaw."
  },
  {
    "_response": {
      "grounding": 4,
      "index": 1,
      "numerical_fidelity": 5,
      "precision": 5,
      "reason": "'one year' is stated directly in paragraph 4; the question's '2013' is not in the target block, which is a minor flaw."
    },
    "grounding": 4,
    "numerical_fidelity": 5,
    "overall": 14,
    "precision": 5,
    "reason": "'one year' is stated directly in paragraph 4; the question's '2013' is not in the target block, which is a minor flaw."
  }
]
````

### mode/un/2013/a/res/68/18#1/practitioner: quality — completed

````json
[
  {
    "_batch_diversity": "fail",
    "_contract": "compact",
    "_keys": [
      "practitioner_realism",
      "anchoring_and_time",
      "consequence",
      "informativeness",
      "linguistic_quality"
    ],
    "_response": {
      "candidate_id": "q_7f0a66b92f6e73beedb29c5a",
      "checks": {
        "metadata": "pass",
        "mode": "pass",
        "support": "pass"
      },
      "index": 0,
      "problems": [
        "anchoring_and_time: the least developed country category is not named in the question, so the regime is unnamed.",
        "linguistic_quality: \"exceptional preparation\" is an imprecise rendering of the \"additional preparatory period granted on an exceptional basis\"."
      ],
      "score_notes": {
        "anchoring_and_time": "\"2013\" is a usable year and \"Equatorial Guinea\" and \"three-year preparatory period for graduation\" are anchors. However, the LDC category regime is never named, so the regime is implicit. \"Exceptional preparation\" is a mildly ambiguous scope.",
        "consequence": "A concrete, specific dated transition term for a named country; useful for graduation/smooth-transition work.",
        "informativeness": "\"Six months\" fully answers the question and is explicit in the block. It is short, but is a genuine figure that is not a default completion.",
        "linguistic_quality": "\"Exceptional preparation before the three-year preparatory period\" is awkward and imprecise; it should say \"additional preparatory period\".",
        "practitioner_realism": "Bounded need about the additional preparatory period, but \"exceptional preparation\" is a vague slot and a stilted paraphrase of the additional preparatory period before the three-year period."
      },
      "scores": {
        "anchoring_and_time": 3,
        "consequence": 4,
        "informativeness": 4,
        "linguistic_quality": 3,
        "practitioner_realism": 3
      }
    },
    "anchoring_and_time": 3,
    "consequence": 4,
    "informativeness": 4,
    "linguistic_quality": 3,
    "overall": 17,
    "practitioner_realism": 3,
    "reason": "practitioner_realism: Bounded need about the additional preparatory period, but \"exceptional preparation\" is a vague slot and a stilted paraphrase of the additional preparatory period before the three-year period.; anchoring_and_time: \"2013\" is a usable year and \"Equatorial Guinea\" and \"three-year preparatory period for graduation\" are anchors. However, the LDC category regime is never named, so the regime is implicit. \"Exceptional preparation\" is a mildly ambiguous scope.; consequence: A concrete, specific dated transition term for a named country; useful for graduation/smooth-transition work.; informativeness: \"Six months\" fully answers the question and is explicit in the block. It is short, but is a genuine figure that is not a default completion.; linguistic_quality: \"Exceptional preparation before the three-year preparatory period\" is awkward and imprecise; it should say \"additional preparatory period\"."
  },
  {
    "_batch_diversity": "fail",
    "_contract": "compact",
    "_keys": [
      "practitioner_realism",
      "anchoring_and_time",
      "consequence",
      "informativeness",
      "linguistic_quality"
    ],
    "_response": {
      "candidate_id": "q_143e53079a9d5ed0a059f3e4",
      "checks": {
        "metadata": "pass",
        "mode": "pass",
        "support": "pass"
      },
      "index": 1,
      "problems": [
        "anchoring_and_time: the least developed country category is not named in the question, so the regime is unnamed.",
        "linguistic_quality: \"exceptional preparation\" is an imprecise rendering of the \"additional preparatory period granted on an exceptional basis\"."
      ],
      "score_notes": {
        "anchoring_and_time": "\"2013\" is a usable year and \"Vanuatu\" and \"three-year preparatory period\" are anchors. However, the LDC regime is not named and the scope of \"exceptional preparation\" is a bit loose.",
        "consequence": "A concrete, specific transition period for a named country; useful for graduation-related professional work.",
        "informativeness": "\"One year\" is explicit in the block and fully answers the question. It is a short but genuine figure.",
        "linguistic_quality": "Awkward phrase \"exceptional preparation before the three-year preparatory period\"; not as precise as \"additional preparatory period\".",
        "practitioner_realism": "Same bounded need for Vanuatu, but the vague \"exceptional preparation\" wording is a stilted paraphrase of the additional preparatory period."
      },
      "scores": {
        "anchoring_and_time": 3,
        "consequence": 4,
        "informativeness": 4,
        "linguistic_quality": 3,
        "practitioner_realism": 3
      }
    },
    "anchoring_and_time": 3,
    "consequence": 4,
    "informativeness": 4,
    "linguistic_quality": 3,
    "overall": 17,
    "practitioner_realism": 3,
    "reason": "practitioner_realism: Same bounded need for Vanuatu, but the vague \"exceptional preparation\" wording is a stilted paraphrase of the additional preparatory period.; anchoring_and_time: \"2013\" is a usable year and \"Vanuatu\" and \"three-year preparatory period\" are anchors. However, the LDC regime is not named and the scope of \"exceptional preparation\" is a bit loose.; consequence: A concrete, specific transition period for a named country; useful for graduation-related professional work.; informativeness: \"One year\" is explicit in the block and fully answers the question. It is a short but genuine figure.; linguistic_quality: Awkward phrase \"exceptional preparation before the three-year preparatory period\"; not as precise as \"additional preparatory period\"."
  }
]
````
