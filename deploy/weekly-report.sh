#!/usr/bin/env bash
set -uo pipefail

APP=/srv/osw
OUT_DIR=$APP/reports
DAYS=7
TODAY=$(date +%F)
OUT=$OUT_DIR/osw-report-$TODAY.txt
TMP=$(mktemp)
ACCESS=$(mktemp)
trap 'rm -f "$TMP" "$ACCESS"' EXIT

mkdir -p "$OUT_DIR"
chmod 700 "$OUT_DIR"

DATES=$(for i in $(seq 0 $((DAYS-1))); do date -d "-$i day" +%d/%b/%Y; done | paste -sd'|')
zcat -f /var/log/nginx/access.log* 2>/dev/null | grep -E "\[($DATES):" > "$ACCESS"

TOTAL=$(wc -l < "$ACCESS")
S5=$(awk '$9 ~ /^5/' "$ACCESS" | wc -l)
S429=$(awk '$9 == 429' "$ACCESS" | wc -l)
S404=$(awk '$9 == 404' "$ACCESS" | wc -l)
APP_ERRORS=$(journalctl -u osw --since "$DAYS days ago" -q --no-pager | grep -cE "ERROR|CRITICAL|Traceback")
SSH_PROBES=$(journalctl -u ssh --since "$DAYS days ago" -q --no-pager | grep -c "Invalid user")
DISK=$(df --output=pcent / | tail -n1 | tr -dc '0-9')
UPGRADES=$(apt list --upgradable 2>/dev/null | grep -c "upgradable from")

BAD=""
for s in osw nginx; do
  [ "$(systemctl is-active "$s")" = active ] || BAD="$BAD $s"
done

LATEST_BACKUP=$(ls -t "$APP"/backups/app-*.db 2>/dev/null | head -n1)
BACKUP_AGE=-1
[ -n "$LATEST_BACKUP" ] && BACKUP_AGE=$(( ( $(date +%s) - $(stat -c %Y "$LATEST_BACKUP") ) / 86400 ))

STATUS=OK
[ -n "$BAD" ] && STATUS=ATTENTION
[ "$S5" -gt 0 ] && STATUS=ATTENTION
[ "$APP_ERRORS" -gt 0 ] && STATUS=ATTENTION
[ "$DISK" -ge 85 ] && STATUS=ATTENTION
{ [ "$BACKUP_AGE" -lt 0 ] || [ "$BACKUP_AGE" -gt 2 ]; } && STATUS=ATTENTION

{
echo "Report date: $TODAY"
echo "Summary: $STATUS | 5xx: $S5 | 429: $S429 | app errors: $APP_ERRORS | disk: ${DISK}% | backup age: ${BACKUP_AGE}d"
echo
echo "== System =="
uptime -p
free -h | sed -n '1,2p'
df -h / | tail -n1
echo "Inactive services:${BAD:- none}"
echo "Pending apt upgrades: $UPGRADES"
[ -f /var/run/reboot-required ] && echo "REBOOT REQUIRED"
echo
echo "== Traffic (last $DAYS days) =="
echo "Requests: $TOTAL | 404: $S404 | 429: $S429 | 5xx: $S5"
echo "-- Top 5xx URLs --"
awk '$9 ~ /^5/ {print $9, $7}' "$ACCESS" | sort | uniq -c | sort -rn | head -n 10
echo "-- Top 404 URLs --"
awk '$9 == 404 {print $7}' "$ACCESS" | sort | uniq -c | sort -rn | head -n 10
echo
echo "== Backups =="
echo "Latest: ${LATEST_BACKUP:-none found}"
echo
echo "== SSH =="
echo "Invalid-user attempts: $SSH_PROBES"
echo
echo "== App errors (journal, last $DAYS days) =="
journalctl -u osw --since "$DAYS days ago" -q --no-pager | grep -E "ERROR|CRITICAL|Traceback" | tail -n 50
echo
echo "== App log errors (may include older entries) =="
cat "$APP"/logs/*.log 2>/dev/null | grep -E "ERROR|CRITICAL" | tail -n 50
echo
echo "== nginx errors =="
tail -n 30 /var/log/nginx/error.log
} > "$TMP"

mv "$TMP" "$OUT"
chmod 600 "$OUT"
ln -sfn "$OUT" "$OUT_DIR/latest.txt"
find "$OUT_DIR" -name 'osw-report-*.txt' -mtime +60 -delete
