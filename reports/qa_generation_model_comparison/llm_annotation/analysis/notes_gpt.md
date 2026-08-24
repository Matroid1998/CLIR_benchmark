# GPT-5.6 Sol — document notes and per-question reasons

29 of 30 documents carry a shared note. Q1–Q6 refer to the randomised slots this annotator saw; resolved to models below.

## EP-4504821-A1  ·  technical mode  ·  question language: es

> Q1 es la consulta más sólida; Q4–Q6 son duplicados prácticamente idénticos y comparten una falta crítica de contexto químico.

- **Q1 · sonnet-4.6** (kept, faith 5.00, quality 4.75, ling 5): ¿Cuántos átomos de carbono puede tener el resto R2 en la fórmula de los organopolysiloxanos preentrecruzados?  
  — *3 to 18 carbon atoms*  
  reason: La pregunta es clara, específica al contexto de los organopolisiloxanos preentrecruzados y su respuesta reproduce exactamente el intervalo de 3 a 18 átomos de carbono.
- **Q2 · gpt-5-mini** (DISCARDED, faith 5.00, quality 3.00, ling 5): ¿Qué valores puede tener k1?  
  — *k1 is 0, 1, 2 or 3*  
  reason: Aunque la respuesta enumera fielmente los valores de k1, la consulta aislada carece de contexto químico y difícilmente recuperaría este documento concreto.
- **Q3 · gemini-3.5-flash** (kept, faith 4.67, quality 4.00, ling 5): ¿Cuál es el rango de átomos de carbono permitido para el grupo R 2 bivalente?  
  — *3 to 18*  
  reason: La consulta identifica el grupo R2 bivalente y el intervalo correcto, aunque la respuesta omite la unidad explícita de átomos de carbono y la pregunta podría aportar más contexto documental.
- **Q4 · gpt-5.4-mini** (DISCARDED, faith 5.00, quality 3.00, ling 5): ¿Qué valores puede tomar b?  
  — *0 o un número entero de 1 to 500*  
  reason: El intervalo para b es fiel y exacto, pero la variable b sin fórmula ni contexto químico hace que la consulta sea demasiado genérica para recuperación.
- **Q5 · grok-4.3** (DISCARDED, faith 5.00, quality 3.00, ling 5): ¿Qué valores puede tomar b?  
  — *0 o un entero de 1 a 500*  
  reason: La respuesta está plenamente respaldada, pero preguntar solo por los valores de b no distingue esta patente de numerosos documentos técnicos no relacionados.
- **Q6 · qwen3.6-35b-a3b** (DISCARDED, faith 5.00, quality 3.00, ling 5): ¿Cuáles son los valores permitidos para b?  
  — *0 or an integer from 1 to 500*  
  reason: La respuesta inglesa coincide exactamente con el pasaje, pero la pregunta española es demasiado descontextualizada y genérica para funcionar como consulta de búsqueda.

## EP-4577789-A1  ·  technical mode  ·  question language: zh

> Q1至Q5高度集中于同一冷却气体管道关系；若需文档内去重，可优先保留限定更充分的Q5或表述更概括的Q4。

- **Q1 · grok-4.3** (kept, faith 5.00, quality 3.75, ling 5): 冷却气体如何从冷却区引导至预热区？  
  — *经由冷气管道 (44) 被引导至预热区 (21)*  
  reason: 答案直接且准确地说明冷却气体经由编号44的冷气管道进入预热区，问题自然且聚焦，但未提及竖窑，检索特异性一般。
- **Q2 · gpt-5-mini** (kept, faith 5.00, quality 3.75, ling 5): 冷却气体由哪个管道引导至预热区？  
  — *冷却气体管道 (44)*  
  reason: 答案“冷却气体管道 (44)”与原文完全一致，问题简洁明确，但单独作为检索词时对具体专利的限定较弱。
- **Q3 · gpt-5.4-mini** (kept, faith 5.00, quality 3.75, ling 5): 冷却气体管道把冷却气体从哪里引导到哪里？  
  — *从冷却区 (22) 引导至预热区 (21)*  
  reason: 答案准确复现冷却气体从冷却区22到预热区21的流向，问题流畅且只询问一个管道关系，但缺少设备类型限定。
- **Q4 · qwen3.6-35b-a3b** (kept, faith 4.67, quality 4.25, ling 5): 冷却气体管道连接竖窑内的哪两个区域？  
  — *从冷却区 (22) 引导至预热区 (21)*  
  reason: 两个区域及编号均受原文支持，且“连接”是对管道输送关系的合理概括，不过原文更严格地表述为将气体从一区引导至另一区。
- **Q5 · gemini-3.5-flash** (kept, faith 5.00, quality 4.25, ling 5): 冷却气体经由管道被引导至并流蓄热式竖窑的哪个区域？  
  — *预热区 (21)*  
  reason: 问题以并流蓄热式竖窑为限定并只询问气体的目的区域，答案“预热区 (21)”准确、简洁且具有较强检索特异性。
- **Q6 · sonnet-4.6** (kept, faith 4.67, quality 4.75, ling 5): PFR竖窑中废气通过哪个出口排出？  
  — *废气经由排气出口 (6) 从其中一个竖井 (2) 排出*  
  reason: 排气出口6及废气从其中一个竖井排出的陈述均直接受原文支持，但答案包含了超出“哪个出口”所需的少量附加信息。

## EP-4584229-A1  ·  technical mode  ·  question language: es

> Todas las preguntas recuperan esencialmente la misma definición o su intervalo numérico; Q4 es la formulación más limpia para el dato cuantitativo y Q5 para la definición completa.

- **Q1 · gemini-3.5-flash** (kept, faith 5.00, quality 4.25, ling 5): ¿Cuántos átomos de carbono tiene el grupo hidrocarbonado R en la fórmula R-NR'H?  
  — *1 to 20*  
  reason: La pregunta es clara y concisa, y el rango «1 to 20» coincide exactamente con el pasaje, aunque la fórmula por sí sola aporta una especificidad moderada.
- **Q2 · gpt-5.4-mini** (kept, faith 5.00, quality 3.75, ling 4): ¿Qué rango de carbonos tiene R en R-NR'H?  
  — *1 to 20 carbon atoms*  
  reason: El rango está fielmente respaldado y la consulta se centra en un solo dato, aunque «rango de carbonos» es menos preciso que «rango de átomos de carbono».
- **Q3 · sonnet-4.6** (DISCARDED, faith 5.00, quality 4.00, ling 3): ¿Qué representa el grupo R en la fórmula R-NR'H de los amino compounds utilizados en composiciones de polvos de dispersión?  
  — *a linear or branched and optionally substituted hydrocarbon group with 1 to 20 carbon atoms*  
  reason: La respuesta reproduce fielmente la definición completa de R y el contexto es específico, pero el uso innecesario de «amino compounds» rompe la fluidez de una pregunta en español.
- **Q4 · qwen3.6-35b-a3b** (kept, faith 5.00, quality 4.75, ling 5): ¿Cuál es el rango de átomos de carbono definido para el grupo R en la fórmula R-NR'H?  
  — *1 to 20 carbon atoms*  
  reason: Es una consulta técnica natural, económica y bien enfocada cuya respuesta reproduce exactamente el intervalo de 1 a 20 átomos de carbono.
- **Q5 · gpt-5-mini** (kept, faith 5.00, quality 4.25, ling 5): ¿Qué representa R en la fórmula R-NR'H?  
  — *a linear or branched and optionally substituted hydrocarbon group with 1 to 20 carbon atoms*  
  reason: La pregunta es fluida y solicita una única definición plenamente respaldada, aunque carece del contexto de las composiciones de dispersión y por ello tiene especificidad moderada.
- **Q6 · grok-4.3** (DISCARDED, faith 5.00, quality 4.25, ling 5): ¿Qué representa el resto R en la fórmula R-NR'H?  
  — *un linear or branched, optionally substituted hydrocarbon group con 1 to 20 carbon atoms*  
  reason: La pregunta en sí es correcta y enfocada, pero la respuesta mezcla español e inglés de forma gramaticalmente defectuosa, lo que reduce su idoneidad para el benchmark.

## EP-4627127-A1  ·  technical mode  ·  question language: de

> Q2 und Q5 fragen nahezu denselben Titelfakt ab; Q5 bietet die passendere deutschsprachige Antwort.

- **Q1 · qwen3.6-35b-a3b** (kept, faith 5.00, quality 4.25, ling 5): Welche Verarbeitungsschritte folgen auf das Gießen bei der Herstellung der Aluminiumlegierungsprodukte?  
  — *angepasstes Walzen und nachgelagerte Wärmebehandlungsschritte*  
  reason: Die Antwort gibt die beiden im Abstract unmittelbar auf das Gießen folgenden Verarbeitungsschritte präzise wieder, und die Frage ist klar sowie hinreichend spezifisch.
- **Q2 · sonnet-4.6** (kept, faith 4.67, quality 4.25, ling 5): Für welchen Anwendungsbereich sind diese formbaren, korrosionsbeständigen Aluminiumlegierungen vorgesehen?  
  — *structural component*  
  reason: Der Titel stützt den Einsatz für ein Strukturbauteil eindeutig, auch wenn die englische Antwort sprachlich weniger gut zur deutschen Frage passt.
- **Q3 · grok-4.3** (kept, faith 5.00, quality 3.50, ling 5): Welche Verarbeitungsschritte werden bei Aluminiumlegierungsprodukten durchgeführt?  
  — *Gießen einer Aluminiumlegierung und Durchführung von maßgeschneidertem Walzen und nachgelagerten thermischen Verarbeitungsschritten*  
  reason: Die vollständige Verfahrensfolge ist korrekt wiedergegeben, wobei die Frage relativ nah am Ausgangstext und etwas allgemein formuliert ist.
- **Q4 · gpt-5.4-mini** (DISCARDED, faith 5.00, quality 3.25, ling 5): Welcher Werkstoff wird gegossen?  
  — *eine Aluminiumlegierung*  
  reason: Die Antwort ist zwar exakt belegt, doch die kontextlose Frage nach dem gegossenen Werkstoff ist zu allgemein, um das relevante Patent sinnvoll einzugrenzen.
- **Q5 · gemini-3.5-flash** (kept, faith 5.00, quality 4.00, ling 5): Für welche Art von Komponenten ist die formbare, korrosionsbeständige Aluminiumlegierung vorgesehen?  
  — *Strukturbauteile*  
  reason: Die Antwort entspricht dem im Titel genannten strukturellen Einsatz und die Frage ist präzise, wenn auch eng an der Titelformulierung orientiert.
- **Q6 · gpt-5-mini** (DISCARDED, faith 5.00, quality 3.50, ling 5): Welche Festigkeit weisen die resultierenden Aluminiumlegierungsprodukte auf?  
  — *hohe Festigkeit*  
  reason: Die hohe Festigkeit ist korrekt belegt, aber die Abfrage ist als Suchanfrage zu generisch und könnte auf sehr viele Aluminiumlegierungspatente zutreffen.

## EP-4627881-A1  ·  semantic mode  ·  question language: zh

> Q3和Q4的答案均有依据，但问题加入了原文未提及的应用前提；Q2在概念化改写与可检索性之间最为均衡。

- **Q1 · gpt-5-mini** (kept, faith 5.00, quality 3.25, ling 5): 有哪些专用硬件可以直接生成工业用等离子体火焰？  
  — *用于生成至少一种等离子体火焰(12)的装置(10, 10a, 10b)。*  
  reason: 答案准确对应生成至少一种等离子体火焰的装置，但问题主要询问单一事实，且“工业用”使表述略宽于原文。
