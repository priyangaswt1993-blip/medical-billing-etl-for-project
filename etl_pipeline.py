"""
etl_pipeline.py

A small ETL (Extract, Transform, Load) pipeline for healthcare billing data.

EXTRACT : Read raw billing claims from a CSV file (as if exported from a
          billing system).
TRANSFORM: Clean the data —
          - standardize inconsistent date formats
          - drop rows with missing patient names or procedure codes
          - fix/remove invalid billed amounts (blank, negative)
          - remove duplicate claims
          - standardize text fields (trim whitespace, fix casing)
LOAD    : Write the cleaned data into a SQLite database table, and also
          export a cleaned CSV + a simple summary report.

Run:
    python generate_sample_data.py   # creates raw_billing_data.csv
    python etl_pipeline.py           # runs the ETL pipeline
"""

import sqlite3
import pandas as pd
from datetime import datetime

RAW_FILE = "raw_billing_data.csv"
CLEAN_CSV = "cleaned_billing_data.csv"
DB_FILE = "billing_data.db"
TABLE_NAME = "billing_claims"


def extract(path: str) -> pd.DataFrame:
    """Read the raw CSV into a DataFrame."""
    df = pd.read_csv(path, dtype=str)  # read everything as string first
    print(f"[EXTRACT] Loaded {len(df)} raw rows from {path}")
    return df


def parse_any_date(value: str):
    """Try multiple known date formats and return a standardized YYYY-MM-DD string."""
    if not isinstance(value, str) or not value.strip():
        return None
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m-%d-%Y"):
        try:
            return datetime.strptime(value.strip(), fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None  # unrecognized format


def transform(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and standardize the raw billing data."""
    original_count = len(df)

    # 1. Trim whitespace from all string columns
    for col in df.columns:
        df[col] = df[col].astype(str).str.strip()

    # 2. Replace empty-string placeholders with actual NaN
    df.replace({"": None, "nan": None}, inplace=True)

    # 3. Drop rows missing critical fields
    df.dropna(subset=["patient_name", "procedure_code"], inplace=True)

    # 4. Standardize service_date into YYYY-MM-DD
    df["service_date"] = df["service_date"].apply(parse_any_date)
    df.dropna(subset=["service_date"], inplace=True)

    # 5. Clean billed_amount: convert to numeric, drop invalid/negative values
    df["billed_amount"] = pd.to_numeric(df["billed_amount"], errors="coerce")
    df = df[df["billed_amount"].notna() & (df["billed_amount"] > 0)]

    # 6. Fill missing insurance_provider with a clear label instead of blank
    df["insurance_provider"] = df["insurance_provider"].fillna("Self-Pay / Not Provided")

    # 7. Standardize procedure_code (uppercase, no spaces)
    df["procedure_code"] = df["procedure_code"].str.upper().str.replace(" ", "")

    # 8. Remove duplicate claims (same claim_id)
    df.drop_duplicates(subset=["claim_id"], keep="first", inplace=True)

    # 9. Reset index for a clean final table
    df.reset_index(drop=True, inplace=True)

    print(f"[TRANSFORM] Cleaned data: {original_count} -> {len(df)} rows "
          f"({original_count - len(df)} rows removed as invalid/duplicate)")
    return df


def load(df: pd.DataFrame):
    """Load the cleaned data into SQLite and export a cleaned CSV."""
    # Export cleaned CSV
    df.to_csv(CLEAN_CSV, index=False)
    print(f"[LOAD] Cleaned data written to {CLEAN_CSV}")

    # Load into SQLite
    conn = sqlite3.connect(DB_FILE)
    df.to_sql(TABLE_NAME, conn, if_exists="replace", index=False)
    print(f"[LOAD] Data loaded into {DB_FILE} (table: {TABLE_NAME})")

    # Simple summary report using SQL
    summary = pd.read_sql(f"""
        SELECT insurance_provider,
               COUNT(*) AS num_claims,
               ROUND(SUM(billed_amount), 2) AS total_billed
        FROM {TABLE_NAME}
        GROUP BY insurance_provider
        ORDER BY total_billed DESC
    """, conn)

    print("\n[REPORT] Billing summary by insurance provider:")
    print(summary.to_string(index=False))

    conn.close()
    return summary


def main():
    df_raw = extract(RAW_FILE)
    df_clean = transform(df_raw)
    load(df_clean)


if __name__ == "__main__":
    main()
