from __future__ import annotations
from typing import Dict, List, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from src.infrastructure.persistence.sqlite_models import MISRecordModel, MasterRecordModel

class MilestoneService:
    """Service to calculate business milestones across branches."""
    
    PARAMETERS = [
        "SB", "CD", "CASA", "TD", "Business", 
        "Jewel", "Housing", "Vehicle", "Core Agri", 
        "MSME", "Core Retail"
    ]

    def __init__(self, session: Session):
        self.session = session

    def get_milestone_achievements(self) -> List[Dict[str, Any]]:
        """Identifies branches that crossed a NEW milestone during the month."""
        latest_date = self.session.query(func.max(MISRecordModel.date)).scalar()
        if not latest_date:
            return []
            
        import datetime
        # Previous month end to establish baseline
        prev_month_end = latest_date.replace(day=1) - datetime.timedelta(days=1)
        prev_date = self.session.query(func.max(MISRecordModel.date)).filter(MISRecordModel.date <= prev_month_end).scalar()
        
        # Load baseline levels
        branches = self.session.query(MasterRecordModel).filter(MasterRecordModel.category == 'BRANCH').all()
        branch_map = {b.code: b.name_en for b in branches}
        
        baseline_levels = {}
        if prev_date:
            prev_recs = self.session.query(MISRecordModel).filter(MISRecordModel.date == prev_date).all()
            for r in prev_recs:
                vals = self._calculate_parameters(r)
                baseline_levels[r.sol] = {p: self._get_milestone_level(vals.get(p, 0.0)) for p in self.PARAMETERS}

        # Find all reporting dates in the current month, sorted ascending
        curr_month_dates = self.session.query(MISRecordModel.date)\
            .filter(MISRecordModel.date > prev_month_end)\
            .filter(MISRecordModel.date <= latest_date)\
            .distinct().order_by(MISRecordModel.date.asc()).all()
        
        achievements = []
        # Track already recognized breakthroughs to find the FIRST occurrence
        recognized = set() # (sol, parameter, milestone)

        for (d_date,) in curr_month_dates:
            recs = self.session.query(MISRecordModel).filter(MISRecordModel.date == d_date).all()
            for r in recs:
                if r.sol == 3933: continue
                curr_vals = self._calculate_parameters(r)
                
                for param in self.PARAMETERS:
                    curr_val = curr_vals.get(param, 0.0)
                    curr_level = self._get_milestone_level(curr_val)
                    
                    prev_level = baseline_levels.get(r.sol, {}).get(param, 0)
                    
                    if curr_level > prev_level and curr_level >= 50:
                        key = (r.sol, param, curr_level)
                        if key not in recognized:
                            achievements.append({
                                "sol": r.sol,
                                "branch_name": branch_map.get(str(r.sol), f"SOL {r.sol}"),
                                "parameter": param,
                                "value": curr_val,
                                "previous_value": 0.0, # Not strictly needed for poster
                                "milestone": f"{curr_level}Cr+",
                                "date": d_date
                            })
                            recognized.add(key)
        return achievements

    def get_all_at_milestones(self) -> List[Dict[str, Any]]:
        """Returns all branches currently at any milestone level for all parameters."""
        latest_date = self.session.query(func.max(MISRecordModel.date)).scalar()
        if not latest_date:
            return []
            
        recs = self.session.query(MISRecordModel).filter(MISRecordModel.date == latest_date).all()
        branches = self.session.query(MasterRecordModel).filter(MasterRecordModel.category == 'BRANCH').all()
        branch_map = {b.code: b.name_en for b in branches}
        
        results = []
        for r in recs:
            if r.sol == 3933: continue
            vals = self._calculate_parameters(r)
            for param, val in vals.items():
                level = self._get_milestone_level(val)
                if level >= 50:
                    results.append({
                        "sol": r.sol,
                        "branch_name": branch_map.get(str(r.sol), f"SOL {r.sol}"),
                        "parameter": param,
                        "value": val,
                        "milestone": f"{level}Cr+"
                    })
        return results

    def _get_milestone_level(self, val: float) -> int:
        """Returns the highest milestone level reached (multiple of 50)."""
        if val < 50:
            return 0
        return int(val // 50) * 50

    def _calculate_parameters(self, r: MISRecordModel) -> Dict[str, float]:
        """Maps DB fields to business parameters in Crores."""
        sb = r.sb / 100
        cd = r.cd / 100
        td = r.td / 100
        agri = r.core_agri / 100
        msme = r.msme / 100
        jewel = r.gold / 100
        housing = r.housing / 100
        vehicle = r.vehicle / 100
        
        core_retail = (
            r.housing + r.vehicle + r.personal + 
            r.education + r.mortgage + r.liquirent + r.other_retail
        ) / 100
        
        total_dep = sb + cd + td
        total_adv = agri + msme + jewel + core_retail
        
        return {
            "SB": sb,
            "CD": cd,
            "CASA": sb + cd,
            "TD": td,
            "Business": total_dep + total_adv,
            "Jewel": jewel,
            "Housing": housing,
            "Vehicle": vehicle,
            "Core Agri": agri,
            "MSME": msme,
            "Core Retail": core_retail
        }
    def save_achievements(self, achievements: List[Dict[str, Any]]) -> int:
        """Persists breakthroughs to the database, avoiding duplicates."""
        from src.infrastructure.persistence.sqlite_models import MilestoneAchievementModel
        count = 0
        for a in achievements:
            # Check if already exists
            exists = self.session.query(MilestoneAchievementModel).filter(
                MilestoneAchievementModel.sol == a["sol"],
                MilestoneAchievementModel.parameter == a["parameter"],
                MilestoneAchievementModel.milestone == a["milestone"],
                MilestoneAchievementModel.date == a["date"]
            ).first()
            
            if not exists:
                new_ach = MilestoneAchievementModel(
                    sol=a["sol"],
                    branch_name=a["branch_name"],
                    parameter=a["parameter"],
                    milestone=a["milestone"],
                    value=a["value"],
                    previous_value=a["previous_value"],
                    date=a["date"]
                )
                self.session.add(new_ach)
                count += 1
        
        if count > 0:
            self.session.commit()
        return count
