import hashlib
import json
from datetime import datetime
from typing import List, Dict, Any


class Block:
    """Represents a single block in the blockchain"""
    
    def __init__(self, index: int, timestamp: str, transactions: List[Dict], previous_hash: str):
        self.index = index
        self.timestamp = timestamp
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()
    
    def calculate_hash(self) -> str:
        """Calculate SHA-256 hash of the block"""
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": self.transactions,
            "previous_hash": self.previous_hash
        }, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert block to dictionary for JSON serialization"""
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": self.transactions,
            "previous_hash": self.previous_hash,
            "hash": self.hash
        }


class Blockchain:
    """Represents the blockchain"""
    
    def __init__(self):
        self.chain: List[Block] = []
        self.pending_transactions: List[Dict] = []
        self.create_genesis_block()
    
    def create_genesis_block(self):
        """Create the first block in the blockchain"""
        genesis_block = Block(0, datetime.now().isoformat(), [], "0")
        self.chain.append(genesis_block)
    
    def get_latest_block(self) -> Block:
        """Get the most recent block in the chain"""
        return self.chain[-1]
    
    def add_block(self, transactions: List[Dict]):
        """Add a new block to the blockchain"""
        latest_block = self.get_latest_block()
        new_block = Block(
            index=latest_block.index + 1,
            timestamp=datetime.now().isoformat(),
            transactions=transactions,
            previous_hash=latest_block.hash
        )
        self.chain.append(new_block)
        return new_block
    
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
    
    def mine_pending_transactions(self) -> Block | None:
        """Mine all pending transactions into a new block"""
        if not self.pending_transactions:
            return None
        
        new_block = self.add_block(self.pending_transactions.copy())
        self.pending_transactions = []
        return new_block
