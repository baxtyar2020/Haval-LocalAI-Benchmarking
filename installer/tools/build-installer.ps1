#Requires -Version 5.1
<#
  Haval LocalAI Benchmarking — Windows installer build.

  From the repo root:

    powershell -ExecutionPolicy Bypass -File installer\tools\build-installer.ps1

  What this does, in order:
    1. Convert illustrations to NSIS BMPs + app/wizard icons
    2. Download embeddable CPython and install engine wheels into installer/runtime/python
    3. Run Tauri NSIS bundle (unsigned unless you sign afterwards)

  Output:
    app\src-tauri\target\release\bundle\nsis\*x64-setup.exe
#>
param(
  [switch]$SkipPython
)

$ErrorActionPreference = "Stop"
$root = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent

Write-Host "== 1/3  Wizard art and icons =="
& (Join-Path $PSScriptRoot "prepare-assets.ps1")
if ($LASTEXITCODE -and $LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

if (-not $SkipPython) {
  Write-Host "== 2/3  Bundled Python runtime =="
  & (Join-Path $PSScriptRoot "prepare-python.ps1")
  if ($LASTEXITCODE -and $LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
} else {
  Write-Host "== 2/3  Skipping Python (installer will need a system Python) =="
}

$pythonExe = Join-Path $root "installer\runtime\python\python.exe"
$bundleConfig = Join-Path $root "installer\tauri.bundle.json"
if (-not (Test-Path $pythonExe) -and -not $SkipPython) {
  Write-Error "installer\runtime\python\python.exe is missing after prepare-python.ps1"
}

Write-Host "== 3/3  Tauri NSIS package =="
Push-Location (Join-Path $root "app")
try {
  if (-not (Test-Path "node_modules")) {
    npm install
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
  }
  $tauri = Join-Path (Join-Path $root "app") "node_modules\.bin\tauri.cmd"
  if (Test-Path $pythonExe) {
    & $tauri build --config $bundleConfig
  } else {
    & $tauri build
  }
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
} finally {
  Pop-Location
}

$out = Join-Path $root "app\src-tauri\target\release\bundle\nsis"
Write-Host ""
Write-Host "Installer folder: $out"
if (Test-Path $out) {
  Get-ChildItem $out -Filter "*setup.exe" | ForEach-Object { Write-Host "  $($_.FullName)  ($([math]::Round($_.Length/1MB, 1)) MB)" }
}
Write-Host "Sign next (optional): scripts\sign-release.ps1  (Doc\Code-Signing.md)"
