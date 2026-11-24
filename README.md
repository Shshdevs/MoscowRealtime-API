# Moscow Realtime API

FastAPI service for recognizing Moscow landmarks in images with a local YOLO model, finding nearby locations, and generating landmark descriptions with Yandex Cloud AI Studio.

## Requirements

- Python 3.11 or Docker with Docker Compose
- Firebase service account credentials
- Supabase project and storage bucket named `analyzed-images`
- Yandex Cloud AI Studio API key, folder ID, and model
- Timepad API token with only the `view_events` permission
- YOLO weights and the matching location metadata

## Configuration

Create a local environment file from the example:

```sh
cp .env.example .env
```

Set the Supabase, Yandex, and `TIMEPAD_API_TOKEN` values in `.env`. The Timepad token is read only by this server and must not be copied into the mobile app or its build configuration. Grant only `view_events`. The Yandex model URI is built as `gpt://<YANDEX_CLOUD_FOLDER>/<YANDEX_CLOUD_MODEL>`. Set `CORS_ALLOWED_ORIGINS` to a comma-separated list of allowed origins and `FORWARDED_ALLOW_IPS` to the IP addresses of trusted proxies.

Place these runtime files in `sensitive/`:

- `serviceAccountKey.json` — Firebase service account key
- `best.pt` — YOLO model weights
- `locations.json` — mapping from YOLO class labels to location IDs and names

The `sensitive/` directory is excluded from Git. Keep credentials and model files out of commits.

## Run locally

Install dependencies and start the API:

```sh
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m app.main
```

The API listens on port 80 by default.

## Run with Docker Compose

```sh
docker compose up --build -d
```

The local Compose configuration publishes the API on port 4000. View logs with `docker compose logs -f moscow-realtime-server` and stop it with `docker compose down`.

## API endpoints

All endpoints use the `/api` prefix.

### Health check

```sh
curl http://localhost:4000/api/health
```

### Find the closest location

```sh
curl --get http://localhost:4000/api/closest \
  --data-urlencode 'lat=55.7558' \
  --data-urlencode 'lon=37.6173'
```

### Get events

```sh
curl 'http://localhost:4000/api/events?limit=100&skip=0'
curl --get http://localhost:4000/api/events/nearby --data-urlencode 'lat=55.7558' --data-urlencode 'lon=37.6173' --data-urlencode 'radius=1000'
curl http://localhost:4000/api/events/12345
```

Event responses use provider-neutral fields. The nearby endpoint scans at most 500 upcoming Moscow events and returns only entries that include coordinates within the requested radius. The source currently provides coordinates for only a portion of events, so nearby results may be incomplete.

### Analyze an image

`imgPath` is the path of an image already stored in the Supabase `analyzed-images` bucket. `userId` is optional.

```sh
curl -X POST http://localhost:4000/api/analyze \
  -F 'imgPath=uploads/landmark.jpg' \
  -F 'userId=example-user'
```

## Production deployment

See [deploy/README.md](deploy/README.md) for the nginx, HTTPS, and certificate renewal setup.
