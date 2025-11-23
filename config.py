import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent

# Database Configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '',  # Change this to your MySQL password
    'database': 'grocery_store_db',
    'charset': 'utf8mb4',
    'autocommit': False,
    'pool_name': 'grocery_pool',
    'pool_size': 5
}

# Application Settings
APP_CONFIG = {
    'app_name': 'Grocery Store Management System',
    'version': '1.0.0',
    'window_size': '1400x800',
    'min_window_size': (1200, 700)
}

# Tax and Discount Settings
BUSINESS_CONFIG = {
    'tax_rate': 0.12,  # 12% VAT
    'currency_symbol': '₱',  # Philippine Peso
    'discount_max': 0.50,  # Maximum 50% discount
    'low_stock_threshold': 10
}

# Security Settings
SECURITY_CONFIG = {
    'bcrypt_rounds': 12,
    'session_timeout': 3600,  # 1 hour in seconds
    'max_login_attempts': 5
}

# Logging Configuration
LOG_CONFIG = {
    'log_dir': BASE_DIR / 'logs',
    'log_file': 'activity.log',
    'max_size': 10 * 1024 * 1024,  # 10 MB
    'backup_count': 5,
    'log_level': 'INFO'
}

# PDF Settings
PDF_CONFIG = {
    'company_name': 'Grocery Store Inc.',
    'company_address': '123 Main Street, City, Country',
    'company_phone': '+1 234 567 8900',
    'company_email': 'info@grocerystore.com',
    'logo_path': None  # Set path to logo image if available
}

# UI Theme Colors
COLORS = {
    'primary': '#2c3e50',
    'secondary': '#34495e',
    'success': '#27ae60',
    'danger': '#e74c3c',
    'warning': '#f39c12',
    'info': '#3498db',
    'light': '#ecf0f1',
    'dark': '#2c3e50',
    'white': '#ffffff',
    'background': '#f5f6fa',
    'text': '#2c3e50',
    'text_light': '#7f8c8d'
}

# Fonts
FONTS = {
    'family': 'Segoe UI',
    'size_small': 9,
    'size_normal': 10,
    'size_medium': 12,
    'size_large': 14,
    'size_title': 18,
    'size_header': 24
}

# Create necessary directories
def initialize_directories():
    """Create necessary directories if they don't exist"""
    directories = [
        LOG_CONFIG['log_dir'],
        BASE_DIR / 'reports',
        BASE_DIR / 'receipts'
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

# Initialize on import
initialize_directories()