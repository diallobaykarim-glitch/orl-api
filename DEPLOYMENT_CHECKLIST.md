# Pre-Deployment Checklist — orl-api Production

## Infrastructure

- [ ] Serveur cible configuré (RAM ≥ 16GB, disque ≥ 100GB, CPU ≥ 4 cores)
- [ ] Docker & Docker Compose installés (version ≥ 25.0)
- [ ] Firewall ouvert : ports 80 (HTTP), 443 (HTTPS si TLS), 8000 (API debug), 8501 (Dashboard debug)
- [ ] Certificats SSL/TLS préparés (si production avec HTTPS)
- [ ] Reverse proxy externe configuré (optionnel, Nginx/HAProxy/CloudFlare)

## Configuration

- [ ] `.env.prod.local` créé avec secrets uniques (ne pas utiliser .env.prod)
- [ ] `API_KEY_SECRET` changé en prod
- [ ] `ALLOWED_ORIGINS` configuré avec domaines réels
- [ ] `DATABASE_URL` validée (chemin write-accessible)
- [ ] Ressources limites ajustées selon serveur (CPU, RAM)
- [ ] Timezone serveur alignée avec app (check `/etc/timezone`)

## Code & Images

- [ ] Branches mergées : dev → main
- [ ] Tests complets passent (`pytest` ou custom suite)
- [ ] `model.pkl` pré-entraîné et versioned
- [ ] Images Docker buildées et testées (`docker-compose.prod.yml build`)
- [ ] Image sizes vérifiées (API ~3GB, Dashboard ~600MB)
- [ ] Dockerfile multi-stage optimisé (pas de debug tools en prod)

## Data & Volumes

- [ ] Répertoire `./data/` existe et write-accessible
- [ ] Base de données SQLite initialisée (ou migration script préparé)
- [ ] Sauvegarde initiale de `./data/` effectuée
- [ ] Politique de backup planifiée (cron job ou cloud storage)
- [ ] Rotation des logs configurée (json-file driver 20MB × 10)

## Networking & Monitoring

- [ ] Proxy nginx en place et testé (`http://localhost/api/`, `/dashboard/`)
- [ ] Health checks validés (`docker ps` show healthy)
- [ ] Logs aggregation préparée (optionnel : ELK, DataDog, CloudWatch)
- [ ] Monitoring/alerting setup (optionnel : Prometheus, New Relic)
- [ ] DNS records pointant vers serveur

## Security

- [ ] Secrets (API_KEY, DB credentials) stockés en `.env.prod.local` (git-ignored)
- [ ] `.env.prod.local` restreint en permissions (`chmod 600`)
- [ ] Aucun secret en `.env` ni en git
- [ ] Containers tournent non-root (`USER` spécifié en Dockerfile)
- [ ] `no-new-privileges:true` activé dans docker-compose.prod.yml
- [ ] Firewall règles restrictives (whitelist IPs si interne)
- [ ] HTTPS/TLS configuré (même en interne)

## Deployment Commands

### Première exécution

```bash
# Clone / pull repo
git clone <repo> orl-api-prod
cd orl-api-prod

# Setup production env
cp .env.prod .env.prod.local
# EDIT .env.prod.local avec secrets réels

# Build images
docker-compose -f docker-compose.prod.yml build --no-cache

# Démarrage
docker-compose -f docker-compose.prod.yml up -d

# Vérifier
docker ps
docker-compose -f docker-compose.prod.yml logs
```

### Mise à jour (rolling)

```bash
# Pull changes
git pull origin main

# Rebuild & restart
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d

# Vérifier santé
docker-compose -f docker-compose.prod.yml logs
```

### Rollback (urgent)

```bash
docker-compose -f docker-compose.prod.yml down
# Restore backup data/
docker-compose -f docker-compose.prod.yml up -d
```

## Post-Deployment Verification

### Minute 0 : Services démarrés

```bash
docker ps
# Tous les containers doivent être "healthy" ou "up"
```

### Minute 5 : Santé des services

```bash
docker-compose -f docker-compose.prod.yml logs --tail=50
curl http://localhost:8000/docs        # API accessible
curl http://localhost:8501             # Dashboard accessible
curl http://localhost/api/             # Proxy API
curl http://localhost/dashboard/       # Proxy Dashboard
```

### Minute 10 : Données persistantes

```bash
ls -lh data/orl.db                     # BD existe et grandit
docker inspect orl-api-prod | grep -A5 Mounts
```

### Minute 15 : Performance baseline

```bash
docker stats --no-stream               # Vérifier RAM/CPU
# API ≈ 500MB-1GB RAM, Dashboard ≈ 200-300MB RAM
```

### Minute 30 : Logs stables

```bash
docker logs orl-api-prod | grep ERROR  # Pas d'erreurs?
docker logs orl-dashboard-prod | grep ERROR
docker logs orl-nginx-prod | grep ERROR
```

## Ongoing Operations

### Monitoring (quotidien)

```bash
# Health check
docker ps --format "table {{.Names}}\t{{.Status}}"

# Logs (last 100 lines)
docker logs --tail=100 orl-api-prod
docker logs --tail=100 orl-dashboard-prod

# Disk usage
docker system df

# Database size
du -sh data/
```

### Backup (hebdomadaire minimum)

```bash
# Snapshot data/
tar -czf data-backup-$(date +%Y%m%d).tar.gz data/

# Upload distant
aws s3 cp data-backup-*.tar.gz s3://my-bucket/backups/
```

### Update (mensuel ou sur hotfix)

```bash
# Test en staging d'abord
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml build --no-cache

# Restart services
docker-compose -f docker-compose.prod.yml up -d

# Verify
curl http://localhost/api/health
```

### Logs rotation

Docker gère automatiquement (json-file driver, max 20MB × 10 fichiers).
Optionnel : `logrotate` pour logs hors Docker.

## Emergency Contacts & Docs

- [ ] Documentation API : http://localhost:8000/docs
- [ ] On-call contact : [FILL IN]
- [ ] Escalation path : [FILL IN]
- [ ] Disaster recovery plan : [FILL IN]

---

**Status :** ⬜ Ready for deployment
**Last Updated :** 2026-05-05
**Deployed By :** [name]
**Deployment Date :** [date]
