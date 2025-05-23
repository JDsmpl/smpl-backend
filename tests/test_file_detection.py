import unittest
import os
import tempfile
from pathlib import Path
from transaction_processor.core import TransactionProcessor

class TestFileDetection(unittest.TestCase):
    """Test file detection functionality."""
    
    def setUp(self):
        """Set up for tests."""
        self.processor = TransactionProcessor()
        self.temp_dir = tempfile.TemporaryDirectory()
    
    def tearDown(self):
        """Clean up after tests."""
        self.temp_dir.cleanup()
    
    def create_temp_file(self, content, filename):
        """Create a temporary file with the given content and filename."""
        file_path = Path(self.temp_dir.name) / filename
        with open(file_path, 'w') as f:
            f.write(content)
        return file_path
    
    def test_csv_detection(self):
        """Test CSV file detection."""
        csv_content = "Date,Description,Amount\n01/01/2024,Test,100.00"
        file_path = self.create_temp_file(csv_content, "test.csv")
        
        # Test the file reading method directly
        df = self.processor._read_file(file_path)
        
        self.assertFalse(df.empty)
        self.assertEqual(len(df), 1)
        self.assertEqual(list(df.columns), ["Date", "Description", "Amount"])
    
    def test_detect_credit_card(self):
        """Test credit card detection from filename and content."""
        csv_content = "Date,Description,Amount\n01/01/2024,PAYMENT THANK YOU,-100.00"
        file_path = self.create_temp_file(csv_content, "creditcard_statement.csv")
        
        # Load the file
        df = self.processor._read_file(file_path)
        
        # Run detection
        self.processor._detect_account_type(df, file_path.name)
        
        from transaction_processor.core import AccountType
        self.assertEqual(self.processor.account_type, AccountType.CREDIT_CARD)
    
    def test_detect_bank_account(self):
        """Test bank account detection from filename and content."""
        csv_content = "Date,Description,Amount\n01/01/2024,DEPOSIT,100.00"
        file_path = self.create_temp_file(csv_content, "checking_account.csv")
        
        # Load the file
        df = self.processor._read_file(file_path)
        
        # Run detection
        self.processor._detect_account_type(df, file_path.name)
        
        from transaction_processor.core import AccountType
        self.assertEqual(self.processor.account_type, AccountType.BANK_ACCOUNT)

if __name__ == '__main__':
    unittest.main()