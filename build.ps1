# Docker build script for GORU project (PowerShell)

param(
    [Parameter(Position=0)]
    [string]$Command = "help"
)

# Function to print colored output
function Write-Status {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# Function to check if Docker is running
function Test-Docker {
    try {
        docker info | Out-Null
        Write-Success "Docker is running"
        return $true
    }
    catch {
        Write-Error "Docker is not running. Please start Docker and try again."
        return $false
    }
}

# Function to build development image
function Build-Dev {
    Write-Status "Building development image..."
    docker build -t goru-backend:dev --target development ./backend
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Development image built successfully"
    } else {
        Write-Error "Failed to build development image"
        exit 1
    }
}

# Function to build production image
function Build-Prod {
    Write-Status "Building production image..."
    docker build -t goru-backend:prod --target production ./backend
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Production image built successfully"
    } else {
        Write-Error "Failed to build production image"
        exit 1
    }
}

# Function to build test image
function Build-Test {
    Write-Status "Building test image..."
    docker build -t goru-backend:test --target test ./backend
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Test image built successfully"
    } else {
        Write-Error "Failed to build test image"
        exit 1
    }
}

# Function to build all images
function Build-All {
    Write-Status "Building all images..."
    Build-Dev
    Build-Prod
    Build-Test
    Write-Success "All images built successfully"
}

# Function to run tests
function Run-Tests {
    Write-Status "Running tests..."
    docker-compose --profile test up test --build --abort-on-container-exit
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Tests completed"
    } else {
        Write-Error "Tests failed"
        exit 1
    }
}

# Function to start development environment
function Start-Dev {
    Write-Status "Starting development environment..."
    docker-compose up -d
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Development environment started"
    } else {
        Write-Error "Failed to start development environment"
        exit 1
    }
}

# Function to start production environment
function Start-Prod {
    Write-Status "Starting production environment..."
    docker-compose -f docker-compose.prod.yml up -d
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Production environment started"
    } else {
        Write-Error "Failed to start production environment"
        exit 1
    }
}

# Function to stop all containers
function Stop-All {
    Write-Status "Stopping all containers..."
    docker-compose down
    docker-compose -f docker-compose.prod.yml down
    Write-Success "All containers stopped"
}

# Function to clean up
function Cleanup {
    Write-Status "Cleaning up Docker resources..."
    docker system prune -f
    docker volume prune -f
    Write-Success "Cleanup completed"
}

# Function to show usage
function Show-Usage {
    Write-Host "Usage: .\build.ps1 [COMMAND]" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Commands:" -ForegroundColor Cyan
    Write-Host "  dev-build     Build development image"
    Write-Host "  prod-build    Build production image"
    Write-Host "  test-build    Build test image"
    Write-Host "  build-all     Build all images"
    Write-Host "  test          Run tests"
    Write-Host "  dev           Start development environment"
    Write-Host "  prod          Start production environment"
    Write-Host "  stop          Stop all containers"
    Write-Host "  cleanup       Clean up Docker resources"
    Write-Host "  help          Show this help message"
    Write-Host ""
}

# Main script
switch ($Command) {
    "dev-build" {
        if (Test-Docker) { Build-Dev }
    }
    "prod-build" {
        if (Test-Docker) { Build-Prod }
    }
    "test-build" {
        if (Test-Docker) { Build-Test }
    }
    "build-all" {
        if (Test-Docker) { Build-All }
    }
    "test" {
        if (Test-Docker) { Run-Tests }
    }
    "dev" {
        if (Test-Docker) { Start-Dev }
    }
    "prod" {
        if (Test-Docker) { Start-Prod }
    }
    "stop" {
        Stop-All
    }
    "cleanup" {
        Cleanup
    }
    "help" {
        Show-Usage
    }
    default {
        Show-Usage
    }
} 