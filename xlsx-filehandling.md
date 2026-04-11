## Source Data URL

The official source is published daily by ENA (Energetikos agentūra):
- **Listing page:** `https://www.ena.lt/degalu-kainos-degalinese/`

**Current method (as of ~2026-04-10):** ENA moved files to SharePoint. `pipeline.py` scrapes the listing page and finds all SharePoint URLs containing `/:x:/` (SharePoint's Excel file-type prefix). Two candidates are extracted in document order: the first match is the "Naujausios degalų kainos" banner link above the table (primary); the last match is the rightmost table column (fallback — normally the same URL). The sharing URL has `&download=1` appended to force a direct download. The file date is read from column A of the xlsx itself rather than derived from the URL.

**Re-download on every run:** ENA edits the SharePoint file live throughout the day, and may make a final edit after the last cron tick. The pipeline always re-downloads and re-processes on every cron tick, regardless of the file's date. The git commit step handles idempotency: it only commits if `stations.json` actually changed on disk.

**Fallback:** If scraping finds no SharePoint link, `pipeline.py` falls back to the old direct URL pattern:
- `https://www.ena.lt/uploads/{YYYY}-EDAC/dk-degalinese-{YYYY}/dk-{YYYY}-{MM}-{DD}.xlsx`
- Both `dk-` and `DK-` casings tried; today through 4 days ago (5 attempts each).

**Date fallback rationale:** Covers weekends, single public holidays, and Christmas week edge cases (worst case: Dec 26 falling on a Tuesday after a holiday Monday needs 4 days back). No weekend or holiday special-casing needed.

# xlsx Data Shape

**Format assumption:** ENA has used at least two different layouts since this initiative started (2026-04). The format below (wide, one row per station) was introduced on 2026-04-09 and is treated as the current standard. If a future file breaks parsing, revisit this section.

**Header detection:** Do not hardcode the header row number — it varies between files. Scan rows top-to-bottom for the first row where column A equals `'Data'`; that is the header. Data begins on the next row.

**Confirmed column map (as of 2026-04-09):**

| Index | Header (Lithuanian) | Description | Type |
|---|---|---|---|
| 0 | `Data` | Price validity date | String `'2026 04 09'` (spaces, not dashes) |
| 1 | `Įmonė (Degalinių tinklas)` | Gas station company/brand | String |
| 2 | `Degalinės vieta (Savivaldybė)` | Municipality | String e.g. `'Utenos r. sav.'` |
| 3 | `Degalinės vieta (Gyvenvietė, gatvė)` | Full address | String |
| 4 | `95 benzinas` | 95 octane petrol price, €/L | Float or `'neprekiauja'` |
| 5 | `Dyzelinas` | Diesel price, €/L | Float or `'neprekiauja'` |
| 6 | `SND` | LPG (autogas) price, €/L | Float or `'neprekiauja'` |

**"Not sold" value:** The string `'neprekiauja'` (case may vary). Always check `isinstance(value, float)` before using a price cell as a number — never assume a non-`None` cell is numeric.
