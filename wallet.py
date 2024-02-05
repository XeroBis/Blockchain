import socket
import sys
import logging

class Wallet:
    def __init__(self, address, port, miner_port):
        logging.basicConfig(filename=f'logs/wallet_{port}.log', encoding='utf-8', level=logging.DEBUG, filemode="w")
        logging.debug(f"Wallet_{port}.__init__")
        
        self.address = address
        self.port = port
        self.connected_miner = ("127.0.0.1", int(miner_port))
        
        self.start()
        # self.connect_to_miner("127.0.0.1", miner_port)
        # self.send_message_to_miner(message)
        # self.receive_response()

    def start(self):
        logging.debug(f"Wallet_{self.port}.start")

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((self.address, self.port))
        try:
            while True:
                message = input("Transaction : ")
                self.connect_to_miner(self.connected_miner[0], self.connected_miner[1])
                self.send_message_to_miner(message)
                self.receive_response()
        except Exception as e:
            logging.debug(e)
            sock.close()
            return


    def connect_to_miner(self, miner_address, miner_port):
        # Connection a un miner
        logging.debug(f"Attempting connection to Miner {miner_address}:{miner_port}")
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((miner_address, miner_port))
            logging.debug(f"Successfully connected to {miner_address} : {miner_port}")
            self.connected_miner = (miner_address, miner_port)
        except Exception as e:
            logging.debug(e)
            self.connected_miner = None
        

    def send_message_to_miner(self, message):
        # Envoi de message à un miner
        if not self.connected_miner:
            logging.debug("Attempt to send message but no miner is connected")
            return
        
        miner_address, miner_port = self.connected_miner
        
        try:
            message = f"From Wallet:{self.address}:{self.port}:" + message
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Connection au miner
            sock.connect((miner_address, miner_port))
            # Envoi du message
            sock.sendall(message.encode('utf-8'))
            logging.debug(f"Message \"{message}\" sent to miner at {miner_address}:{miner_port}")
            sock.close()
            
        except Exception as e:
            logging.debug(e)
            
        

    def receive_response(self):
        # Handle responses received from the miner
        logging.debug(f"Wallet_{self.port} waiting for response...")

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.listen()
        try:
            while True:
                client_socket, client_address = sock.accept()
                msg = client_socket.recv(1024).decode('utf-8')
                logging.debug(f"Recieved : {msg}")
        except Exception as e:
            logging.debug(e)
            sock.close()

    # Additional methods as needed for wallet functionality

if __name__ == "__main__":
    # Code to instantiate and use the wallet
    wallet = Wallet("127.0.0.1", int(sys.argv[1]), int(sys.argv[2]))  # Example port and address
    # Connect to a miner, send a message, etc.
