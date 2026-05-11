import socket
import threading
import os
import json
import hashlib
import tkinter as tk
from tkinter import messagebox, filedialog, ttk

# --- CONFIGURAÇÕES ---
SERVER_IP = "192.168.1.3" 
SERVER_PORT = 5000
MY_IP = socket.gethostbyname(socket.gethostname())
MY_PORT = 5003 # Usando uma porta diferente para a GUI
SHARED_DIR = "musicas_pc"

if not os.path.exists(SHARED_DIR):
    os.makedirs(SHARED_DIR)

def hash_file(path):
    h = hashlib.md5()
    with open(path, 'rb') as f:
        while chunk := f.read(4096):
            h.update(chunk)
    return h.hexdigest()

class P2PClientGUI:
    def __init__(self, root):
        self.root = root
        self.root.title(f"P2P Music Share - {MY_IP}")
        self.root.geometry("700x500")
        
        self.label = tk.Label(root, text="🎵 Rede P2P Festa Colaborativa", font=("Arial", 16, "bold"))
        self.label.pack(pady=10)

        # Tabela de Playlist
        self.tree = ttk.Treeview(root, columns=("Arquivo", "Hash"), show="headings")
        self.tree.heading("Arquivo", text="Nome da Música")
        self.tree.heading("Hash", text="Hash MD5")
        self.tree.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

        self.btn_frame = tk.Frame(root)
        self.btn_frame.pack(pady=20)

        ttk.Button(self.btn_frame, text="🔄 Atualizar Lista", command=self.get_playlist).grid(row=0, column=0, padx=10)
        ttk.Button(self.btn_frame, text="📤 Publicar Música", command=self.publish_file).grid(row=0, column=1, padx=10)
        ttk.Button(self.btn_frame, text="📥 Baixar Selecionada", command=self.start_download).grid(row=0, column=2, padx=10)

        # Iniciar servidor de arquivos (para os outros baixarem de você)
        threading.Thread(target=self.start_file_server, daemon=True).start()
        self.get_playlist()

    def send_to_server(self, msg):
        """Auxiliar para enviar JSON ao server.py"""
        try:
            s = socket.socket()
            s.connect((SERVER_IP, SERVER_PORT))
            s.send(json.dumps(msg).encode())
            data = s.recv(8192).decode()
            s.close()
            return json.loads(data)
        except Exception as e:
            print(f"Erro na comunicação: {e}")
            return None

    def get_playlist(self):
        res = self.send_to_server({"type": "PLAYLIST"})
        if res:
            for i in self.tree.get_children(): self.tree.delete(i)
            for item in res.get("playlist", []):
                self.tree.insert("", tk.END, values=(item['nome'], item['hash']))
        else:
            messagebox.showerror("Erro", "Servidor offline!")

    def publish_file(self):
        path = filedialog.askopenfilename(initialdir=SHARED_DIR)
        if path:
            nome = os.path.basename(path)
            h = hash_file(path)
            res = self.send_to_server({
                "type": "PUBLISH", 
                "ip": MY_IP, 
                "port": MY_PORT, 
                "nome": nome, 
                "hash": h
            })
            if res:
                messagebox.showinfo("Sucesso", "Música publicada!")
                self.get_playlist()

    def start_download(self):
        selected = self.tree.selection()
        if not selected: return
        
        item = self.tree.item(selected)['values']
        # Aqui o seu server.py precisaria retornar o IP do dono na playlist.
        # Como o seu server.py atual não envia o IP na PLAYLIST, 
        # vamos pedir o IP manualmente para testar.
        peer_ip = tk.simpledialog.askstring("IP do Dono", "Digite o IP:Porta de quem tem a música:")
        if peer_ip:
            threading.Thread(target=self.download_logic, args=(item[1], peer_ip, item[0])).start()

    def download_logic(self, file_hash, peer_info, nome):
        try:
            ip, port = peer_info.split(":")
            s = socket.socket()
            s.connect((ip, int(port)))
            s.send(f"DOWNLOAD {file_hash}".encode())
            
            with open(os.path.join(SHARED_DIR, f"baixado_{nome}"), "wb") as f:
                while data := s.recv(4096): f.write(data)
            messagebox.showinfo("Fim", "Download Concluído!")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def start_file_server(self):
        """Upload P2P (Mesma lógica do seu client.py)"""
        s = socket.socket()
        s.bind(("0.0.0.0", MY_PORT))
        s.listen(5)
        while True:
            conn, addr = s.accept()
            try:
                data = conn.recv(1024).decode()
                if data.startswith("DOWNLOAD"):
                    h_req = data.split()[1]
                    for f in os.listdir(SHARED_DIR):
                        path = os.path.join(SHARED_DIR, f)
                        if os.path.isfile(path) and hash_file(path) == h_req:
                            with open(path, "rb") as file:
                                while chunk := file.read(4096): conn.send(chunk)
                            break
            except: pass
            finally: conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = P2PClientGUI(root)
    root.mainloop()