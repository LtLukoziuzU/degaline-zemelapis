# Project Progress

## Completed

### Step 1 — xlsx inspection
Downloaded today's file (`dk-2026-04-09.xlsx`) and confirmed column structure. Header row detected dynamically by scanning for `'Data'` in column A (row number varies between files). Confirmed 7-column wide format: date, company, municipality, address, 95 petrol, diesel, LPG. LPG/price cells can be float or string `'neprekiauja'`. Yesterday's file used a different 6-column long format — treating today's wide format as the standard going forward.

### Step 2 — minimal index.html with SheetJS parsing
Built first version of `index.html` with a file input, SheetJS (bundled at `lib/xlsx.full.min.js`), dynamic header detection, and on-screen display of parsed rows. Verified correct parsing of `latest.xlsx`.

### Step 3 — Leaflet map with test markers
Added full-screen Leaflet map (bundled at `lib/leaflet/`) centred on Lithuania with 5 hardcoded test markers and sample popups. Switched tile provider from OSM default to CartoDB Voyager — OSM blocks `file://` requests due to missing Referer header. Dark toolbar overlay with file picker and status text.

### Step 4 — local HTTP server + unified geocache
Scrapped the File System Access API / IndexedDB dual-backend approach. Instead, `update.bat` and `update.sh` now start a local HTTP server (`server.ps1` on Windows via PowerShell, `server.py` on Linux via Python 3) on port 58472, then open the browser to `http://localhost:58472`. The server serves static files and accepts `POST /data/geocache.json` to write the cache to disk. All browsers use identical `fetch()` calls — no browser-specific code. Verified: 714 stations parsed, geocache loaded, server running on fresh launch.

### Step 5 — Live geocoding
Switched from Nominatim to Photon (komoot.io) — better handling of Lithuanian addresses, no API key required. Geocache built for all 713 stations. 23 addresses required manual coordinate lookup (municipality fallbacks and wrong-country results); saved to `data/manual-geocache-addresses.md`. `Duomenys:` stray row marked as `source: "failed"` to prevent geocoding.

### Step 6 — Full data pipeline + markers
All 713 stations placed as Leaflet markers. Stations sharing identical coordinates combined into one popup. Popup shows company, address, and non-null prices. Map bounds restricted to prevent panning far outside Lithuania.

### Step 7 — `update.bat` and `update.sh`
Both scripts written and verified. No changes needed after Steps 5–6.

### Step 8 (partial) — UI polish
1. Attribution/licensing text for LEA data source in UI + company list generated dynamically from xlsx ✓
2. Marker clustering for dense areas (e.g. Vilnius) ✓
3. Marker colours by company — SVG teardrop pins, each company gets a distinct hex color derived from their brand, small operators (≤3 stations) share grey. Color map in `COMPANY_COLORS` in `index.html`, reference colors in `data/company-colors.txt` ✓
4. Marker popup styling ✓
5. Persist last map position and zoom level in localStorage (restore on next load) ✓

### Step 9 — GitHub migration + hosted deployment
Project moved to a public GitHub repo (`LtLukoziuzU/degaline-zemelapis`). Hosted on GitHub Pages at `https://ltlukoziuzu.github.io/degaline-zemelapis/`.

- `pipeline.py` — server-side script replacing browser-side xlsx parsing and geocoding. Downloads xlsx, parses with openpyxl, geocodes new addresses via Photon, writes `data/stations.json` and updates `data/geocache.json`. Also diffs against previous data and writes daily change logs to `data/logs/` and snapshots to `data/history/`.
- `index.html` rewritten — removed SheetJS, geocoding, and local server dependency. Now simply fetches `data/stations.json` and renders markers.
- `.github/workflows/update.yml` — daily GitHub Actions workflow at 07:00 UTC: runs `pipeline.py`, commits updated data, deploys to Pages. Sends email notification (via Gmail SMTP) when new, removed, or geocoding-changed stations are detected.
- Geocache normalised to stripped address keys (trailing spaces from SheetJS removed).

See [plan-github-migration.md](plan-github-migration.md) for full migration plan.

### Step 10 — Dev verification tool (`dev.html`)

A developer-only page for manually verifying station geocoordinates.

- `dev.html` — same map as `index.html` but with "Teisinga / Neteisinga" buttons in each popup. Marker inner circle turns green/red to reflect per-station verdict. "Kita netikrinta →" toolbar button cycles through unverified groups in order, panning and zooming to each.
- `data/verifications.json` — stores verification state: `"company|||address"` → `"correct" | "incorrect"`. Tracked in git; absent key = unchecked.
- **Save mechanism:** on localhost, POSTs to `server.py` (which now also accepts `POST /data/verifications.json`). On GitHub Pages, PUTs via GitHub Contents API using a fine-grained PAT stored in localStorage. PAT prompt shown on first load; `🔑` toolbar button to update/clear it.
- **CI deploy on push:** `update.yml` now also triggers on `push` to main. `update-data` job is skipped on push events; `deploy` job runs regardless, so any commit to main deploys immediately.
- Verification work is ongoing / deferred to a later date.

### Step 11 — Mobile-first redesign

