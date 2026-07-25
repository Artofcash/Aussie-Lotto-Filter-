import streamlit as st
import pandas as pd
import os
from datetime import datetime
import json

# =====================
# إعدادات Streamlit
# =====================
st.set_page_config(
    page_title="🎰 منقي اليانصيب الأسترالي",
    page_icon="🎰",
    layout="centered",
    initial_sidebar_state="expanded"
)

# =====================
# CSS للموبايل والتنسيق
# =====================
st.markdown("""
<style>
    /* الخط الأساسي */
    body {
        font-family: 'Arial', sans-serif;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* العناوين */
    h1, h2, h3 {
        color: #667eea;
        text-align: center;
        font-weight: bold;
    }
    
    /* صناديق النتائج */
    .result-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* أزرار */
    button {
        background-color: #667eea !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 10px 20px !important;
        font-size: 16px !important;
        cursor: pointer;
    }
    
    button:hover {
        background-color: #764ba2 !important;
    }
    
    /* الإدخال */
    input, textarea, select {
        border-radius: 8px !important;
        padding: 10px !important;
        font-size: 14px !important;
    }
    
    /* الموبايل (شاشات أقل من 768px) */
    @media (max-width: 768px) {
        h1 { font-size: 24px !important; }
        h2 { font-size: 20px !important; }
        p { font-size: 14px !important; }
        button { font-size: 14px !important; }
        .result-box { padding: 15px !important; }
    }
    
    /* الموبايل الصغير جداً (أقل من 480px) */
    @media (max-width: 480px) {
        h1 { font-size: 20px !important; }
        h2 { font-size: 16px !important; }
        p { font-size: 12px !important; }
        button { font-size: 12px !important; padding: 8px 15px !important; }
    }
</style>
""", unsafe_allow_html=True)

# =====================
# المتغيرات العامة
# =====================
VIP_CODES_FILE = "vip_codes.json"
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# =====================
# دوال إضافية
# =====================

