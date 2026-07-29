#!/bin/bash

# ============================================
# Auto Sync Develop Branch
# Trigger: Perbedaan commit local vs remote
# Blocker: Uncommitted changes
# Conflict: Remote wins (theirs)
# ============================================

REPO_PATH="$(cd "$(dirname "$0")/../.." && pwd)"
LOG_FILE="$(cd "$(dirname "$0")" && pwd)/auto-sync.log"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date '+%H:%M:%S')]${NC} $1"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

warn() {
    echo -e "${YELLOW}[$(date '+%H:%M:%S')] WARNING:${NC} $1"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] WARNING: $1" >> "$LOG_FILE"
}

error() {
    echo -e "${RED}[$(date '+%H:%M:%S')] ERROR:${NC} $1"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1" >> "$LOG_FILE"
}

info() {
    echo -e "${BLUE}[$(date '+%H:%M:%S')] INFO:${NC} $1"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] INFO: $1" >> "$LOG_FILE"
}

# ─── 1. Masuk repo ───
cd "$REPO_PATH" || { error "Gagal masuk ke $REPO_PATH"; exit 1; }

# ─── 2. Pastikan di branch develop ───
CURRENT=$(git rev-parse --abbrev-ref HEAD)
if [ "$CURRENT" != "develop" ]; then
    info "Sedang di branch '$CURRENT', checkout ke develop..."
    git checkout develop 2>&1 || { error "Gagal checkout develop"; exit 1; }
fi

# ─── 3. BLOCKER: Cek uncommitted changes ───
if [ -n "$(git status --porcelain)" ]; then
    warn "Ada uncommitted changes. Script di-skip."
    exit 0
fi

# ─── 4. Fetch remote develop ───
git fetch origin develop 2>&1 || { error "Gagal fetch origin/develop"; exit 1; }

LOCAL=$(git rev-parse develop)
REMOTE=$(git rev-parse origin/develop)

# ─── 5. TRIGGER: Cek perbedaan commit ───
if [ "$LOCAL" = "$REMOTE" ]; then
    info "Local & remote sudah sinkron. Tidak ada tindakan."
    exit 0
fi

AHEAD=$(git rev-list --count origin/develop..develop)
BEHIND=$(git rev-list --count develop..origin/develop)

log "Trigger aktif! Local ahead: $AHEAD | behind: $BEHIND"

# ─── 6. EKSEKUSI ───

# CASE A: Remote lebih maju → PULL
if [ "$BEHIND" -gt 0 ] && [ "$AHEAD" -eq 0 ]; then
    log "Remote lebih maju. Pulling dengan 'theirs'..."
    git pull -X theirs origin develop 2>&1
    if [ $? -eq 0 ]; then
        log "✅ Pull berhasil. Local up-to-date."
    else
        error "❌ Pull gagal. Perlu cek manual."
        exit 1
    fi

# CASE B: Local lebih maju → PUSH
elif [ "$AHEAD" -gt 0 ] && [ "$BEHIND" -eq 0 ]; then
    log "Local lebih maju. Pushing..."
    git push origin develop 2>&1
    if [ $? -eq 0 ]; then
        log "✅ Push berhasil. Remote up-to-date."
    else
        error "❌ Push gagal."
        exit 1
    fi

# CASE C: DIVERGE → PULL (remote menang) lalu PUSH
elif [ "$AHEAD" -gt 0 ] && [ "$BEHIND" -gt 0 ]; then
    warn "Local & remote diverge!"
    log "Merge dengan strategi 'theirs' (remote menang saat conflict)..."

    git pull -X theirs origin develop 2>&1
    if [ $? -eq 0 ]; then
        log "✅ Merge berhasil. Pushing hasil merge..."
        git push origin develop 2>&1
        if [ $? -eq 0 ]; then
            log "✅ Sinkronisasi selesai. Kedua branch sama sekarang."
        else
            error "❌ Push setelah merge gagal."
            exit 1
        fi
    else
        error "❌ Merge gagal meski pakai theirs. Perlu bantuan manual."
        exit 1
    fi
fi
