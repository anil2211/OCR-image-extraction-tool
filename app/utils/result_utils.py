from __future__ import annotations

from typing import Any

import numpy as np


def make_json_serializable(value: Any) -> Any:

    if isinstance(value, dict):
        return {
            str(key): make_json_serializable(item)
            for key, item in value.items()
        }

    if isinstance(value, (list, tuple)):
        return [
            make_json_serializable(item)
            for item in value
        ]

    if isinstance(value, np.ndarray):
        return value.tolist()

    if isinstance(value, np.generic):
        return value.item()

    # Handle objects that expose tolist()
    if hasattr(value, "tolist"):
        try:
            return value.tolist()
        except Exception:
            pass

    # Primitive values
    if value is None:
        return None

    if isinstance(
        value,
        (str, int, float, bool)
    ):
        return value

    # Final fallback
    try:
        return str(value)

    except Exception:
        return None