# Moscow Realtime API

Flask API for recognizing Moscow landmarks in images with a local YOLO model, finding nearby locations, and generating landmark descriptions with Yandex Cloud AI Studio.

## Requirements

- Python 3.11 or Docker with Docker Compose
- Firebase service account credentials
- Supabase project and storage bucket named `analyzed-images`
- Yandex Cloud AI Studio API key, folder ID, and model
- YOLO weights and the matching location metadata

## Configuration

Create a local environment file from the example:

```sh
cp .env.example .env
```

Set the Supabase and Yandex values in `.env`. The Yandex model URI is built as `gpt://<YANDEX_CLOUD_FOLDER>/<YANDEX_CLOUD_MODEL>`.

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
python main.py
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

### Analyze an image

`imgPath` is the path of an image already stored in the Supabase `analyzed-images` bucket. `userId` is optional.

```sh
curl -X POST http://localhost:4000/api/analyze \
  -F 'imgPath=uploads/landmark.jpg' \
  -F 'userId=example-user'
```

## Production deployment

See [deploy/README.md](deploy/README.md) for the nginx, HTTPS, and certificate renewal setup.
