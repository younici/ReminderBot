#!/usr/bin/env bash
set -euo pipefail

REPO_URL="${REPO_URL:-https://github.com/younici/ReminderBot.git}"
APP_DIR="${APP_DIR:-/opt/reminderbot}"

echo "Using repo: $REPO_URL"
echo "Target dir: $APP_DIR"

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker is required. Please install Docker and rerun." >&2
  exit 1
fi

if ! command -v docker compose >/dev/null 2>&1; then
  echo "Docker Compose v2 is required (docker compose). Please install and rerun." >&2
  exit 1
fi

if [ -d "$APP_DIR/.git" ]; then
  git -C "$APP_DIR" fetch --all
  git -C "$APP_DIR" reset --hard origin/$(git -C "$APP_DIR" rev-parse --abbrev-ref origin/HEAD | sed 's|origin/||')
else
  mkdir -p "$APP_DIR"
  git clone "$REPO_URL" "$APP_DIR"
fi

cd "$APP_DIR"

if [ ! -f .env ]; then
  cp .env.example .env
  echo "Edit .env with your tokens before starting." >&2
fi

docker compose down
docker compose up -d --build

echo "Deployment complete. Logs: docker compose logs -f"
