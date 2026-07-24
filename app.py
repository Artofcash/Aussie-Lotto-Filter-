import streamlit as st
import datetime
import hashlib

def parse_range(value, default_min, default_max):
    try:
        if not value or '-' not in value:
            return default_min, default_max
        parts = value.split('-')
        return int(parts[0].strip()), int(parts[1].strip())
    except:
        return default_min, default_max

st.set_page_config(page_title="Aussie Smart Lotto Filter Pro", page_icon="🎰", layout="wide")

if "registered_devices" not in st.session_state:
    st.session_state["registered_devices"] = set()

st.markdown("""
    <style>
    .main-title { text-align: center; color: #1e3a8a; font-size: 40px; font-weight: bold; margin-bottom: 20px; }
    .vip-box { background-color: #fef3c7; padding: 15px; border-left: 5px solid #d97706; border-radius: 5px; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🎰 Aussie Smart Lotto Filter Pro 📊</div>', unsafe_allow_html=True)

st.sidebar.header("🔑 VIP Membership Activation")
user_code = st.sidebar.text_input("Enter your VIP Code:", type="password")

is_vip = False
if user_code:
    user_code_clean = user_code.strip().upper()
    
    if user_code_clean == "VIP":
        if "default_user" in st.session_state["registered_devices"] or len(st.session_state["registered_devices"]) < 2:
            st.session_state["registered_devices"].add("default_user")
            st.sidebar.success("📅 VIP Subscription Active!")
            is_vip = True
        else:
            st.sidebar.error("❌ Device limit reached for this code (Max 2 devices).")
    else:
        st.sidebar.error("❌ Invalid Code. Please check your receipt.")

st.header("📋 Core Number Selection (FREE Tier)")
numbers_input = st.text_input("Enter your main numbers (separated by spaces, e.g., 5 12 23 34 45):")
game_size = st.selectbox("Select Game/System Size:", [6, 7], index=0)

st.header("💎 Advanced Statistical Filters (VIP Tier)")

if is_vip:
    st.markdown('<div class="vip-box">⚡ Premium Features Unlocked Successfully!</div>', unsafe_allow_html=True)
    sum_range_input = st.text_input("Golden Sum Range (e.g., 100-140):", "100-140")
    min_sum, max_sum = parse_range(sum_range_input, 100, 140)
    empty_decades = st.checkbox("Enable Empty Decades Analysis")
    fixed_power = st.text_input("Fixed Power Numbers (Optional):")
    st.button("Run Advanced Lotto Filter 🚀")
else:
    st.info("🔒 Advanced Filters are locked. Activate VIP Tier via Monthly Membership ($15) or Lifetime Access ($99) to unlock.")
