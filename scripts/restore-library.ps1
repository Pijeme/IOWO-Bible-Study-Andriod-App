param([Parameter(Mandatory=$true)][string]$ApkPath)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.IO.Compression.FileSystem
$projectDirectory = [IO.Path]::GetFullPath((Split-Path -Parent $PSScriptRoot))
$manifest = Get-Content -LiteralPath (Join-Path $projectDirectory 'app/src/main/assets/resource-manifest.json') -Raw | ConvertFrom-Json
$archive = [IO.Compression.ZipFile]::OpenRead((Resolve-Path -LiteralPath $ApkPath).Path)
try {
    foreach ($item in $manifest.files) {
        $destination = [IO.Path]::GetFullPath((Join-Path $projectDirectory $item.project_path))
        if (-not $destination.StartsWith($projectDirectory + [IO.Path]::DirectorySeparatorChar)) { throw 'Invalid library destination.' }
        if (Test-Path -LiteralPath $destination) {
            if ((Get-FileHash -LiteralPath $destination -Algorithm SHA256).Hash.ToLowerInvariant() -eq $item.sha256) { continue }
            throw "Existing file differs: $($item.project_path). Keep it safe and review before replacing."
        }
        $entry = $archive.GetEntry('assets/' + $item.path)
        if (-not $entry) { throw "This APK is missing $($item.path). Use the matching standalone APK, not a Play split APK." }
        [IO.Directory]::CreateDirectory([IO.Path]::GetDirectoryName($destination)) | Out-Null
        $staging = $destination + '.restore-tmp'
        $inputStream = $entry.Open()
        $outputStream = [IO.File]::Create($staging)
        try { $inputStream.CopyTo($outputStream) } finally { $inputStream.Dispose(); $outputStream.Dispose() }
        if ((Get-Item -LiteralPath $staging).Length -ne $item.bytes -or (Get-FileHash -LiteralPath $staging -Algorithm SHA256).Hash.ToLowerInvariant() -ne $item.sha256) { throw "Library verification failed: $($item.project_path)" }
        Move-Item -LiteralPath $staging -Destination $destination
        Write-Host "Restored $($item.project_path)"
    }
} finally { $archive.Dispose() }
Write-Host 'The exact offline library is restored and verified. No personal notes were imported.'
