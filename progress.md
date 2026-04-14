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
- **Early-exit pipeline logic removed** — all date-based skips dropped. ENA edits the SharePoint file live throughout the day (and potentially after the last cron tick), so every run re-downloads and re-processes whatever is currently in the file, regardless of its date. The git commit step skips committing if `stations.json` is byte-for-byte unchanged on disk.
- **Referer header** added to xlsx download requests to mimic a browser referral from `ena.lt/degalu-kainos-degalinese/`.
- **Download diagnosis** — confirmed download failures are timing-only (file not yet published by LEA at time of run); CDN is Cloudflare LAX, no geographic IP block. Pipeline catches the file on a later cron tick once LEA publishes.
- **`getCompanyColor()` helper** — franchise stations named "Foo (Circle K)" automatically inherit the parent brand's color via regex suffix match; used for all marker and panel color lookups.

### Step 12 (remaining) — UI polish

- **Address preprocessing for `/` double-street format:** `pipeline.py` now strips the secondary street reference (e.g. `Beržų g. 24/Drąsiųjų 7` → `Beržų g. 24`) before querying Photon. Cache key remains the original address string.
- **Browser error handling:** no action needed — geocoding is server-side only; all realistic browser failure paths (`file://`, fetch failure) already show friendly Lithuanian UI errors.

### Step 14 — Cheapest in radius

- **🎯 toolbar button** enters pick mode — crosshair cursor on desktop, floating hint banner on mobile ("Bakstelėkite vietą žemėlapyje"), button highlights blue
- **Map click** drops a non-clustered crosshair marker at the tapped point and opens the results panel
- **"📍 Rasti pigesnes netoliese"** button injected into every station popup — uses that station as center with company-first rule (same-company cheapest shown first with ⭐ tag, no medals in this mode; plain radius search uses 🥇🥈🥉); price tiebreak by distance
- **Results panel** — bottom sheet on mobile, floating card bottom-right on desktop (media query `pointer: fine` + `min-width: 600px`)
  - Fuel type pills (95 / Dyzelis / Dujos), default 95, persisted in localStorage
  - Radius slider 1–50 km (resets to 5 km on each new center — see Step 16)
  - "Rodyti tikrinamą plotą žemėlapyje" checkbox — toggles dashed filled radius circle on map
  - 3 result rows: colored dot, company, address, distance, price; click zooms to station and opens popup
  - 🎯 reposition button inside panel to re-enter pick mode without closing
  - ✕ closes and cleans up all map overlays; Escape key also closes on desktop
- **1.75× oversized non-clustered markers** placed directly on map for the 3 result stations — always visible regardless of zoom/clustering; clicking them opens the station popup
- **Collapsible panel on mobile** — tapping anywhere on the header bar (except ✕) collapses/expands the controls and results; chevron indicator (▾/▸) hidden on desktop
- **Bug fix:** collapse click handler now checks `getComputedStyle` on `#rp-chevron` — no-ops on desktop where chevron is `display:none`
- **Bug fix:** map click in pick mode now always passes `null` as `fromStation` — manual repositioning always produces generic top-3, never company-biased results

### Step 16 — GPS locate-me button + radius UX polish

- **📍 locate-me button** — fixed bottom-left corner, circular, accent-coloured; visually distinct from all other controls
  - Tries `navigator.geolocation` first (GPS, zoom 14, no toast); on any failure falls back to `ipwho.is` was tried but requires paid CORS plan → switched to **`ipinfo.io`** (free, HTTPS, CORS, 50k req/month); parses `loc` field (`"lat,lng"` string)
  - IP fallback zooms to 11 and shows toast "Apytikslė vieta (pagal IP adresą.)"
  - Spinner SVG shown while waiting; button re-enables on success or error
  - Button always present (ipinfo.io fallback means even browsers without Geolocation API benefit)
- **Mobile panel-push** — button slides up by `panel.offsetHeight + 12px` whenever panel has `open` class (covers both expanded and collapsed-header states); desktop unaffected; `syncLocateBtn()` called after source tag appears to account for its added height
- **Mobile centering fix** — projects `latlng` to pixel space, shifts south by `panel.offsetHeight / 2`, unprojects back to `setView` target; avoids the animation-override bug of the earlier `panBy` approach
- **Radius resets to 5 km** on every new center pick (map click, popup button, or locate-me); localStorage persistence for radius removed — user decides each time
- **Medal fixes:**
  - Locate-me was getting no medals (bug: `fromStation = 'gps'` is truthy); fixed by checking `typeof fromStation === 'object'`
  - Station-popup mode now shows 🥇🥈 for positions 2 and 3 (same-company first result keeps its ⭐ tag, no medal)
