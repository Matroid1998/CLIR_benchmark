# Keep/discard disagreements between the human and the LLM annotators

One entry per question where at least one LLM annotator disagrees with the human keep decision. LLM one-sentence reasons are quoted verbatim.

## human keeps, both LLMs discard (26)

- **EP-4504821-A1 · gpt-5-mini** (technical, es): ¿Qué valores puede tener k1?  
  — *k1 is 0, 1, 2 or 3*  
  human: faith 5.0, quality 4.0 · Claude: no (faith 5.0, quality 2.75) — Answer matches the passage exactly, but asking for the values of k1 with no subject context makes the question useless for retrieval.  
  GPT: no (faith 5.0, quality 3.0) — Aunque la respuesta enumera fielmente los valores de k1, la consulta aislada carece de contexto químico y difícilmente recuperaría este documento concreto.

- **EP-4504821-A1 · gpt-5.4-mini** (technical, es): ¿Qué valores puede tomar b?  
  — *0 o un número entero de 1 to 500*  
  human: faith 5.0, quality 3.5 · Claude: no (faith 5.0, quality 2.75) — Duplicate of Q1 with a mixed-language answer ('1 to 500'); faithful but entirely unanchored and unspecific.  
  GPT: no (faith 5.0, quality 3.0) — El intervalo para b es fiel y exacto, pero la variable b sin fórmula ni contexto químico hace que la consulta sea demasiado genérica para recuperación.

- **EP-4504821-A1 · grok-4.3** (technical, es): ¿Qué valores puede tomar b?  
  — *0 o un entero de 1 a 500*  
  human: faith 5.0, quality 3.5 · Claude: no (faith 5.0, quality 2.75) — Answer is exact, but 'what values can b take' has no anchoring context at all and would match countless patents with a variable b.  
  GPT: no (faith 5.0, quality 3.0) — La respuesta está plenamente respaldada, pero preguntar solo por los valores de b no distingue esta patente de numerosos documentos técnicos no relacionados.

- **EP-4504821-A1 · qwen3.6-35b-a3b** (technical, es): ¿Cuáles son los valores permitidos para b?  
  — *0 or an integer from 1 to 500*  
  human: faith 5.0, quality 3.5 · Claude: no (faith 5.0, quality 2.75) — Correct answer (in English rather than Spanish), but the question is context-free and cannot narrow retrieval to this document.  
  GPT: no (faith 5.0, quality 3.0) — La respuesta inglesa coincide exactamente con el pasaje, pero la pregunta española es demasiado descontextualizada y genérica para funcionar como consulta de búsqueda.

- **EP-4584229-A1 · grok-4.3** (technical, es): ¿Qué representa el resto R en la fórmula R-NR'H?  
  — *un linear or branched, optionally substituted hydrocarbon group con 1 to 20 carbon atoms*  
  human: faith 5.0, quality 4.5 · Claude: no (faith 5.0, quality 3.25) — Answer is a Spanish/English mash-up ('un ... con') and the question lacks any discriminative context.  
  GPT: no (faith 5.0, quality 4.25) — La pregunta en sí es correcta y enfocada, pero la respuesta mezcla español e inglés de forma gramaticalmente defectuosa, lo que reduce su idoneidad para el benchmark.

- **EP-4627127-A1 · gpt-5-mini** (technical, de): Welche Festigkeit weisen die resultierenden Aluminiumlegierungsprodukte auf?  
  — *hohe Festigkeit*  
  human: faith 5.0, quality 4.75 · Claude: no (faith 5.0, quality 2.75) — Answer 'hohe Festigkeit' is supported, but the question is vacuous (asks for a strength value and gets 'high'), generic, and useless for retrieval.  
  GPT: no (faith 5.0, quality 3.5) — Die hohe Festigkeit ist korrekt belegt, aber die Abfrage ist als Suchanfrage zu generisch und könnte auf sehr viele Aluminiumlegierungspatente zutreffen.

- **EP-4630021-A1 · gpt-5.4-mini** (technical, de): Welche Eigenschaften hat das flüssige Injektionsprodukt?  
  — *clear, safe, and physiologically and biologically active*  
  human: faith 5.0, quality 4.5 · Claude: no (faith 5.0, quality 2.75) — Answer is exact, but 'Welche Eigenschaften hat das flüssige Injektionsprodukt' lacks any equine/placental anchor and would match countless injectable documents.  
  GPT: no (faith 5.0, quality 3.5) — The answer is directly supported and the question is fluent, but the generic reference to „das flüssige Injektionsprodukt“ is too underspecified to retrieve this document reliably.

- **EP-4633791-A1 · gpt-5.4-mini** (semantic, zh): 这类带香味的消费品更偏向哪些日常护理场景？  
  — *家居护理或个人护理产品*  
  human: faith 4.67, quality 4.5 · Claude: no (faith 5.0, quality 2.25) — Answer is correct, but the question is anaphoric ('这类') and generic, with awkward phrasing ('更偏向'), so it would not retrieve this passage over any other perfumed-product document.  
  GPT: no (faith 5.0, quality 3.25) — 答案准确对应原文的家居护理和个人护理场景，但“这类”缺乏独立指代且问题未提及蛋白质微胶囊，难以有效定位该文献。

- **MX-2025002756-A · gpt-5-mini** (technical, en): What is the weight percent range of Cu in the alloy?  
  — *59 to 62 wt % Cu*  
  human: faith 5.0, quality 4.5 · Claude: no (faith 5.0, quality 3.5) — Correct answer, but 'the alloy' gives no context (not even brass or lead-free), making it arbitrary as a retrieval query.  
  GPT: no (faith 5.0, quality 3.5) — The copper range is reproduced exactly, but the generic reference to “the alloy” gives the query little power to retrieve this particular document.

- **MX-2025002756-A · qwen3.6-35b-a3b** (technical, en): What is the maximum allowable lead content in the alloy?  
  — *less than 0.1 wt %*  
  human: faith 4.67, quality 4.5 · Claude: no (faith 5.0, quality 3.5) — Answer is correct but 'the alloy' is unanchored, so the query would match countless lead-limited alloy documents.  
  GPT: no (faith 5.0, quality 3.75) — The answer exactly matches the stated lead threshold, but the standalone query is underspecified because “the alloy” does not identify lead-free brass.

- **MX-2025007206-A · gpt-5-mini** (technical, de): Welche Lagertemperatur wird für langfristige Aufbewahrung genannt?  
  — *temperatures above -80 °C*  
  human: faith 5.0, quality 4.0 · Claude: no (faith 5.0, quality 3.0) — The answer is faithful, but the query names no rAAV/formulation anchor and is phrased as a meta-question about what the text 'nennt', so it would match arbitrary storage-temperature documents.  
  GPT: no (faith 5.0, quality 3.5) — Die Antwort ist ein exakter Passagenspan, aber die Frage nennt weder rAAV noch Formulierungen und ist daher für eine technische Suche zu unspezifisch.

- **MX-2025009131-A · gpt-5-mini** (technical, zh): 聚合物由哪类聚合物组成？  
  — *one or more non-cross-linked thermoplastic polymers that are recyclable and/or biodegradable*  
  human: faith 5.0, quality 5.0 · Claude: no (faith 5.0, quality 3.0) — Answer is exact, but the question ('what kind of polymer is the polymer composed of') has no anchoring context and would match countless polymer documents.  
  GPT: no (faith 5.0, quality 3.25) — 答案是原文的直接连续表述，但“聚合物由哪类聚合物组成”措辞重复、缺少工艺语境且难以锁定该文献。

- **MX-2025009131-A · gpt-5.4-mini** (technical, zh): 用于把腔体加压到高压的流体是什么？  
  — *超临界流体*  
  human: faith 5.0, quality 4.0 · Claude: no (faith 5.0, quality 3.5) — Faithful and fluent but too generic ('what fluid pressurizes the chamber') with no domain anchor.  
  GPT: no (faith 5.0, quality 3.5) — 答案忠实且问题只涉及一个事实，但“把腔体加压到高压”略显生硬和重复，且缺少泡沫、高压釜或聚合物等区分性信息。

