import chardet
from pathlib import Path

csv_path = Path("files/Staff.csv")
if csv_path.exists():
    with open(csv_path, 'rb') as f:
        rawdata = f.read(10000)
        result = chardet.detect(rawdata)
        print(f"Detected encoding for Staff.csv: {result}")
else:
    print("Staff.csv not found")

excel_path = Path("files/Staff Details - Dindigul as on 11052026.xlsx")
if excel_path.exists():
    print("Excel file exists")
