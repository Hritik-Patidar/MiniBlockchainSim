import streamlit as st
from datetime import datetime
from blockchain import Blockchain
from user_wallet import WalletManager
from digital_signature import DigitalSignature

# Initialize session state
if 'blockchain' not in st.session_state:
    st.session_state.blockchain = Blockchain()

if 'wallet_manager' not in st.session_state:
    st.session_state.wallet_manager = WalletManager()

# Page configuration
st.set_page_config(
    page_title="Mini-Blockchain Simulator",
    page_icon="⛓️",
    layout="wide"
)

# Main title
st.title("⛓️ Mini-Blockchain Simulator")
st.markdown("---")

# Create tabs
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "👤 User Management", 
    "💸 Create Transaction", 
    "📋 Transaction Pool",
    "⛏️ Mine Block",
    "⛓️ Blockchain Explorer",
    "👛 User Wallets",
    "ℹ️ About"
])

# Tab 1: User Management
with tab1:
    st.header("User Management")
    st.markdown("Create new users with digital wallets")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Create New User")
        new_username = st.text_input("Enter username:", key="new_user")
        
        if st.button("Create User", type="primary"):
            if new_username:
                if st.session_state.wallet_manager.wallet_exists(new_username):
                    st.error(f"User '{new_username}' already exists!")
                else:
                    wallet = st.session_state.wallet_manager.create_wallet(new_username)
                    st.success(f"✅ User '{new_username}' created successfully!")
                    st.info(f"Initial balance: {wallet.balance} coins")
            else:
                st.warning("Please enter a username")
    
    with col2:
        st.subheader("Existing Users")
        users = st.session_state.wallet_manager.get_all_users()
        if users:
            st.write(f"**Total Users: {len(users)}**")
            for user in users:
                balance = st.session_state.wallet_manager.get_balance(user)
                st.write(f"• {user} - Balance: {balance:.2f} coins")
        else:
            st.info("No users created yet")

