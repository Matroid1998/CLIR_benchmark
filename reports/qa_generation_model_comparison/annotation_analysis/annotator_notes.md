# Annotator notes — question generation review (2026-08-18 export)

17 of 30 documents carry a free-text note. Q1–Q6 in a note
refer to the randomised slots the annotator saw; the key under each note
resolves them to models (from `model_slot_mapping.json` — private).

## MX-2025009666-A  ·  technical mode  ·  question language: en

> Q3 is the strongest dump-tank question because it includes the reactor-product context while remaining concise and precise. Q1, Q2, and Q4 are also strong and directly supported, although Q1 and Q4 are nearly duplicates. Q5 is usable but slightly less precise because it refers broadly to the dump tank rather than the bottom of the vessel. Q6 is a strong standalone formulation question and is fully supported.

- **Q1 · gpt-5-mini** (kept, faith 5.00, quality 5.00): Where are the one or more gas outlets located on the dump tank vessel?
  — *at a top of the vessel*
- **Q2 · qwen3.6-35b-a3b** (kept, faith 5.00, quality 5.00): Where is the fluid outlet positioned in the dump tank vessel?
  — *at a bottom of the vessel*
- **Q3 · sonnet-4.6** (kept, faith 5.00, quality 5.00): Where is the fluid outlet located on the dump tank vessel used to receive reactor product?
  — *at a bottom of the vessel*
- **Q4 · gemini-3.5-flash** (kept, faith 5.00, quality 5.00): Where are the gas outlets located on the dump tank vessel?
  — *at a top of the vessel*
- **Q5 · gpt-5.4-mini** (kept, faith 5.00, quality 4.50): Where is the fluid outlet located in the dump tank?
  — *at a bottom of the vessel*
- **Q6 · grok-4.3** (kept, faith 5.00, quality 5.00): What solvent is used to form the metallocene solution?
  — *hydrocarbon solvent*

## WO-2023149795-A1  ·  technical mode  ·  question language: en

> Q5 and Q6 are the strongest questions because they are specific and fully supported by the source. Q1-Q4 are also correct, but they are very repetitive and mostly ask the same thing with only small wording changes. Q6 is better than Q1-Q4 because it gives more context about insect larval cultivation.

- **Q1 · gpt-5-mini** (kept, faith 5.00, quality 4.50): Which protein synthesis stimulator is included in the second nutrient medium?
  — *zinc acetate*
- **Q2 · grok-4.3** (kept, faith 5.00, quality 4.50): What protein synthesis stimulator is included in the second nutrient medium?
  — *zinc acetate*
- **Q3 · gpt-5.4-mini** (kept, faith 5.00, quality 4.50): What protein synthesis stimulator is added to the second nutrient medium?
  — *zinc acetate*
- **Q4 · gemini-3.5-flash** (kept, faith 5.00, quality 4.50): What chemical is used as a protein synthesis stimulator in the second nutrient medium?
  — *zinc acetate*
- **Q5 · qwen3.6-35b-a3b** (kept, faith 5.00, quality 5.00): At what temperature are the lyophilized larvae re-ground?
  — *-55°C*
- **Q6 · sonnet-4.6** (kept, faith 5.00, quality 5.00): What protein synthesis stimulator is added to the second nutrient medium for insect larval cultivation?
  — *zinc acetate*

## WO-2025211128-A1  ·  technical mode  ·  question language: en

> Q1 and Q5 are the strongest questions because they are specific, self-contained, and directly supported by the source. Q3 and Q6 are also good but are identical to each other. Q2 and Q4 have the correct answers, but the questions are too vague because they do not identify the silicon member or any material context.

- **Q1 · qwen3.6-35b-a3b** (kept, faith 5.00, quality 5.00): What is the preferred percentage range of Σ9 grain boundaries within the coincidence grain boundary?
  — *from 3% to 20%*
- **Q2 · gpt-5-mini** (DISCARDED, faith 4.67, quality 3.00): What recess depth from the surface is required?
  — *0.5 μm or less*
- **Q3 · gemini-3.5-flash** (kept, faith 5.00, quality 4.50): What is the recess depth from the surface of the silicon member?
  — *0.5 μm or less*
- **Q4 · gpt-5.4-mini** (DISCARDED, faith 5.00, quality 3.25): What is the recess depth from the surface?
  — *0.5 μm or less*
