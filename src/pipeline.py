import pandas as pd
import os
import ast

# --- Configuration ---
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
OUTPUT_DIR = DATA_DIR

def load_and_clean_data():
    """
    Loads the three raw CSV files, performs cleaning operations, and merges them.

    Cleaning Steps:
    1.  Load `transactions.csv`, `employee_access.csv`, `vendor_master.csv`.
    2.  Standardize date formats (`date` and `registration_date`).
    3.  Correct data types (e.g., ensure 'permissions' is a list).
    4.  Handle potential missing values (though our generator creates clean data).
    5.  Merge the DataFrames into a single master table.

    Returns:
        pd.DataFrame: A cleaned and merged DataFrame ready for analysis.
    """
    print("Starting data pipeline...")

    # --- 1. Load Data ---
    try:
        transactions_path = os.path.join(DATA_DIR, "transactions.csv")
        employees_path = os.path.join(DATA_DIR, "employee_access.csv")
        vendors_path = os.path.join(DATA_DIR, "vendor_master.csv")

        transactions_df = pd.read_csv(transactions_path)
        employees_df = pd.read_csv(employees_path)
        vendors_df = pd.read_csv(vendors_path)
        print("Successfully loaded all source CSV files.")
    except FileNotFoundError as e:
        print(f"Error: {e}. Please ensure 'generate_data.py' has been run successfully.")
        return None

    # --- 2. Clean and Transform Data ---

    # Clean Transactions Data
    # Convert 'date' column to datetime objects for proper time-based analysis.
    transactions_df['date'] = pd.to_datetime(transactions_df['date'])

    # Clean Employee Data
    # The 'permissions' column is stored as a string representation of a list.
    # We use `ast.literal_eval` to safely convert it back into a Python list.
    # A try-except block handles any rows where the format might be invalid.
    def safe_literal_eval(s):
        try:
            return ast.literal_eval(s)
        except (ValueError, SyntaxError):
            return [] # Return an empty list if the string is not a valid list
    employees_df['permissions'] = employees_df['permissions'].apply(safe_literal_eval)

    # Clean Vendor Data
    # Convert 'registration_date' to datetime objects.
    vendors_df['registration_date'] = pd.to_datetime(vendors_df['registration_date'])

    print("Data cleaning and type conversion complete.")

    # --- 3. Merge DataFrames ---

    # Merge transactions with employee data on 'employee_id'
    # A left merge ensures we keep all transactions, even if an employee ID was missing.
    master_table = pd.merge(transactions_df, employees_df, on="employee_id", how="left", suffixes=('', '_employee'))

    # Merge the result with vendor data on 'vendor_id'
    master_table = pd.merge(master_table, vendors_df, on="vendor_id", how="left", suffixes=('', '_vendor'))

    # Resolve duplicate business_unit columns by keeping the transaction's business unit
    if 'business_unit_employee' in master_table.columns:
        master_table.drop(columns=['business_unit_employee'], inplace=True)
    if 'business_unit_vendor' in master_table.columns:
        master_table.drop(columns=['business_unit_vendor'], inplace=True)

    # --- 4. Handle Missing Values (Imputation) ---
    # After a left merge, unmatched keys result in NaNs. We impute them to prevent downstream errors.
    master_table['name'] = master_table['name'].fillna("UNKNOWN_EMPLOYEE")
    master_table['role'] = master_table['role'].fillna("UNKNOWN_ROLE")
    master_table['vendor_name'] = master_table['vendor_name'].fillna("UNKNOWN_VENDOR")
    master_table['risk_category'] = master_table['risk_category'].fillna("normal")
    
    # Fill empty permissions list for missing employees
    # pandas fillna doesn't easily support filling with lists directly, so we use a lambda or apply
    master_table['permissions'] = master_table['permissions'].apply(lambda x: x if isinstance(x, list) else [])

    print("Successfully merged and cleaned all data into a master table.")

    return master_table

# --- Main Execution ---
if __name__ == "__main__":
    master_table = load_and_clean_data()

    if master_table is not None:
        # Ensure output directory exists
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        # Save the master table to a new CSV
        output_path = os.path.join(OUTPUT_DIR, "master_table.csv")
        master_table.to_csv(output_path, index=False)
        
        print(f"\nPipeline complete. Master table created with {len(master_table)} rows.")
        print(f"Saved to: {output_path}")
        # print("\nColumns in master_table.csv:")
        # print(master_table.info())
