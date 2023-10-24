import socket
import struct
import time

def main():
    host = '127.0.0.1'  # L'adresse du serveur
    port = 42424       # Le port utilisé par le serveur

    # Socket pour la connexion au dispatcher
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        s.connect((host, port))
        local_address, local_port = s.getsockname()
        print(f"Je suis {local_address}:{local_port}")
    except ConnectionRefusedError:
        print("Impossible de se connecter au serveur.")
        return

    # Définir l'option SO_LINGER à zéro pour une fermeture immédiate
    s.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, struct.pack('ii', 1, 0))

    s.sendall(b'i_have_a_request_please')
    s.close() 

    # Socket pour écouter des connexions entrantes
    s_listen = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    s_listen.bind((local_address, local_port))  # utiliser les mêmes adresse IP et port
    s_listen.listen(1)

    s_listen.settimeout(5.0)  # timeout de 5 secondes

    try:
        print(f"En attente de connexion du worker sur {local_address}:{local_port}")
        conn, addr = s_listen.accept()
        conn.settimeout(5.0) 
        print(f"Connexion établie avec {addr}")

        try:
            data = conn.recv(1024)  # Attends la réponse
            print(f"Reçu : {data.decode('utf-8')}")

            #envoi de la requete
            conn.sendall(b"get_time")

            data = conn.recv(1024)  # Attends la réponse
            print(f"Reçu : {data.decode('utf-8')}")
        except socket.timeout:
            print("Timeout lors de la réception des données.")
            
    except socket.timeout:
        print("Timeout lors de la connexion du worker.")
        return


    conn.close()
    s_listen.close()

if __name__ == "__main__":
    main()
