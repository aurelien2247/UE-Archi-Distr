import subprocess
import os
import sys

# Les répertoires des projets et les scripts à exécuter
projects = {
    "movie": "movie.py",    # Exécuter le composant movie
    "user": "user.py",      # Exécuter le composant user
    "booking": "booking.py",  # Nouveau microservice gRPC
}

processes = []

# Lancer les scripts pour chaque projet
for project, script in projects.items():
    db_path = os.path.join(project, 'databases', f"{project}s.json")  # Construire le chemin vers la base de données JSON
    print(f"Lancement du composant {project}")
    
    # Commande pour activer l'environnement virtuel et exécuter le script
    command = f"{os.path.join('shared_env', 'Scripts', 'activate')} & python {os.path.join(project, script)} {db_path}"
    
    # Lancer le script en tant que processus en arrière-plan
    process = subprocess.Popen(command, shell=True)
    processes.append(process)

# Afficher un message après le lancement de tous les scripts
print("")
print("----- Les composants sélectionnés ont été lancés, vous pouvez tester leur fonctionnement -----")
print("")

# Optionnel : Attendre que tous les processus se terminent (dans ce cas, cela ne se fera pas car ce sont des serveurs)
# Vous pouvez choisir de ne pas attendre ou d'ajouter une méthode pour les arrêter plus tard.
try:
    while True:
        pass  # Boucle infinie pour garder le script en cours d'exécution
except KeyboardInterrupt:
    print("Arrêt des serveurs...")
    for process in processes:
        process.terminate()  # Arrêter les serveurs lorsque vous le souhaitez
    print("Tous les serveurs ont été arrêtés.")
