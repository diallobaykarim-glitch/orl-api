# orl-api — Documentation Complète

Plateforme médicale IA containerisée avec Docker Compose.

**Stack :** FastAPI (API) + Streamlit (Dashboard) + Nginx (Proxy)

## 📁 Structure du Projet

```
orl-api/
├── app/                      # Source API FastAPI
│   ├── main.py
│   ├── schemas.py
│   ├── utils.py
│   ├── model.pkl             # Modèle ML
│   └── ...
├── dashboard/                # Source Dashboard Streamlit
│   └── app.py
├── nginx/
│   └── default.conf          # Configuration proxy
├── data/                      # Base de données SQLite (volume)
├── Dockerfile                # API (multi-stage)
├── Dockerfile.dashboard      # Dashboard
├── docker-compose.yml        # Base configuration
├── docker-compose.dev.yml    # Développement (hot reload)
├── docker-compose.prod.yml   # Production
├── .env                      # Configuration locale
├── .env.prod                 # Configuration production template
├── .dockerignore             # Contexte build nettoyé
├── .gitignore                # Secrets & données protégés
├── requirements.txt          # Dépendances API
├── requirements-dashboard.txt # Dépendances Dashboard
├── start.sh                  # Script bash (Linux/Mac)
├── start.ps1                 # Script PowerShell (Windows)
├── DEPLOYMENT.md             # Guide dev/prod
├── DEPLOYMENT_CHECKLIST.md   # Checklist pré-déploiement
└── DEPLOY_TO_SERVER.md       # Guide déploiement serveur
```

---

## 🚀 Démarrage Rapide

### Développement (hot reload)

```bash
# Linux/Mac
bash start.sh dev

# Windows (PowerShell)
.\start.ps1 dev

# Accès
http://localhost:8000/docs       # API Docs
http://localhost:8501            # Dashboard
http://localhost/api/            # Proxy API
```

### Production

```bash
# Linux/Mac
bash start.sh prod

# Windows (PowerShell)
.\start.ps1 prod

# Vérifier
docker ps --format "table {{.Names}}\t{{.Status}}"
```

---

## 📖 Documentation Détaillée

1. **[DEPLOYMENT.md](./DEPLOYMENT.md)** — Modes dev/prod, logs, monitoring
2. **[DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md)** — Checklist 60+ points pré-production
3. **[DEPLOY_TO_SERVER.md](./DEPLOY_TO_SERVER.md)** — Guide déploiement serveur (Ubuntu/CentOS)

---

## 🐳 Architecture Docker

### Services

| Service | Image | Port | Rôle |
|---------|-------|------|------|
| **orl-api** | `python:3.10.20-slim` | 8000 | API FastAPI uvicorn |
| **orl-dashboard** | `python:3.11.15-slim` | 8501 | Dashboard Streamlit |
| **orl-nginx** | `nginx:1.29-alpine` | 80 | Reverse proxy |

### Modes de Déploiement

#### Dev (`docker-compose.dev.yml`)
- ✅ Hot reload : modification fichiers = redémarrage auto
- ✅ Volumes bind : `./app` et `./dashboard` montés en live
- ✅ Logs détaillés : 10MB × 3 fichiers
- ✅ Ressources généreuses : API 4GB/2GB, Dashboard 2GB/1GB
- ✅ Réseau : `orl-network-dev`

#### Prod (`docker-compose.prod.yml`)
- ✅ Ressources strictes : API 3GB/1.5GB, Dashboard 1.5GB/800MB
- ✅ Health checks renforcés : 60s interval, 5 retries
- ✅ Logging production : 20MB × 10 fichiers (archivage)
- ✅ Sécurité : `no-new-privileges:true`
- ✅ Réseau : `orl-network-prod`

---

## 🔧 Configuration

### Variables d'Environnement

Voir `.env` pour liste complète.

