<<<<<<< HEAD
# ################################################################################
# RELATÓRIO TÉCNICO: SISTEMA P2P HÍBRIDO - FESTA COLABORATIVA
# Disciplina: Sistemas Distribuídos
# ################################################################################

# 1. INTRODUÇÃO
# Este documento descreve o desenvolvimento de um sistema de compartilhamento de 
# músicas utilizando arquitetura Peer-to-Peer (P2P) híbrida[cite: 1]. 
# O sistema simula uma "Festa Colaborativa" onde os participantes (peers) 
# contribuem com arquivos para uma playlist global, permitindo que qualquer 
# convidado baixe músicas diretamente de outros membros da rede[cite: 1].

# 2. OBJETIVO DO PROJETO
# * Implementar um Tracker Central para gerenciar metadados e a playlist global[cite: 1].
# * Garantir a transferência direta entre peers sem sobrecarregar o servidor[cite: 1].
# * Utilizar Docker para isolamento de nós e simulação de rede distribuída[cite: 1].
# * Otimização: Manter o uso de CPU estável e abaixo de 5% em ambiente de containers.

# 3. TECNOLOGIAS UTILIZADAS
# * Python 3 (Sockets TCP e Multithreading)[cite: 1].
# * JSON para protocolo de mensagens entre os componentes[cite: 1].
# * Docker & Docker Compose para orquestração da infraestrutura[cite: 1].
# * Hash MD5: Para identificação única e garantia da integridade dos arquivos.

# 4. ARQUITETURA DO SISTEMA

# 4.1 TRACKER CENTRAL (O ORGANIZADOR)
# * Mantém a Playlist Global em tempo real com base nos arquivos publicados[cite: 1].
# * Gerencia o estado dos peers via Heartbeat, com limpeza automática após 60s[cite: 1].
# * Otimização Técnica: Uso de time.sleep e flag SO_REUSEADDR para alta estabilidade.

# 4.2 PEERS (OS CONVIDADOS)
# * Publicação: Contribuem com arquivos locais registrados por Hash MD5 no Tracker.
# * Busca & Download: Localizam músicas e realizam a transferência binária direta 
#   via Socket TCP, caracterizando a comunicação puramente P2P[cite: 1].

# 5. ESTRUTURA DE PASTAS
# RedesP2P/
# ├── client.py
# ├── server.py
# ├── Dockerfile
# ├── docker-compose.yml
# ├── shared_peer1/ (Diretório de músicas do Convidado 1)
# └── shared_peer2/ (Diretório de músicas do Convidado 2)

# 6. IMPLEMENTAÇÃO DO SERVIDOR (server.py)
# O servidor foi otimizado para evitar o alto consumo de CPU observado em 
# versões iniciais. Abaixo, a estrutura principal de controle:
# 
# (Código resumido para documentação)
# - Socket configurado com SO_REUSEADDR.
# - Loop principal com time.sleep(0.1) para descanso do processador.
# - Thread de Cleanup rodando a cada 30 segundos para remover peers inativos.

# 7. COMANDOS PARA EXECUÇÃO

# 7.1 BUILD E INICIALIZAÇÃO
# No terminal da raiz do projeto, execute:
# $ docker-compose up -d --build

# 7.2 ACESSO AOS TERMINAIS DOS PEERS
# Peer 1: $ docker exec -it redesp2p-peer1-1 python client.py
# Peer 2: $ docker exec -it redesp2p-peer2-1 python client.py

# 8. TESTES E VALIDAÇÃO
# * Teste 1 (Estabilidade): Uso de CPU mantido abaixo de 5% no Docker Desktop.
# * Teste 2 (Festa): Peer 1 publicou MP3 que apareceu na playlist global do Peer 2.
# * Teste 3 (P2P): Download realizado com sucesso diretamente entre os containers.

