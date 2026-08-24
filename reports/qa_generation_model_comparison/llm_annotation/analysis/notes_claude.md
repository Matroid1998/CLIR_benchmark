# Claude Fable 5 — document notes and per-question reasons

30 of 30 documents carry a shared note. Q1–Q6 refer to the randomised slots this annotator saw; resolved to models below.

## EP-4504821-A1  ·  technical mode  ·  question language: es

> All six answers are faithful to the passage; the problem is specificity. Q1, Q2, Q4 are near-identical questions about variable b, and Q5 about k1, with no subject anchoring — they would match any patent defining such variables. Q3 is the strongest; Q6 is acceptable. Several answers are in English or mixed Spanish/English despite the Spanish question language.

- **Q1 · grok-4.3** (DISCARDED, faith 5.00, quality 2.75, ling 5): ¿Qué valores puede tomar b?  
  — *0 o un entero de 1 a 500*  
  reason: Answer is exact, but 'what values can b take' has no anchoring context at all and would match countless patents with a variable b.
- **Q2 · qwen3.6-35b-a3b** (DISCARDED, faith 5.00, quality 2.75, ling 5): ¿Cuáles son los valores permitidos para b?  
  — *0 or an integer from 1 to 500*  
  reason: Correct answer (in English rather than Spanish), but the question is context-free and cannot narrow retrieval to this document.
- **Q3 · sonnet-4.6** (kept, faith 5.00, quality 4.25, ling 4): ¿Cuántos átomos de carbono puede tener el resto R2 en la fórmula de los organopolysiloxanos preentrecruzados?  
  — *3 to 18 carbon atoms*  
  reason: Accurate 3-18 range, anchored to R2 in pre-crosslinked organopolysiloxanes, which makes it a plausible and reasonably specific query despite the Spanish-English term mix in the question.
- **Q4 · gpt-5.4-mini** (DISCARDED, faith 5.00, quality 2.75, ling 5): ¿Qué valores puede tomar b?  
  — *0 o un número entero de 1 to 500*  
  reason: Duplicate of Q1 with a mixed-language answer ('1 to 500'); faithful but entirely unanchored and unspecific.
- **Q5 · gpt-5-mini** (DISCARDED, faith 5.00, quality 2.75, ling 5): ¿Qué valores puede tener k1?  
  — *k1 is 0, 1, 2 or 3*  
  reason: Answer matches the passage exactly, but asking for the values of k1 with no subject context makes the question useless for retrieval.
- **Q6 · gemini-3.5-flash** (kept, faith 5.00, quality 3.75, ling 4): ¿Cuál es el rango de átomos de carbono permitido para el grupo R 2 bivalente?  
  — *3 to 18*  
  reason: Correct 3-18 range and some anchoring via 'divalent R2 group', though it lacks the organopolysiloxane context that would make it more discriminative.

## EP-4577789-A1  ·  technical mode  ·  question language: zh

> Five of six questions target the same fact (cooling gas duct 44 from cooling zone 22 to preheating zone 21); Q3 and Q6 are near-duplicates. Only Q4 covers a different fact. Q2 is the strongest overall for search realism and specificity; Q5 is tautological.

- **Q1 · grok-4.3** (kept, faith 4.67, quality 3.00, ling 5): 冷却气体如何从冷却区引导至预热区？  
  — *经由冷气管道 (44) 被引导至预热区 (21)*  
  reason: Answer is lifted directly from the ZH abstract with slight redundancy (repeats the destination), and the question largely reuses source wording without naming the kiln type.
- **Q2 · gemini-3.5-flash** (kept, faith 5.00, quality 4.00, ling 5): 冷却气体经由管道被引导至并流蓄热式竖窑的哪个区域？  
  — *预热区 (21)*  
  reason: Clean single-fact question that names the PFR shaft kiln, with a minimal exact answer (预热区 (21)).
- **Q3 · qwen3.6-35b-a3b** (kept, faith 5.00, quality 3.75, ling 5): 冷却气体管道连接竖窑内的哪两个区域？  
  — *从冷却区 (22) 引导至预热区 (21)*  
  reason: Well-paraphrased query about the duct's endpoints; answer is exact, though it asks for a pair rather than a single item and lacks kiln-type context.
- **Q4 · sonnet-4.6** (kept, faith 4.67, quality 3.75, ling 5): PFR竖窑中废气通过哪个出口排出？  
  — *废气经由排气出口 (6) 从其中一个竖井 (2) 排出*  
  reason: Grounded and the only question on a different fact (waste gas outlet), but the answer adds the 'from one of the shafts' clause and the fact itself is generic to shaft kilns.
- **Q5 · gpt-5-mini** (DISCARDED, faith 5.00, quality 3.25, ling 5): 冷却气体由哪个管道引导至预热区？  
  — *冷却气体管道 (44)*  
  reason: Nearly tautological — asking which duct conducts the cooling gas and answering 'cooling gas duct' yields little discriminative value as a benchmark question.
- **Q6 · gpt-5.4-mini** (kept, faith 5.00, quality 3.50, ling 4): 冷却气体管道把冷却气体从哪里引导到哪里？  
  — *从冷却区 (22) 引导至预热区 (21)*  
  reason: Correct and paraphrased, but colloquial '从哪里...到哪里' phrasing is less search-like and it is effectively a duplicate of Q3.

## EP-4584229-A1  ·  technical mode  ·  question language: es

