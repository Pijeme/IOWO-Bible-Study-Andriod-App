param([int]$Port = 8765)
$ErrorActionPreference = 'Stop'
$projectDirectory = Split-Path -Parent $PSScriptRoot
$testPython = Join-Path $projectDirectory '.tools/test-env/Scripts/python.exe'
if (-not (Test-Path -LiteralPath $testPython)) { throw 'Prepare .tools/test-env first using README.md.' }
& $testPython (Join-Path $projectDirectory 'app/src/main/python/offline_app.py') --project $projectDirectory --port $Port
