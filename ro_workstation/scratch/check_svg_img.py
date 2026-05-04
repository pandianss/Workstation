import base64
import io
from PIL import Image
import re

with open(r'c:\Users\63039\Videos\workstation\Workstation\ro_workstation\src\assets\beti.svg', 'r', encoding='utf-8') as f:
    content = f.read()

pattern = r'data:image/png;base64,([A-Za-z0-9+/=]+)'
matches = re.findall(pattern, content)

for i, m in enumerate(matches):
    try:
        data = base64.b64decode(m)
        img = Image.open(io.BytesIO(data))
        print(f"Image {i} size: {img.size}, format: {img.format}, mode: {img.mode}")
    except Exception as e:
        print(f"Image {i} failed: {e}")
