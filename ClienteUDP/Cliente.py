from socket import socket, AF_INET, SOCK_DGRAM
from threading import Thread

sock = socket(AF_INET, SOCK_DGRAM)
sock.bind(('localhost', 8080))
def conectarQuiz():
    participar = False
    comecou = False
    naPartida = False
    while not participar or not comecou:
        if not participar:
            mensagem = input('Para Participar o Quiz digite: participar + seu nome\nEx: participar Vinicius\n> ').lower()
            sock.sendto(mensagem.encode(), ('localhost', 9500))  # localhost deve ser alterado para o IP do servidor
            data, client_address = sock.recvfrom(2048)
            print(data.decode())
            if 'ERRO:' not in data.decode():
                naPartida = True
                participar = True
            if not comecou:
                data, client_address = sock.recvfrom(2048)
                if data.decode() == '1':
                    comecou = True
                    return naPartida

def enviarProtocolo(mensagem, rodada):
    protocolo = str([{'mensagem': mensagem, 'rodada': rodada}])
    # MUDAR LOCALHOST PARA IP DO SERVIDOR QUANDO USAR VPN
    sock.sendto(protocolo.encode(),  ('localhost', 9500))

def receberProtocolo():
    data, client_address = sock.recvfrom(2048)
    if data is not None:
        protocolo = eval(data.decode())
        pergunta = protocolo[0]['mensagem']
        global rodada
        rodada = protocolo[0]['rodada']
        if int(rodada) != -1:
            print(pergunta)
        else:
            global rodadaAux
            rodadaAux = -1
            print(f'\n{pergunta}')

def comecarQuiz(naPartida):
    terminou = False
    while naPartida and not terminou:
        receberProtocolo()
        if rodadaAux != -1:
            resposta = input('resposta\n> ')
            Thread(target=enviarProtocolo, args=(resposta, rodada)).start()
            data, server = sock.recvfrom(2048)
            print(data.decode())
        else:
            terminou = True
            print('FIM DO QUIZ')

naPartida = conectarQuiz()
print('O QUIZ IRÁ COMEÇAR!\n')
rodadaAux = None
comecarQuiz(naPartida)
sock.close()