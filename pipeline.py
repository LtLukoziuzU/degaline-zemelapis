#!/usr/bin/env python3
"""
pipeline.py — Degaline data pipeline

Downloads today's .xlsx from ENA, parses it, geocodes any new addresses via
Photon, and writes data/stations.json + updates data/geocache.json.

Run locally:  python3 pipeline.py
Run in CI:    same command — GitHub Actions installs openpyxl first.
"""

import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import openpyxl

# ── Paths ──────────────────────────────────────────────────────────────────────
ROOT          = Path(__file__).parent
DATA          = ROOT / 'data'
GEOCACHE_PATH = DATA / 'geocache.json'
STATIONS_PATH = DATA / 'stations.json'
XLSX_PATH     = DATA / 'latest.xlsx'
HISTORY_DIR   = DATA / 'history'
LOGS_DIR      = DATA / 'logs'

# ── Constants ──────────────────────────────────────────────────────────────────
USER_AGENT    = 'degaline-map/1.0 (LtLukoziuz+degaline@gmail.com)'
GEOCODE_DELAY = 5.0   # seconds between Photon requests
FLUSH_EVERY   = 20    # flush geocache to disk after this many new entries

# ── xlsx download ──────────────────────────────────────────────────────────────
def _xlsx_urls(d: date):
    """Both dk- and DK- casings for a given date."""
    y, m, dd = d.year, f'{d.month:02d}', f'{d.day:02d}'
    base = f'https://www.ena.lt/uploads/{y}-EDAC/dk-degalinese-{y}/'
    return [
        f'{base}dk-{y}-{m}-{dd}.xlsx',
        f'{base}DK-{y}-{m}-{dd}.xlsx',
    ]

def download_xlsx() -> str:
    """
    Try today through 4 days ago, both casings each day.
    Saves to data/latest.xlsx and returns the file date as ISO string.
    Raises RuntimeError if all attempts fail.
    """
    today = date.today()
    for days_back in range(5):
        d = today - timedelta(days=days_back)
        for url in _xlsx_urls(d):
            try:
                print(f'Trying {url}')
                req = urllib.request.Request(url, headers={
                    'User-Agent': USER_AGENT,
                    'Referer': 'https://www.ena.lt/degalu-kainos-degalinese/',
                })
                with urllib.request.urlopen(req, timeout=30) as resp:
                    XLSX_PATH.write_bytes(resp.read())
                date_str = d.isoformat()
                print(f'Downloaded ({date_str}): {url}')
                return date_str
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    continue
                raise
    raise RuntimeError(
        'Nepavyko atsisiųsti xlsx failo — bandyta 5 dienos, abi rašybos.'
    )

# ── xlsx parsing ───────────────────────────────────────────────────────────────
def parse_xlsx(date_str: str) -> list[dict]:
    """
    Parse data/latest.xlsx. Detects header row dynamically (column A == 'Data').
    Returns a list of station dicts.
    """
    wb = openpyxl.load_workbook(XLSX_PATH, read_only=True, data_only=True)
    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))
    wb.close()

    header_idx = next(
        (i for i, row in enumerate(rows) if row and str(row[0]).strip() == 'Data'),
        None,
    )
    if header_idx is None:
        raise RuntimeError("Nerasta antraštės eilutė ('Data' A stulpelyje).")

    def price(v):
        # Accept int or float, reject bool (bool is a subclass of int in Python)
        return float(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else None

    stations = []
    for row in rows[header_idx + 1:]:
        if not row or row[3] is None:
            continue
        stations.append({
            'date':         date_str,
            'company':      str(row[1]).strip() if row[1] is not None else None,
            'municipality': str(row[2]).strip() if row[2] is not None else None,
            'address':      str(row[3]).strip() if row[3] is not None else None,
            'p95':          price(row[4]),
            'diesel':       price(row[5]),
            'lpg':          price(row[6]),
        })
    return stations

# ── Geocache ───────────────────────────────────────────────────────────────────
def load_geocache() -> dict:
    if GEOCACHE_PATH.exists():
        return json.loads(GEOCACHE_PATH.read_text(encoding='utf-8'))
    return {}

def save_geocache(cache: dict):
    GEOCACHE_PATH.write_text(
        json.dumps(cache, ensure_ascii=False, indent=2), encoding='utf-8'
    )

# ── Photon geocoding ───────────────────────────────────────────────────────────
def _photon(query: str) -> tuple[float, float] | None:
    """
    Single Photon query. Returns (lat, lng) or None.
    Retries on 429: waits 10s then 20s before giving up.
    Lithuanian latitudes: ~54–57, longitudes: ~21–26.
    """
    url = 'https://photon.komoot.io/api/?q=' + urllib.parse.quote(query) + '&limit=1'
    for wait in [0, 10, 20]:
        if wait:
            print(f'    429 — waiting {wait}s...')
            time.sleep(wait)
        try:
            req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read())
            features = data.get('features', [])
            if not features:
                return None
            # GeoJSON order is [longitude, latitude]
            lng, lat = features[0]['geometry']['coordinates']
            return float(lat), float(lng)
        except urllib.error.HTTPError as e:
            if e.code == 429:
                continue
            return None
        except Exception:
            return None
    return None

