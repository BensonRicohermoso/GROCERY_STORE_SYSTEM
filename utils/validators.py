import re
from typing import Tuple, Optional
from datetime import datetime


class Validator:
    """Input validation class with comprehensive validation methods"""
    
    @staticmethod
    def validate_email(email: str) -> Tuple[bool, str]:
        """
        Validate email format
        
        Args:
            email: Email string to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not email:
            return True, ""  # Email is optional
        
        # Basic email pattern
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if re.match(pattern, email):
            # Additional checks
            if len(email) > 100:
                return False, "Email too long (maximum 100 characters)"
            if '..' in email:
                return False, "Email cannot contain consecutive dots"
            if email.startswith('.') or email.endswith('.'):
                return False, "Email cannot start or end with a dot"
            return True, ""
        
        return False, "Invalid email format (example: user@example.com)"
    
    @staticmethod
    def validate_phone(phone: str) -> Tuple[bool, str]:
        """
        Validate phone number
        
        Args:
            phone: Phone number string
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not phone:
            return True, ""  # Phone is optional
        
        # Remove common separators
        cleaned = re.sub(r'[\s\-\(\)\.]', '', phone)
        
        # Check if it contains only digits and optional + prefix
        if re.match(r'^\+?\d{10,15}$', cleaned):
            return True, ""
        
        # Provide specific error messages
        if len(cleaned) < 10:
            return False, "Phone number too short (minimum 10 digits)"
        if len(cleaned) > 15:
            return False, "Phone number too long (maximum 15 digits)"
        if not re.match(r'^[\d\s\-\(\)\+\.]+$', phone):
            return False, "Phone number contains invalid characters"
        
        return False, "Invalid phone number format"
    
    @staticmethod
    def validate_barcode(barcode: str) -> Tuple[bool, str]:
        """
        Validate barcode format
        
        Args:
            barcode: Barcode string
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not barcode or len(barcode.strip()) == 0:
            return False, "Barcode is required"
        
        barcode = barcode.strip()
        
        # Check length
        if len(barcode) < 3:
            return False, "Barcode too short (minimum 3 characters)"
        
        if len(barcode) > 50:
            return False, "Barcode too long (maximum 50 characters)"
        
        # Check for valid characters (alphanumeric and some special chars)
        if not re.match(r'^[A-Za-z0-9\-_]+$', barcode):
            return False, "Barcode can only contain letters, numbers, hyphens, and underscores"
        
        return True, ""
    
    @staticmethod
    def validate_price(price_str: str, allow_zero: bool = False) -> Tuple[bool, str, float]:
        """
        Validate and parse price
        
        Args:
            price_str: Price as string
            allow_zero: Whether zero is allowed
            
        Returns:
            Tuple of (is_valid, error_message, parsed_value)
        """
        if not price_str or len(str(price_str).strip()) == 0:
            return False, "Price is required", 0.0
        
        try:
            # Remove currency symbols and commas
            cleaned = str(price_str).replace(',', '').replace('₱', '').replace('$', '').strip()
            price = float(cleaned)
            
            # Validation checks
            if price < 0:
                return False, "Price cannot be negative", 0.0
            
            if not allow_zero and price == 0:
                return False, "Price must be greater than zero", 0.0
            
            if price > 999999.99:
                return False, "Price too large (maximum 999,999.99)", 0.0
            
            # Check decimal places
            decimal_places = len(str(price).split('.')[-1]) if '.' in str(price) else 0
            if decimal_places > 2:
                return False, "Price can have maximum 2 decimal places", 0.0
            
            return True, "", round(price, 2)
        
        except (ValueError, TypeError):
            return False, "Invalid price format (use numbers only)", 0.0
    
    @staticmethod
    def validate_quantity(quantity_str: str, allow_zero: bool = False, 
                         max_quantity: int = 999999) -> Tuple[bool, str, int]:
        """
        Validate and parse quantity
        
        Args:
            quantity_str: Quantity as string
            allow_zero: Whether zero is allowed
            max_quantity: Maximum allowed quantity
            
        Returns:
            Tuple of (is_valid, error_message, parsed_value)
        """
        if not quantity_str or len(str(quantity_str).strip()) == 0:
            return False, "Quantity is required", 0
        
        try:
            # Remove commas
            cleaned = str(quantity_str).replace(',', '').strip()
            quantity = int(float(cleaned))  # Convert to float first to handle "10.0"
            
            # Validation checks
            if quantity < 0:
                return False, "Quantity cannot be negative", 0
            
            if not allow_zero and quantity == 0:
                return False, "Quantity must be greater than zero", 0
            
            if quantity > max_quantity:
                return False, f"Quantity too large (maximum {max_quantity:,})", 0
            
            return True, "", quantity
        
        except (ValueError, TypeError):
            return False, "Invalid quantity (must be a whole number)", 0
    
    @staticmethod
    def validate_discount(discount_str: str, max_discount: float = 100.0) -> Tuple[bool, str, float]:
        """
        Validate discount percentage
        
        Args:
            discount_str: Discount percentage as string
            max_discount: Maximum allowed discount percentage
            
        Returns:
            Tuple of (is_valid, error_message, parsed_value)
        """
        if not discount_str or len(str(discount_str).strip()) == 0:
            return True, "", 0.0  # Discount is optional
        
        try:
            # Remove % symbol
            cleaned = str(discount_str).replace('%', '').strip()
            discount = float(cleaned)
            
            # Validation checks
            if discount < 0:
                return False, "Discount cannot be negative", 0.0
            
            if discount > max_discount:
                return False, f"Discount cannot exceed {max_discount}%", 0.0
            
            return True, "", round(discount, 2)
        
        except (ValueError, TypeError):
            return False, "Invalid discount format (use numbers only)", 0.0
    
    @staticmethod
    def validate_username(username: str) -> Tuple[bool, str]:
        """
        Validate username
        
        Args:
            username: Username string
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not username or len(username.strip()) == 0:
            return False, "Username is required"
        
        username = username.strip()
        
        # Length checks
        if len(username) < 3:
            return False, "Username must be at least 3 characters"
        
        if len(username) > 50:
            return False, "Username too long (maximum 50 characters)"
        
        # Character validation - only letters, numbers, and underscores
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            return False, "Username can only contain letters, numbers, and underscores"
        
        # Cannot start with a number
        if username[0].isdigit():
            return False, "Username cannot start with a number"
        
        return True, ""
    
    @staticmethod
    def validate_password(password: str, min_length: int = 6) -> Tuple[bool, str]:
        """
        Validate password strength
        
        Args:
            password: Password string
            min_length: Minimum password length
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not password:
            return False, "Password is required"
        
        # Length check
        if len(password) < min_length:
            return False, f"Password must be at least {min_length} characters"
        
        if len(password) > 100:
            return False, "Password too long (maximum 100 characters)"
        
        # Strength checks
        has_letter = re.search(r'[a-zA-Z]', password)
        has_number = re.search(r'\d', password)
        
        if not has_letter:
            return False, "Password must contain at least one letter"
        
        if not has_number:
            return False, "Password must contain at least one number"
        
        # Optional: Check for special characters (uncomment if needed)
        # has_special = re.search(r'[!@#$%^&*(),.?":{}|<>]', password)
        # if not has_special:
        #     return False, "Password must contain at least one special character"
        
        return True, ""
    
    @staticmethod
    def validate_name(name: str, field_name: str = "Name", 
                     min_length: int = 2, max_length: int = 100) -> Tuple[bool, str]:
        """
        Validate name fields (full name, product name, etc.)
        
        Args:
            name: Name string
            field_name: Name of the field for error messages
            min_length: Minimum name length
            max_length: Maximum name length
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not name or len(name.strip()) == 0:
            return False, f"{field_name} is required"
        
        name = name.strip()
        
        # Length checks
        if len(name) < min_length:
            return False, f"{field_name} must be at least {min_length} characters"
        
        if len(name) > max_length:
            return False, f"{field_name} too long (maximum {max_length} characters)"
        
        # Check for invalid characters (only letters, spaces, hyphens, apostrophes)
        if not re.match(r"^[a-zA-Z\s\-'\.]+$", name):
            return False, f"{field_name} contains invalid characters"
        
        return True, ""
    
    @staticmethod
    def validate_date(date_str: str, date_format: str = "%Y-%m-%d") -> Tuple[bool, str, Optional[datetime]]:
        """
        Validate and parse date string
        
        Args:
            date_str: Date string
            date_format: Expected date format
            
        Returns:
            Tuple of (is_valid, error_message, parsed_datetime)
        """
        if not date_str or len(str(date_str).strip()) == 0:
            return False, "Date is required", None
        
        try:
            parsed_date = datetime.strptime(date_str, date_format)
            
            # Check if date is too far in the past or future
            current_year = datetime.now().year
            if parsed_date.year < 2000:
                return False, "Date is too far in the past", None
            if parsed_date.year > current_year + 10:
                return False, "Date is too far in the future", None
            
            return True, "", parsed_date
        
        except ValueError:
            return False, f"Invalid date format (expected: {date_format})", None
    
    @staticmethod
    def validate_date_range(start_date_str: str, end_date_str: str, 
                           date_format: str = "%Y-%m-%d") -> Tuple[bool, str]:
        """
        Validate date range
        
        Args:
            start_date_str: Start date string
            end_date_str: End date string
            date_format: Expected date format
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Validate start date
        valid_start, msg_start, start_date = Validator.validate_date(start_date_str, date_format)
        if not valid_start:
            return False, f"Start date: {msg_start}"
        
        # Validate end date
        valid_end, msg_end, end_date = Validator.validate_date(end_date_str, date_format)
        if not valid_end:
            return False, f"End date: {msg_end}"
        
        # Check if start date is before end date
        if start_date > end_date:
            return False, "Start date must be before end date"
        
        # Check if range is reasonable (not more than 10 years)
        days_diff = (end_date - start_date).days
        if days_diff > 3650:  # 10 years
            return False, "Date range too large (maximum 10 years)"
        
        return True, ""
    
    @staticmethod
    def validate_required(value: str, field_name: str = "Field") -> Tuple[bool, str]:
        """
        Validate that a field is not empty
        
        Args:
            value: Value to check
            field_name: Name of the field for error messages
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if value is None or len(str(value).strip()) == 0:
            return False, f"{field_name} is required"
        return True, ""
    
    @staticmethod
    def sanitize_input(text: str, max_length: int = None) -> str:
        """
        Sanitize text input by removing potentially harmful characters
        
        Args:
            text: Input text
            max_length: Maximum allowed length
            
        Returns:
            Sanitized text
        """
        if not text:
            return ""
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        # Remove control characters except newline and tab
        text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\t')
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Truncate if needed
        if max_length and len(text) > max_length:
            text = text[:max_length]
        
        return text
    
    @staticmethod
    def validate_category_id(category_id: int, valid_categories: list = None) -> Tuple[bool, str]:
        """
        Validate category ID
        
        Args:
            category_id: Category ID to validate
            valid_categories: List of valid category IDs (optional)
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if category_id is None or category_id <= 0:
            return False, "Please select a valid category"
        
        if valid_categories and category_id not in valid_categories:
            return False, "Selected category does not exist"
        
        return True, ""
    
    @staticmethod
    def validate_numeric_range(value: str, min_val: float, max_val: float,
                               field_name: str = "Value") -> Tuple[bool, str, float]:
        """
        Validate that a numeric value is within a range
        
        Args:
            value: Value string to validate
            min_val: Minimum allowed value
            max_val: Maximum allowed value
            field_name: Name of the field for error messages
            
        Returns:
            Tuple of (is_valid, error_message, parsed_value)
        """
        try:
            num_value = float(value)
            
            if num_value < min_val:
                return False, f"{field_name} must be at least {min_val}", 0.0
            
            if num_value > max_val:
                return False, f"{field_name} cannot exceed {max_val}", 0.0
            
            return True, "", num_value
        
        except (ValueError, TypeError):
            return False, f"Invalid {field_name.lower()} format", 0.0


# Utility function for testing
if __name__ == "__main__":
    print("Testing Validator class...")
    
    # Test cases
    tests = [
        ("Email", Validator.validate_email("user@example.com")),
        ("Invalid Email", Validator.validate_email("invalid-email")),
        ("Phone", Validator.validate_phone("+1234567890")),
        ("Barcode", Validator.validate_barcode("ABC12345")),
        ("Price", Validator.validate_price("99.99")),
        ("Quantity", Validator.validate_quantity("10")),
        ("Discount", Validator.validate_discount("15.5")),
        ("Username", Validator.validate_username("john_doe123")),
        ("Password", Validator.validate_password("Pass123")),
        ("Name", Validator.validate_name("John Doe", "Full Name")),
    ]
    
    for test_name, result in tests:
        is_valid = result[0]
        message = result[1]
        status = "✓" if is_valid else "✗"
        print(f"{status} {test_name}: {message if message else 'Valid'}")