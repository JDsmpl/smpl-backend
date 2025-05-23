# Transaction Processor

A Python library for processing financial transaction files (CSV, Excel) and normalizing them into a consistent format. Hello

## Installation

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

```python
from transaction_processor import process_transaction_file

# Process a transaction file
transactions = process_transaction_file("path/to/your/transactions.csv")

# Print the normalized transactions
import json
print(json.dumps(transactions, indent=2))
```

## Supported File Formats

- CSV (`.csv`)
- Excel (`.xlsx`, `.xls`)
- PDF (coming soon)

## Transaction Format

Each transaction is returned as a dictionary with the following fields:

- `date` (str): Date in YYYY-MM-DD format
- `name` (str): Cleaned merchant name
- `amount` (float): Signed amount (negative for expenses, positive for income)
- `type` (str): One of 'income', 'expense', 'debt', 'savings', 'investment'
- `category` (str): Transaction category (e.g., 'Groceries', 'Utilities')
- `fundamental` (str): One of 'Income', 'Expenses', 'Debts', 'Savings', 'Investments'
- `essential` (bool): Whether the expense is essential
- `fixed` (bool): Whether the expense is fixed (vs. variable)

## Extending the Processor

To handle custom file formats or add new categorization rules, you can extend the `TransactionProcessor` class and override the appropriate methods.

## License

MIT
