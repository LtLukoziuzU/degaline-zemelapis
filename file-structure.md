# File Structure

```
degaline_project/          ← development root (includes CLAUDE.md, docs, scripts)
├── CLAUDE.md
├── progress.md
├── nominatim.md
├── dev-environment.md
├── data-flow.md
├── xlsx-data-shape.md
├── geocoding-strategy.md
├── file-structure.md
├── update.bat
├── update.sh
├── server.ps1
├── server.py
├── index.html
├── lib/
│   ├── xlsx.full.min.js
│   └── leaflet/
│       ├── leaflet.min.js
│       ├── leaflet.min.css
│       └── images/
└── data/
    ├── latest.xlsx
    └── geocache.json

dist/                      ← build output, zipped for handoff to Windows user
├── update.bat
├── server.ps1
├── index.html
├── lib/                   ← same as above
└── data/
    └── geocache.json      ← pre-built cache included; latest.xlsx excluded (downloaded on first run)
```

## Build / Handoff

Produce a `dist/` folder containing only the files above — no development docs, no `update.sh`, no `server.py`, no `progress.md`. Zip `dist/` into `degaline.zip` for the Windows user.

`data/geocache.json` must be included (pre-built). `data/latest.xlsx` is intentionally excluded — `update.bat` downloads it fresh on first launch.

There is no automated build script yet — assembling `dist/` is a manual copy step.
