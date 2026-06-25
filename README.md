# AuditIQ – Audit Analytics & Continuous Controls Monitoring

AuditIQ is a Python-based audit analytics platform that simulates how internal audit teams in financial institutions identify control weaknesses, segregation of duties (SoD) conflicts, and potentially fraudulent transactions using data analytics and machine learning.

The project combines data engineering, audit rules, unsupervised anomaly detection, and interactive reporting into a single workflow that supports risk-based audit planning.

**Live Demo**

https://audit-iq-ecpram8fsmtjku7kawuzte.streamlit.app/

---

## Why I built this

Traditional audits often rely on manual sampling, which can miss unusual patterns hidden within large transaction datasets.

This project explores how audit teams can automate parts of that process by combining:

* Data pipelines
* Rule-based control testing
* Machine learning
* Interactive dashboards

The objective was to build a realistic portfolio project that reflects the type of analytical workflows used by internal audit and operational risk teams.

---

## Features

* Generates realistic banking transaction and employee access datasets
* Performs ETL and data standardization
* Detects Segregation of Duties (SoD) violations
* Identifies anomalous transactions using Isolation Forest
* Calculates department-level risk scores
* Visualizes findings through an interactive Streamlit dashboard

---

## Project Structure

```text
audit-iq/
├── dashboard/
│   └── app.py
├── data/
├── src/
│   ├── generate_data.py
│   ├── pipeline.py
│   ├── sod_engine.py
│   ├── anomaly_engine.py
│   └── risk_scoring.py
├── README.md
└── requirements.txt
```

---

## Workflow

```
Raw Data
    │
    ▼
ETL Pipeline
    │
    ▼
Master Dataset
    │
 ┌──┴─────────────┐
 ▼                ▼
SoD Checks   Anomaly Detection
 └──────┬─────────┘
        ▼
Risk Scoring
        ▼
Streamlit Dashboard
```

---

## Technologies Used

* Python
* Pandas
* NumPy
* Scikit-learn
* Plotly
* Streamlit
* Faker

---

## Running the Project

Install the required packages:

```bash
pip install -r requirements.txt
```

Generate the datasets:

```bash
python src/generate_data.py
```

Run the analytical pipeline:

```bash
python src/pipeline.py
python src/sod_engine.py
python src/anomaly_engine.py
python src/risk_scoring.py
```

Launch the dashboard:

```bash
streamlit run dashboard/app.py
```

---

## Dashboard

The dashboard provides:

* Department-wise risk rankings
* KPI summary cards
* Segregation of Duties violations
* Anomaly investigation tables
* Interactive filtering using Streamlit widgets

---

## Possible Improvements

Some areas I would extend in a future version include:

* Database-backed storage (PostgreSQL)
* Real-time transaction ingestion
* User authentication
* REST API integration
* Scheduled audit jobs
* Model monitoring and retraining

---

## Author

**Abdul Basith Syed**

B.Tech Computer Science Engineering

Interested in Data Science, Machine Learning, and Audit Analytics.
