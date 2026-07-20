"""
Code-switched document variants: swap one chemistry term, see what survives.

From a patent document that mentions a ChEBI concept, build perturbed copies in
which exactly one chemistry term is replaced:

  A  baseline        -- the untouched anchor document
  B  in-set swap     -- the concept's name in another language the patent IS in
  C  out-of-set swap -- the concept's name in a working language the patent is NOT in
  D  spelling noise  -- same language, perturbed surface (Greek/oxidation/hyphen/typo/case)
  E  non-chemistry   -- an ordinary noun swapped to another language (the only LLM variant)
  F  ontology form   -- another form from the concept's ``chebi`` name bucket (e.g. CO(2))

Replacement forms come from the alias graph's ``name_set``. Every change is
tracked (original term, replacement, languages, variant) so the QA step can ask
about the ORIGINAL term while the gold document contains the replacement --
which is the whole experiment. All occurrences of the chosen term are replaced
across the document's text fields.

B/C/D/F are deterministic given the seed; only E calls a model.

The swap primitives here are also the progressive ladder's primitives
(``progressive.py`` imports them): the two builders must perturb text
identically or their results are not comparable.
"""

from __future__ import annotations

import argparse
import json
import random
import re
from collections import defaultdict
from pathlib import Path
from typing import Any, Mapping, Optional, Sequence

from clir_bench.core import corpus as corpus_io
from clir_bench.core.context import AppContext
from clir_bench.core.domain import CorpusSchema

# Columns a swap rewrites. Order is irrelevant; membership is not -- a term left
# unreplaced in one field would leak the original surface into the gold document.
TEXT_FIELDS: tuple[str, ...] = ("title", "abstract", "description", "first_claim", "context")

TRACKING_FIELDS: tuple[str, ...] = (
    "variant",
    "concept_chebi_id",
    "concept_name",
    "original_term",
    "replacement_term",
    "anchor_language",
    "target_language",
    "source_id",
    "source_publication_number",
)

VARIANTS: tuple[str, ...] = ("A", "B", "C", "D", "E", "F")

# Variant documents are identified by suffixing their source document id. The
# double underscore is this subsystem's separator (``<doc>__B``, ``<doc>__r3``,
# ``<doc>__q_de``) and is published, so it is fixed.
VARIANT_ID_SEPARATOR = "__"

CORPUS_FILENAME = "code_switched_corpus.csv"
QAC_FILENAME = "code_switched_qac.csv"
ALIAS_GRAPH_FILENAME = "alias_graph.json"

# Same script ranges the alias-graph name matcher uses. Duplicated rather than
# imported because the two apply it to different things: the matcher tests
# normalized token strings, this module tests raw surfaces before any
# normalization, and the two must be free to diverge without breaking each other.
_CJK_RE = re.compile(r"[぀-ヿ㐀-鿿가-힯豈-﫿]")

_QUALIFIER_RE = re.compile(r"\s*\([^)]*\)\s*$")


def output_fieldnames(schema: CorpusSchema) -> tuple[str, ...]:
    return tuple(schema.fields) + TRACKING_FIELDS


def alias_graph_path(context: AppContext) -> Path:
    return context.workspace.data("alias_graph") / ALIAS_GRAPH_FILENAME


def load_concepts(path: Path) -> list[dict[str, Any]]:
    """The alias graph's concept list (ChEBI id, names, gold publications)."""
    with Path(path).open(encoding="utf-8") as fh:
        return json.load(fh)["concepts"]


# --------------------------------------------------------------------------- #
# Locating and replacing a term in raw text
# --------------------------------------------------------------------------- #

def term_regex(term: str) -> re.Pattern:
    """Match a term as a standalone token.

    CJK writes without word separators, so a CJK term matches as a plain
    substring; Latin terms need non-word-character boundaries (case-insensitive)
    so that "acid" does not match inside "acidic".
    """
    if _CJK_RE.search(term):
        return re.compile(re.escape(term))
    return re.compile(r"(?<!\w)" + re.escape(term) + r"(?!\w)", re.IGNORECASE)


def doc_text(row: Mapping[str, str]) -> str:
    """Every text field of a document, concatenated, for term search."""
    return "\n".join(row.get(field) or "" for field in TEXT_FIELDS)


def clean_name(name: str) -> str:
    """Drop a trailing disambiguation qualifier: 'Silane (composé)' -> 'Silane'."""
    return _QUALIFIER_RE.sub("", name).strip() or name


