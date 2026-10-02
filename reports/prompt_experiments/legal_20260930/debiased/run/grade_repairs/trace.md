# Legal question generation and grading: complete call trace

Run status: **completed**. Recorded calls: **0**.

[Questions and grades](results.csv) · [Full provider responses and run data](llm_calls.json) · Resumable state: `run.sqlite`.

Every recorded call, including retries, appears in chronological order. API status describes transport; stage status describes final parsing and validation. The JSON export retains every recorded provider response field. Any candidates beyond a requested quota remain in the raw outcomes.

## Run configuration and source targets

````json
{
  "eurlex": 50,
  "generator": "gpt-5.6-luna",
  "jev_model": "~typesafe/jev-latest",
  "keep": 3,
  "language": "en",
  "max_per_document": 1,
  "meeting_modes": "all",
  "prompt_registry": {
    "bundle": "debiased",
    "bundle_sha256": "d4deb32e2668a73f124204f949674307a885cfc03c3b7f17178534150ef470b1",
    "label": "legal-20260930-debiased",
    "prompts": {
      "eurlex/decider/generator": {
        "name": "clir-legal-eurlex-decider-generator-en",
        "sha256": "892009920fb64b7cd0c81129cb037619a102d6bb02bb5fbaad00474bbd5cf31a",
        "version": 2
      },
      "eurlex/decider/jev": {
        "name": "clir-legal-eurlex-decider-jev-en",
        "sha256": "d5e57a94077bb199aeec14a5df975da80d220440f23e05d687a8634fea0ee16c",
        "version": 2
      },
      "eurlex/faithfulness": {
        "name": "clir-legal-eurlex-faithfulness-batch-en",
        "sha256": "ff5f30bc175b59a055e9a990127b62d541efaa75e08fbb50a288e12c4384e5a9",
        "version": 2
      },
      "eurlex/generation/fact_pattern": {
        "name": "clir-legal-eurlex-generation-fact_pattern-en",
        "sha256": "2b976b322cd36a7266854ed71481d891d5a17824f1dac810c8e5a42b9431504f",
        "version": 2
      },
      "eurlex/generation/fact_pattern/de": {
        "name": "clir-legal-eurlex-generation-fact_pattern-de",
        "sha256": "43fefbeb978df6b4d613e65069841686491e762bad38a4cf1171ea07d31b9bef",
        "version": 2
      },
      "eurlex/generation/fact_pattern/es": {
        "name": "clir-legal-eurlex-generation-fact_pattern-es",
        "sha256": "8a4a59262f98cca530633ff599dede127914d5d7378f3f9f471947a2cc0f572a",
        "version": 2
      },
      "eurlex/generation/fact_pattern/fr": {
        "name": "clir-legal-eurlex-generation-fact_pattern-fr",
        "sha256": "003d0523f3172d5cd18b85f3fdb5f618e99c0bacd368c966628b6e592fa99cee",
        "version": 2
      },
      "eurlex/generation/fact_pattern/zh": {
        "name": "clir-legal-eurlex-generation-fact_pattern-zh",
        "sha256": "800c52b222bcd8c9c25fea09ed0504e100bc9b20b6f7fce8d0ddf90d1b26e0eb",
        "version": 2
      },
      "eurlex/generation/lookup": {
        "name": "clir-legal-eurlex-generation-lookup-en",
        "sha256": "42098d0db141007ccbc262a423bc9b188f5ff2aa2e5badbc4b4812033edd3605",
        "version": 2
      },
      "eurlex/generation/lookup/de": {
        "name": "clir-legal-eurlex-generation-lookup-de",
        "sha256": "466643a5ae1f950925129cb3c1d9570934a5dcd548856d9e833c78f9a9caa290",
        "version": 2
      },
      "eurlex/generation/lookup/es": {
        "name": "clir-legal-eurlex-generation-lookup-es",
        "sha256": "70a5f36b78fe5602645417514ea66ea0599d5864281abcb4aa401790af9d6eda",
        "version": 2
      },
      "eurlex/generation/lookup/fr": {
        "name": "clir-legal-eurlex-generation-lookup-fr",
        "sha256": "c39539d3bdf1edb7b22514559fbeade6a046465c250b73b11c1c4e4b2174b85b",
        "version": 2
      },
      "eurlex/generation/lookup/zh": {
        "name": "clir-legal-eurlex-generation-lookup-zh",
        "sha256": "008dc1dcbb74f9863199b026f7adb2583050136eaa1bb918c0bf41b752dac3a0",
        "version": 2
      },
      "eurlex/quality/fact_pattern": {
        "name": "clir-legal-eurlex-quality-fact_pattern-en",
        "sha256": "80be78fb2b112042153dc98ab63613b37dd35c4d96493cf722d6b453dcc004d8",
        "version": 2
      },
      "eurlex/quality/lookup": {
        "name": "clir-legal-eurlex-quality-lookup-en",
        "sha256": "e2a53fa6b4bf713264d8cd393fda6ad761fc146e88288569e43d1993a0af81bd",
        "version": 2
      },
      "un/decider/generator": {
        "name": "clir-legal-un-decider-generator-en",
        "sha256": "551c0ccae2a55332cf6048f5d99028433c1bb939d4af4ff272ed380337143585",
        "version": 2
      },
      "un/decider/jev": {
        "name": "clir-legal-un-decider-jev-en",
        "sha256": "afb32a59f0aad7606d2742b0aa51b01f29d3316652c72b2fcffdd655e14c82d5",
        "version": 2
      },
      "un/faithfulness": {
        "name": "clir-legal-un-faithfulness-batch-en",
        "sha256": "93c94344805ba111890beaa702b15f1c148c61e53245b7b3c54406fd7696fdbf",
        "version": 2
      },
      "un/generation/descriptive": {
        "name": "clir-legal-un-generation-descriptive-en",
        "sha256": "33ae092af1f6b3821788794dc5ab5c5e81e6fd75d043a69a24555dae182c0957",
        "version": 2
      },
      "un/generation/descriptive/de": {
        "name": "clir-legal-un-generation-descriptive-de",
        "sha256": "9f5e9ea4b2e7a67c380656a8cec34463492ee83e174e8db188b0764eabd60fd0",
        "version": 2
      },
      "un/generation/descriptive/es": {
        "name": "clir-legal-un-generation-descriptive-es",
        "sha256": "82b9ceb4a693856e7d1bb44e8084f40103d837ae9d4048734b11a7adf4760a6d",
        "version": 2
      },
      "un/generation/descriptive/fr": {
        "name": "clir-legal-un-generation-descriptive-fr",
        "sha256": "01f33b6ca8fb66afe1a8db9b4c65fc1997067834748da90d21b9c34bbf4aeb08",
        "version": 2
      },
      "un/generation/descriptive/zh": {
        "name": "clir-legal-un-generation-descriptive-zh",
        "sha256": "788cd99c769153fa0abea925d18e4b522b6919aa5b67d82267e4b126c3e5a971",
        "version": 2
      },
      "un/generation/lookup": {
        "name": "clir-legal-un-generation-lookup-en",
        "sha256": "6f8ee6797635bd087a340b6ba3256ec58341616bd2bfdf8376027bb8b6bd699e",
        "version": 2
      },
      "un/generation/lookup/de": {
        "name": "clir-legal-un-generation-lookup-de",
        "sha256": "7f760bbfebb981823e96fd0a2a28583aadaaf7259639a668d83043c06bea65ea",
        "version": 2
      },
      "un/generation/lookup/es": {
        "name": "clir-legal-un-generation-lookup-es",
        "sha256": "cf66a8e9b2ed592da6b89d22984aa43bcbe8a3cc4a16256b9f0bbaa13f559083",
        "version": 2
      },
      "un/generation/lookup/fr": {
        "name": "clir-legal-un-generation-lookup-fr",
        "sha256": "13b9e03f7761f6636ce9cef24ddba720ac5fc6cf1db7dee8b977087afb273f1b",
        "version": 2
      },
      "un/generation/lookup/zh": {
        "name": "clir-legal-un-generation-lookup-zh",
        "sha256": "8073bad190efe5c35da03fe8c8fefeedf49e4a124adae50426884d88ee982538",
        "version": 2
      },
      "un/generation/practitioner": {
        "name": "clir-legal-un-generation-practitioner-en",
        "sha256": "4453fa3dec8e4eb1b3427e945f1e39e32b0ab048fe579b68c3b8c6239a3a2a7c",
        "version": 2
      },
      "un/generation/practitioner/de": {
        "name": "clir-legal-un-generation-practitioner-de",
        "sha256": "43e174381a7d9fb1ede5432bff921aa7cf84904264c03f9e5a98355b61901f79",
        "version": 2
      },
      "un/generation/practitioner/es": {
        "name": "clir-legal-un-generation-practitioner-es",
        "sha256": "918fb6a4b591cd019f6d06012aa76dd74798cc15947c1af83d1f244ebc25fe8a",
        "version": 2
      },
      "un/generation/practitioner/fr": {
        "name": "clir-legal-un-generation-practitioner-fr",
        "sha256": "d82e89e6bb6d173e84a7e52f640347d57ee1d74954264ee549b8f9cad81401ac",
        "version": 2
      },
      "un/generation/practitioner/zh": {
        "name": "clir-legal-un-generation-practitioner-zh",
        "sha256": "08b06f038b5183955ace29c1ff6841e2be100f13e3a12d38af6e6274a5256049",
        "version": 2
      },
      "un/generation/semantic": {
        "name": "clir-legal-un-generation-semantic-en",
        "sha256": "a8005d77bd9a39d30e512e50eb8b1d1652261e10f4da6c5f37493a39e6caf3a5",
        "version": 2
      },
      "un/generation/semantic/de": {
        "name": "clir-legal-un-generation-semantic-de",
        "sha256": "353b6527439a4a03e1ac36f283a7168c0b8d490e0bf08a6e41f171d3722d2016",
        "version": 2
      },
      "un/generation/semantic/es": {
        "name": "clir-legal-un-generation-semantic-es",
        "sha256": "ca58d653bde75e9c3034e5b134d1b2c1113994d5a31643e49d604a98ef5c8ee3",
        "version": 2
      },
      "un/generation/semantic/fr": {
        "name": "clir-legal-un-generation-semantic-fr",
        "sha256": "123b00126c0f95be85e3125b7bad9ca4efab3feb1230de7a62a22ddd84648e96",
        "version": 2
      },
      "un/generation/semantic/zh": {
        "name": "clir-legal-un-generation-semantic-zh",
        "sha256": "3648d1c00dd08731d999a1f3a4174a2d1be20b3560b0cbe8e496a2a26e737d84",
        "version": 2
      },
      "un/generation/technical": {
        "name": "clir-legal-un-generation-technical-en",
        "sha256": "d1342668e6b6e37c0a0384c5ec99932ab3b652629c7b17506f1bcc39951d3534",
        "version": 2
      },
      "un/generation/technical/de": {
        "name": "clir-legal-un-generation-technical-de",
        "sha256": "cf958f05ea552acf007c63a0d6e3348781f191919bcb440b769e2ed0640d2646",
        "version": 2
      },
      "un/generation/technical/es": {
        "name": "clir-legal-un-generation-technical-es",
        "sha256": "fe48723f1f4d0f64ed92608f06d1df59a267a4d0e6e68dd37191763b8a94ad8c",
        "version": 2
      },
      "un/generation/technical/fr": {
        "name": "clir-legal-un-generation-technical-fr",
        "sha256": "be3ec8a50372f18db783f73ee87b7503461e0c1ae812108bb0e46376921b7e65",
        "version": 2
      },
      "un/generation/technical/zh": {
        "name": "clir-legal-un-generation-technical-zh",
        "sha256": "8dd91cd9af75fddf9cbea58f89bf0e88ff5fd626f286202822aeba0c0e9e4c16",
        "version": 2
      },
      "un/quality/descriptive": {
        "name": "clir-legal-un-quality-descriptive-en",
        "sha256": "5c0b3bfa22579ca330233bfaf525d32c1d520f8bf36d48c04d43f19a87febd5a",
        "version": 2
      },
      "un/quality/lookup": {
        "name": "clir-legal-un-quality-lookup-en",
        "sha256": "58897421a24d70994ffcd742e0479f922cdd596c88a72fd4ecf41bf5c2711261",
        "version": 2
      },
      "un/quality/practitioner": {
        "name": "clir-legal-un-quality-practitioner-en",
        "sha256": "cf902d2248b1ed234d78c0dd9968060e47f605252f2424a271e35731ddb750b7",
        "version": 2
      },
      "un/quality/semantic": {
        "name": "clir-legal-un-quality-semantic-en",
        "sha256": "022a71c28d27661bc162c8dc36836dd7320c3c3fd148adb4efea555a8aa3d8e2",
        "version": 2
      },
      "un/quality/technical": {
        "name": "clir-legal-un-quality-technical-en",
        "sha256": "f705288ccd9a16f99f505f20dea44cbe3662bada6b5c65322d99f784d56891f7",
        "version": 2
      }
    },
    "provider": "mlflow",
    "registry_uri": "sqlite:////home/mehdi/Projects/CLIR_benchmark/.clir/prompts.db",
    "schema_version": 1
  },
  "prompts_sha256": "64c5c1736ca3dd72df4905722025a4f4d846ce7d0a1edc09abb8600dc6be734c",
  "retries": 3,
  "seed": 20260930,
  "selection_source": "/home/mehdi/Projects/CLIR_benchmark/reports/decider_screening/fresh100_20260930_examples/selection.json",
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
  "inputs_by_model": {},
  "generation_overproduction": []
}
````

## Final stage results

| Task | Stage | Attempts | Final status | Error |
|---|---|---:|---|---|
| mode/eurlex/http://data.europa.eu/eli/dir/2014/50/art_5/oj/fact_pattern | faithfulness | 1 | completed |  |
| mode/eurlex/http://data.europa.eu/eli/dir/2014/50/art_5/oj/fact_pattern | quality_index_recovery | 1 | completed |  |
| mode/eurlex/http://data.europa.eu/eli/reg/2009/436/art_36/oj/fact_pattern | faithfulness | 1 | completed |  |
| mode/eurlex/http://data.europa.eu/eli/reg/2009/436/art_36/oj/fact_pattern | quality_index_recovery | 1 | completed |  |
| mode/eurlex/http://data.europa.eu/eli/reg/2011/333/art_2/oj/fact_pattern | faithfulness | 1 | completed |  |
| mode/eurlex/http://data.europa.eu/eli/reg/2011/333/art_2/oj/fact_pattern | quality_index_recovery | 1 | completed |  |
| mode/un/2001/s/res/1376_2001_#2/practitioner | faithfulness | 1 | completed |  |
| mode/un/2001/s/res/1376_2001_#2/practitioner | quality_index_recovery | 1 | completed |  |
| mode/un/2002/a/res/56/188#8/semantic | faithfulness | 1 | completed |  |
| mode/un/2002/a/res/56/188#8/semantic | quality_index_recovery | 1 | completed |  |
| mode/un/2003/a/res/57/300#10/semantic | faithfulness | 1 | completed |  |
| mode/un/2003/a/res/57/300#10/semantic | quality_index_recovery | 1 | completed |  |
| mode/un/2004/a/c_2/58/sr_24#18/semantic | faithfulness | 1 | completed |  |
| mode/un/2004/a/c_2/58/sr_24#18/semantic | quality_index_recovery | 1 | completed |  |
| mode/un/2004/s/2004/505#15/semantic | faithfulness | 1 | completed |  |
| mode/un/2004/s/2004/505#15/semantic | quality_index_recovery | 1 | completed |  |
| mode/un/2004/s/2004/674#6/practitioner | faithfulness | 1 | completed |  |
| mode/un/2004/s/2004/674#6/practitioner | quality_index_recovery | 1 | completed |  |
| mode/un/2007/a/res/62/137#12/practitioner | faithfulness | 1 | completed |  |
| mode/un/2007/a/res/62/137#12/practitioner | quality_index_recovery | 1 | completed |  |
| mode/un/2008/a/ac_109/2008/sr_2#1/semantic | faithfulness | 1 | completed |  |
| mode/un/2008/a/ac_109/2008/sr_2#1/semantic | quality_index_recovery | 1 | completed |  |
| mode/un/2013/a/res/67/199#12/semantic | faithfulness | 1 | completed |  |
| mode/un/2013/a/res/67/199#12/semantic | quality_index_recovery | 1 | completed |  |
| mode/un/2014/s/res/2140__2014_#13/semantic | faithfulness | 1 | completed |  |
| mode/un/2014/s/res/2140__2014_#13/semantic | quality_index_recovery | 1 | completed |  |

