#!/usr/bin/env python3
"""
Test script for the transaction processor.
"""

import json
import sys
from pathlib import Path
from transaction_processor import process_transaction_file

def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <transaction_file>")
        sys.exit(1)
    
    input_file = Path(sys.argv[1])
    if not input_file.exists():
        print(f"Error: File not found: {input_file}")
        sys.exit(1)
    
    try:
        # Process the transaction file
        transactions = process_transaction_file(input_file)
        
        # Print the results
        print(json.dumps(transactions, indent=2))
        print(f"\nSuccessfully processed {len(transactions)} transactions.")
        
        # Optional: Save to output file
        output_file = input_file.with_suffix('.processed.json')
        with open(output_file, 'w') as f:
            json.dump(transactions, f, indent=2)
        print(f"Results saved to: {output_file}")
        
    except Exception as e:
        print(f"Error processing file: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
