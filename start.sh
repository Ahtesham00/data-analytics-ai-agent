#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# start.sh  –  Sets up and runs the Data Analytics AI Agent via Docker (Linux / macOS)
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

BACKEND_PORT=5000
FRONTEND_PORT=5173

# ── Colours ──────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'

log()  { echo -e "${CYAN}[setup]${NC} $*"; }
ok()   { echo -e "${GREEN}[ok]${NC}    $*"; }
warn() { echo -e "${YELLOW}[warn]${NC}  $*"; }
die()  { echo -e "${RED}[error]${NC} $*" >&2; exit 1; }

echo ""
echo -e "${BOLD}==================================================${NC}"
echo -e "${BOLD}  Data Analytics AI Agent - Setup and Start${NC}"
echo -e "${BOLD}==================================================${NC}"
echo ""

# ── 1. Check Docker ───────────────────────────────────────────────────────────
log "Checking Docker..."
command -v docker &>/dev/null || die "Docker not found. Install Docker from https://docker.com"
docker info &>/dev/null       || die "Docker is not running. Start Docker and try again."
ok "Docker: $(docker --version)"

# ── 2. Environment file ───────────────────────────────────────────────────────
log "Checking .env file..."
if [[ ! -f ".env" ]]; then
    if [[ -f ".env.example" ]]; then
        cp .env.example .env
        warn ".env created from .env.example"
        warn "Edit .env with your API keys, then re-run this script."
        exit 1
    else
        die ".env missing and no .env.example found."
    fi
fi
ok ".env found"

# ── 3. Data directory & CSV check ────────────────────────────────────────────
log "Checking data directory..."
mkdir -p data

CSV_PATH=$(grep '^CSV_PATH=' .env | cut -d= -f2 | tr -d ' "'"'" )
CSV_PATH="${CSV_PATH:-./data/superstore.csv}"
if [[ ! -f "$CSV_PATH" ]]; then
    warn "superstore.csv not found at: $CSV_PATH"
    warn "Place superstore.csv in the data folder — the table will be empty until then."
else
    ok "superstore.csv found"
fi

# ── 4. Build and start Docker container (logs stream here) ───────────────────
echo ""
echo -e "${BOLD}==================================================${NC}"
echo -e "  Backend  → ${GREEN}http://localhost:$BACKEND_PORT${NC}"
echo -e "  Frontend → ${GREEN}http://localhost:3000${NC}"
echo -e "  Health   → ${CYAN}http://localhost:$BACKEND_PORT/api/health${NC}"
echo -e "  ${BOLD}Ctrl+C${NC} stops the container."
echo -e "${BOLD}==================================================${NC}"
echo ""

docker compose up --build
