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
## Architecture & Data Flow

```text
                      +-----------------------------+
                      |   1. MOCK DATA GENERATOR    |
                      |     (generate_data.py)      |
                      +--------------+--------------+
                                     |
             +-----------------------+-----------------------+
             |                       |                       |
             v                       v                       v
     [ transactions.csv ]    [ employee_access.csv ]  [ vendor_master.csv ]
     (3,000 corporate spend  (200 employee roles &    (100 approved vendors &
      records + anomalies)    access permissions)      risk categories)
             |                       |                       |
             |                       +-----------+           |
             |                                   |           |
             v                                   v           v
+------------+------------+            +--------+-----------+-------+
|    2. ETL DATA PIPELINE |            | 3. SEGREGATION OF DUTIES   |
|      (pipeline.py)      |            |         ENGINE             |
+------------+------------+            |     (sod_engine.py)        |
             |                         +--------+-------------------+
             |                                   |
             v                                   v
    [ master_table.csv ]               [ sod_violations.csv ]
    (Joined, standardized,             (Employees holding conflicting
     and cleaned database)              privileges, e.g. vendor create
             |                          + payment approve)
             |                                   |
             v                                   |
+------------+------------+                      |
| 4. ANOMALY DETECTION    |                      |
|        ENGINE           |                      |
|  (anomaly_engine.py)    |                      |
+------------+------------+                      |
             |                                   |
             v                                   v
      [ anomalies.csv ]                          |
      (Isolation Forest flags                    |
       & plain-English reasons)                  |
             |                                   |
             +-----------------------+-----------+
                                     |
                                     v
                       +-------------+-------------+
                       |   5. RISK SCORING ENGINE  |
                       |      (risk_scoring.py)    |
                       +-------------+-------------+
                                     |
                                     v
                            [ risk_ranking.csv ]
                            (Business units ranked by
                             weighted risk scores)
                                     |
                                     v
                       +-------------+-------------+
                       |    6. STREAMLIT APP       |
                       |     (dashboard/app.py)    |
                       +---------------------------+
```

### Pipeline Summary

1. **Mock Data Generator** creates realistic banking datasets containing transactions, employee access records, and vendor information with intentionally injected control failures and anomalies.

2. **ETL Pipeline** cleans, standardizes, and integrates the datasets into a consolidated audit dataset.

3. **Segregation of Duties Engine** evaluates employee permissions against predefined control rules and identifies conflicting access rights.

4. **Anomaly Detection Engine** applies an Isolation Forest model to identify unusual transaction patterns and generates explainable audit findings.

5. **Risk Scoring Engine** combines SoD violations, anomaly counts, and transaction volume into weighted department-level risk scores.

6. **Streamlit Dashboard** presents the results through interactive visualizations, KPI cards, risk rankings, and drill-down investigation tables.

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