- **Q5 · sonnet-4.6** (kept, faith 5.00, quality 5.00): What is the maximum recess depth from the surface specified for a polycrystalline silicon member?
  — *0.5 μm or less*
- **Q6 · grok-4.3** (kept, faith 5.00, quality 4.50): What is the recess depth from the surface of the silicon member?
  — *0.5 μm or less*

## MX-2025002756-A  ·  technical mode  ·  question language: en

> Q2 is the strongest because it gives the most context and asks for the exact Cu range. Q1 is also clear and specific. Q3 is correct but basically repeats Q1 with slightly weaker wording. Q4 and Q5 are both correct, but “maximum allowable” is a little less precise than saying Pb must be less than 0.1 wt%. Q6 is correct but gives less context than Q2.

- **Q1 · grok-4.3** (kept, faith 5.00, quality 5.00): What is the manganese content range in the lead-free brass alloy?
  — *2.0 to 2.5 wt % Mn*
- **Q2 · gemini-3.5-flash** (kept, faith 5.00, quality 5.00): What is the copper weight percent range in a lead-free brass alloy containing manganese and silicon?
  — *59 to 62 wt %*
- **Q3 · gpt-5.4-mini** (kept, faith 5.00, quality 5.00): What Mn content range is in the lead-free brass alloy?
  — *2.0 to 2.5 wt % Mn*
- **Q4 · qwen3.6-35b-a3b** (kept, faith 4.67, quality 4.50): What is the maximum allowable lead content in the alloy?
  — *less than 0.1 wt %*
- **Q5 · sonnet-4.6** (kept, faith 4.67, quality 5.00): What is the maximum allowable Pb content in lead-free brass alloy?
  — *less than 0.1 wt % Pb*
- **Q6 · gpt-5-mini** (kept, faith 5.00, quality 4.50): What is the weight percent range of Cu in the alloy?
  — *59 to 62 wt % Cu*

## EP-4504821-A1  ·  technical mode  ·  question language: es

> Q1 and Q3 are the strongest because they clearly identify R2 and ask for its exact carbon range. Q4 is also correct but gives less context because it only refers to k1. Q2, Q5, and Q6 are all correct but very repetitive and too dependent on knowing what b refers to. Q5 and Q6 also have weaker language quality because the answers mix Spanish and English or are fully in English.

- **Q1 · sonnet-4.6** (kept, faith 5.00, quality 5.00): ¿Cuántos átomos de carbono puede tener el resto R2 en la fórmula de los organopolysiloxanos preentrecruzados?
  — *3 to 18 carbon atoms*
- **Q2 · grok-4.3** (kept, faith 5.00, quality 3.50): ¿Qué valores puede tomar b?
  — *0 o un entero de 1 a 500*
- **Q3 · gemini-3.5-flash** (kept, faith 5.00, quality 5.00): ¿Cuál es el rango de átomos de carbono permitido para el grupo R 2 bivalente?
  — *3 to 18*
- **Q4 · gpt-5-mini** (kept, faith 5.00, quality 4.00): ¿Qué valores puede tener k1?
  — *k1 is 0, 1, 2 or 3*
- **Q5 · gpt-5.4-mini** (kept, faith 5.00, quality 3.50): ¿Qué valores puede tomar b?
  — *0 o un número entero de 1 to 500*
- **Q6 · qwen3.6-35b-a3b** (kept, faith 5.00, quality 3.50): ¿Cuáles son los valores permitidos para b?
  — *0 or an integer from 1 to 500*

## WO-2025211336-A1  ·  semantic mode  ·  question language: en

> Q2 is the strongest question because it is specific, clearly answerable, and fully supported by the source. Q1 and Q3 are useful semantic questions, although both introduce problem-oriented language such as poor depth-of-cure or deep-section curing that is not explicitly stated. Q5 is the weakest because it asks how the properties are achieved, while its answer only repeats the desired properties. Q4 should also not be kept because it introduces an addition-reaction mechanism and filler terminology that are absent from the source. Q6 is usable but has borderline faithfulness due to stronger paraphrases such as “high temperatures” and “heavy layers.”

- **Q1 · gemini-3.5-flash** (kept, faith 4.33, quality 4.25): What type of material formulation is designed to solve the issue of poor depth-of-cure in thick coatings while maintaining thermal stability and bendability?
  — *photocurable resin composition which has favorable thick film curability and of which the cured product after curing is excellent in flexibility and heat resistance*
