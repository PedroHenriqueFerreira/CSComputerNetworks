from typing import Any

from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
from json import loads, dumps

from settings import HOST, PORT

class Manager:
    ''' Gerenciador de conexões com os clientes '''
    
    def __init__(self, code: int):
        self.code = code # Código para autenticação dos clientes
        self.connections: list[dict[str, Any]] = [] # Conexões com os clientes
    
    def find_connection(self, search: dict[str, Any]):
        ''' Procura uma conexão com base nos critérios de busca '''	
        
        connections = self.find_connections(search)
        
        if len(connections) == 0:
            return {}
        
        return connections[0]
    
    def find_connections(self, search: dict[str, Any]):
        ''' Procura todas as conexões com base nos critérios de busca '''	
        
        connections = []
        
        for connection in self.connections:
            is_valid = True
            
            for key in search:
                if key not in connection:
                    is_valid = False
                    break
                
                if connection[key] != search[key]:
                    is_valid = False
                    break
            
            if is_valid:
                connections.append(connection)
            
        return connections
    
    def run(self):  
        ''' Método que cria todas as conexões com os clientes '''
        
        try:
            s = socket(AF_INET, SOCK_STREAM)
            s.bind((HOST, PORT))
            s.listen()
            
            print('Aguardando conexões...')
            
            # Para cada nova conexão, cria uma nova thread
            while True: 
                conn, ender = s.accept()
                
                print(f'Nova conexão: {ender}')
                
                Thread(target=self.create_connection, args=(conn, ender)).start()
        
        except Exception as e:
            print(f'Erro: {e}')
            
    def create_connection(self, conn: socket, ender: Any):
        ''' Método que gerencia a conexão com o cliente '''

        print(f'Estabelecendo conexão: {ender}')
        
        initial_data: dict[str, Any] = loads(conn.recv(1024).decode())
            
        if initial_data['code'] != self.code:
            print(f'Conexão rejeitada: {ender}')

            conn.sendall(dumps({ 'connected': False }).encode())

            return conn.close()
        
        conn.sendall(dumps({ 'connected': True }).encode())
        
        print(f'Conexão estabelecida: {ender}')
        
        self.connections.append({
            'conn': conn,
            'ender': ender,
            **initial_data,
        })

        while True:
            data = loads(conn.recv(1024).decode())  
            
            # print(f'Dados recebidos de {ender}: {data}')
            
            match data['type']: 
                case 'sensor':
                    sensor = self.find_connection({ 'id': data['id'] })
                    
                    sensor['value'] = data['value'] # Atualiza o valor do sensor

                    match sensor['name']:
                        case 'temperatura':
                            aquecedor = self.find_connection({ 'type': 'atuador', 'name': 'aquecedor' })
                            resfriador = self.find_connection({ 'type': 'atuador', 'name': 'resfriador' })
                            
                            if not aquecedor or not resfriador:
                                continue
                            
                            if data['value'] < sensor['min_value']:
                                print('Ligando o aquecedor')
                                aquecedor['conn'].sendall(dumps({ 'state': True }).encode())
                
                            elif data['value'] > sensor['max_value']:
                                print('Ligando o resfriador')
                                resfriador['conn'].sendall(dumps({ 'state': True }).encode())
                            
                            else:
                                print('Desligando o aquecedor')
                                aquecedor['conn'].sendall(dumps({ 'state': False }).encode())
                        
                                print('Desligando o resfriador')
                                resfriador['conn'].sendall(dumps({ 'state': False }).encode())
                                
                        case 'umidade':
                            irrigador = self.find_connection({ 'type': 'atuador', 'name': 'irrigador' })
                            
                            if not irrigador:
                                continue
                            
                            if data['value'] < sensor['min_value']:
                                print('Ligando o irrigador')
                                irrigador['conn'].sendall(dumps({ 'state': True }).encode())
                            else:
                                print('Desligando o irrigador')
                                irrigador['conn'].sendall(dumps({ 'state': False }).encode())
                                
                        case 'co2':
                            injetor = self.find_connection({ 'type': 'atuador', 'name': 'injetor' })
                            
                            if not injetor:
                                continue
                            
                            if data['value'] < sensor['min_value']:
                                print('Ligando o injetor')
                                injetor['conn'].sendall(dumps({ 'state': True }).encode())
                            else:
                                print('Desligando o injetor')
                                injetor['conn'].sendall(dumps({ 'state': False }).encode())
                    
                case 'atuador':
                    atuador = self.find_connection({ 'id': data['id'] })
                    
                    atuador['state'] = data['state'] # Atualiza o estado do atuador 
                    
                    temperatura = self.find_connection({ 'type': 'sensor', 'name': 'temperatura' })
                    umidade = self.find_connection({ 'type': 'sensor', 'name': 'umidade' })
                    co2 = self.find_connection({ 'type': 'sensor', 'name': 'co2' })
                    
                    delta = atuador['delta'] if atuador['state'] else 0
                    
                    match atuador['name']:
                        case 'aquecedor' | 'resfriador':
                            # Atualiza a temperatura do ambiente
                            temperatura['conn'].sendall(dumps({ 'delta': delta }).encode())
                        
                        case 'irrigador':
                            # Atualiza a umidade do ambiente
                            umidade['conn'].sendall(dumps({ 'delta': delta }).encode())
                        
                        case 'injetor':
                            # Atualiza o CO2 do ambiente
                            co2['conn'].sendall(dumps({ 'delta': delta }).encode())
                    
                case 'cliente':
                    cliente = self.find_connection({ 'id': data['id'] })
                    
                    match data['action']:
                        case 'ler sensores':
                            sensores = self.find_connections({ 'type': 'sensor' })

                            cliente['conn'].sendall(dumps({ se['name']: se['value'] for se in sensores }).encode())
                        
                        case 'ler atuadores':
                            atuadores = self.find_connections({ 'type': 'atuador' })

                            cliente['conn'].sendall(dumps({ at['name']: at['state'] for at in atuadores }).encode())
                            
                        case 'alterar sensor':
                            sensor = self.find_connection({ 'type': 'sensor', 'name': data['name'] })
                            
                            sensor['min_value'] = data['min_value']
                            
                            if sensor['name'] == 'temperatura':
                                sensor['max_value'] = data['max_value'] 

                            cliente['conn'].sendall(dumps({ 'success': True }).encode())

if __name__ == '__main__':
    Manager(1234).run()