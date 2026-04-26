import json
import pandas as pd
from pathlib import Path
from tabulate import tabulate
from schema_drift import detect_schema_drift
from datetime import datetime

# ─── 1. Load dbt artifacts ────────────────────────────────────────────────────
def load_artifacts():
    with open("target/manifest.json") as f:
        manifest = json.load(f)
    with open("target/run_results.json") as f:
        run_results = json.load(f)
    return manifest, run_results


# ─── 2. Extract failed tests ──────────────────────────────────────────────────
def extract_failures(run_results):
    failures = []
    for result in run_results["results"]:
        if result["status"] in ("fail", "error", "warn"):
            failures.append({
                "test": result["unique_id"].split(".")[-1],
                "status": result["status"].upper(),
                "failures": result.get("failures", 0),
                "message": result.get("message", ""),
            })
    return failures


# ─── 3. Profile the CSV data ──────────────────────────────────────────────────
def profile_data(csv_path="data/orders.csv"):
    df = pd.read_csv(csv_path)
    profile = {}

    for col in df.columns:
        profile[col] = {
            "total_rows": len(df),
            "null_count": int(df[col].isnull().sum()),
            "null_percent": round(df[col].isnull().mean() * 100, 2),
            "unique_values": int(df[col].nunique()),
        }

        # Extra checks for numeric columns
        if pd.api.types.is_numeric_dtype(df[col]):
            profile[col]["min"] = float(df[col].min())
            profile[col]["max"] = float(df[col].max())
            profile[col]["mean"] = round(float(df[col].mean()), 2)

    return profile, df


# ─── 4. AI analysis (mock — no API needed) ────────────────────────────────────
def analyze_failure(test_name, profile):
    analyses = {
        "not_null_orders_order_id": {
            "root_cause": "The 'order_id' column has NULL values. Every order must have a unique ID — missing IDs break joins and reporting.",
            "severity": "CRITICAL",
            "fix": "Find the source system sending NULL order_ids and add a NOT NULL constraint at ingestion.",
            "new_test": "not_null: order_id"
        },
        "accepted_values_orders_status": {
            "root_cause": "The 'status' column contains an unexpected value 'INVALID'. Only 'completed' and 'pending' are allowed.",
            "severity": "WARN",
            "fix": "Add input validation at the source. Clean existing rows with: UPDATE orders SET status='pending' WHERE status='INVALID'.",
            "new_test": "accepted_values:\n          values: ['completed', 'pending']"
        },
        "positive_amount_orders": {
            "root_cause": "The 'amount' column has a negative value (-50). Order amounts should always be positive numbers.",
            "severity": "CRITICAL",
            "fix": "Check if this is a refund that was incorrectly recorded. Add a dbt test to flag amounts below zero.",
            "new_test": "dbt_utils.expression_is_true:\n          expression: \">= 0\""
        },
    }

    return analyses.get(test_name, {
        "root_cause": "Unknown failure — manual investigation required.",
        "severity": "WARN",
        "fix": "Review the raw data and dbt test logic manually.",
        "new_test": "not_null"
    })


# ─── 5. Print a beautiful report ──────────────────────────────────────────────
def print_report(failures, drift, profile, analyses):
    print("\n" + "="*65)
    print("         🔍 DBT DATA QUALITY MONITOR REPORT")
    print(f"         Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*65)

    # Schema drift
    print("\n📊 SCHEMA DRIFT CHECK")
    print("-"*65)
    if drift:
        for d in drift:
            print(f"  ⚠️  Drift in model '{d['model']}': {d['changes']}")
    else:
        print("  ✅ No schema drift detected")

    # Data profile
    print("\n📈 DATA PROFILE SUMMARY")
    print("-"*65)
    profile_rows = []
    for col, stats in profile.items():
        profile_rows.append([
            col,
            stats["total_rows"],
            stats["null_count"],
            f"{stats['null_percent']}%",
            stats["unique_values"],
            f"{stats.get('min', 'N/A')} → {stats.get('max', 'N/A')}"
        ])
    print(tabulate(
        profile_rows,
        headers=["Column", "Rows", "Nulls", "Null%", "Unique", "Range"],
        tablefmt="rounded_outline"
    ))

    # Failures + AI analysis
    print("\n🚨 TEST FAILURES & AI ANALYSIS")
    print("-"*65)
    if not failures:
        print("  ✅ All tests passed!")
    else:
        for i, failure in enumerate(failures, 1):
            analysis = analyses[i-1]
            severity_icon = "🔴" if analysis["severity"] == "CRITICAL" else "🟡"
            print(f"\n  {severity_icon} [{analysis['severity']}] {failure['test']}")
            print(f"     Failures : {failure['failures']} row(s)")
            print(f"     Root cause: {analysis['root_cause']}")
            print(f"     Fix       : {analysis['fix']}")
            print(f"     New test  : {analysis['new_test']}")

    print("\n" + "="*65)
    print("  ✅ Monitor run complete! Check above for issues.")
    print("="*65 + "\n")


# ─── 6. Run everything ────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("🚀 Starting dbt Data Quality Monitor...")

    # Load files
    manifest, run_results = load_artifacts()

    # Run all checks
    drift = detect_schema_drift(manifest)
    failures = extract_failures(run_results)
    profile, df = profile_data()

    # Analyze each failure
    analyses = [analyze_failure(f["test"], profile) for f in failures]

    # Print final report
    print_report(failures, drift, profile, analyses)