from typing import List, Dict, Optional
from datetime import datetime
from database.db_connection import db


class InventoryTransaction:
    """Inventory transaction model"""
    
    def __init__(self, transaction_id: int = None, product_id: int = None,
                 product_name: str = None, transaction_type: str = None,
                 quantity_change: int = 0, previous_stock: int = 0,
                 new_stock: int = 0, reference_id: int = None,
                 notes: str = None, user_id: int = None,
                 transaction_date: datetime = None):
        self.transaction_id = transaction_id
        self.product_id = product_id
        self.product_name = product_name
        self.transaction_type = transaction_type
        self.quantity_change = quantity_change
        self.previous_stock = previous_stock
        self.new_stock = new_stock
        self.reference_id = reference_id
        self.notes = notes
        self.user_id = user_id
        self.transaction_date = transaction_date


class InventoryManager:
    """Handles all inventory-related operations"""
    
    @staticmethod
    def update_stock(product_id: int, quantity_change: int,
                    transaction_type: str, user_id: int = None,
                    reference_id: int = None, notes: str = None) -> bool:
        """
        Update product stock and log transaction
        
        Args:
            product_id: Product ID
            quantity_change: Positive or negative quantity change
            transaction_type: Type (restock, sale, adjustment, return)
            user_id: User performing the action
            reference_id: Related transaction ID (e.g., sale_id)
            notes: Additional notes
            
        Returns:
            Boolean indicating success
        """
        try:
            # Get current stock
            stock_query = "SELECT stock_quantity FROM products WHERE product_id = %s"
            result = db.fetch_one(stock_query, (product_id,))
            
            if not result:
                print(f"Product {product_id} not found")
                return False
            
            previous_stock = result[0]
            new_stock = previous_stock + quantity_change
            
            if new_stock < 0:
                print(f"Insufficient stock. Available: {previous_stock}")
                return False
            
            # Update product stock
            update_query = "UPDATE products SET stock_quantity = %s WHERE product_id = %s"
            db.execute_query(update_query, (new_stock, product_id))
            
            # Log transaction
            log_query = """
                INSERT INTO inventory_transactions 
                (product_id, transaction_type, quantity_change, previous_stock, 
                 new_stock, reference_id, notes, user_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            db.execute_query(log_query, (
                product_id, transaction_type, quantity_change, previous_stock,
                new_stock, reference_id, notes, user_id
            ))
            
            return True
        except Exception as e:
            print(f"Error updating stock: {e}")
            return False
    
    @staticmethod
    def restock_product(product_id: int, quantity: int, user_id: int = None,
                       notes: str = None) -> bool:
        """
        Add stock to a product
        
        Args:
            product_id: Product ID
            quantity: Quantity to add
            user_id: User performing restock
            notes: Additional notes
            
        Returns:
            Boolean indicating success
        """
        return InventoryManager.update_stock(
            product_id, quantity, 'restock', user_id, notes=notes
        )
    
    @staticmethod
    def adjust_stock(product_id: int, new_quantity: int, user_id: int = None,
                    notes: str = None) -> bool:
        """
        Adjust stock to a specific quantity (for corrections)
        
        Args:
            product_id: Product ID
            new_quantity: New stock quantity
            user_id: User performing adjustment
            notes: Reason for adjustment
            
        Returns:
            Boolean indicating success
        """
        # Get current stock
        query = "SELECT stock_quantity FROM products WHERE product_id = %s"
        result = db.fetch_one(query, (product_id,))
        
        if not result:
            return False
        
        current_stock = result[0]
        quantity_change = new_quantity - current_stock
        
        return InventoryManager.update_stock(
            product_id, quantity_change, 'adjustment', user_id, notes=notes
        )
    
    @staticmethod
    def get_low_stock_products() -> List[Dict]:
        """
        Get products with stock at or below reorder level
        
        Returns:
            List of dictionaries with product details
        """
        query = """
            SELECT product_id, barcode, product_name, category_name,
                   stock_quantity, reorder_level, unit_price
            FROM low_stock_products
        """
        
        try:
            return db.fetch_all_dict(query)
        except Exception as e:
            print(f"Error fetching low stock products: {e}")
            return []
    
    @staticmethod
    def get_inventory_transactions(product_id: int = None, 
                                   transaction_type: str = None,
                                   limit: int = 100) -> List[InventoryTransaction]:
        """
        Get inventory transaction history
        
        Args:
            product_id: Filter by product (optional)
            transaction_type: Filter by type (optional)
            limit: Maximum records to return
            
        Returns:
            List of InventoryTransaction objects
        """
        query = """
            SELECT it.transaction_id, it.product_id, p.product_name,
                   it.transaction_type, it.quantity_change, it.previous_stock,
                   it.new_stock, it.reference_id, it.notes, it.user_id,
                   it.transaction_date
            FROM inventory_transactions it
            JOIN products p ON it.product_id = p.product_id
            WHERE 1=1
        """
        
        params = []
        
        if product_id:
            query += " AND it.product_id = %s"
            params.append(product_id)
        
        if transaction_type:
            query += " AND it.transaction_type = %s"
            params.append(transaction_type)
        
        query += " ORDER BY it.transaction_date DESC LIMIT %s"
        params.append(limit)
        
        try:
            results = db.execute_query(query, tuple(params), fetch=True)
            return [InventoryTransaction(*row) for row in results]
        except Exception as e:
            print(f"Error fetching transactions: {e}")
            return []
    
    @staticmethod
    def get_inventory_summary() -> Dict:
        """
        Get overall inventory summary statistics
        
        Returns:
            Dictionary with inventory metrics
        """
        query = """
            SELECT 
                COUNT(*) as total_products,
                SUM(stock_quantity) as total_stock_units,
                SUM(stock_quantity * unit_price) as total_stock_value,
                SUM(stock_quantity * cost_price) as total_cost_value,
                COUNT(CASE WHEN stock_quantity <= reorder_level THEN 1 END) as low_stock_count,
                COUNT(CASE WHEN stock_quantity = 0 THEN 1 END) as out_of_stock_count
            FROM products
            WHERE is_active = TRUE
        """
        
        try:
            result = db.fetch_one(query)
            if result:
                return {
                    'total_products': result[0] or 0,
                    'total_stock_units': result[1] or 0,
                    'total_stock_value': float(result[2] or 0),
                    'total_cost_value': float(result[3] or 0),
                    'low_stock_count': result[4] or 0,
                    'out_of_stock_count': result[5] or 0
                }
            return {}
        except Exception as e:
            print(f"Error getting inventory summary: {e}")
            return {}
    
    @staticmethod
    def check_stock_availability(product_id: int, required_quantity: int) -> bool:
        """
        Check if sufficient stock is available for a product
        
        Args:
            product_id: Product ID
            required_quantity: Required quantity
            
        Returns:
            Boolean indicating if stock is sufficient
        """
        query = "SELECT stock_quantity FROM products WHERE product_id = %s"
        
        try:
            result = db.fetch_one(query, (product_id,))
            if result:
                return result[0] >= required_quantity
            return False
        except Exception as e:
            print(f"Error checking stock: {e}")
            return False
    
    @staticmethod
    def get_stock_movements_report(start_date: str = None, 
                                   end_date: str = None) -> List[Dict]:
        """
        Get stock movements report for a date range
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            List of movement records
        """
        query = """
            SELECT 
                p.product_name,
                it.transaction_type,
                SUM(CASE WHEN it.quantity_change > 0 THEN it.quantity_change ELSE 0 END) as stock_in,
                SUM(CASE WHEN it.quantity_change < 0 THEN ABS(it.quantity_change) ELSE 0 END) as stock_out,
                SUM(it.quantity_change) as net_change
            FROM inventory_transactions it
            JOIN products p ON it.product_id = p.product_id
            WHERE 1=1
        """
        
        params = []
        
        if start_date:
            query += " AND DATE(it.transaction_date) >= %s"
            params.append(start_date)
        
        if end_date:
            query += " AND DATE(it.transaction_date) <= %s"
            params.append(end_date)
        
        query += """
            GROUP BY p.product_name, it.transaction_type
            ORDER BY p.product_name, it.transaction_type
        """
        
        try:
            return db.fetch_all_dict(query, tuple(params) if params else None)
        except Exception as e:
            print(f"Error generating stock movements report: {e}")
            return []