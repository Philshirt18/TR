# Grid Mean-Reversion Top-15 (Auto-Update)

Mobilfreundliche, statische PWA, die täglich per GitHub Actions aktualisiert wird. Sie liest outputs/top15_table.csv (aus deinem Research-Script) und veröffentlicht docs/top15.json + eine schlanke Website für GitHub Pages.

## Quickstart

1. Stelle sicher, dass dein run_grid_research.py im Repo liegt und beim Run outputs/top15_table.csv erzeugt.
2. Push nach GitHub.
3. Aktiviere Pages: Settings → Pages → Source: Deploy from a branch, Branch: main, Folder: /docs.
4. Warte auf den Cron-Run oder triggere Actions → Run workflow manuell.
5. Öffne: https://GH_USER.github.io/REPO_NAME/ auf dem Handy → „Zum Home-Bildschirm hinzufügen“.

## Optional: Telegram Push

Setze Secrets:

* TELEGRAM_BOT_TOKEN
* TELEGRAM_CHAT_ID

## Lokal testen

```
python -m http.server -d docs 9000
```
und dann http://localhost:9000

## Tech

* GitHub Actions (Cron)
* Static PWA (Manifest + Service Worker)
* Minimal JS, schnell & offline-freundlich
