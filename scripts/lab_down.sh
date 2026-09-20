#!/bin/sh
set -e
cd "$(dirname "$0")/.."
docker compose down
for name in link_r1_r2 link_r1_r3 link_r2_r3; do
  docker network rm "$name" >/dev/null 2>&1 || true
done
