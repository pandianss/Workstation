from PIL import Image
import os
import numpy as np

def crop_image(input_path, output_path):
    img = Image.open(input_path).convert("RGBA")
    
    # Try transparency first
    bbox = img.getbbox()
    
    # Check if it's mostly white and opaque
    alpha = img.getchannel('A')
    if alpha.getextrema()[0] == 255:
        data = np.array(img.convert("RGB"))
        non_white = (data < [245, 245, 245]).any(axis=2)
        coords = np.argwhere(non_white)
        if coords.size > 0:
            y_min, x_min = coords.min(axis=0)
            y_max, x_max = coords.max(axis=0)
            bbox = (int(x_min), int(y_min), int(x_max + 1), int(y_max + 1))
    
    if bbox:
        cropped = img.crop(bbox)
        # Add a tiny margin
        margin = 5
        final_bbox = (max(0, bbox[0]-margin), max(0, bbox[1]-margin), 
                      min(img.width, bbox[2]+margin), min(img.height, bbox[3]+margin))
        cropped = img.crop(final_bbox)
        cropped.save(output_path)
        print(f"Cropped {input_path} to {output_path}. BBox: {final_bbox}")
        return final_bbox
    return None

base_path = r"c:\Users\63039\Videos\workstation\Workstation\ro_workstation"
png_path = os.path.join(base_path, "src", "assets", "iob_logo_premium.png")
crop_image(png_path, png_path)
