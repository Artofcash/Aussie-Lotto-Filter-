import streamlit as st
import datetime
import os

def parse_range(value, default_min, default_max):
    """Parse a range string (e.g., '100-140') into min and max values."""
    try:
        if not value or '-' not in value:
            return default_min, default_max
        parts = value.split('-')
        return int(parts[0].strip()), int(parts[1].strip())
    except ValueError:
        return default_min, default_max

def validate_numbers(numbers_str, game_size):
    """Validate and parse user input numbers."""
    try:
        if not numbers_str.strip():
            return None, "❌ Please enter numbers."
        
        numbers = [int(x.strip()) for x in numbers_str.split()]
        
        # Check for duplicates
        if len(numbers) != len(set(numbers)):
            return None, "❌ Duplicate numbers detected. Each number must be unique."
        
        # Check count matches game size
        if len(numbers) != game_size:
            return None, f"❌ Expected {game_size} numbers, got {len(numbers)}."
        
        # Check valid range (Australian lotto is 1-45)
        if any(n < 1 or n > 45 for n in numbers):
            return None, "❌ Numbers must be between 1 and 45."
        
        return sorted(numbers), None
    except ValueError:
        return None, "❌ Invalid input. Please enter numbers separated by spaces."

def calculate_sum(numbers):
    """Calculate sum of numbers."""
    return sum(numbers)

def analyze_decades(numbers):
    """Analyze distribution across decades (1-10, 11-20, etc)."""
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
    """Check if sum is within range."""
    total = calculate_sum(numbers)
    return min_sum <= total <= max_sum, total

def extract_fixed_power(power_str):
    """Extract fixed power numbers from user input."""
    if not power_str.strip():
        return []
    try:
        return [int(x.strip()) for x in power_str.split()]
    except ValueError:
        return []

def run_filter(numbers, game_size, min_sum, max_sum, use_decades, power_numbers):
    """Run the advanced lotto filter and return results."""
    results = {
        "numbers": numbers,
        "sum": calculate_sum(numbers),
        "sum_valid": False,
        "decades": {},
        "has_empty_decades": False,
        "power_numbers": power_numbers,
        "recommendations": []
    }
    
    # Check sum range
    sum_valid, total = filter_by_sum(numbers, min_sum, max_sum)
    results["sum_valid"] = sum_valid
    
    # Analyze decades if requested
    if use_decades:
        decades = analyze_decades(numbers)
        results["decades"] = decades
        results["has_empty_decades"] = 0 in decades.values()
    
    # Generate recommendations
    recommendations = []
    if not sum_valid:
        recommendations.append(f"⚠️ Sum is {total}, which is outside the range {min_sum}-{max_sum}. Consider adjusting.")
    if results["has_empty_decades"]:
        empty_decades = [k for k, v in decades.items() if v == 0]
        recommendations.append(f"📊 Your selection has empty decades: {', '.join(empty_decades)}. Consider adding numbers from these ranges.")
    if power_numbers:
        recommendations.append(f"✨ Power numbers {power_numbers} are included for extra luck!")
    else:
        recommendations.append("💡 You can add power numbers for more combinations.")
    
    results["recommendations"] = recommendations
    return results

# Page config
st.set_page_config(page_title="Aussie Smart Lotto Filter Pro", page_icon="🎰", layout="wide")

# Initialize session state
if "registered_devices" not in st.session_state:
    st.session_state["registered_devices"] = []

if "is_vip" not in st.session_state:
    st.session_state["is_vip"] = False

if "device_id" not in st.session_state:
    st.session_state["device_id"] = None

