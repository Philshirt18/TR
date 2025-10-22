import os, json, requests, pathlib

bot = os.environ.get("TELEGRAM_BOT_TOKEN")
chat = os.environ.get("TELEGRAM_CHAT_ID")
if not bot or not chat:
    print("Telegram secrets not set; skipping.")
    raise SystemExit(0)

data_path = pathlib.Path("docs/top15.json")
if not data_path.exists():
    print("No docs/top15.json; skipping.")
    raise SystemExit(0)

d = json.loads(data_path.read_text())
rows = d.get("rows", [])[:5]
lines = [f"Grid Top-15 update ({d.get('updated','')})"]
for r in rows:
    lines.append(f"#{r[0]} {r[1]} | HR {r[3]} | Edge {r[4]} | Sig/W {r[2]}")
msg = "\n".join(lines)
url = f"https://api.telegram.org/bot{bot}/sendMessage"
resp = requests.post(url, json={"chat_id": chat, "text": msg})
resp.raise_for_status()
print("Telegram notification sent.")