## Parsed pipeline outputs

### mode/eurlex/http://data.europa.eu/eli/dir/2014/50/art_5/oj/fact_pattern: faithfulness — completed

````json
[
  {
    "_response": {
      "grounding": 4,
      "index": 0,
      "numerical_fidelity": 5,
      "precision": 5,
      "reason": "Extracted from Art. 5(1), with correct provenance. The 'Subject to paragraphs 3 and 4' qualifier is omitted and 'can remain' is permissive, which is a minor ambiguity against the question's 'must'. The span is tight."
    },
    "grounding": 4,
    "numerical_fidelity": 5,
    "overall": 14,
    "precision": 5,
    "reason": "Extracted from Art. 5(1), with correct provenance. The 'Subject to paragraphs 3 and 4' qualifier is omitted and 'can remain' is permissive, which is a minor ambiguity against the question's 'must'. The span is tight."
  },
  {
    "_response": {
      "grounding": 5,
      "index": 1,
      "numerical_fidelity": 5,
      "precision": 5,
      "reason": "Matches Art. 5(2)(c) verbatim: the inflation-adjusted case is handled by adjusting the dormant rights, subject to the proportionate limit. Provenance is correct and nothing is added."
    },
    "grounding": 5,
    "numerical_fidelity": 5,
    "overall": 15,
    "precision": 5,
    "reason": "Matches Art. 5(2)(c) verbatim: the inflation-adjusted case is handled by adjusting the dormant rights, subject to the proportionate limit. Provenance is correct and nothing is added."
  },
  {
    "_response": {
      "grounding": 5,
      "index": 2,
      "numerical_fidelity": 5,
      "precision": 4,
      "reason": "Directly supported by Art. 5(3), quoted almost verbatim. It repeats the question's conditions, which is a bit of extra context, but it is grounded and correctly attributed."
    },
    "grounding": 5,
    "numerical_fidelity": 5,
    "overall": 14,
    "precision": 4,
    "reason": "Directly supported by Art. 5(3), quoted almost verbatim. It repeats the question's conditions, which is a bit of extra context, but it is grounded and correctly attributed."
  }
]
````

### mode/eurlex/http://data.europa.eu/eli/dir/2014/50/art_5/oj/fact_pattern: quality_index_recovery — completed

````json
[
  {
    "_batch_diversity": "fail",
    "_contract": "compact",
    "_keys": [
      "situation",
      "regime_fixing",
      "terminology_and_distance",
      "focus",
      "linguistic_quality"
    ],
    "_response": {
      "candidate_id": "q_d130da6b83269ec72123c059",
      "checks": {
        "metadata": "pass",
        "mode": "fail",
        "support": "pass"
      },
      "index": 0,
      "problems": [
        "No real third-person protagonist or case, so the question is abstract.",
        "The answer span is a Member State-directed phrase ('can remain') and is subject to paragraphs 3 and 4 exceptions. The question does not exclude those exceptions.",
        "The question wrongly ties the employment relationship to the scheme."
      ],
      "score_notes": {
        "focus": "There is one ask, but 'What must happen to those rights?' is vague. Paragraph 3 allows payout of a capital sum, and paragraph 4 allows derogation, so the answer is not bounded.",
        "linguistic_quality": "The prose is clear but generic, and the wording is slightly awkward: 'employment relationship with a supplementary pension scheme'. The employment relationship is with the employer, not the scheme.",
        "regime_fixing": "'Supplementary pension scheme', 'outgoing worker' and 'vested pension rights' point to the domain. The question does not separate the general rule from the Member State option to pay a capital sum or from collective-agreement derogations, so a material distinction is missing.",
        "situation": "There is no concrete protagonist or case. It is an abstract rule restated as a story, and its particulars restate the same premise. Cap of 3 applies, and it is weaker still.",
        "terminology_and_distance": "The question reuses the article's own terms, which is acceptable. It also gives away the answer, because 'vested pension rights' in 'that scheme' nearly restates the answer span."
      },
      "scores": {
        "focus": 3,
        "linguistic_quality": 3,
        "regime_fixing": 3,
        "situation": 2,
        "terminology_and_distance": 2
      }
    },
    "focus": 3,
    "linguistic_quality": 3,
    "overall": 13,
    "reason": "situation: There is no concrete protagonist or case. It is an abstract rule restated as a story, and its particulars restate the same premise. Cap of 3 applies, and it is weaker still.; regime_fixing: 'Supplementary pension scheme', 'outgoing worker' and 'vested pension rights' point to the domain. The question does not separate the general rule from the Member State option to pay a capital sum or from collective-agreement derogations, so a material distinction is missing.; terminology_and_distance: The question reuses the article's own terms, which is acceptable. It also gives away the answer, because 'vested pension rights' in 'that scheme' nearly restates the answer span.; focus: There is one ask, but 'What must happen to those rights?' is vague. Paragraph 3 allows payout of a capital sum, and paragraph 4 allows derogation, so the answer is not bounded.; linguistic_quality: The prose is clear but generic, and the wording is slightly awkward: 'employment relationship with a supplementary pension scheme'. The employment relationship is with the employer, not the scheme.",
    "regime_fixing": 3,
    "situation": 2,
    "terminology_and_distance": 2
  },
  {
    "_batch_diversity": "fail",
    "_contract": "compact",
    "_keys": [
      "situation",
      "regime_fixing",
      "terminology_and_distance",
      "focus",
      "linguistic_quality"
    ],
    "_response": {
      "candidate_id": "q_905e20f76eb2a1e87b4139b4",
      "checks": {
        "metadata": "pass",
        "mode": "fail",
        "support": "pass"
      },
      "index": 1,
      "problems": [
        "There is no concrete protagonist, so the situation is essentially an abstract restatement of paragraph 2(c).",
        "The answer span depends on the paragraph 2 lead-in ('treated in line with...', 'or in other ways considered fair'). It is only one of several permitted treatments, so the word 'must' overstates the rule.",
        "The question does not give the supplementary pension scheme context."
      ],
      "score_notes": {
        "focus": "There is a single bounded ask: how the dormant rights' value is to be handled.",
        "linguistic_quality": "The prose is understandable. The sentence is clunky, since 'the worker's rights have become dormant after the employment relationship ended' repeats information and reads as scaffolding.",
        "regime_fixing": "'Dormant', 'accrued pension rights' and 'inflation rate' place the question within the pension-rights domain. There is no explicit supplementary pension scheme or other scope term.",
        "situation": "No actor or concrete case beyond a generic outgoing worker. It is an abstract rule in a story, so the cap of 3 applies. The inflation-adjustment fact does make a rule-relevant particular.",
        "terminology_and_distance": "Terms are appropriate and the inflation fact is paraphrased from the text. However, 'adjusted... in accordance with the inflation rate' comes close to the answer wording 'adjusting... accordingly'."
      },
      "scores": {
        "focus": 4,
        "linguistic_quality": 3,
        "regime_fixing": 3,
        "situation": 2,
        "terminology_and_distance": 3
      }
    },
    "focus": 4,
    "linguistic_quality": 3,
    "overall": 15,
    "reason": "situation: No actor or concrete case beyond a generic outgoing worker. It is an abstract rule in a story, so the cap of 3 applies. The inflation-adjustment fact does make a rule-relevant particular.; regime_fixing: 'Dormant', 'accrued pension rights' and 'inflation rate' place the question within the pension-rights domain. There is no explicit supplementary pension scheme or other scope term.; terminology_and_distance: Terms are appropriate and the inflation fact is paraphrased from the text. However, 'adjusted... in accordance with the inflation rate' comes close to the answer wording 'adjusting... accordingly'.; focus: There is a single bounded ask: how the dormant rights' value is to be handled.; linguistic_quality: The prose is understandable. The sentence is clunky, since 'the worker's rights have become dormant after the employment relationship ended' repeats information and reads as scaffolding.",
    "regime_fixing": 3,
    "situation": 2,
    "terminology_and_distance": 3
  },
  {
    "_batch_diversity": "fail",
    "_contract": "compact",
    "_keys": [
      "situation",
      "regime_fixing",
      "terminology_and_distance",
      "focus",
      "linguistic_quality"
    ],
    "_response": {
      "candidate_id": "q_367057e49c3a42952e2090ef",
      "checks": {
        "metadata": "fail",
        "mode": "pass",
        "support": "uncertain"
      },
      "index": 2,
      "problems": [
        "The answer span is addressed to Member States ('Member States may allow'), but the question asks whether the scheme may pay. Whether the Member State has exercised the option is not stated, so support is uncertain.",
        "The question type 'scope_or_applicability' is a weak fit for a permission question, which should be obligation_or_prohibition (permission/authorization).",
        "The question closely tracks the article's conditions and so gives away the answer."
      ],
      "score_notes": {
        "focus": "There is one yes/no ask. The answer as a Member State option is not exactly 'may the scheme', since the power depends on national implementation, which the question does not state.",
        "linguistic_quality": "Fluent, precise and natural prose.",
        "regime_fixing": "'Supplementary pension scheme', 'vested pension rights', 'outgoing worker' and 'threshold established by the Member State' identify the regime clearly.",
        "situation": "There is a scheme as the actor and several rule-relevant facts: threshold, informed consent and charges. It is still generic and lacks a named protagonist.",
        "terminology_and_distance": "The facts almost copy the article's conditions: 'does not exceed a threshold established by the Member State concerned', 'informed consent', 'applicable charges'. The question therefore largely restates the permission and gives it away."
      },
      "scores": {
        "focus": 3,
        "linguistic_quality": 4,
        "regime_fixing": 4,
        "situation": 3,
        "terminology_and_distance": 2
      }
    },
    "focus": 3,
    "linguistic_quality": 4,
    "overall": 16,
    "reason": "situation: There is a scheme as the actor and several rule-relevant facts: threshold, informed consent and charges. It is still generic and lacks a named protagonist.; regime_fixing: 'Supplementary pension scheme', 'vested pension rights', 'outgoing worker' and 'threshold established by the Member State' identify the regime clearly.; terminology_and_distance: The facts almost copy the article's conditions: 'does not exceed a threshold established by the Member State concerned', 'informed consent', 'applicable charges'. The question therefore largely restates the permission and gives it away.; focus: There is one yes/no ask. The answer as a Member State option is not exactly 'may the scheme', since the power depends on national implementation, which the question does not state.; linguistic_quality: Fluent, precise and natural prose.",
    "regime_fixing": 4,
    "situation": 3,
    "terminology_and_distance": 2
  }
]
````

### mode/eurlex/http://data.europa.eu/eli/reg/2009/436/art_36/oj/fact_pattern: faithfulness — completed

````json
[
  {
    "_response": {
      "grounding": 5,
      "index": 0,
      "numerical_fidelity": 5,
      "precision": 5,
      "reason": "The span is taken directly from Article 36(1), and the declared article 36 is correct."
    },
    "grounding": 5,
    "numerical_fidelity": 5,
    "overall": 15,
    "precision": 5,
    "reason": "The span is taken directly from Article 36(1), and the declared article 36 is correct."
  },
  {
    "_response": {
      "grounding": 4,
      "index": 1,
      "numerical_fidelity": 5,
      "precision": 5,
      "reason": "Article 36(3) supports the answer and cites Article 41(1), which includes bottling (f). Both 36 and 41 are declared. The answer does not name bottling, so the link to it is only implicit, which is a minor ambiguity."
    },
    "grounding": 4,
    "numerical_fidelity": 5,
    "overall": 14,
    "precision": 5,
    "reason": "Article 36(3) supports the answer and cites Article 41(1), which includes bottling (f). Both 36 and 41 are declared. The answer does not name bottling, so the link to it is only implicit, which is a minor ambiguity."
  },
  {
    "_response": {
      "grounding": 5,
      "index": 2,
      "numerical_fidelity": 5,
      "precision": 5,
      "reason": "The span is the second sentence of Article 36(3) and matches it exactly. Article 36 is the only article used and is declared."
    },
    "grounding": 5,
    "numerical_fidelity": 5,
    "overall": 15,
    "precision": 5,
    "reason": "The span is the second sentence of Article 36(3) and matches it exactly. Article 36 is the only article used and is declared."
  }
]
````

### mode/eurlex/http://data.europa.eu/eli/reg/2009/436/art_36/oj/fact_pattern: quality_index_recovery — completed

````json
[
  {
    "_batch_diversity": "pass",
    "_contract": "compact",
    "_keys": [
      "situation",
      "regime_fixing",
      "terminology_and_distance",
      "focus",
      "linguistic_quality"
    ],
    "_response": {
      "candidate_id": "q_60dc7bf3576c75352470ebac",
      "checks": {
        "metadata": "pass",
        "mode": "pass",
        "support": "pass"
      },
      "index": 0,
      "problems": [
        "The facts track the article's wording closely, so the question leaks part of the answer.",
        "The particulars are just the rule's conditions restated."
      ],
      "score_notes": {
        "focus": "There is a single ask: what records must be kept.",
        "linguistic_quality": "The prose is clear and natural. It is slightly redundant, because \"legal person\" adds little.",
        "regime_fixing": "\"wine products\" and \"holds ... for commercial purposes\" identify the wine regime well enough. It does not distinguish registers from other obligations, since \"records\" is generic.",
        "situation": "A wine merchant holding wine for commercial purposes is a plausible protagonist with relevant facts. However, the facts are thin and nearly restate the rule's conditions, so this reads close to an abstract rule.",
        "terminology_and_distance": "The question copies the article's scaffolding (\"legal person\", \"holds wine products\", \"commercial purposes\"). It also uses \"records\", which is close to the answer's \"registers\", so the question nearly gives away the answer."
      },
      "scores": {
        "focus": 5,
        "linguistic_quality": 4,
        "regime_fixing": 3,
        "situation": 3,
        "terminology_and_distance": 2
      }
    },
    "focus": 5,
    "linguistic_quality": 4,
    "overall": 17,
    "reason": "situation: A wine merchant holding wine for commercial purposes is a plausible protagonist with relevant facts. However, the facts are thin and nearly restate the rule's conditions, so this reads close to an abstract rule.; regime_fixing: \"wine products\" and \"holds ... for commercial purposes\" identify the wine regime well enough. It does not distinguish registers from other obligations, since \"records\" is generic.; terminology_and_distance: The question copies the article's scaffolding (\"legal person\", \"holds wine products\", \"commercial purposes\"). It also uses \"records\", which is close to the answer's \"registers\", so the question nearly gives away the answer.; focus: There is a single ask: what records must be kept.; linguistic_quality: The prose is clear and natural. It is slightly redundant, because \"legal person\" adds little.",
    "regime_fixing": 3,
    "situation": 3,
    "terminology_and_distance": 2
  },
  {
    "_batch_diversity": "pass",
    "_contract": "compact",
    "_keys": [
      "situation",
      "regime_fixing",
      "terminology_and_distance",
      "focus",
      "linguistic_quality"
    ],
    "_response": {
      "candidate_id": "q_391e7df988b799c8a0390756",
      "checks": {
        "metadata": "pass",
        "mode": "pass",
        "support": "pass"
      },
      "index": 1,
      "problems": [
        "The answer span contains the phrase \"as referred to in paragraph 1\" and the reference \"Article 41(1)\". The span is a bit stitched, but it is contiguous."
      ],
      "score_notes": {
        "focus": "The ask is one information need, what must be recorded. It covers both the batch movements and the operations, but these come from a single sentence of the article.",
        "linguistic_quality": "The prose is natural and precise. It is slightly long.",
        "regime_fixing": "\"winery\", \"wine products\" and \"bottling\" clearly identify the wine registers rule. The question has no identifiers.",
        "situation": "A winery that holds wine and bottles on its premises is a concrete, plausible case. Both the holding and the bottling are relevant particulars.",
        "terminology_and_distance": "\"registers\", \"entering or leaving\" and \"bottling operation\" are necessary terms. There is only mild closeness to the article's wording, and no leakage of the answer."
      },
      "scores": {
        "focus": 4,
        "linguistic_quality": 4,
        "regime_fixing": 4,
        "situation": 4,
        "terminology_and_distance": 4
      }
    },
    "focus": 4,
    "linguistic_quality": 4,
    "overall": 20,
    "reason": "situation: A winery that holds wine and bottles on its premises is a concrete, plausible case. Both the holding and the bottling are relevant particulars.; regime_fixing: \"winery\", \"wine products\" and \"bottling\" clearly identify the wine registers rule. The question has no identifiers.; terminology_and_distance: \"registers\", \"entering or leaving\" and \"bottling operation\" are necessary terms. There is only mild closeness to the article's wording, and no leakage of the answer.; focus: The ask is one information need, what must be recorded. It covers both the batch movements and the operations, but these come from a single sentence of the article.; linguistic_quality: The prose is natural and precise. It is slightly long.",
    "regime_fixing": 4,
    "situation": 4,
    "terminology_and_distance": 4
  },
  {
    "_batch_diversity": "pass",
    "_contract": "compact",
    "_keys": [
      "situation",
      "regime_fixing",
      "terminology_and_distance",
      "focus",
      "linguistic_quality"
    ],
    "_response": {
      "candidate_id": "q_21143ca1721cebbf702d1d26",
      "checks": {
        "metadata": "pass",
        "mode": "pass",
        "support": "pass"
      },
      "index": 2,
      "problems": [],
      "score_notes": {
        "focus": "There is one bounded ask: which supporting material must be presentable.",
        "linguistic_quality": "The prose is natural, economical and clear.",
        "regime_fixing": "\"entry and withdrawal registers\" and \"wine\" fix the regime. The question has no identifiers.",
        "situation": "A wine producer with an annotation for a delivered consignment is a realistic compliance question. Both particulars are relevant.",
        "terminology_and_distance": "Register terminology is necessary. The question does not give away the answer, which concerns supporting documents. \"Supporting material\" is only a mild echo of the article's wording."
      },
      "scores": {
        "focus": 5,
        "linguistic_quality": 5,
        "regime_fixing": 4,
        "situation": 4,
        "terminology_and_distance": 4
      }
    },
    "focus": 5,
    "linguistic_quality": 5,
    "overall": 22,
    "reason": "situation: A wine producer with an annotation for a delivered consignment is a realistic compliance question. Both particulars are relevant.; regime_fixing: \"entry and withdrawal registers\" and \"wine\" fix the regime. The question has no identifiers.; terminology_and_distance: Register terminology is necessary. The question does not give away the answer, which concerns supporting documents. \"Supporting material\" is only a mild echo of the article's wording.; focus: There is one bounded ask: which supporting material must be presentable.; linguistic_quality: The prose is natural, economical and clear.",
    "regime_fixing": 4,
    "situation": 4,
    "terminology_and_distance": 4
  }
]
````

