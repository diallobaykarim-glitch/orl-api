#!/usr/bin/env pwsh

# Script PowerShell pour Développement vs Production (Windows)

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("dev", "prod", "stop", "logs", "build")]
    [string]$Mode,
    [string]$Target = "dev"
)

switch ($Mode) {
    "dev" {
        Write-Host "🚀 Démarrage en MODE DÉVELOPPEMENT (hot reload activé)..." -ForegroundColor Green
        & docker-compose -f docker-compose.dev.yml up -d
        Write-Host "✅ Services démarrés. Accès :" -ForegroundColor Green
        Write-Host "   - API Docs:    http://localhost:8000/docs" -ForegroundColor Cyan
        Write-Host "   - Dashboard:   http://localhost:8501" -ForegroundColor Cyan
        Write-Host "   - Proxy:       http://localhost" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Logs en temps réel :" -ForegroundColor Yellow
        & docker-compose -f docker-compose.dev.yml logs -f
    }

    "prod" {
        Write-Host "🚀 Démarrage en MODE PRODUCTION..." -ForegroundColor Green
        & docker-compose -f docker-compose.prod.yml up -d
        Write-Host "✅ Services démarrés. Accès :" -ForegroundColor Green
        Write-Host "   - API Docs:    http://localhost:8000/docs" -ForegroundColor Cyan
        Write-Host "   - Dashboard:   http://localhost:8501" -ForegroundColor Cyan
        Write-Host "   - Proxy:       http://localhost" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Logs (limited) :" -ForegroundColor Yellow
        & docker-compose -f docker-compose.prod.yml logs
    }

    "stop" {
        Write-Host "⛔ Arrêt des services..." -ForegroundColor Yellow
        & docker-compose -f docker-compose.dev.yml -f docker-compose.prod.yml down
        Write-Host "✅ Services arrêtés." -ForegroundColor Green
    }

    "logs" {
        if ($Target -eq "prod") {
            Write-Host "📊 Logs PRODUCTION..." -ForegroundColor Cyan
            & docker-compose -f docker-compose.prod.yml logs -f
        }
        else {
            Write-Host "📊 Logs DÉVELOPPEMENT..." -ForegroundColor Cyan
            & docker-compose -f docker-compose.dev.yml logs -f
        }
    }

    "build" {
        if ($Target -eq "prod") {
            Write-Host "🔨 Build PRODUCTION (no-cache)..." -ForegroundColor Green
            & docker-compose -f docker-compose.prod.yml build --no-cache
        }
        else {
            Write-Host "🔨 Build DÉVELOPPEMENT..." -ForegroundColor Green
            & docker-compose -f docker-compose.dev.yml build
        }
    }
}
