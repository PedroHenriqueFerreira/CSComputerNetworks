from socket import socket, AF_INET, SOCK_STREAM
from json import loads, dumps
from random import uniform
from threading import Thread
from time import sleep

from settings import HOST, PORT

class Sensor:
    ''' Simula um sensor qualquer '''
    
    def __init__(self, name: str, value: float, min_delta: float, max_delta: float, code: int):
        self.id = id(self) # Identificador único do sensor
        
        self.name = name # Nome do sensor
        self.value = value # Valor do sensor
        
        self.min_delta = min_delta # Variação mínima
        self.max_delta = max_delta # Variação máxima
        
        self.min_value = float('-inf') # Valor mínimo
        self.max_value = float('inf') # Valor máximo
        
        self.code = code # Código de conexão com o servidor

    def run(self):  
        ''' Método que se comunica com o servidor '''
        
        try:
            s = socket(AF_INET, SOCK_STREAM)
            s.connect((HOST, PORT))
            
            print(f'Sensor {self.name} se conectando ao servidor...')
            
            initial_data = { 
                'id': self.id, 
                'type': 'sensor',
                'name': self.name, 
                'value': self.value, 
                'min_value': self.min_value,
                'max_value': self.max_value,
                'code': self.code
            }
            
            s.sendall(dumps(initial_data).encode())
            
            response = loads(s.recv(1024).decode())
            
            if response['connected'] == False:
                print(f'{self.name} rejeitada(o) pelo servidor')
                
                return s.close()
            
            print(f'{self.name} aceita(o) pelo servidor')
            
            Thread(target=self.sender, args=(s, )).start()
            Thread(target=self.receiver, args=(s, )).start()
            
        except Exception as e:
            print(f'Erro: {e}')
        
    def sender(self, s: socket):
        ''' Método que envia os dados do sensor para o servidor '''
        
        while True:
            self.value += uniform(self.min_delta, self.max_delta)
            
            print('Enviando dados ao gerenciador...')
            s.sendall(dumps({ 'type': 'sensor', 'id': self.id, 'value': self.value }).encode())
            
            sleep(1)
    
    def receiver(self, s: socket):
        ''' Método que recebe os dados do servidor '''
        
        while True:
            data = loads(s.recv(1024).decode())
            
            self.value += data['delta']
        
if __name__ == '__main__':
    sensors = [
        Sensor('temperatura', uniform(0, 35), -0.1, 0.2, 1234),
        Sensor('umidade', uniform(25, 100), -0.1, 0, 1234),
        Sensor('co2', uniform(100, 1000), -1, 0, 1234),
    ]
    
    for sensor in sensors:
        Thread(target=sensor.run).start()