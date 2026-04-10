# Degaline — Lithuanian Fuel Price Map

A locally-run web app displaying Lithuanian fuel prices on an interactive map. The daily .xlsx is fetched by a launch script; all gas stations appear as pins with price info.

**Two audiences:**
- **End-users (Windows, non-technical):** Zero prerequisites, launched via `update.bat`, use Chrome or Edge.
- **Developer/tester (Linux, technical):** Launched via `update.sh`, use any modern browser including Firefox.

## Hard Constraints

- **Zero prerequisites on Windows.** No Python, Node.js, or any runtime may be required. The app must work on a stock Windows 10/11 machine out of the box.
- **Linux support for developer use.** On Linux (CachyOS/Arch), `curl` and `xdg-open` are assumed available.
- **All three browsers must work:** Chrome, Edge, Firefox. The feature set may differ slightly by browser, but all three must load data and display the map correctly.
- **Target Windows users are completely non-technical.** No CLI, no config files, no error messages that require interpretation.
- **Local only.** No server, no backend, no database. All processing happens in the browser.

## Architecture

Launch scripts start a local HTTP server on `localhost:58472`; the browser opens that address.

- `update.bat` / `update.sh` — Download the daily .xlsx, start a background HTTP server (`server.ps1` / `server.py`), open the browser.
- `index.html` — Auto-fetches `data/latest.xlsx` and `data/geocache.json` on load. No file pickers needed.
- `server.ps1` / `server.py` — Serve static files + accept `POST /data/geocache.json` to write the cache. Die when the terminal closes.

**Why not `file://`:** browser security blocks auto-reading sibling files and writing files without user gestures. A local server avoids both. PowerShell `HttpListener` is built into Windows 10/11; Python `http.server` is built into Python 3.

**Port:** `58472` — fixed, avoids conflicts with common dev tools.

## Reference Docs

- [data-flow.md](data-flow.md) — Full data flow diagram (scripts → server → browser)
- [xlsx-filehandling.md](xlsx-filehandling.md) — xlsx source URL, naming/casing, data shape, column map, "neprekiauja" handling
- [geocoding-strategy.md](geocoding-strategy.md) — Nominatim config, cache format, failure handling
- [file-structure.md](file-structure.md) — Project and dist directory layout, build/handoff instructions
- [nominatim.md](nominatim.md) — Nominatim User-Agent, rate limiting, 429 retry logic
- [dev-environment.md](dev-environment.md) — Confirmed tools installed on developer's machine
- [progress.md](progress.md) — Current task tracking and order of work
- [error-handling-practices.md](error-handling-practices.md) — Practices on how specific errors should be handled

## UI/UX Requirements

- **Map fills the screen.** Controls are minimal overlays.
- **One-button simplicity.** Auto-loads data on open; no file pickers, no manual steps.
- **Marker colors by fuel type availability:** e.g., green = has 95+diesel+LPG, yellow = partial, grey = data incomplete.
- **Popups in Lithuanian.** All labels should be in Lithuanian.
- **No error stack traces shown to user.** On failure, show a friendly Lithuanian-language message.

## Working with the Developer

**Never assume system tools are installed.** Before running any command that depends on a non-core tool (Python packages, Node modules, CLI utilities, etc.), check whether it is available first. If it is missing, stop and tell the user exactly what to install and how, rather than silently trying an alternative or failing mid-task.

See [dev-environment.md](dev-environment.md) for the confirmed list of tools already installed on the developer's machine.

## Key Implementation Notes

- **CORS:** Nominatim allows browser requests. The xlsx fetch is done by the launch script — do not fetch the xlsx from JavaScript directly (ena.lt does not send permissive CORS headers).
- **`file://` guard:** If `location.protocol === 'file:'`, show a full-screen error telling the user to launch via the bat/sh script. Do not attempt to load data in this case.
- **Libraries are bundled locally** in `lib/` — do not use CDN links. The app must work without internet (apart from geocoding and tile fetching).
- **Leaflet tiles:** Use CartoDB Voyager (`basemaps.cartocdn.com/rastertiles/voyager`), not OSM default — OSM blocks requests without a Referer header. If offline, the map shows a grey grid but markers and popups still work.
- **Date parsing:** Excel dates are often stored as serial numbers. Use SheetJS `cellDates: true` or convert manually.
- **Price formatting:** Display prices as `X.XXX €/L` (3 decimal places, Lithuanian convention).
- **Empty price cells:** Treat as "not available" — show "–", not 0.000.
- **geocache write timing:** Write after every 20 newly geocoded entries so progress is preserved if the tab is closed mid-run.