- **Q2 · sonnet-4.6** (kept, faith 5.00, quality 4.25, ling 5): 有没有一种统一的控制方法，可以同时适用于单台等离子体发生器和整套高温熔融系统？  
  — *一种用于操作此类设备（10, 10a, 10b）、此类等离子体发生装置（100）或此类高温工艺设备（尤其是熔融装置（26））的方法*  
  reason: 答案完整涵盖设备、等离子体发生单元及高温工艺设备的操作方法，问题也以适用范围进行了较自然的概念化改写。
- **Q3 · gemini-3.5-flash** (DISCARDED, faith 5.00, quality 3.25, ling 4): 当单一喷嘴所提供的电离气体束能效不足时，可以采用什么方案将多套发生装置集结协同运作？  
  — *Plasmaerzeugungseinrichtung (100) 包含多个 Vorrichtungen (10, 10a, 10b)*  
  reason: 答案本身忠实于多个装置组成发生单元的原文，但问题虚构了单一喷嘴、电离气体束能效不足和协同运行等未获支持的情境。
- **Q4 · qwen3.6-35b-a3b** (DISCARDED, faith 5.00, quality 3.75, ling 5): 面对连续化生产要求，如何将独立的小型发生器集成到完整产线中？  
  — *包含多个上述发生装置的等离子体发生单元*  
  reason: 答案准确概括等离子体发生单元的构成，但连续化生产、小型发生器和完整产线均非原文信息，使检索框架失真。
- **Q5 · grok-4.3** (kept, faith 5.00, quality 4.00, ling 5): 工业熔化设备中实现多等离子体火焰供应的系统如何构建？  
  — *a plasma generation unit (100) comprising a plurality of devices (10, 10a, 10b)*  
  reason: 答案精确给出由多个装置构成的等离子体发生单元，且问题将其合理置于工业熔化和多火焰供应的系统构建语境中。
- **Q6 · gpt-5.4-mini** (kept, faith 5.00, quality 3.75, ling 5): 如果要把多个等离子火焰发生装置组合起来，相关的等离子生成单元是怎样构成的？  
  — *eine Plasmaerzeugungseinrichtung (100) umfassend mehrere Vorrichtungen (10, 10a, 10b)*  
  reason: 问题自然且答案逐项忠实于原文中的单元构成，不过其措辞与原文概念非常接近，语义改写幅度较小。

## EP-4630021-A1  ·  technical mode  ·  question language: de

> Q4 and Q5 are near-duplicates, while Q3 is the most document-specific query.

- **Q1 · gpt-5.4-mini** (DISCARDED, faith 5.00, quality 3.50, ling 5): Welche Eigenschaften hat das flüssige Injektionsprodukt?  
  — *clear, safe, and physiologically and biologically active*  
  reason: The answer is directly supported and the question is fluent, but the generic reference to „das flüssige Injektionsprodukt“ is too underspecified to retrieve this document reliably.
- **Q2 · qwen3.6-35b-a3b** (kept, faith 5.00, quality 4.00, ling 4): Welche Komponenten bleiben nach der Aufbereitung des Injektionsprodukts erhalten?  
  — *postbiotics, proteins, exosomes, biocomponents*  
  reason: The preserved components are extracted exactly from the passage, and the focused query is useful despite being somewhat generic and slightly imprecise about what undergoes processing.
- **Q3 · sonnet-4.6** (kept, faith 5.00, quality 3.75, ling 4): Was wird bei der Verarbeitung von eingehendem plazentaren Gewebe und Fluid mit Verfärbungen und Verunreinigungen als Endprodukt erzeugt?  
  — *a clear amnion and amniotic fluid injectable product*  
  reason: The answer is an exact supported product description and the query is highly specific, although its long wording closely mirrors the source.
- **Q4 · gemini-3.5-flash** (kept, faith 5.00, quality 4.50, ling 5): Aus welchen Ausgangsstoffen werden pferdespezifische therapeutische Zusammensetzungen hergestellt?  
  — *aus der Plazenta gewonnenen Materialien*  
  reason: This is a fluent, focused, and suitably paraphrased query whose answer accurately identifies the placental-derived starting materials.
- **Q5 · gpt-5-mini** (kept, faith 5.00, quality 4.00, ling 5): Welche Materialien enthalten die equinen therapeutischen Zusammensetzungen?  
  — *Plazenta-abgeleitete Materialien*  
  reason: The question and answer are fully faithful and focused, though the wording remains fairly close to the source formulation.
- **Q6 · grok-4.3** (kept, faith 4.33, quality 4.00, ling 5): Welche Eigenschaften besitzt das produzierte Amnion- und Fruchtwasser-Injektionsprodukt?  
  — *clear, safe, and physiologically and biologically active liquid injectable*  
  reason: The listed properties are supported for the therapeutic liquid injectable overall, although applying all of them specifically to the amnion and amniotic-fluid product requires a minor cross-sentence inference.

## EP-4633645-A1  ·  technical mode  ·  question language: fr

> Les six questions ciblent le même fait; Q2 est la plus distinctive grâce à sa référence explicite aux composés de formule (I).

- **Q1 · gpt-5.4-mini** (kept, faith 5.00, quality 4.25, ling 5): Quelle caractéristique de phosphorylation est associée aux maladies neurodégénératives visées ?  
  — *un niveau élevé de phosphorylation de l'ubiquitine Ser65*  
  reason: La réponse reprend exactement la caractéristique indiquée dans le passage, et la question est claire, ciblée et suffisamment spécifique.
- **Q2 · sonnet-4.6** (kept, faith 5.00, quality 4.50, ling 5): Quel marqueur biologique caractérise les maladies neurodégénératives traitées par les composés de formule (I) ?  
  — *Un niveau élevé de phosphorylation de l'ubiquitine Ser65*  
  reason: Le marqueur demandé est directement attesté, tandis que la mention des composés de formule (I) rend la requête particulièrement distinctive.
- **Q3 · grok-4.3** (kept, faith 5.00, quality 3.75, ling 5): Quel niveau de phosphorylation de l'ubiquitine Ser65 caractérise les maladies neurodégénératives traitées ?  
  — *niveau élevé*  
  reason: La réponse « niveau élevé » est exacte et répond précisément à la question, même si la formulation reste très proche du texte source.
- **Q4 · gpt-5-mini** (DISCARDED, faith 4.33, quality 3.50, ling 3): Quel site de phosphorylation de l'ubiquitine est élevé dans les maladies neurodégénératives ?  
  — *phosphorylation de l'ubiquitine Ser65*  
  reason: Le passage soutient la réponse, mais la question confond le site de phosphorylation, qui est Ser65, avec le niveau de phosphorylation, qui est élevé.
- **Q5 · gemini-3.5-flash** (kept, faith 5.00, quality 4.50, ling 4): Quel état de l'ubiquitine Ser65 caractérise les pathologies neurodégénératives ciblées ?  
  — *un niveau élevé de phosphorylation de l'ubiquitine Ser65*  
  reason: La réponse est intégralement fondée et la paraphrase est efficace, bien que le terme « état » soit légèrement moins précis que « niveau de phosphorylation ».
- **Q6 · qwen3.6-35b-a3b** (DISCARDED, faith 4.67, quality 3.75, ling 4): Quelle modification biochimique spécifique est élevée dans les affections neurodégénératives ciblées ?  
  — *un niveau élevé de phosphorylation de l'ubiquitine Ser65*  
  reason: La réponse est bien extraite, mais la question omet l'ubiquitine Ser65 et la formule (I), ce qui la rend trop générique pour retrouver spécifiquement ce document.

## EP-4633791-A1  ·  semantic mode  ·  question language: zh

> Q2是最可保留的问题；Q1、Q4和Q5超出了摘要的实际披露程度，而Q3和Q6分别存在答案线索前置和指代过泛的问题。

- **Q1 · qwen3.6-35b-a3b** (DISCARDED, faith 4.33, quality 3.75, ling 5): 家用清洁或个人洗护产品如何通过微囊化技术整合香氛成分？  
  — *含有所述微胶囊的香调组合物以及包含这些微胶囊的消费产品，尤其是以家庭护理或个人护理产品形式出现的含香消费产品。*  
  reason: 答案忠实复述了含微胶囊的香氛组合物及护理产品，但并未真正说明如何通过微囊化整合香氛成分。
- **Q2 · gemini-3.5-flash** (kept, faith 5.00, quality 3.25, ling 4): 这种微包裹体通常适用于哪些类型的加香日化产品？  
  — *家庭护理或个人护理产品形式的加香消费品*  
  reason: 问题虽使用略显生硬的“微包裹体”和泛指词“这种”，但答案准确概括了原文明确列出的家居护理与个人护理产品类别。
- **Q3 · grok-4.3** (DISCARDED, faith 4.67, quality 3.25, ling 4): 蛋白质基微胶囊适合加入到哪些家用或个人护理产品中发挥作用？  
  — *香味组合物和包含所述微胶囊的消费产品，特别是以家用护理或个人护理产品形式存在的香味消费产品*  
  reason: 答案有原文依据，但问题已直接给出“家用或个人护理”这一核心答案线索，且“发挥作用”的表述没有得到说明。
- **Q4 · gpt-5-mini** (DISCARDED, faith 4.00, quality 2.50, ling 5): 有哪些新的工艺可用于制备以蛋白质为基础的微胶囊？  
  — *一种制备蛋白质基微胶囊的新工艺。*  
  reason: 原文只宣称存在一种新工艺而没有披露工艺内容，因此答案无法回应“有哪些工艺”这一要求且几乎只是重复问题。
- **Q5 · sonnet-4.6** (DISCARDED, faith 3.33, quality 5.00, ling 5): 有没有一种不依赖合成聚合物壳材、利用天然生物大分子封装香料的微囊化技术？  
  — *La présente invention concerne un nouveau procédé de préparation de microcapsules à base de protéines*  
  reason: 查询具有很强的概念性和检索价值，但原文并未说明不使用合成聚合物、采用天然生物大分子或将香料封装其中，所引法文答案也仅证明存在蛋白质基微胶囊制备工艺。
- **Q6 · gpt-5.4-mini** (DISCARDED, faith 5.00, quality 3.25, ling 5): 这类带香味的消费品更偏向哪些日常护理场景？  
  — *家居护理或个人护理产品*  
  reason: 答案准确对应原文的家居护理和个人护理场景，但“这类”缺乏独立指代且问题未提及蛋白质微胶囊，难以有效定位该文献。

## EP-4634436-A1  ·  semantic mode  ·  question language: fr

> Q1, Q5 et Q6 sont très proches sur le fond; Q5 offre la correspondance question-réponse la plus précise, tandis que Q4 ajoute des capacités non attestées.

- **Q1 · grok-4.3** (kept, faith 4.33, quality 4.50, ling 4): Comment des gaz inertes injectés aux deux pôles d'une cellule peuvent-ils servir à valider l'existence réelle de membranes défectueuses ?  
  — *au moins l'un du ou des premiers tests sur la base d'une injection de gaz inertes au niveau d'une anode et au niveau d'une cathode de chaque cellule*  
  reason: La question reformule de façon distinctive le rôle diagnostique de l’injection aux deux électrodes, même si la réponse indique seulement qu’un premier test repose sur cette injection sans en expliquer précisément le mécanisme.
- **Q2 · gemini-3.5-flash** (kept, faith 4.67, quality 4.00, ling 5): Quel protocole de validation applique-t-on suite à la substitution de composants détériorés pour garantir l'absence de pannes résiduelles ?  
  — *l'exécution d'un deuxième test pour évaluer s'il reste au moins une autre cellule endommagée*  
  reason: Le deuxième test après remplacement est bien décrit et fortement paraphrasé, quoique « garantir » soit légèrement plus fort que la simple évaluation mentionnée dans le passage.