- **Q2 · gpt-5-mini** (kept, faith 5.00, quality 4.50): What combination of ingredient types is used to formulate a photocurable resin that yields flexible, heat-resistant cured films?
  — *includes component (A): a polyorganosiloxane having one or more vinyl groups in one molecule, component (B): a compound having one or more mercapto groups in one molecule, component (C): a photoinitiator, and component (D): hollow resin particles.*
- **Q3 · sonnet-4.6** (kept, faith 4.00, quality 4.00): What approach addresses the challenge of achieving deep-section light cure in flexible, heat-stable coatings?
  — *a photocurable resin composition which has favorable thick film curability and of which the cured product after curing is excellent in flexibility and heat resistance*
- **Q4 · grok-4.3** (DISCARDED, faith 3.67, quality 4.00): What components form the basis of a resin that relies on addition reactions between silicon-containing polymers and sulfur-based molecules for light-induced hardening along with filler particles?
  — *includes component (A): a polyorganosiloxane having one or more vinyl groups in one molecule, component (B): a compound having one or more mercapto groups in one molecule, component (C): a photoinitiator, and component (D): hollow resin particles.*
- **Q5 · gpt-5.4-mini** (DISCARDED, faith 3.00, quality 2.75): How can a photocurable resin be made suitable for thick-film curing while still giving a flexible, heat-resistant cured product?
  — *has favorable thick film curability and of which the cured product after curing is excellent in flexibility and heat resistance*
- **Q6 · qwen3.6-35b-a3b** (kept, faith 3.67, quality 4.25): What specific ingredient combination enables UV-sensitive polymers to retain pliability and withstand high temperatures when cured into heavy layers?
  — *component (A): a polyorganosiloxane having one or more vinyl groups in one molecule, component (B): a compound having one or more mercapto groups in one molecule, component (C): a photoinitiator, and component (D): hollow resin particles*

## EP-4584229-A1  ·  technical mode  ·  question language: es

> Q4 is the strongest because it gives the most context and asks exactly what R represents. Q3 is also strong and clearly asks for the carbon range. Q1 and Q2 are correct but more repetitive.

- **Q1 · gpt-5.4-mini** (kept, faith 5.00, quality 4.50): ¿Qué rango de carbonos tiene R en R-NR'H?
  — *1 to 20 carbon atoms*
- **Q2 · gemini-3.5-flash** (kept, faith 5.00, quality 5.00): ¿Cuántos átomos de carbono tiene el grupo hidrocarbonado R en la fórmula R-NR'H?
  — *1 to 20*
- **Q3 · qwen3.6-35b-a3b** (kept, faith 5.00, quality 5.00): ¿Cuál es el rango de átomos de carbono definido para el grupo R en la fórmula R-NR'H?
  — *1 to 20 carbon atoms*
- **Q4 · sonnet-4.6** (kept, faith 5.00, quality 4.75): ¿Qué representa el grupo R en la fórmula R-NR'H de los amino compounds utilizados en composiciones de polvos de dispersión?
  — *a linear or branched and optionally substituted hydrocarbon group with 1 to 20 carbon atoms*
- **Q5 · grok-4.3** (kept, faith 5.00, quality 4.50): ¿Qué representa el resto R en la fórmula R-NR'H?
  — *un linear or branched, optionally substituted hydrocarbon group con 1 to 20 carbon atoms*
- **Q6 · gpt-5-mini** (kept, faith 5.00, quality 4.50): ¿Qué representa R en la fórmula R-NR'H?
  — *a linear or branched and optionally substituted hydrocarbon group with 1 to 20 carbon atoms*

## WO-2025054647-A1  ·  semantic mode  ·  question language: es

> Q2 is the strongest because it is specific and covers both the structure and the exact matrix properties given in the source.

- **Q1 · gpt-5.4-mini** (kept, faith 4.33, quality 4.75): ¿Qué características debe tener la matriz para funcionar bien en un sistema de almacenamiento térmico de este tipo?
  — *la matriz presentando un coeficiente de difusión de gas para el gas de 2,25*10 -9 m 2 /s a 4,25*10 -9 m 2 /s en una plage de temperatura de -30 °C a 300 °C, y una expansión máxima ε en la plage de ley de Hooke de 25 % a 300 %*
