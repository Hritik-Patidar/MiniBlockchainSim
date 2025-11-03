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

if 'pending_transactions' not in st.session_state:
    st.session_state.pending_transactions = []

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
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "👤 User Management", 
    "💸 Create Transaction", 
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
                        
                        # Add to pending transactions
                        st.session_state.pending_transactions.append(complete_transaction)
                        
                        # Update balances
                        st.session_state.wallet_manager.update_balances(sender, receiver, amount)
                        
                        # Add block to blockchain
                        st.session_state.blockchain.add_block([complete_transaction])
                        
                        st.success("✅ Transaction created, signed, and added to blockchain!")
                        st.balloons()
                        
                        # Clear pending transactions
                        st.session_state.pending_transactions = []
                    else:
                        st.error("❌ Signature verification failed!")
                        
            except Exception as e:
                st.error(f"Error creating transaction: {str(e)}")

# Tab 3: Blockchain Explorer
with tab3:
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
            
            with col2:
                if block['index'] == 0:
                    st.info("🎉 Genesis Block (First block in the chain)")
                else:
                    st.write(f"**Transactions:** {len(block['transactions'])}")
            
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

# Tab 4: User Wallets
with tab4:
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

# Tab 5: About
with tab5:
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
    - Balances are tracked and updated with each transaction
    - Public keys serve as wallet addresses
    
    **5. Transaction Verification**
    - All transactions are digitally signed
    - Signatures are verified before adding to the blockchain
    - Invalid transactions are rejected
    
    #### 🛠️ How to Use:
    
    1. **Create Users**: Go to "User Management" and create at least 2 users
    2. **Make Transactions**: Send coins between users in "Create Transaction"
    3. **Explore Blockchain**: View all blocks and transactions in "Blockchain Explorer"
    4. **View Wallets**: Check user balances and keys in "User Wallets"
    
    #### 🔒 Security Features:
    
    - RSA-2048 encryption for digital signatures
    - SHA-256 hashing for block integrity
    - Blockchain validation to detect tampering
    - Balance verification to prevent overspending
    
    #### 📚 Educational Purpose:
    
    This is a simplified blockchain for learning purposes. Production blockchains include:
    - Proof of Work / Proof of Stake consensus mechanisms
    - Network distribution across multiple nodes
    - Advanced cryptography and security measures
    - Transaction pools and mining rewards
    
    ---
    
    **Built with:** Python, Streamlit, Cryptography Library
    """)

# Footer
st.markdown("---")
st.markdown("**Mini-Blockchain Simulator** | Educational Blockchain Implementation | Powered by Python & Streamlit")
