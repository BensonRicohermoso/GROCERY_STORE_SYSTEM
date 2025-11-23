from typing import Optional, List, Dict, Tuple
from database.db_connection import db


class Product:
    """Product model class"""
    
    def __init__(self, product_id: int = None, barcode: str = None,
                 product_name: str = None, category_id: int = None,
                 category_name: str = None, unit_price: float = 0.0,
                 cost_price: float = 0.0, stock_quantity: int = 0,
                 reorder_level: int = 10, description: str = None,
                 is_active: bool = True):
        self.product_id = product_id
        self.barcode = barcode
        self.product_name = product_name
        self.category_id = category_id
        self.category_name = category_name
        self.unit_price = unit_price
        self.cost_price = cost_price
        self.stock_quantity = stock_quantity
        self.reorder_level = reorder_level
        self.description = description
        self.is_active = is_active
    
    def to_dict(self) -> Dict:
        """Convert product to dictionary"""
        return {
            'product_id': self.product_id,
            'barcode': self.barcode,
            'product_name': self.product_name,
            'category_id': self.category_id,
            'category_name': self.category_name,
            'unit_price': self.unit_price,
            'cost_price': self.cost_price,
            'stock_quantity': self.stock_quantity,
            'reorder_level': self.reorder_level,
            'description': self.description,
            'is_active': self.is_active
        }


