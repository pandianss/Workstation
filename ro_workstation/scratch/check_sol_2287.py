from src.infrastructure.persistence.database import get_db_session
from src.infrastructure.persistence.sqlite_models import MISRecordModel
from sqlalchemy import func

def check_2287():
    with get_db_session() as session:
        latest_date = session.query(func.max(MISRecordModel.date)).scalar()
        print(f"Latest Date: {latest_date}")
        
        rec = session.query(MISRecordModel).filter(MISRecordModel.sol == 2287, MISRecordModel.date == latest_date).first()
        if not rec:
            print("No record for SOL 2287 on latest date.")
            # Check if it exists at all
            any_rec = session.query(MISRecordModel).filter(MISRecordModel.sol == 2287).order_by(MISRecordModel.date.desc()).first()
            if any_rec:
                print(f"Found record for SOL 2287 on {any_rec.date}")
                rec = any_rec
            else:
                print("SOL 2287 not found in MIS records at all.")
                return

        # Calculate parameters as per MilestoneService
        sb = rec.sb / 100
        cd = rec.cd / 100
        td = rec.td / 100
        agri = rec.core_agri / 100
        msme = rec.msme / 100
        gold = rec.gold / 100
        
        core_retail = (
            rec.housing + rec.vehicle + rec.personal + 
            rec.education + rec.mortgage + rec.liquirent + rec.other_retail
        ) / 100
        
        total_dep = sb + cd + td
        total_adv = agri + msme + gold + core_retail # Wait! In service gold is separate from core_retail but in Total Adv?
        
        # Let's check MilestoneService._calculate_parameters
        # agri = r.core_agri / 100
        # msme = r.msme / 100
        # core_retail = (...) / 100
        # total_dep = sb + cd + td
        # total_adv = agri + msme + core_retail  <-- WAIT! I missed 'gold' in total_adv in the service?
        
        print("\nSOL 2287 Metrics (Cr):")
        print(f"  SB: {sb:.2f}")
        print(f"  CD: {cd:.2f}")
        print(f"  TD: {td:.2f}")
        print(f"  Agri: {agri:.2f}")
        print(f"  MSME: {msme:.2f}")
        print(f"  Jewel (Gold): {gold:.2f}")
        print(f"  Core Retail: {core_retail:.2f}")
        print(f"  Total Deposits: {total_dep:.2f}")
        print(f"  Total Advances: {total_adv:.2f}")
        print(f"  Business: {total_dep + total_adv:.2f}")

if __name__ == "__main__":
    check_2287()
