import streamlit as st
from datetime import datetime, date, timedelta
import base64
import json
import requests
import pandas as pd

# Page Setup
st.set_page_config(page_title="INSTAPLAST Leave Portal", page_icon="🏭", layout="wide")

ADMIN_PASSWORD = "admin123"  

# --- 🌐 LIVE GOOGLE APPS SCRIPT API CONFIGURATION ---
API_URL = "https://script.google.com/macros/s/AKfycbyIvA-XxT1qpezKEU2-DXze6eqEhEGtJmZIM14TbpQVzmhVpVC3pM-DEXT3XJxXNIVf/exec"
SHEET_ID = "1UjhsblmHa9UoUsbkx9-OYc98rXRcqToTJDdBAHZDciI"
GSHEET_WORKER_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Worker"
GSHEET_REQUESTS_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Requests"

# --- 📥 CLOUD DATA LOADING LOGIC ---
def load_cloud_database():
    # Initialize session states if not present
    if "workers_dict" not in st.session_state:
        st.session_state.workers_dict = {}
    if "leave_requests" not in st.session_state:
        st.session_state.leave_requests = []
    if "logged_in_user" not in st.session_state:
        st.session_state.logged_in_user = None
    if "admin_authenticated" not in st.session_state:
        st.session_state.admin_authenticated = False

    try:
        # Load Workers from Google Sheet CSV
        workers_df = pd.read_csv(GSHEET_WORKER_URL)
        if not workers_df.empty:
            temp_workers = {}
            for _, row in workers_df.iterrows():
                w_name = str(row.get('name', '')).strip()
                if w_name:
                    temp_workers[w_name] = {
                        "id": str(row.get('id', '')).replace('.0', '').strip(),
                        "cnic": str(row.get('cnic', '')).replace('.0', '').strip(),
                        "father_name": str(row.get('father_name', 'N/A')),
                        "mobile": str(row.get('mobile', 'N/A')).replace('.0', '').strip(),
                        "salary": str(row.get('salary', '0')),
                        "joining_date": str(row.get('joining_date', '')),
                        "end_date": str(row.get('end_date', '-')),
                        "department": str(row.get('department', 'STORE')),
                        "password": str(row.get('password', '123')),
                        "photo": str(row.get('photo', '')) if pd.notna(row.get('photo')) else "",
                        "CL": int(row.get('CL', 0)) if pd.notna(row.get('CL')) else 0,
                        "Sick": int(row.get('Sick', 0)) if pd.notna(row.get('Sick')) else 0,
                        "Annual": int(row.get('Annual', 0)) if pd.notna(row.get('Annual')) else 0,
                        "CO": int(row.get('CO', 0)) if pd.notna(row.get('CO')) else 0
                    }
            st.session_state.workers_dict = temp_workers

        # Load Leave Requests from Google Sheet CSV
        requests_df = pd.read_csv(GSHEET_REQUESTS_URL)
        if not requests_df.empty:
            temp_reqs = []
            for idx, row in requests_df.iterrows():
                temp_reqs.append({
                    "id": str(row.get('id', idx+1)).replace('.0', '').strip(),
                    "worker": str(row.get('worker', '')).strip(),
                    "leave_type": str(row.get('leave_type', 'CL')).strip(),
                    "days": int(row.get('days', 1)) if pd.notna(row.get('days')) else 1,
                    "date_from": str(row.get('date_from', '')),
                    "date_to": str(row.get('date_to', '')),
                    "reason": str(row.get('reason', '-')),
                    "applied_on": str(row.get('applied_on', '')),
                    "status": str(row.get('status', 'Pending')).strip()
                })
            st.session_state.leave_requests = temp_reqs
    except Exception as e:
        st.sidebar.error(f"⚠️ Live Data Fetch Notice: Connecting to Cloud...")