# 9. CONCLUSÃO
# O sistema atendeu aos requisitos de um sistema P2P híbrido funcional.
# A utilização de Docker permitiu simular uma rede distribuída real, enquanto 
# as otimizações no código garantiram eficiência para o hardware, suportando 
# múltiplos usuários simultâneos no fluxo da "Festa Colaborativa".

# ################################################################################
=======
# Relatório / Tutorial de Implementação

## Sistema P2P Híbrido de Compartilhamento de Músicas com Docker

---

# 1. Introdução

Este documento descreve o desenvolvimento completo de um sistema de compartilhamento de músicas utilizando arquitetura **Peer-to-Peer (P2P) híbrida**, no qual um servidor central atua como **tracker** para registrar peers e manter metadados dos arquivos compartilhados, enquanto a transferência dos arquivos ocorre diretamente entre os clientes.

Além de servir como relatório técnico do projeto, este documento também funciona como tutorial para que qualquer integrante do grupo possa executar o sistema em sua máquina.

---

# 2. Objetivo do Projeto

Implementar um sistema distribuído de compartilhamento de músicas onde:

* Um **tracker central** mantém registro dos peers ativos e dos arquivos disponíveis.
* Os **peers** compartilham músicas diretamente entre si.
* O servidor **não armazena os arquivos**, apenas metadados.
* O sistema utiliza **Docker** para simulação de múltiplos nós em uma única máquina.

---

# 3. Tecnologias Utilizadas

* Python 3
* Sockets TCP
* JSON
* Docker
* Docker Compose

---

# 4. Arquitetura P2P Híbrida

A arquitetura do sistema é composta por:

## 4.1 Tracker Central (Servidor)

Responsável por:

* Registrar peers ativos
* Receber heartbeat periódico
* Armazenar metadados dos arquivos compartilhados
* Responder buscas por arquivos
* Manter playlist global de músicas

---

## 4.2 Peers (Clientes)

Responsáveis por:

* Compartilhar arquivos locais
* Registrar músicas no tracker
* Buscar músicas disponíveis
* Realizar download diretamente de outros peers

---

# 5. Estrutura de Pastas do Projeto

```text
P2P_musicas/
│
├── client.py
├── server.py
├── Dockerfile
├── docker-compose.yml
│
├── shared_peer1/
│   └── musica1.mp3
│
└── shared_peer2/
```

---

# 6. Implementação do Servidor (Tracker)

Arquivo: `server.py`

```python
import socket
import threading
import json
import time

HOST = "0.0.0.0"
PORT = 5000

peers = {}
files = {}

def cleanup():
    while True:
        now = time.time()

        for peer in list(peers):
            if now - peers[peer] > 60:
                del peers[peer]

                for h in list(files):
                    if peer in files[h]["peers"]:
                        files[h]["peers"].remove(peer)

                    if not files[h]["peers"]:
                        del files[h]

        time.sleep(10)

def handle(conn):
    data = json.loads(conn.recv(4096).decode())
    t = data["type"]

    if t == "REGISTER":
        peer = f'{data["ip"]}:{data["port"]}'
        peers[peer] = time.time()
        conn.send(json.dumps({"status":"ok"}).encode())

    elif t == "HEARTBEAT":
        peer = f'{data["ip"]}:{data["port"]}'
        peers[peer] = time.time()
        conn.send(json.dumps({"status":"ok"}).encode())

    elif t == "PUBLISH":
        h = data["hash"]

        if h not in files:
            files[h] = {
                "nome": data["nome"],
                "hash": h,
                "peers": []
            }

        peer = f'{data["ip"]}:{data["port"]}'

        if peer not in files[h]["peers"]:
            files[h]["peers"].append(peer)

        conn.send(json.dumps({"status":"ok"}).encode())

    elif t == "SEARCH":
        q = data["query"].lower()

        res = [
            f for f in files.values()
            if q in f["nome"].lower()
        ]

        conn.send(json.dumps({"results":res}).encode())

    elif t == "PLAYLIST":
        conn.send(json.dumps({"playlist":[f["nome"] for f in files.values()]}).encode())

    conn.close()

def main():
    s = socket.socket()
    s.bind((HOST, PORT))
    s.listen()

    threading.Thread(target=cleanup, daemon=True).start()

    while True:
        conn, _ = s.accept()
        threading.Thread(target=handle, args=(conn,), daemon=True).start()

main()
```

