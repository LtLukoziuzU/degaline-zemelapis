## Source Data URL

The official source is published daily by ENA (Energetikos agentūra):
- **Listing page:** `https://www.ena.lt/degalu-kainos-degalinese/`
- **File URL pattern:** `https://www.ena.lt/uploads/{YYYY}-EDAC/dk-degalinese-{YYYY}/dk-{YYYY}-{MM}-{DD}.xlsx`
- **Example (2026-04-09):** `https://www.ena.lt/uploads/2026-EDAC/dk-degalinese-2026/dk-2026-04-09.xlsx`

**Casing inconsistency:** ENA has published files with both `DK-` and `dk-` prefixes (e.g. `DK-2026-04-08.xlsx` vs `dk-2026-04-09.xlsx`). Both casings are tried for each date.

**Date fallback:** Both scripts try today through 4 days ago (5 attempts), both casings each. This covers weekends, single public holidays, and Christmas week edge cases (worst case: Dec 26 falling on a Tuesday after a holiday Monday needs 4 days back). If all 10 attempts fail, a clear error is shown. No weekend or holiday special-casing needed.

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
