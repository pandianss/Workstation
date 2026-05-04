import base64
import io
from PIL import Image

source_img = r'C:\Users\63039\.gemini\antigravity\brain\e7db57be-55c1-4bce-b0b3-19e00b351d29\beti_bachao_logo_clean_1777716121707.png'
target_svg = r'c:\Users\63039\Videos\workstation\Workstation\ro_workstation\src\assets\beti.svg'

img = Image.open(source_img)
# Resize to 256x256 for a good balance of quality and size
img.thumbnail((256, 256), Image.Resampling.LANCZOS)

# Save with optimization
buffer = io.BytesIO()
img.save(buffer, format="PNG", optimize=True)
img_data = buffer.getvalue()
img_base64 = base64.b64encode(img_data).decode('utf-8')

img_href = f"data:image/png;base64,{img_base64}"

svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="121" height="121" viewBox="0 0 256 256" version="1.1">
  <image x="0" y="0" width="256" height="256" xlink:href="{img_href}" preserveAspectRatio="xMidYMid meet"/>
</svg>'''

with open(target_svg, 'w', encoding='utf-8') as f:
    f.write(svg_content)

print(f"Updated {target_svg} with {len(img_base64)} bytes of base64 data (Resized to 256x256).")
