import json
from datetime import datetime, UTC
from pathlib import Path

import pandas as pd
from docx import Document

from modules.knowledge.indexer import index_document
from modules.utils.paths import project_path

DATA_DIR = project_path("app", "data")
KNOWLEDGE_DIR = DATA_DIR / "knowledge_docs"
REGISTRY_FILE = DATA_DIR / "knowledge_index.json"

SUPPORTED_EXTENSIONS = {".txt", ".md", ".docx"}


def _ensure_storage():
    KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)
    if not REGISTRY_FILE.exists():
        REGISTRY_FILE.write_text("[]", encoding="utf-8")


def _load_registry():
    _ensure_storage()
    return json.loads(REGISTRY_FILE.read_text(encoding="utf-8"))


def _save_registry(records):
    REGISTRY_FILE.write_text(json.dumps(records, indent=2), encoding="utf-8")


def _chunk_text(text, chunk_size=1200):
    cleaned = " ".join(text.split())
    if not cleaned:
        return []
    return [cleaned[i:i + chunk_size] for i in range(0, len(cleaned), chunk_size)]


def _extract_text(path: Path):
    suffix = path.suffix.lower()
    if suffix in {".txt", ".md"}:
        return path.read_text(encoding="utf-8", errors="ignore")
    if suffix == ".docx":
        doc = Document(str(path))
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    raise ValueError(f"Unsupported file type: {suffix}. Supported types are {', '.join(sorted(SUPPORTED_EXTENSIONS))}.")


def store_uploaded_documents(uploaded_files):
    _ensure_storage()
    saved_paths = []
    for uploaded_file in uploaded_files:
        target = KNOWLEDGE_DIR / uploaded_file.name
        target.write_bytes(uploaded_file.getbuffer())
        saved_paths.append(target)
    return saved_paths


def index_saved_document(path: Path, department: str, uploaded_by: str):
    text = _extract_text(path)
    chunks = _chunk_text(text)
    if not chunks:
        raise ValueError("The uploaded document does not contain readable text.")

    metadata = {
        "title": path.stem,
        "department": department or "ALL",
        "uploaded_by": uploaded_by or "unknown",
    }
    index_document(str(path), chunks, metadata)

    records = _load_registry()
    record = {
        "file_name": path.name,
        "department": metadata["department"],
        "uploaded_by": metadata["uploaded_by"],
        "chunks": len(chunks),
        "indexed_at": datetime.now(UTC).isoformat(),
    }

    existing_index = next((idx for idx, item in enumerate(records) if item["file_name"] == path.name), None)
    if existing_index is None:
        records.append(record)
    else:
        records[existing_index] = record
    _save_registry(records)
    return record


def index_uploaded_documents(uploaded_files, department: str, uploaded_by: str):
    saved_paths = store_uploaded_documents(uploaded_files)
    return [index_saved_document(path, department, uploaded_by) for path in saved_paths]


def list_indexed_documents():
    records = _load_registry()
    if not records:
        return pd.DataFrame(columns=["file_name", "department", "uploaded_by", "chunks", "indexed_at"])
    return pd.DataFrame(records).sort_values("indexed_at", ascending=False)