### mode/eurlex/http://data.europa.eu/eli/reg/2011/333/art_2/oj/fact_pattern: faithfulness — completed

````json
[
  {
    "_response": {
      "grounding": 5,
      "index": 0,
      "numerical_fidelity": 5,
      "precision": 5,
      "reason": "The answer quotes the Article 2(c) definition of 'holder' exactly, and the declared article 2 is correct."
    },
    "grounding": 5,
    "numerical_fidelity": 5,
    "overall": 15,
    "precision": 5,
    "reason": "The answer quotes the Article 2(c) definition of 'holder' exactly, and the declared article 2 is correct."
  },
  {
    "_response": {
      "grounding": 5,
      "index": 1,
      "numerical_fidelity": 5,
      "precision": 5,
      "reason": "The answer quotes the Article 2(d) definition of 'producer' verbatim, and the declared article 2 is correct."
    },
    "grounding": 5,
    "numerical_fidelity": 5,
    "overall": 15,
    "precision": 5,
    "reason": "The answer quotes the Article 2(d) definition of 'producer' verbatim, and the declared article 2 is correct."
  },
  {
    "_response": {
      "grounding": 5,
      "index": 2,
      "numerical_fidelity": 5,
      "precision": 5,
      "reason": "The answer quotes the Article 2(h) definition of 'consignment' verbatim, and the declared article 2 is correct."
    },
    "grounding": 5,
    "numerical_fidelity": 5,
    "overall": 15,
    "precision": 5,
    "reason": "The answer quotes the Article 2(h) definition of 'consignment' verbatim, and the declared article 2 is correct."
  }
]
````

### mode/eurlex/http://data.europa.eu/eli/reg/2011/333/art_2/oj/fact_pattern: quality_index_recovery — completed

````json
[
  {
    "_batch_diversity": "fail",
    "_contract": "compact",
    "_keys": [
      "situation",
      "regime_fixing",
      "terminology_and_distance",
      "focus",
      "linguistic_quality"
    ],
    "_response": {
      "candidate_id": "q_866de03cc5f2749fb2f4d033",
      "checks": {
        "metadata": "pass",
        "mode": "pass",
        "support": "pass"
      },
      "index": 0,
      "problems": [
        "The question names the defined term 'holder' and echoes the definition's wording, so it is close to a trivial restatement.",
        "Belgian nationality is irrelevant to the rule."
      ],
      "score_notes": {
        "focus": "A single bounded ask: whether the company is a holder.",
        "linguistic_quality": "Clear and natural, with one slightly stilted phrase ('fall within the defined category').",
        "regime_fixing": "'Aluminium scrap that has ceased to be waste' points to the scrap metal criteria regime. 'Defined category of a holder' is generic and leaves the scope open.",
        "situation": "The protagonist is a private company with two particulars (aluminium scrap, in possession). Belgium adds nothing. The scenario is thin and only restates the definition in story form.",
        "terminology_and_distance": "The question mirrors the answer: 'in possession of' closely tracks 'in possession of scrap metal', and the term 'holder' is named. This leaks the answer, although it is only a definition lookup."
      },
      "scores": {
        "focus": 4,
        "linguistic_quality": 4,
        "regime_fixing": 3,
        "situation": 3,
        "terminology_and_distance": 3
      }
    },
    "focus": 4,
    "linguistic_quality": 4,
    "overall": 17,
    "reason": "situation: The protagonist is a private company with two particulars (aluminium scrap, in possession). Belgium adds nothing. The scenario is thin and only restates the definition in story form.; regime_fixing: 'Aluminium scrap that has ceased to be waste' points to the scrap metal criteria regime. 'Defined category of a holder' is generic and leaves the scope open.; terminology_and_distance: The question mirrors the answer: 'in possession of' closely tracks 'in possession of scrap metal', and the term 'holder' is named. This leaks the answer, although it is only a definition lookup.; focus: A single bounded ask: whether the company is a holder.; linguistic_quality: Clear and natural, with one slightly stilted phrase ('fall within the defined category').",
    "regime_fixing": 3,
    "situation": 3,
    "terminology_and_distance": 3
  },
  {
    "_batch_diversity": "fail",
    "_contract": "compact",
    "_keys": [
      "situation",
      "regime_fixing",
      "terminology_and_distance",
      "focus",
      "linguistic_quality"
    ],
    "_response": {
      "candidate_id": "q_e6c102bee5c9e6ccef1450b7",
      "checks": {
        "metadata": "pass",
        "mode": "pass",
        "support": "pass"
      },
      "index": 1,
      "problems": [
        "The facts reproduce the definitional text and so leak the answer.",
        "The question type is acceptable, and the article-level metadata is fine."
      ],
      "score_notes": {
        "focus": "A single ask: whether the company is a producer.",
        "linguistic_quality": "Fluent and clear, though the phrasing is slightly repetitive.",
        "regime_fixing": "'Iron and steel scrap that has ceased to be waste' identifies the scrap metal regime. 'Defined category of a producer' remains generic.",
        "situation": "There are relevant particulars (iron and steel scrap, first transfer to another holder), but the case merely dresses up the definition. German nationality is irrelevant.",
        "terminology_and_distance": "The facts copy the definition almost verbatim ('transfers ... to another holder for the first time', 'ceased to be waste'). This effectively asks the answer back as a question."
      },
      "scores": {
        "focus": 4,
        "linguistic_quality": 4,
        "regime_fixing": 3,
        "situation": 3,
        "terminology_and_distance": 2
      }
    },
    "focus": 4,
    "linguistic_quality": 4,
    "overall": 16,
    "reason": "situation: There are relevant particulars (iron and steel scrap, first transfer to another holder), but the case merely dresses up the definition. German nationality is irrelevant.; regime_fixing: 'Iron and steel scrap that has ceased to be waste' identifies the scrap metal regime. 'Defined category of a producer' remains generic.; terminology_and_distance: The facts copy the definition almost verbatim ('transfers ... to another holder for the first time', 'ceased to be waste'). This effectively asks the answer back as a question.; focus: A single ask: whether the company is a producer.; linguistic_quality: Fluent and clear, though the phrasing is slightly repetitive.",
    "regime_fixing": 3,
    "situation": 3,
    "terminology_and_distance": 2
  },
  {
    "_batch_diversity": "fail",
    "_contract": "compact",
    "_keys": [
      "situation",
      "regime_fixing",
      "terminology_and_distance",
      "focus",
      "linguistic_quality"
    ],
    "_response": {
      "candidate_id": "q_1eff785030d676d9a7c07883",
      "checks": {
        "metadata": "pass",
        "mode": "pass",
        "support": "pass"
      },
      "index": 2,
      "problems": [
        "The facts echo the definition's wording and leak the answer.",
        "The particulars list four items, and the answer span is long but fits the definition."
      ],
      "score_notes": {
        "focus": "A single ask: whether the batch is a consignment.",
        "linguistic_quality": "Natural and precise prose.",
        "regime_fixing": "'Aluminium scrap that has ceased to be waste' and 'producer' point to the regime. 'Defined category of a consignment' is generic.",
        "situation": "There are several particulars (batch, delivery to another holder, three containers). The scenario simply mirrors the definition. Spanish nationality is irrelevant.",
        "terminology_and_distance": "Wording such as 'batch', 'for delivery ... to another holder' and 'containers' is taken directly from the definition, and the defined term is named. The question nearly restates the answer."
      },
      "scores": {
        "focus": 4,
        "linguistic_quality": 4,
        "regime_fixing": 3,
        "situation": 3,
        "terminology_and_distance": 2
      }
    },
    "focus": 4,
    "linguistic_quality": 4,
    "overall": 16,
    "reason": "situation: There are several particulars (batch, delivery to another holder, three containers). The scenario simply mirrors the definition. Spanish nationality is irrelevant.; regime_fixing: 'Aluminium scrap that has ceased to be waste' and 'producer' point to the regime. 'Defined category of a consignment' is generic.; terminology_and_distance: Wording such as 'batch', 'for delivery ... to another holder' and 'containers' is taken directly from the definition, and the defined term is named. The question nearly restates the answer.; focus: A single ask: whether the batch is a consignment.; linguistic_quality: Natural and precise prose.",
    "regime_fixing": 3,
    "situation": 3,
    "terminology_and_distance": 2
  }
]
````

### mode/un/2001/s/res/1376_2001_#2/practitioner: faithfulness — completed

````json
[
  {
    "_response": {
      "grounding": 4,
      "index": 0,
      "numerical_fidelity": 5,
      "precision": 3,
      "reason": "The target supports that the Council called on the Congolese parties to work together for the success of the dialogue. The Council also expressed support for the Facilitator's call on the parties to make the dialogue fully inclusive. The question's premise, 'call on the Congolese parties regarding an inclusive dialogue', slightly blends these two points, which is a minor framing limitation. The answer copies the whole paragraph. The opening support for the dialogue and the Facilitator is extra material, and the direct answer is only the 'calls on... work together' clause. No numbers appear."
    },
    "grounding": 4,
    "numerical_fidelity": 5,
    "overall": 12,
    "precision": 3,
    "reason": "The target supports that the Council called on the Congolese parties to work together for the success of the dialogue. The Council also expressed support for the Facilitator's call on the parties to make the dialogue fully inclusive. The question's premise, 'call on the Congolese parties regarding an inclusive dialogue', slightly blends these two points, which is a minor framing limitation. The answer copies the whole paragraph. The opening support for the dialogue and the Facilitator is extra material, and the direct answer is only the 'calls on... work together' clause. No numbers appear."
  },
  {
    "_response": {
      "grounding": 4,
      "index": 1,
      "numerical_fidelity": 5,
      "precision": 4,
      "reason": "The target says the Council called on the international community to increase, without delay, its support for humanitarian activities. The question's 'immediate support' is a fair paraphrase of 'without delay'. The answer is fully supported. It adds the clause on serious concern about the humanitarian situation, which is mildly removable context. The question asks what support to increase, and the text only says 'support for humanitarian activities', so the question slightly overstates specificity. No numbers appear."
    },
    "grounding": 4,
    "numerical_fidelity": 5,
    "overall": 13,
    "precision": 4,
    "reason": "The target says the Council called on the international community to increase, without delay, its support for humanitarian activities. The question's 'immediate support' is a fair paraphrase of 'without delay'. The answer is fully supported. It adds the clause on serious concern about the humanitarian situation, which is mildly removable context. The question asks what support to increase, and the text only says 'support for humanitarian activities', so the question slightly overstates specificity. No numbers appear."
  },
  {
    "_response": {
      "grounding": 5,
      "index": 2,
      "numerical_fidelity": 5,
      "precision": 4,
      "reason": "The target explicitly says the Council demands that illegal exploitation cease and stresses that the resources should not be used to finance the conflict. The question matches this. The answer includes the reiterated condemnation, which the question does not ask about. This is minor but removable. No numbers appear."
    },
    "grounding": 5,
    "numerical_fidelity": 5,
    "overall": 14,
    "precision": 4,
    "reason": "The target explicitly says the Council demands that illegal exploitation cease and stresses that the resources should not be used to finance the conflict. The question matches this. The answer includes the reiterated condemnation, which the question does not ask about. This is minor but removable. No numbers appear."
  }
]
````

