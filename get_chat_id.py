"""Helper: print the Telegram chat_id(s) that have messaged your bot.

Usage (locally, once Python is installed):
    TELEGRAM_BOT_TOKEN=123:ABC python get_chat_id.py
or:
    python get_chat_id.py 123:ABC

First send any message to your bot in Telegram, then run this.
(Alternatively, just message @userinfobot on Telegram to get your numeric ID.)
"""
import os
import sys

import requests

token = os.environ.get("TELEGRAM_BOT_TOKEN") or (sys.argv[1] if len(sys.argv) > 1 else None)
if not token:
    sys.exit("Provide the bot token via TELEGRAM_BOT_TOKEN env var or as the first argument.")

data = requests.get(f"https://api.telegram.org/bot{token}/getUpdates", timeout=30).json()
if not data.get("ok"):
    sys.exit(f"Telegram error: {data}")

found = False
for update in data.get("result", []):
    msg = update.get("message") or update.get("channel_post") or {}
    chat = msg.get("chat", {})
    if chat:
        found = True
        name = chat.get("first_name") or chat.get("title") or "?"
        print(f"chat_id: {chat.get('id')}  |  name: {name}  |  type: {chat.get('type')}")

if not found:
    print("No messages found. Send a message to your bot first, then re-run.")