- `viewport-fit=cover` added for iOS notch / Android edge-to-edge safe area support
- Toolbar restructured to `flex-direction: column` with `.toolbar-main` inner row; ready for additional rows (search already added below)
- Buttons enlarged to `2.5rem` (40px) for proper touch targets
- `ResizeObserver` on `#toolbar` writes `--toolbar-height` CSS var; map `top` tracks it dynamically — toolbar can grow without manual adjustment
- Map `bottom: env(safe-area-inset-bottom, 0)` for iOS home indicator / Android gesture bar
- `env(safe-area-inset-top)` padding on `.toolbar-main` for notch devices
- Status text truncates with ellipsis on narrow screens

### Step 12 (partial) — Search bar

- `.toolbar-search` row added inside `#toolbar` below `.toolbar-main`; `--toolbar-height` auto-adjusts map
- Full-width input with clear (✕) button; `input.blur()` on selection dismisses Android keyboard
- Dropdown (`#search-dropdown`) positioned `fixed` at `top: var(--toolbar-height)`, overlays the map
- Searches company + address + municipality; query split into words, all must match (supports "Circle K Šiauliai")
- Up to 8 results; each shows company bold + address/municipality
- Selecting a result: clears input, blurs, calls `cluster.zoomToShowLayer()` then opens popup
- Keyboard: ↑↓ navigate, Enter select, Esc dismiss
- `mousedown` + `e.preventDefault()` on results prevents blur-before-click race

### Step 13 — Pipeline reliability + versioning

- **Build SHA** stamped into `index.html` at deploy time (`__BUILD_SHA__` → short git commit SHA); shown in about dialog under "Versija:".
- **Data timestamp** (`fetched_at`) written to `stations.json` by `pipeline.py` (UTC ISO with `+00:00` suffix); stamped into `index.html` at deploy as "Naujausi duomenys gauti: YYYY-MM-DD HH:MM" (Vilnius timezone). The `+00:00` suffix is required so `TZ=Europe/Vilnius date -d` correctly converts from UTC rather than treating the value as already-Vilnius time.
- **Date removed from toolbar** status — now shows only station count.
- **Workflow cron changed** from daily 07:00 UTC to every 15 minutes Mon–Fri 06:00–14:45 UTC (≈ 08:00–17:00 Vilnius time), to catch LEA publishing at an unpredictable time during the workday.
- **Early-exit pipeline logic** — implemented. At start of `main()`: if `stations.json` already has today's date, exits immediately. After download: if xlsx date ≠ today (LEA hasn't published yet), exits without touching `stations.json`.
- **Referer header** added to xlsx download requests to mimic a browser referral from `ena.lt/degalu-kainos-degalinese/`.
- **Download diagnosis** — confirmed download failures are timing-only (file not yet published by LEA at time of run); CDN is Cloudflare LAX, no geographic IP block. Pipeline catches the file on a later cron tick once LEA publishes.
- **`getCompanyColor()` helper** — franchise stations named "Foo (Circle K)" automatically inherit the parent brand's color via regex suffix match; used for all marker and panel color lookups.

### Step 14 — Cheapest in radius

- **🎯 toolbar button** enters pick mode — crosshair cursor on desktop, floating hint banner on mobile ("Bakstelėkite vietą žemėlapyje"), button highlights blue
- **Map click** drops a non-clustered crosshair marker at the tapped point and opens the results panel
- **"📍 Rasti pigesnes netoliese"** button injected into every station popup — uses that station as center with company-first rule (same-company cheapest shown first with ⭐ tag, no medals in this mode; plain radius search uses 🥇🥈🥉); price tiebreak by distance
- **Results panel** — bottom sheet on mobile, floating card bottom-right on desktop (media query `pointer: fine` + `min-width: 600px`)
  - Fuel type pills (95 / Dyzelis / Dujos), default 95, persisted in localStorage
  - Radius slider 1–50 km, persisted in localStorage
  - "Rodyti tikrinamą plotą žemėlapyje" checkbox — toggles dashed filled radius circle on map
  - 3 result rows: colored dot, company, address, distance, price; click zooms to station and opens popup
  - 🎯 reposition button inside panel to re-enter pick mode without closing
  - ✕ closes and cleans up all map overlays; Escape key also closes on desktop
- **1.75× oversized non-clustered markers** placed directly on map for the 3 result stations — always visible regardless of zoom/clustering; clicking them opens the station popup
- **Collapsible panel on mobile** — tapping anywhere on the header bar (except ✕) collapses/expands the controls and results; chevron indicator (▾/▸) hidden on desktop

---

## Pending

### Step 12 (remaining) — remaining UI polish and remaining features

1. Address preprocessing for `/` double-street format — still relevant for pipeline.py geocoding runs
2. All errors surfaced in browser UI, never terminal-only — still relevant for hosted version

---

## Known Issues / Decisions

- **Address preprocessing for future geocoding:** Addresses with two streets separated by `/` (e.g. `Beržų g. 24/Drąsiųjų 7, Tryškiai`) were patched manually. `pipeline.py` should strip the second street before querying Photon so future new stations with this format geocode correctly.
- **xlsx format may change** — parser is flexible on header row position but assumes wide 7-column format.
- **Light/dark mode refinement:** Map tiles stay on Voyager in both modes; only UI chrome switches. Could be further polished (popup contrast, cluster colours, etc.) but deferred.
- **Geocache key normalisation:** Keys are now stripped of surrounding whitespace. If ENA ever changes address strings in the xlsx, affected stations will be re-geocoded automatically on the next pipeline run.
- **Node.js 20 deprecation warning** in the deploy job — caused by `actions/upload-pages-artifact@v4` using `actions/upload-artifact@v7` internally. Cannot be fixed from our side; upstream will update before September 2026.
