import socket
import logging
import threading
import sys



class Miner:
    def __init__(self, address, port, address_b=None, port_b=None):
        logging.basicConfig(filename=f'logs/miner_{port}.log', encoding='utf-8', level=logging.DEBUG, filemode="w")
        logging.debug(f"Miner_{port}.__init__")

        self.address = address
        self.port = port
        self.miner_list = []

        # si on a les coordonnées d'un autre miner, on se connecte à lui
        if address_b and port_b:
            logging.debug(f"Miner_{self.port}.__init__ : connect to miner {address_b}:{port_b}")
            self.miner_list = [f"{address_b}:{port_b}"]
            self.connect_to_miner(address_b, port_b)
        self.start()


    def start(self):
        logging.debug(f"Miner_{self.port}.start")

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((self.address, self.port))
        sock.listen()
        try:
            while True:
                logging.debug(f"Miner_{self.port}.start : waiting for connection")
                client_socket, client_address = sock.accept()
                msg = client_socket.recv(1024).decode('utf-8')
                logging.debug(f"Miner_{self.port} receive msg : {msg}")
                t = threading.Thread(target=self.handle_message, args=(msg, client_address, client_socket))
                t.start()
        except Exception as e:
            sock.close()
        

    def handle_message(self, msg, client_address, client_socket):
        logging.debug(f"Miner_{self.port}.handle_message")
        if msg == "Hello, I'm a miner!":
            logging.debug(f"Miner_{self.port}.handle_message : miner connected from {client_address[0]}:{client_address[1]}")
            # on envoie les coordonnées du nouveau miner à tous les autres miners que l'on connait déjà
            for miner in self.miner_list:
                t = threading.Thread(target=self.send_miner_info, args=(miner[0], int(miner[1]), client_address[0], client_address[1]))
                t.start()
                # self.send_miner_info(miner[0], int(miner[1]), client_address[0], client_address[1])
            # on envoie la liste des miners au nouveau miner
            
            list_m = ','.join(self.miner_list)
            if self.miner_list == []:
                client_socket.send("None".encode("utf-8"))
            else:
                client_socket.send((','.join(self.miner_list)).encode("utf-8"))
            # on ajoute le nouveau miner à la liste des miners connus
            self.miner_list.append(f"{client_address[0]}:{client_address[1]}")
            
        elif msg[:10] == "New Miner":
            msg_split = msg.split(":")
            logging.debug(f"Miner_{self.port}.handle_message : received adress of Miner {msg_split[1]}:{msg_split[2]} from miner : {client_address[0]}:{client_address[1]}")
            self.miner_list.append(f"{msg_split[1]}:{msg_split[2]}")


    def connect_to_miner(self, address, port):
        logging.debug(f"Miner_{self.port}.connect_to_miner")

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        logging.debug(f"Miner_{self.port}.connect_to_miner : connect to {address}:{port}")
        sock.connect((address, port))

        logging.debug(f"Miner_{self.port}.connect_to_miner : send message")
        sock.send(b"Hello, I'm a miner!")

        # on reçoit la liste des miners
        data = sock.recv(1024).decode('utf-8')

        # si la liste est vide, on ne fait rien
        if data == "None":
            logging.debug(f"Miner_{self.port}.connect_to_miner : no miner")
            return
        # sinon on ajoute les miners de la liste à notre liste
        miner_list = data.split(',')
        logging.debug(f"Miner_{self.port}.connect_to_miner : {miner_list}")
        # Send the miner's information to all the miners in the list
        for miner in miner_list:
            if miner not in self.miner_list:
                miner_address, miner_port = miner.split(':')
                logging.debug(f"Miner_{self.port}.connect_to_miner : {miner_address}:{miner_port}")
                self.miner_list.append(f"{miner_address}:{miner_port}")


    def send_miner_info(self, address, port, new_miner_address, new_miner_port):
        logging.debug(f"Miner_ {self.port}.send_miner_info")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((address, port))
        message = f"New miner:{new_miner_address}:{new_miner_port}"
        sock.send(message.encode("utf-8"))
        sock.close()


if __name__ == "__main__":
    if len(sys.argv) > 2:
        miner = Miner("127.0.0.1", int(sys.argv[1]), "127.0.0.1", int(sys.argv[2]))
    else :
        miner = Miner("127.0.0.1", int(sys.argv[1]))