- **Q2 · gpt-5-mini** (kept, faith 5.00, quality 4.75): ¿Qué diseño estructural integra el material termochímico y qué propiedades de difusión y deformación especifica la matriz?
  — *el medio de almacenamiento termochímico incorporado en una matriz; la matriz tiene un coeficiente de difusión de gas para el gas de 2.25*10 -9 m 2 /s a 4.25*10 -9 m 2 /s en un intervalo de temperatura de -30°C a 300°C, y una expansión máxima ε en el rango de la ley de Hooke de 25% a 300%; el medio de almacenamiento termochímico está distribuido sustancialmente de forma homogénea en la matriz.*
- **Q3 · grok-4.3** (kept, faith 4.33, quality 4.75): ¿Qué propiedades de transporte de gas y de estabilidad mecánica debe poseer la estructura soporte para que un material termquímico funcione correctamente en un amplio margen de temperaturas?
  — *la matriz tiene un coeficiente de difusión de gas para el gas de 2,25*10-9 m2/s a 4,25*10-9 m2/s en un rango de temperatura de -30°C a 300°C, y una expansión máxima ε en el rango de la ley de Hooke de 25% a 300%*
- **Q4 · sonnet-4.6** (kept, faith 4.33, quality 4.75): ¿Qué propiedades mecánicas y de transporte debe reunir una matriz que aloje un medio de almacenamiento termoquímico para funcionar de forma estable en un amplio rango térmico?
  — *die Matrix einen Gasdiffusionskoeffizient für das Gas von 2,25*10-9 m2/s bis 4,25*10-9 m2/s in einem Temperaturbereich von -30°C bis 300°C, und eine maximale Dehnung ε im Hooke'schen Bereich von 25% bis 300% aufweist*
- **Q5 · gemini-3.5-flash** (DISCARDED, faith 3.33, quality 4.00): ¿Cómo se resuelven las tensiones mecánicas por dilatación y se asegura la permeabilidad al gas en acumuladores térmicos que operan en condiciones térmicas extremas?
  — *la matriz presenta un coeficiente de difusión de gas para el gas de 2.25*10 -9 m 2 /s a 4.25*10 -9 m 2 /s en un rango de temperatura de -30°C a 300°C, y una expansión máxima ε en el rango de la ley de Hooke de 25% a 300%*
- **Q6 · qwen3.6-35b-a3b** (kept, faith 4.33, quality 4.25): ¿Qué parámetros de permeabilidad y dilatación estructural debe cumplir el material soporte para garantizar un funcionamiento estable en acumuladores de calor químico?
  — *la matriz tiene un coeficiente de difusión de gas para el gas de 2.25*10 -9 m 2 /s to 4.25*10 -9 m 2 /s en un rango de temperatura de -30°C to 300°C, y una expansión máxima ε en el rango de la ley de Hooke de 25% to 300%*

## EP-4630021-A1  ·  technical mode  ·  question language: de

> Q3, Q4, and Q6 are the strongest because they are specific and directly supported by the source. Q1 is also correct but slightly broader in how it describes the placental-derived materials as starting materials.

- **Q1 · gemini-3.5-flash** (kept, faith 4.67, quality 4.50): Aus welchen Ausgangsstoffen werden pferdespezifische therapeutische Zusammensetzungen hergestellt?
  — *aus der Plazenta gewonnenen Materialien*
- **Q2 · grok-4.3** (kept, faith 4.33, quality 5.00): Welche Eigenschaften besitzt das produzierte Amnion- und Fruchtwasser-Injektionsprodukt?
  — *clear, safe, and physiologically and biologically active liquid injectable*
- **Q3 · gpt-5-mini** (kept, faith 5.00, quality 5.00): Welche Materialien enthalten die equinen therapeutischen Zusammensetzungen?
  — *Plazenta-abgeleitete Materialien*
- **Q4 · sonnet-4.6** (kept, faith 5.00, quality 4.75): Was wird bei der Verarbeitung von eingehendem plazentaren Gewebe und Fluid mit Verfärbungen und Verunreinigungen als Endprodukt erzeugt?
  — *a clear amnion and amniotic fluid injectable product*
- **Q5 · gpt-5.4-mini** (kept, faith 5.00, quality 4.50): Welche Eigenschaften hat das flüssige Injektionsprodukt?
  — *clear, safe, and physiologically and biologically active*
- **Q6 · qwen3.6-35b-a3b** (kept, faith 5.00, quality 5.00): Welche Komponenten bleiben nach der Aufbereitung des Injektionsprodukts erhalten?
  — *postbiotics, proteins, exosomes, biocomponents*

