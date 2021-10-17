from socket import socket, AF_INET, SOCK_DGRAM
from threading import Thread
from random import randint
from time import sleep

server_socket = socket(AF_INET, SOCK_DGRAM)  # Montar socket
server_socket.bind(('localhost', 9500))
##localhost deve ser alterado para o IP do servidor

def conectarClientes():
    # server_socket.listen()
    conectar_clientes = True
    while conectar_clientes:
        data, client_address = server_socket.recvfrom(2048)
        recebido = data.decode()
        recebido = recebido.split()
        if recebido[0] == 'participar':
            if len(clientes) == 5:
                msg = 'ERRO: Limite máximo de 5 usuários foi alcançado'
                server_socket.sendto(msg.encode(), client_address)
                conectar_clientes = False
            elif client_address not in clientes:
                clientes[client_address] = [recebido[1], 0, [False] * numRodadas]
                msg = f'Você está participando do Quiz! No momento há {len(clientes)} participando, aguarde.'
                server_socket.sendto(msg.encode(), client_address)
        finalizar = input(f'Há {len(clientes)} usuário participando, deseja iniciar o Quiz? (s/n)').lower()
        if finalizar == 's':
            for client in clientes:
                server_socket.sendto('1'.encode(), client)
            conectar_clientes = False

def enviarProtocolo(mensagem, rodada, client):
    protocolo = str([{'mensagem': mensagem, 'rodada': rodada}])
    # MUDAR LOCALHOST PARA IP DO SERVIDOR QUANDO USAR VPN
    server_socket.sendto(protocolo.encode(), client)

def receberProtocolo():
    data, client_address = server_socket.recvfrom(2048)
    protocolo = eval(data)
    resposta = protocolo[0]['mensagem']
    rodada = protocolo[0]['rodada']
    global tupla
    tupla = (str(resposta), client_address, int(rodada))

def tempo():
    sleep(10)
    return False

def quiz(perguntas):
    q = True
    perguntasFeitas = []
    while q:
        for r in range(1, 6):
            pergValida = False
            while not pergValida:
                num = randint(0, 4)
                if num not in perguntasFeitas:
                    pergValida = True
                    perguntasFeitas.append(num)
                    pergunta = f'Pergunta nº {r}: {perguntas[num][0]}'

            sleep(2)
            for client in clientes:
                enviarProtocolo(pergunta, r, client)
            respostaCorreta = False
            print(f'Servidor enviou a pergunta  {r} para todos os {len(clientes)} participantes')
            while True:
                print('ELE ENVIOU\n',pergunta)
                tempo()
                receberProtocolo()
                resposta, cliente, rodada = tupla[0], tupla[1], tupla[2]
                if rodada == r:
                    if resposta == perguntas[num][1]:
                        clientes[cliente][1] += 25
                        respostaCorreta = True
                    else:
                        clientes[cliente][1] -= 5
                    clientes[cliente][2][r - 1] = True
                    if respostaCorreta:
                        mensagem = str(f'Fim da {r}º rodada')
                        for client in clientes:
                            server_socket.sendto(mensagem.encode(), client)
                    else:
                        mensagem = str(f'Resposta da {r}º pergunta está errada')
                        server_socket.sendto(mensagem.encode(), cliente)
                else:
                    mensagem = str(f'O quiz está na {r}º rodada')
                    server_socket.sendto(mensagem.encode(), cliente)

                for c in clientes.values():
                    print(f'{c[0]}: {c[1]} pontos')

                for cliente in clientes:
                    if clientes[cliente][2][r - 1] == False:
                        clientes[cliente][1] -= 1
                break
            if r == 5:
                print('TODAS AS PERGUNTAS FORAM FEITAS')
                return


tupla = (None, None, None)
perguntas = open('perguntas.txt', 'r')
perguntas = perguntas.readlines()
cont = 0
for x in perguntas:
    perguntas[cont] = eval(x)
    cont += 1
numRodadas = 5
clientes = {}
conectarClientes()
quiz(perguntas)

pontuacao = ''
for cliente in clientes.values():
    pontuacao += f'{cliente[0]}: {cliente[1]}\n'
for cliente in clientes:
    enviarProtocolo(pontuacao, -1, cliente)