#!/bin/sh
set -eu

project_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
entry="17 3 * * * cd '$project_dir' && sh deploy/renew-certificate.sh >> deploy/certbot-renewal.log 2>&1"
current_crontab=$(crontab -l 2>/dev/null || true)

if printf '%s\n' "$current_crontab" | grep -Fq "sh deploy/renew-certificate.sh"; then
    exit 0
fi

printf '%s\n%s\n' "$current_crontab" "$entry" | crontab -
