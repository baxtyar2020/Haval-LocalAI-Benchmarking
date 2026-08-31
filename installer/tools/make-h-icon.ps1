#Requires -Version 5.1
# Builds EXE / shortcut / wizard icons from Doc\desktopicon.png
# via a square PNG + `tauri icon` (RC.EXE-safe ICO).
$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Drawing

$root = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$iconDir = Join-Path $root "app\src-tauri\icons"
$bmpDir = Join-Path $root "installer\assets\bmp"
$sourcePng = Join-Path $root "Doc\desktopicon.png"
$sourceCopy = Join-Path $root "installer\assets\source\desktopicon.png"
$squarePng = Join-Path $iconDir "icon-source.png"
New-Item -ItemType Directory -Force -Path $iconDir, $bmpDir, (Split-Path $sourceCopy -Parent) | Out-Null

if (-not (Test-Path $sourcePng)) {
  throw "Desktop icon source is missing: $sourcePng"
}

Copy-Item $sourcePng $sourceCopy -Force
$srcImg = [System.Drawing.Image]::FromFile($sourcePng)
try {
  $side = [Math]::Max($srcImg.Width, $srcImg.Height)
  $square = New-Object System.Drawing.Bitmap $side, $side
  $g = [System.Drawing.Graphics]::FromImage($square)
  $g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
  $g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::HighQuality
  $g.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::HighQuality
  $g.CompositingQuality = [System.Drawing.Drawing2D.CompositingQuality]::HighQuality
  $g.Clear([System.Drawing.Color]::Transparent)
  $dx = [int](($side - $srcImg.Width) / 2)
  $dy = [int](($side - $srcImg.Height) / 2)
  $g.DrawImage($srcImg, $dx, $dy, $srcImg.Width, $srcImg.Height)
  $g.Dispose()

  $out = New-Object System.Drawing.Bitmap 1024, 1024
  $g2 = [System.Drawing.Graphics]::FromImage($out)
  $g2.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
  $g2.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::HighQuality
  $g2.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::HighQuality
  $g2.Clear([System.Drawing.Color]::Transparent)
  $g2.DrawImage($square, 0, 0, 1024, 1024)
  $g2.Dispose()
  $square.Dispose()
  if (Test-Path $squarePng) { Remove-Item $squarePng -Force }
  $out.Save($squarePng, [System.Drawing.Imaging.ImageFormat]::Png)
  $out.Dispose()
} finally {
  $srcImg.Dispose()
}

$tauri = Join-Path $root "app\node_modules\.bin\tauri.cmd"
if (-not (Test-Path $tauri)) {
  throw "tauri CLI not found at $tauri. Run npm install in app."
}
& $tauri icon $squarePng --output $iconDir
if ($LASTEXITCODE -and $LASTEXITCODE -ne 0) {
  throw "tauri icon failed with exit $LASTEXITCODE"
}

$icoPath = Join-Path $iconDir "icon.ico"
if (-not (Test-Path $icoPath)) {
  throw "tauri icon did not write $icoPath"
}
Copy-Item $icoPath (Join-Path $bmpDir "wizard.ico") -Force
Write-Host "Wrote desktop icons from Doc\desktopicon.png"