def load_vip_codes():
    """تحميل رموز VIP من JSON"""
    if os.path.exists(VIP_CODES_FILE):
        try:
            with open(VIP_CODES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_vip_codes(data):
    """حفظ رموز VIP إلى JSON"""
    with open(VIP_CODES_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def send_email(recipient_email, subject, message):
    """إرسال بريد إلكتروني عبر Yahoo SMTP"""
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        st.error("❌ لم يتم تكوين بيانات البريد الإلكتروني")
        return False
    
    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(message, 'plain', 'utf-8'))
        
        server = smtplib.SMTP('smtp.mail.yahoo.com', 587)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        return True
    except Exception as e:
        st.error(f"❌ خطأ في إرسال البريد: {str(e)}")
        return False

def filter_numbers(numbers, exclude_list, include_list):
    """تصفية الأرقام بناءً على القوائم"""
    numbers = [n for n in numbers if n not in exclude_list]
    
    if include_list:
        numbers = [n for n in numbers if n in include_list]
    
    return sorted(numbers)

# =====================
# الواجهة الرئيسية
# =====================

st.title("🎰 منقي اليانصيب الأسترالي")
st.markdown("---")

# التبويبات
tab1, tab2, tab3, tab4 = st.tabs(["🎯 المرشح", "📊 الإحصائيات", "🔐 أدمن", "ℹ️ معلومات"])

# =====================
# التبويب الأول: المرشح
# =====================
with tab1:
    st.header("🎯 منقي الأرقام")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("ℹ️ المدخلات")
        lottery_type = st.selectbox(
            "اختر نوع اليانصيب:",
            ["Powerball", "Oz Lotto", "Saturday Lotto", "Wednesday Lotto"]
        )
        
        exclude_input = st.text_input(
            "أدخل الأرقام المستثناة (مفصولة بفواصل):",
            placeholder="مثال: 1,2,3"
        )
        
        include_input = st.text_input(
            "أدخل الأرقام المفضلة (اتركها فارغة للكل):",
            placeholder="مثال: 5,10,15"
        )
    
    with col2:
        st.subheader("🎲 النتائج")
        
        if st.button("🔄 تصفية الأرقام", use_container_width=True):
            try:
                # تحديد نطاق الأرقام حسب نوع اليانصيب
                if lottery_type == "Powerball":
                    max_num = 35
                elif lottery_type == "Oz Lotto":
                    max_num = 45
                else:
                    max_num = 45
                
                all_numbers = list(range(1, max_num + 1))
                
                # معالجة المدخلات
                exclude_list = [int(x.strip()) for x in exclude_input.split(',') if x.strip()]
                include_list = [int(x.strip()) for x in include_input.split(',') if x.strip()] if include_input else []
                
                filtered = filter_numbers(all_numbers, exclude_list, include_list)
                
                # عرض النتائج
                st.markdown(f"""
                <div class="result-box">
                    <h3>✅ النتائج المصفاة</h3>
                    <p><strong>الأرقام:</strong> {', '.join(map(str, filtered))}</p>
                    <p><strong>العدد الكلي:</strong> {len(filtered)} أرقام</p>
                </div>
                """, unsafe_allow_html=True)
                
            except ValueError:
                st.error("❌ تأكد من إدخال أرقام صحيحة مفصولة بفواصل")

# =====================
# التبويب الثاني: الإحصائيات
# =====================
with tab2:
    st.header("📊 الإحصائيات")
    st.write("سيتم إضافة رسوم بيانية هنا قريباً...")

# =====================
# التبويب الثالث: أدمن
# =====================
with tab3:
    st.header("🔐 لوحة التحكم")
    
    password_input = st.text_input("أدخل كلمة المرور:", type="password")
    
    if password_input == ADMIN_PASSWORD:
        st.success("✅ تم تسجيل الدخول بنجاح")
        
        admin_tab1, admin_tab2 = st.tabs(["💳 رموز VIP", "📧 إرسال بريد"])
        
        # إدارة رموز VIP
        with admin_tab1:
            st.subheader("إدارة رموز VIP")
            
            col1, col2 = st.columns(2)
            
            with col1:
                new_code = st.text_input("أدخل رمز VIP جديد:")
                code_email = st.text_input("البريد الإلكتروني المرتبط:")
                
                if st.button("➕ إضافة رمز VIP"):
                    if new_code and code_email:
                        vip_codes = load_vip_codes()
                        vip_codes[new_code] = {
                            "email": code_email,
                            "created": datetime.now().isoformat(),
                            "used": False
                        }
                        save_vip_codes(vip_codes)
                        st.success(f"✅ تم إضافة الرمز: {new_code}")
                    else:
                        st.error("❌ أملأ جميع الحقول")
            
            with col2:
                st.subheader("رموز VIP الحالية")
                vip_codes = load_vip_codes()
                if vip_codes:
                    for code, data in vip_codes.items():
                        status = "✅ مستخدم" if data.get("used") else "⏳ جديد"
                        st.write(f"**{code}** - {data.get('email')} ({status})")
                else:
                    st.info("لا توجد رموز VIP حالياً")
        
        # إرسال بريد
        with admin_tab2:
            st.subheader("📧 إرسال بريد جماعي")
            
            recipient = st.text_input("البريد الإلكتروني:")
            subject = st.text_input("الموضوع:")
            message = st.text_area("الرسالة:")
            
            if st.button("📤 إرسال"):
                if send_email(recipient, subject, message):
                    st.success("✅ تم إرسال البريد بنجاح")
                else:
                    st.error("❌ فشل إرسال البريد")
    
    elif password_input:
        st.error("❌ كلمة المرور غير صحيحة")

# =====================
# التبويب الرابع: معلومات
# =====================
with tab4:
    st.header("ℹ️ معلومات التطبيق")
    st.write("""
    ### 🎯 الميزات:
    - ✅ تصفية أرقام اليانصيب
    - ✅ إدارة رموز VIP
    - ✅ إرسال بريد إلكتروني
    - ✅ واجهة صديقة للموبايل
    
    ### 📱 التوافق:
    - العمل على الموبايل والكمبيوتر
    - تصميم متجاوب (Responsive)
    
    ### 🔒 الأمان:
    - استخدام متغيرات البيئة للبيانات الحساسة
    - حفظ آمن لرموز VIP
    """)
    
    st.markdown("---")
    st.write("**النسخة:** 1.0.0")
    st.write(f"**آخر تحديث:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
