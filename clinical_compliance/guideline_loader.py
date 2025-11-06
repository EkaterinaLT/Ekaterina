"""Utilities for parsing clinical guidelines."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, List, Sequence
import json
import re

try:
    from PyPDF2 import PdfReader
except ModuleNotFoundError:  # pragma: no cover - handled gracefully at runtime
    PdfReader = None  # type: ignore


@dataclass
class TreatmentGuideline:
    """Representation of a guideline for a specific diagnosis.

    Attributes
    ----------
    diagnosis_keywords:
        Keywords that, when found in the patient's diagnosis, indicate
        that the guideline applies.
    required_interventions:
        A collection of interventions that must appear in the patient record.
    optional_interventions:
        Interventions that are allowed but not required.
    contraindications:
        Items that must *not* appear in the patient record when the guideline applies.
    notes:
        Additional free-form text explaining the rule.
    """

    diagnosis_keywords: Sequence[str]
    required_interventions: Sequence[str] = field(default_factory=tuple)
    optional_interventions: Sequence[str] = field(default_factory=tuple)
    contraindications: Sequence[str] = field(default_factory=tuple)
    notes: str | None = None

    def matches_diagnosis(self, diagnosis: str) -> bool:
        normalized = diagnosis.lower()
        return all(keyword.lower() in normalized for keyword in self.diagnosis_keywords)


def _load_guidelines_from_pdf(path: Path) -> List[TreatmentGuideline]:
    if PdfReader is None:
        raise RuntimeError(
            "PyPDF2 is required to parse guideline PDFs. Install it via 'pip install PyPDF2'."
        )

    reader = PdfReader(str(path))
    text_fragments: List[str] = []
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text_fragments.append(extracted)
    text = "\n".join(text_fragments)
    return list(_parse_guideline_text(text))


def _parse_guideline_text(text: str) -> Iterable[TreatmentGuideline]:
    # Expect structured blocks such as:
    # Diagnosis: Diabetes Mellitus Type 2
    # Required: Metformin; Lifestyle counselling
    # Optional: DPP-4 inhibitors
    # Contraindications: Sulfonylureas in pregnancy
    # Notes: follow-up every 3 months
    block_pattern = re.compile(
        r"Diagnosis:\s*(?P<diagnosis>.*?)\n"  # diagnosis line
        r"Required:\s*(?P<required>.*?)\n"  # required interventions
        r"Optional:\s*(?P<optional>.*?)\n"  # optional interventions
        r"Contraindications:\s*(?P<contra>.*?)\n"  # contraindications
        r"Notes:\s*(?P<notes>.*?)(?:\n{2,}|\Z)",  # free-form notes
        flags=re.IGNORECASE | re.DOTALL,
    )

    for match in block_pattern.finditer(text):
        diagnosis = match.group("diagnosis").strip()
        required = _split_items(match.group("required"))
        optional = _split_items(match.group("optional"))
        contraindications = _split_items(match.group("contra"))
        notes = match.group("notes").strip() or None
        if diagnosis:
            yield TreatmentGuideline(
                diagnosis_keywords=tuple(_split_items(diagnosis)),
                required_interventions=tuple(required),
                optional_interventions=tuple(optional),
                contraindications=tuple(contraindications),
                notes=notes,
            )


def _split_items(raw: str) -> List[str]:
    return [item.strip() for item in re.split(r"[,;\n]", raw) if item.strip()]


def _load_guidelines_from_json(path: Path) -> List[TreatmentGuideline]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("Guideline JSON must contain a list of guideline objects")

    guidelines: List[TreatmentGuideline] = []
    for entry in payload:
        guidelines.append(
            TreatmentGuideline(
                diagnosis_keywords=tuple(entry.get("diagnosis_keywords", [])),
                required_interventions=tuple(entry.get("required_interventions", [])),
                optional_interventions=tuple(entry.get("optional_interventions", [])),
                contraindications=tuple(entry.get("contraindications", [])),
                notes=entry.get("notes"),
            )
        )
    return guidelines


def load_guidelines(path: str | Path) -> List[TreatmentGuideline]:
    """Load guidelines from PDF or JSON."""

    path = Path(path)
    suffix = path.suffix.lower()
    if suffix == ".json":
        return _load_guidelines_from_json(path)
    if suffix == ".pdf":
        return _load_guidelines_from_pdf(path)
    raise ValueError("Unsupported guideline format. Use PDF or JSON.")