def is_clean_swap(original: str, replacement: str) -> bool:
    """True when the replacement genuinely removes the original surface.

    'sulfate' -> 'Sulfate ion' is not a swap: the original term is still there,
    so a retriever could still match on it and the perturbation measures nothing.
    """
    if not replacement or replacement.casefold() == original.casefold():
        return False
    return not term_regex(original).search(replacement)


def clean_lang_swap(
    name_set: Mapping[str, Any],
    original: str,
    languages: Sequence[str],
    rng: random.Random,
) -> Optional[tuple[str, str]]:
    """Pick a ``(target_language, replacement)`` among ``languages``, or None."""
    options = list(languages)
    rng.shuffle(options)
    for language in options:
        for name in name_set.get(language, []):
            candidate = clean_name(name)
            if is_clean_swap(original, candidate):
                return language, candidate
    return None


def replace_all(
    row: Mapping[str, str], term: str, replacement: str
) -> Optional[dict[str, str]]:
    """A copy of ``row`` with every occurrence of ``term`` replaced.

    None when the term occurs nowhere, which is the signal that this document
    cannot carry this perturbation.
    """
    pattern = term_regex(term)
    new = dict(row)
    total = 0
    for field in TEXT_FIELDS:
        value = row.get(field) or ""
        if not value:
            continue
        replaced, count = pattern.subn(replacement, value)
        if count:
            new[field] = replaced
            total += count
    return new if total else None


def is_distinctive(name: str) -> bool:
    """Distinctive enough to be a chemistry term rather than a common word.

    ChEBI lists brand names as synonyms; some of them ("Action") are ordinary
    words that would anchor on unrelated text. A digit, hyphen, space or decent
    length is what separates "fluthiacet-methyl" and "CO2" from those.
    """
    return len(name) >= 8 or any(c.isdigit() for c in name) or "-" in name or " " in name


def locate_anchor(
    name_set: Mapping[str, Any],
    rows_by_language: Mapping[str, Mapping[str, str]],
    rng: random.Random,
) -> Optional[tuple[str, str]]:
    """Pick a random ``(anchor_language, original_term)`` that actually occurs.

    Prefers the per-language Wikipedia name (a real natural-language term); falls
    back to an ontology form -- the canonical name plus distinctive synonyms --
    which can appear in a document of any language (e.g. "CO2"), so concepts
    detected through a ChEBI synonym can still anchor.
    """
    natural: list[tuple[str, str]] = []
    fallback: list[tuple[str, str]] = []
    chebi = list(name_set.get("chebi", []))
    chebi_fallback = (chebi[:1] if chebi else []) + [n for n in chebi[1:] if is_distinctive(n)]

    for language, row in rows_by_language.items():
        text = doc_text(row)
        hit = next(
            (name for name in name_set.get(language, []) if term_regex(name).search(text)), None
        )
        if hit is not None:
            natural.append((language, hit))
            continue
        hit = next((name for name in chebi_fallback if term_regex(name).search(text)), None)
        if hit is not None:
            fallback.append((language, hit))

    pool = natural or fallback
    return rng.choice(pool) if pool else None


# --------------------------------------------------------------------------- #
# Variant D -- spelling perturbations
# --------------------------------------------------------------------------- #
# Two of the five rules are chemistry-specific notation swaps (Greek locants,
# oxidation-state numerals); the other three are generic surface noise. Together
# they cover how a chemistry term is actually mis-written in the wild.

_GREEK_TO_NAME = {
    "α": "alpha", "β": "beta", "γ": "gamma", "δ": "delta", "ε": "epsilon",
    "ζ": "zeta", "η": "eta", "θ": "theta", "κ": "kappa", "λ": "lambda",
    "μ": "mu", "π": "pi", "ρ": "rho", "σ": "sigma", "τ": "tau", "φ": "phi",
    "χ": "chi", "ψ": "psi", "ω": "omega",
}
_NAME_TO_GREEK = {name: letter for letter, name in _GREEK_TO_NAME.items()}

_ROMAN_TO_CHARGE = {
    "(0)": "(0)", "(I)": "(1+)", "(II)": "(2+)", "(III)": "(3+)", "(IV)": "(4+)",
    "(V)": "(5+)", "(VI)": "(6+)", "(VII)": "(7+)",
}
# "(0)" maps to itself, so it is not a usable reverse rule.
_CHARGE_TO_ROMAN = {
    charge: roman for roman, charge in _ROMAN_TO_CHARGE.items() if roman != "(0)"
}


