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
    "bundle": "simple",
    "bundle_sha256": "cde839246750e3c4f941e2bd1bce2674c9a8b05d9f69be02f3889a2a6527923b",
    "label": "legal-20260930-simple",
    "prompts": {
      "eurlex/decider/generator": {
        "name": "clir-legal-eurlex-decider-generator-en",
        "sha256": "1960b04f96dc771a52fd6146a4493a18f7aa82bdc08d24461e46c1a1b1d2a82e",
        "version": 3
      },
      "eurlex/decider/jev": {
        "name": "clir-legal-eurlex-decider-jev-en",
        "sha256": "40c81300a8f0e897d740257c98e1dccdc3f3d5fb3e9560b06abfb37361bdfb0c",
        "version": 3
      },
      "eurlex/faithfulness": {
        "name": "clir-legal-eurlex-faithfulness-batch-en",
        "sha256": "82d008fcc33b7537fda795806d8bfa54de16752b7bea955c86fe5b74ed6f9fdf",
        "version": 3
      },
      "eurlex/generation/fact_pattern": {
        "name": "clir-legal-eurlex-generation-fact_pattern-en",
        "sha256": "9d4fa96f8c9c744db83a5d1b721f4bece4a0790fe0056131777e9e9e0873e4ef",
        "version": 3
      },
      "eurlex/generation/fact_pattern/de": {
        "name": "clir-legal-eurlex-generation-fact_pattern-de",
        "sha256": "43fefbeb978df6b4d613e65069841686491e762bad38a4cf1171ea07d31b9bef",
        "version": 3
      },
      "eurlex/generation/fact_pattern/es": {
        "name": "clir-legal-eurlex-generation-fact_pattern-es",
        "sha256": "8a4a59262f98cca530633ff599dede127914d5d7378f3f9f471947a2cc0f572a",
        "version": 3
      },
      "eurlex/generation/fact_pattern/fr": {
        "name": "clir-legal-eurlex-generation-fact_pattern-fr",
        "sha256": "003d0523f3172d5cd18b85f3fdb5f618e99c0bacd368c966628b6e592fa99cee",
        "version": 3
      },
      "eurlex/generation/fact_pattern/zh": {
        "name": "clir-legal-eurlex-generation-fact_pattern-zh",
        "sha256": "800c52b222bcd8c9c25fea09ed0504e100bc9b20b6f7fce8d0ddf90d1b26e0eb",
        "version": 3
      },
      "eurlex/generation/lookup": {
        "name": "clir-legal-eurlex-generation-lookup-en",
        "sha256": "57208e6a3c9aa565a89999babe979d1031deef2d9da643a0d54b1529c2b368b6",
        "version": 3
      },
      "eurlex/generation/lookup/de": {
        "name": "clir-legal-eurlex-generation-lookup-de",
        "sha256": "466643a5ae1f950925129cb3c1d9570934a5dcd548856d9e833c78f9a9caa290",
        "version": 3
      },
      "eurlex/generation/lookup/es": {
        "name": "clir-legal-eurlex-generation-lookup-es",
        "sha256": "70a5f36b78fe5602645417514ea66ea0599d5864281abcb4aa401790af9d6eda",
        "version": 3
      },
      "eurlex/generation/lookup/fr": {
        "name": "clir-legal-eurlex-generation-lookup-fr",
        "sha256": "c39539d3bdf1edb7b22514559fbeade6a046465c250b73b11c1c4e4b2174b85b",
        "version": 3
      },
      "eurlex/generation/lookup/zh": {
        "name": "clir-legal-eurlex-generation-lookup-zh",
        "sha256": "008dc1dcbb74f9863199b026f7adb2583050136eaa1bb918c0bf41b752dac3a0",
        "version": 3
      },
      "eurlex/quality/fact_pattern": {
        "name": "clir-legal-eurlex-quality-fact_pattern-en",
        "sha256": "999888883452f5fb8ff818c227cae70b665ea17c5f88da64f93e2190ebb71aa8",
        "version": 3
      },
      "eurlex/quality/lookup": {
        "name": "clir-legal-eurlex-quality-lookup-en",
        "sha256": "c63e9ea1045611a59600f4aafc0641ea7555808cf78744273398cfecf5c8a7e7",
        "version": 3
      },
      "un/decider/generator": {
        "name": "clir-legal-un-decider-generator-en",
        "sha256": "862b4191fb21a0e4fc8561b36b9e116088ef630a689b42d263ffee049ca1b8e2",
        "version": 3
      },
      "un/decider/jev": {
        "name": "clir-legal-un-decider-jev-en",
        "sha256": "dbd7eebf35da7ec529e86c57eaedaad4804862bc23fbd7118f350fe934a3093a",
        "version": 3
      },
      "un/faithfulness": {
        "name": "clir-legal-un-faithfulness-batch-en",
        "sha256": "20e0336b86601ed7941a0180d38d9dda8dda540d5d5c18e8335c94578c5fb84a",
        "version": 3
      },
      "un/generation/descriptive": {
        "name": "clir-legal-un-generation-descriptive-en",
        "sha256": "33ae092af1f6b3821788794dc5ab5c5e81e6fd75d043a69a24555dae182c0957",
        "version": 3
      },
      "un/generation/descriptive/de": {
        "name": "clir-legal-un-generation-descriptive-de",
        "sha256": "9f5e9ea4b2e7a67c380656a8cec34463492ee83e174e8db188b0764eabd60fd0",
        "version": 3
      },
      "un/generation/descriptive/es": {
        "name": "clir-legal-un-generation-descriptive-es",
        "sha256": "82b9ceb4a693856e7d1bb44e8084f40103d837ae9d4048734b11a7adf4760a6d",
        "version": 3
      },
      "un/generation/descriptive/fr": {
        "name": "clir-legal-un-generation-descriptive-fr",
        "sha256": "01f33b6ca8fb66afe1a8db9b4c65fc1997067834748da90d21b9c34bbf4aeb08",
        "version": 3
      },
      "un/generation/descriptive/zh": {
        "name": "clir-legal-un-generation-descriptive-zh",
        "sha256": "788cd99c769153fa0abea925d18e4b522b6919aa5b67d82267e4b126c3e5a971",
        "version": 3
      },
      "un/generation/lookup": {
        "name": "clir-legal-un-generation-lookup-en",
        "sha256": "e93a3d7288502c2aed4b17c41e288eaa30b2b7bb76159c1848c7bef75d1e31e7",
        "version": 3
      },
      "un/generation/lookup/de": {
        "name": "clir-legal-un-generation-lookup-de",
        "sha256": "7f760bbfebb981823e96fd0a2a28583aadaaf7259639a668d83043c06bea65ea",
        "version": 3
      },
      "un/generation/lookup/es": {
        "name": "clir-legal-un-generation-lookup-es",
        "sha256": "cf66a8e9b2ed592da6b89d22984aa43bcbe8a3cc4a16256b9f0bbaa13f559083",
        "version": 3
      },
      "un/generation/lookup/fr": {
        "name": "clir-legal-un-generation-lookup-fr",
        "sha256": "13b9e03f7761f6636ce9cef24ddba720ac5fc6cf1db7dee8b977087afb273f1b",
        "version": 3
      },
      "un/generation/lookup/zh": {
        "name": "clir-legal-un-generation-lookup-zh",
        "sha256": "8073bad190efe5c35da03fe8c8fefeedf49e4a124adae50426884d88ee982538",
        "version": 3
      },
      "un/generation/practitioner": {
        "name": "clir-legal-un-generation-practitioner-en",
        "sha256": "55f37b15d7996c687d943603befff77fd1d31f0fffcee6090238ef43676ea516",
        "version": 3
      },
      "un/generation/practitioner/de": {
        "name": "clir-legal-un-generation-practitioner-de",
        "sha256": "43e174381a7d9fb1ede5432bff921aa7cf84904264c03f9e5a98355b61901f79",
        "version": 3
      },
      "un/generation/practitioner/es": {
        "name": "clir-legal-un-generation-practitioner-es",
        "sha256": "918fb6a4b591cd019f6d06012aa76dd74798cc15947c1af83d1f244ebc25fe8a",
        "version": 3
      },
      "un/generation/practitioner/fr": {
        "name": "clir-legal-un-generation-practitioner-fr",
        "sha256": "d82e89e6bb6d173e84a7e52f640347d57ee1d74954264ee549b8f9cad81401ac",
        "version": 3
      },
      "un/generation/practitioner/zh": {
        "name": "clir-legal-un-generation-practitioner-zh",
        "sha256": "08b06f038b5183955ace29c1ff6841e2be100f13e3a12d38af6e6274a5256049",
        "version": 3
      },
      "un/generation/semantic": {
        "name": "clir-legal-un-generation-semantic-en",
        "sha256": "04570ef539a70a92902f8caebbc31324f10cbc11af584003db8d3d8ba6b12ffe",
        "version": 3
      },
      "un/generation/semantic/de": {
        "name": "clir-legal-un-generation-semantic-de",
        "sha256": "353b6527439a4a03e1ac36f283a7168c0b8d490e0bf08a6e41f171d3722d2016",
        "version": 3
      },
      "un/generation/semantic/es": {
        "name": "clir-legal-un-generation-semantic-es",
        "sha256": "ca58d653bde75e9c3034e5b134d1b2c1113994d5a31643e49d604a98ef5c8ee3",
        "version": 3
      },
      "un/generation/semantic/fr": {
        "name": "clir-legal-un-generation-semantic-fr",
        "sha256": "123b00126c0f95be85e3125b7bad9ca4efab3feb1230de7a62a22ddd84648e96",
        "version": 3
      },
      "un/generation/semantic/zh": {
        "name": "clir-legal-un-generation-semantic-zh",
        "sha256": "3648d1c00dd08731d999a1f3a4174a2d1be20b3560b0cbe8e496a2a26e737d84",
        "version": 3
      },
      "un/generation/technical": {
        "name": "clir-legal-un-generation-technical-en",
        "sha256": "d1342668e6b6e37c0a0384c5ec99932ab3b652629c7b17506f1bcc39951d3534",
        "version": 3
      },
      "un/generation/technical/de": {
        "name": "clir-legal-un-generation-technical-de",
        "sha256": "cf958f05ea552acf007c63a0d6e3348781f191919bcb440b769e2ed0640d2646",
        "version": 3
      },
      "un/generation/technical/es": {
        "name": "clir-legal-un-generation-technical-es",
        "sha256": "fe48723f1f4d0f64ed92608f06d1df59a267a4d0e6e68dd37191763b8a94ad8c",
        "version": 3
      },
      "un/generation/technical/fr": {
        "name": "clir-legal-un-generation-technical-fr",
        "sha256": "be3ec8a50372f18db783f73ee87b7503461e0c1ae812108bb0e46376921b7e65",
        "version": 3
      },
      "un/generation/technical/zh": {
        "name": "clir-legal-un-generation-technical-zh",
        "sha256": "8dd91cd9af75fddf9cbea58f89bf0e88ff5fd626f286202822aeba0c0e9e4c16",
        "version": 3
      },
      "un/quality/descriptive": {
        "name": "clir-legal-un-quality-descriptive-en",
        "sha256": "5c0b3bfa22579ca330233bfaf525d32c1d520f8bf36d48c04d43f19a87febd5a",
        "version": 3
      },
      "un/quality/lookup": {
        "name": "clir-legal-un-quality-lookup-en",
        "sha256": "c5b505eb0af0b6775319f18b0bb8e9599658c8cca618d77feee736866244abc5",
        "version": 3
      },
      "un/quality/practitioner": {
        "name": "clir-legal-un-quality-practitioner-en",
        "sha256": "87aee7a4fc4e86b1df9abcfd98c9bed9584c6de854edb832fe54cd290d801e3a",
        "version": 3
      },
      "un/quality/semantic": {
        "name": "clir-legal-un-quality-semantic-en",
        "sha256": "79208d28d2d2951fbd20538c26001141aad44bc5173bbfa6d7cb904becca1d47",
        "version": 3
      },
      "un/quality/technical": {
        "name": "clir-legal-un-quality-technical-en",
        "sha256": "f705288ccd9a16f99f505f20dea44cbe3662bada6b5c65322d99f784d56891f7",
        "version": 3
      }
    },
    "provider": "mlflow",
    "registry_uri": "sqlite:////home/mehdi/Projects/CLIR_benchmark/.clir/prompts.db",
    "schema_version": 1
  },
  "prompts_sha256": "490186d83ec124579b3118d0476e2f620e40b627d049151af9efefe04a9b49dd",
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
| mode/eurlex/http://data.europa.eu/eli/reg/2006/1083/art_47/oj/lookup | faithfulness | 1 | completed |  |
| mode/eurlex/http://data.europa.eu/eli/reg/2006/1083/art_47/oj/lookup | quality_index_recovery | 1 | completed |  |
| mode/eurlex/http://data.europa.eu/eli/reg/2011/492/art_17/oj/fact_pattern | faithfulness | 1 | completed |  |
| mode/eurlex/http://data.europa.eu/eli/reg/2011/492/art_17/oj/fact_pattern | quality_index_recovery | 1 | completed |  |
| mode/eurlex/http://data.europa.eu/eli/reg_impl/2012/282/art_1/oj/lookup | faithfulness | 1 | completed |  |
| mode/eurlex/http://data.europa.eu/eli/reg_impl/2012/282/art_1/oj/lookup | quality_index_recovery | 1 | completed |  |
| mode/un/2000/cd/pv_841#11/lookup | faithfulness_json_recovery | 1 | completed |  |
| mode/un/2000/cd/pv_841#11/lookup | quality | 1 | completed |  |
| mode/un/2001/cd/pv_880#1/lookup | faithfulness | 1 | completed |  |
| mode/un/2001/cd/pv_880#1/lookup | quality_index_recovery | 1 | completed |  |
| mode/un/2001/s/res/1376_2001_#2/lookup | faithfulness | 1 | completed |  |
| mode/un/2001/s/res/1376_2001_#2/lookup | quality_index_recovery | 1 | completed |  |
| mode/un/2003/a/res/58/298#4/practitioner | faithfulness | 1 | completed |  |
| mode/un/2003/a/res/58/298#4/practitioner | quality_index_recovery | 1 | completed |  |
| mode/un/2004/s/2004/505#15/lookup | faithfulness | 1 | completed |  |
| mode/un/2004/s/2004/505#15/lookup | quality_index_recovery | 1 | completed |  |
| mode/un/2005/a/res/60/226#3/practitioner | faithfulness | 1 | completed |  |
| mode/un/2005/a/res/60/226#3/practitioner | quality_index_recovery | 1 | completed |  |
| mode/un/2006/ccw/conf_iii/sr_2#8/practitioner | faithfulness | 1 | completed |  |
| mode/un/2006/ccw/conf_iii/sr_2#8/practitioner | quality_index_recovery | 1 | completed |  |
| mode/un/2008/s/res/1806_2008_#8/practitioner | faithfulness | 1 | completed |  |
| mode/un/2008/s/res/1806_2008_#8/practitioner | quality_index_recovery | 1 | completed |  |
| mode/un/2009/a/ac_109/2009/sr_7#4/lookup | faithfulness | 1 | completed |  |
| mode/un/2009/a/ac_109/2009/sr_7#4/lookup | quality_index_recovery | 1 | completed |  |
| mode/un/2011/a/res/65/263#2/practitioner | faithfulness | 1 | completed |  |
| mode/un/2011/a/res/65/263#2/practitioner | quality_index_recovery | 1 | completed |  |
| mode/un/2013/a/res/68/18#1/lookup | faithfulness | 1 | completed |  |
| mode/un/2013/a/res/68/18#1/lookup | quality_index_recovery | 1 | completed |  |

## Parsed pipeline outputs