- **MX-2025009131-A · grok-4.3** (technical, zh): 维持升高压力是为了什么？  
  — *to infuse the supercritical fluid into the polymer*  
  human: faith 5.0, quality 4.5 · Claude: no (faith 5.0, quality 2.75) — Answer is grounded, but 'why maintain elevated pressure' is context-free and arbitrarily generic as a retrieval query.  
  GPT: no (faith 5.0, quality 3.5) — 答案准确说明维持升高压力是为了使超临界流体渗入聚合物，但问题脱离泡沫制造语境后过于宽泛，检索区分度不足。

- **MX-2025010190-A · gpt-5.4-mini** (technical, en): What do the polynucleotides encode?  
  — *the recombinant polypeptides*  
  human: faith 5.0, quality 4.0 · Claude: no (faith 5.0, quality 2.75) — Trivially true of almost any biotech patent; the question cannot narrow to this document at all.  
  GPT: no (faith 5.0, quality 3.0) — Although the answer is fully supported, the query is too generic to distinguish this patent from numerous unrelated documents about polynucleotides.

- **WO-2025054647-A1 · gpt-5.4-mini** (semantic, es): ¿Qué características debe tener la matriz para funcionar bien en un sistema de almacenamiento térmico de este tipo?  
  — *la matriz presentando un coeficiente de difusión de gas para el gas de 2,25*10 -9 m 2 /s a 4,25*10 -9 m 2 /s en una plage de temperatura de -30 °C a 300 °C, y una expansión máxima ε en la plage de ley de Hooke de 25 % a 300 %*  
  human: faith 4.33, quality 4.75 · Claude: no (faith 5.0, quality 2.75) — Question is too generic ('de este tipo') to distinguish this passage, and the answer is a sloppy translation leaving French 'plage' untranslated.  
  GPT: no (faith 5.0, quality 2.75) — La respuesta está respaldada y conserva las cifras, pero la referencia vaga a «un sistema de este tipo» hace que la consulta sea poco autónoma y escasamente discriminativa.

- **WO-2025177605-A1 · gpt-5-mini** (technical, fr): Quel pourcentage d'Al contient l'alliage à base de Ni ?  
  — *2,0% en poids ou plus d'Al*  
  human: faith 4.67, quality 4.75 · Claude: no (faith 5.0, quality 3.0) — Answer is exact, but the question lacks any retort/welding context and 'Ni-based alloy with Al' matches many patents; also asks for 'what percentage' while the answer is a minimum threshold.  
  GPT: no (faith 5.0, quality 3.75) — Bien que la réponse soit exacte, la formulation demande un pourcentage apparemment fixe sans préciser qu’il s’agit d’une teneur minimale, ce qui la rend potentiellement trompeuse.

- **WO-2025177605-A1 · gpt-5.4-mini** (technical, fr): Quel type de soudage est utilisé pour joindre la partie de jonction du matériau de base ?  
  — *soudage au plasma*  
  human: faith 5.0, quality 5.0 · Claude: no (faith 5.0, quality 3.0) — Answer correct but the question lifts 'partie de jonction du matériau de base' verbatim and omits 'cornue', making it generic to any welding patent.  
  GPT: no (faith 5.0, quality 3.5) — La réponse est fidèle, mais l’expression « joindre la partie de jonction » est redondante et maladroite, et la formulation reprend de près celle du passage.

- **WO-2025187661-A8 · gpt-5-mini** (semantic, es): ¿Qué defecto durante el reprocesado en planta pretende evitar esta composición de resina?  
  — *puede ser inhibida de formar rebabas durante el reciclaje.*  
  human: faith 5.0, quality 4.75 · Claude: no (faith 5.0, quality 3.0) — 'Esta composición de resina' presupposes the document is already in hand, so as a standalone retrieval query it is too vague to find this passage among others.  
  GPT: no (faith 5.0, quality 2.5) — La respuesta identifica correctamente las rebabas, pero la consulta es deíctica, poco distinguible fuera de contexto y pide un dato simple en vez de un concepto.

- **WO-2025187661-A8 · gpt-5.4-mini** (semantic, es): ¿Cómo se puede evitar que una resina de poly(arylene sulfide) reciclada genere rebabas?  
  — *que, durante el reciclaje, puede ser impedida de formar burrs*  
  human: faith 4.33, quality 4.25 · Claude: no (faith 4.67, quality 3.5) — Question is fine but the answer is a dangling, half-translated fragment ('puede ser impedida de formar burrs') that mixes languages and does not stand on its own.  
  GPT: no (faith 4.67, quality 4.0) — Es recuperable y está respaldada, pero la respuesta es circular, no ofrece la composición y mezcla innecesariamente español e inglés.

- **WO-2025202347-A1 · qwen3.6-35b-a3b** (semantic, de): Welche Formulierungsstrategie ermöglicht es, iota-carrageenan als zentrales oder einziges therapeutisches Element in einer wässrigen Augenmedikation einzusetzen?  
  — *als Haupt- oder alleiniger Wirkstoff in einer wässrigen pharmazeutischen Zubereitung*  
  human: faith 5.0, quality 5.0 · Claude: no (faith 4.67, quality 3.0) — The passage states no 'formulation strategy'; the question presupposes something absent, and the answer merely restates the claim wording so the question is circular and unrealistic.  
  GPT: no (faith 5.0, quality 3.0) — Die Antwort ist vollständig belegt, doch die Frage nimmt mit „zentrales oder einziges therapeutisches Element“ und „wässriger Augenmedikation“ nahezu den gesamten Antwortinhalt bereits vorweg.

- **WO-2025207810-A1 · gpt-5.4-mini** (technical, zh): 错误校验 barcode nucleotide sequences 基于什么编码？  
  — *Hamming codes*  
  human: faith 5.0, quality 4.5 · Claude: no (faith 5.0, quality 3.5) — Correct answer but unnatural mixed-language phrasing and redundant with Q1/Q3/Q5 which ask the same fact more fluently.  
  GPT: no (faith 5.0, quality 3.5) — 答案与原文一致，但“错误校验 barcode nucleotide sequences”的中英拼接明显生硬，不符合自然中文检索表达。

- **WO-2025210445-A1 · gemini-3.5-flash** (technical, fr): Quelle plage de tension est plus préférentiellement appliquée entre les électrodes ?  
  — *entre 1 V et 20 V*  
  human: faith 5.0, quality 4.0 · Claude: no (faith 5.0, quality 3.25) — Identical to Q4: correct answer but generic, source-lifted phrasing with no document-specific anchor.  
  GPT: no (faith 5.0, quality 3.25) — La réponse correspond exactement à la plage la plus préférentielle, mais la question reprend étroitement le libellé du passage et manque de termes identifiant l'invention.

- **WO-2025210445-A1 · gpt-5-mini** (technical, fr): Plage de tension préférée entre les électrodes  
  — *de préférence entre 0 V et 220 V, plus préférentiellement entre 1 V et 20 V*  
  human: faith 5.0, quality 4.25 · Claude: no (faith 4.67, quality 3.0) — Keyword-style query is realistic but far too generic to single out this patent, and the answer bundles both nested ranges while the question asks for one preferred range.  
  GPT: no (faith 5.0, quality 3.5) — Cette requête nominale convient à une barre de recherche et son answer est exact, mais elle est trop générique et regroupe deux niveaux de préférence sans préciser le procédé concerné.

- **WO-2025210445-A1 · gpt-5.4-mini** (technical, fr): Quelle plage de tension est indiquée comme la plus préférée entre les électrodes ?  
  — *entre 1 V et 20 V*  
  human: faith 5.0, quality 4.25 · Claude: no (faith 5.0, quality 3.25) — Slightly better paraphrased than Q4/Q5 and correct, but still has no topical anchor to this patent and reads awkwardly ('la plus préférée entre les électrodes') rather than like a search query.  
  GPT: no (faith 5.0, quality 3.75) — La réponse est entièrement étayée, mais « la plus préférée » est légèrement maladroit et aucun contexte ne distingue cette plage de celles de nombreux autres dispositifs.

- **WO-2025210445-A1 · qwen3.6-35b-a3b** (technical, fr): Quelle plage de tension est plus préférentiellement appliquée entre les électrodes ?  
  — *entre 1 V et 20 V*  
  human: faith 5.0, quality 4.0 · Claude: no (faith 5.0, quality 3.25) — Faithful and single-fact, but it lacks any anchor to this invention (Fenton, pollutants, water) so it would not narrow retrieval, and it is a near-verbatim lift of the source wording.  
  GPT: no (faith 5.0, quality 3.25) — La plage de 1 V à 20 V est exacte et la demande est ciblée sur un seul fait, mais la formulation proche du passage et dépourvue de contexte technique est peu distinctive.