- **Q3 · gpt-5-mini** (kept, faith 4.67, quality 3.75, ling 5): Quelle action est entreprise si, après le remplacement initial, le contrôle détecte encore des cellules endommagées ?  
  — *lorsqu'un résultat du deuxième test indique qu'il reste la ou les autres cellules endommagées, l'arrêt de l'électrolyseur et la répétition de l'exécution du ou des premiers tests, le remplacement de la ou des cellules, et l'exécution du deuxième test,*  
  reason: La réponse restitue fidèlement l’arrêt puis la répétition du cycle de test et de remplacement, avec seulement un peu de contexte conditionnel superflu.
- **Q4 · qwen3.6-35b-a3b** (DISCARDED, faith 3.33, quality 4.75, ling 5): Quelle technique permet de localiser les membranes fissurées au sein d'un électrolyseur sans démonter l'ensemble de la pile ?  
  — *l'injection de gaz inertes au niveau d'une anode et au niveau d'une cathode de chaque cellule*  
  reason: Le passage associe l’injection au dépistage de cellules à membrane endommagée, mais ne soutient ni la localisation de fissures ni l’affirmation d’une procédure sans démontage.
- **Q5 · gpt-5.4-mini** (kept, faith 5.00, quality 4.25, ling 5): Quelle stratégie de vérification utilise une injection de gaz inertes des deux côtés d'une cellule pour confirmer une cellule défectueuse ?  
  — *au moins l'un du ou des premiers tests sur la base d'une injection de gaz inertes au niveau d'une anode et au niveau d'une cathode de chaque cellule*  
  reason: Cette formulation claire et ciblée correspond directement au premier test fondé sur l’injection de gaz inertes à l’anode et à la cathode, malgré une proximité lexicale notable avec la source.
- **Q6 · sonnet-4.6** (kept, faith 4.33, quality 4.75, ling 5): Comment l'injection de gaz inertes côté anode et côté cathode peut-elle être exploitée pour diagnostiquer l'intégrité des séparateurs dans un système d'électrolyse ?  
  — *au moins l'un du ou des premiers tests sur la base d'une injection de gaz inertes au niveau d'une anode et au niveau d'une cathode de chaque cellule*  
  reason: La notion d’intégrité des séparateurs constitue une reformulation plausible des membranes endommagées et forme une requête conceptuelle distinctive, bien que la réponse ne détaille pas comment l’injection produit le diagnostic.

## MX-2025002756-A  ·  technical mode  ·  question language: en

> Q3 and Q4 are near-duplicates, while Q1 and Q6 also ask the same underlying fact; Q5 is the most retrieval-specific formulation.

- **Q1 · qwen3.6-35b-a3b** (DISCARDED, faith 5.00, quality 3.75, ling 5): What is the maximum allowable lead content in the alloy?  
  — *less than 0.1 wt %*  
  reason: The answer exactly matches the stated lead threshold, but the standalone query is underspecified because “the alloy” does not identify lead-free brass.
- **Q2 · gpt-5-mini** (DISCARDED, faith 5.00, quality 3.50, ling 5): What is the weight percent range of Cu in the alloy?  
  — *59 to 62 wt % Cu*  
  reason: The copper range is reproduced exactly, but the generic reference to “the alloy” gives the query little power to retrieve this particular document.
- **Q3 · gpt-5.4-mini** (kept, faith 5.00, quality 4.00, ling 4): What Mn content range is in the lead-free brass alloy?  
  — *2.0 to 2.5 wt % Mn*  
  reason: The manganese range is exact and the material is identified, although the construction “content range is in” is slightly awkward.
- **Q4 · grok-4.3** (kept, faith 5.00, quality 4.25, ling 5): What is the manganese content range in the lead-free brass alloy?  
  — *2.0 to 2.5 wt % Mn*  
  reason: This is a clear, focused composition query whose answer exactly reproduces the disclosed manganese range.
- **Q5 · gemini-3.5-flash** (kept, faith 5.00, quality 4.75, ling 5): What is the copper weight percent range in a lead-free brass alloy containing manganese and silicon?  
  — *59 to 62 wt %*  
  reason: The question accurately targets one value and uses the manganese-and-silicon composition context to distinguish the relevant lead-free brass alloy.
- **Q6 · sonnet-4.6** (kept, faith 5.00, quality 4.50, ling 5): What is the maximum allowable Pb content in lead-free brass alloy?  
  — *less than 0.1 wt % Pb*  
  reason: The query clearly identifies the material and asks for one threshold, with the answer exactly preserving the disclosed Pb limit and unit.

## MX-2025004470-A  ·  semantic mode  ·  question language: en

> Q4 and Q5 are strongly overlapping, while Q2 and Q6 introduce thermal-control rationales not stated in the passage.

- **Q1 · grok-4.3** (kept, faith 4.67, quality 4.00, ling 5): How can electric heating be combined with catalysis inside a dehydrogenation reactor?  
  — *heating the heated paraffinic feedstock in the first dehydrogenation reactor using the at least one first electrical heating element, and contacting the heated paraffinic feedstock with the active dehydrogenation catalyst and the at least one electrical heating element thereby producing an olefinic product stream comprising one or more olefins.*  
  reason: The answer directly describes simultaneous in-reactor electrical heating and catalyst contact, though the product-stream clause adds minor padding beyond the integration question.
- **Q2 · qwen3.6-35b-a3b** (DISCARDED, faith 4.33, quality 4.25, ling 5): How is precise thermal regulation maintained inside the catalytic reaction zone during paraffin conversion?  
  — *heating the heated paraffinic feedstock in the first dehydrogenation reactor using the at least one first electrical heating element*  
  reason: The extracted heating step is supported, but neither it nor the passage establishes precise thermal regulation or explains how such regulation is maintained.
- **Q3 · gpt-5.4-mini** (kept, faith 5.00, quality 3.50, ling 5): How is a paraffinic feedstock brought up to dehydrogenation temperature before entering the reactor?  
  — *combusting the fuel gas stream in the dehydrogenation reactor preheater and heating the paraffinic hydrocarbon feedstock to a temperature in the range of 500-650Â°C*  
  reason: The answer exactly identifies combustion-based preheating and preserves the 500-650Â°C range, although the query closely follows the source vocabulary and targets a straightforward process fact.
- **Q4 · gpt-5-mini** (kept, faith 5.00, quality 3.50, ling 5): What in-reactor heating strategy is used together with a catalyst to carry out the dehydrogenation reaction?  
  — *feeding the heated paraffinic feedstock to a first dehydrogenation reactor operating in a reaction mode and containing an active dehydrogenation catalyst and at least one first electrical heating element, heating the heated paraffinic feedstock in the first dehydrogenation reactor using the at least one first electrical heating element*  
  reason: The answer faithfully explains that an electrical heating element is placed and used alongside the active catalyst in the first reactor, but the wording has substantial source overlap.
- **Q5 · sonnet-4.6** (kept, faith 5.00, quality 4.25, ling 5): How can electrical heating elements be integrated inside a catalytic dehydrogenation reactor to supplement upstream combustion-based preheating?  
  — *feeding the heated paraffinic feedstock to a first dehydrogenation reactor operating in a reaction mode and containing an active dehydrogenation catalyst and at least one first electrical heating element, heating the heated paraffinic feedstock in the first dehydrogenation reactor using the at least one first electrical heating element*  
  reason: The question offers a distinctive system-level framing, and the answer accurately locates electrical heating in the catalytic reactor downstream of the passage's combustion preheater.
- **Q6 · gemini-3.5-flash** (DISCARDED, faith 4.33, quality 4.50, ling 5): How does the reaction vessel design counteract temperature drop during the endothermic conversion process?  
  — *heating the heated paraffinic feedstock in the first dehydrogenation reactor using the at least one first electrical heating element*  
  reason: Although the answer is an exact heating step, the passage does not state that the design counteracts a temperature drop or characterize the conversion as endothermic.

## MX-2025005046-A  ·  semantic mode  ·  question language: de

> Q5 ist die stärkste semantische Retrievalfrage; Q4 weist dagegen die deutlichste begriffliche Überdehnung auf.

- **Q1 · sonnet-4.6** (kept, faith 5.00, quality 4.25, ling 5): Welche Rolle spielen Magnetfelder bei der Erzeugung und Stabilisierung reaktiver Sauerstoffspezies in einem Wasserreinigungsgerät?  
  — *Das/die doppelte(n) Magnetringpaar(e) ist/sind so konfiguriert, dass es/sie die lokalen Magnetfelder verstärkt/verstärken und die Anzahl und mittlere Lebensdauer der radikalisierten Sauerstoffmoleküle erhöht/erhöhen und die Wasserreinigung verbessert/verbessern.*  
  reason: Die Antwort gibt die im Text beschriebene Verstärkung lokaler Magnetfelder sowie die erhöhte Zahl und Lebensdauer radikalisierter Sauerstoffmoleküle präzise wieder, und die Frage ist klar und konzeptionell relevant.
- **Q2 · gpt-5-mini** (kept, faith 5.00, quality 4.25, ling 4): Welcher mechanische oder physikalische Mechanismus wird eingesetzt, um die Zahl und Lebensdauer reaktiver Sauerstoffspezies zu erhöhen und dadurch die Reinigung zu verbessern?  
  — *Die doppelten Paare magnetischer Ringe sind so konfiguriert, die lokalen Magnetfelder zu verstärken, die Anzahl und die mittlere Lebensdauer radikalisierten Sauerstoffmolekülen zu erhöhen und die Wasserreinigung zu verbessern.*  
  reason: Der gesuchte physikalische Mechanismus und seine Wirkung sind vollständig belegt, auch wenn die Formulierung „mechanische oder physikalische“ etwas redundant wirkt.
- **Q3 · gpt-5.4-mini** (kept, faith 5.00, quality 4.25, ling 5): Wie kann UV-Licht zusammen mit Magnetfeldern die Bildung reaktiver Sauerstoffformen für die Wasserreinigung fördern?  
  — *Die UV-Strahlungs-Reflexionsabdeckung ist so ausgelegt, dass sie die Wechselwirkung von UV-Strahlung mit Sauerstoffmolekülen in der einströmenden Luft verstärkt. Das Doppelringpaar aus Magneten intensiviert die lokalen Magnetfelder und erhöht die Anzahl und mittlere Lebensdauer radikalisierter Sauerstoffmoleküle und verbessert die Wasserreinigung.*  
  reason: Frage und Antwort verbinden die beiden unmittelbar aufeinanderfolgenden, textlich belegten Funktionen der UV-Reflexionsabdeckung und der Magnetringpaare sinnvoll.
- **Q4 · gemini-3.5-flash** (DISCARDED, faith 4.33, quality 3.75, ling 4): Wie kann die Verweilzeit und Konzentration von aktivem Sauerstoff bei einer physikalischen Desinfektionsmethode künstlich verlängert und erhöht werden?  
  — *Das doppelte Magnetringpaar ist so konfiguriert, dass es die lokalen Magnetfelder intensiviert, die Anzahl und die mittlere Lebensdauer der radikalisierten Sauerstoffmoleküle erhöht und die Wasserreinigung verbessert.*  
  reason: Die Antwort ist zwar textnah, doch die Frage setzt chemische Lebensdauer mit Verweilzeit und Molekülzahl mit Konzentration gleich und führt zudem den nicht ausdrücklich belegten Desinfektionsbegriff ein.