def geocode_stations(stations: list[dict], cache: dict):
    """
    Geocode all addresses absent from the cache. Mutates cache in place.
    Skips addresses already cached (including source='failed' entries — no retry).
    Flushes cache to disk every FLUSH_EVERY new entries and at the end.
    """
    seen = set()
    todo = []
    for s in stations:
        addr = s['address']
        if not addr or addr in seen:
            continue
        seen.add(addr)
        if addr not in cache:
            todo.append((addr, s['municipality']))

    if not todo:
        print('Geocache up to date — nothing to geocode.')
        return

    print(f'Geocoding {len(todo)} new address(es)...')
    new_count = 0
    failures = []

    for i, (address, municipality) in enumerate(todo):
        print(f'  [{i + 1}/{len(todo)}] {address}')

        # Strip secondary street reference (e.g. "Beržų g. 24/Drąsiųjų 7, Tryškiai"
        # → "Beržų g. 24, Tryškiai") — Photon can't resolve the dual-street format.
        query = re.sub(r'/[^,]+', '', address).strip()
        result = _photon(f'{query}, Lietuva')
        if result:
            lat, lng = result
            cache[address] = {'lat': lat, 'lng': lng, 'source': 'address'}
            print(f'    → {lat:.4f}, {lng:.4f}')
        else:
            time.sleep(GEOCODE_DELAY)
            muni_result = _photon(f'{municipality}, Lietuva') if municipality else None
            if muni_result:
                lat, lng = muni_result
                cache[address] = {'lat': lat, 'lng': lng, 'source': 'municipality'}
                print(f'    → municipality fallback ({municipality}): {lat:.4f}, {lng:.4f}')
            else:
                cache[address] = {'lat': None, 'lng': None, 'source': 'failed'}
                failures.append(address)
                print('    → failed')

        new_count += 1
        if new_count % FLUSH_EVERY == 0:
            save_geocache(cache)
            print(f'  Geocache flushed ({new_count} new so far)')

        if i < len(todo) - 1:
            time.sleep(GEOCODE_DELAY)

    save_geocache(cache)
    ok = len(todo) - len(failures)
    print(f'Geocoding done: {ok} succeeded, {len(failures)} failed.')
    if failures:
        print('Failed addresses:')
        for a in failures:
            print(f'  {a}')

# ── History & change log ──────────────────────────────────────────────────────
def load_previous_stations() -> dict:
    """Load current stations.json keyed by (company, address). Returns {} if missing."""
    if not STATIONS_PATH.exists():
        return {}
    data = json.loads(STATIONS_PATH.read_text(encoding='utf-8'))
    return {(s['company'], s['address']): s for s in data.get('stations', [])}

def fmt_price(v) -> str:
    return f'{v:.3f} €/L' if v is not None else '–'

