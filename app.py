import streamlit as st
from datetime import datetime, date, timedelta
import base64
import json
import requests
import pandas as pd
import calendar

# Page Setup
st.set_page_config(page_title="INSTAPLAST Leave Portal", page_icon="🏭", layout="wide")

ADMIN_PASSWORD = "admin123"  

# --- 🌐 LIVE GOOGLE APPS SCRIPT API CONFIGURATION ---
API_URL = "https://script.google.com/macros/s/AKfycbyIvA-XxT1qpezKEU2-DXze6eqEhEGtJmZIM14TbpQVzmhVpVC3pM-DEXT3XJxXNIVf/exec"
SHEET_ID = "1UjhsblmHa9UoUsbkx9-OYc98rXRcqToTJDdBAHZDciI"
GSHEET_WORKER_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Worker"
GSHEET_REQUESTS_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Requests"

# --- 📥 CLOUD DATA LOADING LOGIC (With Dynamic Force Refresh Support) ---
def load_cloud_database():
    if "workers_dict" not in st.session_state:
        try:
            workers_df = pd.read_csv(GSHEET_WORKER_URL)
            temp_workers = {}
            if not workers_df.empty:
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
        except:
            st.session_state.workers_dict = {}

    if "leave_requests" not in st.session_state:
        try:
            requests_df = pd.read_csv(GSHEET_REQUESTS_URL)
            temp_reqs = []
            if not requests_df.empty:
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
        except:
            st.session_state.leave_requests = []

    if "logged_in_user" not in st.session_state:
        st.session_state.logged_in_user = None
    if "admin_authenticated" not in st.session_state:
        st.session_state.admin_authenticated = False

# --- 📤 CLOUD DATA SYNC LOGIC (POST TO APPS SCRIPT) ---
def sync_data_to_sheet(payload_data, sheet_name):
    try:
        payload = {"sheet": sheet_name, "data": payload_data}
        response = requests.post(API_URL, json=payload, headers={"Content-Type": "application/json"})
        if response.status_code == 200:
            res_json = json.loads(response.text)
            if res_json.get("status") == "success":
                return True
        st.error("❌ Apps Script Sync Error.")
        return False
    except Exception as e:
        st.error(f"❌ Network Sync Error: {str(e)}")
        return False

# Trigger Cloud Fetch at Startup
load_cloud_database()

# Custom CSS for Professional UI and Badges
st.html("""
<style>
    [data-testid="stHeader"] { display: none !important; }
    .block-container { padding-top: 2rem !important; padding-bottom: 2rem !important; }
    .section-title {
        color: #1e3a8a; font-family: 'Segoe UI', Arial, sans-serif; font-weight: 700;
        border-bottom: 3px solid #e0a924; padding-bottom: 5px; margin-bottom: 15px;
    }
    .data-box {
        border-radius: 8px; padding: 20px; margin-top: 15px; background-color: #f8fafc; border: 1px solid #e2e8f0;
    }
    .status-badge-pending { background-color: #fef3c7; color: #d97706; padding: 4px 10px; border-radius: 12px; font-weight: bold; font-size: 13px; }
    .status-badge-approved { background-color: #dcfce7; color: #15803d; padding: 4px 10px; border-radius: 12px; font-weight: bold; font-size: 13px; }
    .status-badge-rejected { background-color: #fee2e2; color: #b91c1c; padding: 4px 10px; border-radius: 12px; font-weight: bold; font-size: 13px; }
    
    /* Calendar Grid Styles */
    .calendar-grid { display: grid; grid-template-columns: repeat(7, 1fr); gap: 8px; margin-top: 15px; text-align: center; }
    .calendar-header { font-weight: bold; background-color: #1e3a8a; padding: 8px; border-radius: 4px; color: #ffffff; }
    .day-cell { padding: 12px; border-radius: 6px; font-weight: bold; border: 1px solid #cbd5e1; position: relative; min-height: 55px; }
    .day-p { background-color: #dcfce7; color: #15803d; border-color: #86efac; } /* Present */
    .day-a { background-color: #fee2e2; color: #b91c1c; border-color: #fca5a5; } /* Absent */
    .day-l { background-color: #dbeafe; color: #1e40af; border-color: #93c5fd; } /* Leave */
    .day-h { background-color: #fef3c7; color: #92400e; border-color: #fde047; } /* Hold */
    .day-empty { background-color: #f1f5f9; color: #94a3b8; border: none; }
</style>
""")

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

