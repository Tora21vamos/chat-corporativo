import socket
import threading
import json
import os
from datetime import datetime

# ─── Configurações ────────────────────────────────────────
HOST = "0.0.0.0"
PORTA_UDP = 9000
ARQUIVO_HISTORICO = "/app/dados/mensagens.json"

clientes = {}  # {endereco: nome}
lock = threading.Lock()

# ─── Histórico ────────────────────────────────────────────

def carregar_historico():
    if os.path.exists(ARQUIVO_HISTORICO):
        with open(ARQUIVO_HISTORICO, "r") as f:
            return json.load(f)
    return []

def salvar_mensagem(remetente, conteudo):
    os.makedirs(os.path.dirname(ARQUIVO_HISTORICO), exist_ok=True)
    historico = carregar_historico()
    mensagem = {
        "remetente": remetente,
        "conteudo": conteudo,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    historico.append(mensagem)
    with open(ARQUIVO_HISTORICO, "w") as f:
        json.dump(historico, f, indent=2, ensure_ascii=False)

# ─── Comunicação ──────────────────────────────────────────

def enviar_para_todos(mensagem, srv, excluir=None):
    with lock:
        for end in list(clientes.keys()):
            if end != excluir:
                try:
                    srv.sendto(mensagem.encode(), end)
                except:
                    pass

def processar(dados, endereco, srv):
    try:
        msg = dados.decode("utf-8").strip()

        if msg.startswith("ENTRAR:"):
            nome = msg.split(":", 1)[1]
            with lock:
                clientes[endereco] = nome
            aviso = f"[SERVIDOR] {nome} entrou no chat!"
            print(aviso)
            enviar_para_todos(aviso, srv)

        elif msg == "SAIR":
            with lock:
                nome = clientes.pop(endereco, "Desconhecido")
            aviso = f"[SERVIDOR] {nome} saiu do chat."
            print(aviso)
            enviar_para_todos(aviso, srv)

        else:
            with lock:
                nome = clientes.get(endereco, "Anónimo")
            msg_fmt = f"[{nome}]: {msg}"
            print(msg_fmt)
            salvar_mensagem(nome, msg)
            enviar_para_todos(msg_fmt, srv, excluir=endereco)

    except Exception as e:
        print(f"Erro: {e}")

# ─── Main ─────────────────────────────────────────────────

def main():
    srv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    srv.bind((HOST, PORTA_UDP))
    print(f"✅ Servidor UDP a escutar em {HOST}:{PORTA_UDP}\n")

    while True:
        try:
            dados, endereco = srv.recvfrom(4096)
            t = threading.Thread(target=processar, args=(dados, endereco, srv))
            t.daemon = True
            t.start()
        except KeyboardInterrupt:
            print("\n[SERVIDOR] Encerrado.")
            break

    srv.close()

if __name__ == "__main__":
    main()
