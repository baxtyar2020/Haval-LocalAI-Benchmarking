#Requires -Version 5.1
<#
  Sets the same SemVer on Tauri, npm, and Cargo so the installer, UI, and
  in-app updater all agree.
#>
param(
  [Parameter(Mandatory = $true)]
  [string]$Version
)

$ErrorActionPreference = "Stop"
if ($Version -notmatch '^\d+\.\d+\.\d+$') {
  Write-Error "Version must look like 1.0.1 (got '$Version')"
}

$root = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent

function Set-JsonVersion([string]$Path) {
  $text = [System.IO.File]::ReadAllText($Path)
  $updated = [regex]::Replace($text, '("version"\s*:\s*")[^"]+(")', { param($m) $m.Groups[1].Value + $Version + $m.Groups[2].Value }, 1)
  [System.IO.File]::WriteAllText($Path, $updated)
}

Set-JsonVersion (Join-Path $root "app\src-tauri\tauri.conf.json")
Set-JsonVersion (Join-Path $root "app\package.json")

$cargo = Join-Path $root "app\src-tauri\Cargo.toml"
$cargoTxt = [System.IO.File]::ReadAllText($cargo)
$cargoTxt = [regex]::Replace($cargoTxt, '(?m)^(version\s*=\s*")[^"]+(")', { param($m) $m.Groups[1].Value + $Version + $m.Groups[2].Value }, 1)
[System.IO.File]::WriteAllText($cargo, $cargoTxt)

Write-Host "App version is now $Version"
