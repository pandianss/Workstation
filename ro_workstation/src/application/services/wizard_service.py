from __future__ import annotations
import json
import datetime
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from src.infrastructure.persistence.sqlite_models import WizardSubmissionModel

class WizardService:
    def __init__(self, session: Session):
        self.session = session

    def save_submission(self, wizard_type: str, submitted_by: str, content: Dict[str, Any], subject: str = None, ref: str = None) -> WizardSubmissionModel:
        # Prevent double-submit by checking if identical content was just added
        last_sub = self.session.query(WizardSubmissionModel).filter(
            WizardSubmissionModel.wizard_type == wizard_type,
            WizardSubmissionModel.submitted_by == submitted_by,
            WizardSubmissionModel.subject == subject
        ).order_by(WizardSubmissionModel.created_at.desc()).first()
        
        if last_sub:
            # If created within last 60 seconds and content matches, skip
            now = datetime.datetime.now()
            if (now - last_sub.created_at).total_seconds() < 60:
                if last_sub.content_json == json.dumps(content, default=str):
                    return last_sub

        new_submission = WizardSubmissionModel(
            wizard_type=wizard_type,
            submitted_by=submitted_by,
            subject=subject,
            reference_no=ref,
            content_json=json.dumps(content, default=str)
        )
        self.session.add(new_submission)
        self.session.commit()
        return new_submission

    def get_submissions(self, wizard_type: str | None = None) -> List[WizardSubmissionModel]:
        query = self.session.query(WizardSubmissionModel)
        if wizard_type:
            query = query.filter(WizardSubmissionModel.wizard_type == wizard_type)
        return query.order_by(WizardSubmissionModel.created_at.desc()).all()

    def delete_submission(self, sub_id: str) -> bool:
        sub = self.session.query(WizardSubmissionModel).filter(WizardSubmissionModel.id == sub_id).first()
        if sub:
            self.session.delete(sub)
            self.session.commit()
            return True
        return False

    def update_submission(self, sub_id: str, content: Dict[str, Any], subject: str = None) -> bool:
        sub = self.session.query(WizardSubmissionModel).filter(WizardSubmissionModel.id == sub_id).first()
        if sub:
            sub.content_json = json.dumps(content, default=str)
            if subject: sub.subject = subject
            self.session.commit()
            return True
        return False

    @staticmethod
    def calculate_broken_period_interest(
        principal: float, 
        rate: float, 
        days: int, 
        frequency: str = "SIMPLE"
    ) -> float:
        """
        Logic from BrokenPeriodInterestForm.tsx
        """
        if days <= 0 or rate <= 0 or principal <= 0:
            return 0.0
            
        if frequency == "SIMPLE":
            # P * R * D / 365
            return round((principal * (rate / 100) * days) / 365, 2)
        
        # Compound logic: Maturity Value = P * (1 + r/n)^(n*t)
        # Interest = Maturity Value - Principal
        t = days / 365
        n_map = {"QUARTERLY": 4, "MONTHLY": 12, "HALFYEARLY": 2, "ANNUALLY": 1}
        n = n_map.get(frequency, 1)
        
        maturity_value = principal * ((1 + (rate / (100 * n))) ** (n * t))
        return round(maturity_value - principal, 2)
