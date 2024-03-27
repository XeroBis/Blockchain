import socket
import sys
import logging
import threading


class Wallet:
    def __init__(self, address, port, miner_port):
        logging.basicConfig(
            filename=f'logs/wallet_{port}.log', encoding='utf-8', level=logging.DEBUG, filemode="w")
        logging.debug(f"Wallet_{port}.__init__")

        self.address = address
        self.port = port
        self.connected_miner = ("127.0.0.1", int(miner_port))

        self.public_key = "123"

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
                message = input("Montant : ")
                port_wallet = input("Port du wallet : ")
                message = f"{self.port}={message}={port_wallet}"
                t = threading.Thread(target=self.send_message_to_miner, args=(
                    message, self.connected_miner[0], self.connected_miner[1]))
                logging.debug(
                    f"Wallet_{self.port}.start : start thread send message")
                t.start()

        except Exception as e:
            logging.debug(e)
            sock.close()
            return

    def send_message_to_miner(self, message, adress, port):
        logging.debug(f"Wallet_{self.port}.send_message_to_miner")
        try:
            message = f"From Wallet:{self.address}:{self.port}:" + message
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((adress, port))
            sock.sendall(message.encode('utf-8'))
            logging.debug(
                f"Message \"{message}\" sent to miner at {adress}:{port}")
            sock.close()
        except Exception as e:
            logging.debug(e)
            return


if __name__ == "__main__":
    # Code to instantiate and use the wallet
    wallet = Wallet("127.0.0.1", int(sys.argv[1]), int(
        sys.argv[2]))  # Example port and address
    # Connect to a miner, send a message, etc.
