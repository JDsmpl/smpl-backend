import os
import json
import magic
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Union, Optional
from pathlib import Path

class TransactionProcessor:
    """
    Processes financial transaction files (CSV, Excel, PDF) and normalizes the data.
    """
    
    def __init__(self):
        self.mime = magic.Magic(mime=True)
        
    def process_transaction_file(self, file_path: Union[str, Path]) -> List[Dict[str, Any]]:
        """
        Process a transaction file and return normalized transactions.
        
        Args:
            file_path: Path to the transaction file
            
        Returns:
            List of normalized transaction dictionaries
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        # Detect file type
        file_type = self._detect_file_type(file_path)
        
        # Extract raw data based on file type
        if file_type == 'text/csv':
            df = pd.read_csv(file_path)
        elif file_type in ['application/vnd.ms-excel', 
                          'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet']:
            df = pd.read_excel(file_path)
        elif file_type == 'application/pdf':
            # PDF processing would go here
            raise NotImplementedError("PDF processing not yet implemented")
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
        
        # Normalize and categorize transactions
        return self._process_dataframe(df)
    
    def _detect_file_type(self, file_path: Path) -> str:
        """Detect the MIME type of the file."""
        return self.mime.from_file(str(file_path))
    
    def _process_dataframe(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Process a pandas DataFrame and return normalized transactions."""
        transactions = []
        
        # Simple mapping of common merchant names to categories
        CATEGORY_MAP = {
            'costco': 'Groceries',
            'walmart': 'Groceries',
            'target': 'Shopping',
            'amazon': 'Shopping',
            'netflix': 'Entertainment',
            'spotify': 'Entertainment',
            'electric': 'Utilities',
            'water': 'Utilities',
            'internet': 'Utilities',
            'at&t': 'Phone',
            'verizon': 'Phone',
            't-mobile': 'Phone',
        }
        
        # Process each row in the dataframe
        for _, row in df.iterrows():
            try:
                # This is a simplified example - you'll need to adjust based on your actual data format
                # and add proper error handling for different column names/formats
                
                # Try to get amount and determine if it's income or expense
                amount = self._extract_amount(row)
                if amount == 0:  # Skip zero-amount transactions
                    continue
                    
                # Create normalized transaction
                transaction = {
                    'date': self._extract_date(row),
                    'name': self._clean_merchant_name(self._extract_merchant(row)),
                    'amount': amount,
                    'type': 'income' if amount > 0 else 'expense',
                }
                
                # Add categorization
                self._categorize_transaction(transaction, CATEGORY_MAP)
                
                transactions.append(transaction)
                
            except (ValueError, KeyError, AttributeError) as e:
                # Skip rows that can't be processed
                print(f"Skipping row: {e}")
                continue
                
        return transactions
    
    def _extract_amount(self, row) -> float:
        """Extract and normalize amount from a row."""
        # This is a simplified example - you'll need to adjust based on your actual data format
        amount_fields = ['amount', 'transaction_amount', 'debit', 'credit']
        for field in amount_fields:
            if field in row and pd.notna(row[field]):
                amount = float(row[field])
                # If it's a credit/debit field, make sure the sign is correct
                if field == 'debit' and amount > 0:
                    return -amount
                elif field == 'credit' and amount > 0:
                    return amount
                return amount
        return 0.0
    
    def _extract_date(self, row) -> str:
        """Extract and format date from a row."""
        # This is a simplified example - you'll need to adjust based on your actual data format
        date_fields = ['date', 'transaction_date', 'posted_date']
        for field in date_fields:
            if field in row and pd.notna(row[field]):
                try:
                    # Try to parse the date
                    date = pd.to_datetime(row[field])
                    return date.strftime('%Y-%m-%d')
                except (ValueError, TypeError):
                    continue
        raise ValueError("No valid date field found")
    
    def _extract_merchant(self, row) -> str:
        """Extract merchant name from a row."""
        # This is a simplified example - you'll need to adjust based on your actual data format
        name_fields = ['name', 'merchant', 'description', 'merchant_name']
        for field in name_fields:
            if field in row and pd.notna(row[field]):
                return str(row[field])
        return "Unknown"
    
    def _clean_merchant_name(self, name: str) -> str:
        """
        Clean and normalize merchant names while preserving important identifiers.
        
        Args:
            name: The merchant name to clean
            
        Returns:
            str: Cleaned and normalized merchant name
        """
        if pd.isna(name) or not str(name).strip():
            return "Unknown"
            
        # Convert to string and clean up whitespace
        name = ' '.join(str(name).split())
        
        # Handle specific merchant patterns first
        patterns = [
            # Amazon patterns - preserve .Com capitalization
            (r'(?i)^amazon\.com$', 'Amazon.Com'),
            # Walmart patterns - preserve store numbers
            (r'(?i)^(walmart)\s*(?:supercenter|neighborhood market|store)?\s*(#\d+)?$', 
             lambda m: f"{m.group(1).title()} {m.group(2) if m.group(2) else ''}".strip()),
            # Target patterns - preserve location info
            (r'(?i)^(target)\s*(store)?\s*(.*)$', 
             lambda m: f"{m.group(1).title()} Store {m.group(3).title()}".strip() if m.group(3) else f"{m.group(1).title()}"),
            # Shell patterns - preserve brand name
            (r'(?i)^(shell)\s*(oil)?\s*(.*)$', 
             lambda m: f"{m.group(1).title()} {m.group(2).title() if m.group(2) else ''}".strip()),
            # Starbucks patterns - preserve card indicator
            (r'(?i)^(starbucks)\s*(card)?\s*(.*)$', 
             lambda m: f"{m.group(1).title()} {m.group(2).title() if m.group(2) else ''}".strip())
        ]
        
        # Apply patterns
        for pattern, replacement in patterns:
            match = re.match(pattern, name, re.IGNORECASE)
            if match:
                if callable(replacement):
                    return replacement(match)
                return re.sub(pattern, replacement, name, flags=re.IGNORECASE)
        
        # If no pattern matched, clean up the name
        
        # Remove common suffixes and clean up
        suffixes = [
            'llc', 'inc', 'ltd', 'corp', 'llp', 'plc', 'lp', 'l.p.', 'company', 'co',
            'corporation', 'incorporated', 'limited', 'holdings', 'group', 'enterprises',
            'store', 'market', 'shop', 'outlet'
        ]
        
        # Remove suffixes with optional punctuation and whitespace
        suffix_pattern = r'(?:\s*[,-]?\s*(?:' + '|'.join(re.escape(s) + r'\b\.?' for s in suffixes) + '))+'
        name = re.sub(suffix_pattern, '', name, flags=re.IGNORECASE)
        
        # Remove any standalone numbers (but preserve numbers that are part of words)
        name = re.sub(r'\b\d+\b', '', name)
        
        # Clean up any remaining special characters except spaces, &, #, and '
        name = re.sub(r"[^\w\s&#']", ' ', name)
        
        # Clean up whitespace
        name = ' '.join(name.split())
        
        # Title case the name while preserving certain words in lowercase
        words = name.split()
        if not words:
            return "Unknown"
            
        lowercase_words = {'a', 'an', 'and', 'as', 'at', 'by', 'for', 'in', 'of', 'or', 'the', 'to', 'with'}
        
        # Special case for names with dots (like Amazon.Com)
        if '.' in words[0]:
            parts = words[0].split('.')
            words[0] = f"{parts[0].title()}.{parts[1].title() if len(parts) > 1 else ''}"
        
        # Process each word
        for i, word in enumerate(words):
            if i == 0 or word.lower() not in lowercase_words:
                # Capitalize first letter, lowercase the rest
                if word and len(word) > 1:
                    words[i] = word[0].upper() + word[1:].lower()
                elif word:
                    words[i] = word.upper()  # Single letter
        
        return ' '.join(words).strip()
    
    def _categorize_transaction(self, transaction: Dict[str, Any], category_map: Dict[str, str]) -> None:
        """Categorize a transaction into fundamental and subcategories."""
        # Default category
        transaction['category'] = 'Other'
        
        # Check if merchant name matches any category
        name = transaction['name'].lower()
        for keyword, category in category_map.items():
            if keyword in name:
                transaction['category'] = category
                break
        
        # Simple categorization into fundamental categories
        if transaction['amount'] > 0:
            transaction['fundamental'] = 'Income'
        else:
            transaction['fundamental'] = 'Expenses'  # Default, can be overridden below
            
            # Simple rules for other fundamentals
            if any(kw in name for kw in ['payment', 'loan', 'credit card', 'mortgage']):
                transaction['fundamental'] = 'Debts'
            elif any(kw in name for kw in ['savings', 'emergency fund']):
                transaction['fundamental'] = 'Savings'
            elif any(kw in name for kw in ['investment', 'robinhood', 'fidelity', 'vanguard']):
                transaction['fundamental'] = 'Investments'
        
        # Simple essential vs lifestyle categorization
        essential_categories = [
            'Groceries', 'Rent', 'Mortgage', 'Utilities', 'Insurance', 
            'Healthcare', 'Phone', 'Internet', 'Transportation', 'Debts'
        ]
        transaction['essential'] = transaction['category'] in essential_categories or \
                                 transaction['fundamental'] in ['Debts', 'Savings']
        
        # Simple fixed vs variable (this is very basic and should be enhanced)
        fixed_keywords = [
            'rent', 'mortgage', 'insurance', 'phone', 'internet', 'subscription',
            'netflix', 'spotify', 'membership', 'loan payment'
        ]
        transaction['fixed'] = any(kw in name for kw in fixed_keywords)


def process_transaction_file(file_path: Union[str, Path]) -> List[Dict[str, Any]]:
    """
    Process a transaction file and return normalized transactions.
    
    This is the main entry point for the module.
    
    Args:
        file_path: Path to the transaction file (CSV, Excel, or PDF)
        
    Returns:
        List of normalized transaction dictionaries
    """
    processor = TransactionProcessor()
    return processor.process_transaction_file(file_path)
