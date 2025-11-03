from typing import Dict, List
from digital_signature import DigitalSignature


class UserWallet:
    """Manages user wallets with public/private keys and balances"""
    
    def __init__(self, username: str):
        self.username = username
        private_key, public_key = DigitalSignature.generate_key_pair()
        self.private_key = private_key
        self.public_key = public_key
        self.balance = 100.0  # Initial balance for each user
    
    def to_dict(self) -> Dict:
        """Convert wallet to dictionary"""
        return {
            "username": self.username,
            "public_key": self.public_key,
            "private_key": self.private_key,
            "balance": self.balance
        }


class WalletManager:
    """Manages all user wallets"""
    
    def __init__(self):
        self.wallets: Dict[str, UserWallet] = {}
    
    def create_wallet(self, username: str) -> UserWallet:
        """Create a new wallet for a user"""
        if username in self.wallets:
            raise ValueError(f"User {username} already exists")
        
        wallet = UserWallet(username)
        self.wallets[username] = wallet
        return wallet
    
    def get_wallet(self, username: str) -> UserWallet:
        """Get a user's wallet"""
        if username not in self.wallets:
            raise ValueError(f"User {username} does not exist")
        return self.wallets[username]
    
    def wallet_exists(self, username: str) -> bool:
        """Check if a wallet exists for a user"""
        return username in self.wallets
    
    def get_all_users(self) -> List[str]:
        """Get list of all usernames"""
        return list(self.wallets.keys())
    
    def update_balances(self, sender: str, receiver: str, amount: float):
        """Update balances after a transaction"""
        if sender not in self.wallets or receiver not in self.wallets:
            raise ValueError("Sender or receiver does not exist")
        
        if self.wallets[sender].balance < amount:
            raise ValueError("Insufficient balance")
        
        self.wallets[sender].balance -= amount
        self.wallets[receiver].balance += amount
    
    def get_balance(self, username: str) -> float:
        """Get a user's balance"""
        if username not in self.wallets:
            return 0.0
        return self.wallets[username].balance
