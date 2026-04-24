# 💬 Chat Corporativo com Mensagens Persistentes
### Grupo 2 — Sistemas Distribuídos | Licenciatura em Informática — MOZAMBIQUE

---

## 📁 Estrutura do Projeto

```
chat-corporativo/
│
├── 📄 docker-compose.yml         ← Liga todos os containers
├── 📄 README.md                  ← Este ficheiro
│
├── 📂 proto/
│   └── historico.proto           ← Contrato gRPC
│
├── 📂 servidor/
│   ├── servidor.py               ← Servidor UDP (mensagens em tempo real)
│   ├── historico_servidor.py     ← Servidor gRPC (busca de histórico)
│   ├── requirements.txt          ← Dependências Python
│   └── Dockerfile                ← Container do servidor
│
├── 📂 cliente/
│   ├── cliente.py                ← Cliente do chat
│   ├── requirements.txt          ← Dependências Python
│   └── Dockerfile                ← Container do cliente
│
└── 📂 .vscode/
    ├── settings.json             ← Configurações VS Code
    └── launch.json               ← Atalhos para executar/debugar
```

---

## 🏗️ Arquitetura

```
┌────────────┐   UDP :9000    ┌──────────────────┐
│  Cliente 1 │ ─────────────► │                  │
├────────────┤                │    SERVIDOR       │
│  Cliente 2 │ ─────────────► │                  │
├────────────┤                │  • Recebe msgs   │
│  Cliente 3 │ ◄────────────► │  • Broadcast     │
└────────────┘   gRPC :50051  │  • Guarda JSON   │
                              └──────────────────┘
```

---

## 🚀 Como Executar

### Opção 1 — Com Docker (recomendado)
```bash
# Subir todos os containers
docker-compose up --build

# Em outro terminal — entrar no cliente 1
docker exec -it cliente_1 python cliente.py

# Em outro terminal — entrar no cliente 2
docker exec -it cliente_2 python cliente.py
```

### Opção 2 — Sem Docker (local)
```bash
# Terminal 1 — Servidor UDP
cd servidor
pip install -r requirements.txt
python servidor.py

# Terminal 2 — Servidor gRPC
cd servidor
python historico_servidor.py

# Terminal 3 — Cliente
cd cliente
pip install -r requirements.txt
SERVIDOR_HOST=localhost python cliente.py
```

---

## 💬 Comandos do Chat

| Comando | O que faz |
|---------|-----------|
| `Olá a todos!` | Envia mensagem para todos |
| `/historico` | Ver últimas 10 mensagens |
| `/historico 20` | Ver últimas 20 mensagens |
| `/user João` | Ver mensagens do utilizador João |
| `/sair` | Sair do chat |

---

## 📊 Comparação UDP vs gRPC

| Critério | UDP (Sockets) | gRPC |
|---------|--------------|------|
| **Velocidade** | ⚡ Muito rápido | 🔄 Mais lento |
| **Confiabilidade** | ❌ Pode perder pacotes | ✅ Garantido |
| **Uso no projeto** | Mensagens em tempo real | Busca de histórico |
| **Complexidade** | Simples | Médio |
| **Serialização** | Texto simples | Protocol Buffers |

---

## 👥 Grupo 2

- Nome 1
- Nome 2
- TELES JULIO

**Data de Entrega:** 7 de Maio de 2026
**Link GitHub:** (adicionar aqui)