## human discards, both LLMs keep (9)

- **EP-4627881-A1 · grok-4.3** (semantic, zh): 工业熔化设备中实现多等离子体火焰供应的系统如何构建？  
  — *a plasma generation unit (100) comprising a plurality of devices (10, 10a, 10b)*  
  human: faith 3.67, quality 4.25 · Claude: yes (faith 5.0, quality 4.0) — Natural, fluent query about constructing a multi-plasma-flame system for melting plants, with an answer extracted verbatim from the EN abstract.  
  GPT: yes (faith 5.0, quality 4.0) — 答案精确给出由多个装置构成的等离子体发生单元，且问题将其合理置于工业熔化和多火焰供应的系统构建语境中。

- **EP-4633645-A1 · sonnet-4.6** (technical, fr): Quel marqueur biologique caractérise les maladies neurodégénératives traitées par les composés de formule (I) ?  
  — *Un niveau élevé de phosphorylation de l'ubiquitine Ser65*  
  human: faith 4.33, quality 3.5 · Claude: yes (faith 5.0, quality 4.0) — Best of the set: faithful answer, natural paraphrase ('marqueur biologique'), and the reference to compounds of formula (I) anchors the query to this patent without leaking the answer.  
  GPT: yes (faith 5.0, quality 4.5) — Le marqueur demandé est directement attesté, tandis que la mention des composés de formule (I) rend la requête particulièrement distinctive.

- **EP-4634436-A1 · grok-4.3** (semantic, fr): Comment des gaz inertes injectés aux deux pôles d'une cellule peuvent-ils servir à valider l'existence réelle de membranes défectueuses ?  
  — *au moins l'un du ou des premiers tests sur la base d'une injection de gaz inertes au niveau d'une anode et au niveau d'une cathode de chaque cellule*  
  human: faith 3.33, quality 3.75 · Claude: yes (faith 5.0, quality 4.25) — Conceptual and well grounded, but 'pôles' is an odd substitute for anode/cathode and 'valider l'existence réelle' is slightly awkward, lowering realism.  
  GPT: yes (faith 4.33, quality 4.5) — La question reformule de façon distinctive le rôle diagnostique de l’injection aux deux électrodes, même si la réponse indique seulement qu’un premier test repose sur cette injection sans en expliquer précisément le mécanisme.

- **EP-4634436-A1 · sonnet-4.6** (semantic, fr): Comment l'injection de gaz inertes côté anode et côté cathode peut-elle être exploitée pour diagnostiquer l'intégrité des séparateurs dans un système d'électrolyse ?  
  — *au moins l'un du ou des premiers tests sur la base d'une injection de gaz inertes au niveau d'une anode et au niveau d'une cathode de chaque cellule*  
  human: faith 3.33, quality 4.0 · Claude: yes (faith 5.0, quality 4.5) — Conceptual, fluent query with good paraphrase (séparateurs/intégrité) that targets the passage's distinctive inert-gas anode/cathode injection idea; answer span is exact.  
  GPT: yes (faith 4.33, quality 4.75) — La notion d’intégrité des séparateurs constitue une reformulation plausible des membranes endommagées et forme une requête conceptuelle distinctive, bien que la réponse ne détaille pas comment l’injection produit le diagnostic.

- **MX-2025007510-A · gpt-5-mini** (semantic, es): ¿En qué indicación clínica se plantea usar esta formulación y qué beneficio de dosificación aporta?  
  — *tratar hipertensión pulmonar con frecuencia de dosificación reducida.*  
  human: faith 4.0, quality 3.0 · Claude: yes (faith 5.0, quality 3.5) — Faithful and fluent, but 'esta formulación' is context-dependent and the two-part question is less search-like.  
  GPT: yes (faith 5.0, quality 4.25) — La pregunta recupera con claridad tanto la indicación como el beneficio posológico, y la respuesta es un fragmento exacto, pertinente y plenamente respaldado.

- **WO-2022005333-A1 · gpt-5.4-mini** (semantic, en): How can low-value olefin-rich byproduct streams be converted into gasoline with higher octane and yield?  
  — *The method makes it possible to produce gasolines using low-demand olefin-containing fractions, such as dry gas from catalytic cracking, a propane-propylene fraction or a butane-butylene fraction, and to increase the octane rating of the product to 95-98 at a product yield of more than 70 wt%, while also reducing the diesel fraction content to less than 2 wt%*  
  human: faith 3.67, quality 4.0 · Claude: yes (faith 5.0, quality 4.25) — Fully paraphrased, concept-level question with an exact multi-benefit answer span including all numbers; generic enough that it could match other olefin-to-gasoline documents.  
  GPT: yes (faith 4.67, quality 4.0) — The question captures the passage’s combined feedstock-valorization and performance concept with exact figures, although the answer adds an unrequested diesel-content result.

- **WO-2022005333-A1 · grok-4.3** (semantic, en): How can low-demand refinery gases like catalytic cracking dry gas be upgraded into gasoline?  
  — *produce gasolines using low-demand olefin-containing fractions, such as dry gas from catalytic cracking, a propane-propylene fraction or a butane-butylene fraction*  
  human: faith 3.67, quality 4.0 · Claude: yes (faith 5.0, quality 4.0) — Natural, concise 'how can X be upgraded' query with an exact answer span; lexical distance is moderate since 'low-demand' and 'catalytic cracking dry gas' echo the passage.  
  GPT: yes (faith 5.0, quality 4.25) — The concise query naturally frames upgrading catalytic-cracking gas as a resource-use concept, and its answer is a precise source span despite moderate vocabulary overlap.

- **WO-2022005333-A1 · sonnet-4.6** (semantic, en): How can low-value refinery off-gases like propane-propylene or butane-butylene cuts be converted into high-octane gasoline?  
  — *The method makes it possible to produce gasolines using low-demand olefin-containing fractions, such as dry gas from catalytic cracking, a propane-propylene fraction or a butane-butylene fraction, and to increase the octane rating of the product to 95-98 at a product yield of more than 70 wt%*  
  human: faith 3.67, quality 4.0 · Claude: yes (faith 5.0, quality 4.25) — Answer span exactly reproduces the 95-98 and >70 wt% figures; 'high-octane gasoline' plus the named cuts make it highly retrievable, though calling propane-propylene cuts 'off-gases' is a slight terminological stretch.  
  GPT: yes (faith 4.67, quality 4.5) — The answer is directly grounded and numerically exact, while the query offers a natural, specific conceptual framing despite including yield information beyond the main request.

- **WO-2025212655-A1 · gemini-3.5-flash** (semantic, de): Wie wird verhindert, dass die langen synthetisierten DNA-Stränge frei in Lösung driften oder unkontrolliert viel Platz auf dem Substrat einnehmen?  
  — *Die Concatemer-Templatmoleküle kollabieren zur Bildung kompakter DNA-Nanoballs, die stabil auf einem Träger immobilisiert sind.*  
  human: faith 3.33, quality 4.0 · Claude: yes (faith 4.33, quality 4.0) — Highly paraphrased problem-oriented framing; the 'drifting/space' motivation is inferred rather than stated, but the nanoball collapse answer is supported.  
  GPT: yes (faith 5.0, quality 4.5) — The answer directly captures the disclosed collapse into compact, stably immobilized DNA nanoballs, while the question provides a strong conceptual paraphrase of that function.

## human keeps, one LLM discards (33)

- **EP-4577789-A1 · gpt-5-mini** (technical, zh): 冷却气体由哪个管道引导至预热区？  
  — *冷却气体管道 (44)*  
  human: faith 5.0, quality 4.5 · Claude: no (faith 5.0, quality 3.25) — Nearly tautological — asking which duct conducts the cooling gas and answering 'cooling gas duct' yields little discriminative value as a benchmark question.  
  GPT: yes (faith 5.0, quality 3.75) — 答案“冷却气体管道 (44)”与原文完全一致，问题简洁明确，但单独作为检索词时对具体专利的限定较弱。