### mode/un/2001/s/res/1376_2001_#2/practitioner: quality_index_recovery — completed

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
      "candidate_id": "q_8bf1d221730eb73583995d01",
      "checks": {
        "metadata": "pass",
        "mode": "fail",
        "support": "pass"
      },
      "index": 0,
      "problems": [
        "mode: no absolute time or period and only a thin regime anchor, so the question is not pinned to 2001.",
        "answer: includes the initial 'Expresses its support' clause, which is not needed for the question."
      ],
      "score_notes": {
        "anchoring_and_time": "Names the inter-Congolese dialogue but gives no time or regime context (2001, DRC peace process, Council resolution). Without it the question could match many Council texts on the DRC.",
        "consequence": "The request to work together for the dialogue's success and to make it inclusive is a modest but concrete political expectation.",
        "informativeness": "The answer includes the call on the parties to work together and the Facilitator's call for full inclusiveness. It also carries extra support language beyond what was asked.",
        "linguistic_quality": "Clear and grammatical. The phrase 'regarding an inclusive inter-Congolese dialogue' is slightly loose.",
        "practitioner_realism": "Asks for a bounded request to the parties, but the wording is generic and reads as comprehension of one paragraph."
      },
      "scores": {
        "anchoring_and_time": 2,
        "consequence": 3,
        "informativeness": 4,
        "linguistic_quality": 4,
        "practitioner_realism": 3
      }
    },
    "anchoring_and_time": 2,
    "consequence": 3,
    "informativeness": 4,
    "linguistic_quality": 4,
    "overall": 16,
    "practitioner_realism": 3,
    "reason": "practitioner_realism: Asks for a bounded request to the parties, but the wording is generic and reads as comprehension of one paragraph.; anchoring_and_time: Names the inter-Congolese dialogue but gives no time or regime context (2001, DRC peace process, Council resolution). Without it the question could match many Council texts on the DRC.; consequence: The request to work together for the dialogue's success and to make it inclusive is a modest but concrete political expectation.; informativeness: The answer includes the call on the parties to work together and the Facilitator's call for full inclusiveness. It also carries extra support language beyond what was asked.; linguistic_quality: Clear and grammatical. The phrase 'regarding an inclusive inter-Congolese dialogue' is slightly loose."
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
      "candidate_id": "q_2edd0934e47ce5c6e38d7c40",
      "checks": {
        "metadata": "pass",
        "mode": "fail",
        "support": "pass"
      },
      "index": 1,
      "problems": [
        "mode: no time anchor, and the question is otherwise generic across DRC resolutions.",
        "answer: the 'serious concern' clause is surplus to the question.",
        "question wording 'immediate support' is a mild paraphrase of 'without delay'."
      ],
      "score_notes": {
        "anchoring_and_time": "Mentions the DRC humanitarian context but gives no date or period, so it could match many Council texts.",
        "consequence": "The call to increase humanitarian support without delay is a specific request, though a general appeal with no measure.",
        "informativeness": "The answer supports 'increase, without delay'. The question presupposes 'immediate support', and the source does not specify what kind of support.",
        "linguistic_quality": "Clear and natural. 'Immediate support' slightly overstates the source.",
        "practitioner_realism": "A plausible need, but 'immediate support' is vague and the request is a generic appeal."
      },
      "scores": {
        "anchoring_and_time": 2,
        "consequence": 3,
        "informativeness": 4,
        "linguistic_quality": 4,
        "practitioner_realism": 3
      }
    },
    "anchoring_and_time": 2,
    "consequence": 3,
    "informativeness": 4,
    "linguistic_quality": 4,
    "overall": 16,
    "practitioner_realism": 3,
    "reason": "practitioner_realism: A plausible need, but 'immediate support' is vague and the request is a generic appeal.; anchoring_and_time: Mentions the DRC humanitarian context but gives no date or period, so it could match many Council texts.; consequence: The call to increase humanitarian support without delay is a specific request, though a general appeal with no measure.; informativeness: The answer supports 'increase, without delay'. The question presupposes 'immediate support', and the source does not specify what kind of support.; linguistic_quality: Clear and natural. 'Immediate support' slightly overstates the source."
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
      "candidate_id": "q_2084410b4b7355d763a80445",
      "checks": {
        "metadata": "pass",
        "mode": "fail",
        "support": "pass"
      },
      "index": 2,
      "problems": [
        "mode: no absolute time or period, so the question is not pinned to 2001.",
        "question_type 'sanction_condition_or_consequence' is a loose fit, since no sanction is involved, but it is acceptable."
      ],
      "score_notes": {
        "anchoring_and_time": "Identifies the DRC's natural resources and conflict financing, a distinctive issue, but gives no date or period. The issue recurs across DRC resolutions.",
        "consequence": "Substantive: the demand that illegal exploitation cease, plus the principle that resources should not finance the conflict.",
        "informativeness": "The answer fully gives the demand and the financing statement. It also restates the condemnation, which is acceptable attribution of the demand.",
        "linguistic_quality": "Clear and concise. 'Demand' is precise, since the source uses 'demands that such exploitation cease'.",
        "practitioner_realism": "A realistic specialist question on resource exploitation and conflict financing, bounded to one paragraph."
      },
      "scores": {
        "anchoring_and_time": 2,
        "consequence": 4,
        "informativeness": 4,
        "linguistic_quality": 4,
        "practitioner_realism": 4
      }
    },
    "anchoring_and_time": 2,
    "consequence": 4,
    "informativeness": 4,
    "linguistic_quality": 4,
    "overall": 18,
    "practitioner_realism": 4,
    "reason": "practitioner_realism: A realistic specialist question on resource exploitation and conflict financing, bounded to one paragraph.; anchoring_and_time: Identifies the DRC's natural resources and conflict financing, a distinctive issue, but gives no date or period. The issue recurs across DRC resolutions.; consequence: Substantive: the demand that illegal exploitation cease, plus the principle that resources should not finance the conflict.; informativeness: The answer fully gives the demand and the financing statement. It also restates the condemnation, which is acceptable attribution of the demand.; linguistic_quality: Clear and concise. 'Demand' is precise, since the source uses 'demands that such exploitation cease'."
  }
]
````

### mode/un/2002/a/res/56/188#8/semantic: faithfulness — completed

````json
[
  {
    "_response": {
      "grounding": 5,
      "index": 0,
      "numerical_fidelity": 5,
      "precision": 4,
      "reason": "Paragraph 13 directly supports the answer, which quotes it. The question's premise that these are 'legal and administrative barriers' and 'control of property and economic resources' is a slight paraphrase of 'laws' and 'administrative reforms', but it is fair. The answer keeps the 'Urges' framing. It is slightly overbroad because it includes markets and information, which is minor. No numbers occur."
    },
    "grounding": 5,
    "numerical_fidelity": 5,
    "overall": 14,
    "precision": 4,
    "reason": "Paragraph 13 directly supports the answer, which quotes it. The question's premise that these are 'legal and administrative barriers' and 'control of property and economic resources' is a slight paraphrase of 'laws' and 'administrative reforms', but it is fair. The answer keeps the 'Urges' framing. It is slightly overbroad because it includes markets and information, which is minor. No numbers occur."
  },
  {
    "_response": {
      "grounding": 5,
      "index": 1,
      "numerical_fidelity": 5,
      "precision": 4,
      "reason": "Paragraph 14 and items (a)-(c) support the answer. The question asks how Governments are 'encouraged' and the answer preserves 'Calls upon Governments to encourage'. Items (a)-(c) address poor women and women-owned businesses. Item (d), on equal treatment of women clients, is omitted, so the list of measures is incomplete. The question is broad enough that the answer is still reasonably complete, and (d) is covered by another candidate. The answer ends with a trailing semicolon, which is harmless. No numbers occur."
    },
    "grounding": 5,
    "numerical_fidelity": 5,
    "overall": 14,
    "precision": 4,
    "reason": "Paragraph 14 and items (a)-(c) support the answer. The question asks how Governments are 'encouraged' and the answer preserves 'Calls upon Governments to encourage'. Items (a)-(c) address poor women and women-owned businesses. Item (d), on equal treatment of women clients, is omitted, so the list of measures is incomplete. The question is broad enough that the answer is still reasonably complete, and (d) is covered by another candidate. The answer ends with a trailing semicolon, which is harmless. No numbers occur."
  },
  {
    "_response": {
      "grounding": 4,
      "index": 2,
      "numerical_fidelity": 5,
      "precision": 3,
      "reason": "Item (d) supports the content. The question says 'measures are proposed' for 'financial-sector decisions'. The answer fragment has no subject and omits the lead-in that Governments are called upon to encourage the financial sector to do this, so the actor and the recommendatory status are lost. The fragment is hard to understand alone. The question premise is supported, since the decision-making positions are within the financial sector context. No numbers occur."
    },
    "grounding": 4,
    "numerical_fidelity": 5,
    "overall": 12,
    "precision": 3,
    "reason": "Item (d) supports the content. The question says 'measures are proposed' for 'financial-sector decisions'. The answer fragment has no subject and omits the lead-in that Governments are called upon to encourage the financial sector to do this, so the actor and the recommendatory status are lost. The fragment is hard to understand alone. The question premise is supported, since the decision-making positions are within the financial sector context. No numbers occur."
  }
]
````

### mode/un/2002/a/res/56/188#8/semantic: quality_index_recovery — completed

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
      "candidate_id": "q_d3bcadee1d9208096c60b480",
      "checks": {
        "metadata": "pass",
        "mode": "fail",
        "support": "pass"
      },
      "index": 0,
      "problems": [
        "anchoring_and_time: no relevant time or distinctive context, so the need is underspecified for retrieval.",
        "mode: missing context or time."
      ],
      "score_notes": {
        "anchoring_and_time": "No time, resolution or forum is given, and \"States\" is generic. The topic is common across UN texts, so the question lacks a distinctive composite anchor and absolute time.",
        "consequence": "The answer gives the specific measures: laws on land and inheritance rights, plus administrative reforms for credit, capital, technologies, markets and information. It fully answers the question and is marked as urging.",
        "lexical_distance": "Reformulates as \"barriers\" and \"control of property and economic resources\" instead of copying \"rights to own land\". Some overlap remains, but it is acceptable.",
        "linguistic_quality": "Clear and idiomatic. \"Remove barriers\" slightly frames the answer as remedying barriers, which the text does not say explicitly.",
        "search_realism": "A natural, bounded need about legal and administrative reform for women's property and economic access. It is somewhat broad but realistic."
      },
      "scores": {
        "anchoring_and_time": 2,
        "consequence": 5,
        "lexical_distance": 4,
        "linguistic_quality": 4,
        "search_realism": 4
      }
    },
    "anchoring_and_time": 2,
    "consequence": 5,
    "lexical_distance": 4,
    "linguistic_quality": 4,
    "overall": 19,
    "reason": "search_realism: A natural, bounded need about legal and administrative reform for women's property and economic access. It is somewhat broad but realistic.; anchoring_and_time: No time, resolution or forum is given, and \"States\" is generic. The topic is common across UN texts, so the question lacks a distinctive composite anchor and absolute time.; consequence: The answer gives the specific measures: laws on land and inheritance rights, plus administrative reforms for credit, capital, technologies, markets and information. It fully answers the question and is marked as urging.; lexical_distance: Reformulates as \"barriers\" and \"control of property and economic resources\" instead of copying \"rights to own land\". Some overlap remains, but it is acceptable.; linguistic_quality: Clear and idiomatic. \"Remove barriers\" slightly frames the answer as remedying barriers, which the text does not say explicitly.",
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
      "candidate_id": "q_33414b464513bd539637bd12",
      "checks": {
        "metadata": "pass",
        "mode": "fail",
        "support": "pass"
      },
      "index": 1,
      "problems": [
        "anchoring_and_time: no absolute time or distinctive anchor.",
        "mode: missing context or time.",
        "consequence: the answer stops after (c) and the chapeau ends with a colon, so it is slightly truncated, though the question's scope is still met."
      ],
      "score_notes": {
        "anchoring_and_time": "No time or forum is given and the subject is generic. Nothing pins the question to this resolution period.",
        "consequence": "The answer lists concrete actions: exploring ways to reach the poor, savings schemes, and research on women-owned businesses. It omits item (d) on training and representation, yet the question's focus on poor women and women-owned businesses is still well covered.",
        "lexical_distance": "Paraphrases \"mainstream a gender perspective\" as \"more responsive to poor women\". The meaning is preserved.",
        "linguistic_quality": "Fluent and clear, and the \"encouraged\" framing matches the source status.",
        "search_realism": "A realistic need about making financial-sector policy responsive to poor women and women entrepreneurs."
      },
      "scores": {
        "anchoring_and_time": 2,
        "consequence": 4,
        "lexical_distance": 4,
        "linguistic_quality": 4,
        "search_realism": 4
      }
    },
    "anchoring_and_time": 2,
    "consequence": 4,
    "lexical_distance": 4,
    "linguistic_quality": 4,
    "overall": 18,
    "reason": "search_realism: A realistic need about making financial-sector policy responsive to poor women and women entrepreneurs.; anchoring_and_time: No time or forum is given and the subject is generic. Nothing pins the question to this resolution period.; consequence: The answer lists concrete actions: exploring ways to reach the poor, savings schemes, and research on women-owned businesses. It omits item (d) on training and representation, yet the question's focus on poor women and women-owned businesses is still well covered.; lexical_distance: Paraphrases \"mainstream a gender perspective\" as \"more responsive to poor women\". The meaning is preserved.; linguistic_quality: Fluent and clear, and the \"encouraged\" framing matches the source status.",
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
      "candidate_id": "q_19a2bc4a924bd233a978aed9",
      "checks": {
        "metadata": "pass",
        "mode": "fail",
        "support": "pass"
      },
      "index": 2,
      "problems": [
        "anchoring_and_time: no time and minimal context; \"women clients\" is unresolved without the financial-sector chapeau.",
        "lexical_distance: the anchor is copied verbatim.",
        "mode: missing context or time."
      ],
      "score_notes": {
        "anchoring_and_time": "\"Financial-sector\" is implied only. There is no time or context, and \"women clients\" is an undefined referent. It is too generic to identify this source.",
        "consequence": "The answer names gender-awareness training and better representation of women in decision-making. It answers both parts. It is somewhat dependent on the clause's context of the financial sector, which the answer omits.",
        "lexical_distance": "Retains \"equal treatment for women clients\" verbatim and mirrors the answer. Little conceptual reformulation.",
        "linguistic_quality": "Clear and grammatical. \"Proposed\" is acceptable.",
        "search_realism": "A plausible need, but it reads as a two-part ask about equal treatment and women's influence in decisions. It is also mostly the answer's own wording."
      },
      "scores": {
        "anchoring_and_time": 1,
        "consequence": 4,
        "lexical_distance": 3,
        "linguistic_quality": 4,
        "search_realism": 3
      }
    },
    "anchoring_and_time": 1,
    "consequence": 4,
    "lexical_distance": 3,
    "linguistic_quality": 4,
    "overall": 15,
    "reason": "search_realism: A plausible need, but it reads as a two-part ask about equal treatment and women's influence in decisions. It is also mostly the answer's own wording.; anchoring_and_time: \"Financial-sector\" is implied only. There is no time or context, and \"women clients\" is an undefined referent. It is too generic to identify this source.; consequence: The answer names gender-awareness training and better representation of women in decision-making. It answers both parts. It is somewhat dependent on the clause's context of the financial sector, which the answer omits.; lexical_distance: Retains \"equal treatment for women clients\" verbatim and mirrors the answer. Little conceptual reformulation.; linguistic_quality: Clear and grammatical. \"Proposed\" is acceptable.",
    "search_realism": 3
  }
]
````

### mode/un/2003/a/res/57/300#10/semantic: faithfulness — completed

````json
[
  {
    "_response": {
      "grounding": 4,
      "index": 0,
      "numerical_fidelity": 5,
      "precision": 5,
      "reason": "Paragraph 27 fully supports the answer: a panel of eminent persons, terms of reference stressing the intergovernmental character, and recommendations considered through the intergovernmental process. The question's 'proposed reviewing' is slightly loose, because the Assembly concurs with the Secretary-General's intention rather than proposing the review itself. This does not change the answer. The span is complete and has no irrelevant material. It contains no numbers."
    },
    "grounding": 4,
    "numerical_fidelity": 5,
    "overall": 14,
    "precision": 5,
    "reason": "Paragraph 27 fully supports the answer: a panel of eminent persons, terms of reference stressing the intergovernmental character, and recommendations considered through the intergovernmental process. The question's 'proposed reviewing' is slightly loose, because the Assembly concurs with the Secretary-General's intention rather than proposing the review itself. This does not change the answer. The span is complete and has no irrelevant material. It contains no numbers."
  },
  {
    "_response": {
      "grounding": 5,
      "index": 1,
      "numerical_fidelity": 5,
      "precision": 5,
      "reason": "Paragraph 28 states that creating the partnership office should be subject to resolutions 55/215 and 56/76. The question asks about conditions, and the answer gives exactly that. The resolution numbers and dates (21 December 2000, 11 December 2001) are copied exactly. The referenced 55/215 is consistent. The span is complete and concise."
    },
    "grounding": 5,
    "numerical_fidelity": 5,
    "overall": 15,
    "precision": 5,
    "reason": "Paragraph 28 states that creating the partnership office should be subject to resolutions 55/215 and 56/76. The question asks about conditions, and the answer gives exactly that. The resolution numbers and dates (21 December 2000, 11 December 2001) are copied exactly. The referenced 55/215 is consistent. The span is complete and concise."
  },
  {
    "_response": {
      "grounding": 5,
      "index": 2,
      "numerical_fidelity": 5,
      "precision": 5,
      "reason": "Paragraph 30 notes the reference to sunset provisions and recalls that no decision has been taken. This directly answers the question about their status. 'Reform report' is a fair description of the Secretary-General's report given the document context. The span is complete and has no numbers."
    },
    "grounding": 5,
    "numerical_fidelity": 5,
    "overall": 15,
    "precision": 5,
    "reason": "Paragraph 30 notes the reference to sunset provisions and recalls that no decision has been taken. This directly answers the question about their status. 'Reform report' is a fair description of the Secretary-General's report given the document context. The span is complete and has no numbers."
  }
]
````

