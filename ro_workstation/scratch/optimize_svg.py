import base64
import re
import io
from PIL import Image

def optimize_svg_raster_dedup(file_path, output_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find first base64 image
    pattern = r'data:image/png;base64,([A-Za-z0-9+/=]+)'
    matches = re.findall(pattern, content)
    
    if not matches:
        print("No base64 images found.")
        return

    # Optimize the image
    img_data = base64.b64decode(matches[0])
    img = Image.open(io.BytesIO(img_data))
    
    target_size = (256, 256)
    img.thumbnail(target_size, Image.Resampling.LANCZOS)
    
    buffer = io.BytesIO()
    img.save(buffer, format="PNG", optimize=True)
    new_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    # Create a clean version with <defs> for the image
    # We replace the first <image ... /> with a defined one and others with <use>
    # Actually, simpler: just put the image data in a variable and replace in template.
    
    # Let's just do a string replacement that works for this specific SVG structure
    # The SVG has two <image ...> tags.
    
    img_href = f'data:image/png;base64,{new_base64}'
    
    # Replace all matches with the same optimized data
    optimized_content = re.sub(pattern, img_href, content)
    
    # Further dedup: 
    # 1. Add <image id="beti_img" ... /> to <defs>
    # 2. Replace <image ... /> with <use xlink:href="#beti_img" />
    
    # This might be tricky with regex, let's see.
    # The image tags look like: <image x="0" y="0" width="413" xlink:href="..." />
    
    img_def = f'<image id="beti_img" x="0" y="0" width="413" xlink:href="{img_href}"/>'
    
    # Insert into <defs>
    if '<defs>' in optimized_content:
        optimized_content = optimized_content.replace('<defs>', f'<defs>{img_def}')
    
    # Replace image tags with <use>
    optimized_content = re.sub(r'<image[^>]+xlink:href="[^"]+"[^>]*/>', '<use xlink:href="#beti_img"/>', optimized_content)
    # Restore the one in defs (it was replaced too)
    optimized_content = optimized_content.replace('<use xlink:href="#beti_img"/>', img_def, 1)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(optimized_content)
    
    print(f"Deduplicated SVG written to {output_path}")

if __name__ == "__main__":
    optimize_svg_raster_dedup(
        r'c:\Users\63039\Videos\workstation\Workstation\ro_workstation\src\assets\beti.svg',
        r'c:\Users\63039\Videos\workstation\Workstation\ro_workstation\src\assets\beti_optimized.svg'
    )
