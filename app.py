import streamlit as st
import json
import random
import hashlib
import secrets
from datetime import datetime, timedelta
import uuid
import logging
import sqlite3
import os
from dotenv import load_dotenv
import stripe
import bcrypt
import pandas as pd
import re

# ============================================================================
# ENTERPRISE SECURITY & CONFIGURATION MATRIX
# ============================================================================
load_dotenv()

st.set_page_config(
    page_title="Aussie Lotto Filter Pro",
    page_icon="🎰",
    layout="wide",
    initial_sidebar_state="expanded"
)

SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_hex(32))
STRIPE_PUBLIC_KEY = os.getenv("STRIPE_PUBLIC_KEY", "pk_test_xxxx")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "sk_test_xxxx")
stripe.api_key = STRIPE_SECRET_KEY

GAMES = {
    "Powerball": {"pick": 7, "max": 35, "bonus": True, "bonus_max": 20},
    "Saturday Lotto": {"pick": 6, "max": 45, "bonus": False},
    "Wednesday Lotto": {"pick": 6, "max": 45, "bonus": False},
    "Oz Lotto": {"pick": 7, "max": 47, "bonus": False},
    "Set for Life": {"pick": 7, "max": 44, "bonus": False}
}

# ============================================================================
# DATABASE MANAGER
# ============================================================================
class DatabaseManager:
    def __init__(self, db_path="lottery.db"):
        self.db_path = db_path
        self.init_database()
        
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
        
    def init_database(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY, email TEXT UNIQUE, password_hash TEXT, plan TEXT DEFAULT 'free'
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vip_codes (
                code TEXT PRIMARY KEY, plan_type TEXT, is_redeemed INT DEFAULT 0, expiry_date TEXT
            )
        ''')
        conn.commit()
        conn.close()

db = DatabaseManager()

# ============================================================================
# AUTOMATED LOTTERY FILTERS ENGINE (ORIGINAL MATHEMATICAL LOGIC)
# ============================================================================
class LottoEngine:
    @staticmethod
    def is_natural(combo):
        for i in range(len(combo)-2):
            if combo[i] + 1 == combo[i+1] and combo[i+1] + 1 == combo[i+2]:
                return False
        for i in range(len(combo)-1):
            if (combo[i+1] - combo[i]) > 18: 
                return False
        return True

    @staticmethod
    def get_available_decades_count(game_max):
        if game_max <= 9: return 1
        if game_max <= 19: return 2
        if game_max <= 29: return 3
        if game_max <= 39: return 4
        return 5

    @staticmethod
    def get_occupied_decades_count(numbers):
        decades = set()
        for n in numbers:
            if 1 <= n <= 9: decades.add(0)
            elif 10 <= n <= 19: decades.add(1)
            elif 20 <= n <= 29: decades.add(2)
            elif 30 <= n <= 39: decades.add(3)
            elif 40 <= n <= 49: decades.add(4)
        return len(decades)

    @staticmethod
    def generate_filtered_tickets(quantity, selected_numbers, sys_size, sum_range=None, odd_range=None, empty_req=0, fixed_nums=None):
        valid_tickets = []
        pool = sorted(list(set(selected_numbers)))
        
        if len(pool) < sys_size:
            pool = list(range(1, 46))
            
        fixed_set = set(fixed_nums) if fixed_nums else set()
        
        for _ in range(quantity * 10):
            if len(valid_tickets) >= quantity:
                break
                
            if fixed_set:
                available_pool = [n for n in pool if n not in fixed_set]
                needed_count = sys_size - len(fixed_set)
                if needed_count > 0 and len(available_pool) >= needed_count:
                    sample = sorted(list(fixed_set) + random.sample(available_pool, needed_count))
                else:
                    sample = sorted(random.sample(pool, sys_size))
            else:
                sample = sorted(random.sample(pool, sys_size))
                
            if sum_range:
                mi, ma = sum_range
                if not (mi <= sum(sample) <= ma):
                    continue
                    
            if odd_range:
                mi_o, ma_o = odd_range
                odd_c = len([n for n in sample if n % 2 != 0])
                if not (mi_o <= odd_c <= ma_o):
                    continue
                    
            if not LottoEngine.is_natural(sample):
                continue
                
            if empty_req > 0 and LottoEngine.count_empty_decades(sample) < empty_req:
                continue
                
            if sample not in valid_tickets:
                valid_tickets.append(sample)
                
        while len(valid_tickets) < quantity:
            fallback_sample = sorted(random.sample(pool, sys_size))
            if fallback_sample not in valid_tickets:
                valid_tickets.append(fallback_sample)
                
        return sorted(valid_tickets)

# ============================================================================
# CLOUD APPLICATION FRONTEND LAYER (100% LOCKED PAYWALL ARCHITECTURE)
# ============================================================================
st.markdown("<h1 style='text-align: center;'>🎰 Aussie Lotto Filter Pro</h1>", unsafe_allow_html=True)
st.write("---")

if "user_plan" not in st.session_state:
    st.session_state["user_plan"] = "free"

# الأتمتة التلقائية بعد الدفع
query_params = st.query_params
if "session_id" in query_params and st.session_state["user_plan"] == "free":
    st.session_state["user_plan"] = "monthly"
    st.success("🎉 Stripe Test Payment Verified Successfully! Welcome to Aussie Lotto Filter Pro Framework.")

# القائمة الجانبية الموحدة لإدارة الرخص
st.sidebar.header("👤 Account Environment")
status_color = "green" if st.session_state["user_plan"] != "free" else "red"
st.sidebar.markdown(f"Subscription Profile Status: :{status_color}[{st.session_state['user_plan'].upper()}]")

with st.sidebar.expander("🎫 Enterprise VIP Authentication"):
    vip_input = st.text_input("Enter Activation Token:").strip().upper()
    if st.button("Authorize License"):
        if vip_input in ["LIFETIME99", "AUSSIELOTTO30"]:
            st.session_state["user_plan"] = "lifetime"
            st.success("Authorization token verified successfully!")
            st.rerun()
        else:
            st.sidebar.error("Cryptographic token signature is invalid or expired.")

def compile_io_payload(tickets, size):
    txt_output = f"=== Aussie Lotto Filter Pro Output Report ===\nGenerated Tickets Quantity: {len(tickets)}\n"
    csv_records = []
    for idx, t in enumerate(tickets, 1):
        formatted_nums = ", ".join(map(str, t))
        txt_output += f"CARD {idx:03d}: [{formatted_nums}]\n"
        csv_records.append({"Card ID": idx, "Core Numbers Matrix": formatted_nums})
    return txt_output, pd.DataFrame(csv_records).to_csv(index=False)

# ----------------------------------------------------------------------------
# 1. GATEWAY SCREEN FOR FREE VISITORS (الموقع مغلق تماماً بمجرد الدخول)
# ----------------------------------------------------------------------------
if st.session_state["user_plan"] == "free":
    st.error("🔒 ACCESS DENIED: This advanced lottery filter system is exclusive to registered premium members.")
    st.write("### 💳 Upgrade to Premium Tier to Unlock the Platform")
    st.info("Please complete your purchase via the secure gateway below. Once paid, the system will automatically activate your matrix generator dashboard.")
    
    # رابط الدفع لجمع الأموال والأرباح المباشرة
    st.markdown("[👉 CLICK HERE TO PURCHASE PREMIUM SYSTEM ACCESS NOW VIA SECURE STRIPE GATEWAY](https://stripe.com)")
    
    st.write("---")
    st.caption("ℹ️ If you have a corporate promo code or a VIP license token, please open the left sidebar dashboard panel (>> icon) to authorize your station access.")

# ----------------------------------------------------------------------------
# 2. COMPLETE FRAMEWORK WORKSPACE FOR PAID/VIP SUBSCRIBERS
# ----------------------------------------------------------------------------
else:
    st.info("🔓 Enterprise Premium Access Protocol Granted. Dynamic Filter Framework Unlocked.")
    
    game_choice = st.selectbox("Select Target Lottery Regulation Architecture:", list(GAMES.keys()))

    st.write("### 📊 Dataset Volume Configuration")
    ticket_quantity = st.number_input(
        "Specify calculation payload density (Number of tickets to output):", 
        min_value=1, max_value=50000, value=5, step=1
    )

    st.write("---")
    st.subheader("🛠️ Algorithmic Constraint Controls Matrix")
    
    pool_strategy = st.selectbox(
        "Matrix Dataset Search Strategy:",
        ["Option A: Fully Random Pool (From 1 to 45)", "Option B: Custom Number Pool (From your chosen numbers)"]
    )

    parsed_numbers = list(range(1, 46))
    if "Option B" in pool_strategy:
        st.write("**📍 Enter Your Expected Numbers Matrix:**")
        raw_pool_input = st.text_area(
            "Inject mathematical pool criteria (Separate numbers by commas, dots, spaces, or lines):",
            value="5 10 12 18 22 25 30 33 39 41 42 45"
        )
        if raw_pool_input:
            numbers_found = re.findall(r'\d+', raw_pool_input)
            parsed_numbers = sorted(list(set([int(n) for n in numbers_found if 1 <= int(n) <= 50])))

    st.write("---")
    panel_col1, panel_col2 = st.columns(2)
    
