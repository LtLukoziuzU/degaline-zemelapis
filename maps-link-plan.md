# Maps Link Improvement Plan

## Problem

The "Atidaryti žemėlapyje" button currently constructs a raw-coordinate URL that drops a pin with no business name, reviews, or hours. Ideally it opens the actual gas station business card in the user's native maps app.

## Approach

Build the maps URL from existing station data (`company`, `address`, `municipality`, `lat`, `lng`) using platform-specific URL schemes. No API key required.

## URL Schemes by Platform

**iOS** — opens native Apple Maps app via Safari intercept:
```
https://maps.apple.com/?q=COMPANY+ADDRESS+MUNICIPALITY&sll=lat,lng&z=17
```

**Android** — `geo:` URI; Chrome hands off to the user's default maps app (Google Maps, OsmAnd, HERE, etc.):
```
geo:lat,lng?q=COMPANY+ADDRESS+MUNICIPALITY
```

**Desktop** — Google Maps web search anchored to coordinates:
```
https://www.google.com/maps/search/COMPANY+ADDRESS+MUNICIPALITY/@lat,lng,17z
```

## Detection Logic

```js
function mapsUrl(company, address, municipality, lat, lng) {
    const query = encodeURIComponent(`${company} ${address} ${municipality}`);
    const ua = navigator.userAgent;
    if (/iPad|iPhone|iPod/.test(ua))
        return `https://maps.apple.com/?q=${query}&sll=${lat},${lng}&z=17`;
    if (/Android/.test(ua))
        return `geo:${lat},${lng}?q=${query}`;
    return `https://www.google.com/maps/search/${query}/@${lat},${lng},17z`;
}
```

## Fallback Behavior (business not in maps database)

| Platform | Business found | Not found |
|---|---|---|
| iOS (Apple Maps) | Business card | Map centered at `sll=` coords |
| Android (`geo:`) | Business card | Map centered at coords, search results shown |
| Desktop (Google) | Business card | Map zoomed to coords, no pin |

All three degrade gracefully — the coordinates anchor the view even when the text search finds nothing. Small/obscure operators (grey "kita" stations) are most at risk of a miss.

## Implementation Location

`index.html` — the popup-building function that constructs the "Atidaryti žemėlapyje" anchor `href`. A one-function swap, no backend changes needed.

## Coordinate Precision Note

Stored coordinates have 7 decimal places (~1 cm precision). This is more than sufficient — geocoding accuracy is ~10–50 m anyway. No need to change precision when embedding in URLs.
