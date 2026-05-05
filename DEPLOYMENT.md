# orl-api — Développement & Production

## Structure

```
orl-api/
├── docker-compose.yml       # Base (original)
├── docker-compose.dev.yml   # DÉVELOPPEMENT avec hot reload
├── docker-compose.prod.yml  # PRODUCTION optimisée
├── start.sh                 # Script bash (Linux/Mac)
├── start.ps1                # Script PowerShell (Windows)
├── .env                     # Configuration globale
├── .dockerignore            # Build context
├── .dockerignore.prod       # Build context production
├── Dockerfile               # API (multi-stage)
├── Dockerfile.dashboard     # Dashboard
├── app/                     # Source API
├── dashboard/               # Source Dashboard
├── nginx/
│   └── default.conf         # Configuration proxy
└── data/                    # Base de données SQLite
```

---

## DÉVELOPPEMENT

### Démarrage

**Linux/Mac :**
```bash
bash start.sh dev
```

**Windows (PowerShell) :**
```powershell
.\start.ps1 dev
```

**Ou directement :**
```bash
docker-compose -f docker-compose.dev.yml up -d
```

### Fonctionnalités

- ✅ **Hot reload** : modifications en direct sans rebuild (`develop: watch:`)
- ✅ **Volumes bind** : `./app` et `./dashboard` montés en live
- ✅ **Logs détaillés** : JSON driver, 10MB max, 3 fichiers
- ✅ **Ressources généreuses** : API 4GB/2GB, Dashboard 2GB/1GB
- ✅ **Health checks** : 30s interval, 3 retries, logs détaillés

### Accès

```
- API Docs:    http://localhost:8000/docs
- API OpenAPI: http://localhost:8000/openapi.json
- Dashboard:   http://localhost:8501
- Proxy:       http://localhost/api/
```

### Logs

```bash
# Temps réel
docker-compose -f docker-compose.dev.yml logs -f

# Service spécifique
docker-compose -f docker-compose.dev.yml logs -f orl-api

# Depuis fichier
docker inspect orl-api | grep LogPath
```

### Rebuild après changement dépendances

```bash
# requirements.txt change
docker-compose -f docker-compose.dev.yml build --no-cache

# requirements-dashboard.txt change
docker-compose -f docker-compose.dev.yml build orl-dashboard --no-cache
```

---

## PRODUCTION

### Démarrage

**Linux/Mac :**
```bash
bash start.sh prod
```

**Windows (PowerShell) :**
```powershell
.\start.ps1 prod
```

**Ou directement :**
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Optimisations

- ✅ **Ressources strictes** : API 3GB/1.5GB, Dashboard 1.5GB/800MB, Nginx 256MB/128MB
- ✅ **Health checks renforcés** : 60s interval, 5 retries, 30s start_period
- ✅ **Logging production** : JSON driver, 20MB max, 10 fichiers (archivage)
- ✅ **Sécurité** : `no-new-privileges:true` sur tous les services
- ✅ **Noms uniques** : containers `-prod` pour coexister avec dev
- ✅ **Réseau isolé** : `orl-network-prod`
- ✅ **Restart policies** : `unless-stopped` (évite restarts cycliques)

### Pré-production

```bash
# Vérifier image sizes
docker images | grep orl-api

# Vérifier limites ressources
docker inspect orl-api-prod | grep -A 20 "MemoryLimit"

# Test de charge (simple)
for i in {1..100}; do curl http://localhost:8000/docs > /dev/null; done
```

### Monitoring

```bash
# Ressources en temps réel
docker stats

# Logs archivés
docker inspect orl-api-prod | grep LogPath
cat /var/lib/docker/containers/<ID>/app-json.log | jq

# État des containers
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Health checks
docker inspect orl-api-prod --format='{{json .State.Health}}'
```

---

## Variables d'environnement (.env)

```bash
ENVIRONMENT=development       # development ou production
API_PORT=8000
DASHBOARD_PORT=8501
PYTHONUNBUFFERED=1           # Logs Python en temps réel
```

---

## Comparaison Dev vs Prod

| Aspect | DEV | PROD |
|--------|-----|------|
| Hot reload | ✅ | ❌ |
| Volumes bind | ✅ | ❌ (data/ only) |
| Logging max | 10MB × 3 | 20MB × 10 |
| Health interval | 30s | 60s |
| API CPU limit | 2 | 2 |
| API Memory | 4GB/2GB | 3GB/1.5GB |
| Network | `orl-network-dev` | `orl-network-prod` |
| Container names | `orl-*` | `orl-*-prod` |
| Security opts | none | `no-new-privileges` |

---

## Scripts utilitaires

### Arrêter tout

```bash
bash start.sh stop
```

### Logs spécifiques

```bash
bash start.sh logs dev    # Dev logs
bash start.sh logs prod   # Prod logs
```

### Rebuild

```bash
bash start.sh build dev   # Dev build
bash start.sh build prod  # Prod build (no-cache)
```

---

## Troubleshooting

### Port en utilisation

```bash
# Linux/Mac
lsof -i :8000
lsof -i :8501
lsof -i :80

# Windows
Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
```

### Container unhealthy

```bash
docker inspect <container> --format='{{json .State.Health}}'
docker logs <container>
```

### Clear complet

```bash
docker-compose -f docker-compose.dev.yml down -v
docker-compose -f docker-compose.prod.yml down -v
docker system prune -a
```

---

## Notes

- Deux réseaux Docker : `orl-network-dev` et `orl-network-prod` (isolation complète)
- Base de données SQLite : `./data/orl.db` (monté en volume dans les deux modes)
- Les deux configurations peuvent coexister (différents container names et ports)