## EP-4627881-A1  ·  semantic mode  ·  question language: zh

> Q3 is the strongest question because it directly and accurately asks how the plasma generation unit is constructed.

- **Q1 · qwen3.6-35b-a3b** (DISCARDED, faith 3.00, quality 3.50): 面对连续化生产要求，如何将独立的小型发生器集成到完整产线中？
  — *包含多个上述发生装置的等离子体发生单元*
- **Q2 · gemini-3.5-flash** (DISCARDED, faith 2.67, quality 3.50): 当单一喷嘴所提供的电离气体束能效不足时，可以采用什么方案将多套发生装置集结协同运作？
  — *Plasmaerzeugungseinrichtung (100) 包含多个 Vorrichtungen (10, 10a, 10b)*
- **Q3 · gpt-5.4-mini** (kept, faith 5.00, quality 4.50): 如果要把多个等离子火焰发生装置组合起来，相关的等离子生成单元是怎样构成的？
  — *eine Plasmaerzeugungseinrichtung (100) umfassend mehrere Vorrichtungen (10, 10a, 10b)*
- **Q4 · sonnet-4.6** (kept, faith 4.33, quality 4.75): 有没有一种统一的控制方法，可以同时适用于单台等离子体发生器和整套高温熔融系统？
  — *一种用于操作此类设备（10, 10a, 10b）、此类等离子体发生装置（100）或此类高温工艺设备（尤其是熔融装置（26））的方法*
- **Q5 · gpt-5-mini** (kept, faith 4.00, quality 4.00): 有哪些专用硬件可以直接生成工业用等离子体火焰？
  — *用于生成至少一种等离子体火焰(12)的装置(10, 10a, 10b)。*
- **Q6 · grok-4.3** (DISCARDED, faith 3.67, quality 4.25): 工业熔化设备中实现多等离子体火焰供应的系统如何构建？
  — *a plasma generation unit (100) comprising a plurality of devices (10, 10a, 10b)*

## MX-2025007206-A  ·  technical mode  ·  question language: de

> Q2, Q3, and Q5 are the strongest because they clearly identify the rAAV formulations and correctly preserve the “above −80 °C” condition. Q1 is also correct but gives less context. Q4 is weak because the answer gives −80 °C without saying “above,” which changes the numerical condition. Q6 is also problematic because it asks for a minimum temperature even though the source only gives a strict threshold above −80 °C.

- **Q1 · gpt-5-mini** (kept, faith 5.00, quality 4.00): Welche Lagertemperatur wird für langfristige Aufbewahrung genannt?
  — *temperatures above -80 °C*
- **Q2 · qwen3.6-35b-a3b** (kept, faith 5.00, quality 5.00): Ab welcher Temperatur ist eine langfristige Lagerung der rAAV-Formulierungen möglich?
  — *above -80°C*
- **Q3 · gpt-5.4-mini** (kept, faith 5.00, quality 5.00): Bei welcher Temperatur können die rAAV-Formulierungen längerfristig gelagert werden?
  — *bei Temperaturen über -80 °C*
- **Q4 · gemini-3.5-flash** (DISCARDED, faith 2.67, quality 5.00): Über welcher Lagertemperatur ermöglichen die rAAV-Formulierungen eine langfristige Haltbarkeit?
  — *-80°C*
- **Q5 · grok-4.3** (kept, faith 5.00, quality 5.00): Oberhalb welcher Temperatur ermöglichen rAAV-Formulierungen langfristige Lagerung?
  — *oberhalb von -80 °C*
- **Q6 · sonnet-4.6** (DISCARDED, faith 3.67, quality 4.75): Bei welcher Mindesttemperatur kann eine rAAV-Formulierung für die Langzeitlagerung im Regal gelagert werden?
  — *oberhalb von -80°C*

## MX-2025010190-A  ·  technical mode  ·  question language: en

> Q5 is the strongest question because it asks for more specific information and is directly supported by the source.

- **Q1 · gemini-3.5-flash** (kept, faith 5.00, quality 5.00): What encodes the recombinant polypeptides with a nutritionally complete amino acid profile?
  — *polynucleotides*
- **Q2 · sonnet-4.6** (kept, faith 5.00, quality 5.00): What type of amino acid profile does the recombinant polypeptide in the nutritional composition provide?
  — *a nutritionally complete amino acid profile*
