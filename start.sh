#!/bin/bash

# Script de démarrage — Développement vs Production

case "$1" in
  dev)
    echo "🚀 Démarrage en MODE DÉVELOPPEMENT (hot reload activé)..."
    docker-compose -f docker-compose.dev.yml up -d
    echo "✅ Services démarrés. Accès :"
    echo "   - API Docs:    http://localhost:8000/docs"
    echo "   - Dashboard:   http://localhost:8501"
    echo "   - Proxy:       http://localhost"
    echo ""
    echo "Logs en temps réel :"
    docker-compose -f docker-compose.dev.yml logs -f
    ;;

  prod)
    echo "🚀 Démarrage en MODE PRODUCTION..."
    docker-compose -f docker-compose.prod.yml up -d
    echo "✅ Services démarrés. Accès :"
    echo "   - API Docs:    http://localhost:8000/docs"
    echo "   - Dashboard:   http://localhost:8501"
    echo "   - Proxy:       http://localhost"
    echo ""
    echo "Logs (limited) :"
    docker-compose -f docker-compose.prod.yml logs
    ;;

  stop)
    echo "⛔ Arrêt des services..."
    docker-compose -f docker-compose.dev.yml -f docker-compose.prod.yml down
    echo "✅ Services arrêtés."
    ;;

  logs)
    MODE=${2:-dev}
    if [ "$MODE" = "prod" ]; then
      docker-compose -f docker-compose.prod.yml logs -f
    else
      docker-compose -f docker-compose.dev.yml logs -f
    fi
    ;;

  build)
    MODE=${2:-dev}
    if [ "$MODE" = "prod" ]; then
      echo "🔨 Build PRODUCTION..."
      docker-compose -f docker-compose.prod.yml build --no-cache
    else
      echo "🔨 Build DÉVELOPPEMENT..."
      docker-compose -f docker-compose.dev.yml build
    fi
    ;;

  *)
    echo "Usage: $0 {dev|prod|stop|logs|build} [MODE]"
    echo ""
    echo "Exemples :"
    echo "  $0 dev              — Démarrer en développement"
    echo "  $0 prod             — Démarrer en production"
    echo "  $0 logs dev         — Logs développement"
    echo "  $0 logs prod        — Logs production"
    echo "  $0 build dev        — Build développement"
    echo "  $0 build prod       — Build production (no-cache)"
    echo "  $0 stop             — Arrêter tous les services"
    exit 1
    ;;
esac
