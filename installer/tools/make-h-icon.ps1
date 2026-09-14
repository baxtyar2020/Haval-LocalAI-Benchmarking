#Requires -Version 5.1
# Builds EXE / shortcut / wizard icons from Doc\desktopicon.png.
# Windows RC.EXE needs a classic BMP-DIB ICO (not PNG-in-ICO from `tauri icon`).
$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Drawing

$root = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$iconDir = Join-Path $root "app\src-tauri\icons"
$bmpDir = Join-Path $root "installer\assets\bmp"
$sourcePng = Join-Path $root "Doc\desktopicon.png"
$sourceCopy = Join-Path $root "installer\assets\source\desktopicon.png"
New-Item -ItemType Directory -Force -Path $iconDir, $bmpDir, (Split-Path $sourceCopy -Parent) | Out-Null

if (-not (Test-Path $sourcePng)) {
  throw "Desktop icon source is missing: $sourcePng"
}

Copy-Item $sourcePng $sourceCopy -Force
$srcImg = [System.Drawing.Image]::FromFile($sourcePng)

function New-IconBitmap([System.Drawing.Image]$src, [int]$size, [double]$zoom = 1.0, [bool]$opaqueOrange = $false) {
  $bmp = New-Object System.Drawing.Bitmap $size, $size, ([System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
  $g = [System.Drawing.Graphics]::FromImage($bmp)
  $g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
  $g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::HighQuality
  $g.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::HighQuality
  $g.CompositingQuality = [System.Drawing.Drawing2D.CompositingQuality]::HighQuality
  $orange = [System.Drawing.Color]::FromArgb(255, 219, 79, 27)
  if ($opaqueOrange) {
    $g.Clear($orange)
  } else {
    $g.Clear([System.Drawing.Color]::Transparent)
  }
  $side = [Math]::Max($src.Width, $src.Height)
  $scale = ($size / [double]$side) * $zoom
  $dw = [int]($src.Width * $scale)
  $dh = [int]($src.Height * $scale)
  $dx = [int](($size - $dw) / 2)
  $dy = [int](($size - $dh) / 2)
  $g.DrawImage($src, $dx, $dy, $dw, $dh)
  $g.Dispose()
  return $bmp
}

function Get-BgraBottomUp([System.Drawing.Bitmap]$bmp) {
  $w = $bmp.Width
  $h = $bmp.Height
  $rect = New-Object System.Drawing.Rectangle 0, 0, $w, $h
  $data = $bmp.LockBits($rect, [System.Drawing.Imaging.ImageLockMode]::ReadOnly, [System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
  try {
    $stride = $data.Stride
    $buf = New-Object byte[] ($stride * $h)
    [System.Runtime.InteropServices.Marshal]::Copy($data.Scan0, $buf, 0, $buf.Length)
    $rowBytes = $w * 4
    $out = New-Object byte[] ($rowBytes * $h)
    for ($y = 0; $y -lt $h; $y++) {
      [Array]::Copy($buf, ($h - 1 - $y) * $stride, $out, $y * $rowBytes, $rowBytes)
    }
    return $out
  } finally {
    $bmp.UnlockBits($data)
  }
}

function Get-AndMask([byte[]]$bgra, [int]$w, [int]$h) {
  $rowData = [int][Math]::Ceiling($w / 8.0)
  $rowSize = [int][Math]::Ceiling($rowData / 4.0) * 4
  $mask = New-Object byte[] ($rowSize * $h)
  for ($y = 0; $y -lt $h; $y++) {
    $srcRow = $y * $w * 4
    $dstRow = $y * $rowSize
    $col = 0
    for ($b = 0; $b -lt $rowData; $b++) {
      $byte = 0
      for ($bit = 0; $bit -lt 8; $bit++) {
        if ($col -ge $w) { break }
        $a = $bgra[$srcRow + $col * 4 + 3]
        if ($a -eq 0) { $byte = $byte -bor (1 -shl (7 - $bit)) }
        $col++
      }
      $mask[$dstRow + $b] = [byte]$byte
    }
  }
  return $mask
}

function New-BmpDib([System.Drawing.Bitmap]$bmp) {
  $w = $bmp.Width
  $h = $bmp.Height
  $xor = Get-BgraBottomUp $bmp
  $and = Get-AndMask $xor $w $h
  $ms = New-Object System.IO.MemoryStream
  $bw = New-Object System.IO.BinaryWriter $ms
  $bw.Write([int32]40)
  $bw.Write([int32]$w)
  $bw.Write([int32]($h * 2))
  $bw.Write([int16]1)
  $bw.Write([int16]32)
  $bw.Write([int32]0)
  $bw.Write([int32]0)
  $bw.Write([int32]0)
  $bw.Write([int32]0)
  $bw.Write([int32]0)
  $bw.Write([int32]0)
  $bw.Write([int32]0)
  $bw.Flush()
  $ms.Write($xor, 0, $xor.Length)
  $ms.Write($and, 0, $and.Length)
  return $ms.ToArray()
}

function Write-WindowsIco([string]$path, [int[]]$sizes, [System.Drawing.Image]$src) {
  $images = New-Object System.Collections.Generic.List[byte[]]
  foreach ($s in $sizes) {
    $small = $s -le 48
    $bmp = New-IconBitmap $src $s $(if ($small) { 1.28 } else { 1.0 }) $small
    $images.Add((New-BmpDib $bmp))
    $bmp.Dispose()
  }
  $fs = [System.IO.File]::Create($path)
  $bw = New-Object System.IO.BinaryWriter $fs
  $bw.Write([uint16]0)
  $bw.Write([uint16]1)
  $bw.Write([uint16]$images.Count)
  $offset = 6 + (16 * $images.Count)
  for ($i = 0; $i -lt $images.Count; $i++) {
    $s = $sizes[$i]
    $dim = 0
    if ($s -lt 256) { $dim = $s }
    $bw.Write([byte]$dim)
    $bw.Write([byte]$dim)
    $bw.Write([byte]0)
    $bw.Write([byte]0)
    $bw.Write([uint16]1)
    $bw.Write([uint16]32)
    $bw.Write([uint32]$images[$i].Length)
    $bw.Write([uint32]$offset)
    $offset += $images[$i].Length
  }
  foreach ($img in $images) { $fs.Write($img, 0, $img.Length) }
  $bw.Flush()
  $fs.Close()
}

try {
  foreach ($pair in @(@(32, "32x32.png"), @(64, "64x64.png"), @(128, "128x128.png"), @(256, "128x128@2x.png"), @(256, "icon.png"))) {
    $sz = [int]$pair[0]
    $small = $sz -le 32
    $b = New-IconBitmap $srcImg $sz $(if ($small) { 1.28 } else { 1.0 }) $small
    $dest = Join-Path $iconDir $pair[1]
    if (Test-Path $dest) { Remove-Item $dest -Force }
    $b.Save($dest, [System.Drawing.Imaging.ImageFormat]::Png)
    $b.Dispose()
  }
  Copy-Item (Join-Path $iconDir "128x128.png") (Join-Path $iconDir "icon.icns") -Force

  $icoPath = Join-Path $iconDir "icon.ico"
  if (Test-Path $icoPath) { Remove-Item $icoPath -Force }
  # 32px first (Explorer / Tauri). All layers are BMP DIB so RC.EXE can embed them.
  Write-WindowsIco $icoPath @(32, 16, 24, 48, 64, 256) $srcImg
  Copy-Item $icoPath (Join-Path $bmpDir "wizard.ico") -Force
  Write-Host "Wrote BMP-DIB Windows icons from Doc\desktopicon.png"
} finally {
  $srcImg.Dispose()
}
