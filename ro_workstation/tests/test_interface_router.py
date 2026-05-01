import unittest

from interface.streamlit.router import PAGE_REGISTRY


class RouterTests(unittest.TestCase):
    def test_required_pages_are_registered(self):
        for page in ["Dashboard", "Operations", "MIS", "Intelligence", "Guardian", "Admin"]:
            self.assertIn(page, PAGE_REGISTRY)
