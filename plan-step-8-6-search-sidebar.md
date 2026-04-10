# Plan: Step 8.6 — Search Field + Sidebar

> **Before testing:** start the local server with `! python3 server.py` from the project directory, then open `http://localhost:58472`.

## Overview

Two linked features sharing the same "selected station" state:
- A fuzzy search field in the toolbar to find a station by address/company
- A persistent right sidebar that activates when a pin is selected

---

## 1. Layout Changes

- Map width: `calc(100% - 15%)` — explicit, not a z-index trick
- Sidebar: `position: fixed; right: 0; top: 0; width: 15%; height: 100%` — always visible, blank when nothing selected
- Minimum sidebar width: `220px` so it stays usable on smaller screens
- Below `500px` viewport width: sidebar hidden entirely (`display: none` via media query), map takes full width
- Sidebar uses same CSS variables as the rest of the UI (light/dark theme already handled)

---

## 2. Search Field

**Placement:** In the toolbar, between the status text and the theme button.

**Input:** Free text. Searches against a flat list of all stations — each entry is `{ address, company, lat, lng, markerRef }`.

**Normalization before matching:**
- Lowercase both query and target
- Strip common Lithuanian address abbreviations: `g.`, `pr.`, `al.`, `k.`, `mstl.`, `r. sav.`, `sav.`
- Collapse multiple spaces

**Matching algorithm:** Substring scoring — check if all query words appear in the target string (order-independent). No library needed. If no word-match, fall back to trigram overlap score. Return top 6 results sorted by score.

**Results dropdown:** Appears below the search field. Each row shows `Company — address`. Click:
1. `map.setView([lat, lng], 11)`
2. Programmatically open the marker popup (`.openPopup()`)
3. Trigger the same "pin selected" handler that populates the sidebar
4. Close the dropdown

**Edge cases:**
- Empty query → hide dropdown
- No results → show "Nerasta rezultatų"
- Click outside dropdown → close it

---

## 3. Sidebar — Structure

```
[ Degalinė: {Company}        ]  ← header, shown when selected
[ {Address}                  ]

[ Kuro tipas: [95▾]          ]  ← fuel type selector (95 / Dyzelinas / Dujos)

[ Spindulys: ──●── 15 km     ]  ← range slider 1–50 km

─────────────────────────────
  Pigiausia — ta pati įmonė
[ {Company} · {address}      ]
[ 1.234 €/L                  ]  ← clickable box

  Pigiausia apylinkėje
[ {Company} · {address}      ]
[ 1.198 €/L                  ]  ← clickable box

  Vidurkis spinduly
  1.247 €/L  (23 degalinės)
─────────────────────────────
```

Blank state (nothing selected): just a thin panel with no content, or a subtle hint "Pasirinkite degalinę".

---

## 4. Sidebar — Data Logic

**Distance:** Haversine formula, ~5 lines of JS. Runs over all 713 stations on every slider change — fast enough with no debouncing.

**Fuel type selector:** Dropdown/segmented control for `95` / `Dyzelinas` / `Dujos`. Filters out stations with `null` for that fuel before ranking. Persists selection across sidebar opens (remember last chosen type in a JS variable).

**Cheapest same-company:** Among stations within radius with the same company as the selected station, lowest price for chosen fuel. If none within radius (or company has only this one station), show "–".

**Cheapest overall:** Lowest price for chosen fuel among all stations within radius. May be the same as the selected station itself.

**Average:** Mean price for chosen fuel across all stations within radius that have a non-null price. Show count.

---

## 5. "Click to highlight" Behaviour (not select)

Clicking a cheapest-station box in the sidebar must NOT trigger the normal pin-click handler (which would replace the sidebar content and break the flow).

Instead:
1. `map.fitBounds([selectedCoords, targetCoords], { padding: [60, 60] })` — zooms out just enough to show both points simultaneously
2. Place a temporary `L.circleMarker` at the target coords: large radius (~20px), accent colour, semi-transparent, with a CSS pulse animation. **Do not open the popup.**
3. Remove the highlight after 4 seconds, or on the next sidebar interaction, whichever comes first
4. The sidebar content stays unchanged throughout

---

## 6. Selection — Unified Handler

Two selection modes share the same sidebar, driven by one function:

```javascript
function selectPoint(lat, lng, station /* or null */) {
  // station present → "pin mode": show company/address header, include same-company cheapest
  // station null   → "map point mode": show "Pasirinktas taškas" header, skip same-company box
}
```

**Triggers:**
- Marker click → `selectPoint(lat, lng, station)`
- Search result click → `selectPoint(lat, lng, station)`
- Map right-click (`map.on('contextmenu')`) → `selectPoint(e.latlng.lat, e.latlng.lng, null)`

**Map point mode sidebar:**
```
[ Pasirinktas taškas         ]  ← header
[ {lat}, {lng}               ]  ← coords, 4 dp

[ Kuro tipas: [95▾]          ]
[ Spindulys: ──●── 15 km     ]

─────────────────────────────
  Pigiausia apylinkėje
[ {Company} · {address}      ]
[ 1.198 €/L                  ]

  Vidurkis spinduly
  1.247 €/L  (23 degalinės)
─────────────────────────────
```
"Cheapest same-company" box is omitted entirely in this mode.

Deselect: left-click anywhere on the map (not a marker) → clear sidebar to blank state.

---

## 7. Implementation Order

1. Layout: add sidebar div, resize map to 85%
2. Blank sidebar with "Pasirinkite degalinę" hint
3. Wire marker click + map right-click → `selectPoint()` → populate sidebar header
4. Fuel selector + radius slider (UI only, no logic yet)
5. Haversine + ranking logic → fill in the three result boxes
6. Highlight behaviour on box click
7. Search field + normalization + dropdown
8. Connect search result → `selectStation()`
9. Polish: dark/light theme for sidebar, mobile-ish minimum width

---

## Open Questions (resolved)

- **Fuel type:** User selects — 95 / Dyzelinas / Dujos dropdown in sidebar. ✓
- **Box click behaviour:** `fitBounds` to show both points + temporary pulse highlight, no selection change. ✓
- **Grouped pins:** All duplicate coordinates were manually patched in Step 6 — every station has unique coords, so `selectStation()` always receives exactly one station. No multi-station disambiguation needed. ✓
