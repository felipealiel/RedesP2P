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
Como possíveis melhorias futuras:

* Download paralelo
* Criptografia entre peers
* Interface gráfica
* Reprodução automática de músicas

---
