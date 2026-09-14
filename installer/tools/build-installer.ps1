#Requires -Version 5.1
<#
  Haval LocalAI Benchmarking — Windows installer build.

  From the repo root:

    powershell -ExecutionPolicy Bypass -File installer\tools\build-installer.ps1

  What this does, in order:
    1. Convert illustrations to NSIS BMPs + app/wizard icons
    2. Download embeddable CPython and official Node.js into installer/runtime/
    3. Run Tauri NSIS bundle (unsigned unless you sign afterwards)

  Output:
    app\src-tauri\target\release\bundle\nsis\*x64-setup.exe
    What-to-ship final\HavalLocalAIBench-<ver>-setup.exe          (first release only)
    What-to-ship final\updates\HavalLocalAIBench-<ver>-setup.exe  (later releases)
    What-to-ship final\updates\latest.json                        (always, for R2)

  First build keeps the current version. Every later build bumps the patch
  (0.1.0 -> 0.1.1) unless you pass -SetVersion.
#>
param(
  [switch]$SkipPython,
  [switch]$SkipNode,
  [switch]$FirstRelease,
  [switch]$Update,
  [string]$SetVersion = "",
  [string]$Notes = "Your reports and settings stay on this PC."
)

$ErrorActionPreference = "Stop"
$root = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$shipRoot = Join-Path $root "What-to-ship final"
$shipUpdates = Join-Path $shipRoot "updates"
New-Item -ItemType Directory -Force -Path $shipRoot | Out-Null
New-Item -ItemType Directory -Force -Path $shipUpdates | Out-Null

function Get-AppVersion {
  $conf = Get-Content (Join-Path $root "app\src-tauri\tauri.conf.json") -Raw
  if ($conf -match '"version"\s*:\s*"([^"]+)"') { return $Matches[1] }
  throw "Could not read version from tauri.conf.json"
}

function Get-NextPatch([string]$ver) {
  $parts = $ver.Split(".")
  if ($parts.Count -lt 3) { throw "Version '$ver' is not major.minor.patch" }
  $patch = [int]$parts[2] + 1
  return "$($parts[0]).$($parts[1]).$patch"
}

$firstMarker = Join-Path $shipRoot ".first-release-version"
$existingFirst = @(Get-ChildItem -Path $shipRoot -Filter "HavalLocalAIBench-*-setup.exe" -File -ErrorAction SilentlyContinue)
$isFirst = $FirstRelease -or ((-not $Update) -and $existingFirst.Count -eq 0 -and -not (Test-Path $firstMarker))

if ($SetVersion) {
  Write-Host "== 0/4  Setting version $SetVersion =="
  & (Join-Path $PSScriptRoot "set-app-version.ps1") -Version $SetVersion
} elseif ($isFirst) {
  $keep = Get-AppVersion
  Write-Host "== 0/4  First release - keeping version $keep =="
} else {
  $next = Get-NextPatch (Get-AppVersion)
  Write-Host "== 0/4  Update release - bumping version to $next =="
  & (Join-Path $PSScriptRoot "set-app-version.ps1") -Version $next
  $isFirst = $false
}

$shipVersion = Get-AppVersion

