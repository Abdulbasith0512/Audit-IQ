import pandas as pd
import numpy as np
import os

# --- Configuration ---
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
MASTER_TABLE_PATH = os.path.join(DATA_DIR, "master_table.csv")
SOD_VIOLATIONS_PATH = os.path.join(DATA_DIR, "sod_violations.csv")
ANOMALIES_PATH = os.path.join(DATA_DIR, "anomalies.csv")
OUTPUT_PATH = os.path.join(DATA_DIR, "risk_ranking.csv")

# Define the list of Business Units
BUSINESS_UNITS = ["Investment Banking", "Wealth Management", "Retail Banking", "Corporate Banking", "Global Markets"]

# Weights for our composite risk score (must sum to 1.0 or 100%)
# - w_sod (45%): Access control / SoD violations represent systemic process vulnerabilities.
# - w_anomaly (45%): Transactional anomalies represent active risk events/errors.
# - w_volume (10%): Total transaction volume represents overall exposure. 
#   We keep this low (10%) so size alone does not dominate small business units with poor controls.
WEIGHT_SOD = 0.45
WEIGHT_ANOMALY = 0.45
WEIGHT_VOLUME = 0.10

def min_max_scale(series):
    """Safely normalizes a series between 0 and 1. Handles edge case of zero variance."""
    if series.max() == series.min():
        return pd.Series(0.0, index=series.index)
    return (series - series.min()) / (series.max() - series.min())

def generate_risk_explanation(row):
    """Generates a plain-English explanation of the risk profile for a business unit."""
    reasons = []
    
    # Analyze SoD violations
    if row['sod_violations'] > 18:
        reasons.append(f"Critical access risk ({int(row['sod_violations'])} SoD violations)")
    elif row['sod_violations'] > 10:
        reasons.append(f"Elevated access risk ({int(row['sod_violations'])} SoD violations)")
        
    # Analyze transaction anomalies
    if row['anomaly_count'] > 20:
        reasons.append(f"Severe transaction anomalies ({int(row['anomaly_count'])} alerts, total severity: {row['total_anomaly_score']:.1f})")
    elif row['anomaly_count'] > 10:
        reasons.append(f"Elevated transaction anomalies ({int(row['anomaly_count'])} alerts)")
        
    # Analyze total transaction volume
    if row['total_transactions'] > 700:
        reasons.append(f"High operational volume ({int(row['total_transactions'])} transactions)")
        
    if row['risk_score'] > 75:
        reasons.append("Overall Profile: HIGH RISK. Immediate supervisory audit recommended.")
    elif row['risk_score'] > 40:
        reasons.append("Overall Profile: MEDIUM RISK. Target for upcoming audit cycle.")
    else:
        reasons.append("Overall Profile: LOW RISK. Monitor routine controls.")
        
    return " | ".join(reasons)

