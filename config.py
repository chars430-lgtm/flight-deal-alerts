"""Load and validate config.yaml into typed objects."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Optional

import yaml


@dataclass
class Route:
    origin: str
    destinations: list[str] = field(default_factory=list)
    max_price: Optional[float] = None
    label: Optional[str] = None


@dataclass
class SearchWindow:
    earliest_days_from_now: int = 1
    latest_days_from_now: int = 90
    min_trip_nights: int = 2
    max_trip_nights: int = 14


@dataclass
class Config:
    currency: str
    max_round_trip_price: float
    cooldown_hours: int
    price_drop_realert_pct: float
    window: SearchWindow
    routes: list[Route]


def load_config(path: str = "config.yaml") -> Config:
    with open(path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}

    w = raw.get("search_window", {}) or {}
    window = SearchWindow(
        earliest_days_from_now=int(w.get("earliest_days_from_now", 1)),
        latest_days_from_now=int(w.get("latest_days_from_now", 90)),
        min_trip_nights=int(w.get("min_trip_nights", 2)),
        max_trip_nights=int(w.get("max_trip_nights", 14)),
    )

    default_max = float(raw.get("max_round_trip_price", 30))

    routes: list[Route] = []
    for r in raw.get("routes", []) or []:
        if "origin" not in r:
            raise ValueError(f"Route missing 'origin': {r!r}")
        routes.append(
            Route(
                origin=str(r["origin"]).upper().strip(),
                destinations=[str(x).upper().strip() for x in (r.get("destinations") or [])],
                max_price=float(r["max_price"]) if r.get("max_price") is not None else default_max,
                label=r.get("label"),
            )
        )
    if not routes:
        raise ValueError("config.yaml defines no routes to watch.")

    return Config(
        currency=str(raw.get("currency", "EUR")).upper().strip(),
        max_round_trip_price=default_max,
        cooldown_hours=int(raw.get("cooldown_hours", 24)),
        price_drop_realert_pct=float(raw.get("price_drop_realert_pct", 10)),
        window=window,
        routes=routes,
    )


def date_windows(window: SearchWindow):
    """Return (outbound_from, outbound_to, return_from, return_to) as dates."""
    today = date.today()
    out_from = today + timedelta(days=window.earliest_days_from_now)
    out_to = today + timedelta(days=window.latest_days_from_now)
    ret_from = out_from + timedelta(days=window.min_trip_nights)
    ret_to = out_to + timedelta(days=window.max_trip_nights)
    return out_from, out_to, ret_from, ret_to
