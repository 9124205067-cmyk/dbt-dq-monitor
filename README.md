# 🔍 DBT Data Quality Monitor

An AI-powered data quality monitoring system built on top of dbt that automatically detects schema drift, profiles data, analyzes test failures, and displays results on an interactive Streamlit dashboard.

---

## 🚀 Features

- ✅ **Automated Test Failure Detection** — reads dbt `run_results.json` and flags failed tests
- ✅ **Schema Drift Detection** — compares current schema against previous run to catch column changes
- ✅ **Data Profiling** — analyzes null counts, unique values, min/max for every column
- ✅ **AI-Powered Root Cause Analysis** — explains why each test failed with severity levels
- ✅ **Streamlit Dashboard** — visualizes all results in a clean web interface

---

## 🛠️ Tech Stack

| Layer | Tool |
|---|---|
| Transformation | dbt Core |
| Schema Diff | DeepDiff |
| Data Profiling | Pandas |
| Dashboard | Streamlit |
| Language | Python 3.x |

---

## 📁 Project Structure
dbt-dq-monitor/
├── app.py              # Streamlit web dashboard
├── monitor.py          # Main monitoring logic
├── schema_drift.py     # Schema drift detection
├── sample_data.py      # Sample data generator
├── data/
│   └── orders.csv      # Sample orders dataset
├── target/
│   ├── manifest.json       # dbt manifest
│   └── run_results.json    # dbt test results
├── requirements.txt
└── README.md
---

## ⚙️ Setup & Run

**1. Clone the repo**
```bash
git clone https://github.com/YOUR_USERNAME/dbt-dq-monitor.git
cd dbt-dq-monitor
```

**2. Create virtual environment**
```bash
python -m venv venv
venv\Scripts\activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Generate sample data**
```bash
python sample_data.py
```

**5. Run the dashboard**
```bash
streamlit run app.py
```

Open `http://localhost:8501` in your browser.

---

## 📊 Dashboard Preview

The dashboard shows:
- 📈 **Data Profile Summary** — null counts, unique values, data ranges
- 🚨 **Test Failures** — with severity badges (CRITICAL / WARN)
- 🔎 **Root Cause Analysis** — AI-generated explanation for each failure
- 🛠️ **Fix Suggestions** — recommended actions to resolve issues
- 📊 **Schema Drift Check** — detects column additions, removals, type changes

---

## 🎯 Use Cases

- Monitor data pipeline quality after every dbt run
- Catch schema changes before they break downstream models
- Get AI-powered explanations for data quality failures
- Track data health trends over time

---

## 👤 Author

**Your Name**  
[GitHub](https://github.com/9124205067-cmyk)