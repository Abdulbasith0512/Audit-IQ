# 🛡️ AuditIQ — End-to-End Audit Analytics & Controls Platform

AuditIQ is an end-to-end audit analytics and continuous controls monitoring (CCM) platform designed to simulate how modern Internal Audit (GIA) and Risk Management teams detect control failures, compliance violations, and fraudulent behaviors in transaction and system access data.

This project was built to demonstrate a data-driven approach to **risk-based audit planning**, bridging the gap between machine learning models and actionable audit evidence.

---

## 📐 Platform Architecture & Data Flow

```
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

---

## 📁 Repository Structure

```
audit-iq/
├── data/                  # Generated mock datasets & analysis outputs (CSV)
│   ├── transactions.csv
│   ├── employee_access.csv
│   ├── vendor_master.csv
│   ├── master_table.csv
│   ├── sod_violations.csv
│   ├── anomalies.csv
│   └── risk_ranking.csv
├── src/                   # Python source code for data pipeline & analytics
│   ├── generate_data.py   # Creates 3 raw datasets with deliberate anomalies
│   ├── pipeline.py        # Loads, cleans, standardizes, and joins data
│   ├── sod_engine.py      # Identifies Segregation of Duties (SoD) violations
│   ├── anomaly_engine.py  # Unsupervised Isolation Forest anomaly detection
│   └── risk_scoring.py    # Computes composite risk scores for business units
├── dashboard/             # Self-service visual monitoring app
│   └── app.py             # Streamlit dashboard script
├── README.md              # Technical documentation & interview guide
└── requirements.txt       # Project dependencies
```

---

## ⚙️ Setup & Installation

Follow these steps to set up and run the platform locally:

### 1. Clone the Repository & Initialize Environment
Ensure you have Python 3.9+ installed. Open a terminal in the project directory:

```bash
# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate  # On macOS/Linux
# venv\Scripts\activate   # On Windows
```

### 2. Install Project Dependencies
Install all required libraries (Pandas, Scikit-Learn, Plotly, Streamlit, and Faker):

```bash
pip install -r requirements.txt
```

### 3. Run the Analytical Pipeline in Order
To populate the database and run the detection engines, execute the scripts sequentially:

```bash
# Step A: Generate the raw mock data
python src/generate_data.py

# Step B: Run the ETL pipeline to clean and integrate data
python src/pipeline.py

# Step C: Detect system access vulnerabilities
python src/sod_engine.py

# Step D: Run machine learning anomaly detection
python src/anomaly_engine.py

# Step E: Compute composite risk rankings
python src/risk_scoring.py
```

### 4. Launch the Self-Service Dashboard
Run the Streamlit application to explore the audit dashboard locally:

```bash
streamlit run dashboard/app.py
```

The app will automatically open in your default browser at `http://localhost:8501`.

---

## 🧩 Detailed Module Descriptions

### 1. Mock Data Generator (`generate_data.py`)
Creates realistic banking data with reproducible randomness using a fixed seed (`42`):
*   **`vendor_master.csv` (100 rows):** Simulates a directory of authorized bank suppliers, with registration dates and risk classifications.
*   **`employee_access.csv` (200 rows):** A list of bank employees, mapping their roles to specific IT privileges. It injects a **5% rate of SoD violations** (employees holding conflicting rights).
*   **`transactions.csv` (3,000 rows):** Multi-million dollar corporate spend transactions, distributed exponentially. To test our pipeline, it injects a **3% rate of fraud anomalies**:
    *   *Threshold-splitting:* Amounts booked just under approval limits (e.g. $49,950 when the limit is $50,000).
    *   *Double-billing:* Duplicate transaction amounts paid to the same vendor twice within 48 hours.
    *   *Unusual hours:* Transactions approved at odd hours (e.g., 2 AM) or during weekends.

### 2. ETL Data Pipeline (`pipeline.py`)
Cleans, standardizes, and joins the raw source CSVs into a single `master_table.csv`:
*   Standardizes date and timestamp columns.
*   Parses string representations of IT lists back into native Python list objects securely using `ast.literal_eval`.
*   Integrates data using left outer joins to prevent transaction record loss.
*   Performs defensive data cleaning by filling missing merge values (imputation) with `"UNKNOWN"` indicators to prevent downstream analytical errors.