### mode/eurlex/http://data.europa.eu/eli/reg/2006/1083/art_47/oj/lookup: faithfulness — completed

````json
[
  {
    "_response": {
      "grounding": 5,
      "index": 0,
      "numerical_fidelity": 5,
      "precision": 4,
      "reason": "Matches Art 47(1) directly. The declared articles_involved of 47 is correct, since no reference supplies answer content. The answer includes the strategy/implementation clause, which is part of the list of things improved, so it is fine. The qualifier about specific structural problems is omitted but not needed."
    },
    "grounding": 5,
    "numerical_fidelity": 5,
    "overall": 14,
    "precision": 4,
    "reason": "Matches Art 47(1) directly. The declared articles_involved of 47 is correct, since no reference supplies answer content. The answer includes the strategy/implementation clause, which is part of the list of things improved, so it is fine. The qualifier about specific structural problems is omitted but not needed."
  },
  {
    "_response": {
      "grounding": 5,
      "index": 1,
      "numerical_fidelity": 5,
      "precision": 5,
      "reason": "Art 47(2) states 'before, during and after the programming period'. The span is exact and concise. Articles_involved of 47 is correct."
    },
    "grounding": 5,
    "numerical_fidelity": 5,
    "overall": 15,
    "precision": 5,
    "reason": "Art 47(2) states 'before, during and after the programming period'. The span is exact and concise. Articles_involved of 47 is correct."
  },
  {
    "_response": {
      "grounding": 5,
      "index": 2,
      "numerical_fidelity": 5,
      "precision": 5,
      "reason": "Art 47(4) states 'the budget for technical assistance'. The span is exact and minimal. Articles_involved of 47 is correct."
    },
    "grounding": 5,
    "numerical_fidelity": 5,
    "overall": 15,
    "precision": 5,
    "reason": "Art 47(4) states 'the budget for technical assistance'. The span is exact and minimal. Articles_involved of 47 is correct."
  }
]
````

### mode/eurlex/http://data.europa.eu/eli/reg/2006/1083/art_47/oj/lookup: quality_index_recovery — completed

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
      "candidate_id": "q_5848d7ca2efad6ad929990d7",
      "checks": {
        "metadata": "pass",
        "mode": "pass",
        "support": "pass"
      },
      "index": 0,
      "problems": [
        "practitioner_realism: near-copy of the article's wording; reads as a comprehension slot.",
        "anchoring: the base does not identify the regime (structural/cohesion funds programming); 'the Funds' is unresolved."
      ],
      "score_notes": {
        "anchoring": "'The Funds' and 'evaluations' point to the cohesion/structural funds domain, but the base names no regime, programming context or actor. It could be confused with other fund evaluation rules, so a material distinction is missing.",
        "focus": "One bounded need, namely the aims of evaluations. The list answer is a single set.",
        "informativeness": "Article 47(1) resolves the ask directly: the quality, effectiveness and consistency of the assistance and of the strategy and implementation of operational programmes. The answer is a list and is fully supported, though the question mostly echoes the text.",
        "linguistic_quality": "Grammatical and clear. The phrase 'In relation to assistance from the Funds' is slightly awkward and redundant.",
        "practitioner_realism": "The ask is a direct point-of-law request, but it reads like a reading-comprehension slot that mirrors the article's first sentence. The scaffolding 'In relation to assistance from the Funds' is lifted from the text."
      },
      "scores": {
        "anchoring": 3,
        "focus": 5,
        "informativeness": 4,
        "linguistic_quality": 4,
        "practitioner_realism": 3
      }
    },
    "anchoring": 3,
    "focus": 5,
    "informativeness": 4,
    "linguistic_quality": 4,
    "overall": 19,
    "practitioner_realism": 3,
    "reason": "practitioner_realism: The ask is a direct point-of-law request, but it reads like a reading-comprehension slot that mirrors the article's first sentence. The scaffolding 'In relation to assistance from the Funds' is lifted from the text.; anchoring: 'The Funds' and 'evaluations' point to the cohesion/structural funds domain, but the base names no regime, programming context or actor. It could be confused with other fund evaluation rules, so a material distinction is missing.; informativeness: Article 47(1) resolves the ask directly: the quality, effectiveness and consistency of the assistance and of the strategy and implementation of operational programmes. The answer is a list and is fully supported, though the question mostly echoes the text.; focus: One bounded need, namely the aims of evaluations. The list answer is a single set.; linguistic_quality: Grammatical and clear. The phrase 'In relation to assistance from the Funds' is slightly awkward and redundant."
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
      "candidate_id": "q_2ec8c00424b7d72e7c555417",
      "checks": {
        "metadata": "pass",
        "mode": "pass",
        "support": "pass"
      },
      "index": 1,
      "problems": [
        "anchoring: generic base with no identification of the programme evaluation context or regime.",
        "practitioner_realism: the borrowed scaffolding phrase is unnatural."
      ],
      "score_notes": {
        "anchoring": "'Assistance from the Funds' is generic and does not say whether the question concerns programme evaluation, which programming period, or which regime. 'Evaluations' could refer to many EU funds, so the anchor is generic.",
        "focus": "A single timing question with a single answer.",
        "informativeness": "Article 47(2) states that evaluations are carried out before, during and after the programming period. This resolves the ask fully. 'Programming period' is itself only loosely defined.",
        "linguistic_quality": "Understandable and grammatical. The opening clause is slightly clumsy, and 'shall' in a question is stilted.",
        "practitioner_realism": "The timing of evaluations is a natural practitioner question, but the phrasing 'In relation to assistance from the Funds' is scaffolding that does not fit the ask."
      },
      "scores": {
        "anchoring": 2,
        "focus": 5,
        "informativeness": 4,
        "linguistic_quality": 4,
        "practitioner_realism": 3
      }
    },
    "anchoring": 2,
    "focus": 5,
    "informativeness": 4,
    "linguistic_quality": 4,
    "overall": 18,
    "practitioner_realism": 3,
    "reason": "practitioner_realism: The timing of evaluations is a natural practitioner question, but the phrasing 'In relation to assistance from the Funds' is scaffolding that does not fit the ask.; anchoring: 'Assistance from the Funds' is generic and does not say whether the question concerns programme evaluation, which programming period, or which regime. 'Evaluations' could refer to many EU funds, so the anchor is generic.; informativeness: Article 47(2) states that evaluations are carried out before, during and after the programming period. This resolves the ask fully. 'Programming period' is itself only loosely defined.; focus: A single timing question with a single answer.; linguistic_quality: Understandable and grammatical. The opening clause is slightly clumsy, and 'shall' in a question is stilted."
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
      "candidate_id": "q_6baa4b6945ded92974a58481",
      "checks": {
        "metadata": "fail",
        "mode": "pass",
        "support": "pass"
      },
      "index": 2,
      "problems": [
        "anchoring: the regime is not identified in the base.",
        "metadata: question_type 'obligation_or_prohibition' is weak for a funding-source question, though the overlap is acceptable."
      ],
      "score_notes": {
        "anchoring": "'Evaluations' and 'the Funds' partly identify the domain, but the base does not name the regime or programme context. The budget for technical assistance could be confused with other funding rules.",
        "focus": "One bounded question with one answer.",
        "informativeness": "Article 47(4) gives the answer directly: the technical assistance budget. It fully resolves the ask.",
        "linguistic_quality": "Clear and grammatical, with slightly awkward framing and 'shall'.",
        "practitioner_realism": "The funding source of evaluations is a realistic practitioner question, but the stilted 'In relation to assistance from the Funds' phrasing is borrowed scaffolding."
      },
      "scores": {
        "anchoring": 3,
        "focus": 5,
        "informativeness": 4,
        "linguistic_quality": 4,
        "practitioner_realism": 3
      }
    },
    "anchoring": 3,
    "focus": 5,
    "informativeness": 4,
    "linguistic_quality": 4,
    "overall": 19,
    "practitioner_realism": 3,
    "reason": "practitioner_realism: The funding source of evaluations is a realistic practitioner question, but the stilted 'In relation to assistance from the Funds' phrasing is borrowed scaffolding.; anchoring: 'Evaluations' and 'the Funds' partly identify the domain, but the base does not name the regime or programme context. The budget for technical assistance could be confused with other funding rules.; informativeness: Article 47(4) gives the answer directly: the technical assistance budget. It fully resolves the ask.; focus: One bounded question with one answer.; linguistic_quality: Clear and grammatical, with slightly awkward framing and 'shall'."
  }
]
````

### mode/eurlex/http://data.europa.eu/eli/reg/2011/492/art_17/oj/fact_pattern: faithfulness — completed

````json
[
  {
    "_response": {
      "grounding": 5,
      "index": 0,
      "numerical_fidelity": 5,
      "precision": 5,
      "reason": "The answer quotes Article 17(2) verbatim, which directly resolves the question about what Member States must do regarding priority. The declared articles_involved (17) is correct, since no references are supplied. Both sentences are needed: the examination duty and the duty to adopt necessary measures. There is no extraneous content. The answer has no numbers to distort, and the only identifier, the article number, is correct."
    },
    "grounding": 5,
    "numerical_fidelity": 5,
    "overall": 15,
    "precision": 5,
    "reason": "The answer quotes Article 17(2) verbatim, which directly resolves the question about what Member States must do regarding priority. The declared articles_involved (17) is correct, since no references are supplied. Both sentences are needed: the examination duty and the duty to adopt necessary measures. There is no extraneous content. The answer has no numbers to distort, and the only identifier, the article number, is correct."
  }
]
````

### mode/eurlex/http://data.europa.eu/eli/reg/2011/492/art_17/oj/fact_pattern: quality_index_recovery — completed

````json
[
  {
    "_batch_diversity": "not_applicable",
    "_contract": "compact",
    "_keys": [
      "situation",
      "regime_fixing",
      "terminology_and_distance",
      "focus",
      "linguistic_quality"
    ],
    "_response": {
      "candidate_id": "q_b00153045725dfc9697df83c",
      "checks": {
        "metadata": "pass",
        "mode": "pass",
        "support": "pass"
      },
      "index": 0,
      "problems": [
        "situation: The second particular merely restates the legal aim and does not add a distinct scoping fact.",
        "regime_fixing: The regime is identified only through generic 'Union employment vacancies' wording, without worker freedom of movement or labour market balance context.",
        "terminology_and_distance: The question leaks the purpose and the notion of priority from the answer, which reduces the unknown legal relationship."
      ],
      "score_notes": {
        "focus": "It asks one bounded thing: what Member States must do regarding priority. The answer covers the examination duty and the duty to adopt measures, which are closely linked qualifications, not separate asks.",
        "linguistic_quality": "The prose is clear and grammatical. The first sentence is slightly clumsy ('handling Union employment vacancies and applications with the aim of balancing...'), but it is natural enough.",
        "regime_fixing": "Union employment vacancies and applications point to the EU worker mobility and vacancy clearance regime. The question does not mention workers, freedom of movement or the labour market balance controls. This leaves the regime somewhat generic, and it could be confused with other employment or vacancy rules.",
        "situation": "The protagonist is a national employment authority, which is allowed. The only facts are that it handles vacancies and that the aim is balance. The second fact restates the rule's purpose rather than adding an independent scope particular. The scenario is thin, and the abstract rule is barely dressed as a case.",
        "terminology_and_distance": "The question copies the rule's purpose, balancing vacancies and applications within the Union. It also says 'priority', which is the core of the required action. This nearly gives away the content of the answer, namely examining priority to nationals in order to achieve a balance. Only the nationality-based priority and the Commission examination remain hidden."
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
    "reason": "situation: The protagonist is a national employment authority, which is allowed. The only facts are that it handles vacancies and that the aim is balance. The second fact restates the rule's purpose rather than adding an independent scope particular. The scenario is thin, and the abstract rule is barely dressed as a case.; regime_fixing: Union employment vacancies and applications point to the EU worker mobility and vacancy clearance regime. The question does not mention workers, freedom of movement or the labour market balance controls. This leaves the regime somewhat generic, and it could be confused with other employment or vacancy rules.; terminology_and_distance: The question copies the rule's purpose, balancing vacancies and applications within the Union. It also says 'priority', which is the core of the required action. This nearly gives away the content of the answer, namely examining priority to nationals in order to achieve a balance. Only the nationality-based priority and the Commission examination remain hidden.; focus: It asks one bounded thing: what Member States must do regarding priority. The answer covers the examination duty and the duty to adopt measures, which are closely linked qualifications, not separate asks.; linguistic_quality: The prose is clear and grammatical. The first sentence is slightly clumsy ('handling Union employment vacancies and applications with the aim of balancing...'), but it is natural enough.",
    "regime_fixing": 3,
    "situation": 3,
    "terminology_and_distance": 2
  }
]
````

### mode/eurlex/http://data.europa.eu/eli/reg_impl/2012/282/art_1/oj/lookup: faithfulness — completed

````json
[
  {
    "_response": {
      "grounding": 4,
      "index": 0,
      "numerical_fidelity": 5,
      "precision": 4,
      "reason": "The answer quotes the opening clause of Article 1, which states what the Regulation governs: securities to be provided under the listed regulations. The clause ends with a colon and does not list the regulations, so it is somewhat incomplete as an answer to 'subject matter'. The articles_involved list is correct. The clause is on point, with only minor trailing material."
    },
    "grounding": 4,
    "numerical_fidelity": 5,
    "overall": 13,
    "precision": 4,
    "reason": "The answer quotes the opening clause of Article 1, which states what the Regulation governs: securities to be provided under the listed regulations. The clause ends with a colon and does not list the regulations, so it is somewhat incomplete as an answer to 'subject matter'. The articles_involved list is correct. The clause is on point, with only minor trailing material."
  },
  {
    "_response": {
      "grounding": 5,
      "index": 1,
      "numerical_fidelity": 5,
      "precision": 4,
      "reason": "The answer lists the regulations in points (a)–(c) with correct numbers: 104/2000, 1234/2007, 73/2009 and 1216/2009. It answers the question directly, and the articles_involved list is correct. The fragment begins with the leftover '(b)' and '(c)' labels and the parentheticals, which is minor formatting noise only."
    },
    "grounding": 5,
    "numerical_fidelity": 5,
    "overall": 14,
    "precision": 4,
    "reason": "The answer lists the regulations in points (a)–(c) with correct numbers: 104/2000, 1234/2007, 73/2009 and 1216/2009. It answers the question directly, and the articles_involved list is correct. The fragment begins with the leftover '(b)' and '(c)' labels and the parentheticals, which is minor formatting noise only."
  },
  {
    "_response": {
      "grounding": 5,
      "index": 2,
      "numerical_fidelity": 5,
      "precision": 5,
      "reason": "The span 'unless other rules are laid down by those regulations' is exactly the qualification asked about. It is concise and sufficient, and the articles_involved list is correct."
    },
    "grounding": 5,
    "numerical_fidelity": 5,
    "overall": 15,
    "precision": 5,
    "reason": "The span 'unless other rules are laid down by those regulations' is exactly the qualification asked about. It is concise and sufficient, and the articles_involved list is correct."
  }
]
````

### mode/eurlex/http://data.europa.eu/eli/reg_impl/2012/282/art_1/oj/lookup: quality_index_recovery — completed

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
      "candidate_id": "q_7a97e1b5813a05146fa95b9c",
      "checks": {
        "metadata": "pass",
        "mode": "pass",
        "support": "pass"
      },
      "index": 0,
      "problems": [
        "practitioner_realism: near-copy, circular ask of the article's own opening sentence.",
        "informativeness: answer largely restates the question and leaves the actual regulations unnamed.",
        "linguistic_quality: redundant phrasing ('rules for securities ... securities regime')."
      ],
      "score_notes": {
        "anchoring": "'Securities for agricultural products' identifies the regime. 'EU agricultural-product securities regime' is circular, and the base does not say which underlying regulations are meant, so a distinction is missing.",
        "focus": "The question is a single ask, though vague about what 'subject matter' means.",
        "informativeness": "The answer mostly restates the question: the rules govern securities under the listed regulations. The only new content is the pointer to 'the following regulations', which is unresolved without the list. The answer is also a dangling sentence ending in a colon.",
        "linguistic_quality": "'Subject matter is governed by the rules for securities ... under the ... securities regime' is redundant and circular.",
        "practitioner_realism": "The question asks what the securities rules govern, and the answer repeats the question's own terms. It reads like a bare reading-comprehension slot rather than a real practitioner query."
      },
      "scores": {
        "anchoring": 3,
        "focus": 4,
        "informativeness": 2,
        "linguistic_quality": 3,
        "practitioner_realism": 2
      }
    },
    "anchoring": 3,
    "focus": 4,
    "informativeness": 2,
    "linguistic_quality": 3,
    "overall": 14,
    "practitioner_realism": 2,
    "reason": "practitioner_realism: The question asks what the securities rules govern, and the answer repeats the question's own terms. It reads like a bare reading-comprehension slot rather than a real practitioner query.; anchoring: 'Securities for agricultural products' identifies the regime. 'EU agricultural-product securities regime' is circular, and the base does not say which underlying regulations are meant, so a distinction is missing.; informativeness: The answer mostly restates the question: the rules govern securities under the listed regulations. The only new content is the pointer to 'the following regulations', which is unresolved without the list. The answer is also a dangling sentence ending in a colon.; focus: The question is a single ask, though vague about what 'subject matter' means.; linguistic_quality: 'Subject matter is governed by the rules for securities ... under the ... securities regime' is redundant and circular."
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
      "candidate_id": "q_4139993fbff6a27f3f9ef7d4",
      "checks": {
        "metadata": "pass",
        "mode": "pass",
        "support": "pass"
      },
      "index": 1,
      "problems": [],
      "score_notes": {
        "anchoring": "'Securities for agricultural products' identifies the regime well. It does not name the actor or activity, and 'underlying EU measures' is slightly vague, but it is sufficient.",
        "focus": "The question asks one bounded thing, the list of covered measures.",
        "informativeness": "The answer gives the list of regulations: the fishery and aquaculture CMO, the Single CMO, direct support, and processed goods trade arrangements. This is exactly the unknown.",
        "linguistic_quality": "The prose is clear, but 'underlying EU measures' is a bit imprecise.",
        "practitioner_realism": "This is a natural scope question a practitioner would ask about which underlying measures the securities rules cover."
      },
      "scores": {
        "anchoring": 4,
        "focus": 5,
        "informativeness": 5,
        "linguistic_quality": 4,
        "practitioner_realism": 4
      }
    },
    "anchoring": 4,
    "focus": 5,
    "informativeness": 5,
    "linguistic_quality": 4,
    "overall": 22,
    "practitioner_realism": 4,
    "reason": "practitioner_realism: This is a natural scope question a practitioner would ask about which underlying measures the securities rules cover.; anchoring: 'Securities for agricultural products' identifies the regime well. It does not name the actor or activity, and 'underlying EU measures' is slightly vague, but it is sufficient.; informativeness: The answer gives the list of regulations: the fishery and aquaculture CMO, the Single CMO, direct support, and processed goods trade arrangements. This is exactly the unknown.; focus: The question asks one bounded thing, the list of covered measures.; linguistic_quality: The prose is clear, but 'underlying EU measures' is a bit imprecise."
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
      "candidate_id": "q_4aaaec5798a4f2f33cc4246e",
      "checks": {
        "metadata": "pass",
        "mode": "pass",
        "support": "pass"
      },
      "index": 2,
      "problems": [
        "informativeness: the answer largely restates the premise of the question.",
        "anchoring: 'underlying regulations' is unresolved in the base.",
        "linguistic_quality: stilted and circular phrasing."
      ],
      "score_notes": {
        "anchoring": "'Underlying regulations' is unresolved in the base, so it is unclear which regulations are meant. The regime is otherwise identified by 'securities for agricultural products'.",
        "focus": "The question asks a single thing, the carve-out.",
        "informativeness": "The answer 'unless other rules are laid down by those regulations' mostly restates the question's premise. It adds only the point that those regulations' own rules take precedence, and that is stated tersely.",
        "linguistic_quality": "'What qualification applies ... where the underlying regulations lay down other rules' is stilted and partly circular.",
        "practitioner_realism": "The question is somewhat natural, but 'what qualification applies' is awkwardly abstract and reads like a slot-fill of the clause."
      },
      "scores": {
        "anchoring": 3,
        "focus": 4,
        "informativeness": 3,
        "linguistic_quality": 3,
        "practitioner_realism": 3
      }
    },
    "anchoring": 3,
    "focus": 4,
    "informativeness": 3,
    "linguistic_quality": 3,
    "overall": 16,
    "practitioner_realism": 3,
    "reason": "practitioner_realism: The question is somewhat natural, but 'what qualification applies' is awkwardly abstract and reads like a slot-fill of the clause.; anchoring: 'Underlying regulations' is unresolved in the base, so it is unclear which regulations are meant. The regime is otherwise identified by 'securities for agricultural products'.; informativeness: The answer 'unless other rules are laid down by those regulations' mostly restates the question's premise. It adds only the point that those regulations' own rules take precedence, and that is stated tersely.; focus: The question asks a single thing, the carve-out.; linguistic_quality: 'What qualification applies ... where the underlying regulations lay down other rules' is stilted and partly circular."
  }
]
````

