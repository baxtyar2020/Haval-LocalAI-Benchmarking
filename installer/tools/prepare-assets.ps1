#Requires -Version 5.1
<#
  Converts installer/assets/source PNGs into NSIS bitmaps and Windows icons.
  Run from repo root:
    powershell -ExecutionPolicy Bypass -File installer\tools\prepare-assets.ps1
#>
$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Drawing

$root = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$src = Join-Path $root "installer\assets\source"
$bmpDir = Join-Path $root "installer\assets\bmp"
$iconDir = Join-Path $root "app\src-tauri\icons"
New-Item -ItemType Directory -Force -Path $bmpDir, $iconDir | Out-Null

function Convert-ToBmp([string]$inPath, [string]$outPath, [int]$w, [int]$h) {
  $img = [System.Drawing.Image]::FromFile($inPath)
  try {
    $bmp = New-Object System.Drawing.Bitmap $w, $h
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
    $g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::HighQuality
    $g.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::HighQuality
    $g.Clear([System.Drawing.Color]::FromArgb(0xFF, 0xF6, 0xF1, 0xE9))
    $scale = [Math]::Max($w / [double]$img.Width, $h / [double]$img.Height)
    $dw = [int]($img.Width * $scale)
    $dh = [int]($img.Height * $scale)
    $dx = [int](($w - $dw) / 2)
    $dy = [int](($h - $dh) / 2)
    $g.DrawImage($img, $dx, $dy, $dw, $dh)
    $g.Dispose()
    if (Test-Path $outPath) { Remove-Item $outPath -Force }
    $bmp.Save($outPath, [System.Drawing.Imaging.ImageFormat]::Bmp)
    $bmp.Dispose()
  } finally {
    $img.Dispose()
  }
}

function Save-PngResize([string]$inPath, [string]$outPath, [int]$w, [int]$h) {
  $img = [System.Drawing.Image]::FromFile($inPath)
  try {
    $bmp = New-Object System.Drawing.Bitmap $w, $h
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
    $g.Clear([System.Drawing.Color]::Transparent)
    $g.DrawImage($img, 0, 0, $w, $h)
    $g.Dispose()
    if (Test-Path $outPath) { Remove-Item $outPath -Force }
    $bmp.Save($outPath, [System.Drawing.Imaging.ImageFormat]::Png)
    $bmp.Dispose()
  } finally {
    $img.Dispose()
  }
}

function Save-Ico([string]$pngPath, [string]$icoPath, [int]$size) {
  # RC.EXE (Tauri Windows resources) requires a classic BMP DIB icon, not PNG-in-ICO.
  $img = [System.Drawing.Image]::FromFile($pngPath)
  try {
    $bmp = New-Object System.Drawing.Bitmap $size, $size
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
    $g.Clear([System.Drawing.Color]::Transparent)
    $g.DrawImage($img, 0, 0, $size, $size)
    $g.Dispose()
    $hicon = $bmp.GetHicon()
    $icon = [System.Drawing.Icon]::FromHandle($hicon)
    if (Test-Path $icoPath) { Remove-Item $icoPath -Force }
    $fs = [System.IO.File]::Create($icoPath)
    $icon.Save($fs)
    $fs.Close()
    $icon.Dispose()
    $bmp.Dispose()
  } finally {
    $img.Dispose()
  }
}

Convert-ToBmp (Join-Path $src "sidebar.png") (Join-Path $bmpDir "sidebar.bmp") 164 314
Convert-ToBmp (Join-Path $src "header.png") (Join-Path $bmpDir "header.bmp") 150 57
Convert-ToBmp (Join-Path $src "ollama.png") (Join-Path $bmpDir "ollama.bmp") 280 120

& (Join-Path $PSScriptRoot "make-h-icon.ps1")

Write-Host "Wrote NSIS bitmaps to $bmpDir"
Write-Host "Wrote icons to $iconDir"