### mode/un/2003/a/res/57/300#10/semantic: quality_index_recovery — completed

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
      "candidate_id": "q_d17fd300f30edc3dffa813d6",
      "checks": {
        "metadata": "pass",
        "mode": "pass",
        "support": "pass"
      },
      "index": 0,
      "problems": [
        "anchoring_and_time: No time frame or reform-agenda context is given to pin the need."
      ],
      "score_notes": {
        "anchoring_and_time": "The topic is identifiable, but the question has no absolute time or context such as the 2002 reform agenda. The UN-civil society review is fairly distinctive, yet the time pin is missing.",
        "consequence": "The answer fully covers the panel, its diverse composition, the intergovernmental emphasis in its terms of reference, and how its recommendations will be handled. The status is preserved as a concurrence with the Secretary-General's intention.",
        "lexical_distance": "Reasonable reformulation (\"reviewing the relationship\" is close to the source), and the legal terms are necessary.",
        "linguistic_quality": "Clear, concise and idiomatic.",
        "search_realism": "A natural, bounded question about a concrete response (a review panel), not an isolated datum."
      },
      "scores": {
        "anchoring_and_time": 2,
        "consequence": 5,
        "lexical_distance": 4,
        "linguistic_quality": 5,
        "search_realism": 4
      }
    },
    "anchoring_and_time": 2,
    "consequence": 5,
    "lexical_distance": 4,
    "linguistic_quality": 5,
    "overall": 20,
    "reason": "search_realism: A natural, bounded question about a concrete response (a review panel), not an isolated datum.; anchoring_and_time: The topic is identifiable, but the question has no absolute time or context such as the 2002 reform agenda. The UN-civil society review is fairly distinctive, yet the time pin is missing.; consequence: The answer fully covers the panel, its diverse composition, the intergovernmental emphasis in its terms of reference, and how its recommendations will be handled. The status is preserved as a concurrence with the Secretary-General's intention.; lexical_distance: Reasonable reformulation (\"reviewing the relationship\" is close to the source), and the legal terms are necessary.; linguistic_quality: Clear, concise and idiomatic.",
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
      "candidate_id": "q_76ce8edeb1a8fcad5a51fcac",
      "checks": {
        "metadata": "pass",
        "mode": "pass",
        "support": "pass"
      },
      "index": 1,
      "problems": [
        "anchoring_and_time: No absolute time or reform context is given."
      ],
      "score_notes": {
        "anchoring_and_time": "There is no time or context. \"Partnership office\" is fairly distinctive, but the question does not say whose proposal it is or when it was made.",
        "consequence": "The answer states the condition, that creation is subject to resolutions 55/215 and 56/76. Those resolutions are only cited by number, so the answer is somewhat thin on substance, though the target says nothing more.",
        "lexical_distance": "Mostly paraphrased, though \"enhance cooperation with the private sector\" is close to the source wording.",
        "linguistic_quality": "Clear. \"Governed\" is slightly odd for a proposal, but acceptable.",
        "search_realism": "A bounded question about the conditions on a proposed institutional mechanism."
      },
      "scores": {
        "anchoring_and_time": 2,
        "consequence": 4,
        "lexical_distance": 4,
        "linguistic_quality": 4,
        "search_realism": 4
      }
    },
    "anchoring_and_time": 2,
    "consequence": 4,
    "lexical_distance": 4,
    "linguistic_quality": 4,
    "overall": 18,
    "reason": "search_realism: A bounded question about the conditions on a proposed institutional mechanism.; anchoring_and_time: There is no time or context. \"Partnership office\" is fairly distinctive, but the question does not say whose proposal it is or when it was made.; consequence: The answer states the condition, that creation is subject to resolutions 55/215 and 56/76. Those resolutions are only cited by number, so the answer is somewhat thin on substance, though the target says nothing more.; lexical_distance: Mostly paraphrased, though \"enhance cooperation with the private sector\" is close to the source wording.; linguistic_quality: Clear. \"Governed\" is slightly odd for a proposal, but acceptable.",
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
      "candidate_id": "q_b772924705818a24a4f1b8cb",
      "checks": {
        "metadata": "pass",
        "mode": "pass",
        "support": "pass"
      },
      "index": 2,
      "problems": [
        "anchoring_and_time: The report is unspecified and no time is given.",
        "search_realism: The content is thin, so the need is weakly substantive."
      ],
      "score_notes": {
        "anchoring_and_time": "\"The Secretary-General's reform report\" is not tied to a date or a named resolution, so it is weakly anchored and lacks time. Sunset provisions are the only distinctive cue.",
        "consequence": "The answer says the Assembly noted the reference and that no decision has been taken. That is accurate and complete about the status, but it carries little substance.",
        "lexical_distance": "It paraphrases \"status\" and \"mentioned\", and keeps the necessary term \"sunset provisions\".",
        "linguistic_quality": "Clear and idiomatic.",
        "search_realism": "A plausible question about the status of a proposal, but narrow and reliant on the phrase \"sunset provisions\". It is a little like asking for a status datum."
      },
      "scores": {
        "anchoring_and_time": 2,
        "consequence": 4,
        "lexical_distance": 4,
        "linguistic_quality": 4,
        "search_realism": 3
      }
    },
    "anchoring_and_time": 2,
    "consequence": 4,
    "lexical_distance": 4,
    "linguistic_quality": 4,
    "overall": 17,
    "reason": "search_realism: A plausible question about the status of a proposal, but narrow and reliant on the phrase \"sunset provisions\". It is a little like asking for a status datum.; anchoring_and_time: \"The Secretary-General's reform report\" is not tied to a date or a named resolution, so it is weakly anchored and lacks time. Sunset provisions are the only distinctive cue.; consequence: The answer says the Assembly noted the reference and that no decision has been taken. That is accurate and complete about the status, but it carries little substance.; lexical_distance: It paraphrases \"status\" and \"mentioned\", and keeps the necessary term \"sunset provisions\".; linguistic_quality: Clear and idiomatic.",
    "search_realism": 3
  }
]
````

### mode/un/2004/a/c_2/58/sr_24#18/semantic: faithfulness — completed

````json
[
  {
    "_response": {
      "grounding": 4,
      "index": 0,
      "numerical_fidelity": 5,
      "precision": 4,
      "reason": "The target states UNIDO's belief that developing countries needed better supply-side capacities to have adequate goods volume and range and to meet stricter conformity requirements. That matches the question. The question says 'supply-side capacity-building measures', while the source says only 'that measure', which refers to something earlier, so the premise is slightly vague. The answer starts with 'UNIDO had taken that measure', an unresolved referent that adds a little removable wording. No numbers appear."
    },
    "grounding": 4,
    "numerical_fidelity": 5,
    "overall": 13,
    "precision": 4,
    "reason": "The target states UNIDO's belief that developing countries needed better supply-side capacities to have adequate goods volume and range and to meet stricter conformity requirements. That matches the question. The question says 'supply-side capacity-building measures', while the source says only 'that measure', which refers to something earlier, so the premise is slightly vague. The answer starts with 'UNIDO had taken that measure', an unresolved referent that adds a little removable wording. No numbers appear."
  },
  {
    "_response": {
      "grounding": 5,
      "index": 1,
      "numerical_fidelity": 5,
      "precision": 5,
      "reason": "The answer matches the target: programmes to build policy-making, institutional and industrial capacities and help meet market requirements and standards, with the listed intersectoral activities. It fully resolves the 'how' question with no extraneous material. No numbers appear."
    },
    "grounding": 5,
    "numerical_fidelity": 5,
    "overall": 15,
    "precision": 5,
    "reason": "The answer matches the target: programmes to build policy-making, institutional and industrial capacities and help meet market requirements and standards, with the listed intersectoral activities. It fully resolves the 'how' question with no extraneous material. No numbers appear."
  },
  {
    "_response": {
      "grounding": 4,
      "index": 2,
      "numerical_fidelity": 5,
      "precision": 3,
      "reason": "The content is supported by the target. The question asks what UNIDO 'would pursue', but the answer opens with the completed act of promoting regional calibration centres and accreditation authorities, which is in the source but is a past action. The answer also includes the paragraph number '39.' and a long list of regional groupings that is only partly relevant to 'activities'. The national-level standards, conformity assessment and metrology activities are covered. The paragraph number is harmless, and no numerical values are wrong."
    },
    "grounding": 4,
    "numerical_fidelity": 5,
    "overall": 12,
    "precision": 3,
    "reason": "The content is supported by the target. The question asks what UNIDO 'would pursue', but the answer opens with the completed act of promoting regional calibration centres and accreditation authorities, which is in the source but is a past action. The answer also includes the paragraph number '39.' and a long list of regional groupings that is only partly relevant to 'activities'. The national-level standards, conformity assessment and metrology activities are covered. The paragraph number is harmless, and no numerical values are wrong."
  }
]
````

### mode/un/2004/a/c_2/58/sr_24#18/semantic: quality_index_recovery — completed

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
      "candidate_id": "q_d6bd707799753d689f69bc87",
      "checks": {
        "metadata": "pass",
        "mode": "uncertain",
        "support": "pass"
      },
      "index": 0,
      "problems": [
        "anchoring_and_time: no absolute time or event context, and the measure is not identified.",
        "consequence: the answer's 'that measure' is unresolved from the target block alone.",
        "mode: the question's 'measures' presupposes an unspecified measure that the target block does not name."
      ],
      "score_notes": {
        "anchoring_and_time": "It names UNIDO and supply-side capacity building, but gives no time or forum context such as 2003 or Cancun. It is also vague about which measure is meant, and 'that measure' is unresolved inside the target block.",
        "consequence": "The answer gives the stated rationale: sufficient volume and range of goods, and meeting conformity requirements. But it opens with the unresolved 'that measure', so the answer is partly deictic and does not identify what the measure was.",
        "lexical_distance": "It reuses 'supply-side capacities' and 'developing countries' from the source. These are largely necessary terms, but 'capacity-building measures' adds little reformulation.",
        "linguistic_quality": "Clear and idiomatic, and concise.",
        "search_realism": "A natural rationale question about why UNIDO acted, and a bounded need."
      },
      "scores": {
        "anchoring_and_time": 2,
        "consequence": 3,
        "lexical_distance": 3,
        "linguistic_quality": 4,
        "search_realism": 4
      }
    },
    "anchoring_and_time": 2,
    "consequence": 3,
    "lexical_distance": 3,
    "linguistic_quality": 4,
    "overall": 16,
    "reason": "search_realism: A natural rationale question about why UNIDO acted, and a bounded need.; anchoring_and_time: It names UNIDO and supply-side capacity building, but gives no time or forum context such as 2003 or Cancun. It is also vague about which measure is meant, and 'that measure' is unresolved inside the target block.; consequence: The answer gives the stated rationale: sufficient volume and range of goods, and meeting conformity requirements. But it opens with the unresolved 'that measure', so the answer is partly deictic and does not identify what the measure was.; lexical_distance: It reuses 'supply-side capacities' and 'developing countries' from the source. These are largely necessary terms, but 'capacity-building measures' adds little reformulation.; linguistic_quality: Clear and idiomatic, and concise.",
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
      "candidate_id": "q_1f72ceec1973722f144f2203",
      "checks": {
        "metadata": "pass",
        "mode": "pass",
        "support": "pass"
      },
      "index": 1,
      "problems": [
        "anchoring_and_time: no time context is given."
      ],
      "score_notes": {
        "anchoring_and_time": "UNIDO's special programmes for developing countries form a fairly distinctive topic. It has no absolute time, though, and the content is fairly recurrent across UNIDO statements.",
        "consequence": "The answer fully covers the capacity-building aims and the listed intersectoral activities. It is concrete and complete.",
        "lexical_distance": "It copies 'meet market requirements and international standards' and 'special programmes' almost verbatim, which is avoidable overlap.",
        "linguistic_quality": "Clear and grammatical. It is slightly long but acceptable.",
        "search_realism": "A natural, bounded question about a programme design and its mechanism."
      },
      "scores": {
        "anchoring_and_time": 3,
        "consequence": 5,
        "lexical_distance": 3,
        "linguistic_quality": 4,
        "search_realism": 5
      }
    },
    "anchoring_and_time": 3,
    "consequence": 5,
    "lexical_distance": 3,
    "linguistic_quality": 4,
    "overall": 20,
    "reason": "search_realism: A natural, bounded question about a programme design and its mechanism.; anchoring_and_time: UNIDO's special programmes for developing countries form a fairly distinctive topic. It has no absolute time, though, and the content is fairly recurrent across UNIDO statements.; consequence: The answer fully covers the capacity-building aims and the listed intersectoral activities. It is concrete and complete.; lexical_distance: It copies 'meet market requirements and international standards' and 'special programmes' almost verbatim, which is avoidable overlap.; linguistic_quality: Clear and grammatical. It is slightly long but acceptable.",
    "search_realism": 5
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
      "candidate_id": "q_207e6bcf99e4e288d3cc4b94",
      "checks": {
        "metadata": "pass",
        "mode": "pass",
        "support": "uncertain"
      },
      "index": 2,
      "problems": [
        "anchoring_and_time: no time context.",
        "support: the answer begins with the paragraph number '39.', which is a pointer artifact in the extracted span.",
        "support: the question ties the national-level activities to smaller countries and LDCs, which the source does not state.",
        "search_realism: it bundles regional and national asks."
      ],
      "score_notes": {
        "anchoring_and_time": "It names UNIDO and the target group, but has no time or event anchor. The activities are also only loosely identified.",
        "consequence": "The answer lists regional calibration centres, accreditation authorities, capacity building in named regions, and national standards, conformity assessment and metrology activities. This answers the question, though the national activities are not specifically for smaller countries and LDCs.",
        "lexical_distance": "It paraphrases reasonably with 'standards-related' and 'pursue'. Only 'smaller countries and LDCs' is retained, which is a necessary term.",
        "linguistic_quality": "Fluent. The 'would pursue' tense is slightly off, since the source mixes past promotion with future plans.",
        "search_realism": "A plausible question, but it bundles regional and national activities. The 'smaller countries and LDCs' framing also slightly misattributes the national-level activities."
      },
      "scores": {
        "anchoring_and_time": 2,
        "consequence": 4,
        "lexical_distance": 4,
        "linguistic_quality": 4,
        "search_realism": 3
      }
    },
    "anchoring_and_time": 2,
    "consequence": 4,
    "lexical_distance": 4,
    "linguistic_quality": 4,
    "overall": 17,
    "reason": "search_realism: A plausible question, but it bundles regional and national activities. The 'smaller countries and LDCs' framing also slightly misattributes the national-level activities.; anchoring_and_time: It names UNIDO and the target group, but has no time or event anchor. The activities are also only loosely identified.; consequence: The answer lists regional calibration centres, accreditation authorities, capacity building in named regions, and national standards, conformity assessment and metrology activities. This answers the question, though the national activities are not specifically for smaller countries and LDCs.; lexical_distance: It paraphrases reasonably with 'standards-related' and 'pursue'. Only 'smaller countries and LDCs' is retained, which is a necessary term.; linguistic_quality: Fluent. The 'would pursue' tense is slightly off, since the source mixes past promotion with future plans.",
    "search_realism": 3
  }
]
````

### mode/un/2004/s/2004/505#15/semantic: faithfulness — completed

