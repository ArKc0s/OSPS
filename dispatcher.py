import os
import time
import socket
from datetime import datetime
import select

def serveur_dispatcher(shared_mem, pipe_out_dwtube, pipe_in_wdtube):
    host, port = '127.0.0.1', 42424
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
                    shared_mem.write(b"get_time" + b'\x00' * (20 - len("get_time")))
                    print("Dispatcher: J'ai écrit la commande 'get_time' dans la mémoire partagée.")
                    os.write(pipe_out_dwtube, b"ping")
            elif src == pipe_in_wdtube:
                msg = os.read(pipe_in_wdtube, 4).decode('utf-8')
                if msg == "pong" and conn:
                    shared_mem.seek(0)
                    time_response = shared_mem.read(50).decode('utf-8').rstrip('\x00')
                    print(f"Dispatcher: J'ai reçu l'heure : {time_response}")
                    conn.send(time_response.encode('utf-8'))
