"""
Core transaction processing functionality for handling financial documents.
"""

import re
import os
from typing import Dict, List, Optional, Tuple, Union, Any, Set
from pathlib import Path
from dataclasses import dataclass, field, asdict
from enum import Enum, auto
import pandas as pd
import numpy as np
import dateparser
from unidecode import unidecode
from loguru import logger
import json
from datetime import datetime
from .categories import CATEGORY_PATTERNS, ESSENTIAL_CATEGORIES, FIXED_CATEGORIES

# Configure logging
logger.remove()  # Remove default handler
logger.add(
    "transaction_processor.log",
    rotation="10 MB",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    encoding="utf-8"
)

class AccountType(Enum):
    """Types of financial accounts."""
    UNKNOWN = auto()
    CREDIT_CARD = auto()
    BANK_ACCOUNT = auto()
    INVESTMENT = auto()

@dataclass
class Transaction:
    """Represents a normalized financial transaction."""
    date: str
    name: str
    amount: float
    type: str = "expense"  # Default to expense unless determined otherwise
    category: str = "Other"
    fundamental: str = "Expenses"
    essential: bool = False
    fixed: bool = False
    original_data: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert transaction to dictionary, including all fields."""
        return asdict(self)

class TransactionProcessor:
    """Processes financial transactions from various file formats."""
    
    def __init__(self, debug: bool = False):
        self.debug = debug
        self.account_type = AccountType.UNKNOWN
        self.column_mapping = {}
        
        # Define keywords for categorization
        self.income_keywords = [
            "payroll", "deposit", "interest", "refund", "payment received",
            "direct dep", "credit", "dividend", "transfer in", "paycheck"
        ]
        
        # Use category patterns from the imported module
        self.category_patterns = CATEGORY_PATTERNS
    
    def log_debug(self, message: str):
        """Log debug messages if debug mode is enabled."""
        if self.debug:
            logger.debug(message)
            print(f"DEBUG: {message}")
    
    def process_file(self, file_path: Union[str, Path]) -> List[Dict[str, Any]]:
        """
        Process a financial document and return normalized transactions.
        
        Args:
            file_path: Path to the file to process
            
        Returns:
            List of dictionaries containing normalized transaction data
        """
        try:
            file_path = Path(file_path)
            self.log_debug(f"Processing file: {file_path.name}")
            
            # Read the file
            df = self._read_file(file_path)
            if df.empty:
                print("No data found in file")
                return []
            
            # Detect account type
            self._detect_account_type(df, file_path.name)
            
            # Map columns to standard names and validate required columns
            if not self._map_columns(df):
                print("Error: Missing required columns in the input file")
                return []
            
            # Process transactions
            transactions = self._process_transactions(df)
            
            # Convert to dictionaries for return
            result = [t.to_dict() for t in transactions]
            logger.info(f"Successfully processed {len(result)} transactions")
            print(f"Successfully processed {len(result)} transactions")
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing file: {str(e)}")
            print(f"Error processing file: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return []
    
    def _read_file(self, file_path: Path) -> pd.DataFrame:
        """
        Read file based on its type, with robust error handling for CSV files.
        
        Args:
            file_path: Path to the file to read
            
        Returns:
            pd.DataFrame: DataFrame containing the file data
            
        Raises:
            ValueError: If the file type is not supported or cannot be read
        """
        suffix = file_path.suffix.lower()
        
        def read_csv_with_retry(file_path, encoding='utf-8', **kwargs):
            """Helper function to read CSV with retry logic and error handling."""
            try:
                # First, try reading with standard parameters
                df = pd.read_csv(
                    file_path,
                    encoding=encoding,
                    quotechar='"',
                    escapechar='\\',  # Handle escape characters
                    quoting=1,  # QUOTE_MINIMAL
                    on_bad_lines='warn',
                    dtype=str,  # Read all columns as strings initially
                    keep_default_na=False,
                    na_values=['', ' ', 'NA', 'N/A', 'NULL', 'None'],
                    skipinitialspace=True,
                    engine='python',  # More consistent handling of quoted fields
                    **kwargs
                )
                return df
            except pd.errors.ParserError as e:
                # If parsing fails, try with error_bad_lines=False to skip problematic lines
                try:
                    return pd.read_csv(
                        file_path,
                        encoding=encoding,
                        quotechar='"',
                        escapechar='\\',  # Handle escape characters
                        quoting=1,
                        error_bad_lines=False,
                        warn_bad_lines=True,
                        dtype=str,
                        keep_default_na=False,
                        na_values=['', ' '],
                        skipinitialspace=True,
                        engine='python'
                    )
                except Exception as inner_e:
                    raise ValueError(f"Failed to parse CSV file: {str(inner_e)}") from inner_e
            except Exception as e:
                raise ValueError(f"Error reading CSV file: {str(e)}") from e
        
        try:
            if suffix == '.csv':
                # First try with UTF-8 encoding
                try:
                    return read_csv_with_retry(file_path, encoding='utf-8')
                except UnicodeDecodeError:
                    # Fall back to latin1 if UTF-8 fails
                    return read_csv_with_retry(file_path, encoding='latin1')
            elif suffix in ['.xls', '.xlsx']:
                return pd.read_excel(file_path)
            elif suffix == '.pdf':
                # PDF processing would go here
                raise NotImplementedError("PDF processing not yet implemented")
            else:
                raise ValueError(f"Unsupported file type: {suffix}")
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {str(e)}")
            raise
    
    def _detect_account_type(self, df: pd.DataFrame, filename: str) -> None:
        """Detect the type of financial account."""
        # Check column names for clues
        columns = ' '.join(df.columns.astype(str).str.lower())
        
        # Check for keywords in filename
        if any(keyword in filename.lower() for keyword in ['credit', 'card', 'visa', 'mastercard']):
            self.account_type = AccountType.CREDIT_CARD
        elif any(keyword in filename.lower() for keyword in ['checking', 'savings', 'bank']):
            self.account_type = AccountType.BANK_ACCOUNT
        elif any(keyword in filename.lower() for keyword in ['investment', 'trading', 'brokerage']):
            self.account_type = AccountType.INVESTMENT
        
        # Check column content clues
        if self.account_type == AccountType.UNKNOWN:
            # Sample some values to look for clues
            sample_values = []
            for col in df.columns:
                try:
                    values = df[col].dropna().astype(str).head(5).tolist()
                    sample_values.extend(values)
                except:
                    pass
            
            sample_text = ' '.join([str(val).lower() for val in sample_values])
            
            if any(term in sample_text for term in ['credit card', 'available credit', 'minimum payment']):
                self.account_type = AccountType.CREDIT_CARD
            elif any(term in sample_text for term in ['deposit', 'withdrawal', 'available balance']):
                self.account_type = AccountType.BANK_ACCOUNT
        
        # Default to credit card if still unknown - most common type
        if self.account_type == AccountType.UNKNOWN:
            self.account_type = AccountType.CREDIT_CARD
        
        self.log_debug(f"Detected account type: {self.account_type.name}")
    
    def _map_columns(self, df: pd.DataFrame) -> bool:
        """
        Map input columns to standard names.
        
        Returns:
            bool: True if all required columns are present and mapped, False otherwise
        """
        col_map = {}
        # Convert column names to lowercase for case-insensitive matching
        cols_lower = {col.lower(): col for col in df.columns}
        
        # First, try to map required columns using patterns
        # Date column
        date_mapped = False
        date_patterns = ['date', 'transaction date', 'post date', 'posted date', 'time']
        for pattern in date_patterns:
            if pattern in cols_lower:
                col_map['date'] = cols_lower[pattern]
                date_mapped = True
                break
        
        # Description column
        desc_mapped = False
        desc_patterns = ['description', 'transaction', 'merchant', 'details', 'name', 'payee']
        for pattern in desc_patterns:
            if pattern in cols_lower:
                col_map['description'] = cols_lower[pattern]
                desc_mapped = True
                break
        
        # Amount column(s)
        amount_mapped = False
        amount_patterns = ['amount', 'amt', 'value', 'transaction amount']
        for pattern in amount_patterns:
            if pattern in cols_lower:
                col_map['amount'] = cols_lower[pattern]
                amount_mapped = True
                break
        
        # Check for separate debit/credit columns if amount not found
        has_debit = False
        has_credit = False
        if not amount_mapped:
            debit_patterns = ['debit', 'withdrawal', 'charge', 'expense', 'payment']
            credit_patterns = ['credit', 'deposit', 'refund', 'return']
            
            for pattern in debit_patterns:
                if pattern in cols_lower:
                    col_map['debit'] = cols_lower[pattern]
                    has_debit = True
                    break
            
            for pattern in credit_patterns:
                if pattern in cols_lower:
                    col_map['credit'] = cols_lower[pattern]
                    has_credit = True
                    break
        
        # Validate required columns before any fallback
        required_columns = ['date', 'description']
        
        # Check if we have either amount or both debit/credit
        has_amount = 'amount' in col_map
        has_both_debit_credit = 'debit' in col_map and 'credit' in col_map
        
        # If we don't have amount or both debit/credit, we're missing required columns
        if not has_amount and not has_both_debit_credit:
            return False
        
        # If we're missing any required columns, don't use fallbacks
        if not all(col in col_map for col in required_columns):
            return False
        
        # Only use fallbacks for non-required columns if we have all required ones
        if 'date' not in col_map and len(df.columns) > 0:
            col_map['date'] = df.columns[0]
        
        if 'description' not in col_map and len(df.columns) > 1:
            col_map['description'] = df.columns[1]
        
        # Only use amount fallback if we don't have either amount or debit/credit
        if not has_amount and not has_both_debit_credit and len(df.columns) > 2:
            col_map['amount'] = df.columns[2]
        
        self.column_mapping = col_map
        self.log_debug(f"Column mapping: {col_map}")
        
        # Final validation
        return all(col in col_map for col in required_columns)
    
    def _process_transactions(self, df: pd.DataFrame) -> List[Transaction]:
        """
        Process and normalize transactions from the dataframe.
        
        Args:
            df: DataFrame containing transaction data with mapped columns
            
        Returns:
            List of processed Transaction objects
        """
        transactions = []
        skipped_count = 0
        
        for idx, row in df.iterrows():
            try:
                # Skip rows with missing description
                date_col = self.column_mapping.get('date')
                desc_col = self.column_mapping.get('description')
                
                if pd.isna(row.get(desc_col)):
                    skipped_count += 1
                    continue

                # Try primary date column first, then fallback to alternatives
                date = None
                if date_col and not pd.isna(row.get(date_col)):
                    date = self._parse_date(row[date_col])
                else:
                    # Try fallback date columns
                    for alt_date_col in ['Posting Date', 'Post Date', 'Effective Date', 'Transaction Date']:
                        if alt_date_col in row and not pd.isna(row[alt_date_col]):
                            date = self._parse_date(row[alt_date_col])
                            if date:
                                break

                if not date:
                    skipped_count += 1
                    continue

                # Handle amount - either single column or separate Debit/Credit
                amount = None
                if 'amount' in self.column_mapping and not pd.isna(row.get(self.column_mapping['amount'])):
                    # Handle single amount column
                    amount = self._parse_amount(row[self.column_mapping['amount']])
                elif 'debit' in self.column_mapping and 'credit' in self.column_mapping:
                    # Handle separate Debit and Credit columns
                    try:
                        debit = float(row.get(self.column_mapping['debit']) or 0)
                        credit = float(row.get(self.column_mapping['credit']) or 0)
                        amount = credit - debit
                    except (ValueError, TypeError):
                        pass

                if amount is None:
                    skipped_count += 1
                    continue
                
                # Get description for determining transaction type
                desc_col = self.column_mapping.get('description', '')
                description = str(row[desc_col]).lower() if desc_col and desc_col in row else ""
                
                # Handle transaction sign based on description and account type
                if self.account_type == AccountType.CREDIT_CARD:
                    # Check if the original value was in scientific notation
                    amount_str = str(amount)
                    is_scientific = 'e' in amount_str.lower()
                    
                    # For credits/refunds, ensure amount is positive
                    if any(keyword in description for keyword in ['payment', 'credit', 'refund', 'return']):
                        amount = abs(amount)
                    # For clear expenses, ensure amount is negative
                    elif any(expense_term in description for expense_term in ['purchase', 'sale', 'charge', 'fee']):
                        amount = -abs(amount)
                    # For large non-scientific amounts, treat as expense
                    elif not is_scientific and abs(amount) >= 1000:
                        amount = -abs(amount)
                    # Otherwise, preserve the original sign
                
                # Get description/merchant name
                desc_col = self.column_mapping.get('description', '')
                description = str(row[desc_col]) if desc_col and desc_col in row else ""
                
                # Create transaction
                txn = Transaction(
                    date=date,
                    name=self._clean_description(description),
                    amount=amount,
                    original_data=row.to_dict()
                )
                
                # Determine transaction type and categorize
                self._determine_transaction_type(txn)
                self._categorize_transaction(txn)
                
                transactions.append(txn)
                
            except Exception as e:
                self.log_debug(f"Skipping row {idx + 1} due to error: {str(e)}")
                skipped_count += 1
                continue
                
        if skipped_count > 0:
            logger.warning(f"Skipped {skipped_count} rows due to errors or missing data")
            print(f"Skipped {skipped_count} rows due to errors or missing data")
        
        return transactions
    
    def _parse_date(self, date_val: Any) -> Optional[str]:
        """
        Parse date string into ISO format (YYYY-MM-DD).
        
        Args:
            date_val: The date value to parse (can be string, datetime, or other types)
            
        Returns:
            str: Date in YYYY-MM-DD format, or None if parsing fails
        """
        if pd.isna(date_val) or not str(date_val).strip():
            return None
        
        date_str = str(date_val).strip()
        
        # If it's already a datetime object, format it
        if isinstance(date_val, (datetime, pd.Timestamp)):
            return date_val.strftime('%Y-%m-%d')
        
        # Common date patterns to try
        date_patterns = [
            '%Y-%m-%d',      # 2023-01-15
            '%m/%d/%Y',      # 01/15/2023
            '%d/%m/%Y',      # 15/01/2023
            '%m-%d-%Y',      # 01-15-2023
            '%d-%m-%Y',      # 15-01-2023
            '%Y/%m/%d',      # 2023/01/15
            '%b %d, %Y',     # Jan 15, 2023
            '%B %d, %Y',     # January 15, 2023
            '%d %b %Y',      # 15 Jan 2023
            '%d %B %Y',      # 15 January 2023
            '%Y%m%d',        # 20230115
            '%m/%d/%y',      # 01/15/23 (2-digit year)
            '%d/%m/%y'       # 15/01/23 (2-digit year)
        ]
        
        # First try parsing with known patterns
        for pattern in date_patterns:
            try:
                dt = datetime.strptime(date_str, pattern)
                return dt.strftime('%Y-%m-%d')
            except (ValueError, TypeError):
                continue
        
        # If no pattern matched, try dateparser as fallback
        try:
            dt = dateparser.parse(date_str, settings={
                'DATE_ORDER': 'MDY',  # Default to Month-Day-Year for ambiguous dates
                'PREFER_DAY_OF_MONTH': 'first',
                'PREFER_LOCALE_DATE_ORDER': True
            })
            if dt:
                return dt.strftime('%Y-%m-%d')
        except Exception as e:
            self.log_debug(f"Date parsing error with dateparser for '{date_str}': {e}")
        
        self.log_debug(f"Failed to parse date: {date_str}")
        return None
    
    def _clean_description(self, name: str) -> str:
        name = str(name).strip()
        if name.isupper() and len(name) > 1:
            name = name.title()
        return name
    
    def _parse_amount(self, raw: Any) -> Optional[float]:
        import pandas as pd

        # If raw is a Series or DataFrame row, extract the 'Amount' field
        if isinstance(raw, pd.Series) and 'Amount' in raw:
            raw = raw['Amount']

        if pd.isna(raw) or str(raw).lower() in ("nan", "none", ""):
            return None

        raw = str(raw).strip()

        # Handle parentheses for negatives
        if raw.startswith("(") and raw.endswith(")"):
            raw = "-" + raw[1:-1]

        # Remove currency symbols and thousand separators
        raw = raw.replace("$", "").replace(",", "")

        try:
            return float(raw)
        except ValueError:
            return None
    
    def _determine_transaction_type(self, txn: Transaction) -> None:
        """Determine the type of transaction based on description and amount."""
        description = txn.name.lower()
        
        # Positive amount means income in our normalized data
        if txn.amount > 0:
            if any(keyword in description for keyword in ["dividend", "interest"]):
                txn.type = "investment"
                txn.fundamental = "Investments"
            else:
                txn.type = "income"
                txn.fundamental = "Income"
        # Negative amount means expense or other outflow in our normalized data
        else:
            # Check for loan/debt payments
            if any(term in description for term in ["loan payment", "mortgage", "credit card payment"]):
                txn.type = "debt"
                txn.fundamental = "Debts"
            # Check for transfers to savings/investments
            elif any(term in description for term in ["transfer to savings", "401k", "ira contribution"]):
                if "savings" in description:
                    txn.type = "savings"
                    txn.fundamental = "Savings"
                else:
                    txn.type = "investment"
                    txn.fundamental = "Investments"
            # Default to expense
            else:
                txn.type = "expense"
                txn.fundamental = "Expenses"
    
    def _categorize_transaction(self, txn: Transaction) -> None:
        """
        Categorize transaction and set essential/fixed flags.
        
        Args:
            txn: The transaction to categorize
        """
        description = txn.name.lower()
        
        # Set category based on description patterns
        txn.category = "Other"  # Default category
        
        # Check for matching category patterns
        for category, patterns in self.category_patterns.items():
            if any(pattern in description for pattern in patterns):
                txn.category = category
                break
        
        # Set essential flag based on category
        txn.essential = txn.category in ESSENTIAL_CATEGORIES
        
        # Set fixed flag based on category or description
        txn.fixed = (txn.category in FIXED_CATEGORIES or 
                    any(term in description for term in ["subscription", "membership"]))

# Function for backward compatibility
def process_transaction_file(file_path: str, debug: bool = False) -> List[Dict[str, Any]]:
    """Process a transaction file and return normalized transactions."""
    processor = TransactionProcessor(debug=debug)
    return processor.process_file(file_path)