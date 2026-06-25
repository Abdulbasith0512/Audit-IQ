import pandas as pd
import os
import ast

# --- Configuration ---
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
EMPLOYEES_PATH = os.path.join(DATA_DIR, "employee_access.csv")
OUTPUT_PATH = os.path.join(DATA_DIR, "sod_violations.csv")

# Define conflicting permission pairs and their explanations
# In internal controls, these pairs represent high-risk combinations where a single individual 
# can execute a transaction from start to finish without independent oversight.
CONFLICTING_PAIRS = {
    ("create_vendor", "approve_payment"): {
        "label": "Vendor Creation & Payment Approval",
        "explanation": "Employee holds both 'create_vendor' and 'approve_payment' permissions. This enables them to set up a fictitious vendor and approve payments to that vendor, bypassing independent review."
    },
    ("edit_invoice", "approve_payment"): {
        "label": "Invoice Edit & Payment Approval",
        "explanation": "Employee holds both 'edit_invoice' and 'approve_payment' permissions. This allows them to modify invoice details (e.g., amount or bank destination) and approve the payment, risking unauthorized funds disbursement."
    }
}

def analyze_sod_violations():
    """
    Scans the employee access records for Segregation of Duties (SoD) conflicts.
    
    Loads employee details, parses their permissions, flags individuals holding
    conflicting permission pairs, saves the results to a CSV, and prints a 
    summary count grouped by business unit.
    """
    print("Starting Segregation of Duties (SoD) check...")
    
    # 1. Load employee data
    if not os.path.exists(EMPLOYEES_PATH):
        print(f"Error: {EMPLOYEES_PATH} not found. Please run the mock data generator first.")
        return
        
    df = pd.read_csv(EMPLOYEES_PATH)
    
    # 2. Parse permissions from string representation to Python list
    def safe_parse_permissions(val):
        try:
            return ast.literal_eval(val)
        except (ValueError, SyntaxError):
            return []
            
    df['permissions'] = df['permissions'].apply(safe_parse_permissions)
    
    violations = []
    
    # 3. Scan each employee for conflicting permissions
    for _, row in df.iterrows():
        emp_perms = set(row['permissions'])
        
        # Check against each defined conflicting pair
        for conflict_pair, info in CONFLICTING_PAIRS.items():
            perm1, perm2 = conflict_pair
            if perm1 in emp_perms and perm2 in emp_perms:
                violations.append({
                    "employee_id": row['employee_id'],
                    "name": row['name'],
                    "business_unit": row['business_unit'],
                    "conflicting_roles": info["label"],  # The conflicting permissions category
                    "explanation": info["explanation"]
                })
                
    violations_df = pd.DataFrame(violations)
    
    # 4. Handle results and save to CSV
    if not violations_df.empty:
        # Save violations to CSV
        violations_df.to_csv(OUTPUT_PATH, index=False)
        print(f"Successfully generated {len(violations_df)} SoD violations -> {OUTPUT_PATH}")
        
        # 5. Print a summary count by Business Unit
        print("\n=== SoD Violations Summary by Business Unit ===")
        summary = violations_df.groupby('business_unit').size().reset_index(name='violation_count')
        summary = summary.sort_values(by='violation_count', ascending=False)
        print(summary.to_string(index=False))
        print("===============================================\n")
    else:
        # Create an empty file with columns to preserve schema
        empty_df = pd.DataFrame(columns=["employee_id", "name", "business_unit", "conflicting_roles", "explanation"])
        empty_df.to_csv(OUTPUT_PATH, index=False)
        print("No SoD violations detected. Saved empty schema to CSV.")

if __name__ == "__main__":
    analyze_sod_violations()
