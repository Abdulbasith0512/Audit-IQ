# 🛡️ AuditIQ — End-to-End Audit Analytics & Continuous Controls Monitoring Platform

> **A data-driven internal audit analytics platform that simulates how modern banks identify fraud, control failures, and compliance risks using machine learning and automated audit rules.**

![Python](https://img.shields.io/badge/Python-3.10-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red)
![Scikit-Learn](https://img.shields.io/badge/ML-IsolationForest-green)
![Pandas](https://img.shields.io/badge/Pandas-Data%20Analytics-purple)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 🚀 Live Demo

**🌐 Streamlit Application**

https://audit-iq-ecpram8fsmtjku7kawuzte.streamlit.app/

---

## 📌 Project Overview

AuditIQ is an end-to-end **Internal Audit Analytics** platform inspired by enterprise audit workflows used in banking and financial institutions.

The platform automatically:

* Generates realistic banking datasets
* Performs ETL and data quality validation
* Detects Segregation of Duties (SoD) violations
* Identifies suspicious financial transactions using Machine Learning
* Calculates department-level risk scores
* Visualizes audit findings in an interactive Streamlit dashboard

The project demonstrates how audit analytics can support **risk-based audit planning** through automation and explainable machine learning.

---

# ✨ Key Features

✅ Automated mock banking data generation

✅ ETL data integration pipeline

✅ Segregation of Duties (SoD) conflict detection

✅ Isolation Forest anomaly detection

✅ Department-wise risk scoring engine

✅ Interactive Streamlit dashboard

✅ Risk Leaderboard

✅ Drill-down investigation panels

✅ KPI cards & interactive filters

---

# 🏗 System Architecture

```
Mock Data Generator
        │
        ▼
ETL Pipeline
        │
        ▼
Master Audit Dataset
        │
 ┌──────┴────────┐
 ▼               ▼
SoD Engine   ML Anomaly Detection
 └──────┬────────┘
        ▼
 Risk Scoring Engine
        ▼
 Streamlit Dashboard
```

---

# 📂 Repository Structure

```
audit-iq/
│
├── dashboard/
│   └── app.py
│
├── data/
│
├── src/
│   ├── generate_data.py
│   ├── pipeline.py
│   ├── sod_engine.py
│   ├── anomaly_engine.py
│   └── risk_scoring.py
│
├── README.md
└── requirements.txt
```

---

# ⚙️ Technology Stack

### Programming

* Python

### Data Analytics

* Pandas
* NumPy

### Machine Learning

* Scikit-Learn
* Isolation Forest

### Visualization

* Streamlit
* Plotly

### Data Generation

* Faker

---

# 🔄 Audit Workflow

### 1️⃣ Generate Mock Banking Data

Creates:

* Vendor Master
* Employee Access Matrix
* Corporate Transactions

---

### 2️⃣ ETL Pipeline

* Data Cleaning
* Data Validation
* Data Integration
* Standardization

---

### 3️⃣ SoD Detection

Identifies employees with conflicting permissions such as:

* Create Vendor + Approve Payment
* Edit Invoice + Approve Payment

---

### 4️⃣ ML-Based Fraud Detection

Uses **Isolation Forest** to identify suspicious transactions based on engineered audit features.

Examples include:

* Threshold splitting
* Duplicate payments
* Weekend approvals
* Late-night approvals

---

### 5️⃣ Risk Scoring

Departments are ranked using a weighted score:

* **45% Access Control Risk**
* **45% Transaction Anomaly Risk**
* **10% Transaction Volume**

---

### 6️⃣ Interactive Dashboard

The Streamlit application provides:

* Executive KPI Cards
* Risk Leaderboard
* Interactive Charts
* Department Filters
* SoD Violations
* Suspicious Transactions
* Audit Evidence Tables

---

# ▶️ Running the Project

Clone the repository

```bash
git clone https://github.com/Abdulbasith0512/Audit-IQ.git
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run the pipeline

```bash
python src/generate_data.py
python src/pipeline.py
python src/sod_engine.py
python src/anomaly_engine.py
python src/risk_scoring.py
```

Launch the dashboard

```bash
streamlit run dashboard/app.py
```

---

# 📊 Dashboard Preview

*(Add screenshots here after deployment.)*

Example:

```
dashboard_images/
    home.png
    risk_leaderboard.png
    anomalies.png
```

---

# 🎯 Business Value

AuditIQ demonstrates how audit analytics can help organizations:

* Detect fraud earlier
* Reduce manual audit effort
* Prioritize high-risk departments
* Strengthen internal controls
* Support continuous auditing
* Improve compliance monitoring

---

# 🚀 Future Enhancements

* Role-based authentication
* Real-time transaction monitoring
* SQL database integration
* REST API services
* Predictive fraud scoring
* AI-powered audit report generation
* Cloud deployment with Docker & Kubernetes

---

# 👨‍💻 Author

**Abdul Basith Syed**

B.Tech Computer Science | Data Science | Machine Learning | Full Stack Development

GitHub: https://github.com/Abdulbasith0512

---

⭐ If you found this project useful, consider giving it a Star!
