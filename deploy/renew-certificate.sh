#!/bin/sh
set -eu

docker compose -f deploy/compose.yml run --rm certbot renew --webroot -w /var/www/certbot
docker compose -f deploy/compose.yml exec -T nginx nginx -s reload
