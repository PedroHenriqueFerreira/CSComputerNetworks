class Sensor:
    def __init__(self, value: float):
        self.id = id(self)
        self.value = value
        
    def is_under_threshold(self):
        return self.value < self.min_value
    
    def is_over_threshold(self):
        return self.value > self.max_value

if __name__ == '__main__':
    from socket import socket, AF_INET, SOCK_STREAM
    from time import sleep

    from settings import HOST, PORT

    s = socket(AF_INET, SOCK_STREAM)
    s.connect((HOST, PORT))

    # while True:
    #     s.sendall(str.encode('Bom dia'))

    #     data = s.recv(1024)

    #     print('Mensagem ecoada:', data.decode())

    #     sleep(1)
    
    print('OK')