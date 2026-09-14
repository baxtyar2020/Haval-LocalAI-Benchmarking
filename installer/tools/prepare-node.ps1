#Requires -Version 5.1
<#
  Downloads official Node.js (Windows x64 zip) for Phase 2 coding hidden tests.
  Output: installer/runtime/node/node.exe  (gitignored)

  Usage (repo root):
    powershell -ExecutionPolicy Bypass -File installer\tools\prepare-node.ps1
#>
param(
  [string]$Version = "22.18.0"
)

$ErrorActionPreference = "Stop"
$root = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$dest = Join-Path $root "installer\runtime\node"
$folder = "node-v$Version-win-x64"
$zipName = "$folder.zip"
$url = "https://nodejs.org/dist/v$Version/$zipName"
$zipPath = Join-Path $env:TEMP $zipName
$extract = Join-Path $env:TEMP $folder

Write-Host "Preparing bundled Node.js $Version -> $dest"

if (-not (Test-Path (Join-Path $dest "node.exe"))) {
  New-Item -ItemType Directory -Force -Path $dest | Out-Null
  Write-Host "Downloading $url"
  Invoke-WebRequest -Uri $url -OutFile $zipPath -UseBasicParsing
  if (Test-Path $extract) { Remove-Item $extract -Recurse -Force }
  Expand-Archive -Path $zipPath -DestinationPath $env:TEMP -Force
  $srcExe = Join-Path $extract "node.exe"
  if (-not (Test-Path $srcExe)) {
    Write-Error "node.exe missing from $extract"
  }
  Copy-Item $srcExe -Destination (Join-Path $dest "node.exe") -Force
}

$releaseDir = Join-Path $root "app\src-tauri\target\release"
if (Test-Path $releaseDir) {
  $releaseNode = Join-Path $releaseDir "node"
  New-Item -ItemType Directory -Force -Path $releaseNode | Out-Null
  Copy-Item (Join-Path $dest "node.exe") -Destination (Join-Path $releaseNode "node.exe") -Force
  Write-Host "Copied node.exe next to the release EXE at $releaseNode"
}

Write-Host "Bundled Node is ready at $dest"
