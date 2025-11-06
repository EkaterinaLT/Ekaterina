"""Rule-based compliance checking between guidelines and patient records."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Sequence

from .guideline_loader import TreatmentGuideline
from .patient_parser import PatientRecord


@dataclass
class ComplianceResult:
    guideline: TreatmentGuideline
    is_applicable: bool
    missing_required: List[str]
    forbidden_present: List[str]
    details: str


class ComplianceChecker:
    """Evaluate whether a patient record follows a set of guidelines."""

    def __init__(self, guidelines: Sequence[TreatmentGuideline]):
        self._guidelines = list(guidelines)

    def evaluate(self, patient: PatientRecord) -> List[ComplianceResult]:
        results: List[ComplianceResult] = []
        for guideline in self._guidelines:
            applicable = guideline.matches_diagnosis(patient.diagnosis)
            if not applicable:
                results.append(
                    ComplianceResult(
                        guideline=guideline,
                        is_applicable=False,
                        missing_required=[],
                        forbidden_present=[],
                        details="Diagnosis keywords not satisfied.",
                    )
                )
                continue

            missing = _find_missing(patient.interventions, guideline.required_interventions)
            forbidden = _find_present(patient.interventions, guideline.contraindications)
            details = _render_details(guideline, missing, forbidden)
            results.append(
                ComplianceResult(
                    guideline=guideline,
                    is_applicable=True,
                    missing_required=missing,
                    forbidden_present=forbidden,
                    details=details,
                )
            )
        return results

    @staticmethod
    def summarize(results: Iterable[ComplianceResult]) -> str:
        lines: List[str] = []
        results_list = list(results)
        if not results_list:
            return "No guideline results to display."
        for result in results_list:
            header = "Applicable" if result.is_applicable else "Not applicable"
            lines.append(f"{header} guideline for {' '.join(result.guideline.diagnosis_keywords)}")
            if result.details:
                lines.append(f"  {result.details}")
        return "\n".join(lines)


def _find_missing(actual: Sequence[str], required: Sequence[str]) -> List[str]:
    actual_lower = {item.lower() for item in actual}
    missing = [item for item in required if item.lower() not in actual_lower]
    return missing


def _find_present(actual: Sequence[str], forbidden: Sequence[str]) -> List[str]:
    actual_lower = {item.lower() for item in actual}
    present = [item for item in forbidden if item.lower() in actual_lower]
    return present


def _render_details(
    guideline: TreatmentGuideline, missing: Sequence[str], forbidden: Sequence[str]
) -> str:
    parts: List[str] = []
    if missing:
        parts.append("Missing required interventions: " + ", ".join(missing))
    if forbidden:
        parts.append("Forbidden interventions present: " + ", ".join(forbidden))
    if not parts:
        parts.append("All requirements satisfied.")
    if guideline.notes:
        parts.append(f"Notes: {guideline.notes}")
    return " ".join(parts)
