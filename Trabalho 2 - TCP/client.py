import socket
import threading
import sys
import os

class Client:
    def __init__(self, host='localhost', port=6363):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.running = False
        self.receive_thread = None

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
                data = self.socket.recv(1024)
                if not data:
                    print("Servidor encerrou a conexao.")
                    break
                print(data.decode(), end="\n")
            except Exception as e:
                if self.running:
                    print(f"Erro ao receber: {e}")
                break
        self.stop()

    def send(self, message):
        if self.running and message:
            try:
                self.socket.send(message.encode())
            except Exception as e:
                print(f"Erro ao enviar msg: {e}")
                self.stop()

    # def save_file(self, filename):
    #     with open(f"{filename}.received", 'wb') as f:
            


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
