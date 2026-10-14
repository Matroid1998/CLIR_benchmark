# Independent chemistry retrieval-question evaluation contract

Evaluate questions made from patent abstracts in English, French, Spanish, German and Chinese. These are source-grounded retrieval tasks in chemistry, materials, chemical engineering, associated biology, assays and technical instruments. Assess fidelity to the supplied source, not whether a patent claim has independent scientific validation. No outside patent text or web research is available as evidence.

## What each component does

The decider assesses independently whether each source can support at least one strong question for each of seven modes. Multiple modes can be suitable simultaneously; none may be suitable. A deterministic balancing policy then chooses one eligible mode. Assess both inappropriate eligibility and missed suitable modes. A bad generated question alone does not demonstrate bad eligibility if a good question in that mode was feasible. Do not reward balance as evidence of correctness.

The generator writes one to three candidates in the assigned mode or abstains. Judge the actual question, answer and evidence, including standalone usefulness, faithful and complete resolution, natural language, mode fit and the literal output contract. Judge all submitted candidates and document coverage; distinguish appropriate abstention from missed usable opportunities. Do not judge merely by the chosen best candidate.

The verifier independently assesses faithfulness and quality. Compare its criteria, explanations and mode/support/metadata checks to your own source-based judgments. Credit correct detections and avoid treating all flags as automatically correct. Distinguish permissive grading, unwarranted rejection and inconsistent explanations. Its numeric total does not override a failed validity check.

## Intended modes

- lookup: a missing technical detail, application, condition, constituent or specification of an identified system.
- process_retrieval: operations connecting a known input/state to an output/state; a clearly described single transformation can qualify. A full executable laboratory protocol is unnecessary when the question asks at an abstract procedural level.
- conceptual: an explicitly stated role, effect, interaction, structure-property relationship or reason. Simple component roles qualify; do not require an unstated molecular mechanism.
- constraint_search: an identifiable material, formulation, system or treatment approach satisfying an objective and at least one meaningful requirement. The candidate may be an operational approach.
- comparison: two identifiable sides on one common, source-supported dimension. A supported sameness comparison is valid.
- assertion_verification: the evidence status of a scoped, uncertain technical assertion. supported and contradicted require decisive matching-scope evidence; absence of information does not prove contradiction. A deliberately uncertain false proposition is not a hallucinated settled premise.
- source_finding: the exact publication identity behind a connected, independently intelligible technical clue. Do not require a globally unique clue or firstness/legal-status claims.

## Source, question and evidence

Read the full relevant supplied abstract, including adjacent qualifications, repeated values, tables and alternative embodiments. Do not invent missing structure, parameters, numerical bases, relationships or source corrections. Values must retain their actual units, bounds, bases and material-stage associations. Source conflict affects the relevant need; it need not invalidate an unrelated sound question.

The question must make sense without the source, title or annotations beside it. A recognizable named class, composition or operational system can provide enough identity; not every question needs a complete molecular scaffold. Unexplained local labels fail only when essential identity depends on them. Do not infer missing question context from an annotation. Known constraints, uncertain assertions and source clues can properly contain facts; they are not automatically answer leakage. There must remain a useful unknown.

The actual submitted answer and selected evidence must resolve the requested scope. Surrounding source text can identify an explicit referent, but cannot supply material answer content missing from the selected span. An exact quotation can be incomplete or mismatched. Necessary intervening text in a sufficient contiguous extract is allowed. Do not penalize a long answer merely for preserving needed steps or two comparison sides. Preserve optionality, alternatives, attribution and the scope of the disclosed example.

## Literal contract

- evidence is one exact, unmodified contiguous substring of one supplied body unit, retaining original language and markup.
- For content-answer modes, when the source is already in the output language, answer equals evidence exactly and answer_is_translation is false. A meaning-preserving paraphrase or shorter subspan can violate this contract while remaining scientifically faithful.
- If the source requires translation, answer faithfully translates that one evidence span and answer_is_translation is true. evidence itself is still copied exactly.
- For source_finding, answer and source_identifier equal the supplied publication number, answer_is_translation is false, and separate body evidence supports the material clue.
- anchor, process_start, process_goal, objective, each constraints entry, each comparison_entities entry, and assertion must be exact question substrings when present. An interrogative assertion may use the full question without its final question mark. These fields also need to serve their named purpose. Category fields such as relationship_type or question_type are enums, not required substrings.

Distinguish representation/annotation repairs from semantic errors. Do not label benign paraphrase fabricated chemistry or automatically lower semantic grounding because of a literal-only defect.

## Recorded verifier rubric

The recorded chemistry-clir-exceptional-r2 rubric has three faithfulness criteria (grounding, precision, numerical_fidelity), each 1-5, and five quality criteria, each 1-5. The first three quality criteria vary by mode; focus_and_economy and linguistic_quality are shared. A 4 is strong ordinary success; a 5 requires concrete exceptional evidence. A 3 reflects a specific nonfatal limitation. A 1 or 2 reflects substantive failure. An inapplicable numerical criterion uses 4 as a compatibility value. Thus 32/40 can be an entirely strong ordinary result. Do not require an arbitrary spread or exceptional-score quota.

Quality mode/support/metadata checks are pass, fail or uncertain. Known invalidity is fail; uncertainty needs a genuine unresolved source/input issue. The scoring contract is provisional. Model grades are observations to audit, not ground truth.

## Independent overall ratings

After inspecting the sources and candidates independently, assign separate generator, verifier and decider ratings on a 0-10 scale using your own expert judgment. State your reasoning and confidence. Suggested interpretation: 9-10 excellent and dependable with few minor limitations; 8 strong with identifiable limited weaknesses; 7 useful but recurring repairs; 5-6 mixed reliability with meaningful recurring errors; below 5 frequent central failures. Half points are allowed. Do not convert a pipeline score into an independent rating or force a target rating/distribution.

Give exact counts and examples where possible, clearly separating observed counts, interpretive judgments and conclusions that the sample cannot establish. Report limitations of a single abstract, multilingual review, abstentions, source selection and unmeasured retrieval performance. Your role is independent evaluation, not prompt optimization.
