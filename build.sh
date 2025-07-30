#!/bin/bash

# Docker build script for GORU project

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    print_success "Docker is running"
}

# Function to build development image
build_dev() {
    print_status "Building development image..."
    docker build -t goru-backend:dev --target development ./backend
    print_success "Development image built successfully"
}

# Function to build production image
build_prod() {
    print_status "Building production image..."
    docker build -t goru-backend:prod --target production ./backend
    print_success "Production image built successfully"
}

# Function to build test image
build_test() {
    print_status "Building test image..."
    docker build -t goru-backend:test --target test ./backend
    print_success "Test image built successfully"
}

# Function to build all images
build_all() {
    print_status "Building all images..."
    build_dev
    build_prod
    build_test
    print_success "All images built successfully"
}

# Function to run tests
run_tests() {
    print_status "Running tests..."
    docker-compose --profile test up test --build --abort-on-container-exit
    print_success "Tests completed"
}

# Function to start development environment
start_dev() {
    print_status "Starting development environment..."
    docker-compose up -d
    print_success "Development environment started"
}

# Function to start production environment
start_prod() {
    print_status "Starting production environment..."
    docker-compose -f docker-compose.prod.yml up -d
    print_success "Production environment started"
}

# Function to stop all containers
stop_all() {
    print_status "Stopping all containers..."
    docker-compose down
    docker-compose -f docker-compose.prod.yml down
    print_success "All containers stopped"
}

# Function to clean up
cleanup() {
    print_status "Cleaning up Docker resources..."
    docker system prune -f
    docker volume prune -f
    print_success "Cleanup completed"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  dev-build     Build development image"
    echo "  prod-build    Build production image"
    echo "  test-build    Build test image"
    echo "  build-all     Build all images"
    echo "  test          Run tests"
    echo "  dev           Start development environment"
    echo "  prod          Start production environment"
    echo "  stop          Stop all containers"
    echo "  cleanup       Clean up Docker resources"
    echo "  help          Show this help message"
    echo ""
}

# Main script
case "${1:-help}" in
    "dev-build")
        check_docker
        build_dev
        ;;
    "prod-build")
        check_docker
        build_prod
        ;;
    "test-build")
        check_docker
        build_test
        ;;
    "build-all")
        check_docker
        build_all
        ;;
    "test")
        check_docker
        run_tests
        ;;
    "dev")
        check_docker
        start_dev
        ;;
    "prod")
        check_docker
        start_prod
        ;;
    "stop")
        stop_all
        ;;
    "cleanup")
        cleanup
        ;;
    "help"|*)
        show_usage
        ;;
esac 