### mode/un/2000/cd/pv_841#11/lookup: faithfulness_json_recovery — completed

````json
[
  {
    "_response": {
      "grounding": 5,
      "index": 0,
      "numerical_fidelity": 5,
      "precision": 4,
      "reason": "The answer is taken directly from the UK statement. It describes the option to appoint special coordinators while agreeing a work programme that includes an FMCT ad hoc committee. The phrasing 'would have permitted' keeps its status as a proposed option, not an adopted one. The opening 'One of which' leaves the set of options unexplained, which is a minor completeness and clarity issue."
    },
    "grounding": 5,
    "numerical_fidelity": 5,
    "overall": 14,
    "precision": 4,
    "reason": "The answer is taken directly from the UK statement. It describes the option to appoint special coordinators while agreeing a work programme that includes an FMCT ad hoc committee. The phrasing 'would have permitted' keeps its status as a proposed option, not an adopted one. The opening 'One of which' leaves the set of options unexplained, which is a minor completeness and clarity issue."
  },
  {
    "_response": {
      "grounding": 5,
      "index": 1,
      "numerical_fidelity": 5,
      "precision": 5,
      "reason": "The answer matches the statement exactly and keeps the attribution ('In our view'). It gives the precondition that there be confidence that no new fissile material can be produced. It is complete and has no extra material."
    },
    "grounding": 5,
    "numerical_fidelity": 5,
    "overall": 15,
    "precision": 5,
    "reason": "The answer matches the statement exactly and keeps the attribution ('In our view'). It gives the precondition that there be confidence that no new fissile material can be produced. It is complete and has no extra material."
  },
  {
    "_response": {
      "grounding": 5,
      "index": 2,
      "numerical_fidelity": 5,
      "precision": 3,
      "reason": "The sentence is accurate to the source. However, the question asks what the assurance is, and the answer only says 'such an assurance'. It never states the content, that no new fissile material for nuclear weapons can be produced. That content is in the previous sentence, so the answer is not self-contained and omits the key substance."
    },
    "grounding": 5,
    "numerical_fidelity": 5,
    "overall": 13,
    "precision": 3,
    "reason": "The sentence is accurate to the source. However, the question asks what the assurance is, and the answer only says 'such an assurance'. It never states the content, that no new fissile material for nuclear weapons can be produced. That content is in the previous sentence, so the answer is not self-contained and omits the key substance."
  }
]
````

### mode/un/2000/cd/pv_841#11/lookup: quality — completed

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
      "candidate_id": "q_7570c73764eb09443f81a460",
      "checks": {
        "metadata": "fail",
        "mode": "pass",
        "support": "pass"
      },
      "index": 0,
      "problems": [
        "anchoring: no distinguishing subject; \"what option\" is ambiguous among the options mentioned.",
        "informativeness: the answer starts with the relative fragment \"One of which\" and depends on prior text for its referent.",
        "linguistic_quality: the question wording is vague and does not convey the conditional or unadopted nature of the option.",
        "metadata: the anchor \"what option was to be considered\" is only the question clause, not a substantive base substring giving subject context."
      ],
      "score_notes": {
        "anchoring": "The date and the UK statement are correct. There is no distinguishing subject (FMCT, work programme, special coordinators), so \"what option\" could point to several options or be read as the President's proposal.",
        "consequence": "The answer says what procedural route was contemplated, which is moderately useful. It was never adopted, and the question does not signal that.",
        "informativeness": "The answer substance is present: special coordinators plus a work programme with an ad hoc committee on an FMCT. It begins \"One of which\", which depends on the unstated \"a number of options\", and the \"would have permitted\" modality is not reflected in the question.",
        "linguistic_quality": "The question is grammatical but vague. The answer is a fragment opening with \"One of which\", so it is not a natural standalone answer.",
        "practitioner_realism": "Asking about the options the President was to bring forward is plausible, but \"what option was to be considered\" is a loose, unfocused need."
      },
      "scores": {
        "anchoring": 3,
        "consequence": 3,
        "informativeness": 3,
        "linguistic_quality": 3,
        "practitioner_realism": 3
      }
    },
    "anchoring": 3,
    "consequence": 3,
    "informativeness": 3,
    "linguistic_quality": 3,
    "overall": 15,
    "practitioner_realism": 3,
    "reason": "practitioner_realism: Asking about the options the President was to bring forward is plausible, but \"what option was to be considered\" is a loose, unfocused need.; anchoring: The date and the UK statement are correct. There is no distinguishing subject (FMCT, work programme, special coordinators), so \"what option\" could point to several options or be read as the President's proposal.; consequence: The answer says what procedural route was contemplated, which is moderately useful. It was never adopted, and the question does not signal that.; informativeness: The answer substance is present: special coordinators plus a work programme with an ad hoc committee on an FMCT. It begins \"One of which\", which depends on the unstated \"a number of options\", and the \"would have permitted\" modality is not reflected in the question.; linguistic_quality: The question is grammatical but vague. The answer is a fragment opening with \"One of which\", so it is not a natural standalone answer."
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
      "candidate_id": "q_c73b641385bc5e54244399c7",
      "checks": {
        "metadata": "pass",
        "mode": "pass",
        "support": "pass"
      },
      "index": 1,
      "problems": [],
      "score_notes": {
        "anchoring": "The date, organ and UK speaker are given, and the subject (effective, verifiable global nuclear-weapons ban) is distinctive enough to find the passage.",
        "consequence": "It gives a specific substantive position (confidence that no new fissile material can be produced) that a practitioner could use.",
        "informativeness": "The answer is a complete, non-circular contiguous span. It keeps the \"In our view\" attribution and the full condition.",
        "linguistic_quality": "The question is clear and natural, with only slight compression in \"nuclear-weapons ban\".",
        "practitioner_realism": "A plausible need: the UK's stated precondition for a verifiable nuclear-weapons ban."
      },
      "scores": {
        "anchoring": 4,
        "consequence": 4,
        "informativeness": 5,
        "linguistic_quality": 4,
        "practitioner_realism": 4
      }
    },
    "anchoring": 4,
    "consequence": 4,
    "informativeness": 5,
    "linguistic_quality": 4,
    "overall": 21,
    "practitioner_realism": 4,
    "reason": "practitioner_realism: A plausible need: the UK's stated precondition for a verifiable nuclear-weapons ban.; anchoring: The date, organ and UK speaker are given, and the subject (effective, verifiable global nuclear-weapons ban) is distinctive enough to find the passage.; consequence: It gives a specific substantive position (confidence that no new fissile material can be produced) that a practitioner could use.; informativeness: The answer is a complete, non-circular contiguous span. It keeps the \"In our view\" attribution and the full condition.; linguistic_quality: The question is clear and natural, with only slight compression in \"nuclear-weapons ban\"."
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
      "candidate_id": "q_a55ee2e0c499e2d13b245892",
      "checks": {
        "metadata": "fail",
        "mode": "pass",
        "support": "fail"
      },
      "index": 2,
      "problems": [
        "informativeness: the answer is circular; it refers to \"such an assurance\" and never states what the assurance is.",
        "support: the target span is incomplete for the question, since the needed content is in the preceding sentence.",
        "metadata: the question_type operative_action fits poorly, because this is a stated assessment of what an FMCT would achieve, not an operative action."
      ],
      "score_notes": {
        "anchoring": "The date, UK speaker and FMCT subject are adequate to locate the passage.",
        "consequence": "The answer is of moderate use: it gives the foundational role of an FMCT, but not the assurance itself.",
        "informativeness": "The answer says \"such an assurance\" without stating it. The content (no new fissile material can be produced) is in the preceding sentence, outside the answer span, so the question is not fully resolved.",
        "linguistic_quality": "The question is fine, but the answer's anaphoric \"such an assurance\" makes it unclear standing alone.",
        "practitioner_realism": "Asking what assurance an FMCT provides is plausible, but it is tied to the prior sentence and reads as a fragment of the argument."
      },
      "scores": {
        "anchoring": 4,
        "consequence": 3,
        "informativeness": 2,
        "linguistic_quality": 3,
        "practitioner_realism": 3
      }
    },
    "anchoring": 4,
    "consequence": 3,
    "informativeness": 2,
    "linguistic_quality": 3,
    "overall": 15,
    "practitioner_realism": 3,
    "reason": "practitioner_realism: Asking what assurance an FMCT provides is plausible, but it is tied to the prior sentence and reads as a fragment of the argument.; anchoring: The date, UK speaker and FMCT subject are adequate to locate the passage.; consequence: The answer is of moderate use: it gives the foundational role of an FMCT, but not the assurance itself.; informativeness: The answer says \"such an assurance\" without stating it. The content (no new fissile material can be produced) is in the preceding sentence, outside the answer span, so the question is not fully resolved.; linguistic_quality: The question is fine, but the answer's anaphoric \"such an assurance\" makes it unclear standing alone."
  }
]
````

### mode/un/2001/cd/pv_880#1/lookup: faithfulness — completed

````json
[
  {
    "_response": {
      "grounding": 5,
      "index": 0,
      "numerical_fidelity": 5,
      "precision": 5,
      "reason": "The answer quotes the President's request verbatim. It covers both parts of the request: considering replies to the questionnaires, and participating actively in the consultations. The question's premises (880th plenary meeting, 2001, the President's statement) match the text and context."
    },
    "grounding": 5,
    "numerical_fidelity": 5,
    "overall": 15,
    "precision": 5,
    "reason": "The answer quotes the President's request verbatim. It covers both parts of the request: considering replies to the questionnaires, and participating actively in the consultations. The question's premises (880th plenary meeting, 2001, the President's statement) match the text and context."
  },
  {
    "_response": {
      "grounding": 5,
      "index": 1,
      "numerical_fidelity": 5,
      "precision": 5,
      "reason": "The answer is a verbatim sentence giving the unanimous interest in maintaining the CD, its credibility, and its status as the sole multilateral disarmament negotiating forum. It is the President's report of delegations' views, and the question frames it that way. The opening 'Nonetheless' is only a connective and does no harm."
    },
    "grounding": 5,
    "numerical_fidelity": 5,
    "overall": 15,
    "precision": 5,
    "reason": "The answer is a verbatim sentence giving the unanimous interest in maintaining the CD, its credibility, and its status as the sole multilateral disarmament negotiating forum. It is the President's report of delegations' views, and the question frames it that way. The opening 'Nonetheless' is only a connective and does no harm."
  },
  {
    "_response": {
      "grounding": 5,
      "index": 2,
      "numerical_fidelity": 5,
      "precision": 5,
      "reason": "The answer is the verbatim sentence reporting that most delegations think progress on substantive issues will be very difficult in the final weeks. The attribution to 'the great majority of delegations' is kept, so it is not presented as established fact. It fully answers the question."
    },
    "grounding": 5,
    "numerical_fidelity": 5,
    "overall": 15,
    "precision": 5,
    "reason": "The answer is the verbatim sentence reporting that most delegations think progress on substantive issues will be very difficult in the final weeks. The attribution to 'the great majority of delegations' is kept, so it is not presented as established fact. It fully answers the question."
  }
]
````