Write-Host "== 1/4  Wizard art and icons =="
& (Join-Path $PSScriptRoot "prepare-assets.ps1")
if ($LASTEXITCODE -and $LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

if (-not $SkipPython) {
  Write-Host "== 2/4  Bundled Python runtime =="
  & (Join-Path $PSScriptRoot "prepare-python.ps1")
  if ($LASTEXITCODE -and $LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
} else {
  Write-Host "== 2/4  Skipping Python (installer will need a system Python) =="
}

if (-not $SkipNode) {
  Write-Host "== 3/4  Bundled Node.js (Phase 2 coding tests) =="
  & (Join-Path $PSScriptRoot "prepare-node.ps1")
  if ($LASTEXITCODE -and $LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
} else {
  Write-Host "== 3/4  Skipping Node (Phase 2 coding will score 0 without it) =="
}

$pythonExe = Join-Path $root "installer\runtime\python\python.exe"
$nodeExe = Join-Path $root "installer\runtime\node\node.exe"
$bundleConfig = Join-Path $root "installer\tauri.bundle.json"
if (-not (Test-Path $pythonExe) -and -not $SkipPython) {
  Write-Error "installer\runtime\python\python.exe is missing after prepare-python.ps1"
}
if (-not (Test-Path $nodeExe) -and -not $SkipNode) {
  Write-Error "installer\runtime\node\node.exe is missing after prepare-node.ps1"
}

Write-Host "== 3b/4  Strip files that must not ship =="
Get-ChildItem (Join-Path $root "engine\haval_engine") -Recurse -Directory -Filter "__pycache__" -ErrorAction SilentlyContinue |
  ForEach-Object { Remove-Item $_.FullName -Recurse -Force }
# Product license is only repo LICENSE (Haval). Do not ship extra license docs from runtimes.
foreach ($runtimeDir in @(
    (Join-Path $root "installer\runtime\node"),
    (Join-Path $root "installer\runtime\python")
  )) {
  if (-not (Test-Path $runtimeDir)) { continue }
  Get-ChildItem $runtimeDir -File -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -match '^(LICENSE|license|COPYING|NOTICE)(\..*)?$' -or $_.Name -ieq "readme.rst" } |
    ForEach-Object { Remove-Item $_.FullName -Force }
}
$noShip = @(
  (Join-Path $root "app\public\app-help-guide\copy-filenames.html"),
  (Join-Path $root "app\public\app-help-guide\media\SHOT-LIST.txt")
)
foreach ($f in $noShip) {
  if (Test-Path $f) {
    Write-Error "Refusing to pack authoring file: $f  (move it out of app\public first)"
  }
}

Write-Host "== 4/4  Tauri NSIS package =="
Push-Location (Join-Path $root "app")
try {
  if (-not (Test-Path "node_modules")) {
    npm install
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
  }
  $tauri = Join-Path (Join-Path $root "app") "node_modules\.bin\tauri.cmd"
  $tauriArgs = @("build", "--no-bundle")
  if (Test-Path $pythonExe) { $tauriArgs += @("--config", $bundleConfig) }
  & $tauri @tauriArgs
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

  $exe = Join-Path $root "app\src-tauri\target\release\haval-localai-bench.exe"
  $ico = Join-Path $root "app\src-tauri\icons\icon.ico"
  $rcedit = Join-Path $PSScriptRoot "rcedit-x64.exe"
  if ((Test-Path $exe) -and (Test-Path $ico)) {
    if (-not (Test-Path $rcedit)) {
      Write-Host "Downloading rcedit to stamp the Windows EXE icon..."
      Invoke-WebRequest -Uri "https://github.com/electron/rcedit/releases/download/v2.0.0/rcedit-x64.exe" -OutFile $rcedit -UseBasicParsing
    }
    if (Test-Path $rcedit) {
      & $rcedit $exe --set-icon $ico
      if ($LASTEXITCODE -and $LASTEXITCODE -ne 0) {
        Write-Warning "rcedit could not stamp $exe"
      } else {
        Write-Host "Stamped Windows icon onto haval-localai-bench.exe"
      }
    }
  }

  $bundleArgs = @("bundle", "-b", "nsis")
  if (Test-Path $pythonExe) { $bundleArgs += @("--config", $bundleConfig) }
  & $tauri @bundleArgs
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

  $dist = Join-Path $root "app\dist"
  $authorHtml = Join-Path $dist "app-help-guide\copy-filenames.html"
  if (Test-Path $authorHtml) {
    Write-Error "Refusing to ship $authorHtml"
  }
  $leaks = Get-ChildItem $dist -Recurse -Include *.html,*.js,*.txt,*.json -ErrorAction SilentlyContinue |
    Select-String -Pattern "E:\\\\Groke|haval2007@" -ErrorAction SilentlyContinue
  if ($leaks) {
    Write-Error ("Refusing to ship personal paths or emails found in:`n" + ($leaks | ForEach-Object { $_.Path } | Sort-Object -Unique | Out-String))
  }
} finally {
  Pop-Location
}

$out = Join-Path $root "app\src-tauri\target\release\bundle\nsis"
$built = Get-ChildItem $out -Filter "*setup.exe" -ErrorAction SilentlyContinue |
  Sort-Object LastWriteTime -Descending |
  Select-Object -First 1
if (-not $built) {
  Write-Error "No NSIS setup.exe was produced under $out"
}

$shipName = "HavalLocalAIBench-$shipVersion-setup.exe"
if ($isFirst) {
  $destExe = Join-Path $shipRoot $shipName
  Copy-Item $built.FullName $destExe -Force
  Set-Content -Path $firstMarker -Value $shipVersion -Encoding ascii
  Write-Host ""
  Write-Host "FIRST RELEASE - upload this EXE to R2 folder havalbencmarkingapp/ only:"
  Write-Host "  $destExe"
} else {
  $destExe = Join-Path $shipUpdates $shipName
  if (Test-Path $destExe) {
    Write-Error "Refusing to overwrite $destExe. That version was already shipped. Bump the version and build again."
  }
  Copy-Item $built.FullName $destExe -Force
  $websiteExe = Join-Path $shipRoot $shipName
  Copy-Item $built.FullName $websiteExe -Force
  Write-Host ""
  Write-Host "UPDATE RELEASE - same EXE for website download and in-app update:"
  Write-Host "  Full installer (website): $websiteExe"
  Write-Host "  Updater copy (R2 update/): $destExe"
}

$signScript = Join-Path $root "scripts\sign-release.ps1"
if (Test-Path $signScript) {
  Write-Host "Signing $destExe with Azure Trusted Signing..."
  & $signScript -File $destExe
  if ($LASTEXITCODE -and $LASTEXITCODE -ne 0) {
    Write-Warning "Signing failed. The unsigned file is still in the ship folder."
  } elseif (-not $isFirst) {
    $websiteExe = Join-Path $shipRoot $shipName
    Copy-Item $destExe $websiteExe -Force
  }
}

$latestPath = Join-Path $shipUpdates "latest.json"
& (Join-Path $PSScriptRoot "make-latest-json.ps1") -SetupExe $destExe -Version $shipVersion -Notes $Notes -OutFile $latestPath
if ($isFirst) {
  Write-Host "Also upload updates\latest.json to R2 havalbencmarkingapp/update/ (check file only; keep the first EXE in the parent R2 folder)."
}

$mb = [math]::Round($built.Length / 1MB, 1)
Write-Host ""
Write-Host "Installer folder: $out"
Write-Host ("  {0}  ({1} MB)" -f $built.FullName, $mb)
Write-Host "latest.json: $latestPath"
Write-Host "Azure Trusted Signing is used automatically when az login is active (scripts\sign-release.ps1)."