- **Q5 · qwen3.6-35b-a3b** (kept, faith 5.00, quality 4.75, ling 5): Wie lässt sich die Bildung langlebiger reaktiver Sauerstoffspezies in einem belüfteten Reinigungssystem physikalisch optimieren?  
  — *Die UV-Strahlungsreflexionsabdeckung ist so ausgelegt, um die Wechselwirkung der UV-Strahlung mit Sauerstoffmolekülen in der einströmenden Luft zu verstärken. Das oder die doppelten magnetischen Ringpaare sind so konfiguriert, um die lokalen Magnetfelder zu intensivieren und die Anzahl sowie die mittlere Lebensdauer von radikalisiertem Sauerstoff zu erhöhen und die Wasserreinigung zu verbessern.*  
  reason: Die Frage formuliert das Zusammenwirken von Luft, UV-Reflexion und Magnetfeldern konzeptionell und gut auffindbar, während die Antwort beide belegten Mechanismen vollständig erfasst.
- **Q6 · grok-4.3** (kept, faith 4.67, quality 3.75, ling 5): Wie lässt sich die Bildung reaktiver Sauerstoffspezies durch UV-Strahlung in einem Wassersystem gezielt verstärken?  
  — *Die UV-Strahlungsreflektionsabdeckung ist konfiguriert, um die Interaktion der UV-Strahlung mit Sauerstoffmolekülen in der eintretenden Luft zu verstärken.*  
  reason: Die Reflexionsabdeckung und ihre Verstärkung der UV-Sauerstoff-Wechselwirkung sind direkt belegt, wenngleich die Bildung reaktiver Sauerstoffspezies im Text nur indirekt aus dieser Wechselwirkung folgt.

## MX-2025006624-A  ·  semantic mode  ·  question language: fr

> Plusieurs questions introduisent des bénéfices de rhéologie, de réactivité ou de mise en œuvre industrielle que le passage ne revendique pas explicitement.

- **Q1 · qwen3.6-35b-a3b** (DISCARDED, faith 5.00, quality 4.25, ling 5): Quelle stratégie formulation permet d'intégrer des précurseurs renouvelables dans des systèmes de revêtements durcis par rayonnement tout en contrôlant la rhéologie ?  
  — *a poly(trimethylene ether) (meth)acrylate compound A having at most two (meth)acrylate groups obtainable by a condensation reaction of biobased 1,3 poly(trimethylene ether) glycol and a (meth)acrylate compound selected from the group consisting of (meth)acrylic acid, (meth)acryloyl chloride, and /or alkylesters thereof*  
  reason: La voie chimique citée est directement étayée, mais la réponse omet le composé B et sa viscosité, indispensables pour répondre à l'aspect de contrôle rhéologique.
- **Q2 · gemini-3.5-flash** (kept, faith 5.00, quality 3.25, ling 5): Quels réactifs sont mis en œuvre pour synthétiser le monomère à base de polyéther-acrylate d'origine naturelle utilisé dans la formulation ?  
  — *une réaction de condensation de biobased 1,3 poly(trimethylene ether) glycol et un (meth)acrylate compound choisi dans le groupe constitué par (meth)acrylic acid, (meth)acryloyl chloride, et /ou alkylesters de ceux-ci*  
  reason: La question est claire et la réponse identifie fidèlement les deux catégories de réactifs, même si elle vise surtout un fait de synthèse et reste lexicalement proche du passage.
- **Q3 · gpt-5-mini** (kept, faith 4.67, quality 3.75, ling 5): Comment la formulation intègre-t-elle un monomère d'origine biobasée dans un revêtement curable par rayonnement actinique ?  
  — *La composition comprend de 10 wt% à 90 wt%, basé sur le poids total de la composition, d'un poly(trimethylene ether) (meth)acrylate compound A ayant au plus deux groupes (meth)acrylate, obtenable par une réaction de condensation de biobased 1,3 poly(trimethylene ether) glycol et d'un composé de (meth)acrylate sélectionné dans le groupe constitué par (meth)acrylic acid, (meth)acryloyl chloride et/ou leurs alkylesters; wherein the biobased 1,3 poly(trimethylene ether) glycol has a number average molecular weight Mn of from 350 to 600 g/mol, more preferably from 400 to 550 g/mol.*  
  reason: La réponse décrit fidèlement l'incorporation du composé A avec des valeurs exactes, bien que le détail sur la masse moléculaire soit légèrement plus développé que nécessaire et que la paraphrase soit limitée.
- **Q4 · gpt-5.4-mini** (DISCARDED, faith 5.00, quality 3.75, ling 4): Comment rendre un revêtement durcissable par radiation actinique tout en utilisant un monomère issu d’un glycol biobasé ?  
  — *une composition de revêtement durcissable par radiation actinique comprenant de 10 wt% à 90 wt% d’un composé A de poly(trimethylene ether) (meth)acrylate*  
  reason: Le constituant et sa teneur sont correctement repris, mais la réponse n'indique pas explicitement que le composé A provient du glycol biobasé mentionné dans la question.
- **Q5 · sonnet-4.6** (DISCARDED, faith 5.00, quality 4.00, ling 5): Comment intégrer des matières premières renouvelables dans une formulation de revêtement durcissable par rayonnement sans sacrifier la réactivité ?  
  — *un composé de (met)acrilato de poly(triméthylène éther) A ayant au plus deux groupes (meth)acrylate, obtenu par réaction de condensation de 1,3 poly(trimethylene ether) glycol d'origine biologique et un composé (meth)acrylate choisi dans le groupe constitué de l'acide (meth)acrylique, du chlorure de (meth)acryloyle et/ou de leurs alkylesters*  
  reason: La préparation du composé biobasé est bien étayée, mais le passage ne démontre pas que cette intégration se fait sans perte de réactivité.
- **Q6 · grok-4.3** (DISCARDED, faith 5.00, quality 3.50, ling 3): Existe-t-il des revêtements polymérisables par actinique qui incorporent des matériaux d'origine biologique tout en maintenant des propriétés de mise en œuvre industrielles ?  
  — *composition de revêtement curable par radiation actinique qui comprend de 10 % en poids à 90 % en poids d'un composé A et entre 10 % en poids et 89.99 % en poids d'un composé B*  
  reason: Les plages de composition sont exactes, mais la réponse ne justifie ni l'origine biologique ni le maintien de propriétés industrielles, et la tournure « polymérisables par actinique » est maladroite.

## MX-2025007206-A  ·  technical mode  ·  question language: de

> Alle sechs Fragen zielen auf denselben Temperaturschwellenwert; Q1 ist die stärkste Kombination aus Genauigkeit, Natürlichkeit und Spezifität.

- **Q1 · grok-4.3** (kept, faith 5.00, quality 4.50, ling 5): Oberhalb welcher Temperatur ermöglichen rAAV-Formulierungen langfristige Lagerung?  
  — *oberhalb von -80 °C*  
  reason: Die Frage ist natürlich formuliert, fokussiert auf den rAAV-Lagerungsschwellenwert und wird durch „oberhalb von -80 °C“ exakt beantwortet.
- **Q2 · qwen3.6-35b-a3b** (kept, faith 4.67, quality 4.50, ling 5): Ab welcher Temperatur ist eine langfristige Lagerung der rAAV-Formulierungen möglich?  
  — *above -80°C*  
  reason: Die Antwort entspricht dem Passageinhalt und dem exakten Wert, wobei „ab“ geringfügig inklusiver klingt als das im Text verwendete „oberhalb“.
- **Q3 · gpt-5.4-mini** (kept, faith 5.00, quality 4.25, ling 5): Bei welcher Temperatur können die rAAV-Formulierungen längerfristig gelagert werden?  
  — *bei Temperaturen über -80 °C*  
  reason: Die flüssige und fokussierte Frage nennt rAAV-Formulierungen und erhält mit dem exakt belegten Temperaturbereich eine passende Antwort.
- **Q4 · sonnet-4.6** (DISCARDED, faith 4.33, quality 3.75, ling 4): Bei welcher Mindesttemperatur kann eine rAAV-Formulierung für die Langzeitlagerung im Regal gelagert werden?  
  — *oberhalb von -80°C*  
  reason: Der Zahlenwert ist belegt, doch „Mindesttemperatur“ deutet fälschlich einen eingeschlossenen Minimalwert an und „im Regal gelagert“ wirkt wie eine unbeholfene wörtliche Übersetzung.
- **Q5 · gemini-3.5-flash** (kept, faith 5.00, quality 4.25, ling 4): Über welcher Lagertemperatur ermöglichen die rAAV-Formulierungen eine langfristige Haltbarkeit?  
  — *-80°C*  
  reason: Die Frage kodiert die Oberhalb-Beziehung korrekt und die Antwort gibt den exakten Schwellenwert wieder, auch wenn „Über welcher Lagertemperatur“ etwas unidiomatisch klingt.
- **Q6 · gpt-5-mini** (DISCARDED, faith 5.00, quality 3.50, ling 5): Welche Lagertemperatur wird für langfristige Aufbewahrung genannt?  
  — *temperatures above -80 °C*  
  reason: Die Antwort ist ein exakter Passagenspan, aber die Frage nennt weder rAAV noch Formulierungen und ist daher für eine technische Suche zu unspezifisch.

## MX-2025007510-A  ·  semantic mode  ·  question language: es

> Q4 es la candidata más sólida; varias de las demás emplean fragmentos literales que no responden con precisión al mecanismo o estrategia preguntados.

- **Q1 · qwen3.6-35b-a3b** (kept, faith 4.67, quality 4.50, ling 5): ¿Qué estrategia de formulación permite vehicular y proteger principios activos de origen ácido que se eliminan rápidamente del organismo?  
  — *una composición farmacéutica que contiene liposomas*  
  reason: La respuesta identifica fielmente la formulación liposomal y la pregunta ofrece una buena reformulación conceptual, aunque la función protectora no se afirma expresamente en el pasaje.
- **Q2 · sonnet-4.6** (DISCARDED, faith 4.33, quality 4.50, ling 5): ¿Qué estrategia de encapsulación lipídica permite reducir la frecuencia de administración en el tratamiento de la hipertensión pulmonar?  
  — *el uso de la composición farmacéutica descrita en la presente para tratar hipertensión pulmonar con frecuencia de dosificación reducida*  
  reason: Aunque el fragmento de respuesta está literalmente respaldado, no identifica de forma autónoma la estrategia de encapsulación solicitada y depende de la referencia vaga a «la composición descrita».
- **Q3 · gemini-3.5-flash** (DISCARDED, faith 4.33, quality 3.50, ling 5): ¿Qué trastorno circulatorio se pretende tratar disminuyendo la cantidad de tomas diarias de la terapia?  
  — *tratar hipertensión pulmonar con frecuencia de dosificación reducida*  
  reason: La hipertensión pulmonar está correctamente identificada, pero «tomas diarias» introduce una periodicidad no especificada y la pregunta se limita principalmente a recuperar una indicación clínica factual.
- **Q4 · gpt-5-mini** (kept, faith 5.00, quality 4.25, ling 5): ¿En qué indicación clínica se plantea usar esta formulación y qué beneficio de dosificación aporta?  
  — *tratar hipertensión pulmonar con frecuencia de dosificación reducida.*  
  reason: La pregunta recupera con claridad tanto la indicación como el beneficio posológico, y la respuesta es un fragmento exacto, pertinente y plenamente respaldado.
- **Q5 · gpt-5.4-mini** (DISCARDED, faith 4.00, quality 3.75, ling 5): ¿Qué tipo de formulación se usa para encapsular un fármaco de ácido débil de vida media corta?  
  — *una composición farmacéutica que contiene liposomas, el liposoma comprende una bicapa de lípido externa; y un medio acuoso interno que incluye 5 un fármaco de ácido débil con una vida media de menos de 2 hours.*  
  reason: La formulación liposomal y la vida media están respaldadas, pero la respuesta es innecesariamente extensa, conserva el artefacto «5» y mezcla español e inglés en lugar de dar el tipo de formulación de manera limpia.
