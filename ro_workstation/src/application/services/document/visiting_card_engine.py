import os
import base64
from typing import Dict, Any
from jinja2 import Environment, FileSystemLoader
from src.core.paths import project_path
from playwright.sync_api import sync_playwright

class VisitingCardEngine:
    """
    High-Resolution Trilingual Visiting Card Generation Engine.
    Uses Playwright (Headless Browser) for perfect trilingual typography.
    """
    
    def __init__(self):
        self.templates_path = project_path("src", "infrastructure", "templates")
        self.assets_path = project_path("src", "assets")
        self.env = Environment(loader=FileSystemLoader(str(self.templates_path)))

    def _get_base64_data(self, path: os.PathLike, mime: str = "image/png") -> str:
        if not os.path.exists(path):
            return ""
        with open(path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()
            return f"data:{mime};base64,{encoded}"

    def render_card(self, data: Dict[str, Any]) -> list[bytes]:
        """Renders high-resolution front and back visiting card PNGs."""
        
        # Prepare Template Data
        template = self.env.get_template("visiting_card.html")
        
        assets = {
            "logo_url": self._get_base64_data(self.assets_path / "2026logo_min.png"),
            "phone_icon": self._get_base64_data(self.assets_path / "themes/executive/vc_phone.png"),
            "mobile_icon": self._get_base64_data(self.assets_path / "themes/executive/vc_mobile.png"),
            "email_icon": self._get_base64_data(self.assets_path / "themes/executive/vc_email.png"),
            "web_icon": self._get_base64_data(self.assets_path / "themes/executive/vc_web.png"),
            "font_en": base64.b64encode(open(project_path("data", "fonts", "SegoeUI-Regular.ttf"), "rb").read()).decode(),
            "font_hi": base64.b64encode(open(project_path("data", "fonts", "NotoSansDevanagari-Regular.ttf"), "rb").read()).decode(),
            "font_ta": base64.b64encode(open(project_path("data", "fonts", "NotoSansTamil-Regular.ttf"), "rb").read()).decode(),
        }
        
        html_content = template.render(**data, **assets)
        
        # Windows ProactorEventLoop fix for Playwright subprocess
        import asyncio
        import sys
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

        pages_bytes = []
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1050, "height": 630}, device_scale_factor=2)
            page.set_content(html_content)
            page.wait_for_timeout(200) # Slightly more for Tamil font
            
            # Capture Front
            pages_bytes.append(page.locator("#front").screenshot(type="png"))
            # Capture Back
            pages_bytes.append(page.locator("#back").screenshot(type="png"))
            
            browser.close()
            
        return pages_bytes
