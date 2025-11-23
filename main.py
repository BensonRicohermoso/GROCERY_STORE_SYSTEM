import tkinter as tk
from tkinter import messagebox
import sys
import traceback

# Import configuration
import config

# Import database connection
from database.db_connection import db

# Import UI modules
from ui.login_window import show_login
from ui.styles import AppStyles


def test_database_connection():
    """Test database connection before starting application"""
    print("=" * 60)
    print("GROCERY STORE MANAGEMENT SYSTEM")
    print(f"Version {config.APP_CONFIG['version']}")
    print("=" * 60)
    print("\nTesting database connection...")
    
    try:
        if db.test_connection():
            print("✓ Database connection successful!")
            return True
        else:
            print("✗ Database connection failed!")
            messagebox.showerror(
                "Database Error",
                "Cannot connect to database.\n\n"
                "Please check:\n"
                "1. MySQL server is running\n"
                "2. Database credentials in config.py are correct\n"
                "3. Database 'grocery_store_db' exists\n\n"
                "Run database/schema.sql to create the database."
            )
            return False
    except Exception as e:
        print(f"✗ Database connection error: {e}")
        messagebox.showerror(
            "Database Error",
            f"Database connection error:\n{str(e)}\n\n"
            "Please check your database configuration in config.py"
        )
        return False


def open_dashboard(user):
    """
    Open main dashboard after successful login
    
    Args:
        user: User object from successful login
    """
    from ui.dashboard import DashboardWindow
    
    # Create main window
    root = tk.Tk()
    
    # Initialize dashboard
    dashboard = DashboardWindow(root, user)
    
    # Start main loop
    root.mainloop()


def main():
    """Main application entry point"""
    try:
        # Test database connection
        if not test_database_connection():
            sys.exit(1)
        
        print("\nStarting application...")
        print("Please login to continue.\n")
        
        # Show login window
        show_login(open_dashboard)
        
    except KeyboardInterrupt:
        print("\n\nApplication interrupted by user.")
        sys.exit(0)
    
    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
        print("\nTraceback:")
        traceback.print_exc()
        
        messagebox.showerror(
            "Fatal Error",
            f"An unexpected error occurred:\n{str(e)}\n\n"
            "Please check the console for details."
        )
        sys.exit(1)


if __name__ == "__main__":
    main()