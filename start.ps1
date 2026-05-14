#Requires -Version 5.1
<#
.SYNOPSIS
    Sets up and runs the Superstore AI Chatbot via Docker.
.DESCRIPTION
    Builds the Docker image, seeds the database, and streams logs here.
    If a frontend/ directory exists, starts its dev server in a new window.
.EXAMPLE
    .\start.ps1
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$Root         = $PSScriptRoot
$BackendPort  = 5000
$FrontendPort = 5173

function Write-Step { param($msg) Write-Host "[setup] $msg" -ForegroundColor Cyan }
function Write-Ok   { param($msg) Write-Host "[ok]    $msg" -ForegroundColor Green }
function Write-Warn { param($msg) Write-Host "[warn]  $msg" -ForegroundColor Yellow }
function Write-Fail { param($msg) Write-Host "[error] $msg" -ForegroundColor Red }

function Test-Cmd {
    param($Name)
    $null -ne (Get-Command $Name -ErrorAction SilentlyContinue)
}

Set-Location $Root

Write-Host ""
Write-Host "==================================================" -ForegroundColor Magenta
Write-Host "  Superstore AI Chatbot - Setup and Start"         -ForegroundColor Magenta
Write-Host "==================================================" -ForegroundColor Magenta
Write-Host ""

# ── 1. Check Docker ───────────────────────────────────────────────────────────
Write-Step "Checking Docker..."
if (-not (Test-Cmd "docker")) {
    Write-Fail "Docker not found. Install Docker Desktop from https://docker.com"
    Read-Host "Press Enter to exit"
    exit 1
}
$null = docker info 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Fail "Docker is not running. Start Docker Desktop and try again."
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Ok "Docker: $(docker --version)"

# ── 2. Environment file ───────────────────────────────────────────────────────
Write-Step "Checking .env file..."
if (-not (Test-Path (Join-Path $Root ".env"))) {
    $example = Join-Path $Root ".env.example"
    if (Test-Path $example) {
        Copy-Item $example (Join-Path $Root ".env")
        Write-Warn ".env created from .env.example"
        Write-Warn "Edit .env with your API keys then re-run this script."
        Read-Host "Press Enter to exit"
        exit 1
    }
    Write-Fail ".env missing and no .env.example found."
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Ok ".env found"

# ── 3. Data directory and CSV check ──────────────────────────────────────────
Write-Step "Checking data directory..."
$DataDir = Join-Path $Root "data"
if (-not (Test-Path $DataDir)) {
    New-Item -ItemType Directory -Path $DataDir | Out-Null
}

$CsvPath = Join-Path $DataDir "superstore.csv"
foreach ($line in Get-Content (Join-Path $Root ".env")) {
    if ($line -match "^CSV_PATH=(.+)$") {
        $raw = $Matches[1].Trim()
        $CsvPath = $raw.Replace("/", [System.IO.Path]::DirectorySeparatorChar)
    }
}

if (-not (Test-Path $CsvPath)) {
    Write-Warn "superstore.csv not found at: $CsvPath"
    Write-Warn "Place superstore.csv in the data folder - the table will be empty until then."
} else {
    Write-Ok "superstore.csv found"
}

# ── 4. Build and start Docker container (logs stream here) ───────────────────
Write-Host ""
Write-Host "==================================================" -ForegroundColor Magenta
Write-Host "  Backend  -> http://localhost:$BackendPort"       -ForegroundColor Green
Write-Host "  Frontend -> http://localhost:3000"               -ForegroundColor Green
Write-Host "  Health   -> http://localhost:$BackendPort/api/health" -ForegroundColor Cyan
Write-Host "  Ctrl+C stops the container."                     -ForegroundColor DarkGray
Write-Host "==================================================" -ForegroundColor Magenta
Write-Host ""

docker compose up --build