- **Q3 · qwen3.6-35b-a3b** (kept, faith 5.00, quality 5.00): What type of amino acid profile characterizes the recombinant polypeptide in the nutritional composition?
  — *nutritionally complete amino acid profile*
- **Q4 · gpt-5.4-mini** (kept, faith 5.00, quality 4.00): What do the polynucleotides encode?
  — *the recombinant polypeptides*
- **Q5 · grok-4.3** (kept, faith 5.00, quality 5.00): What forms of polypeptide are suitable to provide a nutritionally complete amino acid profile when provided in a nutritional composition?
  — *a recombinant polypeptide and variants and truncates thereof*
- **Q6 · gpt-5-mini** (kept, faith 5.00, quality 4.50): What amino acid profile does the recombinant polypeptide have?
  — *a nutritionally complete amino acid profile*

## WO-2025207810-A1  ·  technical mode  ·  question language: zh

> Q5 and Q6 are the strongest because they are clear, specific, and directly supported by the source. Q1 and Q2 are also correct but are repetitive. Q3 is scientifically correct but has weaker language quality because it mixes Chinese and English.

- **Q1 · gpt-5.4-mini** (kept, faith 5.00, quality 4.50): 错误校验 barcode nucleotide sequences 基于什么编码？
  — *Hamming codes*
- **Q2 · grok-4.3** (kept, faith 5.00, quality 4.50): 错误检查条形码核苷酸序列基于什么？
  — *Hamming codes*
- **Q3 · sonnet-4.6** (kept, faith 5.00, quality 5.00): engineered hairpin structure在寡核苷酸中起什么作用？
  — *mitigates hybridizing of the oligonucleotide to undesirable nucleic acid sequences*
- **Q4 · gemini-3.5-flash** (kept, faith 4.33, quality 5.00): 纠错条形码核苷酸序列是基于什么进行设计的？
  — *Hamming codes*
- **Q5 · gpt-5-mini** (kept, faith 5.00, quality 5.00): 哪种结构可减弱寡核苷酸与不良核酸序列的杂交？
  — *工程化的发夹结构*
- **Q6 · qwen3.6-35b-a3b** (kept, faith 5.00, quality 5.00): 错误检查条形码核苷酸序列基于什么编码？
  — *汉明码*

## EP-4577789-A1  ·  technical mode  ·  question language: zh

> Q4 and Q6 are the strongest questions because they clearly ask about both ends of the cooling gas pathway. Q3 and Q5 are also specific and easy to answer from the source. Q1 and Q2 are correct but slightly more repetitive because they ask about the same cooling gas duct and route in different wording.

- **Q1 · gpt-5-mini** (kept, faith 5.00, quality 4.50): 冷却气体由哪个管道引导至预热区？
  — *冷却气体管道 (44)*
- **Q2 · grok-4.3** (kept, faith 5.00, quality 4.50): 冷却气体如何从冷却区引导至预热区？
  — *经由冷气管道 (44) 被引导至预热区 (21)*
- **Q3 · gemini-3.5-flash** (kept, faith 5.00, quality 5.00): 冷却气体经由管道被引导至并流蓄热式竖窑的哪个区域？
  — *预热区 (21)*
- **Q4 · gpt-5.4-mini** (kept, faith 5.00, quality 5.00): 冷却气体管道把冷却气体从哪里引导到哪里？
  — *从冷却区 (22) 引导至预热区 (21)*
- **Q5 · sonnet-4.6** (kept, faith 5.00, quality 5.00): PFR竖窑中废气通过哪个出口排出？
  — *废气经由排气出口 (6) 从其中一个竖井 (2) 排出*
- **Q6 · qwen3.6-35b-a3b** (kept, faith 5.00, quality 5.00): 冷却气体管道连接竖窑内的哪两个区域？
  — *从冷却区 (22) 引导至预热区 (21)*

## WO-2025212655-A1  ·  semantic mode  ·  question language: de

> Q4, Q5, and Q6 are the strongest because they are specific and directly supported by the source.

- **Q1 · qwen3.6-35b-a3b** (kept, faith 4.00, quality 4.50): Welche Strategie nutzt man, um DNA-Fragmente direkt auf einem festen Träger zu replizieren und dabei eine hohe lokale Dichte zu erreichen?
  — *Die concatemer template molecules können durch die Durchführung von rolling circle amplification Reaktionen auf einem Träger erzeugt werden, der ein Gemisch aus immobilisierten capture und pinning primers umfasst.*