# --- 📤 CLOUD DATA SYNC LOGIC (POST TO APPS SCRIPT) ---
def sync_data_to_sheet(payload_data, sheet_name):
    try:
        payload = {"sheet": sheet_name, "data": payload_data}
        response = requests.post(API_URL, json=payload, headers={"Content-Type": "application/json"})
        if response.status_code == 200:
            res_json = json.loads(response.text)
            if res_json.get("status") == "success":
                st.success("✅ Google Sheet Sync Successful!")
                return True
        st.error("❌ Apps Script Sync Error.")
        return False
    except Exception as e:
        st.error(f"❌ Network Sync Error: {str(e)}")
        return False

# Trigger Cloud Fetch at Startup
load_cloud_database()

# Custom CSS for Professional UI and Fixing Logo Cutting Issue
st.html("""
<style>
    [data-testid="stHeader"] {
        display: none !important;
    }
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
    }
    .section-title {
        color: #1e3a8a;
        font-family: 'Segoe UI', Arial, sans-serif;
        font-weight: 700;
        border-bottom: 3px solid #e0a924;
        padding-bottom: 5px;
        margin-bottom: 15px;
    }
    .data-box {
        border-radius: 8px;
        padding: 20px;
        margin-top: 15px;
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
    }
</style>
""")

# Image handling functions
def get_image_base64(uploaded_file):
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        return base64.b64encode(bytes_data).decode()
    return ""

def display_worker_photo(base64_str):
    if base64_str and base64_str != "nan" and base64_str != "-":
        try:
            st.markdown(f'<img src="data:image/png;base64,{base64_str}" style="width:130px; height:130px; border-radius:50%; object-fit:cover; border:3px solid #e0a924; display:block; margin-left:auto; margin-right:auto; margin-bottom:15px;">', unsafe_allow_html=True)
        except:
            st.markdown('<div style="width:130px; height:130px; border-radius:50%; background-color:#e2e8f0; border:3px dashed #cbd5e1; display:flex; align-items:center; justify-content:center; margin-left:auto; margin-right:auto; margin-bottom:15px; color:#64748b; font-weight:bold;">No Photo</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="width:130px; height:130px; border-radius:50%; background-color:#e2e8f0; border:3px dashed #cbd5e1; display:flex; align-items:center; justify-content:center; margin-left:auto; margin-right:auto; margin-bottom:15px; color:#64748b; font-weight:bold;">No Photo</div>', unsafe_allow_html=True)

# --- TOP BAR: BRANDING ---
st.html("""
    <div style="background-color: #1e3a8a; padding: 30px 20px; border-radius: 12px; text-align: center; border-left: 8px solid #e0a924; margin-top: 10px; margin-bottom: 20px;">
        <h1 style="color: #ffffff; margin: 0; font-size: 32px; font-family: 'Segoe UI', Arial, sans-serif; font-weight: bold; line-height: 1.4; letter-spacing: 1px;">🏭 INSTAPLAST PVTLTD</h1>
        <p style="color: #f1f5f9; margin: 10px 0 0 0; font-size: 15px; font-weight: 500; opacity: 0.95;">Time Management & Leave Allocation System</p>
    </div>
""")

# Sidebar Navigation Control
st.sidebar.title("🔒 Gate Panel")
role_options = ["Worker", "Admin Portal"]
access_role = st.sidebar.selectbox("Select Access Role:", role_options)
st.sidebar.divider()
st.sidebar.caption("⚡ Powered by INSTAPLAST Engine v16.0")

is_admin_mode = "Admin" in access_role

