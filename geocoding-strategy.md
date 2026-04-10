# Geocoding Strategy

- Delay between Nominatim requests: **5000ms**. Intentionally slow — geocache is built once by the developer before handoff, speed is not a concern. See [nominatim.md](nominatim.md) for full config including User-Agent header and 429 retry logic.
- Always append ", Lietuva" to address strings for better accuracy.
- If Nominatim returns no result for a full address, retry with just `municipality + ", Lietuva"` and place marker at municipality center.
- During geocoding, log progress to the browser console (`console.log`) — sufficient for the developer doing the initial cache build. Do not block the UI.
- In the toolbar, show a simple text counter ("Geokóduojama 45/312...") only when geocoding is actually running — i.e. when there are cache misses. This covers the edge case where a Windows user opens the app after new stations were added to the xlsx that aren't yet in the cache. Hide the counter once geocoding is complete.
- Cache entries keyed by address string: `{ lat, lng, source: "address"|"municipality" }`.
- Flush cache (POST to server) after every 20 new entries so progress is not lost if the tab is closed mid-run.

**Cache backend:** All browsers use the same path — `fetch('/data/geocache.json')` to load, `POST /data/geocache.json` to save. The server writes it to disk. No browser-specific code needed.

## Coordinate order

Photon returns GeoJSON coordinates as `[longitude, latitude]` — the opposite of the `{ lat, lng }` order used in the geocache and by Leaflet. When reading coordinates from the Photon response, ensure longitude and latitude are assigned to the correct fields before storing. Verify geocache entries: Lithuanian latitudes are ~54–57, longitudes ~21–26.

## Failed geocode addresses

After two failed Nominatim attempts (full address → municipality fallback), mark the entry in the geocache as `{ source: "failed", lat: null, lng: null }` and skip it — do not retry on every run. Rules:
- Do not place a marker for failed entries.
- The `source: "failed"` entries persist in `geocache.json` so they are not retried on future loads.
- Provide a way to inspect failures: after geocoding completes, log all failed addresses to the browser console as a grouped list (`console.group('Geocoding failures')` / `console.groupEnd()`). This gives a developer or curious user a clear list to cross-check against the xlsx without needing to dig through the full cache file.
- To force a retry on a specific address (e.g. after a confirmed typo fix in ENA's data), the entry must be manually deleted from `geocache.json`.
