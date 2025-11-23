Grocery Store Management System
A comprehensive Python-based grocery store management system with inventory tracking, point of sale (POS), sales reporting, and user management.
🎯 Features
Core Functionality

Product Management: Add, edit, delete, and search products with barcode support
Inventory Management: Real-time stock tracking with low-stock alerts and restocking
Point of Sale (POS): Fast checkout with barcode scanning and automatic calculations
Sales Reporting: Daily, weekly, and monthly sales analytics
User Management: Role-based access control (Admin & Cashier)
Activity Logging: Comprehensive audit trail of all system activities
PDF Receipts: Professional receipt and report generation

Technical Features

MySQL database with connection pooling
Secure password hashing with bcrypt
Multi-file modular architecture
Clean OOP design patterns
Comprehensive error handling
Input validation
Tkinter-based GUI

📋 Requirements
System Requirements

Python 3.10 or higher
MySQL 8.0 or higher
Windows/Linux/macOS

Python Dependencies
See requirements.txt for full list:

mysql-connector-python
bcrypt
reportlab
openpyxl
python-dotenv

🚀 Installation
Step 1: Install Python
Download and install Python 3.10+ from python.org
Step 2: Install MySQL
Download and install MySQL from mysql.com
Step 3: Clone or Download Project
bash# If using git
git clone <repository-url>
cd grocery_store_system

# Or download and extract the ZIP file

Step 4: Create Virtual Environment (Recommended)
bash# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS

python3 -m venv venv
source venv/bin/activate
Step 5: Install Dependencies
bashpip install -r requirements.txt
Step 6: Configure Database

Open config.py
Update database credentials:

pythonDB_CONFIG = {
'host': 'localhost',
'port': 3306,
'user': 'root',
'password': 'YOUR_MYSQL_PASSWORD', # Change this!
'database': 'grocery_store_db', # ...
}
Step 7: Create Database
Open MySQL and run:
bashmysql -u root -p < database/schema.sql
Or manually:

Open MySQL Workbench or command line
Copy contents of database/schema.sql
Execute the SQL script

Step 8: Verify Setup
bashpython main.py
🔐 Default Login Credentials
Admin Account:

Username: admin
Password: admin123

⚠️ IMPORTANT: Change the default password immediately after first login!
📁 Project Structure
grocery_store_system/
│
├── main.py # Application entry point
├── config.py # Configuration settings
├── requirements.txt # Python dependencies
│
├── database/
│ ├── db_connection.py # Database connection handler
│ └── schema.sql # Database schema
│
├── modules/
│ ├── products.py # Product management
│ ├── inventory.py # Inventory tracking
│ ├── sales.py # Sales/POS operations
│ └── users.py # User management
│
├── ui/
│ ├── login_window.py # Login interface
│ ├── dashboard.py # Main dashboard
│ ├── product_window.py # Product management UI
│ ├── pos_window.py # Point of sale UI
│ ├── inventory_window.py # Inventory management UI
│ ├── reports_window.py # Reports interface
│ └── styles.py # UI styling
│
├── utils/
│ ├── validators.py # Input validation
│ ├── pdf_generator.py # PDF generation
│ ├── logs.py # Activity logging
│ └── helpers.py # Utility functions
│
└── logs/ # Application logs
🎮 How to Use
Starting the Application
bashpython main.py
Login

Enter username and password
Click "Login"
System will load the appropriate dashboard based on role

Dashboard

View recent orders
Access quick actions (Manage Products, New Order)
View sales summary

Managing Products

Click "Manage Products" button
Add Product: Click "Add New Product", fill form, save
Edit Product: Select product, click "Edit", modify, save
Delete Product: Select product, click "Delete"
Search: Type in search box to filter products

Point of Sale (POS)

Click "New Order" button
Add Items:

Scan barcode or type and press Enter
Or search and click "Add to Cart"

Adjust Quantity: Modify quantity in cart table
Apply Discount: Enter discount percentage
Complete Sale: Click "Complete Sale"
Print Receipt: Receipt PDF auto-generated

Inventory Management

Navigate to Inventory section
View Low Stock: See products below reorder level
Restock: Select product, enter quantity, confirm
View History: See all inventory transactions

Reports

Navigate to Reports section
Select date range
Choose report type:

Sales Summary
Top Selling Products
Inventory Movements

Click "Generate Report"
Export to PDF or Excel

User Management (Admin Only)

Navigate to Settings → Users
Add User: Click "Add User", fill form
Edit User: Select user, modify details
Deactivate: Disable user account without deletion

🔧 Configuration
Customizing Settings
Edit config.py to customize:
Business Settings:
pythonBUSINESS_CONFIG = {
'tax_rate': 0.12, # 12% VAT
'currency_symbol': '₱', # Currency symbol
'discount_max': 0.50, # Max discount (50%)
}
Company Information:
pythonPDF_CONFIG = {
'company_name': 'Your Store Name',
'company_address': 'Your Address',
'company_phone': 'Your Phone',
'company_email': 'your@email.com',
}
UI Colors:
pythonCOLORS = {
'primary': '#2c3e50',
'success': '#27ae60',
'danger': '#e74c3c', # ...
}
🐛 Troubleshooting
Database Connection Errors
Error: Can't connect to MySQL server
Solution:

Verify MySQL is running
Check credentials in config.py
Ensure database exists

Module Import Errors
ModuleNotFoundError: No module named 'mysql'
Solution:
bashpip install -r requirements.txt
Permission Errors
Access denied for user 'root'@'localhost'
Solution:

Reset MySQL password
Grant privileges to user

Low Stock Alerts Not Showing
Solution:

Check reorder_level in products table
Ensure stock_quantity is being updated

📊 Database Backup
Backup Database
bashmysqldump -u root -p grocery*store_db > backup*$(date +%Y%m%d).sql
Restore Database
bashmysql -u root -p grocery_store_db < backup_20240101.sql
🔒 Security Best Practices

Change Default Password: Immediately change admin password
Use Strong Passwords: Minimum 8 characters with letters and numbers
Regular Backups: Backup database daily
Update Dependencies: Keep Python packages updated
Restrict Database Access: Use non-root MySQL user in production
Log Monitoring: Regularly check activity logs

📈 Performance Tips

Database Indexing: Indexes created automatically on key fields
Connection Pooling: Reuses database connections
Regular Maintenance: Run MySQL OPTIMIZE TABLE monthly
Clean Old Logs: Archive old activity logs periodically

🤝 Support
For issues or questions:

Check the troubleshooting section
Review activity logs in logs/activity.log
Verify database schema is up to date

📝 License
This project is provided as-is for educational and commercial use.
🎓 Credits
Developed as a complete grocery store management solution with focus on:

Clean code architecture
Security best practices
User-friendly interface
Comprehensive functionality

Version: 1.0.0
Last Updated: 2024
Python Version: 3.10+
Database: MySQL 8.0+