# Helper function for details subtabs
def render_profile_subdata(w_name, data, unique_key):
    st.write("---")
    st.markdown("### 📋 Detailed Profile Modules")
    
    cb1, cb2, cb3, cb4, cb5 = st.columns(5)
    with cb1: btn_personal = st.button("👤 Personal Data", key=f"btn_p_{unique_key}", use_container_width=True)
    with cb2: btn_job = st.button("💼 Job Data", key=f"btn_j_{unique_key}", use_container_width=True)
    with cb3: btn_time = st.button("⏱️ Time Management", key=f"btn_t_{unique_key}", use_container_width=True)
    with cb4: btn_benefit = st.button("🎁 Benefit & Goals", key=f"btn_b_{unique_key}", use_container_width=True)
    with cb5: btn_payroll = st.button("💰 Payroll & Comp.", key=f"btn_pay_{unique_key}", use_container_width=True)

    state_key = f"active_tab_{unique_key}"
    if state_key not in st.session_state:
        st.session_state[state_key] = "Personal Data"

    if btn_personal: st.session_state[state_key] = "Personal Data"
    if btn_job: st.session_state[state_key] = "Job Data"
    if btn_time: st.session_state[state_key] = "Time Management"
    if btn_benefit: st.session_state[state_key] = "Benefit"
    if btn_payroll: st.session_state[state_key] = "Payroll"

    active = st.session_state[state_key]
    
    if active == "Personal Data":
        st.markdown(f"""
        <div class="data-box" style="border-left: 5px solid #3b82f6;">
            <h4 style="color:#1d4ed8;">👤 Personal Data Record</h4>
            <p><b>Full Name:</b> {w_name}</p>
            <p><b>Father's Name:</b> {data.get('father_name', 'N/A')}</p>
            <p><b>CNIC Number (System Password):</b> {data.get('cnic', 'N/A')}</p>
            <p><b>Mobile / WhatsApp:</b> {data.get('mobile', 'N/A')}</p>
        </div>
        """, unsafe_allow_html=True)
        
    elif active == "Job Data":
        st.markdown(f"""
        <div class="data-box" style="border-left: 5px solid #10b981;">
            <h4 style="color:#047857;">💼 Job Data Record</h4>
            <p><b>Worker Registry ID:</b> {data.get('id', 'N/A')}</p>
            <p><b>Department Name:</b> {data.get('department', 'STORE')}</p>
            <p><b>Official Date of Joining:</b> {data.get('joining_date', 'N/A')}</p>
            <p><b>Date of End (Contract End):</b> {data.get('end_date', 'N/A')}</p>
        </div>
        """, unsafe_allow_html=True)
        
    elif active == "Time Management":
        st.markdown(f"""
        <div class="data-box" style="border-left: 5px solid #f59e0b;">
            <h4 style="color:#b45309;">⏱️ Time Management & Attendance</h4>
            <p><b>Assigned Shift:</b> General Factory Shift</p>
            <p><b>Standard Shift Timings:</b> 08:00 AM - 05:00 PM</p>
            <p><b>Total Approved Leave Balance:</b> {int(data.get('CL', 0)) + int(data.get('Sick', 0)) + int(data.get('Annual', 0)) + int(data.get('CO', 0))} Days</p>
        </div>
        """, unsafe_allow_html=True)
        
    elif active == "Benefit":
        st.markdown(f"""
        <div class="data-box" style="border-left: 5px solid #8b5cf6;">
            <h4 style="color:#6d28d9;">🎁 Benefits, Performance & Goals</h4>
            <p><b>Performance Status:</b> Good Standing</p>
            <p><b>Medical Cover Benefits:</b> Included (Standard Factory Grade Package)</p>
        </div>
        """, unsafe_allow_html=True)
        
    elif active == "Payroll":
        st.markdown(f"""
        <div class="data-box" style="border-left: 5px solid #ec4899;">
            <h4 style="color:#be185d;">💰 Payroll & Compensation</h4>
            <p><b>Basic Monthly Salary:</b> Rs. {data.get('salary', '0')}/-</p>
            <p><b>Compensation Leave (CO) Allotment:</b> {data.get('CO', 0)} Days</p>
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# WORKER PORTAL INTERFACE
# ==========================================
if not is_admin_mode:
    st.html("<h2 class='section-title'>👤 Employee Identity Verification & Leave Application</h2>")
    
    if not st.session_state.workers_dict:
        st.warning("⚠️ No worker profiles found in the system database. Please switch to Admin Portal.")
    else:
        if st.session_state.logged_in_user is None:
            worker_list = list(st.session_state.workers_dict.keys())
            col_sel1, col_sel2 = st.columns(2)
            
            with col_sel1: 
                selected_worker = st.selectbox("Select Profile Name:", worker_list)
            with col_sel2: 
                password_input = st.text_input("Enter Password (Your CNIC Number):", type="password")
                
            if st.button("🔒 Secure Login", use_container_width=True):
                w_data = st.session_state.workers_dict[selected_worker]
                if str(password_input).strip() == str(w_data.get("cnic", "")).strip():
                    st.session_state.logged_in_user = selected_worker
                    st.success("✅ Logged in successfully!")
                    st.rerun()
                else:
                    st.error("❌ Incorrect Password. Please enter your correct CNIC number.")
        else:
            current_worker = st.session_state.logged_in_user
            
            if current_worker not in st.session_state.workers_dict:
                st.session_state.logged_in_user = None
                st.rerun()
                
            w_data = st.session_state.workers_dict[current_worker]
            
            l_out1, l_out2 = st.columns([3, 1])
            with l_out1:
                st.success(f"🔓 Logged In Status: Active Session for '{current_worker}'")
            with l_out2:
                if st.button("🚪 Log Out of System", use_container_width=True):
                    st.session_state.logged_in_user = None
                    st.rerun()
                    
            st.divider()
            
            st.html("<h3 class='section-title'>📊 Your Live Progress Dashboard</h3>")
            cl_val, sl_val = int(w_data.get("CL", 0)), int(w_data.get("Sick", 0))
            al_val, co_val = int(w_data.get("Annual", 0)), int(w_data.get("CO", 0))
            
            col_c1, col_c2, col_c3, col_c4 = st.columns(4)
            with col_c1: st.metric(label="🟢 Casual Leave (CL)", value=f"{cl_val} Days")
            with col_c2: st.metric(label="🟠 Sick Leave (SL)", value=f"{sl_val} Days")
            with col_c3: st.metric(label="🔵 Annual Leave (AL)", value=f"{al_val} Days")
            with col_c4: st.metric(label="🔴 Compensation (CO)", value=f"{co_val} Days")
            
            col_left_form, col_right_profile = st.columns([1.1, 0.9])
            
            with col_left_form:
                st.html("### 📝 Leave Application Form")
                leave_opts = ["Casual Leave (CL)", "Sick Leave (SL)", "Annual Leave (AL)", "Compensation (CO)"]
                leave_type = st.selectbox("Select Leave Type:", leave_opts)
                col_d1, col_d2 = st.columns(2)
                with col_d1: date_from = st.date_input("Leave From:", value=date.today())
                with col_d2: date_to = st.date_input("Leave To:", value=date.today())
                
                leave_days = st.number_input("Number of Days Required:", min_value=1, max_value=30, value=1)
                reason = st.text_area("State Reason for Leave:")
                
                if st.button("Apply Now (Submit Request)", use_container_width=True):
                    leave_key = "CL" if "Casual" in leave_type else "Sick" if "Sick" in leave_type else "Annual" if "Annual" in leave_type else "CO"
                    if int(w_data.get(leave_key, 0)) >= leave_days:
                        new_req = {
                            "id": str(len(st.session_state.leave_requests) + 1),
                            "worker": str(current_worker), "leave_type": str(leave_key), "days": int(leave_days),
                            "date_from": str(date_from), "date_to": str(date_to), "reason": str(reason),
                            "applied_on": str(date.today()), "status": "Pending"
                        }
                        if sync_data_to_sheet(new_req, "Requests"):
                            st.success("✅ Application submitted and synced to Cloud!")
                            st.rerun()
                    else:
                        st.error("❌ Request Rejected: Insufficient leave balance!")
                        
            with col_right_profile:
                st.html("### 🌟 Worker Corporate Profile")
                display_worker_photo(w_data.get("photo"))
                st.write(f"👤 **Name:** {current_worker}")
                st.write(f"🏭 **Department:** {w_data.get('department', 'STORE')}")
                st.write(f"🆔 **ID:** {w_data.get('id', 'N/A')}")
                
                render_profile_subdata(current_worker, w_data, "worker_view")

# ==========================================
# ADMIN PORTAL INTERFACE
# ==========================================
else:
    st.html("<h2 class='section-title'>🛠️ Admin Management Control Panel</h2>")
    
    if not st.session_state.admin_authenticated:
        admin_auth = st.text_input("Enter Admin Security Password:", type="password")
        if st.button("🔒 Verify Admin Access", use_container_width=True):
            if admin_auth == ADMIN_PASSWORD:
                st.session_state.admin_authenticated = True
                st.rerun()
            else:
                st.error("❌ Incorrect Password.")
    else:
        adm_row1, adm_row2 = st.columns([3, 1])
        with adm_row1:
            st.success("🔓 Authorized Access Status: Live Session Open")
        with adm_row2:
            if st.button("🚪 Lock Admin Panel (Log Out)", use_container_width=True):
                st.session_state.admin_authenticated = False
                st.rerun()
                
        st.divider()

        with st.container(border=True):
            admin_tab, edit_tab, requests_tab, records_tab = st.tabs([
                "👥 Register & Delete Workers", "✏️ Edit Worker Profiles", "📥 Leave Requests Queue", "📊 Complete Factory Sheets"
            ])
            
            # TAB 1: REGISTER WORKERS
            with admin_tab:
                st.html("<h4>➕ Register New Factory Worker Profile</h4>")
                col_p1, col_p2, col_p3 = st.columns(3)
                with col_p1:
                    w_id = st.text_input("Worker ID / Roll No:")
                    w_name = st.text_input("Worker Full Name:")
                    w_father = st.text_input("Father's Name:")
                with col_p2:
                    w_cnic = st.text_input("ID Card Number / CNIC:")
                    w_mobile = st.text_input("Mobile / WhatsApp Number:")
                    w_salary = st.text_input("Monthly Salary (Rs.):", value="0")
                with col_p3:
                    w_dept = st.text_input("Department Name (e.g., Production, Store):", value="STORE")
                    w_joining = st.date_input("Date of Joining Company:", value=date.today(), min_value=date(1980,1,1))
                    w_end = st.date_input("Date of End (Contract End):", value=date.today() + timedelta(days=365), min_value=date(1980,1,1))
                    w_photo = st.file_uploader("Upload Worker Photo:", type=["jpg", "jpeg", "png"])
                
                st.html("<h5>📊 Initial Leave Quota Allocation</h5>")
                col_l1, col_l2, col_l3, col_l4 = st.columns(4)
                with col_l1: cl_q = st.number_input("Casual Leave (CL):", value=0, key="reg_cl")
                with col_l2: sl_q = st.number_input("Sick Leave (SL):", value=0, key="reg_sl")
                with col_l3: al_q = st.number_input("Annual Leave (AL):", value=0, key="reg_al")
                with col_l4: co_q = st.number_input("Compensation (CO):", value=0, key="reg_co")
                
                if st.button("Save Profile & Commit Registry", use_container_width=True):
                    if w_name and w_cnic and w_id:
                        photo_b64 = get_image_base64(w_photo)
                        worker_payload = {
                            "name": str(w_name), "id": str(w_id), "cnic": str(w_cnic), "father_name": str(w_father),
                            "mobile": str(w_mobile), "salary": int(w_salary) if w_salary.isdigit() else 0,
                            "joining_date": str(w_joining), "end_date": str(w_end), "department": str(w_dept),
                            "password": str(w_cnic), "photo": str(photo_b64),
                            "CL": int(cl_q), "Sick": int(sl_q), "Annual": int(al_q), "CO": int(co_q),
                            "personal_data": "-", "job_data": "-", "compensation": "-", "time_management": "-", 
                            "benefits": "-", "payroll": "-", "performance_goals": "-", "succession": "-"
                        }
                        if sync_data_to_sheet(worker_payload, "Worker"):
                            st.success(f"💾 Profile for '{w_name}' saved permanently to Google Sheet!")
                            st.rerun()

            # TAB 2: EDIT PROFILES
            with edit_tab:
                st.html("<h4>✏️ Audit & Edit Worker Balances / Profiles</h4>")
                if st.session_state.workers_dict:
                    edit_worker_name = st.selectbox("Select Worker to Edit:", ["Select Worker"] + list(st.session_state.workers_dict.keys()))
                    if edit_worker_name != "Select Worker":
                        current_w_data = st.session_state.workers_dict[edit_worker_name]
                        
                        try: saved_end_dt = datetime.strptime(current_w_data.get("end_date", str(date.today())), '%Y-%m-%d').date()
                        except: saved_end_dt = date.today()
                            
                        col_e1, col_e2, col_e3 = st.columns(3)
                        with col_e1:
                            edit_id = st.text_input("Worker ID:", value=current_w_data.get("id", ""))
                            edit_father = st.text_input("Father Name:", value=current_w_data.get("father_name", ""))
                            edit_dept = st.text_input("Department:", value=current_w_data.get("department", "STORE"))
                        with col_e2:
                            edit_cnic = st.text_input("CNIC Number:", value=current_w_data.get("cnic", ""))
                            edit_mobile = st.text_input("Mobile Number:", value=current_w_data.get("mobile", ""))
                            edit_salary = st.text_input("Monthly Salary:", value=current_w_data.get("salary", "0"))
                        with col_e3:
                            edit_joining = st.date_input("Joining Date:", value=datetime.strptime(current_w_data.get("joining_date", str(date.today())), '%Y-%m-%d').date(), min_value=date(1980,1,1), key="ed_j")
                            edit_end = st.date_input("Date of End (Contract End):", value=saved_end_dt, min_value=date(1980,1,1), key="ed_e")
                            edit_photo = st.file_uploader("Update New Photo (Optional):", type=["jpg", "png"])
                        
                        col_eb1, col_eb2, col_eb3, col_eb4 = st.columns(4)
                        with col_eb1: edit_cl = st.number_input("Casual Leave (CL):", value=int(current_w_data.get("CL", 0)), key="e_cl")
                        with col_eb2: edit_sl = st.number_input("Sick Leave (SL):", value=int(current_w_data.get("Sick", 0)), key="e_sl")
                        with col_eb3: edit_al = st.number_input("Annual Leave (AL):", value=int(current_w_data.get("Annual", 0)), key="e_al")
                        with col_eb4: edit_co = st.number_input("Compensation (CO):", value=int(current_w_data.get("CO", 0)), key="e_co")
                        
                        st.divider()
                        
                        if st.button("Update Profile & Save Changes", use_container_width=True):
                            photo_str = get_image_base64(edit_photo) if edit_photo else current_w_data.get("photo")
                            updated_payload = {
                                "name": str(edit_worker_name), "id": str(edit_id), "cnic": str(edit_cnic), "father_name": str(edit_father),
                                "mobile": str(edit_mobile), "salary": int(edit_salary) if str(edit_salary).isdigit() else 0,
                                "joining_date": str(edit_joining), "end_date": str(edit_end), "department": str(edit_dept),
                                "password": str(edit_cnic), "photo": str(photo_str),
                                "CL": int(edit_cl), "Sick": int(edit_sl), "Annual": int(edit_al), "CO": int(edit_co),
                                "personal_data": "-", "job_data": "-", "compensation": "-", "time_management": "-", 
                                "benefits": "-", "payroll": "-", "performance_goals": "-", "succession": "-"
                            }
                            if sync_data_to_sheet(updated_payload, "Worker"):
                                st.success("✅ Changes saved and updated successfully on Google Sheet.")
                                st.rerun()

            # TAB 3: LEAVE REQUESTS QUEUE
            with requests_tab:
                st.html("<h4>📥 Incoming Leave Applications Queue</h4>")
                pending_reqs = [r for r in st.session_state.leave_requests if r["status"] == "Pending"]
                if not pending_reqs: st.info("🛋️ No pending leave applications.")
                else:
                    for req in pending_reqs:
                        with st.container(border=True):
                            st.write(f"👤 **Worker Name:** {req['worker']} | 📋 **Leave Category:** {req['leave_type']} ({req['days']} Days)")
                            st.write(f"📅 **Duration:** {req['date_from']} to {req['date_to']} | 📝 **Reason:** {req['reason']}")
                            col_app, col_rej = st.columns(2)
                            with col_app:
                                if st.button("✅ Approve Request", key=f"app_{req['id']}", use_container_width=True):
                                    if req['worker'] in st.session_state.workers_dict:
                                        st.session_state.workers_dict[req['worker']][req['leave_type']] -= int(req['days'])
                                        w_info = st.session_state.workers_dict[req['worker']]
                                        
                                        worker_payload = {
                                            "name": str(req['worker']), "id": str(w_info['id']), "cnic": str(w_info['cnic']), "father_name": str(w_info['father_name']),
                                            "mobile": str(w_info['mobile']), "salary": int(w_info['salary']) if str(w_info['salary']).isdigit() else 0,
                                            "joining_date": str(w_info['joining_date']), "end_date": str(w_info['end_date']), "department": str(w_info['department']),
                                            "password": str(w_info['password']), "photo": str(w_info['photo']),
                                            "CL": int(w_info['CL']), "Sick": int(w_info['Sick']), "Annual": int(w_info['Annual']), "CO": int(w_info['CO'])
                                        }
                                        sync_data_to_sheet(worker_payload, "Worker")
                                    
                                    req["status"] = "Approved"
                                    if sync_data_to_sheet(req, "Requests"):
                                        st.rerun()
                                        
                            with col_rej:
                                if st.button("❌ Reject Request", key=f"rej_{req['id']}", use_container_width=True):
                                    req["status"] = "Rejected"
                                    if sync_data_to_sheet(req, "Requests"):
                                        st.rerun()

            # TAB 4: COMPLETE SHEETS RECORD
            with records_tab:
                st.html("<h4>📊 Factory Workers Sheets & Search Panel</h4>")
                search_query = st.text_input("🔍 Search Worker by Name, ID or Department:", "", key="adm_search").lower()
                
                if not st.session_state.workers_dict:
                    st.info("No workers registered in the platform yet.")
                else:
                    for name, details in st.session_state.workers_dict.items():
                        match_name = search_query in name.lower()
                        match_id = search_query in str(details.get('id', '')).lower()
                        match_dept = search_query in str(details.get('department', '')).lower()
                        
                        if match_name or match_id or match_dept:
                            with st.expander(f"📋 Profile: {name} (ID: {details.get('id', 'N/A')} | Dept: {details.get('department', 'N/A')})"):
                                col_v1, col_v2, col_v3 = st.columns([0.6, 1.4, 1.4])
                                with col_v1: display_worker_photo(details.get("photo"))
                                with col_v2:
                                    st.write(f"🧔 **Father's Name:** {details.get('father_name', 'N/A')}")
                                    st.write(f"🆔 **CNIC / Password:** {details.get('cnic', 'N/A')}")
                                    st.write(f"📱 **Mobile:** {details.get('mobile', 'N/A')}")
                                with col_v3:
                                    st.write(f"🏢 **Department:** {details.get('department', 'STORE')}")
                                    st.write(f"📅 **Date of Joining:** {details.get('joining_date', 'N/A')}")
                                    st.write(f"⏳ **Date of End:** {details.get('end_date', 'N/A')}")
                                    st.write(f"💰 **Monthly Salary:** Rs. {details.get('salary', '0')}/-")
                                
                                st.write(f"**Casual (CL):** {details.get('CL', 0)} Days | **Sick (SL):** {details.get('Sick', 0)} Days | **Annual (AL):** {details.get('Annual', 0)} Days | **CO:** {details.get('CO', 0)} Days")
                                
                                render_profile_subdata(name, details, f"admin_view_{details.get('id')}")