def compare_and_log(prev: dict, output: dict):
    """Diff previous vs new stations and write a dated log + history snapshot."""
    HISTORY_DIR.mkdir(exist_ok=True)
    LOGS_DIR.mkdir(exist_ok=True)

    date_str = output['date']
    curr = {(s['company'], s['address']): s for s in output['stations']}

    new_stations     = [s for key, s in curr.items() if key not in prev]
    removed_stations = [s for key, s in prev.items() if key not in curr]
    changed_prices   = []

    for key, s in curr.items():
        if key not in prev:
            continue
        p = prev[key]
        diffs = [
            (label, p[field], s[field])
            for field, label in [('p95', '95 benzinas'), ('diesel', 'Dyzelinas'), ('lpg', 'Dujos')]
            if p[field] != s[field]
        ]
        if diffs:
            changed_prices.append((s, diffs))

    lines = [f'=== {date_str} ===\n\n']

    if not prev:
        lines.append('First run — no previous data to compare.\n')
    else:
        # New stations
        if new_stations:
            lines.append(f'New stations ({len(new_stations)}):\n')
            for s in new_stations:
                lines.append(
                    f"  + {s['company']} — {s['address']}, {s['municipality']}\n"
                    f"    Coords: {s['lat']:.5f}, {s['lng']:.5f}\n"
                    f"    95: {fmt_price(s['p95'])}  |  "
                    f"Dyzelinas: {fmt_price(s['diesel'])}  |  "
                    f"Dujos: {fmt_price(s['lpg'])}\n"
                )
        else:
            lines.append('New stations: none.\n')

        # Removed stations
        if removed_stations:
            lines.append(f'\nRemoved stations ({len(removed_stations)}):\n')
            for s in removed_stations:
                lines.append(f"  - {s['company']} — {s['address']}\n")
        else:
            lines.append('Removed stations: none.\n')

        # Changed prices
        if changed_prices:
            lines.append(f'\nPrice changes ({len(changed_prices)}):\n')
            for s, diffs in changed_prices:
                lines.append(f"  ~ {s['company']} — {s['address']}\n")
                for label, old, new in diffs:
                    lines.append(f"      {label}: {fmt_price(old)} → {fmt_price(new)}\n")
        else:
            lines.append('Price changes: none.\n')

        unchanged = len(output['stations']) - len(new_stations) - len(changed_prices)
        lines.append(f'\nUnchanged: {unchanged} station(s).\n')

    log_path = LOGS_DIR / f'{date_str}.log'
    log_path.write_text(''.join(lines), encoding='utf-8')
    print(
        f'Log: {log_path.name} — '
        f'{len(new_stations)} new, {len(removed_stations)} removed, '
        f'{len(changed_prices)} price change(s).'
    )

    # History snapshot
    history_path = HISTORY_DIR / f'{date_str}.json'
    history_path.write_text(
        json.dumps(output, ensure_ascii=False, indent=2), encoding='utf-8'
    )
    print(f'History snapshot: {history_path.name}')

    # Write outputs for GitHub Actions (no-op when running locally)
    has_changes = bool(prev and (new_stations or removed_stations or changed_prices))
    github_output = os.environ.get('GITHUB_OUTPUT')
    if github_output:
        with open(github_output, 'a') as f:
            f.write(f'has_changes={str(has_changes).lower()}\n')
            f.write(f'new_count={len(new_stations)}\n')
            f.write(f'removed_count={len(removed_stations)}\n')
            f.write(f'changed_count={len(changed_prices)}\n')
            f.write(f'log_path={log_path}\n')
            f.write(f'date={date_str}\n')

# ── stations.json output ───────────────────────────────────────────────────────
def build_output(stations: list[dict], cache: dict, date_str: str) -> dict:
    """
    Combine parsed station data with geocache coordinates.
    Excludes stations with failed or missing geocache entries.
    """
    out = []
    for s in stations:
        entry = cache.get(s['address'])
        if not entry or entry['source'] == 'failed' or entry['lat'] is None:
            continue
        out.append({
            'company':      s['company'],
            'municipality': s['municipality'],
            'address':      s['address'],
            'lat':          entry['lat'],
            'lng':          entry['lng'],
            'p95':          s['p95'],
            'diesel':       s['diesel'],
            'lpg':          s['lpg'],
        })
    fetched_at = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M+00:00')
    return {'date': date_str, 'fetched_at': fetched_at, 'stations': out}

# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    DATA.mkdir(exist_ok=True)

    print('=== Degaline pipeline ===')

    today = date.today().isoformat()

    # Skip if today's data was already processed.
    if STATIONS_PATH.exists():
        existing = json.loads(STATIONS_PATH.read_text(encoding='utf-8'))
        if existing.get('date') == today:
            print(f'stations.json already up to date for {today} — nothing to do.')
            return

    date_str = download_xlsx()

    # Skip if LEA hasn't published today's file yet.
    if date_str != today:
        print(f'Downloaded xlsx is from {date_str}, not today ({today}) — LEA has not published yet. Skipping.')
        return

    print(f'Parsing {XLSX_PATH.name}...')
    stations = parse_xlsx(date_str)
    print(f'Parsed {len(stations)} station(s).')

    cache = load_geocache()
    print(f'Geocache loaded: {len(cache)} entry/entries.')

    geocode_stations(stations, cache)

    prev = load_previous_stations()
    output = build_output(stations, cache, date_str)

    compare_and_log(prev, output)

    STATIONS_PATH.write_text(
        json.dumps(output, ensure_ascii=False, indent=2), encoding='utf-8'
    )
    print(
        f'Written {STATIONS_PATH.name}: '
        f'{len(output["stations"])} station(s), date {date_str}.'
    )

if __name__ == '__main__':
    main()