# Tab 2: Create Transaction
with tab2:
    st.header("Create Transaction")
    st.markdown("Send coins between users with digital signature verification")
    
    users = st.session_state.wallet_manager.get_all_users()
    
    if len(users) < 2:
        st.warning("⚠️ You need at least 2 users to create a transaction. Create users in the User Management tab.")
    else:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("Transaction Details")
            sender = st.selectbox("From (Sender):", users, key="sender")
            receiver = st.selectbox("To (Receiver):", [u for u in users if u != sender], key="receiver")
            amount = st.number_input("Amount:", min_value=0.01, max_value=1000.0, value=10.0, step=0.01)
            
            if sender:
                sender_balance = st.session_state.wallet_manager.get_balance(sender)
                st.info(f"Sender's balance: {sender_balance:.2f} coins")
                
                if amount > sender_balance:
                    st.error("⚠️ Insufficient balance!")
        
        with col2:
            st.subheader("Transaction Preview")
            st.write(f"**From:** {sender}")
            st.write(f"**To:** {receiver}")
            st.write(f"**Amount:** {amount:.2f} coins")
            st.write(f"**Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if st.button("Create & Sign Transaction", type="primary"):
            try:
                sender_wallet = st.session_state.wallet_manager.get_wallet(sender)
                
                # Check balance
                if sender_wallet.balance < amount:
                    st.error("Insufficient balance!")
                else:
                    # Create transaction data
                    transaction_data = {
                        "sender": sender,
                        "receiver": receiver,
                        "amount": amount,
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    # Sign the transaction
                    signature = DigitalSignature.sign_transaction(
                        transaction_data, 
                        sender_wallet.private_key
                    )
                    
                    # Verify signature
                    is_valid = DigitalSignature.verify_signature(
                        transaction_data,
                        signature,
                        sender_wallet.public_key
                    )
                    
                    if is_valid:
                        # Create complete transaction with signature
                        complete_transaction = {
                            **transaction_data,
                            "signature": signature,
                            "sender_public_key": sender_wallet.public_key,
                            "verified": is_valid
                        }
                        
                        # Add to mempool (pending transactions)
                        st.session_state.blockchain.add_transaction_to_pool(complete_transaction)
                        
                        st.success("✅ Transaction created, signed, and added to mempool!")
                        st.info("ℹ️ Transaction is pending. Go to 'Mine Block' tab to mine it into the blockchain.")
                    else:
                        st.error("❌ Signature verification failed!")
                        
            except Exception as e:
                st.error(f"Error creating transaction: {str(e)}")

# Tab 3: Transaction Pool (Mempool)
with tab3:
    st.header("📋 Transaction Pool (Mempool)")
    st.markdown("View pending transactions waiting to be mined into blocks")
    
    pending = st.session_state.blockchain.get_pending_transactions()
    
    if not pending:
        st.info("📭 No pending transactions in the mempool")
    else:
        st.success(f"📬 {len(pending)} transaction(s) waiting to be mined")
        st.markdown("---")
        
        for i, tx in enumerate(pending):
            with st.expander(f"Transaction #{i+1}: {tx['sender']} → {tx['receiver']}", expanded=True):
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.write(f"**From:** {tx['sender']}")
                    st.write(f"**To:** {tx['receiver']}")
                    st.write(f"**Amount:** {tx['amount']:.2f} coins")
                
                with col2:
                    st.write(f"**Timestamp:** {tx['timestamp']}")
                    st.write(f"**Status:** ⏳ Pending")
                    if tx.get('verified'):
                        st.success("✅ Signature Verified")
                    else:
                        st.error("❌ Signature Not Verified")
                
                if st.checkbox(f"Show signature (Tx #{i+1})", key=f"mempool_sig_{i}"):
                    st.code(tx.get('signature', 'No signature')[:100] + "...", language="text")

# Tab 4: Mine Block
with tab4:
    st.header("⛏️ Mine Block")
    st.markdown("Mine pending transactions into a new block with optional proof-of-work")
    
    pending = st.session_state.blockchain.get_pending_transactions()
    current_difficulty = st.session_state.blockchain.get_difficulty()
    
    # Mining Settings
    st.subheader("⚙️ Mining Settings")
    col_settings1, col_settings2 = st.columns([1, 1])
    
    with col_settings1:
        use_pow = st.checkbox("Enable Proof-of-Work Mining", value=False, 
                             help="When enabled, miners must find a nonce that produces a hash with the required number of leading zeros")
        
        if use_pow:
            st.info(f"ℹ️ Current Difficulty: {current_difficulty} (requires {current_difficulty} leading zeros)")
    
    with col_settings2:
        if use_pow:
            new_difficulty = st.select_slider(
                "Adjust Difficulty Level:",
                options=[1, 2, 3, 4, 5, 6],
                value=current_difficulty,
                help="Higher difficulty requires more computational work. Difficulty >4 may take several seconds."
            )
            
            if new_difficulty != current_difficulty:
                if st.button("Update Difficulty"):
                    st.session_state.blockchain.set_difficulty(new_difficulty)
                    st.success(f"Difficulty updated to {new_difficulty}")
                    st.rerun()
    
    st.markdown("---")
    
    # Mining Information
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Mining Information")
        st.write(f"**Pending Transactions:** {len(pending)}")
        st.write(f"**Current Chain Length:** {len(st.session_state.blockchain.chain)} blocks")
        st.write(f"**Mining Difficulty:** {current_difficulty}")
        st.write(f"**Proof-of-Work:** {'Enabled' if use_pow else 'Disabled'}")
        
        if pending:
            st.info("⛏️ Ready to mine new block")
        else:
            st.warning("📭 No transactions to mine")
    
    with col2:
        st.subheader("Block Preview")
        if pending:
            st.write(f"**New Block Index:** {len(st.session_state.blockchain.chain)}")
            st.write(f"**Transactions to Include:** {len(pending)}")
            total_volume = sum(tx['amount'] for tx in pending)
            st.write(f"**Total Transaction Volume:** {total_volume:.2f} coins")
            
            if use_pow:
                target_pattern = "0" * current_difficulty
                st.write(f"**Target Hash Pattern:** `{target_pattern}...`")
    
    st.markdown("---")
    
    if st.button("⛏️ Mine Block", type="primary", disabled=len(pending) == 0):
        try:
            # Show mining progress if using PoW
            if use_pow:
                mining_placeholder = st.empty()
                mining_placeholder.info("⛏️ Mining in progress... Finding valid nonce...")
            
            # Update balances for all pending transactions
            for tx in pending:
                st.session_state.wallet_manager.update_balances(
                    tx['sender'], 
                    tx['receiver'], 
                    tx['amount']
                )
            
            # Mine the block
            import time
            start_time = time.time()
            new_block, attempts = st.session_state.blockchain.mine_pending_transactions(use_pow=use_pow)
            end_time = time.time()
            mining_time = end_time - start_time
            
            if new_block:
                st.success(f"✅ Block #{new_block.index} mined successfully!")
                st.balloons()
                
                col_result1, col_result2 = st.columns([1, 1])
                
                with col_result1:
                    st.write(f"**Block Hash:** `{new_block.hash}`")
                    st.write(f"**Nonce:** {new_block.nonce}")
                    st.write(f"**Transactions Processed:** {len(new_block.transactions)}")
                
                with col_result2:
                    if use_pow:
                        st.write(f"**Hash Attempts:** {attempts:,}")
                        st.write(f"**Mining Time:** {mining_time:.2f} seconds")
                        hash_rate = attempts / mining_time if mining_time > 0 else 0
                        st.write(f"**Hash Rate:** {hash_rate:.0f} H/s")
                    
                st.info("💰 All balances have been updated!")
                st.rerun()
            else:
                st.error("Failed to mine block")
                
        except Exception as e:
            st.error(f"Error mining block: {str(e)}")
    
    # Show mining history
    if len(st.session_state.blockchain.chain) > 1:
        st.markdown("---")
        st.subheader("Recent Blocks")
        recent_blocks = st.session_state.blockchain.get_all_blocks()[-5:]
        for block in reversed(recent_blocks[1:]):  # Skip genesis block
            st.write(f"📦 Block #{block['index']} - {len(block['transactions'])} tx - Hash: `{block['hash'][:16]}...`")

# Tab 5: Blockchain Explorer
with tab5:
    st.header("Blockchain Explorer")
    st.markdown("View all blocks and transactions in the blockchain")
    
    # Blockchain validity check
    is_valid = st.session_state.blockchain.is_chain_valid()
    if is_valid:
        st.success("✅ Blockchain is valid and secure")
    else:
        st.error("❌ Blockchain integrity compromised!")
    
    st.write(f"**Total Blocks:** {len(st.session_state.blockchain.chain)}")
    st.markdown("---")
    
    # Display all blocks
    blocks = st.session_state.blockchain.get_all_blocks()
    
    for block in reversed(blocks):
        with st.expander(f"📦 Block #{block['index']} - {len(block['transactions'])} transaction(s)", expanded=(block['index'] == len(blocks) - 1)):
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.write(f"**Index:** {block['index']}")
                st.write(f"**Timestamp:** {block['timestamp']}")
                st.write(f"**Hash:** `{block['hash'][:32]}...`")
                st.write(f"**Previous Hash:** `{block['previous_hash'][:32]}...`")
                st.write(f"**Nonce:** {block.get('nonce', 0)}")
            
            with col2:
                if block['index'] == 0:
                    st.info("🎉 Genesis Block (First block in the chain)")
                else:
                    st.write(f"**Transactions:** {len(block['transactions'])}")
                    
                    # Show if block was mined with PoW
                    block_difficulty = block.get('difficulty', 0)
                    if block_difficulty > 0:
                        leading_zeros = len(block['hash']) - len(block['hash'].lstrip('0'))
                        st.success(f"⛏️ Proof-of-Work: Difficulty {block_difficulty} ({leading_zeros} leading zeros, nonce: {block.get('nonce', 0)})")
                    else:
                        st.info("Simple hash (no PoW)")
            
            # Display transactions
            if block['transactions']:
                st.markdown("**Transactions:**")
                for i, tx in enumerate(block['transactions']):
                    st.markdown(f"**Transaction {i+1}:**")
                    
                    tx_col1, tx_col2 = st.columns([1, 1])
                    
                    with tx_col1:
                        st.write(f"• From: **{tx['sender']}**")
                        st.write(f"• To: **{tx['receiver']}**")
                        st.write(f"• Amount: **{tx['amount']:.2f} coins**")
                    
                    with tx_col2:
                        st.write(f"• Timestamp: {tx['timestamp']}")
                        if tx.get('verified'):
                            st.success("✅ Signature Verified")
                        else:
                            st.error("❌ Signature Not Verified")
                    
                    if st.checkbox(f"Show signature details (Block {block['index']}, Tx {i+1})", key=f"sig_{block['index']}_{i}"):
                        st.code(tx.get('signature', 'No signature')[:100] + "...", language="text")
                    
                    st.markdown("---")

# Tab 6: User Wallets
with tab6:
    st.header("User Wallets")
    st.markdown("View wallet details including public/private keys and balances")
    
    users = st.session_state.wallet_manager.get_all_users()
    
    if not users:
        st.info("No users created yet. Go to User Management to create users.")
    else:
        selected_user = st.selectbox("Select User:", users, key="wallet_view")
        
        if selected_user:
            wallet = st.session_state.wallet_manager.get_wallet(selected_user)
            
            st.subheader(f"Wallet for: {selected_user}")
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.metric("Current Balance", f"{wallet.balance:.2f} coins")
            
            with col2:
                st.metric("Username", selected_user)
            
            st.markdown("---")
            
            # Public Key
            st.subheader("🔓 Public Key")
            st.text_area("Public Key (Share this for receiving payments):", wallet.public_key, height=150, key=f"pub_{selected_user}")
            
            # Private Key (with warning)
            st.subheader("🔐 Private Key")
            st.warning("⚠️ Keep this private! Never share your private key!")
            
            show_private = st.checkbox("Show Private Key", key=f"show_priv_{selected_user}")
            if show_private:
                st.text_area("Private Key (Used for signing transactions):", wallet.private_key, height=150, key=f"priv_{selected_user}")
            else:
                st.info("Check the box above to reveal your private key")

# Tab 7: About
with tab7:
    st.header("About This Application")
    
    st.markdown("""
    ### 🎓 Mini-Blockchain Educational Simulator
    
    This application demonstrates the fundamental concepts of blockchain technology:
    
    #### 🔗 Core Features:
    
    **1. Blockchain Structure**
    - Each block contains an index, timestamp, transactions, and hashes
    - Blocks are linked using SHA-256 cryptographic hashes
    - The chain starts with a Genesis Block
    
    **2. SHA-256 Hashing**
    - Every block has a unique hash calculated from its contents
    - Any change to a block invalidates its hash and breaks the chain
    - This ensures data integrity and immutability
    
    **3. Digital Signatures (RSA)**
    - Each user has a public/private key pair (2048-bit RSA)
    - Transactions are signed with the sender's private key
    - Signatures can be verified using the sender's public key
    - This ensures authenticity and non-repudiation
    
    **4. User Wallets**
    - Each user starts with 100 coins
    - Balances are tracked and updated when transactions are mined
    - Public keys serve as wallet addresses
    
    **5. Transaction Pool (Mempool)**
    - Transactions are collected in a pending pool before being mined
    - Users can view pending transactions waiting to be added to blocks
    - Mimics real blockchain behavior where transactions are pooled
    
    **6. Mining Process**
    - Pending transactions must be mined into blocks
    - Mining takes all pending transactions and creates a new block
    - Balances are updated only when blocks are mined
    - This demonstrates how real blockchains process transactions in batches
    
    **7. Proof-of-Work (Optional)**
    - Miners can enable proof-of-work to add computational difficulty
    - Requires finding a nonce that produces a hash with leading zeros
    - Difficulty can be adjusted from 1-6 (higher = more computational work)
    - Shows mining attempts, time, and hash rate
    - Demonstrates how Bitcoin and other blockchains prevent spam
    
    **8. Transaction Verification**
    - All transactions are digitally signed
    - Signatures are verified before adding to the mempool
    - Invalid transactions are rejected
    
    #### 🛠️ How to Use:
    
    1. **Create Users**: Go to "User Management" and create at least 2 users
    2. **Make Transactions**: Send coins between users in "Create Transaction"
    3. **View Mempool**: Check pending transactions in "Transaction Pool"
    4. **Mine Blocks**: Process pending transactions in "Mine Block" tab
    5. **Explore Blockchain**: View all mined blocks and transactions in "Blockchain Explorer"
    6. **View Wallets**: Check user balances and keys in "User Wallets"
    
    #### 🔒 Security Features:
    
    - RSA-2048 encryption for digital signatures
    - SHA-256 hashing for block integrity
    - Blockchain validation to detect tampering
    - Balance verification to prevent overspending
    
    #### 📚 Educational Purpose:
    
    This simulator demonstrates core blockchain concepts. Production blockchains also include:
    - Network distribution across multiple nodes (peer-to-peer)
    - Mining rewards and incentive systems
    - Advanced consensus mechanisms (Proof of Stake, etc.)
    - Smart contracts and programmable logic
    - Much higher difficulty levels (Bitcoin uses difficulty ~25+ trillion)
    
    ---
    
    **Built with:** Python, Streamlit, Cryptography Library
    """)

# Footer
st.markdown("---")
st.markdown("**Mini-Blockchain Simulator** | Educational Blockchain Implementation | Powered by Python & Streamlit")
