import socket
import struct
import sys
import os
import hashlib
import random

SERVER_IP='192.168.0.147'
SERVER_PORT=6363

class client:
    def __init__(self, host=SERVER_IP, port=SERVER_PORT):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
    def request_file(self, file_name, debug=False):
        message = f"GET/{file_name}"
        self.server_socket.sendto(message.encode(), (self.host, self.port))

        if debug:
            print("Modo de simulacao de perda ativado.")
            self._debug_receive_file(file_name + ".received")
        else:
            self._receive_file(file_name + ".received")
        print(f"Arquivo {file_name} recebido com sucesso.")

    def _receive_file(self, file_name):
        data, _ = self.server_socket.recvfrom(1024)
        total_size = struct.unpack('!Q', data)[0] #total_size = 13.
        bytes_counter = 0
        #print(f"Tamanho total do arquivo: {total_size} bytes")

        with open(file_name, 'wb') as f:
            
            while bytes_counter < total_size:
                packet, _ = self.server_socket.recvfrom(1024) # 40 bytes do header(4 bytes seq, 4 bytes tam. pacote, 32 bytes hash) + 8 bytes dos dados do pacote
                seq, bytes_length, hash = struct.unpack('!II32s', packet[:40])
                data = packet[40:]
                
                # Hash verification
                calculated_hash = hashlib.sha256(data).digest()
                if calculated_hash != hash:
                    print(f"Erro: Hash do pacote {seq} não confere.")
                    break
                    
                f.write(data)
                bytes_counter += bytes_length
                ack = struct.pack('!I', seq)
                self.server_socket.sendto(ack, (self.host, self.port))

    def _debug_receive_file(self, file_name):
        data, _ = self.server_socket.recvfrom(1024)
        total_size = struct.unpack('!Q', data)[0] #total_size = 13.
        bytes_counter = 0
        random_seq = random.randint(0, int(total_size/512) - 1) # Escolher um número aleatório entre 0 e total_size/8 - 1 para simular perda de pacotes
        #print(f"Tamanho total do arquivo: {total_size} bytes")

        with open(file_name, 'wb') as f:
            
            while bytes_counter < total_size:
                packet, _ = self.server_socket.recvfrom(1024) # 40 bytes do header(4 bytes seq, 4 bytes tam. pacote, 32 bytes hash) + 8 bytes dos dados do pacote
                seq, bytes_length, hash = struct.unpack('!II32s', packet[:40])
                data = packet[40:40+bytes_length]

                # Debugging: Descarta pacotes pares
                if(seq == random_seq):
                    print(f"Simulando perda de pacote: {seq}")
                    continue
                    
                # Hash verification
                calculated_hash = hashlib.sha256(data).digest()
                if calculated_hash != hash:
                    print(f"Erro: Hash do pacote {seq} não confere.")
                    break
                
                f.write(data)
                bytes_counter += bytes_length
                ack = struct.pack('!I', seq)

                self.server_socket.sendto(ack, (self.host, self.port))

def main():
    # Parse command line arguments
    if len(sys.argv) != 2:
        print("Uso: python client.py <nome_do_arquivo>")
        sys.exit(1)

    file_name = sys.argv[1]
    client_instance = client()
    client_instance.request_file(file_name, debug=False) # Modo de simulação de perda ativado

if __name__ == "__main__":
    main()