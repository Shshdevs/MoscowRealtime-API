#!/bin/sh
set -eu

project_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$project_dir"

docker compose -f deploy/compose.yml up -d --build api
docker compose -f deploy/compose.yml ps api
