from __future__ import annotations

import re


def is_valid_ticker(value: str) -> bool:
    if not value or not isinstance(value, str):
        return False
    cleaned = value.strip().upper()
    if not cleaned:
        return False
    return bool(re.fullmatch(r"[A-Z0-9.-]+", cleaned))


def is_valid_forecast_days(value: int) -> bool:
    return value in {7, 15, 30, 60, 90}
