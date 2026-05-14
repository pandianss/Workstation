import pandas as pd
from pathlib import Path

excel_path = Path("files/Staff Details - Dindigul as on 11052026.xlsx")
if excel_path.exists():
    df = pd.read_excel(excel_path)
    # Filter for BR Cd == 3933 or RollNo == 36614
    ro_staff = df[(df['BR Cd'].astype(str) == '3933') | (df['RollNo'].astype(str) == '36614')]
    print("RO Staff from Excel:\n", ro_staff[['RollNo', 'Name', 'Designation', 'BR Cd']])
else:
    print("Excel file not found")
