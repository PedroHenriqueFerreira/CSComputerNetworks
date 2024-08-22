from socket import socket, AF_INET, SOCK_STREAM
from json import loads, dumps
from random import uniform
from threading import Thread

from settings import HOST, PORT

class Actuator:
    ''' Simula um atuador qualquer '''
    
    def __init__(self, name: str, delta: float, code: int):
        self.id = id(self) # Identificador único do atuador
        self.name = name # Nome do atuador
        self.delta = delta # Variação do atuador
        self.code = code # Código de conexão com o servidor
        self.state = False # Estado do atuador
        
    def run(self):
        ''' Método que se comunica com o servidor '''
        
        try:
            s = socket(AF_INET, SOCK_STREAM)
            s.connect((HOST, PORT))
            
            print(f'Atuador {self.name} se conectando ao servidor...')
            
            initial_data = { 
                'id': self.id, 
                'type': 'atuador',
                'name': self.name, 
                'delta': self.delta,
                'code': self.code,
                'state': self.state
            }
            
            s.sendall(dumps(initial_data).encode())
            
            response = loads(s.recv(1024).decode())
            
            if response['connected'] == False:
                print(f'{self.name} rejeitada(o) pelo servidor')
                
                return s.close()
            
            print(f'{self.name} aceita(o) pelo servidor')
            
            while True:
                data = loads(s.recv(1024).decode())
                
                self.state = data['state']
                
                s.sendall(dumps({ 'type': 'atuador', 'id': self.id, 'state': self.state }).encode())
                        
            
        except Exception as e:
            print(f'Erro: {e}')
            
if __name__ == '__main__':
    actuators = [
        Actuator('aquecedor', 1, 1234),
        Actuator('resfriador', -1, 1234),
        Actuator('irrigador', 1, 1234),
        Actuator('injetor', 5, 1234),
    ]
    
    for actuator in actuators:
        Thread(target=actuator.run).start()