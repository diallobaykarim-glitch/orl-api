#!/usr/bin/env python3
"""
Script de push des images vers Docker Hub
Utilisation: python push_to_dockerhub.py <username> <version>
"""

import subprocess
import sys

def run_command(cmd):
    """Execute une commande et affiche le resultat"""
    print(f"\n[EXEC] {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(f"[ERROR] {result.stderr}")
        return False
    return True

def push_images(username, version):
    """Push les images vers Docker Hub"""
    
    if not username or not version:
        print("Usage: python push_to_dockerhub.py <username> <version>")
        print("Example: python push_to_dockerhub.py myusername 1.0")
        sys.exit(1)
    
    images = [
        {
            "local": "orl-api-api:latest",
            "remote": f"{username}/orl-api:latest",
            "remote_versioned": f"{username}/orl-api:{version}"
        },
        {
            "local": "orl-api-dashboard:latest",
            "remote": f"{username}/orl-dashboard:latest",
            "remote_versioned": f"{username}/orl-dashboard:{version}"
        }
    ]
    
    print("=" * 60)
    print("DOCKER HUB PUSH SCRIPT")
    print("=" * 60)
    
    # Etape 1: Login
    print("\n[STEP 1] Connexion a Docker Hub...")
    if not run_command("docker login"):
        print("Echec de la connexion. Verifiez vos credentials.")
        sys.exit(1)
    
    # Etape 2: Tag images
    print("\n[STEP 2] Tagging des images...")
    for img in images:
        if not run_command(f"docker tag {img['local']} {img['remote_versioned']}"):
            sys.exit(1)
        if not run_command(f"docker tag {img['local']} {img['remote']}"):
            sys.exit(1)
    
    # Etape 3: Push images
    print("\n[STEP 3] Push vers Docker Hub...")
    for img in images:
        print(f"\nPush {img['remote_versioned']}...")
        if not run_command(f"docker push {img['remote_versioned']}"):
            sys.exit(1)
        
        print(f"Push {img['remote']} (latest)...")
        if not run_command(f"docker push {img['remote']}"):
            sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✓ PUSH COMPLET")
    print("=" * 60)
    print("\nVos images sont maintenant sur Docker Hub !")
    print("\nUtilisation :")
    for img in images:
        print(f"  docker pull {img['remote']}")
        print(f"  docker pull {img['remote_versioned']}")
    
    # Etape 4: Logout
    print("\n[STEP 4] Logout...")
    run_command("docker logout")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python push_to_dockerhub.py <username> <version>")
        print("\nExemple :")
        print("  python push_to_dockerhub.py diallobaykarim 1.0")
        sys.exit(1)
    
    username = sys.argv[1]
    version = sys.argv[2]
    
    push_images(username, version)
