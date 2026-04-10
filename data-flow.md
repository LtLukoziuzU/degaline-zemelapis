# Data Flow

```
GitHub Actions (update.yml — every 15 min Mon–Fri 06:00–14:45 UTC)
  └─ Run pipeline.py
       ├─ Early-exit if stations.json already has today's date
       ├─ Download xlsx from ena.lt → data/latest.xlsx
       ├─ Early-exit if xlsx date ≠ today (LEA hasn't published yet)
       ├─ Parse xlsx with openpyxl → list of station dicts
       ├─ Geocode new addresses via Photon (5s delay between requests)
       │    ├─ Cache hit  → use cached { lat, lng, source }
       │    ├─ Cache miss → query Photon with "address, Lietuva"
       │    │    ├─ Success → cache[address] = { lat, lng, source: "address" }
       │    │    └─ Fail   → retry with municipality fallback
       │    │         ├─ Success → cache[address] = { lat, lng, source: "municipality" }
       │    │         └─ Fail   → cache[address] = { lat: null, lng: null, source: "failed" }
       │    └─ Flush geocache every 20 new entries + at end
       ├─ Write data/stations.json  { date, fetched_at, stations: [...] }
       ├─ Write data/geocache.json
       ├─ Diff against previous stations.json → write data/logs/<date>.txt
       ├─ Write snapshot to data/history/<date>.json
       └─ Send email if stations changed (new/removed/geocode-changed)
  └─ git commit data/stations.json data/geocache.json data/logs/ data/history/
  └─ Deploy to GitHub Pages

Browser (index.html on load)
  └─ Guard: if protocol is file://, show error and stop
  └─ fetch('data/stations.json') → parse station list
  └─ Place clustered Leaflet markers for each station
  └─ Marker popup: company, address, municipality, prices (95/diesel/LPG)
  └─ Features: search bar, cheapest-in-radius picker, about dialog, dark/light mode

Local dev (developer only)
  └─ python3 pipeline.py   → generates data/stations.json + updates data/geocache.json
  └─ python3 server.py     → serves static files on localhost:58472
  └─ Open http://localhost:58472 in browser

server.py (local dev)
  └─ GET  any path                  → serve static file from project root
  └─ POST /data/geocache.json       → write request body to data/geocache.json
  └─ POST /data/verifications.json  → write request body to data/verifications.json
```
