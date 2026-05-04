import base64
import io
import re
import os
from PIL import Image

source_file = r'c:\Users\63039\Videos\workstation\Workstation\ro_workstation\src\assets\beti copy.svg'
target_file = r'c:\Users\63039\Videos\workstation\Workstation\ro_workstation\src\assets\beti.svg'

with open(source_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Extract the base64 image data
pattern = r'data:image/png;base64,([A-Za-z0-9+/=]+)'
matches = re.findall(pattern, content)

if matches:
    # Use the first match as the master image
    img_data = base64.b64decode(matches[0])
    img = Image.open(io.BytesIO(img_data))
    
    # Resize for optimization (keeping aspect ratio)
    # 200x200 is usually enough for a header logo
    img.thumbnail((200, 200), Image.Resampling.LANCZOS)
    
    # Save with high compression
    buffer = io.BytesIO()
    img.save(buffer, format="PNG", optimize=True)
    new_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    new_href = f"data:image/png;base64,{new_base64}"
    
    # Replace ALL occurrences of the old base64 strings with the new one
    # Note: re.sub with the pattern might be tricky if they are different, 
    # but the user said "don't edit", and usually these files have the same image twice.
    # We'll replace the full data URI.
    
    def replacement(match):
        return new_href
        
    final_content = re.sub(pattern, replacement, content)
    
    with open(target_file, 'w', encoding='utf-8') as f:
        f.write(final_content)
    
    print(f"Optimized SVG saved to {target_file}")
    print(f"New base64 size: {len(new_base64)} chars")
else:
    print("No PNG data found in source SVG.")