````json
[
  {
    "_response": {
      "grounding": 4,
      "index": 0,
      "numerical_fidelity": 5,
      "precision": 5,
      "reason": "The target says all Member States are to submit a first report within six months on steps taken or intended. The question's 'April 2004 resolution' is not named in the target, which says only 'the resolution'. The context identifies it as resolution 1540 (2004), adopted 28 April, so the referent is resolved. The question is slightly vague about which resolution. The answer is complete and exact, and 'six months' is faithful."
    },
    "grounding": 4,
    "numerical_fidelity": 5,
    "overall": 14,
    "precision": 5,
    "reason": "The target says all Member States are to submit a first report within six months on steps taken or intended. The question's 'April 2004 resolution' is not named in the target, which says only 'the resolution'. The context identifies it as resolution 1540 (2004), adopted 28 April, so the referent is resolved. The question is slightly vague about which resolution. The answer is complete and exact, and 'six months' is faithful."
  },
  {
    "_response": {
      "grounding": 4,
      "index": 1,
      "numerical_fidelity": 5,
      "precision": 5,
      "reason": "The answer copies the target sentence accurately, including the agreement that the resolution does not alter existing treaties and is not a basis for unilateral enforcement. The question's 'April 2004 Council agreement' is slightly loose, and the resolution is identified only through context, so there is a minor referent limitation. The answer is complete and concise. No numbers are involved beyond the date in the question, which is consistent."
    },
    "grounding": 4,
    "numerical_fidelity": 5,
    "overall": 14,
    "precision": 5,
    "reason": "The answer copies the target sentence accurately, including the agreement that the resolution does not alter existing treaties and is not a basis for unilateral enforcement. The question's 'April 2004 Council agreement' is slightly loose, and the resolution is identified only through context, so there is a minor referent limitation. The answer is complete and concise. No numbers are involved beyond the date in the question, which is consistent."
  },
  {
    "_response": {
      "grounding": 5,
      "index": 2,
      "numerical_fidelity": 5,
      "precision": 5,
      "reason": "The target says that on 15 April the Council met on the role of business, and it lists the guest speakers at the public meeting. The question's premises are correct, and the context places the meeting in 2004. The answer gives the full speaker list, including Annan, the World Bank President, von Pierer, Rasi and Kumalo. The date is faithful."
    },
    "grounding": 5,
    "numerical_fidelity": 5,
    "overall": 15,
    "precision": 5,
    "reason": "The target says that on 15 April the Council met on the role of business, and it lists the guest speakers at the public meeting. The question's premises are correct, and the context places the meeting in 2004. The answer gives the full speaker list, including Annan, the World Bank President, von Pierer, Rasi and Kumalo. The date is faithful."
  }
]
````

### mode/un/2004/s/2004/505#15/semantic: quality_index_recovery — completed

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
      "candidate_id": "q_53196fe166b420e99c79a2b9",
      "checks": {
        "metadata": "pass",
        "mode": "uncertain",
        "support": "pass"
      },
      "index": 0,
      "problems": [
        "anchoring_and_time: the resolution is not identified (non-proliferation of WMD / 1540), so the need is underspecified and could match several April 2004 resolutions.",
        "mode: the \"resolution\" referent is only resolvable from context outside the target block."
      ],
      "score_notes": {
        "anchoring_and_time": "\"April 2004 Security Council resolution\" is ambiguous. The Council adopted five resolutions that month, and the question does not name the subject (WMD non-proliferation). The answer's \"the resolution\" is left unresolved inside the block.",
        "consequence": "The answer states a concrete obligation: a first report within six months on steps taken or intended. Because the resolution is not identified, the pair is less useful.",
        "lexical_distance": "It reuses \"implementation\", \"reporting\" and \"obligation\" closely, with some paraphrase of the source wording.",
        "linguistic_quality": "The question is clear and grammatical.",
        "search_realism": "It asks about a real obligation, but the wording is generic and the target block never names the resolution."
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
    "reason": "search_realism: It asks about a real obligation, but the wording is generic and the target block never names the resolution.; anchoring_and_time: \"April 2004 Security Council resolution\" is ambiguous. The Council adopted five resolutions that month, and the question does not name the subject (WMD non-proliferation). The answer's \"the resolution\" is left unresolved inside the block.; consequence: The answer states a concrete obligation: a first report within six months on steps taken or intended. Because the resolution is not identified, the pair is less useful.; lexical_distance: It reuses \"implementation\", \"reporting\" and \"obligation\" closely, with some paraphrase of the source wording.; linguistic_quality: The question is clear and grammatical.",
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
      "candidate_id": "q_fc5ce6d48b34b50274c7419d",
      "checks": {
        "metadata": "pass",
        "mode": "uncertain",
        "support": "pass"
      },
      "index": 1,
      "problems": [
        "anchoring_and_time: the resolution is unidentified, with no mention of weapons of mass destruction or non-proliferation.",
        "linguistic_quality: \"Council agreement\" is slightly inaccurate; it was agreement among participants or members."
      ],
      "score_notes": {
        "anchoring_and_time": "Neither the subject (WMD non-proliferation) nor the resolution is named. \"April 2004 Council agreement\" is a poor anchor, so the resolution cannot be identified.",
        "consequence": "The answer gives substantive content: no alteration of treaties, and no basis for unilateral enforcement. The attribution to a general agreement is preserved.",
        "lexical_distance": "It mostly reuses source terms such as \"existing\", \"disarmament\", \"unilateral enforcement\" and \"agreement\".",
        "linguistic_quality": "\"Council agreement\" is awkward, since the source describes agreement among members.",
        "search_realism": "It asks about the resolution's effect on existing arrangements and unilateral enforcement, a substantive concern. The vague \"the resolution\" makes it a less natural search."
      },
      "scores": {
        "anchoring_and_time": 2,
        "consequence": 4,
        "lexical_distance": 3,
        "linguistic_quality": 3,
        "search_realism": 3
      }
    },
    "anchoring_and_time": 2,
    "consequence": 4,
    "lexical_distance": 3,
    "linguistic_quality": 3,
    "overall": 15,
    "reason": "search_realism: It asks about the resolution's effect on existing arrangements and unilateral enforcement, a substantive concern. The vague \"the resolution\" makes it a less natural search.; anchoring_and_time: Neither the subject (WMD non-proliferation) nor the resolution is named. \"April 2004 Council agreement\" is a poor anchor, so the resolution cannot be identified.; consequence: The answer gives substantive content: no alteration of treaties, and no basis for unilateral enforcement. The attribution to a general agreement is preserved.; lexical_distance: It mostly reuses source terms such as \"existing\", \"disarmament\", \"unilateral enforcement\" and \"agreement\".; linguistic_quality: \"Council agreement\" is awkward, since the source describes agreement among members.",
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
      "candidate_id": "q_617b2f226332ec694fed03ce",
      "checks": {
        "metadata": "pass",
        "mode": "fail",
        "support": "pass"
      },
      "index": 2,
      "problems": [
        "search_realism/mode: it is a participant-list question, not a conceptual situation, response or stakeholder need.",
        "consequence: the answer is an attendance list with little substantive value."
      ],
      "score_notes": {
        "anchoring_and_time": "The date, body, meeting and topic are all specified, so the need is fully identified.",
        "consequence": "The answer fully lists the speakers but carries little substantive content about the situation or response.",
        "lexical_distance": "The question reuses the topic phrase \"role of business in conflict prevention, peacekeeping and post-conflict peace-building\" nearly verbatim. That phrase is a necessary anchor.",
        "linguistic_quality": "The question is clear and idiomatic, slightly long.",
        "search_realism": "It asks for a list of speakers, close to an isolated datum by name, with little conceptual need."
      },
      "scores": {
        "anchoring_and_time": 5,
        "consequence": 3,
        "lexical_distance": 3,
        "linguistic_quality": 4,
        "search_realism": 2
      }
    },
    "anchoring_and_time": 5,
    "consequence": 3,
    "lexical_distance": 3,
    "linguistic_quality": 4,
    "overall": 17,
    "reason": "search_realism: It asks for a list of speakers, close to an isolated datum by name, with little conceptual need.; anchoring_and_time: The date, body, meeting and topic are all specified, so the need is fully identified.; consequence: The answer fully lists the speakers but carries little substantive content about the situation or response.; lexical_distance: The question reuses the topic phrase \"role of business in conflict prevention, peacekeeping and post-conflict peace-building\" nearly verbatim. That phrase is a necessary anchor.; linguistic_quality: The question is clear and idiomatic, slightly long.",
    "search_realism": 2
  }
]
````

### mode/un/2004/s/2004/674#6/practitioner: faithfulness — completed

````json
[
  {
    "_response": {
      "grounding": 4,
      "index": 0,
      "numerical_fidelity": 5,
      "precision": 4,
      "reason": "The target contains this exact phrase: the declaration of the Third Summit of the African Union held in Addis Ababa on 8 July 2004 on Darfur, plus AU efforts. The question's phrasing 'identified in connection with Darfur' is vague. The target block is a preambular recalling clause, so 'identified' is loosely worded but acceptable. The answer is a verbatim fragment with a trailing comma. The dates are exact."
    },
    "grounding": 4,
    "numerical_fidelity": 5,
    "overall": 13,
    "precision": 4,
    "reason": "The target contains this exact phrase: the declaration of the Third Summit of the African Union held in Addis Ababa on 8 July 2004 on Darfur, plus AU efforts. The question's phrasing 'identified in connection with Darfur' is vague. The target block is a preambular recalling clause, so 'identified' is loosely worded but acceptable. The answer is a verbatim fragment with a trailing comma. The dates are exact."
  },
  {
    "_response": {
      "grounding": 5,
      "index": 1,
      "numerical_fidelity": 5,
      "precision": 4,
      "reason": "The target supports the answer: the 3 July 2004 joint communiqué, the Joint Implementation Mechanism, and the Darfur Plan of Action signed 5 August 2004. The answer omits 'to the Sudan' after 'Special Representative of the Secretary-General of the United Nations', which is a minor truncation. The question is slightly awkward in calling the communiqué and plan 'instruments', but it is faithful. The dates are correct. The 'Welcoming' wording keeps the clause's status as welcomed."
    },
    "grounding": 5,
    "numerical_fidelity": 5,
    "overall": 14,
    "precision": 4,
    "reason": "The target supports the answer: the 3 July 2004 joint communiqué, the Joint Implementation Mechanism, and the Darfur Plan of Action signed 5 August 2004. The answer omits 'to the Sudan' after 'Special Representative of the Secretary-General of the United Nations', which is a minor truncation. The question is slightly awkward in calling the communiqué and plan 'instruments', but it is faithful. The dates are correct. The 'Welcoming' wording keeps the clause's status as welcomed."
  },
  {
    "_response": {
      "grounding": 5,
      "index": 2,
      "numerical_fidelity": 5,
      "precision": 5,
      "reason": "The target says verbatim that the body reaffirms its commitment to respect and ensure respect for Sudan's sovereignty, territorial integrity and independence, and calls on all States actively to affirm that commitment. The answer resolves both parts of the question completely, with no extra material and no numbers to check."
    },
    "grounding": 5,
    "numerical_fidelity": 5,
    "overall": 15,
    "precision": 5,
    "reason": "The target says verbatim that the body reaffirms its commitment to respect and ensure respect for Sudan's sovereignty, territorial integrity and independence, and calls on all States actively to affirm that commitment. The answer resolves both parts of the question completely, with no extra material and no numbers to check."
  }
]
````

### mode/un/2004/s/2004/674#6/practitioner: quality_index_recovery — completed

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
      "candidate_id": "q_70c74e683d239dc0cd98c809",
      "checks": {
        "metadata": "pass",
        "mode": "fail",
        "support": "pass"
      },
      "index": 0,
      "problems": [
        "mode: the question is a generic recall with no substantive need",
        "informativeness: the answer has no substantive content and only restates the question",
        "The anchor 'Darfur' is generic, though it is a valid substring"
      ],
      "score_notes": {
        "anchoring_and_time": "The question gives the date 8 July 2004, Darfur and the African Union, but no regime or issue beyond that. The answer essentially restates the question's anchors. The question's 'on 8 July 2004' is supported.",
        "consequence": "The content is a preambular citation of an AU summit declaration and unspecified 'efforts'. It has no substantive content on measures, conditions or findings.",
        "informativeness": "The answer just repeats the date and Darfur. It does not say what the declaration or the efforts contained, so it is largely circular.",
        "linguistic_quality": "Grammatical, but 'identified in connection with' is vague. The answer is a dangling fragment ending in a comma.",
        "practitioner_realism": "Asks a vague 'what event and efforts were identified', which is close to generic comprehension. It also reads as a preambular recall, not a real specialist need."
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
    "reason": "practitioner_realism: Asks a vague 'what event and efforts were identified', which is close to generic comprehension. It also reads as a preambular recall, not a real specialist need.; anchoring_and_time: The question gives the date 8 July 2004, Darfur and the African Union, but no regime or issue beyond that. The answer essentially restates the question's anchors. The question's 'on 8 July 2004' is supported.; consequence: The content is a preambular citation of an AU summit declaration and unspecified 'efforts'. It has no substantive content on measures, conditions or findings.; informativeness: The answer just repeats the date and Darfur. It does not say what the declaration or the efforts contained, so it is largely circular.; linguistic_quality: Grammatical, but 'identified in connection with' is vague. The answer is a dangling fragment ending in a comma."
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
      "candidate_id": "q_cb1e0d0614fa551d7542e3e1",
      "checks": {
        "metadata": "pass",
        "mode": "pass",
        "support": "pass"
      },
      "index": 1,
      "problems": [
        "linguistic_quality: awkward wording 'Sudan-related instruments and implementation arrangement'",
        "The question does not say who welcomed the instruments"
      ],
      "score_notes": {
        "anchoring_and_time": "Gives the dates 3 July and 5 August 2004 plus Sudan and Darfur. The instruments are identifiable, though the welcoming body (the Arab League) is not named.",
        "consequence": "The content is concrete: a joint communiqué, a Joint Implementation Mechanism and a Plan of Action. It still sits in a preambular welcoming clause.",
        "informativeness": "The answer names the communiqué parties, the mechanism and the Plan of Action signatories, so it resolves the question fully. It includes the 'Welcoming' opener, which is minor.",
        "linguistic_quality": "The phrase 'Sudan-related instruments and implementation arrangement' is clumsy and the question is slightly bundled.",
        "practitioner_realism": "A plausible need to identify which instruments the Arab League welcomed. It is a bit list-like, asking for instruments together with a mechanism."
      },
      "scores": {
        "anchoring_and_time": 4,
        "consequence": 3,
        "informativeness": 4,
        "linguistic_quality": 3,
        "practitioner_realism": 3
      }
    },
    "anchoring_and_time": 4,
    "consequence": 3,
    "informativeness": 4,
    "linguistic_quality": 3,
    "overall": 17,
    "practitioner_realism": 3,
    "reason": "practitioner_realism: A plausible need to identify which instruments the Arab League welcomed. It is a bit list-like, asking for instruments together with a mechanism.; anchoring_and_time: Gives the dates 3 July and 5 August 2004 plus Sudan and Darfur. The instruments are identifiable, though the welcoming body (the Arab League) is not named.; consequence: The content is concrete: a joint communiqué, a Joint Implementation Mechanism and a Plan of Action. It still sits in a preambular welcoming clause.; informativeness: The answer names the communiqué parties, the mechanism and the Plan of Action signatories, so it resolves the question fully. It includes the 'Welcoming' opener, which is minor.; linguistic_quality: The phrase 'Sudan-related instruments and implementation arrangement' is clumsy and the question is slightly bundled."
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
      "candidate_id": "q_fa66bd17b1d72307fa85d960",
      "checks": {
        "metadata": "pass",
        "mode": "fail",
        "support": "pass"
      },
      "index": 2,
      "problems": [
        "anchoring_and_time: no time reference and no identification of the body or situation",
        "mode: insufficient context and time, so the question could match many documents"
      ],
      "score_notes": {
        "anchoring_and_time": "There is no date, no body and no situation such as Darfur. 'Sudan' alone cannot pin down the period, so the question is unanchored in time.",
        "consequence": "The content is a substantive commitment and a call on States, though the language is boilerplate.",
        "informativeness": "The answer fully covers both parts: the commitment to respect the sovereignty, territorial integrity and independence of the Sudan, and the call on all States to affirm it.",
        "linguistic_quality": "Clear, but the wording 'what were all States called upon to do' is slightly awkward.",
        "practitioner_realism": "A reasonable question on a reaffirmed commitment to sovereignty, but it is a two-part bundle."
      },
      "scores": {
        "anchoring_and_time": 1,
        "consequence": 3,
        "informativeness": 4,
        "linguistic_quality": 3,
        "practitioner_realism": 3
      }
    },
    "anchoring_and_time": 1,
    "consequence": 3,
    "informativeness": 4,
    "linguistic_quality": 3,
    "overall": 14,
    "practitioner_realism": 3,
    "reason": "practitioner_realism: A reasonable question on a reaffirmed commitment to sovereignty, but it is a two-part bundle.; anchoring_and_time: There is no date, no body and no situation such as Darfur. 'Sudan' alone cannot pin down the period, so the question is unanchored in time.; consequence: The content is a substantive commitment and a call on States, though the language is boilerplate.; informativeness: The answer fully covers both parts: the commitment to respect the sovereignty, territorial integrity and independence of the Sudan, and the call on all States to affirm it.; linguistic_quality: Clear, but the wording 'what were all States called upon to do' is slightly awkward."
  }
]
````

