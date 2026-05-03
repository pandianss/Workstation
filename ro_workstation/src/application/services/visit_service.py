from __future__ import annotations
from typing import List, Dict, Any
import datetime
from sqlalchemy.orm import Session
from sqlalchemy import extract, and_
from src.infrastructure.persistence.database import engine
from src.infrastructure.persistence.sqlite_models import Base, BranchVisitModel, MasterRecordModel

# Ensure tables are created
Base.metadata.create_all(engine)

class VisitService:
    def __init__(self, session: Session):
        self.session = session

    def add_visit(self, sol: int, visit_date: datetime.date, visitor_name: str, 
                  observations: str, advice: str) -> BranchVisitModel:
        # Get branch name from masters
        branch = self.session.query(MasterRecordModel).filter(
            and_(MasterRecordModel.category == "UNIT", MasterRecordModel.code == str(sol))
        ).first()
        branch_name = branch.name_en if branch else f"SOL {sol}"

        new_visit = BranchVisitModel(
            sol=sol,
            branch_name=branch_name,
            visit_date=visit_date,
            visitor_name=visitor_name,
            observations=observations,
            advice_to_branch=advice
        )
        self.session.add(new_visit)
        self.session.commit()
        return new_visit

    def get_monthly_visits(self, year: int, month: int) -> List[BranchVisitModel]:
        return self.session.query(BranchVisitModel).filter(
            and_(
                extract('year', BranchVisitModel.visit_date) == year,
                extract('month', BranchVisitModel.visit_date) == month
            )
        ).order_by(BranchVisitModel.visit_date.asc()).all()

    def delete_visit(self, visit_id: int):
        visit = self.session.query(BranchVisitModel).filter(BranchVisitModel.id == visit_id).first()
        if visit:
            self.session.delete(visit)
            self.session.commit()

    def update_reply_status(self, visit_id: int, status: bool):
        visit = self.session.query(BranchVisitModel).filter(BranchVisitModel.id == visit_id).first()
        if visit:
            visit.reply_received = status
            self.session.commit()
