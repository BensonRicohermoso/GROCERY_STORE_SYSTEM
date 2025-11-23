import logging
from logging.handlers import RotatingFileHandler
from functools import wraps
from datetime import datetime
from typing import Optional
import config
from database.db_connection import db


# Setup file logger
def setup_file_logger():
    """Setup rotating file handler for logging"""
    log_file = config.LOG_CONFIG['log_dir'] / config.LOG_CONFIG['log_file']
    
    handler = RotatingFileHandler(
        log_file,
        maxBytes=config.LOG_CONFIG['max_size'],
        backupCount=config.LOG_CONFIG['backup_count']
    )
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    
    logger = logging.getLogger('GroceryStore')
    logger.setLevel(getattr(logging, config.LOG_CONFIG['log_level']))
    logger.addHandler(handler)
    
    return logger


# Initialize logger
file_logger = setup_file_logger()


class ActivityLogger:
    """Handles activity logging to database"""
    
    @staticmethod
    def log_activity(user_id: int, action: str, entity_type: str = None,
                    entity_id: int = None, details: str = None,
                    ip_address: str = None) -> bool:
        """
        Log user activity to database
        
        Args:
            user_id: User performing the action
            action: Action performed (e.g., 'login', 'create_product')
            entity_type: Type of entity (e.g., 'product', 'sale')
            entity_id: ID of the entity affected
            details: Additional details as JSON or text
            ip_address: User's IP address
            
        Returns:
            Boolean indicating success
        """
        query = """
            INSERT INTO activity_logs 
            (user_id, action, entity_type, entity_id, details, ip_address)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        try:
            db.execute_query(query, (
                user_id, action, entity_type, entity_id, details, ip_address
            ))
            
            # Also log to file
            file_logger.info(
                f"User {user_id} - {action} - {entity_type}:{entity_id} - {details}"
            )
            
            return True
        except Exception as e:
            file_logger.error(f"Error logging activity: {e}")
            return False
    
    @staticmethod
    def log_login(user_id: int, username: str, success: bool = True,
                 ip_address: str = None):
        """Log user login attempt"""
        action = 'login_success' if success else 'login_failed'
        details = f"User '{username}' login {'successful' if success else 'failed'}"
        ActivityLogger.log_activity(user_id, action, 'user', user_id, details, ip_address)
    
    @staticmethod
    def log_logout(user_id: int, username: str, ip_address: str = None):
        """Log user logout"""
        details = f"User '{username}' logged out"
        ActivityLogger.log_activity(user_id, 'logout', 'user', user_id, details, ip_address)
    
    @staticmethod
    def log_product_action(user_id: int, action: str, product_id: int,
                          product_name: str, details: str = None):
        """Log product-related actions"""
        full_details = f"{action.title()} product '{product_name}'"
        if details:
            full_details += f" - {details}"
        ActivityLogger.log_activity(user_id, action, 'product', product_id, full_details)
    
    @staticmethod
    def log_sale(user_id: int, sale_id: int, sale_number: str,
                total_amount: float):
        """Log sale transaction"""
        details = f"Sale {sale_number} - Total: {config.BUSINESS_CONFIG['currency_symbol']}{total_amount:.2f}"
        ActivityLogger.log_activity(user_id, 'sale_completed', 'sale', sale_id, details)
    
    @staticmethod
    def log_inventory_action(user_id: int, action: str, product_id: int,
                            product_name: str, quantity_change: int):
        """Log inventory changes"""
        details = f"{action.title()} - Product '{product_name}' - Quantity: {quantity_change}"
        ActivityLogger.log_activity(user_id, action, 'inventory', product_id, details)
    
    @staticmethod
    def get_user_activity(user_id: int = None, limit: int = 100):
        """
        Get activity logs
        
        Args:
            user_id: Filter by user (optional)
            limit: Maximum records to return
            
        Returns:
            List of activity log dictionaries
        """
        query = """
            SELECT al.log_id, al.user_id, u.username, u.full_name,
                   al.action, al.entity_type, al.entity_id, al.details,
                   al.ip_address, al.log_date
            FROM activity_logs al
            LEFT JOIN users u ON al.user_id = u.user_id
            WHERE 1=1
        """
        
        params = []
        
        if user_id:
            query += " AND al.user_id = %s"
            params.append(user_id)
        
        query += " ORDER BY al.log_date DESC LIMIT %s"
        params.append(limit)
        
        try:
            return db.fetch_all_dict(query, tuple(params))
        except Exception as e:
            file_logger.error(f"Error fetching activity logs: {e}")
            return []


def log_action(action: str, entity_type: str = None):
    """
    Decorator to automatically log function calls
    
    Usage:
        @log_action('create_product', 'product')
        def create_product(...):
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Execute function
            result = func(*args, **kwargs)
            
            # Try to extract user_id from arguments
            user_id = kwargs.get('user_id')
            if not user_id and args:
                # Try to find user_id in positional args
                for arg in args:
                    if isinstance(arg, dict) and 'user_id' in arg:
                        user_id = arg['user_id']
                        break
            
            # Log the action if user_id is found and result is successful
            if user_id and result:
                entity_id = result if isinstance(result, int) else None
                ActivityLogger.log_activity(
                    user_id, action, entity_type, entity_id,
                    f"Function {func.__name__} executed"
                )
            
            return result
        return wrapper
    return decorator