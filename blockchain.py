import hashlib
import json
from datetime import datetime
from typing import List, Dict, Any


class Block:
    """Represents a single block in the blockchain"""
    
    def __init__(self, index: int, timestamp: str, transactions: List[Dict], previous_hash: str, nonce: int = 0, difficulty: int = 0):
        self.index = index
        self.timestamp = timestamp
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.difficulty = difficulty  # 0 means no PoW, >0 means PoW with that difficulty
        self.hash = self.calculate_hash()
    
    def calculate_hash(self) -> str:
        """Calculate SHA-256 hash of the block"""
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": self.transactions,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert block to dictionary for JSON serialization"""
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": self.transactions,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
            "difficulty": self.difficulty,
            "hash": self.hash
        }
    
    def mine_block(self, difficulty: int) -> int:
        """Mine the block using proof-of-work
        
        Args:
            difficulty: Number of leading zeros required in hash
            
        Returns:
            Number of hash attempts (nonce) required
        """
        target = "0" * difficulty
        attempts = 0
        
        while not self.hash.startswith(target):
            self.nonce += 1
            attempts += 1
            self.hash = self.calculate_hash()
        
        return attempts


class Blockchain:
    """Represents the blockchain"""
    
    def __init__(self, difficulty: int = 2):
        self.chain: List[Block] = []
        self.pending_transactions: List[Dict] = []
        self.difficulty = difficulty
        self.create_genesis_block()
    
    def create_genesis_block(self):
        """Create the first block in the blockchain"""
        genesis_block = Block(0, datetime.now().isoformat(), [], "0")
        self.chain.append(genesis_block)
    
    def get_latest_block(self) -> Block:
        """Get the most recent block in the chain"""
        return self.chain[-1]
    
    def add_block(self, transactions: List[Dict], mine_with_pow: bool = False):
        """Add a new block to the blockchain
        
        Args:
            transactions: List of transactions to include in the block
            mine_with_pow: Whether to use proof-of-work mining
            
        Returns:
            tuple: (new_block, attempts) where attempts is number of hashes calculated
        """
        latest_block = self.get_latest_block()
        difficulty_used = self.difficulty if mine_with_pow else 0
        new_block = Block(
            index=latest_block.index + 1,
            timestamp=datetime.now().isoformat(),
            transactions=transactions,
            previous_hash=latest_block.hash,
            difficulty=difficulty_used
        )
        
        attempts = 0
        if mine_with_pow:
            attempts = new_block.mine_block(self.difficulty)
        
        self.chain.append(new_block)
        return new_block, attempts
    
    def is_chain_valid(self) -> bool:
        """Verify the integrity of the blockchain"""
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            
            # Check if the current block's hash is correct
            if current_block.hash != current_block.calculate_hash():
                return False
            
            # Check if the previous hash matches
            if current_block.previous_hash != previous_block.hash:
                return False
        
        return True
    
    def get_all_blocks(self) -> List[Dict]:
        """Get all blocks as dictionaries"""
        return [block.to_dict() for block in self.chain]
    
    def get_block_by_index(self, index: int) -> Dict | None:
        """Get a specific block by index"""
        if 0 <= index < len(self.chain):
            return self.chain[index].to_dict()
        return None
    
    def add_transaction_to_pool(self, transaction: Dict):
        """Add a transaction to the pending transaction pool (mempool)"""
        self.pending_transactions.append(transaction)
    
    def get_pending_transactions(self) -> List[Dict]:
        """Get all pending transactions from the mempool"""
        return self.pending_transactions
    
    def mine_pending_transactions(self, use_pow: bool = False) -> tuple[Block | None, int]:
        """Mine all pending transactions into a new block
        
        Args:
            use_pow: Whether to use proof-of-work for mining
            
        Returns:
            tuple: (new_block, attempts) where attempts is number of hashes calculated
        """
        if not self.pending_transactions:
            return None, 0
        
        new_block, attempts = self.add_block(self.pending_transactions.copy(), mine_with_pow=use_pow)
        self.pending_transactions = []
        return new_block, attempts
    
    def set_difficulty(self, difficulty: int):
        """Set the mining difficulty level"""
        if difficulty < 1 or difficulty > 6:
            raise ValueError("Difficulty must be between 1 and 6")
        self.difficulty = difficulty
    
    def get_difficulty(self) -> int:
        """Get the current mining difficulty"""
        return self.difficulty
