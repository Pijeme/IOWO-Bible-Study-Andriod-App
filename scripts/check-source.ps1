param([switch]$Browser, [switch]$PlayDelivery)
$ErrorActionPreference = 'Stop'
$projectDirectory = Split-Path -Parent $PSScriptRoot
Push-Location -LiteralPath $projectDirectory
try {
    # Existing test APKs are allowed after the user requests phone testing;
    # this source-check workflow must not create or change any package itself.
    $packagesBefore = @{}
    Get-ChildItem -LiteralPath $projectDirectory -Recurse -File | Where-Object { $_.Extension -in '.apk','.aab' } | ForEach-Object {
        $packagesBefore[$_.FullName] = "$($_.Length):$($_.LastWriteTimeUtc.Ticks)"
    }
    $testPython = Join-Path $projectDirectory '.tools/test-env/Scripts/python.exe'
    if (-not (Test-Path -LiteralPath $testPython)) { throw 'Prepare .tools/test-env first using README.md.' }
    $env:IOWO_BROWSER_TESTS = if ($Browser) { '1' } else { '0' }
    & $testPython 'tests/test_offline.py'
    if ($LASTEXITCODE -ne 0) { throw 'Offline engine or browser verification failed.' }
    if (-not $env:JAVA_HOME) { $env:JAVA_HOME = 'C:/Program Files/Android/Android Studio/jbr' }
    $env:DEBUG = ''
    $gradleArguments = @(':app:compileDebugJavaWithJavac', ':app:lintDebug', '--console=plain')
    if ($PlayDelivery) { $gradleArguments += '-PplayDelivery=true' }
    # These tasks compile and inspect source. Never invoke assemble, bundle or install.
    & '.\gradlew.bat' @gradleArguments
    if ($LASTEXITCODE -ne 0) { throw 'Android compilation or lint failed.' }
    # Windows PowerShell ignores -Include with -LiteralPath in this form.
    $packages = @(Get-ChildItem -LiteralPath $projectDirectory -Recurse -File | Where-Object { $_.Extension -in '.apk','.aab' })
    foreach ($package in $packages) {
        $packageStamp = "$($package.Length):$($package.LastWriteTimeUtc.Ticks)"
        if (-not $packagesBefore.ContainsKey($package.FullName) -or $packagesBefore[$package.FullName] -ne $packageStamp) {
            throw 'An APK/AAB was created or changed by a source-only check.'
        }
    }
    Write-Host 'All requested source checks passed. No APK or AAB generated.'
} finally { Pop-Location }
