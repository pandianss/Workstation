import base64
import io
from PIL import Image

source_img = r'C:\Users\63039\.gemini\antigravity\brain\e7db57be-55c1-4bce-b0b3-19e00b351d29\media__1777716299069.png'
target_svg = r'c:\Users\63039\Videos\workstation\Workstation\ro_workstation\src\assets\beti.svg'

img = Image.open(source_img).convert("RGBA")

# Make white (or near-white) transparent
datas = img.getdata()
newData = []
for item in datas:
    # The logo has a white outer box and inner background.
    # We want to make the background transparent.
    # If the pixel is very light (white-ish), make it transparent
    if item[0] > 240 and item[1] > 240 and item[2] > 240:
        newData.append((255, 255, 255, 0))
    else:
        newData.append(item)
img.putdata(newData)

# Crop the image to its bounding box of non-transparent pixels
bbox = img.getbbox()
if bbox:
    img = img.crop(bbox)

# Resize to 256x256 for a good balance of quality and size
img.thumbnail((256, 256), Image.Resampling.LANCZOS)

buffer = io.BytesIO()
img.save(buffer, format="PNG", optimize=True)
img_data = buffer.getvalue()
img_base64 = base64.b64encode(img_data).decode('utf-8')

img_href = f"data:image/png;base64,{img_base64}"

# Adjust viewBox based on the cropped aspect ratio if needed, but 256x256 is fine if we use preserveAspectRatio
svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="121" height="121" viewBox="0 0 256 256" version="1.1">
  <image x="0" y="0" width="256" height="256" xlink:href="{img_href}" preserveAspectRatio="xMidYMid meet"/>
</svg>'''

with open(target_svg, 'w', encoding='utf-8') as f:
    f.write(svg_content)

print(f"Updated {target_svg} with the correct Beti logo (Size: {len(img_base64)} bytes, Alpha enabled).")
