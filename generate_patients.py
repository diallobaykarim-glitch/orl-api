import requests
import random
import json
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from datetime import datetime

# Configuration
API_URL = "http://localhost:8000"
NUM_PATIENTS = 33

# Set random seed for reproducibility
random.seed(42)

def generate_patient_data():
    """Genere des donnees patient aleatoires"""
    return {
        "age": random.randint(30, 85),
        "sex": random.randint(0, 1),  # 0=M, 1=F
        "smoking": random.randint(0, 3),  # 0=non, 1=ancien, 2=actuel, 3=lourd
        "alcohol": random.randint(0, 3),  # 0=non, 1=modere, 2=regulier, 3=excessif
        "dysphonia": random.randint(0, 2),  # 0=non, 1=legere, 2=severe
        "dysphagia": random.randint(0, 2),  # 0=non, 1=legere, 2=severe
        "dyspnea": random.randint(0, 2),  # 0=non, 1=legere, 2=severe
        "pain_scale": random.randint(0, 10),
        "duration_months": random.uniform(1, 24),
        "imaging_suspicious": random.randint(0, 1)  # 0=non, 1=oui
    }

def generate_patients(num=33):
    """Genere et envoie les patients a l'API"""
    results = []
    
    print(f"Generation de {num} patients...\\n")
    
    for i in range(1, num + 1):
        patient_data = generate_patient_data()
        
        # Preparer les donnees pour l'API (sans duration_months et imaging_suspicious)
        api_data = {
            "age": patient_data["age"],
            "sex": patient_data["sex"],
            "smoking": patient_data["smoking"],
            "alcohol": patient_data["alcohol"],
            "dysphonia": patient_data["dysphonia"],
            "dysphagia": patient_data["dysphagia"],
            "dyspnea": patient_data["dyspnea"],
            "pain_scale": patient_data["pain_scale"],
            "duration_months": patient_data["duration_months"],
            "imaging_suspicious": patient_data["imaging_suspicious"]
        }
        
        try:
            response = requests.post(f"{API_URL}/predict", json=api_data)
            
            if response.status_code == 200:
                prediction = response.json()
                result = {
                    "id": i,
                    **api_data,
                    "probability": prediction["probability"],
                    "risk_level": prediction["risk_level"]
                }
                results.append(result)
                print(f"[OK] Patient {i}: Risk={prediction['risk_level']}, Prob={prediction['probability']}")
            else:
                print(f"[ERROR] Patient {i}: Erreur {response.status_code} - {response.text}")
        except Exception as e:
            print(f"[ERROR] Patient {i}: {str(e)}")
    
    return results

