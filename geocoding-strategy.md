# Geocoding Strategy

All geocoding runs in `pipeline.py` server-side (GitHub Actions or local). The browser never geocodes.

- **Provider:** Photon (photon.komoot.io) — no API key required, good Lithuanian address support.
- **User-Agent:** `degaline-map/1.0 (LtLukoziuz+degaline@gmail.com)` — required by Photon's fair-use policy.
- **Delay:** 5000ms between requests (`GEOCODE_DELAY`). Geocache is built once per new address — speed is not a concern.
- **Query format:** Always append `", Lietuva"` to address strings for better accuracy.
- **Address preprocessing:** Strip secondary street references before querying — e.g. `Beržų g. 24/Drąsiųjų 7, Tryškiai` → `Beržų g. 24, Tryškiai`. Photon cannot resolve dual-street format.
- **Cache key:** Raw address string stripped of surrounding whitespace (as read from xlsx). Preprocessing only affects the Photon query, not the key.

## Fallback logic

1. Query Photon with `"address, Lietuva"` (preprocessed)
2. If no result → wait 5s → retry with `"municipality, Lietuva"` (municipality centre fallback)
3. If still no result → mark as `{ source: "failed", lat: null, lng: null }` — no retry on future runs
4. Failed entries are skipped when building `stations.json` (no marker placed)
5. To force a retry: manually delete the entry from `geocache.json`

## 429 handling

On HTTP 429 (rate limit): wait 10s, retry. If still 429: wait 20s, retry. If still failing: return None (triggers fallback logic above).

## Cache format

```json
{
  "Didžioji g. 1, Vilnius": { "lat": 54.6872, "lng": 25.2797, "source": "address" },
  "Aleksoto k.":            { "lat": 54.8833, "lng": 23.9167, "source": "municipality" },
  "Nežinoma g. 99":         { "lat": null,    "lng": null,    "source": "failed" }
}
```

## Coordinate validation

Photon returns GeoJSON coordinates as `[longitude, latitude]`. When reading, assign correctly — longitude is NOT latitude. Lithuanian latitudes: ~54–57, longitudes: ~21–26. Results outside this bounding box are likely wrong-country results and should be treated as failures.

## Flush timing

`pipeline.py` flushes `geocache.json` to disk every `FLUSH_EVERY` (20) newly geocoded entries, and once more at the end. This preserves progress if the process is interrupted mid-run.
