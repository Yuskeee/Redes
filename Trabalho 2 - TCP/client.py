import socket
import threading
import sys
import io

""""
Protocolo de aplicação sugerido pelos alunos:

- Conexão TCP/IP

Cada mensagem deve ser precedida do seguinte cabeçalho:

No caso de uma mensagem de arquivo, o cabeçalho deve ser:
+---------------------------+
| Tipo da msg               |
+---------------------------+
| Tamanho em bytes do nome  |
+---------------------------+
| Nome do arquivo           |
+---------------------------+
| Tamanho total do arquivo  |
+---------------------------+
| Conteúdo da msg           |

No caso de uma mensagem de texto, o cabeçalho deve ser:
+---------------------------+
| Tipo da msg               |
+---------------------------+
| Conteúdo da msg           |

Onde:
- Tipo da msg: um byte que indica o tipo da mensagem (0 para texto para buffer CLI, 1 para arquivo)
- Tamanho da msg: um valor binario representando o tamanho da mensagem em bytes
- Conteúdo da msg: o conteúdo da mensagem, que pode ser texto ou dados de arquivo
"""

class Client:
    def __init__(self, host='localhost', port=6363):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.running = False
        self.receive_thread = None
        self.download_buffer = io.BytesIO()  # Buffer para armazenar dados recebidos de arquivos
        self.is_downloading = False  # Flag para indicar se está baixando um arquivo

    def connect(self):
        try:
            self.socket.connect((self.host, self.port))
            print(f"Conexao com sucesso em {self.host}:{self.port}")
            self.running = True
            self.receive_thread = threading.Thread(target=self._receive_messages, daemon=True)
            self.receive_thread.start()
        except Exception as e:
            print(f"Nao foi possivel conectar {self.host}:{self.port}: {e}")
            sys.exit(1)

    def _receive_messages(self):
        while self.running:
            try:
                # data = self.socket.recv(1024)
                # if not data:
                #     print("Servidor encerrou a conexao.")
                #     break
                # print(data.decode(), end="\n")
                self.handle_data() # Rotina para tratar a mensagem recebida
            except Exception as e:
                if self.running:
                    print(f"Erro ao receber: {e}")
                break
        self.stop()

    def handle_data(self):
        # Extrai informações do cabeçalho
        message_type = self.socket.recv(1).decode()
        if message_type == '0':
            # Mensagem de texto
            content = self.socket.recv(1024-1).decode()
            if content:
                print(f"Mensagem recebida: {content}")
            
        elif message_type == '1': 
            # Tamanho em bytes do nome do arquivo
            file_name_length = int.from_bytes(self.socket.recv(1), 'big')  # Recebe o tamanho do nome do arquivo como um inteiro de 1 byte
            if file_name_length <= 0:
                print("Tamanho do nome do arquivo inválido.")
                return
            # Nome do arquivo
            file_name = self.socket.recv(file_name_length).decode()  # Recebe o nome do arquivo
            if not file_name:
                print("Nome do arquivo vazio.")
                return
            file_size = int.from_bytes(self.socket.recv(4), 'big')  # Recebe o tamanho do arquivo como um inteiro de 4 bytes
            print(f"Recebendo arquivo: {file_name} ({file_size} bytes)")
            content = self.socket.recv(1024 - file_name_length - 6)  # Recebe o conteúdo do arquivo, descontando o tamanho do nome e do tamanho do arquivo
            # print("content: ", content)
            # print(len(content))

            if not content:
                print(f"Arquivo {file_name} vazio ou não recebido.")
                return
            # Verifica se o arquivo já está sendo baixado
            if not self.is_downloading:
                self.is_downloading = True
                self.download_buffer = io.BytesIO()
            # Adiciona o conteúdo ao buffer de download
            self.download_buffer.write(content)
            # Verifica se o tamanho do buffer é igual ao tamanho do arquivo
            if self.download_buffer.tell() >= file_size:    
                # Se o buffer contém todo o arquivo, salva em disco
                with open(f"{file_name}.received", 'wb') as f:
                    f.write(self.download_buffer.getvalue())
                print(f"Arquivo {file_name} recebido com sucesso.")
                self.is_downloading = False
                self.download_buffer.close()
            else:
                # Se o buffer não contém todo o arquivo, continua recebendo
                print(f"Recebido {self.download_buffer.tell()} de {file_size} bytes do arquivo {file_name} ({(self.download_buffer.tell())/file_size * 100:.2f}%).")

    def send(self, message):
        if self.running and message:
            try:
                self.socket.send(message.encode())
            except Exception as e:
                print(f"Erro ao enviar msg: {e}")
                self.stop()
            
    def stop(self):
        if self.running:
            self.running = False
            try:
                self.socket.shutdown(socket.SHUT_RDWR)
            except:
                pass
            self.socket.close()
            print("Desconectado.")
        sys.exit(0)

    def run(self):
        self.connect()
        try:
            while True:
                message = input()
                if message.lower() in ('sair'):
                    print("Desconectado...")
                    break
                self.send(message)
        except KeyboardInterrupt:
            print("\nSaindo...")
        finally:
            self.stop()

if __name__ == "__main__":
    host = 'localhost'
    port = 6363
    if len(sys.argv) >= 2:
        host = sys.argv[1]
    if len(sys.argv) >= 3:
        try:
            port = int(sys.argv[2])
        except ValueError:
            print("Usando porta padrão 6363.")

    client = Client(host, port)
    client.run()