> All six questions target the same fact (definition/carbon count of R in R-NR'H); none asks about the distinctive features of the patent (vinyl acetate-ethylene dispersion powder, amino compound classes, epoxide exclusion). Q2 is the only one adding document-specific context.

- **Q1 · gemini-3.5-flash** (kept, faith 5.00, quality 3.50, ling 5): ¿Cuántos átomos de carbono tiene el grupo hidrocarbonado R en la fórmula R-NR'H?  
  — *1 to 20*  
  reason: Answer exact and focused, but the generic R-NR'H carbon range is weakly discriminative across patents.
- **Q2 · sonnet-4.6** (kept, faith 5.00, quality 3.50, ling 3): ¿Qué representa el grupo R en la fórmula R-NR'H de los amino compounds utilizados en composiciones de polvos de dispersión?  
  — *a linear or branched and optionally substituted hydrocarbon group with 1 to 20 carbon atoms*  
  reason: Most specific question thanks to the dispersion-powder context, though the untranslated 'amino compounds' mars the Spanish.
- **Q3 · gpt-5.4-mini** (DISCARDED, faith 5.00, quality 3.75, ling 3): ¿Qué rango de carbonos tiene R en R-NR'H?  
  — *1 to 20 carbon atoms*  
  reason: Telegraphic and vague ('rango de carbonos'), no document context, and near-duplicate of Q1/Q4.
- **Q4 · qwen3.6-35b-a3b** (kept, faith 5.00, quality 3.50, ling 5): ¿Cuál es el rango de átomos de carbono definido para el grupo R en la fórmula R-NR'H?  
  — *1 to 20 carbon atoms*  
  reason: Faithful and well-formed but generic and redundant with Q1.
- **Q5 · grok-4.3** (DISCARDED, faith 5.00, quality 3.25, ling 4): ¿Qué representa el resto R en la fórmula R-NR'H?  
  — *un linear or branched, optionally substituted hydrocarbon group con 1 to 20 carbon atoms*  
  reason: Answer is a Spanish/English mash-up ('un ... con') and the question lacks any discriminative context.
- **Q6 · gpt-5-mini** (DISCARDED, faith 5.00, quality 3.00, ling 5): ¿Qué representa R en la fórmula R-NR'H?  
  — *a linear or branched and optionally substituted hydrocarbon group with 1 to 20 carbon atoms*  
  reason: Faithful but maximally generic: R in R-NR'H without any context would match countless amine patents.

## EP-4627127-A1  ·  technical mode  ·  question language: de

> The passage is a short abstract with no numbers, so numerical fidelity is 5 throughout and all answers are grounded. The main weakness across questions is low specificity: Q2/Q4/Q5/Q6 could match many aluminum-alloy patents. Q1 and Q3 are near-duplicates (Q3 has an English answer despite a German question). Q6 is the strongest of the set.

- **Q1 · gemini-3.5-flash** (kept, faith 5.00, quality 3.50, ling 5): Für welche Art von Komponenten ist die formbare, korrosionsbeständige Aluminiumlegierung vorgesehen?  
  — *Strukturbauteile*  
  reason: Answer 'Strukturbauteile' matches the title's 'structural component'; question is a single fact but phrased conversationally rather than as a search query, and somewhat generic.
- **Q2 · grok-4.3** (kept, faith 5.00, quality 2.75, ling 5): Welche Verarbeitungsschritte werden bei Aluminiumlegierungsprodukten durchgeführt?  
  — *Gießen einer Aluminiumlegierung und Durchführung von maßgeschneidertem Walzen und nachgelagerten thermischen Verarbeitungsschritten*  
  reason: Answer is an accurate translation of the abstract's processing steps, but the question is very generic (could match countless aluminum alloy patents) and asks for a multi-part list.
- **Q3 · sonnet-4.6** (DISCARDED, faith 5.00, quality 3.50, ling 4): Für welchen Anwendungsbereich sind diese formbaren, korrosionsbeständigen Aluminiumlegierungen vorgesehen?  
  — *structural component*  
  reason: Grounded, but the answer is in English while the question is German, 'diese' makes the question deictic and not standalone, and it duplicates Q1.
- **Q4 · gpt-5.4-mini** (DISCARDED, faith 5.00, quality 2.75, ling 5): Welcher Werkstoff wird gegossen?  
  — *eine Aluminiumlegierung*  
  reason: Trivially grounded but entirely non-specific — 'which material is cast?' would match essentially any casting patent and cannot retrieve this document.
- **Q5 · gpt-5-mini** (DISCARDED, faith 5.00, quality 2.75, ling 5): Welche Festigkeit weisen die resultierenden Aluminiumlegierungsprodukte auf?  
  — *hohe Festigkeit*  
  reason: Answer 'hohe Festigkeit' is supported, but the question is vacuous (asks for a strength value and gets 'high'), generic, and useless for retrieval.
- **Q6 · qwen3.6-35b-a3b** (kept, faith 5.00, quality 3.50, ling 5): Welche Verarbeitungsschritte folgen auf das Gießen bei der Herstellung der Aluminiumlegierungsprodukte?  
  — *angepasstes Walzen und nachgelagerte Wärmebehandlungsschritte*  
  reason: Accurately grounded answer ('tailored rolling and downstream thermal processing'), better paraphrased and more specific than Q2 by anchoring on the post-casting steps, though still fairly generic.

## EP-4627881-A1  ·  semantic mode  ·  question language: zh

> The passage is an abstract-only record with very little substantive content, so all questions are limited to the device/unit/plant/method structure. Q2 is the strongest; Q1 and Q4 introduce premises absent from the source.

- **Q1 · gemini-3.5-flash** (DISCARDED, faith 4.33, quality 3.00, ling 3): 当单一喷嘴所提供的电离气体束能效不足时，可以采用什么方案将多套发生装置集结协同运作？  
  — *Plasmaerzeugungseinrichtung (100) 包含多个 Vorrichtungen (10, 10a, 10b)*  
  reason: The premise ('when a single nozzle's ionised gas beam is insufficient') and the terms nozzle/ionised gas beam are invented and not in the passage, the query is contrived, and the answer awkwardly mixes German terms with Chinese.
- **Q2 · grok-4.3** (kept, faith 5.00, quality 4.00, ling 5): 工业熔化设备中实现多等离子体火焰供应的系统如何构建？  
  — *a plasma generation unit (100) comprising a plurality of devices (10, 10a, 10b)*  
  reason: Natural, fluent query about constructing a multi-plasma-flame system for melting plants, with an answer extracted verbatim from the EN abstract.
- **Q3 · gpt-5.4-mini** (kept, faith 5.00, quality 3.00, ling 4): 如果要把多个等离子火焰发生装置组合起来，相关的等离子生成单元是怎样构成的？  
  — *eine Plasmaerzeugungseinrichtung (100) umfassend mehrere Vorrichtungen (10, 10a, 10b)*  
  reason: Reasonable paraphrase of the plasma generation unit concept with a verbatim German answer span, though it is somewhat wordy and close to the source wording.
- **Q4 · qwen3.6-35b-a3b** (DISCARDED, faith 4.00, quality 3.00, ling 4): 面对连续化生产要求，如何将独立的小型发生器集成到完整产线中？  
  — *包含多个上述发生装置的等离子体发生单元*  
  reason: The question's framing (continuous production, small generators, complete production line) is not in the passage and is too generic to retrieve it, even though the answer itself is a fair Chinese rendering of the plasma generation unit.
- **Q5 · sonnet-4.6** (kept, faith 5.00, quality 3.50, ling 5): 有没有一种统一的控制方法，可以同时适用于单台等离子体发生器和整套高温熔融系统？  
  — *一种用于操作此类设备（10, 10a, 10b）、此类等离子体发生装置（100）或此类高温工艺设备（尤其是熔融装置（26））的方法*  
  reason: Fluent conceptual query about an operating method spanning single devices and the whole melting plant, with a faithful Chinese translation of the passage's method clause; 'unified control' is a slight stretch of 'operating method'.
- **Q6 · gpt-5-mini** (DISCARDED, faith 5.00, quality 2.75, ling 5): 有哪些专用硬件可以直接生成工业用等离子体火焰？  
  — *用于生成至少一种等离子体火焰(12)的装置(10, 10a, 10b)。*  
  reason: Fluent but extremely generic ('what hardware generates industrial plasma flames') and would match countless plasma torch documents; answer is faithful but trivial.

## EP-4630021-A1  ·  technical mode  ·  question language: de

> Q1 and Q3 ask essentially the same fact (properties of the injectable); Q4 and Q5 duplicate each other (placental-derived materials). Q4/Q5 are the strongest; Q1 and Q2 are too generic to retrieve this patent.

- **Q1 · gpt-5.4-mini** (DISCARDED, faith 5.00, quality 2.75, ling 5): Welche Eigenschaften hat das flüssige Injektionsprodukt?  
  — *clear, safe, and physiologically and biologically active*  
  reason: Answer is exact, but 'Welche Eigenschaften hat das flüssige Injektionsprodukt' lacks any equine/placental anchor and would match countless injectable documents.
- **Q2 · qwen3.6-35b-a3b** (DISCARDED, faith 5.00, quality 3.50, ling 5): Welche Komponenten bleiben nach der Aufbereitung des Injektionsprodukts erhalten?  
  — *postbiotics, proteins, exosomes, biocomponents*  
  reason: Answer list is exact and the question is well paraphrased, but 'Injektionsprodukt' alone gives no equine/amnion/placenta cue, so it barely narrows to this patent.
- **Q3 · grok-4.3** (kept, faith 5.00, quality 3.75, ling 5): Welche Eigenschaften besitzt das produzierte Amnion- und Fruchtwasser-Injektionsprodukt?  
  — *clear, safe, and physiologically and biologically active liquid injectable*  
  reason: Names the amnion/amniotic-fluid injectable explicitly so it targets this document, and the answer is an exact span.
- **Q4 · gpt-5-mini** (kept, faith 5.00, quality 4.25, ling 5): Welche Materialien enthalten die equinen therapeutischen Zusammensetzungen?  
  — *Plazenta-abgeleitete Materialien*  
  reason: Concise, specific query combining equine and therapeutic compositions; answer (placental-derived materials) is directly supported.
- **Q5 · gemini-3.5-flash** (kept, faith 5.00, quality 4.50, ling 4): Aus welchen Ausgangsstoffen werden pferdespezifische therapeutische Zusammensetzungen hergestellt?  
  — *aus der Plazenta gewonnenen Materialien*  
  reason: Good paraphrase ('Ausgangsstoffe', 'pferdespezifisch') with a faithful answer; answer phrase 'aus der Plazenta gewonnenen Materialien' is slightly ungrammatical standalone.
- **Q6 · sonnet-4.6** (kept, faith 5.00, quality 3.75, ling 5): Was wird bei der Verarbeitung von eingehendem plazentaren Gewebe und Fluid mit Verfärbungen und Verunreinigungen als Endprodukt erzeugt?  
  — *a clear amnion and amniotic fluid injectable product*  
  reason: Highly specific and faithfully answered, but the long, near-translated sentence reads more like a comprehension question than a search-bar query.

## EP-4633645-A1  ·  technical mode  ·  question language: fr

> All six questions target the same single fact (elevated Ubiquitin Ser65 phosphorylation) from a short abstract, so they are near-duplicates; Q6 stands out as the most retrieval-realistic, while Q1 and Q5 leak the answer terms in the question.

- **Q1 · grok-4.3** (DISCARDED, faith 5.00, quality 2.75, ling 4): Quel niveau de phosphorylation de l'ubiquitine Ser65 caractérise les maladies neurodégénératives traitées ?  
  — *niveau élevé*  
  reason: Answer is exact, but the question gives away the key terms and asks only for a trivial qualifier ('élevé'), reading more like a cloze test than a search query.
- **Q2 · gpt-5.4-mini** (kept, faith 5.00, quality 3.25, ling 5): Quelle caractéristique de phosphorylation est associée aux maladies neurodégénératives visées ?  
  — *un niveau élevé de phosphorylation de l'ubiquitine Ser65*  
  reason: Faithful answer and a reasonably paraphrased, single-fact question, though 'caractéristique de phosphorylation' is somewhat vague and only weakly anchored to this patent.
- **Q3 · gpt-5-mini** (kept, faith 4.67, quality 3.25, ling 4): Quel site de phosphorylation de l'ubiquitine est élevé dans les maladies neurodégénératives ?  
  — *phosphorylation de l'ubiquitine Ser65*  
  reason: Supported and focused, but the answer ('phosphorylation de l'ubiquitine Ser65') slightly mismatches the question asking for the site (Ser65) and the question already reveals most of the answer terms.
- **Q4 · qwen3.6-35b-a3b** (kept, faith 5.00, quality 3.50, ling 5): Quelle modification biochimique spécifique est élevée dans les affections neurodégénératives ciblées ?  
  — *un niveau élevé de phosphorylation de l'ubiquitine Ser65*  
  reason: Well-paraphrased single-fact question with an exact answer, though 'affections neurodégénératives ciblées' alone does not strongly narrow to this document.
- **Q5 · gemini-3.5-flash** (DISCARDED, faith 5.00, quality 3.00, ling 4): Quel état de l'ubiquitine Ser65 caractérise les pathologies neurodégénératives ciblées ?  
  — *un niveau élevé de phosphorylation de l'ubiquitine Ser65*  
  reason: Answer is faithful, but 'Quel état de l'ubiquitine Ser65' is an unnatural formulation that leaks the key term and reads poorly as a search query.
- **Q6 · sonnet-4.6** (kept, faith 5.00, quality 4.00, ling 5): Quel marqueur biologique caractérise les maladies neurodégénératives traitées par les composés de formule (I) ?  
  — *Un niveau élevé de phosphorylation de l'ubiquitine Ser65*  
  reason: Best of the set: faithful answer, natural paraphrase ('marqueur biologique'), and the reference to compounds of formula (I) anchors the query to this patent without leaking the answer.

## EP-4633791-A1  ·  semantic mode  ·  question language: zh

> The passage is only an abstract with no technical detail, so all answers are limited to the product-application or 'new process' sentences; Q2 stands out for conceptual framing, Q3 is too vague to retrieve, and Q2's answer is in French while the question is Chinese.

- **Q1 · grok-4.3** (kept, faith 4.67, quality 3.50, ling 4): 蛋白质基微胶囊适合加入到哪些家用或个人护理产品中发挥作用？  
  — *香味组合物和包含所述微胶囊的消费产品，特别是以家用护理或个人护理产品形式存在的香味消费产品*  
  reason: Answer is a faithful rendering of the abstract's application sentence; question is a plausible query naming protein microcapsules and home/personal care, though fairly close to the passage wording.
- **Q2 · sonnet-4.6** (kept, faith 5.00, quality 4.75, ling 5): 有没有一种不依赖合成聚合物壳材、利用天然生物大分子封装香料的微囊化技术？  
  — *La présente invention concerne un nouveau procédé de préparation de microcapsules à base de protéines*  
  reason: Strongly paraphrased, concept-level query (natural biomacromolecule vs synthetic shell) that maps well to protein-based fragrance microcapsules; answer is a verbatim French span, though the 'no synthetic polymer' contrast is the asker's framing rather than stated in the passage.
- **Q3 · gpt-5.4-mini** (DISCARDED, faith 5.00, quality 2.25, ling 3): 这类带香味的消费品更偏向哪些日常护理场景？  
  — *家居护理或个人护理产品*  
  reason: Answer is correct, but the question is anaphoric ('这类') and generic, with awkward phrasing ('更偏向'), so it would not retrieve this passage over any other perfumed-product document.
- **Q4 · qwen3.6-35b-a3b** (kept, faith 4.00, quality 3.75, ling 4): 家用清洁或个人洗护产品如何通过微囊化技术整合香氛成分？  
  — *含有所述微胶囊的香调组合物以及包含这些微胶囊的消费产品，尤其是以家庭护理或个人护理产品形式出现的含香消费产品。*  
  reason: Good conceptual query about integrating fragrance into household/personal care products via microencapsulation, but the passage gives no 'how', so the answer merely restates the product list and only loosely answers the question.
- **Q5 · gpt-5-mini** (kept, faith 4.67, quality 2.75, ling 4): 有哪些新的工艺可用于制备以蛋白质为基础的微胶囊？  
  — *一种制备蛋白质基微胶囊的新工艺。*  
  reason: Faithful and retrieves the document well, but the question nearly mirrors the abstract wording and the answer is circular ('a new process') with no substantive content.
- **Q6 · gemini-3.5-flash** (kept, faith 5.00, quality 3.50, ling 4): 这种微包裹体通常适用于哪些类型的加香日化产品？  
  — *家庭护理或个人护理产品形式的加香消费品*  
  reason: Well paraphrased ('微包裹体', '加香日化产品') and the answer is exactly supported, though the demonstrative '这种' makes it somewhat context-dependent as a standalone query.

## EP-4634436-A1  ·  semantic mode  ·  question language: fr

> Q2, Q5 and Q6 target the identical answer span (inert gas injection at anode and cathode); Q2 is the strongest of the three. Q3 introduces unsupported premises; Q4 is too generic to retrieve.

- **Q1 · gpt-5-mini** (kept, faith 4.67, quality 3.25, ling 5): Quelle action est entreprise si, après le remplacement initial, le contrôle détecte encore des cellules endommagées ?  
  — *lorsqu'un résultat du deuxième test indique qu'il reste la ou les autres cellules endommagées, l'arrêt de l'électrolyseur et la répétition de l'exécution du ou des premiers tests, le remplacement de la ou des cellules, et l'exécution du deuxième test,*  
  reason: Answer is a verbatim span matching the conditional step; question is well paraphrased but reads more like a comprehension question than a retrieval query and is somewhat generic.
- **Q2 · sonnet-4.6** (kept, faith 5.00, quality 4.50, ling 5): Comment l'injection de gaz inertes côté anode et côté cathode peut-elle être exploitée pour diagnostiquer l'intégrité des séparateurs dans un système d'électrolyse ?  
  — *au moins l'un du ou des premiers tests sur la base d'une injection de gaz inertes au niveau d'une anode et au niveau d'une cathode de chaque cellule*  
  reason: Conceptual, fluent query with good paraphrase (séparateurs/intégrité) that targets the passage's distinctive inert-gas anode/cathode injection idea; answer span is exact.
- **Q3 · qwen3.6-35b-a3b** (DISCARDED, faith 4.33, quality 4.25, ling 5): Quelle technique permet de localiser les membranes fissurées au sein d'un électrolyseur sans démonter l'ensemble de la pile ?  
  — *l'injection de gaz inertes au niveau d'une anode et au niveau d'une cathode de chaque cellule*  
  reason: Question adds claims not in the passage ('fissurées', 'sans démonter l'ensemble de la pile') and localisation is not what the test is said to do, so the question premise is partly unsupported.
- **Q4 · gemini-3.5-flash** (DISCARDED, faith 5.00, quality 3.50, ling 5): Quel protocole de validation applique-t-on suite à la substitution de composants détériorés pour garantir l'absence de pannes résiduelles ?  
  — *l'exécution d'un deuxième test pour évaluer s'il reste au moins une autre cellule endommagée*  
  reason: Heavily paraphrased and accurate, but so abstracted (components, faults, validation protocol) that it would match countless maintenance documents and not retrieve this electrolyzer passage.
- **Q5 · gpt-5.4-mini** (kept, faith 5.00, quality 3.75, ling 5): Quelle stratégie de vérification utilise une injection de gaz inertes des deux côtés d'une cellule pour confirmer une cellule défectueuse ?  
  — *au moins l'un du ou des premiers tests sur la base d'une injection de gaz inertes au niveau d'une anode et au niveau d'une cathode de chaque cellule*  
  reason: Accurate and retrievable, though it keeps much of the source vocabulary and is close to a fact lookup; near-duplicate of Q2/Q6 on the same span.
- **Q6 · grok-4.3** (kept, faith 5.00, quality 4.25, ling 4): Comment des gaz inertes injectés aux deux pôles d'une cellule peuvent-ils servir à valider l'existence réelle de membranes défectueuses ?  
  — *au moins l'un du ou des premiers tests sur la base d'une injection de gaz inertes au niveau d'une anode et au niveau d'une cathode de chaque cellule*  
  reason: Conceptual and well grounded, but 'pôles' is an odd substitute for anode/cathode and 'valider l'existence réelle' is slightly awkward, lowering realism.

## MX-2025002756-A  ·  technical mode  ·  question language: en

> All six answers are exact extractions from the abstract; the questions split into three pairs (Cu: Q1/Q5, Pb: Q2/Q4, Mn: Q3/Q6). Q1 stands out for adding discriminative context; Q4 and Q5 are weakened by the bare 'the alloy' reference.

- **Q1 · gemini-3.5-flash** (kept, faith 5.00, quality 4.50, ling 5): What is the copper weight percent range in a lead-free brass alloy containing manganese and silicon?  
  — *59 to 62 wt %*  
  reason: Exact answer, and the Mn/Si qualifiers make the query discriminative among lead-free brass patents.
- **Q2 · sonnet-4.6** (kept, faith 5.00, quality 4.00, ling 4): What is the maximum allowable Pb content in lead-free brass alloy?  
  — *less than 0.1 wt % Pb*  
  reason: Faithful and concise, though Pb limits in lead-free brass are a common claim so it only moderately narrows the search.
- **Q3 · grok-4.3** (kept, faith 5.00, quality 4.00, ling 5): What is the manganese content range in the lead-free brass alloy?  
  — *2.0 to 2.5 wt % Mn*  
  reason: Accurate and focused, but 'the lead-free brass alloy' alone does not strongly distinguish this document.
- **Q4 · qwen3.6-35b-a3b** (DISCARDED, faith 5.00, quality 3.50, ling 5): What is the maximum allowable lead content in the alloy?  
  — *less than 0.1 wt %*  
  reason: Answer is correct but 'the alloy' is unanchored, so the query would match countless lead-limited alloy documents.
- **Q5 · gpt-5-mini** (DISCARDED, faith 5.00, quality 3.50, ling 5): What is the weight percent range of Cu in the alloy?  
  — *59 to 62 wt % Cu*  
  reason: Correct answer, but 'the alloy' gives no context (not even brass or lead-free), making it arbitrary as a retrieval query.
- **Q6 · gpt-5.4-mini** (kept, faith 5.00, quality 3.75, ling 3): What Mn content range is in the lead-free brass alloy?  
  — *2.0 to 2.5 wt % Mn*  
  reason: Faithful near-duplicate of Q3 with slightly awkward phrasing ('What Mn content range is in'), acceptable but weaker.

## MX-2025004470-A  ·  semantic mode  ·  question language: en

> Q1, Q3, Q4, Q5 and Q6 all target the same fact (electrical heating element inside the reactor); Q6 is the stand-out for distinguishing the passage, Q5 overstates what the abstract says.

- **Q1 · gpt-5-mini** (kept, faith 4.33, quality 4.00, ling 5): What in-reactor heating strategy is used together with a catalyst to carry out the dehydrogenation reaction?  
  — *feeding the heated paraffinic feedstock to a first dehydrogenation reactor operating in a reaction mode and containing an active dehydrogenation catalyst and at least one first electrical heating element, heating the heated paraffinic feedstock in the first dehydrogenation reactor using the at least one first electrical heating element*  
  reason: Good conceptual paraphrase of the in-reactor electrical heating idea; answer is verbatim but includes the feeding step, which is padding relative to the question.
- **Q2 · gpt-5.4-mini** (kept, faith 5.00, quality 3.50, ling 5): How is a paraffinic feedstock brought up to dehydrogenation temperature before entering the reactor?  
  — *combusting the fuel gas stream in the dehydrogenation reactor preheater and heating the paraffinic hydrocarbon feedstock to a temperature in the range of 500-650Â°C*  
  reason: Clean answer on the preheater combustion step with exact 500-650°C, but fired preheating before a dehydrogenation reactor is generic and less distinctive than the electric-heating novelty.
- **Q3 · grok-4.3** (kept, faith 4.67, quality 4.25, ling 5): How can electric heating be combined with catalysis inside a dehydrogenation reactor?  
  — *heating the heated paraffinic feedstock in the first dehydrogenation reactor using the at least one first electrical heating element, and contacting the heated paraffinic feedstock with the active dehydrogenation catalyst and the at least one electrical heating element thereby producing an olefinic product stream comprising one or more olefins.*  
  reason: Concept-oriented question on combining electric heating with catalysis that targets the passage's core idea; answer is a contiguous span with slight tail padding about the product stream.
- **Q4 · gemini-3.5-flash** (kept, faith 4.67, quality 4.25, ling 5): How does the reaction vessel design counteract temperature drop during the endothermic conversion process?  
  — *heating the heated paraffinic feedstock in the first dehydrogenation reactor using the at least one first electrical heating element*  
  reason: Strongly paraphrased and plausible, though 'counteract temperature drop' and 'endothermic' are inferred framing not stated in the passage, so the link to the answer is slightly indirect.
- **Q5 · qwen3.6-35b-a3b** (DISCARDED, faith 4.33, quality 3.50, ling 5): How is precise thermal regulation maintained inside the catalytic reaction zone during paraffin conversion?  
  — *heating the heated paraffinic feedstock in the first dehydrogenation reactor using the at least one first electrical heating element*  
  reason: 'Precise thermal regulation' is not something the passage claims—it only says an electrical element heats the feed—so the question overreaches and is too generic to single out this document.
- **Q6 · sonnet-4.6** (kept, faith 4.33, quality 4.50, ling 5): How can electrical heating elements be integrated inside a catalytic dehydrogenation reactor to supplement upstream combustion-based preheating?  
  — *feeding the heated paraffinic feedstock to a first dehydrogenation reactor operating in a reaction mode and containing an active dehydrogenation catalyst and at least one first electrical heating element, heating the heated paraffinic feedstock in the first dehydrogenation reactor using the at least one first electrical heating element*  
  reason: Best retrievability: captures both the combustion preheater and in-reactor electric elements, uniquely matching this passage; answer span includes the feeding step as mild padding.

## MX-2025005046-A  ·  semantic mode  ·  question language: de

> All six answers are faithful to the abstract. Q3, Q5 and Q6 target the same magnetic-ring sentence, and Q1/Q2 both cover the combined UV+magnet mechanism, so there is substantial redundancy; Q2 and Q5 are the strongest.

- **Q1 · qwen3.6-35b-a3b** (kept, faith 5.00, quality 4.25, ling 4): Wie lässt sich die Bildung langlebiger reaktiver Sauerstoffspezies in einem belüfteten Reinigungssystem physikalisch optimieren?  
  — *Die UV-Strahlungsreflexionsabdeckung ist so ausgelegt, um die Wechselwirkung der UV-Strahlung mit Sauerstoffmolekülen in der einströmenden Luft zu verstärken. Das oder die doppelten magnetischen Ringpaare sind so konfiguriert, um die lokalen Magnetfelder zu intensivieren und die Anzahl sowie die mittlere Lebensdauer von radikalisiertem Sauerstoff zu erhöhen und die Wasserreinigung zu verbessern.*  
  reason: Answer is a faithful rendering of both mechanism sentences; question is strongly paraphrased and conceptual, though 'belüftetes Reinigungssystem' is vague and 'so ausgelegt, um' is slightly awkward German.
- **Q2 · gpt-5.4-mini** (kept, faith 5.00, quality 4.50, ling 5): Wie kann UV-Licht zusammen mit Magnetfeldern die Bildung reaktiver Sauerstoffformen für die Wasserreinigung fördern?  
  — *Die UV-Strahlungs-Reflexionsabdeckung ist so ausgelegt, dass sie die Wechselwirkung von UV-Strahlung mit Sauerstoffmolekülen in der einströmenden Luft verstärkt. Das Doppelringpaar aus Magneten intensiviert die lokalen Magnetfelder und erhöht die Anzahl und mittlere Lebensdauer radikalisierter Sauerstoffmoleküle und verbessert die Wasserreinigung.*  
  reason: Fluent, natural query combining UV and magnetic fields for water purification, clearly distinguishing this passage, with a fully grounded answer.
- **Q3 · gemini-3.5-flash** (kept, faith 5.00, quality 4.00, ling 4): Wie kann die Verweilzeit und Konzentration von aktivem Sauerstoff bei einer physikalischen Desinfektionsmethode künstlich verlängert und erhöht werden?  
  — *Das doppelte Magnetringpaar ist so konfiguriert, dass es die lokalen Magnetfelder intensiviert, die Anzahl und die mittlere Lebensdauer der radikalisierten Sauerstoffmoleküle erhöht und die Wasserreinigung verbessert.*  
  reason: Answer matches the magnetic ring sentence exactly; question is heavily paraphrased ('Verweilzeit', 'aktiver Sauerstoff') but 'künstlich' and the lack of any water/magnet cue weaken realism and retrievability.
- **Q4 · grok-4.3** (kept, faith 5.00, quality 4.00, ling 4): Wie lässt sich die Bildung reaktiver Sauerstoffspezies durch UV-Strahlung in einem Wassersystem gezielt verstärken?  
  — *Die UV-Strahlungsreflektionsabdeckung ist konfiguriert, um die Interaktion der UV-Strahlung mit Sauerstoffmolekülen in der eintretenden Luft zu verstärken.*  
  reason: Grounded single-sentence answer about the reflection cover; question is a plausible conceptual query, though 'Reflektionsabdeckung' spelling and 'konfiguriert, um' are minor flaws.
- **Q5 · sonnet-4.6** (kept, faith 5.00, quality 4.50, ling 5): Welche Rolle spielen Magnetfelder bei der Erzeugung und Stabilisierung reaktiver Sauerstoffspezies in einem Wasserreinigungsgerät?  
  — *Das/die doppelte(n) Magnetringpaar(e) ist/sind so konfiguriert, dass es/sie die lokalen Magnetfelder verstärkt/verstärken und die Anzahl und mittlere Lebensdauer der radikalisierten Sauerstoffmoleküle erhöht/erhöhen und die Wasserreinigung verbessert/verbessern.*  
  reason: Well-framed conceptual question on the role of magnetic fields in a water purifier; answer is accurate though the slash-heavy singular/plural form is clumsy to read.
- **Q6 · gpt-5-mini** (DISCARDED, faith 5.00, quality 3.50, ling 3): Welcher mechanische oder physikalische Mechanismus wird eingesetzt, um die Zahl und Lebensdauer reaktiver Sauerstoffspezies zu erhöhen und dadurch die Reinigung zu verbessern?  
  — *Die doppelten Paare magnetischer Ringe sind so konfiguriert, die lokalen Magnetfelder zu verstärken, die Anzahl und die mittlere Lebensdauer radikalisierten Sauerstoffmolekülen zu erhöhen und die Wasserreinigung zu verbessern.*  
  reason: Answer is grounded but has a grammar error ('radikalisierten Sauerstoffmolekülen' should be genitive 'radikalisierter Sauerstoffmoleküle') and the question is long, never mentions water, and largely duplicates Q3/Q5.

## MX-2025006624-A  ·  semantic mode  ·  question language: fr

> Several answers mix languages (Q3 fully English, Q4 English/French, Q6 Spanish fragment). Q3, Q5 and Q6 are the strongest semantic queries; Q4 is the weakest because of lexical overlap and a padded, mixed-language answer.

- **Q1 · gpt-5.4-mini** (kept, faith 5.00, quality 3.50, ling 4): Comment rendre un revêtement durcissable par radiation actinique tout en utilisant un monomère issu d’un glycol biobasé ?  
  — *une composition de revêtement durcissable par radiation actinique comprenant de 10 wt% à 90 wt% d’un composé A de poly(trimethylene ether) (meth)acrylate*  
  reason: Answer is a faithful extract; question is a natural, moderately paraphrased problem-style query, though 'comment rendre' is slightly awkward and the query is somewhat generic.
- **Q2 · grok-4.3** (kept, faith 4.33, quality 3.50, ling 3): Existe-t-il des revêtements polymérisables par actinique qui incorporent des matériaux d'origine biologique tout en maintenant des propriétés de mise en œuvre industrielles ?  
  — *composition de revêtement curable par radiation actinique qui comprend de 10 % en poids à 90 % en poids d'un composé A et entre 10 % en poids et 89.99 % en poids d'un composé B*  
  reason: Answer combines two supported spans with correct figures, but 'propriétés de mise en œuvre industrielles' is an inference beyond the passage and 'polymérisables par actinique' is ungrammatical French.
- **Q3 · qwen3.6-35b-a3b** (kept, faith 5.00, quality 4.25, ling 3): Quelle stratégie formulation permet d'intégrer des précurseurs renouvelables dans des systèmes de revêtements durcis par rayonnement tout en contrôlant la rhéologie ?  
  — *a poly(trimethylene ether) (meth)acrylate compound A having at most two (meth)acrylate groups obtainable by a condensation reaction of biobased 1,3 poly(trimethylene ether) glycol and a (meth)acrylate compound selected from the group consisting of (meth)acrylic acid, (meth)acryloyl chloride, and /or alkylesters thereof*  
  reason: Answer is verbatim from the passage; question is well paraphrased and conceptual, with 'contrôlant la rhéologie' loosely tied to the viscosity limit, but 'stratégie formulation' is missing 'de' and the answer is in English rather than French.
- **Q4 · gpt-5-mini** (DISCARDED, faith 4.67, quality 2.75, ling 3): Comment la formulation intègre-t-elle un monomère d'origine biobasée dans un revêtement curable par rayonnement actinique ?  
  — *La composition comprend de 10 wt% à 90 wt%, basé sur le poids total de la composition, d'un poly(trimethylene ether) (meth)acrylate compound A ayant au plus deux groupes (meth)acrylate, obtenable par une réaction de condensation de biobased 1,3 poly(trimethylene ether) glycol et d'un composé de (meth)acrylate sélectionné dans le groupe constitué par (meth)acrylic acid, (meth)acryloyl chloride et/ou leurs alkylesters; wherein the biobased 1,3 poly(trimethylene ether) glycol has a number average molecular weight Mn of from 350 to 600 g/mol, more preferably from 400 to 550 g/mol.*  
  reason: Faithful but the answer is a long, half-translated English/French mash-up with padding, and the question largely reuses passage vocabulary with a redundant 'origine biobasée'.
- **Q5 · gemini-3.5-flash** (kept, faith 5.00, quality 3.75, ling 4): Quels réactifs sont mis en œuvre pour synthétiser le monomère à base de polyéther-acrylate d'origine naturelle utilisé dans la formulation ?  
  — *une réaction de condensation de biobased 1,3 poly(trimethylene ether) glycol et un (meth)acrylate compound choisi dans le groupe constitué par (meth)acrylic acid, (meth)acryloyl chloride, et /ou alkylesters de ceux-ci*  
  reason: Answer exactly matches the reagent list; question is a realistic, specific, well-paraphrased query ('polyéther-acrylate d'origine naturelle'), though more fact- than concept-oriented and 'réactifs' slightly stretches the passage.
- **Q6 · sonnet-4.6** (kept, faith 5.00, quality 4.25, ling 3): Comment intégrer des matières premières renouvelables dans une formulation de revêtement durcissable par rayonnement sans sacrifier la réactivité ?  
  — *un composé de (met)acrilato de poly(triméthylène éther) A ayant au plus deux groupes (meth)acrylate, obtenu par réaction de condensation de 1,3 poly(trimethylene ether) glycol d'origine biologique et un composé (meth)acrylate choisi dans le groupe constitué de l'acide (meth)acrylique, du chlorure de (meth)acryloyle et/ou de leurs alkylesters*  
  reason: Answer is a faithful French rendering of compound A; question is strongly paraphrased and conceptual, but 'sans sacrifier la réactivité' is not stated in the passage and the answer contains a stray Spanish fragment '(met)acrilato'.

## MX-2025007206-A  ·  technical mode  ·  question language: de

> All six candidates target the same single fact — the -80°C long-term storage threshold — so this document yields almost no question diversity across systems; if only a subset is kept, Q2 and Q4 are the cleanest (fluent German, language-consistent answers). Cross-cutting issues: Q1 and Q5 leave the answer span in English while the question is German, Q6 drops the 'above' qualifier from its answer, and Q3 renders 'shelf storage' as a literal 'im Regal' calque. The passage also contains encoding noise ('-80Â°C', 'vector quality7'), which no candidate propagated.

- **Q1 · qwen3.6-35b-a3b** (kept, faith 5.00, quality 4.25, ling 5): Ab welcher Temperatur ist eine langfristige Lagerung der rAAV-Formulierungen möglich?  
  — *above -80°C*  
  reason: Fluent German question whose answer ('above -80°C') is directly supported by the passage and names the rAAV formulations, though the answer span is left in English while the question is German.
- **Q2 · grok-4.3** (kept, faith 5.00, quality 4.25, ling 5): Oberhalb welcher Temperatur ermöglichen rAAV-Formulierungen langfristige Lagerung?  
  — *oberhalb von -80 °C*  
  reason: Clean, grammatical German question with a language-consistent, exactly grounded answer ('oberhalb von -80 °C') and a single clear fact target.
- **Q3 · sonnet-4.6** (kept, faith 5.00, quality 3.50, ling 3): Bei welcher Mindesttemperatur kann eine rAAV-Formulierung für die Langzeitlagerung im Regal gelagert werden?  
  — *oberhalb von -80°C*  
  reason: Correctly grounded and specific, but wordy and stilted ('für die Langzeitlagerung im Regal gelagert' is a literal calque of 'shelf storage'), which hurts realism and fluency.
- **Q4 · gpt-5.4-mini** (kept, faith 4.67, quality 4.25, ling 5): Bei welcher Temperatur können die rAAV-Formulierungen längerfristig gelagert werden?  
  — *bei Temperaturen über -80 °C*  
  reason: Fluent and well grounded, with only a slight mismatch between the point-temperature framing ('Bei welcher Temperatur') and the threshold answer 'bei Temperaturen über -80 °C'.
- **Q5 · gpt-5-mini** (DISCARDED, faith 5.00, quality 3.00, ling 4): Welche Lagertemperatur wird für langfristige Aufbewahrung genannt?  
  — *temperatures above -80 °C*  
  reason: The answer is faithful, but the query names no rAAV/formulation anchor and is phrased as a meta-question about what the text 'nennt', so it would match arbitrary storage-temperature documents.
- **Q6 · gemini-3.5-flash** (DISCARDED, faith 4.00, quality 3.50, ling 3): Über welcher Lagertemperatur ermöglichen die rAAV-Formulierungen eine langfristige Haltbarkeit?  
  — *-80°C*  
  reason: Awkward German ('Über welcher Lagertemperatur' instead of 'Oberhalb welcher') and a bare '-80°C' answer that drops the 'above' threshold direction make it the weakest of several near-identical items.

## MX-2025007510-A  ·  semantic mode  ·  question language: es

> All six are faithful; Q2 and Q6 stand out. Q1's answer span should be trimmed to remove the stray '5' and the English 'hours'. Q2, Q3, Q5 and Q6 all target the same dosing-frequency/pulmonary-hypertension fact.

- **Q1 · gpt-5.4-mini** (kept, faith 4.33, quality 3.75, ling 5): ¿Qué tipo de formulación se usa para encapsular un fármaco de ácido débil de vida media corta?  
  — *una composición farmacéutica que contiene liposomas, el liposoma comprende una bicapa de lípido externa; y un medio acuoso interno que incluye 5 un fármaco de ácido débil con una vida media de menos de 2 hours.*  
  reason: Good paraphrased concept question, but the answer span is over-long, carries the OCR artifact '5' and mixes in English 'hours'.
- **Q2 · gemini-3.5-flash** (kept, faith 5.00, quality 4.25, ling 5): ¿Qué trastorno circulatorio se pretende tratar disminuyendo la cantidad de tomas diarias de la terapia?  
  — *tratar hipertensión pulmonar con frecuencia de dosificación reducida*  
  reason: Well paraphrased (trastorno circulatorio, tomas diarias) and tightly answered from the passage.
- **Q3 · gpt-5-mini** (kept, faith 5.00, quality 3.50, ling 5): ¿En qué indicación clínica se plantea usar esta formulación y qué beneficio de dosificación aporta?  
  — *tratar hipertensión pulmonar con frecuencia de dosificación reducida.*  
  reason: Faithful and fluent, but 'esta formulación' is context-dependent and the two-part question is less search-like.
- **Q4 · qwen3.6-35b-a3b** (kept, faith 4.67, quality 4.25, ling 5): ¿Qué estrategia de formulación permite vehicular y proteger principios activos de origen ácido que se eliminan rápidamente del organismo?  
  — *una composición farmacéutica que contiene liposomas*  
  reason: Strongly paraphrased conceptual query; 'proteger' slightly exceeds the passage and the query is generic enough to match many liposome documents.
- **Q5 · grok-4.3** (kept, faith 5.00, quality 4.00, ling 4): Manera de bajar la frecuencia con que se administra medicación a pacientes con hipertensión pulmonar  
  — *para tratar hipertensión pulmonar con frecuencia de dosificación reducida*  
  reason: Natural search-style phrasing with a faithful answer, though the query could match many pulmonary-hypertension dosing documents.
- **Q6 · sonnet-4.6** (kept, faith 4.67, quality 4.50, ling 5): ¿Qué estrategia de encapsulación lipídica permite reducir la frecuencia de administración en el tratamiento de la hipertensión pulmonar?  
  — *el uso de la composición farmacéutica descrita en la presente para tratar hipertensión pulmonar con frecuencia de dosificación reducida*  
  reason: Combines encapsulation strategy with the indication and dosing benefit, making it highly distinctive and well grounded.

## MX-2025009131-A  ·  technical mode  ·  question language: zh

> Q3-Q6 all ask the same fact (supercritical fluid); Q5 and Q6 are near-identical and the best of the set. Q1-Q4 lack any document-anchoring context. Answer language is mixed (Q3/Q4 in Chinese, others in English) despite the zh question language.

- **Q1 · gpt-5-mini** (DISCARDED, faith 5.00, quality 3.00, ling 4): 聚合物由哪类聚合物组成？  
  — *one or more non-cross-linked thermoplastic polymers that are recyclable and/or biodegradable*  
  reason: Answer is exact, but the question ('what kind of polymer is the polymer composed of') has no anchoring context and would match countless polymer documents.
- **Q2 · grok-4.3** (DISCARDED, faith 5.00, quality 2.75, ling 4): 维持升高压力是为了什么？  
  — *to infuse the supercritical fluid into the polymer*  
  reason: Answer is grounded, but 'why maintain elevated pressure' is context-free and arbitrarily generic as a retrieval query.
- **Q3 · qwen3.6-35b-a3b** (DISCARDED, faith 5.00, quality 3.50, ling 4): 为升高腔室或型腔压力使用的是何种流体？  
  — *超临界流体*  
  reason: Correct answer and decent paraphrase, but lacks the foam/polymer context needed to narrow to this document.
- **Q4 · gpt-5.4-mini** (DISCARDED, faith 5.00, quality 3.50, ling 4): 用于把腔体加压到高压的流体是什么？  
  — *超临界流体*  
  reason: Faithful and fluent but too generic ('what fluid pressurizes the chamber') with no domain anchor.
- **Q5 · gemini-3.5-flash** (kept, faith 5.00, quality 4.00, ling 5): 在柔性泡沫生产工艺中，使用什么对高压釜腔或模腔进行加压？  
  — *supercritical fluid*  
  reason: Faithful, fluent, and anchored by 'flexible foam production process' plus autoclave/mold cavity, making it reasonably specific.
- **Q6 · sonnet-4.6** (kept, faith 5.00, quality 4.00, ling 5): 生产柔性泡沫时，用什么流体对高压釜腔室或模具腔体加压？  
  — *supercritical fluid*  
  reason: Faithful and natural, with flexible-foam and autoclave/mold context that narrows the query; near-duplicate of Q5.

## MX-2025009666-A  ·  technical mode  ·  question language: en

> Five of six questions target the apparently misappended dump-tank system text rather than the metallocene catalyst subject of the patent; Q2/Q3/Q6 are near-duplicates (fluid outlet at bottom) and Q1/Q4 are near-duplicates (gas outlets at top). All answers are faithful. Q5 stands out as the only question about the patent's real subject.

- **Q1 · gpt-5-mini** (kept, faith 5.00, quality 3.50, ling 4): Where are the one or more gas outlets located on the dump tank vessel?  
  — *at a top of the vessel*  
  reason: Answer is directly extracted and focused, though the phrasing borrows claim language ('one or more gas outlets') and targets a generic dump-tank detail rather than the metallocene catalyst subject of the patent.
- **Q2 · qwen3.6-35b-a3b** (kept, faith 5.00, quality 3.75, ling 5): Where is the fluid outlet positioned in the dump tank vessel?  
  — *at a bottom of the vessel*  
  reason: Faithful, concise, single-fact question with light paraphrase ('positioned'), but the dump-tank fluid outlet is a generic detail that would match many reactor patents.
- **Q3 · sonnet-4.6** (kept, faith 5.00, quality 3.50, ling 4): Where is the fluid outlet located on the dump tank vessel used to receive reactor product?  
  — *at a bottom of the vessel*  
  reason: Faithful and correctly answered; adding 'used to receive reactor product' slightly aids specificity but makes it wordier and less search-like.
- **Q4 · gemini-3.5-flash** (kept, faith 5.00, quality 4.00, ling 5): Where are the gas outlets located on the dump tank vessel?  
  — *at a top of the vessel*  
  reason: Shortest, cleanest variant of the gas-outlet question, faithful and focused, though still a generic equipment detail with limited retrieval power.
- **Q5 · grok-4.3** (kept, faith 5.00, quality 4.00, ling 5): What solvent is used to form the metallocene solution?  
  — *hydrocarbon solvent*  
  reason: The only question targeting the patent's actual subject (metallocene catalyst preparation); answer 'hydrocarbon solvent' is directly supported, though the fact is fairly generic across metallocene patents.
- **Q6 · gpt-5.4-mini** (kept, faith 5.00, quality 3.75, ling 5): Where is the fluid outlet located in the dump tank?  
  — *at a bottom of the vessel*  
  reason: Faithful and search-like, but the most generic of the fluid-outlet variants; 'bottom of the vessel' is a near-trivial answer that would match many dump-tank descriptions.

## MX-2025010190-A  ·  technical mode  ·  question language: en

> All six answers are exactly grounded in the English abstract. Q1, Q3 and Q4 ask essentially the same fact (nutritionally complete amino acid profile); Q3/Q4 are the better phrasings. Q2 and Q6 likewise overlap on polynucleotides/encoding. The passage is abstract-only, so no question can be highly specific.

- **Q1 · gpt-5-mini** (DISCARDED, faith 5.00, quality 3.25, ling 5): What amino acid profile does the recombinant polypeptide have?  
  — *a nutritionally complete amino acid profile*  
  reason: Answer is exact, but 'recombinant polypeptide' with 'amino acid profile' is generic and the question gives little to distinguish this patent from many others.
- **Q2 · gpt-5.4-mini** (DISCARDED, faith 5.00, quality 2.75, ling 5): What do the polynucleotides encode?  
  — *the recombinant polypeptides*  
  reason: Trivially true of almost any biotech patent; the question cannot narrow to this document at all.
- **Q3 · qwen3.6-35b-a3b** (kept, faith 5.00, quality 3.75, ling 5): What type of amino acid profile characterizes the recombinant polypeptide in the nutritional composition?  
  — *nutritionally complete amino acid profile*  
  reason: Faithful, single-fact, and mentioning 'nutritional composition' plus 'recombinant polypeptide' gives moderate discriminative power.
- **Q4 · sonnet-4.6** (kept, faith 5.00, quality 3.50, ling 5): What type of amino acid profile does the recombinant polypeptide in the nutritional composition provide?  
  — *a nutritionally complete amino acid profile*  
  reason: Near-duplicate of Q3 but equally faithful and focused, with enough context to point toward this patent.
- **Q5 · grok-4.3** (DISCARDED, faith 5.00, quality 3.00, ling 4): What forms of polypeptide are suitable to provide a nutritionally complete amino acid profile when provided in a nutritional composition?  
  — *a recombinant polypeptide and variants and truncates thereof*  
  reason: Answer is verbatim-supported and the query is specific, but the question is lifted almost word-for-word from the abstract and reads as a sentence, not a search query.
- **Q6 · gemini-3.5-flash** (kept, faith 5.00, quality 3.75, ling 5): What encodes the recombinant polypeptides with a nutritionally complete amino acid profile?  
  — *polynucleotides*  
  reason: Faithful and the 'nutritionally complete amino acid profile' qualifier adds specificity, though the answer 'polynucleotides' is somewhat trivial.

## WO-2022005333-A1  ·  semantic mode  ·  question language: en

> All six questions target the same sentence of the abstract (using low-demand olefin fractions to make gasoline), so they are near-duplicates; Q4 and Q5 stand out for also capturing the octane/yield benefits with exact numbers, while Q6 is the weakest on search realism.

- **Q1 · qwen3.6-35b-a3b** (kept, faith 5.00, quality 3.75, ling 5): Which unutilized refinery byproduct streams are suitable for conversion into high-quality automotive fuel?  
  — *low-demand olefin-containing fractions, such as dry gas from catalytic cracking, a propane-propylene fraction or a butane-butylene fraction*  
  reason: Answer is an exact span; question is strongly paraphrased ('unutilized refinery byproduct', 'automotive fuel') though it asks for a list of facts rather than a concept and 'high-quality' is a slight gloss.
- **Q2 · gpt-5-mini** (kept, faith 4.67, quality 3.75, ling 4): How can low-value olefin-rich feeds like dry catalytic cracking gas or propane‑propylene cuts be converted into gasoline in this process?  
  — *The method makes it possible to produce gasolines using low-demand olefin-containing fractions, such as dry gas from catalytic cracking, a propane-propylene fraction or a butane-butylene fraction,*  
  reason: Well grounded and conceptually framed, but the question names the specific feeds from the passage (lower lexical distance) and the trailing 'in this process' plus a dangling comma in the answer are minor blemishes.
- **Q3 · grok-4.3** (kept, faith 5.00, quality 4.00, ling 5): How can low-demand refinery gases like catalytic cracking dry gas be upgraded into gasoline?  
  — *produce gasolines using low-demand olefin-containing fractions, such as dry gas from catalytic cracking, a propane-propylene fraction or a butane-butylene fraction*  
  reason: Natural, concise 'how can X be upgraded' query with an exact answer span; lexical distance is moderate since 'low-demand' and 'catalytic cracking dry gas' echo the passage.
- **Q4 · sonnet-4.6** (kept, faith 5.00, quality 4.25, ling 5): How can low-value refinery off-gases like propane-propylene or butane-butylene cuts be converted into high-octane gasoline?  
  — *The method makes it possible to produce gasolines using low-demand olefin-containing fractions, such as dry gas from catalytic cracking, a propane-propylene fraction or a butane-butylene fraction, and to increase the octane rating of the product to 95-98 at a product yield of more than 70 wt%*  
  reason: Answer span exactly reproduces the 95-98 and >70 wt% figures; 'high-octane gasoline' plus the named cuts make it highly retrievable, though calling propane-propylene cuts 'off-gases' is a slight terminological stretch.
- **Q5 · gpt-5.4-mini** (kept, faith 5.00, quality 4.25, ling 5): How can low-value olefin-rich byproduct streams be converted into gasoline with higher octane and yield?  
  — *The method makes it possible to produce gasolines using low-demand olefin-containing fractions, such as dry gas from catalytic cracking, a propane-propylene fraction or a butane-butylene fraction, and to increase the octane rating of the product to 95-98 at a product yield of more than 70 wt%, while also reducing the diesel fraction content to less than 2 wt%*  
  reason: Fully paraphrased, concept-level question with an exact multi-benefit answer span including all numbers; generic enough that it could match other olefin-to-gasoline documents.
- **Q6 · gemini-3.5-flash** (DISCARDED, faith 5.00, quality 3.25, ling 4): How can chemical processors salvage low-demand refinery byproducts containing olefins for fuel synthesis?  
  — *produce gasolines using low-demand olefin-containing fractions, such as dry gas from catalytic cracking, a propane-propylene fraction or a butane-butylene fraction*  
  reason: Grounded answer, but 'How can chemical processors salvage ... for fuel synthesis' is stilted and unlike a real search query, and retains 'low-demand' and 'olefins' from the passage.

## WO-2023149795-A1  ·  technical mode  ·  question language: en

> Five of six questions (Q1, Q2, Q3, Q5, Q6) ask the same fact (zinc acetate) with near-identical wording and all mirror the passage's vocabulary; they are effectively tied, with Q6 marginally most specific. Q4 stands out as the only question on a different fact. All answers are fully supported by the passage and there are no faithfulness problems.

- **Q1 · gpt-5-mini** (kept, faith 5.00, quality 3.50, ling 5): Which protein synthesis stimulator is included in the second nutrient medium?  
  — *zinc acetate*  
  reason: Correct and single-fact, but reuses the passage's own wording ('protein synthesis stimulator', 'second nutrient medium') and is generic enough to match other insect-rearing documents.
- **Q2 · gpt-5.4-mini** (kept, faith 5.00, quality 3.50, ling 5): What protein synthesis stimulator is added to the second nutrient medium?  
  — *zinc acetate*  
  reason: Near-identical to Q1 and Q3; accurate answer but lifted phrasing and moderate specificity.
- **Q3 · grok-4.3** (kept, faith 5.00, quality 3.50, ling 5): What protein synthesis stimulator is included in the second nutrient medium?  
  — *zinc acetate*  
  reason: Essentially a duplicate of Q1 with 'What' for 'Which'; faithful but keyword-lifted and only moderately discriminative.
- **Q4 · qwen3.6-35b-a3b** (kept, faith 5.00, quality 4.00, ling 5): At what temperature are the lyophilized larvae re-ground?  
  — *-55°C*  
  reason: The only question targeting a different fact; the -55°C re-grinding temperature is exactly reproduced, the phrasing is condensed, and lyophilized-larvae re-grinding is fairly distinctive.
- **Q5 · gemini-3.5-flash** (kept, faith 5.00, quality 3.50, ling 5): What chemical is used as a protein synthesis stimulator in the second nutrient medium?  
  — *zinc acetate*  
  reason: Faithful and slightly reworded ('what chemical is used as'), but still the same lifted key terms and the same fact as Q1–Q3 and Q6.
- **Q6 · sonnet-4.6** (kept, faith 5.00, quality 3.75, ling 5): What protein synthesis stimulator is added to the second nutrient medium for insect larval cultivation?  
  — *zinc acetate*  
  reason: Adding 'for insect larval cultivation' improves discriminability over the other zinc-acetate variants, though the core wording remains lifted from the abstract.

## WO-2025054647-A1  ·  semantic mode  ·  question language: es

> All six target the same matrix diffusion/expansion span; Q3 and Q5 stand out for lexical distance. Several answers contain untranslated fragments (German in Q2, French 'plage' in Q4, English 'to' in Q5) and two questions have spelling errors in 'termoquímico'.

- **Q1 · gpt-5-mini** (DISCARDED, faith 4.67, quality 3.25, ling 3): ¿Qué diseño estructural integra el material termochímico y qué propiedades de difusión y deformación especifica la matriz?  
  — *el medio de almacenamiento termochímico incorporado en una matriz; la matriz tiene un coeficiente de difusión de gas para el gas de 2.25*10 -9 m 2 /s a 4.25*10 -9 m 2 /s en un intervalo de temperatura de -30°C a 300°C, y una expansión máxima ε en el rango de la ley de Hooke de 25% a 300%; el medio de almacenamiento termochímico está distribuido sustancialmente de forma homogénea en la matriz.*  
  reason: Answer is faithful but the question is a two-part compound with the misspelling 'termochímico' and reads more like a summary prompt than a retrieval query.
- **Q2 · sonnet-4.6** (kept, faith 5.00, quality 4.00, ling 5): ¿Qué propiedades mecánicas y de transporte debe reunir una matriz que aloje un medio de almacenamiento termoquímico para funcionar de forma estable en un amplio rango térmico?  
  — *die Matrix einen Gasdiffusionskoeffizient für das Gas von 2,25*10-9 m2/s bis 4,25*10-9 m2/s in einem Temperaturbereich von -30°C bis 300°C, und eine maximale Dehnung ε im Hooke'schen Bereich von 25% bis 300% aufweist*  
  reason: Well-paraphrased conceptual Spanish query with an exact German answer span, though the answer being in a different language from the question is a minor oddity.
- **Q3 · gemini-3.5-flash** (kept, faith 4.67, quality 4.50, ling 5): ¿Cómo se resuelven las tensiones mecánicas por dilatación y se asegura la permeabilidad al gas en acumuladores térmicos que operan en condiciones térmicas extremas?  
  — *la matriz presenta un coeficiente de difusión de gas para el gas de 2.25*10 -9 m 2 /s a 4.25*10 -9 m 2 /s en un rango de temperatura de -30°C a 300°C, y una expansión máxima ε en el rango de la ley de Hooke de 25% a 300%*  
  reason: Strong conceptual paraphrase with little keyword overlap; the 'how is it solved' framing slightly overreaches what the span states, but the answer still matches the passage exactly.
- **Q4 · gpt-5.4-mini** (DISCARDED, faith 5.00, quality 2.75, ling 4): ¿Qué características debe tener la matriz para funcionar bien en un sistema de almacenamiento térmico de este tipo?  
  — *la matriz presentando un coeficiente de difusión de gas para el gas de 2,25*10 -9 m 2 /s a 4,25*10 -9 m 2 /s en una plage de temperatura de -30 °C a 300 °C, y una expansión máxima ε en la plage de ley de Hooke de 25 % a 300 %*  
  reason: Question is too generic ('de este tipo') to distinguish this passage, and the answer is a sloppy translation leaving French 'plage' untranslated.
- **Q5 · qwen3.6-35b-a3b** (kept, faith 5.00, quality 4.25, ling 5): ¿Qué parámetros de permeabilidad y dilatación estructural debe cumplir el material soporte para garantizar un funcionamiento estable en acumuladores de calor químico?  
  — *la matriz tiene un coeficiente de difusión de gas para el gas de 2.25*10 -9 m 2 /s to 4.25*10 -9 m 2 /s en un rango de temperatura de -30°C to 300°C, y una expansión máxima ε en el rango de la ley de Hooke de 25% to 300%*  
  reason: Good paraphrase (permeabilidad, material soporte, acumuladores de calor químico) with an exact answer, despite stray English 'to' in the answer ranges.
- **Q6 · grok-4.3** (kept, faith 5.00, quality 4.00, ling 4): ¿Qué propiedades de transporte de gas y de estabilidad mecánica debe poseer la estructura soporte para que un material termquímico funcione correctamente en un amplio margen de temperaturas?  
  — *la matriz tiene un coeficiente de difusión de gas para el gas de 2,25*10-9 m2/s a 4,25*10-9 m2/s en un rango de temperatura de -30°C a 300°C, y una expansión máxima ε en el rango de la ley de Hooke de 25% a 300%*  
  reason: Well-framed conceptual query with faithful numerical answer; only flaw is the typo 'termquímico'.

## WO-2025177605-A1  ·  technical mode  ·  question language: fr

> All six answers are faithful; the set is highly redundant (three 'soudage au plasma' questions, two Al-content questions). Q2 and Q6 are near-duplicates; Q6 is slightly better paraphrased. Q4 is the only question targeting a distinct fact (Ni content) with strong document anchoring.

- **Q1 · gpt-5-mini** (DISCARDED, faith 5.00, quality 3.00, ling 5): Quel pourcentage d'Al contient l'alliage à base de Ni ?  
  — *2,0% en poids ou plus d'Al*  
  reason: Answer is exact, but the question lacks any retort/welding context and 'Ni-based alloy with Al' matches many patents; also asks for 'what percentage' while the answer is a minimum threshold.
- **Q2 · qwen3.6-35b-a3b** (kept, faith 5.00, quality 4.25, ling 5): Quelle méthode de soudage est employée pour la fabrication de la cornue ?  
  — *soudage au plasma*  
  reason: Concise, well paraphrased, anchored on 'cornue' which narrows retrieval, and the answer is directly in the passage.
- **Q3 · grok-4.3** (DISCARDED, faith 5.00, quality 3.50, ling 5): Quelle est la teneur minimale en Al de l'alliage à base de Ni ?  
  — *2,0% en poids ou plus d'Al*  
  reason: Correctly framed as a minimum, but no mention of retort or welding so it would match arbitrary Ni-Al alloy documents.
- **Q4 · sonnet-4.6** (kept, faith 5.00, quality 4.25, ling 5): Quelle est la teneur minimale en Ni requise dans l'alliage à base de Ni utilisé pour le matériau de base d'une cornue ?  
  — *90,0% en poids ou plus de Ni*  
  reason: Accurate and highly specific (Ni minimum, base material, retort), though somewhat long for a search-bar query.
- **Q5 · gpt-5.4-mini** (DISCARDED, faith 5.00, quality 3.00, ling 5): Quel type de soudage est utilisé pour joindre la partie de jonction du matériau de base ?  
  — *soudage au plasma*  
  reason: Answer correct but the question lifts 'partie de jonction du matériau de base' verbatim and omits 'cornue', making it generic to any welding patent.
- **Q6 · gemini-3.5-flash** (kept, faith 5.00, quality 4.25, ling 5): Quelle méthode de soudage est utilisée pour assembler le matériau de base de la cornue ?  
  — *soudage au plasma*  
  reason: Well paraphrased ('assembler'), anchored on the retort, single fact, correctly answered.

## WO-2025187661-A8  ·  semantic mode  ·  question language: es

> Several answers are mixed-language (Spanish with English 'burrs'/'poly(arylene sulfide)') or left entirely in English (Q2); Q3 and Q5 are the strongest, Q1 acceptable.

- **Q1 · gemini-3.5-flash** (kept, faith 5.00, quality 4.00, ling 4): ¿Cómo se puede resolver el reto de la aparición de imperfecciones físicas o rebabas en polímeros de ingeniería cuando se someten a procesos de recuperación y reprocesamiento?  
  — *una composición de resina de poly(arylene sulfide) que, durante el reciclaje, puede evitar la formación de rebabas*  
  reason: Answer is a faithful translation of the abstract's core claim; the question is strongly paraphrased (engineering polymers, recovery/reprocessing) but somewhat long and generic, so retrievability is only moderate.
- **Q2 · qwen3.6-35b-a3b** (DISCARDED, faith 4.67, quality 3.75, ling 3): ¿Qué enfoque se propone para prevenir la aparición de rebabas o exudaciones al reprocesar polímeros de cadena aromática con enlaces de azufre?  
  — *can be inhibited from forming burrs*  
  reason: The answer is an untranslated English fragment that does not actually name the approach asked for, and 'exudaciones' introduces a defect not in the passage.
- **Q3 · grok-4.3** (kept, faith 5.00, quality 3.50, ling 4): ¿Cómo se puede evitar la formación de rebabas durante el reciclaje de resinas de poly(arylene sulfide)?  
  — *una composición de resina de poly(arylene sulfide) que, durante el reciclaje, puede ser inhibida de formar rebabas*  
  reason: Clear, natural query and grounded answer, but it largely reuses the passage's own vocabulary (rebabas, reciclaje, poly(arylene sulfide)) and is closer to a fact lookup than a concept.
- **Q4 · gpt-5.4-mini** (DISCARDED, faith 4.67, quality 3.50, ling 4): ¿Cómo se puede evitar que una resina de poly(arylene sulfide) reciclada genere rebabas?  
  — *que, durante el reciclaje, puede ser impedida de formar burrs*  
  reason: Question is fine but the answer is a dangling, half-translated fragment ('puede ser impedida de formar burrs') that mixes languages and does not stand on its own.
- **Q5 · sonnet-4.6** (kept, faith 5.00, quality 3.75, ling 5): ¿Cómo se puede evitar la formación de rebabas durante el reciclado de resinas termoplásticas de alto rendimiento?  
  — *La composición de resina de poly(arylene sulfide) (X) para materiales de reciclaje comprende (A) 100 partes en masa de una resina de poly(arylene sulfide) lineal con grupo carboxy y (B) 0,3-10 partes en masa de un compuesto alkoxysilane.*  
  reason: Well-paraphrased question (high-performance thermoplastics) with an answer that reproduces the composition and 0.3-10 parts range exactly; generalisation slightly weakens retrievability.
- **Q6 · gpt-5-mini** (DISCARDED, faith 5.00, quality 3.00, ling 4): ¿Qué defecto durante el reprocesado en planta pretende evitar esta composición de resina?  
  — *puede ser inhibida de formar rebabas durante el reciclaje.*  
  reason: 'Esta composición de resina' presupposes the document is already in hand, so as a standalone retrieval query it is too vague to find this passage among others.

## WO-2025202347-A1  ·  semantic mode  ·  question language: de

> Q3 and Q6 are near-duplicates targeting the late-complication list; Q3 is the cleaner of the two. Q2 is the weakest since it asks for a 'strategy' the passage never describes.

- **Q1 · gpt-5-mini** (kept, faith 5.00, quality 3.50, ling 4): Welche konkreten Augenzustände und Spätkomplikationen können mit einer iota-carrageenan-haltigen Formulierung behandelt werden?  
  — *die klinisch relevanten Augenleiden sind ausgewählt aus der Gruppe bestehend aus erhöhter Augeninnendruck, nicht-allergischer und nicht-viraler Konjunktivitis, Reizungen verursacht durch luftgetragene Partikel außer Allergenen, und späte Komplikationen dieser Konjunktivitis, bestehend aus Kornea-Opazitäten, subepithelialen Infiltraten und Bildung von okulären Pseudomembranen.*  
  reason: Answer faithfully reproduces the full condition list; question is a bit list-enumerating but specific enough to retrieve this patent, with minor grammatical slips in the answer (erhöhter Augeninnendruck case).
- **Q2 · qwen3.6-35b-a3b** (DISCARDED, faith 4.67, quality 3.00, ling 4): Welche Formulierungsstrategie ermöglicht es, iota-carrageenan als zentrales oder einziges therapeutisches Element in einer wässrigen Augenmedikation einzusetzen?  
  — *als Haupt- oder alleiniger Wirkstoff in einer wässrigen pharmazeutischen Zubereitung*  
  reason: The passage states no 'formulation strategy'; the question presupposes something absent, and the answer merely restates the claim wording so the question is circular and unrealistic.
- **Q3 · gemini-3.5-flash** (kept, faith 5.00, quality 4.00, ling 5): Welche klinischen Folgeerscheinungen einer Bindehautreizung, die weder auf Allergene noch auf Viren zurückzuführen ist, lassen sich behandeln?  
  — *Spätkomplikationen einer nicht-viralen und nicht-allergischen Konjunktivitis, ausgewählt aus der Gruppe bestehend aus Hornhauttrübungen, subepithelialen Infiltraten und der Bildung von okulären Pseudomembranen*  
  reason: Well-paraphrased (Bindehautreizung, Folgeerscheinungen) and accurately answered with the late-complication list, though it omits iota-carrageenan so retrievability is slightly weaker.
- **Q4 · gpt-5.4-mini** (kept, faith 5.00, quality 3.75, ling 4): Welche Art von Augenleiden soll mit einer iota-carrageenan-basierten Formulierung behandelt oder verhindert werden?  
  — *nicht allergische, nicht virale klinisch relevante Augenbeschwerden, die mindestens eines der folgenden Bereiche betreffen: die Schleimhautgewebe am oder um das Auge, die Augenoberfläche, das Hornhautgewebe und die Flüssigkeit im Auge*  
  reason: Conceptual question about the class of conditions with a faithful answer covering the tissue scope; minor grammar ('eines der folgenden Bereiche' should be 'einen').
- **Q5 · grok-4.3** (kept, faith 4.33, quality 4.00, ling 5): Wie lassen sich Augenirritationen durch luftgetragene Partikel, die keine Allergene sind, gezielt behandeln?  
  — *iota-Carrageenan als Haupt- oder alleiniger Wirkstoff in einer wässrigen pharmazeutischen Zusammensetzung zur Prävention oder Behandlung von Reizungen verursacht durch luftgetragene Partikelmasse außer Allergenen.*  
  reason: Realistic how-to query with good paraphrase; the answer combines two spans (active ingredient + particulate irritation) and 'Partikelmasse' is a slightly odd rendering, but it is supported.
- **Q6 · sonnet-4.6** (kept, faith 4.67, quality 4.00, ling 5): Wie können Spätfolgen einer nicht-viralen Bindehautentzündung, wie Hornhauttrübungen oder Pseudomembranbildung, pharmakologisch adressiert werden?  
  — *Die klinisch relevanten Augenerkrankungen umfassen Spätkomplikationen nicht-viraler und nicht-allergischer Konjunktivitis, ausgewählt aus der Gruppe bestehend aus Hornhauttrübungen (corneal opacities), subepitheliale Infiltrate und die Bildung okulärer Pseudomembranen (formation of ocular pseudomembranes).*  
  reason: Fluent conceptual query; the answer is grounded but merely lists the complications rather than naming iota-carrageenan as the pharmacological means the question asks for, and includes English glosses as padding.

## WO-2025207810-A1  ·  technical mode  ·  question language: zh

> Four of six questions (Q1, Q3, Q4, Q5) target the same Hamming-code fact; Q6 stands out as the most distinctive and best paraphrased. Q2 and Q4 mix English terms into Chinese questions, hurting fluency.

- **Q1 · gemini-3.5-flash** (kept, faith 5.00, quality 3.75, ling 5): 纠错条形码核苷酸序列是基于什么进行设计的？  
  — *Hamming codes*  
  reason: Fluent Chinese question with exact Hamming-code answer, though barcode/Hamming is a fairly common NGS topic so specificity is moderate.
- **Q2 · sonnet-4.6** (kept, faith 5.00, quality 3.75, ling 3): engineered hairpin structure在寡核苷酸中起什么作用？  
  — *mitigates hybridizing of the oligonucleotide to undesirable nucleic acid sequences*  
  reason: Answer is a verbatim span and the hairpin detail is distinctive, but the English/Chinese code-mixing in the question reads awkwardly.
- **Q3 · qwen3.6-35b-a3b** (kept, faith 5.00, quality 3.75, ling 5): 错误检查条形码核苷酸序列基于什么编码？  
  — *汉明码*  
  reason: Clean Chinese question with correctly translated answer 汉明码; near-duplicate of Q1/Q5 in content.
- **Q4 · gpt-5.4-mini** (DISCARDED, faith 5.00, quality 3.50, ling 3): 错误校验 barcode nucleotide sequences 基于什么编码？  
  — *Hamming codes*  
  reason: Correct answer but unnatural mixed-language phrasing and redundant with Q1/Q3/Q5 which ask the same fact more fluently.
- **Q5 · grok-4.3** (kept, faith 5.00, quality 3.75, ling 5): 错误检查条形码核苷酸序列基于什么？  
  — *Hamming codes*  
  reason: Grammatical, concise and correct, essentially the same question as Q1 and Q3.
- **Q6 · gpt-5-mini** (kept, faith 5.00, quality 4.25, ling 5): 哪种结构可减弱寡核苷酸与不良核酸序列的杂交？  
  — *工程化的发夹结构*  
  reason: Well-paraphrased, distinctive question about the engineered hairpin with a correct translated answer; the strongest of the set.

## WO-2025210445-A1  ·  technical mode  ·  question language: fr

> All six questions target the same voltage-range fact; Q4 and Q5 are word-for-word duplicates. Only Q1 anchors the query to the invention's content (Fenton reagents generated in situ), which is why it is the sole keep; the rest would retrieve arbitrary electrochemical documents.

- **Q1 · sonnet-4.6** (kept, faith 5.00, quality 4.00, ling 5): Quelle est la plage de tension préférentielle appliquée entre les électrodes dans un procédé électrochimique de génération de réactifs de Fenton in situ ?  
  — *entre 1 V et 20 V*  
  reason: Answer exactly matches the 'more preferred' range and the question's Fenton-in-situ context makes it highly discriminative, though it is long for a search bar and 'plage préférentielle' is slightly ambiguous between the two nested ranges.
- **Q2 · gpt-5-mini** (DISCARDED, faith 4.67, quality 3.00, ling 4): Plage de tension préférée entre les électrodes  
  — *de préférence entre 0 V et 220 V, plus préférentiellement entre 1 V et 20 V*  
  reason: Keyword-style query is realistic but far too generic to single out this patent, and the answer bundles both nested ranges while the question asks for one preferred range.
- **Q3 · grok-4.3** (DISCARDED, faith 4.67, quality 2.50, ling 5): Quelle tension est appliquée entre les électrodes ?  
  — *de préférence entre 0 V et 220 V, plus préférentiellement entre 1 V et 20 V*  
  reason: Grammatical and grounded, but 'quelle tension entre les électrodes' would match almost any electrochemistry document and the answer gives two ranges rather than one fact.
- **Q4 · qwen3.6-35b-a3b** (DISCARDED, faith 5.00, quality 3.25, ling 4): Quelle plage de tension est plus préférentiellement appliquée entre les électrodes ?  
  — *entre 1 V et 20 V*  
  reason: Faithful and single-fact, but it lacks any anchor to this invention (Fenton, pollutants, water) so it would not narrow retrieval, and it is a near-verbatim lift of the source wording.
- **Q5 · gemini-3.5-flash** (DISCARDED, faith 5.00, quality 3.25, ling 4): Quelle plage de tension est plus préférentiellement appliquée entre les électrodes ?  
  — *entre 1 V et 20 V*  
  reason: Identical to Q4: correct answer but generic, source-lifted phrasing with no document-specific anchor.
- **Q6 · gpt-5.4-mini** (DISCARDED, faith 5.00, quality 3.25, ling 4): Quelle plage de tension est indiquée comme la plus préférée entre les électrodes ?  
  — *entre 1 V et 20 V*  
  reason: Slightly better paraphrased than Q4/Q5 and correct, but still has no topical anchor to this patent and reads awkwardly ('la plus préférée entre les électrodes') rather than like a search query.

## WO-2025211128-A1  ·  technical mode  ·  question language: en

> Five of six questions target the same 0.5 μm recess-depth fact; Q2 and Q4 are word-for-word duplicates. Q1 and Q3 stand out as the only ones with real retrieval specificity.

- **Q1 · sonnet-4.6** (kept, faith 5.00, quality 4.25, ling 5): What is the maximum recess depth from the surface specified for a polycrystalline silicon member?  
  — *0.5 μm or less*  
  reason: Answer exactly matches the passage and the question adds 'polycrystalline silicon member' and 'maximum', making it the most specific and best-paraphrased of the recess-depth questions.
- **Q2 · gemini-3.5-flash** (kept, faith 5.00, quality 3.25, ling 5): What is the recess depth from the surface of the silicon member?  
  — *0.5 μm or less*  
  reason: Faithful answer but the question nearly lifts the source wording and 'silicon member' alone is generic; borderline keep.
- **Q3 · qwen3.6-35b-a3b** (kept, faith 5.00, quality 4.25, ling 5): What is the preferred percentage range of Σ9 grain boundaries within the coincidence grain boundary?  
  — *from 3% to 20%*  
  reason: Exact answer, and the Σ9 coincidence-grain-boundary range is a highly distinctive fact that would narrow retrieval to this document.
- **Q4 · grok-4.3** (kept, faith 5.00, quality 3.25, ling 5): What is the recess depth from the surface of the silicon member?  
  — *0.5 μm or less*  
  reason: Identical to Q2: faithful but near-verbatim and only moderately specific.
- **Q5 · gpt-5.4-mini** (DISCARDED, faith 5.00, quality 2.50, ling 5): What is the recess depth from the surface?  
  — *0.5 μm or less*  
  reason: Answer is correct but the question names no material or component at all, so it would match arbitrary documents.
- **Q6 · gpt-5-mini** (DISCARDED, faith 5.00, quality 2.75, ling 4): What recess depth from the surface is required?  
  — *0.5 μm or less*  
  reason: Faithful answer, but the question lacks any subject (silicon, polycrystalline) and reads awkwardly, giving no retrieval signal.

## WO-2025211336-A1  ·  semantic mode  ·  question language: en

> The abstract is short, so answers cluster on two spans: the component list (Q1, Q3, Q6) and the properties clause (Q2, Q4, Q5). Q2 is the weakest because its answer does not actually address the 'how'; Q6 is the most distinctive but leans on domain inference (thiol-ene) beyond the passage text.

- **Q1 · qwen3.6-35b-a3b** (kept, faith 5.00, quality 4.00, ling 4): What specific ingredient combination enables UV-sensitive polymers to retain pliability and withstand high temperatures when cured into heavy layers?  
  — *component (A): a polyorganosiloxane having one or more vinyl groups in one molecule, component (B): a compound having one or more mercapto groups in one molecule, component (C): a photoinitiator, and component (D): hollow resin particles*  
  reason: Answer is the exact component list; question is strongly paraphrased (UV-sensitive polymers, pliability, heavy layers) though 'UV-sensitive polymers' is slightly loose and the phrasing is a bit contrived for a search query.
- **Q2 · gpt-5.4-mini** (DISCARDED, faith 4.00, quality 3.25, ling 5): How can a photocurable resin be made suitable for thick-film curing while still giving a flexible, heat-resistant cured product?  
  — *has favorable thick film curability and of which the cured product after curing is excellent in flexibility and heat resistance*  
  reason: The question asks 'how' but the answer merely restates the properties rather than the means (the composition components), so the answer fragment does not respond to the question and the wording largely copies the abstract.
- **Q3 · gpt-5-mini** (kept, faith 5.00, quality 3.75, ling 5): What combination of ingredient types is used to formulate a photocurable resin that yields flexible, heat-resistant cured films?  
  — *includes component (A): a polyorganosiloxane having one or more vinyl groups in one molecule, component (B): a compound having one or more mercapto groups in one molecule, component (C): a photoinitiator, and component (D): hollow resin particles.*  
  reason: Well-formed, natural query with an exactly grounded answer, though it reuses 'photocurable resin' and omits the thick-film aspect.
- **Q4 · sonnet-4.6** (kept, faith 4.33, quality 4.25, ling 5): What approach addresses the challenge of achieving deep-section light cure in flexible, heat-stable coatings?  
  — *a photocurable resin composition which has favorable thick film curability and of which the cured product after curing is excellent in flexibility and heat resistance*  
  reason: Nicely paraphrased conceptual query ('deep-section light cure'), answer is a grounded span, though it is a somewhat circular restatement and the query could match other thick-film photocure patents.
- **Q5 · gemini-3.5-flash** (kept, faith 4.33, quality 4.25, ling 5): What type of material formulation is designed to solve the issue of poor depth-of-cure in thick coatings while maintaining thermal stability and bendability?  
  — *photocurable resin composition which has favorable thick film curability and of which the cured product after curing is excellent in flexibility and heat resistance*  
  reason: Strong paraphrase with a grounded span, but the answer is generic ('photocurable resin composition...') and the question slightly overstates the passage by framing 'poor depth-of-cure' as a solved problem, which the abstract only implies.
- **Q6 · grok-4.3** (kept, faith 5.00, quality 4.50, ling 4): What components form the basis of a resin that relies on addition reactions between silicon-containing polymers and sulfur-based molecules for light-induced hardening along with filler particles?  
  — *includes component (A): a polyorganosiloxane having one or more vinyl groups in one molecule, component (B): a compound having one or more mercapto groups in one molecule, component (C): a photoinitiator, and component (D): hollow resin particles.*  
  reason: Highly distinctive conceptual query (thiol-ene chemistry inferred from vinyl siloxane plus mercapto compound) with exact answer, though the inference about 'addition reactions' is not stated in the passage and 'filler particles' is a loose gloss on hollow resin particles; sentence is long.

## WO-2025212655-A1  ·  semantic mode  ·  question language: de

> Most answers leave key terms (concatemer template molecules, rolling circle amplification, capture/pinning primers) in English within German text; Q1 is the weakest due to generic wording, Q2 the most retrievable.

- **Q1 · gpt-5-mini** (DISCARDED, faith 5.00, quality 3.25, ling 4): Welcher Ansatz wird vorgeschlagen, um zahlreiche Vorlagen direkt auf einem festen Träger zu erzeugen?  
  — *In einigen Ausführungsformen können die concatemer template molecules erzeugt werden, indem rolling circle amplification-Reaktionen auf einem Support durchgeführt werden, der eine Mischung aus immobilisierten capture und pinning primers enthält.*  
  reason: Answer is faithful, but 'zahlreiche Vorlagen auf einem festen Träger' is too generic to single out this passage (no hint of RCA, concatemers or nanoballs).
- **Q2 · grok-4.3** (kept, faith 5.00, quality 4.00, ling 4): Welcher Amplifikationsmechanismus auf einem Träger mit gemischten Primern erzeugt kompakte, stabil haftende DNA-Strukturen?  
  — *In einigen Ausführungsformen können die Concatemer template molecules durch Durchführung von Rolling circle amplification Reaktionen auf einem Support erzeugt werden, der eine Mischung aus immobilisierten Capture- und Pinning-Primern umfasst.*  
  reason: Well-paraphrased concept query combining mixed primers, on-support amplification and compact stably attached DNA structures; answer matches the passage.
- **Q3 · sonnet-4.6** (kept, faith 4.67, quality 3.75, ling 5): Wie lassen sich DNA-Vorlagen für hochdurchsatzfähige Sequenzierläufe stabil auf einer festen Oberfläche verankern?  
  — *Die concatemer template molecules können durch die Durchführung von rolling circle amplification Reaktionen auf einem Support generiert werden, der eine Mischung aus immobilisierten capture und pinning primers enthält. Die entstehenden Moleküle kollabieren zu kompakten DNA nanoballs, die stabil auf dem Support immobilisiert sind.*  
  reason: Natural query about stably anchoring templates for high-throughput sequencing; answer spans two sentences but is accurate, retrievability moderate.
- **Q4 · gemini-3.5-flash** (kept, faith 4.33, quality 4.00, ling 5): Wie wird verhindert, dass die langen synthetisierten DNA-Stränge frei in Lösung driften oder unkontrolliert viel Platz auf dem Substrat einnehmen?  
  — *Die Concatemer-Templatmoleküle kollabieren zur Bildung kompakter DNA-Nanoballs, die stabil auf einem Träger immobilisiert sind.*  
  reason: Highly paraphrased problem-oriented framing; the 'drifting/space' motivation is inferred rather than stated, but the nanoball collapse answer is supported.
- **Q5 · qwen3.6-35b-a3b** (kept, faith 5.00, quality 3.75, ling 5): Welche Strategie nutzt man, um DNA-Fragmente direkt auf einem festen Träger zu replizieren und dabei eine hohe lokale Dichte zu erreichen?  
  — *Die concatemer template molecules können durch die Durchführung von rolling circle amplification Reaktionen auf einem Träger erzeugt werden, der ein Gemisch aus immobilisierten capture und pinning primers umfasst.*  
  reason: Fluent conceptual query; 'hohe lokale Dichte' is a loose inference from compact nanoballs, but the RCA-on-mixed-primer answer is faithful.
- **Q6 · gpt-5.4-mini** (kept, faith 4.67, quality 3.75, ling 5): Wie werden die Amplifikationsprodukte so verdichtet, dass sie fest auf dem Träger verbleiben?  
  — *concatemer template molecules, die zu compact DNA nanoballs kollabieren und stabil auf einem support immobilisiert sind*  
  reason: Concise, paraphrased query on densifying amplification products for stable attachment; answer is a correct though fragmentary span.

## WO-2025215167-A1  ·  semantic mode  ·  question language: de

> All six answers are verbatim spans of the German abstract, so faithfulness is uniformly high. Q1–Q5 are near-ties in semantic quality; Q6 is the most keyword-heavy and least semantic. Several questions (Q1, Q4, Q5) add small unsupported premises ('dauerhaft', 'robust', 'ohne Quanteneigenschaften zu verlieren') that the abstract does not state.

- **Q1 · sonnet-4.6** (kept, faith 5.00, quality 4.00, ling 5): Wie lassen sich dotierte Nanodiamanten dauerhaft in eine Oxidkeramikschicht einbetten, ohne ihre Quanteneigenschaften zu verlieren?  
  — *Die Beschichtung aus Zirconium(IV)-oxid wird durch einen Sol-Gel-Prozess aus einer flüssigen Phase mit darin verteilten dotierten Nanodiamanten auf einem Substrat abgeschieden und nach ihrer Trocknung durch einen Kalzinierungsprozess bei erhöhter Temperatur in einen kristallinen Zustand überführt.*  
  reason: Well-paraphrased conceptual query with an answer lifted verbatim from the passage, though the 'ohne Quanteneigenschaften zu verlieren' premise is not addressed in the abstract.
- **Q2 · gpt-5.4-mini** (kept, faith 5.00, quality 3.75, ling 5): Wie kann man Quantensensoren direkt in eine ZrO2-Beschichtung auf einem Träger integrieren?  
  — *eine Beschichtung aus Zirconium(IV)-oxid, welche durch einen Sol-Gel-Prozess aus einer flüssigen Phase mit darin verteilten dotierten Nanodiamanten auf einem Substrat abgeschieden*  
  reason: Natural query using ZrO2/Quantensensoren abstraction; answer is a faithful contiguous span, question is fluent German.
- **Q3 · gemini-3.5-flash** (kept, faith 5.00, quality 3.75, ling 5): Mit welcher Methode lässt sich eine nanostrukturierte Beschichtung auf Zirconiumbasis herstellen, die gleichmäßig verteilte Quantensensoren enthält?  
  — *durch einen Sol-Gel-Prozess aus einer flüssigen Phase mit darin verteilten dotierten Nanodiamanten auf einem Substrat abgeschieden*  
  reason: Answer span is exact; question paraphrases well, though 'nanostrukturiert' is a mild interpretive addition not in the passage.
- **Q4 · qwen3.6-35b-a3b** (kept, faith 5.00, quality 4.00, ling 5): Wie kann eine robuste Oxidschicht gefertigt werden, die funktionale Nanopartikel gleichmäßig verteilt und anschließend eine definierte Kristallstruktur ausbildet?  
  — *Eine Beschichtung aus Zirconium(IV)-oxid, welche durch einen Sol-Gel-Prozess aus einer flüssigen Phase mit darin verteilten dotierten Nanodiamanten auf einem Substrat abgeschieden und nach Ihrer Trocknung durch einen Kalzinierungsprozess bei erhöhter Temperatur in einen kristallinen Zustand überfuhrt wird, in dem das Zirconium(IV)-oxid zum überwiegendem Anteil in seiner tetragonalen Phase vorliegt.*  
  reason: Highly abstracted conceptual framing with full verbatim answer, but 'robust' is unsupported and the generic wording (Oxidschicht, funktionale Nanopartikel) weakens retrievability.
- **Q5 · grok-4.3** (kept, faith 5.00, quality 3.75, ling 5): Wie können Quantensensoren dauerhaft in eine keramische Oxid-Schicht auf Oberflächen eingebracht werden?  
  — *Die Erfindung betrifft eine Beschichtung aus Zirconium(IV)-oxid, welche durch einen Sol-Gel-Prozess aus einer flüssigen Phase mit darin verteilten dotierten Nanodiamanten auf einem Substrat abgeschieden und nach Ihrer Trocknung durch einen Kalzinierungsprozess bei erhöhter Temperatur in einen kristallinen Zustand überfuhrt wird, in dem das Zirconium(IV)-oxid zum überwiegendem Anteil in seiner tetragonalen Phase vorliegt.*  
  reason: Fluent conceptual query with verbatim answer; 'dauerhaft' is not supported and 'keramische Oxid-Schicht auf Oberflächen' is somewhat generic.
- **Q6 · gpt-5-mini** (kept, faith 5.00, quality 3.25, ling 5): Welches Herstellungsverfahren wird vorgeschlagen, um eine Zirconium(IV)-oxid-Schicht mit eingebrachten dotierten Nanodiamanten auf einem Substrat zu erzeugen?  
  — *Die Erfindung betrifft eine Beschichtung aus Zirconium(IV)-oxid, welche durch einen Sol-Gel-Prozess aus einer flüssigen Phase mit darin verteilten dotierten Nanodiamanten auf einem Substrat abgeschieden und nach Ihrer Trocknung durch einen Kalzinierungsprozess bei erhöhter Temperatur in einen kristallinen Zustand überfuhrt wird.*  
  reason: Highly retrievable and faithful, but reuses the passage's exact terms (Zirconium(IV)-oxid, dotierte Nanodiamanten, Substrat) and asks for a fact rather than a concept.
