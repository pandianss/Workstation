import os
import pandas as pd
from typing import List
import datetime
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker

from src.core.paths import project_path
from src.infrastructure.persistence.json_repo import JsonRepository
from src.infrastructure.persistence.sqlite_models import Base, BudgetModel

class BudgetRepository:
    def __init__(self) -> None:
        self.excel_path = project_path().parent / "samples" / "budgets2.xlsx"
        self.db_path = project_path("data", "mis_store.db")
        
        # Mapping from MIS Enriched Names (Uppercase) to Excel Budget PARAMETER codes
        self.param_map = {
            "TOTAL ADVANCES": "Adv",
            "TOTAL DEPOSITS": "TD",
            "CASA": "CASA",
            "NPA": "NPA",
            "SB": "SB",
            "CD": "CD",
            "RET TD": "Ret_TD",
            "ADV": "Adv",
            "BUS": "Bus",
            "CORE AGRI": "Core_Agri",
            "AGRI JL": "Agri_JL",
            "GOLD": "Gold",
            "HOUSING": "HL",
            "VEHICLE": "VL",
            "PERSONAL": "PL",
            "MORTGAGE": "Mort",
            "EDUCATION": "EL",
            "LIQUIRENT": "Liq",
            "OTHER RETAIL": "OthRet",
            "MSME": "MSME",
            "SHG": "SHG",
            "KCC": "KCC",
            "MUDRA": "Mudra",
            "GOVT SPON": "Gov",
            "OTH SCHEMATIC": "OthSch",
            "CORE RETAIL": "Core Ret",
            "TOTAL RETAIL": "Ret"
        }

        self.engine = create_engine(f"sqlite:///{self.db_path.as_posix()}")
        Base.metadata.create_all(self.engine)
        self.session_factory = sessionmaker(bind=self.engine)
        
        self.json_repo = JsonRepository(
            project_path("data", "budgets.json"),
            {"defaults": {"Total Advances": 500000.0}}
        )
        
        # Automatically sync if file changed
        self.sync_if_needed()

    def sync_if_needed(self):
        """Checks if Excel was modified since last ingestion and re-syncs if needed."""
        if not self.excel_path.exists():
            return

        file_mtime = os.path.getmtime(self.excel_path)
        file_size = os.path.getsize(self.excel_path)
        
        # Store sync state in a tiny JSON sidecar or just check table count
        # For simplicity, we'll re-sync if the file is newer than the last recorded sync
        sync_meta_path = project_path("data", "budget_sync.json")
        last_sync = 0
        if os.path.exists(sync_meta_path):
            try:
                with open(sync_meta_path, 'r') as f:
                    import json
                    meta = json.load(f)
                    last_sync = meta.get("mtime", 0)
                    last_size = meta.get("size", 0)
                    if last_sync == file_mtime and last_size == file_size:
                        return # No changes
            except: pass

        self._ingest_excel()
        
        # Save sync state
        with open(sync_meta_path, 'w') as f:
            import json
            json.dump({"mtime": file_mtime, "size": file_size}, f)

    def _ingest_excel(self) -> None:
        """Reads Excel, melts it, and saves to SQLite."""
        try:
            df = pd.read_excel(self.excel_path)
            date_cols = [c for c in df.columns if isinstance(c, (datetime.date, datetime.datetime))]
            
            melted = df.melt(
                id_vars=["SOL", "PARAMETER"], 
                value_vars=date_cols,
                var_name="DATE",
                value_name="TARGET"
            )
            melted["DATE"] = pd.to_datetime(melted["DATE"])
            
            session = self.session_factory()
            try:
                # Clear existing budgets
                session.query(BudgetModel).delete()
                
                # Bulk insert new budgets
                objects = []
                for _, row in melted.iterrows():
                    objects.append(BudgetModel(
                        sol=int(row["SOL"]),
                        parameter=str(row["PARAMETER"]),
                        date=row["DATE"].date(),
                        target=float(row["TARGET"])
                    ))
                
                session.bulk_save_objects(objects)
                session.commit()
            except Exception:
                session.rollback()
                raise
            finally:
                session.close()
        except Exception as e:
            print(f"Sync error: {e}")

    def get_target(self, metric: str, year_month: str | None = None, sols: List[int] | None = None) -> float:
        """Retrieves aggregated budget target from SQLite."""
        excel_param = self.param_map.get(metric.upper(), self.param_map.get(metric, metric))
        
        session = self.session_factory()
        try:
            query = session.query(func.sum(BudgetModel.target)).filter(BudgetModel.parameter == excel_param)
            
            if sols:
                query = query.filter(BudgetModel.sol.isin(sols))
            
            if year_month:
                target_dt = pd.to_datetime(year_month).date()
                # Match year and month
                first_day = target_dt.replace(day=1)
                if target_dt.month == 12:
                    last_day = target_dt.replace(year=target_dt.year + 1, month=1, day=1)
                else:
                    last_day = target_dt.replace(month=target_dt.month + 1, day=1)
                
                query = query.filter(BudgetModel.date >= first_day, BudgetModel.date < last_day)
            
            result = query.scalar()
            if result is not None:
                return float(result)
        except Exception as e:
            print(f"Query error: {e}")
        finally:
            session.close()

        # Fallback to JSON defaults
        data = self.json_repo.read()
        return float(data.get("defaults", {}).get(metric, 0.0))

    def save_target(self, metric: str, value: float) -> None:
        data = self.json_repo.read()
        data["defaults"][metric] = value
        self.json_repo.write(data)
