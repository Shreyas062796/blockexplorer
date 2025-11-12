#!/usr/bin/env bash

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${REPO_ROOT}"

TAG="$(git rev-parse --short HEAD)"
IMAGE="eth-balance:${TAG}"
CONTAINER_NAME="eth-balance-${TAG}"

cleanup() {
  docker rm -f "${CONTAINER_NAME}" >/dev/null 2>&1 || true
}

trap cleanup EXIT

docker build -t "${IMAGE}" .

cleanup

docker run -d \
  --name "${CONTAINER_NAME}" \
  -e INFURA_ENDPOINT="https://mainnet.infura.io/v3/f3c095656381439aa1acb1722d9c62f2" \
  -p 8080:8080 \
  "${IMAGE}"

echo "Waiting for the service to become available..."
for _ in $(seq 1 20); do
  if curl -fsS "http://localhost:8080/address/balance/0xc94770007dda54cF92009BFF0dE90c06F603a09f" >/dev/null; then
    break
  fi
  sleep 1
done

echo "Fetching balance:"
curl "http://localhost:8080/address/balance/0xc94770007dda54cF92009BFF0dE90c06F603a09f"


