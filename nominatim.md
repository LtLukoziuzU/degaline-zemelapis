# Nominatim Configuration

## User-Agent

All requests to Nominatim must include a descriptive `User-Agent` header per their ToS:

```
User-Agent: degaline-map/1.0 (LtLukoziuz+degaline@gmail.com)
```

Add this to every `fetch()` call made to `nominatim.openstreetmap.org`.

## Rate limiting

- **Delay between requests:** 5000ms (5 seconds). Intentionally conservative — geocache is built once by the developer before handoff, so speed does not matter.
- **429 handling:** If a 429 is received, wait 10s and retry. If it fails again, wait 20s and retry once more. If it still fails, mark as `{ source: "failed" }` and move on.

## Address format

Always query as: `"${address}, Lietuva"`

Fallback (if no result): `"${municipality}, Lietuva"`

If fallback also fails: mark as `{ source: "failed", lat: null, lng: null }` in geocache.