### 3. SoD Conflict Engine (`sod_engine.py`)
A preventative control scanner. It reads the employee database and flags individuals holding incompatible permissions. 
*   **SoD Rules Evaluated:** `create_vendor` + `approve_payment` (prevents fictitious vendor fraud) and `edit_invoice` + `approve_payment` (prevents payment diversion fraud).
*   Outputs a detailed log of violations (`sod_violations.csv`) alongside audit rationales and groups them to highlight structural IT audit risks.

### 4. Anomaly Detection Engine (`anomaly_engine.py`)
A detective control engine. It engineers financial features and trains an **unsupervised Isolation Forest model** to isolate outliers.
*   **Engineered Features:** Transaction amount, amount-to-threshold ratio, weekend indicator, round-number indicator, and duplicate billing velocity.
*   Outputs `anomalies.csv` with a normalized 0 to 100% anomaly score and a plain-English reasoning column translating the model's triggers back into standard business audit findings.

### 5. Risk Scoring Engine (`risk_scoring.py`)
Aggregates findings to enable risk-based audit planning:
*   Collects transactional volume, SoD violations, and anomaly counts per department.
*   Normalizes metrics using MinMax Scaling to place them on an equal scale.
*   Applies a weighted formula: **45% Access Controls + 45% ML Anomalies + 10% Volume**.
*   Generates a ranked risk leaderboard (`risk_ranking.csv`) detailing which department is the highest target priority.

### 6. Interactive Streamlit Dashboard (`dashboard/app.py`)
A self-service analytics console designed for chief auditors:
*   **Risk Leaderboard:** An interactive, color-coded table ranking departments from High to Low risk.
*   **Horizontal Bar Chart:** A Plotly visualization showing risk scores.
*   **KPI Cards:** High-level summary metrics (Volume, Anomalies, Access Violations) that update instantly.
*   **Sidebar Controls:** Interactive slide filters for date ranges and focus areas. Adjusting filters dynamically recomputes risk scores in real-time.
*   **Drill-Down Panels:** Granular views of detailed SoD violations, anomalous transactions (with risk score progress bars), and a searchable ledger log.

---

## 💬 Interview Quick-Reference Guide

Be prepared to answer these technical and business questions in your data science / internal audit interview:

### Q1: Why did you choose Isolation Forest instead of a standard classification model?
> "In transaction auditing, we deal with **unlabeled data** and **extreme class imbalance**. True fraud is rare (often < 0.1%) and we rarely have a set of labeled examples. Standard supervised models (like Random Forests or XGBoost) would fail or overfit. 
> 
> Isolation Forest is an unsupervised algorithm designed specifically for outlier detection. Instead of profiling normal transactions, it isolates anomalies. It does this by building an ensemble of isolation trees. Because anomalies have distinct values, they require fewer splits to isolate and appear closer to the root of the trees. It is computationally efficient and requires no feature scaling."

### Q2: Why did you normalize the variables in the Risk Scoring Engine?
> "Volume is measured in hundreds of transactions, whereas SoD violations and anomalies are measured in tens. If we plugged these raw numbers directly into a weighted formula, the volume would completely dominate the risk score. We normalized the metrics using **MinMax Scaling** so that all metrics sit on a standardized `[0, 1]` scale before applying our weights. This ensures that a department with massive volume but perfect controls isn't incorrectly flagged as high-risk."

### Q3: Why is Segregation of Duties (SoD) checking critical in a bank?
> "SoD is the core of preventative control in financial institutions. It ensures that no single individual can complete a transaction cycle without independent oversight. 
> 
> If an analyst can both create a vendor and approve payments to that vendor, they can execute fictitious vendor fraud. By writing a rule checker to flag these access anomalies, we catch system access vulnerabilities *before* they translate into active fraudulent payments."

### Q4: How would you upgrade this platform in a production environment?
> 1.  **Transition to Supervised Learning:** If we get feedback from auditors (i.e. 'audited and found true issue' labels), we can upgrade the weighted formula to a **supervised Logistic Regression model**, which allows us to mathematically optimize our risk weights and evaluate feature coefficients for audit explainability.
> 2.  **Incremental Pipelines (Spark/Airflow):** Run the ETL and model training on a weekly or daily schedule using Apache Airflow, processing streaming transaction files directly from the bank's core ledger database.
> 3.  **Model Monitoring:** Track feature drift and prediction distributions over time to monitor for changes in employee spending patterns and prevent model degradation.