- **Source tag** — thin muted line between panel header and controls; always shown when panel is open:
  - Map click → "Pagal pasirinktą tašką"
  - Popup button → "Pagal pasirinktą degalinę"
  - Locate GPS → "Tiksli vieta (GPS)"
  - Locate IP → "Apytikslė vieta (pagal IP adresą)"
  - Hidden when panel is collapsed; cleared on each new center pick then overridden by source
- **Icon consistency** — toolbar radius button and in-panel reposition button now use the same pin+arcs SVG; locate-me uses GPS crosshair SVG; all three are visually distinct to first-time visitors
- **Mobile close UX** — ✕ button gets larger padding/font on touch screens; reposition button pushed left with `margin-right` to avoid accidental close taps
- **Small operator pin color** changed from mid-grey `#9ca3af` to dark near-black `#3d3d3d` — visible on light tiles, neutral grey (no blue cast) keeps it distinct from Skulas (`#1f2937`)
- **Locate-me button** hardcoded to `#2563eb` instead of `var(--accent)` — stays vivid blue in dark mode where accent fades to `#89b4fa`

### Step 15 — Dark mode tile filter

- CSS `filter` applied to `.leaflet-tile-pane` in `html.dark`: `brightness(0.65) saturate(0.6) hue-rotate(190deg) contrast(1.1)`
- Dims and desaturates Voyager tiles, then hue-rotates warm beige/green tones toward cool blue-grey — similar feel to Google Maps dark mode
- No tile URL change, no API key, works offline; one CSS rule

### Step 17 — Licensing, theme detection, about dialog polish

- **MIT License** added (`LICENSE` file in repo root); GitHub auto-detected and displays it in the repo sidebar.
- **System theme detection** — first-time visitors no longer default to dark mode unconditionally; `window.matchMedia('(prefers-color-scheme: dark)')` is used when no `degaline-theme` key exists in localStorage. Returning visitors still get their last manually chosen theme.
- **Geocoding accuracy note** added to the about dialog — explains that coordinates are Photon-generated and may occasionally be imprecise; notes the verification tool exists to address this over time.
- **Company list collapsed by default** — the list of gas station networks in the about dialog is now hidden under a `<details>`/`<summary>` spoiler block to reduce visual noise on open.

### Step 18 — Search persistence, share link, and related fixes

- **Last search persisted in localStorage** (`degaline-search`: lat, lng, radiusKm, source) — restored automatically on next visit with the same radius and source context. Cleared when user explicitly closes the panel with ✕, so only "left-open" searches are restored.
- **Share link button** (chain icon, `#rp-share`) added to panel header — copies a URL with `?lat=…&lng=…&r=…&z=…&f=…` to clipboard via `navigator.clipboard`; shows "Nuoroda nukopijuota!" toast on success (reuses `#locate-toast`).
  - Fuel type encoded as short aliases: `95` / `dyz` / `snd` (receiving end also accepts `lpg` → LPG).
  - On open: URL params take priority over localStorage saved search; lat/lng snapped to nearest station within 30 m → station-based search with correct company-first medals; params stripped from address bar via `history.replaceState` after apply.
  - Mobile centering fix applied — `requestAnimationFrame` defers `map.setView` with panel-offset adjustment to after the browser's first layout pass (panel height is 0 during synchronous init).
- **Panel button spacing fixed on mobile** — `margin-right` moved from `#rp-reposition` to `margin-left` on `#rp-share`; all three icon buttons now have uniform gaps.
- **Geocache collision investigated** — `Gegužių g. 28, Šiauliai` (Neste) and `Gegužių g. 28` (Plovimo sistemos) share coordinates; confirmed intentional (two separate businesses at the same address). No action taken.

### Step 19 — Company logo processing for custom map pins

- Sourced logo images for all companies into `originallogo/` (gitignored). Photo-based logos (real-world station photos) scrapped — those companies fall back to default pin.
- `process_logos.py` — resizes and crops each logo to a 256×256 circle PNG with transparent exterior; no color changes.
- `make_circleextend.py` — detects each logo's background color and fills the full circle with it, removing artifact black corners left by the putalpha approach. Auto-detection worked for ~24 of 34 logos; 10 required manual fixing (black text removal issues, color quantization mismatches, transparent-bg logos).
- Final output in `goodlogo/` — one `{company}.png` per company, ready for use as map pins.
- Full strategy, decisions, and manual fix log documented in [logo-processing.md](logo-processing.md).

### Step 20 — Company logo map pins and UI integration

