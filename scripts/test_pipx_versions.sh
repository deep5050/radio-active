#!/bin/bash

# Configuration: List of Python versions to test
PYTHON_VERSIONS=("3.8" "3.9" "3.10" "3.11" "3.12")
TAG_PREFIX="radio-active-pipx-test"

# Get project root from script location
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "Starting pipx installation tests on several Python versions..."
echo "Project Root: $PROJECT_ROOT"

# Cleanup function to be called on script exit or interrupt
cleanup() {
    if [[ -n "$tag" ]]; then
        echo "Cleaning up image $tag..."
        docker rmi "$tag" 2>/dev/null || true
    fi
    exit
}

# Trap signals for cleanup
trap cleanup SIGINT SIGTERM EXIT

failed_versions=()

for version in "${PYTHON_VERSIONS[@]}"; do
    echo "--------------------------------------------------------"
    echo "Testing on Python $version..."
    echo "--------------------------------------------------------"
    
    tag="${TAG_PREFIX}:${version}"
    
    # Build docker image while passing PYTHON_VERSION as build arg
    # Running build from project root so it can copy the source
    if docker build -t "$tag" \
        -f "$PROJECT_ROOT/docker/Dockerfile.pipx_test" \
        --build-arg PYTHON_VERSION="$version" \
        "$PROJECT_ROOT"; then
        echo "✅ Test PASSED for Python $version"
    else
        echo "❌ Test FAILED for Python $version"
        failed_versions+=("$version")
    fi

    # Cleanup: Remove the image after testing to save space
    echo "Cleaning up image $tag..."
    docker rmi "$tag" 2>/dev/null || echo "Warning: Failed to remove image $tag"
    tag=""
done

echo "--------------------------------------------------------"
if [ ${#failed_versions[@]} -eq 0 ]; then
    echo "Summarizing results: ALL TESTS PASSED! 🎉"
    exit 0
else
    echo "Summarizing results: SOME TESTS FAILED! ❌"
    echo "Failed versions: ${failed_versions[*]}"
    exit 1
fi
