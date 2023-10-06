import os
import time
import signal
import sys
import mmap
import socket
import threading
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

child_pids = []

def kill_children(signum, frame):
    global already_killed
    if already_killed:
        return
    already_killed = True
    print("Watchdog: Terminaison en cours...")
    for pid in child_pids:
        os.remove('heartbeats/server_' + str(pid))
        os.kill(pid, signal.SIGTERM)
    os.remove(dw_pipe_path)
    os.remove(wd_pipe_path)
    
    sys.exit(0)

def handle_heartbeat(conn, pid):
    while True:
        data = conn.recv(1024)
        if not data:
            print(f"Serveur {pid} est mort.")
            break

def launch_heartbeat_monitor(pid):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('localhost', 10000 + pid))
    s.listen(1)
    conn, _ = s.accept()
    threading.Thread(target=handle_heartbeat, args=(conn, pid)).start()

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
        launch_heartbeat_monitor(pid)
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

    
       

        
