"""Track which deals we've already alerted, to avoid spamming."""
from __future__ import annotations

import json
import os
from datetime import datetime, timedelta, timezone


def _now() -> datetime:
    return datetime.now(timezone.utc)


def load_state(path: str) -> dict:
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f) or {}
    except Exception:
        return {}


def save_state(path: str, state: dict) -> None:
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, sort_keys=True)


def should_alert(state: dict, deal, cooldown_hours: int, drop_pct: float) -> bool:
    entry = state.get(deal.key)
    if entry is None:
        return True
    try:
        last = datetime.fromisoformat(entry["last_alerted"])
        prev_price = float(entry.get("price", 1e9))
    except Exception:
        return True
    # Re-alert immediately if the price dropped meaningfully.
    if deal.price <= prev_price * (1 - drop_pct / 100.0):
        return True
    # Otherwise honor the cooldown window.
    return _now() - last >= timedelta(hours=cooldown_hours)


def record_alert(state: dict, deal) -> None:
    state[deal.key] = {"price": deal.price, "last_alerted": _now().isoformat()}


def prune(state: dict, max_age_days: int = 120) -> None:
    cutoff = _now() - timedelta(days=max_age_days)
    for k in list(state.keys()):
        try:
            if datetime.fromisoformat(state[k]["last_alerted"]) < cutoff:
                del state[k]
        except Exception:
            del state[k]
