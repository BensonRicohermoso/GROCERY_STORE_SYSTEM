from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from database.db_connection import db
from modules.inventory import InventoryManager
import config


class CartItem:
    """Shopping cart item model"""
    
    def __init__(self, product_id: int, product_name: str, barcode: str,
                 unit_price: float, quantity: int = 1):
        self.product_id = product_id
        self.product_name = product_name
        self.barcode = barcode
        self.unit_price = unit_price
        self.quantity = quantity
        self.subtotal = unit_price * quantity
    
    def update_quantity(self, quantity: int):
        """Update quantity and recalculate subtotal"""
        self.quantity = quantity
        self.subtotal = self.unit_price * quantity
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'product_id': self.product_id,
            'product_name': self.product_name,
            'barcode': self.barcode,
            'unit_price': self.unit_price,
            'quantity': self.quantity,
            'subtotal': self.subtotal
        }


class Sale:
    """Sale transaction model"""
    
    def __init__(self, sale_id: int = None, sale_number: str = None,
                 customer_name: str = None, customer_phone: str = None,
                 subtotal: float = 0.0, tax_amount: float = 0.0,
                 discount_amount: float = 0.0, total_amount: float = 0.0,
                 payment_method: str = 'cash', cashier_id: int = None,
                 sale_date: datetime = None, items: List[Dict] = None):
        self.sale_id = sale_id
        self.sale_number = sale_number
        self.customer_name = customer_name
        self.customer_phone = customer_phone
        self.subtotal = subtotal
        self.tax_amount = tax_amount
        self.discount_amount = discount_amount
        self.total_amount = total_amount
        self.payment_method = payment_method
        self.cashier_id = cashier_id
        self.sale_date = sale_date
        self.items = items or []


