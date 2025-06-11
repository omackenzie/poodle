#!/bin/bash

# Helper script for development tasks with Docker

set -e

# Check if docker-compose is running
check_container() {
    if ! docker-compose ps web | grep -q "Up"; then
        echo "Starting containers..."
        docker-compose up -d
        echo "Waiting for containers to be ready..."
        sleep 5
    fi
}

case "$1" in
    test)
        check_container
        echo "Running tests..."
        docker-compose exec web python manage.py test
        ;;
    coverage)
        check_container
        echo "Running coverage..."
        docker-compose exec web coverage run manage.py test
        docker-compose exec web coverage report -m
        ;;
    lint)
        check_container
        echo "Running linter..."
        docker-compose exec web ruff check .
        ;;
    format)
        check_container
        echo "Running import sorting..."
        docker-compose exec web isort .
        ;;
    all)
        check_container
        echo "Running all checks..."
        docker-compose exec web python manage.py test
        docker-compose exec web ruff check .
        docker-compose exec web isort --check-only .
        echo "All checks passed!"
        ;;
    *)
        echo "Usage: $0 {test|coverage|lint|format|all}"
        echo ""
        echo "Commands:"
        echo "  test     - Run Django tests"
        echo "  coverage - Run tests with coverage report"
        echo "  lint     - Run ruff linter"
        echo "  format   - Run isort import sorting"
        echo "  all      - Run tests, linting, and import checks"
        exit 1
        ;;
esac
