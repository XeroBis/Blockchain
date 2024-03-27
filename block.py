import hashlib
import time
import threading
import logging

class Block:
    def __init__(self, index=0, previous_hash=None, transactions=None):
        logging.debug(f"block_{index}.__init__")
        self.index = index
        if transactions is not None:
            self.transactions = transactions
        else:
            self.transactions = []
        self.previous_hash = previous_hash
        self.timestamp = time.time()
        self.nonce = 0
        self.size = 5
        self.hash = ""
    
    def add_transaction(self, transaction):
        self.transactions.append(transaction)
        logging.debug(f"Block_{self.index}.add_transaction : {transaction}")
        return self.size == len(self.transactions)

    def compute_hash(self):
        block_string = f"{self.index}{self.transactions}{self.previous_hash}{self.timestamp}{self.nonce}"
        return hashlib.sha256(block_string.encode()).hexdigest()

    # Proof of Work
    # difficulty is the number of leading zeroes that must be in the hash
    def mine_block(self, stop_event, difficulty=6):
        logging.debug(f"Block_{self.index}.mine_block")
        self.nonce = 0
        computed_hash = self.compute_hash()
        while not computed_hash.startswith('0' * difficulty):
            if stop_event.is_set():
                logging.debug(f"Block_{self.index}.mine_block stopped")
                return False
            self.nonce += 1
            computed_hash = self.compute_hash()
        logging.debug(f"Block_{self.index}.mine_block hash found")
        self.hash = computed_hash
        return True
    
    def get_hash(self):
        logging.debug(f"Block_{self.index}.get_hash : {self.hash}")
        return self.hash
    
    def set_hash(self, hash):
        # in case another miner has already mined the block
        self.hash = hash
        logging.debug(f"Block_{self.index}.set_hash : {hash}")