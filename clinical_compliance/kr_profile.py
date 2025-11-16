"""Utilities for working with locally stored clinical guideline profiles."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Mapping

_PACKAGE_ROOT = Path(__file__).resolve().parent
_PROJECT_ROOT = _PACKAGE_ROOT.parent


def _coerce_criteria(obj: Mapping[str, Any] | None) -> Dict[str, list]:
    """Return a shallow copy of a criteria mapping with list values only."""
    result: Dict[str, list] = {}
    if not obj:
        return result
    for key, value in obj.items():
        if isinstance(value, list):
            result[key] = value
        elif value is None:
            result[key] = []
        else:
            raise ValueError(
                f"Criteria entry '{key}' must be a list, got {type(value).__name__}"
            )
    return result


def load_profile(path: str | Path) -> Dict[str, Any]:
    """Load a JSON profile that represents a clinical guideline snapshot.

    Parameters
    ----------
    path:
        Either an absolute path or a path relative to the project root.  The
        helper accepts both strings and :class:`~pathlib.Path` instances so that
        it can be used from scripts, tests, or interactive notebooks.

    Returns
    -------
    dict
        A dictionary with at least ``diagnosis_scope`` and ``criteria`` keys.

    Raises
    ------
    FileNotFoundError
        If the profile file does not exist.
    ValueError
        If the JSON payload is not an object or does not contain the expected
        structure.
    """

    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = (_PROJECT_ROOT / candidate).resolve()

    data = json.loads(candidate.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Profile JSON must contain an object at the top level")

    diagnosis_scope = data.get("diagnosis_scope")
    if not isinstance(diagnosis_scope, str):
        raise ValueError("Profile must define 'diagnosis_scope' as a string")

    criteria = data.get("criteria")
    if criteria is None:
        raise ValueError("Profile must include a 'criteria' object")
    if not isinstance(criteria, Mapping):
        raise ValueError("'criteria' must be a JSON object")

    normalized = _coerce_criteria(criteria)

    profile: Dict[str, Any] = {
        "diagnosis_scope": diagnosis_scope,
        "criteria": normalized,
        "notes": data.get("notes"),
    }
    return profile
