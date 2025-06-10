from contextlib import chdir
import os

# Création du dossier s'il n'existe pas
courses_dir = "courses"  # Suppression de l'espace en trop
os.makedirs(courses_dir, exist_ok=True)

with chdir(courses_dir):
    print("Téléchargement en cours...")
    result = os.system("moodle-dl")
    if result == 0:
        print("✅ Téléchargement terminé")
    else:
        print("❌ Erreur lors du téléchargement")