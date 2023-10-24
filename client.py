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

    # On attend les infos du worker
    data = s.recv(1024)  # Attends la réponse
    print(f"Reçu : {data.decode('utf-8')}")
    addr, port = data.decode('utf-8').split(' ')
    port = int(port)

    s.close()

    # Socket pour la connexion au worker
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((addr, port))
    print(f"Je suis connecté à {addr}:{port}")

    #On envoie get_time au worker
    s.sendall(b'get_time')

    # On attend la réponse du worker
    data = s.recv(1024)  # Attends la réponse
    print(f"Reçu : {data.decode('utf-8')}")
    s.close()



    

if __name__ == "__main__":
    main()

