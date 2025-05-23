import unittest
import os
import tempfile
from pathlib import Path
from transaction_processor import process_transaction_file

class TestIntegration(unittest.TestCase):
    """Integration tests for the transaction processor."""
    
    def setUp(self):
        """Set up for tests."""
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
    
    def test_credit_card_processing(self):
        """Test full processing of a credit card file."""
        csv_content = '''"Date","Description","Amount"
"01/01/2024","WALMART","100.00"
"01/02/2024","SHELL GAS","50.00"
"01/03/2024","NETFLIX","15.99"
"01/04/2024","PAYMENT THANK YOU","-165.99"
'''
        file_path = self.create_temp_file(csv_content, "credit_card.csv")
        
        # Process the file
        results = process_transaction_file(str(file_path), debug=True)
        
        # Check results
        self.assertEqual(len(results), 4)
        
        # Check WALMART transaction
        walmart_tx = next((tx for tx in results if "Walmart" in tx["name"]), None)
        self.assertIsNotNone(walmart_tx)
        self.assertEqual(walmart_tx["amount"], -100.00)
        self.assertEqual(walmart_tx["category"], "Groceries")
        self.assertTrue(walmart_tx["essential"])
        
        # Check PAYMENT transaction
        payment_tx = next((tx for tx in results if "Payment" in tx["name"]), None)
        self.assertIsNotNone(payment_tx)
        self.assertEqual(payment_tx["amount"], -165.99)
        self.assertEqual(payment_tx["type"], "expense")

if __name__ == '__main__':
    unittest.main()