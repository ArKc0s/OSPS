import os
import time
import sys
import signal
import mmap
from datetime import datetime

def serveur_dispatcher(shared_mem, pipe_out_dwtube, pipe_in_wdtube):
    token = True  # Initialise avec le jeton
    while True:
        if token:
            shared_mem.seek(0)
            shared_mem.write(b"get_time")
            print("Dispatcher: J'ai écrit la commande 'get_time' dans la mémoire partagée.")
            os.write(pipe_out_dwtube, b"ping")
            token = False
        else:
            msg = os.read(pipe_in_wdtube, 4).decode('utf-8')
            if msg == "pong":
                shared_mem.seek(0)
                time_response = shared_mem.read(50).decode('utf-8')
                print(f"Dispatcher: J'ai reçu l'heure : {time_response}")
                token = True
        time.sleep(2)

def serveur_worker(shared_mem, pipe_in_dwtube, pipe_out_wdtube):
    while True:
        msg = os.read(pipe_in_dwtube, 4).decode('utf-8')
        if msg == "ping":
            shared_mem.seek(0)
            command = shared_mem.read(20).decode('utf-8').strip()
            if command == "get_time":
                current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                shared_mem.seek(0)
                shared_mem.write(current_time.encode('utf-8'))
                print(f"Worker: J'ai écrit l'heure : {current_time}")
            os.write(pipe_out_wdtube, b"pong")
        else:
            print("Worker: En attente du jeton...")
        time.sleep(2)

def kill_children(signum, frame):
    global child_pids
    print("Watchdog: Terminaison en cours...")
    for pid in child_pids:
        os.kill(pid, signal.SIGTERM)
    sys.exit(0)

if __name__ == "__main__":
    global child_pids
    child_pids = []

    shared_mem = mmap.mmap(-1, 1024)

    pipe_in_dwtube, pipe_out_dwtube = os.pipe()
    pipe_in_wdtube, pipe_out_wdtube = os.pipe()

    signal.signal(signal.SIGTERM, kill_children)
    signal.signal(signal.SIGINT, kill_children)

    print("Je suis le watchdog.")

    pid = os.fork()
    if pid == -1:
        print("Erreur lors du fork pour le serveur dispatcher.")
        sys.exit(1)
    elif pid == 0:
        os.close(pipe_in_dwtube)
        os.close(pipe_out_wdtube)
        serveur_dispatcher(shared_mem, pipe_out_dwtube, pipe_in_wdtube)
    else:
        child_pids.append(pid)

        pid = os.fork()
        if pid == -1:
            print("Erreur lors du fork pour le serveur worker.")
            sys.exit(1)
        elif pid == 0:
            os.close(pipe_out_dwtube)
            os.close(pipe_in_wdtube)
            serveur_worker(shared_mem, pipe_in_dwtube, pipe_out_wdtube)
        else:
            child_pids.append(pid)
            print("Watchdog: J'ai lancé les serveurs.")

    while True:
        time.sleep(1)
