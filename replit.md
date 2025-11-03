# Mini-Blockchain Simulator

## Overview

This is an educational blockchain simulator built with Streamlit that demonstrates core blockchain concepts including cryptographic hashing, digital signatures, transaction management, and wallet systems. The application allows users to create wallets, sign and execute transactions, and explore the blockchain structure in an interactive web interface.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture

**Technology**: Streamlit web framework

The application uses Streamlit for the entire user interface, leveraging its session state management for maintaining blockchain and wallet data across user interactions. The UI is organized into five tabbed sections for different functionalities (User Management, Transaction Creation, Blockchain Explorer, User Wallets, and About).

**Rationale**: Streamlit was chosen for rapid prototyping of data-centric applications with minimal frontend code. It provides built-in state management and reactive UI updates without requiring separate frontend/backend architecture.

**Pros**: Quick development, Python-native, excellent for demos and educational tools
**Cons**: Limited customization compared to traditional web frameworks, not suitable for production-scale applications

### Backend Architecture

**Design Pattern**: Object-oriented with core domain models

The application follows a modular architecture with three main domain components:

1. **Blockchain Module** (`blockchain.py`): Implements Block and Blockchain classes using immutable hash-linked data structures
2. **Digital Signature Module** (`digital_signature.py`): Handles RSA cryptography for transaction signing and verification
3. **Wallet Management Module** (`user_wallet.py`): Manages user wallets with key pairs and balances

**Rationale**: Each component encapsulates a specific blockchain concept (chain structure, cryptography, user accounts), making the codebase educational and maintainable. The separation allows each module to be understood and modified independently.

**Alternatives Considered**: A single monolithic module would be simpler but less educational and harder to extend.

### Data Storage

**Approach**: In-memory storage using Python data structures

All blockchain data, wallets, and pending transactions are stored in Streamlit's session state (Python dictionaries and lists). No persistent database is used.

**Rationale**: As an educational simulator, persistence is not required. In-memory storage keeps the application simple and demonstrates blockchain concepts without database complexity.

**Pros**: Simple implementation, no database setup required, easy to reset
**Cons**: Data lost on page refresh, not suitable for real applications, no multi-user support

### Cryptographic Architecture

**Technology**: RSA-2048 digital signatures using Python's `cryptography` library

The system uses asymmetric cryptography where each wallet has:
- A private key (kept secret, used for signing transactions)
- A public key (shared publicly, used for verification)

**Rationale**: RSA demonstrates real-world blockchain security principles. The 2048-bit key size balances security with computational efficiency for an educational tool.

**Implementation Details**: 
- Keys are serialized in PEM format for storage
- Transaction signatures use PKCS1v15 padding with SHA-256 hashing
- Each transaction is signed by the sender's private key and verifiable with their public key

### Hashing Strategy

**Algorithm**: SHA-256 cryptographic hash function

Block hashes are calculated from JSON-serialized block data (index, timestamp, transactions, previous hash) to create the immutable chain linkage.

**Rationale**: SHA-256 is the industry standard for blockchain applications, providing strong collision resistance and demonstrating real blockchain security.

## External Dependencies

### Core Libraries

1. **streamlit**: Web framework for the entire user interface
   - Purpose: UI rendering, state management, user interaction
   - Integration: Main application entry point (`app.py`)

2. **cryptography**: Cryptographic operations library
   - Purpose: RSA key generation, digital signatures, hashing
   - Integration: Used in `digital_signature.py` for all cryptographic operations
   - Specific modules: `hazmat.primitives.asymmetric.rsa`, `hazmat.primitives.hashes`, `hazmat.primitives.serialization`

### Standard Library Dependencies

- **hashlib**: SHA-256 hashing for block integrity
- **json**: Serialization of block and transaction data
- **datetime**: Timestamp generation for blocks and transactions
- **typing**: Type hints for code clarity
- **base64**: Encoding for cryptographic data (in `digital_signature.py`)

### No External Services

The application is fully self-contained with no external API integrations, databases, or third-party services. All functionality runs locally within the Streamlit application.