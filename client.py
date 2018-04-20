#!/usr/bin/python3

import socket
import threading

CONFIG_FILE = "client.cfg"


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


def send_comand(ip, port, cmd):
    sock_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        sock_client.sendto(cmd[:1400].encode(), (ip, port))
    except Exception as error:
        print("\nFalha no envio:", error)

    try:
        msg, addr = sock_client.recvfrom(2048)
        print("\n", msg.decode())
    except Exception as error:
        print("\nFalha no resposta:", error)


if __name__ == "__main__":
    ip, port = open_config(CONFIG_FILE)

    print("Digite /help para receber ajuda")

    # Thread pai fica recebendo comandos do input
    while True:
        cmd = input(">> ")
        # Nova thread para enviar comandos e mostrar a resposta na tela
        threading.Thread(target=send_comand, args=(ip, port, cmd)).start()
