import unittest
from transaction_processor.core import TransactionProcessor, Transaction

class TestCategorization(unittest.TestCase):
    """Test transaction categorization functionality."""
    
    def setUp(self):
        """Set up for tests."""
        self.processor = TransactionProcessor()
    
    def test_expense_category_detection(self):
        """Test categorization of expense transactions."""
        cases = [
            ("Walmart Supercenter", "Groceries"),
            ("Starbucks Coffee", "Dining"),
            ("Shell Gas Station", "Transportation"),
            ("Netflix", "Entertainment"),
            ("City Water Payment", "Utilities"),
            ("State Farm Insurance", "Insurance"),
            ("Mortgage Payment", "Housing"),
        ]
        
        for desc, expected in cases:
            with self.subTest(desc=desc):
                txn = Transaction(
                    date="2024-01-01",
                    name=desc,
                    amount=-100.00,
                    type="expense"
                )
                self.processor._categorize_transaction(txn)
                self.assertEqual(txn.category, expected)
    
    def test_essential_flag(self):
        """Test essential flag determination."""
        essentials = [
            ("Walmart", True),
            ("Rent Payment", True),
            ("Doctor Visit", True),
            ("Netflix", False),
        ]
        
        for desc, expected in essentials:
            with self.subTest(desc=desc):
                txn = Transaction(
                    date="2024-01-01",
                    name=desc,
                    amount=-100.00,
                    type="expense"
                )
                self.processor._categorize_transaction(txn)
                self.assertEqual(txn.essential, expected)
    
    def test_fixed_flag(self):
        """Test fixed flag determination."""
        cases = [
            ("Mortgage", True),
            ("State Farm", True),
            ("Spotify Membership", True),
            ("Walmart", False),
            ("Restaurant Bill", False)
        ]
        
        for desc, expected in cases:
            with self.subTest(desc=desc):
                txn = Transaction(
                    date="2024-01-01",
                    name=desc,
                    amount=-75.00,
                    type="expense"
                )
                self.processor._categorize_transaction(txn)
                self.assertEqual(txn.fixed, expected)

if __name__ == "__main__":
    unittest.main()