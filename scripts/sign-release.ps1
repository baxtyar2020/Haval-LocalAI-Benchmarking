#Requires -Version 5.1
<#
  Authenticode-sign a built installer or EXE. Does not create a certificate.
  Requires an EV or standard code-signing cert in the Windows cert store,
  and Windows SDK signtool.exe.

  Example:
    $env:HAVAL_SIGN_FILE = "E:\builds\Haval LocalAI Bench_0.1.0_x64-setup.exe"
    $env:HAVAL_SIGN_THUMBPRINT = "<cert sha1>"
    powershell -ExecutionPolicy Bypass -File scripts\sign-release.ps1
#>
param(
  [string]$File = $env:HAVAL_SIGN_FILE,
  [string]$Thumbprint = $env:HAVAL_SIGN_THUMBPRINT,
  [string]$TimestampUrl = "http://timestamp.digicert.com"
)

$ErrorActionPreference = "Stop"
if (-not $File -or -not (Test-Path $File)) {
  Write-Error "Set -File or HAVAL_SIGN_FILE to an existing installer or EXE."
}
if (-not $Thumbprint) {
  Write-Error "Set -Thumbprint or HAVAL_SIGN_THUMBPRINT to the signing certificate SHA1."
}

$signtool = Get-ChildItem -Path "${env:ProgramFiles(x86)}\Windows Kits\10\bin" -Recurse -Filter signtool.exe -ErrorAction SilentlyContinue |
  Where-Object { $_.FullName -match "\\x64\\signtool.exe$" } |
  Select-Object -Last 1 -ExpandProperty FullName
if (-not $signtool) {
  Write-Error "signtool.exe not found. Install the Windows 10/11 SDK."
}

& $signtool sign /fd SHA256 /td SHA256 /tr $TimestampUrl /sha1 $Thumbprint $File
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
Write-Host "Signed $File"
