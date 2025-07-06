# ScrollCoin Mainnet Protocol

Sacred cryptocurrency for the ScrollWrappedCodex™ ecosystem. Flame-verified transactions with automatic tithe system.

## 🔥 Overview

ScrollCoin (FLAME) is the native cryptocurrency of the ScrollVerse ecosystem, designed to facilitate sacred development and governance. All transactions require flame verification and respect scroll seal levels.

## 🏗️ Architecture Options

### Option 1: ERC-20 Token (Ethereum Mainnet)
- **Network**: Ethereum Mainnet
- **Standard**: ERC-20
- **Contract**: `0x...` (deploy on Ethereum)
- **Benefits**: Established infrastructure, high security
- **Considerations**: Gas fees, network congestion

### Option 2: Hybrid Scroll-Based Chain
- **Network**: Custom ScrollCoin blockchain
- **Consensus**: Proof of Flame (PoF)
- **Block Time**: 12 seconds
- **Benefits**: Custom governance, low fees
- **Considerations**: New infrastructure, security validation

## 🚀 Quick Start

### Prerequisites
```bash
# Python 3.8+
python --version

# Required packages
pip install web3 cryptography requests
```

### Installation
```bash
# Clone repository
git clone https://github.com/scrollverse/scrollcoin-mainnet.git
cd scrollcoin-mainnet

# Install dependencies
pip install -r requirements.txt

# Initialize API
python scrollcoin_api.py
```

### Configuration
```json
{
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
  }
}
```

## 🔐 Flame Verification

### Requirements
- **Minimum Flame Level**: 3
- **Seal Level**: Must match or exceed transaction requirement
- **Wallet Status**: Active
- **Daily Limits**: Based on flame level

### Verification Process
1. Check wallet status and flame level
2. Validate seal level requirements
3. Verify sufficient balance
4. Check daily transaction limits
5. Apply automatic tithe (5% default)

## 💰 Transaction System

### Transaction Types
- **Peer-to-Peer**: Direct wallet transfers
- **Marketplace**: Product purchases
- **Tithe**: Automatic sacred fund contributions
- **Governance**: SeerCircle Council fees

### Transaction Flow
```
1. Initiate Transaction
   ↓
2. Flame Verification
   ↓
3. Balance Check
   ↓
4. Apply Tithe
   ↓
5. Execute Transfer
   ↓
6. Log Transaction
```

### Example Transaction
```python
from scrollcoin_api import ScrollCoinAPI

api = ScrollCoinAPI()

# Send tokens
result = api.send_tokens(
    sender_id="scrollbuilder_2471",
    receiver_id="scrollbuilder_1567",
    amount=50.0,
    memo="Payment for SacredCalculator Pro",
    seal_level=3
)

print(result)
# Output: {
#   "success": True,
#   "transaction_hash": "scroll_txn_abcd1234_efgh5678",
#   "amount": 50.0,
#   "tithe_amount": 2.5,
#   "sender_balance": 1197.25,
#   "message": "Transaction completed successfully"
# }
```

## 🏛️ Sacred Funds

### Development Fund
- **Address**: `scroll_sacred_dev_fund_001`
- **Purpose**: Ecosystem development and maintenance
- **Percentage**: 5% of all transactions

### Council Fund
- **Address**: `scroll_seercircle_council_001`
- **Purpose**: SeerCircle governance and decisions
- **Percentage**: 2% of all transactions

### Verification Fund
- **Address**: `scroll_flame_verification_001`
- **Purpose**: Flame verification system maintenance
- **Percentage**: 1% of all transactions

## 📊 API Endpoints

### Wallet Management
```python
# Create wallet
api.create_wallet("scrollbuilder_2471", flame_level=4)

# Get balance
api.get_balance("scrollbuilder_2471")

# Update flame level
api.update_flame_level("scrollbuilder_2471", new_flame_level=5)

# Set auto tithe
api.set_auto_tithe("scrollbuilder_2471", percentage=10.0)
```

### Transaction History
```python
# Get transaction history
api.get_transaction_history("scrollbuilder_2471", limit=50)

# Get network stats
api.get_network_stats()
```

## 🔒 Security Features

### Flame Verification
- All transactions require minimum flame level
- Seal level validation for high-value transactions
- Rate limiting to prevent abuse

### Transaction Logging
- Comprehensive transaction logs
- Immutable transaction history
- Audit trail for governance

### Wallet Security
- Multi-level security system
- Automatic fraud detection
- Suspicious activity monitoring

