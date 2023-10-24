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


def main():
    host = '127.0.0.1'  # L'adresse du serveur
    port = 42424        # Le port utilisé par le serveur
    timeout = 5         # Timeout en secondes

    # Crée un socket pour la connexion au dispatcher
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        
        # Définir un timeout pour la connexion et les opérations de socket
        s.settimeout(timeout)
        
        try:
            # Tentative de connexion au dispatcher
            s.connect((host, port))
            local_address, local_port = s.getsockname()
            print(f"Je suis {local_address}:{local_port}")
        except (ConnectionRefusedError, socket.timeout):
            print("Impossible de se connecter au serveur.")
            return

        # Définir l'option SO_LINGER à zéro pour une fermeture immédiate
        s.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, struct.pack('ii', 1, 0))

        # Envoie la requête initiale au dispatcher
        s.sendall(b'i_have_a_request_please')

        try:
            # Attends les infos du worker
            data = s.recv(1024)
        except socket.timeout:
            print("Timeout lors de la réception des données.")
            return

        print(f"Reçu : {data.decode('utf-8')}")
        addr, port = data.decode('utf-8').split(' ')
        port = int(port)

    # Crée un socket pour la connexion au worker
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        
        # Définir un timeout pour la connexion et les opérations de socket
        s.settimeout(timeout)

        # Tentative de connexion au worker
        s.connect((addr, port))
        print(f"Je suis connecté à {addr}:{port}")

        # Envoie la requête 'get_time' au worker
        s.sendall(b'get_time')

        try:
            # Attends la réponse du worker
            data = s.recv(1024)
        except socket.timeout:
            print("Timeout lors de la réception des données.")
            return

        print(f"Reçu : {data.decode('utf-8')}")

if __name__ == "__main__":
    main()