def calculate_risk_scores():
    """
    Aggregates SoD violations, anomalies, and transaction volume per business unit.
    Normalizes indicators, computes a composite risk score, ranks units, and saves output.
    """
    print("Starting risk scoring engine...")
    
    # 1. Load source datasets
    try:
        master_df = pd.read_csv(MASTER_TABLE_PATH)
        sod_df = pd.read_csv(SOD_VIOLATIONS_PATH)
        anomalies_df = pd.read_csv(ANOMALIES_PATH)
    except FileNotFoundError as e:
        print(f"Error loading files: {e}. Ensure prior stages have run successfully.")
        return

    # 2. Aggregate metrics by Business Unit
    
    # Metric A: Total Transaction Volume (exposure size)
    volume_agg = master_df.groupby('business_unit').size().reset_index(name='total_transactions')
    
    # Metric B: Count of SoD Violations
    sod_agg = sod_df.groupby('business_unit').size().reset_index(name='sod_violations')
    
    # Metric C: Count & Summed Severity of Anomalies
    anomaly_agg = anomalies_df.groupby('business_unit').agg(
        anomaly_count=('anomaly_score', 'count'),
        total_anomaly_score=('anomaly_score', 'sum')
    ).reset_index()

    # 3. Compile base metrics dataframe for all business units
    risk_df = pd.DataFrame({'business_unit': BUSINESS_UNITS})
    risk_df = pd.merge(risk_df, volume_agg, on='business_unit', how='left').fillna(0)
    risk_df = pd.merge(risk_df, sod_agg, on='business_unit', how='left').fillna(0)
    risk_df = pd.merge(risk_df, anomaly_agg, on='business_unit', how='left').fillna(0)

    # 4. Normalize metrics (0 to 1 scale)
    # This prevents different ranges (e.g., thousands of transactions vs. single digit violations) 
    # from skewing the final weighted formula.
    risk_df['volume_norm'] = min_max_scale(risk_df['total_transactions'])
    risk_df['sod_norm'] = min_max_scale(risk_df['sod_violations'])
    risk_df['anomaly_norm'] = min_max_scale(risk_df['total_anomaly_score'])

    # 5. Calculate composite risk score (0 to 100 scale)
    risk_df['risk_score'] = np.round(
        (WEIGHT_SOD * risk_df['sod_norm'] + 
         WEIGHT_ANOMALY * risk_df['anomaly_norm'] + 
         WEIGHT_VOLUME * risk_df['volume_norm']) * 100, 
        2
    )

    # 6. Generate explanations and sort rankings
    risk_df['risk_explanation'] = risk_df.apply(generate_risk_explanation, axis=1)
    
    # Sort from highest risk to lowest risk
    risk_ranking = risk_df.sort_values(by='risk_score', ascending=False)
    
    # Keep only the final audit-facing columns
    output_cols = [
        'business_unit', 'total_transactions', 'sod_violations', 
        'anomaly_count', 'total_anomaly_score', 'risk_score', 'risk_explanation'
    ]
    risk_ranking = risk_ranking[output_cols]
    
    # Save to CSV
    risk_ranking.to_csv(OUTPUT_PATH, index=False)
    print(f"Successfully generated risk rankings -> {OUTPUT_PATH}")
    
    # Print leaderboard to console
    print("\n=== AuditIQ Risk Leaderboard ===")
    for rank, (_, row) in enumerate(risk_ranking.iterrows(), 1):
        print(f"{rank}. {row['business_unit']}: Risk Score = {row['risk_score']:.2f}")
        print(f"   [Metrics] Vol: {int(row['total_transactions'])}, SoD Violations: {int(row['sod_violations'])}, Anomalies: {int(row['anomaly_count'])}")
        print(f"   [Details] {row['risk_explanation']}\n")
    print("===============================\n")

def demonstrate_logistic_regression_upgrade():
    """
    Conceptual helper function demonstrating how to upgrade to a supervised 
    Logistic Regression model if labeled audit feedback data was available.
    """
    concept_code = """
    # --- Conceptual Upgrade: Supervised Logistic Regression ---
    # In a mature audit department, historical audits provide a binary label:
    # `is_confirmed_issue` (1 if the transaction was audited and found to be fraud/error, 0 otherwise).
    #
    # We would train a Logistic Regression model to estimate the probability of a transaction being a true issue:
    
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler
    
    # 1. Feature matrix (X) and label vector (y)
    # Assume we have historical audited transactions:
    # X = df[['amount', 'amount_to_threshold_ratio', 'is_weekend', 'is_round_number', 'days_since_last_same_vendor_amount', 'sod_violation_present']]
    # y = df['is_confirmed_issue']
    
    # 2. Split into train and test sets to validate model generalizability
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)
    
    # 3. Standardize features (highly recommended for Logistic Regression to aid convergence and coefficient interpretation)
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # 4. Train the model
    # We use class_weight='balanced' because fraud is highly rare (imbalanced data)
    lr_model = LogisticRegression(class_weight='balanced', random_state=42)
    lr_model.fit(X_train_scaled, y_train)
    
    # 5. Predict risk probability
    # Instead of a hard 0/1 prediction, we output probability estimates which are more useful for auditing:
    risk_probabilities = lr_model.predict_proba(X_test_scaled)[:, 1] # Probability of target class (1)
    
    # 6. Coefficient Interpretation (Explainability is critical for audit compliance)
    # Coefficients tell us the log-odds change. E.g., a coefficient of +1.5 for 'amount_to_threshold_ratio'
    # means that as a transaction gets closer to the threshold, the odds of it being a true issue increase exponentially.
    coefficients = pd.DataFrame({
        'Feature': feature_cols,
        'Coefficient': lr_model.coef_[0]
    }).sort_values(by='Coefficient', ascending=False)
    """
    pass

if __name__ == "__main__":
    calculate_risk_scores()
