# Healthcare Billing Data ETL Pipeline

A small Python ETL (Extract, Transform, Load) project that cleans messy
healthcare billing claim data and loads it into a SQLite database,
producing a summary report.

This project simulates a common real-world scenario in medical billing
operations: raw claim exports often contain missing values, inconsistent
date formats, duplicate records, and invalid amounts. This pipeline
extracts that raw data, applies a series of cleaning/transformation
rules, and loads the cleaned result into a structured database.

## What it does

**Extract**
- Reads raw billing claims from `raw_billing_data.csv`

**Transform**
- Standardizes inconsistent date formats (`YYYY-MM-DD`, `DD/MM/YYYY`, `MM-DD-YYYY`) into one format
- Removes rows with missing patient name or procedure code
- Fixes/removes invalid billed amounts (blank, negative, non-numeric)
- Labels missing insurance provider values instead of leaving them blank
- Standardizes procedure codes (uppercase, no stray whitespace)
- Removes duplicate claims

**Load**
- Writes the cleaned dataset to `cleaned_billing_data.csv`
- Loads the cleaned data into a SQLite database (`billing_data.db`)
- Runs a SQL query to generate a billing summary by insurance provider

## How to run

```bash
pip install pandas

python generate_sample_data.py   # creates a sample raw dataset (raw_billing_data.csv)
python etl_pipeline.py           # runs the ETL pipeline end-to-end
```

## Example output

```
[EXTRACT] Loaded 60 raw rows from raw_billing_data.csv
[TRANSFORM] Cleaned data: 60 -> 26 rows (34 rows removed as invalid/duplicate)
[LOAD] Cleaned data written to cleaned_billing_data.csv
[LOAD] Data loaded into billing_data.db (table: billing_claims)

[REPORT] Billing summary by insurance provider:
     insurance_provider  num_claims  total_billed
          ICICI Lombard           6      58673.06
            Star Health           5      45213.71
              HDFC Ergo           4      43070.51
Self-Pay / Not Provided           4      34626.67
          United Health           4      30030.53
            Care Health           3       4185.39
```

## Tech used

- Python 3
- pandas (data cleaning/transformation)
- sqlite3 (database load + SQL summary query)

## Background

Built to combine prior experience in medical billing/coding operations
with newly self-studied ETL, SQL, and Python skills — reflecting the
kind of data cleanup and reporting tasks common in healthcare billing
systems.
