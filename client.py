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
                out = int(input('\nEscolha uma opção: \n1 - Ler sensores \n2 - Ler atuadores \n3 - Alterar sensores\n\n'))
                
                if out == 1:
                    print('\nLendo sensores...\n')
                    s.sendall(dumps({ 'type': 'cliente', 'action': 'ler sensores', 'id': self.id }).encode())
                
                    data = loads(s.recv(1024).decode())

                    print(f'Temperatura: {data["temperatura"]:.3f}\nUmidade: {data["umidade"]:.3f}\nCO2: {data["co2"]:.3f}')
                    
                elif out == 2:
                    print('\nLendo atuadores...\n')
                    s.sendall(dumps({ 'type': 'cliente', 'action': 'ler atuadores', 'id': self.id }).encode())
                    
                    data = loads(s.recv(1024).decode())

                    print(f'Aquecedor: {"Ligado" if data["aquecedor"] else "Desligado"}\nResfriador: {"Ligado" if data["resfriador"] else "Desligado"}\nIrrigador: {"Ligado" if data["irrigador"] else "Desligado"}\nInjetor: {"Ligado" if data["injetor"] else "Desligado"}')
                elif out == 3:
                    sensor = int(input('\nEscolha um sensor:\n1 - Temperatura \n2 - Umidade \n3 - CO2\n\n'))
                    
                    if sensor == 1:
                        min_value = float(input('\nValor mínimo: '))
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
                        min_value = float(input('\nValor mínimo: '))
                        
                        s.sendall(dumps({ 
                            'type': 'cliente', 
                            'action': 'alterar sensor', 
                            'name': 'umidade', 
                            'min_value': min_value, 
                            'id': self.id
                        }).encode())
                    
                    elif sensor == 3:
                        min_value = float(input('\nValor mínimo: '))
                        
                        s.sendall(dumps({ 
                            'type': 'cliente', 
                            'action': 'alterar sensor', 
                            'name': 'co2', 
                            'min_value': min_value, 
                            'id': self.id
                        }).encode())
                        
                    else:
                        print('\nOpção inválida\n')
                    
                    response = loads(s.recv(1024).decode())
                        
                    print('\nAlteração realizada com sucesso!' if response['success'] else '\nAlteração falhou!')
                
                else:
                    print('Opção inválida')
                
        except Exception as e:
            print(f'Erro: {e}')
            
if __name__ == '__main__':
    client = Client(1234)
    client.run()