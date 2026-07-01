"""
XLSX/CSV loader using pandas.
Each sheet becomes a separate "page", column headers included.
"""
import pandas as pd
from typing import List, Dict, Any
from pathlib import Path


def load_xlsx(file_path: str) -> List[Dict[str, Any]]:
    """
    Load an Excel or CSV file.
    Returns each sheet as a page with a text representation of the data.
    """
    path = Path(file_path)
    pages = []
    suffix = path.suffix.lower()

    try:
        if suffix == ".csv":
            sheets = {"Sheet1": pd.read_csv(str(path))}
        else:
            xf = pd.ExcelFile(str(path))
            sheets = {name: xf.parse(name) for name in xf.sheet_names}

        for sheet_name, df in sheets.items():
            # Convert to readable text format
            df = df.fillna("")
            text_lines = [f"Sheet: {sheet_name}"]
            text_lines.append("Columns: " + ", ".join(str(c) for c in df.columns.tolist()))
            text_lines.append("")

            for idx, row in df.iterrows():
                row_str = " | ".join(f"{col}: {val}" for col, val in row.items() if str(val).strip())
                if row_str:
                    text_lines.append(row_str)

            pages.append({
                "page_number": 1,
                "text": "\n".join(text_lines),
                "section_heading": sheet_name,
                "source": path.name,
                "file_path": str(path),
                "file_type": suffix.lstrip("."),
            })

    except Exception as e:
        raise ValueError(f"Failed to load XLSX/CSV '{file_path}': {e}")

    return pages
