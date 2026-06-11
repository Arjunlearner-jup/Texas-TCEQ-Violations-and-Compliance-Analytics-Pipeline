import pandas as pd
import numpy as np

# =============================================================================
# STEP 1: Load source tables
# =============================================================================
viol = pd.read_csv("tceq_violations.csv")
comp = pd.read_csv("Texas_Commission_on_Environmental_Quality_-_Compliance_History_Report_cleaned.csv")

# =============================================================================
# STEP 2: Standardize column names
# =============================================================================
viol.columns = viol.columns.str.strip().str.lower()
comp.columns = comp.columns.str.strip().str.lower()

# =============================================================================
# STEP 3: Clean join key (rn_number)
# =============================================================================
for df in [viol, comp]:
    if "rn_number" in df.columns:
        df["rn_number"] = (
            df["rn_number"]
            .astype("string")
            .str.strip()
            .str.upper()
            .str.replace(r"\s+", "", regex=True)
        )

# =============================================================================
# STEP 4: Parse dates
# =============================================================================
for col in ["invest_approved_dt", "violation_status_date", "ingested_at"]:
    if col in viol.columns:
        viol[col] = pd.to_datetime(viol[col], errors="coerce")

for col in ["customer_rating_date", "rn_rating_date"]:
    if col in comp.columns:
        comp[col] = pd.to_datetime(comp[col], errors="coerce")

# =============================================================================
# STEP 5: Aggregate violations at RN level before merge
# =============================================================================
viol_agg = (
    viol.groupby("rn_number", dropna=False)
    .agg(
        distinct_investigations=("investigation_no", "nunique"),
        distinct_violation_ids=("violation_id", "nunique"),
        total_viol_cnt=("viol_cnt", "sum"),
        first_violation_date=("invest_approved_dt", "min"),
        latest_violation_date=("invest_approved_dt", "max"),
    )
    .reset_index()
)

# =============================================================================
# STEP 6: Merge tables
# =============================================================================
merged = comp.merge(viol_agg, on="rn_number", how="left", validate="m:1")

# =============================================================================
# STEP 7: Create derived fields
# =============================================================================
merged["violation_year"] = merged["latest_violation_date"].dt.year
merged["rn_rating_year"] = merged["rn_rating_date"].dt.year
merged["customer_rating_year"] = merged["customer_rating_date"].dt.year

# =============================================================================
# STEP 8: Fill numeric nulls (from aggregation)
# =============================================================================
for col in ["distinct_investigations", "distinct_violation_ids", "total_viol_cnt"]:
    merged[col] = merged[col].fillna(0).astype("Int64")

# =============================================================================
# STEP 9: Save intermediate merged file
# =============================================================================
merged.to_csv("tceq_merged_dashboard_ready.csv", index=False, encoding="utf-8-sig")
print("Saved: tceq_merged_dashboard_ready.csv")
print("Rows:", len(merged))
print("Columns:", len(merged.columns))

# =============================================================================
# STEP 10: Load the merged data for cleaning
# =============================================================================
df = pd.read_csv('tceq_merged_dashboard_ready.csv')

print(f"\nOriginal rows: {len(df)}")
print(f"Null counts by column:")
print(df.isnull().sum())

# =============================================================================
# STEP 11: Clean column names to lowercase (ensure consistency)
# =============================================================================
df.columns = df.columns.str.strip().str.lower()

# =============================================================================
# STEP 12: Clean city (text column) - replace nulls with "Unknown"
# =============================================================================
df['city'] = df['city'].fillna('Unknown')

# =============================================================================
# STEP 13: Clean additional_identifiers (text column) - replace nulls with "None"
# =============================================================================
df['additional_identifiers'] = df['additional_identifiers'].fillna('None')

# =============================================================================
# STEP 14: Clean first_violation_date (date column)
# =============================================================================
df['first_violation_date'] = pd.to_datetime(df['first_violation_date'], errors='coerce')
df['first_violation_date'] = df['first_violation_date'].fillna(pd.Timestamp('1900-01-01'))

# =============================================================================
# STEP 15: Clean latest_violation_date (date column)
# =============================================================================
df['latest_violation_date'] = pd.to_datetime(df['latest_violation_date'], errors='coerce')
df['latest_violation_date'] = df['latest_violation_date'].fillna(pd.Timestamp('1900-01-01'))

# =============================================================================
# STEP 16: Clean violation_year (numeric column) - replace nulls with 0
# =============================================================================
df['violation_year'] = df['violation_year'].fillna(0)

# =============================================================================
# STEP 17: Verify cleaning results
# =============================================================================
print(f"\nCleaned rows: {len(df)}")
print(f"Remaining null counts:")
print(df.isnull().sum())

print(f"\nNull percentages by column:")
null_pct = (df.isnull().sum() / len(df)) * 100
print(null_pct)

# =============================================================================
# STEP 18: Save cleaned data
# =============================================================================
df.to_excel('tceq_merged_dashboard_ready_cleaned.xlsx', index=False)
print(f"\nCleaned data saved to: tceq_merged_dashboard_ready_cleaned.csv")

# =============================================================================
# STEP 19: Create a data quality summary
# =============================================================================
data_quality = {
    'Total Rows': len(df),
    'Rows with Missing City (now Unknown)': df['city'].eq('Unknown').sum(),
    'Rows with Missing Additional_identifiers (now None)': df['additional_identifiers'].eq('None').sum(),
    'Rows with Missing First_violation_date (now 1900-01-01)': df['first_violation_date'].eq(pd.Timestamp('1900-01-01')).sum(),
    'Rows with Missing Latest_violation_date (now 1900-01-01)': df['latest_violation_date'].eq(pd.Timestamp('1900-01-01')).sum(),
    'Rows with Missing violation_year (now 0)': df['violation_year'].eq(0).sum(),
}

print("\nData Quality Summary:")
for key, value in data_quality.items():
    print(f"{key}: {value}")

# =============================================================================
# STEP 20: Save data quality summary to Excel (opens directly in Excel)
# =============================================================================
quality_df = pd.DataFrame({
    'Metric': list(data_quality.keys()),
    'Count': list(data_quality.values())
})

