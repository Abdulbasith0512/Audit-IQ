import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os

# --- Page Configuration ---
st.set_page_config(
    page_title="AuditIQ — Audit Analytics Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Configuration ---
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
MASTER_TABLE_PATH = os.path.join(DATA_DIR, "master_table.csv")
SOD_VIOLATIONS_PATH = os.path.join(DATA_DIR, "sod_violations.csv")
ANOMALIES_PATH = os.path.join(DATA_DIR, "anomalies.csv")
BUSINESS_UNITS = ["Investment Banking", "Wealth Management", "Retail Banking", "Corporate Banking", "Global Markets"]

# --- Helper Functions ---
@st.cache_data
def load_data():
    """Loads and caches the cleaned datasets to optimize dashboard performance."""
    try:
        master_df = pd.read_csv(MASTER_TABLE_PATH)
        master_df['date'] = pd.to_datetime(master_df['date'])
        
        sod_df = pd.read_csv(SOD_VIOLATIONS_PATH)
        
        anomalies_df = pd.read_csv(ANOMALIES_PATH)
        anomalies_df['date'] = pd.to_datetime(anomalies_df['date'])
        
        return master_df, sod_df, anomalies_df
    except FileNotFoundError as e:
        st.error(f"Data files not found: {e}. Please run generate_data.py, pipeline.py, sod_engine.py, and anomaly_engine.py in order first.")
        return None, None, None

def min_max_scale(series):
    """Normalizes a series between 0 and 1. Handles zero-variance edge cases."""
    if series.max() == series.min():
        return pd.Series(0.0, index=series.index)
    return (series - series.min()) / (series.max() - series.min())

def compute_dynamic_risk(df_master, df_sod, df_anomalies, start_d, end_d):
    """
    Dynamically recalculates the composite risk score for each business unit 
    based on the selected date range.
    """
    # Filter transactional data by date range
    df_m_filtered = df_master[
        (df_master['date'].dt.date >= start_d) & 
        (df_master['date'].dt.date <= end_d)
    ]
    df_a_filtered = df_anomalies[
        (df_anomalies['date'].dt.date >= start_d) & 
        (df_anomalies['date'].dt.date <= end_d)
    ]
    
    # 1. Volume Exposure
    vol_agg = df_m_filtered.groupby('business_unit').size().reset_index(name='total_transactions')
    
    # 2. Access Control Risk (SoD) is static (system access settings)
    sod_agg = df_sod.groupby('business_unit').size().reset_index(name='sod_violations')
    
    # 3. Transactional Anomaly Risk (Count and summed severity)
    anomaly_agg = df_a_filtered.groupby('business_unit').agg(
        anomaly_count=('anomaly_score', 'count'),
        total_anomaly_score=('anomaly_score', 'sum')
    ).reset_index()
    
    # Merge metrics
    risk_df = pd.DataFrame({'business_unit': BUSINESS_UNITS})
    risk_df = pd.merge(risk_df, vol_agg, on='business_unit', how='left').fillna(0)
    risk_df = pd.merge(risk_df, sod_agg, on='business_unit', how='left').fillna(0)
    risk_df = pd.merge(risk_df, anomaly_agg, on='business_unit', how='left').fillna(0)
    
    # Normalize metrics (0 to 1)
    risk_df['volume_norm'] = min_max_scale(risk_df['total_transactions'])
    risk_df['sod_norm'] = min_max_scale(risk_df['sod_violations'])
    risk_df['anomaly_norm'] = min_max_scale(risk_df['total_anomaly_score'])
    
    # Calculate composite risk score
    # 45% SoD violations, 45% Anomalies, 10% Transaction Volume
    risk_df['risk_score'] = np.round(
        (0.45 * risk_df['sod_norm'] + 
         0.45 * risk_df['anomaly_norm'] + 
         0.10 * risk_df['volume_norm']) * 100, 
        2
    )
    
    # Assign Risk Level Label
    def get_risk_level(score):
        if score >= 60:
            return "🔴 HIGH RISK"
        elif score >= 40:
            return "🟡 MEDIUM RISK"
        else:
            return "🟢 LOW RISK"
            
    risk_df['risk_level'] = risk_df['risk_score'].apply(get_risk_level)
    
    return risk_df.sort_values(by='risk_score', ascending=False)

# --- Load Datasets ---
master_df, sod_df, anomalies_df = load_data()

if master_df is not None:
    # --- Sidebar Filters ---
    st.sidebar.markdown("<h1 style='text-align: center; margin-bottom: 0px;'>🛡️</h1>", unsafe_allow_html=True)
    st.sidebar.title("AuditIQ Controls Panel")
    st.sidebar.markdown("---")
    
    # Date Range Slider
    min_date = master_df['date'].min().date()
    max_date = master_df['date'].max().date()
    
    st.sidebar.subheader("📅 Timeframe Filter")
    date_range = st.sidebar.slider(
        "Select Date Range",
        min_value=min_date,
        max_value=max_date,
        value=(min_date, max_date),
        format="YYYY-MM-DD"
    )
    start_d, end_d = date_range
    
    # Business Unit Filter
    st.sidebar.subheader("🏢 Focus Area")
    bu_selected = st.sidebar.selectbox(
        "Select Business Unit Focus",
        ["All Business Units"] + BUSINESS_UNITS
    )
    
    # Apply date filters and calculate dynamic risk rankings
    dynamic_risk_df = compute_dynamic_risk(master_df, sod_df, anomalies_df, start_d, end_d)
    
    # Filter datasets for displays
    filtered_master = master_df[
        (master_df['date'].dt.date >= start_d) & 
        (master_df['date'].dt.date <= end_d)
    ]
    filtered_anomalies = anomalies_df[
        (anomalies_df['date'].dt.date >= start_d) & 
        (anomalies_df['date'].dt.date <= end_d)
    ]
    
    # If a specific BU is selected in the sidebar, filter the datasets further
    if bu_selected != "All Business Units":
        filtered_master = filtered_master[filtered_master['business_unit'] == bu_selected]
        filtered_anomalies = filtered_anomalies[filtered_anomalies['business_unit'] == bu_selected]
        sod_filtered = sod_df[sod_df['business_unit'] == bu_selected]
    else:
        sod_filtered = sod_df

    # --- Main Header ---
    st.title("🛡️ AuditIQ — Audit Analytics Platform")
    st.markdown(
        f"**Continuous Controls Monitoring (CCM) & Transaction Auditing Console** | "
        f"Selected range: `{start_d}` to `{end_d}`"
    )
    
    st.info(
        "💡 **About this tool:** This dashboard represents an end-to-end audit analytics system designed for "
        "detecting internal control failures. It combines static system permission scans (Segregation of Duties checking) "
        "with transaction anomaly detection (driven by an unsupervised Isolation Forest model trained on employee billing behaviors)."
    )

    # --- KPI Metric Cards ---
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            label="Total Transactions",
            value=f"{len(filtered_master):,}",
            help="Total transactions processed during the selected timeframe."
        )
    with col2:
        st.metric(
            label="SoD Access Violations",
            value=len(sod_filtered),
            delta="-5% from last audit" if len(sod_filtered) > 0 else None,
            delta_color="inverse",
            help="Number of employees holding conflicting permissions (e.g. vendor creation + payment approval)."
        )
    with col3:
        st.metric(
            label="Flagged Transaction Anomalies",
            value=len(filtered_anomalies),
            help="Transactions flagged by the Isolation Forest model as exhibiting suspicious attributes."
        )
    with col4:
        avg_risk = dynamic_risk_df['risk_score'].mean()
        st.metric(
            label="Average Risk Rating",
            value=f"{avg_risk:.1f}/100",
            help="The average normalized risk score across all active business units."
        )
        
    st.markdown("---")

    # --- Section: Leaderboard and Plotly Bar Chart ---
    left_col, right_col = st.columns([1, 1])
    
    with left_col:
        st.subheader("📊 Business Unit Risk Leaderboard")
        st.caption("Group level ranking based on composite risk score (45% SoD + 45% Anomaly + 10% Volume).")
        
        # Format and style the leaderboard
        leaderboard_display = dynamic_risk_df[[
            'business_unit', 'risk_score', 'risk_level', 
            'sod_violations', 'anomaly_count', 'total_transactions'
        ]].copy()
        
        leaderboard_display.columns = [
            "Business Unit", "Risk Score", "Risk Level", 
            "SoD Violations", "Anomalies Flagged", "Total Volume"
        ]
        
        # Color coding cell logic
        def color_risk_level(val):
            if "HIGH" in val:
                return 'background-color: #ffe6e6; color: #cc0000; font-weight: bold; border-radius: 4px;'
            elif "MEDIUM" in val:
                return 'background-color: #fff2cc; color: #b38600; font-weight: bold; border-radius: 4px;'
            elif "LOW" in val:
                return 'background-color: #e2f0d9; color: #385723; font-weight: bold; border-radius: 4px;'
            return ''
            
        styled_leaderboard = leaderboard_display.style.map(color_risk_level, subset=['Risk Level'])
        
        st.dataframe(
            styled_leaderboard,
            use_container_width=True,
            hide_index=True,
            height=218, # Set height to fit all 5 rows perfectly without scrollbar
            column_config={
                "Risk Score": st.column_config.NumberColumn("Risk Score (0-100)", format="%.2f"),
                "Total Volume": st.column_config.NumberColumn("Total Volume", format="%d")
            }
        )
        
    with right_col:
        st.subheader("📈 Risk Profiles by Department")
        st.caption("Visual breakdown of composite risk ratings (Plotly interactive charts).")
        
        # Sort values ascending for horizontal bar chart
        fig_df = dynamic_risk_df.sort_values(by='risk_score', ascending=True)
        
        fig = px.bar(
            fig_df,
            x='risk_score',
            y='business_unit',
            orientation='h',
            text='risk_score',
            color='risk_score',
            color_continuous_scale=px.colors.sequential.Reds,
            labels={'risk_score': 'Composite Risk Score (0-100)', 'business_unit': 'Business Unit'}
        )
        
        # Update layout to look sleek and modern
        fig.update_layout(
            margin=dict(l=10, r=60, t=20, b=10), # Optimized margins to fit column width
            height=220, # Matches leaderboard height perfectly
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            coloraxis_showscale=False
        )
        fig.update_xaxes(title_text="", showticklabels=True) # Hide x-axis title to save space
        fig.update_yaxes(title_text="") # Hide y-axis title to prevent overlapping and save space
        fig.update_traces(
            textposition='outside', 
            texttemplate='%{text:.1f}',
            marker_line_color='rgb(8,48,107)', 
            marker_line_width=1.5, 
            opacity=0.85
        )
        
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # --- Section: Drill-Down Details ---
    st.subheader("🔍 Departmental Audit Drill-Down Panel")
    
    # Select box to drill down on a business unit (if not already locked by sidebar)
    if bu_selected == "All Business Units":
        drill_bu = st.selectbox(
            "Select a Business Unit to inspect control exceptions:",
            BUSINESS_UNITS
        )
    else:
        st.markdown(f"Focusing drill-down tables on: **{bu_selected}** (Locked by sidebar)")
        drill_bu = bu_selected
        
    # Get filtered lists for the selected drill-down BU
    bu_sod = sod_df[sod_df['business_unit'] == drill_bu]
    bu_anomalies = filtered_anomalies[filtered_anomalies['business_unit'] == drill_bu]
    
    tab_sod, tab_anomalies, tab_all = st.tabs([
        f"🔑 Segregation of Duties ({len(bu_sod)} violations)",
        f"🚨 Flagged Anomalies ({len(bu_anomalies)} transactions)",
        "📋 Full Transaction Log"
    ])
    
    with tab_sod:
        st.markdown(f"#### Access Control Violations — {drill_bu}")
        st.write("These employees hold administrative or financial access privileges that present a Segregation of Duties conflict.")
        
        if not bu_sod.empty:
            st.dataframe(
                bu_sod[['employee_id', 'name', 'conflicting_roles', 'explanation']],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "employee_id": "Employee ID",
                    "name": "Employee Name",
                    "conflicting_roles": "Conflict Violation",
                    "explanation": "Auditing Risk Explanation"
                }
            )
        else:
            st.success("No SoD violations identified for this business unit.")
            
    with tab_anomalies:
        st.markdown(f"#### Suspicious Transaction Warnings — {drill_bu}")
        st.write("These transactions were flagged by our Isolation Forest engine as demonstrating high-risk variance across timing, amounts, limits, and velocity.")
        
        if not bu_anomalies.empty:
            # Sort anomalies by score descending
            bu_anomalies_sorted = bu_anomalies.sort_values(by='anomaly_score', ascending=False)
            
            # Format display
            disp_anom = bu_anomalies_sorted[[
                'transaction_id', 'date', 'employee_id', 'name', 
                'vendor_name', 'amount', 'approval_threshold', 
                'anomaly_score', 'reason'
            ]].copy()
            
            st.dataframe(
                disp_anom,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "transaction_id": "Txn ID",
                    "date": st.column_config.DatetimeColumn("Date/Time", format="YYYY-MM-DD HH:mm"),
                    "employee_id": "Emp ID",
                    "name": "Initiator",
                    "vendor_name": "Vendor",
                    "amount": st.column_config.NumberColumn("Amount", format="$%,.2f"),
                    "approval_threshold": st.column_config.NumberColumn("Limit", format="$%,.0f"),
                    "anomaly_score": st.column_config.ProgressColumn("Risk Score", min_value=0.0, max_value=1.0, format="%.2f"),
                    "reason": "Detection Flags & Audit Trail"
                }
            )
        else:
            st.success("No transactional anomalies flagged for this business unit in the selected timeframe.")
            
    with tab_all:
        st.markdown(f"#### Complete Audit Ledger — {drill_bu}")
        st.write("Search, filter, and review all processed transactions.")
        
        bu_master = filtered_master[filtered_master['business_unit'] == drill_bu]
        
        # Add a text input to search by vendor or employee name
        search_query = st.text_input("🔍 Search ledger by Vendor Name or Employee Name:")
        if search_query:
            bu_master = bu_master[
                bu_master['vendor_name'].str.contains(search_query, case=False, na=False) |
                bu_master['name'].str.contains(search_query, case=False, na=False)
            ]
            
        st.dataframe(
            bu_master[[
                'transaction_id', 'date', 'employee_id', 'name', 'role',
                'vendor_id', 'vendor_name', 'amount', 'approval_threshold', 'payment_method'
            ]].sort_values(by='date', ascending=False),
            use_container_width=True,
            hide_index=True,
            column_config={
                "transaction_id": "Txn ID",
                "date": st.column_config.DatetimeColumn("Timestamp", format="YYYY-MM-DD HH:mm"),
                "employee_id": "Emp ID",
                "name": "Employee Name",
                "role": "Job Role",
                "vendor_id": "Vendor ID",
                "vendor_name": "Vendor Name",
                "amount": st.column_config.NumberColumn("Amount", format="$%,.2f"),
                "approval_threshold": st.column_config.NumberColumn("Threshold", format="$%,.0f"),
                "payment_method": "Payment Method"
            }
        )
else:
    st.warning("Please ensure the data generation pipeline has run successfully to populate the CSV files.")
