import bcrypt
from typing import Optional, List, Dict
from datetime import datetime
from database.db_connection import db


class User:
    """User model class"""
    
    def __init__(self, user_id: int = None, username: str = None, 
                 full_name: str = None, role: str = 'cashier', 
                 email: str = None, phone: str = None, is_active: bool = True):
        self.user_id = user_id
        self.username = username
        self.full_name = full_name
        self.role = role
        self.email = email
        self.phone = phone
        self.is_active = is_active
    
    def to_dict(self) -> Dict:
        """Convert user object to dictionary"""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'full_name': self.full_name,
            'role': self.role,
            'email': self.email,
            'phone': self.phone,
            'is_active': self.is_active
        }
    
    def __repr__(self):
        """String representation of User object"""
        return f"User(id={self.user_id}, username='{self.username}', role='{self.role}')"


class UserManager:
    """Handles all user-related operations"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password using bcrypt
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password string
        """
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """
        Verify a password against its hash
        
        Args:
            password: Plain text password
            password_hash: Hashed password from database
            
        Returns:
            Boolean indicating if password matches
        """
        try:
            return bcrypt.checkpw(password.encode('utf-8'), 
                                 password_hash.encode('utf-8'))
        except Exception as e:
            print(f"Error verifying password: {e}")
            return False
    
    @staticmethod
    def authenticate(username: str, password: str) -> Optional[User]:
        """
        Authenticate a user with username and password
        
        Args:
            username: User's username
            password: User's plain text password
            
        Returns:
            User object if authentication successful, None otherwise
        """
        query = """
            SELECT user_id, username, password_hash, full_name, role, 
                   email, phone, is_active
            FROM users
            WHERE username = %s AND is_active = TRUE
        """
        
        try:
            result = db.fetch_one(query, (username,))
            
            if result and UserManager.verify_password(password, result[2]):
                return User(
                    user_id=result[0],
                    username=result[1],
                    full_name=result[3],
                    role=result[4],
                    email=result[5],
                    phone=result[6],
                    is_active=result[7]
                )
            return None
        except Exception as e:
            print(f"Authentication error: {e}")
            return None
    
    @staticmethod
    def create_user(username: str, password: str, full_name: str, 
                   role: str = 'cashier', email: str = None, 
                   phone: str = None) -> Optional[int]:
        """
        Create a new user
        
        Args:
            username: Unique username
            password: Plain text password (will be hashed)
            full_name: User's full name
            role: User role (admin/cashier)
            email: User's email
            phone: User's phone number
            
        Returns:
            New user ID if successful, None otherwise
        """
        # Validate inputs
        from utils.validators import Validator
        
        valid, msg = Validator.validate_username(username)
        if not valid:
            print(f"Invalid username: {msg}")
            return None
        
        valid, msg = Validator.validate_password(password)
        if not valid:
            print(f"Invalid password: {msg}")
            return None
        
        if email:
            valid, msg = Validator.validate_email(email)
            if not valid:
                print(f"Invalid email: {msg}")
                return None
        
        if phone:
            valid, msg = Validator.validate_phone(phone)
            if not valid:
                print(f"Invalid phone: {msg}")
                return None
        
        # Hash password
        password_hash = UserManager.hash_password(password)
        
        query = """
            INSERT INTO users (username, password_hash, full_name, role, email, phone)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        try:
            user_id = db.execute_query(
                query, 
                (username, password_hash, full_name, role, email, phone)
            )
            print(f"✓ User '{username}' created successfully with ID: {user_id}")
            return user_id
        except Exception as e:
            print(f"Error creating user: {e}")
            return None
    
    @staticmethod
    def update_user(user_id: int, full_name: str = None, email: str = None,
                   phone: str = None, role: str = None) -> bool:
        """
        Update user information
        
        Args:
            user_id: ID of user to update
            full_name: New full name
            email: New email
            phone: New phone
            role: New role
            
        Returns:
            Boolean indicating success
        """
        updates = []
        params = []
        
        if full_name:
            updates.append("full_name = %s")
            params.append(full_name)
        
        if email is not None:  # Allow clearing email
            from utils.validators import Validator
            if email:  # Only validate if not empty
                valid, msg = Validator.validate_email(email)
                if not valid:
                    print(f"Invalid email: {msg}")
                    return False
            updates.append("email = %s")
            params.append(email)
        
        if phone is not None:  # Allow clearing phone
            from utils.validators import Validator
            if phone:  # Only validate if not empty
                valid, msg = Validator.validate_phone(phone)
                if not valid:
                    print(f"Invalid phone: {msg}")
                    return False
            updates.append("phone = %s")
            params.append(phone)
        
        if role:
            if role not in ['admin', 'cashier']:
                print(f"Invalid role: {role}")
                return False
            updates.append("role = %s")
            params.append(role)
        
        if not updates:
            print("No updates provided")
            return False
        
        params.append(user_id)
        query = f"UPDATE users SET {', '.join(updates)} WHERE user_id = %s"
        
        try:
            db.execute_query(query, tuple(params))
            print(f"✓ User {user_id} updated successfully")
            return True
        except Exception as e:
            print(f"Error updating user: {e}")
            return False
    
    @staticmethod
    def change_password(user_id: int, old_password: str, 
                       new_password: str) -> bool:
        """
        Change user password
        
        Args:
            user_id: ID of user
            old_password: Current password
            new_password: New password
            
        Returns:
            Boolean indicating success
        """
        # Validate new password
        from utils.validators import Validator
        valid, msg = Validator.validate_password(new_password)
        if not valid:
            print(f"Invalid new password: {msg}")
            return False
        
        # Verify old password
        query = "SELECT password_hash FROM users WHERE user_id = %s"
        result = db.fetch_one(query, (user_id,))
        
        if not result:
            print(f"User {user_id} not found")
            return False
        
        if not UserManager.verify_password(old_password, result[0]):
            print("Current password is incorrect")
            return False
        
        # Update to new password
        new_hash = UserManager.hash_password(new_password)
        update_query = "UPDATE users SET password_hash = %s WHERE user_id = %s"
        
        try:
            db.execute_query(update_query, (new_hash, user_id))
            print(f"✓ Password changed successfully for user {user_id}")
            return True
        except Exception as e:
            print(f"Error changing password: {e}")
            return False
    
    @staticmethod
    def reset_password(user_id: int, new_password: str) -> bool:
        """
        Reset user password (admin function - no old password required)
        
        Args:
            user_id: ID of user
            new_password: New password
            
        Returns:
            Boolean indicating success
        """
        # Validate new password
        from utils.validators import Validator
        valid, msg = Validator.validate_password(new_password)
        if not valid:
            print(f"Invalid password: {msg}")
            return False
        
        new_hash = UserManager.hash_password(new_password)
        query = "UPDATE users SET password_hash = %s WHERE user_id = %s"
        
        try:
            db.execute_query(query, (new_hash, user_id))
            print(f"✓ Password reset successfully for user {user_id}")
            return True
        except Exception as e:
            print(f"Error resetting password: {e}")
            return False
    
    @staticmethod
    def deactivate_user(user_id: int) -> bool:
        """
        Deactivate a user account (soft delete)
        
        Args:
            user_id: ID of user to deactivate
            
        Returns:
            Boolean indicating success
        """
        query = "UPDATE users SET is_active = FALSE WHERE user_id = %s"
        
        try:
            db.execute_query(query, (user_id,))
            print(f"✓ User {user_id} deactivated")
            return True
        except Exception as e:
            print(f"Error deactivating user: {e}")
            return False
    
    @staticmethod
    def activate_user(user_id: int) -> bool:
        """
        Reactivate a deactivated user account
        
        Args:
            user_id: ID of user to activate
            
        Returns:
            Boolean indicating success
        """
        query = "UPDATE users SET is_active = TRUE WHERE user_id = %s"
        
        try:
            db.execute_query(query, (user_id,))
            print(f"✓ User {user_id} activated")
            return True
        except Exception as e:
            print(f"Error activating user: {e}")
            return False
    
    @staticmethod
    def delete_user(user_id: int) -> bool:
        """
        Permanently delete a user (use with caution!)
        
        Args:
            user_id: ID of user to delete
            
        Returns:
            Boolean indicating success
        """
        # Don't allow deleting user with ID 1 (default admin)
        if user_id == 1:
            print("Cannot delete default admin user")
            return False
        
        query = "DELETE FROM users WHERE user_id = %s"
        
        try:
            db.execute_query(query, (user_id,))
            print(f"✓ User {user_id} permanently deleted")
            return True
        except Exception as e:
            print(f"Error deleting user: {e}")
            return False
    
    @staticmethod
    def get_all_users(include_inactive: bool = False) -> List[User]:
        """
        Get all users
        
        Args:
            include_inactive: Include deactivated users
            
        Returns:
            List of User objects
        """
        query = """
            SELECT user_id, username, full_name, role, email, phone, is_active
            FROM users
        """
        
        if not include_inactive:
            query += " WHERE is_active = TRUE"
        
        query += " ORDER BY full_name"
        
        try:
            results = db.execute_query(query, fetch=True)
            return [
                User(
                    user_id=row[0],
                    username=row[1],
                    full_name=row[2],
                    role=row[3],
                    email=row[4],
                    phone=row[5],
                    is_active=row[6]
                )
                for row in results
            ]
        except Exception as e:
            print(f"Error fetching users: {e}")
            return []
    
    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[User]:
        """
        Get user by ID
        
        Args:
            user_id: User ID
            
        Returns:
            User object or None
        """
        query = """
            SELECT user_id, username, full_name, role, email, phone, is_active
            FROM users
            WHERE user_id = %s
        """
        
        try:
            result = db.fetch_one(query, (user_id,))
            if result:
                return User(
                    user_id=result[0],
                    username=result[1],
                    full_name=result[2],
                    role=result[3],
                    email=result[4],
                    phone=result[5],
                    is_active=result[6]
                )
            return None
        except Exception as e:
            print(f"Error fetching user: {e}")
            return None
    
    @staticmethod
    def get_user_by_username(username: str) -> Optional[User]:
        """
        Get user by username
        
        Args:
            username: Username to search for
            
        Returns:
            User object or None
        """
        query = """
            SELECT user_id, username, full_name, role, email, phone, is_active
            FROM users
            WHERE username = %s
        """
        
        try:
            result = db.fetch_one(query, (username,))
            if result:
                return User(
                    user_id=result[0],
                    username=result[1],
                    full_name=result[2],
                    role=result[3],
                    email=result[4],
                    phone=result[5],
                    is_active=result[6]
                )
            return None
        except Exception as e:
            print(f"Error fetching user: {e}")
            return None
    
    @staticmethod
    def search_users(search_term: str) -> List[User]:
        """
        Search users by username or full name
        
        Args:
            search_term: Search keyword
            
        Returns:
            List of User objects
        """
        query = """
            SELECT user_id, username, full_name, role, email, phone, is_active
            FROM users
            WHERE (username LIKE %s OR full_name LIKE %s)
            AND is_active = TRUE
            ORDER BY full_name
        """
        
        search_pattern = f"%{search_term}%"
        
        try:
            results = db.execute_query(query, (search_pattern, search_pattern), fetch=True)
            return [
                User(
                    user_id=row[0],
                    username=row[1],
                    full_name=row[2],
                    role=row[3],
                    email=row[4],
                    phone=row[5],
                    is_active=row[6]
                )
                for row in results
            ]
        except Exception as e:
            print(f"Error searching users: {e}")
            return []
    
    @staticmethod
    def get_users_by_role(role: str) -> List[User]:
        """
        Get all users with a specific role
        
        Args:
            role: User role ('admin' or 'cashier')
            
        Returns:
            List of User objects
        """
        query = """
            SELECT user_id, username, full_name, role, email, phone, is_active
            FROM users
            WHERE role = %s AND is_active = TRUE
            ORDER BY full_name
        """
        
        try:
            results = db.execute_query(query, (role,), fetch=True)
            return [
                User(
                    user_id=row[0],
                    username=row[1],
                    full_name=row[2],
                    role=row[3],
                    email=row[4],
                    phone=row[5],
                    is_active=row[6]
                )
                for row in results
            ]
        except Exception as e:
            print(f"Error fetching users by role: {e}")
            return []
    
    @staticmethod
    def username_exists(username: str) -> bool:
        """
        Check if username already exists
        
        Args:
            username: Username to check
            
        Returns:
            Boolean indicating if username exists
        """
        query = "SELECT COUNT(*) FROM users WHERE username = %s"
        
        try:
            result = db.fetch_one(query, (username,))
            return result[0] > 0 if result else False
        except Exception as e:
            print(f"Error checking username: {e}")
            return False
    
    @staticmethod
    def get_user_stats() -> Dict:
        """
        Get user statistics
        
        Returns:
            Dictionary with user counts
        """
        query = """
            SELECT 
                COUNT(*) as total_users,
                SUM(CASE WHEN role = 'admin' THEN 1 ELSE 0 END) as admin_count,
                SUM(CASE WHEN role = 'cashier' THEN 1 ELSE 0 END) as cashier_count,
                SUM(CASE WHEN is_active = TRUE THEN 1 ELSE 0 END) as active_count,
                SUM(CASE WHEN is_active = FALSE THEN 1 ELSE 0 END) as inactive_count
            FROM users
        """
        
        try:
            result = db.fetch_one(query)
            if result:
                return {
                    'total_users': result[0] or 0,
                    'admin_count': result[1] or 0,
                    'cashier_count': result[2] or 0,
                    'active_count': result[3] or 0,
                    'inactive_count': result[4] or 0
                }
            return {}
        except Exception as e:
            print(f"Error getting user stats: {e}")
            return {}


# Utility function for quick testing
if __name__ == "__main__":
    print("Testing UserManager...")
    
    # Test authentication
    user = UserManager.authenticate("admin", "admin123")
    if user:
        print(f"✓ Authentication successful: {user}")
    else:
        print("✗ Authentication failed")
    
    # Test getting all users
    users = UserManager.get_all_users()
    print(f"\nTotal users: {len(users)}")
    for user in users:
        print(f"  - {user}")