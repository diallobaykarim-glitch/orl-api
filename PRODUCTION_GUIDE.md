# Guide Production - ORL API : Security, Optimization, Hub & AI

Documentation pour les 4 etapes de production : Scanner, Optimisation, Docker Hub, Model Runner.

---

## 1. SCANNER SECURITE (Docker Scout)

### Qu'est-ce que Docker Scout ?

Docker Scout scanne vos images pour detecter les vulnerabilites de securite (CVE).

### Commandes

```bash
# Scan rapide
docker scout quickview orl-api-api:latest

# Scan detaille des CVE
docker scout cves orl-api-api:latest

# Scan dashboard
docker scout cves orl-api-dashboard:latest
```

### Interpreter les resultats

Les vulnerabilites sont classees par severite :

- **CRITICAL** — Faille grave, patch immediatement
- **HIGH** — Faille importante, patcher bientot
- **MEDIUM** — Faille moderee, patcher dans le mois
- **LOW** — Faille mineure, patcher a terme

### Exemple resultat

```
Vulnerabilities

  CRITICAL (0)
  
  HIGH (2)
    CVE-2024-1234 — OpenSSL vulnerability in python:3.10
    → Update to python:3.10.13 or later
    
  MEDIUM (5)
    ...
    
  LOW (3)
    ...

Recommendations:
  Update base image to python:3.10-slim
  → Reduces vulnerabilities by 80%
```

### Recommandations

1. Utiliser images `-slim` (plus petit, moins vulnerable)
2. Scanner avant chaque push
3. Mettre a jour dependances regulierement
4. Utiliser images officielles (postgres, nginx, python)

---

## 2. OPTIMISER IMAGES (Multi-Stage Build)

### Pourquoi optimiser ?

- **Avant** : Image build + dependencies = 800 MB
- **Apres** : Image runtime minimal = 200 MB
- **Resultat** : 75% plus petit, plus rapide, plus securise

### Comparaison

#### Dockerfile Simple (NON-OPTIMISE)

```dockerfile
FROM python:3.10
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]
```

**Problemes :**
- python:3.10 entier (900 MB)
- Tous les outils build restes dans l'image finale
- Pas d'utilisateur non-root (risque securite)

#### Dockerfile Multi-Stage (OPTIMISE)

```dockerfile
# STAGE 1: Builder
FROM python:3.10-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir -r requirements.txt

# STAGE 2: Runtime
FROM python:3.10-slim
WORKDIR /app
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY . .
RUN useradd -m -u 1000 appuser && chown -R appuser /app
USER appuser
CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]
```

**Avantages :**
- `-slim` au lieu de complet (200 MB vs 900 MB)
- Venv uniquement (dependances seules)
- Utilisateur non-root (securite +)
- Image finale : 250 MB au lieu de 1.5 GB

### Fichiers optimises fournis

- `app/Dockerfile.optimized` — API multi-stage
- `dashboard/Dockerfile.optimized` — Dashboard multi-stage

### Build avec images optimisees

```bash
# Option 1: Utiliser les fichiers .optimized
docker build -f app/Dockerfile.optimized -t orl-api-api:optimized ./app

# Option 2: Remplacer les fichiers originaux
cp app/Dockerfile app/Dockerfile.backup
cp app/Dockerfile.optimized app/Dockerfile
docker compose build
```

### Verifier reduction taille

```bash
# Avant
docker images orl-api-api
# REPOSITORY          TAG        SIZE
# orl-api-api         latest     1.2GB

# Apres
docker images orl-api-api
# REPOSITORY          TAG        SIZE
# orl-api-api         optimized  280MB
```

---

## 3. DOCKER HUB (Push Images)

### Qu'est-ce que Docker Hub ?

Registre centralisé (marketplace) pour vos images Docker. Vous pouvez :
- Partager images publiquement
- Stocker images privees
- Distribuer vos apps globalement

### URL

