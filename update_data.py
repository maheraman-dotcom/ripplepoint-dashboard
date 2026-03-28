"""
update_data.py — RIPPLEPOINT Daily Auto-Updater
Runs in GitHub Actions at 5pm IST and 8:30am IST every weekday
Updates dashboard_data.json with fresh prices and pushes to GitHub
"""

import json
import os
import datetime
from datetime import timezone, timedelta

# ── RUN CONTEXT ───────────────────────────────────────────────────────────────
IST      = timezone(timedelta(hours=5, minutes=30))
now_ist  = datetime.datetime.now(IST)
hour_ist = now_ist.hour
min_ist  = now_ist.minute

if 7 <= hour_ist <= 10:
    run_context = "global_open_830am_IST"
    run_label   = f"08:30 IST — Global Markets Open — {now_ist.strftime('%d %b %Y')}"
    ai_context  = (
        "global market open context. Asian markets have closed, "
        "European markets are opening, US futures are active."
    )
elif 16 <= hour_ist <= 18:
    run_context = "india_close_5pm_IST"
    run_label   = f"17:00 IST — India Markets Close — {now_ist.strftime('%d %b %Y')}"
    ai_context  = (
        "India market close context. NSE/BSE have closed for the day. "
        "Analyse the day's price action and its regime implications."
    )
else:
    run_context = "scheduled_run"
    run_label   = f"Scheduled — {now_ist.strftime('%d %b %Y %H:%M IST')}"
    ai_context  = "scheduled update context."

print(f"RIPPLEPOINT Auto-Update")
print(f"Run context : {run_label}")
print(f"UTC time    : {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
print("")

# ── FETCH PRICES ──────────────────────────────────────────────────────────────
def safe_fetch(ticker):
    try:
        import yfinance as yf
        data = yf.download(ticker, period="2d", progress=False, auto_adjust=True)
        if data is None or data.empty:
            return None
        return float(data["Close"].iloc[-1])
    except Exception as e:
        print(f"  Warning: {ticker} fetch failed — {str(e)[:40]}")
        return None

print("Fetching latest market prices...")
prices = {
    "nifty_close":      safe_fetch("^NSEI"),
    "sp500_close":      safe_fetch("^GSPC"),
    "nasdaq_close":     safe_fetch("^IXIC"),
    "dxy_close":        safe_fetch("DX-Y.NYB"),
    "brent_close":      safe_fetch("BZ=F"),
    "gold_close":       safe_fetch("GC=F"),
    "vix_close":        safe_fetch("^VIX"),
    "india_vix_close":  safe_fetch("^INDIAVIX"),
    "usdinr_close":     safe_fetch("USDINR=X"),
    "us10y_close":      safe_fetch("^TNX"),
}

for k, v in prices.items():
    status = f"{v:.2f}" if v else "failed"
    print(f"  {k:<22}: {status}")

# ── UPDATE JSON ───────────────────────────────────────────────────────────────
print("\nUpdating dashboard_data.json...")

try:
    with open("dashboard_data.json", "r") as f:
        data = json.load(f)
except FileNotFoundError:
    print("ERROR: dashboard_data.json not found in repo")
    raise

curr = data.get("current", {})

# Update all prices that fetched successfully
for key, val in prices.items():
    if val is not None:
        curr[key] = round(val, 4)

# Update metadata
data["current"]      = curr
data["run_context"]  = run_context
data["run_label"]    = run_label
data["ai_context"]   = ai_context
data["last_updated"] = now_ist.strftime("%Y-%m-%d %H:%M IST")
data["generated"]    = now_ist.strftime("%Y-%m-%d")

# Add today to a simple price history log (last 5 entries)
price_log = data.get("price_log", [])
price_log.append({
    "date":       now_ist.strftime("%Y-%m-%d"),
    "time":       now_ist.strftime("%H:%M IST"),
    "context":    run_context,
    "nifty":      prices.get("nifty_close"),
    "sp500":      prices.get("sp500_close"),
    "dxy":        prices.get("dxy_close"),
    "brent":      prices.get("brent_close"),
    "vix":        prices.get("vix_close"),
})
data["price_log"] = price_log[-10:]  # keep last 10 entries

with open("dashboard_data.json", "w") as f:
    json.dump(data, f, indent=2)

print(f"\n✅ dashboard_data.json updated")
print(f"   Run:  {run_label}")
print(f"   GCPI: {curr.get('gcpi_score','—')}")
print(f"   Phase: {curr.get('phase','—')}")
print(f"\nRender will redeploy automatically in ~2 minutes.")
