from socket import socket, AF_INET, SOCK_STREAM
from time import sleep

from settings import HOST, PORT

s = socket(AF_INET, SOCK_STREAM)
s.connect((HOST, PORT))

while True:
    s.sendall(str.encode('Bom dia'))

    data = s.recv(1024)

    print('Mensagem ecoada:', data.decode())

    sleep(1)