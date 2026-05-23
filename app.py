import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

# Page Configuration with Professional Styling
st.set_page_config(page_title="INSTAPLAST Leave Portal", page_icon="🏭", layout="wide")

# Custom Professional Theme Colors (Insta Plast Style)
st.markdown("""
    <style>
    .stApp {
        background-color: #F8FAFC;
    }
    h1 {
        color: #1E3A8A !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-weight: 700;
    }
    .stButton>button {
        background-color: #1E3A8A !important;
        color: white !important;
        border-radius: 6px !important;
        border: none !important;
        font-weight: bold !important;
    }
    .stButton>button:hover {
        background-color: #1D4ED8 !important;
        color: white !important;
    }
    div[data-testid="stSidebarNav"] {
        background-color: #1E3A8A;
    }
    </style>
""", unsafe_allow_html=True)

# Connect to Google Sheets via st.connection
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error("Google Sheets connection error. Please check your secrets.toml file.")
    st.stop()

# Helper function to read data from Google Sheets
def load_sheet_data(worksheet_name):
    try:
        return conn.read(worksheet=worksheet_name, ttl=0)
    except Exception:
        if worksheet_name == "Worker":
            return pd.DataFrame(columns=["name", "id", "cnic", "father_name", "mobile", "salary", "joining_date", "end_date", "department", "password", "photo", "CL", "Sick", "Annual", "CO"])
        else:
            return pd.DataFrame(columns=["id", "worker", "leave_type", "days", "date_from", "date_to", "reason", "applied_on", "status"])

# Helper function to update Google Sheets directly
def save_sheet_data(df, worksheet_name):
    try:
        conn.update(worksheet=worksheet_name, data=df)
        st.success("Data synchronized with Google Sheets successfully!")
    except Exception as e:
        st.error(f"Failed to update Google Sheets: {e}")

# Load live data from Google Sheets
workers_df = load_sheet_data("Worker")
requests_df = load_sheet_data("Requests")

# Ensure IDs are strings and not floating numbers
if not workers_df.empty:
    workers_df['id'] = workers_df['id'].astype(str).str.replace(r'\.0$', '', regex=True)
if not requests_df.empty:
    requests_df['id'] = requests_df['id'].astype(str).str.replace(r'\.0$', '', regex=True)

# Application UI Header
st.markdown("<h1 style='text-align: center;'>🏭 INSTAPLAST Leave Portal</h1>", unsafe_allow_html=True)
st.markdown("---")

# Sidebar - Role Selection
st.sidebar.header("🔒 Gate Panel")
role = st.sidebar.selectbox("Select Access Role:", ["Worker", "Admin"])
st.sidebar.markdown("<br><br><small style='color: #94A3B8;'>Powered by INSTAPLAST Engine v15.1</small>", unsafe_allow_html=True)

# ----------------- WORKER DASHBOARD -----------------
if role == "Worker":
    st.subheader("📋 Worker Leave Application & Profile")
    
    worker_id_input = st.text_input("Enter your Worker ID to unlock profile (e.g., IPL-1020):").strip()
    
    if worker_id_input:
        worker_match = workers_df[workers_df['id'] == worker_id_input]
        
        if not worker_match.empty:
            worker_data = worker_match.iloc[0]
            st.success(f"Logged In Status: Active Session for '{worker_data['name']}'")
            
            # Display Balances
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("🟢 Casual Leave (CL)", f"{worker_data.get('CL', 0)} Days")
            col2.metric("🔴 Sick Leave (SL)", f"{worker_data.get('Sick', 0)} Days")
            col3.metric("🔵 Annual Leave (AL)", f"{worker_data.get('Annual', 0)} Days")
            col4.metric("🟤 Compensation (CO)", f"{worker_data.get('CO', 0)} Days")
            
            col_form, col_profile = st.columns([2, 1])
            
            with col_form:
                st.markdown("### 📝 Leave Application Form")
                leave_type = st.selectbox("Select Leave Type:", ["Casual Leave (CL)", "Sick Leave (SL)", "Annual Leave (AL)", "Compensation (CO)"])
                
                c1, c2 = st.columns(2)
                date_from = c1.date_input("Leave From:", min_value=datetime(2010, 1, 1))
                date_to = c2.date_input("Leave To:", min_value=datetime(2010, 1, 1))
                
                days_required = st.number_input("Number of Days Required:", min_value=1, value=1)
                reason = st.text_area("State Reason for Leave:")
                
                if st.button("Apply Now (Submit Request)"):
                    new_request = pd.DataFrame([{
                        "id": worker_data['id'],
                        "worker": worker_data['name'],
                        "leave_type": leave_type,
                        "days": days_required,
                        "date_from": str(date_from),
                        "date_to": str(date_to),
                        "reason": reason,
                        "applied_on": str(datetime.now().date()),
                        "status": "Pending"
                    }])
                    
                    updated_requests = pd.concat([requests_df, new_request], ignore_index=True)
                    save_sheet_data(updated_requests, "Requests")
                    st.button("Click to Refresh Panel")
            
            with col_profile:
                st.markdown("### 🌟 Worker Corporate Profile")
                st.info(f"**Name:** {worker_data['name']}\n\n**Department:** {worker_data['department']}\n\n**ID:** {worker_data['id']}\n\n**Joining Date:** {worker_data['joining_date']}")
        else:
            st.error("Worker ID not found in INSTAPLAST active records.")