### mode/un/2001/cd/pv_880#1/lookup: quality_index_recovery — completed

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
      "candidate_id": "q_596fa0a4e6170290067dfbd3",
      "checks": {
        "metadata": "pass",
        "mode": "pass",
        "support": "pass"
      },
      "index": 0,
      "problems": [],
      "score_notes": {
        "anchoring": "The organ, the 880th plenary meeting, the year 2001, the President as speaker and the subject (special coordinators' questionnaires and consultations) are all accurate and identify the passage.",
        "consequence": "A specific, useful procedural request, but of modest substantive weight.",
        "informativeness": "The contiguous target span fully answers the question: reply to the questionnaires and participate actively in the consultations, with the purpose stated.",
        "linguistic_quality": "The question is clear and natural. The answer span carries a small lead-in ('I will take this opportunity to ask'), which is an extraction artifact.",
        "practitioner_realism": "Plausible bounded need: what the President asked delegations to do about the questionnaires and consultations."
      },
      "scores": {
        "anchoring": 4,
        "consequence": 3,
        "informativeness": 5,
        "linguistic_quality": 4,
        "practitioner_realism": 4
      }
    },
    "anchoring": 4,
    "consequence": 3,
    "informativeness": 5,
    "linguistic_quality": 4,
    "overall": 20,
    "practitioner_realism": 4,
    "reason": "practitioner_realism: Plausible bounded need: what the President asked delegations to do about the questionnaires and consultations.; anchoring: The organ, the 880th plenary meeting, the year 2001, the President as speaker and the subject (special coordinators' questionnaires and consultations) are all accurate and identify the passage.; consequence: A specific, useful procedural request, but of modest substantive weight.; informativeness: The contiguous target span fully answers the question: reply to the questionnaires and participate actively in the consultations, with the purpose stated.; linguistic_quality: The question is clear and natural. The answer span carries a small lead-in ('I will take this opportunity to ask'), which is an extraction artifact."
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
      "candidate_id": "q_41e4b92b884b031671f3ab73",
      "checks": {
        "metadata": "fail",
        "mode": "pass",
        "support": "pass"
      },
      "index": 1,
      "problems": [
        "metadata: the anchor 'maintaining the Conference on Disarmament' does not appear in the question text. It lies inside the answer span, so it cannot survive substitution as an independent outside anchor.",
        "metadata: the type situation_scope_or_coverage fits poorly; finding_event_or_assessment would be more compatible.",
        "anchoring: the subject is too vague to pin the passage down independently."
      ],
      "score_notes": {
        "anchoring": "The meeting and year are correct, but the subject is vague ('unanimous interest'). The question does not name the topic, and several statements in the opening could fit.",
        "consequence": "The answer is a general expression of support for the CD's credibility and role, with little specific operative or factual value.",
        "informativeness": "The span answers the question and is non-circular. It opens with the connective 'Nonetheless', which is a small extraction artifact.",
        "linguistic_quality": "The wording is clear and natural.",
        "practitioner_realism": "A plausible but loose need; 'unanimous interest' reads as a generic prompt rather than a bounded fact."
      },
      "scores": {
        "anchoring": 3,
        "consequence": 2,
        "informativeness": 4,
        "linguistic_quality": 4,
        "practitioner_realism": 3
      }
    },
    "anchoring": 3,
    "consequence": 2,
    "informativeness": 4,
    "linguistic_quality": 4,
    "overall": 16,
    "practitioner_realism": 3,
    "reason": "practitioner_realism: A plausible but loose need; 'unanimous interest' reads as a generic prompt rather than a bounded fact.; anchoring: The meeting and year are correct, but the subject is vague ('unanimous interest'). The question does not name the topic, and several statements in the opening could fit.; consequence: The answer is a general expression of support for the CD's credibility and role, with little specific operative or factual value.; informativeness: The span answers the question and is non-circular. It opens with the connective 'Nonetheless', which is a small extraction artifact.; linguistic_quality: The wording is clear and natural."
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
      "candidate_id": "q_c736d1955b18405d6c28756f",
      "checks": {
        "metadata": "fail",
        "mode": "pass",
        "support": "pass"
      },
      "index": 2,
      "problems": [
        "metadata: the anchor 'make headway on substantive issues' does not appear in the question text. The question says 'substantive progress', and the anchor phrase is in the answer span."
      ],
      "score_notes": {
        "anchoring": "The President, the Conference's final weeks, and 2001 are accurate and sufficient to locate the statement. The meeting number is missing from the base question.",
        "consequence": "A moderately useful assessment of prospects for substantive progress.",
        "informativeness": "The span fully answers the question and keeps the attribution to 'the great majority of delegations'. The 'difficulty' is a reported assessment, not a fact.",
        "linguistic_quality": "The wording is clear and natural.",
        "practitioner_realism": "A plausible need, although 'what difficulty' is generic."
      },
      "scores": {
        "anchoring": 4,
        "consequence": 3,
        "informativeness": 4,
        "linguistic_quality": 4,
        "practitioner_realism": 3
      }
    },
    "anchoring": 4,
    "consequence": 3,
    "informativeness": 4,
    "linguistic_quality": 4,
    "overall": 18,
    "practitioner_realism": 3,
    "reason": "practitioner_realism: A plausible need, although 'what difficulty' is generic.; anchoring: The President, the Conference's final weeks, and 2001 are accurate and sufficient to locate the statement. The meeting number is missing from the base question.; consequence: A moderately useful assessment of prospects for substantive progress.; informativeness: The span fully answers the question and keeps the attribution to 'the great majority of delegations'. The 'difficulty' is a reported assessment, not a fact.; linguistic_quality: The wording is clear and natural."
  }
]
````

### mode/un/2001/s/res/1376_2001_#2/lookup: faithfulness — completed

````json
[
  {
    "_response": {
      "grounding": 5,
      "index": 0,
      "numerical_fidelity": 5,
      "precision": 5,
      "reason": "Paragraph 8 is quoted verbatim. The answer states the demand that exploitation cease, together with the condemnation and the statement that the resources should not finance the conflict. The date matches the context (9 November 2001). The extra condemnation clause is relevant context."
    },
    "grounding": 5,
    "numerical_fidelity": 5,
    "overall": 15,
    "precision": 5,
    "reason": "Paragraph 8 is quoted verbatim. The answer states the demand that exploitation cease, together with the condemnation and the statement that the resources should not finance the conflict. The date matches the context (9 November 2001). The extra condemnation clause is relevant context."
  },
  {
    "_response": {
      "grounding": 5,
      "index": 1,
      "numerical_fidelity": 5,
      "precision": 5,
      "reason": "Paragraph 4 is quoted verbatim. It covers both the support (for the dialogue, the efforts to promote it, and the Facilitator) and the call on the Congolese parties to work together. Nothing is overstated, and the date is correct."
    },
    "grounding": 5,
    "numerical_fidelity": 5,
    "overall": 15,
    "precision": 5,
    "reason": "Paragraph 4 is quoted verbatim. It covers both the support (for the dialogue, the efforts to promote it, and the Facilitator) and the call on the Congolese parties to work together. Nothing is overstated, and the date is correct."
  },
  {
    "_response": {
      "grounding": 5,
      "index": 2,
      "numerical_fidelity": 5,
      "precision": 4,
      "reason": "Paragraph 7 is quoted verbatim. It supports both the interdependence characterization and the underlined need for increased international economic assistance. The opening clause about serious concern is slightly extra to the question, which is a minor issue. The date is correct."
    },
    "grounding": 5,
    "numerical_fidelity": 5,
    "overall": 14,
    "precision": 4,
    "reason": "Paragraph 7 is quoted verbatim. It supports both the interdependence characterization and the underlined need for increased international economic assistance. The opening clause about serious concern is slightly extra to the question, which is a minor issue. The date is correct."
  }
]
````

### mode/un/2001/s/res/1376_2001_#2/lookup: quality_index_recovery — completed

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
      "candidate_id": "q_24261496f41feae9007ab787",
      "checks": {
        "metadata": "pass",
        "mode": "pass",
        "support": "pass"
      },
      "index": 0,
      "problems": [],
      "score_notes": {
        "anchoring": "Organ, type, date and subject are present and accurate. The resolution number is not given, but the date plus subject is nearly unique.",
        "consequence": "Gives a specific operative demand and the condition that resources not finance the conflict.",
        "informativeness": "The answer contains the demand to cease, the condemnation and the no-conflict-financing clause, so it fully resolves the question.",
        "linguistic_quality": "Clear and natural; 'resolution adopted on 9 November 2001' is slightly wordy.",
        "practitioner_realism": "A plausible need: what the Council demanded on illegal exploitation of DRC resources."
      },
      "scores": {
        "anchoring": 4,
        "consequence": 4,
        "informativeness": 5,
        "linguistic_quality": 4,
        "practitioner_realism": 4
      }
    },
    "anchoring": 4,
    "consequence": 4,
    "informativeness": 5,
    "linguistic_quality": 4,
    "overall": 21,
    "practitioner_realism": 4,
    "reason": "practitioner_realism: A plausible need: what the Council demanded on illegal exploitation of DRC resources.; anchoring: Organ, type, date and subject are present and accurate. The resolution number is not given, but the date plus subject is nearly unique.; consequence: Gives a specific operative demand and the condition that resources not finance the conflict.; informativeness: The answer contains the demand to cease, the condemnation and the no-conflict-financing clause, so it fully resolves the question.; linguistic_quality: Clear and natural; 'resolution adopted on 9 November 2001' is slightly wordy."
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
      "candidate_id": "q_30147879329668e52f0aae1f",
      "checks": {
        "metadata": "pass",
        "mode": "pass",
        "support": "pass"
      },
      "index": 1,
      "problems": [
        "linguistic_quality: awkward, multi-part phrasing in the question",
        "consequence: low specificity; the content is a general expression of support"
      ],
      "score_notes": {
        "anchoring": "Organ, date and subject (inter-Congolese dialogue) are accurate and sufficient.",
        "consequence": "The answer is a general expression of support and a call, with little concrete detail, so it is moderately useful.",
        "informativeness": "The answer covers the support, the call on the parties and the Facilitator's call. It is complete, but the question asks for little beyond restating the paragraph.",
        "linguistic_quality": "'Express support for and call on ... to do regarding' is awkward and clumsy.",
        "practitioner_realism": "Plausible, but the question bundles support with calls on the parties and is less like a single bounded need."
      },
      "scores": {
        "anchoring": 4,
        "consequence": 3,
        "informativeness": 4,
        "linguistic_quality": 3,
        "practitioner_realism": 3
      }
    },
    "anchoring": 4,
    "consequence": 3,
    "informativeness": 4,
    "linguistic_quality": 3,
    "overall": 17,
    "practitioner_realism": 3,
    "reason": "practitioner_realism: Plausible, but the question bundles support with calls on the parties and is less like a single bounded need.; anchoring: Organ, date and subject (inter-Congolese dialogue) are accurate and sufficient.; consequence: The answer is a general expression of support and a call, with little concrete detail, so it is moderately useful.; informativeness: The answer covers the support, the call on the parties and the Facilitator's call. It is complete, but the question asks for little beyond restating the paragraph.; linguistic_quality: 'Express support for and call on ... to do regarding' is awkward and clumsy."
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
      "candidate_id": "q_01cc2c6928e86ee2a2747c6e",
      "checks": {
        "metadata": "pass",
        "mode": "pass",
        "support": "pass"
      },
      "index": 2,
      "problems": [
        "linguistic_quality: wordy compound question"
      ],
      "score_notes": {
        "anchoring": "Organ, date and subject are accurate and sufficient.",
        "consequence": "Gives a specific finding (interdependence) and the call for international economic assistance.",
        "informativeness": "The answer fully covers the interdependence finding and the underlined need for assistance.",
        "linguistic_quality": "Wordy two-part question ('characterize ... and what did it underline'); understandable but clumsy.",
        "practitioner_realism": "Plausible need on the Council's link between the peace process and economic recovery."
      },
      "scores": {
        "anchoring": 4,
        "consequence": 4,
        "informativeness": 5,
        "linguistic_quality": 3,
        "practitioner_realism": 4
      }
    },
    "anchoring": 4,
    "consequence": 4,
    "informativeness": 5,
    "linguistic_quality": 3,
    "overall": 20,
    "practitioner_realism": 4,
    "reason": "practitioner_realism: Plausible need on the Council's link between the peace process and economic recovery.; anchoring: Organ, date and subject are accurate and sufficient.; consequence: Gives a specific finding (interdependence) and the call for international economic assistance.; informativeness: The answer fully covers the interdependence finding and the underlined need for assistance.; linguistic_quality: Wordy two-part question ('characterize ... and what did it underline'); understandable but clumsy."
  }
]
````

### mode/un/2003/a/res/58/298#4/practitioner: faithfulness — completed

````json
[
  {
    "_response": {
      "grounding": 5,
      "index": 0,
      "numerical_fidelity": 5,
      "precision": 5,
      "reason": "Paragraph 13 is quoted verbatim. The date 18 June 2004 comes from the document title. The answer is complete and matches the question."
    },
    "grounding": 5,
    "numerical_fidelity": 5,
    "overall": 15,
    "precision": 5,
    "reason": "Paragraph 13 is quoted verbatim. The date 18 June 2004 comes from the document title. The answer is complete and matches the question."
  },
  {
    "_response": {
      "grounding": 5,
      "index": 1,
      "numerical_fidelity": 5,
      "precision": 5,
      "reason": "Paragraph 14 is quoted verbatim. The amount of 121,610,300 dollars, the 743 continuing posts and the 18 new temporary posts all match. The answer is complete."
    },
    "grounding": 5,
    "numerical_fidelity": 5,
    "overall": 15,
    "precision": 5,
    "reason": "Paragraph 14 is quoted verbatim. The amount of 121,610,300 dollars, the 743 continuing posts and the 18 new temporary posts all match. The answer is complete."
  },
  {
    "_response": {
      "grounding": 5,
      "index": 2,
      "numerical_fidelity": 5,
      "precision": 5,
      "reason": "Paragraph 15(a) is quoted and matches the source. The figures 8,478,600, 8,350,800 and 127,800 dollars, the periods ended 30 June 2003 and 30 June 2001, and the 2004-2005 application period are all correct. The answer omits the lead-in 'Decides that... financed as follows', but the question's 'direct' framing is implied by the context. The 'to be applied' phrasing directly answers the question."
    },
    "grounding": 5,
    "numerical_fidelity": 5,
    "overall": 15,
    "precision": 5,
    "reason": "Paragraph 15(a) is quoted and matches the source. The figures 8,478,600, 8,350,800 and 127,800 dollars, the periods ended 30 June 2003 and 30 June 2001, and the 2004-2005 application period are all correct. The answer omits the lead-in 'Decides that... financed as follows', but the question's 'direct' framing is implied by the context. The 'to be applied' phrasing directly answers the question."
  }
]
````

