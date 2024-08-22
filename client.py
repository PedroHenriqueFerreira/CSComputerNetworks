from socket import socket, AF_INET, SOCK_STREAM
from json import dumps, loads

from settings import HOST, PORT

s = socket(AF_INET, SOCK_STREAM)
s.connect((HOST, PORT))

class Client:
    ''' Simula um cliente qualquer '''
    
    def __init__(self, code: int):
        self.id = id(self) # Identificador único do cliente
        self.code = code # Código de autenticação do cliente
        
    def run(self):
        ''' Método que se comunica com o servidor '''
        
        try:
            s = socket(AF_INET, SOCK_STREAM)
            s.connect((HOST, PORT))
            
            print(f'Cliente se conectando ao servidor...')
            
            initial_data = { 
                'id': self.id, 
                'code': self.code,
                'type': 'cliente'
            }
            
            s.sendall(dumps(initial_data).encode())
                
            response = loads(s.recv(1024).decode())
            
            if response['connected'] == False:
                print(f'Cliente rejeitado pelo servidor')
                
                return s.close()
            
            print(f'Cliente aceito pelo servidor')
            
            while True:
                out = int(input('''
                    1 - Ler sensores
                    2 - Ler atuadores
                    3 - Alterar sensores
                '''))
                
                if out == 1:
                    print('Lendo sensores...')
                    s.sendall(dumps({ 'type': 'cliente', 'action': 'ler sensores', 'id': self.id }).encode())
                
                    print(loads(s.recv(1024).decode()))
                    
                elif out == 2:
                    print('Lendo atuadores...')
                    s.sendall(dumps({ 'type': 'cliente', 'action': 'ler atuadores', 'id': self.id }).encode())
                    
                    print(loads(s.recv(1024).decode()))
                elif out == 3:
                    sensor = int(input('''
                        1 - Temperatura
                        2 - Umidade
                        3 - CO2                
                    '''))
                    
                    if sensor == 1:
                        min_value = float(input('Valor mínimo: '))
                        max_value = float(input('Valor máximo: '))
                        
                        s.sendall(dumps({ 
                            'type': 'cliente', 
                            'action': 'alterar sensor', 
                            'name': 'temperatura', 
                            'min_value': min_value, 
                            'max_value': max_value,
                            'id': self.id
                        }).encode())
                    elif sensor == 2:
                        min_value = float(input('Valor mínimo: '))
                        
                        s.sendall(dumps({ 
                            'type': 'cliente', 
                            'action': 'alterar sensor', 
                            'name': 'umidade', 
                            'min_value': min_value, 
                            'id': self.id
                        }).encode())
                    
                    elif sensor == 3:
                        min_value = float(input('Valor mínimo: '))
                        
                        s.sendall(dumps({ 
                            'type': 'cliente', 
                            'action': 'alterar sensor', 
                            'name': 'co2', 
                            'min_value': min_value, 
                            'id': self.id
                        }).encode())
                        
                        response = loads(s.recv(1024).decode())
                        
                        print(response)
                    else:
                        print('Opção inválida')
                else:
                    print('Opção inválida')
                
        except Exception as e:
            print(f'Erro: {e}')
            
if __name__ == '__main__':
    client = Client(1234)
    client.run()