# ----------------- ADMIN DASHBOARD -----------------
elif role == "Admin":
    st.subheader("⚙️ Admin Management System")
    
    menu = st.tabs(["👥 Worker Directory", "📥 Pending Requests", "➕ Add New Worker"])
    
    # Tab 1: Directory
    with menu[0]:
        st.markdown("### Active Staff Records")
        if not workers_df.empty:
            st.dataframe(workers_df, use_container_width=True)
        else:
            st.info("No worker data found in the system.")
            
    # Tab 2: Action Center for Leaves
    with menu[1]:
        st.markdown("### Manage Leave Applications")
        if not requests_df.empty:
            pending_requests = requests_df[requests_df['status'] == "Pending"]
        else:
            pending_requests = pd.DataFrame()
        
        if not pending_requests.empty:
            for idx, row in pending_requests.iterrows():
                with st.expander(f"Request from {row['worker']} ({row['id']}) for {row['days']} days of {row['leave_type']}"):
                    st.write(f"**Dates:** {row['date_from']} to {row['date_to']}")
                    st.write(f"**Reason:** {row['reason']}")
                    
                    c1, c2 = st.columns(2)
                    if c1.button("✅ Approve Request", key=f"app_{idx}"):
                        requests_df.at[idx, 'status'] = "Approved"
                        
                        w_idx = workers_df[workers_df['id'] == str(row['id'])].index
                        if len(w_idx) > 0:
                            short_type = "CL" if "Casual" in row['leave_type'] else "Sick" if "Sick" in row['leave_type'] else "Annual" if "Annual" in row['leave_type'] else "CO"
                            current_bal = pd.to_numeric(workers_df.at[w_idx[0], short_type], errors='coerce')
                            if pd.isna(current_bal):
                                current_bal = 0
                            workers_df.at[w_idx[0], short_type] = max(0, int(current_bal) - int(row['days']))
                        
                        save_sheet_data(workers_df, "Worker")
                        save_sheet_data(requests_df, "Requests")
                        st.button("Click to Update Status")
                        
                    if c2.button("❌ Reject Request", key=f"rej_{idx}"):
                        requests_df.at[idx, 'status'] = "Rejected"
                        save_sheet_data(requests_df, "Requests")
                        st.button("Click to Update Status")
        else:
            st.success("All clear! No pending leave requests found.")
            
    # Tab 3: Onboard New Staff
    with menu[2]:
        st.markdown("### Worker Registration Form")
        with st.form("add_worker_form"):
            w_name = st.text_input("Worker Full Name:")
            w_id = st.text_input("Assign Unique Worker ID (e.g. IPL-1025):")
            w_cnic = st.text_input("CNIC Number:")
            w_father = st.text_input("Father's Name:")
            w_mobile = st.text_input("Mobile Number:")
            w_salary = st.number_input("Monthly Salary (PKR):", min_value=0, value=25000)
            w_join = st.date_input("Date of Joining:", min_value=datetime(2010, 1, 1))
            w_dept = st.selectbox("Department:", ["PRODUCTION", "STORE", "QUALITY", "MAINTENANCE", "ADMIN"])
            
            # Form balances default to 0 so Admin must allocate manually
            st.markdown("#### Initial Leave Quota Allocations (Issue by Admin)")
            q_cl = st.number_input("Casual Leave Balance (CL):", min_value=0, value=0)
            q_sl = st.number_input("Sick Leave Balance (SL):", min_value=0, value=0)
            q_al = st.number_input("Annual Leave Balance (AL):", min_value=0, value=0)
            q_co = st.number_input("Compensation Leave Balance (CO):", min_value=0, value=0)
            
            submitted = st.form_submit_button("Register & Sync Worker")
            
            if submitted and w_name and w_id:
                new_worker = pd.DataFrame([{
                    "name": w_name, "id": w_id, "cnic": w_cnic, "father_name": w_father,
                    "mobile": w_mobile, "salary": w_salary, "joining_date": str(w_join),
                    "end_date": "-", "department": w_dept, "password": "123", "photo": "",
                    "CL": q_cl, "Sick": q_sl, "Annual": q_al, "CO": q_co
                }])
                
                updated_workers = pd.concat([workers_df, new_worker], ignore_index=True)
                save_sheet_data(updated_workers, "Worker")
                st.button("Click to Refresh Sheet")