def analyze_and_plot(results):
    """Analyse les resultats et genere des graphiques"""
    df = pd.DataFrame(results)
    
    # Creer le dossier de sortie
    import os
    os.makedirs("reports", exist_ok=True)
    
    # Statistiques generales
    print("\\n" + "="*60)
    print("STATISTIQUES GENERALES")
    print("="*60)
    print(f"Nombre de patients: {len(df)}")
    print(f"\\nRisque par niveau:")
    print(df["risk_level"].value_counts())
    print(f"\\nProbabilite de risque:")
    print(f"  Moyenne: {df['probability'].mean():.3f}")
    print(f"  Mediane: {df['probability'].median():.3f}")
    print(f"  Ecart-type: {df['probability'].std():.3f}")
    print(f"  Min: {df['probability'].min():.3f}")
    print(f"  Max: {df['probability'].max():.3f}")
    
    # Configurer le style
    sns.set_style("whitegrid")
    plt.rcParams['figure.figsize'] = (15, 12)
    
    # Figure 1: Subplots multiples (2x3)
    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    fig.suptitle("Analyse ORL IA - 33 Patients", fontsize=16, fontweight='bold')
    
    # 1. Distribution des probabilites
    axes[0, 0].hist(df['probability'], bins=12, color='steelblue', edgecolor='black', alpha=0.7)
    axes[0, 0].set_title('Distribution Probabilites Risque', fontweight='bold')
    axes[0, 0].set_xlabel('Probabilite')
    axes[0, 0].set_ylabel('Frequence')
    axes[0, 0].axvline(df['probability'].mean(), color='red', linestyle='--', label=f"Moyenne: {df['probability'].mean():.3f}")
    axes[0, 0].legend()
    
    # 2. Risque par niveau (Pie chart)
    risk_counts = df['risk_level'].value_counts()
    colors = ['#2ecc71', '#f39c12', '#e74c3c']
    axes[0, 1].pie(risk_counts.values, labels=risk_counts.index, autopct='%1.1f%%', colors=colors, startangle=90)
    axes[0, 1].set_title('Distribution Niveau Risque', fontweight='bold')
    
    # 3. Age vs Probabilite
    scatter = axes[0, 2].scatter(df['age'], df['probability'], c=df['smoking'], cmap='RdYlGn_r', s=100, alpha=0.6)
    axes[0, 2].set_title('Age vs Probabilite Risque', fontweight='bold')
    axes[0, 2].set_xlabel('Age')
    axes[0, 2].set_ylabel('Probabilite')
    plt.colorbar(scatter, ax=axes[0, 2], label='Tabagisme')
    
    # 4. Tabagisme vs Probabilite
    df.boxplot(column='probability', by='smoking', ax=axes[1, 0])
    axes[1, 0].set_title('Impact Tabagisme', fontweight='bold')
    axes[1, 0].set_xlabel('Tabagisme (0-3)')
    axes[1, 0].set_ylabel('Probabilite Risque')
    plt.sca(axes[1, 0])
    plt.xticks([1, 2, 3, 4], ['Non', 'Ancien', 'Actuel', 'Lourd'])
    
    # 5. Alcool vs Probabilite
    df.boxplot(column='probability', by='alcohol', ax=axes[1, 1])
    axes[1, 1].set_title('Impact Alcool', fontweight='bold')
    axes[1, 1].set_xlabel('Alcool (0-3)')
    axes[1, 1].set_ylabel('Probabilite Risque')
    plt.sca(axes[1, 1])
    plt.xticks([1, 2, 3, 4], ['Non', 'Modere', 'Regulier', 'Excessif'])
    
    # 6. Duree des symptomes vs Probabilite
    axes[1, 2].scatter(df['duration_months'], df['probability'], color='purple', s=100, alpha=0.6)
    axes[1, 2].set_title('Duree Symptomes vs Risque', fontweight='bold')
    axes[1, 2].set_xlabel('Duree (mois)')
    axes[1, 2].set_ylabel('Probabilite Risque')
    
    plt.tight_layout()
    plt.savefig('reports/analyse_orl_patients.png', dpi=300, bbox_inches='tight')
    print("\\n[OK] Graphique sauvegarde: reports/analyse_orl_patients.png")
    
    # Figure 2: Correlations
    fig2, ax2 = plt.subplots(figsize=(10, 8))
    numeric_cols = ['age', 'smoking', 'alcohol', 'dysphonia', 'dysphagia', 'dyspnea', 'duration_months', 'pain_scale', 'imaging_suspicious', 'probability']
    correlation = df[numeric_cols].corr()
    sns.heatmap(correlation, annot=True, fmt='.2f', cmap='coolwarm', center=0, ax=ax2, cbar_kws={'label': 'Correlation'})
    ax2.set_title('Matrice de Correlation', fontweight='bold', fontsize=14)
    plt.tight_layout()
    plt.savefig('reports/correlation_matrix.png', dpi=300, bbox_inches='tight')
    print("[OK] Graphique sauvegarde: reports/correlation_matrix.png")
    
    # Figure 3: Sexe vs Risque
    fig3, axes3 = plt.subplots(1, 2, figsize=(12, 5))
    
    sex_labels = {0: "M", 1: "F"}
    df['sex_label'] = df['sex'].map(sex_labels)
    
    sex_risk = df.groupby('sex_label')['probability'].mean()
    axes3[0].bar(sex_risk.index, sex_risk.values, color=['#3498db', '#e91e63'], alpha=0.7)
    axes3[0].set_title('Probabilite Moyenne par Sexe', fontweight='bold')
    axes3[0].set_ylabel('Probabilite Moyenne')
    
    sex_level = pd.crosstab(df['sex_label'], df['risk_level'], normalize='index') * 100
    sex_level.plot(kind='bar', ax=axes3[1], color=['#2ecc71', '#f39c12', '#e74c3c'], alpha=0.7)
    axes3[1].set_title('Repartition Risque par Sexe (%)', fontweight='bold')
    axes3[1].set_ylabel('Pourcentage')
    axes3[1].legend(title='Niveau Risque')
    plt.setp(axes3[1].xaxis.get_majorticklabels(), rotation=0)
    
    plt.tight_layout()
    plt.savefig('reports/analyse_sexe.png', dpi=300, bbox_inches='tight')
    print("[OK] Graphique sauvegarde: reports/analyse_sexe.png")
    
    # Sauvegarder les donnees en CSV
    df.to_csv('reports/patients_data.csv', index=False)
    print("[OK] Donnees sauvegardees: reports/patients_data.csv")
    
    # Rapport JSON
    report = {
        "timestamp": datetime.now().isoformat(),
        "total_patients": len(df),
        "statistics": {
            "probability": {
                "mean": float(df['probability'].mean()),
                "median": float(df['probability'].median()),
                "std": float(df['probability'].std()),
                "min": float(df['probability'].min()),
                "max": float(df['probability'].max())
            },
            "risk_distribution": df['risk_level'].value_counts().to_dict(),
            "age": {
                "mean": float(df['age'].mean()),
                "median": float(df['age'].median()),
                "std": float(df['age'].std())
            }
        },
        "sex_distribution": df['sex_label'].value_counts().to_dict()
    }
    
    with open('reports/report.json', 'w') as f:
        json.dump(report, f, indent=2)
    print("[OK] Rapport JSON sauvegarde: reports/report.json")
    
    print("\\n" + "="*60)
    print("Tous les fichiers ont ete sauvegarde dans le dossier 'reports/'")
    print("="*60)

if __name__ == "__main__":
    try:
        results = generate_patients(NUM_PATIENTS)
        
        if results:
            print(f"\\n[OK] {len(results)} patients generes avec succes")
            analyze_and_plot(results)
        else:
            print("Erreur: Aucun patient n'a pu etre genere")
    except Exception as e:
        print(f"Erreur: {str(e)}")
