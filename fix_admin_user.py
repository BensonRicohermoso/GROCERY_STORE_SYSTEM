import bcrypt
import mysql.connector

# ============================================================================
# STEP 1: UPDATE THESE VALUES WITH YOUR MYSQL INFO
# ============================================================================
MYSQL_HOST = 'localhost'
MYSQL_USER = 'root'
MYSQL_PASSWORD = 'ADS-9X0Z-D1T1-1UAX'  # ← PUT YOUR MYSQL PASSWORD HERE
MYSQL_DATABASE = 'grocery_store_db'

# ============================================================================
# STEP 2: RUN THIS SCRIPT
# ============================================================================

def main():
    print("\n" + "="*60)
    print("FIXING ADMIN USER LOGIN")
    print("="*60 + "\n")
    
    # Generate correct password hash for "admin123"
    password = "admin123"
    salt = bcrypt.gensalt(rounds=12)
    password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    print(f"Generated new password hash for: {password}")
    print(f"Hash: {password_hash[:50]}...\n")
    
    try:
        # Connect to database
        print("Connecting to MySQL...")
        connection = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE
        )
        print("✓ Connected to database\n")
        
        cursor = connection.cursor()
        
        # Check if admin exists
        print("Checking for existing admin user...")
        cursor.execute("SELECT user_id, username FROM users WHERE username = 'admin'")
        result = cursor.fetchone()
        
        if result:
            # Update existing admin
            print(f"✓ Found admin user (ID: {result[0]})")
            print("Updating password...\n")
            
            cursor.execute(
                "UPDATE users SET password_hash = %s, is_active = TRUE WHERE username = 'admin'",
                (password_hash,)
            )
            connection.commit()
            print("✓ Password updated!\n")
            
        else:
            # Create new admin
            print("Admin not found. Creating new admin user...\n")
            
            cursor.execute("""
                INSERT INTO users (username, password_hash, full_name, role, email, is_active)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, ('admin', password_hash, 'System Administrator', 'admin', 'admin@grocerystore.com', True))
            
            connection.commit()
            print("✓ Admin user created!\n")
        
        # Verify
        cursor.execute("""
            SELECT user_id, username, full_name, role, is_active 
            FROM users WHERE username = 'admin'
        """)
        admin = cursor.fetchone()
        
        print("="*60)
        print("ADMIN USER DETAILS:")
        print("="*60)
        print(f"User ID:     {admin[0]}")
        print(f"Username:    {admin[1]}")
        print(f"Full Name:   {admin[2]}")
        print(f"Role:        {admin[3]}")
        print(f"Active:      {'Yes' if admin[4] else 'No'}")
        print("="*60 + "\n")
        
        # Test the password
        print("Testing password verification...")
        cursor.execute("SELECT password_hash FROM users WHERE username = 'admin'")
        stored_hash = cursor.fetchone()[0]
        
        if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
            print("✓ Password verification test PASSED!\n")
        else:
            print("✗ Password verification test FAILED!\n")
        
        cursor.close()
        connection.close()
        
        print("="*60)
        print("SUCCESS! You can now login with:")
        print("  Username: admin")
        print("  Password: admin123")
        print("="*60 + "\n")
        
    except mysql.connector.Error as e:
        print(f"\n✗ MySQL Error: {e}\n")
        print("Please check:")
        print("1. MySQL is running")
        print("2. MYSQL_PASSWORD in this script is correct")
        print("3. Database 'grocery_store_db' exists\n")
        
    except Exception as e:
        print(f"\n✗ Error: {e}\n")

if __name__ == "__main__":
    print("\n*** IMPORTANT ***")
    print("Before running this script:")
    print("1. Make sure bcrypt is installed: pip install bcrypt")
    print("2. Update MYSQL_PASSWORD in this file (line 13)")
    print("3. Make sure MySQL is running")
    print("\nPress Enter to continue or Ctrl+C to cancel...")
    input()
    
    main()