- **Q6 · grok-4.3** (DISCARDED, faith 4.00, quality 3.75, ling 3): Manera de bajar la frecuencia con que se administra medicación a pacientes con hipertensión pulmonar  
  — *para tratar hipertensión pulmonar con frecuencia de dosificación reducida*  
  reason: El fragmento está presente en la fuente, pero repite el objetivo de reducir la frecuencia sin explicar la manera de lograrlo y la consulta está formulada como un sintagma incompleto.

## MX-2025009131-A  ·  technical mode  ·  question language: zh

> Q1、Q3、Q4和Q5询问同一加压介质，其中Q3和Q4因工艺语境完整而明显优于较泛化的Q1和Q5。

- **Q1 · qwen3.6-35b-a3b** (kept, faith 5.00, quality 4.00, ling 4): 为升高腔室或型腔压力使用的是何种流体？  
  — *超临界流体*  
  reason: 答案准确对应原文中的超临界流体，问题简洁且只问一个事实，但未提及柔性泡沫或高压釜，检索特异性一般。
- **Q2 · gpt-5-mini** (DISCARDED, faith 5.00, quality 3.25, ling 3): 聚合物由哪类聚合物组成？  
  — *one or more non-cross-linked thermoplastic polymers that are recyclable and/or biodegradable*  
  reason: 答案是原文的直接连续表述，但“聚合物由哪类聚合物组成”措辞重复、缺少工艺语境且难以锁定该文献。
- **Q3 · gemini-3.5-flash** (kept, faith 5.00, quality 4.75, ling 5): 在柔性泡沫生产工艺中，使用什么对高压釜腔或模腔进行加压？  
  — *supercritical fluid*  
  reason: 问题明确结合柔性泡沫、高压釜腔和模腔，答案由原文直接支持，表述自然且聚焦单一事实。
- **Q4 · sonnet-4.6** (kept, faith 5.00, quality 4.75, ling 5): 生产柔性泡沫时，用什么流体对高压釜腔室或模具腔体加压？  
  — *supercritical fluid*  
  reason: 该问题自然、具体并包含足够的工艺检索线索，且答案“supercritical fluid”与原文完全一致。
- **Q5 · gpt-5.4-mini** (DISCARDED, faith 5.00, quality 3.50, ling 3): 用于把腔体加压到高压的流体是什么？  
  — *超临界流体*  
  reason: 答案忠实且问题只涉及一个事实，但“把腔体加压到高压”略显生硬和重复，且缺少泡沫、高压釜或聚合物等区分性信息。
- **Q6 · grok-4.3** (DISCARDED, faith 5.00, quality 3.50, ling 5): 维持升高压力是为了什么？  
  — *to infuse the supercritical fluid into the polymer*  
  reason: 答案准确说明维持升高压力是为了使超临界流体渗入聚合物，但问题脱离泡沫制造语境后过于宽泛，检索区分度不足。

## MX-2025009666-A  ·  technical mode  ·  question language: en

> Q2 and Q4 are near duplicates, as are Q3, Q5, and Q6, so the set has substantial redundancy despite each question being independently valid.

- **Q1 · grok-4.3** (kept, faith 5.00, quality 4.25, ling 5): What solvent is used to form the metallocene solution?  
  — *hydrocarbon solvent*  
  reason: The answer is directly supported, concise, and the fluent question targets one clearly identifiable component of the metallocene-solution preparation.
- **Q2 · gpt-5-mini** (kept, faith 5.00, quality 4.00, ling 5): Where are the one or more gas outlets located on the dump tank vessel?  
  — *at a top of the vessel*  
  reason: The location is extracted exactly and the question is focused and specific, although its wording closely mirrors the source.
- **Q3 · qwen3.6-35b-a3b** (kept, faith 5.00, quality 4.25, ling 5): Where is the fluid outlet positioned in the dump tank vessel?  
  — *at a bottom of the vessel*  
  reason: The answer exactly matches the passage, while the concise, fluent question asks for a single well-defined equipment detail.
- **Q4 · gemini-3.5-flash** (kept, faith 5.00, quality 4.00, ling 5): Where are the gas outlets located on the dump tank vessel?  
  — *at a top of the vessel*  
  reason: This is a faithful and focused equipment-location query, though it uses much of the passage's original terminology.
- **Q5 · gpt-5.4-mini** (kept, faith 5.00, quality 4.00, ling 5): Where is the fluid outlet located in the dump tank?  
  — *at a bottom of the vessel*  
  reason: The answer is fully grounded and the question is economical and fluent, although identifying only the dump tank makes it slightly less document-specific.
- **Q6 · sonnet-4.6** (kept, faith 5.00, quality 4.00, ling 4): Where is the fluid outlet located on the dump tank vessel used to receive reactor product?  
  — *at a bottom of the vessel*  
  reason: The added reactor-product context makes the query highly specific and the answer is exact, but the wording is somewhat cumbersome and source-like.

## MX-2025010190-A  ·  technical mode  ·  question language: en

> Q1, Q2, and Q6 are near-duplicates; Q2 is the strongest of the three because it offers slightly better paraphrasing while retaining specificity.

- **Q1 · sonnet-4.6** (kept, faith 5.00, quality 4.00, ling 5): What type of amino acid profile does the recombinant polypeptide in the nutritional composition provide?  
  — *a nutritionally complete amino acid profile*  
  reason: The answer is directly supported and the question is fluent and focused, though its wording closely tracks the title and abstract.
- **Q2 · qwen3.6-35b-a3b** (kept, faith 5.00, quality 4.25, ling 5): What type of amino acid profile characterizes the recombinant polypeptide in the nutritional composition?  
  — *nutritionally complete amino acid profile*  
  reason: This is a clear, focused paraphrase whose concise answer is explicitly stated in the passage.
- **Q3 · gpt-5.4-mini** (DISCARDED, faith 5.00, quality 3.00, ling 5): What do the polynucleotides encode?  
  — *the recombinant polypeptides*  
  reason: Although the answer is fully supported, the query is too generic to distinguish this patent from numerous unrelated documents about polynucleotides.
- **Q4 · gemini-3.5-flash** (kept, faith 5.00, quality 4.50, ling 5): What encodes the recombinant polypeptides with a nutritionally complete amino acid profile?  
  — *polynucleotides*  
  reason: The question accurately links the encoding polynucleotides to the nutritionally complete recombinant polypeptides and is specific, concise, and focused.
- **Q5 · grok-4.3** (kept, faith 5.00, quality 3.75, ling 4): What forms of polypeptide are suitable to provide a nutritionally complete amino acid profile when provided in a nutritional composition?  
  — *a recombinant polypeptide and variants and truncates thereof*  
  reason: The answer is directly extracted and highly specific, but the question is somewhat cumbersome and reproduces much of the source phrasing.
- **Q6 · gpt-5-mini** (kept, faith 5.00, quality 3.75, ling 5): What amino acid profile does the recombinant polypeptide have?  
  — *a nutritionally complete amino acid profile*  
  reason: The question is accurate, concise, and single-focused, although it provides less document-specific context and closely echoes the passage.

## WO-2022005333-A1  ·  semantic mode  ·  question language: en

> Q1 and Q6 are the most distinctive performance-oriented queries, whereas Q3 is overly source-like and Q4 is better suited to a factual than a semantic benchmark.

- **Q1 · sonnet-4.6** (kept, faith 4.67, quality 4.50, ling 5): How can low-value refinery off-gases like propane-propylene or butane-butylene cuts be converted into high-octane gasoline?  
  — *The method makes it possible to produce gasolines using low-demand olefin-containing fractions, such as dry gas from catalytic cracking, a propane-propylene fraction or a butane-butylene fraction, and to increase the octane rating of the product to 95-98 at a product yield of more than 70 wt%*  
  reason: The answer is directly grounded and numerically exact, while the query offers a natural, specific conceptual framing despite including yield information beyond the main request.
- **Q2 · gemini-3.5-flash** (kept, faith 5.00, quality 4.00, ling 5): How can chemical processors salvage low-demand refinery byproducts containing olefins for fuel synthesis?  
  — *produce gasolines using low-demand olefin-containing fractions, such as dry gas from catalytic cracking, a propane-propylene fraction or a butane-butylene fraction*  
  reason: This fluent and well-paraphrased resource-valorization query has an exact supporting span, though its lack of named feedstocks makes it only moderately distinctive.
- **Q3 · gpt-5-mini** (DISCARDED, faith 5.00, quality 3.50, ling 5): How can low-value olefin-rich feeds like dry catalytic cracking gas or propane‑propylene cuts be converted into gasoline in this process?  
  — *The method makes it possible to produce gasolines using low-demand olefin-containing fractions, such as dry gas from catalytic cracking, a propane-propylene fraction or a butane-butylene fraction,*  
  reason: Although fully supported and specific, the query closely mirrors the source vocabulary, depends on the vague phrase “this process,” and receives a largely circular answer.
- **Q4 · qwen3.6-35b-a3b** (DISCARDED, faith 5.00, quality 3.25, ling 5): Which unutilized refinery byproduct streams are suitable for conversion into high-quality automotive fuel?  
  — *low-demand olefin-containing fractions, such as dry gas from catalytic cracking, a propane-propylene fraction or a butane-butylene fraction*  
  reason: The extracted list is exact and the wording is strongly paraphrased, but the question seeks a simple factual enumeration and is too generic to distinguish this document reliably.
- **Q5 · grok-4.3** (kept, faith 5.00, quality 4.25, ling 5): How can low-demand refinery gases like catalytic cracking dry gas be upgraded into gasoline?  
  — *produce gasolines using low-demand olefin-containing fractions, such as dry gas from catalytic cracking, a propane-propylene fraction or a butane-butylene fraction*  
  reason: The concise query naturally frames upgrading catalytic-cracking gas as a resource-use concept, and its answer is a precise source span despite moderate vocabulary overlap.
- **Q6 · gpt-5.4-mini** (kept, faith 4.67, quality 4.00, ling 5): How can low-value olefin-rich byproduct streams be converted into gasoline with higher octane and yield?  
  — *The method makes it possible to produce gasolines using low-demand olefin-containing fractions, such as dry gas from catalytic cracking, a propane-propylene fraction or a butane-butylene fraction, and to increase the octane rating of the product to 95-98 at a product yield of more than 70 wt%, while also reducing the diesel fraction content to less than 2 wt%*  
  reason: The question captures the passage’s combined feedstock-valorization and performance concept with exact figures, although the answer adds an unrequested diesel-content result.

## WO-2023149795-A1  ·  technical mode  ·  question language: en

> Q1–Q5 are highly redundant variants of the same fact, with Q5 offering the strongest paraphrasing among them.

- **Q1 · gpt-5.4-mini** (kept, faith 5.00, quality 4.50, ling 5): What protein synthesis stimulator is added to the second nutrient medium?  
  — *zinc acetate*  
  reason: The question is fluent, focused, and directly supported by the passage, with zinc acetate precisely identified as the second medium's protein synthesis stimulator.
- **Q2 · grok-4.3** (kept, faith 5.00, quality 4.25, ling 5): What protein synthesis stimulator is included in the second nutrient medium?  
  — *zinc acetate*  
  reason: The answer is exactly grounded and the query is clear and focused, though its wording closely mirrors the source.
- **Q3 · gpt-5-mini** (kept, faith 5.00, quality 4.25, ling 5): Which protein synthesis stimulator is included in the second nutrient medium?  
  — *zinc acetate*  
  reason: This is a grammatical, single-fact query whose answer is directly stated, although it uses much of the passage's original phrasing.
- **Q4 · sonnet-4.6** (kept, faith 5.00, quality 4.75, ling 5): What protein synthesis stimulator is added to the second nutrient medium for insect larval cultivation?  
  — *zinc acetate*  
  reason: The added cultivation context makes the focused query more document-specific while retaining a fully supported and precise answer.
