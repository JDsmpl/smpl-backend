import unittest
import pandas as pd
from transaction_processor.core import TransactionProcessor, Transaction

class TestNormalization(unittest.TestCase):
    """Test transaction normalization functionality."""
    
    def setUp(self):
        """Set up for tests."""
        self.processor = TransactionProcessor()
    
    def test_date_normalization(self):
        """Test date string normalization."""
        cases = [
            ("01/02/2024", "2024-01-02"),
            ("2024-01-02", "2024-01-02"),
            ("Jan 2, 2024", "2024-01-02"),
            ("2 Jan 2024", "2024-01-02"),
            ("01-02-2024", "2024-01-02"),
            ("1/2/24", "2024-01-02"),
        ]
        
        for input_date, expected in cases:
            with self.subTest(input_date=input_date):
                row = {"Description": "Test", "Amount": "100.00"}
                result = self.processor._parse_date(input_date)
                self.assertEqual(result, expected)
    
    def test_merchant_name_cleaning(self):
        """Test merchant name cleaning."""
        test_cases = [
            ("AMAZON.COM", "Amazon.Com"),
            ("WALMART #1234", "Walmart"),
            ("TARGET STORE   SANDY   UT", "Target Store Sandy Ut"),
            ("SHELL OIL 12345", "Shell Oil"),
            ("STARBUCKS CARD 1234", "Starbucks Card"),
        ]
        
        for input_name, expected_output in test_cases:
            with self.subTest(input_name=input_name):
                result = self.processor._clean_description(input_name)
                self.assertEqual(result, expected_output)
    
    def test_amount_parsing(self):
        """Test amount parsing with different formats."""
        test_cases = [
            ({"Amount": "100.00"}, 100.0),         # Basic positive number
            ({"Amount": "-100.00"}, -100.0),       # Negative number
            ({"Amount": "$100.00"}, 100.0),        # With currency symbol
            ({"Amount": "(100.00)"}, -100.0),      # Parentheses for negative
            ({"Amount": "1,000.00"}, 1000.0),      # With thousand separator
            ({"Amount": "$1,234.56"}, 1234.56),    # Currency and thousand separator
            ({"Amount": "invalid"}, None),         # Invalid input
            ({"Amount": ""}, None),                # Empty string
            ({"Amount": None}, None),               # None input
        ]
        
        for input_data, expected in test_cases:
            with self.subTest(input_data=input_data):
                # Call the method with the input data
                result = self.processor._parse_amount(pd.Series(input_data))
                
                # Assert the result is as expected
                self.assertEqual(result, expected, 
                              f"Failed for {input_data['Amount']}")

if __name__ == '__main__':
    unittest.main()