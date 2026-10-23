#!/bin/bash
# ============================================================
# 🧠 هوش افزا — Regular Docker Runner
# ============================================================
# This script runs all services using standalone Docker commands
# (NOT docker-compose)
#
# Stack is aligned with production MySQL 5.7.44:
#   - Django 4.2 LTS (Django 5+ rejects MySQL 5.7)
#   - default MYSQL_IMAGE=mysql:5.7 with utf8mb4 / InnoDB large-prefix
#   - reuse host or existing mysql 5.7 instead of forcing MySQL 8
# ============================================================

set -e

# Absolute path to this script, used when re-executing under `infisical run`.
SCRIPT_PATH="$(cd "$(dirname "$0")" && pwd)/$(basename "$0")"
PROJECT_ROOT="$(cd "$(dirname "$SCRIPT_PATH")" && pwd)"
DEBUG_LOG="${PROJECT_ROOT}/debug-267002.log"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored message
print_msg() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}  🧠 هوش افزا — Hooshafza Platform${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

# #region agent log
agent_log() {
    local hypothesis_id="$1"
    local message="$2"
    local data_json="${3:-{}}"
    local ts
    ts="$(date +%s)000"
    printf '{"sessionId":"267002","hypothesisId":"%s","location":"run.sh","message":"%s","data":%s,"timestamp":%s}\n' \
        "${hypothesis_id}" "${message}" "${data_json}" "${ts}" >> "${DEBUG_LOG}" 2>/dev/null || true
}
# #endregion

# ============================================================
# Infisical secret delivery
# ============================================================
# Secrets are no longer read from a local .env file. This script
# re-executes itself under `infisical run`, which injects the project's
# secrets into the process environment. Django, FastAPI and this script
# keep reading the same variables (SECRET_KEY, DB_PASSWORD, ...), so no
# application code changes are needed.
#
# Local development:
#     INFISICAL_ENV=dev ./run.sh start
#
# Production / server (non-interactive machine identity):
#     export INFISICAL_PROJECT_ID=<project-id>
#     export INFISICAL_CLIENT_ID=<machine-identity-client-id>
#     export INFISICAL_CLIENT_SECRET=<machine-identity-client-secret>
#     ./run.sh start
#
# A machine identity ignores .infisical.json, so INFISICAL_PROJECT_ID is
# required in that case. See INFISICAL.md for the full setup.
INFISICAL_ENV="${INFISICAL_ENV:-prod}"

# Production is MySQL 5.7.44. Default the container image to 5.7 so a fresh
# stack matches the server. Override only when you intentionally run 8.x:
#   MYSQL_IMAGE=mysql:8.0.28 ./run.sh start
MYSQL_IMAGE="${MYSQL_IMAGE:-mysql:5.7}"

# Accept either variable spelling for machine-identity credentials.
INFISICAL_CLIENT_ID="${INFISICAL_CLIENT_ID:-${INFISICAL_UNIVERSAL_AUTH_CLIENT_ID:-}}"
INFISICAL_CLIENT_SECRET="${INFISICAL_CLIENT_SECRET:-${INFISICAL_UNIVERSAL_AUTH_CLIENT_SECRET:-}}"

# Re-exec this script under `infisical run` so secrets are injected into
# the environment instead of being read from disk.
ensure_infisical() {
    if [ -n "${INFISICAL_INJECTED:-}" ]; then
        return 0
    fi

    # If Infisical CLI is not installed, fall back to loading secrets from a .env file.
    if ! command -v infisical >/dev/null 2>&1; then
        if [ -f "$(dirname "$SCRIPT_PATH")/.env" ]; then
            print_warn "Infisical CLI not found. Loading secrets from .env file instead."
            set -a
            # shellcheck disable=SC1091
            source "$(dirname "$SCRIPT_PATH")/.env"
            set +a
            INFISICAL_INJECTED=1
            return 0
        else
            print_error "Infisical CLI not found and no .env file exists."
            print_error "Either install Infisical (https://infisical.com/docs/cli/overview)"
            print_error "or create a .env file from .env.example and fill in your secrets."
            exit 1
        fi
    fi

    # Authenticate with a machine identity when no token is present yet.
    if [ -z "${INFISICAL_TOKEN:-}" ] && [ -n "${INFISICAL_CLIENT_ID}" ] && [ -n "${INFISICAL_CLIENT_SECRET}" ]; then
        print_msg "Authenticating with Infisical using a machine identity..."
        INFISICAL_TOKEN="$(infisical login --method=universal-auth \
            --client-id="${INFISICAL_CLIENT_ID}" \
            --client-secret="${INFISICAL_CLIENT_SECRET}" \
            --silent --plain)"
        export INFISICAL_TOKEN
    fi

    local infisical_args=(run "--env=${INFISICAL_ENV}")
    if [ -n "${INFISICAL_PROJECT_ID:-}" ]; then
        infisical_args+=("--projectId=${INFISICAL_PROJECT_ID}")
    fi

    print_msg "Fetching secrets from Infisical (environment: ${INFISICAL_ENV})..."
    INFISICAL_INJECTED=1 exec infisical "${infisical_args[@]}" -- "$SCRIPT_PATH" "$@"
}

# Fail fast if Infisical did not inject the secrets the stack needs,
# instead of silently falling back to insecure defaults.
check_env() {
    local missing="" key value
    for key in SECRET_KEY DEBUG DB_NAME DB_USER DB_PASSWORD DB_ROOT_PASSWORD JWT_SECRET_KEY SITE_DOMAIN; do
        value="${!key:-}"
        if [ -z "${value}" ]; then
            missing="${missing} ${key}"
        fi
    done
    if [ -n "${missing}" ]; then
        print_error "Missing required secrets:${missing}"
        print_error "They must come from Infisical. Run: infisical run --env=${INFISICAL_ENV} -- ./run.sh start"
        exit 1
    fi
}

# Resolve which MySQL to use. MySQL 5.7 is first-class (production is 5.7.44).
# Priority:
#   1. If DB_HOST is set in Infisical to something other than "hooshafza-mysql" → use it as-is (no container)
#   2. If a Docker container named "mysql" is already running → attach it and reuse it (5.7 or 8.x)
#   3. If native system MySQL is listening on 3306 → host.docker.internal (host-gateway)
#   4. Otherwise → start mysql:5.7 as hooshafza-mysql
resolve_db() {
    START_OWN_MYSQL=1
    DB_HOST_LOCAL="${DB_HOST:-hooshafza-mysql}"

    # Priority 1: custom DB_HOST from Infisical — use as-is, no container needed
    if [ "${DB_HOST_LOCAL}" != "hooshafza-mysql" ]; then
        START_OWN_MYSQL=0
        # #region agent log
        agent_log "C" "resolve_db_custom_host" "{\"db_host\":\"${DB_HOST_LOCAL}\",\"start_own\":0}"
        # #endregion
        return 0
    fi

    # Priority 2: existing Docker container named "mysql" (production often has 5.7 here)
    if docker ps --format '{{.Names}}' | grep -qx 'mysql'; then
        local mysql_ver
        mysql_ver="$(docker exec mysql mysql --version 2>/dev/null || echo unknown)"
        print_msg "Reusing the existing 'mysql' Docker container (${mysql_ver})..."
        docker network connect hooshafza-net mysql 2>/dev/null || true
        START_OWN_MYSQL=0
        DB_HOST_LOCAL="mysql"
        # #region agent log
        agent_log "C" "resolve_db_reuse_mysql_container" "{\"mysql_version\":\"${mysql_ver}\",\"db_host\":\"mysql\"}"
        # #endregion
        return 0
    fi

    # Priority 3: native system MySQL on the host (typical Ubuntu 5.7.44 install)
    if ss -tlnp 2>/dev/null | grep -q ':3306 ' || netstat -tlnp 2>/dev/null | grep -q ':3306 '; then
        print_msg "Detected native system MySQL on port 3306. Containers will use host.docker.internal."
        START_OWN_MYSQL=0
        DB_HOST_LOCAL="host.docker.internal"
        # #region agent log
        agent_log "C" "resolve_db_native_host_mysql" "{\"db_host\":\"host.docker.internal\",\"port\":3306}"
        # #endregion
        return 0
    fi

    # Priority 4: no MySQL found — start MySQL 5.7 so the stack matches production
    print_msg "No existing MySQL found. Starting ${MYSQL_IMAGE} (MySQL 5.7-compatible defaults)..."
    DB_HOST_LOCAL="hooshafza-mysql"
    # #region agent log
    agent_log "E" "resolve_db_start_own" "{\"image\":\"${MYSQL_IMAGE}\"}"
    # #endregion
}

# Create network
create_network() {
    print_msg "Creating Docker network..."
    docker network create hooshafza-net 2>/dev/null || true
}

# Stop all containers
stop_all() {
    print_msg "Stopping all containers..."
    docker stop hooshafza-mysql hooshafza-backend hooshafza-api hooshafza-frontend 2>/dev/null || true
    docker rm hooshafza-mysql hooshafza-backend hooshafza-api hooshafza-frontend 2>/dev/null || true
    print_msg "All containers stopped."
}

wait_for_mysql_container() {
    local container="$1"
    local i
    print_msg "Waiting for MySQL in '${container}' to accept connections..."
    for i in $(seq 1 45); do
        if docker exec "${container}" mysqladmin ping -h 127.0.0.1 --silent 2>/dev/null; then
            print_msg "MySQL is ready."
            # #region agent log
            agent_log "E" "mysql_ready" "{\"container\":\"${container}\",\"attempts\":${i}}"
            # #endregion
            return 0
        fi
        sleep 2
    done
    print_error "MySQL in '${container}' did not become ready in time."
    docker logs "${container}" --tail 40 || true
    # #region agent log
    agent_log "E" "mysql_not_ready" "{\"container\":\"${container}\"}"
    # #endregion
    return 1
}

ensure_app_database() {
    local container="$1"
    if [ -z "${container}" ]; then
        return 0
    fi
    if ! docker ps --format '{{.Names}}' | grep -qx "${container}"; then
        return 0
    fi
    print_msg "Ensuring database '${DB_NAME}' exists on '${container}'..."
    docker exec "${container}" mysql -uroot -p"${DB_ROOT_PASSWORD}" -e \
        "CREATE DATABASE IF NOT EXISTS \`${DB_NAME}\` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci; GRANT ALL PRIVILEGES ON \`${DB_NAME}\`.* TO '${DB_USER}'@'%'; FLUSH PRIVILEGES;" \
        2>/dev/null || print_warn "Could not auto-create database on '${container}' (user/grants may already exist)."
}

# Start MySQL 5.7 (or reuse an existing 5.7/8 server)
start_mysql() {
    if [ "${START_OWN_MYSQL}" -ne 1 ]; then
        print_msg "Skipping MySQL startup — using existing server (host: ${DB_HOST_LOCAL})."
        if [ "${DB_HOST_LOCAL}" = "mysql" ]; then
            wait_for_mysql_container mysql || true
            ensure_app_database mysql
        fi
        return 0
    fi

    print_msg "Starting MySQL container (${MYSQL_IMAGE}) with utf8mb4 / InnoDB 5.7 settings..."

    docker run -d \
        --name hooshafza-mysql \
        --network hooshafza-net \
        --restart unless-stopped \
        -e MYSQL_ROOT_PASSWORD="${DB_ROOT_PASSWORD}" \
        -e MYSQL_DATABASE="${DB_NAME}" \
        -e MYSQL_USER="${DB_USER}" \
        -e MYSQL_PASSWORD="${DB_PASSWORD}" \
        -p 127.0.0.1:3306:3306 \
        -v hooshafza-mysql-data:/var/lib/mysql \
        -v "${PROJECT_ROOT}/docker/mysql/init.sql:/docker-entrypoint-initdb.d/01-init.sql" \
        -v "${PROJECT_ROOT}/docker/mysql/mysql57.cnf:/etc/mysql/conf.d/mysql57.cnf:ro" \
        "${MYSQL_IMAGE}" \
        --character-set-server=utf8mb4 \
        --collation-server=utf8mb4_unicode_ci \
        --innodb-large-prefix=1 \
        --innodb-file-format=Barracuda \
        --innodb-file-per-table=1 \
        --innodb-default-row-format=DYNAMIC \
        --sql-mode=STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION

    wait_for_mysql_container hooshafza-mysql
    print_msg "MySQL started."
}

log_django_mysql_probe() {
    local probe
    probe="$(docker exec -i -e DEBUG_LOG_PATH=/tmp/debug-267002.log hooshafza-backend python - <<'PY' || true
import json, time, os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
try:
    import django
    django.setup()
    from django.db import connection
    data = {"django_version": django.get_version(), "django_major": django.VERSION[0]}
    try:
        with connection.cursor() as c:
            c.execute("SELECT VERSION()")
            data["mysql_version"] = c.fetchone()[0]
            c.execute("SHOW VARIABLES LIKE 'character_set_connection'")
            row = c.fetchone()
            data["charset"] = row[1] if row else None
            c.execute("SHOW VARIABLES LIKE 'sql_mode'")
            row = c.fetchone()
            data["sql_mode"] = row[1] if row else None
            c.execute("SHOW VARIABLES LIKE 'innodb_large_prefix'")
            row = c.fetchone()
            data["innodb_large_prefix"] = row[1] if row else None
        data["connected"] = True
        data["error"] = None
        hid = "A" if data["django_major"] >= 5 else "B"
    except Exception as exc:
        data["connected"] = False
        data["error"] = type(exc).__name__ + ": " + str(exc)[:240]
        hid = "A" if "NotSupportedError" in type(exc).__name__ or "NotSupported" in str(exc) else ("D" if "1071" in str(exc) else "C")
    print(json.dumps({
        "sessionId": "267002",
        "hypothesisId": hid,
        "location": "run.sh:log_django_mysql_probe",
        "message": "django_mysql_probe",
        "data": data,
        "timestamp": int(time.time() * 1000),
    }))
except Exception as exc:
    print(json.dumps({
        "sessionId": "267002",
        "hypothesisId": "A",
        "location": "run.sh:log_django_mysql_probe",
        "message": "django_mysql_probe_failed",
        "data": {"error": type(exc).__name__ + ": " + str(exc)[:240]},
        "timestamp": int(time.time() * 1000),
    }))
PY
)"
    # #region agent log
    if [ -n "${probe}" ]; then
        printf '%s\n' "${probe}" >> "${DEBUG_LOG}" 2>/dev/null || true
    fi
    # #endregion
}

