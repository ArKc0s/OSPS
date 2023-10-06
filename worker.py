import os
import time
import mmap
import signal
import threading
import socket
from datetime import datetime

def send_heartbeat_to_watchdog(pid):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('localhost', 10000 + pid))
    while True:
        s.sendall(b'heartbeat')
        time.sleep(2)

def serveur_worker(shared_mem, pipe_in_dwtube, pipe_out_wdtube):
    threading.Thread(target=send_heartbeat_to_watchdog, args=(os.getpid(),)).start()
    while True:

        try:
            msg = os.read(pipe_in_dwtube, 4).decode('utf-8')
        except BlockingIOError:
            continue
        if msg == "ping":
            shared_mem.seek(0)
            command = shared_mem.read(20).decode('utf-8').rstrip('\x00')
            if command == "get_time":
                print(f"Worker: J'ai reçu la commande : {command}")
                current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                shared_mem.seek(0)
                shared_mem.write((current_time + '\x00' * (50 - len(current_time))).encode('utf-8'))
                print(f"Worker: J'ai écrit l'heure : {current_time}")
            os.write(pipe_out_wdtube, b"pong")
        else:
            print("Worker: En attente du jeton...")
        time.sleep(2)
