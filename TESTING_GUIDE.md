# Guide de Tests Statistiques - ORL API

Documentation complete pour generer et analyser les tests avec 33 patients.

---

## 1. Prerequisites

Installer les dependances necessaires :

```bash
pip install pandas matplotlib seaborn requests
```

Ou directement depuis requirements :

```bash
pip install -r requirements.txt
```

---

## 2. Lancer le Script de Genération

### Sur une session Docker active

Assurez-vous que l'API est demarree :

```bash
# Terminal 1 : Demarrer l'API
docker compose up

# Terminal 2 : Lancer le script de test
cd C:\Users\UTILISATEUR\orl-api-test\orl-api
python generate_patients.py
```

### Sortie attendue

```
Generation de 33 patients...

[OK] Patient 1: Risk=Eleve, Prob=0.644
[OK] Patient 2: Risk=Eleve, Prob=0.601
...
[OK] Patient 33: Risk=Eleve, Prob=0.768

[OK] 33 patients generes avec succes

============================================================
STATISTIQUES GENERALES
============================================================
Nombre de patients: 33
Risque par niveau:
risk_level
Eleve     32
Modere     1
Name: count, dtype: int64

Probabilite de risque:
  Moyenne: 0.754
  Mediane: 0.763
  Ecart-type: 0.080
  Min: 0.581
  Max: 0.906

[OK] Graphique sauvegarde: reports/analyse_orl_patients.png
[OK] Graphique sauvegarde: reports/correlation_matrix.png
[OK] Graphique sauvegarde: reports/analyse_sexe.png
[OK] Donnees sauvegardees: reports/patients_data.csv
[OK] Rapport JSON sauvegarde: reports/report.json

============================================================
Tous les fichiers ont ete sauvegarde dans le dossier 'reports/'
============================================================
```

---

## 3. Fichiers Generes

### 📊 Graphiques

#### analyse_orl_patients.png
6 sous-graphiques en une seule image (2 lignes x 3 colonnes) :

1. **Distribution des Probabilites** (Histogramme)
   - Affiche la distribution des 33 scores de risque
   - Ligne rouge : moyenne (0.754)
   - Permet d'identifier les clusters de risque

2. **Distribution Niveau Risque** (Pie Chart)
   - 32 patients Eleve (96.9%)
   - 1 patient Modere (3.1%)
   - Aucun patient a faible risque

3. **Age vs Probabilite** (Scatter Plot)
   - Points colores par niveau de tabagisme
   - Identifie la correlation age-risque
   - Couleurs : vert (non-fumeurs) a rouge (gros fumeurs)

4. **Impact du Tabagisme** (Box Plot)
   - 4 categories : Non (0), Ancien (1), Actuel (2), Lourd (3)
   - Montre la mediane, quartiles, outliers
   - Tabagisme lourd = risque plus eleve

5. **Impact de l'Alcool** (Box Plot)
   - 4 categories : Non (0), Modere (1), Regulier (2), Excessif (3)
   - Meme format que tabagisme
   - Alcool excessif = impact sur le risque

6. **Duree Symptomes vs Risque** (Scatter Plot)
   - X : duree en mois (1-24)
   - Y : probabilite de risque
   - Identifie si la duree augmente le risque

#### correlation_matrix.png
Heatmap montrant les correlations entre toutes les variables :

- Variables : age, smoking, alcohol, dysphonia, dysphagia, dyspnea, duration_months, pain_scale, imaging_suspicious, probability
- Couleurs : bleu (correlation negative) a rouge (positive)
- Permet d'identifier les facteurs cles de risque

#### analyse_sexe.png
Deux graphiques comparant Hommes vs Femmes :

1. **Probabilite Moyenne par Sexe** (Bar Chart)
   - Bleu : Hommes
   - Rose : Femmes
   - Compare les niveaux moyens de risque

2. **Repartition Risque par Sexe** (Stacked Bar Chart)
   - Vert : Faible
   - Orange : Modere
   - Rouge : Eleve
   - Montre la distribution en % pour H et F

---

### 📄 Donnees Structurees

#### patients_data.csv
Fichier CSV avec 33 lignes (patients) et colonnes :

```
id, age, sex, smoking, alcohol, dysphonia, dysphagia, dyspnea, pain_scale, duration_months, imaging_suspicious, probability, risk_level
1, 45, 0, 2, 1, 1, 0, 0, 5, 12.34, 1, 0.644, Eleve
2, 67, 1, 3, 2, 2, 1, 1, 8, 18.56, 0, 0.601, Eleve
...
```

**Utilisation :**
- Importer dans Excel, Python, R pour analyses supplementaires
- `pandas.read_csv('reports/patients_data.csv')`
- Filtrer/grouper les donnees

#### report.json
Rapport structure avec statistiques agrégees :

```json
{
  "timestamp": "2026-05-07T01:28:22.123456",
  "total_patients": 33,
  "statistics": {
    "probability": {
      "mean": 0.754,
      "median": 0.763,
      "std": 0.080,
      "min": 0.581,
      "max": 0.906
    },
    "risk_distribution": {
      "Eleve": 32,
      "Modere": 1
    },
    "age": {
      "mean": 58.5,
      "median": 59.0,
      "std": 15.3
    },
    "sex_distribution": {
      "M": 17,
      "F": 16
    }
  }
}
```

**Utilisation :**
- Parser en JSON pour dashboards/API
- Intégrer dans des rapports automatisés
- Comparer resultats multi-runs

