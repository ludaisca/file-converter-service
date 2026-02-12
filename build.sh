#!/bin/bash
# ============================================================================
# Docker Build Script - Multi-Version Support
# ============================================================================
# Usage:
#   ./build.sh [version] [options]
#
# Versions:
#   full       - Build with Dockerfile (full version, 2.5GB)
#   optimized  - Build with Dockerfile.optimized (recommended, 900MB)
#   minimal    - Build with Dockerfile.minimal (ultra-light, 500MB)
#   all        - Build all versions
#
# Options:
#   --no-cache    Force rebuild without cache
#   --test        Run tests after build
#   --push        Push to registry (requires login)
# ============================================================================

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
IMAGE_NAME="file-converter"
VERSION="2.1.0"
REGISTRY=""  # Set your registry here (e.g., "docker.io/username")

# Parse arguments
VERSION_TYPE="${1:-optimized}"
NO_CACHE=""
RUN_TESTS=false
PUSH_IMAGE=false

shift || true
while [[ $# -gt 0 ]]; do
    case $1 in
        --no-cache)
            NO_CACHE="--no-cache"
            shift
            ;;
        --test)
            RUN_TESTS=true
            shift
            ;;
        --push)
            PUSH_IMAGE=true
            shift
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# Functions
print_header() {
    echo -e "${BLUE}======================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}======================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}➡ $1${NC}"
}

build_image() {
    local version=$1
    local dockerfile=$2
    local tag="${IMAGE_NAME}:${version}"
    
    print_header "Building ${version} version"
    print_info "Dockerfile: ${dockerfile}"
    print_info "Tag: ${tag}"
    
    # Build
    echo ""
    if docker build ${NO_CACHE} -f "${dockerfile}" -t "${tag}" .; then
        print_success "Build completed: ${tag}"
        
        # Show image size
        SIZE=$(docker images "${tag}" --format "{{.Size}}")
        print_info "Image size: ${SIZE}"
        
        # Tag with version
        docker tag "${tag}" "${IMAGE_NAME}:${VERSION}-${version}"
        print_success "Tagged: ${IMAGE_NAME}:${VERSION}-${version}"
        
        return 0
    else
        print_error "Build failed for ${version}"
        return 1
    fi
}

test_image() {
    local tag=$1
    
    print_header "Testing ${tag}"
    
    # Start container
    print_info "Starting container..."
    CONTAINER_ID=$(docker run -d -p 5001:5000 "${tag}")
    
    # Wait for service to be ready
    print_info "Waiting for service to be ready..."
    sleep 10
    
    # Test health endpoint
    print_info "Testing /health endpoint..."
    if curl -sf http://localhost:5001/health > /dev/null; then
        print_success "Health check passed"
    else
        print_error "Health check failed"
        docker logs "${CONTAINER_ID}"
        docker stop "${CONTAINER_ID}" > /dev/null 2>&1
        docker rm "${CONTAINER_ID}" > /dev/null 2>&1
        return 1
    fi
    
    # Test formats endpoint
    print_info "Testing /formats endpoint..."
    if curl -sf http://localhost:5001/formats > /dev/null; then
        print_success "Formats endpoint passed"
    else
        print_error "Formats endpoint failed"
    fi
    
    # Cleanup
    print_info "Cleaning up..."
    docker stop "${CONTAINER_ID}" > /dev/null 2>&1
    docker rm "${CONTAINER_ID}" > /dev/null 2>&1
    
    print_success "Tests completed for ${tag}"
    return 0
}

push_image() {
    local tag=$1
    
    if [ -z "${REGISTRY}" ]; then
        print_error "REGISTRY not set. Edit build.sh and set REGISTRY variable."
        return 1
    fi
    
    print_header "Pushing ${tag}"
    
    # Tag for registry
    local registry_tag="${REGISTRY}/${tag}"
    docker tag "${tag}" "${registry_tag}"
    
    # Push
    print_info "Pushing to ${registry_tag}..."
    if docker push "${registry_tag}"; then
        print_success "Pushed: ${registry_tag}"
        return 0
    else
        print_error "Push failed"
        return 1
    fi
}

show_summary() {
    print_header "Build Summary"
    echo ""
    docker images | grep "${IMAGE_NAME}" | head -10
    echo ""
    print_info "To run an image:"
    echo "  docker run -p 5000:5000 ${IMAGE_NAME}:[version]"
    echo ""
    print_info "To use with docker-compose:"
    echo "  Edit docker-compose.yml and change 'dockerfile' to desired version"
    echo ""
}

# Main execution
print_header "File Converter - Docker Build Script"
echo "Version: ${VERSION}"
echo "Build type: ${VERSION_TYPE}"
echo ""

case "${VERSION_TYPE}" in
    full)
        build_image "full" "Dockerfile" && \
        [ "${RUN_TESTS}" = true ] && test_image "${IMAGE_NAME}:full"
        [ "${PUSH_IMAGE}" = true ] && push_image "${IMAGE_NAME}:full"
        ;;
    
    optimized)
        build_image "optimized" "Dockerfile.optimized" && \
        [ "${RUN_TESTS}" = true ] && test_image "${IMAGE_NAME}:optimized"
        [ "${PUSH_IMAGE}" = true ] && push_image "${IMAGE_NAME}:optimized"
        ;;
    
    minimal)
        build_image "minimal" "Dockerfile.minimal" && \
        [ "${RUN_TESTS}" = true ] && test_image "${IMAGE_NAME}:minimal"
        [ "${PUSH_IMAGE}" = true ] && push_image "${IMAGE_NAME}:minimal"
        ;;
    
    all)
        print_info "Building all versions..."
        echo ""
        
        build_image "minimal" "Dockerfile.minimal"
        [ "${RUN_TESTS}" = true ] && test_image "${IMAGE_NAME}:minimal"
        
        echo ""
        build_image "optimized" "Dockerfile.optimized"
        [ "${RUN_TESTS}" = true ] && test_image "${IMAGE_NAME}:optimized"
        
        echo ""
        build_image "full" "Dockerfile"
        [ "${RUN_TESTS}" = true ] && test_image "${IMAGE_NAME}:full"
        ;;
    
    *)
        print_error "Unknown version: ${VERSION_TYPE}"
        echo ""
        echo "Usage: $0 [full|optimized|minimal|all] [--no-cache] [--test] [--push]"
        exit 1
        ;;
esac

echo ""
show_summary

print_success "Done!"
