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

already_killed = False

if os.path.exists(dw_pipe_path):
    os.remove(dw_pipe_path)
if os.path.exists(wd_pipe_path):
    os.remove(wd_pipe_path)

# Crée les dossiers et pipes si besoin
if not os.path.exists('pipes'):
    os.makedirs('pipes')
if not os.path.exists(dw_pipe_path):
    os.mkfifo(dw_pipe_path)
if not os.path.exists(wd_pipe_path):
    os.mkfifo(wd_pipe_path)

if not os.path.exists('hearthbeats'):
    os.makedirs('hearthbeats')

child_pids = []

def kill_children(signum, frame):
    global already_killed
    if already_killed:
        return
    already_killed = True
    print("Watchdog: Terminaison en cours...")
    for pid in child_pids:
        os.remove('hearthbeats/server_' + str(pid))
        os.kill(pid, signal.SIGTERM)
    os.remove(dw_pipe_path)
    os.remove(wd_pipe_path)
    
    sys.exit(0)

def check_alive(pid):
    try:
        os.kill(pid, signal.SIG_DFL)
        return True
    except ProcessLookupError:
        return False

def launch_server(func, args_tuple, child_pids):
    pid = os.fork()
    if pid == -1:
        print("Erreur lors du fork.")
        sys.exit(1)
    elif pid == 0:
        signal.signal(signal.SIGTERM, signal.SIG_DFL)
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        func(*args_tuple)
    else:
        print(f"Watchdog: J'ai lancé un serveur avec le PID {pid}.")
        open('hearthbeats/server_' + str(pid), 'w').close()
        child_pids.append(pid)
        return pid

if __name__ == "__main__":
    signal.signal(signal.SIGTERM, kill_children)
    signal.signal(signal.SIGINT, kill_children)

    print("Je suis le watchdog.")

    shared_mem = mmap.mmap(-1, 1024)
    pipe_in_dwtube = os.open(dw_pipe_path, os.O_RDONLY | os.O_NONBLOCK)
    pipe_out_dwtube = os.open(dw_pipe_path, os.O_WRONLY)
    pipe_in_wdtube = os.open(wd_pipe_path, os.O_RDONLY | os.O_NONBLOCK)
    pipe_out_wdtube = os.open(wd_pipe_path, os.O_WRONLY)


    dispatcher_pid = launch_server(serveur_dispatcher, (shared_mem, pipe_out_dwtube, pipe_in_wdtube), child_pids)
    worker_pid = launch_server(serveur_worker, (shared_mem, pipe_in_dwtube, pipe_out_wdtube), child_pids)

    print("Watchdog: Serveurs lancés.")

    while True:
        if not check_alive(dispatcher_pid):
            print("Watchdog: Relance du serveur dispatcher.")
            dispatcher_pid = launch_server(serveur_dispatcher, (shared_mem, pipe_out_dwtube, pipe_in_wdtube), child_pids)

        if not check_alive(worker_pid):
            print("Watchdog: Relance du serveur worker.")
            worker_pid = launch_server(serveur_worker, (shared_mem, pipe_in_dwtube, pipe_out_wdtube), child_pids)

        time.sleep(5)  # Vérifie l'état toutes les 5 secondes
