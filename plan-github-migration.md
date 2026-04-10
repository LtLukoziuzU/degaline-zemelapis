# Plan: GitHub Migration — Public Repo + Pages + Actions

Move degaline from a local-only app to a publicly hosted static site with automated daily data updates.

**Goal:** Zero-cost hosting on GitHub Pages, accessible on any device, daily xlsx pull and geocoding handled by GitHub Actions — no local server needed for the hosted version.

---

## Phase 1 — Local git setup

1. Initialise the repo:
   ```bash
   git init
   git branch -M main
   ```

2. Create `.gitignore`:
   ```
   data/latest.xlsx
   __pycache__/
   *.pyc
   ```
   `data/geocache.json` and `data/stations.json` stay tracked — they are persistent artifacts, not build output.

3. First commit:
   ```bash
   git add .
   git commit -m "Initial commit"
   ```

---

## Phase 2 — Create the GitHub repo

4. Install `gh` CLI (not yet on developer machine):
   ```bash
   sudo pacman -S github-cli
   gh auth login   # follow browser prompt
   ```

5. Create repo and push in one command:
   ```bash
   gh repo create degaline --public --source=. --remote=origin --push
   ```

---

## Phase 3 — Enable GitHub Pages

6. Enable Pages via CLI:
   ```bash
   gh api repos/:owner/degaline/pages --method POST \
     -f build_type=legacy \
     -f source.branch=main \
     -f source.path=/
   ```
   Or: repo Settings → Pages → Source: `main` branch, `/ (root)`.

   Site goes live at `https://<username>.github.io/degaline/` within a minute.
   Will fail on data until Phase 4 is complete.

---

## Phase 4 — Adapt the app for static hosting

This is the main coding work. Three parts:

### Step 7 — Write `pipeline.py`
Server-side script that replaces the browser's current xlsx + geocoding pipeline:
- Download `latest.xlsx` from ena.lt (no CORS issue server-side)
- Parse with `openpyxl` (already installed)
- Load `data/geocache.json`; geocode only new/missing stations via Photon
- Write updated `data/geocache.json`
- Write `data/stations.json` — pre-baked array of all stations with coords and prices, plus a top-level `date` field

### Step 8 — Rewrite `index.html` data loading
- Remove SheetJS (`lib/xlsx.full.min.js`) and its `<script>` tag
- Remove browser-side geocoding loop
- Remove `POST /data/geocache.json` call
- Replace entire data-load path with `fetch('data/stations.json')` → parse → render markers
- `server.py`, `server.ps1`, `update.sh`, `update.bat` are no longer needed for the hosted version; keep for local dev or remove

### Step 9 — Data date indicator
`pipeline.py` writes `{ "date": "YYYY-MM-DD", "stations": [...] }`.
Toolbar shows "Duomenys: YYYY-MM-DD" so users can see data freshness.

---

## Phase 5 — GitHub Actions workflow

### Step 10 — Create `.github/workflows/update.yml`
Triggers: daily cron at **07:00 UTC** (after LEA typically publishes the new file).

Job steps:
1. Checkout repo
2. Set up Python
3. Run `pipeline.py`
4. If `data/stations.json` or `data/geocache.json` changed → commit and push to `main`
5. GitHub Pages auto-deploys on the new commit

### Step 11 — Add manual trigger
Add `workflow_dispatch` so the workflow can be triggered manually from the GitHub UI — useful for testing and recovering from a failed day without waiting for the next cron.

---

## Effort estimate

| Phase | What | Who | Effort |
|---|---|---|---|
| 1–3 | git + GitHub setup | User (Claude can't push) | ~15 min |
| 4 step 7 | `pipeline.py` | Claude writes, user pushes | ~half a day |
| 4 step 8 | `index.html` rewrite | Claude writes, user pushes | ~half a day |
| 5 | Actions workflow | Claude writes, user pushes | ~1–2 hours |

---

## Open Questions

- **Mobile sidebar/search:** Planned features (step 8.6) need a mobile-first redesign before implementation. Separate plan to be drafted. Do not implement the desktop sidebar plan as-is.
- **Repo name:** `degaline` assumed — confirm before Phase 2.
- **GitHub username:** needed for the Pages URL and API calls.
