from typing import Any

from socket import socket, AF_INET, SOCK_STREAM, _RetAddress
from threading import Thread
from json import loads, dumps

from settings import HOST, PORT

class Manager:
    ''' Gerenciador de conexões com os clientes '''
    
    def __init__(self, code: int):
        self.code = code # Código para autenticação dos clientes
        self.connections: list[dict[str, Any]] = [] # Conexões com os clientes
    
    def run(self):  
        ''' Método que cria todas as conexões com os clientes '''
        
        s = socket(AF_INET, SOCK_STREAM)
        s.bind((HOST, PORT))
        s.listen()
        
        print('Aguardando conexões...')
        
        # Para cada nova conexão, cria uma nova thread
        while True: 
            conn, ender = s.accept()
            
            print(f'Nova conexão: {ender}')
            
            Thread(target=self.create_connection, args=(conn, ender)).start()
            
    def create_connection(self, conn: socket, ender: _RetAddress):
        ''' Método que gerencia a conexão com o cliente '''

        try:
            print(f'Estabelecendo conexão: {ender}')
            
            initial_data: dict[str, Any] = loads(conn.recv(1024).decode())
                
            if initial_data['code'] != self.code:
                print(f'Conexão rejeitada: {ender}')

                conn.sendall(dumps({ 'connected': False }).encode())

                return conn.close()
            
            conn.sendall(dumps({ 'connected': True }).encode())
            
            print(f'Conexão estabelecida: {ender}')
            
            connection = {
                'conn': conn,
                'ender': ender,
                'id': initial_data['id'],
                'type': initial_data['type']
            }
            
            match initial_data['type']:
                case 'sensor':
                    connection['min_value'] = initial_data['min_value']
                    connection['max_value'] = initial_data['max_value']
            
            self.connections.append({ 
                'conn': conn, 
                'ender': ender,
                'id': initial_data['id'],
                'type': initial_data['type']
            })

            while True:
                data = loads(conn.recv(1024).decode())  
                
                print(f'Dados recebidos de {ender}: {data}')
                
                match data['type']: 
                    case 'sensor':
                        sensor = self.find_connection(data['id'])
                        
                        sensor
                                                
                        ... 
                        
                    case 'actuator':
                        ...
                        
                    case 'client':
                        ...
                        
            
        except Exception as e:
            print(f'Erro: {e}')
            
            print(f'Fechando conexão: {ender}')
                
            return conn.close()

    def find_connection(self, id: int):
        ''' Obtém uma conexão pelo id '''
        
        for connection in self.connections:
            if connection['id'] != id:
                continue
            
            return connection
            
        return None