- Teardrop pins replaced with logo-embedded teardrops: white disk (r=8 in 24-unit viewBox) behind each logo so light/white content reads regardless of teardrop color. No-logo companies keep the plain teardrop with white semi-transparent circle. Old teardrop code retained for easy revert.
- `LOGO_MAP` in `index.html` maps company name strings to `goodlogo/` filenames; Circle K franchisees matched via `/circle\s*k/i` regex.
- Plovimo sistemos has no logo (shares address with Neste); grouped pins prefer the first logo-having company in the group regardless of data order.
- Pin size: 36×54 px normal (3:4 ratio, logo ~40px); result panel markers same size but not clustered.
- Company logo shown in station popup (above name) and in radius panel result rows (2.8rem square, between medal and text).
- Post-processing fixes to `goodlogo/`: emsi/pynauja/stateta transparent interiors → white; melkasta black background → white; jozita/naftrus/neste/RV/utentra marks expanded and re-centered; circlek/orlen/viada marks expanded (red border preserved for CK/Viada); orlen nudged up 12px to compensate for text-heavy bottom.
- Cluster radii tightened: zoom ≤10 → 70px, 11–13 → 60px, ≥14 → 40px.
- Attribution note added to company list spoiler in about dialog: "Įmonių logotipai paimti iš viešai prieinamų duomenų."

### Step 21 — Pin location audit and mass correction

- **`check_pins.py`** — new script that compares each station's coordinates against its declared municipality's centroid (hardcoded table of 60 Lithuanian municipalities with radius thresholds). Outputs `check_pins_report.txt` sorted by worst offender, with Google Maps links per entry.
- **32 suspicious pins flagged**, manually reviewed by opening each Maps link. 31 confirmed wrong (geocoder resolved ambiguous bare addresses to the wrong city); 1 (Alauša / Laisvės pr. 125A, Vilnius) confirmed correct pin with only a wrong municipality field in LEA source data.
- **`data/stations.json` and `data/geocache.json`** updated with corrected coordinates for all 31 entries; geocache entries marked `source: "manual"`.
- **`data/verifications.json`** extended to 58 entries: the 3 pre-existing manual verifications + 32 check_pins entries + 23 previously manually geocoded addresses from `manual-geocache-addresses.md`.

### Step 22 — "Open in Maps" button in popups

- **Both `index.html` and `dev.html`** — new button in each station popup: red filled button with white pin SVG icon.
  - `index.html`: appears above "Rasti pigesnes netoliese"; visually distinct (solid red vs. outlined blue) so external-link intent is clear without hovering.
  - `dev.html`: appears below Teisinga/Neteisinga buttons; muted style appropriate for dev tooling.
- **Platform-aware URL** (`mapsUrl()` helper, detected once at load):
  - Android → `geo:0,0?q=lat,lng` (opens system maps chooser, drops a pin)
  - iOS → `https://maps.apple.com/?q=lat,lng` (opens Apple Maps app with pin)
  - Desktop → `https://www.google.com/maps?q=lat,lng` (Google Maps web)
- **Label** — "Atidaryti žemėlapyje" on Android/iOS; "Atidaryti Google Maps" on desktop.
- **`color: #ffffff !important`** required to override browser UA stylesheet link color on the `<a>` element.

### Logo fixes (post Step 20)

- **Trevena** — original is a 150×34 px wide banner (4.5:1 ratio); rebuilt circle at 82% width fill on yellow background.
- **Boostpetrol** — mark was only 39% fill; cropped from original JPEG, scaled to 72% fill on navy `(0,55,117)` background.

### Step 23 — Maps link improvement, price tooltips on pins, Pastaba update

- **"Atidaryti žemėlapyje" improved** — `mapsUrl()` now accepts `company`, `address`, `municipality` and builds a business-search URL per platform: Android `geo:lat,lng?q=...`, iOS `maps.apple.com/?q=...&sll=...&z=17`, Desktop `google.com/maps/search/?api=1&query=...`. Opens business card instead of bare coordinate pin.
- **Price tooltip on every unclustered pin** — permanent Leaflet tooltip above each map pin showing the selected fuel's price (`1.299 €/L`) or `nėra` if unavailable. Adapts to light/dark mode via CSS vars; 2px border (black/white) for contrast. Applies to both cluster markers and cheapest-in-radius result markers.
- **Default fuel type changed to Dyzelinas** — first-time visitors see diesel prices by default (was 95); persisted in localStorage as before.
- **Fuel type selection updates all tooltips** — switching fuel type in the radius panel immediately refreshes all visible pin labels.
- **Pastaba text updated** in the about dialog with corrected geocoding error breakdown.
- **`company-color-review.md`** created — plain list of all 49 companies from `stations.json` for manual color/logo background review.

