from transaction_processor.core import process_transaction_file
from pathlib import Path

# Folder containing your real CSVs
data_dir = Path("test_transaction_data")

# List the files you want to test
files = [
    "March2025_0111.csv",
    "April2025_0111.csv",
    "Chase0139_Activity20240101_20250502_20250502.CSV",
    "currentTransaction_0111.csv",
    "ExportedTransactions (10).csv",
    "Date range (6).CSV",
]

for filename in files:
    file_path = data_dir / filename
    print(f"\n📄 Processing: {filename}")
    try:
        transactions = process_transaction_file(str(file_path))
        print(f"✅ {len(transactions)} transactions processed")
        print("🔍 Sample:")
        for tx in transactions[:3]:  # Show a preview
            print(" ", tx)
    except Exception as e:
        print(f"❌ Error processing {filename}: {e}")
