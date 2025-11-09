import hashlib
import json
from datetime import datetime
from typing import List, Dict, Any


class Block:
    def __init__(self, index: int, timestamp: str, transactions: List[Dict], previous_hash: str, nonce: int = 0, difficulty: int = 0):
        self.index = index
        self.timestamp = timestamp
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.difficulty = difficulty  # 0 means no PoW, >0 means PoW with that difficulty
        self.hash = self.calculate_hash()
    
    def calculate_hash(self) -> str:
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": self.transactions,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def to_dict(self) -> Dict[str, Any]:

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

        genesis_block = Block(0, datetime.now().isoformat(), [], "0")
        self.chain.append(genesis_block)
    
    def get_latest_block(self) -> Block:

        return self.chain[-1]
    
    def add_block(self, transactions: List[Dict], mine_with_pow: bool = False):

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
    
    def is_chain_valid(self, check_pow: bool = True) -> tuple[bool, str]:

        # Validate genesis block
        if len(self.chain) > 0:
            genesis = self.chain[0]
            if genesis.hash != genesis.calculate_hash():
                return False, "Genesis block: Hash mismatch (block has been tampered with)"
            if genesis.previous_hash != "0":
                return False, "Genesis block: Invalid previous hash (should be '0')"
            if genesis.index != 0:
                return False, "Genesis block: Invalid index (should be 0)"
        
        # Validate remaining blocks
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            
            # Check if the current block hash is correct
            if current_block.hash != current_block.calculate_hash():
                return False, f"Block #{i}: Hash mismatch (block has been tampered with)"
            
            # Check if the previous hash matches
            if current_block.previous_hash != previous_block.hash:
                return False, f"Block #{i}: Previous hash doesn't match (chain link broken)"
            
            # Check proof of work if enabled
            if check_pow and current_block.difficulty > 0:
                required_prefix = "0" * current_block.difficulty
                if not current_block.hash.startswith(required_prefix):
                    return False, f"Block #{i}: Proof-of-work requirement not met (difficulty {current_block.difficulty})"
        
        return True, "Blockchain is valid"
    
    def get_chain_stats(self) -> Dict[str, Any]:
        total_blocks = len(self.chain)
        pow_blocks = sum(1 for block in self.chain if block.difficulty > 0)
        total_transactions = sum(len(block.transactions) for block in self.chain)
        
        return {
            "total_blocks": total_blocks,
            "pow_blocks": pow_blocks,
            "simple_blocks": total_blocks - pow_blocks,
            "total_transactions": total_transactions,
            "current_difficulty": self.difficulty
        }
    
    def get_all_blocks(self) -> List[Dict]:
        return [block.to_dict() for block in self.chain]
    
    def get_block_by_index(self, index: int) -> Dict | None:
        if 0 <= index < len(self.chain):
            return self.chain[index].to_dict()
        return None
    
    def add_transaction_to_pool(self, transaction: Dict):
        self.pending_transactions.append(transaction)
    
    def get_pending_transactions(self) -> List[Dict]:
        return self.pending_transactions
    
    def mine_pending_transactions(self, use_pow: bool = False) -> tuple[Block | None, int]:

        if not self.pending_transactions:
            return None, 0
        
        new_block, attempts = self.add_block(self.pending_transactions.copy(), mine_with_pow=use_pow)
        self.pending_transactions = []
        return new_block, attempts
    
    def set_difficulty(self, difficulty: int):
        if difficulty < 1 or difficulty > 6:
            raise ValueError("Difficulty must be between 1 and 6")
        self.difficulty = difficulty
    
    def get_difficulty(self) -> int:
        return self.difficulty
    
    def get_user_transactions(self, username: str) -> List[Dict]:
        user_transactions = []
        
        for block in self.chain:
            for tx in block.transactions:
                if tx.get('sender') == username or tx.get('receiver') == username:
                    # Add block information to transaction
                    tx_with_block = tx.copy()
                    tx_with_block['block_index'] = block.index
                    tx_with_block['block_hash'] = block.hash
                    tx_with_block['block_timestamp'] = block.timestamp
                    user_transactions.append(tx_with_block)
        
        return user_transactions
    
    def export_to_json(self, include_metadata: bool = True) -> str:

        export_data = {
            "blocks": self.get_all_blocks(),
        }
        
        if include_metadata:
            is_valid, message = self.is_chain_valid(check_pow=True)
            stats = self.get_chain_stats()
            
            export_data["metadata"] = {
                "export_timestamp": datetime.now().isoformat(),
                "is_valid": is_valid,
                "validation_message": message,
                "statistics": stats
            }
        
        return json.dumps(export_data, indent=2)
    
    def export_block_range(self, start_index: int, end_index: int) -> str:

        if start_index < 0 or end_index >= len(self.chain) or start_index > end_index:
            raise ValueError("Invalid block range")
        
        blocks = [self.chain[i].to_dict() for i in range(start_index, end_index + 1)]
        
        export_data = {
            "blocks": blocks,
            "metadata": {
                "export_timestamp": datetime.now().isoformat(),
                "block_range": f"{start_index}-{end_index}",
                "total_blocks": len(blocks)
            }
        }
        
        return json.dumps(export_data, indent=2)
