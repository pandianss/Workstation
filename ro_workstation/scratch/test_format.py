from src.core.utils.number_utils import format_indian_number

test_values = [
    1000,
    100000,
    1000000,
    3250000,
    "3250000",
    "3,250,000.00"
]

for v in test_values:
    print(f"Input: {v} -> Output: {format_indian_number(v)}")
