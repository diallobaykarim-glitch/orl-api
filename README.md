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
├── reports/                  # Rapports statistiques generés
│   ├── analyse_orl_patients.png
│   ├── correlation_matrix.png
│   ├── analyse_sexe.png
│   ├── patients_data.csv
│   └── report.json
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
├── generate_patients.py      # Script de test statistique
├── start.sh                  # Script bash (Linux/Mac)
├── start.ps1                 # Script PowerShell (Windows)
├── DEPLOYMENT.md             # Guide dev/prod
├── DEPLOYMENT_CHECKLIST.md   # Checklist pré-déploiement
└── DEPLOY_TO_SERVER.md       # Guide déploiement serveur
```

---

## 📊 Tests Statistiques et Rapports

Un script Python genere 33 patients de test avec analyses statistiques et graphiques.

### Utilisation

```bash
python generate_patients.py
```

### Fichiers Generes

Les rapports sont sauvegardes dans le dossier `reports/` :

- **analyse_orl_patients.png** — 6 graphiques :
  - Distribution des probabilites de risque
  - Pie chart du niveau de risque (Faible/Modere/Eleve)
  - Age vs Probabilite (colore par tabagisme)
  - Impact du tabagisme sur le risque
  - Impact de l'alcool sur le risque
  - Duree des symptomes vs probabilite

- **correlation_matrix.png** — Matrice de correlation entre toutes les variables

- **analyse_sexe.png** — Analyse comparative par sexe

- **patients_data.csv** — Donnees completes des 33 patients (importable dans Excel/Pandas)

- **report.json** — Rapport statistique structure (moyenne, mediane, ecart-type, distributions)

### Statistiques Generees

Pour chaque patient :
- Age, sexe, tabagisme, alcool
- Dysphonie, dysphagie, dyspnee
- Echelle douleur, duree symptomes
- Imagerie suspecte
- **Probabilite de risque** (0-1)
- **Niveau de risque** (Faible/Modere/Eleve)

### Resultats Exemple

```
Nombre de patients: 33
Probabilite moyenne: 0.754
Ecart-type: 0.080
Risque eleve: 32 patients (96.9%)
Risque modere: 1 patient (3.1%)
```

### Requirements

Installer les dependances supplementaires :

```bash
pip install pandas matplotlib seaborn
```

---

## 🚀 Demarrage Rapide

### Developpement (hot reload)

```bash
# Linux/Mac
bash start.sh dev

# Windows (PowerShell)
.\start.ps1 dev

# Acces
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

# Verifier
docker ps --format "table {{.Names}}\t{{.Status}}"
```

---

## 📖 Documentation Detaillee

1. **[DEPLOYMENT.md](./DEPLOYMENT.md)** — Modes dev/prod, logs, monitoring
2. **[DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md)** — Checklist 60+ points pre-production
3. **[DEPLOY_TO_SERVER.md](./DEPLOY_TO_SERVER.md)** — Guide deploiement serveur (Ubuntu/CentOS)

---

## 🐳 Architecture Docker

### Services

| Service | Image | Port | Role |
|---------|-------|------|------|
| **orl-api** | `python:3.10.20-slim` | 8000 | API FastAPI uvicorn |
| **orl-dashboard** | `python:3.11.15-slim` | 8501 | Dashboard Streamlit |
| **orl-nginx** | `nginx:1.29-alpine` | 80 | Reverse proxy |

### Modes de Deploiement

#### Dev (`docker-compose.dev.yml`)
- ✅ Hot reload : modification fichiers = redemarrage auto
- ✅ Volumes bind : `./app` et `./dashboard` montes en live
- ✅ Logs detailles : 10MB x 3 fichiers
- ✅ Ressources genereuses : API 4GB/2GB, Dashboard 2GB/1GB
- ✅ Reseau : `orl-network-dev`

#### Prod (`docker-compose.prod.yml`)
- ✅ Ressources strictes : API 3GB/1.5GB, Dashboard 1.5GB/800MB
- ✅ Health checks renforces : 60s interval, 5 retries
- ✅ Logging production : 20MB x 10 fichiers (archivage)
- ✅ Securite : `no-new-privileges:true`
- ✅ Reseau : `orl-network-prod`

---

## 🔧 Configuration

### Variables d'Environnement

Voir `.env` pour liste complete.

```bash
ENVIRONMENT=development          # development ou production
API_PORT=8000                    # Port API
DASHBOARD_PORT=8501              # Port Dashboard
PYTHONUNBUFFERED=1               # Logs Python en temps reel
API_KEY_SECRET=your-secret       # Secret production
```

### Secrets Production

1. Creer `.env.prod.local` (git-ignored) :
   ```bash
   cp .env.prod .env.prod.local
   nano .env.prod.local
   ```

2. Changer secrets reels :
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

### Logs en temps reel

```bash
# Dev
docker-compose -f docker-compose.dev.yml logs -f

# Prod
docker-compose -f docker-compose.prod.yml logs -f

# Service specifique
docker logs -f orl-api-prod
docker logs -f orl-dashboard-prod
```

### Health Checks

```bash
docker ps --format "table {{.Names}}\t{{.Status}}"

# Detail health check
docker inspect orl-api-prod --format='{{json .State.Health}}'
```

### Ressources

```bash
# CPU/Memoire en temps reel
docker stats --no-stream

# Utilisation disque
docker system df
```

---

## 🔐 Securite

- ✅ `.env` et `.env.prod.local` git-ignored
- ✅ Aucun secret en plaintext en git
- ✅ Containers non-root (si config Dockerfile)
- ✅ `no-new-privileges:true` active (prod)
- ✅ Health checks validant sante services
- ✅ Firewall rules (port 80 seulement en prod)

---

## 🚢 Deploiement Serveur

Voir **[DEPLOY_TO_SERVER.md](./DEPLOY_TO_SERVER.md)** pour :

1. Prerequis serveur (Ubuntu 22.04+)
2. Installation Docker
3. Clonage depuis git
4. Configuration secrets
5. Build et demarrage
6. HTTPS/TLS (reverse proxy)
7. Monitoring & alerting
8. Backup automatise
9. Mise a jour code
10. Rollback d'urgence

---

## 🔄 Mise a Jour du Code

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
bash start.sh dev                # Demarrer dev
bash start.sh prod               # Demarrer prod
bash start.sh logs dev           # Logs dev
bash start.sh logs prod          # Logs prod
bash start.sh build dev          # Build dev
bash start.sh build prod         # Build prod (no-cache)
bash start.sh stop               # Arreter tout
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
**Last Updated :** 2026-05-07
**Maintainer :** ORL API Team
