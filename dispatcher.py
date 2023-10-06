import os
import time
import socket
from datetime import datetime
import select

def serveur_dispatcher(shared_mem, pipe_out_dwtube, pipe_in_wdtube):
    host, port = '127.0.0.1', 42424
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, port))
    s.listen(5)
    s.setblocking(0)  # non-blocking

    inputs = [s, pipe_in_wdtube]  # ajouter d'autres sockets ou des fichiers ici si nécessaire

    print(f"Dispatcher: Écoute sur {host}:{port}")

    conn = None  # Initialisation de la variable conn
    while True:
        readable, _, _ = select.select(inputs, [], [])
        for src in readable:
            if src == s:
                # Nouvelle connexion
                if conn:  # Si une ancienne connexion existe, on la ferme
                    inputs.remove(conn)
                    conn.close()
                conn, addr = s.accept()
                conn.setblocking(0)
                inputs.append(conn)
                print(f"Dispatcher: Connexion de {addr}")
            elif src == conn:
                data = conn.recv(1024)
                if data:
                    print(f"Dispatcher: Requête reçue du client : {data.decode()}")
                    shared_mem.seek(0)
                    # ecrire les infos du client dans la mémoire partagée avec un message signalant qu'il y'a une requête
                    shared_mem.write((data.decode() + ' ' + str(addr) + '\x00' * (100 - len(data.decode()))).encode('utf-8'))
                    print("Dispatcher: J'ai envoyé la demande au worker.")
                    os.write(pipe_out_dwtube, b"ping")
                    # fermer la connexion
                    inputs.remove(conn)
                    conn.close()
                    conn = None
                    print("Dispatcher: J'ai fermé la connexion avec le client.")
            elif src == pipe_in_wdtube:
                msg = os.read(pipe_in_wdtube, 4).decode('utf-8')
                if msg == "pong":
                    print(f"Dispatcher: Je sais que le worker est de nouveau prêt.")