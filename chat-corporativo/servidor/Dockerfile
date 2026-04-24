FROM python:3.11-slim

WORKDIR /app

# Instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fonte
COPY . .

# Copiar ficheiro proto e gerar código gRPC
COPY ../proto/historico.proto .
RUN python -m grpc_tools.protoc \
    -I. \
    --python_out=. \
    --grpc_python_out=. \
    historico.proto

# Criar pasta de dados
RUN mkdir -p /app/dados

# Iniciar servidor UDP e gRPC em paralelo
CMD ["sh", "-c", "python servidor.py & python historico_servidor.py && wait"]