class SalesManager:
    """Handles all sales-related operations"""
    
    @staticmethod
    def generate_sale_number() -> str:
        """
        Generate unique sale number
        Format: SALE-YYYYMMDD-XXXX
        
        Returns:
            Sale number string
        """
        date_str = datetime.now().strftime("%Y%m%d")
        
        # Get count of sales today
        query = """
            SELECT COUNT(*) FROM sales 
            WHERE DATE(sale_date) = CURDATE()
        """
        
        try:
            result = db.fetch_one(query)
            count = result[0] if result else 0
            return f"SALE-{date_str}-{count + 1:04d}"
        except Exception as e:
            print(f"Error generating sale number: {e}")
            # Fallback
            return f"SALE-{date_str}-{datetime.now().strftime('%H%M%S')}"
    
    @staticmethod
    def calculate_totals(cart_items: List[CartItem], discount_percent: float = 0.0) -> Dict:
        """
        Calculate sale totals including tax and discount
        
        Args:
            cart_items: List of CartItem objects
            discount_percent: Discount percentage (0-100)
            
        Returns:
            Dictionary with subtotal, tax, discount, and total
        """
        subtotal = sum(item.subtotal for item in cart_items)
        discount_amount = subtotal * (discount_percent / 100)
        amount_after_discount = subtotal - discount_amount
        tax_amount = amount_after_discount * config.BUSINESS_CONFIG['tax_rate']
        total_amount = amount_after_discount + tax_amount
        
        return {
            'subtotal': round(subtotal, 2),
            'discount_percent': discount_percent,
            'discount_amount': round(discount_amount, 2),
            'tax_amount': round(tax_amount, 2),
            'total_amount': round(total_amount, 2)
        }
    
    @staticmethod
    def process_sale(cart_items: List[CartItem], customer_name: str = None,
                    customer_phone: str = None, discount_percent: float = 0.0,
                    payment_method: str = 'cash', cashier_id: int = None) -> Optional[int]:
        """
        Process a complete sale transaction
        
        Args:
            cart_items: List of CartItem objects
            customer_name: Customer name
            customer_phone: Customer phone
            discount_percent: Discount percentage
            payment_method: Payment method
            cashier_id: Cashier user ID
            
        Returns:
            Sale ID if successful, None otherwise
        """
        if not cart_items:
            print("Cart is empty")
            return None
        
        # Check stock availability for all items
        for item in cart_items:
            if not InventoryManager.check_stock_availability(
                item.product_id, item.quantity
            ):
                print(f"Insufficient stock for {item.product_name}")
                return None
        
        # Calculate totals
        totals = SalesManager.calculate_totals(cart_items, discount_percent)
        sale_number = SalesManager.generate_sale_number()
        
        try:
            # Insert sale record
            sale_query = """
                INSERT INTO sales (sale_number, customer_name, customer_phone,
                                  subtotal, tax_amount, discount_amount, total_amount,
                                  payment_method, cashier_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            sale_id = db.execute_query(sale_query, (
                sale_number, customer_name, customer_phone,
                totals['subtotal'], totals['tax_amount'], totals['discount_amount'],
                totals['total_amount'], payment_method, cashier_id
            ))
            
            # Insert sale items and update inventory
            item_query = """
                INSERT INTO sale_items (sale_id, product_id, quantity, unit_price, subtotal)
                VALUES (%s, %s, %s, %s, %s)
            """
            
            for item in cart_items:
                # Insert sale item
                db.execute_query(item_query, (
                    sale_id, item.product_id, item.quantity,
                    item.unit_price, item.subtotal
                ))
                
                # Update inventory (reduce stock)
                InventoryManager.update_stock(
                    item.product_id,
                    -item.quantity,
                    'sale',
                    cashier_id,
                    sale_id,
                    f"Sale: {sale_number}"
                )
            
            return sale_id
            
        except Exception as e:
            print(f"Error processing sale: {e}")
            return None
    
    @staticmethod
    def get_sale_by_id(sale_id: int) -> Optional[Sale]:
        """
        Get complete sale details including items
        
        Args:
            sale_id: Sale ID
            
        Returns:
            Sale object or None
        """
        # Get sale header
        sale_query = """
            SELECT sale_id, sale_number, customer_name, customer_phone,
                   subtotal, tax_amount, discount_amount, total_amount,
                   payment_method, cashier_id, sale_date
            FROM sales
            WHERE sale_id = %s
        """
        
        # Get sale items
        items_query = """
            SELECT si.product_id, p.product_name, p.barcode,
                   si.unit_price, si.quantity, si.subtotal
            FROM sale_items si
            JOIN products p ON si.product_id = p.product_id
            WHERE si.sale_id = %s
        """
        
        try:
            sale_result = db.fetch_one(sale_query, (sale_id,))
            if not sale_result:
                return None
            
            items_results = db.execute_query(items_query, (sale_id,), fetch=True)
            
            items = [
                {
                    'product_id': row[0],
                    'product_name': row[1],
                    'barcode': row[2],
                    'unit_price': float(row[3]),
                    'quantity': row[4],
                    'subtotal': float(row[5])
                }
                for row in items_results
            ]
            
            return Sale(
                sale_id=sale_result[0],
                sale_number=sale_result[1],
                customer_name=sale_result[2],
                customer_phone=sale_result[3],
                subtotal=float(sale_result[4]),
                tax_amount=float(sale_result[5]),
                discount_amount=float(sale_result[6]),
                total_amount=float(sale_result[7]),
                payment_method=sale_result[8],
                cashier_id=sale_result[9],
                sale_date=sale_result[10],
                items=items
            )
            
        except Exception as e:
            print(f"Error fetching sale: {e}")
            return None
    
    @staticmethod
    def get_recent_sales(limit: int = 50) -> List[Dict]:
        """
        Get recent sales
        
        Args:
            limit: Maximum number of records
            
        Returns:
            List of sale dictionaries
        """
        query = """
            SELECT s.sale_id, s.sale_number, s.customer_name, s.total_amount,
                   s.sale_date, u.full_name as cashier_name
            FROM sales s
            LEFT JOIN users u ON s.cashier_id = u.user_id
            ORDER BY s.sale_date DESC
            LIMIT %s
        """
        
        try:
            return db.fetch_all_dict(query, (limit,))
        except Exception as e:
            print(f"Error fetching recent sales: {e}")
            return []
    
    @staticmethod
    def get_sales_report(start_date: str = None, end_date: str = None) -> Dict:
        """
        Generate sales report for date range
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            Dictionary with sales metrics
        """
        query = """
            SELECT 
                COUNT(*) as total_orders,
                SUM(total_amount) as total_revenue,
                SUM(subtotal) as total_subtotal,
                SUM(tax_amount) as total_tax,
                SUM(discount_amount) as total_discounts,
                AVG(total_amount) as average_order_value,
                MAX(total_amount) as highest_sale,
                MIN(total_amount) as lowest_sale
            FROM sales
            WHERE 1=1
        """
        
        params = []
        
        if start_date:
            query += " AND DATE(sale_date) >= %s"
            params.append(start_date)
        
        if end_date:
            query += " AND DATE(sale_date) <= %s"
            params.append(end_date)
        
        try:
            result = db.fetch_one(query, tuple(params) if params else None)
            if result:
                return {
                    'total_orders': result[0] or 0,
                    'total_revenue': float(result[1] or 0),
                    'total_subtotal': float(result[2] or 0),
                    'total_tax': float(result[3] or 0),
                    'total_discounts': float(result[4] or 0),
                    'average_order_value': float(result[5] or 0),
                    'highest_sale': float(result[6] or 0),
                    'lowest_sale': float(result[7] or 0)
                }
            return {}
        except Exception as e:
            print(f"Error generating sales report: {e}")
            return {}
    
    @staticmethod
    def get_top_selling_products(limit: int = 10, days: int = 30) -> List[Dict]:
        """
        Get top selling products
        
        Args:
            limit: Number of products to return
            days: Time period in days
            
        Returns:
            List of product sales data
        """
        query = """
            SELECT 
                p.product_name,
                SUM(si.quantity) as total_quantity_sold,
                SUM(si.subtotal) as total_revenue,
                COUNT(DISTINCT si.sale_id) as times_sold,
                AVG(si.unit_price) as average_price
            FROM sale_items si
            JOIN products p ON si.product_id = p.product_id
            JOIN sales s ON si.sale_id = s.sale_id
            WHERE s.sale_date >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
            GROUP BY p.product_id, p.product_name
            ORDER BY total_quantity_sold DESC
            LIMIT %s
        """
        
        try:
            return db.fetch_all_dict(query, (days, limit))
        except Exception as e:
            print(f"Error fetching top products: {e}")
            return []