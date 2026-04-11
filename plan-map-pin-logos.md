# Plan: Replace Map Pins with Company Logos

## Goal

Replace the current SVG teardrop pins in `index.html` with the circular logo images from `goodlogo/`. Clusters remain unchanged (Leaflet.markercluster handles those).

## Logo Files

`goodlogo/` contains 34 files named `{company}.png` (256×256 px, circular, transparent exterior). These are committed to the repo and served by GitHub Pages.

## Company → Logo Mapping

Company names in `stations.json` do not always match `goodlogo/` filenames directly (Lithuanian characters, spaces, punctuation). An explicit lookup table is needed in `index.html`. Draft:

```js
const LOGO_MAP = {
  'Adukesta':                          'adukesta',
  'Alauša':                            'alausa',
  'Apsaga':                            'apsaga',
  'Baltic Petroleum':                  'balticpetroleum',
  'Boost Petrol':                      'boostpetrol',   // branded "abromika" on logo
  'Borusta':                           'borusta',
  'Circle K':                          'circlek',
  'Degta':                             'degta',
  'Deliuvis':                          'deliuvis',
  'Emsi':                              'emsi',
  'Gazimpeksas':                       'gazimpeksas',
  'Gelvybė':                           'gelvybe',
  'Jozita':                            'jozita',
  'Junasa':                            'junasa',
  'Melkasta':                          'melkasta',
  'Naftrus':                           'naftrus',
  'Narjanta':                          'narjanta',
  'Neste Lietuva':                     'neste',
  'Nostrada':                          'nostrada',      // "RV Transport" on logo
  'Orlen':                             'orlen',
  'Plovimo sistemos':                  'neste',         // shares address with Neste Lietuva — use Neste logo
  'Propano ir butano dujų centras':    'propanoirbutanodujucentras',
  'Pynauja':                           'pynauja',
  'Regusa':                            'regusa',
  'RV':                                'RV',
  'Saurida':                           'saurida',
  'Skulas':                            'skulas',
  'Stateta':                           'stateta',
  'Šventosios investicijos':           'sventosiosinvesticijos',
  'Tomega':                            'tomega',
  'Trevena':                           'trevena',
  'Utentra':                           'utentra',
  'Velseka':                           'velseka',
  'Viada':                             'viada',
  'Virši':                             'virsi',
};
```

Companies verified against `stations.json`. The following companies are in the data but have no logo — they fall back to the default pin: `Antivis`, `Atsiauta`, `Autograndas`, `Eniris`, `Eu Verslas`, `Madalva`, `Pakelės namai`, `Prie Luksto`, `Skaistčio ŽŪB`, `Tumasa`, `Žibalas`.

## Special Cases

### Circle K Franchisees
Several companies are Circle K franchise stations and include "Circle K" in their name (e.g. "Foo (Circle K)"). All should use `circlek.png`. The `getCompanyColor()` helper already handles this via regex suffix match — the same pattern should apply to logo lookup:

```js
function getCompanyLogo(company) {
  if (/circle\s*k/i.test(company)) return 'circlek';
  return LOGO_MAP[company] || null;
}
```

Return `null` → fall back to current SVG teardrop pin.

### Plovimo sistemos + Neste at the same address
These two companies share identical coordinates (Gegužių g. 28, Šiauliai — confirmed intentional, two businesses at same address). Their stations are combined into one popup. For the pin icon, only Neste has a logo. Since the pin represents a grouped location, use the Neste logo. Implementation: when building the icon for a group of stations at the same coordinates, pick the first company in the group that has a logo entry; if none, fall back to the default pin.

### Companies Without Logos
Companies not present in `goodlogo/` (photos scrapped, logos not found online, etc.) keep the existing colored SVG teardrop pin using `COMPANY_COLORS`. No visual change for those.

## Display Size

- Normal pins: suggest **40×40 px** display size (Leaflet `iconSize: [40, 40]`)
- Oversized result pins (radius panel top-3): suggest **70×70 px** (`iconSize: [70, 70]`)
- Anchor: center of circle (`iconAnchor: [half, half]`) — unlike teardrops which anchor at the tip, circles look better anchored at center

## Implementation Notes

- Preload / cache Leaflet `L.icon` instances keyed by logo name — don't recreate the same icon object for every marker.
- The logo PNGs already have transparent exteriors, so they'll display as clean circles over the map tiles with no additional clipping needed.
- Popup anchor (`popupAnchor`) should be adjusted — for a 40px circle, `[0, -20]` (above center) is reasonable.
- Clusters are unaffected — Leaflet.markercluster renders its own cluster bubbles regardless of individual marker icons.
- The 1.75× oversized non-clustered markers placed for radius results (Step 14) currently use the same SVG pin at larger size — update those to use 70px logo circles instead.

## Fallback for No-Logo Companies

Use a plain filled circle (SVG data URI or Canvas-drawn) in the company's `COMPANY_COLORS` color, same 40×40 px size and center-anchor as logo pins. This keeps the visual style consistent across the map.

The existing SVG teardrop pin code must be **kept in place but unused** — do not delete it. A one-line swap (switching the icon factory function) is enough to revert to teardrops instantly if the circle style doesn't work out.

## Open Questions Resolved

1. ✅ Company name strings verified against `stations.json` — `LOGO_MAP` is final.
2. ✅ No-logo companies: plain colored circle matching `COMPANY_COLORS`; teardrop code kept for quick revert.
3. Popup anchor positioning (`popupAnchor`) to be confirmed visually during implementation on both mobile and desktop.
