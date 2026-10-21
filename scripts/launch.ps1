$projectRoot = Split-Path -Parent $PSScriptRoot
$env:TEMP = Join-Path $projectRoot 'tools'
$env:TMP = $env:TEMP
$bridgeExe = Join-Path $projectRoot 'tools\bridge\AltirraBridge-nightly-windows-x86_64\AltirraBridgeServer.exe'
Start-Process -FilePath $bridgeExe -ArgumentList '--bridge=tcp:127.0.0.1:0' -WindowStyle Hidden -WorkingDirectory $projectRoot -RedirectStandardError (Join-Path $projectRoot 'results\server-stderr.txt') -RedirectStandardOutput (Join-Path $projectRoot 'results\server-stdout.txt')
