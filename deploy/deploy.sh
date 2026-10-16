#!/usr/bin/env bash
# Deploy Open Source Wizard from your laptop to the droplet.
# Usage: deploy/deploy.sh [--push] [--force]
#   --push   push local commits to origin before deploying
#   --force  restart even if the server is already up to date
set -euo pipefail

HOST="${OSW_HOST:-osw}"                      # ssh alias from ~/.ssh/config
BRANCH="${OSW_BRANCH:-main}"
APP_DIR="${OSW_APP_DIR:-/srv/osw}"
SERVICE="${OSW_SERVICE:-osw}"
PORT="${OSW_PORT:-3001}"
SITE_URL="${OSW_SITE_URL:-https://opensourcewizard.com}"

PUSH=0
FORCE=0
for arg in "$@"; do
  case "$arg" in
    --push)  PUSH=1 ;;
    --force) FORCE=1 ;;
    -h|--help) sed -n '2,6p' "$0"; exit 0 ;;
    *) echo "Unknown option: $arg" >&2; exit 2 ;;
  esac
done

say() { printf '\n==> %s\n' "$*"; }
die() { printf 'ERROR: %s\n' "$*" >&2; exit 1; }

cd "$(git rev-parse --show-toplevel)" || die "Not inside a git repository"

say "Checking local repository"
[[ "$(git rev-parse --abbrev-ref HEAD)" == "$BRANCH" ]] \
  || die "You are not on '$BRANCH'. Switch branches or set OSW_BRANCH."
[[ -z "$(git status --porcelain --untracked-files=no)" ]] \
  || die "You have uncommitted changes. Commit or stash them first."

git fetch --quiet origin "$BRANCH"
AHEAD="$(git rev-list --count "origin/$BRANCH..HEAD")"
if [[ "$AHEAD" -gt 0 ]]; then
  if [[ "$PUSH" -eq 1 ]]; then
    say "Pushing $AHEAD commit(s) to origin/$BRANCH"
    git push origin "$BRANCH"
  else
    die "$AHEAD local commit(s) not pushed. Push them or run with --push."
  fi
fi
echo "Deploying $(git rev-parse --short HEAD): $(git log -1 --pretty=%s)"

say "Updating $HOST:$APP_DIR"
ssh "$HOST" bash -s -- "$APP_DIR" "$BRANCH" "$SERVICE" "$PORT" "$FORCE" <<'REMOTE'
set -euo pipefail
APP_DIR="$1"; BRANCH="$2"; SERVICE="$3"; PORT="$4"; FORCE="$5"

cd "$APP_DIR"
OLD="$(git rev-parse HEAD)"
BACKUP=""

rollback() {
  echo "!! Deploy failed. Rolling code back to ${OLD:0:7}" >&2
  git reset --hard "$OLD" >&2
  sudo -n systemctl restart "$SERVICE" >&2 || true
  [[ -n "$BACKUP" ]] && echo "!! Database backup from before the migration: $BACKUP" >&2
  echo "!! Migrations are NOT undone automatically. Restore the backup if the schema changed." >&2
}
trap rollback ERR

git fetch --quiet origin "$BRANCH"
NEW="$(git rev-parse "origin/$BRANCH")"

if [[ "$OLD" == "$NEW" && "$FORCE" -ne 1 ]]; then
  echo "Server already at ${OLD:0:7}. Nothing to deploy (use --force to restart anyway)."
  trap - ERR
  exit 0
fi

CHANGED="$(git diff --name-only "$OLD" "$NEW")"
echo "Updating ${OLD:0:7} -> ${NEW:0:7}"
git merge --ff-only "origin/$BRANCH"

if grep -qx 'requirements.txt' <<<"$CHANGED"; then
  echo "requirements.txt changed: installing dependencies"
  ./venv/bin/pip install --no-cache-dir -r requirements.txt
fi

if grep -q '^migrations/' <<<"$CHANGED"; then
  echo "Migrations changed: backing up database, then upgrading"
  if [[ -f app.db ]]; then
    mkdir -p backups
    BACKUP="$APP_DIR/backups/pre-deploy-$(date +%F-%H%M%S).db"
    sqlite3 app.db ".backup '$BACKUP'"
    echo "Backup written to $BACKUP"
  fi
  FLASK_APP=run.py ./venv/bin/flask db upgrade
fi

if grep -q '^deploy/osw.nginx.conf$' <<<"$CHANGED"; then
  echo "NOTE: deploy/osw.nginx.conf changed. Copy it to /etc/nginx/sites-available/osw and reload nginx manually."
fi
if grep -q '^deploy/osw.service$' <<<"$CHANGED"; then
  echo "NOTE: deploy/osw.service changed. Copy it to /etc/systemd/system/ and run daemon-reload manually."
fi

echo "Restarting $SERVICE"
sudo -n systemctl restart "$SERVICE"

echo "Waiting for the app on 127.0.0.1:$PORT"
for i in $(seq 1 20); do
  if curl -fsS -o /dev/null "http://127.0.0.1:$PORT/"; then
    echo "App is healthy after ${i}s"
    trap - ERR
    exit 0
  fi
  sleep 1
done
echo "Health check failed" >&2
false
REMOTE

say "Checking $SITE_URL"
CODE="$(curl -s -o /dev/null -w '%{http_code}' --max-time 20 "$SITE_URL" || true)"
echo "HTTP $CODE from $SITE_URL"
[[ "$CODE" == "200" ]] || die "Public site did not return 200. Check Cloudflare and: ssh $HOST 'journalctl -u $SERVICE -n 50 --no-pager'"

say "Deploy finished"
