import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime

# Page Configuration & Professional Theme (Insta Plast Branding)
st.set_page_config(page_title="INSTAPLAST Leave Portal", page_icon="🏭", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #F8FAFC; }
    h1, h2, h3 { color: #1E3A8A !important; font-family: 'Segoe UI', sans-serif; font-weight: 700; }
    .stButton>button { background-color: #1E3A8A !important; color: white !important; border-radius: 6px !important; font-weight: bold !important; width: 100%; }
    .stButton>button:hover { background-color: #1D4ED8 !important; }
    .balance-box { background-color: white; padding: 15px; border-radius: 8px; border-left: 5px solid #1E3A8A; box-shadow: 0 2px 4px rgba(0,0,0,0.05); text-align: center; }
    </style>
""", unsafe_allow_html=True)

# 🔴 LIVE GOOGLE APPS SCRIPT URL
API_URL = "https://script.google.com/macros/s/AKfycbyIvA-XxT1qpezKEU2-DXze6eqEhEGtJmZIM14TbpQVzmhVpVC3pM-DEXT3XJxXNIVf/exec"

# Google Sheet CSV Reading Links
SHEET_ID = "1UjhsblmHa9UoUsbkx9-OYc98rXRcqToTJDdBAHZDciI"
GSHEET_WORKER_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Worker"
GSHEET_REQUESTS_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Requests"

# --- CLOUD DATA FETCHING ---
def load_cloud_data(url, columns):
    try:
        return pd.read_csv(url)
    except Exception:
        return pd.DataFrame(columns=columns)

# --- SEND DATA TO GOOGLE SHEET ---
def send_data_to_sheet(payload_data, sheet_name):
    try:
        payload = {"sheet": sheet_name, "data": payload_data}
        response = requests.post(API_URL, json=payload, headers={"Content-Type": "application/json"})
        if response.status_code == 200 and json.loads(response.text).get("status") == "success":
            st.success("✅ Data Sync Successful!")
            return True
        else:
            st.error("❌ Apps Script Sync Error.")
            return False
    except Exception as e:
        st.error(f"❌ Network Error: {str(e)}")
        return False

# Initialize Schemas
worker_cols = ["name", "id", "cnic", "father_name", "mobile", "salary", "joining_date", "end_date", "department", "password", "photo", "CL", "Sick", "Annual", "CO", "personal_data", "job_data", "compensation", "time_management", "benefits", "payroll", "performance_goals", "succession"]
req_cols = ["id", "worker", "leave_type", "days", "date_from", "date_to", "reason", "applied_on", "status"]

workers_df = load_cloud_data(GSHEET_WORKER_URL, worker_cols)
requests_df = load_cloud_data(GSHEET_REQUESTS_URL, req_cols)

# Clean ID Strings
for df in [workers_df, requests_df]:
    if not df.empty and 'id' in df.columns:
        df['id'] = df['id'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()

# Initialize Session State for Permanent Login
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_role" not in st.session_state:
    st.session_state.user_role = None
if "user_id" not in st.session_state:
    st.session_state.user_id = None

# Header
st.markdown("<h1 style='text-align: center;'>🏭 INSTAPLAST LEAVE MANAGEMENT SYSTEM</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #64748B;'>Corporate Employee Portal</p>", unsafe_allow_html=True)
st.markdown("---")

# --- LOGOUT LOGIC ---
if st.session_state.logged_in:
    if st.sidebar.button("🚪 Logout / Sign Out"):
        st.session_state.logged_in = False
        st.session_state.user_role = None
        st.session_state.user_id = None
        st.rerun()

# --- LOGIN PANEL (IF NOT LOGGED IN) ---
if not st.session_state.logged_in:
    st.sidebar.header("🔒 Access Control Gate")
    role_selection = st.sidebar.selectbox("Select Authentication Role:", ["Worker Login", "Admin Security Login"])
    
    if role_selection == "Worker Login":
        st.subheader("👤 Worker Corporate Authentication")
        login_id = st.text_input("Enter Worker ID:", placeholder="e.g., IPL-1020").strip()
        login_cnic = st.text_input("Enter CNIC Card Number (As Password):", type="password").strip()
        
        if st.button("Unlock Worker Session"):
            if login_id and login_cnic:
                worker_match = workers_df[(workers_df['id'] == login_id) & (workers_df['cnic'].astype(str).str.strip() == login_cnic)]
                if not worker_match.empty:
                    st.session_state.logged_in = True
                    st.session_state.user_role = "Worker"
                    st.session_state.user_id = login_id
                    st.rerun()
                else:
                    st.error("❌ Invalid Worker ID or CNIC Password.")
            else:
                st.warning("⚠️ Please fill all login parameters.")

    elif role_selection == "Admin Security Login":
        st.subheader("⚙️ Administrator System Authentication")
        admin_password = st.text_input("Enter Executive Admin Password:", type="password").strip()
        
        if st.button("Unlock Admin Dashboard"):
            if admin_password == "admin123":  # Secure admin access token
                st.session_state.logged_in = True
                st.session_state.user_role = "Admin"
                st.rerun()
            else:
                st.error("❌ Access Denied. Unauthorized Security Token.")

# ----------------- LIVE SESSION WORKER DASHBOARD -----------------
elif st.session_state.logged_in and st.session_state.user_role == "Worker":
    worker_id = st.session_state.user_id
    worker_data = workers_df[workers_df['id'] == worker_id].iloc[0]
    
    st.success(f"🔓 Authorized Session: Active for '{worker_data['name']}'")
    
    # Leave Balances Visual Grid
    st.markdown("### 📊 Your Leave Balances")
    b1, b2, b3, b4 = st.columns(4)
    with b1: st.markdown(f"<div class='balance-box'><h4>Casual Leave (CL)</h4><h2>{int(worker_data.get('CL', 0))}</h2><p>Days Left</p></div>", unsafe_allow_html=True)
    with b2: st.markdown(f"<div class='balance-box'><h4>Sick Leave (SL)</h4><h2>{int(worker_data.get('Sick', 0))}</h2><p>Days Left</p></div>", unsafe_allow_html=True)
    with b3: st.markdown(f"<div class='balance-box'><h4>Annual Leave (AL)</h4><h2>{int(worker_data.get('Annual', 0))}</h2><p>Days Left</p></div>", unsafe_allow_html=True)
    with b4: st.markdown(f"<div class='balance-box'><h4>Compensation (CO)</h4><h2>{int(worker_data.get('CO', 0))}</h2><p>Days Left</p></div>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col_form, col_profile = st.columns([2, 1])
    
    with col_form:
        st.markdown("### 📝 Leave Application Form")
        leave_type = st.selectbox("Select Leave Type Category:", ["Casual Leave (CL)", "Sick Leave (SL)", "Annual Leave (AL)", "Compensation (CO)"])
        
        c1, c2 = st.columns(2)
        date_from = c1.date_input("Leave From Date:", min_value=datetime(2010, 1, 1))
        date_to = c2.date_input("Leave To Date:", min_value=datetime(2010, 1, 1))
        
        days_required = st.number_input("Total Leave Days Required:", min_value=1, value=1, step=1)
        reason = st.text_area("State Detailed Reason for Leave:")
        
        if st.button("Submit Leave Request Application"):
            new_req = {
                "id": str(worker_data['id']), "worker": str(worker_data['name']), "leave_type": str(leave_type),
                "days": int(days_required), "date_from": str(date_from), "date_to": str(date_to),
                "reason": str(reason), "applied_on": str(datetime.now().date()), "status": "Pending"
            }
            if send_data_to_sheet(new_req, "Requests"):
                st.rerun()
                
    with col_profile:
        st.markdown("### 📋 Corporate Identity Profile")
        st.info(f"""
        **Name:** {worker_data['name']}  
        **Father Name:** {worker_data['father_name']}  
        **Department:** {worker_data['department']}  
        **Date of Joining:** {worker_data['joining_date']}  
        """)

# ----------------- LIVE SESSION ADMIN DASHBOARD -----------------
elif st.session_state.logged_in and st.session_state.user_role == "Admin":
    st.subheader("⚙️ Central Admin Management Control")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "👥 Worker Directory", 
        "📥 Pending Application Requests", 
        "➕ Add New Worker Profile", 
        "✏️ Edit Worker Database"
    ])
    
    with tab1:
        st.markdown("### 🔍 Search & Filter Staff Database")
        search_query = st.text_input("Enter Worker Name or ID Number:").strip().lower()
        
        if not workers_df.empty:
            if search_query:
                filtered_df = workers_df[workers_df['name'].astype(str).str.lower().str.contains(search_query) | workers_df['id'].astype(str).str.lower().str.contains(search_query)]
                st.dataframe(filtered_df, use_container_width=True)
            else:
                st.dataframe(workers_df, use_container_width=True)
        else:
            st.info("No active corporate records found.")
            
    with tab2:
        st.markdown("### 📥 Pending Leave System Requests")
        st.caption("Note: Balance deductions trigger solely upon manual executive authorization to avoid errors.")
        
        if not requests_df.empty:
            pending_df = requests_df[requests_df['status'] == "Pending"]
            if not pending_df.empty:
                st.dataframe(pending_df, use_container_width=True)
            else:
                st.success("🎉 Executive Task Queue Empty! No pending requests found.")
        else:
            st.info("Application history logs are empty.")
            
    with tab3:
        st.markdown("### ➕ Register New Corporate Worker Profile")
        with st.form("new_worker_form"):
            
            # Form Split into Expandable Accordions per Your Requested Column Parameters
            with st.expander("👤 Personal Data", expanded=True):
                w_name = st.text_input("Worker Full Name:")
                w_father = st.text_input("Father's Name:")
                w_cnic = st.text_input("CNIC Card Identity Number:")
                w_mobile = st.text_input("Active Mobile Number:")
                
            with st.expander("💼 Job Data"):
                w_id = st.text_input("Assign Unique Worker ID Code:", placeholder="e.g., IPL-1025")
                w_dept = st.selectbox("Assign Operational Department:", ["PRODUCTION", "STORE", "QUALITY", "MAINTENANCE", "ADMIN"])
                w_join = st.date_input("Corporate Date of Joining:", min_value=datetime(2010, 1, 1))
                
            with st.expander("💰 Compensation"):
                w_salary = st.number_input("Base Monthly Salary Allocation (PKR):", min_value=0, value=25000)
                w_allowance = st.text_input("Additional Corporate Allowances Details:")
                
            with st.expander("📅 Time Management"):
                st.markdown("#### Admin Allowed Leaves Quota System")
                q_cl = st.number_input("Set Allowed Casual Leave Quota (CL):", min_value=0, value=12)
                q_sl = st.number_input("Set Allowed Sick Leave Quota (SL):", min_value=0, value=8)
                q_al = st.number_input("Set Allowed Annual Leave Quota (AL):", min_value=0, value=14)
                q_co = st.number_input("Set Allowed Compensation Quota (CO):", min_value=0, value=0)
                
            with st.expander("🏥 Benefits"):
                w_benefits = st.text_area("Corporate Employee Health & Security Benefits:")
                
            with st.expander("💳 Payroll"):
                w_payroll = st.text_input("Payroll Account Bank Structure Details / IBFT Keys:")
                
            with st.expander("📈 Performance and Goals"):
                w_performance = st.text_area("Set Departmental KPIs, Performance Records and Active Goals:")
                
            with st.expander("🔄 Succession"):
                w_succession = st.text_input("Succession Pipeline Plan / Substitute Management Profile:")

            submit_btn = st.form_submit_button("Save & Deploy New Worker Profile")
            
            if submit_btn and w_name and w_id:
                worker_payload = {
                    "name": str(w_name), "id": str(w_id), "cnic": str(w_cnic), "father_name": str(w_father),
                    "mobile": str(w_mobile), "salary": int(w_salary), "joining_date": str(w_join),
                    "end_date": "-", "department": str(w_dept), "password": "123", "photo": "",
                    "CL": int(q_cl), "Sick": int(q_sl), "Annual": int(q_al), "CO": int(q_co),
                    "personal_data": str(w_cnic), "job_data": str(w_dept), "compensation": str(w_allowance),
                    "time_management": f"CL:{q_cl},SL:{q_sl}", "benefits": str(w_benefits), 
                    "payroll": str(w_payroll), "performance_goals": str(w_performance), "succession": str(w_succession)
                }
                if send_data_to_sheet(worker_payload, "Worker"):
                    st.rerun()

    with tab4:
        st.markdown("### ✏️ Edit Existing Worker Corporate Profile Data")
        if not workers_df.empty:
            worker_list = workers_df['id'].tolist()
            selected_worker_id = st.selectbox("Select Worker ID Code to Edit Profile:", worker_list)
            
            if selected_worker_id:
                selected_worker = workers_df[workers_df['id'] == selected_worker_id].iloc[0]
                
                with st.form("edit_worker_form"):
                    st.info(f"Modifying Database Values For: {selected_worker['name']} ({selected_worker['id']})")
                    
                    edit_salary = st.number_input("Modify Base Salary Amount:", value=int(selected_worker.get('salary', 25000)))
                    edit_cl = st.number_input("Modify Allowed Casual Leave Balance (CL):", value=int(selected_worker.get('CL', 0)))
                    edit_sl = st.number_input("Modify Allowed Sick Leave Balance (SL):", value=int(selected_worker.get('Sick', 0)))
                    edit_al = st.number_input("Modify Allowed Annual Leave Balance (AL):", value=int(selected_worker.get('Annual', 0)))
                    edit_co = st.number_input("Modify Allowed Compensation Balance (CO):", value=int(selected_worker.get('CO', 0)))
                    
                    edit_comp_notes = st.text_area("Modify Compensation & Allowance Field Information:", value=str(selected_worker.get('compensation', '')))
                    edit_benefits = st.text_area("Modify Corporate Employee Benefits Profile:", value=str(selected_worker.get('benefits', '')))
                    
                    save_edit_btn = st.form_submit_button("Update & Save Structural Matrix Changes")
                    
                    if save_edit_btn:
                        updated_payload = {
                            "name": str(selected_worker['name']), "id": str(selected_worker['id']), "cnic": str(selected_worker['cnic']),
                            "father_name": str(selected_worker['father_name']), "mobile": str(selected_worker['mobile']), 
                            "salary": int(edit_salary), "joining_date": str(selected_worker['joining_date']), "end_date": "-", 
                            "department": str(selected_worker['department']), "password": "123", "photo": "",
                            "CL": int(edit_cl), "Sick": int(edit_sl), "Annual": int(edit_al), "CO": int(edit_co),
                            "personal_data": str(selected_worker.get('personal_data', '')), "job_data": str(selected_worker.get('job_data', '')),
                            "compensation": str(edit_comp_notes), "time_management": str(selected_worker.get('time_management', '')),
                            "benefits": str(edit_benefits), "payroll": str(selected_worker.get('payroll', '')),
                            "performance_goals": str(selected_worker.get('performance_goals', '')), "succession": str(selected_worker.get('succession', ''))
                        }
                        # Apps script appends or edits rows systematically via dataset matrix targets
                        if send_data_to_sheet(updated_payload, "Worker"):
                            st.rerun()
