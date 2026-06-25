import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta
import os

# --- Configuration ---
NUM_TRANSACTIONS = 3000
NUM_EMPLOYEES = 200
NUM_VENDORS = 100
SUSPICIOUS_TRANSACTION_PCT = 0.03
SOD_VIOLATION_PCT = 0.05
DATA_DIR = "data" # Changed to relative path for simplicity
SEED = 42

# --- Setup ---
fake = Faker()
random.seed(SEED)
np.random.seed(SEED)

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# --- Define Realistic Data Elements ---
BUSINESS_UNITS = ["Investment Banking", "Wealth Management", "Retail Banking", "Corporate Banking", "Global Markets"]
PAYMENT_METHODS = ["Wire Transfer", "ACH", "Credit Card", "Check"]
ROLES = {
    "Analyst": ["create_invoice", "view_reports"],
    "Manager": ["approve_payment", "view_reports", "edit_invoice"],
    "Director": ["approve_payment", "create_vendor", "view_reports"],
    "Clerk": ["create_invoice", "data_entry"],
    "IT Admin": ["manage_users", "system_backup"]
}
ALL_PERMISSIONS = list(set(p for permissions in ROLES.values() for p in permissions))
CONFLICTING_PAIRS = [
    ("create_vendor", "approve_payment"),
    ("edit_invoice", "approve_payment")
]

# --- 1. Generate vendor_master.csv ---
def generate_vendors():
    """Generates a DataFrame of vendors."""
    vendors = []
    for i in range(1, NUM_VENDORS + 1):
        vendors.append({
            "vendor_id": f"V{i:04d}",
            "vendor_name": fake.company(),
            "business_unit": random.choice(BUSINESS_UNITS),
            "registration_date": fake.date_between(start_date="-3y", end_date="today"),
            "risk_category": "high" if random.random() < 0.1 else "normal" # 10% high risk
        })
    return pd.DataFrame(vendors)

# --- 2. Generate employee_access.csv ---
def generate_employees():
    """Generates a DataFrame of employees, injecting SoD violations."""
    employees = []
    employee_ids = [f"E{i:04d}" for i in range(1, NUM_EMPLOYEES + 1)]
    
    # Select employees to have SoD violations
    sod_violation_count = int(NUM_EMPLOYEES * SOD_VIOLATION_PCT)
    sod_violation_indices = np.random.choice(NUM_EMPLOYEES, sod_violation_count, replace=False)

    for i, emp_id in enumerate(employee_ids):
        role_name = random.choice(list(ROLES.keys()))
        permissions = ROLES[role_name][:] # Make a copy

        if i in sod_violation_indices:
            # Inject a conflict
            conflict_to_add = random.choice(CONFLICTING_PAIRS)
            permissions.extend(conflict_to_add)
            permissions = list(set(permissions)) # Remove duplicates

        employees.append({
            "employee_id": emp_id,
            "name": fake.name(),
            "business_unit": random.choice(BUSINESS_UNITS),
            "role": role_name,
            "permissions": permissions
        })
    return pd.DataFrame(employees)

# --- 3. Generate transactions.csv ---
def generate_transactions(employee_ids, vendor_ids):
    """Generates a DataFrame of transactions, injecting suspicious activities."""
    transactions = []
    
    suspicious_indices = np.random.choice(NUM_TRANSACTIONS, int(NUM_TRANSACTIONS * SUSPICIOUS_TRANSACTION_PCT), replace=False)
    
    # Pre-generate some duplicate combos to inject
    duplicate_combos = []
    for _ in range(len(suspicious_indices) // 3): # Use 1/3 of suspicious slots for duplicates
        vendor = random.choice(vendor_ids)
        amount = round(np.random.uniform(1000, 20000), 2)
        date1 = fake.date_time_between(start_date="-1y", end_date="now")
        date2 = date1 + timedelta(days=random.randint(1, 2))
        duplicate_combos.append({"vendor_id": vendor, "amount": amount, "date": date1})
        duplicate_combos.append({"vendor_id": vendor, "amount": amount, "date": date2})

    suspicious_slot = 0
    for i in range(NUM_TRANSACTIONS):
        is_suspicious = i in suspicious_indices
        
        # Base transaction data
        threshold = random.choice([1000, 5000, 10000, 50000])
        amount = round(np.random.exponential(scale=threshold/5) * random.uniform(0.5, 1.5), 2)
        amount = min(amount, threshold * 1.5) # Cap amount
        date = fake.date_time_between(start_date="-1y", end_date="now")
        vendor_id_choice = random.choice(vendor_ids)

        # Inject suspicious data
        if is_suspicious:
            suspicious_type = random.choice(["threshold", "weekend", "duplicate"])
            
            if suspicious_type == "threshold":
                amount = threshold - round(random.uniform(1, 100), 2)
            
            elif suspicious_type == "weekend":
                # Force date to be a weekend
                days_to_saturday = (5 - date.weekday() + 7) % 7
                weekend_date = date + timedelta(days=days_to_saturday + random.randint(0, 1))
                # Set time to be off-hours
                date = weekend_date.replace(hour=random.choice([2, 3, 22, 23]), minute=random.randint(0, 59))

            elif suspicious_type == "duplicate" and duplicate_combos:
                combo = duplicate_combos.pop()
                vendor_id_choice = combo["vendor_id"]
                amount = combo["amount"]
                date = combo["date"]
        
        transactions.append({
            "transaction_id": f"T{i:05d}",
            "date": date,
            "vendor_id": vendor_id_choice,
            "employee_id": random.choice(employee_ids),
            "amount": amount,
            "business_unit": random.choice(BUSINESS_UNITS),
            "approval_threshold": threshold,
            "payment_method": random.choice(PAYMENT_METHODS)
        })

    return pd.DataFrame(transactions)

# --- Main Execution ---
if __name__ == "__main__":
    print("Starting mock data generation...")

    # Generate DataFrames
    vendors_df = generate_vendors()
    employees_df = generate_employees()
    transactions_df = generate_transactions(
        employee_ids=employees_df["employee_id"].tolist(),
        vendor_ids=vendors_df["vendor_id"].tolist()
    )

    # Save to CSV
    vendors_df.to_csv(os.path.join(DATA_DIR, "vendor_master.csv"), index=False)
    print(f"Successfully generated {len(vendors_df)} vendors -> {DATA_DIR}/vendor_master.csv")

    employees_df.to_csv(os.path.join(DATA_DIR, "employee_access.csv"), index=False)
    print(f"Successfully generated {len(employees_df)} employees -> {DATA_DIR}/employee_access.csv")

    transactions_df.to_csv(os.path.join(DATA_DIR, "transactions.csv"), index=False)
    print(f"Successfully generated {len(transactions_df)} transactions -> {DATA_DIR}/transactions.csv")

    print("\nData generation complete.")
