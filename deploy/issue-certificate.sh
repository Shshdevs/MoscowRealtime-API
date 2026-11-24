#!/bin/sh
set -eu

domain="moscowrealtime-api.sytes.net"
email="${LETSENCRYPT_EMAIL:?Set LETSENCRYPT_EMAIL in the environment}"

docker compose -f deploy/compose.yml up -d --build api nginx
docker compose -f deploy/compose.yml run --rm certbot certonly \
  --webroot -w /var/www/certbot \
  --email "$email" --agree-tos --no-eff-email \
  -d "$domain"

cp deploy/nginx/tls.conf deploy/nginx/conf.d/tls.conf
docker compose -f deploy/compose.yml exec nginx nginx -t
docker compose -f deploy/compose.yml exec nginx nginx -s reload