https://hub.docker.com

### Preparation

1. **Creer compte Docker Hub**
   - Aller a https://hub.docker.com/signup
   - Email + mot de passe
   - Verifier email

2. **Obtenir username**
   - Votre username Docker Hub est affiche sur votre profil
   - Exemple: `diallobaykarim`

3. **Creer token (optionnel mais recommande)**
   - Profil → Account Settings → Security → New Access Token
   - Utiliser ce token au lieu du mot de passe

### Push Script

Un script Python `push_to_dockerhub.py` est fourni pour automatiser le push.

**Usage :**

```bash
python push_to_dockerhub.py <username> <version>
```

**Exemple :**

```bash
python push_to_dockerhub.py diallobaykarim 1.0
```

**Le script fait :**
1. docker login (demande username + password/token)
2. Tag images avec versioning
3. Push vers Docker Hub
4. docker logout

**Resultat :**
```
Vos images publiees sur Docker Hub :
- diallobaykarim/orl-api:1.0
- diallobaykarim/orl-api:latest
- diallobaykarim/orl-dashboard:1.0
- diallobaykarim/orl-dashboard:latest
```

### Utilisation apres push

Quiconque peut maintenant utiliser vos images :

```bash
docker pull diallobaykarim/orl-api:1.0
docker run -p 8000:8000 diallobaykarim/orl-api:1.0
```

### Commandes manuelles (sans script)

Si vous preferez faire manuellement :

```bash
# 1. Login
docker login

# 2. Tag
docker tag orl-api-api:latest diallobaykarim/orl-api:1.0
docker tag orl-api-api:latest diallobaykarim/orl-api:latest

# 3. Push
docker push diallobaykarim/orl-api:1.0
docker push diallobaykarim/orl-api:latest

# 4. Logout
docker logout
```

### Gerer vos images sur le Hub

```bash
# Voir sur Docker Hub
# https://hub.docker.com/r/diallobaykarim/orl-api

# Supprimer une image
# Docker Hub web UI → Image → Delete

# Rendre prive
# Docker Hub web UI → Settings → Make Private
```

---

## 4. MODEL RUNNER (Recommandations IA)

### Qu'est-ce que Model Runner ?

Service Docker pour executer des modeles IA (LLM) comme Llama2, Mistral, etc.

### Configuration

#### docker-compose.ai.yml fourni

Le fichier `docker-compose.ai.yml` inclut le service Model Runner (Ollama).

**Services :**
- PostgreSQL (db)
- FastAPI (api)
- Streamlit (dashboard)
- **Ollama (model-runner)** — NEW

#### Demarrer avec Model Runner

```bash
# Avec Model Runner
docker compose -f docker-compose.ai.yml up -d

# Seulement Model Runner
docker compose -f docker-compose.ai.yml up -d model-runner
```

#### Verifier

```bash
# Lister models disponibles
curl http://localhost:11434/api/tags

# Health check
curl http://localhost:11434/api/tags | jq .
```

### Telecharger un model

Par defaut, pas de model inclus. Telecharger un :

```bash
# Telecharger Llama2 (4 GB)
docker exec orl-model-runner ollama pull llama2

# Ou Mistral (3.5 GB)
docker exec orl-model-runner ollama pull mistral

# Ou Neural Chat (4 GB)
docker exec orl-model-runner ollama pull neural-chat
```

Voir tous les models : https://ollama.ai/library

### Utiliser Model Runner depuis Python

Script `ai_recommendations.py` genere des recommandations IA pour patients.

**Usage :**

```bash
# 1. Demarrer tous les services
docker compose -f docker-compose.ai.yml up -d

# 2. Telecharger un model
docker exec orl-model-runner ollama pull llama2

# 3. Lancer le script recommandations
python ai_recommendations.py
```

**Resultat exemple :**

