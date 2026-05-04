import base64
import io
from PIL import Image, ImageDraw

# Create a 256x256 colorful placeholder image
img = Image.new('RGBA', (256, 256), color=(255, 255, 255, 0))
draw = ImageDraw.Draw(img)
draw.ellipse([10, 10, 246, 246], fill=(255, 100, 100, 255), outline=(200, 0, 0, 255), width=5)
draw.text((60, 110), "BETI LOGO", fill=(255, 255, 255, 255))

buffer = io.BytesIO()
img.save(buffer, format="PNG")
img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
img_href = f"data:image/png;base64,{img_base64}"

svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="121" height="121" viewBox="0 0 413 413" version="1.1">
  <image x="0" y="0" width="413" height="413" xlink:href="{img_href}" preserveAspectRatio="xMidYMid meet"/>
</svg>'''

with open(r'c:\Users\63039\Videos\workstation\Workstation\ro_workstation\src\assets\beti.svg', 'w', encoding='utf-8') as f:
    f.write(svg_content)
