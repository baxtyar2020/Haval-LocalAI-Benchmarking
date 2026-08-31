#Requires -Version 5.1
<#
  Builds the offline Python runtime that the NSIS installer ships.
  Output: installer/runtime/python/python.exe  (gitignored)

  Usage (repo root):
    powershell -ExecutionPolicy Bypass -File installer\tools\prepare-python.ps1
#>
param(
  [string]$Version = "3.12.8"
)

$ErrorActionPreference = "Stop"
$root = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$dest = Join-Path $root "installer\runtime\python"
$zipName = "python-$Version-embed-amd64.zip"
$url = "https://www.python.org/ftp/python/$Version/$zipName"
$zipPath = Join-Path $env:TEMP $zipName

Write-Host "Preparing bundled CPython $Version -> $dest"

if (-not (Test-Path (Join-Path $dest "python.exe"))) {
  New-Item -ItemType Directory -Force -Path $dest | Out-Null
  Write-Host "Downloading $url"
  Invoke-WebRequest -Uri $url -OutFile $zipPath
  Expand-Archive -Path $zipPath -DestinationPath $dest -Force
}

$pth = Get-ChildItem $dest -Filter "python*._pth" | Select-Object -First 1
if ($pth) {
  $text = Get-Content $pth.FullName -Raw
  if ($text -notmatch '(?m)^import site') {
    $text = $text -replace '(?m)^#\s*import site', 'import site'
    if ($text -notmatch '(?m)^import site') {
      $text = $text.TrimEnd() + "`r`nimport site`r`n"
    }
  }
  if ($text -notmatch '(?m)^\.\.$') {
    $text = $text.TrimEnd() + "`r`n..`r`n"
  }
  Set-Content -Path $pth.FullName -Value $text -NoNewline
}

$python = Join-Path $dest "python.exe"
$getPip = Join-Path $env:TEMP "get-pip.py"
if (-not (Test-Path (Join-Path $dest "Lib\site-packages\pip"))) {
  Write-Host "Installing pip into the embeddable runtime"
  Invoke-WebRequest -Uri "https://bootstrap.pypa.io/get-pip.py" -OutFile $getPip
  & $python $getPip --no-warn-script-location
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

Write-Host "Installing engine wheels (pytest is not shipped)"
$pipPkgs = @(
  "fastapi>=0.115.0",
  "uvicorn[standard]>=0.32.0",
  "psutil>=6.0.0",
  "pywin32>=308",
  "WMI>=1.5.1",
  "jinja2>=3.1.0"
)
& $python -m pip install --no-warn-script-location @pipPkgs
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "Bundled Python is ready at $dest"
