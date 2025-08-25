#!/bin/bash

# Development environment management script
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Load environment variables
if [ -f "$PROJECT_ROOT/.env" ]; then
    export $(cat "$PROJECT_ROOT/.env" | grep -v '^#' | xargs)
else
    echo -e "${YELLOW}Warning: .env file not found. Copying from .env.example${NC}"
    cp "$PROJECT_ROOT/.env.example" "$PROJECT_ROOT/.env"
fi

function print_help() {
    echo "StackWizard Development Environment Manager"
    echo ""
    echo "Usage: ./dev.sh [command]"
    echo ""
    echo "Commands:"
    echo "  start       - Start all services"
    echo "  stop        - Stop all services"
    echo "  restart     - Restart all services"
    echo "  status      - Show status of all services"
    echo "  logs        - Show logs (use: logs [service])"
    echo "  shell       - Open shell in container (use: shell [service])"
    echo "  db:reset    - Reset database to initial state"
    echo "  db:backup   - Backup database"
    echo "  db:restore  - Restore database from backup"
    echo "  db:migrate  - Run database migrations"
    echo "  db:seed     - Seed database with test data"
    echo "  test        - Run tests"
    echo "  clean       - Remove all containers and volumes"
    echo "  build       - Rebuild all containers"
    echo "  urls        - Show all service URLs"
}

function start_services() {
    echo -e "${GREEN}Starting development environment...${NC}"
    docker-compose -f "$PROJECT_ROOT/docker-compose.yml" up -d
    echo -e "${GREEN}Services started!${NC}"
    show_urls
}

function stop_services() {
    echo -e "${YELLOW}Stopping development environment...${NC}"
    docker-compose -f "$PROJECT_ROOT/docker-compose.yml" down
    echo -e "${GREEN}Services stopped!${NC}"
}

function restart_services() {
    stop_services
    start_services
}

function show_status() {
    docker-compose -f "$PROJECT_ROOT/docker-compose.yml" ps
}

function show_logs() {
    SERVICE=${1:-}
    if [ -z "$SERVICE" ]; then
        docker-compose -f "$PROJECT_ROOT/docker-compose.yml" logs -f --tail=100
    else
        docker-compose -f "$PROJECT_ROOT/docker-compose.yml" logs -f --tail=100 "$SERVICE"
    fi
}

function open_shell() {
    SERVICE=${1:-backend}
    case $SERVICE in
        backend)
            docker-compose -f "$PROJECT_ROOT/docker-compose.yml" exec backend /bin/bash
            ;;
        frontend)
            docker-compose -f "$PROJECT_ROOT/docker-compose.yml" exec frontend /bin/sh
            ;;
        postgres|db)
            docker-compose -f "$PROJECT_ROOT/docker-compose.yml" exec postgres psql -U ${POSTGRES_USER:-stackwizard} ${POSTGRES_DB:-stackwizard_dev}
            ;;
        redis)
            docker-compose -f "$PROJECT_ROOT/docker-compose.yml" exec redis redis-cli
            ;;
        *)
            echo -e "${RED}Unknown service: $SERVICE${NC}"
            echo "Available services: backend, frontend, postgres (or db), redis"
            ;;
    esac
}