### mode/un/2007/a/res/62/137#12/practitioner: faithfulness — completed

````json
[
  {
    "_response": {
      "grounding": 4,
      "index": 0,
      "numerical_fidelity": 5,
      "precision": 4,
      "reason": "The target names the actors: Governments, all UN system entities (including agencies, funds and programmes) and relevant civil society actors. It also gives the stages: implementation, follow-up, and preparation for summits, conferences and special sessions. The question's framing as the 2007 follow-up to the Beijing Platform is a slight misframing, since paragraph 12 concerns UN summits and conferences generally, although the resolution is the Beijing follow-up resolution of 2007. The answer is the whole paragraph, including the long list of named events, which is more than the actors-and-stages question needs, so precision is slightly reduced. The numbers and dates in the span match the source exactly."
    },
    "grounding": 4,
    "numerical_fidelity": 5,
    "overall": 13,
    "precision": 4,
    "reason": "The target names the actors: Governments, all UN system entities (including agencies, funds and programmes) and relevant civil society actors. It also gives the stages: implementation, follow-up, and preparation for summits, conferences and special sessions. The question's framing as the 2007 follow-up to the Beijing Platform is a slight misframing, since paragraph 12 concerns UN summits and conferences generally, although the resolution is the Beijing follow-up resolution of 2007. The answer is the whole paragraph, including the long list of named events, which is more than the actors-and-stages question needs, so precision is slightly reduced. The numbers and dates in the span match the source exactly."
  },
  {
    "_response": {
      "grounding": 5,
      "index": 1,
      "numerical_fidelity": 5,
      "precision": 4,
      "reason": "The question asks which 2007 and 2008 events were specifically named for gender attention in preparation, and the target lists them: the commemorative high-level plenary meeting on children, the COP 13 and CMP 3 in Bali, the Doha Financing for Development follow-up conference, and the Accra High-level Forum on Aid Effectiveness. The answer contains all of these. It also carries the opening clause on the actors and the general integration call, which is unnecessary for this question, so precision is slightly reduced. The years, places and ordinals are exact."
    },
    "grounding": 5,
    "numerical_fidelity": 5,
    "overall": 14,
    "precision": 4,
    "reason": "The question asks which 2007 and 2008 events were specifically named for gender attention in preparation, and the target lists them: the commemorative high-level plenary meeting on children, the COP 13 and CMP 3 in Bali, the Doha Financing for Development follow-up conference, and the Accra High-level Forum on Aid Effectiveness. The answer contains all of these. It also carries the opening clause on the actors and the general integration call, which is unnecessary for this question, so precision is slightly reduced. The years, places and ordinals are exact."
  }
]
````

### mode/un/2007/a/res/62/137#12/practitioner: quality_index_recovery — completed

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
      "candidate_id": "q_0e85e915d132f55d373aedd8",
      "checks": {
        "metadata": "fail",
        "mode": "pass",
        "support": "pass"
      },
      "index": 0,
      "problems": [
        "metadata: the anchors \"integration of gender perspectives\" and \"implementation of and follow-up\" are not verbatim substrings of the question. The question has \"integrate gender perspectives\" and no \"implementation of and follow-up\". \"Governments and all entities of the United Nations system\" is also absent from the question.",
        "anchoring_and_time: the question does not hint at the summit or conference context, so the framing is vague.",
        "informativeness: the answer includes the full event list, which goes beyond what the question asks."
      ],
      "score_notes": {
        "anchoring_and_time": "\"2007 follow-up to the Beijing Platform for Action\" gives the regime and year. It is a bit loose because the resolution was adopted in Dec 2007 and the paragraph also covers 2008 events. The anchor is adequate but not distinctive about this paragraph.",
        "consequence": "The paragraph gives concrete content: who is urged to integrate gender perspectives into summit and conference follow-up and preparation. That is operative and specific.",
        "informativeness": "The answer covers the actors and the stages (implementation, follow-up, preparation). It is the whole paragraph, including a long list of events that the question does not ask for. The \"stages\" part is only loosely matched, so the span is overlong relative to the ask.",
        "linguistic_quality": "The question is readable, but \"at what stages\" is ambiguous. \"In the 2007 follow-up\" is awkward phrasing. The answer is an unnecessarily long verbatim span.",
        "practitioner_realism": "The need is plausible but bundles two asks (which actors, and at what stages). The phrase \"at what stages\" is vague and reads as a generic comprehension prompt."
      },
      "scores": {
        "anchoring_and_time": 3,
        "consequence": 4,
        "informativeness": 3,
        "linguistic_quality": 3,
        "practitioner_realism": 3
      }
    },
    "anchoring_and_time": 3,
    "consequence": 4,
    "informativeness": 3,
    "linguistic_quality": 3,
    "overall": 16,
    "practitioner_realism": 3,
    "reason": "practitioner_realism: The need is plausible but bundles two asks (which actors, and at what stages). The phrase \"at what stages\" is vague and reads as a generic comprehension prompt.; anchoring_and_time: \"2007 follow-up to the Beijing Platform for Action\" gives the regime and year. It is a bit loose because the resolution was adopted in Dec 2007 and the paragraph also covers 2008 events. The anchor is adequate but not distinctive about this paragraph.; consequence: The paragraph gives concrete content: who is urged to integrate gender perspectives into summit and conference follow-up and preparation. That is operative and specific.; informativeness: The answer covers the actors and the stages (implementation, follow-up, preparation). It is the whole paragraph, including a long list of events that the question does not ask for. The \"stages\" part is only loosely matched, so the span is overlong relative to the ask.; linguistic_quality: The question is readable, but \"at what stages\" is ambiguous. \"In the 2007 follow-up\" is awkward phrasing. The answer is an unnecessarily long verbatim span."
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
      "candidate_id": "q_a393585afd4aaf7245746f35",
      "checks": {
        "metadata": "fail",
        "mode": "uncertain",
        "support": "pass"
      },
      "index": 1,
      "problems": [
        "metadata: the anchors \"gender attention\" and \"Doha in 2008\" and \"Accra in 2008\" are not in the question. The question has \"2007 and 2008\" and \"in preparation\". The anchors are not verbatim substrings.",
        "mode: \"this General Assembly follow-up\" is a deictic reference that depends on the source document and does not identify the regime. This makes the anchoring weak."
      ],
      "score_notes": {
        "anchoring_and_time": "\"2007 and 2008 events\" and \"General Assembly follow-up\" give only a vague regime anchor. The Beijing/women follow-up is not named, so the topic is weakly identified, although the gender attention and preparation cues help.",
        "consequence": "Identifies concrete named events (the children's special session follow-up, the Bali COP 13/CMP 3, the Doha FfD review, and the Accra forum), which is specific and useful.",
        "informativeness": "The answer span contains the full event list. It includes the leading urging clause, which is useful context. The listing fully determines the answer.",
        "linguistic_quality": "The question is understandable but wordy and awkward: \"specifically named for gender attention in preparation under this General Assembly follow-up\". \"This\" is a deictic reference that is unresolved without the document.",
        "practitioner_realism": "A bounded, realistic need: which specific events were named for gender attention. It is a single ask and useful for a gender-mainstreaming practitioner."
      },
      "scores": {
        "anchoring_and_time": 3,
        "consequence": 4,
        "informativeness": 4,
        "linguistic_quality": 3,
        "practitioner_realism": 4
      }
    },
    "anchoring_and_time": 3,
    "consequence": 4,
    "informativeness": 4,
    "linguistic_quality": 3,
    "overall": 18,
    "practitioner_realism": 4,
    "reason": "practitioner_realism: A bounded, realistic need: which specific events were named for gender attention. It is a single ask and useful for a gender-mainstreaming practitioner.; anchoring_and_time: \"2007 and 2008 events\" and \"General Assembly follow-up\" give only a vague regime anchor. The Beijing/women follow-up is not named, so the topic is weakly identified, although the gender attention and preparation cues help.; consequence: Identifies concrete named events (the children's special session follow-up, the Bali COP 13/CMP 3, the Doha FfD review, and the Accra forum), which is specific and useful.; informativeness: The answer span contains the full event list. It includes the leading urging clause, which is useful context. The listing fully determines the answer.; linguistic_quality: The question is understandable but wordy and awkward: \"specifically named for gender attention in preparation under this General Assembly follow-up\". \"This\" is a deictic reference that is unresolved without the document."
  }
]
````

### mode/un/2008/a/ac_109/2008/sr_2#1/semantic: faithfulness — completed

````json
[
  {
    "_response": {
      "grounding": 5,
      "index": 0,
      "numerical_fidelity": 5,
      "precision": 5,
      "reason": "The target says the Bureau recommended holding the seminar in Bandung on 14-16 May 2008, that the Committee would also celebrate the Week of Solidarity at the seminar, and that 'It was so decided.' The question's premise of an approved arrangement is therefore supported. The answer covers the location, dates, solidarity week and approval, and the dates are exact. The paragraph number '3.' embedded in the span is trivial noise."
    },
    "grounding": 5,
    "numerical_fidelity": 5,
    "overall": 15,
    "precision": 5,
    "reason": "The target says the Bureau recommended holding the seminar in Bandung on 14-16 May 2008, that the Committee would also celebrate the Week of Solidarity at the seminar, and that 'It was so decided.' The question's premise of an approved arrangement is therefore supported. The answer covers the location, dates, solidarity week and approval, and the dates are exact. The paragraph number '3.' embedded in the span is trivial noise."
  },
  {
    "_response": {
      "grounding": 5,
      "index": 1,
      "numerical_fidelity": 5,
      "precision": 5,
      "reason": "The target lists the delegation by regional group (Congo and Ethiopia; Syrian Arab Republic and India; Cuba and Dominica; Russian Federation) and says the UN would bear travel costs. This answers both parts of the question. The 'agreed ad referendum' status is kept in the answer, and no numbers appear in the span."
    },
    "grounding": 5,
    "numerical_fidelity": 5,
    "overall": 15,
    "precision": 5,
    "reason": "The target lists the delegation by regional group (Congo and Ethiopia; Syrian Arab Republic and India; Cuba and Dominica; Russian Federation) and says the UN would bear travel costs. This answers both parts of the question. The 'agreed ad referendum' status is kept in the answer, and no numbers appear in the span."
  }
]
````

### mode/un/2008/a/ac_109/2008/sr_2#1/semantic: quality_index_recovery — completed

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
      "candidate_id": "q_c2cf79811fabd66bfa21cc48",
      "checks": {
        "metadata": "pass",
        "mode": "pass",
        "support": "pass"
      },
      "index": 0,
      "problems": [
        "consequence: the question gives away the venue and dates, so the answer adds little beyond the Week of Solidarity.",
        "consequence: the answer span includes procedural scaffolding and a paragraph number."
      ],
      "score_notes": {
        "anchoring_and_time": "The question names Bandung and the exact dates, and the seminar is clearly identifiable.",
        "consequence": "The answer supplies the decision and the Week of Solidarity observance. The venue and dates are already in the question, so the new substance is thin. The answer also includes procedural filler such as 'If there was no objection...' and '3. It was so decided.'",
        "lexical_distance": "The question copies the venue, dates and 'Pacific regional seminar' from the source. These are anchors, but it also reuses 'solidarity' and adds little reformulation.",
        "linguistic_quality": "The question is clear and grammatical. 'Arrangement... approved' is slightly vague, and the phrase 'associated solidarity observance' is a bit clunky.",
        "search_realism": "The need (what was approved for the seminar) is reasonable, but it is mostly a logistics lookup about venue and dates, and the question already gives them, so it is somewhat generic."
      },
      "scores": {
        "anchoring_and_time": 5,
        "consequence": 3,
        "lexical_distance": 3,
        "linguistic_quality": 4,
        "search_realism": 3
      }
    },
    "anchoring_and_time": 5,
    "consequence": 3,
    "lexical_distance": 3,
    "linguistic_quality": 4,
    "overall": 18,
    "reason": "search_realism: The need (what was approved for the seminar) is reasonable, but it is mostly a logistics lookup about venue and dates, and the question already gives them, so it is somewhat generic.; anchoring_and_time: The question names Bandung and the exact dates, and the seminar is clearly identifiable.; consequence: The answer supplies the decision and the Week of Solidarity observance. The venue and dates are already in the question, so the new substance is thin. The answer also includes procedural filler such as 'If there was no objection...' and '3. It was so decided.'; lexical_distance: The question copies the venue, dates and 'Pacific regional seminar' from the source. These are anchors, but it also reuses 'solidarity' and adds little reformulation.; linguistic_quality: The question is clear and grammatical. 'Arrangement... approved' is slightly vague, and the phrase 'associated solidarity observance' is a bit clunky.",
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
      "candidate_id": "q_939d0b48eefc9b913a928a29",
      "checks": {
        "metadata": "pass",
        "mode": "pass",
        "support": "pass"
      },
      "index": 1,
      "problems": [],
      "score_notes": {
        "anchoring_and_time": "The question identifies the Special Committee's delegation to the 2008 Pacific seminar, which is enough to pin it down. It has no venue, but the year and seminar suffice.",
        "consequence": "The answer gives the full composition by regional group and states that the UN bears travel costs. This fully resolves both parts of the question. The 'ad referendum' status is preserved.",
        "lexical_distance": "The question paraphrases the source ('composed', 'cover its travel costs') and keeps only the necessary terms.",
        "linguistic_quality": "The question is concise, idiomatic and clear.",
        "search_realism": "This is a natural stakeholder question about who represents the Committee and who pays. It asks two linked things, but both concern the same delegation arrangement."
      },
      "scores": {
        "anchoring_and_time": 4,
        "consequence": 5,
        "lexical_distance": 4,
        "linguistic_quality": 5,
        "search_realism": 4
      }
    },
    "anchoring_and_time": 4,
    "consequence": 5,
    "lexical_distance": 4,
    "linguistic_quality": 5,
    "overall": 22,
    "reason": "search_realism: This is a natural stakeholder question about who represents the Committee and who pays. It asks two linked things, but both concern the same delegation arrangement.; anchoring_and_time: The question identifies the Special Committee's delegation to the 2008 Pacific seminar, which is enough to pin it down. It has no venue, but the year and seminar suffice.; consequence: The answer gives the full composition by regional group and states that the UN bears travel costs. This fully resolves both parts of the question. The 'ad referendum' status is preserved.; lexical_distance: The question paraphrases the source ('composed', 'cover its travel costs') and keeps only the necessary terms.; linguistic_quality: The question is concise, idiomatic and clear.",
    "search_realism": 4
  }
]
````

### mode/un/2013/a/res/67/199#12/semantic: faithfulness — completed