# Build and start Backend (Django) — bound to loopback only; Nginx proxies /admin/ → this container
start_backend() {
    print_msg "Building Backend Docker image (Django 4.2 / MySQL 5.7)..."
    docker build -t hooshafza-backend "${PROJECT_ROOT}/backend"

    print_msg "Starting Backend container..."
    # Ensure the debug log exists as a file before bind-mounting it.
    # #region agent log
    agent_log "A" "backend_starting" "{\"db_host\":\"${DB_HOST_LOCAL}\",\"mysql_image\":\"${MYSQL_IMAGE}\"}"
    # #endregion

    docker run -d \
        --name hooshafza-backend \
        --network hooshafza-net \
        --restart unless-stopped \
        --add-host=host.docker.internal:host-gateway \
        -e DB_HOST="${DB_HOST_LOCAL}" \
        -e DB_PORT=3306 \
        -e DB_NAME="${DB_NAME}" \
        -e DB_USER="${DB_USER}" \
        -e DB_PASSWORD="${DB_PASSWORD}" \
        -e SECRET_KEY="${SECRET_KEY}" \
        -e DEBUG="${DEBUG}" \
        -e JWT_SECRET_KEY="${JWT_SECRET_KEY}" \
        -e SITE_DOMAIN="${SITE_DOMAIN}" \
        -e SITE_NAME="${SITE_NAME}" \
        -e PAYMENT_GATEWAY="${PAYMENT_GATEWAY}" \
        -e PAYMENT_API_KEY="${PAYMENT_API_KEY}" \
        -e PAYMENT_MERCHANT_ID="${PAYMENT_MERCHANT_ID}" \
        -e SPOTPLAYER_API_KEY="${SPOTPLAYER_API_KEY}" \
        -e SPOTPLAYER_BASE_URL="${SPOTPLAYER_BASE_URL}" \
        -e PYTHONPATH=/app \
        -e ALLOWED_HOSTS="localhost,127.0.0.1,${SITE_DOMAIN},www.${SITE_DOMAIN}" \
        -e DEBUG_LOG_PATH=/tmp/debug-267002.log \
        -v "${PROJECT_ROOT}/backend:/app" \
        -v hooshafza-media:/app/media \
        -v "${DEBUG_LOG}:/tmp/debug-267002.log" \
        -p 127.0.0.1:8001:8001 \
        hooshafza-backend

    print_msg "Backend started. Checking Django version (must be 4.2.x for MySQL 5.7)..."
    sleep 3

    local django_ver django_major
    django_ver="$(docker exec hooshafza-backend python -c "import django; print(django.get_version())" 2>/dev/null || echo unknown)"
    django_major="${django_ver%%.*}"
    print_msg "Installed Django version: ${django_ver}"
    # #region agent log
    agent_log "A" "django_version_in_image" "{\"django_version\":\"${django_ver}\"}"
    # #endregion
    if [ "${django_major}" != "unknown" ] && [ "${django_major}" -ge 5 ] 2>/dev/null; then
        print_error "Django ${django_ver} rejects MySQL 5.7. Rebuild after pinning Django>=4.2,<5.0."
        docker logs hooshafza-backend --tail 50 || true
        exit 1
    fi

    # Run migrations + collect static files for admin
    print_msg "Running Django migrations..."
    if ! docker exec hooshafza-backend python manage.py migrate --noinput; then
        log_django_mysql_probe
        print_error "Django migrate failed against MySQL (${DB_HOST_LOCAL})."
        docker logs hooshafza-backend --tail 80 || true
        exit 1
    fi
    log_django_mysql_probe
    print_msg "Collecting admin static files..."
    docker exec hooshafza-backend python manage.py collectstatic --noinput || true

    print_msg "Backend ready on port 8001."
}

