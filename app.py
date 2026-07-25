import streamlit as st
import json
import random
import hashlib
import secrets
from datetime import datetime, timedelta
from pathlib import Path
import uuid
import logging
import sqlite3
import os
from dotenv import load_dotenv
import stripe
from functools import wraps
import re
from cryptography.fernet import Fernet
from base64 import urlsafe_b64encode
import hashlib as hl
from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import bcrypt

# ============================================================================
# CONFIGURATION & SECURITY SETUP
# ============================================================================

load_dotenv()

# Page Configuration
st.set_page_config(
    page_title="🎰 Lottery Generator Pro",
    page_icon="🎰",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://yourdomain.com/help",
        "Report a bug": "https://yourdomain.com/support",
        "About": "Professional Lottery Number Generator v2.0"
    }
)

# ============================================================================
# LOGGING SETUP
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('lottery_app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============================================================================
# ENVIRONMENT VARIABLES
# ============================================================================

SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_hex(32))
STRIPE_PUBLIC_KEY = os.getenv("STRIPE_PUBLIC_KEY", "pk_test_xxxx")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "sk_test_xxxx")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123456")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///lottery.db")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_EMAIL = os.getenv("SMTP_EMAIL", "your_email@gmail.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "your_app_password")
APP_URL = os.getenv("APP_URL", "https://yourdomain.com")

stripe.api_key = STRIPE_SECRET_KEY

# ============================================================================
# GAME CONFIGURATION
# ============================================================================

GAMES = {
    "Powerball": {"pick": 7, "max": 35, "bonus": True},
    "Saturday Lotto": {"pick": 6, "max": 45, "bonus": False},
    "Wednesday Lotto": {"pick": 6, "max": 45, "bonus": False},
    "Oz Lotto": {"pick": 7, "max": 47, "bonus": True},
    "Set for Life": {"pick": 7, "max": 44, "bonus": True},
    "TattsLotto": {"pick": 6, "max": 48, "bonus": False}
}

STRONG_NUMBERS = {
    "Powerball": [7, 14, 21, 28, 35],
    "Saturday Lotto": [38, 32, 41, 20, 12],
    "Wednesday Lotto": [38, 32, 41, 20, 12],
    "Oz Lotto": [37, 26, 43, 38, 31],
    "Set for Life": [26, 20, 34, 42, 37],
    "TattsLotto": [38, 32, 41, 20, 12]
}

PRICES = {
    "monthly": 15.00,
    "lifetime": 99.00
}

# ============================================================================
# DATABASE MODELS & INITIALIZATION
# ============================================================================

Base = declarative_base()

class SecurityManager:
    """Advanced security operations"""
    
    def __init__(self):
        self.secret_key = SECRET_KEY.encode()
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt"""
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt(12)).decode()
    
    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """Verify password"""
        try:
            return bcrypt.checkpw(password.encode(), password_hash.encode())
        except:
            return False
    
    @staticmethod
    def generate_secure_token(length: int = 32) -> str:
        """Generate secure token"""
        return secrets.token_urlsafe(length)
    
    def encrypt_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        try:
            kdf = hl.pbkdf2_hmac('sha256', self.secret_key, b'salt', 100000)
            from base64 import urlsafe_b64encode
            key = urlsafe_b64encode(kdf[:32])
            from cryptography.fernet import Fernet
            cipher = Fernet(key)
            return cipher.encrypt(data.encode()).decode()
        except:
            return data
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt data"""
        try:
            kdf = hl.pbkdf2_hmac('sha256', self.secret_key, b'salt', 100000)
            from base64 import urlsafe_b64encode
            key = urlsafe_b64encode(kdf[:32])
            from cryptography.fernet import Fernet
            cipher = Fernet(key)
            return cipher.decrypt(encrypted_data.encode()).decode()
        except:
            return None

security_manager = SecurityManager()

class DatabaseManager:
    """Manage SQLite database"""
    
    def __init__(self, db_path: str = "lottery.db"):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                username TEXT UNIQUE,
                password_hash TEXT,
                email_verified BOOLEAN DEFAULT 0,
                verification_token TEXT,
                plan TEXT DEFAULT 'free',
                vip_code TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        ''')
        
        # VIP Codes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vip_codes (
                code TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                type TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expiry_date TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                is_redeemed BOOLEAN DEFAULT 0,
                redeemed_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # Transactions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                stripe_payment_id TEXT UNIQUE,
                amount REAL NOT NULL,
                currency TEXT DEFAULT 'AUD',
                plan TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # Number generations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS number_generations (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                game TEXT NOT NULL,
                numbers TEXT NOT NULL,
                bonus_number INTEGER,
                filters_used TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # Security logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS security_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                action TEXT NOT NULL,
                ip_address TEXT,
                details TEXT,
                status TEXT DEFAULT 'success',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # Create indexes for performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_vip_codes_user ON vip_codes(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_transactions_user ON transactions(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_generations_user ON number_generations(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_security_logs_user ON security_logs(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_security_logs_created ON security_logs(created_at)')
        
        conn.commit()
        conn.close()
        logger.info("Database initialized successfully")

db = DatabaseManager()

# ============================================================================
# USER AUTHENTICATION & MANAGEMENT
# ============================================================================

class UserManager:
    """Manage user accounts"""
    
    @staticmethod
    def create_user(email: str, password: str = None) -> tuple:
        """Create new user account"""
        try:
            conn = db.get_connection()
            cursor = conn.cursor()
            
            user_id = str(uuid.uuid4())
            verification_token = security_manager.generate_secure_token()
            password_hash = security_manager.hash_password(password) if password else None
            
            cursor.execute('''
                INSERT INTO users (id, email, password_hash, verification_token, plan)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, email, password_hash, verification_token, "free"))
            
            conn.commit()
            conn.close()
            
            logger.info(f"User created: {email}")
            return user_id, verification_token
        except sqlite3.IntegrityError:
            logger.warning(f"Email already exists: {email}")
            return None, None
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            return None, None
    
    @staticmethod
    def get_user(user_id: str) -> dict:
        """Get user by ID"""
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        conn.close()
        return dict(user) if user else None
    
    @staticmethod
    def get_user_by_email(email: str) -> dict:
        """Get user by email"""
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        conn.close()
        return dict(user) if user else None
    
    @staticmethod
    def verify_email(token: str) -> bool:
        """Verify email address"""
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE users 
            SET email_verified = 1, verification_token = NULL
            WHERE verification_token = ?
        ''', (token,))
        affected = cursor.rowcount
        conn.commit()
        conn.close()
        return affected > 0
    
    @staticmethod
    def is_vip_active(user_id: str) -> dict:
        """Check if user has active VIP"""
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM vip_codes 
            WHERE user_id = ? AND is_active = 1 
            AND (expiry_date IS NULL OR expiry_date > datetime('now'))
        ''', (user_id,))
        code = cursor.fetchone()
        conn.close()
        return dict(code) if code else None
    
    @staticmethod
    def update_last_login(user_id: str):
        """Update user last login time"""
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?
        ''', (user_id,))
        conn.commit()
        conn.close()

# ============================================================================
# VIP CODE MANAGEMENT
# ============================================================================

class VIPManager:
    """Manage VIP codes and subscriptions"""
    
    @staticmethod
    def generate_vip_code(user_id: str, plan_type: str) -> str:
        """Generate new VIP code"""
        try:
            conn = db.get_connection()
            cursor = conn.cursor()
            
            code = security_manager.generate_secure_token(12).upper()
            expiry_date = None
            
            if plan_type == "monthly":
                expiry_date = (datetime.now() + timedelta(days=30)).isoformat()
            
            cursor.execute('''
                INSERT INTO vip_codes (code, user_id, type, expiry_date)
                VALUES (?, ?, ?, ?)
            ''', (code, user_id, plan_type, expiry_date))
            
            cursor.execute('UPDATE users SET plan = ?, vip_code = ? WHERE id = ?',
                          (plan_type, code, user_id))
            
            conn.commit()
            conn.close()
            
            logger.info(f"VIP code generated for user: {user_id}")
            return code
        except Exception as e:
            logger.error(f"Error generating VIP code: {str(e)}")
            return None
    
    @staticmethod
    def redeem_vip_code(user_id: str, code: str) -> bool:
        """Redeem VIP code"""
        try:
            conn = db.get_connection()
            cursor = conn.cursor()
            
            # Check code validity
            cursor.execute('''
                SELECT * FROM vip_codes 
                WHERE code = ? AND is_active = 1 
                AND (expiry_date IS NULL OR expiry_date > datetime('now'))
                AND is_redeemed = 0
            ''', (code,))
            
            vip_code = cursor.fetchone()
            if not vip_code:
                conn.close()
                return False
            
            # Update code as redeemed
            cursor.execute('''
                UPDATE vip_codes 
                SET is_redeemed = 1, redeemed_at = CURRENT_TIMESTAMP, user_id = ?
                WHERE code = ?
            ''', (user_id, code))
            
            # Update user plan
            cursor.execute('UPDATE users SET plan = ?, vip_code = ? WHERE id = ?',
                          (vip_code['type'], code, user_id))
            
            conn.commit()
            conn.close()
            
            logger.info(f"VIP code redeemed: {code}")
            return True
        except Exception as e:
            logger.error(f"Error redeeming VIP code: {str(e)}")
            return False

# ============================================================================
# PAYMENT PROCESSING
# ============================================================================

class PaymentManager:
    """Manage payment processing"""
    
    @staticmethod
    def create_checkout_session(user_id: str, plan_type: str, email: str) -> str:
        """Create Stripe checkout session"""
        try:
            amount = PRICES[plan_type]
            
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'aud',
                        'product_data': {
                            'name': f'Lottery Generator Pro - {plan_type.title()} Plan',
                            'description': f'Access all advanced filters for {plan_type}'
                        },
                        'unit_amount': int(amount * 100),
                    },
                    'quantity': 1,
                }],
                metadata={'user_id': user_id, 'plan': plan_type},
                mode='payment',
                success_url=f'{APP_URL}?session_id={{CHECKOUT_SESSION_ID}}',
                cancel_url=APP_URL
            )
            
            logger.info(f"Checkout session created:
