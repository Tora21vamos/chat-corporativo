import socket
import threading
import grpc
import os

import historico_pb2
import historico_pb2_grpc

# ─── Configurações ────────────────────────────────────────
SERVIDOR_HOST = os.getenv("SERVIDOR_HOST", "servidor")
PORTA_UDP     = 9000
PORTA_GRPC    = 50051

# ─── Receber mensagens (thread) ───────────────────────────

def receber(sock):
    while True:
        try:
            dados, _ = sock.recvfrom(4096)
            print(f"\n{dados.decode('utf-8')}")
            print("Tu: ", end="", flush=True)
        except:
            break

# ─── Histórico via gRPC ───────────────────────────────────

def ver_historico(quantidade=10):
    try:
        canal   = grpc.insecure_channel(f"{SERVIDOR_HOST}:{PORTA_GRPC}")
        stub    = historico_pb2_grpc.HistoricoServiceStub(canal)
        pedido  = historico_pb2.PedidoHistorico(quantidade=quantidade)
        resposta = stub.BuscarHistorico(pedido)

        print("\n" + "="*45)
        print(f"  📜 HISTÓRICO — últimas {quantidade} mensagens")
        print("="*45)
        if not resposta.mensagens:
            print("  (Nenhuma mensagem encontrada)")
        for m in resposta.mensagens:
            print(f"  [{m.timestamp}] {m.remetente}: {m.conteudo}")
        print("="*45 + "\n")
    except Exception as e:
        print(f"Erro no gRPC: {e}")

def ver_utilizador(nome):
    try:
        canal    = grpc.insecure_channel(f"{SERVIDOR_HOST}:{PORTA_GRPC}")
        stub     = historico_pb2_grpc.HistoricoServiceStub(canal)
        pedido   = historico_pb2.PedidoUtilizador(nome=nome)
        resposta = stub.BuscarPorUtilizador(pedido)

        print(f"\n  📜 Mensagens de '{nome}':")
        for m in resposta.mensagens:
            print(f"  [{m.timestamp}] {m.conteudo}")
        print()
    except Exception as e:
        print(f"Erro no gRPC: {e}")

# ─── Main ─────────────────────────────────────────────────

def main():
    nome = input("👤 O teu nome: ").strip() or "Anónimo"

    sock     = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    servidor = (SERVIDOR_HOST, PORTA_UDP)

    # Registar no servidor
    sock.sendto(f"ENTRAR:{nome}".encode(), servidor)

    # Thread de receção
    t = threading.Thread(target=receber, args=(sock,))
    t.daemon = True
    t.start()

    print(f"\n✅ Ligado como '{nome}'!")
    print("  /historico [N]  → ver histórico (padrão: 10 msgs)")
    print("  /user <nome>    → mensagens de um utilizador")
    print("  /sair           → sair do chat\n")

    while True:
        try:
            msg = input("Tu: ").strip()
            if not msg:
                continue

            if msg == "/sair":
                sock.sendto("SAIR".encode(), servidor)
                print("Até logo! 👋")
                break

            elif msg.startswith("/historico"):
                partes = msg.split()
                qtd = int(partes[1]) if len(partes) > 1 else 10
                ver_historico(qtd)

            elif msg.startswith("/user "):
                ver_utilizador(msg.split(" ", 1)[1])

            else:
                sock.sendto(msg.encode(), servidor)

        except KeyboardInterrupt:
            sock.sendto("SAIR".encode(), servidor)
            print("\nSaindo...")
            break

    sock.close()

if __name__ == "__main__":
    main()
