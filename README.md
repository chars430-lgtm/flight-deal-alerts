# ✈️ Flight Deal Alerts

Get a **Telegram push notification** the moment a **round-trip Ryanair fare**
drops below a price you set. Runs free in the cloud via GitHub Actions — no need
to keep your computer on.

- Watches any number of origin airports, to specific destinations **or "anywhere"**.
- You set the max round-trip price, date window, and trip length.
- De-duplicates so you aren't spammed with the same deal (re-alerts on price drops).

---

## How it works

```
GitHub Actions (every 30 min)
   → main.py queries Ryanair's cheapest-fares API (ryanair-py)
   → keeps only round trips at/under your price threshold
   → sends new ones to your phone via a Telegram bot
   → commits which deals it already sent, so it won't repeat them
```

---

## Setup (about 10 minutes, one time)

### 1. Create your Telegram bot
1. In Telegram, open a chat with **@BotFather**.
2. Send `/newbot`, follow the prompts, pick a name and username.
3. BotFather replies with a **bot token** like `123456789:AA...`. Copy it.
4. **Send your new bot any message** (e.g. "hi") — this is required so it can message you back.

### 2. Get your chat ID
Easiest: message **@userinfobot** on Telegram — it replies with your numeric ID (e.g. `987654321`). That's your `TELEGRAM_CHAT_ID`.

### 3. Put this project on GitHub
1. Create a **new repository** on GitHub (a **public** repo is recommended — Actions
   minutes are unlimited on public repos, and this code contains no secrets).
2. Push this folder to it:
   ```bash
   cd flight-deal-alerts
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/<your-username>/<your-repo>.git
   git push -u origin main
   ```

### 4. Add your secrets
In your repo on GitHub: **Settings → Secrets and variables → Actions → New repository secret**. Add two:
| Name | Value |
|------|-------|
| `TELEGRAM_BOT_TOKEN` | the token from BotFather |
| `TELEGRAM_CHAT_ID` | your numeric chat ID |

### 5. Enable and test
1. Go to the **Actions** tab → if prompted, enable workflows.
2. Open **Flight Deal Alerts** → **Run workflow** → set **test = true** → **Run**.
3. Within ~1 minute you should receive a ✅ test message in Telegram. 🎉

If you don't get it, open the workflow run logs — the "Run flight monitor" step
prints the exact Telegram API error (usually a wrong token or chat ID).

---

## Configure what to watch

Edit [`config.yaml`](config.yaml), commit, and push. The next scheduled run uses it.

```yaml
currency: EUR
max_round_trip_price: 30        # default ceiling (total out + back)
cooldown_hours: 24              # don't repeat a deal within this window...
price_drop_realert_pct: 10      # ...unless price drops this % (then re-alert)

search_window:
  earliest_days_from_now: 1
  latest_days_from_now: 90
  min_trip_nights: 2
  max_trip_nights: 14

routes:
  - origin: DUB                 # Dublin
    destinations: []            # [] = ANYWHERE
    max_price: 25
    label: "Dublin -> anywhere"

  - origin: STN                 # London Stansted
    destinations: ["OPO", "LIS"]
    max_price: 20
    label: "Stansted -> Portugal"
```

- **`destinations: []`** = alert for the cheapest deal to *any* destination — best for
  finding extreme prices.
- **`destinations: ["MAD","BCN"]`** = only those airports.
- **`max_price`** per route overrides the global default.
- Airport codes are 3-letter **IATA** codes (MAD = Madrid, CRL = Brussels Charleroi, etc.).

---

## Change how often it checks
In [`.github/workflows/check-flights.yml`](.github/workflows/check-flights.yml), edit the cron line:
```yaml
- cron: "*/30 * * * *"   # every 30 min. "0 * * * *" = hourly, "*/15 * * * *" = every 15 min
```

---

## Notes & limits
- Uses Ryanair's public fare API through the community `ryanair-py` library — **unofficial**,
  so it can occasionally change or rate-limit. The script fails gracefully and retries next run.
- GitHub sometimes delays scheduled Actions by a few minutes under load — normal.
- Prices are for **1 adult**, and are the fare only (bags/seats extra), same as the Ryanair site's headline price.
- Want SMS or email too later? The notification logic lives in [`notifier.py`](notifier.py) —
  a second channel can be added there.

## Run locally (optional)
Requires Python 3.11+:
```bash
pip install -r requirements.txt
export TELEGRAM_BOT_TOKEN=...   # Windows PowerShell: $env:TELEGRAM_BOT_TOKEN="..."
export TELEGRAM_CHAT_ID=...
python main.py                  # or: TEST_MODE=1 python main.py  to send a test ping
```