- **EP-4584229-A1 · gpt-5-mini** (technical, es): ¿Qué representa R en la fórmula R-NR'H?  
  — *a linear or branched and optionally substituted hydrocarbon group with 1 to 20 carbon atoms*  
  human: faith 5.0, quality 4.5 · Claude: no (faith 5.0, quality 3.0) — Faithful but maximally generic: R in R-NR'H without any context would match countless amine patents.  
  GPT: yes (faith 5.0, quality 4.25) — La pregunta es fluida y solicita una única definición plenamente respaldada, aunque carece del contexto de las composiciones de dispersión y por ello tiene especificidad moderada.

- **EP-4584229-A1 · gpt-5.4-mini** (technical, es): ¿Qué rango de carbonos tiene R en R-NR'H?  
  — *1 to 20 carbon atoms*  
  human: faith 5.0, quality 4.5 · Claude: no (faith 5.0, quality 3.75) — Telegraphic and vague ('rango de carbonos'), no document context, and near-duplicate of Q1/Q4.  
  GPT: yes (faith 5.0, quality 3.75) — El rango está fielmente respaldado y la consulta se centra en un solo dato, aunque «rango de carbonos» es menos preciso que «rango de átomos de carbono».

- **EP-4584229-A1 · sonnet-4.6** (technical, es): ¿Qué representa el grupo R en la fórmula R-NR'H de los amino compounds utilizados en composiciones de polvos de dispersión?  
  — *a linear or branched and optionally substituted hydrocarbon group with 1 to 20 carbon atoms*  
  human: faith 5.0, quality 4.75 · Claude: yes (faith 5.0, quality 3.5) — Most specific question thanks to the dispersion-powder context, though the untranslated 'amino compounds' mars the Spanish.  
  GPT: no (faith 5.0, quality 4.0) — La respuesta reproduce fielmente la definición completa de R y el contexto es específico, pero el uso innecesario de «amino compounds» rompe la fluidez de una pregunta en español.

- **EP-4627127-A1 · sonnet-4.6** (technical, de): Für welchen Anwendungsbereich sind diese formbaren, korrosionsbeständigen Aluminiumlegierungen vorgesehen?  
  — *structural component*  
  human: faith 4.67, quality 4.75 · Claude: no (faith 5.0, quality 3.5) — Grounded, but the answer is in English while the question is German, 'diese' makes the question deictic and not standalone, and it duplicates Q1.  
  GPT: yes (faith 4.67, quality 4.25) — Der Titel stützt den Einsatz für ein Strukturbauteil eindeutig, auch wenn die englische Antwort sprachlich weniger gut zur deutschen Frage passt.

- **EP-4627881-A1 · gpt-5-mini** (semantic, zh): 有哪些专用硬件可以直接生成工业用等离子体火焰？  
  — *用于生成至少一种等离子体火焰(12)的装置(10, 10a, 10b)。*  
  human: faith 4.0, quality 4.0 · Claude: no (faith 5.0, quality 2.75) — Fluent but extremely generic ('what hardware generates industrial plasma flames') and would match countless plasma torch documents; answer is faithful but trivial.  
  GPT: yes (faith 5.0, quality 3.25) — 答案准确对应生成至少一种等离子体火焰的装置，但问题主要询问单一事实，且“工业用”使表述略宽于原文。

- **EP-4630021-A1 · qwen3.6-35b-a3b** (technical, de): Welche Komponenten bleiben nach der Aufbereitung des Injektionsprodukts erhalten?  
  — *postbiotics, proteins, exosomes, biocomponents*  
  human: faith 5.0, quality 5.0 · Claude: no (faith 5.0, quality 3.5) — Answer list is exact and the question is well paraphrased, but 'Injektionsprodukt' alone gives no equine/amnion/placenta cue, so it barely narrows to this patent.  
  GPT: yes (faith 5.0, quality 4.0) — The preserved components are extracted exactly from the passage, and the focused query is useful despite being somewhat generic and slightly imprecise about what undergoes processing.

- **EP-4633645-A1 · gemini-3.5-flash** (technical, fr): Quel état de l'ubiquitine Ser65 caractérise les pathologies neurodégénératives ciblées ?  
  — *un niveau élevé de phosphorylation de l'ubiquitine Ser65*  
  human: faith 4.0, quality 3.0 · Claude: no (faith 5.0, quality 3.0) — Answer is faithful, but 'Quel état de l'ubiquitine Ser65' is an unnatural formulation that leaks the key term and reads poorly as a search query.  
  GPT: yes (faith 5.0, quality 4.5) — La réponse est intégralement fondée et la paraphrase est efficace, bien que le terme « état » soit légèrement moins précis que « niveau de phosphorylation ».

- **EP-4633645-A1 · grok-4.3** (technical, fr): Quel niveau de phosphorylation de l'ubiquitine Ser65 caractérise les maladies neurodégénératives traitées ?  
  — *niveau élevé*  
  human: faith 5.0, quality 4.25 · Claude: no (faith 5.0, quality 2.75) — Answer is exact, but the question gives away the key terms and asks only for a trivial qualifier ('élevé'), reading more like a cloze test than a search query.  
  GPT: yes (faith 5.0, quality 3.75) — La réponse « niveau élevé » est exacte et répond précisément à la question, même si la formulation reste très proche du texte source.

- **EP-4633645-A1 · qwen3.6-35b-a3b** (technical, fr): Quelle modification biochimique spécifique est élevée dans les affections neurodégénératives ciblées ?  
  — *un niveau élevé de phosphorylation de l'ubiquitine Ser65*  
  human: faith 4.67, quality 3.75 · Claude: yes (faith 5.0, quality 3.5) — Well-paraphrased single-fact question with an exact answer, though 'affections neurodégénératives ciblées' alone does not strongly narrow to this document.  
  GPT: no (faith 4.67, quality 3.75) — La réponse est bien extraite, mais la question omet l'ubiquitine Ser65 et la formule (I), ce qui la rend trop générique pour retrouver spécifiquement ce document.

- **EP-4633791-A1 · grok-4.3** (semantic, zh): 蛋白质基微胶囊适合加入到哪些家用或个人护理产品中发挥作用？  
  — *香味组合物和包含所述微胶囊的消费产品，特别是以家用护理或个人护理产品形式存在的香味消费产品*  
  human: faith 4.0, quality 4.0 · Claude: yes (faith 4.67, quality 3.5) — Answer is a faithful rendering of the abstract's application sentence; question is a plausible query naming protein microcapsules and home/personal care, though fairly close to the passage wording.  
  GPT: no (faith 4.67, quality 3.25) — 答案有原文依据，但问题已直接给出“家用或个人护理”这一核心答案线索，且“发挥作用”的表述没有得到说明。

- **EP-4634436-A1 · gemini-3.5-flash** (semantic, fr): Quel protocole de validation applique-t-on suite à la substitution de composants détériorés pour garantir l'absence de pannes résiduelles ?  
  — *l'exécution d'un deuxième test pour évaluer s'il reste au moins une autre cellule endommagée*  
  human: faith 4.67, quality 5.0 · Claude: no (faith 5.0, quality 3.5) — Heavily paraphrased and accurate, but so abstracted (components, faults, validation protocol) that it would match countless maintenance documents and not retrieve this electrolyzer passage.  
  GPT: yes (faith 4.67, quality 4.0) — Le deuxième test après remplacement est bien décrit et fortement paraphrasé, quoique « garantir » soit légèrement plus fort que la simple évaluation mentionnée dans le passage.

- **MX-2025005046-A · gemini-3.5-flash** (semantic, de): Wie kann die Verweilzeit und Konzentration von aktivem Sauerstoff bei einer physikalischen Desinfektionsmethode künstlich verlängert und erhöht werden?  
  — *Das doppelte Magnetringpaar ist so konfiguriert, dass es die lokalen Magnetfelder intensiviert, die Anzahl und die mittlere Lebensdauer der radikalisierten Sauerstoffmoleküle erhöht und die Wasserreinigung verbessert.*  
  human: faith 4.0, quality 4.5 · Claude: yes (faith 5.0, quality 4.0) — Answer matches the magnetic ring sentence exactly; question is heavily paraphrased ('Verweilzeit', 'aktiver Sauerstoff') but 'künstlich' and the lack of any water/magnet cue weaken realism and retrievability.  
  GPT: no (faith 4.33, quality 3.75) — Die Antwort ist zwar textnah, doch die Frage setzt chemische Lebensdauer mit Verweilzeit und Molekülzahl mit Konzentration gleich und führt zudem den nicht ausdrücklich belegten Desinfektionsbegriff ein.

