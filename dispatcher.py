import os
import time
import mmap
from datetime import datetime

def serveur_dispatcher(shared_mem, pipe_out_dwtube, pipe_in_wdtube):
    token = True  # Initialise avec le jeton
    while True:
        if token:
            shared_mem.seek(0)
            shared_mem.write(b"get_time" + b'\x00' * (20 - len("get_time")))
            print("Dispatcher: J'ai écrit la commande 'get_time' dans la mémoire partagée.")
            os.write(pipe_out_dwtube, b"ping")
            token = False
        else:
            try:
                msg = os.read(pipe_in_wdtube, 4).decode('utf-8')
            except BlockingIOError:
                continue
            if msg == "pong":
                shared_mem.seek(0)
                time_response = shared_mem.read(50).decode('utf-8').rstrip('\x00')
                print(f"Dispatcher: J'ai reçu l'heure : {time_response}")
                token = True
        time.sleep(2)
