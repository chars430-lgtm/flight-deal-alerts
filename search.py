"""Query Ryanair's cheapest-fares API for round-trip deals."""
from __future__ import annotations

from dataclasses import dataclass

from ryanair import Ryanair

from config import Config, Route, date_windows


@dataclass
class Deal:
    origin: str
    destination: str
    origin_name: str
    destination_name: str
    out_date: str  # ISO date, e.g. 2026-08-01
    in_date: str
    nights: int
    price: float
    currency: str

    @property
    def key(self) -> str:
        return f"{self.origin}-{self.destination}-{self.out_date}-{self.in_date}"

    def booking_url(self) -> str:
        return (
            "https://www.ryanair.com/gb/en/trip/flights/select"
            "?adults=1&teens=0&children=0&infants=0"
            f"&dateOut={self.out_date}&dateIn={self.in_date}"
            f"&originIata={self.origin}&destinationIata={self.destination}"
            "&isConnectedFlight=false&isReturn=true&discount=0"
        )


def make_api(currency: str) -> Ryanair:
    try:
        return Ryanair(currency=currency)
    except TypeError:
        # Fallback for library versions with a different constructor signature.
        return Ryanair()


def search_route(api: Ryanair, route: Route, cfg: Config) -> list[Deal]:
    out_from, out_to, ret_from, ret_to = date_windows(cfg.window)
    try:
        trips = api.get_cheapest_return_flights(route.origin, out_from, out_to, ret_from, ret_to)
    except Exception as e:  # network / API hiccups shouldn't kill the whole run
        print(f"[warn] search failed for {route.origin}: {e}")
        return []

    max_price = route.max_price if route.max_price is not None else cfg.max_round_trip_price
    deals: list[Deal] = []

    for t in trips or []:
        out = getattr(t, "outbound", None)
        inb = getattr(t, "inbound", None)
        if out is None or inb is None:
            continue

        price = float(getattr(t, "totalPrice", 0) or 0)
        if price <= 0 or price > max_price:
            continue

        dest = getattr(out, "destination", "")
        if route.destinations and dest not in route.destinations:
            continue

        out_dt = getattr(out, "departureTime", None)
        in_dt = getattr(inb, "departureTime", None)
        if out_dt is None or in_dt is None:
            continue

        nights = (in_dt.date() - out_dt.date()).days
        if nights < cfg.window.min_trip_nights or nights > cfg.window.max_trip_nights:
            continue

        deals.append(
            Deal(
                origin=getattr(out, "origin", route.origin),
                destination=dest,
                origin_name=getattr(out, "originFull", route.origin),
                destination_name=getattr(out, "destinationFull", dest),
                out_date=out_dt.date().isoformat(),
                in_date=in_dt.date().isoformat(),
                nights=nights,
                price=round(price, 2),
                currency=getattr(out, "currency", cfg.currency) or cfg.currency,
            )
        )

    deals.sort(key=lambda d: d.price)
    return deals
