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

    while True:
        try:
            data = conn.recv(4096).decode()
            if not data:
                break

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
                    files[file_hash] = {
                        "nome": msg["nome"],
                        "peers": []
                    }

                if peer_id not in files[file_hash]["peers"]:
                    files[file_hash]["peers"].append(peer_id)

                if file_hash not in playlist:
                    playlist.append(file_hash)

                response = {"status": "PUBLISHED"}

            elif msg["type"] == "SEARCH":
                query = msg["query"].lower()
                results = []

                for h, f in files.items():
                    if query in f["nome"].lower():
                        results.append({
                            "nome": f["nome"],
                            "hash": h,
                            "peers": f["peers"]
                        })

                response = {"results": results}

            elif msg["type"] == "PLAYLIST":
                pl = []
                for h in playlist:
                    pl.append({
                        "nome": files[h]["nome"],
                        "hash": h
                    })

                response = {"playlist": pl}

            conn.send(json.dumps(response).encode())

        except:
            break

    conn.close()


def cleanup_peers():
    while True:
        now = time.time()
        for peer in list(peers):
            if now - peers[peer] > 60:
                print(f"Removendo peer inativo: {peer}")
                del peers[peer]
        time.sleep(30)


def start_server():
    s = socket.socket()
    s.bind((HOST, PORT))
    s.listen()

    print(f"Servidor rodando em {HOST}:{PORT}")

    threading.Thread(target=cleanup_peers, daemon=True).start()

    while True:
        conn, addr = s.accept()
        threading.Thread(target=handle_client, args=(conn, addr)).start()


if __name__ == "__main__":
    start_server()