# Works in Windows PowerShell 5.1 and PowerShell 7+.
<#
.SYNOPSIS
  Install the whale-maid DSH pet into $DSH_HOME/pets/whale-maid.

.DESCRIPTION
  The pet plugin scans $DSH_HOME/pets once at host startup. This script copies
  the pet package there; restart DSH Desktop afterwards to load it.

.PARAMETER DshHome
  DSH home directory. Defaults to $env:DSH_HOME, then ~/.dsh-beta, then ~/.dsh.

.PARAMETER Profile
  Desktop profile name used by -Select. Defaults to "desktop".

.PARAMETER Select
  Also set petId: whale-maid in profiles/<Profile>/cordis.patch.yml. Only edits
  the existing "- id: pet" block; never appends a new plugin row.

.EXAMPLE
  powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\install.ps1

.EXAMPLE
  powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\install.ps1 -Select
#>
[CmdletBinding()]
param(
  [string]$DshHome = '',
  [string]$Profile = 'desktop',
  [switch]$Select
)

$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent $PSScriptRoot
$petSource = Join-Path $repoRoot 'pet'
$manifestSource = Join-Path $petSource 'pet.json'
if (-not (Test-Path $manifestSource)) {
  throw "pet/pet.json not found under $repoRoot"
}

if (-not $DshHome) {
  if ($env:DSH_HOME -and $env:DSH_HOME.Trim().Length -gt 0) {
    $DshHome = $env:DSH_HOME.Trim()
  } elseif (Test-Path (Join-Path $HOME '.dsh-beta')) {
    $DshHome = Join-Path $HOME '.dsh-beta'
  } elseif (Test-Path (Join-Path $HOME '.dsh')) {
    $DshHome = Join-Path $HOME '.dsh'
  } else {
    throw "Cannot find DSH_HOME. Pass -DshHome 'C:\path\to\.dsh-beta'."
  }
}

$DshHome = [System.IO.Path]::GetFullPath($DshHome)
if (-not (Test-Path $DshHome)) {
  throw "DSH home does not exist: $DshHome"
}
if (-not (Test-Path (Join-Path $DshHome 'profiles')) -and -not (Test-Path (Join-Path $DshHome 'pet.json'))) {
  Write-Warning "$DshHome does not look like a DSH home (no profiles/ or pet.json). Continuing because -DshHome was explicit."
}

$dest = Join-Path $DshHome 'pets\whale-maid'
New-Item -ItemType Directory -Force -Path $dest | Out-Null
Copy-Item (Join-Path $petSource '*') $dest -Recurse -Force

$manifestPath = Join-Path $dest 'pet.json'
$manifestText = [System.IO.File]::ReadAllText($manifestPath, [System.Text.Encoding]::UTF8)
$manifest = $manifestText | ConvertFrom-Json
$idleCount = @($manifest.frames2d.tracks.idle.frames).Count
$hopCount = @($manifest.frames2d.tracks.hop.frames).Count
$missing = @()
foreach ($track in @($manifest.frames2d.tracks.PSObject.Properties)) {
  foreach ($frame in @($track.Value.frames)) {
    $path = Join-Path $dest (Join-Path $track.Name $frame)
    if (-not (Test-Path $path)) { $missing += $path }
  }
}
$totalBytes = (Get-ChildItem $dest -Recurse -File | Measure-Object Length -Sum).Sum
$totalMb = [math]::Round($totalBytes / 1MB, 2)

Write-Host ""
Write-Host "Installed: $dest" -ForegroundColor Green
Write-Host "  id:     $($manifest.id)  ($($manifest.displayName))"
Write-Host "  idle:   $idleCount frames"
Write-Host "  hop:    $hopCount frames"
Write-Host "  size:   $totalMb MB"
if ($missing.Count -gt 0) {
  Write-Warning "Missing frame files:"
  $missing | ForEach-Object { Write-Warning "  $_" }
}

if ($Select) {
  $patch = Join-Path $DshHome "profiles\$Profile\cordis.patch.yml"
  if (-not (Test-Path $patch)) {
    Write-Warning "-Select: profile patch not found: $patch"
  } else {
    $lines = [System.IO.File]::ReadAllLines($patch)
    $out = [System.Collections.Generic.List[string]]::new()
    $inPet = $false
    $foundPet = $false
    $set = $false
    $configIndex = -1
    $configIndent = ''

    for ($i = 0; $i -lt $lines.Length; $i++) {
      $line = $lines[$i]
      if ($line -match '^-\s+id:\s*pet\s*$') {
        $inPet = $true
        $foundPet = $true
        $out.Add($line)
        continue
      }
      if ($inPet -and $line -match '^-\s+id:\s*') {
        $inPet = $false
      }
      if ($inPet -and $line -match '^(\s*)config:\s*$') {
        $configIndex = $out.Count
        $configIndent = $Matches[1]
      }
      if ($inPet -and $line -match '^(\s*)petId:\s*') {
        $out.Add($Matches[1] + 'petId: whale-maid')
        $set = $true
        continue
      }
      $out.Add($line)
    }

    if (-not $set -and $configIndex -ge 0) {
      $out.Insert($configIndex + 1, $configIndent + '  petId: whale-maid')
      $set = $true
    }

    if ($set) {
      [System.IO.File]::WriteAllLines($patch, $out, [System.Text.UTF8Encoding]::new($false))
      Write-Host "Selected in: $patch" -ForegroundColor Green
    } elseif (-not $foundPet) {
      Write-Warning "-Select: no '- id: pet' row found in $patch; select the pet in Settings -> Pet instead."
    } else {
      Write-Warning "-Select: could not find a config: block to edit; select the pet in Settings -> Pet instead."
    }
  }
}

Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Restart DSH Desktop (tray icon -> Restart DSH Desktop)."
Write-Host "  2. Open Settings -> Pet and choose '$($manifest.displayName)'."
Write-Host "     (If you used -Select and the row existed, it is already the default.)"
Write-Host ""