# --- 📆 MONTHLY CALENDAR RENDERER FUNCTION ---
def render_monthly_attendance_calendar(worker_name):
    st.html(f"<h4>📆 Monthly Attendance & Leave Grid ({datetime.now().strftime('%B %Y')})</h4>")
    
    col_legend1, col_legend2, col_legend3, col_legend4 = st.columns(4)
    with col_legend1: st.markdown("🟢 **Present (P)**: Active Workdays")
    with col_legend2: st.markdown("🔵 **Leave (L)**: Approved Factory Leaves")
    with col_legend3: st.markdown("🔴 **Absent (A)**: Unexcused / Sunday Offs")
    with col_legend4: st.markdown("🟡 **Hold (H)**: Future Calendar Days")

    # Get approved leave dates for this specific worker
    approved_dates = set()
    worker_reqs = [r for r in st.session_state.leave_requests if r["worker"].strip().lower() == worker_name.strip().lower() and r["status"] == "Approved"]
    
    for req in worker_reqs:
        try:
            start_dt = datetime.strptime(req["date_from"], "%Y-%m-%d").date()
            end_dt = datetime.strptime(req["date_to"], "%Y-%m-%d").date()
            curr = start_dt
            while curr <= end_dt:
                approved_dates.add(curr)
                curr += timedelta(days=1)
        except:
            pass

    today = date.today()
    year, month = today.year, today.month
    cal = calendar.Calendar(firstweekday=6) # Starts on Sunday
    month_days = cal.itermonthdays(year, month)
    
    days_headers = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    grid_html = '<div class="calendar-grid">'
    for day in days_headers:
        grid_html += f'<div class="calendar-header">{day}</div>'
        
    p_count, a_count, l_count, h_count = 0, 0, 0, 0
    
    for day in month_days:
        if day == 0:
            grid_html += '<div class="day-cell day-empty"></div>'
        else:
            current_loop_date = date(year, month, day)
            
            if current_loop_date in approved_dates:
                cell_class = "day-l"
                status_label = "L"
                l_count += 1
            elif current_loop_date.weekday() == 6: # Sunday Off
                cell_class = "day-a"
                status_label = "A"
                a_count += 1
            elif current_loop_date > today:
                cell_class = "day-h"
                status_label = "H"
                h_count += 1
            else:
                cell_class = "day-p"
                status_label = "P"
                p_count += 1
                
            grid_html += f'<div class="day-cell {cell_class}">{day}<br><span style="font-size:11px;">{status_label}</span></div>'
            
    grid_html += '</div>'
    st.html(grid_html)
    
    cm1, cm2, cm3, cm4 = st.columns(4)
    with cm1: st.metric("Presents (P)", f"{p_count} Days")
    with cm2: st.metric("Leaves (L)", f"{l_count} Days")
    with cm3: st.metric("Absents / Off (A)", f"{a_count} Days")
    with cm4: st.metric("Future Hold (H)", f"{h_count} Days")

# --- TOP BAR: BRANDING ---
st.html("""
    <div style="background-color: #1e3a8a; padding: 30px 20px; border-radius: 12px; text-align: center; border-left: 8px solid #e0a924; margin-top: 10px; margin-bottom: 20px;">
        <h1 style="color: #ffffff; margin: 0; font-size: 32px; font-family: 'Segoe UI', Arial, sans-serif; font-weight: bold; line-height: 1.4; letter-spacing: 1px;">🏭 INSTAPLAST PVTLTD</h1>
        <p style="color: #f1f5f9; margin: 10px 0 0 0; font-size: 15px; font-weight: 500; opacity: 0.95;">Time Management & Leave Allocation System</p>
    </div>
""")

st.sidebar.title("🔒 Gate Panel")
role_options = ["Worker", "Admin Portal"]
access_role = st.sidebar.selectbox("Select Access Role:", role_options)
st.sidebar.divider()
st.sidebar.caption("⚡ Powered by INSTAPLAST Engine v16.0")

