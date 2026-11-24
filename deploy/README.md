# Production deployment

This project uses its own nginx and Certbot containers. Stop any other service that publishes host ports 80 or 443 before the first deployment. Nginx handles HTTPS for `moscowrealtime-api.sytes.net`; the API container remains private on the Compose network.

## First deployment

1. Point the No-IP A record for `moscowrealtime-api.sytes.net` to the server's public IPv4 address. If the address changes, configure a No-IP Dynamic Update Client on the host or router.
2. Allow inbound TCP ports 80 and 443 in the host firewall and forward them from the router to this server. The router must have a public address; CGNAT prevents inbound access without a public IP, tunnel, or provider-side port forwarding.
3. Create the project `.env` from [`.env.example`](../.env.example) and fill in the required Supabase and Yandex Cloud values. Set `TIMEPAD_API_TOKEN` with only the `view_events` permission. Add the Firebase service account key, YOLO weights, and location metadata under `sensitive/` as described in the root [README](../README.md). Do not copy the token into the mobile application or commit the `.env` file.
4. From the repository root, export the certificate contact email and run:

```sh
export LETSENCRYPT_EMAIL="you@example.com"
sh deploy/issue-certificate.sh
```

The script builds and starts the API and HTTP nginx, obtains a Let's Encrypt certificate with Certbot, enables HTTPS, validates nginx, and reloads it. It also creates the persistent certificate files under `deploy/certbot/`.

## Updating the application

From the repository root, run:

```sh
sh deploy/deploy.sh
```

This rebuilds and replaces only the API container. Nginx remains running and continues to serve the certificate.

## Certificate renewal

Install the daily renewal job once:

```sh
sh deploy/install-renewal-cron.sh
```

The job runs Certbot daily and reloads nginx. Certbot renews only when the certificate is due. Renewal output is written to `deploy/certbot-renewal.log`.

To check the deployment:

```sh
docker compose -f deploy/compose.yml ps
docker compose -f deploy/compose.yml logs --tail=100 api nginx
curl -fsS https://moscowrealtime-api.sytes.net/api/health
```
