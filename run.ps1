# ============================================================
# 🧠 هوش افزا — Windows PowerShell Docker Runner
# ============================================================
# This script runs all services using standalone Docker commands
# for Windows users
# ============================================================

param(
    [Parameter(Position=0)]
    [ValidateSet('start', 'stop', 'restart', 'status', 'logs', 'build', 'migrate', 'createsuperuser')]
    [string]$Action = 'start'
)

# Colors
$Green = "`e[32m"
$Yellow = "`e[33m"
$Red = "`e[31m"
$Blue = "`e[34m"
$NC = "`e[0m"

function Print-Header {
    Write-Host "`n${Blue}========================================${NC}"
    Write-Host "${Blue}  🧠 هوش افزا — Hooshafza Platform${NC}"
    Write-Host "${Blue}========================================${NC}`n"
}

function Print-Info {
    param([string]$Message)
    Write-Host "${Green}[INFO]${NC} $Message"
}

function Print-Warn {
    param([string]$Message)
    Write-Host "${Yellow}[WARN]${NC} $Message"
}

function Print-Error {
    param([string]$Message)
    Write-Host "${Red}[ERROR]${NC} $Message"
}

# ============================================================
# Infisical secret delivery
# ============================================================
# Secrets are no longer read from a local .env file. The script
# re-executes itself under `infisical run`, which injects the project's
# secrets into the process environment. The services keep reading the
# same variables (SECRET_KEY, DB_PASSWORD, ...), so no application code
# changes are needed.
#
# Local development:
#     $env:INFISICAL_ENV = 'dev'; .\run.ps1 start
#
# Production / server (non-interactive machine identity):
#     $env:INFISICAL_PROJECT_ID = '<project-id>'
#     $env:INFISICAL_CLIENT_ID = '<machine-identity-client-id>'
#     $env:INFISICAL_CLIENT_SECRET = '<machine-identity-client-secret>'
#     .\run.ps1 start
#
# See INFISICAL.md for the full setup.
$InfisicalEnv = if ($env:INFISICAL_ENV) { $env:INFISICAL_ENV } else { 'prod' }

# MySQL image is configurable. Default is mysql:5.7 to match production
# (MySQL 5.7.44 + Django 4.2 LTS). Override with MYSQL_IMAGE if needed.
$MySqlImage = if ($env:MYSQL_IMAGE) { $env:MYSQL_IMAGE } else { 'mysql:5.7' }
$InfisicalClientId = if ($env:INFISICAL_CLIENT_ID) { $env:INFISICAL_CLIENT_ID } else { $env:INFISICAL_UNIVERSAL_AUTH_CLIENT_ID }
$InfisicalClientSecret = if ($env:INFISICAL_CLIENT_SECRET) { $env:INFISICAL_CLIENT_SECRET } else { $env:INFISICAL_UNIVERSAL_AUTH_CLIENT_SECRET }

function Invoke-UnderInfisical {
    if (-not (Get-Command infisical -ErrorAction SilentlyContinue)) {
        Print-Error "Infisical CLI not found. Install it: https://infisical.com/docs/cli/overview"
        exit 1
    }

    if (-not $env:INFISICAL_TOKEN -and $InfisicalClientId -and $InfisicalClientSecret) {
        Print-Info "Authenticating with Infisical using a machine identity..."
        $env:INFISICAL_TOKEN = (& infisical login --method=universal-auth --client-id=$InfisicalClientId --client-secret=$InfisicalClientSecret --silent --plain)
    }

    $infisicalArgs = @('run', "--env=$InfisicalEnv")
    if ($env:INFISICAL_PROJECT_ID) { $infisicalArgs += "--projectId=$($env:INFISICAL_PROJECT_ID)" }

    Print-Info "Fetching secrets from Infisical (environment: $InfisicalEnv)..."
    $env:INFISICAL_INJECTED = '1'
    & infisical @infisicalArgs -- $PSCommandPath $Action
    exit $LASTEXITCODE
}

