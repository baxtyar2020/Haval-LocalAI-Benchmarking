#Requires -Version 5.1
<#
  Downloads the official Windows embeddable Python (opt-in; large ZIP).
  Puts python.exe under python-embed\ at the repo root (legacy helper).
  Customer installers should use installer\tools\prepare-python.ps1 instead,
  which writes installer\runtime\python\ and is invoked by build-installer.ps1.

  Usage (from repo root):
    powershell -ExecutionPolicy Bypass -File scripts\prepare-python-embed.ps1
#>
param(
  [string]$Version = "3.12.8"
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$dest = Join-Path $root "python-embed"
$zipName = "python-$Version-embed-amd64.zip"
$url = "https://www.python.org/ftp/python/$Version/$zipName"
$zipPath = Join-Path $env:TEMP $zipName

Write-Host "This downloads the official embeddable CPython $Version (~10+ MB)."
Write-Host "Target: $dest"
if (Test-Path (Join-Path $dest "python.exe")) {
  Write-Host "python.exe already present. Delete $dest to re-download."
  exit 0
}

Invoke-WebRequest -Uri $url -OutFile $zipPath
New-Item -ItemType Directory -Force -Path $dest | Out-Null
Expand-Archive -Path $zipPath -DestinationPath $dest -Force
Write-Host "Extracted. Enable import site in python*._pth (uncomment import site) and pip-install engine\requirements.txt into this runtime before shipping."
Write-Host "Copy this folder to the NSIS resource tree as python\ if you want a fully offline installer."
