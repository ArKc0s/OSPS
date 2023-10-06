import os
import time
import mmap
import signal
import socket
import ast
from datetime import datetime

def serveur_worker(shared_mem, pipe_in_dwtube, pipe_out_wdtube):
    while True:
        try:
            msg = os.read(pipe_in_dwtube, 4).decode('utf-8')
        except BlockingIOError:
            continue
        if msg == "ping":
            shared_mem.seek(0)
            command = shared_mem.read(100).decode('utf-8').rstrip('\x00')
            if command.startswith("i_have_a_request_please"):
                print(f"Worker: J'ai reçu la commande : {command}")
                # récuperer l'ip et le port du client dans command
                time.sleep(2)
                full_address = command.split(' ')[1] + ' ' + command.split(' ')[2]
                adresse_tuple = ast.literal_eval(full_address)
                host, port = adresse_tuple
                # se connecter au client
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.connect((host, port))
                # envoyer un ping au client pour lui dire que je suis pret a traiter sa requete
                s.sendall(b"hello_i_am_ready")

                # attendre la reponse du client
                data = s.recv(1024)
                print(f"Worker: Reçu de {adresse_tuple} : {data.decode('utf-8')}")

                if data.decode('utf-8') == "get_time":
                    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    s.sendall(current_time.encode('utf-8'))
                    print(f"Worker: J'ai envoyé l'heure : {current_time}")
                s.close()

                shared_mem.seek(0)
                shared_mem.write(('hey_i_finished' + '\x00' * (100 - len(current_time))).encode('utf-8'))
                print(f"Worker: Je suis de nouveau disponible.")
            os.write(pipe_out_wdtube, b"pong")
        else:
            print("Worker: En attente du jeton...")
        time.sleep(2)