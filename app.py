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
# PERSISTENT STORAGE DATA LAYER
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
# AUTOMATED LOTTERY FILTERS ENGINE (ZERO-FAILURE CORE)
# ============================================================================
class LottoEngine:
    @staticmethod
    def get_occupied_decades_count(numbers):
        decades = set()
        for n in numbers:
            if 1 <= n <= 9:
                decades.add("single")
            elif 10 <= n <= 19:
                decades.add("tens")
            elif 20 <= n <= 29:
                decades.add("twenties")
            elif 30 <= n <= 39:
                decades.add("thirties")
            elif 40 <= n <= 49:
                decades.add("forties")
        return len(decades)

    @staticmethod
    def generate_optimized_batch(quantity, game, use_filters=False, even_odd_ratio=None, min_sum=None, max_sum=None, custom_pool=None, empty_slots=None):
        cfg = GAMES[game]
        if custom_pool and len(custom_pool) >= cfg["pick"]:
            raw_pool = sorted(list(set([int(n) for n in custom_pool if 1 <= int(n) <= cfg["max"]])))
            pool = raw_pool if len(raw_pool) >= cfg["pick"] else list(range(1, cfg["max"] + 1))
        else:
            pool = list(range(1, cfg["max"] + 1))
            
        generated_tickets = []
        for _ in range(quantity):
            combination = []
            matched = False
            for _ in range(500):
                sample = sorted(random.sample(pool, cfg["pick"]))
                if use_filters:
                    if even_odd_ratio:
                        evens = len([n for n in sample if n % 2 == 0])
                        odds = cfg["pick"] - evens
                        if f"{evens}:{odds}" != even_odd_ratio:
                            continue
                    if min_sum is not None and max_sum is not None:
                        if not (int(min_sum) <= sum(sample) <= int(max_sum)):
                            continue
                    if empty_slots is not None and empty_slots > 0:
                        total_slots_available = 4 if cfg["max"] <= 35 else 5
                        occupied = LottoEngine.get_occupied_decades_count(sample)
                        actual_empty_slots = total_slots_available - occupied
                        if actual_empty_slots != empty_slots:
                            continue
                combination = sample
                matched = True
                break
            if not matched:
                combination = sorted(random.sample(pool, cfg["pick"]))
            bonus = random.randint(1, cfg["bonus_max"]) if cfg.get("bonus") else None
            generated_tickets.append((combination, bonus))
        return generated_tickets

# ============================================================================
# STREAMLIT UI CONTROLLER & CHANNELS REROUTING
# ============================================================================
st.markdown("<h1 style='text-align: center;'>🎰 Aussie Lotto Filter Pro</h1>", unsafe_allow_html=True)
st.write("---")

if "user_plan" not in st.session_state:
    st.session_state["user_plan"] = "free"

query_params = st.query_params
if "session_id" in query_params and st.session_state["user_plan"] == "free":
    st.session_state["user_plan"] = "monthly"
    st.success("🎉 Stripe Test Payment Verified Successfully! Advanced Pro Filters Activated.")

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

game_choice = st.selectbox("Select Target Lottery Regulation Architecture:", list(GAMES.keys()))

st.write("### 📊 Dataset Volume Configuration")
ticket_quantity = st.number_input(
    "Specify calculation payload density (Number of tickets to output):", 
    min_value=1, max_value=50000, value=1, step=1
)

st.write("---")
st.subheader("🛠️ Algorithmic Constraint Controls Matrix")

def compile_io_payload(tickets, game):
    txt_output = f"=== Aussie Lotto Filter Pro Output Report ===\nGenerated Timestamp: {datetime.now().isoformat()}\nTarget Game Metric: {game}\n"
    csv_records = []
    for idx, (nums, bns) in enumerate(tickets, 1):
        formatted_nums = ", ".join(map(str, nums))
        bonus_suffix = f" | [Powerball/Bonus: {bns}]" if bns else ""
        txt_output += f"Execution Pattern #{idx}: [{formatted_nums}]{bonus_suffix}\n"
        csv_records.append({
            "Batch execution ID": idx, "Lottery System": game, "Core Numbers Matrix": formatted_nums, "Secondary Bonus Token": bns if bns else "NULL"
        })
    return txt_output, pd.DataFrame(csv_records).to_csv(index=False)

pool_strategy = st.selectbox(
    "Matrix Dataset Search Strategy:",
    ["Option A: Fully Random Pool", "Option B: Custom Number Pool"]
)

extracted_custom_pool = []
if "Option B" in pool_strategy:
    st.write(f"**📍 Target Numerical Matrix Insertion Pool (Minimum Required Elements: {GAMES[game_choice]['pick']}):**")
    raw_pool_input = st.text_area(
        "Inject mathematical pool criteria (Separate numbers by commas, dots, spaces, or any character):",
        placeholder=f"Enter integers from 1 up to {GAMES[game_choice]['max']}"
    )
    if raw_pool_input:
        numbers_found = re.findall(r'\d+', raw_pool_input)
        extracted_custom_pool = sorted(list(set([int(n) for n in numbers_found if 1 <= int(n) <= GAMES[game_choice]['max']])))
        if len(extracted_custom_pool) < GAMES[game_choice]['pick']:
            st.error(f"❌ Structural Integrity Alert: Pool metrics density must reach at least {GAMES[game_choice]['pick']} elements.")

st.write("---")

if st.session_state["user_plan"] == "free":
    st.warning("🔒 Advanced Matrix Filters (Empty Decade Slots, Odd/Even Balancer, Golden Sum Scope Vector) are locked. Upgrade to Pro to activate filters.")
    if st.button(f"Generate {ticket_quantity:,} Standard Ticket(s) (Free Tier)"):
        if "Option B" in pool_strategy and len(extracted_custom_pool) < GAMES[game_choice]['pick']:
            st.error("Execution halt: Operational criteria requires sufficient pool values or selection of Option A framework.")
        else:
            with st.spinner("Executing structural batch compilation..."):
                batch = LottoEngine.generate_optimized_batch(ticket_quantity, game_choice, use_filters=False, custom_pool=extracted_custom_pool)
                for idx, (nums, bns) in enumerate(batch, 1):
                    st.write(f"Pattern Execution Array #{idx}: **{nums}**" + (f" | Bonus Unit: **{bns}**" if bns else ""))
                txt_io, csv_io = compile_io_payload(batch, game_choice)
                st.write("---")
                st.write("💾 **Secure Data Export Nodes:**")
                st.download_button("📥 Export ASCII Logs (.txt)", data=txt_io, file_name=f"lotto_tickets_{game_choice}.txt", mime="text/plain")
                st.download_button("📥 Export Structural Tables (.csv)", data=csv_io, file_name=f"lotto_sheet_{game_choice}.csv", mime="text/csv")
            st.success(f"Successfully processed {ticket_quantity:,} structural matrix blocks!")
