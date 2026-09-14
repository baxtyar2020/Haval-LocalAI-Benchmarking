#Requires -Version 5.1
<#
  Sign a built EXE or NSIS setup with Azure Trusted Signing
  (same account/profile as Model PR-21 / Sky Rescue / Nantindo).

  Requires: az login (haval2007@gmail.com), and:
    dotnet tool install -g sign --prerelease
#>
param(
  [string]$File = $env:HAVAL_SIGN_FILE
)

$ErrorActionPreference = "Stop"
$root = Split-Path $PSScriptRoot -Parent
if (-not $File) {
  $File = Join-Path $root "What-to-ship final\HavalLocalAIBench-0.1.0-setup.exe"
}
if (-not (Test-Path $File)) {
  Write-Error "File not found: $File"
}

$sign = Join-Path $env:USERPROFILE ".dotnet\tools\sign.exe"
if (-not (Test-Path $sign)) {
  Write-Error "sign.exe not found. Run: dotnet tool install -g sign --prerelease"
}

Write-Host "Signing with Azure Trusted Signing (personal-developer / SkyRescueGame)"
Write-Host "  $File"
& $sign code artifact-signing $File `
  --artifact-signing-endpoint "https://eus.codesigning.azure.net/" `
  --artifact-signing-account "personal-developer" `
  --artifact-signing-certificate-profile "SkyRescueGame" `
  --azure-credential-type azure-cli `
  --timestamp-url "http://timestamp.acs.microsoft.com/" `
  --verbosity Information
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
Write-Host "Signed $File"
