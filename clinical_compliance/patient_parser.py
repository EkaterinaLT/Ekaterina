"""Parser for structured patient XML cards."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Sequence
import xml.etree.ElementTree as ET


@dataclass
class PatientRecord:
    """Minimal representation of a patient record used for compliance checks."""

    identifier: str | None
    diagnosis: str
    interventions: Sequence[str] = field(default_factory=tuple)
    contraindications: Sequence[str] = field(default_factory=tuple)
    metadata: Dict[str, str] = field(default_factory=dict)


def load_patient_record(path: str | Path) -> PatientRecord:
    path = Path(path)
    tree = ET.parse(str(path))
    root = tree.getroot()

    identifier = _get_text(root.find(".//Identifier")) or root.attrib.get("id")
    diagnosis = _get_text(root.find(".//Diagnosis")) or ""
    interventions = _extract_items(root, "Treatment", attribute="name")
    contraindications = _extract_items(root, "Contraindication")

    metadata: Dict[str, str] = {}
    for elem in root.findall(".//Meta/*"):
        if elem.text:
            metadata[elem.tag] = elem.text.strip()
    return PatientRecord(
        identifier=identifier,
        diagnosis=diagnosis,
        interventions=tuple(interventions),
        contraindications=tuple(contraindications),
        metadata=metadata,
    )


def _extract_items(root: ET.Element, tag: str, attribute: str | None = None) -> List[str]:
    items: List[str] = []
    for elem in root.findall(f".//{tag}"):
        if attribute and attribute in elem.attrib:
            value = elem.attrib[attribute].strip()
            if value:
                items.append(value)
        elif elem.text:
            items.append(elem.text.strip())
    return items


def _get_text(element: ET.Element | None) -> str | None:
    if element is None:
        return None
    text = element.text or ""
    return text.strip() or None