---

# 7. Implementação do Cliente (Peer)

Arquivo: `client.py`

```python
[INSERIR CLIENT.PY FINAL AQUI]
```

> Substituir pelo código final do cliente implementado no projeto.

---

# 8. Dockerfile

Arquivo: `Dockerfile`

```dockerfile
FROM python:3.10

WORKDIR /app

COPY . .

CMD ["python"]
```

---

# 9. Docker Compose

Arquivo: `docker-compose.yml`

```yaml
services:
  server:
    build: .
    command: python server.py
    ports:
      - "5000:5000"

  peer1:
    build: .
    command: python client.py
    environment:
      - PORT=5001
    volumes:
      - ./shared_peer1:/app/shared
    depends_on:
      - server

  peer2:
    build: .
    command: python client.py
    environment:
      - PORT=5002
    volumes:
      - ./shared_peer2:/app/shared
    depends_on:
      - server
```

---

# 10. Como Executar o Projeto

---

## 10.1 Build e Inicialização

Na raiz do projeto:

```bash
docker compose up --build
```

---

## 10.2 Verificar Containers

```bash
docker ps
```

Saída esperada:

```text
p2p_musicas-peer1-1
p2p_musicas-peer2-1
p2p_musicas-server-1
```

---

# 11. Como Utilizar o Sistema

---

## 11.1 Abrir Terminal Interativo do Peer 1

```bash
docker exec -it p2p_musicas-peer1-1 python -c "import client; client.interactive()"
```

---

## 11.2 Abrir Terminal Interativo do Peer 2

```bash
docker exec -it p2p_musicas-peer2-1 python -c "import client; client.interactive()"
```

---

# 12. Comandos Disponíveis

---

## Publicar Música

```bash
publish musica1.mp3
```

---

## Buscar Música

```bash
search musica
```

---

## Download de Música

```bash
download HASH_DO_ARQUIVO PEER:PORTA
```

Exemplo:

```bash
download 184ed0976af84bdd964eb445c24da521 peer1:5001
```

---

## Ver Playlist Global

```bash
playlist
```

---

## Listar Arquivos Locais

```bash
list_local
```

---

## Encerrar Sessão Interativa

```bash
exit
```

---

# 13. Protocolo de Comunicação

---

## Cliente ↔ Servidor

Formato JSON sobre TCP.

### Exemplos:

```json
{"type":"REGISTER","ip":"peer1","port":5001}
```

```json
{"type":"SEARCH","query":"musica"}
```

---

## Peer ↔ Peer

Transferência TCP direta.

Comando:

```text
DOWNLOAD <hash>
```

---

# 14. Testes Realizados

---

## Teste 1 – Registro de Peers

Todos os peers registraram-se corretamente no tracker.

---

## Teste 2 – Publicação de Música

Peer1 publicou arquivo `.mp3`.

---

## Teste 3 – Busca de Música

Peer2 encontrou corretamente a música publicada.

---

## Teste 4 – Download P2P

Peer2 realizou download direto do Peer1.

---

# 15. Conclusão

O sistema implementado atendeu aos requisitos propostos para um sistema P2P híbrido de compartilhamento de músicas.

Foram validadas as funcionalidades de:

* Registro de peers
* Heartbeat
* Publicação de arquivos
* Busca de recursos
* Download Peer-to-Peer
* Playlist global

A utilização de Docker permitiu a simulação eficiente de múltiplos nós distribuídos em uma única máquina.

>>>>>>> ffeeaad74be6770aeedead40e2488024ece6a4f8
Como possíveis melhorias futuras:

* Download paralelo
* Criptografia entre peers
* Interface gráfica
* Reprodução automática de músicas

---
