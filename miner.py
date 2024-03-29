import socket
import logging
import threading
import sys
from block import Block
from ThreadWithReturnValue import ThreadWithReturnValue
import datetime

class Miner:
    def __init__(self, address, port, address_b=None, port_b=None):
        logging.basicConfig(
            filename=f'logs/miner_{port}.log', encoding='utf-8', level=logging.DEBUG, filemode="w")
        logging.debug(f"{datetime.datetime.now()}:Miner_{port}.__init__")

        self.address = address
        self.port = port
        self.miner_list = []
        self.blocks = []
        self.current_block = Block()
        self.stop_mining = False
        self.event_stop = threading.Event()

        # si on a les coordonnées d'un autre miner, on se connecte à lui
        if address_b and port_b:
            logging.debug(
                f"Miner_{self.port}.__init__ : connect to miner {address_b}:{port_b}")
            self.miner_list = [f"{address_b}:{port_b}"]
            self.connect_to_miner(address_b, port_b)
        self.start()

    def start(self):
        logging.debug(f"{datetime.datetime.now()}:Miner_{self.port}.start")

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((self.address, self.port))
        sock.listen()
        try:
            while True:
                logging.debug(
                    f"Miner_{self.port}.start : waiting for connection")
                logging.debug(
                    f"Miner_{self.port}.start :I know those miners : {self.miner_list}")
                client_socket, client_address = sock.accept()
                msg = client_socket.recv(1024).decode('utf-8')
                logging.debug(f"{datetime.datetime.now()}:Miner_{self.port} receive msg : {msg}")
                t = threading.Thread(target=self.handle_message, args=(
                    msg, client_address, client_socket))
                logging.debug(f"{datetime.datetime.now()}:Miner_{self.port}.start : start thread")
                t.start()
        except Exception as e:
            logging.debug(e)
            sock.close()
            return

    def handle_message(self, msg, client_address, client_socket):
        logging.debug(f"{datetime.datetime.now()}:Miner_{self.port}.handle_message")
        if "Hello, I'm a miner!" in msg:
            port = msg.split("=")[1]
            logging.debug(
                f"Miner_{self.port}.handle_message : miner connected from {client_address[0]}:{port}")
            # on envoie les coordonnées du nouveau miner à tous les autres miners que l'on connait déjà
            for miner in self.miner_list:
                adr_miner, port_miner = miner.split(":")
                t = threading.Thread(target=self.send_miner_info, args=(
                    adr_miner, int(port_miner), client_address[0], port))
                t.start()
            # si on n'a pas de miner dans notre liste, on envoie None
            if self.miner_list == []:
                client_socket.send("None".encode("utf-8"))
            else:
                # on envoie la liste des miners au nouveau miner
                client_socket.send((','.join(self.miner_list)).encode("utf-8"))
            # on ajoute le nouveau miner à la liste des miners connus
            self.miner_list.append(f"{client_address[0]}:{port}")

        elif "New miner" in msg:
            msg_split = msg.split(":")
            logging.debug(
                f"Miner_{self.port}.handle_message : received adress of Miner {msg_split[1]}:{msg_split[2]} from miner : {client_address[0]}:{client_address[1]}")
            self.miner_list.append(f"{msg_split[1]}:{msg_split[2]}")

        elif "From Wallet" in msg:
            msg_split = msg.split(":")
            logging.debug(
                f"Miner_{self.port}.handle_message : received message \"{msg_split[-1]}\" from Wallet {msg_split[1]}:{msg_split[2]}")
            
            for miner in self.miner_list:
                adr_miner, port_miner = miner.split(":")
                self.send_info(
                    adr_miner, port_miner, "Message from:" + ":".join(msg.split(":")[1:]))
            
            transaction = msg_split[-1]
            self.add_transaction(transaction)

        elif "Message from" in msg:
            msg_split = msg.split(":")
            logging.debug(
                f"Miner_{self.port}.handle_message : transfered message \"{msg_split[-1]}\" from Wallet {msg_split[1]}:{msg_split[2]} from miner : {client_address[0]}:{client_address[1]}")
            self.add_transaction(msg_split[-1])

        elif "Block mined" in msg:
            self.event_stop.set()
            logging.debug(
                f"Miner_{self.port}.handle_message : received block mined from miner : {client_address[0]}:{client_address[1]}")
            hash_block = msg.split(":")[1]
            self.current_block.set_hash(hash_block)
            self.blocks.append(self.current_block)
            self.current_block = Block(index=len(self.blocks), previous_hash=hash_block)
            self.event_stop.clear()

    def add_transaction(self, transaction):
        logging.debug(f"{datetime.datetime.now()}:Miner_{self.port}.add_transaction")
        # ici ajouter dans le block
        full = self.current_block.add_transaction(transaction)
        if full :
            logging.debug(f"{datetime.datetime.now()}:Miner_{self.port}.add_transaction : block full")
            mine_thread = ThreadWithReturnValue(target=self.current_block.mine_block, args=(self.event_stop,))
            mine_thread.start()
            res = mine_thread.join()
            if res == True: # on as miner le block
                block_hash = self.current_block.get_hash()
                if not self.event_stop.is_set():
                    for miner in self.miner_list:
                        adr_miner, port_miner = miner.split(":")
                        self.send_info(
                            adr_miner, port_miner, "Block mined:" + block_hash)
                    self.blocks.append(self.current_block)
                    self.current_block = Block(index=len(self.blocks), previous_hash=block_hash)
                    logging.debug(f"{datetime.datetime.now()}:Miner_{self.port}.handle_message : block mined")

    def connect_to_miner(self, address, port):
        """
        Connecte le miner à un autre miner (adress port)
        et récupère sa liste de contact
        """
        logging.debug(f"{datetime.datetime.now()}:Miner_{self.port}.connect_to_miner")

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        logging.debug(
            f"Miner_{self.port}.connect_to_miner : connect to {address}:{port}")
        sock.connect((address, port))

        logging.debug(f"{datetime.datetime.now()}:Miner_{self.port}.connect_to_miner : send message")
        sock.send(f"Hello, I'm a miner! Port={self.port}".encode("utf-8"))

        # on reçoit la liste des miners
        data = sock.recv(1024).decode('utf-8')

        # si la liste est vide, on ne fait rien
        if data == "None":
            logging.debug(f"{datetime.datetime.now()}:Miner_{self.port}.connect_to_miner : no miner")
            return
        # sinon on ajoute les miners de la liste à notre liste
        miner_list = data.split(',')
        logging.debug(f"{datetime.datetime.now()}:Miner_{self.port}.connect_to_miner : {miner_list}")
        # Send the miner's information to all the miners in the list
        for miner in miner_list:
            if miner not in self.miner_list:
                miner_address, miner_port = miner.split(':')
                logging.debug(
                    f"Miner_{self.port}.connect_to_miner : {miner_address}:{miner_port}")
                self.miner_list.append(f"{miner_address}:{miner_port}")

    def send_miner_info(self, address, port, new_miner_address, new_miner_port):
        """
        Envoi les coordonnées du nouveau miner à un autre miner (address port)
        """
        logging.debug(f"{datetime.datetime.now()}:Miner_{self.port}.send_miner_info")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        logging.debug(
            f"Miner_{self.port}.send_miner_info : connect to {address}:{port}")
        sock.connect((address, port))
        message = f"New miner:{new_miner_address}:{new_miner_port}"
        logging.debug(
            f"Miner_{self.port}.send_miner_info : send message : {message} to {address}:{port}")
        sock.send(message.encode("utf-8"))
        sock.close()

    def send_info(self, address, port, msg):
        logging.debug(f"{datetime.datetime.now()}:Miner_{self.port}.send_wallet_info")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        logging.debug(
            f"Miner_{self.port}.send_wallet_info : connect to {address}:{port}")
        sock.connect((address, int(port)))
        message = f"{msg}"
        logging.debug(f"{datetime.datetime.now()}:Miner_{self.port}.send_wallet_info : {msg}")
        sock.send(message.encode("utf-8"))
        sock.close()


if __name__ == "__main__":
    if len(sys.argv) > 2:
        miner = Miner("127.0.0.1", int(
            sys.argv[1]), "127.0.0.1", int(sys.argv[2]))
    else:
        miner = Miner("127.0.0.1", int(sys.argv[1]))