- **Q2 · grok-4.3** (kept, faith 4.67, quality 5.00): Welcher Amplifikationsmechanismus auf einem Träger mit gemischten Primern erzeugt kompakte, stabil haftende DNA-Strukturen?
  — *In einigen Ausführungsformen können die Concatemer template molecules durch Durchführung von Rolling circle amplification Reaktionen auf einem Support erzeugt werden, der eine Mischung aus immobilisierten Capture- und Pinning-Primern umfasst.*
- **Q3 · gemini-3.5-flash** (DISCARDED, faith 3.33, quality 4.00): Wie wird verhindert, dass die langen synthetisierten DNA-Stränge frei in Lösung driften oder unkontrolliert viel Platz auf dem Substrat einnehmen?
  — *Die Concatemer-Templatmoleküle kollabieren zur Bildung kompakter DNA-Nanoballs, die stabil auf einem Träger immobilisiert sind.*
- **Q4 · sonnet-4.6** (kept, faith 5.00, quality 5.00): Wie lassen sich DNA-Vorlagen für hochdurchsatzfähige Sequenzierläufe stabil auf einer festen Oberfläche verankern?
  — *Die concatemer template molecules können durch die Durchführung von rolling circle amplification Reaktionen auf einem Support generiert werden, der eine Mischung aus immobilisierten capture und pinning primers enthält. Die entstehenden Moleküle kollabieren zu kompakten DNA nanoballs, die stabil auf dem Support immobilisiert sind.*
- **Q5 · gpt-5-mini** (kept, faith 5.00, quality 4.75): Welcher Ansatz wird vorgeschlagen, um zahlreiche Vorlagen direkt auf einem festen Träger zu erzeugen?
  — *In einigen Ausführungsformen können die concatemer template molecules erzeugt werden, indem rolling circle amplification-Reaktionen auf einem Support durchgeführt werden, der eine Mischung aus immobilisierten capture und pinning primers enthält.*
- **Q6 · gpt-5.4-mini** (kept, faith 5.00, quality 5.00): Wie werden die Amplifikationsprodukte so verdichtet, dass sie fest auf dem Träger verbleiben?
  — *concatemer template molecules, die zu compact DNA nanoballs kollabieren und stabil auf einem support immobilisiert sind*

## MX-2025006624-A  ·  semantic mode  ·  question language: fr

> Q2 and Q4 are the strongest questions because they are specific and directly supported by the formulation and synthesis details.

- **Q1 · grok-4.3** (DISCARDED, faith 3.33, quality 4.25): Existe-t-il des revêtements polymérisables par actinique qui incorporent des matériaux d'origine biologique tout en maintenant des propriétés de mise en œuvre industrielles ?
  — *composition de revêtement curable par radiation actinique qui comprend de 10 % en poids à 90 % en poids d'un composé A et entre 10 % en poids et 89.99 % en poids d'un composé B*
- **Q2 · gpt-5-mini** (kept, faith 5.00, quality 4.75): Comment la formulation intègre-t-elle un monomère d'origine biobasée dans un revêtement curable par rayonnement actinique ?
  — *La composition comprend de 10 wt% à 90 wt%, basé sur le poids total de la composition, d'un poly(trimethylene ether) (meth)acrylate compound A ayant au plus deux groupes (meth)acrylate, obtenable par une réaction de condensation de biobased 1,3 poly(trimethylene ether) glycol et d'un composé de (meth)acrylate sélectionné dans le groupe constitué par (meth)acrylic acid, (meth)acryloyl chloride et/ou leurs alkylesters; wherein the biobased 1,3 poly(trimethylene ether) glycol has a number average molecular weight Mn of from 350 to 600 g/mol, more preferably from 400 to 550 g/mol.*
- **Q3 · gpt-5.4-mini** (kept, faith 4.67, quality 5.00): Comment rendre un revêtement durcissable par radiation actinique tout en utilisant un monomère issu d’un glycol biobasé ?
  — *une composition de revêtement durcissable par radiation actinique comprenant de 10 wt% à 90 wt% d’un composé A de poly(trimethylene ether) (meth)acrylate*
