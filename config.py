import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables if .env exists
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / '.env')

class Config:
    """Base configuration for API SENTINEL SOC Platform."""
    SECRET_KEY = os.getenv('SECRET_KEY', 'sentinel_enterprise_soc_secret_key_prod_v2')
    
    # SQLite Database configuration in instance directory
    INSTANCE_DIR = BASE_DIR / 'instance'
    INSTANCE_DIR.mkdir(parents=True, exist_ok=True)
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', f'sqlite:///{INSTANCE_DIR / "api_sentinel.db"}')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Security and session settings
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max payload limit
    
    # Risk Score Thresholds
    RISK_LOW_MAX = 29
    RISK_MEDIUM_MAX = 59
    RISK_HIGH_MAX = 79
    RISK_CRITICAL_MIN = 80
    
    # Demo credentials for easy testing and evaluation
    DEMO_USERS = {
        'admin': {
            'password': 'Sentinel@2025',
            'role': 'SOC Administrator',
            'name': 'Chief Security Officer'
        },
        'analyst': {
            'password': 'Analyst@2025',
            'role': 'Security Analyst',
            'name': 'Lead Threat Hunter'
        }
    }

