import socket
import struct
import os
import hashlib

TIMEOUT = 1

class server:
    def __init__(self, host='localhost', port=6363):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind((self.host, self.port))
        print(f"Servidor TCP iniciado em {self.host}:{self.port}")

    def start(self):
        print("Aguardando conexão...")

        while True:
            data, client_address = self.server_socket.recvfrom(1024)
            if not data:
                break

            print(f"Recebido: {data.decode()} de {client_address}")
            message = data.decode()
            split_message = message.split("/")
            if(split_message[0] == "GET"):
                self.send_file(split_message[1], client_address)

    def send_file(self, file_path, client_address):
        file_size = os.path.getsize(file_path)
        self.server_socket.sendto(struct.pack('!Q', file_size), client_address)

        seq = 0
        with open(file_path, 'rb') as f:
            while True:
                file = f.read(8) # arquivo inteiro quebrado em pacotes de 8 bytes
                if not file:
                    break
                    
                hash = hashlib.sha256(file).digest()
                #print(f"Enviando pacote com {len(file)} bytes")
                header = struct.pack('!II32s', seq, len(file), hash) # cabeçalho com numero de sequência, tamanho do pacote e hash
                packet = header + file # adiciona o cabeçalho no pacote

                # envia e aguarda ACK
                while True:
                    self.server_socket.sendto(packet, client_address)
                    self.server_socket.settimeout(TIMEOUT)
                    try:
                        ack_data, _ = self.server_socket.recvfrom(8)
                        ack_seq = struct.unpack('!I', ack_data[:4])[0]
                        if ack_seq == seq:
                            # Libera o timeout
                            self.server_socket.settimeout(None)
                            break  # próximo pacote
                    except socket.timeout:
                        print(f"Timeout: Ack do pacote {seq} não recebido. Reenviando...")
                        continue  # retransmite
                seq += 1
    
        print("Envio concluído.")

            
def main():
    server_instance = server()
    server_instance.start()

if __name__ == "__main__":
    main()