# Build and start API (FastAPI) — NOT exposed publicly; Nginx proxies /api → this container
start_api() {
    print_msg "Building API Docker image..."
    docker build -t hooshafza-api "${PROJECT_ROOT}/api"

    print_msg "Starting API container..."
    docker run -d \
        --name hooshafza-api \
        --network hooshafza-net \
        --restart unless-stopped \
        --add-host=host.docker.internal:host-gateway \
        -e DB_HOST="${DB_HOST_LOCAL}" \
        -e DB_PORT=3306 \
        -e DB_NAME="${DB_NAME}" \
        -e DB_USER="${DB_USER}" \
        -e DB_PASSWORD="${DB_PASSWORD}" \
        -e SECRET_KEY="${SECRET_KEY}" \
        -e DEBUG="${DEBUG}" \
        -e JWT_SECRET_KEY="${JWT_SECRET_KEY}" \
        -e DJANGO_SETTINGS_MODULE=config.settings \
        -e IN_DOCKER=1 \
        -e PYTHONPATH=/backend:/app \
        -e SITE_DOMAIN="${SITE_DOMAIN}" \
        -e SITE_NAME="${SITE_NAME}" \
        -e PAYMENT_GATEWAY="${PAYMENT_GATEWAY}" \
        -e PAYMENT_API_KEY="${PAYMENT_API_KEY}" \
        -e PAYMENT_MERCHANT_ID="${PAYMENT_MERCHANT_ID}" \
        -e SPOTPLAYER_API_KEY="${SPOTPLAYER_API_KEY}" \
        -e SPOTPLAYER_BASE_URL="${SPOTPLAYER_BASE_URL}" \
        -e DEBUG_LOG_PATH=/tmp/debug-267002.log \
        -v "${PROJECT_ROOT}/api:/app" \
        -v "${PROJECT_ROOT}/backend:/backend" \
        -v hooshafza-media:/app/media \
        -v "${DEBUG_LOG}:/tmp/debug-267002.log" \
        -p 127.0.0.1:8000:8000 \
        hooshafza-api

    print_msg "API started on port 8000."
}