### mode/un/2003/a/res/58/298#4/practitioner: quality_index_recovery — completed

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
      "candidate_id": "q_1e9d19c16bd117633679d948",
      "checks": {
        "metadata": "fail",
        "mode": "pass",
        "support": "pass"
      },
      "index": 0,
      "problems": [
        "informativeness: the answer largely repeats the question's content.",
        "consequence: the content is a mere acknowledgement of a report.",
        "metadata: the anchors 'financial-performance report for 1 July 2002 to 30 June 2003' and 'the General Assembly take note of on 18 June 2004' are not verbatim substrings of the question. The first has a hyphen and is missing 'the', and the second is missing 'did'.",
        "metadata: the date 18 June 2004 comes from the document title, not the target, but the question handles it correctly as context."
      ],
      "score_notes": {
        "anchoring_and_time": "The period and the date of 18 June 2004 are given. The 'support account' is identified only loosely, since the question does not say it is for peacekeeping operations.",
        "consequence": "The content is only a takes-note of a report, with no norm, task or figure. It has minimal operational consequence.",
        "informativeness": "The question already contains the report's subject and period, so the answer largely repeats it. The only new information is that it is the Secretary-General's report, which is circular.",
        "linguistic_quality": "The question is clear and grammatical. 'Take note of on 18 June' is slightly awkward.",
        "practitioner_realism": "Asking which report was noted is a weak specialist need. It is nearly a lookup of a procedural acknowledgement."
      },
      "scores": {
        "anchoring_and_time": 4,
        "consequence": 2,
        "informativeness": 2,
        "linguistic_quality": 4,
        "practitioner_realism": 2
      }
    },
    "anchoring_and_time": 4,
    "consequence": 2,
    "informativeness": 2,
    "linguistic_quality": 4,
    "overall": 14,
    "practitioner_realism": 2,
    "reason": "practitioner_realism: Asking which report was noted is a weak specialist need. It is nearly a lookup of a procedural acknowledgement.; anchoring_and_time: The period and the date of 18 June 2004 are given. The 'support account' is identified only loosely, since the question does not say it is for peacekeeping operations.; consequence: The content is only a takes-note of a report, with no norm, task or figure. It has minimal operational consequence.; informativeness: The question already contains the report's subject and period, so the answer largely repeats it. The only new information is that it is the Secretary-General's report, which is circular.; linguistic_quality: The question is clear and grammatical. 'Take note of on 18 June' is slightly awkward."
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
      "candidate_id": "q_e000b0ac0ee9360558b7c29c",
      "checks": {
        "metadata": "pass",
        "mode": "pass",
        "support": "pass"
      },
      "index": 1,
      "problems": [],
      "score_notes": {
        "anchoring_and_time": "The period is explicit and the support account is named. The question does not say 'peacekeeping', though the support account is distinctive enough in context.",
        "consequence": "It asks for an approved amount and post numbers. Both are concrete, consequential figures.",
        "informativeness": "The answer gives the amount of 121,610,300 dollars and the 743 continuing and 18 new posts. It resolves both parts of the question.",
        "linguistic_quality": "The question is clear. It is a compound question but reads naturally.",
        "practitioner_realism": "Budget approval and post numbers are a realistic need for a budget practitioner."
      },
      "scores": {
        "anchoring_and_time": 4,
        "consequence": 5,
        "informativeness": 5,
        "linguistic_quality": 4,
        "practitioner_realism": 4
      }
    },
    "anchoring_and_time": 4,
    "consequence": 5,
    "informativeness": 5,
    "linguistic_quality": 4,
    "overall": 22,
    "practitioner_realism": 4,
    "reason": "practitioner_realism: Budget approval and post numbers are a realistic need for a budget practitioner.; anchoring_and_time: The period is explicit and the support account is named. The question does not say 'peacekeeping', though the support account is distinctive enough in context.; consequence: It asks for an approved amount and post numbers. Both are concrete, consequential figures.; informativeness: The answer gives the amount of 121,610,300 dollars and the 743 continuing and 18 new posts. It resolves both parts of the question.; linguistic_quality: The question is clear. It is a compound question but reads naturally."
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
      "candidate_id": "q_45215b9fdcd983b91d2cd7e2",
      "checks": {
        "metadata": "fail",
        "mode": "pass",
        "support": "pass"
      },
      "index": 2,
      "problems": [
        "anchoring_and_time: the support account or peacekeeping is not mentioned.",
        "informativeness: the answer is partly circular, since 'applied to the resources required' repeats the question.",
        "metadata: the anchor '8,478,600-dollar unencumbered balance and other income' is not a verbatim substring, because the question has 'the 8,478,600-dollar unencumbered...' and the anchor is actually present. The second anchor 'applied for 1 July 2004 to 30 June 2005' is not verbatim, since the question says 'be applied for'. It is a substring, so this part passes, but the answer text is a fragment that begins with 'The unencumbered balance' rather than a full proposition."
      ],
      "score_notes": {
        "anchoring_and_time": "The question gives the period and the amount but never names the support account for peacekeeping operations. Only the figure anchors it, so the regime context is thin.",
        "consequence": "It concerns a concrete financing decision.",
        "informativeness": "The answer is essentially that the balance is applied to the resources required for 2004/05. That is mostly restated in the question and adds little beyond the breakdown of the amount. The comprising figures are useful.",
        "linguistic_quality": "The question is clear and natural.",
        "practitioner_realism": "How the balance is applied is a plausible financing question."
      },
      "scores": {
        "anchoring_and_time": 3,
        "consequence": 4,
        "informativeness": 3,
        "linguistic_quality": 4,
        "practitioner_realism": 4
      }
    },
    "anchoring_and_time": 3,
    "consequence": 4,
    "informativeness": 3,
    "linguistic_quality": 4,
    "overall": 18,
    "practitioner_realism": 4,
    "reason": "practitioner_realism: How the balance is applied is a plausible financing question.; anchoring_and_time: The question gives the period and the amount but never names the support account for peacekeeping operations. Only the figure anchors it, so the regime context is thin.; consequence: It concerns a concrete financing decision.; informativeness: The answer is essentially that the balance is applied to the resources required for 2004/05. That is mostly restated in the question and adds little beyond the breakdown of the amount. The comprising figures are useful.; linguistic_quality: The question is clear and natural."
  }
]
````

### mode/un/2004/s/2004/505#15/lookup: faithfulness — completed

````json
[
  {
    "_response": {
      "grounding": 5,
      "index": 0,
      "numerical_fidelity": 5,
      "precision": 4,
      "reason": "The answer matches the target text. The question says 'the resolution' without naming it; context shows it is resolution 1540 (2004). 'Legal effect' is a slight paraphrase, but the answer content (no alteration of existing treaties, no basis for unilateral enforcement) is fully supported. The answer is complete."
    },
    "grounding": 5,
    "numerical_fidelity": 5,
    "overall": 14,
    "precision": 4,
    "reason": "The answer matches the target text. The question says 'the resolution' without naming it; context shows it is resolution 1540 (2004). 'Legal effect' is a slight paraphrase, but the answer content (no alteration of existing treaties, no basis for unilateral enforcement) is fully supported. The answer is complete."
  },
  {
    "_response": {
      "grounding": 5,
      "index": 1,
      "numerical_fidelity": 5,
      "precision": 4,
      "reason": "The answer is supported verbatim: 'within the next six months' and a first report on steps taken or intended. The 'resolution' referent is 1540, resolved by context. The 'next six months' timing is relative to the resolution's adoption, which the answer leaves implicit, a minor point. The question is slightly loose in asking 'when', but the answer matches the span."
    },
    "grounding": 5,
    "numerical_fidelity": 5,
    "overall": 14,
    "precision": 4,
    "reason": "The answer is supported verbatim: 'within the next six months' and a first report on steps taken or intended. The 'resolution' referent is 1540, resolved by context. The 'next six months' timing is relative to the resolution's adoption, which the answer leaves implicit, a minor point. The question is slightly loose in asking 'when', but the answer matches the span."
  },
  {
    "_response": {
      "grounding": 5,
      "index": 2,
      "numerical_fidelity": 5,
      "precision": 5,
      "reason": "The guest list matches the target exactly, including the names and roles. The 15 April date is correct and the answer includes no extraneous material. The World Bank President is left unnamed, as in the source."
    },
    "grounding": 5,
    "numerical_fidelity": 5,
    "overall": 15,
    "precision": 5,
    "reason": "The guest list matches the target exactly, including the names and roles. The 15 April date is correct and the answer includes no extraneous material. The World Bank President is left unnamed, as in the source."
  }
]
````

### mode/un/2004/s/2004/505#15/lookup: quality_index_recovery — completed

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
      "candidate_id": "q_e55029e6a278351d2fa5502d",
      "checks": {
        "metadata": "fail",
        "mode": "pass",
        "support": "pass"
      },
      "index": 0,
      "problems": [
        "anchoring: the resolution is not identified, so the subject anchor is insufficient.",
        "metadata: the anchor 'what agreement was reached' is generic question wording, not a substantive base-locator substring.",
        "metadata: the type sanction_condition_or_consequence fits poorly, since the content is an understanding about the resolution's scope."
      ],
      "score_notes": {
        "anchoring": "The letter and date are right, but 'the resolution' is unresolved. The assessment covers five resolutions, and this passage concerns the non-proliferation resolution (1540), which is not named. Subject anchoring is therefore insufficient.",
        "consequence": "The answer is useful for knowing what the Council understood about the resolution's scope. It is a single bounded fact.",
        "informativeness": "The answer span is a complete contiguous statement. It covers both that existing treaties are unaltered and that there is no basis for unilateral enforcement. It is not circular.",
        "linguistic_quality": "The wording is clear and natural. 'Legal effect' is slightly loose for what is an agreed understanding.",
        "practitioner_realism": "Asking what was agreed about a resolution's effect on existing arms-control treaties is plausible. The question never says which resolution, which weakens it as a realistic known-source need."
      },
      "scores": {
        "anchoring": 2,
        "consequence": 3,
        "informativeness": 4,
        "linguistic_quality": 4,
        "practitioner_realism": 3
      }
    },
    "anchoring": 2,
    "consequence": 3,
    "informativeness": 4,
    "linguistic_quality": 4,
    "overall": 16,
    "practitioner_realism": 3,
    "reason": "practitioner_realism: Asking what was agreed about a resolution's effect on existing arms-control treaties is plausible. The question never says which resolution, which weakens it as a realistic known-source need.; anchoring: The letter and date are right, but 'the resolution' is unresolved. The assessment covers five resolutions, and this passage concerns the non-proliferation resolution (1540), which is not named. Subject anchoring is therefore insufficient.; consequence: The answer is useful for knowing what the Council understood about the resolution's scope. It is a single bounded fact.; informativeness: The answer span is a complete contiguous statement. It covers both that existing treaties are unaltered and that there is no basis for unilateral enforcement. It is not circular.; linguistic_quality: The wording is clear and natural. 'Legal effect' is slightly loose for what is an agreed understanding."
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
      "candidate_id": "q_7b76f98f43754156454a9ac2",
      "checks": {
        "metadata": "fail",
        "mode": "pass",
        "support": "pass"
      },
      "index": 1,
      "problems": [
        "anchoring: the resolution is not named, so 'implementation report' is ambiguous.",
        "informativeness: the six-month period is relative and has no stated starting point.",
        "metadata: the anchor 'when must Member States submit' is generic question wording, not a substantive locator."
      ],
      "score_notes": {
        "anchoring": "The letter, date and April 2004 presidency are correct. The subject ('their first implementation report') does not say which resolution is meant, so the independent subject anchor is weak.",
        "consequence": "A reporting deadline is specific and useful.",
        "informativeness": "The answer is complete as extracted. 'Within the next six months' is a relative period with no start date, so it gives no absolute deadline.",
        "linguistic_quality": "The question is clear and concise.",
        "practitioner_realism": "A reporting deadline is a plausible practitioner question. Without naming the resolution it reads as vague."
      },
      "scores": {
        "anchoring": 3,
        "consequence": 3,
        "informativeness": 3,
        "linguistic_quality": 4,
        "practitioner_realism": 3
      }
    },
    "anchoring": 3,
    "consequence": 3,
    "informativeness": 3,
    "linguistic_quality": 4,
    "overall": 16,
    "practitioner_realism": 3,
    "reason": "practitioner_realism: A reporting deadline is a plausible practitioner question. Without naming the resolution it reads as vague.; anchoring: The letter, date and April 2004 presidency are correct. The subject ('their first implementation report') does not say which resolution is meant, so the independent subject anchor is weak.; consequence: A reporting deadline is specific and useful.; informativeness: The answer is complete as extracted. 'Within the next six months' is a relative period with no start date, so it gives no absolute deadline.; linguistic_quality: The question is clear and concise."
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
      "candidate_id": "q_371ab9efe4baaa62552ccfb8",
      "checks": {
        "metadata": "fail",
        "mode": "pass",
        "support": "pass"
      },
      "index": 2,
      "problems": [
        "metadata: the anchor 'who spoke as guests' is generic question wording, not a substantive base-locator substring."
      ],
      "score_notes": {
        "anchoring": "The letter date, the German presidency assessment, the 15 April 2004 meeting and the business-in-conflict-prevention subject jointly identify a unique passage.",
        "consequence": "It gives a specific factual answer about participation, which is useful though modest in significance.",
        "informativeness": "The answer span lists all the guest speakers with their roles and is complete and non-circular.",
        "linguistic_quality": "The question is clear and natural. The answer keeps the source's 'Guests speakers' typo, which is a copying artifact and not the question's fault.",
        "practitioner_realism": "Asking who the guest speakers were at a named Council meeting is a plausible bounded lookup. The answer is a list of five speakers."
      },
      "scores": {
        "anchoring": 5,
        "consequence": 4,
        "informativeness": 5,
        "linguistic_quality": 4,
        "practitioner_realism": 4
      }
    },
    "anchoring": 5,
    "consequence": 4,
    "informativeness": 5,
    "linguistic_quality": 4,
    "overall": 22,
    "practitioner_realism": 4,
    "reason": "practitioner_realism: Asking who the guest speakers were at a named Council meeting is a plausible bounded lookup. The answer is a list of five speakers.; anchoring: The letter date, the German presidency assessment, the 15 April 2004 meeting and the business-in-conflict-prevention subject jointly identify a unique passage.; consequence: It gives a specific factual answer about participation, which is useful though modest in significance.; informativeness: The answer span lists all the guest speakers with their roles and is complete and non-circular.; linguistic_quality: The question is clear and natural. The answer keeps the source's 'Guests speakers' typo, which is a copying artifact and not the question's fault."
  }
]
````

### mode/un/2005/a/res/60/226#3/practitioner: faithfulness — completed

````json
[
  {
    "_response": {
      "grounding": 4,
      "index": 0,
      "numerical_fidelity": 5,
      "precision": 4,
      "reason": "The answer reproduces paragraph 4(b) accurately, including the conditions: the group of governmental experts, available resources, equitable geographical representation, and the decision at the sixty-first session. The question says 'arrange and report in 2006', but the text says the group is convened in 2006, not that the report is due in 2006. That is a slight premise mismatch. The answer is complete, with minor extra detail. The dates and session numbers match."
    },
    "grounding": 4,
    "numerical_fidelity": 5,
    "overall": 13,
    "precision": 4,
    "reason": "The answer reproduces paragraph 4(b) accurately, including the conditions: the group of governmental experts, available resources, equitable geographical representation, and the decision at the sixty-first session. The question says 'arrange and report in 2006', but the text says the group is convened in 2006, not that the report is due in 2006. That is a slight premise mismatch. The answer is complete, with minor extra detail. The dates and session numbers match."
  },
  {
    "_response": {
      "grounding": 5,
      "index": 1,
      "numerical_fidelity": 5,
      "precision": 5,
      "reason": "Paragraph 4(a) is quoted faithfully: views on the continuing operation of the Register and its further development, and on transparency measures related to weapons of mass destruction. The answer is complete and contains no extra material. The date in the question matches the resolution date, and there are no numerical issues."
    },
    "grounding": 5,
    "numerical_fidelity": 5,
    "overall": 15,
    "precision": 5,
    "reason": "Paragraph 4(a) is quoted faithfully: views on the continuing operation of the Register and its further development, and on transparency measures related to weapons of mass destruction. The answer is complete and contains no extra material. The date in the question matches the resolution date, and there are no numerical issues."
  }
]
````