- **MX-2025005046-A · gpt-5-mini** (semantic, de): Welcher mechanische oder physikalische Mechanismus wird eingesetzt, um die Zahl und Lebensdauer reaktiver Sauerstoffspezies zu erhöhen und dadurch die Reinigung zu verbessern?  
  — *Die doppelten Paare magnetischer Ringe sind so konfiguriert, die lokalen Magnetfelder zu verstärken, die Anzahl und die mittlere Lebensdauer radikalisierten Sauerstoffmolekülen zu erhöhen und die Wasserreinigung zu verbessern.*  
  human: faith 5.0, quality 5.0 · Claude: no (faith 5.0, quality 3.5) — Answer is grounded but has a grammar error ('radikalisierten Sauerstoffmolekülen' should be genitive 'radikalisierter Sauerstoffmoleküle') and the question is long, never mentions water, and largely duplicates Q3/Q5.  
  GPT: yes (faith 5.0, quality 4.25) — Der gesuchte physikalische Mechanismus und seine Wirkung sind vollständig belegt, auch wenn die Formulierung „mechanische oder physikalische“ etwas redundant wirkt.

- **MX-2025006624-A · gpt-5-mini** (semantic, fr): Comment la formulation intègre-t-elle un monomère d'origine biobasée dans un revêtement curable par rayonnement actinique ?  
  — *La composition comprend de 10 wt% à 90 wt%, basé sur le poids total de la composition, d'un poly(trimethylene ether) (meth)acrylate compound A ayant au plus deux groupes (meth)acrylate, obtenable par une réaction de condensation de biobased 1,3 poly(trimethylene ether) glycol et d'un composé de (meth)acrylate sélectionné dans le groupe constitué par (meth)acrylic acid, (meth)acryloyl chloride et/ou leurs alkylesters; wherein the biobased 1,3 poly(trimethylene ether) glycol has a number average molecular weight Mn of from 350 to 600 g/mol, more preferably from 400 to 550 g/mol.*  
  human: faith 5.0, quality 4.75 · Claude: no (faith 4.67, quality 2.75) — Faithful but the answer is a long, half-translated English/French mash-up with padding, and the question largely reuses passage vocabulary with a redundant 'origine biobasée'.  
  GPT: yes (faith 4.67, quality 3.75) — La réponse décrit fidèlement l'incorporation du composé A avec des valeurs exactes, bien que le détail sur la masse moléculaire soit légèrement plus développé que nécessaire et que la paraphrase soit limitée.

- **MX-2025006624-A · gpt-5.4-mini** (semantic, fr): Comment rendre un revêtement durcissable par radiation actinique tout en utilisant un monomère issu d’un glycol biobasé ?  
  — *une composition de revêtement durcissable par radiation actinique comprenant de 10 wt% à 90 wt% d’un composé A de poly(trimethylene ether) (meth)acrylate*  
  human: faith 4.67, quality 5.0 · Claude: yes (faith 5.0, quality 3.5) — Answer is a faithful extract; question is a natural, moderately paraphrased problem-style query, though 'comment rendre' is slightly awkward and the query is somewhat generic.  
  GPT: no (faith 5.0, quality 3.75) — Le constituant et sa teneur sont correctement repris, mais la réponse n'indique pas explicitement que le composé A provient du glycol biobasé mentionné dans la question.

- **MX-2025007510-A · gemini-3.5-flash** (semantic, es): ¿Qué trastorno circulatorio se pretende tratar disminuyendo la cantidad de tomas diarias de la terapia?  
  — *tratar hipertensión pulmonar con frecuencia de dosificación reducida*  
  human: faith 3.33, quality 3.75 · Claude: yes (faith 5.0, quality 4.25) — Well paraphrased (trastorno circulatorio, tomas diarias) and tightly answered from the passage.  
  GPT: no (faith 4.33, quality 3.5) — La hipertensión pulmonar está correctamente identificada, pero «tomas diarias» introduce una periodicidad no especificada y la pregunta se limita principalmente a recuperar una indicación clínica factual.

- **MX-2025007510-A · gpt-5.4-mini** (semantic, es): ¿Qué tipo de formulación se usa para encapsular un fármaco de ácido débil de vida media corta?  
  — *una composición farmacéutica que contiene liposomas, el liposoma comprende una bicapa de lípido externa; y un medio acuoso interno que incluye 5 un fármaco de ácido débil con una vida media de menos de 2 hours.*  
  human: faith 4.33, quality 3.5 · Claude: yes (faith 4.33, quality 3.75) — Good paraphrased concept question, but the answer span is over-long, carries the OCR artifact '5' and mixes in English 'hours'.  
  GPT: no (faith 4.0, quality 3.75) — La formulación liposomal y la vida media están respaldadas, pero la respuesta es innecesariamente extensa, conserva el artefacto «5» y mezcla español e inglés en lugar de dar el tipo de formulación de manera limpia.

- **MX-2025007510-A · sonnet-4.6** (semantic, es): ¿Qué estrategia de encapsulación lipídica permite reducir la frecuencia de administración en el tratamiento de la hipertensión pulmonar?  
  — *el uso de la composición farmacéutica descrita en la presente para tratar hipertensión pulmonar con frecuencia de dosificación reducida*  
  human: faith 4.0, quality 4.75 · Claude: yes (faith 4.67, quality 4.5) — Combines encapsulation strategy with the indication and dosing benefit, making it highly distinctive and well grounded.  
  GPT: no (faith 4.33, quality 4.5) — Aunque el fragmento de respuesta está literalmente respaldado, no identifica de forma autónoma la estrategia de encapsulación solicitada y depende de la referencia vaga a «la composición descrita».

- **MX-2025009131-A · qwen3.6-35b-a3b** (technical, zh): 为升高腔室或型腔压力使用的是何种流体？  
  — *超临界流体*  
  human: faith 5.0, quality 4.5 · Claude: no (faith 5.0, quality 3.5) — Correct answer and decent paraphrase, but lacks the foam/polymer context needed to narrow to this document.  
  GPT: yes (faith 5.0, quality 4.0) — 答案准确对应原文中的超临界流体，问题简洁且只问一个事实，但未提及柔性泡沫或高压釜，检索特异性一般。

- **MX-2025010190-A · gpt-5-mini** (technical, en): What amino acid profile does the recombinant polypeptide have?  
  — *a nutritionally complete amino acid profile*  
  human: faith 5.0, quality 4.5 · Claude: no (faith 5.0, quality 3.25) — Answer is exact, but 'recombinant polypeptide' with 'amino acid profile' is generic and the question gives little to distinguish this patent from many others.  
  GPT: yes (faith 5.0, quality 3.75) — The question is accurate, concise, and single-focused, although it provides less document-specific context and closely echoes the passage.

- **MX-2025010190-A · grok-4.3** (technical, en): What forms of polypeptide are suitable to provide a nutritionally complete amino acid profile when provided in a nutritional composition?  
  — *a recombinant polypeptide and variants and truncates thereof*  
  human: faith 5.0, quality 5.0 · Claude: no (faith 5.0, quality 3.0) — Answer is verbatim-supported and the query is specific, but the question is lifted almost word-for-word from the abstract and reads as a sentence, not a search query.  
  GPT: yes (faith 5.0, quality 3.75) — The answer is directly extracted and highly specific, but the question is somewhat cumbersome and reproduces much of the source phrasing.

- **WO-2022005333-A1 · qwen3.6-35b-a3b** (semantic, en): Which unutilized refinery byproduct streams are suitable for conversion into high-quality automotive fuel?  
  — *low-demand olefin-containing fractions, such as dry gas from catalytic cracking, a propane-propylene fraction or a butane-butylene fraction*  
  human: faith 5.0, quality 4.5 · Claude: yes (faith 5.0, quality 3.75) — Answer is an exact span; question is strongly paraphrased ('unutilized refinery byproduct', 'automotive fuel') though it asks for a list of facts rather than a concept and 'high-quality' is a slight gloss.  
  GPT: no (faith 5.0, quality 3.25) — The extracted list is exact and the wording is strongly paraphrased, but the question seeks a simple factual enumeration and is too generic to distinguish this document reliably.