# Build and start Frontend (Nginx: static files + reverse proxy for API/admin)
start_frontend() {
    print_msg "Building Frontend Docker image (Nginx)..."

    # Build from frontend directory
    docker build -t hooshafza-frontend -f "${PROJECT_ROOT}/frontend/Dockerfile" "${PROJECT_ROOT}/frontend"

    print_msg "Starting Frontend container (Nginx on port 80)..."
    docker run -d \
        --name hooshafza-frontend \
        --network hooshafza-net \
        --restart unless-stopped \
        -p 80:80 \
        hooshafza-frontend

    print_msg "Frontend started on port 80."
}

# Show status
show_status() {
    echo ""
    print_msg "Container Status:"
    docker ps --filter "name=hooshafza" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  🌐 Access Points:${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo -e "  Frontend:      http://DOMAIN (Nginx, port 80)"
    echo -e "  API Docs:      http://DOMAIN/docs (proxied)"
    echo -e "  Django Admin:  http://DOMAIN/admin/ (proxied)"
    echo -e "${GREEN}========================================${NC}"
    echo ""
}

# Show logs
show_logs() {
    docker logs -f hooshafza-mysql &
    docker logs -f hooshafza-backend &
    docker logs -f hooshafza-api &
    docker logs -f hooshafza-frontend
}

# Main menu
main() {
    case "${1:-start}" in
        start|restart)
            ensure_infisical "$@"
            check_env
            ;;
    esac

    case "${1:-start}" in
        start)
            print_header
            create_network
            resolve_db
            start_mysql
            start_backend
            start_api
            start_frontend
            show_status
            ;;
        stop)
            stop_all
            ;;
        restart)
            stop_all
            create_network
            resolve_db
            start_mysql
            start_backend
            start_api
            start_frontend
            show_status
            ;;
        status)
            show_status
            ;;
        logs)
            show_logs
            ;;
        build)
            docker build -t hooshafza-backend "${PROJECT_ROOT}/backend"
            docker build -t hooshafza-api "${PROJECT_ROOT}/api"
            docker build -t hooshafza-frontend -f "${PROJECT_ROOT}/frontend/Dockerfile" "${PROJECT_ROOT}/frontend"
            print_msg "All images built successfully."
            ;;
        migrate)
            docker exec hooshafza-backend python manage.py migrate
            ;;
        createsuperuser)
            docker exec -it hooshafza-backend python manage.py createsuperuser
            ;;
        *)
            echo "Usage: $0 {start|stop|restart|status|logs|build|migrate|createsuperuser}"
            exit 1
            ;;
    esac
}

main "$@"
