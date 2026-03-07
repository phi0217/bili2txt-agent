# FFmpeg Auto-Install Script for Windows
# Usage: Run .\install-ffmpeg.ps1 in PowerShell

Write-Host "====================================" -ForegroundColor Cyan
Write-Host "  FFmpeg Auto-Install Script" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

# Check if FFmpeg is already installed
Write-Host "Checking if FFmpeg is installed..." -ForegroundColor Yellow
try {
    $ffmpegCheck = Get-Command ffmpeg -ErrorAction Stop
    Write-Host "FFmpeg is already installed:" -ForegroundColor Green
    ffmpeg -version | Select-Object -First 1
    Write-Host ""
    Write-Host "No need to reinstall. If you want to reinstall, uninstall the current version first." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 0
} catch {
    Write-Host "FFmpeg not found, starting installation..." -ForegroundColor Red
}

Write-Host ""

# Configuration
$ffmpegUrl = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
$zipPath = "$env:TEMP\ffmpeg-release-essentials.zip"
$installPath = "C:\ffmpeg"

Write-Host "Installation path: $installPath" -ForegroundColor Cyan
Write-Host ""

# Create installation directory
Write-Host "Creating installation directory..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path $installPath | Out-Null

# Download FFmpeg
Write-Host "Downloading FFmpeg (approx. 100MB)..." -ForegroundColor Yellow
Write-Host "Download URL: $ffmpegUrl" -ForegroundColor Gray
try {
    $ProgressPreference = 'SilentlyContinue'
    Invoke-WebRequest -Uri $ffmpegUrl -OutFile $zipPath -UseBasicParsing
    Write-Host "Download completed" -ForegroundColor Green
} catch {
    Write-Host "Download failed: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please download and install manually:" -ForegroundColor Yellow
    Write-Host "1. Download: $ffmpegUrl" -ForegroundColor Gray
    Write-Host "2. Extract to: $installPath" -ForegroundColor Gray
    Write-Host "3. Add $installPath\bin to system PATH" -ForegroundColor Gray
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""

# Extract files
Write-Host "Extracting files..." -ForegroundColor Yellow
try {
    Expand-Archive -Path $zipPath -DestinationPath $installPath -Force
    Write-Host "Extraction completed" -ForegroundColor Green
} catch {
    Write-Host "Extraction failed: $_" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""

# Find actual ffmpeg.exe path (in subdirectory after extraction)
$ffmpegBinPath = Get-ChildItem -Path $installPath -Recurse -Filter "ffmpeg.exe" | Select-Object -First 1
if ($ffmpegBinPath) {
    $binDir = Split-Path $ffmpegBinPath.FullName -Parent

    # Move files to root directory (simplify path)
    Write-Host "Organizing file structure..." -ForegroundColor Yellow
    Move-Item -Path "$binDir\*" -Destination "$installPath\" -Force
    $binDir = "$installPath"
} else {
    $binDir = "$installPath\bin"
}

Write-Host ""

# Add to system PATH
Write-Host "Adding FFmpeg to system PATH..." -ForegroundColor Yellow

# Get current PATH from registry
$regPath = "Registry::HKEY_LOCAL_MACHINE\System\CurrentControlSet\Control\Session Manager\Environment"
$currentPath = (Get-ItemProperty -Path $regPath -Name Path).Path

# Check if already in PATH
if ($currentPath -notlike "*$binDir*") {
    # Add to PATH
    $newPath = "$currentPath;$binDir"
    Set-ItemProperty -Path $regPath -Name Path -Value $newPath

    # Notify system of environment variable change
    [System.Environment]::SetEnvironmentVariable("Path", $newPath, "Machine")

    Write-Host "Added to system PATH: $binDir" -ForegroundColor Green
    Write-Host ""
    Write-Host "IMPORTANT: Restart PowerShell or Command Prompt for changes to take effect" -ForegroundColor Yellow
} else {
    Write-Host "FFmpeg is already in PATH" -ForegroundColor Green
}

Write-Host ""

# Clean up temporary files
Write-Host "Cleaning up temporary files..." -ForegroundColor Yellow
Remove-Item -Path $zipPath -Force -ErrorAction SilentlyContinue

# Remove extracted subdirectory if empty
$extractedDir = Get-ChildItem -Path $installPath -Directory
if ($extractedDir) {
    Remove-Item -Path $extractedDir.FullName -Recurse -Force -ErrorAction SilentlyContinue
}

Write-Host "Cleanup completed" -ForegroundColor Green

Write-Host ""
Write-Host "====================================" -ForegroundColor Cyan
Write-Host "  FFmpeg Installation Complete!" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Installation path: $binDir" -ForegroundColor Gray
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Close current PowerShell window" -ForegroundColor White
Write-Host "2. Open a new PowerShell window" -ForegroundColor White
Write-Host "3. Run verification command: ffmpeg -version" -ForegroundColor White
Write-Host ""
Read-Host "Press Enter to exit"
