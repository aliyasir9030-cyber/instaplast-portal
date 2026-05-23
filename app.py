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
    .login-container { background-color: white; padding: 25px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 30px; border: 1px solid #E2E8F0; }
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

# Clean ID Strings and Drop Duplicates to ensure uniqueness
if not workers_df.empty and 'id' in workers_df.columns:
    workers_df['id'] = workers_df['id'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
    workers_df = workers_df.drop_duplicates(subset=['id'], keep='last')

if not requests_df.empty and 'id' in requests_df.columns:
    requests_df['id'] = requests_df['id'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()

# Initialize Session State for Permanent Login
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_role" not in st.session_state:
    st.session_state.user_role = None
if "user_id" not in st.session_state:
    st.session_state.user_id = None

# Main Dashboard Header
st.markdown("<h1 style='text-align: center;'>🏭 INSTAPLAST LEAVE MANAGEMENT SYSTEM</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #64748B;'>Corporate Employee Portal</p>", unsafe_allow_html=True)
st.markdown("---")

# --- GLOBAL LOGOUT BUTTON (If anyone is logged in) ---
if st.session_state.logged_in:
    if st.sidebar.button("🚪 Logout / Sign Out"):
        st.session_state.logged_in = False
        st.session_state.user_role = None
        st.session_state.user_id = None
        st.rerun()

# --- MAIN DASHBOARD: BOTH GATEWAYS VISIBLE TOGETHER ON SINGLE SCREEN ---
if not st.session_state.logged_in:
    
    # 1. WORKER LOGIN GATEWAY (Top Section)
    st.markdown("<div class='login-container'>", unsafe_allow_html=True)
    st.subheader("👤 Worker Corporate Authentication")
    col_w1, col_w2 = st.columns(2)
    login_id = col_w1.text_input("Enter Worker ID:", placeholder="e.g., IPL-1020").strip()
    login_cnic = col_w2.text_input("Enter CNIC Card Number (As Password):", type="password").strip()
    
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
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 2. ADMIN LOGIN GATEWAY (Bottom Section on same page)
    st.markdown("<div class='login-container'>", unsafe_allow_html=True)
    st.subheader("⚙️ Administrator System Authentication")
    admin_password = st.text_input("Enter Executive Admin Password:", type="password", key="admin_pass_field").strip()
    
    if st.button("Unlock Admin Dashboard"):
        if admin_password == "admin123":
            st.session_state.logged_in = True
            st.session_state.user_role = "Admin"
            st.rerun()
        else:
            st.error("❌ Access Denied. Unauthorized Security Token.")
    st.markdown("</div>", unsafe_allow_html=True)

# ----------------- LIVE SESSION: WORKER PORTAL -----------------
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
    
    col_form, col_profile = st.columns([1, 1])
    
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
        st.markdown("### 📋 Complete Worker Corporate Profile")
        
        # Displaying requested 8 column categories transparently in worker view
        with st.expander("👤 Personal Data", expanded=True):
            st.write(f"**Full Name:** {worker_data.get('name', '-')}")
            st.write(f"**Father Name:** {worker_data.get('father_name', '-')}")
            st.write(f"**CNIC Number:** {worker_data.get('cnic', '-')}")
            st.write(f"**Mobile Contact:** {worker_data.get('mobile', '-')}")
            st.write(f"**Other Personal Info:** {worker_data.get('personal_data', '-')}")
            
        with st.expander("💼 Job Data"):
            st.write(f"**Worker ID Code:** {worker_data.get('id', '-')}")
            st.write(f"**Assigned Department:** {worker_data.get('department', '-')}")
            st.write(f"**Date of Joining:** {worker_data.get('joining_date', '-')}")
            st.write(f"**Job Metadata:** {worker_data.get('job_data', '-')}")
            
        with st.expander("💰 Compensation"):
            st.write(f"**Base Salary:** PKR {worker_data.get('salary', '-')}")
            st.write(f"**Allowances Details:** {worker_data.get('compensation', '-')}")
            
        with st.expander("📅 Time Management"):
            st.write(f"**Active Leave Structural Allocation Matrix:** {worker_data.get('time_management', '-')}")
            
        with st.expander("🏥 Benefits"):
            st.write(f"**Employee Health & Security Security Cover:** {worker_data.get('benefits', '-')}")
            
        with st.expander("💳 Payroll"):
            st.write(f"**Bank Account Channels / IBFT:** {worker_data.get('payroll', '-')}")
            
        with st.expander("📈 Performance and Goals"):
            st.write(f"**Target KPIs and Goal Records:** {worker_data.get('performance_goals', '-')}")
            
        with st.expander("🔄 Succession"):
            st.write(f"**Succession Management Strategy Map:** {worker_data.get('succession', '-')}")

# ----------------- LIVE SESSION: ADMIN DASHBOARD -----------------
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
            
            with st.expander("👤 Personal Data", expanded=True):
                w_name = st.text_input("Worker Full Name:")
                w_father = st.text_input("Father's Name:")
                w_cnic = st.text_input("CNIC Card Identity Number:")
                w_mobile = st.text_input("Active Mobile Number:")
                w_personal_extra = st.text_input("Additional Personal Notes:")
                
            with st.expander("💼 Job Data"):
                w_id = st.text_input("Assign Unique Worker ID Code:", placeholder="e.g., IPL-1025")
                # 🛠️ FIXED: Dropdown replaced with Manual Text Entry for custom items like POWER HOUSE
                w_dept = st.text_input("Enter Department Name (e.g., POWER HOUSE, STORE, PRODUCTION):")
                w_join = st.date_input("Corporate Date of Joining:", min_value=datetime(2010, 1, 1))
                w_job_extra = st.text_input("Additional Job Description Details:")
                
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
                    "personal_data": str(w_personal_extra), "job_data": str(w_job_extra), "compensation": str(w_allowance),
                    "time_management": f"CL:{q_cl},SL:{q_sl},AL:{q_al},CO:{q_co}", "benefits": str(w_benefits), 
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
                    
                    edit_dept = st.text_input("Modify Department:", value=str(selected_worker.get('department', '')))
                    edit_salary = st.number_input("Modify Base Salary Amount:", value=int(selected_worker.get('salary', 25000)))
                    edit_cl = st.number_input("Modify Allowed Casual Leave Balance (CL):", value=int(selected_worker.get('CL', 0)))
                    edit_sl = st.number_input("Modify Allowed Sick Leave Balance (SL):", value=int(selected_worker.get('Sick', 0)))
                    edit_al = st.number_input("Modify Allowed Annual Leave Balance (AL):", value=int(selected_worker.get('Annual', 0)))
                    edit_co = st.number_input("Modify Allowed Compensation Balance (CO):", value=int(selected_worker.get('CO', 0)))
                    
                    edit_personal_extra = st.text_input("Modify Personal Data Extra:", value=str(selected_worker.get('personal_data', '')))
                    edit_job_extra = st.text_input("Modify Job Data Extra:", value=str(selected_worker.get('job_data', '')))
                    edit_comp_notes = st.text_area("Modify Compensation & Allowance Field Information:", value=str(selected_worker.get('compensation', '')))
                    edit_benefits = st.text_area("Modify Corporate Employee Benefits Profile:", value=str(selected_worker.get('benefits', '')))
                    edit_payroll = st.text_input("Modify Payroll Details:", value=str(selected_worker.get('payroll', '')))
                    edit_performance = st.text_area("Modify Performance goals:", value=str(selected_worker.get('performance_goals', '')))
                    edit_succession = st.text_input("Modify Succession fields:", value=str(selected_worker.get('succession', '')))
                    
                    save_edit_btn = st.form_submit_button("Update & Save Structural Matrix Changes")
                    
                    if save_edit_btn:
                        updated_payload = {
                            "name": str(selected_worker['name']), "id": str(selected_worker['id']), "cnic": str(selected_worker['cnic']),
                            "father_name": str(selected_worker['father_name']), "mobile": str(selected_worker['mobile']), 
                            "salary": int(edit_salary), "joining_date": str(selected_worker['joining_date']), "end_date": "-", 
                            "department": str(edit_dept), "password": "123", "photo": "",
                            "CL": int(edit_cl), "Sick": int(edit_sl), "Annual": int(edit_al), "CO": int(edit_co),
                            "personal_data": str(edit_personal_extra), "job_data": str(edit_job_extra), "compensation": str(edit_comp_notes), 
                            "time_management": f"CL:{edit_cl},SL:{edit_sl},AL:{edit_al},CO:{edit_co}", "benefits": str(edit_benefits), 
                            "payroll": str(edit_payroll), "performance_goals": str(edit_performance), "succession": str(edit_succession)
                        }
                        if send_data_to_sheet(updated_payload, "Worker"):
                            st.rerun()
