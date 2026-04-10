# Degaline — Lithuanian Fuel Price Map

A publicly hosted web app displaying Lithuanian fuel prices on an interactive map, available at **https://ltlukoziuzu.github.io/degaline-zemelapis/**. Daily data is fetched and processed by a GitHub Actions pipeline; all gas stations appear as pins with price info. A local dev mode is also supported.

**Two audiences:**
- **End-users (any device):** Zero prerequisites — just open the website in any modern browser.
- **Developer/tester (Linux, technical):** Can run locally via `server.py` after running `pipeline.py` to generate `data/stations.json`. CachyOS/Arch; `curl` and `xdg-open` assumed available.

## Hard Constraints

- **Zero prerequisites for end-users.** No installs required — the app runs at https://ltlukoziuzu.github.io/degaline-zemelapis/ in any modern browser on any device.
- **All three browsers must work:** Chrome, Edge, Firefox. The feature set may differ slightly by browser, but all three must load data and display the map correctly.
- **Mobile and desktop must both work.** The UI must be fully functional on phones and tablets, not just desktop.
- **No local server required for end-users.** GitHub Pages serves the static files; GitHub Actions handles data updates. The local server (`server.py`) is for developer use only.

## Architecture

**Hosted (primary):**
- `pipeline.py` — runs daily via GitHub Actions. Downloads the xlsx from ENA, parses with openpyxl, geocodes new addresses via Photon, writes `data/stations.json` and updates `data/geocache.json`. Diffs against previous data and writes logs to `data/logs/` and snapshots to `data/history/`.
- `.github/workflows/update.yml` — daily cron at 07:00 UTC. Runs `pipeline.py`, commits updated data back to `main`, deploys to GitHub Pages. Sends email notification when stations change.
- `index.html` — fetches `data/stations.json` on load, renders markers. No xlsx parsing, no geocoding, no local server dependency.

**Local dev:**
- Run `python3 pipeline.py` to generate `data/stations.json`, then serve with `python3 server.py` and open `http://localhost:58472`.
- `server.py` serves static files only (no POST endpoint needed anymore — geocaching is handled by `pipeline.py`).
- `update.bat` / `update.sh` and `server.ps1` are retained but no longer the primary workflow.

**Why not `file://`:** browser security blocks auto-reading sibling files. A local server avoids this for dev use.

**Port:** `58472` — fixed, avoids conflicts with common dev tools.

## Reference Docs

- [data-flow.md](data-flow.md) — Full data flow diagram (scripts → server → browser)
- [xlsx-filehandling.md](xlsx-filehandling.md) — xlsx source URL, naming/casing, data shape, column map, "neprekiauja" handling
- [geocoding-strategy.md](geocoding-strategy.md) — Photon config, cache format, failure handling
- [file-structure.md](file-structure.md) — Project and dist directory layout, build/handoff instructions
- [nominatim.md](nominatim.md) — Photon/Nominatim User-Agent, rate limiting, 429 retry logic
- [dev-environment.md](dev-environment.md) — Confirmed tools installed on developer's machine
- [progress.md](progress.md) — Current task tracking and order of work
- [error-handling-practices.md](error-handling-practices.md) — Practices on how specific errors should be handled
- [plan-github-migration.md](plan-github-migration.md) — Completed GitHub Pages + Actions migration plan
- [plan-step-8-6-search-sidebar.md](plan-step-8-6-search-sidebar.md) — Search + sidebar plan (desktop-only, superseded — needs mobile-first redesign)

## UI/UX Requirements

- **Map fills the screen.** Controls are minimal overlays.
- **One-button simplicity.** Auto-loads data on open; no file pickers, no manual steps.
- **Marker colors by company:** each company gets a distinct hex color; small operators (≤3 stations) share grey. Color map in `COMPANY_COLORS` in `index.html`, reference in `data/company-colors.txt`.
- **Popups in Lithuanian.** All labels should be in Lithuanian.
- **No error stack traces shown to user.** On failure, show a friendly Lithuanian-language message.
- **Mobile-first for all new UI features.** Design for phone first; desktop layout follows from that.

## Working with the Developer

**Never assume system tools are installed.** Before running any command that depends on a non-core tool (Python packages, Node modules, CLI utilities, etc.), check whether it is available first. If it is missing, stop and tell the user exactly what to install and how, rather than silently trying an alternative or failing mid-task.

See [dev-environment.md](dev-environment.md) for the confirmed list of tools already installed on the developer's machine.

## Key Implementation Notes

- **CORS:** The xlsx fetch is done by `pipeline.py` server-side — do not fetch the xlsx from JavaScript directly (ena.lt does not send permissive CORS headers).
- **`file://` guard:** If `location.protocol === 'file:'`, show a full-screen error telling the user to open the app at https://ltlukoziuzu.github.io/degaline-zemelapis/. Do not attempt to load data in this case.
- **Libraries are bundled locally** in `lib/` — do not use CDN links. The app must work without internet (apart from tile fetching).
- **Leaflet tiles:** Use CartoDB Voyager (`basemaps.cartocdn.com/rastertiles/voyager`), not OSM default — OSM blocks requests without a Referer header. If offline, the map shows a grey grid but markers and popups still work.
- **Price formatting:** Display prices as `X.XXX €/L` (3 decimal places, Lithuanian convention).
- **Empty price cells:** Treat as "not available" — show "–", not 0.000.
- **Geocache key format:** Keys are address strings stripped of surrounding whitespace. Do not change this — pipeline.py strips addresses from the xlsx before cache lookup.
- **Geocache write timing:** `pipeline.py` flushes to disk every 20 newly geocoded entries so progress is preserved if the process is interrupted.
- **stations.json format:** `{ "date": "YYYY-MM-DD", "stations": [...] }`. Each station has `company`, `municipality`, `address`, `lat`, `lng`, `p95`, `diesel`, `lpg`. Prices are floats or `null`.
