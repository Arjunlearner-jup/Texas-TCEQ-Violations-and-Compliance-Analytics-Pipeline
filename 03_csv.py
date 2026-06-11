import pandas as pd

INPUT_FILE = "Texas_Commission_on_Environmental_Quality_-_Compliance_History_Report.csv"
OUTPUT_FILE = "Texas_Commission_on_Environmental_Quality_-_Compliance_History_Report_cleaned.csv"

df = pd.read_csv(INPUT_FILE)

df.columns = (
    df.columns.str.strip()
    .str.replace(r"\s+", " ", regex=True)
)

rename_map = {
    "Customer Number (CN)": "customer_number",
    "Customer Name": "customer_name",
    "Customer Rating": "customer_rating",
    "Customer Classification": "customer_classification",
    "Customer Rating Date": "customer_rating_date",
    "Regulated Entity Number (RN)": "rn_number",
    "Regulated Entity Name": "rn_name",
    "City": "city",
    "County": "county",
    "TCEQ Region": "region",
    "Regulated Entity Rating": "rn_rating",
    "Regulated Entity Classification": "rn_classification",
    "Regulated Entity Rating Date": "rn_rating_date",
    "Additional Identifiers": "additional_identifiers"
}

df = df.rename(columns=rename_map)

text_cols = [
    "customer_number", "customer_name", "customer_rating", "customer_classification",
    "rn_number", "rn_name", "city", "county", "region",
    "rn_rating", "rn_classification", "additional_identifiers"
]

for col in text_cols:
    if col in df.columns:
        df[col] = (
            df[col]
            .astype("string")
            .str.strip()
            .str.replace(r"\s+", " ", regex=True)
        )

if "customer_number" in df.columns:
    df["customer_number"] = df["customer_number"].str.upper().str.replace(r"\s+", "", regex=True)

if "rn_number" in df.columns:
    df["rn_number"] = df["rn_number"].str.upper().str.replace(r"\s+", "", regex=True)

if "customer_name" in df.columns:
    df["customer_name"] = df["customer_name"].str.title()

if "rn_name" in df.columns:
    df["rn_name"] = df["rn_name"].str.title()

if "county" in df.columns:
    df["county"] = df["county"].str.title()

if "city" in df.columns:
    df["city"] = df["city"].str.title()

if "region" in df.columns:
    df["region"] = df["region"].str.replace(r"[^\dA-Za-z ]", "", regex=True).str.strip()

classification_map = {
    "HIGH PERFORMER": "High Performer",
    "SATISFACTORY PERFORMER": "Satisfactory Performer",
    "UNSATISFACTORY PERFORMER": "Unsatisfactory Performer",
    "UNCLASSIFIED": "Unclassified"
}

for col in ["customer_classification", "rn_classification"]:
    if col in df.columns:
        df[col] = (
            df[col]
            .astype("string")
            .str.upper()
            .str.strip()
            .map(classification_map)
            .fillna(df[col])
        )

for col in ["customer_rating_date", "rn_rating_date"]:
    if col in df.columns:
        df[col] = pd.to_datetime(df[col], errors="coerce")

if "customer_rating_date" in df.columns:
    df["customer_rating_year"] = df["customer_rating_date"].dt.year

if "rn_rating_date" in df.columns:
    df["rn_rating_year"] = df["rn_rating_date"].dt.year

dedupe_cols = [c for c in ["customer_number", "rn_number", "customer_rating_date", "rn_rating_date"] if c in df.columns]
if dedupe_cols:
    df = df.drop_duplicates(subset=dedupe_cols)
else:
    df = df.drop_duplicates()

df.to_csv(OUTPUT_FILE, index=False)

print("Cleaned file saved:", OUTPUT_FILE)
print("Rows after cleaning:", len(df))
print("Missing values by column:")
print(df.isna().sum())