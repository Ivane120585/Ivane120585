#!/usr/bin/env python3
"""
ScrollCoin Mainnet API
Sacred cryptocurrency API for ScrollWrappedCodex™ ecosystem
"""

import json
import csv
import datetime
import hashlib
import uuid
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

@dataclass
class ScrollCoinTransaction:
    """ScrollCoin transaction data structure"""
    timestamp: str
    sender: str
    receiver: str
    amount: float
    memo: str
    seal_level: int
    transaction_hash: str
    status: str
    flame_verified: bool

@dataclass
class ScrollCoinWallet:
    """ScrollCoin wallet data structure"""
    builder_id: str
    flame_balance: float
    seal_required: int
    auto_tithe_percentage: float
    wallet_address: str
    flame_level: int
    last_transaction: Optional[str]
    transaction_count: int
    total_received: float
    total_sent: float
    tithe_total: float
    wallet_status: str
    security_level: int
    created_at: str
    updated_at: str

class ScrollCoinAPI:
    """Sacred ScrollCoin API for flame-verified transactions"""
    
    def __init__(self, data_dir: str = "scrollcoin_mainnet"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # File paths
        self.wallet_file = self.data_dir / "wallets.json"
        self.transaction_file = self.data_dir / "scrollcoin_txn_log.csv"
        self.config_file = self.data_dir / "scrollcoin_config.json"
        
        # Initialize data structures
        self.wallets: Dict[str, ScrollCoinWallet] = {}
        self.transactions: List[ScrollCoinTransaction] = []
        
        # Load existing data
        self._load_wallets()
        self._load_transactions()
        self._load_config()
    
    def _load_wallets(self) -> None:
        """Load wallet data from JSON file"""
        if self.wallet_file.exists():
            try:
                with open(self.wallet_file, 'r') as f:
                    wallet_data = json.load(f)
                    for wallet_id, data in wallet_data.items():
                        self.wallets[wallet_id] = ScrollCoinWallet(**data)
            except Exception as e:
                print(f"Error loading wallets: {e}")
    
    def _save_wallets(self) -> None:
        """Save wallet data to JSON file"""
        wallet_data = {}
        for wallet_id, wallet in self.wallets.items():
            wallet_data[wallet_id] = wallet.__dict__
        
        with open(self.wallet_file, 'w') as f:
            json.dump(wallet_data, f, indent=2)
    
    def _load_transactions(self) -> None:
        """Load transaction data from CSV file"""
        if self.transaction_file.exists():
            try:
                with open(self.transaction_file, 'r') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        transaction = ScrollCoinTransaction(
                            timestamp=row['timestamp'],
                            sender=row['sender'],
                            receiver=row['receiver'],
                            amount=float(row['amount']),
                            memo=row['memo'],
                            seal_level=int(row['seal_level']),
                            transaction_hash=row['transaction_hash'],
                            status=row['status'],
                            flame_verified=row['flame_verified'].lower() == 'true'
                        )
                        self.transactions.append(transaction)
            except Exception as e:
                print(f"Error loading transactions: {e}")
    
    def _save_transaction(self, transaction: ScrollCoinTransaction) -> None:
        """Save transaction to CSV file"""
        with open(self.transaction_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                transaction.timestamp,
                transaction.sender,
                transaction.receiver,
                transaction.amount,
                transaction.memo,
                transaction.seal_level,
                transaction.transaction_hash,
                transaction.status,
                transaction.flame_verified
            ])
    
    def _load_config(self) -> None:
        """Load API configuration"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
            except Exception as e:
                print(f"Error loading config: {e}")
                self.config = self._get_default_config()
        else:
            self.config = self._get_default_config()
            self._save_config()
    
    def _save_config(self) -> None:
        """Save API configuration"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def _get_default_config(self) -> Dict:
        """Get default API configuration"""
        return {
            "network_name": "ScrollCoin Mainnet",
            "flame_required": 3,
            "transaction_fee": 0.001,
            "tithe_percentage": 5.0,
            "daily_limit": {
                1: 100.0,
                2: 500.0,
                3: 1000.0,
                4: 5000.0,
                5: 10000.0
            },
            "sacred_funds": {
                "development": "scroll_sacred_dev_fund_001",
                "council": "scroll_seercircle_council_001",
                "verification": "scroll_flame_verification_001"
            }
        }
    
    def _generate_transaction_hash(self, sender: str, receiver: str, amount: float, timestamp: str) -> str:
        """Generate unique transaction hash"""
        data = f"{sender}:{receiver}:{amount}:{timestamp}"
        return f"scroll_txn_{hashlib.md5(data.encode()).hexdigest()[:16]}"
    
    def _verify_flame_permission(self, sender_id: str, amount: float, seal_level: int) -> Tuple[bool, str]:
        """Verify flame permission for transaction"""
        if sender_id not in self.wallets:
            return False, "Wallet not found"
        
        wallet = self.wallets[sender_id]
        
        # Check wallet status
        if wallet.wallet_status != "active":
            return False, f"Wallet status: {wallet.wallet_status}"
        
        # Check flame level requirement
        if wallet.flame_level < self.config["flame_required"]:
            return False, f"Insufficient flame level. Required: {self.config['flame_required']}, Current: {wallet.flame_level}"
        
        # Check seal level requirement
        if seal_level > wallet.flame_level:
            return False, f"Insufficient seal level. Required: {seal_level}, Current: {wallet.flame_level}"
        
        # Check balance
        if wallet.flame_balance < amount:
            return False, f"Insufficient balance. Required: {amount}, Available: {wallet.flame_balance}"
        
        # Check daily limit
        daily_limit = self.config["daily_limit"].get(wallet.flame_level, 100.0)
        today_transactions = [
            t for t in self.transactions 
            if t.sender == sender_id and 
            t.timestamp.startswith(datetime.datetime.now().strftime("%Y-%m-%d"))
        ]
        daily_total = sum(t.amount for t in today_transactions)
        
        if daily_total + amount > daily_limit:
            return False, f"Daily limit exceeded. Limit: {daily_limit}, Used: {daily_total}, Requested: {amount}"
        
        return True, "Flame permission verified"
    
    def create_wallet(self, builder_id: str, flame_level: int = 1) -> Dict:
        """Create new ScrollCoin wallet"""
        if builder_id in self.wallets:
            return {"success": False, "error": "Wallet already exists"}
        
        # Generate wallet address
        wallet_address = f"scroll_{uuid.uuid4().hex[:4]}_{uuid.uuid4().hex[:4]}_{uuid.uuid4().hex[:4]}_{uuid.uuid4().hex[:4]}"
        
        # Create wallet
        wallet = ScrollCoinWallet(
            builder_id=builder_id,
            flame_balance=0.0,
            seal_required=flame_level,
            auto_tithe_percentage=5.0,
            wallet_address=wallet_address,
            flame_level=flame_level,
            last_transaction=None,
            transaction_count=0,
            total_received=0.0,
            total_sent=0.0,
            tithe_total=0.0,
            wallet_status="pending",
            security_level=1,
            created_at=datetime.datetime.now().isoformat(),
            updated_at=datetime.datetime.now().isoformat()
        )
        
        self.wallets[builder_id] = wallet
        self._save_wallets()
        
        return {
            "success": True,
            "wallet": wallet.__dict__,
            "message": "Wallet created successfully"
        }
    
    def get_balance(self, builder_id: str) -> Dict:
        """Get wallet balance"""
        if builder_id not in self.wallets:
            return {"success": False, "error": "Wallet not found"}
        
        wallet = self.wallets[builder_id]
        return {
            "success": True,
            "builder_id": builder_id,
            "flame_balance": wallet.flame_balance,
            "flame_level": wallet.flame_level,
            "wallet_status": wallet.wallet_status,
            "last_transaction": wallet.last_transaction
        }
    
    def send_tokens(self, sender_id: str, receiver_id: str, amount: float, memo: str, seal_level: int) -> Dict:
        """Send ScrollCoin tokens"""
        # Verify flame permission
        permission_ok, error_msg = self._verify_flame_permission(sender_id, amount, seal_level)
        if not permission_ok:
            return {"success": False, "error": error_msg}
        
        # Check if receiver exists (for non-sacred funds)
        if not receiver_id.startswith("scroll_") and receiver_id not in self.wallets:
            return {"success": False, "error": "Receiver wallet not found"}
        
        # Create transaction
        timestamp = datetime.datetime.now().isoformat()
        transaction_hash = self._generate_transaction_hash(sender_id, receiver_id, amount, timestamp)
        
        transaction = ScrollCoinTransaction(
            timestamp=timestamp,
            sender=sender_id,
            receiver=receiver_id,
            amount=amount,
            memo=memo,
            seal_level=seal_level,
            transaction_hash=transaction_hash,
            status="completed",
            flame_verified=True
        )
        
        # Update sender wallet
        sender_wallet = self.wallets[sender_id]
        sender_wallet.flame_balance -= amount
        sender_wallet.total_sent += amount
        sender_wallet.transaction_count += 1
        sender_wallet.last_transaction = timestamp
        sender_wallet.updated_at = timestamp
        
        # Calculate and apply tithe
        tithe_amount = amount * (sender_wallet.auto_tithe_percentage / 100.0)
        if tithe_amount > 0:
            tithe_transaction = ScrollCoinTransaction(
                timestamp=timestamp,
                sender=sender_id,
                receiver=self.config["sacred_funds"]["development"],
                amount=tithe_amount,
                memo=f"Auto tithe from {memo}",
                seal_level=seal_level,
                transaction_hash=f"{transaction_hash}_tithe",
                status="completed",
                flame_verified=True
            )
            sender_wallet.tithe_total += tithe_amount
            sender_wallet.flame_balance -= tithe_amount
            self.transactions.append(tithe_transaction)
            self._save_transaction(tithe_transaction)
        
        # Update receiver wallet (if it's a regular wallet)
        if receiver_id in self.wallets:
            receiver_wallet = self.wallets[receiver_id]
            receiver_wallet.flame_balance += amount
            receiver_wallet.total_received += amount
            receiver_wallet.transaction_count += 1
            receiver_wallet.last_transaction = timestamp
            receiver_wallet.updated_at = timestamp
        
        # Save transaction and update wallets
        self.transactions.append(transaction)
        self._save_transaction(transaction)
        self._save_wallets()
        
        return {
            "success": True,
            "transaction_hash": transaction_hash,
            "amount": amount,
            "tithe_amount": tithe_amount,
            "sender_balance": sender_wallet.flame_balance,
            "message": "Transaction completed successfully"
        }
    
    def get_transaction_history(self, builder_id: str, limit: int = 50) -> Dict:
        """Get transaction history for wallet"""
        if builder_id not in self.wallets:
            return {"success": False, "error": "Wallet not found"}
        
        # Filter transactions for this wallet
        wallet_transactions = [
            t for t in self.transactions 
            if t.sender == builder_id or t.receiver == builder_id
        ]
        
        # Sort by timestamp (newest first) and limit
        wallet_transactions.sort(key=lambda x: x.timestamp, reverse=True)
        wallet_transactions = wallet_transactions[:limit]
        
        return {
            "success": True,
            "builder_id": builder_id,
            "transactions": [t.__dict__ for t in wallet_transactions],
            "total_count": len(wallet_transactions)
        }
    
    def update_flame_level(self, builder_id: str, new_flame_level: int) -> Dict:
        """Update wallet flame level"""
        if builder_id not in self.wallets:
            return {"success": False, "error": "Wallet not found"}
        
        wallet = self.wallets[builder_id]
        old_level = wallet.flame_level
        wallet.flame_level = new_flame_level
        wallet.updated_at = datetime.datetime.now().isoformat()
        
        self._save_wallets()
        
        return {
            "success": True,
            "builder_id": builder_id,
            "old_flame_level": old_level,
            "new_flame_level": new_flame_level,
            "message": "Flame level updated successfully"
        }
    
    def set_auto_tithe(self, builder_id: str, percentage: float) -> Dict:
        """Set auto tithe percentage"""
        if builder_id not in self.wallets:
            return {"success": False, "error": "Wallet not found"}
        
        if percentage < 0 or percentage > 100:
            return {"success": False, "error": "Tithe percentage must be between 0 and 100"}
        
        wallet = self.wallets[builder_id]
        wallet.auto_tithe_percentage = percentage
        wallet.updated_at = datetime.datetime.now().isoformat()
        
        self._save_wallets()
        
        return {
            "success": True,
            "builder_id": builder_id,
            "auto_tithe_percentage": percentage,
            "message": "Auto tithe percentage updated successfully"
        }
    
    def get_network_stats(self) -> Dict:
        """Get network statistics"""
        total_wallets = len(self.wallets)
        total_transactions = len(self.transactions)
        total_volume = sum(t.amount for t in self.transactions if t.status == "completed")
        
        # Calculate flame level distribution
        flame_distribution = {}
        for wallet in self.wallets.values():
            level = wallet.flame_level
            flame_distribution[level] = flame_distribution.get(level, 0) + 1
        
        return {
            "success": True,
            "network_name": self.config["network_name"],
            "total_wallets": total_wallets,
            "total_transactions": total_transactions,
            "total_volume": total_volume,
            "flame_distribution": flame_distribution,
            "active_wallets": len([w for w in self.wallets.values() if w.wallet_status == "active"])
        }

# Example usage and testing
if __name__ == "__main__":
    # Initialize API
    api = ScrollCoinAPI()
    
    # Create test wallets
    print("Creating test wallets...")
    api.create_wallet("scrollbuilder_2471", flame_level=4)
    api.create_wallet("scrollbuilder_1567", flame_level=3)
    
    # Get balance
    balance = api.get_balance("scrollbuilder_2471")
    print(f"Balance: {balance}")
    
    # Send tokens
    result = api.send_tokens(
        sender_id="scrollbuilder_2471",
        receiver_id="scrollbuilder_1567",
        amount=50.0,
        memo="Test transaction",
        seal_level=3
    )
    print(f"Transaction result: {result}")
    
    # Get network stats
    stats = api.get_network_stats()
    print(f"Network stats: {stats}") 