### Step 24 — Pin color overhaul and dark mode overlay fixes

- **Full `COMPANY_COLORS` rewrite** — all 34 named companies now use brand-accurate hex colors sourced from logo review (`company-color-review.md`). 14 additional companies added that were previously falling through to small-operator grey. GM Circle K entry removed — Circle K franchises now handled entirely by the existing regex.
- **Hue spreading for white-background logos** — companies whose logos have white backgrounds (where the teardrop color is the sole differentiator) had hues slightly spread within each color cluster to improve map readability: oranges, ambers, yellows, and blues each shifted 5–13° apart. Dark greens (Gazimpeksas, Pynauja, Emsi, Jozita) brightened instead of hue-shifted (too dark/desaturated for hue shifts to matter visually), at half the initially computed brightening after visual review.
- **Skulas and Stateta** switched to alt colors: Skulas `#201d1d` (near-black) and Stateta `#f5821f` (orange), avoiding the all-red cluster.
- **Dark mode crosshair marker** — white halo strokes drawn behind the accent-colored lines so the center marker is visible on dark-filtered tiles.
- **Dark mode radius circle** — uses `#60a5fa` (vivid blue) instead of the pale `#89b4fa` accent; weight bumped to 2px; fill opacity 0.10 vs 0.08 in light mode.

### Step 25 — Fuel type selector in toolbar + map center fix

- **Map center corrected** — default `setView` lat moved from `55.913` → `55.2`; first-time visitors now see Lithuania centred without Latvia bleeding into the top of the viewport.
- **Fuel type selector moved to toolbar** — three buttons (`95`, `Dyzelinas`, `Dujos`) added as a persistent row below the search input. On mobile: full-width flex row, each button `flex: 1`. On desktop: buttons are auto-width and share the same row as the search input (`.toolbar-second-row` flex container).
- **`setActiveFuel(type)`** introduced as the single function for all fuel-type changes — updates `activeFuel`, persists to localStorage, syncs button active states, refreshes price tooltips, dispatches `fuelchange` custom event. All prior duplicate sync code (URL restore, panel buttons) replaced with calls to this function.
- **Radius panel decluttered** — fuel type row (`Kuras:` label + pills) removed; reposition pin-drop button removed from panel header (toolbar button already serves this purpose). Panel now shows only radius slider and circle-toggle checkbox.

### Step 26 — Deploy pipeline bug fix + Circle K franchisee normalisation

**Bug: GitHub Pages never redeployed after scheduled pipeline runs**

- Root cause: `deploy` job condition checked `needs.update-data.outputs.data_changed == 'true'`, but `update-data` had no `outputs:` block and the commit step never wrote to `$GITHUB_OUTPUT`. Output was always empty → deploy always skipped after scheduled runs. Pages only redeployed on `push` events (where `update-data` is `skipped`, satisfying the other branch of the condition).
- Fix in `.github/workflows/update.yml`: added `outputs: data_changed` to the `update-data` job; added `id: commit` to the commit step; emit `data_changed=true/false` to `$GITHUB_OUTPUT` based on whether `git diff --staged --quiet` found changes.
- Symptom: site showed `Naujausi duomenys gauti: 2026-04-10 13:15` even after a pipeline run that sent a change-notification email (12 new stations, 1 removed on 2026-04-13).

**Circle K franchisee normalisation**

- ENA xlsx listed one new station as `S.Savicko įmonė (Circle K)` — a franchisee string. Pipeline emitted it verbatim, so it would appear as a grey small-operator pin instead of using the Circle K colour/logo.
- Added `COMPANY_ALIASES` dict to `pipeline.py` (constants section). Substring match: any company name containing a key is replaced with the alias value. First entry: `'(Circle K)' → 'Circle K'`. Applied at xlsx parse time so the raw ENA string never reaches `stations.json`.

### Design decisions

- Substring match (not exact) for `COMPANY_ALIASES` — franchisee names follow pattern `Franchisee (Brand)`, so matching the parenthetical is robust to future operators with different names.
- `next(..., raw_company)` as fallback — one-liner, no branch, leaves unmatched names untouched.

### Known rough edges

- `COMPANY_ALIASES` is a silent transform — the change log/email will show `Circle K` for a station ENA lists under a different name. If the raw ENA name is ever needed for auditing, the mismatch could confuse.
- AS 24 Lietuva at Europos g. 17, Salaperaugio k. co-locates with Alauša at the exact same address with different diesel prices (2.209 vs 2.159). Intentional — AS 24 is a fleet card network with separate pricing. Two pins will stack at identical coords.

