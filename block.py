import hashlib
import time

class Block:
    def __init__(self, index, transactions, previous_hash):
        self.index = index
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.timestamp = time.time()
        self.nonce = 0

    def compute_hash(self):
        block_string = f"{self.index}{self.transactions}{self.previous_hash}{self.timestamp}{self.nonce}"
        return hashlib.sha256(block_string.encode()).hexdigest()

# Proof of Work
# difficulty is the number of leading zeroes that must be in the hash
def proof_of_work(block, difficulty=4):
    block.nonce = 0
    computed_hash = block.compute_hash()
    while not computed_hash.startswith('0' * difficulty):
        block.nonce += 1
        computed_hash = block.compute_hash()
    return computed_hash

# Example Usage
transactions = ['Alice sends 1 BTC to Bob', 'Charlie sends 2 BTC to Dave']
genesis_block = Block(0, transactions, "0")
print("Mining genesis block...")
proof_of_work(genesis_block)
print(f"Genesis Block Hash: {genesis_block.compute_hash()}")
