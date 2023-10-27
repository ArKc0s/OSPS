"""
Authors: Léo WADIN & Aurélien HOUDART
Date: 24 octobre 2023
Version: 3.1

Description:
    Ce script réalise les étapes suivantes :
        1. Établit une connexion TCP avec un dispatcher sur l'adresse et le port donnés.
        2. Envoie une requête initiale ("i_have_a_request_please") au dispatcher.
        3. Reçoit l'adresse et le port d'un worker du dispatcher.
        4. Ferme la connexion avec le dispatcher.
        5. Établit une nouvelle connexion TCP avec le worker.
        6. Envoie une requête ("get_time") au worker.
        7. Reçoit la réponse du worker, qui est censée être l'heure actuelle.
        8. Ferme la connexion avec le worker.
    
    Note : Des timeouts sont ajoutés pour chaque opération réseau pour une meilleure robustesse.
"""

import socket
import struct
import time

# Nombre de tentatives de connexion avant abandon et timeout pour chaque opération réseau
MAX_RETRIES = 3
TIMEOUT = 5
# Adresse et port du serveur dispatcher
ADDR = '127.0.0.1'
PORT = 42424

def main():
    
    # Nombre de tentatives de connexion
    retries = 0

    while retries < MAX_RETRIES:
        try:
            # Crée un socket pour la connexion avec le dispatcher
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(TIMEOUT)
                s.connect((ADDR, PORT))
                local_address, local_port = s.getsockname()
                print(f"Je suis {local_address}:{local_port}")
                
                # Evite le problème de "Address already in use" lors de la fermeture du socket
                s.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, struct.pack('ii', 1, 0))
                
                # Envoie une requête initiale au dispatcher
                try:
                    s.sendall(b'i_have_a_request_please')
                    data = s.recv(1024)
                except (socket.timeout, socket.error):
                    print("Erreur lors de l'envoi ou de la réception des données avec le dispatcher.")
                    retries += 1
                    continue

                # Reçoit l'adresse et le port d'un worker
                print(f"Reçu : {data.decode('utf-8')}")
                addr, port = data.decode('utf-8').split(' ')
                port = int(port)

            # Crée un socket pour la connexion avec le worker   
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(TIMEOUT)
                s.connect((addr, port))
                print(f"Je suis connecté à {addr}:{port}")

                # Envoie une requête au worker
                try:
                    s.sendall(b'get_time')
                    data = s.recv(1024)
                except (socket.timeout, socket.error):
                    print("Erreur lors de l'envoi ou de la réception des données avec le worker.")
                    return
                
                # Reçoit la réponse du worker
                print(f"Reçu : {data.decode('utf-8')}")
                s.close()
            break

        except (ConnectionRefusedError, socket.timeout, socket.error, OSError) as e:
            print(f"Impossible de se connecter au serveur. Erreur : {e}")
            retries += 1

        time.sleep(3)

    if retries == MAX_RETRIES:
        print("Trop de tentatives infructueuses, abandon.")

if __name__ == "__main__":
    main()