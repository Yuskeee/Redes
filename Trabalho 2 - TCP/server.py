import socket
import os
import threading
import time
import sys

class Server:
    def __init__(self, host='localhost', port=6363):
        self.host = host
        self.port = port
        self.server_socket = None
        self.client_sockets = []
        self.running = True
        self.lock = threading.Lock()
        
    def start(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"Servidor conectado com {self.host}:{self.port}")

        threading.Thread(target=self.send_message_clients, args=()).start()

        while self.running:
            client_socket, addr = self.server_socket.accept()
            print(f"Conexao com {addr}")
            with self.lock:
                self.client_sockets.append(client_socket)
            threading.Thread(target=self.handle_client, args=(client_socket,)).start()
            
    def send_message_clients(self):
        while self.running:
            msg = sys.stdin.readline().strip()
            if msg:
                with self.lock:
                    for sock in self.client_sockets:
                        try:
                            sock.sendall(msg.encode())
                        except Exception as e:
                            print(f"Erro ao enviar mensagem para o cliente: {e}")

    def handle_request(self, message, client_socket): 
        if message == "sair":
            print("Operação 'Sair'")
            with self.lock:
                self.client_sockets.remove(client_socket)
            client_socket.close()
            print("Cliente desconectado")
            return
        
        if message.startswith("arquivo "):
            filename = message.split(" ", 1)[1]
            print(f"Operação 'Arquivo' com arquivo: {filename}")
            try:
                with open(filename, 'rb') as f:
                    data = f.read()
                    client_socket.sendall(data)
                    print(f"Arquivo {filename} enviado para o cliente.")
            except FileNotFoundError:
                print(f"Arquivo {filename} não encontrado.")
                client_socket.sendall(b"Arquivo nao encontrado.")
        elif message.startswith("chat "):
            chat_message = message.split(" ", 1)[1]
            print(f"Operação 'Chat' com mensagem: {chat_message}")
            with self.lock:
                for sock in self.client_sockets:
                    if sock != client_socket:
                        try:
                            sock.sendall(chat_message.encode())
                        except Exception as e:
                            print(f"Erro ao enviar mensagem para o cliente: {e}")
        else:
            print(f"Operação desconhecida: {message}")
            client_socket.sendall(b"Operacao desconhecida.")


    def handle_client(self, client_socket):
        while self.running:
            try:
                data = client_socket.recv(1024)
                if not data:
                    break
                print(f"Recebido: {data.decode()}")
                message = data.decode().strip()
                self.handle_request(message, client_socket)
            except (ConnectionResetError, ConnectionAbortedError):
                print("Cliente desconectado inesperadamente")
                break
            except Exception as e:
                break
        if client_socket not in self.client_sockets:
            return
        with self.lock:
            self.client_sockets.remove(client_socket)
        client_socket.close()
        print("Cliente desconectado")

    def stop(self):
        self.running = False
        with self.lock:
            for client_socket in self.client_sockets:
                client_socket.close()
            self.client_sockets.clear()
        if self.server_socket:
            self.server_socket.close()
        print("Servidor encerrado.")
        os._exit(0)

if __name__ == "__main__":
    server = Server()
    try:
        server.start()
    except KeyboardInterrupt:
        server.stop()
    except Exception as e:
        print(f"Erro no servidor: {e}")
        server.stop()