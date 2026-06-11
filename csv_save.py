import gzip
import shutil
from pathlib import Path

input_file = Path("Texas_Commission_on_Environmental_Quality_-_Compliance_History_Report (1).csv.gz")
output_file = Path("Texas_Commission_on_Environmental_Quality_-_Compliance_History_Report.csv")

with gzip.open(input_file, "rb") as f_in:
    with open(output_file, "wb") as f_out:
        shutil.copyfileobj(f_in, f_out)

print(f"Saved: {output_file}")