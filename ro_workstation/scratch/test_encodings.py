import codecs
from pathlib import Path

csv_path = Path("files/Staff.csv")
encodings = ['utf-8', 'latin-1', 'cp1252', 'utf-16']

if csv_path.exists():
    with open(csv_path, 'rb') as f:
        data = f.read(5000)
    
    for enc in encodings:
        try:
            data.decode(enc)
            print(f"Decoded successfully with: {enc}")
        except UnicodeDecodeError as e:
            print(f"Failed with {enc}: {e}")
else:
    print("Staff.csv not found")
