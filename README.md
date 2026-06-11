# Texas TCEQ Violations and Compliance Analytics Pipeline

An end-to-end data engineering and analytics project that ingests, cleans, integrates, and prepares Texas Commission on Environmental Quality (TCEQ) violation and compliance data for reporting and dashboard visualization.

## Project overview

This project combines multiple ETL workflows into a single pipeline for transforming raw TCEQ source files into a clean, dashboard-ready analytical dataset. The pipeline uses MongoDB for initial ingestion of semi-structured violation records, PostgreSQL for structured storage and export, pandas for cleaning and transformation, and a final merge process to generate a unified dataset for analytics.

## Project title

**Texas TCEQ Violations and Compliance Analytics Pipeline**

## Objectives

- Ingest TCEQ Notices of Violation (NOV) JSON data into MongoDB.
- Normalize and move curated violation records into PostgreSQL.
- Clean and standardize TCEQ Compliance History Report CSV data.
- Merge violations and compliance history into a single analytical dataset.
- Aggregate violation information by regulated entity.
- Produce a dashboard-ready dataset with data quality metrics.

## End-to-end workflow

```text
Raw TCEQ NOV JSON
        |
        v
Script 1: JSON ingestion into MongoDB
        |
        v
MongoDB collection of NOV records
        |
        v
Script 2: MongoDB to PostgreSQL migration
        |
        v
PostgreSQL relational table
        |
        v
CSV export from PostgreSQL

Raw TCEQ Compliance History CSV
        |
        v
Script 3: CSV cleaning and standardization
        |
        v
Cleaned compliance history dataset

Violation export + Cleaned compliance dataset
        |
        v
Script 4: Merge, aggregate, and quality checks
        |
        v
Dashboard-ready merged dataset
```

## Workflow by script

### Script 1: NOV JSON ingestion into MongoDB

This script performs the first-stage ingestion of TCEQ Notices of Violation data.

**Main tasks:**
- Read raw JSON source files.
- Extract relevant violation attributes.
- Transform records into a MongoDB-friendly document structure.
- Insert the documents into a local MongoDB database.

**Purpose:**
- Store semi-structured government compliance data in a flexible NoSQL format.
- Create a reliable source collection for downstream relational processing.

### Script 2: MongoDB to PostgreSQL migration and CSV export

This script moves curated NOV data from MongoDB into PostgreSQL and then exports it for further use.

**Main tasks:**
- Create the PostgreSQL database if it does not already exist.
- Connect to MongoDB and read ingested NOV documents.
- Map document fields into a relational schema.
- Create the target PostgreSQL table.
- Bulk insert rows using efficient batch operations.
- Query the relational table into pandas.
- Export the result to CSV.

**Purpose:**
- Convert semi-structured documents into a structured relational model.
- Improve queryability, consistency, and downstream interoperability.
- Generate a tabular violation dataset for merge operations and analysis.

### Script 3: Compliance History CSV cleaning and standardization

This script cleans the TCEQ Compliance History Report data using pandas.

**Main tasks:**
- Read the raw compliance history CSV file.
- Fix inconsistent spacing and capitalization.
- Standardize classifications and text values.
- Normalize date fields into usable formats.
- Prepare a clean dataset suitable for integration.

**Purpose:**
- Resolve common real-world data quality problems in public-sector CSV files.
- Ensure compliance history data is consistent before merging with violation data.

### Script 4: Merge, aggregation, and dashboard-ready output

This script combines the prepared datasets and creates the final analytical output.

**Main tasks:**
- Merge cleaned compliance history data with violation data.
- Aggregate violations by regulated entity.
- Generate summary metrics for analysis.
- Add data quality indicators.
- Produce a cleaned dataset for dashboarding and reporting.

**Purpose:**
- Build a unified analytical layer from multiple TCEQ sources.
- Create a final dataset that supports reporting, Power BI dashboards, and further analysis.

## Data flow architecture

| Stage | Input | Process | Output |
|---|---|---|---|
| 1 | TCEQ NOV JSON | Ingest into MongoDB | MongoDB NOV collection |
| 2 | MongoDB NOV collection | Map into PostgreSQL and export | Structured violations CSV |
| 3 | TCEQ Compliance History CSV | Clean and standardize with pandas | Cleaned compliance CSV |
| 4 | Violations CSV + cleaned compliance CSV | Merge, aggregate, validate | Dashboard-ready merged dataset |

## Suggested folder structure

```text
project/
├── scripts/
│   ├── 01_ingest_nov_json_to_mongodb.py
│   ├── 02_mongodb_to_postgresql_and_export.py
│   ├── 03_clean_compliance_history_csv.py
│   └── 04_merge_and_prepare_dashboard_dataset.py
├── data/
│   ├── raw/
│   ├── interim/
│   └── processed/
├── output/
│   └── tceq_merged_dashboard_ready_cleaned.xlsx
└── README.md
```

## Technology stack

- **Python** for ETL scripting and data processing.
- **MongoDB** for ingesting and storing semi-structured NOV JSON documents.
- **PostgreSQL** for relational storage and structured export.
- **pandas** for data cleaning, transformation, merging, aggregation, and file export.
- **PyMongo** for MongoDB connectivity.
- **psycopg2** or equivalent PostgreSQL connector for relational loading.

## Expected outputs

The final project should produce outputs such as:

- A MongoDB collection containing ingested NOV records.
- A PostgreSQL table containing normalized violation records.
- A CSV export of structured violations data.
- A cleaned compliance history dataset.
- A merged dashboard-ready dataset in CSV or Excel format.
- Data quality metrics to support validation and reporting.

## Use cases

This pipeline supports:

- Environmental compliance reporting.
- Regulatory trend analysis.
- County- or entity-level dashboard visualizations.
- Data quality assessment for public compliance records.
- Business intelligence workflows in tools such as Power BI.

## Summary

The Texas TCEQ Violations and Compliance Analytics Pipeline is a full data workflow that takes raw environmental compliance data from JSON and CSV sources, processes it through MongoDB and PostgreSQL, standardizes and merges it with pandas, and produces a final dashboard-ready dataset for analysis and visualization.