### Full project review (post Step 26)

Reviewed all project files (index.html, dev.html, pipeline.py, server.py, check_pins.py, process_logos.py, make_circleextend.py, update.yml). Three fixes applied:

- **pipeline.py:** removed dead `today` variable (leftover from Step 13 early-exit removal) and removed unused `data_changed=true` output from `compare_and_log()` — only the commit step's `data_changed` is consumed by the workflow; having both was confusing.
- **dev.html:** replaced `toB64()` spread operator (`String.fromCodePoint(...bytes)`) with chunked approach (`Array.from`) — the spread would hit stack overflow at ~750 verification entries.

dev.html color/center/maps drift noted but not fixed (deliberately low-priority temporary tool). index.html single-file architecture (~1390 lines) noted as approaching the threshold but not worth splitting yet — no build step is a genuine feature.

### Data audit (2026-04-14)

Cross-checked local `stations.json`, GitHub `stations.json`, and a fresh pipeline run against the live ENA SharePoint file. All three sources agree on station count (736) and prices.

**Two email notifications explained:**
- **2026-04-13** — 3 Circle K franchisee renames (VVARFF, Plungės lagūna, S.Savicko įmonė → Circle K). Same physical stations, same coords, same prices. `COMPANY_ALIASES` from Step 26 handled these correctly.
- **2026-04-14** — 3 station address/name changes (Baltic Petroleum address reformatted, Nostrada → Nostrada (RV Transport), Autograndas Taikos pr. 48 → 47) + 592 price changes across all companies.

**Autograndas geocache fix:**
- ENA renamed the address from "Taikos pr. 48" to "Taikos pr. 47" (Visaginas). The old entry had `source: "manual"` coords (55.591, 26.463 — correctly in Visaginas). The new address was auto-geocoded by Photon to 55.697, 21.151 — a "Taikos pr. 47" in Klaipėda, 300 km away on the wrong side of the country.
- Fix: set "Taikos pr. 47" geocache entry to the same manual Visaginas coords as the old "Taikos pr. 48", with `source: "manual"`. Updated both `geocache.json` and `stations.json`.

**Floating point precision (pre-existing, cosmetic):**
- ~100 Baltic Petroleum and Orlen prices have float artifacts (e.g. `1.7389999999999999` instead of `1.739`). All display correctly with 3-decimal formatting in the UI. Root cause is xlsx cell value parsing in openpyxl — not new today.

**Summary row parsed as station (pre-existing, harmless):**
- xlsx footer row "Duomenys: 54 įmonės, 736 degalinės" is parsed as a station row. Geocoding fails (no valid address), so it never reaches `stations.json`. Pipeline logs the failure but continues.

---

## Pending

---

## Known Issues / Decisions

- **Mobile panel height / scrollable results:** Results are currently capped at 3 to avoid the panel growing too tall. To show more (top 5, 10, or all in radius), the panel needs a max-height constraint (~50% viewport) and `#rp-results` made `overflow-y: scroll`, otherwise results would push off-screen on mobile.

- **SharePoint layout — verified 2026-04-14:** ENA SharePoint scraping confirmed working on Monday 2026-04-14. `/:x:/` regex + `matches[0]` correctly downloaded the current day's file. No page restructuring observed.
- **xlsx format may change** — parser is flexible on header row position but assumes wide 7-column format.
- **Light/dark mode refinement:** Tile filter applied (Step 15). Popup contrast addressed via CSS variables. Cluster colours unchanged by design.
- **Geocache key normalisation:** Keys are now stripped of surrounding whitespace. If ENA ever changes address strings in the xlsx, affected stations will be re-geocoded automatically on the next pipeline run.
- **Node.js 20 deprecation warning** in the deploy job — caused by `actions/upload-pages-artifact@v4` using `actions/upload-artifact@v7` internally. Cannot be fixed from our side; upstream will update before September 2026.
- **index.html single-file split plan:** Currently ~1390 lines. No action needed yet. When it grows:
  - **~2500 lines:** Extract JS into `app.js` (plain `<script src>`, no bundler). Gets proper editor symbol nav and jump-to-definition.
  - **~3000+ lines or 3+ independent UI panels:** Extract CSS into `style.css` too. CSS specificity conflicts become real at that scale.
  - **Never:** Don't introduce a bundler or framework. `index.html` + `style.css` + `app.js` via plain tags keeps zero-build-step deployment.
  - The real trigger is when you're scrolling past 3+ unrelated sections to edit two related things — that's when the single file costs time instead of saving it.
