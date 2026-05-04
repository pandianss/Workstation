from src.infrastructure.persistence.database import get_db_session
from src.infrastructure.persistence.sqlite_models import MISRecordModel, MasterRecordModel
from sqlalchemy import func
import pandas as pd

def calculate_milestones():
    with get_db_session() as session:
        # Fetch latest MIS records for all branches
        latest_date = session.query(func.max(MISRecordModel.date)).scalar()
        recs = session.query(MISRecordModel).filter(MISRecordModel.date == latest_date).all()
        
        # Fetch branch masters for names
        branches = session.query(MasterRecordModel).filter(MasterRecordModel.category == 'BRANCH').all()
        branch_map = {b.code: b.name_en for b in branches}
        
        data = []
        for r in recs:
            if r.sol == 3933: continue # Skip RO
            
            # Definitions (Values are in Lakhs, convert to Crores)
            sb_cr = r.sb / 100
            cd_cr = r.cd / 100
            casa_cr = sb_cr + cd_cr
            td_cr = r.td / 100
            
            jewel_cr = r.gold / 100
            housing_cr = r.housing / 100
            vehicle_cr = r.vehicle / 100
            agri_cr = r.core_agri / 100
            msme_cr = r.msme / 100
            
            # Core Retail = sum of retail sub-fields
            core_retail_cr = (r.housing + r.vehicle + r.gold + r.personal + 
                             r.education + r.mortgage + r.liquirent + r.other_retail) / 100
            
            total_adv_cr = agri_cr + msme_cr + core_retail_cr
            total_dep_cr = sb_cr + cd_cr + td_cr
            business_cr = total_dep_cr + total_adv_cr
            
            branch_data = {
                "SOL": r.sol,
                "Branch": branch_map.get(str(r.sol), "Unknown"),
                "SB": sb_cr,
                "CD": cd_cr,
                "CASA": casa_cr,
                "TD": td_cr,
                "Business": business_cr,
                "Jewel": jewel_cr,
                "Housing": housing_cr,
                "Vehicle": vehicle_cr,
                "Core Agri": agri_cr,
                "MSME": msme_cr,
                "Core Retail": core_retail_cr
            }
            data.append(branch_data)
            
        df = pd.DataFrame(data)
        
        # Check milestones
        parameters = ["SB", "CD", "CASA", "TD", "Business", "Jewel", "Housing", "Vehicle", "Core Agri", "MSME", "Core Retail"]
        
        results = []
        for p in parameters:
            m50 = df[df[p] >= 50].shape[0]
            m100 = df[df[p] >= 100].shape[0]
            results.append({"Parameter": p, "Reached 50Cr": m50, "Reached 100Cr": m100})
            
        print("\n--- Milestones Summary (Branches Count) ---")
        print(pd.DataFrame(results).to_string(index=False))
        
        # Top 5 branches for Business
        print("\n--- Top 5 Branches by Business (Cr) ---")
        print(df.nlargest(5, "Business")[["Branch", "Business"]].to_string(index=False))

if __name__ == "__main__":
    calculate_milestones()
