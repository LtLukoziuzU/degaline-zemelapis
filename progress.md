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

---

## Pending

### Step 8 (remaining) — UI polish and remaining features

6. Search field + sidebar — **needs mobile-first redesign before implementation**; desktop-only plan in [plan-step-8-6-search-sidebar.md](plan-step-8-6-search-sidebar.md) is superseded
7. Progress bar during geocoding — no longer relevant (geocoding is server-side)
8. Missing geocache warning — no longer relevant (geocache managed by pipeline.py)
9. Address preprocessing for `/` double-street format — still relevant for pipeline.py geocoding runs
10. All errors surfaced in browser UI, never terminal-only — still relevant for hosted version

### Step 10 — Mobile-first redesign
Full UI redesign for mobile compatibility before implementing remaining features (search/sidebar). Viewport meta tag already added. Key items:
- Toolbar layout on narrow screens (search field won't fit in current single row)
- Sidebar replaced with bottom drawer pattern on mobile
- Touch alternative for right-click (map point mode)
- iOS safe-area insets for map bottom edge

---

## Attribution / Licensing (TODO before handoff)
- **Data source:** LEA — Lietuvos Energetikos Agentūra (https://www.ena.lt/)
- **Primary sources:** the list of gas station companies must be generated dynamically from the current xlsx (companies change as new ones are added or existing ones fix compliance). Do not hardcode the list.
- Credit/attribution text must appear somewhere in the UI (footer or About dialog). Decide on exact wording before handoff.

---

## Known Issues / Decisions

- **Address preprocessing for future geocoding:** Addresses with two streets separated by `/` (e.g. `Beržų g. 24/Drąsiųjų 7, Tryškiai`) were patched manually. `pipeline.py` should strip the second street before querying Photon so future new stations with this format geocode correctly.
- **xlsx format may change** — parser is flexible on header row position but assumes wide 7-column format.
- **Light/dark mode refinement:** Map tiles stay on Voyager in both modes; only UI chrome switches. Could be further polished (popup contrast, cluster colours, etc.) but deferred.
- **Geocache key normalisation:** Keys are now stripped of surrounding whitespace. If ENA ever changes address strings in the xlsx, affected stations will be re-geocoded automatically on the next pipeline run.
- **Node.js 20 deprecation warning** in the deploy job — caused by `actions/upload-pages-artifact@v4` using `actions/upload-artifact@v7` internally. Cannot be fixed from our side; upstream will update before September 2026.
