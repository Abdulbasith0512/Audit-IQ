import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
import os

# --- Configuration ---
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
MASTER_TABLE_PATH = os.path.join(DATA_DIR, "master_table.csv")
OUTPUT_PATH = os.path.join(DATA_DIR, "anomalies.csv")
SEED = 42

# Contamination parameter: We choose 0.03 (3%) because we injected roughly 3% suspicious transactions.
# In a real-world internal audit department, this parameter is calibrated based on historical fraud/error rates 
# and the audit team's capacity to investigate alerts (avoiding "alert fatigue").
CONTAMINATION = 0.03

def engineer_features(df):
    """
    Performs feature engineering on the merged master table to prepare it for anomaly detection.
    
    Features engineered:
    1. amount: The transaction amount.
    2. amount_to_threshold_ratio: Ratio of the amount to the approval threshold.
    3. is_weekend: Binary indicator (1 if Saturday/Sunday, 0 otherwise).
    4. is_round_number: Binary indicator (1 if amount is divisible by 100, 0 otherwise).
    5. days_since_last_same_vendor_amount: Time in days since the previous transaction
       with the exact same vendor and amount.
    """
    df = df.copy()
    
    # Ensure date is a datetime object
    df['date'] = pd.to_datetime(df['date'])
    
    # Feature 1: Amount (already exists)
    
    # Feature 2: Amount to threshold ratio
    # Captures transactions designed to "split" or squeeze right under approval limits.
    df['amount_to_threshold_ratio'] = df['amount'] / df['approval_threshold']
    
    # Feature 3: Is Weekend
    # Flags bookings outside normal working days.
    df['is_weekend'] = df['date'].dt.weekday.apply(lambda x: 1 if x >= 5 else 0)
    
    # Feature 4: Is Round Number
    # Checks if transaction is a whole number ending in '00'. Fraudulent or dummy invoices 
    # are frequently round numbers (e.g. $5,000.00 rather than $5,142.67).
    df['is_round_number'] = df['amount'].apply(lambda x: 1 if (x % 100 == 0 and x > 0) else 0)
    
    # Feature 5: Days since last same vendor and amount
    # Identifies duplicate billing cycles. We sort by vendor, amount, and date to calculate diffs.
    df = df.sort_values(by=['vendor_id', 'amount', 'date'])
    same_vendor = df['vendor_id'] == df['vendor_id'].shift(1)
    same_amount = df['amount'] == df['amount'].shift(1)
    date_diff = df['date'].diff()
    
    df['days_since_last_same_vendor_amount'] = np.where(
        same_vendor & same_amount,
        date_diff.dt.total_seconds() / (24 * 3600),
        999.0 # Large default value indicating no recent prior occurrence
    )
    
    # Restore original index sorting
    df = df.sort_index()
    return df

def generate_plain_english_reason(row):
    """
    Generates a human-readable auditing rationale explaining why a transaction was flagged.
    """
    reasons = []
    
    # 1. Proximity to approval threshold
    if 0.98 <= row['amount_to_threshold_ratio'] < 1.0:
        pct = row['amount_to_threshold_ratio'] * 100
        reasons.append(f"Amount is {pct:.1f}% of the approval threshold (${row['approval_threshold']:,}) — possible threshold-splitting.")
        
    # 2. Duplicate transactions within 2 days
    if row['days_since_last_same_vendor_amount'] <= 2.0:
        reasons.append(f"Duplicate payment of ${row['amount']:,} to vendor {row['vendor_id']} within {row['days_since_last_same_vendor_amount']:.1f} days — possible double-billing.")
        
    # 3. Weekend and off-hours activity
    dt = pd.to_datetime(row['date'])
    if row['is_weekend'] == 1:
        if dt.hour in [2, 3, 22, 23]:
            reasons.append(f"Processed on a weekend ({dt.day_name()}) at odd hours ({dt.strftime('%I:%M %p')}) — operational control bypass risk.")
        else:
            reasons.append(f"Processed on a weekend ({dt.day_name()}) — unusual business day transaction.")
    elif dt.hour in [2, 3, 22, 23]:
        reasons.append(f"Processed at odd hours ({dt.strftime('%I:%M %p')}) — unusual booking time.")
        
    # 4. High-risk vendor with large amount
    if row['risk_category'] == 'high' and row['amount'] > 10000:
        reasons.append("High amount transaction processed with a high-risk vendor.")
        
    # If Isolation Forest flagged it, but no single rule triggered (a multi-attribute anomaly)
    if not reasons:
        reasons.append("Multi-attribute anomaly — unusual combination of spending amount, threshold ratio, timing, and velocity.")
        
    return " | ".join(reasons)

def detect_anomalies():
    """
    Loads master_table.csv, performs feature engineering, runs Isolation Forest,
    filters the anomalies, computes user-friendly anomaly scores, attaches audit reasons,
    and saves the results to anomalies.csv.
    """
    print("Starting anomaly detection engine...")
    
    if not os.path.exists(MASTER_TABLE_PATH):
        print(f"Error: {MASTER_TABLE_PATH} not found. Please run the pipeline script first.")
        return
        
    df = pd.read_csv(MASTER_TABLE_PATH)
    
    # 1. Feature Engineering
    df_feat = engineer_features(df)
    
    # Select features for the machine learning model
    feature_cols = [
        'amount', 
        'amount_to_threshold_ratio', 
        'is_weekend', 
        'is_round_number', 
        'days_since_last_same_vendor_amount'
    ]
    X = df_feat[feature_cols]
    
    # 2. Train Isolation Forest
    # We use scikit-learn's Isolation Forest. It builds an ensemble of isolation trees.
    # Because anomalies are few and have different feature values, they require fewer splits to isolate 
    # (i.e. they are closer to the root of the trees).
    model = IsolationForest(
        n_estimators=100,
        contamination=CONTAMINATION,
        random_state=SEED
    )
    
    # Fit the model and predict labels (-1: anomaly, 1: normal)
    df_feat['anomaly_label'] = model.fit_predict(X)
    
    # Get the raw decision function scores (negative is more anomalous)
    raw_scores = model.decision_function(X)
    
    # Normalize decision scores to a clean 0 to 100% risk rating where higher is more anomalous
    min_score = raw_scores.min()
    max_score = raw_scores.max()
    df_feat['anomaly_score'] = np.round((raw_scores - max_score) / (min_score - max_score), 4)
    
    # 3. Filter Flagged Anomalies
    anomalies_df = df_feat[df_feat['anomaly_label'] == -1].copy()
    
    # 4. Generate plain-English audit reasons
    anomalies_df['reason'] = anomalies_df.apply(generate_plain_english_reason, axis=1)
    
    # Clean up output columns
    output_cols = [
        'transaction_id', 'date', 'vendor_id', 'vendor_name', 'employee_id', 'name', 
        'business_unit', 'amount', 'approval_threshold', 'payment_method', 
        'risk_category', 'anomaly_score', 'reason'
    ]
    anomalies_out = anomalies_df[output_cols].sort_values(by='anomaly_score', ascending=False)
    
    # Save anomalies to CSV
    anomalies_out.to_csv(OUTPUT_PATH, index=False)
    print(f"Successfully flagged {len(anomalies_out)} anomalies -> {OUTPUT_PATH}")

if __name__ == "__main__":
    detect_anomalies()
