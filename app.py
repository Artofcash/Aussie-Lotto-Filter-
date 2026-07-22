import streamlit as st
import itertools
import random

# --- STYLES & CONFIGURATION ---
st.set_page_config(page_title="Aussie Smart Lotto Filter", page_icon="📊", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #f9f9f9; }
    h1 { color: #1e3a8a; text-align: center; font-family: 'Arial', sans-serif; }
    .stButton>button { width: 100%; background-color: #10b981; color: white; font-weight: bold; height: 3em; border-radius: 8px; }
    .stButton>button:hover { background-color: #059669; }
    .vip-lock { background-color: #fef3c7; padding: 15px; border-left: 5px solid #d97706; border-radius: 5px; margin-bottom: 15px; }
    </style>
""", unsafe_allowed_html=True)

st.title("📊 Aussie Smart Lotto Filter Pro")
st.write("Optimize your numbers, eliminate low-probability combinations, and catch the prize with fewer games!")

# --- CORE MATHEMATICAL ENGINE ---
def is_natural(combo):
    for i in range(len(combo)-2):
        if combo[i] + 1 == combo[i+1] and combo[i+1] + 1 == combo[i+2]:
            return False
    for i in range(len(combo)-1):
        if (combo[i+1] - combo[i]) > 18: return False
    return True

def count_empty_decades(combo):
    decades = {0:0, 1:0, 2:0, 3:0, 4:0}
    for n in combo:
        decades[n // 10] += 1
    return list(decades.values()).count(0)

# --- USER INPUTS (FREE SECTION) ---
st.header("1. Core Numbers Selection")
nums_str = st.text_input("Enter your pool of numbers (Separated by space):", placeholder="e.g. 5 12 19 23 34 40 45")

col1, col2 = st.columns(2)
with col1:
    sys_size = st.number_input("Game/System Size (6 for Saturday Lotto, 7 for Powerball):", min_value=1, max_value=20, value=7)
with col2:
    odd_range = st.text_input("Odd Numbers Filter (e.g. 3-4):", placeholder="e.g. 3-4")

# --- PRO / VIP PREMIUM FILTERS (LOCK SYSTEM) ---
st.header("2. Advanced Mathematical Filters (VIP)")

# VIP Protection Mechanism
is_vip = False
vip_password = st.text_input("🔑 VIP Password (Leave blank to use Free Version Only):", type="password")

# --- PASSWORD CONFIGURATION ---
# يمكنك تغيير كلمة المرور أدناه لأي كلمة تريدها، وسيحصل عليها المستخدم بعد الدفع تلقائياً
if vip_password == "AussieLottoVIP2026":
    is_vip = True
    st.success("✅ VIP Filters Unlocked Successfully!")
else:
    if vip_password:
        st.error("❌ Incorrect VIP Password. Using Free Filters Only.")
    st.markdown("""
        <div class="vip-lock">
            <strong>🔒 Premium Filters Locked</strong><br>
            Filters like <i>Golden Sum Range</i>, <i>Empty Decades Analysis</i>, and <i>Fixed Power Numbers</i> are exclusive to VIP members.<br>
            <a href="https://gumroad.com" target="_blank"><strong>Click here to Unlock all VIP features instantly for just $15!</strong></a>
        </div>
    """, unsafe_allowed_html=True)

# Render inputs based on VIP status
if is_vip:
    sum_range = st.text_input("🏆 Golden Sum Range Filter (e.g. 100-150):", placeholder="100-150")
    empty_req = st.number_input("🏆 Empty Decades Required (0-2):", min_value=0, max_value=2, value=0)
    fixed_in = st.text_input("🏆 Fixed Power Numbers (Must be in all tickets):", placeholder="e.g. 7 19")
else:
    # Default values for free version (Hidden filters)
    sum_range = ""
    empty_req = 0
    fixed_in = ""
    st.text_input("🏆 Golden Sum Range Filter (VIP Only):", placeholder="🔒 Locked", disabled=True)
    st.number_input("🏆 Empty Decades Required (VIP Only):", min_value=0, max_value=2, value=0, disabled=True)
    st.text_input("🏆 Fixed Power Numbers (VIP Only):", placeholder="🔒 Locked", disabled=True)

limit_val = st.text_input("Max Tickets to Generate (Optional):", placeholder="e.g. 50")

# --- GENERATION PROCESS ---
if st.button("🚀 Optimize & Generate Tickets Now"):
    if not nums_str:
        st.error("Please enter your numbers first!")
    else:
        try:
            selected_numbers = sorted([int(x) for x in nums_str.split()])
            fixed_nums = [int(x) for x in fixed_in.split()] if fixed_in else []
            limit = int(limit_val) if limit_val else None

            all_combos = itertools.combinations(selected_numbers, sys_size)
            valid_tickets = []

            for combo in all_combos:
                if fixed_nums and not all(n in combo for n in fixed_nums): continue
                if sum_range:
                    mi, ma = map(int, sum_range.split('-'))
                    if not (mi <= sum(combo) <= ma): continue
                if odd_range:
                    mi_o, ma_o = (map(int, odd_range.split('-'))) if '-' in odd_range else (int(odd_range), int(odd_range))
                    odd_c = len([n for n in combo if n % 2 != 0])
                    if not (mi_o <= odd_c <= ma_o): continue
                
                if not is_natural(combo): continue
                if empty_req > 0 and count_empty_decades(combo) < empty_req: continue
                valid_tickets.append(combo)

            if limit and len(valid_tickets) > limit:
                valid_tickets = random.sample(valid_tickets, limit)
                valid_tickets.sort()

            # Output results to web screen
            st.success(f"✨ Successfully Generated {len(valid_tickets)} Smart Tickets!")
            
            # Format output for copy/paste
            results_text = f"--- Aussie Smart Lotto Filter Results ---\nTotal Tickets: {len(valid_tickets)}\n\n"
            for i, t in enumerate(valid_tickets, 1):
                results_text += f"TICKET {i:03d}: {list(t)}\n"
            
            st.text_area("📋 Your Smart Tickets (Copy and Play):", value=results_text, height=300)
            
            # Download button
            st.download_button(
                label="📥 Download Results as TXT File",
                data=results_text,
                file_name="Aussie_Smart_Lotto_Results.txt",
                mime="text/plain"
            )

        except Exception as e:
            st.error(f"Error processing your data. Please ensure format is correct. Error: {e}")