- **WO-2025054647-A1 · gpt-5-mini** (semantic, es): ¿Qué diseño estructural integra el material termochímico y qué propiedades de difusión y deformación especifica la matriz?  
  — *el medio de almacenamiento termochímico incorporado en una matriz; la matriz tiene un coeficiente de difusión de gas para el gas de 2.25*10 -9 m 2 /s a 4.25*10 -9 m 2 /s en un intervalo de temperatura de -30°C a 300°C, y una expansión máxima ε en el rango de la ley de Hooke de 25% a 300%; el medio de almacenamiento termochímico está distribuido sustancialmente de forma homogénea en la matriz.*  
  human: faith 5.0, quality 4.75 · Claude: no (faith 4.67, quality 3.25) — Answer is faithful but the question is a two-part compound with the misspelling 'termochímico' and reads more like a summary prompt than a retrieval query.  
  GPT: yes (faith 5.0, quality 3.5) — La pregunta es específica y recuperable, y su respuesta cubre fielmente la incorporación, la distribución homogénea y las propiedades cuantitativas de la matriz, aunque permanece bastante próxima al texto fuente.

- **WO-2025054647-A1 · qwen3.6-35b-a3b** (semantic, es): ¿Qué parámetros de permeabilidad y dilatación estructural debe cumplir el material soporte para garantizar un funcionamiento estable en acumuladores de calor químico?  
  — *la matriz tiene un coeficiente de difusión de gas para el gas de 2.25*10 -9 m 2 /s to 4.25*10 -9 m 2 /s en un rango de temperatura de -30°C to 300°C, y una expansión máxima ε en el rango de la ley de Hooke de 25% to 300%*  
  human: faith 4.33, quality 4.25 · Claude: yes (faith 5.0, quality 4.25) — Good paraphrase (permeabilidad, material soporte, acumuladores de calor químico) with an exact answer, despite stray English 'to' in the answer ranges.  
  GPT: no (faith 4.33, quality 4.0) — Aunque las cifras son exactas y la consulta resulta plausible, equipara de manera imprecisa el coeficiente de difusión con la permeabilidad y afirma una garantía de estabilidad no expresada en el pasaje.

- **WO-2025177605-A1 · grok-4.3** (technical, fr): Quelle est la teneur minimale en Al de l'alliage à base de Ni ?  
  — *2,0% en poids ou plus d'Al*  
  human: faith 5.0, quality 5.0 · Claude: no (faith 5.0, quality 3.5) — Correctly framed as a minimum, but no mention of retort or welding so it would match arbitrary Ni-Al alloy documents.  
  GPT: yes (faith 5.0, quality 4.0) — La réponse reproduit exactement le seuil minimal d’aluminium, et la question est claire et ciblée, quoique peu spécifique à la cornue concernée.

- **WO-2025187661-A8 · grok-4.3** (semantic, es): ¿Cómo se puede evitar la formación de rebabas durante el reciclaje de resinas de poly(arylene sulfide)?  
  — *una composición de resina de poly(arylene sulfide) que, durante el reciclaje, puede ser inhibida de formar rebabas*  
  human: faith 4.33, quality 4.25 · Claude: yes (faith 5.0, quality 3.5) — Clear, natural query and grounded answer, but it largely reuses the passage's own vocabulary (rebabas, reciclaje, poly(arylene sulfide)) and is closer to a fact lookup than a concept.  
  GPT: no (faith 4.67, quality 4.0) — La pregunta es específica y fiel al pasaje, pero la respuesta repite que la composición evita las rebabas sin explicar cómo lo consigue.

- **WO-2025207810-A1 · sonnet-4.6** (technical, zh): engineered hairpin structure在寡核苷酸中起什么作用？  
  — *mitigates hybridizing of the oligonucleotide to undesirable nucleic acid sequences*  
  human: faith 5.0, quality 5.0 · Claude: yes (faith 5.0, quality 3.75) — Answer is a verbatim span and the hairpin detail is distinctive, but the English/Chinese code-mixing in the question reads awkwardly.  
  GPT: no (faith 5.0, quality 4.0) — 答案忠实对应原文，但问题和答案均不必要地中英混杂，作为指定中文问题不够自然。

- **WO-2025211336-A1 · qwen3.6-35b-a3b** (semantic, en): What specific ingredient combination enables UV-sensitive polymers to retain pliability and withstand high temperatures when cured into heavy layers?  
  — *component (A): a polyorganosiloxane having one or more vinyl groups in one molecule, component (B): a compound having one or more mercapto groups in one molecule, component (C): a photoinitiator, and component (D): hollow resin particles*  
  human: faith 3.67, quality 4.25 · Claude: yes (faith 5.0, quality 4.0) — Answer is the exact component list; question is strongly paraphrased (UV-sensitive polymers, pliability, heavy layers) though 'UV-sensitive polymers' is slightly loose and the phrasing is a bit contrived for a search query.  
  GPT: no (faith 4.67, quality 4.5) — The ingredient list is exact and highly retrievable, but describing the material specifically as UV-sensitive is an unsupported narrowing of the source's broader photocurable formulation.

- **WO-2025212655-A1 · gpt-5-mini** (semantic, de): Welcher Ansatz wird vorgeschlagen, um zahlreiche Vorlagen direkt auf einem festen Träger zu erzeugen?  
  — *In einigen Ausführungsformen können die concatemer template molecules erzeugt werden, indem rolling circle amplification-Reaktionen auf einem Support durchgeführt werden, der eine Mischung aus immobilisierten capture und pinning primers enthält.*  
  human: faith 5.0, quality 4.75 · Claude: no (faith 5.0, quality 3.25) — Answer is faithful, but 'zahlreiche Vorlagen auf einem festen Träger' is too generic to single out this passage (no hint of RCA, concatemers or nanoballs).  
  GPT: yes (faith 5.0, quality 3.5) — The method is accurately extracted and clearly phrased, though the comparatively generic query and source-adjacent wording make it less distinctive.

- **WO-2025215167-A1 · gemini-3.5-flash** (semantic, de): Mit welcher Methode lässt sich eine nanostrukturierte Beschichtung auf Zirconiumbasis herstellen, die gleichmäßig verteilte Quantensensoren enthält?  
  — *durch einen Sol-Gel-Prozess aus einer flüssigen Phase mit darin verteilten dotierten Nanodiamanten auf einem Substrat abgeschieden*  
  human: faith 4.33, quality 4.25 · Claude: yes (faith 5.0, quality 3.75) — Answer span is exact; question paraphrases well, though 'nanostrukturiert' is a mild interpretive addition not in the passage.  
  GPT: no (faith 4.33, quality 4.25) — Der Sol-Gel-Antwortausschnitt ist korrekt, aber die Frage behauptet ohne klare Textgrundlage eine nanostrukturierte Beschichtung und eine gleichmäßige Verteilung der Sensoren.

- **WO-2025215167-A1 · gpt-5-mini** (semantic, de): Welches Herstellungsverfahren wird vorgeschlagen, um eine Zirconium(IV)-oxid-Schicht mit eingebrachten dotierten Nanodiamanten auf einem Substrat zu erzeugen?  
  — *Die Erfindung betrifft eine Beschichtung aus Zirconium(IV)-oxid, welche durch einen Sol-Gel-Prozess aus einer flüssigen Phase mit darin verteilten dotierten Nanodiamanten auf einem Substrat abgeschieden und nach Ihrer Trocknung durch einen Kalzinierungsprozess bei erhöhter Temperatur in einen kristallinen Zustand überfuhrt wird.*  
  human: faith 5.0, quality 4.5 · Claude: yes (faith 5.0, quality 3.25) — Highly retrievable and faithful, but reuses the passage's exact terms (Zirconium(IV)-oxid, dotierte Nanodiamanten, Substrat) and asks for a fact rather than a concept.  
  GPT: no (faith 5.0, quality 3.25) — Frage und Antwort sind sachlich exakt, doch die Frage übernimmt nahezu die gesamte Terminologie des Abstracts und bietet für einen semantischen Benchmark zu wenig Paraphrase.

