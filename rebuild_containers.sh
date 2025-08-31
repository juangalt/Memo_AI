#!/bin/bash

# Rebuild Containers Script for Memo AI Coach
# Usage: ./rebuild_containers.sh [frontend|backend|all]
# If no parameter is passed, rebuilds all containers

set -e  # Exit on any error

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
}

# Function to check if docker-compose is available
check_docker_compose() {
    if ! command -v docker compose > /dev/null 2>&1; then
        print_error "Docker Compose is not available. Please install Docker Compose and try again."
        exit 1
    fi
}

# Function to rebuild frontend container
rebuild_frontend() {
    print_status "Rebuilding frontend container..."
    
    # Stop frontend container if running
    if docker compose ps vue-frontend | grep -q "Up"; then
        print_status "Stopping frontend container..."
        docker compose stop vue-frontend
    fi
    
    # Build frontend container
    print_status "Building frontend container..."
    docker compose build vue-frontend
    
    # Start frontend container
    print_status "Starting frontend container..."
    docker compose up -d vue-frontend
    
    # Wait for health check
    print_status "Waiting for frontend health check..."
    sleep 10
    
    # Check status
    if docker compose ps vue-frontend | grep -q "healthy"; then
        print_success "Frontend container rebuilt and running successfully!"
    else
        print_warning "Frontend container started but health check may still be in progress."
        print_status "Current status:"
        docker compose ps vue-frontend
    fi
}

# Function to rebuild backend container
rebuild_backend() {
    print_status "Rebuilding backend container..."
    
    # Stop backend container if running
    if docker compose ps backend | grep -q "Up"; then
        print_status "Stopping backend container..."
        docker compose stop backend
    fi
    
    # Build backend container
    print_status "Building backend container..."
    docker compose build backend
    
    # Start backend container
    print_status "Starting backend container..."
    docker compose up -d backend
    
    # Wait for health check
    print_status "Waiting for backend health check..."
    sleep 15
    
    # Check status
    if docker compose ps backend | grep -q "healthy"; then
        print_success "Backend container rebuilt and running successfully!"
    else
        print_warning "Backend container started but health check may still be in progress."
        print_status "Current status:"
        docker compose ps backend
    fi
}

# Function to rebuild all containers
rebuild_all() {
    print_status "Rebuilding all containers..."
    
    # Stop all containers
    print_status "Stopping all containers..."
    docker compose down
    
    # Build all containers
    print_status "Building all containers..."
    docker compose build
    
    # Start all containers
    print_status "Starting all containers..."
    docker compose up -d
    
    # Wait for health checks
    print_status "Waiting for health checks..."
    sleep 20
    
    # Check status
    print_status "Container status:"
    docker compose ps
    
    # Check if all containers are healthy
    unhealthy_count=$(docker compose ps | grep -c "unhealthy" || true)
    if [ "$unhealthy_count" -eq 0 ]; then
        print_success "All containers rebuilt and running successfully!"
    else
        print_warning "Some containers may still be starting up."
        print_status "Check container logs if needed: docker compose logs [service-name]"
    fi
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [frontend|backend|all]"
    echo ""
    echo "Options:"
    echo "  frontend  - Rebuild only the frontend container"
    echo "  backend   - Rebuild only the backend container"
    echo "  all       - Rebuild all containers (default if no parameter)"
    echo ""
    echo "Examples:"
    echo "  $0              # Rebuild all containers"
    echo "  $0 frontend     # Rebuild only frontend"
    echo "  $0 backend      # Rebuild only backend"
    echo "  $0 all          # Rebuild all containers"
}

# Main script logic
main() {
    # Check prerequisites
    check_docker
    check_docker_compose
    
    # Get the target from command line argument
    TARGET=${1:-all}
    
    print_status "Starting container rebuild process..."
    print_status "Target: $TARGET"
    
    # Validate target parameter
    case $TARGET in
        frontend|backend|all)
            ;;
        *)
            print_error "Invalid target: $TARGET"
            show_usage
            exit 1
            ;;
    esac
    
    # Execute rebuild based on target
    case $TARGET in
        frontend)
            rebuild_frontend
            ;;
        backend)
            rebuild_backend
            ;;
        all)
            rebuild_all
            ;;
    esac
    
    print_success "Rebuild process completed!"
    
    # Show final status
    echo ""
    print_status "Final container status:"
    docker compose ps
}

# Run main function with all arguments
main "$@"