is_admin_mode = "Admin" in access_role

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
            w_data = st.session_state.workers_dict[current_worker]
            
            l_out1, l_out2 = st.columns([3, 1])
            with l_out1: st.success(f"🔓 Logged In Status: Active Session for '{current_worker}'")
            with l_out2:
                if st.button("🚪 Log Out of System", use_container_width=True):
                    st.session_state.logged_in_user = None
                    st.rerun()
                    
            st.divider()
            
            # --- 📆 MONTHLY CALENDAR GRID ON WORKER DISPLAY ---
            with st.container(border=True):
                render_monthly_attendance_calendar(current_worker)
                
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
                            if "leave_requests" in st.session_state:
                                del st.session_state["leave_requests"]
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
            
            # --- WORKER LIVE LEAVE HISTORY SECTION ---
            st.write("---")
            st.html("<h3 class='section-title'>📝 Your Leave Applications History</h3>")
            worker_history = [r for r in st.session_state.leave_requests if r["worker"].strip().lower() == current_worker.strip().lower()]
            
            if not worker_history:
                st.info("ℹ️ You haven't submitted any leave requests yet.")
            else:
                for idx, req in enumerate(reversed(worker_history)):
                    status = req.get("status", "Pending").strip()
                    if status == "Approved": badge = f'<span class="status-badge-approved">✅ Approved</span>'
                    elif status == "Rejected": badge = f'<span class="status-badge-rejected">❌ Rejected</span>'
                    else: badge = f'<span class="status-badge-pending">⏳ Pending Admin Approval</span>'
                        
                    with st.container(border=True):
                        col_h1, col_h2 = st.columns([3, 1])
                        with col_h1:
                            st.markdown(f"**Leave Category:** {req['leave_type']} ({req['days']} Days) | **Applied On:** {req['applied_on']}")
                            st.markdown(f"📅 **Duration:** {req['date_from']} to {req['date_to']} | **Reason:** {req['reason']}")
                        with col_h2:
                            st.html(f"<div style='text-align: right; margin-top: 10px;'>{badge}</div>")

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
            else: st.error("❌ Incorrect Password.")
    else:
        adm_row1, adm_row2 = st.columns([3, 1])
        with adm_row1: st.success("🔓 Authorized Access Status: Live Session Open")
        with adm_row2:
            if st.button("🚪 Lock Admin Panel (Log Out)", use_container_width=True):
                st.session_state.admin_authenticated = False
                st.rerun()
                
        st.divider()

        with st.container(border=True):
            admin_tab, edit_tab, requests_tab, records_tab = st.tabs([
                "👥 Register & Delete Workers", "✏️ Edit Worker Profiles", "📥 Leave Requests Queue", "📊 Complete Factory Sheets"
            ])
            
            # TAB 1: REGISTER & DELETE WORKERS
            with admin_tab:
                col_reg_side, col_del_side = st.columns([1.4, 0.6])
                
                with col_reg_side:
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
                                "CL": int(cl_q), "Sick": int(sl_q), "Annual": int(al_q), "CO": int(co_q)
                            }
                            if sync_data_to_sheet(worker_payload, "Worker"):
                                if "workers_dict" in st.session_state:
                                    del st.session_state["workers_dict"]
                                st.success(f"💾 Profile saved permanently!")
                                st.rerun()
                                
                # 🔥 NEW PERMANENT DELETE MODULE 🔥
                with col_del_side:
                    st.html("<h4 style='color:#b91c1c;'>🗑️ Delete Worker Profile</h4>")
                    st.markdown("کسی بھی ورکر کو ڈیٹا بیس سے مکمل طور پر خارج کرنے کے لیے نیچے سے نام منتخب کریں:")
                    if st.session_state.workers_dict:
                        delete_target = st.selectbox("Select Profile to Remove:", ["Select Worker"] + list(st.session_state.workers_dict.keys()), key="del_tgt")
                        if delete_target != "Select Worker":
                            st.warning(f"⚠️ انتباہ: '{delete_target}' کو ڈیلیٹ کرنے سے ان کا سارا ریکارڈ فائل سے ہمیشہ کے لیے ختم ہو جائے گا۔")
                            
                            # Secure Confirmation Checkbox
                            confirm_del = st.checkbox("جی ہاں، میں اس ورکر کو مستقل حذف کرنا چاہتا ہوں۔", key="conf_del")
                            if st.button("❌ Delete Worker Permanently", use_container_width=True, disabled=not confirm_del):
                                # Payload to send delete instruction to script
                                delete_payload = {"name": str(delete_target), "action": "DELETE"}
                                if sync_data_to_sheet(delete_payload, "Worker"):
                                    # Force Reset Local Session State for Immediate UI Clearing
                                    if "workers_dict" in st.session_state:
                                        del st.session_state["workers_dict"]
                                    if "leave_requests" in st.session_state:
                                        del st.session_state["leave_requests"]
                                    st.success(f"🗑️ '{delete_target}' کا پروفائل کامیابی سے کلیئر کر دیا گیا ہے۔")
                                    st.rerun()
                    else:
                        st.info("No active profiles loaded to delete.")

            # TAB 2: EDIT PROFILES
            with edit_tab:
                st.html("<h4>✏️ Audit & Edit Worker Balances / Profiles</h4>")
                if st.session_state.workers_dict:
                    edit_worker_name = st.selectbox("Select Worker to Edit:", ["Select Worker"] + list(st.session_state.workers_dict.keys()))
                    if edit_worker_name != "Select Worker":
                        current_w_data = st.session_state.workers_dict[edit_worker_name]
                        col_e1, col_e2, col_e3 = st.columns(3)
                        with col_e1:
                            edit_id = st.text_input("Worker ID:", value=current_w_data.get("id", ""))
                            edit_father = st.text_input("Father Name:", value=current_w_data.get("father_name", ""))
                        with col_e2:
                            edit_cnic = st.text_input("CNIC Number:", value=current_w_data.get("cnic", ""))
                            edit_mobile = st.text_input("Mobile Number:", value=current_w_data.get("mobile", ""))
                        with col_e3:
                            edit_dept = st.text_input("Department:", value=current_w_data.get("department", "STORE"))
                        
                        col_eb1, col_eb2, col_eb3, col_eb4 = st.columns(4)
                        with col_eb1: edit_cl = st.number_input("Casual (CL):", value=int(current_w_data.get("CL", 0)), key="e_cl")
                        with col_eb2: edit_sl = st.number_input("Sick (SL):", value=int(current_w_data.get("Sick", 0)), key="e_sl")
                        with col_eb3: edit_al = st.number_input("Annual (AL):", value=int(current_w_data.get("Annual", 0)), key="e_al")
                        with col_eb4: edit_co = st.number_input("Compensation (CO):", value=int(current_w_data.get("CO", 0)), key="e_co")
                        
                        if st.button("Update Profile Changes", use_container_width=True):
                            updated_payload = {
                                "name": str(edit_worker_name), "id": str(edit_id), "cnic": str(edit_cnic), "father_name": str(edit_father),
                                "mobile": str(edit_mobile), "salary": int(current_w_data.get('salary', 0)),
                                "joining_date": str(current_w_data.get('joining_date', '')), "end_date": str(current_w_data.get('end_date', '')), "department": str(edit_dept),
                                "password": str(edit_cnic), "photo": str(current_w_data.get('photo', '')),
                                "CL": int(edit_cl), "Sick": int(edit_sl), "Annual": int(edit_al), "CO": int(edit_co)
                            }
                            if sync_data_to_sheet(updated_payload, "Worker"):
                                if "workers_dict" in st.session_state:
                                    del st.session_state["workers_dict"]
                                st.success("✅ Changes saved successfully.")
                                st.rerun()

            # TAB 3: LEAVE REQUESTS QUEUE (With Active Force Reset and Clear Fix)
            with requests_tab:
                st.html("<h4>📥 Incoming Leave Applications Queue</h4>")
                pending_reqs = [r for r in st.session_state.leave_requests if r["status"].strip() == "Pending"]
                
                if not pending_reqs: 
                    st.info("🛋️ No pending leave applications.")
                else:
                    for idx, req in enumerate(pending_reqs):
                        with st.container(border=True):
                            st.write(f"👤 **Worker Name:** {req['worker']} | 📋 **Leave Category:** {req['leave_type']} ({req['days']} Days)")
                            st.write(f"📅 **Duration:** {req['date_from']} to {req['date_to']} | 📝 **Reason:** {req['reason']}")
                            col_app, col_rej = st.columns(2)
                            
                            with col_app:
                                if st.button("✅ Approve Request", key=f"app_{req['id']}_{idx}", use_container_width=True):
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
                                    sync_data_to_sheet(req, "Requests")
                                    
                                    # 🔥 FORCE RESET CLEAR FOR LIVE REFRESH 🔥
                                    if "leave_requests" in st.session_state:
                                        del st.session_state["leave_requests"]
                                    if "workers_dict" in st.session_state:
                                        del st.session_state["workers_dict"]
                                        
                                    st.rerun()
                                        
                            with col_rej:
                                if st.button("❌ Reject Request", key=f"rej_{req['id']}_{idx}", use_container_width=True):
                                    req["status"] = "Rejected"
                                    sync_data_to_sheet(req, "Requests")
                                    
                                    # 🔥 FORCE RESET CLEAR FOR LIVE REFRESH 🔥
                                    if "leave_requests" in st.session_state:
                                        del st.session_state["leave_requests"]
                                    if "workers_dict" in st.session_state:
                                        del st.session_state["workers_dict"]
                                        
                                    st.rerun()

            # TAB 4: COMPLETE SHEETS RECORD & ADMIN CALENDAR VIEW
            with records_tab:
                st.html("<h4>📊 Factory Workers Sheets & Calendar Logs</h4>")
                search_query = st.text_input("🔍 Search Worker to view their Full Sheet or Calendar:", "").lower()
                
                if st.session_state.workers_dict:
                    for name, details in st.session_state.workers_dict.items():
                        if search_query in name.lower() or search_query in str(details.get('id', '')).lower():
                            with st.expander(f"📋 Profile Logs: {name} (ID: {details.get('id', 'N/A')})"):
                                render_monthly_attendance_calendar(name)
                                st.write("---")
                                render_profile_subdata(name, details, f"adm_grid_{details.get('id')}")
