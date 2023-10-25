"""
Authors: Léo WADIN & Aurélien HOUDART
Date: 24 octobre 2023
Version: 3.2

Description:
    Ce script réalise les étapes suivantes :
        1. Reçoit une requête initiale ("i_have_a_request_please") du dispatcher.
        2. Crée un socket pour la connexion du client.
        3. Envoie l'adresse et le port au dispatcher.
        4. Attends la connexion du client.
        5. Attends la requête du client.
        6. Envoie l'heure au client.
        7. Ferme la connexion avec le client.
        8. Ferme le socket d'écoute.
        9. Envoie un message au dispatcher pour signaler qu'il est de nouveau disponible.

    Note : Des timeouts sont ajoutés pour chaque opération réseau pour une meilleure robustesse.
"""

import server
import os
import time
import socket
from datetime import datetime

# Adresse et port du serveur
ADDR = '127.0.0.1'
PORT = 52525

def serveur_worker(shared_mem, pipe_in_dwtube, pipe_out_wdtube):
    while True:

        # Initialisation
        conn = None
        s_listen = None

        # Vérifie si le dispatcher a envoyé un message
        try:
            msg = os.read(pipe_in_dwtube, 4).decode('utf-8')
            if msg == "ping":
                command = server.read_command(shared_mem)

                # Vérifie si le dispatcher a envoyé une requête
                if command.startswith("i_have_a_request_please"):
                    print(f"Worker: J'ai reçu la commande : {command}")

                    # Crée un socket pour la connexion du client
                    try:
                        s_listen = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        s_listen.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                        s_listen.bind((ADDR, PORT))
                        s_listen.listen(1)
                        s_listen.settimeout(5.0)
                    except socket.error as e:
                        set_ready(shared_mem, pipe_out_wdtube, f"Erreur lors du bind/listen: {e}")
                    else:
                        # Envoie l'adresse et le port au dispatcher
                        server.send_command(shared_mem, pipe_out_wdtube, 'hey_buddy_i_am_ok ' + str(ADDR) + ' ' + str(PORT), False)

                        # Attends la connexion du client
                        try:
                            print(f"En attente de connexion du client sur {ADDR}:{PORT}")
                            conn, addr = s_listen.accept()
                            conn.settimeout(5.0)
                            print(f"Connexion établie avec {addr}")
                        except socket.timeout:
                            set_ready(shared_mem, pipe_out_wdtube, "Timeout lors de la connexion du client.")
                        else:
                            # Attends la requête du client
                            try:
                                data = conn.recv(1024)
                            except (BrokenPipeError, ConnectionResetError, socket.error):
                                set_ready(shared_mem, pipe_out_wdtube, "Erreur lors de la réception des données.")
                            else:
                                print(f"Worker: Reçu -> {data.decode('utf-8')}")
                                if data.decode('utf-8') == "get_time":
                                    # Envoie l'heure au client
                                    try:
                                        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                        conn.sendall(current_time.encode('utf-8'))
                                        print(f"Worker: J'ai envoyé l'heure : {current_time}")
                                    except (BrokenPipeError, ConnectionResetError, socket.timeout):
                                        set_ready(shared_mem, pipe_out_wdtube, "Erreur lors de l'envoi des données.")
                        finally:
                            # Ferme la connexion
                            if conn:
                                conn.close()
                    finally:
                        # Ferme le socket d'écoute
                        if s_listen:
                            s_listen.close()

                    set_ready(shared_mem, pipe_out_wdtube, "Je suis de nouveau disponible.")
                else:
                    os.write(pipe_out_wdtube, b"pong")
        except BlockingIOError:
            continue
        finally:
            time.sleep(2)

# Envoie un message au dispatcher pour signaler qu'il est de nouveau disponible.
def set_ready(shared_mem, pipe_out_wdtube, message):
    print(f"Worker: {message}")
    server.send_command(shared_mem, pipe_out_wdtube, 'hey_i_finished', False)