### mode/un/2005/a/res/60/226#3/practitioner: quality_index_recovery — completed

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
      "candidate_id": "q_f1c889ed6350d4d8dc8baf53",
      "checks": {
        "metadata": "fail",
        "mode": "pass",
        "support": "pass"
      },
      "index": 0,
      "problems": [
        "anchoring_and_time: the question names no subject (Register, transparency in armaments), so the regime is hard to identify.",
        "linguistic_quality/support: 'arrange and report in 2006' misdescribes the request; 2006 is the year the group is convened, not the year of the report.",
        "metadata: the anchors 'convened in 2006' and 'group of governmental experts' do not appear verbatim in the question text; only 'Secretary-General' does."
      ],
      "score_notes": {
        "anchoring_and_time": "The date 23 December 2005 is given, but the subject is missing. The question never mentions the Register, conventional arms or transparency in armaments, and calls the resolution a 'review'. Anyone reading it cold could not tell which regime is meant.",
        "consequence": "It asks for a concrete task and procedure: an expert-assisted report feeding a decision at the sixty-first session.",
        "informativeness": "The answer span fully covers the expert group, the 2006 convening, the resource and geographic conditions, and the purpose of the report. The question's phrase 'arrange and report in 2006' is slightly off, because the group is convened in 2006 and the report is aimed at a sixty-first session decision.",
        "linguistic_quality": "'Review' is loose and 'arrange and report in 2006' misstates the timing and the action. The wording is understandable but imprecise.",
        "practitioner_realism": "A request to convene an expert group and prepare a report is a bounded specialist need, but the vague wording of the question weakens the realism."
      },
      "scores": {
        "anchoring_and_time": 2,
        "consequence": 4,
        "informativeness": 4,
        "linguistic_quality": 3,
        "practitioner_realism": 3
      }
    },
    "anchoring_and_time": 2,
    "consequence": 4,
    "informativeness": 4,
    "linguistic_quality": 3,
    "overall": 16,
    "practitioner_realism": 3,
    "reason": "practitioner_realism: A request to convene an expert group and prepare a report is a bounded specialist need, but the vague wording of the question weakens the realism.; anchoring_and_time: The date 23 December 2005 is given, but the subject is missing. The question never mentions the Register, conventional arms or transparency in armaments, and calls the resolution a 'review'. Anyone reading it cold could not tell which regime is meant.; consequence: It asks for a concrete task and procedure: an expert-assisted report feeding a decision at the sixty-first session.; informativeness: The answer span fully covers the expert group, the 2006 convening, the resource and geographic conditions, and the purpose of the report. The question's phrase 'arrange and report in 2006' is slightly off, because the group is convened in 2006 and the report is aimed at a sixty-first session decision.; linguistic_quality: 'Review' is loose and 'arrange and report in 2006' misstates the timing and the action. The wording is understandable but imprecise."
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
      "candidate_id": "q_8873839e9a9c93a7dcf3c3cc",
      "checks": {
        "metadata": "fail",
        "mode": "pass",
        "support": "pass"
      },
      "index": 1,
      "problems": [
        "anchoring_and_time: the subject (UN Register of Conventional Arms / transparency in armaments) is not identified in the question.",
        "metadata: neither reported anchor ('views on the continuing operation of the Register and its further development', 'transparency measures related to weapons of mass destruction') appears verbatim in the question text."
      ],
      "score_notes": {
        "anchoring_and_time": "The date 23 December 2005 is present, but the question never names the Register or transparency in armaments. The answer supplies the topic, which the question should have done.",
        "consequence": "It concerns a recalled, earlier request to Member States and so is a modest input task. It is still concrete, and it adds the weapons of mass destruction transparency element.",
        "informativeness": "The answer names both topics: the continuing operation and further development of the Register, and transparency measures related to weapons of mass destruction. It partly repeats the question's 'recall requesting' phrasing, but it is not circular.",
        "linguistic_quality": "The question is clear and grammatical. 'Recall requesting' is slightly clumsy.",
        "practitioner_realism": "Asking what views Member States were asked to supply is a plausible specialist query, though a narrow one."
      },
      "scores": {
        "anchoring_and_time": 3,
        "consequence": 3,
        "informativeness": 4,
        "linguistic_quality": 4,
        "practitioner_realism": 3
      }
    },
    "anchoring_and_time": 3,
    "consequence": 3,
    "informativeness": 4,
    "linguistic_quality": 4,
    "overall": 17,
    "practitioner_realism": 3,
    "reason": "practitioner_realism: Asking what views Member States were asked to supply is a plausible specialist query, though a narrow one.; anchoring_and_time: The date 23 December 2005 is present, but the question never names the Register or transparency in armaments. The answer supplies the topic, which the question should have done.; consequence: It concerns a recalled, earlier request to Member States and so is a modest input task. It is still concrete, and it adds the weapons of mass destruction transparency element.; informativeness: The answer names both topics: the continuing operation and further development of the Register, and transparency measures related to weapons of mass destruction. It partly repeats the question's 'recall requesting' phrasing, but it is not circular.; linguistic_quality: The question is clear and grammatical. 'Recall requesting' is slightly clumsy."
  }
]
````

### mode/un/2006/ccw/conf_iii/sr_2#8/practitioner: faithfulness — completed

````json
[
  {
    "_response": {
      "grounding": 4,
      "index": 0,
      "numerical_fidelity": 5,
      "precision": 5,
      "reason": "The answer is taken directly from the target block. The block does not name Japan as the speaker in that sentence, but the context places the passage in Japan's statement, so attribution is resolved. The 'Third Review Conference' premise is supported by the context. The question says 'basis', which fits 'practical basis' (the McCormack report). Minor point: the sentence about substantial discussions is slightly extra but relevant. No numbers are involved."
    },
    "grounding": 4,
    "numerical_fidelity": 5,
    "overall": 14,
    "precision": 5,
    "reason": "The answer is taken directly from the target block. The block does not name Japan as the speaker in that sentence, but the context places the passage in Japan's statement, so attribution is resolved. The 'Third Review Conference' premise is supported by the context. The question says 'basis', which fits 'practical basis' (the McCormack report). Minor point: the sentence about substantial discussions is slightly extra but relevant. No numbers are involved."
  },
  {
    "_response": {
      "grounding": 5,
      "index": 1,
      "numerical_fidelity": 5,
      "precision": 4,
      "reason": "The answer matches the target text, and it is attributed to Japan. The question asks 'what compliance mechanism', and the answer gives the universally applicable mechanism Japan urged States to cooperate on, with a will to compromise. The answer is complete. It is slightly wordy but acceptable."
    },
    "grounding": 5,
    "numerical_fidelity": 5,
    "overall": 14,
    "precision": 4,
    "reason": "The answer matches the target text, and it is attributed to Japan. The question asks 'what compliance mechanism', and the answer gives the universally applicable mechanism Japan urged States to cooperate on, with a will to compromise. The answer is complete. It is slightly wordy but acceptable."
  },
  {
    "_response": {
      "grounding": 5,
      "index": 2,
      "numerical_fidelity": 5,
      "precision": 5,
      "reason": "Both sentences are faithful to the target block. The statement is correctly attributed to Ukraine, with 'hoped' preserved as a hope rather than a fact. It covers both compliance and strengthening, as the question asks. No numbers are involved."
    },
    "grounding": 5,
    "numerical_fidelity": 5,
    "overall": 15,
    "precision": 5,
    "reason": "Both sentences are faithful to the target block. The statement is correctly attributed to Ukraine, with 'hoped' preserved as a hope rather than a fact. It covers both compliance and strengthening, as the question asks. No numbers are involved."
  }
]
````

### mode/un/2006/ccw/conf_iii/sr_2#8/practitioner: quality_index_recovery — completed

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
      "candidate_id": "q_31aa29a672d0f98e1cb5374d",
      "checks": {
        "metadata": "fail",
        "mode": "pass",
        "support": "pass"
      },
      "index": 0,
      "problems": [
        "metadata: question_type operative_action fits poorly, since Japan describes an existing basis rather than an action; finding_event_or_assessment fits better.",
        "anchoring_and_time: no absolute date and no Convention or CCW named."
      ],
      "score_notes": {
        "anchoring_and_time": "The speaker and the topic are clear. \"Third Review Conference\" is named without the CCW/Convention and without a year, so the regime and date are not stated.",
        "consequence": "The answer is a concrete attributed assessment, the McCormack report as a practical basis for further work. It is modest in weight.",
        "informativeness": "The answer span names the McCormack report as the basis. It also adds the preceding clause about ongoing discussions, which is harmless context.",
        "linguistic_quality": "Clear and natural.",
        "practitioner_realism": "A plausible bounded query about what Japan cited as a basis for work on preventive measures for munitions."
      },
      "scores": {
        "anchoring_and_time": 3,
        "consequence": 3,
        "informativeness": 4,
        "linguistic_quality": 4,
        "practitioner_realism": 4
      }
    },
    "anchoring_and_time": 3,
    "consequence": 3,
    "informativeness": 4,
    "linguistic_quality": 4,
    "overall": 18,
    "practitioner_realism": 4,
    "reason": "practitioner_realism: A plausible bounded query about what Japan cited as a basis for work on preventive measures for munitions.; anchoring_and_time: The speaker and the topic are clear. \"Third Review Conference\" is named without the CCW/Convention and without a year, so the regime and date are not stated.; consequence: The answer is a concrete attributed assessment, the McCormack report as a practical basis for further work. It is modest in weight.; informativeness: The answer span names the McCormack report as the basis. It also adds the preceding clause about ongoing discussions, which is harmless context.; linguistic_quality: Clear and natural."
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
      "candidate_id": "q_3d6ad41b7ee9ac40b4fef6e6",
      "checks": {
        "metadata": "pass",
        "mode": "pass",
        "support": "pass"
      },
      "index": 1,
      "problems": [
        "anchoring_and_time: no absolute date and no explicit Convention named."
      ],
      "score_notes": {
        "anchoring_and_time": "Japan and the subject are clear, but the Convention and the year are not stated. \"Third Review Conference\" is the only contextual marker.",
        "consequence": "Captures an attributed request or proposal, a universally applicable compliance mechanism, with its status as an urging preserved.",
        "informativeness": "The answer is complete and non-circular. The mechanism is described only generically, which is all the source says.",
        "linguistic_quality": "Fluent and precise.",
        "practitioner_realism": "A plausible question about a State's position on a compliance mechanism for the Convention."
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
    "reason": "practitioner_realism: A plausible question about a State's position on a compliance mechanism for the Convention.; anchoring_and_time: Japan and the subject are clear, but the Convention and the year are not stated. \"Third Review Conference\" is the only contextual marker.; consequence: Captures an attributed request or proposal, a universally applicable compliance mechanism, with its status as an urging preserved.; informativeness: The answer is complete and non-circular. The mechanism is described only generically, which is all the source says.; linguistic_quality: Fluent and precise."
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
      "candidate_id": "q_901cb4be43a168e8e7ac87f4",
      "checks": {
        "metadata": "fail",
        "mode": "pass",
        "support": "pass"
      },
      "index": 2,
      "problems": [
        "metadata: question_type situation_scope_or_coverage does not fit a question about a State's stated commitment and hopes.",
        "practitioner_realism: vague, open-ended question.",
        "anchoring_and_time: no absolute date and no explicit Convention named."
      ],
      "score_notes": {
        "anchoring_and_time": "Ukraine and the conference are identified, but the Convention and the year are not stated.",
        "consequence": "The content is largely general commitment and aspiration (compliance, effectiveness, hoped-for strengthening) with limited concrete norm or task content.",
        "informativeness": "The two-sentence answer span fully and accurately covers the question, and the speaker attribution is preserved.",
        "linguistic_quality": "Understandable; \"the Convention's instruments\" is slightly loose.",
        "practitioner_realism": "Broad \"what did Ukraine state\" framing seeks general statements of commitment rather than a precise specialist need."
      },
      "scores": {
        "anchoring_and_time": 3,
        "consequence": 3,
        "informativeness": 4,
        "linguistic_quality": 4,
        "practitioner_realism": 3
      }
    },
    "anchoring_and_time": 3,
    "consequence": 3,
    "informativeness": 4,
    "linguistic_quality": 4,
    "overall": 17,
    "practitioner_realism": 3,
    "reason": "practitioner_realism: Broad \"what did Ukraine state\" framing seeks general statements of commitment rather than a precise specialist need.; anchoring_and_time: Ukraine and the conference are identified, but the Convention and the year are not stated.; consequence: The content is largely general commitment and aspiration (compliance, effectiveness, hoped-for strengthening) with limited concrete norm or task content.; informativeness: The two-sentence answer span fully and accurately covers the question, and the speaker attribution is preserved.; linguistic_quality: Understandable; \"the Convention's instruments\" is slightly loose."
  }
]
````

### mode/un/2008/s/res/1806_2008_#8/practitioner: faithfulness — completed

````json
[
  {
    "_response": {
      "grounding": 5,
      "index": 0,
      "numerical_fidelity": 5,
      "precision": 4,
      "reason": "The answer copies paragraph 8 and is fully supported. The question asks what the JCMB needed to strengthen, and the answer covers the authority and capacity to measure progress and to facilitate coordination, plus the reporting to the aid coordination unit and the JCMB. The paragraph's opening reaffirmation of the JCMB's central role is minor extra context. There are no numbers."
    },
    "grounding": 5,
    "numerical_fidelity": 5,
    "overall": 14,
    "precision": 4,
    "reason": "The answer copies paragraph 8 and is fully supported. The question asks what the JCMB needed to strengthen, and the answer covers the authority and capacity to measure progress and to facilitate coordination, plus the reporting to the aid coordination unit and the JCMB. The paragraph's opening reaffirmation of the JCMB's central role is minor extra context. There are no numbers."
  },
  {
    "_response": {
      "grounding": 5,
      "index": 1,
      "numerical_fidelity": 5,
      "precision": 4,
      "reason": "The answer is supported by paragraph 9: pledges made at the London Conference, possible new pledges, and increased assistance to the core budget. The question's premise that resources are for 'launching the finalized ANDS' is slightly loose. The text says resource mobilization matters 'in this context' of finalization and launch. The welcome of progress is minor extra material. No numbers are involved."
    },
    "grounding": 5,
    "numerical_fidelity": 5,
    "overall": 14,
    "precision": 4,
    "reason": "The answer is supported by paragraph 9: pledges made at the London Conference, possible new pledges, and increased assistance to the core budget. The question's premise that resources are for 'launching the finalized ANDS' is slightly loose. The text says resource mobilization matters 'in this context' of finalization and launch. The welcome of progress is minor extra material. No numbers are involved."
  },
  {
    "_response": {
      "grounding": 5,
      "index": 2,
      "numerical_fidelity": 5,
      "precision": 5,
      "reason": "The answer covers the proposal, the hosting offer and the reporting follow-up from paragraph 10. It keeps the attribution of the intention to JCMB members and keeps the conditional 'if necessary' on recommendations about UNAMA's mandate. The dates (5 February 2008, June 2008) and the places (Tokyo, Paris) are accurate. The question fits the span."
    },
    "grounding": 5,
    "numerical_fidelity": 5,
    "overall": 15,
    "precision": 5,
    "reason": "The answer covers the proposal, the hosting offer and the reporting follow-up from paragraph 10. It keeps the attribution of the intention to JCMB members and keeps the conditional 'if necessary' on recommendations about UNAMA's mandate. The dates (5 February 2008, June 2008) and the places (Tokyo, Paris) are accurate. The question fits the span."
  }
]
````