- **Q5 · gemini-3.5-flash** (kept, faith 5.00, quality 4.75, ling 5): What chemical is used as a protein synthesis stimulator in the second nutrient medium?  
  — *zinc acetate*  
  reason: The question provides a concise and natural paraphrase of the relevant fact, and zinc acetate is fully supported as the requested chemical.
- **Q6 · qwen3.6-35b-a3b** (kept, faith 5.00, quality 4.75, ling 5): At what temperature are the lyophilized larvae re-ground?  
  — *-55°C*  
  reason: The query asks one specific processing fact, and the answer reproduces the stated re-grinding temperature of -55°C exactly.

## WO-2025054647-A1  ·  semantic mode  ·  question language: es

> Varias respuestas mezclan español con conectores o términos ingleses y franceses, pese a conservar correctamente todos los valores numéricos.

- **Q1 · sonnet-4.6** (kept, faith 5.00, quality 4.00, ling 5): ¿Qué propiedades mecánicas y de transporte debe reunir una matriz que aloje un medio de almacenamiento termoquímico para funcionar de forma estable en un amplio rango térmico?  
  — *die Matrix einen Gasdiffusionskoeffizient für das Gas von 2,25*10-9 m2/s bis 4,25*10-9 m2/s in einem Temperaturbereich von -30°C bis 300°C, und eine maximale Dehnung ε im Hooke'schen Bereich von 25% bis 300% aufweist*  
  reason: La pregunta reformula con fluidez las propiedades mecánicas y de transporte de la matriz, y la respuesta reproduce fielmente todos los valores y rangos pertinentes.
- **Q2 · qwen3.6-35b-a3b** (DISCARDED, faith 4.33, quality 4.00, ling 4): ¿Qué parámetros de permeabilidad y dilatación estructural debe cumplir el material soporte para garantizar un funcionamiento estable en acumuladores de calor químico?  
  — *la matriz tiene un coeficiente de difusión de gas para el gas de 2.25*10 -9 m 2 /s to 4.25*10 -9 m 2 /s en un rango de temperatura de -30°C to 300°C, y una expansión máxima ε en el rango de la ley de Hooke de 25% to 300%*  
  reason: Aunque las cifras son exactas y la consulta resulta plausible, equipara de manera imprecisa el coeficiente de difusión con la permeabilidad y afirma una garantía de estabilidad no expresada en el pasaje.
- **Q3 · gpt-5-mini** (kept, faith 5.00, quality 3.50, ling 4): ¿Qué diseño estructural integra el material termochímico y qué propiedades de difusión y deformación especifica la matriz?  
  — *el medio de almacenamiento termochímico incorporado en una matriz; la matriz tiene un coeficiente de difusión de gas para el gas de 2.25*10 -9 m 2 /s a 4.25*10 -9 m 2 /s en un intervalo de temperatura de -30°C a 300°C, y una expansión máxima ε en el rango de la ley de Hooke de 25% a 300%; el medio de almacenamiento termochímico está distribuido sustancialmente de forma homogénea en la matriz.*  
  reason: La pregunta es específica y recuperable, y su respuesta cubre fielmente la incorporación, la distribución homogénea y las propiedades cuantitativas de la matriz, aunque permanece bastante próxima al texto fuente.
- **Q4 · gpt-5.4-mini** (DISCARDED, faith 5.00, quality 2.75, ling 4): ¿Qué características debe tener la matriz para funcionar bien en un sistema de almacenamiento térmico de este tipo?  
  — *la matriz presentando un coeficiente de difusión de gas para el gas de 2,25*10 -9 m 2 /s a 4,25*10 -9 m 2 /s en una plage de temperatura de -30 °C a 300 °C, y una expansión máxima ε en la plage de ley de Hooke de 25 % a 300 %*  
  reason: La respuesta está respaldada y conserva las cifras, pero la referencia vaga a «un sistema de este tipo» hace que la consulta sea poco autónoma y escasamente discriminativa.
- **Q5 · grok-4.3** (kept, faith 5.00, quality 4.00, ling 3): ¿Qué propiedades de transporte de gas y de estabilidad mecánica debe poseer la estructura soporte para que un material termquímico funcione correctamente en un amplio margen de temperaturas?  
  — *la matriz tiene un coeficiente de difusión de gas para el gas de 2,25*10-9 m2/s a 4,25*10-9 m2/s en un rango de temperatura de -30°C a 300°C, y una expansión máxima ε en el rango de la ley de Hooke de 25% a 300%*  
  reason: La consulta ofrece una buena reformulación conceptual de las propiedades de transporte y estabilidad, con una respuesta exacta, aunque contiene la errata «termquímico».
- **Q6 · gemini-3.5-flash** (DISCARDED, faith 4.00, quality 4.25, ling 5): ¿Cómo se resuelven las tensiones mecánicas por dilatación y se asegura la permeabilidad al gas en acumuladores térmicos que operan en condiciones térmicas extremas?  
  — *la matriz presenta un coeficiente de difusión de gas para el gas de 2.25*10 -9 m 2 /s a 4.25*10 -9 m 2 /s en un rango de temperatura de -30°C a 300°C, y una expansión máxima ε en el rango de la ley de Hooke de 25% a 300%*  
  reason: La formulación tiene buena distancia léxica y plantea un problema conceptual, pero el pasaje solo especifica propiedades de la matriz y no explica cómo se resuelven tensiones ni cómo se asegura la permeabilidad.

## WO-2025177605-A1  ·  technical mode  ·  question language: fr

> Q4 et Q6 sont les meilleures formulations sur le procédé de soudage, tandis que Q1–Q3 sont largement redondantes sur la teneur en aluminium.

- **Q1 · grok-4.3** (kept, faith 5.00, quality 4.00, ling 5): Quelle est la teneur minimale en Al de l'alliage à base de Ni ?  
  — *2,0% en poids ou plus d'Al*  
  reason: La réponse reproduit exactement le seuil minimal d’aluminium, et la question est claire et ciblée, quoique peu spécifique à la cornue concernée.
- **Q2 · sonnet-4.6** (kept, faith 5.00, quality 4.50, ling 5): Quelle est la teneur minimale en Ni requise dans l'alliage à base de Ni utilisé pour le matériau de base d'une cornue ?  
  — *90,0% en poids ou plus de Ni*  
  reason: La teneur minimale de 90,0 % en poids de Ni est fidèlement restituée dans une question précise qui identifie le matériau de base de la cornue.
- **Q3 · gpt-5-mini** (DISCARDED, faith 5.00, quality 3.75, ling 4): Quel pourcentage d'Al contient l'alliage à base de Ni ?  
  — *2,0% en poids ou plus d'Al*  
  reason: Bien que la réponse soit exacte, la formulation demande un pourcentage apparemment fixe sans préciser qu’il s’agit d’une teneur minimale, ce qui la rend potentiellement trompeuse.
- **Q4 · qwen3.6-35b-a3b** (kept, faith 5.00, quality 4.50, ling 5): Quelle méthode de soudage est employée pour la fabrication de la cornue ?  
  — *soudage au plasma*  
  reason: La question demande clairement une seule méthode de soudage et la réponse « soudage au plasma » est directement étayée par le passage.
- **Q5 · gpt-5.4-mini** (DISCARDED, faith 5.00, quality 3.50, ling 3): Quel type de soudage est utilisé pour joindre la partie de jonction du matériau de base ?  
  — *soudage au plasma*  
  reason: La réponse est fidèle, mais l’expression « joindre la partie de jonction » est redondante et maladroite, et la formulation reprend de près celle du passage.
- **Q6 · gemini-3.5-flash** (kept, faith 5.00, quality 4.75, ling 5): Quelle méthode de soudage est utilisée pour assembler le matériau de base de la cornue ?  
  — *soudage au plasma*  
  reason: Cette paraphrase naturelle et concise cible une seule caractéristique technique, avec une réponse directement confirmée par le procédé décrit.

## WO-2025187661-A8  ·  semantic mode  ·  question language: es

> Q6 es la opción más sólida porque, a diferencia de varias respuestas circulares, proporciona la composición concreta que resuelve el problema planteado.

- **Q1 · grok-4.3** (DISCARDED, faith 4.67, quality 4.00, ling 4): ¿Cómo se puede evitar la formación de rebabas durante el reciclaje de resinas de poly(arylene sulfide)?  
  — *una composición de resina de poly(arylene sulfide) que, durante el reciclaje, puede ser inhibida de formar rebabas*  
  reason: La pregunta es específica y fiel al pasaje, pero la respuesta repite que la composición evita las rebabas sin explicar cómo lo consigue.
- **Q2 · qwen3.6-35b-a3b** (DISCARDED, faith 4.00, quality 4.50, ling 5): ¿Qué enfoque se propone para prevenir la aparición de rebabas o exudaciones al reprocesar polímeros de cadena aromática con enlaces de azufre?  
  — *can be inhibited from forming burrs*  
  reason: Aunque está muy bien parafraseada, introduce «exudaciones» y la respuesta solo enuncia el efecto inhibidor, no el enfoque solicitado.
- **Q3 · gpt-5.4-mini** (DISCARDED, faith 4.67, quality 4.00, ling 4): ¿Cómo se puede evitar que una resina de poly(arylene sulfide) reciclada genere rebabas?  
  — *que, durante el reciclaje, puede ser impedida de formar burrs*  
  reason: Es recuperable y está respaldada, pero la respuesta es circular, no ofrece la composición y mezcla innecesariamente español e inglés.
- **Q4 · gpt-5-mini** (DISCARDED, faith 5.00, quality 2.50, ling 5): ¿Qué defecto durante el reprocesado en planta pretende evitar esta composición de resina?  
  — *puede ser inhibida de formar rebabas durante el reciclaje.*  
  reason: La respuesta identifica correctamente las rebabas, pero la consulta es deíctica, poco distinguible fuera de contexto y pide un dato simple en vez de un concepto.
- **Q5 · gemini-3.5-flash** (kept, faith 4.67, quality 4.00, ling 5): ¿Cómo se puede resolver el reto de la aparición de imperfecciones físicas o rebabas en polímeros de ingeniería cuando se someten a procesos de recuperación y reprocesamiento?  
  — *una composición de resina de poly(arylene sulfide) que, durante el reciclaje, puede evitar la formación de rebabas*  
  reason: La formulación conceptual y alejada del léxico fuente sigue siendo coherente con la solución basada en una composición de poli(sulfuro de arileno), aunque resulta algo amplia.
- **Q6 · sonnet-4.6** (kept, faith 5.00, quality 4.50, ling 5): ¿Cómo se puede evitar la formación de rebabas durante el reciclado de resinas termoplásticas de alto rendimiento?  
  — *La composición de resina de poly(arylene sulfide) (X) para materiales de reciclaje comprende (A) 100 partes en masa de una resina de poly(arylene sulfide) lineal con grupo carboxy y (B) 0,3-10 partes en masa de un compuesto alkoxysilane.*  
  reason: La consulta plantea naturalmente el problema y la respuesta aporta la formulación completa respaldada por el pasaje, con cantidades y rango exactos.

## WO-2025202347-A1  ·  semantic mode  ·  question language: de

- **Q1 · qwen3.6-35b-a3b** (DISCARDED, faith 5.00, quality 3.00, ling 5): Welche Formulierungsstrategie ermöglicht es, iota-carrageenan als zentrales oder einziges therapeutisches Element in einer wässrigen Augenmedikation einzusetzen?  
  — *als Haupt- oder alleiniger Wirkstoff in einer wässrigen pharmazeutischen Zubereitung*  
  reason: Die Antwort ist vollständig belegt, doch die Frage nimmt mit „zentrales oder einziges therapeutisches Element“ und „wässriger Augenmedikation“ nahezu den gesamten Antwortinhalt bereits vorweg.
