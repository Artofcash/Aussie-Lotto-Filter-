import streamlit as st
import datetime
import os
import json
import uuid
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time

# ============================================
# 📧 Email Configuration
# ============================================

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS", "legendoflove3@yahoo.com")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")
ADMIN_PASSWORD = "Art Cash 1B$$$"

# ============================================
# 💾 Local Database (JSON)
# ============================================

VIP_CODES_FILE = "vip_codes.json"

def load_vip_codes():
    """Load VIP codes from file"""
    if os.path.exists(VIP_CODES_FILE):
        with open(VIP_CODES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"codes": [], "subscribers": [], "logs": []}

def save_vip_codes(data):
    """Save VIP codes to file"""
    with open(VIP_CODES_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def generate_unique_vip_code():
    """Generate a unique VIP code"""
    return f"VIP-{uuid.uuid4().hex[:12].upper()}"

# ============================================
# 📧 Send Email
# ============================================

def send_vip_code_email(customer_email, customer_name, vip_code):
    """Send VIP code to customer via email"""
    try:
        subject = "🎰 Your Aussie Lotto Filter Pro VIP Code"
        
        body = f"""
        <html>
            <body style="font-family: Arial; text-align: left;">
                <h2>🎉 Hello {customer_name}!</h2>
                
                <p>Thank you for subscribing to <strong>Aussie Lotto Filter Pro</strong></p>
                
                <h3>Your Exclusive VIP Code:</h3>
                <div style="background-color: #f0f0f0; padding: 20px; border-radius: 10px; text-align: center;">
                    <h1 style="color: #1e3a8a; font-family: monospace; letter-spacing: 2px;">{vip_code}</h1>
                </div>
                
                <h3>How to Use Your Code:</h3>
                <ol>
                    <li>Open the app: <a href="https://aussie-lotto-filter-.streamlit.app">https://aussie-lotto-filter-.streamlit.app</a></li>
                    <li>In the Sidebar, click "🔓 Unlock VIP"</li>
                    <li>Enter your code above</li>
                    <li>Enjoy all premium features! ✨</li>
                </ol>
                
                <h3>Your Premium Features:</h3>
                <ul>
                    <li>🎯 Advanced Number Filtering</li>
                    <li>📊 Decade Distribution Analysis</li>
                    <li>⚡ Power Number Selection</li>
                    <li>💡 Smart Recommendations</li>
                    <li>📈 Advanced Statistics</li>
                    <li>🔄 Support for 2 Devices</li>
                </ul>
                
                <h3>Important Notes:</h3>
                <ul>
                    <li>Your code is valid on up to 2 devices</li>
                    <li>Keep this code confidential</li>
                    <li>Do not share this code with others</li>
                </ul>
                
                <p>If you have any questions, please contact us at: legendoflove3@yahoo.com</p>
                
                <hr>
                <p style="color: #666; font-size: 12px;">
                    🎰 Aussie Lotto Filter Pro | Version 3.0 Professional<br>
                    Advanced Lottery Analysis System
                </p>
            </body>
        </html>
        """
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = customer_email
        
        part = MIMEText(body, 'html', 'utf-8')
        msg.attach(part)
        
        # Send via Yahoo SMTP
        with smtplib.SMTP('smtp.mail.yahoo.com', 587) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
        
        return True
    except Exception as e:
        st.warning(f"⚠️ Email not sent: {str(e)}")
        return False

# ============================================
# 🔄 Original Filtering Functions
# ============================================

def parse_range(value, default_min, default_max):
    """Parse a range string (e.g., '100-140')"""
    try:
        if not value or '-' not in value:
            return default_min, default_max
        parts = value.split('-')
        return int(parts[0].strip()), int(parts[1].strip())
    except ValueError:
        return default_min, default_max

def validate_numbers(numbers_str, game_size):
    """Validate user input numbers"""
    try:
        if not numbers_str.strip():
            return None, "❌ Please enter numbers."
        
        numbers = [int(x.strip()) for x in numbers_str.split()]
        
        if len(numbers) != len(set(numbers)):
            return None, "❌ Duplicate numbers detected."
        
        if len(numbers) != game_size:
            return None, f"❌ Expected {game_size} numbers, got {len(numbers)}."
        
        if any(n < 1 or n > 45 for n in numbers):
            return None, "❌ Numbers must be between 1-45."
        
        return sorted(numbers), None
    except ValueError:
        return None, "❌ Invalid input."

def calculate_sum(numbers):
    return sum(numbers)

def analyze_decades(numbers):
    decade_counts = {
        '1-10': 0, '11-20': 0, '21-30': 0, '31-40': 0, '41-45': 0
    }
    for num in numbers:
        if num <= 10:
            decade_counts['1-10'] += 1
        elif num <= 20:
            decade_counts['11-20'] += 1
        elif num <= 30:
            decade_counts['21-30'] += 1
        elif num <= 40:
            decade_counts['31-40'] += 1
        else:
            decade_counts['41-45'] += 1
    return decade_counts

def filter_by_sum(numbers, min_sum, max_sum):
    total = calculate_sum(numbers)
    return min_sum <= total <= max_sum, total

def extract_fixed_power(power_str):
    if not power_str.strip():
        return []
    try:
        return [int(x.strip()) for x in power_str.split()]
    except ValueError:
        return []

def run_filter(numbers, game_size, min_sum, max_sum, use_decades, power_numbers):
    results = {
        "numbers": numbers,
        "sum": calculate_sum(numbers),
        "sum_valid": False,
        "decades": {},
        "has_empty_decades": False,
        "power_numbers": power_numbers,
        "recommendations": []
    }
    
    sum_valid, total = filter_by_sum(numbers, min_sum, max_sum)
    results["sum_valid"] = sum_valid
    
    if use_decades:
        decades = analyze_decades(numbers)
        results["decades"] = decades
        results["has_empty_decades"] = 0 in decades.values()
    
    recommendations = []
    if not sum_valid:
        recommendations.append(f"⚠️ Sum is {total}, outside range {min_sum}-{max_sum}.")
    if results["has_empty_decades"]:
        empty_decades = [k for k, v in decades.items() if v == 0]
        recommendations.append(f"📊 Empty decades: {', '.join(empty_decades)}.")
    if power_numbers:
        recommendations.append(f"✨ Power numbers selected: {power_numbers}")
    else:
        recommendations.append("💡 Add power numbers for extra combinations.")
    
    results["recommendations"] = recommendations
    return results

# ============================================
# 🎨 Main Interface
# ============================================

st.set_page_config(page_title="Aussie Smart Lotto Filter Pro", page_icon="🎰", layout="wide")

# Initialize session state
if "is_vip" not in st.session_state:
    st.session_state["is_vip"] = False
if "results" not in st.session_state:
    st.session_state["results"] = None
if "vip_code" not in st.session_state:
    st.session_state["vip_code"] = None

st.markdown("""
    <style>
    .main-title { 
        text-align: center; 
        color: #1e3a8a; 
        font-size: 40px; 
        font-weight: bold; 
        margin-bottom: 20px; 
    }
    .vip-box { 
        background-color: #fef3c7; 
        padding: 15px; 
        border-left: 5px solid #d97706; 
        border-radius: 5px; 
        margin-bottom: 20px; 
    }
    .results-box { 
        background-color: #dbeafe; 
        padding: 15px; 
        border-radius: 5px; 
        margin-top: 20px;
        border-left: 5px solid #0284c7;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🎰 Aussie Smart Lotto Filter Pro 📊</div>', unsafe_allow_html=True)

# ============================================
# 📍 Sidebar
# ============================================

st.sidebar.header("🔑 VIP Membership")

# Login button
if st.sidebar.button("🔓 Unlock VIP", use_container_width=True):
    st.session_state["show_login"] = True

if st.session_state.get("show_login", False):
    user_code = st.sidebar.text_input(
        "Enter Your VIP Code:",
        type="password",
        key="vip_input"
    )
    
    if user_code:
        data = load_vip_codes()
        code_found = False
        
        for code_info in data.get("codes", []):
            if code_info["code"].upper() == user_code.upper():
                if code_info.get("is_active", True):
                    st.sidebar.success("✅ VIP Activated!")
                    st.session_state["is_vip"] = True
                    st.session_state["vip_code"] = user_code.upper()
                    code_found = True
                    break
                else:
                    st.sidebar.error("❌ Code is inactive")
                    code_found = True
                    break
        
        if not code_found:
            st.sidebar.error("❌ Invalid code")

# VIP Status
if st.session_state["is_vip"]:
    st.sidebar.markdown("### ⭐ Status: **ACTIVE**")
    st.sidebar.write(f"Code: `{st.session_state['vip_code'][:10]}...`")
    if st.sidebar.button("🚪 Logout"):
        st.session_state["is_vip"] = False
        st.session_state["vip_code"] = None
        st.rerun()
else:
    st.sidebar.markdown("### 🔒 Status: **INACTIVE**")

# Admin Panel
with st.sidebar.expander("👨‍💼 Admin Panel"):
    admin_pass = st.text_input("Admin Password:", type="password", key="admin_pass")
    
    if admin_pass == ADMIN_PASSWORD:
        st.success("✅ Welcome Admin!")
        
        # ====== Add New Subscriber ======
        st.subheader("➕ Add New Subscriber")
        
        col1, col2 = st.columns(2)
        with col1:
            subscriber_name = st.text_input("Subscriber Name:")
        with col2:
            subscriber_email = st.text_input("Subscriber Email:")
        
        col1, col2 = st.columns(2)
        with col1:
            plan_type = st.selectbox("Plan Type:", ["Monthly ($15)", "Lifetime ($99)"])
        with col2:
            max_devices = st.selectbox("Max Devices:", [1, 2, 3])
        
        if st.button("✅ Add Subscriber & Send Code", key="add_subscriber"):
            if subscriber_name and subscriber_email:
                # Generate unique code
                vip_code = generate_unique_vip_code()
                
                # Save subscriber and code
                data = load_vip_codes()
                
                # Add code
                data["codes"].append({
                    "code": vip_code,
                    "customer_name": subscriber_name,
                    "customer_email": subscriber_email,
                    "plan_type": plan_type,
                    "max_devices": max_devices,
                    "is_active": True,
                    "created_at": datetime.datetime.now().isoformat(),
                    "expires_at": None if "Lifetime" in plan_type else (datetime.datetime.now() + datetime.timedelta(days=30)).isoformat()
                })
                
                # Add subscriber
                data["subscribers"].append({
                    "name": subscriber_name,
                    "email": subscriber_email,
                    "vip_code": vip_code,
                    "plan_type": plan_type,
                    "joined_at": datetime.datetime.now().isoformat()
                })
                
                save_vip_codes(data)
                
                # Send email
                email_sent = send_vip_code_email(subscriber_email, subscriber_name, vip_code)
                
                if email_sent:
                    st.success(f"✅ Subscriber added and code sent to {subscriber_email}")
                    st.info(f"Code: `{vip_code}`")
                else:
                    st.warning(f"⚠️ Subscriber added but email failed\nCode: `{vip_code}`")
                
                # Log event
                data["logs"].append({
                    "event": "subscriber_added",
                    "subscriber": subscriber_name,
                    "code": vip_code,
                    "timestamp": datetime.datetime.now().isoformat()
                })
                save_vip_codes(data)
            else:
                st.error("❌ Please fill all fields")
        
        # ====== View Active Subscribers ======
        st.subheader("📋 Active Subscribers")
        data = load_vip_codes()
        
        if data.get("codes"):
            st.write(f"**Total Active Codes: {len(data.get('codes', []))}**")
            
            for code in data.get("codes", []):
                if code.get("is_active"):
                    st.write(f"""
                    **👤 {code.get('customer_name')}**
                    - 📧 {code.get('customer_email')}
                    - 🎫 {code.get('code')}
                    - 📅 {code.get('plan_type')}
                    """)
        else:
            st.info("No active codes yet")
        
        # ====== Deactivate Code ======
        st.subheader("🗑️ Deactivate Code")
        code_to_delete = st.text_input("Enter code to deactivate:")
        if st.button("Deactivate"):
            data = load_vip_codes()
            for code in data.get("codes", []):
                if code["code"] == code_to_delete:
                    code["is_active"] = False
                    save_vip_codes(data)
                    st.success("✅ Code deactivated")
                    break
    
    elif admin_pass and admin_pass != ADMIN_PASSWORD:
        st.error("❌ Invalid password")

# ============================================
# 📋 Core Number Selection (FREE)
# ============================================

st.header("📋 Core Number Selection (FREE Tier)")
col1, col2 = st.columns([3, 1])

with col1:
    numbers_input = st.text_input(
        "Enter your numbers (e.g., 5 12 23 34 45):",
        key="numbers_input"
    )

with col2:
    game_size = st.selectbox("Game Size:", [6, 7], index=0)

# ============================================
# 💎 Advanced Filters (VIP)
# ============================================

st.header("💎 Advanced Statistical Filters (VIP Tier)")

if st.session_state["is_vip"]:
    st.markdown('<div class="vip-box">⚡ Premium Features Unlocked!</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        sum_range_input = st.text_input("Golden Sum Range (e.g., 100-140):", "100-140")
        min_sum, max_sum = parse_range(sum_range_input, 100, 140)
    
    with col2:
        fixed_power = st.text_input("Power Numbers (Optional, e.g., 7 14):")
    
    empty_decades = st.checkbox("Enable Empty Decades Analysis")
    
    if st.button("🚀 Run Advanced Filter", type="primary"):
        if numbers_input:
            numbers, error = validate_numbers(numbers_input, game_size)
            if error:
                st.error(error)
            else:
                power_numbers = extract_fixed_power(fixed_power)
                st.session_state["results"] = run_filter(
                    numbers, game_size, min_sum, max_sum, empty_decades, power_numbers
                )
        else:
            st.warning("⚠️ Please enter numbers first")
    
    if st.session_state["results"]:
        results = st.session_state["results"]
        
        st.markdown('<div class="results-box">', unsafe_allow_html=True)
        st.subheader("✅ Filter Results")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Selected Numbers", str(results["numbers"]))
        with col2:
            st.metric("Sum", results["sum"], delta=f"Range: {min_sum}-{max_sum}")
        with col3:
            status = "✅ Valid" if results["sum_valid"] else "⚠️ Out of Range"
            st.metric("Sum Status", status)
        
        if results["decades"]:
            st.subheader("📊 Decade Distribution")
            st.bar_chart(results["decades"])
        
        if results["recommendations"]:
            st.subheader("💡 Recommendations")
            for i, rec in enumerate(results["recommendations"], 1):
                st.write(f"{i}. {rec}")
        
        if st.button("Clear Results"):
            st.session_state["results"] = None
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

else:
    st.info("🔒 Advanced Filters are locked. Subscribe now!")
    
    with st.expander("📌 VIP Features"):
        st.write("""
        ✨ **Premium Features:**
        - 🎯 Advanced Number Filtering
        - 📊 Decade Distribution Analysis
        - ⚡ Power Number Selection
        - 💡 Smart Recommendations
        - 📈 Advanced Statistics
        - 🔄 Support for 2 Devices
        """)

# ============================================
# 📝 Footer
# ============================================

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>🎰 Aussie Lotto Filter Pro | Version 3.0 Professional</p>
    <p>Advanced Lottery Analysis System with Automatic VIP Management</p>
    <p>Support: legendoflove3@yahoo.com</p>
</div>
""", unsafe_allow_html=True)
