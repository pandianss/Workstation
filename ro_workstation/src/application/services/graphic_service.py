from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os
from pathlib import Path
from src.core.paths import project_path

class GraphicService:
    """Service to generate social media recognition posters (1080x1920)."""
    
    def __init__(self):
        self.width = 1080
        self.height = 1920
        self.fonts_dir = project_path("data", "fonts")
        self.assets_dir = project_path("src", "assets")
        
    def generate_milestone_poster(self, achievement: dict) -> bytes:
        """Creates a professional IOB-branded celebratory poster (1080x1920)."""
        # 1. Background (IOB Royal Blue Gradient)
        img = Image.new('RGB', (self.width, self.height), color='#0a1e45')
        draw = ImageDraw.Draw(img, 'RGBA')
        
        # Professional deep blue gradient
        for i in range(self.height):
            r = int(10 + (i / self.height) * 10)
            g = int(30 + (i / self.height) * 20)
            b = int(69 + (i / self.height) * 50)
            draw.line([(0, i), (self.width, i)], fill=(r, g, b))

        # 2. Institutional Branding
        self._draw_glow(img, (540, 960), 800, (212, 175, 55, 10)) # Subtle central glow

        # 3. Load Fonts
        font_huge = self._get_font("NotoSans-Bold.ttf", 130)
        font_large = self._get_font("NotoSans-Bold.ttf", 100)
        font_regular = self._get_font("NotoSans-Regular.ttf", 60)
        font_small = self._get_font("NotoSans-Bold.ttf", 65) # Highlighted Region
        font_label = self._get_font("NotoSans-Regular.ttf", 45)

        # 4. Celebration Mood (Favicon Rain with varying blur)
        try:
            favicon_path = os.path.join(self.assets_dir, "favicon.png")
            if os.path.exists(favicon_path):
                fav = Image.open(favicon_path).convert("RGBA")
                self._draw_favicon_rain(img, fav)
        except: pass

        # 5. Official Branding Header
        try:
            logo_path = os.path.join(self.assets_dir, "2026logo_min.png")
            if os.path.exists(logo_path):
                logo = Image.open(logo_path).convert("RGBA")
                logo_h = 140
                logo_w = int(logo.width * (logo_h / logo.height))
                logo = logo.resize((logo_w, logo_h), Image.Resampling.LANCZOS)
                img.paste(logo, (self.width//2 - logo_w//2, 120), logo)
        except: pass

        # Highlighted Region Name (Larger as requested)
        header_y = 320
        draw.text((self.width//2, header_y), "DINDIGUL REGION", fill="#d4af37", font=font_small, anchor="mm")
        
        # 6. Content Section
        draw.text((self.width//2, 600), "CONGRATULATIONS!", fill="#FFFFFF", font=font_large, anchor="mm")
        
        # Branch Name (Wrapped)
        branch_name = achievement.get("branch_name", "Unknown Branch").upper()
        import textwrap
        wrapped = textwrap.wrap(branch_name, width=15)
        
        curr_y = 850
        for line in wrapped:
            # Drop shadow for readability against confetti
            draw.text((self.width//2 + 5, curr_y + 5), line, fill=(0,0,0,200), font=font_huge, anchor="mm")
            draw.text((self.width//2, curr_y), line, fill="#FFFFFF", font=font_huge, anchor="mm")
            curr_y += 150

        # 7. Milestone Badge
        milestone = achievement.get("milestone", "50Cr+")
        param = achievement.get("parameter", "Business")
        
        badge_y = 1300
        badge_w, badge_h = 650, 240
        badge_box = [self.width//2 - badge_w//2, badge_y, self.width//2 + badge_w//2, badge_y + badge_h]
        
        draw.rounded_rectangle(badge_box, radius=30, fill="#d4af37")
        draw.text((self.width//2, badge_y + 90), milestone, fill="#0a1e45", font=font_huge, anchor="mm")
        draw.text((self.width//2, badge_y + 175), param.upper(), fill="#0a1e45", font=font_label, anchor="mm")

        # 8. Exact Breakthrough Date
        achievement_date = achievement.get("date")
        date_str = achievement_date.strftime("%d %B %Y").upper() if hasattr(achievement_date, "strftime") else str(achievement_date)

        footer_y = 1700
        draw.text((self.width//2, footer_y), "THRESHOLD CROSSED ON", fill="#cbd5e1", font=font_label, anchor="mm")
        draw.text((self.width//2, footer_y + 80), date_str, fill="#FFFFFF", font=font_regular, anchor="mm")

        # 9. Institutional Footer
        draw.line([(250, 1820), (830, 1820)], fill="#d4af37", width=3)
        draw.text((self.width//2, 1880), "INDIAN OVERSEAS BANK", fill="#d4af37", font=font_label, anchor="mm")

        # 10. Export
        from io import BytesIO
        buf = BytesIO()
        img.save(buf, format='PNG', optimize=True)
        return buf.getvalue()

    def _draw_favicon_rain(self, img, fav_img):
        """Draws a rain of favicons with varying scales and blurs."""
        import random
        for _ in range(80):
            # Random scale
            scale = random.uniform(0.3, 1.2)
            size = int(64 * scale)
            f = fav_img.resize((size, size), Image.Resampling.LANCZOS)
            
            # Random blur (Depth of Field effect)
            blur_radius = random.uniform(0, 4)
            if blur_radius > 0.5:
                f = f.filter(ImageFilter.GaussianBlur(blur_radius))
            
            # Random position and rotation
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            angle = random.randint(0, 360)
            f = f.rotate(angle, expand=True)
            
            # Paste with varying transparency
            alpha = int(random.uniform(50, 150))
            f_mask = f.split()[3].point(lambda p: p * (alpha / 255.0))
            img.paste(f, (x, y), f_mask)

    def _get_font(self, name, size):
        font_path = os.path.join(self.fonts_dir, name)
        try:
            if os.path.exists(font_path):
                return ImageFont.truetype(font_path, size)
        except: pass
        return ImageFont.load_default()

    def _draw_glow(self, img, pos, radius, color):
        """Draws a soft institutional radial glow."""
        glow = Image.new('RGBA', (radius*2, radius*2), (0,0,0,0))
        d = ImageDraw.Draw(glow)
        for i in range(radius):
            alpha = int(color[3] * (1 - i/radius))
            d.ellipse([radius-i, radius-i, radius+i, radius+i], outline=(color[0], color[1], color[2], alpha))
        img.paste(glow, (pos[0]-radius, pos[1]-radius), glow)



