import mysql.connector
from mysql.connector import pooling, Error
from typing import Optional, List, Tuple, Any, Dict
import config


class DatabaseConnection:
    """Singleton database connection class with connection pooling"""
    
    _instance = None
    _pool = None
    
    def __new__(cls):
        """Ensure only one instance exists (Singleton pattern)"""
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
            cls._instance._initialize_pool()
        return cls._instance
    
    def _initialize_pool(self):
        """Initialize connection pool"""
        try:
            self._pool = pooling.MySQLConnectionPool(
                pool_name=config.DB_CONFIG['pool_name'],
                pool_size=config.DB_CONFIG['pool_size'],
                host=config.DB_CONFIG['host'],
                port=config.DB_CONFIG['port'],
                user=config.DB_CONFIG['user'],
                password=config.DB_CONFIG['password'],
                database=config.DB_CONFIG['database'],
                charset=config.DB_CONFIG['charset'],
                autocommit=config.DB_CONFIG['autocommit']
            )
            print("✓ Database connection pool initialized successfully")
        except Error as e:
            print(f"✗ Error initializing connection pool: {e}")
            raise
    
    def get_connection(self):
        """Get a connection from the pool"""
        try:
            return self._pool.get_connection()
        except Error as e:
            print(f"Error getting connection from pool: {e}")
            raise
    
    def execute_query(self, query: str, params: Optional[Tuple] = None, 
                     fetch: bool = False) -> Optional[List[Tuple]]:
        """
        Execute a SQL query with optional parameters
        
        Args:
            query: SQL query string
            params: Query parameters (for prepared statements)
            fetch: Whether to fetch and return results
            
        Returns:
            List of tuples if fetch=True, None otherwise
        """
        connection = None
        cursor = None
        
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if fetch:
                result = cursor.fetchall()
                return result
            else:
                connection.commit()
                return cursor.lastrowid if cursor.lastrowid else None
                
        except Error as e:
            if connection:
                connection.rollback()
            print(f"Database error: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    def execute_many(self, query: str, data: List[Tuple]) -> bool:
        """
        Execute multiple queries with different parameters
        
        Args:
            query: SQL query string
            data: List of tuples containing parameters
            
        Returns:
            Boolean indicating success
        """
        connection = None
        cursor = None
        
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            cursor.executemany(query, data)
            connection.commit()
            return True
        except Error as e:
            if connection:
                connection.rollback()
            print(f"Database error in execute_many: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    def fetch_one(self, query: str, params: Optional[Tuple] = None) -> Optional[Tuple]:
        """
        Fetch a single row from database
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            Single tuple or None
        """
        connection = None
        cursor = None
        
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            return cursor.fetchone()
        except Error as e:
            print(f"Database error in fetch_one: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    def fetch_all_dict(self, query: str, params: Optional[Tuple] = None) -> List[Dict]:
        """
        Fetch all rows as list of dictionaries
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            List of dictionaries with column names as keys
        """
        connection = None
        cursor = None
        
        try:
            connection = self.get_connection()
            cursor = connection.cursor(dictionary=True)
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            return cursor.fetchall()
        except Error as e:
            print(f"Database error in fetch_all_dict: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    def call_procedure(self, proc_name: str, params: Tuple) -> Any:
        """
        Call a stored procedure
        
        Args:
            proc_name: Name of the stored procedure
            params: Procedure parameters
            
        Returns:
            Procedure result
        """
        connection = None
        cursor = None
        
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            cursor.callproc(proc_name, params)
            connection.commit()
            
            # Get OUT parameters if any
            results = []
            for result in cursor.stored_results():
                results.extend(result.fetchall())
            
            return results if results else True
        except Error as e:
            if connection:
                connection.rollback()
            print(f"Error calling procedure {proc_name}: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            cursor.close()
            connection.close()
            return result[0] == 1
        except Error as e:
            print(f"Connection test failed: {e}")
            return False


# Singleton instance
db = DatabaseConnection()