- **WO-2025215167-A1 · qwen3.6-35b-a3b** (semantic, de): Wie kann eine robuste Oxidschicht gefertigt werden, die funktionale Nanopartikel gleichmäßig verteilt und anschließend eine definierte Kristallstruktur ausbildet?  
  — *Eine Beschichtung aus Zirconium(IV)-oxid, welche durch einen Sol-Gel-Prozess aus einer flüssigen Phase mit darin verteilten dotierten Nanodiamanten auf einem Substrat abgeschieden und nach Ihrer Trocknung durch einen Kalzinierungsprozess bei erhöhter Temperatur in einen kristallinen Zustand überfuhrt wird, in dem das Zirconium(IV)-oxid zum überwiegendem Anteil in seiner tetragonalen Phase vorliegt.*  
  human: faith 3.67, quality 4.5 · Claude: yes (faith 5.0, quality 4.0) — Highly abstracted conceptual framing with full verbatim answer, but 'robust' is unsupported and the generic wording (Oxidschicht, funktionale Nanopartikel) weakens retrievability.  
  GPT: no (faith 4.33, quality 4.25) — Die starke konzeptionelle Paraphrase ist flüssig, führt aber die nicht belegten Eigenschaften „robust“ und „gleichmäßig“ ein und lässt die kennzeichnenden Quantensensoren beziehungsweise Nanodiamanten unerwähnt.

## human discards, one LLM keeps (17)