def _greek_swap(term: str, rng: random.Random) -> Optional[str]:
    for char in term:
        if char in _GREEK_TO_NAME:
            return term.replace(char, _GREEK_TO_NAME[char], 1)
    # Longest first, so "epsilon" is not shadowed by a shorter name inside it.
    for name in sorted(_NAME_TO_GREEK, key=len, reverse=True):
        match = re.search(name, term, re.IGNORECASE)
        if match:
            return term[: match.start()] + _NAME_TO_GREEK[name] + term[match.end():]
    return None


def _oxidation_swap(term: str, rng: random.Random) -> Optional[str]:
    for roman, charge in _ROMAN_TO_CHARGE.items():
        if roman in term and roman != charge:
            return term.replace(roman, charge, 1)
    for charge, roman in _CHARGE_TO_ROMAN.items():
        if charge in term:
            return term.replace(charge, roman, 1)
    return None


def _hyphen_insert(term: str, rng: random.Random) -> Optional[str]:
    spots = [i for i in range(1, len(term)) if term[i - 1].isalpha() and term[i].isalpha()]
    if not spots:
        return None
    index = rng.choice(spots)
    return term[:index] + "-" + term[index:]


def _typo(term: str, rng: random.Random) -> Optional[str]:
    letters = [i for i, c in enumerate(term) if c.isalpha()]
    if len(letters) < 2:
        return None
    kind = rng.choice(["swap", "drop", "dup"])
    if kind == "swap":
        adjacent = [i for i in letters if (i + 1) in letters]
        if not adjacent:
            return None
        index = rng.choice(adjacent)
        return term[:index] + term[index + 1] + term[index] + term[index + 2:]
    index = rng.choice(letters)
    if kind == "drop":
        return term[:index] + term[index + 1:]
    return term[:index] + term[index] + term[index:]


