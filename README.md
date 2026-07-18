# medical-billing-etl-for-project
import csv
import random
from datetime import datetime, timedelta

random.seed(42)

PATIENTS = ["John Mathew", "Priya S", "Ahmed Khan", "Lakshmi R", "David Paul",
            "Fatima N", "Ravi Kumar", "Sneha T", "", "Anitha M"]

PROCEDURE_CODES = ["99213", "99214", "99215", "36415", "80053", "85025", "  ", "99213"]

INSURANCE = ["Star Health", "HDFC Ergo", "ICICI Lombard", "United Health", None,
             "Star Health", "Care Health"]

DATE_FORMATS = ["%Y-%m-%d", "%d/%m/%Y", "%m-%d-%Y"]


def random_date():
    start = datetime(2024, 1, 1)
    random_days = random.randint(0, 300)
    dt = start + timedelta(days=random_days)
    fmt = random.choice(DATE_FORMATS)
    return dt.strftime(fmt)


def generate_rows(n=60):
    rows = []
    for i in range(1, n + 1):
        claim_id = f"CLM{1000 + i}"

        # occasionally duplicate a claim to simulate real-world messiness
        if random.random() < 0.1 and rows:
            rows.append(rows[-1])
            continue

        patient = random.choice(PATIENTS)
        proc_code = random.choice(PROCEDURE_CODES)
        insurance = random.choice(INSURANCE)
        billed_amount = round(random.uniform(500, 15000), 2)

        # randomly introduce missing/negative/blank amounts
        if random.random() < 0.08:
            billed_amount = -billed_amount
        if random.random() < 0.05:
            billed_amount = ""

        rows.append({
            "claim_id": claim_id,
            "patient_name": patient,
            "procedure_code": proc_code,
            "billed_amount": billed_amount,
            "insurance_provider": insurance if insurance else "",
            "service_date": random_date(),
        })
    return rows


def main():
    rows = generate_rows()
    fieldnames = ["claim_id", "patient_name", "procedure_code",
                  "billed_amount", "insurance_provider", "service_date"]

    with open("raw_billing_data.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Generated raw_billing_data.csv with {len(rows)} rows.")


if __name__ == "__main__":
    main()
