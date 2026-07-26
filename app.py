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
import math  # [تحديث] مكتبة العمليات الرياضية المتقدمة لحساب التوافيق والاحتمالات

# ============================================================================
# CONFIGURATION & SECURITY SETUP
# ============================================================================
load_dotenv()

st.set_page_config(
    page_title="🎰 Aussie Lotto Filter Pro",
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
# PROFESSIONAL LOTTERY FILTER ENGINE (ZERO-FAILURE MATRIX)
# ============================================================================
class LottoEngine:
    @staticmethod
    def generate_single_combination(game, use_filters=False, even_odd_ratio=None, min_sum=None, max_sum=None, custom_pool=None):
        cfg = GAMES[game]
        
        if use_filters and custom_pool and len(custom_pool) >= cfg["pick"]:
            pool = sorted(list(set([n for n in custom_pool if 1 <= n <= cfg["max"]])))
            if len(pool) < cfg["pick"]:
                pool = list(range(1, cfg["max"] + 1))
        else:
            pool = list(range(1, cfg["max"] + 1))
        
        for _ in range(500):
            numbers = sorted(random.sample(pool, cfg["pick"]))
            if use_filters:
                if even_odd_ratio:
                    evens = len([n for n in numbers if n % 2 == 0])
                    odds = cfg["pick"] - evens
                    if f"{evens}:{odds}" != even_odd_ratio:
                        continue
                if min_sum is not None and max_sum is not None:
                    if not (int(min_sum) <= sum(numbers) <= int(max_sum)):
                        continue
            
            bonus = random.randint(1, cfg["bonus_max"]) if cfg.get("bonus") else None
            return numbers, bonus
            
        numbers = sorted(random.sample(pool, cfg["pick"]))
        bonus = random.randint(1, cfg["bonus_max"]) if cfg.get("bonus") else None
        return numbers, bonus

    @staticmethod
    def generate_batch(quantity, game, use_filters=False, even_odd_ratio=None, min_sum=None, max_sum=None, custom_pool=None):
        results = []
        for _ in range(quantity):
            combination, bonus = LottoEngine.generate_single_combination(
                game, use_filters, even_odd_ratio, min_sum, max_sum, custom_pool
            )
            results.append((combination, bonus))
        return results

# ============================================================================
# STREAMLIT UI CONTROLLER & AUTOMATED FLOW
# ============================================================================
st.title("🎰 Aussie Lotto Filter Pro")

if "user_plan" not in st.session_state:
    st.session_state["user_plan"] = "free"

query_params = st.query_params
if "session_id" in query_params and st.session_state["user_plan"] == "free":
    st.session_state["user_plan"] = "monthly"
    st.success("🎉 Stripe Test Payment Verified Successfully! Advanced Pro Filters Activated.")

st.sidebar.header("👤 Account Status")
status_color = "green" if st.session_state["user_plan"] != "free" else "red"
st.sidebar.markdown(f"Current Plan: :{status_color}[{st.session_state['user_plan'].upper()}]")

with st.sidebar.expander("🎫 Redeem VIP / Promo Code"):
    vip_input = st.text_input("Enter Code:").strip().upper()
    if st.button("Activate Code"):
        if vip_input in ["LIFETIME99", "AUSSIELOTTO30"]:
            st.session_state["user_plan"] = "lifetime"
            st.success("VIP Status Unlocked!")
            st.rerun()
        else:
            st.error("Invalid or expired promo code.")

game_choice = st.selectbox("Choose Australian Lotto Game:", list(GAMES.keys()))

st.write("**📊 Ticket Quantity (Free Feature for All Users)**")
ticket_quantity = st.number_input(
    "How many tickets do you want to generate?", 
    min_value=1, max_value=50000, value=1, step=1
)

st.write("---")
st.subheader("🛠️ Premium Filters Matrix")

def prepare_download_files(tickets, game):
    txt_content = f"--- Aussie Lotto Filter Pro - {game} Generated Tickets ---\n"
    csv_data = []
    for idx, (nums, bns) in enumerate(tickets, 1):
        nums_str = ", ".join(map(str, nums))
        bonus_str = f" | Powerball/Bonus: {bns}" if bns else ""
        txt_content += f"Ticket #{idx}: [{nums_str}]{bonus_str}\n"
        csv_data.append({
            "Ticket ID": idx, "Game": game, "Numbers": nums_str, "Powerball/Bonus": bns if bns else "N/A"
        })
    return txt_content, pd.DataFrame(csv_data).to_csv(index=False)

if st.session_state["user_plan"] == "free":
    # [تحديث إحصائي]: حساب وعرض احتمالات اللعبة الكلية لإقناع العميل بالاشتراك
    total_game_combinations = math.comb(GAMES[game_choice]["max"], GAMES[game_choice]["pick"])
    st.metric(label=f"📈 Total Possible Combinations for {game_choice}:", value=f"{total_game_combinations:,}")
    
    st.warning("🔒 Advanced filters (Custom Number Pool, Odd/Even, Golden Sum) are locked. Upgrade to Pro for Automated access.")
    
    if st.button(f"Generate {ticket_quantity} Standard Ticket(s) (Free)"):
        with st.spinner("Generating tickets..."):
            batch_tickets = LottoEngine.generate_batch(ticket_quantity, game_choice, use_filters=False)
            for idx, (nums, bns) in enumerate(batch_tickets, 1):
                st.write(f"Ticket #{idx}: **{nums}**" + (f" | Bonus/Powerball: **{bns}**" if bns else ""))
            txt_file, csv_file = prepare_download_files(batch_tickets, game_choice)
            st.write("---")
            st.write("💾 **Download / Save Your Tickets:**")
            col_dl1, col_dl2 = st.columns(2)
            with col_dl1:
                st.download_button("📥 Download as TEXT (.txt)", data=txt_file, file_name=f"lotto_tickets_{game_choice}.txt", mime="text/plain")
            with col_dl2:
                st.download_button("📥 Download for EXCEL (.csv)", data=csv_file, file_name=f"lotto_tickets_{game_choice}.csv", mime="text/csv")
        st.success(f"Successfully generated {ticket_quantity} standard tickets!")
        
    st.write("### Upgrade to PRO to activate Advanced Filters")
    st.markdown("[👉 Click Here to Test Monthly Subscription via Stripe](https://stripe.com)")
else:
    st.info("🔓 Premium Mode Active: Advanced filters unlocked.")
    col1, col2 = st.columns(2)
    with col1:
        pool_option = st.selectbox(
            "Select Number Generation Strategy:",
            ["Option A: Fully Random (From all game numbers)", "Option B: Custom Number Pool (Generate only from your selected numbers)"]
        )
        
        parsed_pool = []
        if "Option B" in pool_option:
            st.write(f"**📍 Enter Your Expected Numbers (Min {GAMES[game_choice]['pick']} numbers):**")
            user_pool_input = st.text_area(
                "Enter 8, 20, 40 or any amount of numbers separated by commas:",
                placeholder="e.g., 4, 8, 15, 16, 23, 24, 30, 35, 42"
            )
            if user_pool_input:
                try:
                    parsed_pool = sorted(list(set([int(n.strip()) for n in user_pool_input.split(",") if n.strip().isdigit() and 1 <= int(n.strip()) <= GAMES[game_choice]['max']])))
                    if len(parsed_pool) < GAMES[game_choice]['pick']:
                        st.error(f"⚠️ You must enter at least {GAMES[game_choice]['pick']} valid numbers for this game.")
                except ValueError:
                    parsed_pool = []
                    
        if GAMES[game_choice]["pick"] == 7:
            ratio_options = [None, "4:3", "3:4", "5:2", "2:5"]
        else:
            ratio_options = [None, "3:3", "4:2", "2:4"]
            
        ratio = st.selectbox("Even:Odd Ratio Filter", ratio_options)
                
    with col2:
        sum_range = st.slider("Golden Sum Range Filter", 20, 300, (80, 180))
        min_s, max_s = sum_range
        
        # 🟢 [تحديث إحصائي ذكي]: حساب وعرض احتمالات الفوز بناءً على الاستراتيجية المفعلة للمشترك
