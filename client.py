import socket
import struct
import time

def main():
    host = '127.0.0.1'  # L'adresse du serveur
    port = 42424        # Assure-toi que c'est le même port que celui du serveur

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

    print(f"En attente de connexion du worker sur {local_address}:{local_port}")
    conn, addr = s_listen.accept()
    print(f"Connexion établie avec {addr}")

    data = conn.recv(1024)  # Attends la réponse
    print(f"Reçu : {data.decode('utf-8')}")

    #envoi de la requete
    conn.sendall(b"get_time")

    data = conn.recv(1024)  # Attends la réponse
    print(f"Reçu : {data.decode('utf-8')}")

    conn.close()
    s_listen.close()

if __name__ == "__main__":
    main()

