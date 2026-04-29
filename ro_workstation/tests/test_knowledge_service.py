import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.services import knowledge_service


class KnowledgeServiceTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        temp_path = Path(self.temp_dir.name)
        knowledge_service.DATA_DIR = temp_path
        knowledge_service.KNOWLEDGE_DIR = temp_path / "knowledge_docs"
        knowledge_service.REGISTRY_FILE = temp_path / "knowledge_index.json"

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_index_saved_document_registers_chunks(self):
        source = knowledge_service.KNOWLEDGE_DIR / "policy.txt"
        knowledge_service.KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)
        source.write_text("Policy text " * 300, encoding="utf-8")

        with patch("app.services.knowledge_service.index_document") as mock_index:
            record = knowledge_service.index_saved_document(source, "CRMD", "tester")

        self.assertEqual(record["department"], "CRMD")
        self.assertGreater(record["chunks"], 1)
        mock_index.assert_called_once()

    def test_list_indexed_documents_returns_empty_dataframe_when_uninitialized(self):
        df = knowledge_service.list_indexed_documents()
        self.assertTrue(df.empty)
