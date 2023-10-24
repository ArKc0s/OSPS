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

                # Socket pour écouter des connexions entrantes
                s_listen = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                addr = '127.0.0.1'
                port = 52525
                
                s_listen.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s_listen.bind((addr, port))
                s_listen.listen(1)
                s_listen.settimeout(5.0)  # timeout de 5 secondes
                

                shared_mem.seek(0)
                shared_mem.write(('hey_buddy_i_am_ok ' + str(addr) + ' ' + str(port) + '\x00' * (100 - len('hey_buddy_i_am_ok ' + str(addr) + ' ' + str(port)))).encode('utf-8'))
                os.write(pipe_out_wdtube, b"pong")

                try:
                    print(f"En attente de connexion du client sur {addr}:{port}")
                    conn, addr = s_listen.accept()
                    conn.settimeout(5.0) 
                    print(f"Connexion établie avec {addr}")

                    # On attend la commande du client
                    data = conn.recv(1024)
                    print(f"Reçu : {data.decode('utf-8')}")

                    if data.decode('utf-8') == "get_time":
                        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        conn.sendall(current_time.encode('utf-8'))
                        print(f"Worker: J'ai envoyé l'heure : {current_time}")
                        conn.close()
                        s_listen.close()
                    
                except socket.timeout:
                    print("Timeout lors de la connexion du worker.")
                    return

                shared_mem.seek(0)
                shared_mem.write(('hey_i_finished' + '\x00' * (100 - len(current_time))).encode('utf-8'))
                print(f"Worker: Je suis de nouveau disponible.")

            os.write(pipe_out_wdtube, b"pong")
        else:
            print("Worker: En attente du jeton...")
        time.sleep(2)