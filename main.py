"""Entry point: search all routes, send Telegram alerts for new cheap deals."""
from __future__ import annotations

import os
import sys

from config import load_config
from notifier import format_deal, send_message
from search import make_api, search_route
from state import load_state, prune, record_alert, save_state, should_alert

STATE_PATH = os.path.join("state", "seen_deals.json")


def run_test() -> None:
    send_message(
        "✅ <b>Flight Deal Alerts is connected.</b>\n"
        "You'll get a message here the moment a round trip drops below your price threshold."
    )
    print("Test message sent.")


def main() -> None:
    if os.environ.get("TEST_MODE", "").strip().lower() in ("1", "true", "yes"):
        run_test()
        return

    cfg = load_config()
    api = make_api(cfg.currency)
    state = load_state(STATE_PATH)

    all_deals = []
    for route in cfg.routes:
        deals = search_route(api, route, cfg)
        tag = route.label or route.origin
        print(f"{tag}: {len(deals)} deal(s) at/under threshold")
        all_deals.extend(deals)

    sent = 0
    for deal in sorted(all_deals, key=lambda d: d.price):
        if should_alert(state, deal, cfg.cooldown_hours, cfg.price_drop_realert_pct):
            send_message(format_deal(deal))
            record_alert(state, deal)
            sent += 1

    prune(state)
    save_state(STATE_PATH, state)
    print(f"Done. {len(all_deals)} qualifying deal(s) found, {sent} alert(s) sent.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:  # noqa: BLE001
        print(f"[fatal] {e}", file=sys.stderr)
        sys.exit(1)