- **Q4 · gemini-3.5-flash** (kept, faith 5.00, quality 4.75): Quels réactifs sont mis en œuvre pour synthétiser le monomère à base de polyéther-acrylate d'origine naturelle utilisé dans la formulation ?
  — *une réaction de condensation de biobased 1,3 poly(trimethylene ether) glycol et un (meth)acrylate compound choisi dans le groupe constitué par (meth)acrylic acid, (meth)acryloyl chloride, et /ou alkylesters de ceux-ci*
- **Q5 · sonnet-4.6** (DISCARDED, faith 3.33, quality 4.00): Comment intégrer des matières premières renouvelables dans une formulation de revêtement durcissable par rayonnement sans sacrifier la réactivité ?
  — *un composé de (met)acrilato de poly(triméthylène éther) A ayant au plus deux groupes (meth)acrylate, obtenu par réaction de condensation de 1,3 poly(trimethylene ether) glycol d'origine biologique et un composé (meth)acrylate choisi dans le groupe constitué de l'acide (meth)acrylique, du chlorure de (meth)acryloyle et/ou de leurs alkylesters*
- **Q6 · qwen3.6-35b-a3b** (DISCARDED, faith 3.33, quality 4.00): Quelle stratégie formulation permet d'intégrer des précurseurs renouvelables dans des systèmes de revêtements durcis par rayonnement tout en contrôlant la rhéologie ?
  — *a poly(trimethylene ether) (meth)acrylate compound A having at most two (meth)acrylate groups obtainable by a condensation reaction of biobased 1,3 poly(trimethylene ether) glycol and a (meth)acrylate compound selected from the group consisting of (meth)acrylic acid, (meth)acryloyl chloride, and /or alkylesters thereof*

## WO-2025187661-A8  ·  semantic mode  ·  question language: es

> Q2 is the clearest question because it directly asks what defect is being prevented. Q6 is also strong because the answer actually gives the composition used to reduce burr formation, although the question is broader than the source. Q3, Q4, and Q5 are usable but mostly restate that burrs can be prevented instead of clearly explaining how. Q1 is the weakest because it adds exudation, which is not mentioned in the source, and the answer does not actually give the proposed approach.

- **Q1 · qwen3.6-35b-a3b** (DISCARDED, faith 3.33, quality 3.75): ¿Qué enfoque se propone para prevenir la aparición de rebabas o exudaciones al reprocesar polímeros de cadena aromática con enlaces de azufre?
  — *can be inhibited from forming burrs*
- **Q2 · gpt-5-mini** (kept, faith 5.00, quality 4.75): ¿Qué defecto durante el reprocesado en planta pretende evitar esta composición de resina?
  — *puede ser inhibida de formar rebabas durante el reciclaje.*
- **Q3 · gemini-3.5-flash** (kept, faith 4.00, quality 4.50): ¿Cómo se puede resolver el reto de la aparición de imperfecciones físicas o rebabas en polímeros de ingeniería cuando se someten a procesos de recuperación y reprocesamiento?
  — *una composición de resina de poly(arylene sulfide) que, durante el reciclaje, puede evitar la formación de rebabas*
- **Q4 · grok-4.3** (kept, faith 4.33, quality 4.25): ¿Cómo se puede evitar la formación de rebabas durante el reciclaje de resinas de poly(arylene sulfide)?
  — *una composición de resina de poly(arylene sulfide) que, durante el reciclaje, puede ser inhibida de formar rebabas*
- **Q5 · gpt-5.4-mini** (kept, faith 4.33, quality 4.25): ¿Cómo se puede evitar que una resina de poly(arylene sulfide) reciclada genere rebabas?
  — *que, durante el reciclaje, puede ser impedida de formar burrs*
- **Q6 · sonnet-4.6** (kept, faith 4.33, quality 4.75): ¿Cómo se puede evitar la formación de rebabas durante el reciclado de resinas termoplásticas de alto rendimiento?
  — *La composición de resina de poly(arylene sulfide) (X) para materiales de reciclaje comprende (A) 100 partes en masa de una resina de poly(arylene sulfide) lineal con grupo carboxy y (B) 0,3-10 partes en masa de un compuesto alkoxysilane.*

---

Documents without a note (13): WO-2025210445-A1, MX-2025009131-A, WO-2022005333-A1, MX-2025005046-A, EP-4627127-A1, EP-4633645-A1, MX-2025007510-A, WO-2025202347-A1, EP-4633791-A1, EP-4634436-A1, WO-2025215167-A1, MX-2025004470-A, WO-2025177605-A1
