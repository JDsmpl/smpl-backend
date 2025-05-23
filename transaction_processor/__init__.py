"""
Transaction Processor for financial documents.

This module provides functionality to process and normalize financial transactions
from various file formats including CSV, Excel, and PDF.
"""

from .core import TransactionProcessor, Transaction, AccountType

def process_transaction_file(file_path: str, debug: bool = False) -> list:
    """
    Process a financial document and return normalized transactions.
    
    Args:
        file_path: Path to the transaction file (CSV, Excel, or PDF)
        debug: If True, enables debug logging
        
    Returns:
        List of dictionaries containing normalized transaction data
        
    Example:
        >>> transactions = process_transaction_file('transactions.csv')
        >>> debug_transactions = process_transaction_file('transactions.csv', debug=True)
        >>> for txn in transactions:
        ...     print(f"{txn['date']} {txn['name']}: {txn['amount']}")
    """
    processor = TransactionProcessor(debug=debug)
    return processor.process_file(file_path)

__all__ = ['process_transaction_file', 'Transaction', 'AccountType']