```
PATIENT 1
Age: 45 | Sexe: H | Risque: Eleve
Probabilite: 75.4%

Generation recommandation IA...

Recommandation:
Ce patient presente une probabilite elevee de pathologie ORL. 
Recommande une consultation ORL urgente avec imagerie. 
Evaluer tabagisme actuel et impacts sur voies aeriennes superieures.
```

### API Model Runner

Utiliser directement l'API :

```python
import requests

response = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "llama2",
        "prompt": "Quel est le traitement de la dysphonie ?",
        "stream": False
    }
)

print(response.json()["response"])
```

### Intégrer dans votre API FastAPI

Exemple d'endpoint avec recommandations IA :

```python
@app.post("/predict-with-ai")
def predict_with_ai(data: PatientData):
    # Prediction existante
    prediction = predict(data)
    
    # Generer recommandation IA
    prompt = f"Patient age {data.age} avec probabilite {prediction['probability']}"
    ai_response = requests.post(
        "http://model-runner:11434/api/generate",
        json={"model": "llama2", "prompt": prompt, "stream": False}
    )
    
    return {
        "prediction": prediction,
        "ai_recommendation": ai_response.json()["response"]
    }
```

### Performance & Ressources

- **Llama2** : 4 GB RAM, ~2-5 sec par requete
- **Mistral** : 3.5 GB RAM, ~1-3 sec par requete
- **Neural Chat** : 4 GB RAM, ~1-2 sec par requete

Augmentez les limites memoire dans docker-compose si lent :

```yaml
model-runner:
  deploy:
    resources:
      limits:
        memory: 8G
      reservations:
        memory: 4G
```

---

## 🔄 Workflow Complet Production

### 1. Developpement Local
```bash
docker compose up -d
python generate_patients.py
# Tester sur localhost:8000, :8501
```

### 2. Optimiser Images
```bash
docker build -f app/Dockerfile.optimized -t orl-api-api:optimized ./app
docker scout cves orl-api-api:optimized
```

### 3. Scanner Securite
```bash
docker scout cves orl-api-api:optimized
# Verifier aucune CRITICAL
```

### 4. Push vers Hub
```bash
python push_to_dockerhub.py votre-username 1.0
```

### 5. Deployer Production
```bash
# Sur serveur
docker pull votre-username/orl-api:1.0
docker run -d -p 8000:8000 votre-username/orl-api:1.0
```

### 6. Ajouter IA (optionnel)
```bash
docker compose -f docker-compose.ai.yml up -d
docker exec orl-model-runner ollama pull llama2
python ai_recommendations.py
```

---

## 📋 Checklist Production

- [ ] Images scannees avec Docker Scout
- [ ] Aucune vulnerabilite CRITICAL
- [ ] Images optimisees (multi-stage)
- [ ] Taille image < 500 MB
- [ ] Utilisateur non-root dans Dockerfile
- [ ] Images taggees avec version
- [ ] Images pushees vers Docker Hub
- [ ] Tests passent sur images Hub
- [ ] Model Runner (optionnel) configures
- [ ] Recommandations IA fonctionnelles

---

## 🆘 Troubleshooting

### Scout timeout
```bash
# Scout peut etre lent, augmentez le timeout
docker scout cves --timeout 120 orl-api-api:latest
```

### Push Docker Hub echoue
```bash
# Verifier login
docker login

# Verifier username correct
docker tag orl-api-api:latest YOUR_USERNAME/orl-api:latest

# Push avec username correct
docker push YOUR_USERNAME/orl-api:latest
```

### Model Runner lent
```bash
# Verifier disponibilite CPU/RAM
docker stats orl-model-runner

# Augmenter limites dans docker-compose.ai.yml
# Augmenter memory limite
```

### Ollama model non trouve
```bash
# Lister models installes
docker exec orl-model-runner ollama list

# Si aucun, telecharger
docker exec orl-model-runner ollama pull llama2
```

---

**Version :** 1.0
**Date :** 2026-05-07