def _case_noise(term: str, rng: random.Random) -> Optional[str]:
    letters = [i for i, c in enumerate(term) if c.isalpha()]
    if not letters:
        return None
    count = max(1, len(letters) // 3)
    flip = set(rng.sample(letters, min(count, len(letters))))
    out = "".join(
        (c.upper() if c.islower() else c.lower()) if i in flip else c
        for i, c in enumerate(term)
    )
    return out if out != term else None


def perturb(term: str, rng: random.Random) -> Optional[str]:
    """Apply one applicable spelling perturbation, or None if none applies."""
    rules = [_greek_swap, _oxidation_swap, _hyphen_insert, _typo, _case_noise]
    rng.shuffle(rules)
    for rule in rules:
        out = rule(term, rng)
        if out and out != term:
            return out
    return None


# --------------------------------------------------------------------------- #
# Variant F -- ontology form
# --------------------------------------------------------------------------- #

def pick_ontology_variant(
    chebi_names: Sequence[str], original: str, rng: random.Random
) -> Optional[str]:
    """Another ontology surface form for the same concept.

    Formula-like forms (CO(2)) are preferred so the swap is visibly a different
    style of naming rather than a near-synonym; the clean-swap filter rejects
    forms that still contain the original ('chloride' -> 'Chloride(1-)').
    """
    pool = [name for name in chebi_names if is_clean_swap(original, name)]
    if not pool:
        return None
    formulas = [name for name in pool if any(c.isdigit() for c in name)]
    return rng.choice(formulas or pool)


# --------------------------------------------------------------------------- #
# Build
# --------------------------------------------------------------------------- #

def _variant_row(
    row: Mapping[str, str],
    variant: str,
    *,
    schema: CorpusSchema,
    concept_id: str,
    concept_name: str,
    original_term: str,
    replacement_term: str,
    anchor_language: str,
    target_language: str,
    source_id: str,
    family: str,
) -> dict[str, str]:
    out = {key: row.get(key, "") for key in schema.fields}
    out[schema.id_field] = f"{source_id}{VARIANT_ID_SEPARATOR}{variant}"
    out.update(
        {
            "variant": variant,
            "concept_chebi_id": concept_id,
            "concept_name": concept_name,
            "original_term": original_term,
            "replacement_term": replacement_term,
            "anchor_language": anchor_language,
            "target_language": target_language,
            "source_id": source_id,
            "source_publication_number": family,
        }
    )
    return out


def build_code_switched(context: AppContext, args: argparse.Namespace) -> int:
    """Build the A-F variant corpus. Returns the number of rows written."""
    schema = context.schema
    wanted = {v.strip().upper() for v in str(args.variants).split(",") if v.strip()}
    unknown = wanted - set(VARIANTS)
    if unknown:
        raise ValueError(f"unknown variant(s): {sorted(unknown)}; known: {list(VARIANTS)}")

    concepts = load_concepts(alias_graph_path(context))
    if args.limit is not None:
        concepts = concepts[: args.limit]

    corpus_path = context.workspace.corpus_csv(args.source)
    by_family: dict[str, dict[str, dict[str, str]]] = defaultdict(dict)
    for row in corpus_io.read_rows(corpus_path):
        by_family[schema.family_of(row)][schema.language_of(row)] = row

    working = list(context.languages.working)
    rng = random.Random(args.seed)

    swapper = None
    if "E" in wanted:
        from clir_bench.domains.chem_patents.codeswitch.llm_swap import nonchem_swapper

        swapper = nonchem_swapper(context, model=args.model)

    out_rows: list[dict[str, str]] = []
    counts: dict[str, int] = defaultdict(int)

    from tqdm import tqdm

    for entry in tqdm(concepts, desc="Code-switch", unit="concept"):
        concept_id, concept_name = entry["chebi_id"], entry["name"]
        name_set = entry["name_set"]
        gold = [family for family in entry["gold"] if family in by_family]
        if not gold:
            continue
        family = rng.choice(gold)
        family_rows = by_family[family]
        present = set(family_rows)

        anchor = locate_anchor(name_set, family_rows, rng)
        if anchor is None:
            continue
        anchor_language, original = anchor
        anchor_row = family_rows[anchor_language]
        source_id = schema.id_of(anchor_row)

        def emit(
            variant: str,
            new_row: Optional[Mapping[str, str]],
            replacement: str,
            target_language: str,
            *,
            term: str = original,
        ) -> None:
            if new_row is None:
                return
            out_rows.append(
                _variant_row(
                    new_row,
                    variant,
                    schema=schema,
                    concept_id=concept_id,
                    concept_name=concept_name,
                    original_term=term,
                    replacement_term=replacement,
                    anchor_language=anchor_language,
                    target_language=target_language,
                    source_id=source_id,
                    family=family,
                )
            )
            counts[variant] += 1

        if "A" in wanted:
            emit("A", anchor_row, "", "")
        if "B" in wanted:
            swap = clean_lang_swap(
                name_set, original, [l for l in present if l != anchor_language], rng
            )
            if swap:
                target, replacement = swap
                emit("B", replace_all(anchor_row, original, replacement), replacement, target)
        if "C" in wanted:
            swap = clean_lang_swap(
                name_set, original, [l for l in working if l not in present], rng
            )
            if swap:
                target, replacement = swap
                emit("C", replace_all(anchor_row, original, replacement), replacement, target)
        if "D" in wanted:
            replacement = perturb(original, rng)
            if replacement:
                emit(
                    "D",
                    replace_all(anchor_row, original, replacement),
                    replacement,
                    anchor_language,
                )
        if "F" in wanted:
            replacement = pick_ontology_variant(name_set.get("chebi", []), original, rng)
            if replacement:
                emit("F", replace_all(anchor_row, original, replacement), replacement, "chebi")
        if swapper is not None:
            # E replaces a term the model chooses, not the concept's term, so the
            # avoid-list is every known surface of the concept plus its registry
            # codes -- otherwise the "control" would perturb chemistry after all.
            avoid = {n for names in name_set.values() for n in names} | set(entry.get("codes", []))
            target = rng.choice([l for l in working if l != anchor_language])
            picked = swapper(doc_text(anchor_row), sorted(avoid), target)
            if picked:
                term, replacement = picked
                emit(
                    "E",
                    replace_all(anchor_row, term, replacement),
                    replacement,
                    target,
                    term=term,
                )

    output_path = context.workspace.data("code_switched") / CORPUS_FILENAME
    written = corpus_io.write_rows(output_path, out_rows, output_fieldnames(schema))

    print(f"\nWrote {written} variant rows -> {output_path}")
    print(f"  per variant: {dict(sorted(counts.items()))}")
    return 0


__all__ = [
    "ALIAS_GRAPH_FILENAME",
    "CORPUS_FILENAME",
    "QAC_FILENAME",
    "TEXT_FIELDS",
    "TRACKING_FIELDS",
    "VARIANTS",
    "VARIANT_ID_SEPARATOR",
    "alias_graph_path",
    "build_code_switched",
    "clean_lang_swap",
    "clean_name",
    "doc_text",
    "is_clean_swap",
    "is_distinctive",
    "load_concepts",
    "locate_anchor",
    "output_fieldnames",
    "perturb",
    "pick_ontology_variant",
    "replace_all",
    "term_regex",
]
