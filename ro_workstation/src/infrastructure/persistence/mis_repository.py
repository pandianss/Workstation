from __future__ import annotations

from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.core.paths import project_path
from src.infrastructure.persistence.sqlite_models import Base, IngestedFileModel, MISRecordModel


class MISRepository:
    def __init__(self, db_path: Path | None = None) -> None:
        self.db_path = db_path or project_path("data", "mis_store.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.engine = create_engine(f"sqlite:///{self.db_path.as_posix()}")
        Base.metadata.create_all(self.engine)
        self.session_factory = sessionmaker(bind=self.engine)

    def is_file_ingested(self, filename: str) -> bool:
        session = self.session_factory()
        exists = session.query(IngestedFileModel).filter(IngestedFileModel.filename == filename).first() is not None
        session.close()
        return exists

    def mark_file_ingested(self, filename: str) -> None:
        session = self.session_factory()
        session.add(IngestedFileModel(filename=filename))
        session.commit()
        session.close()

    def save_records(self, records: list[dict]) -> None:
        session = self.session_factory()
        try:
            objects = []
            valid_keys = set(MISRecordModel.__table__.columns.keys())
            for record in records:
                normalized = {key.lower().replace(" ", "_"): value for key, value in record.items()}
                filtered = {key: value for key, value in normalized.items() if key in valid_keys}
                if "date" in filtered and hasattr(filtered["date"], "date"):
                    filtered["date"] = filtered["date"].date()
                objects.append(MISRecordModel(**filtered))
            session.bulk_save_objects(objects)
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def load_frame(self) -> pd.DataFrame:
        session = self.session_factory()
        query = session.query(MISRecordModel)
        frame = pd.read_sql(query.statement, self.engine)
        session.close()
        return frame
