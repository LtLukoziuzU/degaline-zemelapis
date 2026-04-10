#!/usr/bin/env bash
set -euo pipefail

DIR="$(cd "$(dirname "$0")" && pwd)"
OUT="$DIR/data/latest.xlsx"

mkdir -p "$DIR/data"

try_download() {
    local DATE=$1
    local YYYY=${DATE:0:4}
    local MM=${DATE:5:2}
    local DD=${DATE:8:2}
    local BASE="https://www.ena.lt/uploads/${YYYY}-EDAC/dk-degalinese-${YYYY}"

    curl -fsSL "${BASE}/dk-${YYYY}-${MM}-${DD}.xlsx" -o "$OUT" 2>/dev/null && return 0
    curl -fsSL "${BASE}/DK-${YYYY}-${MM}-${DD}.xlsx" -o "$OUT" 2>/dev/null && return 0
    return 1
}

SUCCESS=false
for DAYS_BACK in 0 1 2 3 4; do
    DATE=$(date -d "${DAYS_BACK} days ago" +%Y-%m-%d)
    echo "Bandoma: ${DATE}..."
    if try_download "$DATE"; then
        echo "Įkeltas ${DATE} dienos failas."
        SUCCESS=true
        break
    fi
done

if [ "$SUCCESS" = false ]; then
    echo "Klaida: nepavyko rasti duomenų failo (bandyta 5 dienos). Patikrinkite interneto ryšį."
    exit 1
fi

# Kill any leftover server on our port
pkill -f "server.py" 2>/dev/null || true

# Start server in background
python3 "$DIR/server.py" &
SERVER_PID=$!

sleep 2

echo "Atidaroma žemėlapis..."
xdg-open "http://localhost:58472"

echo "Serveris veikia. Ctrl+C norėdami sustabdyti."
wait $SERVER_PID || true