````json
[
  {
    "_response": {
      "grounding": 5,
      "index": 0,
      "numerical_fidelity": 5,
      "precision": 4,
      "reason": "Paragraph 24 states that sovereign debt crises tend to be costly and disruptive, including for employment and productive investments, and tend to be followed by public spending cuts that affect the poor and vulnerable. This matches the question. The date is a permitted contextual pin from the resolution's adoption date. The answer also includes the first clause on debt sustainability and growth, which the question does not ask about and which could be trimmed."
    },
    "grounding": 5,
    "numerical_fidelity": 5,
    "overall": 14,
    "precision": 4,
    "reason": "Paragraph 24 states that sovereign debt crises tend to be costly and disruptive, including for employment and productive investments, and tend to be followed by public spending cuts that affect the poor and vulnerable. This matches the question. The date is a permitted contextual pin from the resolution's adoption date. The answer also includes the first clause on debt sustainability and growth, which the question does not ask about and which could be trimmed."
  },
  {
    "_response": {
      "grounding": 5,
      "index": 1,
      "numerical_fidelity": 5,
      "precision": 5,
      "reason": "Paragraph 25 says the crisis highlighted the need for reform and added new impetus to international discussions on reforming the international financial system and architecture. It also says to encourage open, inclusive and transparent dialogue. The span answers the question completely and with little extra material. The date comes from the resolution's metadata. The wording \"calls for reform\" is a slight paraphrase but is supported."
    },
    "grounding": 5,
    "numerical_fidelity": 5,
    "overall": 15,
    "precision": 5,
    "reason": "Paragraph 25 says the crisis highlighted the need for reform and added new impetus to international discussions on reforming the international financial system and architecture. It also says to encourage open, inclusive and transparent dialogue. The span answers the question completely and with little extra material. The date comes from the resolution's metadata. The wording \"calls for reform\" is a slight paraphrase but is supported."
  },
  {
    "_response": {
      "grounding": 5,
      "index": 2,
      "numerical_fidelity": 5,
      "precision": 5,
      "reason": "Paragraph 26 notes efforts at the national, regional and international levels. Their stated aims are a full return to growth with quality jobs, reform and strengthening of financial systems, and strong, sustainable and balanced global growth. The answer covers the question completely, and its \"notes\" framing preserves the status as an acknowledgment. The date is a permitted contextual pin."
    },
    "grounding": 5,
    "numerical_fidelity": 5,
    "overall": 15,
    "precision": 5,
    "reason": "Paragraph 26 notes efforts at the national, regional and international levels. Their stated aims are a full return to growth with quality jobs, reform and strengthening of financial systems, and strong, sustainable and balanced global growth. The answer covers the question completely, and its \"notes\" framing preserves the status as an acknowledgment. The date is a permitted contextual pin."
  }
]
````

### mode/un/2013/a/res/67/199#12/semantic: quality_index_recovery — completed

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
      "candidate_id": "q_db630e82142135c62669faff",
      "checks": {
        "metadata": "pass",
        "mode": "pass",
        "support": "pass"
      },
      "index": 0,
      "problems": [
        "anchoring_and_time: the date is the document's adoption date and there is no other subject context."
      ],
      "score_notes": {
        "anchoring_and_time": "The date anchors the question to the GA resolution, but it is a document date and the question has no topical context such as development financing. It is still reasonably identifiable.",
        "consequence": "The answer states the costly and disruptive effects, employment and investment impacts, and spending cuts hitting the poor. It also carries extra material on debt sustainability and growth, which is acceptable as context.",
        "lexical_distance": "It reuses 'sovereign debt crises' and 'consequences', which are necessary terms, but the rest stays close to the source wording with little reformulation.",
        "linguistic_quality": "Clear, concise and idiomatic. 'Identified' is slightly generic.",
        "search_realism": "A natural, bounded need about the effects of sovereign debt crises. It asks about consequences, not an isolated datum."
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
    "reason": "search_realism: A natural, bounded need about the effects of sovereign debt crises. It asks about consequences, not an isolated datum.; anchoring_and_time: The date anchors the question to the GA resolution, but it is a document date and the question has no topical context such as development financing. It is still reasonably identifiable.; consequence: The answer states the costly and disruptive effects, employment and investment impacts, and spending cuts hitting the poor. It also carries extra material on debt sustainability and growth, which is acceptable as context.; lexical_distance: It reuses 'sovereign debt crises' and 'consequences', which are necessary terms, but the rest stays close to the source wording with little reformulation.; linguistic_quality: Clear, concise and idiomatic. 'Identified' is slightly generic.",
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
      "candidate_id": "q_fa89f15ebd637b6f184d3b29",
      "checks": {
        "metadata": "pass",
        "mode": "pass",
        "support": "pass"
      },
      "index": 1,
      "problems": [
        "anchoring_and_time: the December 2012 date is the document date, not a supported event date.",
        "metadata: the 'response' framing is arguable, since the question is closer to a situation/rationale, but it is acceptable."
      ],
      "score_notes": {
        "anchoring_and_time": "'December 2012' is the document date and is used as if it were the event time. The subject is clear but generic, since many texts discuss crisis and reform.",
        "consequence": "The answer states that the crisis highlighted the need for reform and added impetus to discussions, and it lists the issues covered. It fully answers the 'shape' relationship.",
        "lexical_distance": "It paraphrases 'highlighted the need' as 'shape calls'. It keeps necessary terms such as 'international financial system'.",
        "linguistic_quality": "Fluent and clear. 'Shape calls for reform' is slightly loose.",
        "search_realism": "A plausible conceptual question on how the crisis influenced reform discussions. It is bounded and asks for a rationale."
      },
      "scores": {
        "anchoring_and_time": 3,
        "consequence": 4,
        "lexical_distance": 4,
        "linguistic_quality": 4,
        "search_realism": 4
      }
    },
    "anchoring_and_time": 3,
    "consequence": 4,
    "lexical_distance": 4,
    "linguistic_quality": 4,
    "overall": 19,
    "reason": "search_realism: A plausible conceptual question on how the crisis influenced reform discussions. It is bounded and asks for a rationale.; anchoring_and_time: 'December 2012' is the document date and is used as if it were the event time. The subject is clear but generic, since many texts discuss crisis and reform.; consequence: The answer states that the crisis highlighted the need for reform and added impetus to discussions, and it lists the issues covered. It fully answers the 'shape' relationship.; lexical_distance: It paraphrases 'highlighted the need' as 'shape calls'. It keeps necessary terms such as 'international financial system'.; linguistic_quality: Fluent and clear. 'Shape calls for reform' is slightly loose.",
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
      "candidate_id": "q_ffb125f3725a8bb55900b17e",
      "checks": {
        "metadata": "pass",
        "mode": "pass",
        "support": "pass"
      },
      "index": 2,
      "problems": [
        "search_realism: the question is framed around 'the General Assembly's resolution', which is generic-report phrasing.",
        "anchoring_and_time: the question refers to 'the resolution' by date, close to document deixis."
      ],
      "score_notes": {
        "anchoring_and_time": "The date and the resolution are given, but the document is cited by date in a way that edges toward document-reference phrasing. The crisis subject is clear.",
        "consequence": "The answer gives the specific aims: a return to growth with quality jobs, stronger financial systems, and balanced global growth. It is informative, and the note that the efforts were only noted is preserved.",
        "lexical_distance": "It reuses 'efforts', 'financial and economic crisis' and 'address', with little reformulation.",
        "linguistic_quality": "Somewhat wordy and awkward: 'objectives were associated with efforts... in the resolution'.",
        "search_realism": "The need is bounded, but it is partly a generic report of what the resolution noted. 'Associated with efforts' is vague."
      },
      "scores": {
        "anchoring_and_time": 3,
        "consequence": 4,
        "lexical_distance": 3,
        "linguistic_quality": 3,
        "search_realism": 3
      }
    },
    "anchoring_and_time": 3,
    "consequence": 4,
    "lexical_distance": 3,
    "linguistic_quality": 3,
    "overall": 16,
    "reason": "search_realism: The need is bounded, but it is partly a generic report of what the resolution noted. 'Associated with efforts' is vague.; anchoring_and_time: The date and the resolution are given, but the document is cited by date in a way that edges toward document-reference phrasing. The crisis subject is clear.; consequence: The answer gives the specific aims: a return to growth with quality jobs, stronger financial systems, and balanced global growth. It is informative, and the note that the efforts were only noted is preserved.; lexical_distance: It reuses 'efforts', 'financial and economic crisis' and 'address', with little reformulation.; linguistic_quality: Somewhat wordy and awkward: 'objectives were associated with efforts... in the resolution'.",
    "search_realism": 3
  }
]
````

### mode/un/2014/s/res/2140__2014_#13/semantic: faithfulness — completed

````json
[
  {
    "_response": {
      "grounding": 5,
      "index": 0,
      "numerical_fidelity": 5,
      "precision": 5,
      "reason": "Items (b) and (c) directly state the Committee's tasks to seek and review information on those who may engage in the acts in paras 17–18 and to designate individuals and entities for the measures. The question's premise (Yemen sanctions committee, 2014) is supported by the resolution. The answer is concise and complete. The numbers in the answer (paragraphs 11, 15, 17, 18) match the target."
    },
    "grounding": 5,
    "numerical_fidelity": 5,
    "overall": 15,
    "precision": 5,
    "reason": "Items (b) and (c) directly state the Committee's tasks to seek and review information on those who may engage in the acts in paras 17–18 and to designate individuals and entities for the measures. The question's premise (Yemen sanctions committee, 2014) is supported by the resolution. The answer is concise and complete. The numbers in the answer (paragraphs 11, 15, 17, 18) match the target."
  },
  {
    "_response": {
      "grounding": 4,
      "index": 1,
      "numerical_fidelity": 5,
      "precision": 3,
      "reason": "Item (e) clearly supports the reporting duty, and the 60-day figure is exact. Item (d), establishing guidelines to facilitate implementation, is a task and only loosely fits 'support'. The question's 'support and reporting duties' is vague and somewhat misframed, and the answer leaves that ambiguity unresolved. Nothing is unsupported. Numbers are accurate."
    },
    "grounding": 4,
    "numerical_fidelity": 5,
    "overall": 12,
    "precision": 3,
    "reason": "Item (e) clearly supports the reporting duty, and the 60-day figure is exact. Item (d), establishing guidelines to facilitate implementation, is a task and only loosely fits 'support'. The question's 'support and reporting duties' is vague and somewhat misframed, and the answer leaves that ambiguity unresolved. Nothing is unsupported. Numbers are accurate."
  },
  {
    "_response": {
      "grounding": 5,
      "index": 2,
      "numerical_fidelity": 5,
      "precision": 5,
      "reason": "Items (f) and (g) cover engaging States through dialogue and seeking information. Item (h) covers examining and acting on information about alleged violations or non-compliance. All three are needed to answer both parts of the question and all are supported. Paragraphs 11 and 15 are cited correctly."
    },
    "grounding": 5,
    "numerical_fidelity": 5,
    "overall": 15,
    "precision": 5,
    "reason": "Items (f) and (g) cover engaging States through dialogue and seeking information. Item (h) covers examining and acting on information about alleged violations or non-compliance. All three are needed to answer both parts of the question and all are supported. Paragraphs 11 and 15 are cited correctly."
  }
]
````

### mode/un/2014/s/res/2140__2014_#13/semantic: quality_index_recovery — completed

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
      "candidate_id": "q_8bff6165432cc9d1291645ee",
      "checks": {
        "metadata": "pass",
        "mode": "pass",
        "support": "pass"
      },
      "index": 0,
      "problems": [],
      "score_notes": {
        "anchoring_and_time": "Yemen sanctions committee, 2014 and the threat to peace and stability identify the regime well. The 2014 date is supported by the resolution.",
        "consequence": "The answer covers seeking and reviewing information and designating individuals and entities, which fully answers the question. It cites paragraph numbers, but its substance is clear.",
        "lexical_distance": "The question rephrases 'acts that threaten peace, security or stability' and 'designate' as 'identify and designate' and 'involved in threatening'. Legal terms are retained appropriately.",
        "linguistic_quality": "Clear and idiomatic. 'How could' is slightly loose for a mandate, but acceptable.",
        "search_realism": "A natural, bounded process question about how the committee finds and designates targets. It asks about a mechanism, not an isolated datum."
      },
      "scores": {
        "anchoring_and_time": 4,
        "consequence": 4,
        "lexical_distance": 4,
        "linguistic_quality": 4,
        "search_realism": 4
      }
    },
    "anchoring_and_time": 4,
    "consequence": 4,
    "lexical_distance": 4,
    "linguistic_quality": 4,
    "overall": 20,
    "reason": "search_realism: A natural, bounded process question about how the committee finds and designates targets. It asks about a mechanism, not an isolated datum.; anchoring_and_time: Yemen sanctions committee, 2014 and the threat to peace and stability identify the regime well. The 2014 date is supported by the resolution.; consequence: The answer covers seeking and reviewing information and designating individuals and entities, which fully answers the question. It cites paragraph numbers, but its substance is clear.; lexical_distance: The question rephrases 'acts that threaten peace, security or stability' and 'designate' as 'identify and designate' and 'involved in threatening'. Legal terms are retained appropriately.; linguistic_quality: Clear and idiomatic. 'How could' is slightly loose for a mandate, but acceptable.",
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
      "candidate_id": "q_bdf8fbabc0ca762d3e2c2d88",
      "checks": {
        "metadata": "pass",
        "mode": "pass",
        "support": "pass"
      },
      "index": 1,
      "problems": [
        "search_realism: Two loosely bundled asks under a vague label.",
        "consequence: 'Support duties' does not clearly correspond to establishing guidelines."
      ],
      "score_notes": {
        "anchoring_and_time": "Yemen sanctions committee and 2014 give a basic anchor. It is fairly generic and lacks any discriminating topic, such as guidelines on implementation.",
        "consequence": "The answer gives guidelines to facilitate implementation and a 60-day report, which is useful substance. However, 'support duties' does not match guideline-setting well, so the fit is imperfect.",
        "lexical_distance": "Uses generic paraphrase ('support and reporting duties') rather than copying the source wording.",
        "linguistic_quality": "Grammatical, but 'support' is ambiguous and misleading as a label for guideline-setting.",
        "search_realism": "A real need, but 'support and reporting duties' is vague and bundles two asks. The answer items, guidelines and reporting, are only loosely connected."
      },
      "scores": {
        "anchoring_and_time": 3,
        "consequence": 3,
        "lexical_distance": 4,
        "linguistic_quality": 3,
        "search_realism": 3
      }
    },
    "anchoring_and_time": 3,
    "consequence": 3,
    "lexical_distance": 4,
    "linguistic_quality": 3,
    "overall": 16,
    "reason": "search_realism: A real need, but 'support and reporting duties' is vague and bundles two asks. The answer items, guidelines and reporting, are only loosely connected.; anchoring_and_time: Yemen sanctions committee and 2014 give a basic anchor. It is fairly generic and lacks any discriminating topic, such as guidelines on implementation.; consequence: The answer gives guidelines to facilitate implementation and a 60-day report, which is useful substance. However, 'support duties' does not match guideline-setting well, so the fit is imperfect.; lexical_distance: Uses generic paraphrase ('support and reporting duties') rather than copying the source wording.; linguistic_quality: Grammatical, but 'support' is ambiguous and misleading as a label for guideline-setting.",
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
      "candidate_id": "q_811abf42c74f0854fec44c8e",
      "checks": {
        "metadata": "pass",
        "mode": "pass",
        "support": "pass"
      },
      "index": 2,
      "problems": [],
      "score_notes": {
        "anchoring_and_time": "Yemen sanctions and 2014 are sufficient. 'The committee' depends on the Yemen sanctions context, which is stated.",
        "consequence": "The answer fully covers dialogue with States, seeking information and acting on alleged violations, so it resolves both parts of the question.",
        "lexical_distance": "'Suspected breaches' paraphrases 'alleged violations or non-compliance'. 'Engage States' is a natural reformulation.",
        "linguistic_quality": "Clear, concise and idiomatic.",
        "search_realism": "A natural question about the committee's engagement with States and its handling of violations. The two parts are related, both concerning the committee's compliance-oriented functions."
      },
      "scores": {
        "anchoring_and_time": 4,
        "consequence": 5,
        "lexical_distance": 4,
        "linguistic_quality": 4,
        "search_realism": 4
      }
    },
    "anchoring_and_time": 4,
    "consequence": 5,
    "lexical_distance": 4,
    "linguistic_quality": 4,
    "overall": 21,
    "reason": "search_realism: A natural question about the committee's engagement with States and its handling of violations. The two parts are related, both concerning the committee's compliance-oriented functions.; anchoring_and_time: Yemen sanctions and 2014 are sufficient. 'The committee' depends on the Yemen sanctions context, which is stated.; consequence: The answer fully covers dialogue with States, seeking information and acting on alleged violations, so it resolves both parts of the question.; lexical_distance: 'Suspected breaches' paraphrases 'alleged violations or non-compliance'. 'Engage States' is a natural reformulation.; linguistic_quality: Clear, concise and idiomatic.",
    "search_realism": 4
  }
]
````
