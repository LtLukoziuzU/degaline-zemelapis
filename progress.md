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

## Pending

### Step 8 — UI polish and remaining features

1. ~~Attribution/licensing text for LEA data source in UI + company list generated dynamically from xlsx~~ ✓
2. ~~Marker clustering for dense areas (e.g. Vilnius)~~ ✓
3. ~~Marker colours by fuel type availability~~ ✓ — switched to colour-by-company instead. SVG teardrop pins, each company gets a distinct hex color derived from their brand, small operators (≤3 stations) share grey. Color map in `COMPANY_COLORS` in `index.html`, reference colors in `data/company-colors.txt`.
4. ~~Marker popup styling~~ ✓
5. ~~Persist last map position and zoom level in localStorage (restore on next load)~~ ✓
6. Search field + sidebar — see [plan-step-8-6-search-sidebar.md](plan-step-8-6-search-sidebar.md)
7. Progress bar during geocoding
8. Missing geocache warning before long re-geocoding run begins
9. Address preprocessing for `/` double-street format so future geocoding runs handle it correctly
10. All errors surfaced in browser UI, never terminal-only

### Step 7 — `update.bat` and `update.sh`
Both scripts written and verified. No changes needed after Steps 5–6.
- Step 8 — UI polish: progress bar, popups, marker colours, Lithuanian strings, marker clustering for dense areas (e.g. Vilnius), search field, aggregate list around clicked point in X km radius (show cheapest in that radius with link)
- Step 9 — bundle `lib/` for fully offline use after first setup

## Attribution / Licensing (TODO before handoff)
- **Data source:** LEA — Lietuvos Energetikos Agentūra (https://www.ena.lt/)
- **Primary sources:** the list of gas station companies must be generated dynamically from the current xlsx (companies change as new ones are added or existing ones fix compliance). Do not hardcode the list.
- Credit/attribution text must appear somewhere in the UI (footer or About dialog). Decide on exact wording before handoff.

## Known Issues / Decisions

- **Missing geocache warning:** If `geocache.json` is deleted, a ~60 min re-geocoding run starts without warning. Should show a friendly Lithuanian-language UI warning before the long wait begins.
- **Address preprocessing for future geocoding:** Addresses with two streets separated by `/` (e.g. `Beržų g. 24/Drąsiųjų 7, Tryškiai`) were patched manually this time. Code should strip the second street before querying Photon so future new stations with this format geocode correctly.
- Marker clustering needed for dense cities (deferred to step 8)
- xlsx format may change in future — parser is flexible on header row position but assumes wide 7-column format
- Export/import buttons for geocache no longer needed — server writes physical file directly, same for all browsers
- If user deletes `data/geocache.json`, re-geocoding 714 stations at 5s/address takes ~1 hour. The browser should detect a missing or empty geocache on load and show a clear, friendly warning in the UI before the long wait begins.
- **Light/dark mode refinement:** Map tiles stay on Voyager in both modes; only UI chrome switches. Could be further polished (popup contrast, cluster colours, etc.) but deferred.
- **All errors visible to the end user must appear in the browser, never in the terminal or PowerShell window.** Non-technical users will ignore or panic at terminal output. The bat/sh scripts may use the terminal for developer-facing messages only (download progress, server start). Anything the Windows user might need to act on — missing geocache, failed download fallback, parse errors — must surface as UI in the browser.
