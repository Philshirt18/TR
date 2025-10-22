import json, pandas as pd, datetime as dt, pathlib

csv_path = pathlib.Path('outputs/top15_table.csv')
docs = pathlib.Path('docs')
docs.mkdir(parents=True, exist_ok=True)
columns = ["Rank","Ticker","Signals/W","Hitrate ±3%","Net P&L/Trade","Median Hold","24h Vol","MaxDD","Robustness","Notes"]
if csv_path.exists():
    df = pd.read_csv(csv_path)
    if set(columns).issubset(set(df.columns)):
        df = df[columns]
        rows = df.values.tolist()
    else:
        rows = [[i+1,"—","—","—","—","—","—","—","0.00",""] for i in range(15)]
else:
    rows = [[i+1,"—","—","—","—","—","—","—","0.00",""] for i in range(15)]
out = {
"updated": dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
"columns": columns,
"rows": rows
}
(docs / 'top15.json').write_text(json.dumps(out), encoding='utf-8')
print("Wrote docs/top15.json")
