# Guide Déploiement sur Serveur Production

## 1. Prérequis Serveur

```bash
# OS recommandé : Ubuntu 22.04 LTS / CentOS 8+
# RAM : ≥ 16GB
# Disque : ≥ 100GB (SSD recommandé)
# CPU : ≥ 4 cores

# Installer Docker & Docker Compose
sudo apt update
sudo apt install -y docker.io docker-compose git

# Ajouter l'utilisateur de déploiement au groupe docker
sudo usermod -aG docker $USER
newgrp docker

# Vérifier installation
docker --version
docker-compose --version
```

---

## 2. Cloner le Projet

```bash
# Option A : SSH (recommandé pour sécurité)
git clone git@github.com:votre-org/orl-api.git /home/deploy/orl-api

# Option B : HTTPS
git clone https://github.com/votre-org/orl-api.git /home/deploy/orl-api

# Naviguer dans le répertoire
cd /home/deploy/orl-api
```

---

## 3. Configurer les Secrets Production

```bash
# Créer .env.prod.local (git-ignored)
cp .env.prod .env.prod.local

# Éditer avec secrets réels
nano .env.prod.local

# À changer :
# - API_KEY_SECRET=votre_secret_complexe_ici
# - ALLOWED_ORIGINS=https://votre-domaine.com
# - DATABASE_URL (si pas SQLite local)
```

**Exemple `.env.prod.local` sécurisé :**
```bash
ENVIRONMENT=production
API_HOST=0.0.0.0
API_PORT=8000
DASHBOARD_PORT=8501

# Secrets (NE JAMAIS en clair en git)
API_KEY_SECRET=$(openssl rand -hex 32)
DATABASE_URL=sqlite:///./data/orl.db

# Limites production
API_MEMORY_LIMIT=3G
DASHBOARD_MEMORY_LIMIT=1.5G
NGINX_MEMORY_LIMIT=256M
```

**Permissions :**
```bash
chmod 600 .env.prod.local
ls -la .env.prod.local
# Devrait montrer : -rw------- 1 deploy deploy
```

---

## 4. Créer Répertoires de Données

```bash
# Créer répertoires persistants
mkdir -p /home/deploy/orl-api/data
mkdir -p /home/deploy/orl-api/logs

# Permissions
chmod 755 /home/deploy/orl-api/data
chmod 755 /home/deploy/orl-api/logs

# Pré-créer la base de données
touch /home/deploy/orl-api/data/orl.db
chmod 664 /home/deploy/orl-api/data/orl.db
```

---

## 5. Builder les Images Docker

```bash
cd /home/deploy/orl-api

# Build sans cache (recommandé pour prod)
docker-compose -f docker-compose.prod.yml build --no-cache

# Vérifier les images
docker images | grep orl-api

# Résultat attendu :
# orl-api-orl-api          <version>   4.1GB
# orl-api-orl-dashboard    <version>   792MB
```

---

## 6. Démarrer les Services Production

```bash
# Lancer en background
docker-compose -f docker-compose.prod.yml up -d

# Vérifier statut
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Résultat attendu :
# orl-api-prod          Up 10s (healthy)   0.0.0.0:8000->8000
# orl-dashboard-prod    Up 8s  (healthy)   0.0.0.0:8501->8501
# orl-nginx-prod        Up 5s  (healthy)   0.0.0.0:80->80
```

---

## 7. Tester Accès

```bash
# Depuis le serveur
curl http://localhost:8000/docs          # API (200 OK)
curl http://localhost:8501               # Dashboard (200 OK)
curl http://localhost/api/               # Proxy (200 OK)

# Depuis l'extérieur (remplacer par IP/domaine serveur)
curl http://123.45.67.89/api/
curl http://votre-api.com/dashboard/
```

---

## 8. Configurer Logs Persistants

```bash
# Les logs sont automatiquement archivés (json-file driver)
# Voir la config dans docker-compose.prod.yml

# Consulter les logs
docker logs orl-api-prod
docker logs orl-dashboard-prod
docker logs orl-nginx-prod

# Logs archivés (Docker gère automatiquement)
docker inspect orl-api-prod | grep LogPath
# → /var/lib/docker/containers/<ID>/<ID>-json.log

# Limites : 20MB par fichier, 10 fichiers max (200MB total par service)
```

---

## 9. Reverse Proxy Nginx Externe (Optionnel)