function reset_database() {
    echo -e "${YELLOW}Resetting database...${NC}"
    
    # Stop backend to disconnect from database
    docker-compose -f "$PROJECT_ROOT/docker-compose.yml" stop backend
    
    # Drop and recreate database
    docker-compose -f "$PROJECT_ROOT/docker-compose.yml" exec postgres psql -U ${POSTGRES_USER:-stackwizard} -c "DROP DATABASE IF EXISTS ${POSTGRES_DB:-stackwizard_dev};"
    docker-compose -f "$PROJECT_ROOT/docker-compose.yml" exec postgres psql -U ${POSTGRES_USER:-stackwizard} -c "CREATE DATABASE ${POSTGRES_DB:-stackwizard_dev};"
    
    # Run initialization scripts
    for sql_file in "$PROJECT_ROOT/../kedro-pipeline/data/01_raw/sql/schema"/*.sql; do
        echo "Executing $(basename $sql_file)..."
        docker-compose -f "$PROJECT_ROOT/docker-compose.yml" exec -T postgres psql -U ${POSTGRES_USER:-stackwizard} ${POSTGRES_DB:-stackwizard_dev} < "$sql_file"
    done
    
    # Load seed data
    for sql_file in "$PROJECT_ROOT/../kedro-pipeline/data/01_raw/sql/seed"/*.sql; do
        echo "Loading seed data from $(basename $sql_file)..."
    docker-compose -f "$PROJECT_ROOT/docker-compose.yml" exec postgres psql -U "${POSTGRES_USER:-stackwizard}" -c "DROP DATABASE IF EXISTS ${POSTGRES_DB:-stackwizard_dev};"
    docker-compose -f "$PROJECT_ROOT/docker-compose.yml" exec postgres psql -U "${POSTGRES_USER:-stackwizard}" -c "CREATE DATABASE ${POSTGRES_DB:-stackwizard_dev};"
    
    # Run initialization scripts
    for sql_file in "$PROJECT_ROOT/../kedro-pipeline/data/01_raw/sql/schema"/*.sql; do
        echo "Executing $(basename $sql_file)..."
        docker-compose -f "$PROJECT_ROOT/docker-compose.yml" exec -T postgres psql -U "${POSTGRES_USER:-stackwizard}" "${POSTGRES_DB:-stackwizard_dev}" < "$sql_file"
    done
    
    # Load seed data
    for sql_file in "$PROJECT_ROOT/../kedro-pipeline/data/01_raw/sql/seed"/*.sql; do
        echo "Loading seed data from $(basename $sql_file)..."
        docker-compose -f "$PROJECT_ROOT/docker-compose.yml" exec -T postgres psql -U "${POSTGRES_USER:-stackwizard}" "${POSTGRES_DB:-stackwizard_dev}" < "$sql_file"
    done
    
    # Restart backend
    docker-compose -f "$PROJECT_ROOT/docker-compose.yml" start backend
    
    echo -e "${GREEN}Database reset complete!${NC}"
}

function backup_database() {
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    BACKUP_FILE="$PROJECT_ROOT/database/backup/backup_${TIMESTAMP}.sql"
    
    echo -e "${GREEN}Creating database backup...${NC}"
    docker-compose -f "$PROJECT_ROOT/docker-compose.yml" exec postgres pg_dump -U ${POSTGRES_USER:-stackwizard} ${POSTGRES_DB:-stackwizard_dev} > "$BACKUP_FILE"
    echo -e "${GREEN}Backup saved to: $BACKUP_FILE${NC}"
}

function restore_database() {
    BACKUP_FILE=${1:-}
    if [ -z "$BACKUP_FILE" ]; then
        # Find latest backup
        BACKUP_FILE=$(ls -t "$PROJECT_ROOT/database/backup"/*.sql 2>/dev/null | head -1)
        if [ -z "$BACKUP_FILE" ]; then
            echo -e "${RED}No backup file found!${NC}"
            exit 1
        fi
    fi
    
    echo -e "${YELLOW}Restoring database from: $BACKUP_FILE${NC}"
    
    # Stop backend
    docker-compose -f "$PROJECT_ROOT/docker-compose.yml" stop backend
    
    # Drop and recreate database
    docker-compose -f "$PROJECT_ROOT/docker-compose.yml" exec postgres psql -U ${POSTGRES_USER:-stackwizard} -c "DROP DATABASE IF EXISTS ${POSTGRES_DB:-stackwizard_dev};"
    docker-compose -f "$PROJECT_ROOT/docker-compose.yml" exec postgres psql -U ${POSTGRES_USER:-stackwizard} -c "CREATE DATABASE ${POSTGRES_DB:-stackwizard_dev};"
    
    # Restore from backup
    docker-compose -f "$PROJECT_ROOT/docker-compose.yml" exec -T postgres psql -U ${POSTGRES_USER:-stackwizard} ${POSTGRES_DB:-stackwizard_dev} < "$BACKUP_FILE"
    
    # Restart backend
    docker-compose -f "$PROJECT_ROOT/docker-compose.yml" start backend
    
    echo -e "${GREEN}Database restored!${NC}"
}

function run_migrations() {
    echo -e "${GREEN}Running database migrations...${NC}"
    docker-compose -f "$PROJECT_ROOT/docker-compose.yml" exec backend alembic upgrade head
    echo -e "${GREEN}Migrations complete!${NC}"
}

function seed_database() {
    echo -e "${GREEN}Seeding database...${NC}"
    for sql_file in "$PROJECT_ROOT/../kedro-pipeline/data/01_raw/sql/seed"/*.sql; do
        echo "Loading $(basename $sql_file)..."
        docker-compose -f "$PROJECT_ROOT/docker-compose.yml" exec -T postgres psql -U ${POSTGRES_USER:-stackwizard} ${POSTGRES_DB:-stackwizard_dev} < "$sql_file"
    done
    echo -e "${GREEN}Database seeded!${NC}"
}

function run_tests() {
    echo -e "${GREEN}Running tests...${NC}"
    
    # Backend tests
    echo "Running backend tests..."
    docker-compose -f "$PROJECT_ROOT/docker-compose.yml" exec backend pytest tests/ -v
    
    # Frontend tests
    echo "Running frontend tests..."
    docker-compose -f "$PROJECT_ROOT/docker-compose.yml" exec frontend npm test -- --watchAll=false
    
    echo -e "${GREEN}Tests complete!${NC}"
}

function clean_environment() {
    echo -e "${RED}WARNING: This will remove all containers and volumes!${NC}"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker-compose -f "$PROJECT_ROOT/docker-compose.yml" down -v
        echo -e "${GREEN}Environment cleaned!${NC}"
    else
        echo "Cancelled."
    fi
}

function build_containers() {
    echo -e "${GREEN}Building containers...${NC}"
    docker-compose -f "$PROJECT_ROOT/docker-compose.yml" build
    echo -e "${GREEN}Build complete!${NC}"
}

function show_urls() {
    echo ""
    echo -e "${GREEN}Service URLs:${NC}"
    echo "  Frontend:    http://localhost:${FRONTEND_PORT:-3000}"
    echo "  Backend API: http://localhost:${API_PORT:-8000}"
    echo "  API Docs:    http://localhost:${API_PORT:-8000}/docs"
    echo "  Adminer:     http://localhost:${ADMINER_PORT:-8080}"
    echo "  MailHog:     http://localhost:${MAILHOG_UI_PORT:-8025}"
    echo "  Redis:       localhost:${REDIS_PORT:-6379}"
    echo "  PostgreSQL:  localhost:${DB_PORT:-5432}"
    echo ""
}

# Main command handler
case "$1" in
    start)
        start_services
        ;;
    stop)
        stop_services
        ;;
    restart)
        restart_services
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs "$2"
        ;;
    shell)
        open_shell "$2"
        ;;
    db:reset)
        reset_database
        ;;
    db:backup)
        backup_database
        ;;
    db:restore)
        restore_database "$2"
        ;;
    db:migrate)
        run_migrations
        ;;
    db:seed)
        seed_database
        ;;
    test)
        run_tests
        ;;
    clean)
        clean_environment
        ;;
    build)
        build_containers
        ;;
    urls)
        show_urls
        ;;
    help|--help|-h|"")
        print_help
        ;;
    *)
        echo -e "${RED}Unknown command: $1${NC}"
        echo ""
        print_help
        exit 1
        ;;
esac