function Assert-Env {
    $required = @('SECRET_KEY', 'DEBUG', 'DB_NAME', 'DB_USER', 'DB_PASSWORD', 'DB_ROOT_PASSWORD', 'JWT_SECRET_KEY', 'SITE_DOMAIN')
    $missing = @($required | Where-Object { [string]::IsNullOrEmpty([Environment]::GetEnvironmentVariable($_, 'Process')) })
    if ($missing.Count -gt 0) {
        Print-Error "Missing required secrets: $($missing -join ', ')"
        Print-Error "They must come from Infisical. Run: infisical run --env=$InfisicalEnv -- .\run.ps1 $Action"
        exit 1
    }
}

# Resolve which MySQL to use. If a standalone `mysql` container is already
# running (e.g. a pre-existing MySQL on the server), reuse it instead of
# starting a second database: attach it to hooshafza-net and point the app
# containers at it by overriding DB_HOST. A custom DB_HOST coming from
# Infisical (anything other than hooshafza-mysql) is always respected as-is.
function Resolve-Db {
    $script:StartOwnMySql = $true
    $script:DbHostLocal = if ($env:DB_HOST) { $env:DB_HOST } else { 'hooshafza-mysql' }
    if ($script:DbHostLocal -ne 'hooshafza-mysql') { return }
    $running = docker ps --format '{{.Names}}'
    if ($running -contains 'mysql') {
        $mysqlVersion = (docker exec mysql mysql --version 2>$null)
        Print-Info "Reusing the existing 'mysql' container as the database ($mysqlVersion)..."
        docker network connect hooshafza-net mysql 2>$null
        $script:StartOwnMySql = $false
        $script:DbHostLocal = 'mysql'
    } else {
        $script:DbHostLocal = 'hooshafza-mysql'
    }
}

# Create network
function Create-Network {
    Print-Info "Creating Docker network..."
    docker network create hooshafza-net 2>$null
}

# Stop all containers
function Stop-All {
    Print-Info "Stopping all containers..."
    docker stop hooshafza-mysql, hooshafza-backend, hooshafza-api, hooshafza-frontend 2>$null
    docker rm hooshafza-mysql, hooshafza-backend, hooshafza-api, hooshafza-frontend 2>$null
    Print-Info "All containers stopped."
}

# Start MySQL
function Start-MySQL {
    if (-not $script:StartOwnMySql) {
        Print-Info "Skipping MySQL startup — using the existing 'mysql' container (host: $($script:DbHostLocal))."
        return
    }

    Print-Info "Starting MySQL container ($MySqlImage)..."
    
    docker run -d --name hooshafza-mysql --network hooshafza-net --restart unless-stopped -e MYSQL_ROOT_PASSWORD=$env:DB_ROOT_PASSWORD -e MYSQL_DATABASE=$env:DB_NAME -e MYSQL_USER=$env:DB_USER -e MYSQL_PASSWORD=$env:DB_PASSWORD -p 3306:3306 -v hooshafza-mysql-data:/var/lib/mysql -v "${PWD}\docker\mysql\init.sql:/docker-entrypoint-initdb.d/01-init.sql" $MySqlImage
    
    Print-Info "Waiting for MySQL to be ready..."
    Start-Sleep -Seconds 10
    Print-Info "MySQL started."
}

# Start Backend (Django)
function Start-Backend {
    Print-Info "Building Backend Docker image..."
    docker build -t hooshafza-backend ./backend
    
    Print-Info "Starting Backend container..."
    docker run -d --name hooshafza-backend --network hooshafza-net --restart unless-stopped -e DB_HOST=$($script:DbHostLocal) -e DB_PORT=3306 -e DB_NAME=$env:DB_NAME -e DB_USER=$env:DB_USER -e DB_PASSWORD=$env:DB_PASSWORD -e SECRET_KEY=$env:SECRET_KEY -e DEBUG=$env:DEBUG -e JWT_SECRET_KEY=$env:JWT_SECRET_KEY -e SITE_DOMAIN=$env:SITE_DOMAIN -e SITE_NAME="$env:SITE_NAME" -e PAYMENT_GATEWAY=$env:PAYMENT_GATEWAY -e PAYMENT_API_KEY=$env:PAYMENT_API_KEY -e PAYMENT_MERCHANT_ID=$env:PAYMENT_MERCHANT_ID -e SPOTPLAYER_API_KEY=$env:SPOTPLAYER_API_KEY -e SPOTPLAYER_BASE_URL=$env:SPOTPLAYER_BASE_URL -e PYTHONPATH=/app -v "${PWD}\backend:/app" -v hooshafza-media:/app/media -p 8001:8001 hooshafza-backend
    
    Print-Info "Backend started. Waiting for Django to initialize..."
    Start-Sleep -Seconds 5
    
    # Run migrations
    Print-Info "Running Django migrations..."
    docker exec hooshafza-backend python manage.py migrate --noinput
    
    Print-Info "Backend ready on port 8001."
}