Si vous voulez HTTPS/TLS devant le proxy Docker :

```nginx
# /etc/nginx/sites-available/orl-api
upstream orl_api {
    server 127.0.0.1:80;
}

server {
    listen 443 ssl http2;
    server_name votre-api.com;

    ssl_certificate /etc/letsencrypt/live/votre-api.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/votre-api.com/privkey.pem;

    location / {
        proxy_pass http://orl_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

server {
    listen 80;
    server_name votre-api.com;
    return 301 https://$server_name$request_uri;
}
```

Activer :
```bash
sudo ln -s /etc/nginx/sites-available/orl-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 10. Monitoring & Alerting Basique

### CPU/Mémoire en temps réel
```bash
watch -n 2 'docker stats --no-stream'

# Ou logging continu
docker stats --no-stream > monitoring.log 2>&1 &
```

### Vérifier Health Checks
```bash
docker inspect orl-api-prod --format='{{json .State.Health}}'
# → {"Status":"healthy", "FailingStreak":0, ...}
```

### Alertes (cron job)
```bash
# /home/deploy/check-health.sh
#!/bin/bash
STATUS=$(docker inspect orl-api-prod --format='{{.State.Health.Status}}')
if [ "$STATUS" != "healthy" ]; then
  echo "ALERT: orl-api-prod is $STATUS" | mail -s "ORL API Alert" admin@company.com
fi

# Ajouter au crontab
# */5 * * * * /home/deploy/check-health.sh
```

---

## 11. Backup Automatisé

### Backup quotidien (cron)
```bash
# /home/deploy/backup.sh
#!/bin/bash
BACKUP_DIR="/backups/orl-api"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR
tar -czf $BACKUP_DIR/data-$DATE.tar.gz /home/deploy/orl-api/data/

# Garder 30 jours de backups
find $BACKUP_DIR -name "data-*.tar.gz" -mtime +30 -delete

# Ajouter au crontab (quotidien 02:00)
# 0 2 * * * /home/deploy/backup.sh
```

### Upload vers cloud (optionnel)
```bash
# Exemple avec AWS S3
aws s3 cp $BACKUP_DIR/data-$DATE.tar.gz s3://my-backup-bucket/orl-api/
```

---

## 12. Mise à Jour du Code

```bash
# Pull changes depuis git
cd /home/deploy/orl-api
git pull origin main

# Rebuild si Dockerfile changé
docker-compose -f docker-compose.prod.yml build

# Redémarrer services
docker-compose -f docker-compose.prod.yml up -d

# Vérifier
docker-compose -f docker-compose.prod.yml logs --tail=50
```

---

## 13. Rollback d'Urgence

```bash
# Si ça casse, restart avec ancienne image
docker-compose -f docker-compose.prod.yml down

# Restaurer data depuis backup
cd /home/deploy/orl-api/data
tar -xzf /backups/orl-api/data-YYYYMMDD_HHMMSS.tar.gz

# Redémarrer
docker-compose -f docker-compose.prod.yml up -d
```

---

## 14. Systemd Service (Auto-restart après reboot)

```bash
# /etc/systemd/system/orl-api.service
[Unit]
Description=ORL API Docker Compose Service
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
User=deploy
WorkingDirectory=/home/deploy/orl-api
ExecStart=/usr/bin/docker-compose -f docker-compose.prod.yml up -d
ExecStop=/usr/bin/docker-compose -f docker-compose.prod.yml down
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
```

Activer :
```bash
sudo systemctl daemon-reload
sudo systemctl enable orl-api
sudo systemctl start orl-api
```

---

## 15. Checklist Final

- [ ] Server reqs validés (RAM, disque, CPU)
- [ ] Docker/Compose installés et testés
- [ ] Projet cloné depuis git
- [ ] `.env.prod.local` créé avec secrets (chmod 600)
- [ ] Répertoires `/data` et `/logs` créés
- [ ] Images Docker buildées
- [ ] Services démarrés et healthy
- [ ] Accès validé (http://localhost et http://IP_SERVEUR)
- [ ] HTTPS configuré (reverse proxy externe)
- [ ] Logs archivés et accessibles
- [ ] Backup script opérationnel
- [ ] Monitoring actif
- [ ] Systemd service activé

---

**Status de déploiement :**
```bash
docker ps
docker-compose -f docker-compose.prod.yml logs
curl http://localhost/api/
```

Si tout est vert → **Production Live ✅**
