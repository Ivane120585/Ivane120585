#!/usr/bin/env python3
"""
ScrollInvest UI
Donation + tithe portal for ScrollCoin economy
"""

import streamlit as st
import json
import csv
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional
import datetime
import hashlib
import hmac

class ScrollInvest:
    """Sacred investment and donation portal"""
    
    def __init__(self):
        self.transaction_log_file = Path("scrollverse_portal/investment/vault_transaction_log.csv")
        self.funding_policy_file = Path("scrollverse_portal/investment/scrollfunding_policy.md")
        self.donation_tiers_file = Path("scrollverse_portal/investment/donation_tiers.json")
        self.transactions = self.load_transactions()
        self.donation_tiers = self.load_donation_tiers()
        self.funding_policy = self.load_funding_policy()
    
    def load_transactions(self) -> List[Dict]:
        """Load transaction log"""
        try:
            df = pd.read_csv(self.transaction_log_file)
            return df.to_dict('records')
        except FileNotFoundError:
            return []
    
    def save_transactions(self):
        """Save transaction log"""
        df = pd.DataFrame(self.transactions)
        df.to_csv(self.transaction_log_file, index=False)
    
    def load_donation_tiers(self) -> Dict:
        """Load donation tiers"""
        try:
            with open(self.donation_tiers_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def load_funding_policy(self) -> str:
        """Load funding policy"""
        try:
            with open(self.funding_policy_file, 'r') as f:
                return f.read()
        except FileNotFoundError:
            return "Funding policy not found"
    
    def generate_flame_seal(self, transaction_data: str) -> str:
        """Generate flame seal for transaction integrity"""
        secret_key = "scrollverse_investment_secret".encode('utf-8')
        message = transaction_data.encode('utf-8')
        signature = hmac.new(secret_key, message, hashlib.sha256).hexdigest()
        return f"flame_{signature[:16]}"
    
    def create_transaction(self, donor_name: str, amount: float, 
                          transaction_type: str, purpose: str, 
                          seal_level: int) -> Dict:
        """Create a new transaction with flame verification"""
        transaction_id = f"txn_{len(self.transactions) + 1:06d}"
        timestamp = datetime.datetime.now().isoformat()
        
        # Create transaction data
        transaction_data = f"{transaction_id}:{donor_name}:{amount}:{transaction_type}:{purpose}"
        flame_seal = self.generate_flame_seal(transaction_data)
        
        transaction = {
            'transaction_id': transaction_id,
            'timestamp': timestamp,
            'donor_name': donor_name,
            'amount': amount,
            'transaction_type': transaction_type,
            'purpose': purpose,
            'seal_level': seal_level,
            'flame_seal': flame_seal,
            'status': 'completed'
        }
        
        self.transactions.append(transaction)
        self.save_transactions()
        
        return transaction
    
    def render_donation_form(self):
        """Render donation form"""
        st.header("💰 Make a Sacred Donation")
        st.write("Support the ScrollVerse ecosystem with your contribution.")
        
        with st.form("donation_form"):
            donor_name = st.text_input("Your Name", placeholder="Enter your name")
            amount = st.number_input("Donation Amount (ScrollCoin)", min_value=1.0, value=10.0, step=1.0)
            
            transaction_type = st.selectbox(
                "Transaction Type",
                ["Donation", "Tithe", "Investment", "Blessing"]
            )
            
            purpose = st.selectbox(
                "Purpose",
                [
                    "Platform Development",
                    "Seer Ordination",
                    "Embassy Construction",
                    "Academy Funding",
                    "Prophetic Missions",
                    "General Support"
                ]
            )
            
            seal_level = st.slider("Your Seal Level", min_value=1, max_value=8, value=1)
            
            if st.form_submit_button("🔥 Submit Donation"):
                if donor_name and amount > 0:
                    transaction = self.create_transaction(
                        donor_name=donor_name,
                        amount=amount,
                        transaction_type=transaction_type,
                        purpose=purpose,
                        seal_level=seal_level
                    )
                    
                    st.success(f"✅ Donation submitted successfully!")
                    st.write(f"**Transaction ID:** {transaction['transaction_id']}")
                    st.write(f"**Flame Seal:** {transaction['flame_seal']}")
                    st.write(f"**Amount:** {amount} ScrollCoin")
                    st.write(f"**Purpose:** {purpose}")
                else:
                    st.error("Please fill in all required fields.")
    
    def render_donation_tiers(self):
        """Render donation tiers"""
        st.header("🏆 Donation Tiers")
        
        if not self.donation_tiers:
            st.info("Donation tiers not configured")
            return
        
        tiers = self.donation_tiers.get('tiers', [])
        
        for tier in tiers:
            with st.expander(f"💎 {tier['name']} - {tier['amount']} ScrollCoin"):
                st.write(f"**Description:** {tier['description']}")
                st.write(f"**Benefits:**")
                for benefit in tier['benefits']:
                    st.write(f"• {benefit}")
                st.write(f"**Seal Level Required:** {tier['seal_level_required']}")
    
    def render_transaction_history(self):
        """Render transaction history"""
        st.header("📜 Transaction History")
        
        if not self.transactions:
            st.info("No transactions found")
            return
        
        # Filter options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            transaction_type_filter = st.selectbox(
                "Filter by Type",
                ["All"] + list(set(t['transaction_type'] for t in self.transactions))
            )
        
        with col2:
            purpose_filter = st.selectbox(
                "Filter by Purpose",
                ["All"] + list(set(t['purpose'] for t in self.transactions))
            )
        
        with col3:
            min_amount = st.number_input("Min Amount", min_value=0.0, value=0.0)
        
        # Filter transactions
        filtered_transactions = self.transactions.copy()
        
        if transaction_type_filter != "All":
            filtered_transactions = [t for t in filtered_transactions 
                                  if t['transaction_type'] == transaction_type_filter]
        
        if purpose_filter != "All":
            filtered_transactions = [t for t in filtered_transactions 
                                  if t['purpose'] == purpose_filter]
        
        filtered_transactions = [t for t in filtered_transactions 
                              if t['amount'] >= min_amount]
        
        # Display transactions
        if filtered_transactions:
            df = pd.DataFrame(filtered_transactions)
            
            # Format timestamp
            df['timestamp'] = pd.to_datetime(df['timestamp']).dt.strftime('%Y-%m-%d %H:%M')
            
            # Display table
            st.dataframe(
                df[['transaction_id', 'timestamp', 'donor_name', 'amount', 
                    'transaction_type', 'purpose', 'seal_level', 'status']],
                use_container_width=True
            )
            
            # Statistics
            total_amount = sum(t['amount'] for t in filtered_transactions)
            total_transactions = len(filtered_transactions)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Amount", f"{total_amount:.2f} ScrollCoin")
            with col2:
                st.metric("Total Transactions", total_transactions)
            with col3:
                avg_amount = total_amount / total_transactions if total_transactions > 0 else 0
                st.metric("Average Amount", f"{avg_amount:.2f} ScrollCoin")
        else:
            st.info("No transactions match the selected filters")
    
    def render_funding_statistics(self):
        """Render funding statistics"""
        st.header("📊 Funding Statistics")
        
        if not self.transactions:
            st.info("No transaction data available")
            return
        
        # Create statistics
        df = pd.DataFrame(self.transactions)
        
        # Transaction type distribution
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("💰 Transaction Types")
            type_stats = df.groupby('transaction_type')['amount'].agg(['sum', 'count']).reset_index()
            type_stats.columns = ['Type', 'Total Amount', 'Count']
            
            fig = px.pie(
                type_stats,
                values='Total Amount',
                names='Type',
                title="Donation Distribution by Type"
            )
            st.plotly_chart(fig)
        
        with col2:
            st.subheader("🎯 Purpose Distribution")
            purpose_stats = df.groupby('purpose')['amount'].agg(['sum', 'count']).reset_index()
            purpose_stats.columns = ['Purpose', 'Total Amount', 'Count']
            
            fig = px.bar(
                purpose_stats,
                x='Purpose',
                y='Total Amount',
                title="Funding by Purpose",
                color='Count',
                color_continuous_scale='viridis'
            )
            st.plotly_chart(fig)
        
        # Time series
        st.subheader("📈 Funding Over Time")
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['date'] = df['timestamp'].dt.date
        
        daily_stats = df.groupby('date')['amount'].sum().reset_index()
        
        fig = px.line(
            daily_stats,
            x='date',
            y='amount',
            title="Daily Funding Trends",
            labels={'amount': 'ScrollCoin', 'date': 'Date'}
        )
        st.plotly_chart(fig)
        
        # Seal level analysis
        st.subheader("🔐 Seal Level Analysis")
        seal_stats = df.groupby('seal_level')['amount'].agg(['sum', 'count']).reset_index()
        seal_stats.columns = ['Seal Level', 'Total Amount', 'Count']
        
        fig = px.scatter(
            seal_stats,
            x='Seal Level',
            y='Total Amount',
            size='Count',
            title="Donations by Seal Level",
            labels={'Total Amount': 'ScrollCoin', 'Count': 'Transaction Count'}
        )
        st.plotly_chart(fig)
    
    def render_funding_policy(self):
        """Render funding policy"""
        st.header("📋 Funding Policy")
        
        st.markdown(self.funding_policy)
    
    def render_blessing_registry(self):
        """Render scroll blessings registry"""
        st.header("🙏 Scroll Blessings Registry")
        
        # Load blessings registry
        blessings_file = Path("scrollverse_portal/investment/scroll_blessings_registry.json")
        try:
            with open(blessings_file, 'r') as f:
                blessings = json.load(f)
        except FileNotFoundError:
            st.info("Blessings registry not found")
            return
        
        blessings_list = blessings.get('blessings', [])
        
        if not blessings_list:
            st.info("No blessings recorded")
            return
        
        # Display blessings
        for blessing in blessings_list:
            with st.expander(f"🙏 {blessing['title']} - {blessing['donor']}"):
                st.write(f"**Donor:** {blessing['donor']}")
                st.write(f"**Amount:** {blessing['amount']} ScrollCoin")
                st.write(f"**Blessing:** {blessing['blessing']}")
                st.write(f"**Date:** {blessing['date']}")
                st.write(f"**Seal Level:** {blessing['seal_level']}")
                if blessing.get('flame_seal'):
                    st.write(f"**Flame Seal:** {blessing['flame_seal']}")
    
    def run(self):
        """Run the ScrollInvest interface"""
        st.set_page_config(
            page_title="ScrollInvest",
            page_icon="💰",
            layout="wide"
        )
        
        st.title("💰 ScrollInvest")
        st.markdown("**Sacred Investment and Donation Portal**")
        
        # Sidebar navigation
        st.sidebar.title("💰 Navigation")
        page = st.sidebar.selectbox(
            "Choose a section:",
            ["💸 Make Donation", "🏆 Donation Tiers", "📜 Transaction History", 
             "📊 Statistics", "📋 Funding Policy", "🙏 Blessings Registry"]
        )
        
        if page == "💸 Make Donation":
            self.render_donation_form()
        
        elif page == "🏆 Donation Tiers":
            self.render_donation_tiers()
        
        elif page == "📜 Transaction History":
            self.render_transaction_history()
        
        elif page == "📊 Statistics":
            self.render_funding_statistics()
        
        elif page == "📋 Funding Policy":
            self.render_funding_policy()
        
        elif page == "🙏 Blessings Registry":
            self.render_blessing_registry()
        
        # Footer
        st.sidebar.markdown("---")
        st.sidebar.markdown("""
        ### Investment Summary
        - **Total Transactions**: {total_txns}
        - **Total Amount**: {total_amount:.2f} ScrollCoin
        - **Active Donors**: {active_donors}
        
        ### Sacred Reminder
        All donations support the ScrollVerse ecosystem and are flame-verified for integrity.
        """.format(
            total_txns=len(self.transactions),
            total_amount=sum(t['amount'] for t in self.transactions),
            active_donors=len(set(t['donor_name'] for t in self.transactions))
        ))

# Run the investment portal
if __name__ == "__main__":
    scroll_invest = ScrollInvest()
    scroll_invest.run() 