# Start API (FastAPI)
function Start-API {
    Print-Info "Building API Docker image..."
    docker build -t hooshafza-api ./api
    
    Print-Info "Starting API container..."
    docker run -d --name hooshafza-api --network hooshafza-net --restart unless-stopped -e DB_HOST=$($script:DbHostLocal) -e DB_PORT=3306 -e DB_NAME=$env:DB_NAME -e DB_USER=$env:DB_USER -e DB_PASSWORD=$env:DB_PASSWORD -e SECRET_KEY=$env:SECRET_KEY -e DEBUG=$env:DEBUG -e JWT_SECRET_KEY=$env:JWT_SECRET_KEY -e DJANGO_SETTINGS_MODULE=config.settings -e PYTHONPATH=/backend:/app -e SITE_DOMAIN=$env:SITE_DOMAIN -e SITE_NAME="$env:SITE_NAME" -e PAYMENT_GATEWAY=$env:PAYMENT_GATEWAY -e PAYMENT_API_KEY=$env:PAYMENT_API_KEY -e PAYMENT_MERCHANT_ID=$env:PAYMENT_MERCHANT_ID -e SPOTPLAYER_API_KEY=$env:SPOTPLAYER_API_KEY -e SPOTPLAYER_BASE_URL=$env:SPOTPLAYER_BASE_URL -v "${PWD}\api:/app" -v "${PWD}\backend:/backend" -v hooshafza-media:/app/media -p 8000:8000 hooshafza-api
    
    Print-Info "API started on port 8000."
}

# Start Frontend (Python HTTP Server)
function Start-Frontend {
    Print-Info "Building Frontend Docker image..."
    docker build -t hooshafza-frontend -f ./frontend/Dockerfile ./frontend
    
    Print-Info "Starting Frontend container..."
    docker run -d --name hooshafza-frontend --network hooshafza-net --restart unless-stopped -p 80:80 hooshafza-frontend
    
    Print-Info "Frontend started on port 80."
}

# Show status
function Show-Status {
    Write-Host ""
    Print-Info "Container Status:"
    docker ps --filter "name=hooshafza" --format "table {{.Names}}`t{{.Status}}`t{{.Ports}}"
    Write-Host ""
    Write-Host "${Green}========================================${NC}"
    Write-Host "${Green}  🌐 Access Points:${NC}"
    Write-Host "${Green}========================================${NC}"
    Write-Host "  Frontend:      http://localhost"
    Write-Host "  API Docs:      http://localhost:8000/docs"
    Write-Host "  Django Admin:  http://localhost:8001/admin/"
    Write-Host "${Green}========================================${NC}"
    Write-Host ""
}

# Main
if ($Action -in @('start', 'restart')) {
    if (-not $env:INFISICAL_INJECTED) {
        Invoke-UnderInfisical
    }
    Assert-Env
}

switch ($Action) {
    'start' {
        Print-Header
        Create-Network
        Resolve-Db
        Start-MySQL
        Start-Backend
        Start-API
        Start-Frontend
        Show-Status
    }
    'stop' {
        Stop-All
    }
    'restart' {
        Stop-All
        Create-Network
        Resolve-Db
        Start-MySQL
        Start-Backend
        Start-API
        Start-Frontend
        Show-Status
    }
    'status' {
        Show-Status
    }
    'logs' {
        docker logs -f hooshafza-mysql
        docker logs -f hooshafza-backend
        docker logs -f hooshafza-api
        docker logs -f hooshafza-frontend
    }
    'build' {
        docker build -t hooshafza-backend ./backend
        docker build -t hooshafza-api ./api
        docker build -t hooshafza-frontend -f ./frontend/Dockerfile ./frontend
        Print-Info "All images built successfully."
    }
    'migrate' {
        docker exec hooshafza-backend python manage.py migrate
    }
    'createsuperuser' {
        docker exec -it hooshafza-backend python manage.py createsuperuser
    }
}
