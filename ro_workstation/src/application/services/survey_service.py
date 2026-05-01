import json
import os
from datetime import datetime
from typing import List, Dict, Optional

class SurveyService:
    def __init__(self, data_path="data/surveys.json"):
        self.data_path = data_path
        self._ensure_data_file()

    def _ensure_data_file(self):
        if not os.path.exists(self.data_path):
            with open(self.data_path, 'w') as f:
                json.dump([], f)

    def _load_data(self) -> List[Dict]:
        with open(self.data_path, 'r') as f:
            data = json.load(f)
            if isinstance(data, dict) and "surveys" in data:
                return data["surveys"]
            return data if isinstance(data, list) else []

    def _save_data(self, surveys: List[Dict]):
        with open(self.data_path, 'w') as f:
            json.dump({"surveys": surveys}, f, indent=2)

    def calculate_viability(self, data: Dict) -> Dict:
        """
        Calculate financial viability based on BranchOpeningSurveyReport.jsx logic.
        All inputs are assumed to be in thousands (000s) as per sample.
        """
        def to_float(val):
            try:
                return float(str(val or 0).replace(',', '').replace('₹', '').strip())
            except:
                return 0.0

        manual_holidays = to_float(data.get('manualHolidays', 0))
        # 365 - 52 (Sundays) - 24 (2nd/4th Saturdays) - Holidays
        working_days = 365 - 52 - 24 - manual_holidays
        
        # Growth and Rates
        dep_growth = to_float(data.get('depositGrowth', 0))
        cost_of_dep = to_float(data.get('costOfDeposit', 0))
        adv_growth = to_float(data.get('advanceGrowth', 0))
        yield_on_adv = to_float(data.get('yieldOnAdvance', 0))
        monthly_rent = to_float(data.get('monthlyRent', 0))

        # Prospects (Growth * Working Days)
        prospects_dep = dep_growth * working_days
        prospects_adv = adv_growth * working_days

        # Interest Calculations (Growth * 182.5 * Rate / 100)
        # 182.5 is average days for interest calculation on growth? 
        # (Actually Growth * 365 / 2 = 182.5 * Growth)
        int_on_dep = dep_growth * 182.5 * (cost_of_dep / 100)
        int_on_adv = adv_growth * 182.5 * (yield_on_adv / 100)

        # Rent
        rent_annum = monthly_rent * 12

        # Expenditure
        total_exp = (
            to_float(data.get('stationeryMisc', 0)) +
            rent_annum +
            int_on_dep +
            to_float(data.get('interestBorrowed', 0)) +
            to_float(data.get('estCharges', 0))
        )

        # Income
        total_inc = (
            int_on_adv +
            to_float(data.get('commission', 0)) +
            to_float(data.get('exchange', 0)) +
            to_float(data.get('interestLent', 0))
        )

        profit = total_inc - total_exp

        return {
            'workingDays': working_days,
            'prospectsDeposits': round(prospects_dep, 2),
            'prospectsAdvances': round(prospects_adv, 2),
            'interestDeposits': round(int_on_dep, 2),
            'interestAdvances': round(int_on_adv, 2),
            'rentAnnum': round(rent_annum, 2),
            'totalExpenditure': round(total_exp, 2),
            'totalIncome': round(total_inc, 2),
            'cumulativeProfit': round(profit, 2)
        }

    def save_survey(self, survey: Dict):
        surveys = self._load_data()
        if 'id' not in survey:
            survey['id'] = datetime.now().strftime("%Y%m%d%H%M%S")
        survey['updated_at'] = datetime.now().isoformat()
        
        # Auto-calculate viability before saving
        viability = self.calculate_viability(survey)
        survey.update(viability)

        # Check if updating
        updated = False
        for i, s in enumerate(surveys):
            if isinstance(s, dict) and s.get('id') == survey['id']:
                surveys[i] = survey
                updated = True
                break
        
        if not updated:
            surveys.append(survey)
            
        self._save_data(surveys)
        return survey

    def get_all(self) -> List[Dict]:
        data = self._load_data()
        valid_data = [x for x in data if isinstance(x, dict)]
        return sorted(valid_data, key=lambda x: x.get('updated_at', ''), reverse=True)
