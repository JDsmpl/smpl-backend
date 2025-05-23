#!/usr/bin/env python3
"""
Example usage of the transaction processor.
"""
import json
import sys
from transaction_processor import process_transaction_file

def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <transaction_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    try:
        # Process the transaction file
        transactions = process_transaction_file(input_file)
        
        # Print the results
        print(json.dumps(transactions, indent=2))
        print(f"\nProcessed {len(transactions)} transactions.")
        
    except Exception as e:
        print(f"Error processing file: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
