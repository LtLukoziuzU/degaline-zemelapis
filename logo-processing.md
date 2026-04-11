# Logo Processing — Strategy & Decisions

## Goal

Produce circular logo images for each gas station company, to be used as custom map pins in place of the current SVG teardrop pins.

## Folder Structure

- `originallogo/` — untouched source images. Never modified. Reset point if anything goes wrong. Gitignored — not committed.
- `modifiedlogo/` — temporary working folder used during processing. Gitignored — not committed. Can be deleted once processing is done.
- `goodlogo/` — final output: one `{company}.png` per company, 256×256 px circular PNG with transparent outside the circle. **Committed to the repo** — this is the deliverable.

## Scripts

### `process_logos.py`
Generates a `_circle.png` for every image in `originallogo/`. No color/background changes — only resize and crop to a uniform 256×256 circle shape. Palette-mode images (P) are converted to RGBA first.

Key parameters:
- Canvas: 256×256
- Padding: 10% (logo fits within 230×230)
- Circle mask applied via `putalpha`

**Known limitation:** `putalpha` replaces the entire alpha channel, so transparent canvas pixels inside the circle become opaque black `(0,0,0,255)` — an artifact that needs to be handled downstream.

### `make_circleextend.py`
Generates a `_circleextend.png` from each `_circle.png`. Extends the logo's background color to fill the full circle, removing the artifact black corners.

Detection strategy:
1. Find all opaque inside-circle pixels.
2. Separate near-black `(r,g,b < 15)` from non-black.
3. Find the most common non-black color (quantized to nearest 8).
4. If that color dominates ≥50% of non-black pixels → solid background → use it as fill.
5. Special case for near-white dominant colors: threshold lowered to 30% (white backgrounds are common; no logo uses white as a graphic color).
6. If black fraction >97% → genuine black background → copy circle as-is.
7. If no dominant color found → no solid background → copy circle as-is.
8. Junasa hardcoded: blue `(0,91,190)` top half, yellow `(255,214,0)` bottom half, split at row 126.

Compositing: bbox-limited deartifact — only removes artifact blacks **outside** the logo's content bounding box (the corner arc regions), preserving black text/graphic elements inside the logo.

## Manual Fixes Required

The automated pipeline handled the majority of logos correctly. The following 10 required manual intervention:

| Company | Issue | Fix applied |
|---|---|---|
| boostpetrol | Fill blue `(0,48,112)` didn't match logo interior blue `(0,55,119)` — JPEG quantization mismatch | Sampled exact blue from logo corners; shrunk bbox by 4px to remove JPEG edge artifact |
| degta | Black letters removed by deartifact (JPEG near-black text pixels fell below threshold) | Bbox-limited deartifact only; white fill |
| emsi | No background color — black was all artifact | All near-black inside circle → transparent |
| gazimpeksas | Same as degta | Bbox-limited deartifact only; white fill |
| nostrada | Same as degta | Bbox-limited deartifact only; white fill |
| pynauja | No background color — black was all artifact | All near-black inside circle → transparent |
| skulas | Same as degta | Bbox-limited deartifact only; white fill |
| stateta | No background color — black was all artifact | All near-black inside circle → transparent |
| trevena | Yellow fill too small to cross 50% dominance threshold | Explicitly sampled yellow `(252,233,75)` from logo; bbox deartifact + yellow fill |
| utentra | Same as degta | Bbox-limited deartifact only; white fill |

Photo-based logos (real-world photos of stations with no clean logo) were scrapped entirely — those companies fall back to the default map pin design.

## Logos Without Images (fallback to default pin)

Companies present in `stations.json` but not in `goodlogo/` should fall back to the existing SVG teardrop pin colored by `COMPANY_COLORS`.

## Future Companies

If new companies appear in the ENA data:
- Manually source a logo image and add to `originallogo/`
- Run `process_logos.py` to generate the circle variant
- Run `make_circleextend.py` for the auto-extend attempt
- Review the result — for most solid-background logos it will work automatically
- If it fails, handle manually using the patterns above (bbox deartifact + fill, or full black → transparent)
- The scripts are reliable reference tools for the majority of cases; edge cases need human review