- **Q2 · gpt-5.4-mini** (kept, faith 5.00, quality 3.75, ling 5): Welche Art von Augenleiden soll mit einer iota-carrageenan-basierten Formulierung behandelt oder verhindert werden?  
  — *nicht allergische, nicht virale klinisch relevante Augenbeschwerden, die mindestens eines der folgenden Bereiche betreffen: die Schleimhautgewebe am oder um das Auge, die Augenoberfläche, das Hornhautgewebe und die Flüssigkeit im Auge*  
  reason: Die Frage erfasst den therapeutischen Anwendungsbereich auf konzeptioneller Ebene, und die Antwort gibt sowohl die Art der Erkrankungen als auch die betroffenen Augenstrukturen korrekt wieder.
- **Q3 · grok-4.3** (kept, faith 5.00, quality 4.25, ling 5): Wie lassen sich Augenirritationen durch luftgetragene Partikel, die keine Allergene sind, gezielt behandeln?  
  — *iota-Carrageenan als Haupt- oder alleiniger Wirkstoff in einer wässrigen pharmazeutischen Zusammensetzung zur Prävention oder Behandlung von Reizungen verursacht durch luftgetragene Partikelmasse außer Allergenen.*  
  reason: Die realistische Behandlungsfrage führt zu einer vollständig gestützten und dokumentenspezifischen Antwort über Iota-Carrageenan bei nicht allergenen luftgetragenen Partikeln.
- **Q4 · sonnet-4.6** (DISCARDED, faith 4.67, quality 4.00, ling 5): Wie können Spätfolgen einer nicht-viralen Bindehautentzündung, wie Hornhauttrübungen oder Pseudomembranbildung, pharmakologisch adressiert werden?  
  — *Die klinisch relevanten Augenerkrankungen umfassen Spätkomplikationen nicht-viraler und nicht-allergischer Konjunktivitis, ausgewählt aus der Gruppe bestehend aus Hornhauttrübungen (corneal opacities), subepitheliale Infiltrate und die Bildung okulärer Pseudomembranen (formation of ocular pseudomembranes).*  
  reason: Obwohl die aufgezählten Spätkomplikationen belegt sind, beantwortet die Antwort nicht die Frage nach der pharmakologischen Behandlungsmethode und enthält entbehrliche englische Glossare.
- **Q5 · gemini-3.5-flash** (kept, faith 5.00, quality 4.00, ling 5): Welche klinischen Folgeerscheinungen einer Bindehautreizung, die weder auf Allergene noch auf Viren zurückzuführen ist, lassen sich behandeln?  
  — *Spätkomplikationen einer nicht-viralen und nicht-allergischen Konjunktivitis, ausgewählt aus der Gruppe bestehend aus Hornhauttrübungen, subepithelialen Infiltraten und der Bildung von okulären Pseudomembranen*  
  reason: Die konzeptionell paraphrasierte Frage ist gut auffindbar und wird durch die vollständige, quellengetreue Liste der Spätkomplikationen beantwortet, auch wenn „Bindehautreizung“ weniger präzise als „Konjunktivitis“ ist.
- **Q6 · gpt-5-mini** (kept, faith 5.00, quality 3.50, ling 5): Welche konkreten Augenzustände und Spätkomplikationen können mit einer iota-carrageenan-haltigen Formulierung behandelt werden?  
  — *die klinisch relevanten Augenleiden sind ausgewählt aus der Gruppe bestehend aus erhöhter Augeninnendruck, nicht-allergischer und nicht-viraler Konjunktivitis, Reizungen verursacht durch luftgetragene Partikel außer Allergenen, und späte Komplikationen dieser Konjunktivitis, bestehend aus Kornea-Opazitäten, subepithelialen Infiltraten und Bildung von okulären Pseudomembranen.*  
  reason: Die Antwort reproduziert den gesamten gestützten Behandlungsumfang korrekt und ist sehr dokumentenspezifisch, wenngleich die Frage eher eine Faktenliste verlangt und lexikalisch eng an der Quelle bleibt.

## WO-2025207810-A1  ·  technical mode  ·  question language: zh

> Q1、Q2和Q4内容高度相近且质量相当；Q3和Q6的主要问题是中英混杂。

- **Q1 · gemini-3.5-flash** (kept, faith 5.00, quality 4.75, ling 5): 纠错条形码核苷酸序列是基于什么进行设计的？  
  — *Hamming codes*  
  reason: 问题表述自然且明确指向纠错条形码的设计依据，答案“Hamming codes”与原文完全一致。
- **Q2 · qwen3.6-35b-a3b** (kept, faith 5.00, quality 4.50, ling 5): 错误检查条形码核苷酸序列基于什么编码？  
  — *汉明码*  
  reason: 问题流畅、单一且具有较强检索指向性，答案“汉明码”准确翻译了原文中的“Hamming codes”。
- **Q3 · sonnet-4.6** (DISCARDED, faith 5.00, quality 4.00, ling 3): engineered hairpin structure在寡核苷酸中起什么作用？  
  — *mitigates hybridizing of the oligonucleotide to undesirable nucleic acid sequences*  
  reason: 答案忠实对应原文，但问题和答案均不必要地中英混杂，作为指定中文问题不够自然。
- **Q4 · grok-4.3** (kept, faith 5.00, quality 4.50, ling 5): 错误检查条形码核苷酸序列基于什么？  
  — *Hamming codes*  
  reason: 该问题简洁自然并聚焦于条形码序列的编码基础，英文答案也受到原文直接支持。
- **Q5 · gpt-5-mini** (kept, faith 5.00, quality 4.75, ling 5): 哪种结构可减弱寡核苷酸与不良核酸序列的杂交？  
  — *工程化的发夹结构*  
  reason: 问题以明确的功能反问对应结构，答案“工程化的发夹结构”准确且无多余信息。
- **Q6 · gpt-5.4-mini** (DISCARDED, faith 5.00, quality 3.50, ling 2): 错误校验 barcode nucleotide sequences 基于什么编码？  
  — *Hamming codes*  
  reason: 答案与原文一致，但“错误校验 barcode nucleotide sequences”的中英拼接明显生硬，不符合自然中文检索表达。

## WO-2025210445-A1  ·  technical mode  ·  question language: fr

> Q3 se distingue nettement grâce à son contexte sur la génération in situ des réactifs de Fenton, tandis que les autres requêtes pourraient correspondre à de nombreux équipements électrochimiques.

- **Q1 · grok-4.3** (DISCARDED, faith 5.00, quality 3.50, ling 5): Quelle tension est appliquée entre les électrodes ?  
  — *de préférence entre 0 V et 220 V, plus préférentiellement entre 1 V et 20 V*  
  reason: La réponse reproduit exactement les deux plages hiérarchisées, mais la question reste trop générique pour retrouver spécifiquement ce procédé électrochimique.
- **Q2 · qwen3.6-35b-a3b** (DISCARDED, faith 5.00, quality 3.25, ling 4): Quelle plage de tension est plus préférentiellement appliquée entre les électrodes ?  
  — *entre 1 V et 20 V*  
  reason: La plage de 1 V à 20 V est exacte et la demande est ciblée sur un seul fait, mais la formulation proche du passage et dépourvue de contexte technique est peu distinctive.
- **Q3 · sonnet-4.6** (kept, faith 5.00, quality 4.50, ling 5): Quelle est la plage de tension préférentielle appliquée entre les électrodes dans un procédé électrochimique de génération de réactifs de Fenton in situ ?  
  — *entre 1 V et 20 V*  
  reason: La réponse est numériquement exacte et la mention de la génération in situ des réactifs de Fenton rend la requête précise, fluide et propre à ce procédé.
- **Q4 · gpt-5.4-mini** (DISCARDED, faith 5.00, quality 3.75, ling 4): Quelle plage de tension est indiquée comme la plus préférée entre les électrodes ?  
  — *entre 1 V et 20 V*  
  reason: La réponse est entièrement étayée, mais « la plus préférée » est légèrement maladroit et aucun contexte ne distingue cette plage de celles de nombreux autres dispositifs.
- **Q5 · gpt-5-mini** (DISCARDED, faith 5.00, quality 3.50, ling 4): Plage de tension préférée entre les électrodes  
  — *de préférence entre 0 V et 220 V, plus préférentiellement entre 1 V et 20 V*  
  reason: Cette requête nominale convient à une barre de recherche et son answer est exact, mais elle est trop générique et regroupe deux niveaux de préférence sans préciser le procédé concerné.
- **Q6 · gemini-3.5-flash** (DISCARDED, faith 5.00, quality 3.25, ling 4): Quelle plage de tension est plus préférentiellement appliquée entre les électrodes ?  
  — *entre 1 V et 20 V*  
  reason: La réponse correspond exactement à la plage la plus préférentielle, mais la question reprend étroitement le libellé du passage et manque de termes identifiant l'invention.

## WO-2025211128-A1  ·  technical mode  ·  question language: en

> Q2 and Q6 are the strongest retrieval questions; Q1, Q3, Q4, and Q5 repeatedly target the same recess-depth fact with varying amounts of identifying context.

- **Q1 · gpt-5-mini** (DISCARDED, faith 5.00, quality 3.00, ling 5): What recess depth from the surface is required?  
  — *0.5 μm or less*  
  reason: The answer is exact and the question is fluent and focused, but without identifying the silicon member it is too generic and closely echoes the source wording.
- **Q2 · sonnet-4.6** (kept, faith 5.00, quality 4.75, ling 5): What is the maximum recess depth from the surface specified for a polycrystalline silicon member?  
  — *0.5 μm or less*  
  reason: This fluent, focused query accurately frames 0.5 μm as the maximum recess depth and provides enough technical context to retrieve the relevant document.
- **Q3 · gemini-3.5-flash** (kept, faith 5.00, quality 3.75, ling 5): What is the recess depth from the surface of the silicon member?  
  — *0.5 μm or less*  
  reason: The question is faithful, numerically exact, and adequately specific through its reference to the silicon member, though its wording is largely lifted from the passage.
- **Q4 · gpt-5.4-mini** (DISCARDED, faith 5.00, quality 2.75, ling 5): What is the recess depth from the surface?  
  — *0.5 μm or less*  
  reason: Although the answer is fully supported and the question asks one fact, the absence of any silicon or polycrystalline context makes it far too generic for retrieval.
- **Q5 · grok-4.3** (kept, faith 5.00, quality 3.75, ling 5): What is the recess depth from the surface of the silicon member?  
  — *0.5 μm or less*  
  reason: The query is clear, focused, and grounded with an exact answer, but it offers little paraphrasing beyond the source phrase.
- **Q6 · qwen3.6-35b-a3b** (kept, faith 5.00, quality 4.50, ling 5): What is the preferred percentage range of Σ9 grain boundaries within the coincidence grain boundary?  
  — *from 3% to 20%*  
  reason: This is a highly specific, fluent, single-fact query whose 3% to 20% answer exactly matches the stated preferred Σ9 grain-boundary range.

## WO-2025211336-A1  ·  semantic mode  ·  question language: en

> Q2 and Q6 are near-duplicate conceptual queries, with Q6 offering the greater lexical distance.

- **Q1 · gpt-5.4-mini** (DISCARDED, faith 5.00, quality 4.00, ling 5): How can a photocurable resin be made suitable for thick-film curing while still giving a flexible, heat-resistant cured product?  
  — *has favorable thick film curability and of which the cured product after curing is excellent in flexibility and heat resistance*  
  reason: Although the answer is directly extracted, it merely repeats the desired properties and does not explain how the resin can be made to achieve them.
