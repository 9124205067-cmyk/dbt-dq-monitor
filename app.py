import streamlit as st
import json
import pandas as pd
from schema_drift import detect_schema_drift
from monitor import load_artifacts, extract_failures, profile_data, analyze_failure

# ─── Page config ──────────────────────────────────────────────
st.set_page_config(
    page_title="DBT Data Quality Monitor",
    page_icon="🔍",
    layout="wide"
)

# ─── Header ───────────────────────────────────────────────────
st.title("🔍 DBT Data Quality Monitor")
st.markdown("AI-powered data quality monitoring built on top of dbt")
st.divider()

# ─── Run monitor ──────────────────────────────────────────────
manifest, run_results = load_artifacts()
drift = detect_schema_drift(manifest)
failures = extract_failures(run_results)
profile, df = profile_data()
analyses = [analyze_failure(f["test"], profile) for f in failures]

# ─── Top metrics ──────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
critical = sum(1 for a in analyses if a["severity"] == "CRITICAL")
warnings = sum(1 for a in analyses if a["severity"] == "WARN")

col1.metric("Total Tests", len(run_results["results"]))
col2.metric("Failed Tests", len(failures), delta=f"-{len(failures)}", delta_color="inverse")
col3.metric("Critical Issues", critical, delta=f"-{critical}", delta_color="inverse")
col4.metric("Schema Drifts", len(drift), delta=f"-{len(drift)}", delta_color="inverse")

st.divider()

# ─── Schema drift ─────────────────────────────────────────────
st.subheader("📊 Schema Drift Check")
if drift:
    for d in drift:
        st.warning(f"⚠️ Drift detected in model **{d['model']}**: {d['changes']}")
else:
    st.success("✅ No schema drift detected")

st.divider()

# ─── Data profile ─────────────────────────────────────────────
st.subheader("📈 Data Profile Summary")
profile_rows = []
for col, stats in profile.items():
    profile_rows.append({
        "Column": col,
        "Total Rows": stats["total_rows"],
        "Null Count": stats["null_count"],
        "Null %": f"{stats['null_percent']}%",
        "Unique Values": stats["unique_values"],
        "Min": stats.get("min", "N/A"),
        "Max": stats.get("max", "N/A"),
    })

st.dataframe(pd.DataFrame(profile_rows), use_container_width=True)

st.divider()

# ─── Raw data preview ─────────────────────────────────────────
st.subheader("🗂️ Raw Data Preview")
st.dataframe(df, use_container_width=True)

st.divider()

# ─── Test failures ────────────────────────────────────────────
st.subheader("🚨 Test Failures & AI Analysis")

if not failures:
    st.success("✅ All tests passed!")
else:
    for failure, analysis in zip(failures, analyses):
        if analysis["severity"] == "CRITICAL":
            color = "🔴"
            box = st.error
        else:
            color = "🟡"
            box = st.warning

        with st.expander(f"{color} [{analysis['severity']}] {failure['test']} — {failure['failures']} row(s) failed"):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**🔎 Root Cause**")
                st.write(analysis["root_cause"])
                st.markdown("**🛠️ Fix**")
                st.write(analysis["fix"])
            with col2:
                st.markdown("**✅ Suggested New dbt Test**")
                st.code(analysis["new_test"], language="yaml")