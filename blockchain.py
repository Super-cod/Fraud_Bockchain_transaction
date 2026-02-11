
import hashlib
import json
import time
from typing import List, Dict, Any
from dataclasses import dataclass, field, asdict

class Transaction:
    def __init__(self, sender: str, receiver: str, amount: float, type: str = "PAYMENT", timestamp: float = None):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.type = type
        self.timestamp = timestamp or time.time()
        self.id = self.calculate_hash()
        self.fraud_analysis = None  # To be populated by Fraud Engine

    def calculate_hash(self) -> str:
        tx_string = f"{self.sender}{self.receiver}{self.amount}{self.timestamp}"
        return hashlib.sha256(tx_string.encode()).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tx_id": self.id,
            "sender": self.sender,
            "receiver": self.receiver,
            "amount": self.amount,
            "timestamp": self.timestamp,
            "type": self.type,
            "fraud_analysis": self.fraud_analysis
        }

@dataclass
class Block:
    index: int
    timestamp: float
    transactions: List[Dict[str, Any]]
    previous_hash: str
    nonce: int = 0
    hash: str = ""
    merkle_root: str = ""

    def calculate_hash(self) -> str:
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": self.transactions,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
            "merkle_root": self.merkle_root
        }, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()

    def mine_block(self, difficulty: int):
        target = "0" * difficulty
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()

class Blockchain:
    def __init__(self):
        self.chain: List[Block] = [self.create_genesis_block()]
        self.difficulty = 2  # Adjust for demo speed
        self.mempool: List[Transaction] = []

    def create_genesis_block(self) -> Block:
        genesis_tx = Transaction("SYSTEM", "ADMIN", 1000000, "GENESIS", 0)
        block = Block(0, time.time(), [genesis_tx.to_dict()], "0")
        block.hash = block.calculate_hash()
        return block

    def get_latest_block(self) -> Block:
        return self.chain[-1]

    def add_transaction(self, tx: Transaction):
        """Adds a validated transaction to the mempool."""
        self.mempool.append(tx)

    def mine_pending_transactions(self, miner_address: str):
        """Mines all transactions in the mempool into a new block."""
        if not self.mempool:
            return None

        # Create new block
        latest_block = self.get_latest_block()
        
        # Calculate Merkle Root (Simplified for now)
        tx_hashes = [tx.to_dict()['tx_id'] for tx in self.mempool]
        merkle_root = hashlib.sha256("".join(tx_hashes).encode()).hexdigest()
        
        new_block = Block(
            index=latest_block.index + 1,
            timestamp=time.time(),
            transactions=[tx.to_dict() for tx in self.mempool],
            previous_hash=latest_block.hash,
            merkle_root=merkle_root
        )

        # Proof of Work
        print(f"⛏️ Mining block {new_block.index} with {len(self.mempool)} transactions...")
        new_block.mine_block(self.difficulty)
        print(f"✅ Block mined! Hash: {new_block.hash}")

        # Add to chain
        self.chain.append(new_block)

        # Clear mempool
        self.mempool = []
        
        # Reward Miner (optional, adding a coinbase tx for next block)
        # self.mempool.append(Transaction("SYSTEM", miner_address, 50, "REWARD"))

        return new_block

    def is_chain_valid(self) -> bool:
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]

            if current.hash != current.calculate_hash():
                return False
            if current.previous_hash != previous.hash:
                return False
        return True

    def to_list(self) -> List[Dict[str, Any]]:
        return [asdict(block) for block in self.chain]
