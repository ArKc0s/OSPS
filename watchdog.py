"""
Authors: Léo WADIN & Aurélien HOUDART
Date: 24 octobre 2023
Version: 2.3

Description:
    Ce script agit en tant que watchdog pour des serveurs de type "dispatcher" et "worker".
    Il réalise les tâches suivantes :
    1. Crée des dossiers et pipes nécessaires s'ils n'existent pas.
    2. Lance les serveurs "dispatcher" et "worker".
    3. Surveille la santé de ces serveurs.
    4. Arrête proprement les serveurs et nettoie en cas de signal de terminaison.
"""

import os
import time
import signal
import sys
import mmap
from dispatcher import serveur_dispatcher
from worker import serveur_worker

# Chemins vers les pipes
dw_pipe_path = 'pipes/dwtube'
wd_pipe_path = 'pipes/wdtube'

# Liste des PIDs des processus enfants
child_pids = []

# Flag pour la terminaison
already_killed = False

def create_pipes_and_dirs():
    """Crée les dossiers et pipes nécessaires."""
    if not os.path.exists('pipes'):
        os.makedirs('pipes')
    if not os.path.exists(dw_pipe_path):
        os.mkfifo(dw_pipe_path)
    if not os.path.exists(wd_pipe_path):
        os.mkfifo(wd_pipe_path)

def kill_children(signum, frame):
    """Arrête tous les processus enfants."""
    global already_killed
    if already_killed:
        return
    already_killed = True
    print("Watchdog: Terminaison en cours...")
    for pid in child_pids:
        os.kill(pid, signal.SIGTERM)
    os.remove(dw_pipe_path)
    os.remove(wd_pipe_path)
    sys.exit(0)

def launch_server(func, args_tuple):
    """Lance un serveur et ajoute son PID à la liste."""
    pid = os.fork()
    if pid == -1:
        print("Erreur lors du fork.")
        sys.exit(1)
    elif pid == 0:
        # Réinitialisation des gestionnaires de signaux pour les processus fils
        # pour les faire revenir au comportement par défaut.
        signal.signal(signal.SIGTERM, signal.SIG_DFL)
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        func(*args_tuple)
    else:
        print(f"Watchdog: J'ai lancé un serveur avec le PID {pid}.")
        child_pids.append(pid)

if __name__ == "__main__":
    # Configuration des gestionnaires de signaux
    signal.signal(signal.SIGTERM, kill_children)
    signal.signal(signal.SIGINT, kill_children)

    # Initialisation
    print("Je suis le watchdog.")
    create_pipes_and_dirs()

    # Mémoire partagée et pipes
    shared_mem = mmap.mmap(-1, 1024)
    pipe_in_dwtube = os.open(dw_pipe_path, os.O_RDONLY | os.O_NONBLOCK)
    pipe_out_dwtube = os.open(dw_pipe_path, os.O_WRONLY)
    pipe_in_wdtube = os.open(wd_pipe_path, os.O_RDONLY | os.O_NONBLOCK)
    pipe_out_wdtube = os.open(wd_pipe_path, os.O_WRONLY)

    # Lancement des serveurs
    launch_server(serveur_dispatcher, (shared_mem, pipe_out_dwtube, pipe_in_wdtube))
    launch_server(serveur_worker, (shared_mem, pipe_in_dwtube, pipe_out_wdtube))

    print("Watchdog: Serveurs lancés.")

    # Boucle de surveillance
    while True:
        time.sleep(5)  # Vérifie l'état toutes les 5 secondes

