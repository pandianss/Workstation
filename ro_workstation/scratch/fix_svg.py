import base64
import re
import io
from PIL import Image

def optimize_svg_no_dedup_fixed(file_path, output_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    pattern = r'data:image/png;base64,([A-Za-z0-9+/=]+)'
    matches = re.findall(pattern, content)
    
    if not matches:
        print("No base64 images found.")
        return

    # Use the image data
    img_data = base64.b64decode(matches[0])
    
    # Re-optimize but DON'T resize this time to be 100% safe
    img = Image.open(io.BytesIO(img_data))
    buffer = io.BytesIO()
    img.save(buffer, format="PNG", optimize=True)
    new_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    img_href = f'data:image/png;base64,{new_base64}'

    # EXACT original structure
    original_template = """<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="121" zoomAndPan="magnify" viewBox="0 0 90.75 90.749999" height="121" preserveAspectRatio="xMidYMid meet" version="1.0"><defs><filter x="0%" y="0%" width="100%" height="100%" id="dfb1e59761"><feColorMatrix values="0 0 0 0 1 0 0 0 0 1 0 0 0 0 1 0 0 0 1 0" color-interpolation-filters="sRGB"/></filter><filter x="0%" y="0%" width="100%" height="100%" id="2084c85075"><feColorMatrix values="0 0 0 0 1 0 0 0 0 1 0 0 0 0 1 0.2126 0.7152 0.0722 0 0" color-interpolation-filters="sRGB"/></filter><clipPath id="c7fd652aa7"><path d="M 0 0 L 90.5 0 L 90.5 90.5 L 0 90.5 Z M 0 0 " clip-rule="nonzero"/></clipPath><clipPath id="19a7d266a0"><path d="M 0 0 L 90.5 0 L 90.5 90.5 L 0 90.5 Z M 0 0 " clip-rule="nonzero"/></clipPath><mask id="dc77a20c28"><g filter="url(#dfb1e59761)"><g filter="url(#2084c85075)" transform="matrix(0.238373, 0, 0, 0.238373, -3.977453, -3.977452)"><image x="0" y="0" width="413" xlink:href="REPLACE_ME" height="413" preserveAspectRatio="xMidYMid meet"/></g></g></mask><clipPath id="cdadb14f1b"><rect x="0" width="91" y="0" height="91"/></clipPath></defs><g clip-path="url(#c7fd652aa7)"><g transform="matrix(1, 0, 0, 1, 0, -0.000000000000001434)"><g clip-path="url(#cdadb14f1b)"><g clip-path="url(#19a7d266a0)"><g mask="url(#dc77a20c28)"><g transform="matrix(0.238373, 0, 0, 0.238373, -3.977453, -3.977452)"><image x="0" y="0" width="413" xlink:href="REPLACE_ME" height="413" preserveAspectRatio="xMidYMid meet"/></g></g></g></g></g></g></svg>"""
    
    final_content = original_template.replace("REPLACE_ME", img_href)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(final_content)
    
    print(f"Restored structure (with height and AR) SVG written to {output_path}")

if __name__ == "__main__":
    optimize_svg_no_dedup_fixed(
        r'c:\Users\63039\Videos\workstation\Workstation\ro_workstation\src\assets\beti.svg',
        r'c:\Users\63039\Videos\workstation\Workstation\ro_workstation\src\assets\beti.svg'
    )
