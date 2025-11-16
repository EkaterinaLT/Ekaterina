"""Utility helpers for normalizing free-text medical notes."""

from __future__ import annotations

import re
from typing import Iterable, List, Sequence

_STOPWORDS = {"пациент", "жалобы", "отрицает", "данных"}

_SECTION_CATEGORIES = {
    "objective": {
        "темп": "контроль температуры",
        "давл": "контроль артериального давления",
        "сат": "оценка сатурации",
    },
    "exam_plan": {
        "общий анализ крови": "лабораторная диагностика",
        "рентген": "лучевая диагностика",
        "флюор": "лучевая диагностика",
    },
}

_TREATMENT_CATEGORIES = {
    "жаропонижа": "жаропонижающая терапия",
    "противовирус": "противовирусная терапия",
    "антибиот": "антибактериальная терапия",
}

_ANAMNESIS_HINTS = {
    "кашл": "жалобы на кашель",
    "насморк": "жалобы на ринит",
    "температур": "жалобы на повышение температуры",
    "головн": "жалобы на головную боль",
}


def _clean_token(value: str) -> str:
    normalized = re.sub(r"\s+", " ", value).strip().lower()
    normalized = normalized.strip(".,;:!?")
    return normalized


def normalize_list(items: Sequence[str] | None) -> List[str]:
    """Return a deduplicated, lower-cased list of strings."""
    if not items:
        return []
    seen = set()
    result: List[str] = []
    for raw in items:
        if raw is None:
            continue
        normalized = _clean_token(str(raw))
        if not normalized or normalized in _STOPWORDS:
            continue
        if normalized not in seen:
            seen.add(normalized)
            result.append(normalized)
    return result


def expand_with_categories(items: Sequence[str] | None, section: str) -> List[str]:
    """Augment the list with coarse categories inferred from keywords."""
    normalized = normalize_list(items)
    mapping = _SECTION_CATEGORIES.get(section, {})
    enriched = list(normalized)
    for value in normalized:
        for needle, category in mapping.items():
            if needle in value and category not in enriched:
                enriched.append(category)
    return enriched


def normalize_treatment(items: Iterable[str] | None) -> List[str]:
    return normalize_list(list(items) if items is not None else [])


def expand_treatment_categories(items: Sequence[str] | None) -> List[str]:
    normalized = normalize_list(items)
    enriched = list(normalized)
    for value in normalized:
        for needle, category in _TREATMENT_CATEGORIES.items():
            if needle in value and category not in enriched:
                enriched.append(category)
    return enriched


def enrich_anamnesis(items: Sequence[str] | None, raw_text: str | None) -> List[str]:
    normalized = normalize_list(items)
    if not raw_text:
        return normalized
    text = raw_text.lower()
    enriched = list(normalized)
    for needle, label in _ANAMNESIS_HINTS.items():
        if needle in text and label not in enriched:
            enriched.append(label)
    return enriched