### mode/un/2008/s/res/1806_2008_#8/practitioner: quality_index_recovery — completed

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
      "candidate_id": "q_78d4b5da5207a34dde3fe5fa",
      "checks": {
        "metadata": "pass",
        "mode": "pass",
        "support": "pass"
      },
      "index": 0,
      "problems": [
        "anchoring_and_time: the JCMB is not tied to Afghanistan or the Compact in the question.",
        "linguistic_quality: the phrasing is awkward and stacks two asks into one question."
      ],
      "score_notes": {
        "anchoring_and_time": "2008 is present, but the question only says JCMB, which is undefined and does not name Afghanistan or the Compact. The regime is identifiable only in part.",
        "consequence": "The answer states a concrete request to strengthen the JCMB and a cooperation and reporting task.",
        "informativeness": "The answer covers both parts, with the benchmark measurement, aid coordination and reporting to the aid coordination unit and the JCMB. It also repeats the 'reaffirms' clause, which adds little.",
        "linguistic_quality": "The wording is understandable, but 'authority and capacity ... need to strengthen' is awkward and the question is slightly vague.",
        "practitioner_realism": "The need is plausible, but the two-part question on authority and capacity plus reporting cooperation is somewhat mechanical."
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
    "reason": "practitioner_realism: The need is plausible, but the two-part question on authority and capacity plus reporting cooperation is somewhat mechanical.; anchoring_and_time: 2008 is present, but the question only says JCMB, which is undefined and does not name Afghanistan or the Compact. The regime is identifiable only in part.; consequence: The answer states a concrete request to strengthen the JCMB and a cooperation and reporting task.; informativeness: The answer covers both parts, with the benchmark measurement, aid coordination and reporting to the aid coordination unit and the JCMB. It also repeats the 'reaffirms' clause, which adds little.; linguistic_quality: The wording is understandable, but 'authority and capacity ... need to strengthen' is awkward and the question is slightly vague."
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
      "candidate_id": "q_a8bae69cd5f1026c71c05feb",
      "checks": {
        "metadata": "fail",
        "mode": "pass",
        "support": "pass"
      },
      "index": 1,
      "problems": [
        "metadata: the quantity_force_or_finance type is arguable, since no quantities are given and the content is a non-numeric stress on resource mobilization.",
        "metadata: the anchor 'launching the finalized ANDS' is verbatim but the question slightly mischaracterizes the ANDS status, since the launch is still anticipated."
      ],
      "score_notes": {
        "anchoring_and_time": "ANDS and 2008 give usable context, though Afghanistan is not named.",
        "consequence": "The answer is a stated emphasis on resource mobilization, namely fulfilling pledges and increasing core budget assistance. It is moderately useful.",
        "informativeness": "The answer resolves the question and lists the pledges, new pledges and core budget assistance. It also includes a welcome clause that is not needed, and the question implies resource mobilization is for the launch when the text says 'in this context'.",
        "linguistic_quality": "The wording is readable but clumsy: 'launching the finalized ANDS'.",
        "practitioner_realism": "The need is plausible, but the framing of 'resource mobilization ... for launching' is slightly off the text."
      },
      "scores": {
        "anchoring_and_time": 4,
        "consequence": 3,
        "informativeness": 3,
        "linguistic_quality": 3,
        "practitioner_realism": 3
      }
    },
    "anchoring_and_time": 4,
    "consequence": 3,
    "informativeness": 3,
    "linguistic_quality": 3,
    "overall": 16,
    "practitioner_realism": 3,
    "reason": "practitioner_realism: The need is plausible, but the framing of 'resource mobilization ... for launching' is slightly off the text.; anchoring_and_time: ANDS and 2008 give usable context, though Afghanistan is not named.; consequence: The answer is a stated emphasis on resource mobilization, namely fulfilling pledges and increasing core budget assistance. It is moderately useful.; informativeness: The answer resolves the question and lists the pledges, new pledges and core budget assistance. It also includes a welcome clause that is not needed, and the question implies resource mobilization is for the launch when the text says 'in this context'.; linguistic_quality: The wording is readable but clumsy: 'launching the finalized ANDS'."
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
      "candidate_id": "q_d21843fe0b2124533e0a4397",
      "checks": {
        "metadata": "fail",
        "mode": "pass",
        "support": "pass"
      },
      "index": 2,
      "problems": [
        "metadata: the actor_body_or_procedure type is debatable, because the content is partly a date/mandate and reporting request.",
        "metadata: the single anchor covers the whole list and is not a distinct substantive substring for each part.",
        "linguistic_quality: 'were specified' is vague."
      ],
      "score_notes": {
        "anchoring_and_time": "The distinctive date and place, 5 February 2008 Tokyo, identify the passage well.",
        "consequence": "The answer contains a concrete request to report, the hosting offer and a conditional recommendation on the UNAMA mandate.",
        "informativeness": "The answer covers the proposed conference, the French offer to host in Paris in June 2008, and the Secretary-General's report with conditional recommendations.",
        "linguistic_quality": "The question is a vague three-part list ('specified'), which makes it less natural and less precise.",
        "practitioner_realism": "A practitioner would plausibly want the follow-up to the Tokyo meeting, including the conference, host and reporting."
      },
      "scores": {
        "anchoring_and_time": 5,
        "consequence": 4,
        "informativeness": 4,
        "linguistic_quality": 3,
        "practitioner_realism": 4
      }
    },
    "anchoring_and_time": 5,
    "consequence": 4,
    "informativeness": 4,
    "linguistic_quality": 3,
    "overall": 20,
    "practitioner_realism": 4,
    "reason": "practitioner_realism: A practitioner would plausibly want the follow-up to the Tokyo meeting, including the conference, host and reporting.; anchoring_and_time: The distinctive date and place, 5 February 2008 Tokyo, identify the passage well.; consequence: The answer contains a concrete request to report, the hosting offer and a conditional recommendation on the UNAMA mandate.; informativeness: The answer covers the proposed conference, the French offer to host in Paris in June 2008, and the Secretary-General's report with conditional recommendations.; linguistic_quality: The question is a vague three-part list ('specified'), which makes it less natural and less precise."
  }
]
````

### mode/un/2009/a/ac_109/2009/sr_7#4/lookup: faithfulness — completed

````json
[
  {
    "_response": {
      "grounding": 5,
      "index": 0,
      "numerical_fidelity": 5,
      "precision": 5,
      "reason": "The answer matches paragraph 10 and is attributed to Mr. Mahiga. The date 16 June 2009 matches the meeting date. It gives exactly what was unacceptable, with the necessary concessive clause."
    },
    "grounding": 5,
    "numerical_fidelity": 5,
    "overall": 15,
    "precision": 5,
    "reason": "The answer matches paragraph 10 and is attributed to Mr. Mahiga. The date 16 June 2009 matches the meeting date. It gives exactly what was unacceptable, with the necessary concessive clause."
  },
  {
    "_response": {
      "grounding": 5,
      "index": 1,
      "numerical_fidelity": 5,
      "precision": 5,
      "reason": "Paragraph 11 supports this. Mr. Mahiga reaffirmed his delegation's support for the efforts of people under colonial rule to exercise their inalienable right to self-determination, including independence. The answer is complete and attributed."
    },
    "grounding": 5,
    "numerical_fidelity": 5,
    "overall": 15,
    "precision": 5,
    "reason": "Paragraph 11 supports this. Mr. Mahiga reaffirmed his delegation's support for the efforts of people under colonial rule to exercise their inalienable right to self-determination, including independence. The answer is complete and attributed."
  },
  {
    "_response": {
      "grounding": 4,
      "index": 2,
      "numerical_fidelity": 5,
      "precision": 4,
      "reason": "The answer matches the source text, but 'They' is unresolved without the question. The question says 'Western Sahara's future', and the source says 'the people of Western Sahara', so the referent needs resolving. This is a minor issue. The content is otherwise accurate and complete, and there are no numbers."
    },
    "grounding": 4,
    "numerical_fidelity": 5,
    "overall": 13,
    "precision": 4,
    "reason": "The answer matches the source text, but 'They' is unresolved without the question. The question says 'Western Sahara's future', and the source says 'the people of Western Sahara', so the referent needs resolving. This is a minor issue. The content is otherwise accurate and complete, and there are no numbers."
  }
]
````

### mode/un/2009/a/ac_109/2009/sr_7#4/lookup: quality_index_recovery — completed

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
      "candidate_id": "q_4aa5f169a561d290bb6bf9df",
      "checks": {
        "metadata": "uncertain",
        "mode": "pass",
        "support": "pass"
      },
      "index": 0,
      "problems": [
        "metadata: the anchor 'what was unacceptable about Western Sahara’s status' does not appear verbatim in the base question, which says 'what was unacceptable about Western Sahara’s status?'; the substring is fine, but it is a generic phrase that overlaps the slot and adds little independent anchoring.",
        "anchoring: the anchor is generic and does not carry the speaker or time."
      ],
      "score_notes": {
        "anchoring": "Identifies speaker, date, body and record type, and the subject is clear. The organ/author is slightly ambiguous because Mahiga is a delegate, not an organ. The cited form's paragraph 10 matches.",
        "consequence": "Gives a specific attributed position, but it is a rhetorical assessment rather than an operative or factual detail.",
        "informativeness": "The answer fully resolves the question with the complete condition (consistent recognition by GA and SC, only unresolved case in Africa). The 'unacceptable' framing makes it somewhat echoing.",
        "linguistic_quality": "Clear and natural; 'status' is slightly loose.",
        "practitioner_realism": "Plausible bounded need to find what the Tanzanian representative called unacceptable at this meeting."
      },
      "scores": {
        "anchoring": 4,
        "consequence": 3,
        "informativeness": 4,
        "linguistic_quality": 4,
        "practitioner_realism": 4
      }
    },
    "anchoring": 4,
    "consequence": 3,
    "informativeness": 4,
    "linguistic_quality": 4,
    "overall": 19,
    "practitioner_realism": 4,
    "reason": "practitioner_realism: Plausible bounded need to find what the Tanzanian representative called unacceptable at this meeting.; anchoring: Identifies speaker, date, body and record type, and the subject is clear. The organ/author is slightly ambiguous because Mahiga is a delegate, not an organ. The cited form's paragraph 10 matches.; consequence: Gives a specific attributed position, but it is a rhetorical assessment rather than an operative or factual detail.; informativeness: The answer fully resolves the question with the complete condition (consistent recognition by GA and SC, only unresolved case in Africa). The 'unacceptable' framing makes it somewhat echoing.; linguistic_quality: Clear and natural; 'status' is slightly loose."
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
      "candidate_id": "q_436506461ecdec10ae609440",
      "checks": {
        "metadata": "fail",
        "mode": "pass",
        "support": "pass"
      },
      "index": 1,
      "problems": [
        "anchoring: no absolute time and no organ or document type in the base question.",
        "metadata: the cited form changes the meaning by asking what 'paragraph 11 ... report[ed]', which drops the actor Mr. Mahiga and misattributes the statement.",
        "metadata: the anchor is a verbatim substring of the base question but is a clause about reports, not a distinguishing independent anchor."
      ],
      "score_notes": {
        "anchoring": "Names the speaker and subject but gives no date or document/organ. The Special Committee and 16 June 2009 are missing, so the locator is weak for a known-source lookup.",
        "consequence": "Identifies a reaffirmed position of support, a generic statement of moderate specificity.",
        "informativeness": "The answer is complete and non-circular, giving support for the efforts of people under colonial rule to exercise self-determination, including independence.",
        "linguistic_quality": "Natural and clear wording.",
        "practitioner_realism": "Plausible but narrow: asks what a delegate reaffirmed, a modest need."
      },
      "scores": {
        "anchoring": 3,
        "consequence": 3,
        "informativeness": 4,
        "linguistic_quality": 4,
        "practitioner_realism": 3
      }
    },
    "anchoring": 3,
    "consequence": 3,
    "informativeness": 4,
    "linguistic_quality": 4,
    "overall": 17,
    "practitioner_realism": 3,
    "reason": "practitioner_realism: Plausible but narrow: asks what a delegate reaffirmed, a modest need.; anchoring: Names the speaker and subject but gives no date or document/organ. The Special Committee and 16 June 2009 are missing, so the locator is weak for a known-source lookup.; consequence: Identifies a reaffirmed position of support, a generic statement of moderate specificity.; informativeness: The answer is complete and non-circular, giving support for the efforts of people under colonial rule to exercise self-determination, including independence.; linguistic_quality: Natural and clear wording."
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
      "candidate_id": "q_8769b09a1d0b4716c05a5ed2",
      "checks": {
        "metadata": "fail",
        "mode": "pass",
        "support": "pass"
      },
      "index": 2,
      "problems": [
        "anchoring: no date, organ or record type.",
        "informativeness: the answer's opening pronoun 'They' is unresolved within the span; the speaker identity and the referent come from the question and context.",
        "linguistic_quality: vague 'conditions for doing so' phrasing.",
        "metadata: the anchor is the question's own slot-like phrasing and gives no independent subject anchor that survives substitution."
      ],
      "score_notes": {
        "anchoring": "Names the speaker and Western Sahara, but has no date, organ or document type, so the locator is underspecified.",
        "consequence": "Gives a specific attributed position on who decides the future, though it is rhetorical.",
        "informativeness": "The answer 'They alone could decide...' starts with an unresolved pronoun, so 'they' (the people of Western Sahara) is unclear from the span alone. The substance is complete, but the pronoun needs the question or context to resolve it.",
        "linguistic_quality": "'the conditions for doing so' is awkward, and the question is somewhat double-barrelled.",
        "practitioner_realism": "Plausible, though the wording is vague about what is being sought."
      },
      "scores": {
        "anchoring": 3,
        "consequence": 3,
        "informativeness": 3,
        "linguistic_quality": 3,
        "practitioner_realism": 3
      }
    },
    "anchoring": 3,
    "consequence": 3,
    "informativeness": 3,
    "linguistic_quality": 3,
    "overall": 15,
    "practitioner_realism": 3,
    "reason": "practitioner_realism: Plausible, though the wording is vague about what is being sought.; anchoring: Names the speaker and Western Sahara, but has no date, organ or document type, so the locator is underspecified.; consequence: Gives a specific attributed position on who decides the future, though it is rhetorical.; informativeness: The answer 'They alone could decide...' starts with an unresolved pronoun, so 'they' (the people of Western Sahara) is unclear from the span alone. The substance is complete, but the pronoun needs the question or context to resolve it.; linguistic_quality: 'the conditions for doing so' is awkward, and the question is somewhat double-barrelled."
  }
]
````

### mode/un/2011/a/res/65/263#2/practitioner: faithfulness — completed

