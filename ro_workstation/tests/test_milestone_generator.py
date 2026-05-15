import unittest
from unittest.mock import MagicMock

from src.application.services.document.milestones import MilestoneGenerator


class MilestoneGeneratorTests(unittest.TestCase):
    def test_legacy_staff_milestone_method_returns_pdf_bytes(self):
        engine = MagicMock()
        engine.render_doc.return_value = "<html>poster</html>"
        engine.to_pdf.return_value = b"%PDF"
        generator = MilestoneGenerator(engine)

        result = generator.generate_staff_milestone(
            {"roll": "123", "name": "Staff Member", "desig_en": "Manager"},
            "BIRTHDAY",
            "Regional Office",
        )

        self.assertEqual(result, b"%PDF")
        engine.render_doc.assert_called_once()
        engine.to_pdf.assert_called_once_with("<html>poster</html>")

    def test_legacy_anniversary_note_method_returns_pdf_bytes(self):
        engine = MagicMock()
        engine.render_doc.return_value = "<html>note</html>"
        engine.to_pdf.return_value = b"%PDF"
        generator = MilestoneGenerator(engine)

        result = generator.generate_anniversary_note({"branch_name": "Main"})

        self.assertEqual(result, b"%PDF")
        engine.to_pdf.assert_called_once_with("<html>note</html>")

    def test_staff_milestone_is_monogram_based_without_photo_fields(self):
        engine = MagicMock()
        engine.render_doc.return_value = "<html>poster</html>"
        generator = MilestoneGenerator(engine)

        generator.generate_staff_milestone_html(
            {"roll": "NO_PHOTO", "name": "Divya C B", "name_ta": "Divya C B", "desig_en": "Manager"},
            "BIRTHDAY",
            "Ayyakudi",
        )

        _, kwargs = engine.render_doc.call_args
        self.assertEqual(kwargs["staff_initials"], "DCB")
        self.assertEqual(kwargs["name_ta"], "")
        self.assertNotIn("has_photo", kwargs)
        self.assertNotIn("photo_url", kwargs)


if __name__ == "__main__":
    unittest.main()