- **Q2 · sonnet-4.6** (kept, faith 5.00, quality 4.75, ling 5): What approach addresses the challenge of achieving deep-section light cure in flexible, heat-stable coatings?  
  — *a photocurable resin composition which has favorable thick film curability and of which the cured product after curing is excellent in flexibility and heat resistance*  
  reason: The natural, conceptually framed query paraphrases the performance problem well, and the answer identifies the supported type of composition addressing it.
- **Q3 · qwen3.6-35b-a3b** (DISCARDED, faith 4.67, quality 4.50, ling 4): What specific ingredient combination enables UV-sensitive polymers to retain pliability and withstand high temperatures when cured into heavy layers?  
  — *component (A): a polyorganosiloxane having one or more vinyl groups in one molecule, component (B): a compound having one or more mercapto groups in one molecule, component (C): a photoinitiator, and component (D): hollow resin particles*  
  reason: The ingredient list is exact and highly retrievable, but describing the material specifically as UV-sensitive is an unsupported narrowing of the source's broader photocurable formulation.
- **Q4 · grok-4.3** (DISCARDED, faith 4.67, quality 4.25, ling 4): What components form the basis of a resin that relies on addition reactions between silicon-containing polymers and sulfur-based molecules for light-induced hardening along with filler particles?  
  — *includes component (A): a polyorganosiloxane having one or more vinyl groups in one molecule, component (B): a compound having one or more mercapto groups in one molecule, component (C): a photoinitiator, and component (D): hollow resin particles.*  
  reason: The answer accurately lists the components, but the question adds an unstated addition-reaction mechanism and calls the hollow particles fillers while using cumbersome phrasing.
- **Q5 · gpt-5-mini** (kept, faith 5.00, quality 4.00, ling 5): What combination of ingredient types is used to formulate a photocurable resin that yields flexible, heat-resistant cured films?  
  — *includes component (A): a polyorganosiloxane having one or more vinyl groups in one molecule, component (B): a compound having one or more mercapto groups in one molecule, component (C): a photoinitiator, and component (D): hollow resin particles.*  
  reason: This is a clear and faithful formulation query whose answer exactly supplies the four ingredient types, though its wording remains fairly close to the abstract.
- **Q6 · gemini-3.5-flash** (kept, faith 5.00, quality 5.00, ling 5): What type of material formulation is designed to solve the issue of poor depth-of-cure in thick coatings while maintaining thermal stability and bendability?  
  — *photocurable resin composition which has favorable thick film curability and of which the cured product after curing is excellent in flexibility and heat resistance*  
  reason: The question naturally reframes thick-film curability, heat resistance, and flexibility as a material-design problem, and the answer directly identifies the supported formulation.

## WO-2025212655-A1  ·  semantic mode  ·  question language: de

> Q1 is the strongest conceptual paraphrase, while Q2 relies most heavily on an inferred rather than explicitly stated benefit.

- **Q1 · gemini-3.5-flash** (kept, faith 5.00, quality 4.50, ling 5): Wie wird verhindert, dass die langen synthetisierten DNA-Stränge frei in Lösung driften oder unkontrolliert viel Platz auf dem Substrat einnehmen?  
  — *Die Concatemer-Templatmoleküle kollabieren zur Bildung kompakter DNA-Nanoballs, die stabil auf einem Träger immobilisiert sind.*  
  reason: The answer directly captures the disclosed collapse into compact, stably immobilized DNA nanoballs, while the question provides a strong conceptual paraphrase of that function.
- **Q2 · qwen3.6-35b-a3b** (kept, faith 4.33, quality 4.00, ling 5): Welche Strategie nutzt man, um DNA-Fragmente direkt auf einem festen Träger zu replizieren und dabei eine hohe lokale Dichte zu erreichen?  
  — *Die concatemer template molecules können durch die Durchführung von rolling circle amplification Reaktionen auf einem Träger erzeugt werden, der ein Gemisch aus immobilisierten capture und pinning primers umfasst.*  
  reason: The stated rolling-circle amplification strategy and mixed immobilized primers are supported, although the claimed high local density is only indirectly implied by nanoball compaction.
- **Q3 · sonnet-4.6** (kept, faith 5.00, quality 4.50, ling 5): Wie lassen sich DNA-Vorlagen für hochdurchsatzfähige Sequenzierläufe stabil auf einer festen Oberfläche verankern?  
  — *Die concatemer template molecules können durch die Durchführung von rolling circle amplification Reaktionen auf einem Support generiert werden, der eine Mischung aus immobilisierten capture und pinning primers enthält. Die entstehenden Moleküle kollabieren zu kompakten DNA nanoballs, die stabil auf dem Support immobilisiert sind.*  
  reason: The answer faithfully combines the support-based amplification method with the subsequent formation and stable immobilization of compact DNA nanoballs.
- **Q4 · gpt-5-mini** (kept, faith 5.00, quality 3.50, ling 5): Welcher Ansatz wird vorgeschlagen, um zahlreiche Vorlagen direkt auf einem festen Träger zu erzeugen?  
  — *In einigen Ausführungsformen können die concatemer template molecules erzeugt werden, indem rolling circle amplification-Reaktionen auf einem Support durchgeführt werden, der eine Mischung aus immobilisierten capture und pinning primers enthält.*  
  reason: The method is accurately extracted and clearly phrased, though the comparatively generic query and source-adjacent wording make it less distinctive.
- **Q5 · grok-4.3** (kept, faith 5.00, quality 4.00, ling 5): Welcher Amplifikationsmechanismus auf einem Träger mit gemischten Primern erzeugt kompakte, stabil haftende DNA-Strukturen?  
  — *In einigen Ausführungsformen können die Concatemer template molecules durch Durchführung von Rolling circle amplification Reaktionen auf einem Support erzeugt werden, der eine Mischung aus immobilisierten Capture- und Pinning-Primern umfasst.*  
  reason: The answer correctly identifies rolling-circle amplification on a mixed-primer support, and the query is highly retrievable despite closely mirroring the passage's concepts.
- **Q6 · gpt-5.4-mini** (kept, faith 5.00, quality 4.50, ling 5): Wie werden die Amplifikationsprodukte so verdichtet, dass sie fest auf dem Träger verbleiben?  
  — *concatemer template molecules, die zu compact DNA nanoballs kollabieren und stabil auf einem support immobilisiert sind*  
  reason: The answer directly states the disclosed collapse into compact DNA nanoballs and stable support immobilization, matching the well-framed compaction question.

## WO-2025215167-A1  ·  semantic mode  ·  question language: de

> Q1 und Q2 sind die stärksten semantischen Fragen; mehrere andere Kandidaten ergänzen unbelegte Materialeigenschaften oder Prozessfolgen.

- **Q1 · grok-4.3** (kept, faith 4.67, quality 4.75, ling 5): Wie können Quantensensoren dauerhaft in eine keramische Oxid-Schicht auf Oberflächen eingebracht werden?  
  — *Die Erfindung betrifft eine Beschichtung aus Zirconium(IV)-oxid, welche durch einen Sol-Gel-Prozess aus einer flüssigen Phase mit darin verteilten dotierten Nanodiamanten auf einem Substrat abgeschieden und nach Ihrer Trocknung durch einen Kalzinierungsprozess bei erhöhter Temperatur in einen kristallinen Zustand überfuhrt wird, in dem das Zirconium(IV)-oxid zum überwiegendem Anteil in seiner tetragonalen Phase vorliegt.*  
  reason: Die konzeptionell formulierte und deutlich paraphrasierte Frage wird durch den beschriebenen Sol-Gel- und Kalzinierungsprozess vollständig beantwortet, auch wenn die Antwort etwas mehr Kristallphasendetail als nötig enthält.
- **Q2 · gpt-5.4-mini** (kept, faith 5.00, quality 4.50, ling 5): Wie kann man Quantensensoren direkt in eine ZrO2-Beschichtung auf einem Träger integrieren?  
  — *eine Beschichtung aus Zirconium(IV)-oxid, welche durch einen Sol-Gel-Prozess aus einer flüssigen Phase mit darin verteilten dotierten Nanodiamanten auf einem Substrat abgeschieden*  
  reason: Die knappe, realistische Suchfrage paraphrasiert die direkte Einbettung dotierter Nanodiamanten in ZrO2 präzise und wird vom angegebenen Antwortausschnitt klar gestützt.
- **Q3 · gpt-5-mini** (DISCARDED, faith 5.00, quality 3.25, ling 5): Welches Herstellungsverfahren wird vorgeschlagen, um eine Zirconium(IV)-oxid-Schicht mit eingebrachten dotierten Nanodiamanten auf einem Substrat zu erzeugen?  
  — *Die Erfindung betrifft eine Beschichtung aus Zirconium(IV)-oxid, welche durch einen Sol-Gel-Prozess aus einer flüssigen Phase mit darin verteilten dotierten Nanodiamanten auf einem Substrat abgeschieden und nach Ihrer Trocknung durch einen Kalzinierungsprozess bei erhöhter Temperatur in einen kristallinen Zustand überfuhrt wird.*  
  reason: Frage und Antwort sind sachlich exakt, doch die Frage übernimmt nahezu die gesamte Terminologie des Abstracts und bietet für einen semantischen Benchmark zu wenig Paraphrase.
- **Q4 · qwen3.6-35b-a3b** (DISCARDED, faith 4.33, quality 4.25, ling 5): Wie kann eine robuste Oxidschicht gefertigt werden, die funktionale Nanopartikel gleichmäßig verteilt und anschließend eine definierte Kristallstruktur ausbildet?  
  — *Eine Beschichtung aus Zirconium(IV)-oxid, welche durch einen Sol-Gel-Prozess aus einer flüssigen Phase mit darin verteilten dotierten Nanodiamanten auf einem Substrat abgeschieden und nach Ihrer Trocknung durch einen Kalzinierungsprozess bei erhöhter Temperatur in einen kristallinen Zustand überfuhrt wird, in dem das Zirconium(IV)-oxid zum überwiegendem Anteil in seiner tetragonalen Phase vorliegt.*  
  reason: Die starke konzeptionelle Paraphrase ist flüssig, führt aber die nicht belegten Eigenschaften „robust“ und „gleichmäßig“ ein und lässt die kennzeichnenden Quantensensoren beziehungsweise Nanodiamanten unerwähnt.
- **Q5 · gemini-3.5-flash** (DISCARDED, faith 4.33, quality 4.25, ling 5): Mit welcher Methode lässt sich eine nanostrukturierte Beschichtung auf Zirconiumbasis herstellen, die gleichmäßig verteilte Quantensensoren enthält?  
  — *durch einen Sol-Gel-Prozess aus einer flüssigen Phase mit darin verteilten dotierten Nanodiamanten auf einem Substrat abgeschieden*  
  reason: Der Sol-Gel-Antwortausschnitt ist korrekt, aber die Frage behauptet ohne klare Textgrundlage eine nanostrukturierte Beschichtung und eine gleichmäßige Verteilung der Sensoren.
- **Q6 · sonnet-4.6** (DISCARDED, faith 4.33, quality 4.25, ling 5): Wie lassen sich dotierte Nanodiamanten dauerhaft in eine Oxidkeramikschicht einbetten, ohne ihre Quanteneigenschaften zu verlieren?  
  — *Die Beschichtung aus Zirconium(IV)-oxid wird durch einen Sol-Gel-Prozess aus einer flüssigen Phase mit darin verteilten dotierten Nanodiamanten auf einem Substrat abgeschieden und nach ihrer Trocknung durch einen Kalzinierungsprozess bei erhöhter Temperatur in einen kristallinen Zustand überführt.*  
  reason: Der Herstellungsablauf ist korrekt wiedergegeben, doch weder Passage noch Antwort belegen die entscheidende Behauptung, dass die Quanteneigenschaften der Nanodiamanten erhalten bleiben.
