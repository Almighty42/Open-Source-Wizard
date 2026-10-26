#!/usr/bin/env bash
set -uo pipefail

log()  { printf '[%s] %s\n' "$(date '+%F %T')" "$*" >&2; }
ok()   { printf '[%s] OK   %s\n' "$(date '+%F %T')" "$*" >&2; }
warn() { printf '[%s] WARN %s\n' "$(date '+%F %T')" "$*" >&2; }
die()  { printf '[%s] FAIL %s\n' "$(date '+%F %T')" "$*" >&2; exit 1; }

APP=/srv/osw
DB=$APP/app.db
UPLOADS=$APP/app/static/uploads
ENV_FILE=$APP/.env
BACKUP_DIR=$APP/backups
KEEP=6
STAMP=$(date +%F)
FINAL=$BACKUP_DIR/osw-backup-$STAMP.tar.gz

log "Starting backup for $STAMP"

mkdir -p "$BACKUP_DIR" && chmod 700 "$BACKUP_DIR" || die "Cannot prepare $BACKUP_DIR"
WORK=$(mktemp -d "$BACKUP_DIR/.work.XXXXXX") || die "Cannot create work directory"
trap 'rm -rf "$WORK"' EXIT

log "Copying database"
[ -f "$DB" ] || die "Database not found: $DB"
sqlite3 "$DB" ".backup '$WORK/app.db'" || die "sqlite3 backup failed"
ok "Database copied ($(du -h "$WORK/app.db" | cut -f1))"

log "Checking database integrity"
CHECK=$(sqlite3 "$WORK/app.db" "PRAGMA integrity_check;")
[ "$CHECK" = ok ] || die "Integrity check failed: $CHECK"
TABLES=$(sqlite3 "$WORK/app.db" "SELECT count(*) FROM sqlite_master WHERE type='table';")
[ "${TABLES:-0}" -gt 0 ] || die "Backup contains no tables"
ok "Integrity check passed ($TABLES tables)"

log "Collecting configuration"
if [ -f "$ENV_FILE" ]; then
  cp "$ENV_FILE" "$WORK/env" && ok ".env included" || die "Could not copy .env"
else
  warn ".env not found, it will not be in the archive"
fi
echo "$STAMP" > "$WORK/BACKUP_DATE"

log "Checking uploads"
if [ -d "$UPLOADS" ]; then
  ok "Uploads: $(find "$UPLOADS" -type f | wc -l) files, $(du -sh "$UPLOADS" | cut -f1)"
else
  warn "Uploads directory not found: $UPLOADS"
fi

log "Creating archive"
TAR_ARGS=(-czf "$WORK/out.tar.gz" -C "$WORK" app.db BACKUP_DATE)
[ -f "$WORK/env" ] && TAR_ARGS+=(env)
[ -d "$UPLOADS" ] && TAR_ARGS+=(-C "$(dirname "$UPLOADS")" "$(basename "$UPLOADS")")
tar "${TAR_ARGS[@]}" || die "tar failed"

log "Verifying archive"
gzip -t "$WORK/out.tar.gz" || die "gzip test failed"
ENTRIES=$(tar -tzf "$WORK/out.tar.gz" | wc -l) || die "tar listing failed"
tar -tzf "$WORK/out.tar.gz" | grep -qx 'app.db' || die "Archive has no database"
ok "Archive verified ($ENTRIES entries)"

mv "$WORK/out.tar.gz" "$FINAL" || die "Could not move archive to $FINAL"
chmod 600 "$FINAL"
ln -sfn "osw-backup-$STAMP.tar.gz" "$BACKUP_DIR/latest.tar.gz"
ok "Saved $FINAL ($(du -h "$FINAL" | cut -f1)); latest.tar.gz updated"

log "Removing old backups (keeping $KEEP)"
ls -t "$BACKUP_DIR"/osw-backup-*.tar.gz 2>/dev/null | tail -n +$((KEEP+1)) | while read -r f; do
  rm -f "$f" && ok "Removed $f"
done
find "$BACKUP_DIR" -name 'pre-deploy-*.db' -mtime +30 -delete

ok "Disk free: $(df -h --output=avail / | tail -n1 | tr -d ' ')"
log "Finished"
