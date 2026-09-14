#Requires -Version 5.1
<#
  Build latest.json for Cloudflare R2 (update folder only).

  Does not upload. Use the existing R2 Uploader app, then upload:
    1. the setup EXE to havalbencmarkingapp/update/
    2. this latest.json to havalbencmarkingapp/update/  (last)

  Example:
    powershell -File installer\tools\make-latest-json.ps1 `
      -SetupExe ".\Haval LocalAI Benchmarking_0.1.1_x64-setup.exe" `
      -Version 0.1.1 `
      -Notes "Fixes Doctor GPU label. Your reports stay."
#>
param(
  [Parameter(Mandatory = $true)]
  [string]$SetupExe,
  [Parameter(Mandatory = $true)]
  [string]$Version,
  [string]$Notes = "Your reports and settings stay on this PC.",
  [string]$OutFile = ""
)

$ErrorActionPreference = "Stop"
$exe = (Resolve-Path $SetupExe).Path
$hash = (Get-FileHash -Algorithm SHA256 -Path $exe).Hash.ToLowerInvariant()
$size = (Get-Item $exe).Length
$hostName = "https://pub-3ecafaa87e184cb58f5f8ab76a9f4648.r2.dev"
$url = "$hostName/havalbencmarkingapp/update/HavalLocalAIBench-$Version-setup.exe"

$obj = [ordered]@{
  version = $Version
  url     = $url
  sha256  = $hash
  size    = $size
  notes   = $Notes
}
$json = $obj | ConvertTo-Json -Compress:$false
if (-not $OutFile) {
  $OutFile = Join-Path (Split-Path $exe) "latest.json"
}
$utf8 = New-Object System.Text.UTF8Encoding $false
[System.IO.File]::WriteAllText($OutFile, $json.Trim() + "`n", $utf8)
Write-Host "Wrote $OutFile"
Write-Host "Upload the EXE as: havalbencmarkingapp/update/HavalLocalAIBench-$Version-setup.exe"
Write-Host "Then overwrite:     havalbencmarkingapp/update/latest.json"
Write-Host "Do not replace the first-release EXE in havalbencmarkingapp/"
Write-Host $json