if "results" not in st.session_state:
    st.session_state["results"] = None

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
    .success-box { 
        background-color: #dcfce7; 
        padding: 15px; 
        border-radius: 5px; 
    }
    .error-box {
        background-color: #fee2e2;
        padding: 15px;
        border-radius: 5px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🎰 Aussie Smart Lotto Filter Pro 📊</div>', unsafe_allow_html=True)

# Sidebar VIP activation
st.sidebar.header("🔑 VIP Membership Activation")
user_code = st.sidebar.text_input("Enter your VIP Code:", type="password", key="vip_input")

# Get VIP code from environment or use default
valid_vip_code = os.getenv("VIP_CODE", "VIP123").upper()

if user_code:
    user_code_clean = user_code.strip().upper()
    
    if user_code_clean == valid_vip_code:
        # Check if device already registered
        if st.session_state["device_id"] and st.session_state["device_id"] in st.session_state["registered_devices"]:
            st.sidebar.success("📅 VIP Subscription Active on this device!")
            st.session_state["is_vip"] = True
        elif len(st.session_state["registered_devices"]) < 2:
            device_id = str(datetime.datetime.now().timestamp())
            st.session_state["registered_devices"].append(device_id)
            st.session_state["device_id"] = device_id
            st.sidebar.success("✅ VIP Subscription Activated on this device!")
            st.session_state["is_vip"] = True
        else:
            st.sidebar.error("❌ Device limit reached for this code (Max 2 devices).")
            st.session_state["is_vip"] = False
    else:
        st.sidebar.error("❌ Invalid Code. Please check your receipt.")
        st.session_state["is_vip"] = False

# Display VIP status
if st.session_state["is_vip"]:
    st.sidebar.markdown("### ⭐ VIP Status: **ACTIVE**")
    st.sidebar.write(f"Device ID: `{st.session_state['device_id'][:10]}...`")
    st.sidebar.write(f"Devices Registered: {len(st.session_state['registered_devices'])}/2")
else:
    st.sidebar.markdown("### 🔒 VIP Status: **INACTIVE**")

# Main input section
st.header("📋 Core Number Selection (FREE Tier)")
col1, col2 = st.columns([3, 1])

with col1:
    numbers_input = st.text_input(
        "Enter your main numbers (separated by spaces, e.g., 5 12 23 34 45):",
        key="numbers_input"
    )

with col2:
    game_size = st.selectbox("Game Size:", [6, 7], index=0, key="game_size")

# Advanced filters (VIP)
st.header("💎 Advanced Statistical Filters (VIP Tier)")

if st.session_state["is_vip"]:
    st.markdown('<div class="vip-box">⚡ Premium Features Unlocked Successfully!</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        sum_range_input = st.text_input(
            "Golden Sum Range (e.g., 100-140):", 
            "100-140",
            key="sum_range"
        )
        min_sum, max_sum = parse_range(sum_range_input, 100, 140)
    
    with col2:
        fixed_power = st.text_input(
            "Fixed Power Numbers (Optional, e.g., 7 14):",
            key="fixed_power"
        )
    
    empty_decades = st.checkbox(
        "Enable Empty Decades Analysis",
        key="empty_decades"
    )
    
    # Button to run filter
    if st.button("Run Advanced Lotto Filter 🚀", type="primary", key="run_filter"):
        if numbers_input:
            numbers, error = validate_numbers(numbers_input, game_size)
            if error:
                st.error(error)
            else:
                power_numbers = extract_fixed_power(fixed_power)
                st.session_state["results"] = run_filter(
                    numbers, 
                    game_size, 
                    min_sum, 
                    max_sum, 
                    empty_decades, 
                    power_numbers
                )
        else:
            st.warning("⚠️ Please enter your numbers first.")
    
    # Display results if available
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
        
        # Decade distribution chart
        if results["decades"]:
            st.subheader("📊 Decade Distribution")
            st.bar_chart(results["decades"])
        
        # Recommendations
        if results["recommendations"]:
            st.subheader("💡 Recommendations")
            for i, rec in enumerate(results["recommendations"], 1):
                st.write(f"{i}. {rec}")
        
        # Export option
        st.subheader("📥 Export Results")
        if st.button("Clear Results", key="clear_results"):
            st.session_state["results"] = None
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

else:
    st.info("🔒 Advanced Filters are locked. Activate VIP Tier via Monthly Membership ($15) or Lifetime Access ($99) to unlock.")
    
    # Show what VIP users get
    with st.expander("📌 See VIP Features"):
        st.write("""
        ✨ **VIP Features Include:**
        - 🎯 Advanced Sum Range Filtering
        - 📊 Decade Distribution Analysis
        - ⚡ Power Number Selection
        - 💡 Smart Recommendations
        - 📈 Statistical Insights
        - 🔄 Multiple Device Support (Max 2)
        """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>🎰 Aussie Smart Lotto Filter Pro | Version 2.0</p>
    <p>For support, contact: support@aussielottofilter.com</p>
</div>
""", unsafe_allow_html=True)
