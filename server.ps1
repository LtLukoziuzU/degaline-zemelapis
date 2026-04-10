$port = 58472
$root = Split-Path -Parent $MyInvocation.MyCommand.Path

$mimeTypes = @{
    '.html' = 'text/html; charset=utf-8'
    '.js'   = 'application/javascript'
    '.css'  = 'text/css'
    '.json' = 'application/json'
    '.xlsx' = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    '.png'  = 'image/png'
    '.ico'  = 'image/x-icon'
}

$http = [System.Net.HttpListener]::new()
$http.Prefixes.Add("http://localhost:$port/")

try { $http.Start() }
catch {
    Write-Error "Nepavyko paleisti serverio portu $port`: $_"
    exit 1
}

while ($http.IsListening) {
    $ctx = $http.GetContext()
    $req = $ctx.Request
    $res = $ctx.Response

    try {
        $urlPath = $req.Url.LocalPath

        # POST /data/geocache.json — write cache to disk
        if ($req.HttpMethod -eq 'POST' -and $urlPath -eq '/data/geocache.json') {
            $body = [System.IO.StreamReader]::new(
                $req.InputStream, [System.Text.Encoding]::UTF8
            ).ReadToEnd()
            $outPath = Join-Path $root 'data\geocache.json'
            [System.IO.File]::WriteAllText($outPath, $body, [System.Text.Encoding]::UTF8)
            $res.StatusCode = 200
            $res.Close()
            continue
        }

        # Serve index.html for root
        if ($urlPath -eq '/') { $urlPath = '/index.html' }

        $relPath  = $urlPath.TrimStart('/').Replace('/', [System.IO.Path]::DirectorySeparatorChar)
        $filePath = Join-Path $root $relPath

        if (Test-Path $filePath -PathType Leaf) {
            $bytes = [System.IO.File]::ReadAllBytes($filePath)
            $ext   = [System.IO.Path]::GetExtension($filePath).ToLower()
            $res.ContentType     = if ($mimeTypes.ContainsKey($ext)) { $mimeTypes[$ext] } else { 'application/octet-stream' }
            $res.ContentLength64 = $bytes.Length
            $res.OutputStream.Write($bytes, 0, $bytes.Length)
            $res.StatusCode = 200
        } else {
            $res.StatusCode = 404
        }
    } catch {
        try { $res.StatusCode = 500 } catch {}
    } finally {
        try { $res.Close() } catch {}
    }
}