---

## 4. Script generate_patients.py - Details Techniques

### Fonction generate_patient_data()

Genere les donnees d'un patient aleatoire :

```python
{
    "age": 30-85 ans,
    "sex": 0 (Homme) ou 1 (Femme),
    "smoking": 0-3 (Non a Lourd),
    "alcohol": 0-3 (Non a Excessif),
    "dysphonia": 0-2 (Voix rauque),
    "dysphagia": 0-2 (Difficulte avaler),
    "dyspnea": 0-2 (Difficulte respirer),
    "pain_scale": 0-10 (Echelle douleur),
    "duration_months": 1-24 mois,
    "imaging_suspicious": 0-1 (Resultat imagerie)
}
```

### Fonction generate_patients(num=33)

- Boucle 33 fois
- Pour chaque patient :
  - Genere donnees aleatoires
  - Envoie POST a `http://localhost:8000/predict`
  - Stocke reponse (probability, risk_level)
  - Affiche statut [OK] ou [ERROR]

### Fonction analyze_and_plot(results)

- Convertit resultats en DataFrame Pandas
- Cree 3 figures matplotlib avec sous-graphiques
- Sauvegarde en PNG (300 DPI, haute resolution)
- Exporte CSV et JSON
- Affiche statistiques dans la console

---

## 5. Interpreting Results

### Probabilite de Risque (0-1)

- **0.0 - 0.4** : Risque Faible
- **0.4 - 0.6** : Risque Modere
- **0.6 - 1.0** : Risque Eleve

### Facteurs d'Impact (ordre d'importance)

D'apres le modele API :

1. **Imagerie suspecte** (+3.0) — plus gros impact
2. **Dysphonia** (+2.0)
3. **Tabagisme** (+2.0)
4. **Dysphagia** (+1.5)
5. **Alcool** (+1.5)
6. **Douleur** (+0.2)
7. **Duree symptomes** (+0.1 par mois)
8. **Age** (+0.015 par an)

### Exemple d'Interpretation

Patient avec score 0.754 (Eleve) :
- Age moyen (45-60 ans)
- Fumeur ou ancien fumeur
- Consommation alcool moderee
- Symptomes depuis 3-6 mois
- Imagerie suspecte ou dysphonia presentes

---

## 6. Regenerer les Tests

Pour relancer avec de nouvelles donnees aleatoires :

```bash
# Option 1 : Relancer directement
python generate_patients.py

# Option 2 : Vider d'abord le dossier reports/
rm -r reports/*
python generate_patients.py

# Option 3 : Backup ancien rapport
mv reports reports_backup_2026-05-07
python generate_patients.py
```

---

## 7. Troubleshooting

### Erreur: "Connection refused" ou ERR_EMPTY_RESPONSE

**Cause :** L'API n'est pas demarree

**Solution :**
```bash
docker compose up -d
docker ps  # Verifier que orl-api est Up
python generate_patients.py
```

### Erreur: "Aucun patient n'a pu etre genere"

**Cause :** Tous les POST retournent erreur 422 (validation)

**Solution :**
```bash
# Verifier structure schéma
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"age":45, "sex":0, "smoking":1, "alcohol":1, "dysphonia":0, "dysphagia":0, "dyspnea":0, "pain_scale":5, "duration_months":10.0, "imaging_suspicious":0}'

# Verifier logs API
docker logs orl-api
```

### Graphiques ne s'affichent pas

**Cause :** Matplotlib ne peut pas sauvegarder

**Solution :**
```bash
# Verifier permissions dossier
mkdir -p reports
chmod 755 reports

# Verifier installation matplotlib
python -c "import matplotlib; print(matplotlib.__version__)"
```

### Donnees de 33 patients incorrectes ou extremes

**Cause :** Aleatoire avec seed=42

**Solution :**
```python
# Modifier seed dans generate_patients.py
random.seed(123)  # Nouveau seed

# Ou supprimer seed pour vraie aleatoirete
# random.seed(42)  # Commenter cette ligne
```

---

## 8. Integration CI/CD

### GitHub Actions Exemple

Creer `.github/workflows/test.yml` :

```yaml
name: Run Statistical Tests

on:
  push:
    branches: [main]
  schedule:
    - cron: '0 0 * * 0'  # Chaque dimanche

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      api:
        image: orl-api-api:latest
        ports:
          - 8000:8000

    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: pip install -r requirements.txt pandas matplotlib seaborn
      
      - name: Run tests
        run: python generate_patients.py
      
      - name: Upload reports
        uses: actions/upload-artifact@v2
        with:
          name: test-reports
          path: reports/
```

---

## 9. Prochaines Etapes

- [ ] Ajouter tests unitaires (pytest)
- [ ] Ajouter validation schema Pydantic
- [ ] Creer endpoint `/generate-test-patients` dans API
- [ ] Automatiser tests via CI/CD
- [ ] Exporter rapports en PDF
- [ ] Ajouter alertes si probabilite moyenne > seuil
- [ ] Comparer resultats entre versions modele

---

## 10. Contact & Questions

Pour questions sur l'analyse statistique ou le script :
- Consulter les logs : `docker logs orl-api`
- Verifier la structure CSV : ouvrir `reports/patients_data.csv` dans Excel
- Examiner graphiques PNG : tous les fichiers dans `reports/`
- Lire rapport JSON : `cat reports/report.json`

---

**Version :** 1.0
**Date :** 2026-05-07
**Script :** generate_patients.py
