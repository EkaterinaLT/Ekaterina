"""Command line interface for the compliance checker."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

from .compliance_checker import ComplianceChecker
from .guideline_loader import load_guidelines
from .patient_parser import load_patient_record


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Check whether a patient XML record complies with clinical guidelines",
    )
    parser.add_argument("guidelines", type=Path, help="Path to guidelines PDF or JSON file")
    parser.add_argument("patient", type=Path, help="Path to patient XML file")
    parser.add_argument(
        "--show-all",
        action="store_true",
        help="Show results for non-applicable guidelines as well",
    )
    return parser


def run(args: Sequence[str] | None = None) -> int:
    parser = build_parser()
    namespace = parser.parse_args(args)

    guidelines = load_guidelines(namespace.guidelines)
    patient = load_patient_record(namespace.patient)

    checker = ComplianceChecker(guidelines)
    results = checker.evaluate(patient)

    applicable = [result for result in results if result.is_applicable or namespace.show_all]
    report_lines = [
        f"Patient: {patient.identifier or 'unknown'}",
        f"Diagnosis: {patient.diagnosis or 'unknown'}",
        "",
    ]
    report_lines.append(ComplianceChecker.summarize(applicable))
    print("\n".join(report_lines))
    return 0


def main() -> None:
    raise SystemExit(run())


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    main()
