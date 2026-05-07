import socket
import threading
import json
import time

HOST = '0.0.0.0'
PORT = 5000

peers = {}  # ip:porta -> last_heartbeat
files = {}  # hash -> {nome, peers}
playlist = []

def handle_client(conn, addr):
    global peers, files, playlist
    try:
        # Definimos um timeout para a conexão não ficar aberta eternamente
        conn.settimeout(10) 
        data = conn.recv(4096).decode()
        if not data:
            return

        msg = json.loads(data)
        response = {}

        if msg["type"] == "REGISTER":
            peer_id = f"{msg['ip']}:{msg['port']}"
            peers[peer_id] = time.time()
            response = {"status": "OK"}

        elif msg["type"] == "HEARTBEAT":
            peer_id = f"{msg['ip']}:{msg['port']}"
            peers[peer_id] = time.time()
            response = {"status": "ALIVE"}

        elif msg["type"] == "PUBLISH":
            peer_id = f"{msg['ip']}:{msg['port']}"
            file_hash = msg["hash"]
            if file_hash not in files:
                files[file_hash] = {"nome": msg["nome"], "peers": []}
            if peer_id not in files[file_hash]["peers"]:
                files[file_hash]["peers"].append(peer_id)
            if file_hash not in playlist:
                playlist.append(file_hash)
            response = {"status": "PUBLISHED"}

        elif msg["type"] == "SEARCH":
            query = msg["query"].lower()
            results = [{ "nome": f["nome"], "hash": h, "peers": f["peers"] } 
                       for h, f in files.items() if query in f["nome"].lower()]
            response = {"results": results}

        elif msg["type"] == "PLAYLIST":
            pl = [{"nome": files[h]["nome"], "hash": h} for h in playlist]
            response = {"playlist": pl}

        conn.send(json.dumps(response).encode())
    except Exception as e:
        print(f"Erro no atendimento: {e}")
    finally:
        conn.close()

def cleanup_peers():
    while True:
        now = time.time()
        for peer in list(peers):
            if now - peers[peer] > 60:
                print(f"Removendo peer inativo: {peer}")
                del peers[peer]
        # Pausa longa para não consumir CPU desnecessariamente
        time.sleep(30) 

def start_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Resolve o erro "Address already in use"
    s.bind((HOST, PORT))
    s.listen(5)

    print(f"Servidor Tracker P2P rodando em {HOST}:{PORT}")
    threading.Thread(target=cleanup_peers, daemon=True).start()

    while True:
        try:
            conn, addr = s.accept()
            # Criamos uma thread para cada cliente para não travar o servidor
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
        except Exception as e:
            print(f"Erro ao aceitar conexão: {e}")
        time.sleep(0.1) # DESCANSO PARA A CPU

if __name__ == "__main__":
    start_server()