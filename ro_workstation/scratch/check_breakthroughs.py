from src.application.services.milestone_service import MilestoneService
from src.infrastructure.persistence.database import get_db_session

def check_breakthroughs():
    with get_db_session() as session:
        ms = MilestoneService(session)
        achievements = ms.get_milestone_achievements()
        print(f"Total Breakthroughs in April 2026: {len(achievements)}")
        for a in achievements:
            print(f"  {a['branch_name']} - {a['parameter']}: {a['milestone']} (from {a['previous_value']:.2f} to {a['value']:.2f})")

if __name__ == "__main__":
    check_breakthroughs()
