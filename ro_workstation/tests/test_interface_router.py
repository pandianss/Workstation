import unittest

from src.interface.streamlit.router import PAGE_REGISTRY


class RouterTests(unittest.TestCase):
    def test_required_pages_are_registered(self):
        for page in ["Dashboard", "Operations", "MIS", "Policy & Product Archive", "Field Guardian", "Admin"]:
            self.assertIn(page, PAGE_REGISTRY)
