# Data Flow

```
update.bat (Windows) / update.sh (Linux)
  └─ Build today's URL (try dk- prefix, fallback to DK-)
  └─ Download xlsx → data/latest.xlsx
  └─ Kill any existing process on port 58472
  └─ Start server.ps1 / server.py on localhost:58472 (background)
  └─ Wait 2 seconds for server to be ready
  └─ Open browser to http://localhost:58472
  └─ Stay alive (server dies when terminal window is closed)

index.html (on load)
  └─ Guard: if protocol is file://, show error and stop
  └─ fetch('/data/geocache.json') → load cache into memory (empty {} if 404)
  └─ fetch('/data/latest.xlsx')  → SheetJS parses → array of station objects
  └─ For each station: check in-memory geocache
       ├─ Cache hit  → use cached { lat, lng, source }
       └─ Cache miss → call Nominatim API (rate-limited 1 req/s) → add to cache
  └─ Every 20 new entries: POST /data/geocache.json → server writes geocache.json
  └─ Place Leaflet marker on map for each station
  └─ Marker popup: company, address, municipality, 95 price, diesel price, LPG price, date

server.ps1 / server.py
  └─ GET  any path     → serve static file from project root
  └─ POST /data/geocache.json → write request body to data/geocache.json
  └─ All other methods → 405
```
