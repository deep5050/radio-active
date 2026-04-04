#!/usr/bin/env bash
# Build and run 'make all' (build, format, lint, install) in official Python Docker images.
# Usage:
#   ./scripts/docker-make-all.sh              # default matrix
#   PYTHON_VERSIONS="3.10 3.12" ./scripts/docker-make-all.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

IMAGE_NAME="${IMAGE_NAME:-radio-active-test}"
DOCKERFILE="${DOCKERFILE:-docker/Dockerfile.test}"
# Test on all modern supported Python versions
# Test on all modern supported Python versions
PYTHON_VERSIONS="${PYTHON_VERSIONS:-3.8 3.9 3.10 3.11 3.12 3.13}"

for ver in $PYTHON_VERSIONS; do
  echo "========== Testing 'make' on Python ${ver} =========="
  docker build \
    -f "$DOCKERFILE" \
    --build-arg "PYTHON_VERSION=${ver}" \
    -t "${IMAGE_NAME}:py${ver}" \
    "$ROOT"
  
  # Run the build, install, and basic CLI commands to verify everything works
  docker run --rm \
    -e HOME=/tmp/radioactive-test-home \
    "${IMAGE_NAME}:py${ver}" \
    bash -c "make all && radioactive --version && radio --help"
  
  # Clean up the built image to save disk space
  echo "Cleaning up image for Python ${ver}..."
  docker rmi "${IMAGE_NAME}:py${ver}"
  
  echo "========== PASSED Python ${ver} =========="
done

echo "All requested Python versions passed build and install tests."
