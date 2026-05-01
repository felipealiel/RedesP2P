import socket
import threading
import json
import os
import hashlib
import time

SERVER_IP = "server"
SERVER_PORT = 5000

MY_PORT = int(os.environ.get("PORT", 5001))
MY_IP = socket.gethostname()

SHARED = "shared"


def hash_file(path):
    h = hashlib.md5()
    with open(path, 'rb') as f:
        while chunk := f.read(4096):
            h.update(chunk)
    return h.hexdigest()


def send_server(msg):
    s = socket.socket()
    s.connect((SERVER_IP, SERVER_PORT))
    s.send(json.dumps(msg).encode())
    data = s.recv(4096).decode()
    s.close()
    return json.loads(data)


def register():
    send_server({
        "type": "REGISTER",
        "ip": MY_IP,
        "port": MY_PORT
    })


def heartbeat():
    while True:
        try:
            send_server({
                "type": "HEARTBEAT",
                "ip": MY_IP,
                "port": MY_PORT
            })
        except:
            print("Erro ao enviar heartbeat.")
        time.sleep(30)


def publish(file):
    path = os.path.join(SHARED, file)

    if not os.path.exists(path):
        print("Arquivo não existe.")
        return

    h = hash_file(path)

    send_server({
        "type": "PUBLISH",
        "ip": MY_IP,
        "port": MY_PORT,
        "nome": file,
        "hash": h
    })

    print(f"Publicado com hash: {h}")


def search(q):
    res = send_server({
        "type": "SEARCH",
        "query": q
    })

    if not res["results"]:
        print("Nenhum resultado encontrado.")
        return

    for r in res["results"]:
        print(r)


def download(h, peer):
    ip, port = peer.split(":")
    port = int(port)

    s = socket.socket()

    try:
        s.connect((ip, port))
        s.send(f"DOWNLOAD {h}".encode())

        filename = os.path.join(SHARED, f"{h}.mp3")
        total = 0

        with open(filename, "wb") as f:
            while True:
                data = s.recv(1024)
                if not data:
                    break
                total += len(data)
                f.write(data)

        if total == 0:
            os.remove(filename)
            print("Falha no download: nenhum dado recebido.")
        else:
            print(f"Download concluído ({total} bytes).")

    except Exception as e:
        print("Erro no download:", e)

    finally:
        s.close()


def serve():
    s = socket.socket()
    s.bind(("0.0.0.0", MY_PORT))
    s.listen()

    while True:
        conn, _ = s.accept()

        try:
            data = conn.recv(1024).decode()

            if data.startswith("DOWNLOAD"):
                _, h = data.split()

                found = False

                for f in os.listdir(SHARED):
                    path = os.path.join(SHARED, f)

                    if os.path.isfile(path) and hash_file(path) == h:
                        found = True

                        with open(path, "rb") as file:
                            while True:
                                chunk = file.read(1024)
                                if not chunk:
                                    break
                                conn.send(chunk)
                        break

                if not found:
                    print(f"Arquivo com hash {h} não encontrado.")

        except Exception as e:
            print("Erro ao servir download:", e)

        finally:
            conn.close()


def playlist():
    res = send_server({"type": "PLAYLIST"})

    print("\n=== Playlist Global ===")
    for m in res["playlist"]:
        print(m)


def list_local():
    files = os.listdir(SHARED)

    if not files:
        print("Nenhum arquivo local.")
        return

    print("\n=== Arquivos Locais ===")
    for f in files:
        print(f)


def main():
    os.makedirs(SHARED, exist_ok=True)

    register()

    threading.Thread(target=heartbeat, daemon=True).start()
    threading.Thread(target=serve, daemon=True).start()

    print(f"Cliente rodando na porta {MY_PORT}...")

    while True:
        time.sleep(1)


def interactive():
    while True:
        try:
            cmd = input(">> ").strip()

            if cmd.startswith("publish"):
                _, f = cmd.split(maxsplit=1)
                publish(f)

            elif cmd.startswith("search"):
                _, q = cmd.split(maxsplit=1)
                search(q)

            elif cmd.startswith("download"):
                _, h, p = cmd.split()
                download(h, p)

            elif cmd == "playlist":
                playlist()

            elif cmd == "list_local":
                list_local()

            elif cmd == "exit":
                break

            else:
                print("Comando inválido.")

        except Exception as e:
            print("Erro:", e)


if __name__ == "__main__":
    main()