import pandas as pd
from pathlib import Path

excel_path = Path("files/Staff Details - Dindigul as on 11052026.xlsx")
if excel_path.exists():
    df = pd.read_excel(excel_path)
    print("Columns:", df.columns.tolist())
    print("Head:\n", df.head())
else:
    print("Excel file not found")
