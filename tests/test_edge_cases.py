"""Tests for edge cases in the transaction processor."""

import unittest
import tempfile
import os
from pathlib import Path
import pandas as pd
from transaction_processor import process_transaction_file
from transaction_processor.core import TransactionProcessor

class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling."""
    
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.processor = TransactionProcessor()
    
    def tearDown(self):
        self.temp_dir.cleanup()
    
    def create_temp_file(self, content, filename):
        """Create a temporary file with the given content and filename."""
        file_path = Path(self.temp_dir.name) / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return file_path
    
    def test_empty_file(self):
        """Test handling of completely empty file."""
        empty_file = ""
        file_path = self.create_temp_file(empty_file, "empty.csv")
        results = process_transaction_file(str(file_path))
        self.assertEqual(len(results), 0, "Empty file should return empty results")
    
    def test_headers_only(self):
        """Test file with headers but no data."""
        headers_only = "Date,Description,Amount\n"
        file_path = self.create_temp_file(headers_only, "headers_only.csv")
        results = process_transaction_file(str(file_path))
        self.assertEqual(len(results), 0, "Headers-only file should return empty results")
    
    def test_missing_required_column(self):
        """Test file missing a required column."""
        # Missing Amount column
        missing_amount = "Date,Description\n01/01/2024,Test Transaction\n"
        file_path = self.create_temp_file(missing_amount, "missing_amount.csv")
        results = process_transaction_file(str(file_path))
        self.assertEqual(len(results), 0, "File missing required column should return empty results")
        
        # Missing Date column
        missing_date = "Description,Amount\nTest Transaction,100.00\n"
        file_path = self.create_temp_file(missing_date, "missing_date.csv")
        results = process_transaction_file(str(file_path))
        self.assertEqual(len(results), 0, "File missing required column should return empty results")
        
        # Missing Description column
        missing_desc = "Date,Amount\n01/01/2024,100.00\n"
        file_path = self.create_temp_file(missing_desc, "missing_desc.csv")
        results = process_transaction_file(str(file_path))
        self.assertEqual(len(results), 0, "File missing required column should return empty results")
    
    def test_different_column_order(self):
        """Test file with different column order."""
        different_order = "Description,Amount,Date\nTest Transaction,100.00,01/01/2024\n"
        file_path = self.create_temp_file(different_order, "different_order.csv")
        results = process_transaction_file(str(file_path))
        self.assertGreater(len(results), 0, "Column order should not affect processing")
        self.assertEqual(results[0]["date"], "2024-01-01")
        self.assertEqual(results[0]["amount"], -100.00)
    
    def test_invalid_amount_formats(self):
        """Test various invalid amount formats."""
        invalid_amounts = "\"Date\",\"Description\",\"Amount\"\n"
        invalid_amounts += "\"01/01/2024\",\"Invalid Empty\",\"\"\n"
        invalid_amounts += "\"01/02/2024\",\"Invalid Text\",\"abc\"\n"
        invalid_amounts += "\"01/03/2024\",\"Invalid Symbol\",\"--\"\n"
        invalid_amounts += "\"01/04/2024\",\"Valid Amount\",\"100.00\"\n"
        
        file_path = self.create_temp_file(invalid_amounts, "invalid_amounts.csv")
        results = process_transaction_file(str(file_path))
        
        # Should skip invalid rows but process valid ones
        self.assertEqual(len(results), 1, "Should process only the valid row")
        self.assertEqual(results[0]["name"], "Valid Amount")
    
    def test_currency_symbols(self):
        """Test handling of currency symbols."""
        currency_symbols = "\"Date\",\"Description\",\"Amount\"\n"
        currency_symbols += "\"01/01/2024\",\"Dollar\",\"$100.00\"\n"
        currency_symbols += "\"01/02/2024\",\"Euro\",\"€50.00\"\n"
        currency_symbols += "\"01/03/2024\",\"Pound\",\"£75.25\"\n"
        currency_symbols += "\"01/04/2024\",\"Yen\",\"¥1000\"\n"
        currency_symbols += "\"01/05/2024\",\"Multiple $$100.00\",\"$100.00\"\n"
        currency_symbols += "\"01/06/2024\",\"Space after $ 100.00\",\"$100.00\"\n"
        
        file_path = self.create_temp_file(currency_symbols, "currency_symbols.csv")
        results = process_transaction_file(str(file_path))
        
        # Should handle all currency symbols
        self.assertEqual(len(results), 6, "Should process all rows with currency symbols")
        
        # Check if amounts are correctly parsed
        dollar = next((tx for tx in results if tx["name"] == "Dollar"), None)
        multiple_symbols = next((tx for tx in results if tx["name"] == "Multiple"), None)
        space_after_symbol = next((tx for tx in results if tx["name"] == "Space After"), None)
        
        self.assertIsNotNone(dollar)
        self.assertIsNotNone(multiple_symbols)
        self.assertIsNotNone(space_after_symbol)
        self.assertEqual(dollar["amount"], -100.00)
        self.assertEqual(multiple_symbols["amount"], -100.00)
        self.assertEqual(space_after_symbol["amount"], -100.00)
        
        # Test other currency symbols
        euro = next((tx for tx in results if tx["name"] == "Euro"), None)
        pound = next((tx for tx in results if tx["name"] == "Pound"), None)
        
        self.assertIsNotNone(dollar)
        self.assertIsNotNone(euro)
        self.assertIsNotNone(pound)
        
        self.assertEqual(dollar["amount"], -100.00)
        self.assertEqual(euro["amount"], -50.00)
        self.assertEqual(pound["amount"], -75.25)
    
    def test_special_characters(self):
        """Test handling of special characters in descriptions."""
        special_chars = "\"Date\",\"Description\",\"Amount\"\n"
        special_chars += "\"01/01/2024\",\"Café & Restaurant\",\"100.00\"\n"
        special_chars += "\"01/02/2024\",\"Quotes & Commas, Inc.\",\"50.00\"\n"
        special_chars += "\"01/03/2024\",\"Special-Characters!@#$%^&\",\"75.00\"\n"
        
        file_path = self.create_temp_file(special_chars, "special_chars.csv")
        results = process_transaction_file(str(file_path))
        
        self.assertEqual(len(results), 3, "Should process all rows with special characters")
        
        # Check if descriptions are correctly parsed
        cafe = next((tx for tx in results if "Café" in tx["name"]), None)
        quotes = next((tx for tx in results if "Quotes" in tx["name"]), None)
        special = next((tx for tx in results if "Special" in tx["name"]), None)
        
        self.assertIsNotNone(cafe)
        self.assertIsNotNone(quotes)
        self.assertIsNotNone(special)
    
    def test_unicode_characters(self):
        """Test handling of Unicode characters and emoji."""
        unicode_chars = "\"Date\",\"Description\",\"Amount\"\n"
        unicode_chars += "\"01/01/2024\",\"Café ☕\",\"100.00\"\n"
        unicode_chars += "\"01/02/2024\",\"🍕 Pizza Place\",\"50.00\"\n"
        unicode_chars += "\"01/03/2024\",\"Sushi 🍣 Restaurant\",\"75.00\"\n"
        
        file_path = self.create_temp_file(unicode_chars, "unicode_chars.csv")
        results = process_transaction_file(str(file_path))
        
        self.assertGreaterEqual(len(results), 1, "Should process at least some rows with Unicode characters")
    
    def test_different_date_formats(self):
        """Test handling of different date formats."""
        date_formats = "\"Date\",\"Description\",\"Amount\"\n"
        date_formats += "\"01/02/2024\",\"MM/DD/YYYY\",\"100.00\"\n"
        date_formats += "\"2024-01-03\",\"YYYY-MM-DD\",\"50.00\"\n"
        date_formats += "\"03-01-2024\",\"DD-MM-YYYY\",\"75.00\"\n"
        date_formats += "\"Jan 4, 2024\",\"Month Day Year\",\"25.00\"\n"
        date_formats += "\"4-Jan-2024\",\"Day-Month-Year\",\"30.00\"\n"
        
        file_path = self.create_temp_file(date_formats, "date_formats.csv")
        results = process_transaction_file(str(file_path))
        
        # Should handle all date formats
        self.assertGreaterEqual(len(results), 3, "Should process at least 3 different date formats")
        
        # All dates should be in YYYY-MM-DD format
        for tx in results:
            self.assertRegex(tx["date"], r'^\d{4}-\d{2}-\d{2}$', 
                            f"Date {tx['date']} is not in YYYY-MM-DD format")
    
    def test_parentheses_for_negative(self):
        """Test handling of parentheses to indicate negative amounts."""
        parentheses = "\"Date\",\"Description\",\"Amount\"\n"
        parentheses += "\"01/01/2024\",\"Normal Expense\",\"100.00\"\n"
        parentheses += "\"01/02/2024\",\"Parentheses Credit\",\"(50.00)\"\n"
        
        file_path = self.create_temp_file(parentheses, "parentheses.csv")
        results = process_transaction_file(str(file_path))
        
        # Should handle both formats
        self.assertEqual(len(results), 2, "Should process both normal and parentheses formats")
        
        normal = next((tx for tx in results if tx["name"] == "Normal Expense"), None)
        parens = next((tx for tx in results if tx["name"] == "Parentheses Credit"), None)
        
        self.assertIsNotNone(normal)
        self.assertIsNotNone(parens)
        
        self.assertEqual(normal["amount"], -100.00, "Normal expense should be negative")
        self.assertEqual(parens["amount"], 50.00, "Parentheses amount should be positive (income)")
    
    def test_thousand_separators(self):
        """Test handling of thousand separators in amounts."""
        thousand_sep = "\"Date\",\"Description\",\"Amount\"\n"
        thousand_sep += "\"01/01/2024\",\"With Comma\",\"1,000.00\"\n"
        thousand_sep += "\"01/02/2024\",\"With Space\",\"1 000.00\"\n"
        
        file_path = self.create_temp_file(thousand_sep, "thousand_sep.csv")
        results = process_transaction_file(str(file_path))
        
        # Should handle both formats
        self.assertEqual(len(results), 2, "Should process both formats")
        
        with_comma = next((tx for tx in results if tx["name"] == "With Comma"), None)
        with_space = next((tx for tx in results if tx["name"] == "With Space"), None)
        
        self.assertIsNotNone(with_comma)
        self.assertIsNotNone(with_space)
        
        self.assertEqual(with_comma["amount"], -1000.00, "Amount with comma should be correctly parsed")
        self.assertEqual(with_space["amount"], -1000.00, "Amount with space should be correctly parsed")

    def test_large_amounts(self):
        """Test handling of very large amounts."""
        large_amounts = "\"Date\",\"Description\",\"Amount\"\n"
        large_amounts += "\"01/01/2024\",\"Small Amount\",\"100.00\"\n"
        large_amounts += "\"01/02/2024\",\"Very Large\",\"1,000,000.00\"\n"
        large_amounts += "\"01/03/2024\",\"Scientific\",\"1.23e6\"\n"
        
        file_path = self.create_temp_file(large_amounts, "large_amounts.csv")
        results = process_transaction_file(str(file_path))
        
        # Should process all amounts
        self.assertEqual(len(results), 3, "Should process all large amounts")
        self.assertEqual(results[0]["amount"], -100.00)
        self.assertEqual(results[1]["amount"], -1000000.00)
        self.assertEqual(results[2]["amount"], 1230000.00)
    
    def test_special_characters_in_description(self):
        """Test handling of special characters in descriptions."""
        special_desc = "\"Date\",\"Description\",\"Amount\"\n"
        special_desc += "\"01/01/2024\",\"Quotes, Inc.\",\"100.00\"\n"
        special_desc += "\"01/02/2024\",\"Back\\\\Slash\",\"50.00\"\n"
        special_desc += "\"01/03/2024\",\"Forward/Slash\",\"75.00\"\n"
        
        file_path = self.create_temp_file(special_desc, "special_desc.csv")
        results = process_transaction_file(str(file_path))
        
        # Should process all special character descriptions
        self.assertEqual(len(results), 3, "Should process all special character descriptions")
        self.assertEqual(results[0]["name"], "Quotes, Inc.")
        self.assertEqual(results[1]["name"], "Back\\Slash")
        self.assertEqual(results[2]["name"], "Forward/Slash")
    
    def test_duplicate_transactions(self):
        """Test handling of duplicate transactions."""
        duplicates = "\"Date\",\"Description\",\"Amount\"\n"
        duplicates += "\"01/01/2024\",\"Dup Transaction\",\"100.00\"\n"
        duplicates += "\"01/01/2024\",\"Dup Transaction\",\"100.00\"\n"
        duplicates += "\"01/02/2024\",\"Another Dup\",\"50.00\"\n"
        duplicates += "\"01/02/2024\",\"Another Dup\",\"50.00\"\n"
        
        file_path = self.create_temp_file(duplicates, "duplicates.csv")
        results = process_transaction_file(str(file_path))
        
        # Should process all transactions including duplicates
        self.assertEqual(len(results), 4, "Should process all transactions including duplicates")
    
    def test_mixed_encoding(self):
        """Test handling of files with different encodings."""
        # Test UTF-8 with special characters
        utf8_content = "\"Date\",\"Description\",\"Amount\"\n"
        utf8_content += "\"01/01/2024\",\"Café\",\"100.00\"\n"
        
        # Save with UTF-8 encoding
        file_path = Path(self.temp_dir.name) / "utf8_encoded.csv"
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(utf8_content)
            
        results = process_transaction_file(str(file_path))
        self.assertEqual(len(results), 1, "Should handle UTF-8 encoding")
    
    def test_large_number_of_columns(self):
        """Test handling of files with many columns."""
        # Create a CSV with many columns
        header = ",".join([f"Column{i}" for i in range(50)])
        row = ",".join([""] * 50)  # Empty values
        large_columns = f"{header}\n{row}\n"
        
        file_path = self.create_temp_file(large_columns, "large_columns.csv")
        # Should not raise any exceptions
        results = process_transaction_file(str(file_path))
        self.assertEqual(len(results), 0, "Should handle files with many columns")

if __name__ == '__main__':
    unittest.main()