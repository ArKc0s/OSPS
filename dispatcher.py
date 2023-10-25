"""
Authors: Léo WADIN & Aurélien HOUDART
Date: 24 octobre 2023
Version: 3.2

Description:
    Ce script réalise les étapes suivantes :
        1. Ouvre un socket d'écoute sur l'adresse et le port donnés.
        2. Attend une requête du client.
        3. Transmet la requête au worker.
        4. Attend la réponse du worker contenant ses données de connexion.
        5. Transmet les données de connexion au client.
        6. Ferme la connexion avec le client.
        7. Retourne à l'étape 2.

    Note : Des timeouts sont ajoutés pour chaque opération réseau pour une meilleure robustesse.
"""

import server
import os
import time
import socket
import select

ADDR = '127.0.0.1'
PORT = 42424

def serveur_dispatcher(shared_mem, pipe_out_dwtube, pipe_in_wdtube):

    is_worker_ready = True

    while True:  # Boucle pour réessayer la création du socket
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((ADDR, PORT))
            s.listen(5)
            s.setblocking(0)  # non-blocking
            break  # Sortir de la boucle si tout se passe bien
        except socket.error as e:
            print(f"Erreur lors de la création du socket : {e}")
            time.sleep(5)  # Attendre avant de réessayer

    inputs = [s, pipe_in_wdtube]
    print(f"Dispatcher: Écoute sur {ADDR}:{PORT}")

    conn = None

    while True:
        try:
            readable, _, _ = select.select(inputs, [], [])
            for src in readable:
                if src == s:
                    # Nouvelle connexion
                    if conn:
                        inputs.remove(conn)
                        conn.close()
                    conn, addr = s.accept()
                    conn.setblocking(0)
                    inputs.append(conn)
                    print(f"Dispatcher: Connexion de {addr}")
                elif src == conn and is_worker_ready:
                    data = conn.recv(1024)
                    if data and data.decode() == "i_have_a_request_please":
                        print(f"Dispatcher: Requête reçue du client : {data.decode()}")
                        server.send_command(shared_mem, pipe_out_dwtube, 'i_have_a_request_please', True)
                        print("Dispatcher: J'ai envoyé la demande au worker.")
                        is_worker_ready = False
                elif src == conn and not is_worker_ready:
                    data = conn.recv(1024)
                    if data:
                        print(f"Dispatcher: Requête reçue du client : {data.decode()} mais worker indisponible")
                        inputs.remove(conn)
                        conn.close()
                        conn = None
                        print("Dispatcher: J'ai fermé la connexion avec le client.")
                elif src == pipe_in_wdtube:
                    msg = os.read(pipe_in_wdtube, 4).decode('utf-8')
                    if msg == "pong":
                        command = server.read_command(shared_mem)

                        if command.startswith('hey_buddy_i_am_ok'):
                            print(f"Dispatcher: Le worker est prêt.")
                            addr, port = command.split(' ')[1:]

                            conn.sendall((addr + ' ' + port).encode('utf-8'))
                            print(f"Dispatcher: J'ai envoyé les infos du worker au client.")
                            inputs.remove(conn)
                            conn.close()
                            conn = None
                            print("Dispatcher: J'ai fermé la connexion avec le client.")
                        elif command.startswith('hey_i_finished'):
                            print(f"Dispatcher: Je sais que le worker est de nouveau prêt.")
                            is_worker_ready = True
        except (socket.error, BlockingIOError, select.error, BrokenPipeError) as e:
            print(f"Dispatcher: Une erreur s'est produite : {e}")
            continue
    