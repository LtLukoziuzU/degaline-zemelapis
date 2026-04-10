@echo off
setlocal

if not exist "%~dp0data" mkdir "%~dp0data"

:: Try today, yesterday, and 2 days ago (handles weekends and public holidays)
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "$out = '%~dp0data\latest.xlsx';" ^
    "$success = $false;" ^
    "for ($i = 0; $i -le 4; $i++) {" ^
    "    $date = (Get-Date).AddDays(-$i);" ^
    "    $yyyy = $date.ToString('yyyy');" ^
    "    $mm   = $date.ToString('MM');" ^
    "    $dd   = $date.ToString('dd');" ^
    "    $base = \"https://www.ena.lt/uploads/$yyyy-EDAC/dk-degalinese-$yyyy\";" ^
    "    Write-Host \"Bandoma: $yyyy-$mm-$dd...\";" ^
    "    foreach ($pfx in @('dk','DK')) {" ^
    "        try {" ^
    "            Invoke-WebRequest -Uri \"$base/$pfx-$yyyy-$mm-$dd.xlsx\" -OutFile $out -ErrorAction Stop;" ^
    "            Write-Host \"Ikeltas $yyyy-$mm-$dd dienos failas.\";" ^
    "            $success = $true; break" ^
    "        } catch {}" ^
    "    }" ^
    "    if ($success) { break }" ^
    "}" ^
    "if (-not $success) { Write-Host 'Klaida: nepavyko rasti duomenu failo (bandyta 5 dienos).'; exit 1 }"

if %errorlevel% neq 0 (
    echo Patikrinkite interneto rysį.
    pause
    exit /b 1
)

:: Kill any leftover server on our port
powershell -NoProfile -Command "Get-NetTCPConnection -LocalPort 58472 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }" 2>nul

:: Open browser after 2s delay (background), then run server in this window
start /B powershell -NoProfile -Command "Start-Sleep 2; Start-Process 'http://localhost:58472'"

echo Serveris paleidžiamas. Naršyklė atsidarys automatiškai...
echo Uždaryti šį langą tik pabaigus darbą su žemėlapiu.
echo.

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0server.ps1"