```bash
ENVIRONMENT=development          # development ou production
API_PORT=8000                    # Port API
DASHBOARD_PORT=8501              # Port Dashboard
PYTHONUNBUFFERED=1               # Logs Python en temps réel
API_KEY_SECRET=your-secret       # Secret production
```

### Secrets Production

1. Créer `.env.prod.local` (git-ignored) :
   ```bash
   cp .env.prod .env.prod.local
   nano .env.prod.local
   ```

2. Changer secrets réels :
   ```bash
   API_KEY_SECRET=votre_secret_ici
   ALLOWED_ORIGINS=https://votre-api.com
   ```

3. Restreindre permissions :
   ```bash
   chmod 600 .env.prod.local
   ```

---

## 📊 Monitoring & Logs

### Logs en temps réel

```bash
# Dev
docker-compose -f docker-compose.dev.yml logs -f

# Prod
docker-compose -f docker-compose.prod.yml logs -f

# Service spécifique
docker logs -f orl-api-prod
docker logs -f orl-dashboard-prod
```

### Health Checks

```bash
docker ps --format "table {{.Names}}\t{{.Status}}"

# Détail health check
docker inspect orl-api-prod --format='{{json .State.Health}}'
```

### Ressources

```bash
# CPU/Mémoire en temps réel
docker stats --no-stream

# Utilisation disque
docker system df
```

---

## 🔐 Sécurité

- ✅ `.env` et `.env.prod.local` git-ignored
- ✅ Aucun secret en plaintext en git
- ✅ Containers non-root (si config Dockerfile)
- ✅ `no-new-privileges:true` activé (prod)
- ✅ Health checks validant santé services
- ✅ Firewall rules (port 80 seulement en prod)

---

## 🚢 Déploiement Serveur

Voir **[DEPLOY_TO_SERVER.md](./DEPLOY_TO_SERVER.md)** pour :

1. Prérequis serveur (Ubuntu 22.04+)
2. Installation Docker
3. Clonage depuis git
4. Configuration secrets
5. Build et démarrage
6. HTTPS/TLS (reverse proxy)
7. Monitoring & alerting
8. Backup automatisé
9. Mise à jour code
10. Rollback d'urgence

---

## 🔄 Mise à Jour du Code

```bash
# Pull changes
git pull origin main

# Dev : auto-rebuild via watch
# Prod : rebuild manuel
docker-compose -f docker-compose.prod.yml build --no-cache

# Restart
docker-compose -f docker-compose.prod.yml up -d
```

---

## 🆘 Troubleshooting

### Container unhealthy

```bash
docker logs <container_name>
docker inspect <container_name> --format='{{json .State.Health}}'
```

### Port en utilisation

```bash
# Linux/Mac
lsof -i :8000

# Windows (PowerShell)
Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
```

### Clear complet

```bash
docker-compose -f docker-compose.prod.yml down -v
docker system prune -a
```

---

## 📝 Scripts Utilitaires

### start.sh (Linux/Mac)

```bash
bash start.sh dev                # Démarrer dev
bash start.sh prod               # Démarrer prod
bash start.sh logs dev           # Logs dev
bash start.sh logs prod          # Logs prod
bash start.sh build dev          # Build dev
bash start.sh build prod         # Build prod (no-cache)
bash start.sh stop               # Arrêter tout
```

### start.ps1 (Windows)

```powershell
.\start.ps1 dev
.\start.ps1 prod
.\start.ps1 logs dev
.\start.ps1 logs prod
.\start.ps1 stop
```

---

## 📞 Support & Issues

Consulter logs :
```bash
docker-compose -f docker-compose.prod.yml logs --tail=100
```

Checkpoints :
- API Docs : http://localhost:8000/docs
- Dashboard : http://localhost:8501
- Health : `docker ps` (tous `healthy` ?)

---

**Version :** 1.0 (Production-Ready)
**Last Updated :** 2026-05-05
**Maintainer :** ORL API Team
