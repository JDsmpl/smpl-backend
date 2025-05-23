"""
File reading utilities for the transaction processor.
"""

import pandas as pd
from pathlib import Path
from typing import Union, Any

def detect_file_type(file_path: Union[str, Path]) -> str:
    """
    Detect the type of file based on extension.
    
    Args:
        file_path: Path to the file
        
    Returns:
        str: File type ('csv', 'excel', 'pdf')
        
    Raises:
        ValueError: If the file type is not supported
    """
    file_path = Path(file_path)
    suffix = file_path.suffix.lower()
    
    if suffix == '.csv':
        return 'csv'
    elif suffix in ['.xls', '.xlsx']:
        return 'excel'
    elif suffix == '.pdf':
        return 'pdf'
    else:
        raise ValueError(f"Unsupported file type: {suffix}")

def read_csv_file(file_path: Union[str, Path]) -> pd.DataFrame:
    """
    Read a CSV file into a pandas DataFrame with proper handling of special characters.
    
    Args:
        file_path: Path to the CSV file
        
    Returns:
        pd.DataFrame: DataFrame containing the CSV data
        
    Raises:
        pd.errors.EmptyDataError: If the file is empty
        pd.errors.ParserError: If the file cannot be parsed
    """
    # Common encodings to try
    encodings = ['utf-8', 'latin1', 'iso-8859-1', 'cp1252']
    
    for encoding in encodings:
        try:
            return pd.read_csv(
                file_path,
                encoding=encoding,
                escapechar='\\',  # Handle backslashes in text
                quotechar='"',     # Standard quote character
                doublequote=True,  # Handle doubled quotes within fields
                error_bad_lines=False,  # Skip malformed lines
                warn_bad_lines=True,    # But warn about them
                dtype=str,             # Read all columns as strings initially
                keep_default_na=False,  # Don't interpret 'NA' as NaN
                na_values=[],          # Don't interpret any values as NaN
                skip_blank_lines=True  # Skip empty lines
            )
        except UnicodeDecodeError:
            continue
        except pd.errors.ParserError as e:
            if encoding == encodings[-1]:  # If this was our last encoding attempt
                raise pd.errors.ParserError(f"Failed to parse CSV file after trying multiple encodings: {e}")
            continue
    
    # If we get here, all encoding attempts failed
    raise UnicodeDecodeError("Failed to decode file with any of the supported encodings")

def read_excel_file(file_path: Union[str, Path]) -> pd.DataFrame:
    """
    Read an Excel file into a pandas DataFrame.
    
    Args:
        file_path: Path to the Excel file
        
    Returns:
        pd.DataFrame: DataFrame containing the Excel data
    """
    return pd.read_excel(file_path)

def read_pdf_file(file_path: Union[str, Path]) -> pd.DataFrame:
    """
    Read a PDF file into a pandas DataFrame.
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        pd.DataFrame: DataFrame containing the PDF data
        
    Raises:
        NotImplementedError: PDF support is not yet implemented
    """
    raise NotImplementedError("PDF processing not yet implemented")

def read_file(file_path: Union[str, Path]) -> pd.DataFrame:
    """
    Read a file of any supported type into a pandas DataFrame.
    
    Args:
        file_path: Path to the file
        
    Returns:
        pd.DataFrame: DataFrame containing the file data
        
    Raises:
        ValueError: If the file type is not supported
    """
    file_type = detect_file_type(file_path)
    
    if file_type == 'csv':
        return read_csv_file(file_path)
    elif file_type == 'excel':
        return read_excel_file(file_path)
    elif file_type == 'pdf':
        return read_pdf_file(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_type}")