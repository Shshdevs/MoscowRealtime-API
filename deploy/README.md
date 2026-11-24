# Deployment for moscowrealtime-api.sytes.net

This deployment runs the API behind nginx and serves ACME HTTP-01 challenges for Certbot. The API is not published directly on the host.

## Before starting

1. Point the No-IP A record for `moscowrealtime-api.sytes.net` to the server's public IPv4 address. If the address changes, configure a No-IP Dynamic Update Client on the host or router.
2. Allow inbound TCP ports 80 and 443 in the host firewall and forward them from the router to this server. The router must have a public address; CGNAT prevents inbound access without a public IP, tunnel, or provider-side port forwarding.
3. Create the project `.env` from [`.env.example`](../.env.example) and fill in the required Supabase and Yandex Cloud values. Add the Firebase service account key, YOLO weights, and location metadata under `sensitive/` as described in the root [README](../README.md).
4. Export `LETSENCRYPT_EMAIL` for certificate notifications.

## Start

From the repository root, set the contact email and run:

```sh
export LETSENCRYPT_EMAIL="you@example.com"
sh deploy/issue-certificate.sh
```

The script starts the API and HTTP nginx, obtains the certificate under `deploy/certbot/conf`, enables the HTTPS server, checks the nginx configuration, and reloads nginx. It is safe to run again to renew or recover setup.

```sh
sh deploy/renew-certificate.sh
```

Schedule `sh deploy/renew-certificate.sh` daily on the host with cron or systemd. Certbot renews only when the certificate is due; the script reloads nginx afterward so it reads any renewed certificate. Certificate issuance and renewal require working DNS and external access to port 80. The existing `docker-compose.yml` is unchanged; use only the deployment compose file for production so the API's old port mapping does not expose it directly.

To install a daily 03:17 cron job for the current checkout, run this on the deployment host from the repository root:

```sh
sh deploy/install-renewal-cron.sh
```

The job writes output to `deploy/certbot-renewal.log`. Cron and Docker must be available to the account that runs the installer.
