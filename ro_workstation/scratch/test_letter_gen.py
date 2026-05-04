
import sys
import os
from pathlib import Path

# Add src to path
sys.path.append(str(Path(os.getcwd())))

from src.application.services.performance_letter_service import PerformanceLetterService
import datetime

def test_generation():
    service = PerformanceLetterService()
    # Mock some data
    performance_data = [
        {
            "sol": 2287,
            "branch_name": "DINDIGUL MAIN",
            "date": datetime.date(2026, 3, 31),
            "achievements": [
                {
                    "parameter": "Total Deposits",
                    "actual": 15000.0,
                    "target": 14000.0,
                    "variance": 1000.0,
                    "pct": 107.14
                }
            ],
            "declines": [
                {
                    "parameter": "CASA",
                    "actual": 4000.0,
                    "target": 5000.0,
                    "variance": -1000.0,
                    "pct": 80.0
                }
            ]
        }
    ]
    
    try:
        print("Attempting to generate letters zip...")
        zip_data = service.generate_letters_zip(performance_data)
        print(f"Success! Zip size: {len(zip_data)} bytes")
        
        with open("test_performance_letters.zip", "wb") as f:
            f.write(zip_data)
        print("Saved to test_performance_letters.zip")
        
    except Exception as e:
        print(f"Error during generation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_generation()
