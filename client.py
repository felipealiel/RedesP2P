import socket
import threading
import json
import os
import hashlib
import time

# ================= CONFIGURAÇÃO DO COMPUTADOR =================
SERVER_IP = "192.168.1.3" 
SERVER_PORT = 5000
MY_PORT = 5002            # Porta diferente para não dar conflito
SHARED = "musicas_pc"     # Pasta onde os downloads vão cair no PC

# Descobre o IP do computador automaticamente
def get_my_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

MY_IP = get_my_ip()

# ================= LÓGICA DE REDE E ARQUIVOS =================

def hash_file(path):
    h = hashlib.md5()
    with open(path, 'rb') as f:
        while chunk := f.read(4096):
            h.update(chunk)
    return h.hexdigest()

def send_server(msg):
    try:
        s = socket.socket()
        s.settimeout(5)
        s.connect((SERVER_IP, SERVER_PORT))
        s.send(json.dumps(msg).encode())
        data = s.recv(4096).decode()
        s.close()
        return json.loads(data)
    except:
        return None

def serve_files():
    """Permite que outros baixem arquivos DESTE computador (P2P Upload)"""
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("0.0.0.0", MY_PORT))
    s.listen(5)
    while True:
        conn, addr = s.accept()
        try:
            data = conn.recv(1024).decode()
            if data.startswith("DOWNLOAD"):
                h = data.split()[1]
                for f in os.listdir(SHARED):
                    path = os.path.join(SHARED, f)
                    if os.path.isfile(path) and hash_file(path) == h:
                        with open(path, "rb") as file:
                            while chunk := file.read(4096):
                                conn.send(chunk)
                        break
        except: pass
        finally: conn.close()

# ================= COMANDOS DO USUÁRIO =================

def publish(file):
    path = os.path.join(SHARED, file)
    if not os.path.exists(path): return print(f"Erro: O arquivo deve estar na pasta {SHARED}")
    h = hash_file(path)
    res = send_server({"type": "PUBLISH", "ip": MY_IP, "port": MY_PORT, "nome": file, "hash": h})
    if res: print(f"Sucesso! Arquivo publicado com Hash: {h}")

def playlist():
    res = send_server({"type": "PLAYLIST"})
    if not res: return print("Erro ao conectar ao servidor.")
    print("\n--- PLAYLIST GLOBAL (FESTA) ---")
    if not res["playlist"]: print("A playlist está vazia.")
    for m in res["playlist"]: 
        print(f"♪ {m['nome']} | Hash: {m['hash']}")

def download(h, peer):
    """BAIXA DIRETO DO CELULAR (P2P Download)"""
    ip, port = peer.split(":")
    s = socket.socket()
    try:
        print(f"Conectando ao peer {peer} para download...")
        s.settimeout(10)
        s.connect((ip, int(port)))
        s.send(f"DOWNLOAD {h}".encode())
        
        filepath = os.path.join(SHARED, f"p2p_recebido_{h[:5]}.mp3")
        with open(filepath, "wb") as f:
            while data := s.recv(4096):
                f.write(data)
        print(f"Download P2P Concluído! Salvo em: {filepath}")
    except Exception as e:
        print(f"Erro no download: {e}")
    finally:
        s.close()

def interactive():
    print(f"\n--- CLIENTE PC LOGADO ---")
    print(f"IP: {MY_IP} | Porta: {MY_PORT}")
    print("Comandos: playlist, download [hash] [ip:porta], publish [nome], exit")
    
    while True:
        user_input = input("\n>> ").strip().split()
        if not user_input: continue
        
        cmd = user_input[0].lower()
        if cmd == "playlist": playlist()
        elif cmd == "publish": publish(user_input[1])
        elif cmd == "download": download(user_input[1], user_input[2])
        elif cmd == "exit": break

if __name__ == "__main__":
    os.makedirs(SHARED, exist_ok=True)
    # Registra no servidor
    send_server({"type": "REGISTER", "ip": MY_IP, "port": MY_PORT})
    # Inicia servidor de upload em background
    threading.Thread(target=serve_files, daemon=True).start()
    # Inicia menu
    interactive()