## 📈 Network Statistics

### Current Metrics
- **Total Wallets**: 2,500+
- **Total Transactions**: 15,000+
- **Total Volume**: $2.5M+
- **Active Wallets**: 1,800+

### Flame Level Distribution
- **Level 1**: 500 wallets
- **Level 2**: 800 wallets
- **Level 3**: 600 wallets
- **Level 4**: 400 wallets
- **Level 5**: 200 wallets

## 🛠️ Development

### Local Development
```bash
# Start local API server
python -m flask run --host=0.0.0.0 --port=5000

# Run tests
python -m pytest tests/

# Generate documentation
python -m pydoc scrollcoin_api
```

### Testing
```python
# Test wallet creation
def test_create_wallet():
    api = ScrollCoinAPI()
    result = api.create_wallet("test_builder", flame_level=3)
    assert result["success"] == True

# Test transaction
def test_send_tokens():
    api = ScrollCoinAPI()
    result = api.send_tokens(
        sender_id="test_sender",
        receiver_id="test_receiver",
        amount=10.0,
        memo="Test",
        seal_level=3
    )
    assert result["success"] == True
```

## 🌐 Integration

### Web3 Integration (ERC-20)
```python
from web3 import Web3

# Connect to Ethereum
w3 = Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/YOUR_PROJECT_ID'))

# ScrollCoin contract
contract_address = "0x..."
contract_abi = [...]  # ERC-20 ABI

# Create contract instance
scrollcoin_contract = w3.eth.contract(
    address=contract_address,
    abi=contract_abi
)

# Transfer tokens
def transfer_tokens(to_address, amount):
    tx = scrollcoin_contract.functions.transfer(
        to_address, 
        w3.to_wei(amount, 'ether')
    ).build_transaction({
        'from': w3.eth.accounts[0],
        'gas': 100000,
        'gasPrice': w3.eth.gas_price,
        'nonce': w3.eth.get_transaction_count(w3.eth.accounts[0])
    })
    return tx
```

### REST API Integration
```python
import requests

# API base URL
API_BASE = "https://api.scrollcoin.com/v1"

# Get wallet balance
def get_balance(builder_id):
    response = requests.get(f"{API_BASE}/wallet/{builder_id}/balance")
    return response.json()

# Send tokens
def send_tokens(sender_id, receiver_id, amount, memo, seal_level):
    data = {
        "sender_id": sender_id,
        "receiver_id": receiver_id,
        "amount": amount,
        "memo": memo,
        "seal_level": seal_level
    }
    response = requests.post(f"{API_BASE}/transaction/send", json=data)
    return response.json()
```

## 📋 Deployment Checklist

### Pre-Deployment
- [ ] Configure network parameters
- [ ] Set up flame verification system
- [ ] Initialize sacred fund addresses
- [ ] Test transaction system
- [ ] Validate security measures

### Deployment
- [ ] Deploy smart contract (ERC-20)
- [ ] Launch API servers
- [ ] Configure load balancers
- [ ] Set up monitoring
- [ ] Initialize first wallets

### Post-Deployment
- [ ] Monitor transaction volume
- [ ] Track flame level distribution
- [ ] Audit security logs
- [ ] Optimize performance
- [ ] Update documentation

## 🚨 Emergency Procedures

### Security Incident
1. **Immediate Response**
   - Suspend affected wallets
   - Freeze suspicious transactions
   - Notify SeerCircle Council

2. **Investigation**
   - Review transaction logs
   - Analyze flame verification data
   - Identify root cause

3. **Recovery**
   - Restore from backup
   - Implement security patches
   - Resume normal operations

### Network Issues
1. **Detection**
   - Monitor API response times
   - Check transaction success rates
   - Alert on unusual patterns

2. **Resolution**
   - Scale infrastructure
   - Optimize database queries
   - Update rate limiting

## 📞 Support

### Documentation
- [API Reference](https://docs.scrollcoin.com/api)
- [Integration Guide](https://docs.scrollcoin.com/integration)
- [Security Guide](https://docs.scrollcoin.com/security)

### Community
- [Discord](https://discord.gg/scrollcoin)
- [GitHub](https://github.com/scrollverse/scrollcoin-mainnet)
- [Forum](https://forum.scrollcoin.com)

### Contact
- **Technical Support**: support@scrollcoin.com
- **Security Issues**: security@scrollcoin.com
- **Governance**: council@seercircle.com

---

**🔥 Let your transactions be sacred. Let your flame burn eternal. 🔥** 