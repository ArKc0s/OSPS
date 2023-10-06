import os
import time
import socket
from datetime import datetime

def serveur_dispatcher(shared_mem, pipe_out_dwtube, pipe_in_wdtube):
    host = '127.0.0.1'
    port = 42424
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    s.listen(5)
    print(f"Dispatcher: Écoute sur {host}:{port}")

    client_socket, addr = s.accept()
    print(f"Dispatcher: Connexion de {addr}")

    token = True  # Initialise avec le jeton
    requestRunning = False

    while True:  # utiliser la variable pour la condition

        # Attendre une requête du client
        if not requestRunning:
            request = client_socket.recv(1024).decode('utf-8')

        if request == "get_time":
            requestRunning = True
            if token:
                # Passer la requête au worker via mémoire partagée
                shared_mem.seek(0)
                shared_mem.write(b"get_time" + b'\x00' * (20 - len("get_time")))
                print("Dispatcher: J'ai écrit la commande 'get_time' dans la mémoire partagée.")
                
                # Informer le worker
                os.write(pipe_out_dwtube, b"ping")
                token = False
            else:
                try:
                    msg = os.read(pipe_in_wdtube, 4).decode('utf-8')
                except BlockingIOError:
                    continue

                if msg == "pong":
                    # Lire la réponse du worker dans la mémoire partagée
                    shared_mem.seek(0)
                    time_response = shared_mem.read(50).decode('utf-8').rstrip('\x00')
                    print(f"Dispatcher: J'ai reçu l'heure : {time_response}")

                    token = True

                    # Envoyer la réponse au client
                    client_socket.sendall(time_response.encode('utf-8'))
                    requestRunning = False
                    
                    
