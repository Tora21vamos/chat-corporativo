import grpc
import json
import os
from concurrent import futures

import historico_pb2
import historico_pb2_grpc

ARQUIVO = "/app/dados/mensagens.json"
PORTA   = 50051

# ─── Serviço gRPC ─────────────────────────────────────────

class HistoricoServicer(historico_pb2_grpc.HistoricoServiceServicer):

    def _ler(self):
        if os.path.exists(ARQUIVO):
            with open(ARQUIVO, "r") as f:
                return json.load(f)
        return []

    def BuscarHistorico(self, request, context):
        msgs = self._ler()
        qtd  = request.quantidade if request.quantidade > 0 else 10
        return historico_pb2.RespostaHistorico(
            mensagens=[
                historico_pb2.Mensagem(
                    remetente=m["remetente"],
                    conteudo=m["conteudo"],
                    timestamp=m["timestamp"]
                ) for m in msgs[-qtd:]
            ]
        )

    def BuscarPorUtilizador(self, request, context):
        msgs   = self._ler()
        nome   = request.nome.lower()
        filtro = [m for m in msgs if m["remetente"].lower() == nome]
        return historico_pb2.RespostaHistorico(
            mensagens=[
                historico_pb2.Mensagem(
                    remetente=m["remetente"],
                    conteudo=m["conteudo"],
                    timestamp=m["timestamp"]
                ) for m in filtro
            ]
        )

# ─── Main ─────────────────────────────────────────────────

def main():
    srv = grpc.server(futures.ThreadPoolExecutor(max_workers=5))
    historico_pb2_grpc.add_HistoricoServiceServicer_to_server(HistoricoServicer(), srv)
    srv.add_insecure_port(f"[::]:{PORTA}")
    srv.start()
    print(f"✅ Servidor gRPC a escutar na porta {PORTA}")
    srv.wait_for_termination()

if __name__ == "__main__":
    main()