class ProductManager:
    """Handles all product-related operations"""
    
    @staticmethod
    def create_product(barcode: str, product_name: str, category_id: int,
                      unit_price: float, cost_price: float = None,
                      stock_quantity: int = 0, reorder_level: int = 10,
                      description: str = None) -> Optional[int]:
        """
        Create a new product
        
        Args:
            barcode: Product barcode
            product_name: Product name
            category_id: Category ID
            unit_price: Selling price
            cost_price: Cost price
            stock_quantity: Initial stock
            reorder_level: Minimum stock level
            description: Product description
            
        Returns:
            New product ID if successful, None otherwise
        """
        query = """
            INSERT INTO products (barcode, product_name, category_id, unit_price,
                                 cost_price, stock_quantity, reorder_level, description)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        try:
            product_id = db.execute_query(
                query,
                (barcode, product_name, category_id, unit_price, cost_price,
                 stock_quantity, reorder_level, description)
            )
            return product_id
        except Exception as e:
            print(f"Error creating product: {e}")
            return None
    
    @staticmethod
    def update_product(product_id: int, barcode: str = None, 
                      product_name: str = None, category_id: int = None,
                      unit_price: float = None, cost_price: float = None,
                      reorder_level: int = None, description: str = None) -> bool:
        """
        Update product information (does not update stock)
        
        Args:
            product_id: Product ID to update
            Other args: Fields to update (None = no change)
            
        Returns:
            Boolean indicating success
        """
        updates = []
        params = []
        
        if barcode:
            updates.append("barcode = %s")
            params.append(barcode)
        if product_name:
            updates.append("product_name = %s")
            params.append(product_name)
        if category_id:
            updates.append("category_id = %s")
            params.append(category_id)
        if unit_price is not None:
            updates.append("unit_price = %s")
            params.append(unit_price)
        if cost_price is not None:
            updates.append("cost_price = %s")
            params.append(cost_price)
        if reorder_level is not None:
            updates.append("reorder_level = %s")
            params.append(reorder_level)
        if description is not None:
            updates.append("description = %s")
            params.append(description)
        
        if not updates:
            return False
        
        params.append(product_id)
        query = f"UPDATE products SET {', '.join(updates)} WHERE product_id = %s"
        
        try:
            db.execute_query(query, tuple(params))
            return True
        except Exception as e:
            print(f"Error updating product: {e}")
            return False
    
    @staticmethod
    def delete_product(product_id: int) -> bool:
        """
        Soft delete a product (set is_active to False)
        
        Args:
            product_id: Product ID to delete
            
        Returns:
            Boolean indicating success
        """
        query = "UPDATE products SET is_active = FALSE WHERE product_id = %s"
        
        try:
            db.execute_query(query, (product_id,))
            return True
        except Exception as e:
            print(f"Error deleting product: {e}")
            return False
    
    @staticmethod
    def get_product_by_id(product_id: int) -> Optional[Product]:
        """
        Get product by ID
        
        Args:
            product_id: Product ID
            
        Returns:
            Product object or None
        """
        query = """
            SELECT p.product_id, p.barcode, p.product_name, p.category_id,
                   c.category_name, p.unit_price, p.cost_price, p.stock_quantity,
                   p.reorder_level, p.description, p.is_active
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.category_id
            WHERE p.product_id = %s
        """
        
        try:
            result = db.fetch_one(query, (product_id,))
            if result:
                return Product(*result)
            return None
        except Exception as e:
            print(f"Error fetching product: {e}")
            return None
    
    @staticmethod
    def get_product_by_barcode(barcode: str) -> Optional[Product]:
        """
        Get product by barcode
        
        Args:
            barcode: Product barcode
            
        Returns:
            Product object or None
        """
        query = """
            SELECT p.product_id, p.barcode, p.product_name, p.category_id,
                   c.category_name, p.unit_price, p.cost_price, p.stock_quantity,
                   p.reorder_level, p.description, p.is_active
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.category_id
            WHERE p.barcode = %s AND p.is_active = TRUE
        """
        
        try:
            result = db.fetch_one(query, (barcode,))
            if result:
                return Product(*result)
            return None
        except Exception as e:
            print(f"Error fetching product by barcode: {e}")
            return None
    
    @staticmethod
    def search_products(search_term: str, category_id: int = None,
                       active_only: bool = True) -> List[Product]:
        """
        Search products by name or barcode
        
        Args:
            search_term: Search keyword
            category_id: Filter by category (optional)
            active_only: Only return active products
            
        Returns:
            List of Product objects
        """
        query = """
            SELECT p.product_id, p.barcode, p.product_name, p.category_id,
                   c.category_name, p.unit_price, p.cost_price, p.stock_quantity,
                   p.reorder_level, p.description, p.is_active
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.category_id
            WHERE (p.product_name LIKE %s OR p.barcode LIKE %s)
        """
        
        params = [f"%{search_term}%", f"%{search_term}%"]
        
        if category_id:
            query += " AND p.category_id = %s"
            params.append(category_id)
        
        if active_only:
            query += " AND p.is_active = TRUE"
        
        query += " ORDER BY p.product_name"
        
        try:
            results = db.execute_query(query, tuple(params), fetch=True)
            return [Product(*row) for row in results]
        except Exception as e:
            print(f"Error searching products: {e}")
            return []
    
    @staticmethod
    def get_all_products(active_only: bool = True) -> List[Product]:
        """
        Get all products
        
        Args:
            active_only: Only return active products
            
        Returns:
            List of Product objects
        """
        query = """
            SELECT p.product_id, p.barcode, p.product_name, p.category_id,
                   c.category_name, p.unit_price, p.cost_price, p.stock_quantity,
                   p.reorder_level, p.description, p.is_active
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.category_id
        """
        
        if active_only:
            query += " WHERE p.is_active = TRUE"
        
        query += " ORDER BY p.product_name"
        
        try:
            results = db.execute_query(query, fetch=True)
            return [Product(*row) for row in results]
        except Exception as e:
            print(f"Error fetching products: {e}")
            return []
    
    @staticmethod
    def get_categories() -> List[Tuple[int, str]]:
        """
        Get all categories
        
        Returns:
            List of tuples (category_id, category_name)
        """
        query = "SELECT category_id, category_name FROM categories ORDER BY category_name"
        
        try:
            return db.execute_query(query, fetch=True)
        except Exception as e:
            print(f"Error fetching categories: {e}")
            return []
    
    @staticmethod
    def add_category(category_name: str, description: str = None) -> Optional[int]:
        """
        Add a new category
        
        Args:
            category_name: Category name
            description: Category description
            
        Returns:
            New category ID or None
        """
        query = "INSERT INTO categories (category_name, description) VALUES (%s, %s)"
        
        try:
            return db.execute_query(query, (category_name, description))
        except Exception as e:
            print(f"Error adding category: {e}")
            return None