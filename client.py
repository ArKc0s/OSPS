import socket
import time

def main():
    host = '127.0.0.1'  # L'adresse du serveur
    port = 42424     # Assure-toi que c'est le même port que celui du serveur

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        s.connect((host, port))
    except ConnectionRefusedError:
        print("Impossible de se connecter au serveur.")
        return

    while True:
        s.sendall(b'get_time')  # Envoie la requête au serveur

        data = s.recv(1024)  # Attends la réponse
        print(f"Reçu : {data.decode('utf-8')}")

        time.sleep(2)  # Attend avant de faire la prochaine requête

if __name__ == "__main__":
    main()
