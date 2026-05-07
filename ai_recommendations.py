#!/usr/bin/env python3
"""
Script pour generer des recommandations IA a partir des predictions ORL
Utilise le Model Runner (Ollama) pour generer du texte intelligent
"""

import requests
import json
import sys

# Configuration
API_URL = "http://localhost:8000"
MODEL_URL = "http://localhost:11434"
MODEL_NAME = "llama2"

def get_patients():
    """Recupere la liste des patients"""
    try:
        response = requests.get(f"{API_URL}/patients", timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Erreur connexion API: {e}")
    return []

def generate_recommendation(patient_data, prediction):
    """Genere une recommandation IA pour un patient"""
    
    prompt = f"""Vous etes un assistant medical specialise en ORL (oto-rhino-laryngologie).
    
Donnees patient:
- Age: {patient_data.get('age')} ans
- Sexe: {'Homme' if patient_data.get('sex') == 0 else 'Femme'}
- Tabagisme: {patient_data.get('smoking')}/3
- Alcool: {patient_data.get('alcohol')}/3
- Dysphonie: {'Oui' if patient_data.get('dysphonia') else 'Non'}
- Dysphagie: {'Oui' if patient_data.get('dysphagia') else 'Non'}
- Dyspnee: {'Oui' if patient_data.get('dyspnea') else 'Non'}
- Echelle douleur: {patient_data.get('pain_scale')}/10
- Duree symptomes: {patient_data.get('duration_months')} mois
- Imagerie suspecte: {'Oui' if patient_data.get('imaging_suspicious') else 'Non'}

Resultat prediction:
- Probabilite de risque: {prediction.get('probability'):.1%}
- Niveau de risque: {prediction.get('risk_level')}

Generez une recommandation medicale breve (2-3 phrases) pour ce patient."""
    
    try:
        response = requests.post(
            f"{MODEL_URL}/api/generate",
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False,
                "temperature": 0.7
            },
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get('response', '').strip()
    except Exception as e:
        print(f"Erreur Model Runner: {e}")
    
    return None

def main():
    print("\n" + "="*70)
    print("GENERATEUR DE RECOMMANDATIONS IA - ORL API")
    print("="*70)
    
    # Verification services
    print("\n[CHECK] Verification des services...")
    
    try:
        api_check = requests.get(f"{API_URL}/", timeout=5)
        print(f"✓ API: {api_check.status_code} OK")
    except:
        print("✗ API: Non accessible sur localhost:8000")
        return
    
    try:
        model_check = requests.get(f"{MODEL_URL}/api/tags", timeout=5)
        print(f"✓ Model Runner: Accessible")
    except:
        print("✗ Model Runner: Non accessible sur localhost:11434")
        print("  Demarrez-le avec: docker compose -f docker-compose.ai.yml up -d model-runner")
        return
    
    # Recuperer patients
    print("\n[FETCH] Recuperation des patients...")
    patients = get_patients()
    
    if not patients:
        print("Aucun patient trouve. Generez d'abord les donnees de test.")
        return
    
    print(f"✓ {len(patients)} patients trouves")
    
    # Generer recommandations pour les premiers 3 patients
    print("\n[AI] Generation de recommandations (premiers 3 patients)...\n")
    
    for i, patient in enumerate(patients[:3], 1):
        print(f"\n{'-'*70}")
        print(f"PATIENT {i}")
        print(f"{'-'*70}")
        print(f"Age: {patient.get('age')} | Sexe: {'H' if patient.get('sex')==0 else 'F'} | Risque: {patient.get('risk_level', 'N/A')}")
        print(f"Probabilite: {patient.get('probability', 0):.1%}")
        
        # Generer recommandation
        print("\nGeneration recommandation IA...")
        recommendation = generate_recommendation(patient, patient)
        
        if recommendation:
            print(f"\nRecommandation:\n{recommendation}")
        else:
            print("Impossible de generer la recommandation")
    
    print("\n" + "="*70)
    print("COMPLET")
    print("="*70)

if __name__ == "__main__":
    main()