````json
[
  {
    "_response": {
      "grounding": 3,
      "index": 0,
      "numerical_fidelity": 5,
      "precision": 3,
      "reason": "The question asks what the commitments were. The answer quotes the preambular clause, which names the commitments only by reference and never states their content. The clause gives only the meeting, the reaffirmation and the determination to work together, so the question is not answered. The dates and places match the source. The clause text is faithful, but the question presumes content that the block does not supply."
    },
    "grounding": 3,
    "numerical_fidelity": 5,
    "overall": 11,
    "precision": 3,
    "reason": "The question asks what the commitments were. The answer quotes the preambular clause, which names the commitments only by reference and never states their content. The clause gives only the meeting, the reaffirmation and the determination to work together, so the question is not answered. The dates and places match the source. The clause text is faithful, but the question presumes content that the block does not supply."
  },
  {
    "_response": {
      "grounding": 4,
      "index": 1,
      "numerical_fidelity": 5,
      "precision": 4,
      "reason": "The clause is quoted accurately and states that substantial progress was noted with satisfaction. The question asks what progress, and the source gives no specifics. The answer is correct only at the level of the general statement, and the question's date framing is fine. The missing detail is a limitation of the source."
    },
    "grounding": 4,
    "numerical_fidelity": 5,
    "overall": 13,
    "precision": 4,
    "reason": "The clause is quoted accurately and states that substantial progress was noted with satisfaction. The question asks what progress, and the source gives no specifics. The answer is correct only at the level of the general statement, and the question's date framing is fine. The missing detail is a limitation of the source."
  },
  {
    "_response": {
      "grounding": 4,
      "index": 2,
      "numerical_fidelity": 5,
      "precision": 5,
      "reason": "The clause directly answers the question. It accurately lists the areas: peace, democratic governance and rule of law, economic governance and solidarity, environment, sustainable development, and climate change. The status as noted with satisfaction is preserved. The \"in 2011\" framing is slightly loose, since the resolution is dated 2011 but the commitment is not dated. This is minor."
    },
    "grounding": 4,
    "numerical_fidelity": 5,
    "overall": 14,
    "precision": 5,
    "reason": "The clause directly answers the question. It accurately lists the areas: peace, democratic governance and rule of law, economic governance and solidarity, environment, sustainable development, and climate change. The status as noted with satisfaction is preserved. The \"in 2011\" framing is slightly loose, since the resolution is dated 2011 but the commitment is not dated. This is minor."
  }
]
````

### mode/un/2011/a/res/65/263#2/practitioner: quality_index_recovery — completed

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
      "candidate_id": "q_276dd09b72897d670739d272",
      "checks": {
        "metadata": "fail",
        "mode": "pass",
        "support": "fail"
      },
      "index": 0,
      "problems": [
        "informativeness: the answer does not state the content of the commitments that the question asks for.",
        "support: the target span does not contain the requested substance, so the evidence is incomplete.",
        "metadata: question_type 'operative_action' is wrong for a preambular noting clause.",
        "metadata: the anchors are not verbatim substrings of the question, which says 'September 2010 Millennium Development Goals meeting' and not the anchor wording."
      ],
      "score_notes": {
        "anchoring_and_time": "September 2010, the MDG meeting and the Montreux summit of 22–24 October 2010 identify the event well. The body asserting the commitments is not named.",
        "consequence": "The target is a preambular recognition of unspecified commitments and a general determination. It gives no concrete norm, task or fact.",
        "informativeness": "The answer only says commitments were made and reaffirmed, with a determination to work together for 'added value in these areas'. It never states what the commitments were, so the question is not resolved.",
        "linguistic_quality": "The question is clear and grammatical, though it is slightly long.",
        "practitioner_realism": "The need to know what was committed at the 2010 MDG meeting and the Montreux summit is plausible but broad. The question is also phrased as if it asked for substantive content."
      },
      "scores": {
        "anchoring_and_time": 4,
        "consequence": 2,
        "informativeness": 2,
        "linguistic_quality": 4,
        "practitioner_realism": 3
      }
    },
    "anchoring_and_time": 4,
    "consequence": 2,
    "informativeness": 2,
    "linguistic_quality": 4,
    "overall": 15,
    "practitioner_realism": 3,
    "reason": "practitioner_realism: The need to know what was committed at the 2010 MDG meeting and the Montreux summit is plausible but broad. The question is also phrased as if it asked for substantive content.; anchoring_and_time: September 2010, the MDG meeting and the Montreux summit of 22–24 October 2010 identify the event well. The body asserting the commitments is not named.; consequence: The target is a preambular recognition of unspecified commitments and a general determination. It gives no concrete norm, task or fact.; informativeness: The answer only says commitments were made and reaffirmed, with a determination to work together for 'added value in these areas'. It never states what the commitments were, so the question is not resolved.; linguistic_quality: The question is clear and grammatical, though it is slightly long."
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
      "candidate_id": "q_a3a35943f28d4d7eabb1fb7a",
      "checks": {
        "metadata": "fail",
        "mode": "pass",
        "support": "fail"
      },
      "index": 1,
      "problems": [
        "informativeness: the answer is circular because it restates the question's premise and names no actual progress.",
        "anchoring_and_time: the question leans on the resolution's adoption date as a locator, not on substantive regime context.",
        "support: the target span does not contain the requested 'what progress' content.",
        "metadata: the anchor is not a verbatim substring of the question, which paraphrases it."
      ],
      "score_notes": {
        "anchoring_and_time": "It locates the text only by the resolution's adoption date (14 January 2011), which works as a document locator. The substantive context is thin and the body noting the progress is not named.",
        "consequence": "The target is a generic preambular expression of satisfaction. It has no concrete norm, task or fact.",
        "informativeness": "The answer repeats the question: 'substantial progress achieved in cooperation'. It gives no specifics of what the progress was, so the resolution is circular.",
        "linguistic_quality": "The wording is clear and natural.",
        "practitioner_realism": "The question mainly restates the target premise and does not reflect a real specialist information need."
      },
      "scores": {
        "anchoring_and_time": 3,
        "consequence": 2,
        "informativeness": 1,
        "linguistic_quality": 4,
        "practitioner_realism": 2
      }
    },
    "anchoring_and_time": 3,
    "consequence": 2,
    "informativeness": 1,
    "linguistic_quality": 4,
    "overall": 12,
    "practitioner_realism": 2,
    "reason": "practitioner_realism: The question mainly restates the target premise and does not reflect a real specialist information need.; anchoring_and_time: It locates the text only by the resolution's adoption date (14 January 2011), which works as a document locator. The substantive context is thin and the body noting the progress is not named.; consequence: The target is a generic preambular expression of satisfaction. It has no concrete norm, task or fact.; informativeness: The answer repeats the question: 'substantial progress achieved in cooperation'. It gives no specifics of what the progress was, so the resolution is circular.; linguistic_quality: The wording is clear and natural."
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
      "candidate_id": "q_8d08e42024612384482a0622",
      "checks": {
        "metadata": "fail",
        "mode": "pass",
        "support": "pass"
      },
      "index": 2,
      "problems": [
        "anchoring_and_time: '2011' is the document date, not the time of the commitment, and it confuses the time reference.",
        "metadata: the anchor is not a verbatim substring of the question, which contains only 'commitment of the International Organization of la Francophonie' and not the rest of the anchor."
      ],
      "score_notes": {
        "anchoring_and_time": "The organisation is named. The '2011' is only the resolution's adoption year and is not a meaningful time for the commitment, and the noting body (the General Assembly) is unstated.",
        "consequence": "The target lists concrete areas of cooperation, which is a useful fact. It is still a preambular expression of satisfaction and not an operative norm.",
        "informativeness": "The answer lists the areas of commitment (peace, governance, economic governance and solidarity, environment, sustainable development, climate change). That resolves the question, though the preambular framing adds little.",
        "linguistic_quality": "The wording 'regarding multilateral cooperation in 2011' is slightly awkward and misleading about the time.",
        "practitioner_realism": "A bounded, plausible question about the Francophonie's stated areas of multilateral cooperation."
      },
      "scores": {
        "anchoring_and_time": 3,
        "consequence": 3,
        "informativeness": 4,
        "linguistic_quality": 3,
        "practitioner_realism": 3
      }
    },
    "anchoring_and_time": 3,
    "consequence": 3,
    "informativeness": 4,
    "linguistic_quality": 3,
    "overall": 16,
    "practitioner_realism": 3,
    "reason": "practitioner_realism: A bounded, plausible question about the Francophonie's stated areas of multilateral cooperation.; anchoring_and_time: The organisation is named. The '2011' is only the resolution's adoption year and is not a meaningful time for the commitment, and the noting body (the General Assembly) is unstated.; consequence: The target lists concrete areas of cooperation, which is a useful fact. It is still a preambular expression of satisfaction and not an operative norm.; informativeness: The answer lists the areas of commitment (peace, governance, economic governance and solidarity, environment, sustainable development, climate change). That resolves the question, though the preambular framing adds little.; linguistic_quality: The wording 'regarding multilateral cooperation in 2011' is slightly awkward and misleading about the time."
  }
]
````

### mode/un/2013/a/res/68/18#1/lookup: faithfulness — completed

````json
[
  {
    "_response": {
      "grounding": 5,
      "index": 0,
      "numerical_fidelity": 5,
      "precision": 5,
      "reason": "The answer reproduces paragraph 1 verbatim and answers the question directly. The 2013 date follows from the resolution's number and the session context."
    },
    "grounding": 5,
    "numerical_fidelity": 5,
    "overall": 15,
    "precision": 5,
    "reason": "The answer reproduces paragraph 1 verbatim and answers the question directly. The 2013 date follows from the resolution's number and the session context."
  },
  {
    "_response": {
      "grounding": 5,
      "index": 1,
      "numerical_fidelity": 5,
      "precision": 4,
      "reason": "The answer matches paragraph 2: an exceptional additional six months before the three-year preparatory period. The clause about the ECOSOC endorsement is supporting context the question did not ask for, so it is slightly extra. The figures are correct."
    },
    "grounding": 5,
    "numerical_fidelity": 5,
    "overall": 14,
    "precision": 4,
    "reason": "The answer matches paragraph 2: an exceptional additional six months before the three-year preparatory period. The clause about the ECOSOC endorsement is supporting context the question did not ask for, so it is slightly extra. The figures are correct."
  },
  {
    "_response": {
      "grounding": 5,
      "index": 2,
      "numerical_fidelity": 5,
      "precision": 5,
      "reason": "The answer matches paragraph 3: the national smooth-transition strategy, prepared with UN system support and in cooperation with partners. It keeps the invitation status and gives the three and a half year period correctly."
    },
    "grounding": 5,
    "numerical_fidelity": 5,
    "overall": 15,
    "precision": 5,
    "reason": "The answer matches paragraph 3: the national smooth-transition strategy, prepared with UN system support and in cooperation with partners. It keeps the invitation status and gives the three and a half year period correctly."
  }
]
````

### mode/un/2013/a/res/68/18#1/lookup: quality_index_recovery — completed

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
      "candidate_id": "q_b0146c7659d2b3edd3f7f6e9",
      "checks": {
        "metadata": "pass",
        "mode": "pass",
        "support": "pass"
      },
      "index": 0,
      "problems": [
        "informativeness: the question echoes nearly all of the answer's substantive wording, making it partly circular.",
        "consequence: the answer is a general reaffirmation with little concrete content."
      ],
      "score_notes": {
        "anchoring": "The locator gives organ, year and a general topic ('graduation'). That is adequate but not sharply distinctive, since the year and topic are the only distinguishing anchors.",
        "consequence": "The answer states a general principle about non-disruption of development plans. It is moderately useful but not a concrete fact, figure or deadline.",
        "informativeness": "The question already contains 'disruption of development plans, programmes and projects', so the answer largely repeats it. Only the 'should not result in' relation is new, which makes it partly circular.",
        "linguistic_quality": "The wording is clear and natural. It is slightly long because it repeats the subject phrase.",
        "practitioner_realism": "Asking what a resolution reaffirmed about a general principle is plausible, but the need is fairly generic."
      },
      "scores": {
        "anchoring": 3,
        "consequence": 3,
        "informativeness": 3,
        "linguistic_quality": 4,
        "practitioner_realism": 3
      }
    },
    "anchoring": 3,
    "consequence": 3,
    "informativeness": 3,
    "linguistic_quality": 4,
    "overall": 16,
    "practitioner_realism": 3,
    "reason": "practitioner_realism: Asking what a resolution reaffirmed about a general principle is plausible, but the need is fairly generic.; anchoring: The locator gives organ, year and a general topic ('graduation'). That is adequate but not sharply distinctive, since the year and topic are the only distinguishing anchors.; consequence: The answer states a general principle about non-disruption of development plans. It is moderately useful but not a concrete fact, figure or deadline.; informativeness: The question already contains 'disruption of development plans, programmes and projects', so the answer largely repeats it. Only the 'should not result in' relation is new, which makes it partly circular.; linguistic_quality: The wording is clear and natural. It is slightly long because it repeats the subject phrase."
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
      "candidate_id": "q_808d4c05764f87707686060b",
      "checks": {
        "metadata": "pass",
        "mode": "pass",
        "support": "pass"
      },
      "index": 1,
      "problems": [],
      "score_notes": {
        "anchoring": "The locator names the organ and year (General Assembly, 2013) and the country, Equatorial Guinea. This pins down paragraph 2 accurately.",
        "consequence": "The answer is a concrete, useful interval: six months added before the three-year preparatory period.",
        "informativeness": "The answer span gives the six-month additional period and its relation to the three-year preparatory period. It also keeps the 'exceptional basis' qualifier. The question does not leak the figure.",
        "linguistic_quality": "The question is clear. 'Exceptional preparatory timing' is slightly awkward.",
        "practitioner_realism": "Asking what extra preparatory period a specific country received is a realistic, bounded need."
      },
      "scores": {
        "anchoring": 5,
        "consequence": 4,
        "informativeness": 5,
        "linguistic_quality": 4,
        "practitioner_realism": 5
      }
    },
    "anchoring": 5,
    "consequence": 4,
    "informativeness": 5,
    "linguistic_quality": 4,
    "overall": 23,
    "practitioner_realism": 5,
    "reason": "practitioner_realism: Asking what extra preparatory period a specific country received is a realistic, bounded need.; anchoring: The locator names the organ and year (General Assembly, 2013) and the country, Equatorial Guinea. This pins down paragraph 2 accurately.; consequence: The answer is a concrete, useful interval: six months added before the three-year preparatory period.; informativeness: The answer span gives the six-month additional period and its relation to the three-year preparatory period. It also keeps the 'exceptional basis' qualifier. The question does not leak the figure.; linguistic_quality: The question is clear. 'Exceptional preparatory timing' is slightly awkward."
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
      "candidate_id": "q_1057f40949b32c962ebb8c7d",
      "checks": {
        "metadata": "fail",
        "mode": "pass",
        "support": "pass"
      },
      "index": 2,
      "problems": [
        "metadata: the anchor 'national smooth-transition strategy' does not appear in the question text, so it is not a base-question substring outside the slot. It is also the answer content."
      ],
      "score_notes": {
        "anchoring": "The locator gives the General Assembly, 2013, Equatorial Guinea and the pre-graduation period. It is accurate, though 'during the period before graduation' is a little loose.",
        "consequence": "The answer is a specific deliverable (a national smooth-transition strategy) with its timeframe and support arrangements.",
        "informativeness": "The answer fully resolves the question. It names the strategy, the three-and-a-half-year period and the UN-system support, and it keeps the 'invites' modality.",
        "linguistic_quality": "The question is clear and natural.",
        "practitioner_realism": "Asking what the country is invited to prepare is a plausible need about the transition requirements."
      },
      "scores": {
        "anchoring": 4,
        "consequence": 4,
        "informativeness": 5,
        "linguistic_quality": 4,
        "practitioner_realism": 4
      }
    },
    "anchoring": 4,
    "consequence": 4,
    "informativeness": 5,
    "linguistic_quality": 4,
    "overall": 21,
    "practitioner_realism": 4,
    "reason": "practitioner_realism: Asking what the country is invited to prepare is a plausible need about the transition requirements.; anchoring: The locator gives the General Assembly, 2013, Equatorial Guinea and the pre-graduation period. It is accurate, though 'during the period before graduation' is a little loose.; consequence: The answer is a specific deliverable (a national smooth-transition strategy) with its timeframe and support arrangements.; informativeness: The answer fully resolves the question. It names the strategy, the three-and-a-half-year period and the UN-system support, and it keeps the 'invites' modality.; linguistic_quality: The question is clear and natural."
  }
]
````
