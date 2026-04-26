import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox
import grpc
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import historico_pb2
import historico_pb2_grpc

SERVIDOR_HOST = os.getenv("SERVIDOR_HOST", "localhost")
PORTA_UDP     = 9000
PORTA_GRPC    = 50051

class ChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Chat Corporativo")
        self.root.geometry("700x550")
        self.root.configure(bg="#1e1e2e")
        self.sock = None
        self.nome = None
        self.servidor = (SERVIDOR_HOST, PORTA_UDP)
        self.build_login()

    def build_login(self):
        self.login_frame = tk.Frame(self.root, bg="#1e1e2e")
        self.login_frame.place(relx=0.5, rely=0.5, anchor="center")
        tk.Label(self.login_frame, text="Chat Corporativo", font=("Arial", 22, "bold"), bg="#1e1e2e", fg="#cdd6f4").pack(pady=(0,30))
        tk.Label(self.login_frame, text="O teu nome:", font=("Arial", 12), bg="#1e1e2e", fg="#a6adc8").pack(anchor="w")
        self.entry_nome = tk.Entry(self.login_frame, font=("Arial", 13), width=28, bg="#313244", fg="#cdd6f4", insertbackground="white", relief="flat", bd=8)
        self.entry_nome.pack(pady=(4,16))
        self.entry_nome.bind("<Return>", lambda e: self.entrar())
        self.entry_nome.focus()
        tk.Button(self.login_frame, text="Entrar", font=("Arial", 12, "bold"), bg="#89b4fa", fg="#1e1e2e", relief="flat", padx=20, pady=8, cursor="hand2", command=self.entrar).pack()

    def entrar(self):
        nome = self.entry_nome.get().strip() or "Anonimo"
        self.nome = nome
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.sendto(f"ENTRAR:{self.nome}".encode(), self.servidor)
        except Exception as e:
            messagebox.showerror("Erro", f"Nao foi possivel ligar:\n{e}")
            return
        self.login_frame.destroy()
        self.build_chat()
        threading.Thread(target=self.receber, daemon=True).start()

    def build_chat(self):
        topo = tk.Frame(self.root, bg="#181825", pady=10)
        topo.pack(fill="x")
        tk.Label(topo, text="Chat Corporativo", font=("Arial", 14, "bold"), bg="#181825", fg="#cdd6f4").pack(side="left", padx=16)
        tk.Label(topo, text=f"Utilizador: {self.nome}", font=("Arial", 11), bg="#181825", fg="#a6e3a1").pack(side="right", padx=16)
        self.area_msgs = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, state="disabled", font=("Consolas", 11), bg="#1e1e2e", fg="#cdd6f4", relief="flat", padx=10, pady=10)
        self.area_msgs.pack(fill="both", expand=True, padx=10, pady=(8,0))
        self.area_msgs.tag_config("servidor", foreground="#a6e3a1")
        self.area_msgs.tag_config("eu", foreground="#89b4fa", font=("Consolas", 11, "bold"))
        self.area_msgs.tag_config("outro", foreground="#fab387")
        self.area_msgs.tag_config("sistema", foreground="#f38ba8")
        self.area_msgs.tag_config("historico", foreground="#a6adc8")
        btn_frame = tk.Frame(self.root, bg="#1e1e2e")
        btn_frame.pack(fill="x", padx=10, pady=(6,0))
        tk.Button(btn_frame, text="Historico", font=("Arial", 9), bg="#313244", fg="#cdd6f4", relief="flat", padx=10, pady=4, cursor="hand2", command=self.ver_historico).pack(side="left", padx=(0,6))
        tk.Button(btn_frame, text="Sair", font=("Arial", 9), bg="#f38ba8", fg="#1e1e2e", relief="flat", padx=10, pady=4, cursor="hand2", command=self.sair).pack(side="right")
        rodape = tk.Frame(self.root, bg="#1e1e2e")
        rodape.pack(fill="x", padx=10, pady=10)
        self.entry_msg = tk.Entry(rodape, font=("Arial", 12), bg="#313244", fg="#cdd6f4", insertbackground="white", relief="flat", bd=8)
        self.entry_msg.pack(side="left", fill="x", expand=True, padx=(0,8))
        self.entry_msg.bind("<Return>", lambda e: self.enviar())
        self.entry_msg.focus()
        tk.Button(rodape, text="Enviar", font=("Arial", 11, "bold"), bg="#89b4fa", fg="#1e1e2e", relief="flat", padx=16, pady=6, cursor="hand2", command=self.enviar).pack(side="right")
        self.adicionar_msg(f"Ligado como '{self.nome}'!", "servidor")

    def adicionar_msg(self, texto, tag="outro"):
        self.area_msgs.configure(state="normal")
        self.area_msgs.insert("end", texto + "\n", tag)
        self.area_msgs.configure(state="disabled")
        self.area_msgs.see("end")

    def receber(self):
        while True:
            try:
                dados, _ = self.sock.recvfrom(4096)
                msg = dados.decode("utf-8")
                tag = "servidor" if msg.startswith("[SERVIDOR]") else "outro"
                self.root.after(0, self.adicionar_msg, msg, tag)
            except:
                break

    def enviar(self):
        msg = self.entry_msg.get().strip()
        if not msg:
            return
        self.entry_msg.delete(0, "end")
        self.adicionar_msg(f"Tu: {msg}", "eu")
        try:
            self.sock.sendto(msg.encode(), self.servidor)
        except Exception as e:
            self.adicionar_msg(f"Erro: {e}", "sistema")

    def ver_historico(self):
        try:
            canal = grpc.insecure_channel(f"{SERVIDOR_HOST}:{PORTA_GRPC}")
            stub = historico_pb2_grpc.HistoricoServiceStub(canal)
            pedido = historico_pb2.PedidoHistorico(quantidade=10)
            resposta = stub.BuscarHistorico(pedido)
            self.adicionar_msg("--- HISTORICO ---", "historico")
            for m in resposta.mensagens:
                self.adicionar_msg(f"[{m.timestamp}] {m.remetente}: {m.conteudo}", "historico")
            self.adicionar_msg("-----------------", "historico")
        except Exception as e:
            self.adicionar_msg(f"Erro gRPC: {e}", "sistema")

    def sair(self):
        if self.sock:
            try:
                self.sock.sendto("SAIR".encode(), self.servidor)
                self.sock.close()
            except:
                pass
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatApp(root)
    root.protocol("WM_DELETE_WINDOW", app.sair)
    root.mainloop()
