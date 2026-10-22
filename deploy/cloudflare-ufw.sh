#!/usr/bin/env bash
set -euo pipefail

TMP=$(mktemp)
trap 'rm -f "$TMP"' EXIT

{ curl -fsS https://www.cloudflare.com/ips-v4; echo; curl -fsS https://www.cloudflare.com/ips-v6; } \
  | grep -E '^[0-9a-fA-F:.]+/[0-9]+$' > "$TMP"

COUNT=$(wc -l < "$TMP")
if [ "$COUNT" -lt 20 ]; then
  echo "Only $COUNT ranges downloaded, aborting" >&2
  exit 1
fi

while read -r ip; do
  ufw allow proto tcp from "$ip" to any port 443 comment 'cloudflare'
done < "$TMP"

echo "Cloudflare ranges allowed on 443: $COUNT"
