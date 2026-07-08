"""Send push notifications via a Telegram bot."""
from __future__ import annotations

import os

import requests

_API = "https://api.telegram.org/bot{token}/sendMessage"


def _creds() -> tuple[str, str]:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be set (as GitHub Actions secrets)."
        )
    return token, chat_id


def send_message(text: str) -> None:
    token, chat_id = _creds()
    resp = requests.post(
        _API.format(token=token),
        json={
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": False,
        },
        timeout=30,
    )
    if resp.status_code != 200:
        print(f"[error] Telegram send failed {resp.status_code}: {resp.text}")
    resp.raise_for_status()


def format_deal(deal) -> str:
    return (
        f"🛫 <b>Flight deal!</b> {deal.currency} <b>{deal.price:.2f}</b> round trip\n"
        f"<b>{deal.origin} → {deal.destination}</b>\n"
        f"{deal.origin_name} → {deal.destination_name}\n"
        f"📅 Out {deal.out_date} · Back {deal.in_date} ({deal.nights} nights)\n"
        f'🔗 <a href="{deal.booking_url()}">Book on Ryanair</a>'
    )
