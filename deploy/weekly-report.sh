#!/usr/bin/env bash
set -uo pipefail

log()  { printf '[%s] %s\n' "$(date '+%F %T')" "$*" >&2; }
ok()   { printf '[%s] OK   %s\n' "$(date '+%F %T')" "$*" >&2; }
warn() { printf '[%s] WARN %s\n' "$(date '+%F %T')" "$*" >&2; }

APP=/srv/osw
OUT_DIR=$APP/reports
DAYS=7
TODAY=$(date +%F)
OUT=$OUT_DIR/osw-report-$TODAY.txt
TMP=$(mktemp)
ACCESS=$(mktemp)
trap 'rm -f "$TMP" "$ACCESS"' EXIT

log "Starting weekly report for $TODAY (last $DAYS days)"

mkdir -p "$OUT_DIR" && chmod 700 "$OUT_DIR" \
  && ok "Output directory ready: $OUT_DIR" \
  || warn "Could not prepare output directory: $OUT_DIR"

log "Collecting nginx access log entries"
DATES=$(for i in $(seq 0 $((DAYS-1))); do date -d "-$i day" +%d/%b/%Y; done | paste -sd'|')
zcat -f /var/log/nginx/access.log* 2>/dev/null | grep -E "\[($DATES):" > "$ACCESS"
ok "Access log entries found: $(wc -l < "$ACCESS")"

log "Calculating statistics"
TOTAL=$(wc -l < "$ACCESS")
S5=$(awk '$9 ~ /^5/' "$ACCESS" | wc -l)
S429=$(awk '$9 == 429' "$ACCESS" | wc -l)
S404=$(awk '$9 == 404' "$ACCESS" | wc -l)
ok "Requests: $TOTAL | 5xx: $S5 | 429: $S429 | 404: $S404"

log "Reading app errors from journal"
APP_ERRORS=$(journalctl -u osw --since "$DAYS days ago" -q --no-pager | grep -cE "ERROR|CRITICAL|Traceback")
ok "App errors found: $APP_ERRORS"

log "Counting SSH probes"
SSH_PROBES=$(journalctl -u ssh --since "$DAYS days ago" -q --no-pager | grep -c "Invalid user")
ok "Invalid-user SSH attempts: $SSH_PROBES"

log "Checking disk and package updates"
DISK=$(df --output=pcent / | tail -n1 | tr -dc '0-9')
UPGRADES=$(apt list --upgradable 2>/dev/null | grep -c "upgradable from")
ok "Disk used: ${DISK}% | pending upgrades: $UPGRADES"

log "Checking services"
BAD=""
for s in osw nginx; do
  if [ "$(systemctl is-active "$s")" = active ]; then
    ok "Service $s is active"
  else
    warn "Service $s is NOT active"
    BAD="$BAD $s"
  fi
done

log "Checking latest database backup"
LATEST_BACKUP=$(ls -t "$APP"/backups/app-*.db 2>/dev/null | head -n1)
BACKUP_AGE=-1
if [ -n "$LATEST_BACKUP" ]; then
  BACKUP_AGE=$(( ( $(date +%s) - $(stat -c %Y "$LATEST_BACKUP") ) / 86400 ))
  ok "Latest backup: $LATEST_BACKUP (${BACKUP_AGE} day(s) old)"
else
  warn "No backup found in $APP/backups"
fi

log "Evaluating overall status"
STATUS=OK
[ -n "$BAD" ] && STATUS=ATTENTION
[ "$S5" -gt 0 ] && STATUS=ATTENTION
[ "$APP_ERRORS" -gt 0 ] && STATUS=ATTENTION
[ "$DISK" -ge 85 ] && STATUS=ATTENTION
{ [ "$BACKUP_AGE" -lt 0 ] || [ "$BACKUP_AGE" -gt 2 ]; } && STATUS=ATTENTION
if [ "$STATUS" = OK ]; then ok "Overall status: OK"; else warn "Overall status: ATTENTION"; fi

log "Writing report"
{
echo "Report date: $TODAY"
echo "Summary: $STATUS | 5xx: $S5 | 429: $S429 | app errors: $APP_ERRORS | disk: ${DISK}% | backup age: ${BACKUP_AGE}d"
echo
log "Writing section: System"
echo "== System =="
uptime -p
free -h | sed -n '1,2p'
df -h / | tail -n1
echo "Inactive services:${BAD:- none}"
echo "Pending apt upgrades: $UPGRADES"
[ -f /var/run/reboot-required ] && echo "REBOOT REQUIRED"
echo
log "Writing section: Traffic"
echo "== Traffic (last $DAYS days) =="
echo "Requests: $TOTAL | 404: $S404 | 429: $S429 | 5xx: $S5"
echo "-- Top 5xx URLs --"
awk '$9 ~ /^5/ {print $9, $7}' "$ACCESS" | sort | uniq -c | sort -rn | head -n 10
echo "-- Top 404 URLs --"
awk '$9 == 404 {print $7}' "$ACCESS" | sort | uniq -c | sort -rn | head -n 10
echo
log "Writing section: Backups"
echo "== Backups =="
echo "Latest: ${LATEST_BACKUP:-none found}"
echo
log "Writing section: SSH"
echo "== SSH =="
echo "Invalid-user attempts: $SSH_PROBES"
echo
log "Writing section: App errors (journal)"
echo "== App errors (journal, last $DAYS days) =="
journalctl -u osw --since "$DAYS days ago" -q --no-pager | grep -E "ERROR|CRITICAL|Traceback" | tail -n 50
echo
log "Writing section: App log errors"
echo "== App log errors (may include older entries) =="
cat "$APP"/logs/*.log 2>/dev/null | grep -E "ERROR|CRITICAL" | tail -n 50
echo
log "Writing section: nginx errors"
echo "== nginx errors =="
tail -n 30 /var/log/nginx/error.log
} > "$TMP"

if mv "$TMP" "$OUT"; then
  chmod 600 "$OUT"
  ln -sfn "$OUT" "$OUT_DIR/latest.txt"
  ok "Report saved: $OUT ($(wc -l < "$OUT") lines, $(stat -c %s "$OUT") bytes)"
  ok "latest.txt now points to $OUT"
else
  warn "Failed to save report to $OUT"
  exit 1
fi

DELETED=$(find "$OUT_DIR" -name 'osw-report-*.txt' -mtime +60 -print -delete | wc -l)
ok "Old reports removed (older than 60 days): $DELETED"

log "Finished"