- **EP-4633645-A1 · gpt-5-mini** (technical, fr): Quel site de phosphorylation de l'ubiquitine est élevé dans les maladies neurodégénératives ?  
  — *phosphorylation de l'ubiquitine Ser65*  
  human: faith 3.67, quality 4.25 · Claude: yes (faith 4.67, quality 3.25) — Supported and focused, but the answer ('phosphorylation de l'ubiquitine Ser65') slightly mismatches the question asking for the site (Ser65) and the question already reveals most of the answer terms.  
  GPT: no (faith 4.33, quality 3.5) — Le passage soutient la réponse, mais la question confond le site de phosphorylation, qui est Ser65, avec le niveau de phosphorylation, qui est élevé.

- **EP-4633791-A1 · gpt-5-mini** (semantic, zh): 有哪些新的工艺可用于制备以蛋白质为基础的微胶囊？  
  — *一种制备蛋白质基微胶囊的新工艺。*  
  human: faith 2.67, quality 4.0 · Claude: yes (faith 4.67, quality 2.75) — Faithful and retrieves the document well, but the question nearly mirrors the abstract wording and the answer is circular ('a new process') with no substantive content.  
  GPT: no (faith 4.0, quality 2.5) — 原文只宣称存在一种新工艺而没有披露工艺内容，因此答案无法回应“有哪些工艺”这一要求且几乎只是重复问题。

- **EP-4633791-A1 · qwen3.6-35b-a3b** (semantic, zh): 家用清洁或个人洗护产品如何通过微囊化技术整合香氛成分？  
  — *含有所述微胶囊的香调组合物以及包含这些微胶囊的消费产品，尤其是以家庭护理或个人护理产品形式出现的含香消费产品。*  
  human: faith 3.0, quality 2.75 · Claude: yes (faith 4.0, quality 3.75) — Good conceptual query about integrating fragrance into household/personal care products via microencapsulation, but the passage gives no 'how', so the answer merely restates the product list and only loosely answers the question.  
  GPT: no (faith 4.33, quality 3.75) — 答案忠实复述了含微胶囊的香氛组合物及护理产品，但并未真正说明如何通过微囊化整合香氛成分。

- **EP-4633791-A1 · sonnet-4.6** (semantic, zh): 有没有一种不依赖合成聚合物壳材、利用天然生物大分子封装香料的微囊化技术？  
  — *La présente invention concerne un nouveau procédé de préparation de microcapsules à base de protéines*  
  human: faith 2.33, quality 3.75 · Claude: yes (faith 5.0, quality 4.75) — Strongly paraphrased, concept-level query (natural biomacromolecule vs synthetic shell) that maps well to protein-based fragrance microcapsules; answer is a verbatim French span, though the 'no synthetic polymer' contrast is the asker's framing rather than stated in the passage.  
  GPT: no (faith 3.33, quality 5.0) — 查询具有很强的概念性和检索价值，但原文并未说明不使用合成聚合物、采用天然生物大分子或将香料封装其中，所引法文答案也仅证明存在蛋白质基微胶囊制备工艺。

- **MX-2025004470-A · gemini-3.5-flash** (semantic, en): How does the reaction vessel design counteract temperature drop during the endothermic conversion process?  
  — *heating the heated paraffinic feedstock in the first dehydrogenation reactor using the at least one first electrical heating element*  
  human: faith 3.67, quality 3.75 · Claude: yes (faith 4.67, quality 4.25) — Strongly paraphrased and plausible, though 'counteract temperature drop' and 'endothermic' are inferred framing not stated in the passage, so the link to the answer is slightly indirect.  
  GPT: no (faith 4.33, quality 4.5) — Although the answer is an exact heating step, the passage does not state that the design counteracts a temperature drop or characterize the conversion as endothermic.

- **MX-2025006624-A · grok-4.3** (semantic, fr): Existe-t-il des revêtements polymérisables par actinique qui incorporent des matériaux d'origine biologique tout en maintenant des propriétés de mise en œuvre industrielles ?  
  — *composition de revêtement curable par radiation actinique qui comprend de 10 % en poids à 90 % en poids d'un composé A et entre 10 % en poids et 89.99 % en poids d'un composé B*  
  human: faith 3.33, quality 4.25 · Claude: yes (faith 4.33, quality 3.5) — Answer combines two supported spans with correct figures, but 'propriétés de mise en œuvre industrielles' is an inference beyond the passage and 'polymérisables par actinique' is ungrammatical French.  
  GPT: no (faith 5.0, quality 3.5) — Les plages de composition sont exactes, mais la réponse ne justifie ni l'origine biologique ni le maintien de propriétés industrielles, et la tournure « polymérisables par actinique » est maladroite.

- **MX-2025006624-A · qwen3.6-35b-a3b** (semantic, fr): Quelle stratégie formulation permet d'intégrer des précurseurs renouvelables dans des systèmes de revêtements durcis par rayonnement tout en contrôlant la rhéologie ?  
  — *a poly(trimethylene ether) (meth)acrylate compound A having at most two (meth)acrylate groups obtainable by a condensation reaction of biobased 1,3 poly(trimethylene ether) glycol and a (meth)acrylate compound selected from the group consisting of (meth)acrylic acid, (meth)acryloyl chloride, and /or alkylesters thereof*  
  human: faith 3.33, quality 4.0 · Claude: yes (faith 5.0, quality 4.25) — Answer is verbatim from the passage; question is well paraphrased and conceptual, with 'contrôlant la rhéologie' loosely tied to the viscosity limit, but 'stratégie formulation' is missing 'de' and the answer is in English rather than French.  
  GPT: no (faith 5.0, quality 4.25) — La voie chimique citée est directement étayée, mais la réponse omet le composé B et sa viscosité, indispensables pour répondre à l'aspect de contrôle rhéologique.

- **MX-2025006624-A · sonnet-4.6** (semantic, fr): Comment intégrer des matières premières renouvelables dans une formulation de revêtement durcissable par rayonnement sans sacrifier la réactivité ?  
  — *un composé de (met)acrilato de poly(triméthylène éther) A ayant au plus deux groupes (meth)acrylate, obtenu par réaction de condensation de 1,3 poly(trimethylene ether) glycol d'origine biologique et un composé (meth)acrylate choisi dans le groupe constitué de l'acide (meth)acrylique, du chlorure de (meth)acryloyle et/ou de leurs alkylesters*  
  human: faith 3.33, quality 4.0 · Claude: yes (faith 5.0, quality 4.25) — Answer is a faithful French rendering of compound A; question is strongly paraphrased and conceptual, but 'sans sacrifier la réactivité' is not stated in the passage and the answer contains a stray Spanish fragment '(met)acrilato'.  
  GPT: no (faith 5.0, quality 4.0) — La préparation du composé biobasé est bien étayée, mais le passage ne démontre pas que cette intégration se fait sans perte de réactivité.

- **MX-2025007206-A · gemini-3.5-flash** (technical, de): Über welcher Lagertemperatur ermöglichen die rAAV-Formulierungen eine langfristige Haltbarkeit?  
  — *-80°C*  
  human: faith 2.67, quality 5.0 · Claude: no (faith 4.0, quality 3.5) — Awkward German ('Über welcher Lagertemperatur' instead of 'Oberhalb welcher') and a bare '-80°C' answer that drops the 'above' threshold direction make it the weakest of several near-identical items.  
  GPT: yes (faith 5.0, quality 4.25) — Die Frage kodiert die Oberhalb-Beziehung korrekt und die Antwort gibt den exakten Schwellenwert wieder, auch wenn „Über welcher Lagertemperatur“ etwas unidiomatisch klingt.

- **MX-2025007206-A · sonnet-4.6** (technical, de): Bei welcher Mindesttemperatur kann eine rAAV-Formulierung für die Langzeitlagerung im Regal gelagert werden?  
  — *oberhalb von -80°C*  
  human: faith 3.67, quality 4.75 · Claude: yes (faith 5.0, quality 3.5) — Correctly grounded and specific, but wordy and stilted ('für die Langzeitlagerung im Regal gelagert' is a literal calque of 'shelf storage'), which hurts realism and fluency.  
  GPT: no (faith 4.33, quality 3.75) — Der Zahlenwert ist belegt, doch „Mindesttemperatur“ deutet fälschlich einen eingeschlossenen Minimalwert an und „im Regal gelagert“ wirkt wie eine unbeholfene wörtliche Übersetzung.

- **MX-2025007510-A · grok-4.3** (semantic, es): Manera de bajar la frecuencia con que se administra medicación a pacientes con hipertensión pulmonar  
  — *para tratar hipertensión pulmonar con frecuencia de dosificación reducida*  
  human: faith 3.0, quality 2.5 · Claude: yes (faith 5.0, quality 4.0) — Natural search-style phrasing with a faithful answer, though the query could match many pulmonary-hypertension dosing documents.  
  GPT: no (faith 4.0, quality 3.75) — El fragmento está presente en la fuente, pero repite el objetivo de reducir la frecuencia sin explicar la manera de lograrlo y la consulta está formulada como un sintagma incompleto.

- **WO-2022005333-A1 · gemini-3.5-flash** (semantic, en): How can chemical processors salvage low-demand refinery byproducts containing olefins for fuel synthesis?  
  — *produce gasolines using low-demand olefin-containing fractions, such as dry gas from catalytic cracking, a propane-propylene fraction or a butane-butylene fraction*  
  human: faith 3.67, quality 4.0 · Claude: no (faith 5.0, quality 3.25) — Grounded answer, but 'How can chemical processors salvage ... for fuel synthesis' is stilted and unlike a real search query, and retains 'low-demand' and 'olefins' from the passage.  
  GPT: yes (faith 5.0, quality 4.0) — This fluent and well-paraphrased resource-valorization query has an exact supporting span, though its lack of named feedstocks makes it only moderately distinctive.

- **WO-2022005333-A1 · gpt-5-mini** (semantic, en): How can low-value olefin-rich feeds like dry catalytic cracking gas or propane‑propylene cuts be converted into gasoline in this process?  
  — *The method makes it possible to produce gasolines using low-demand olefin-containing fractions, such as dry gas from catalytic cracking, a propane-propylene fraction or a butane-butylene fraction,*  
  human: faith 3.67, quality 4.0 · Claude: yes (faith 4.67, quality 3.75) — Well grounded and conceptually framed, but the question names the specific feeds from the passage (lower lexical distance) and the trailing 'in this process' plus a dangling comma in the answer are minor blemishes.  
  GPT: no (faith 5.0, quality 3.5) — Although fully supported and specific, the query closely mirrors the source vocabulary, depends on the vague phrase “this process,” and receives a largely circular answer.

- **WO-2025054647-A1 · gemini-3.5-flash** (semantic, es): ¿Cómo se resuelven las tensiones mecánicas por dilatación y se asegura la permeabilidad al gas en acumuladores térmicos que operan en condiciones térmicas extremas?  
  — *la matriz presenta un coeficiente de difusión de gas para el gas de 2.25*10 -9 m 2 /s a 4.25*10 -9 m 2 /s en un rango de temperatura de -30°C a 300°C, y una expansión máxima ε en el rango de la ley de Hooke de 25% a 300%*  
  human: faith 3.33, quality 4.0 · Claude: yes (faith 4.67, quality 4.5) — Strong conceptual paraphrase with little keyword overlap; the 'how is it solved' framing slightly overreaches what the span states, but the answer still matches the passage exactly.  
  GPT: no (faith 4.0, quality 4.25) — La formulación tiene buena distancia léxica y plantea un problema conceptual, pero el pasaje solo especifica propiedades de la matriz y no explica cómo se resuelven tensiones ni cómo se asegura la permeabilidad.

- **WO-2025202347-A1 · sonnet-4.6** (semantic, de): Wie können Spätfolgen einer nicht-viralen Bindehautentzündung, wie Hornhauttrübungen oder Pseudomembranbildung, pharmakologisch adressiert werden?  
  — *Die klinisch relevanten Augenerkrankungen umfassen Spätkomplikationen nicht-viraler und nicht-allergischer Konjunktivitis, ausgewählt aus der Gruppe bestehend aus Hornhauttrübungen (corneal opacities), subepitheliale Infiltrate und die Bildung okulärer Pseudomembranen (formation of ocular pseudomembranes).*  
  human: faith 3.67, quality 4.0 · Claude: yes (faith 4.67, quality 4.0) — Fluent conceptual query; the answer is grounded but merely lists the complications rather than naming iota-carrageenan as the pharmacological means the question asks for, and includes English glosses as padding.  
  GPT: no (faith 4.67, quality 4.0) — Obwohl die aufgezählten Spätkomplikationen belegt sind, beantwortet die Antwort nicht die Frage nach der pharmakologischen Behandlungsmethode und enthält entbehrliche englische Glossare.

- **WO-2025211336-A1 · grok-4.3** (semantic, en): What components form the basis of a resin that relies on addition reactions between silicon-containing polymers and sulfur-based molecules for light-induced hardening along with filler particles?  
  — *includes component (A): a polyorganosiloxane having one or more vinyl groups in one molecule, component (B): a compound having one or more mercapto groups in one molecule, component (C): a photoinitiator, and component (D): hollow resin particles.*  
  human: faith 3.67, quality 4.0 · Claude: yes (faith 5.0, quality 4.5) — Highly distinctive conceptual query (thiol-ene chemistry inferred from vinyl siloxane plus mercapto compound) with exact answer, though the inference about 'addition reactions' is not stated in the passage and 'filler particles' is a loose gloss on hollow resin particles; sentence is long.  
  GPT: no (faith 4.67, quality 4.25) — The answer accurately lists the components, but the question adds an unstated addition-reaction mechanism and calls the hollow particles fillers while using cumbersome phrasing.

- **WO-2025215167-A1 · sonnet-4.6** (semantic, de): Wie lassen sich dotierte Nanodiamanten dauerhaft in eine Oxidkeramikschicht einbetten, ohne ihre Quanteneigenschaften zu verlieren?  
  — *Die Beschichtung aus Zirconium(IV)-oxid wird durch einen Sol-Gel-Prozess aus einer flüssigen Phase mit darin verteilten dotierten Nanodiamanten auf einem Substrat abgeschieden und nach ihrer Trocknung durch einen Kalzinierungsprozess bei erhöhter Temperatur in einen kristallinen Zustand überführt.*  
  human: faith 3.0, quality 4.0 · Claude: yes (faith 5.0, quality 4.0) — Well-paraphrased conceptual query with an answer lifted verbatim from the passage, though the 'ohne Quanteneigenschaften zu verlieren' premise is not addressed in the abstract.  
  GPT: no (faith 4.33, quality 4.25) — Der Herstellungsablauf ist korrekt wiedergegeben, doch weder Passage noch Antwort belegen die entscheidende Behauptung, dass die Quanteneigenschaften der Nanodiamanten erhalten bleiben.
