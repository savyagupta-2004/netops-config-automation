#!/bin/sh
# Brings up the 3-router lab.
#
# Compose's own multi-network attach order for a service is NOT deterministic
# (verified empirically - the same service can come up with its extra
# networks on different ethN each run). So each router only joins the mgmt
# network via docker-compose.yml, and this script creates the point-to-point
# link networks and attaches them per router sequentially and explicitly,
# which *is* deterministic: each `docker network connect` call takes the
# next free ethN in call order. That guarantees eth1/eth2 line up with what
# host_vars/*.yaml (and therefore the rendered FRR config) expect.
set -e

cd "$(dirname "$0")/.."

docker compose up -d --build

for net_subnet in "link_r1_r2:10.12.0.0/29" "link_r1_r3:10.13.0.0/29" "link_r2_r3:10.23.0.0/29"; do
  name="${net_subnet%%:*}"
  subnet="${net_subnet##*:}"
  if ! docker network inspect "$name" >/dev/null 2>&1; then
    docker network create --driver bridge --subnet "$subnet" "$name" >/dev/null
  fi
done

echo "Attaching point-to-point links..."
docker network connect --ip 10.12.0.2 link_r1_r2 r1
docker network connect --ip 10.13.0.2 link_r1_r3 r1

docker network connect --ip 10.12.0.3 link_r1_r2 r2
docker network connect --ip 10.23.0.2 link_r2_r3 r2

docker network connect --ip 10.13.0.3 link_r1_r3 r3
docker network connect --ip 10.23.0.3 link_r2_r3 r3

echo "Lab is up. r1/r2/r3 reachable on 127.0.0.1:2201/2202/2203 (root/frrlab123)."
