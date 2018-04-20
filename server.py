#!/usr/bin/python3

import socket
import threading
import time

CONFIG_FILE = "server.cfg"
LOG_FILE = "server.log"

FILA_COMANDOS = []
DATABASE = {}
SOCKET = None


def save_log(cmd):
    try:
        file = open(LOG_FILE, "a+")
        file.write("\n" + cmd)
        file.close()
    except Exception as error:
        print("Erro no arquivo de log:", LOG_FILE, error)
    return


def recover_log(LOG_FILE):
    try:
        file = open(LOG_FILE)
        print("Recuperando banco de dados...")
        for linha in file:
            execute(linha.strip(), True)
        print("Banco de dados recuperado com sucesso!")
    except Exception as error:
        print("Erro ao recuperar arquivo de log:", LOG_FILE, error)



def open_config(config_file):
    try:
        file = open(config_file)
        linha = file.read()
        info = linha.strip().split(":")
        file.close()
        return info[0], int(info[1])
    except Exception as error:
        print("Erro no arquivo de configuração:", config_file, error)
        exit(1)


# Retorna o banco de dados completo
def all():
    return "Todos os dados:\n" + "".join("{!s} : {!r}\n".format(key, val) for (key, val) in DATABASE.items())


# Adiciona ou faz update de uma valor
def add(chave, valor):
    global DATABASE
    DATABASE[chave] = valor
    return "{} {} adicionado".format(chave, valor)


# Deleta uma chave
def delete(chave):
    global DATABASE
    try:
        valor = DATABASE.pop(chave)
        return "{} {} removido".format(chave, valor)
    except:
        return "Chave {} inexistente".format(chave)


# Retorna o valor de uma chave
def show(chave):
    try:
        return "{} {}".format(chave, DATABASE[chave])
    except:
        return "Chave {} inexistente".format(chave)


# Faz o parsing e manda executar os comandos no database
def execute(comando, recover):
    if comando[:5] in {"/add ", "/del ", "/shw "} or comando.strip() == "/all"\
            or comando.strip() == "/help":
        comando_split = comando.strip().split(" ")

        cmd = comando_split[0]

        chave = None
        try:
            chave = int(comando_split[1])
        except:
            pass

        valor = None
        try:
            if len(comando_split[2]) < 3000:
                valor = comando_split[2]
        except:
            pass

        if cmd == "/help":
            return """
###############################################################################
Comandos disponiveis:
/all - Visualizar banco de dados
/add <chave[int]> <valor[string]> - Adiciona ou faz update de entrada no banco de dados
/del <chave[int]> - Deleta uma entrada no banco de dados
/shw <chave[int]> - Mostra o valor da chave especificada
/help - Visualizar ajuda
###############################################################################
"""
        elif cmd == "/all":
            return all()
        elif cmd == "/add" and chave is not None and valor is not None:
            if not recover:
                threading.Thread(target=save_log, args=("{} {} {}".format(cmd, chave, valor),)).start()  # Thread para salvar em arquivo
            return add(chave, valor)
        elif cmd == "/del" and chave is not None:
            if not recover:
                threading.Thread(target=save_log, args=("{} {}".format(cmd, chave),)).start()
            return delete(chave)
        elif cmd == "/shw" and chave is not None:
            return show(chave)

    return "Comando invalido, digite /help para receber ajuda."


def process(cmd, addr):
    retorno = execute(cmd, False)
    try:
        SOCKET.sendto(retorno.encode(), addr)
    except:
        print("Erro ao responder cliente:", addr)
    return


# Consume a fila de comandos
def consume_fila(FILA_COMANDOS):
    while True:
        try:
            # Remove comando da lista
            cmd, addr = FILA_COMANDOS.pop(0)

            # Thread para executar comando
            threading.Thread(target=process, args=(cmd, addr)).start()
        except Exception as error:
            time.sleep(0.2)


# Loop to bind and receive messages
def accept(ip, port, FILA_COMANDOS):
    global SOCKET
    SOCKET = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        SOCKET.bind((ip, port))
        print("Server escutando em {}:{}".format(ip, port))

        while True:
            data, addr = SOCKET.recvfrom(2048)  # buffer size is 1024 bytes
            data_string = data.decode()
            FILA_COMANDOS.append((data_string, addr))

    except Exception as error:
        print("Erro:", error, port, ip)
        SOCKET.close()
        exit(1)


if __name__ == "__main__":
    ip, port = open_config(CONFIG_FILE)

    # Recover DB from log
    recover_log(LOG_FILE)

    # Thread para abrir servidor e receber comandos e coloca-los em fila
    threading.Thread(target=accept, args=(ip, port, FILA_COMANDOS)).start()

    # Thread para consumir fila
    threading.Thread(target=consume_fila, args=(FILA_COMANDOS,)).start()
