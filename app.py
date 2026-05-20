import streamlit as st
from datetime import datetime, date
import calendar
import pandas as pd

# Page setup and clean corporate theme alignment
st.set_page_config(page_title="Gaironova - INSTAPLAST Leave Portal", page_icon="🏭", layout="wide")

# Custom CSS matching the clean, flat UI of your company screenshots
st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(135deg, #1E3A8A 0%, #0284C7 100%);
        padding: 25px;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        margin-bottom: 25px;
    }
    div[data-testid="stMetricSimpleValue"] {
        font-size: 22px !important;
        font-weight: bold !important;
        color: #1E3A8A !important;
    }
    .profile-card {
        background-color: #F8FAFC;
        padding: 22px;
        border-radius: 10px;
        border-left: 6px solid #1E3A8A;
        box-shadow: 0 2px 6px rgba(0,0,0,0.04);
    }
    .notification-box {
        background-color: #F0FDF4;
        border-left: 5px solid #16A34A;
        padding: 12px 16px;
        margin: 6px 0;
        border-radius: 6px;
        font-size: 14px;
    }
    </style>
""", unsafe_allow_html=True)

# 1. Database Initialization (Updated with Gaironova leave structures and required service dates)
if 'workers_list' not in st.session_state:
    st.session_state.workers_list = [
        {
            "id": "IP-1022",
            "cnic": "42101-1234567-1",
            "name": "Muhammad Raza-ul-Mustafa",
            "f_name": "Ghulam Mustafa",
            "dept": "Utilities (Electrical & Instrumentation)",
            "shift": "G28SHIFT",
            "doj": "2020-03-15",
            "dor": "2045-08-12",
            "role": "Worker",
            "basic_salary": 45000.0,
            "balances": {"annual_m": 8.0, "annual_nm": 9.0, "casual": 8.5, "compensatory": 4.0},
            "attendance": {5: "Annual Leave (M)"} 
        },
        {
            "id": "IP-1023",
            "cnic": "42101-7654321-3",
            "name": "Ali Ahmed",
            "f_name": "Ahmed Khan",
            "dept": "Production",
            "shift": "A-SHIFT",
            "doj": "2022-06-01",
            "dor": "2050-01-10",
            "role": "Worker",
            "basic_salary": 38000.0,
            "balances": {"annual_m": 10.0, "annual_nm": 6.0, "casual": 12.0, "compensatory": 2.0},
            "attendance": {15: "Without Pay"}
        }
    ]

if 'notifications' not in st.session_state:
    st.session_state.notifications = [
        "📢 Muhammad Raza-ul-Mustafa applied for Annual Leave (M) on the 5th of this month.",
        "📢 Ali Ahmed applied for Unpaid Leave (Without Pay) on the 15th of this month."
    ]

DEPARTMENTS = [
    "Utilities (Electrical & Instrumentation)", "Production", "Mechanical", 
    "HR / Admin", "Quality Control", "Store / Logistics", "Finishing & Packing"
]

# 2. Sidebar Portal Gate
st.sidebar.markdown("<h2 style='text-align: center; color: #1E3A8A;'>🔒 INSTAPLAST<br>Gate Panel</h2>", unsafe_allow_html=True)
st.sidebar.write("---")
user_role = st.sidebar.selectbox("Select Access Role", ["Worker", "Admin"])

is_admin_authenticated = False

if user_role == "Admin":
    admin_password = st.sidebar.text_input("Enter Admin Access Token", type="password")
    if admin_password == "insta123":
        is_admin_authenticated = True
        st.sidebar.success("🔑 System Authentication Successful!")
    elif admin_password != "":
        st.sidebar.error("❌ Access Denied! Invalid Key Credentials.")

# --- System Brand Banner ---
st.markdown("""
    <div class="main-header">
        <h1 style="color:white; margin:0; font-family: 'Arial', sans-serif; font-weight:700; letter-spacing: 1px;">🏭 INSTAPLAST PVT LTD</h1>
        <p style="color:#E0F2FE; margin:6px 0 0 0; font-size:16px; font-weight: 400;">Gaironova Time Management & Leave Allocation System</p>
    </div>
""", unsafe_allow_html=True)

# --- Live Notification Logs ---
st.markdown("<h4 style='color: #0284C7; font-weight:600;'>🔔 System Broadcast Dashboard</h4>", unsafe_allow_html=True)
if st.session_state.notifications:
    for note in reversed(st.session_state.notifications[-5:]):
        st.markdown(f"<div class='notification-box'>{note}</div>", unsafe_allow_html=True)
else:
    st.info("Log Stream Clear. No active leave operations recorded.")
st.write("---")


# --- Worker Session Mode ---
if user_role == "Worker":
    worker_names = [w['name'] for w in st.session_state.workers_list]
    
    if not worker_names:
        st.warning("Data Synchronization Error: No profiles detected.")
    else:
        st.markdown("<h4 style='color: #1E3A8A;'>👤 Employee Identity Verification</h4>", unsafe_allow_html=True)
        col_log1, col_log2 = st.columns(2)
        selected_worker_name = col_log1.selectbox("Select Profile Username:", worker_names)
        input_cnic = col_log2.text_input("Enter Identity Token (CNIC without dashes):", type="password")
        
        worker_data = next((w for w in st.session_state.workers_list if w['name'] == selected_worker_name), None)
        
        if worker_data and input_cnic == worker_data["cnic"]:
            st.success(f"🔓 Session Authorized. Authorized Profile: {worker_data['name']}")
            st.write("---")
            
            col1, col2 = st.columns([1.2, 2.0])
            
            with col1:
                st.markdown("<h4 style='color: #1E3A8A; font-weight:600;'>👤 Employee Profile Metrics</h4>", unsafe_allow_html=True)
                st.markdown(f"""
                <div class="profile-card">
                    <p style="margin:6px 0;"><b>Full Name:</b> {worker_data['name']}</p>
                    <p style="margin:6px 0;"><b>Father's Name:</b> {worker_data.get('f_name', '---')}</p>
                    <p style="margin:6px 0;"><b>Identity (CNIC):</b> {worker_data['cnic']}</p>
                    <p style="margin:6px 0;"><b>Worker ID:</b> {worker_data['id']}</p>
                    <p style="margin:6px 0;"><b>Department:</b> {worker_data['dept']}</p>
                    <p style="margin:6px 0;"><b>Current Shift:</b> {worker_data['shift']}</p>
                    <p style="margin:6px 0; color:#0284C7;"><b>Date of Joining (DOJ):</b> {worker_data.get('doj', '---')}</p>
                    <p style="margin:6px 0; color:#EF4444;"><b>Date of Retirement (DOR):</b> {worker_data.get('dor', '---')}</p>
                </div>
                """, unsafe_allow_html=True)
                
                st.write("")
                st.markdown("<h4 style='color: #1E3A8A; font-weight:600;'>📅 Current Month Attendance Ledger</h4>", unsafe_allow_html=True)
                today = date.today()
                num_days = calendar.monthrange(today.year, today.month)[1]
                
                card_data = []
                for day in range(1, num_days + 1):
                    current_date = date(today.year, today.month, day)
                    day_name = current_date.strftime("%A")
                    
                    if day_name == "Sunday":
                        status = "🔴 Weekly Off"
                    else:
                        status = worker_data.get("attendance", {}).get(day, "🟢 Present")
                        
                    card_data.append({"Date": f"{day}/{today.month}", "Day": day_name, "Status": status})
                    
                st.dataframe(card_data, use_container_width=True, height=250)
            
            with col2:
                st.markdown("<h4 style='color: #0D9488; font-weight:600;'>📊 Leave Account Balances (Gaironova Matrix)</h4>", unsafe_allow_html=True)
                st.write("")
                b = worker_data["balances"]
                
                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    st.metric("Annual Leave (M)", f"{b.get('annual_m', 0.0)} Days")
                with c2:
                    st.metric("Annual Leave (NM)", f"{b.get('annual_nm', 0.0)} Days")
                with c3:
                    st.metric("Casual Leave", f"{b.get('casual', 0.0)} Days")
                with c4:
                    st.metric("Compensatory Leave", f"{b.get('compensatory', 0.0)} Days")

                st.write("---")
                
                st.markdown("<h4 style='color: #1E3A8A; font-weight:600;'>📝 Time Off Application Form</h4>", unsafe_allow_html=True)
                leave_options = ["Paid Leave Channel", "Unpaid Leave Channel (Without Pay)"]
                selected_pay_type = st.radio("Select Processing Channel:", leave_options, horizontal=True)
                
                leave_type = "Without Pay"
                if selected_pay_type == "Paid Leave Channel":
                    leave_type = st.selectbox("Select Certified Time Off Type:", [
                        "Annual Leave (M)", 
                        "Annual Leave (NM)", 
                        "Casual Leave", 
                        "Compensatory Leave"
                    ])
                
                col_d1, col_d2 = st.columns(2)
                start_date = col_d1.date_input("Start Operation Date")
                end_date = col_d2.date_input("Terminating Operation Date")
                
                if st.button("🚀 Process Time Off Submission", use_container_width=True):
                    if end_date >= start_date:
                        days_requested = (end_date - start_date).days + 1
                        
                        def apply_attendance_dates():
                            if "attendance" not in worker_data:
                                worker_data["attendance"] = {}
                            for d in range(start_date.day, min(end_date.day + 1, num_days + 1)):
                                worker_data["attendance"][d] = f"⚠️ {leave_type}"
                        
                        if selected_pay_type == "Unpaid Leave Channel (Without Pay)":
                            apply_attendance_dates()
                            st.session_state.notifications.append(f"⚠️ Employee {worker_data['name']} submitted Unpaid Leave from day {start_date.day} to {end_date.day} ({days_requested} Days).")
                            st.success(f"Success: Unpaid Leave window ({days_requested} Days) registered in live track.")
                            st.rerun()
                        else:
                            map_leave = {
                                "Annual Leave (M)": "annual_m", 
                                "Annual Leave (NM)": "annual_nm", 
                                "Casual Leave": "casual", 
                                "Compensatory Leave": "compensatory"
                            }
                            b_key = map_leave[leave_type]
                            
                            if worker_data["balances"].get(b_key, 0.0) >= days_requested:
                                worker_data["balances"][b_key] -= days_requested
                                apply_attendance_dates()
                                st.session_state.notifications.append(f"⚠️ Employee {worker_data['name']} submitted Paid {leave_type} from day {start_date.day} to {end_date.day} ({days_requested} Days).")
                                st.success(f"Success: Balance deduction adjusted. Total Days: {days_requested}")
                                st.balloons()
                                st.rerun()
                            else:
                                st.error(f"Quota Insufficient: Your requested allowance exceeds available {leave_type} credits. Please process under Unpaid Channel.")
                    else:
                        st.error("Timeline Validation Error: Terminating date cannot precede starting operational date.")
        elif input_cnic != "":
            st.error("❌ Authentication Refused: Identity mismatch with profile username.")
        else:
            st.info("🔒 Secure Directory: Provide identity verification token to pull company records.")

# --- Admin Controller Session Mode ---
elif user_role == "Admin" and is_admin_authenticated:
    st.markdown("<h3 style='color: #1E3A8A; font-weight:600;'>🛠️ Enterprise Admin Control Center</h3>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["👥 Workforce Management & Authorization", "📋 Master Leave Balances Registry", "📊 Financial Payroll Compensation Sheet"])
    
    with tab1:
        col_admin1, col_admin2 = st.columns(2)
        
        with col_admin1:
            st.markdown("<h4 style='color: #0D9488;'>➕ Onboard New Workforce Profile</h4>", unsafe_allow_html=True)
            with st.form("add_form", clear_on_submit=True):
                w_id = st.text_input("Assign Enterprise Worker ID")
                w_cnic = st.text_input("Identity Card Token (CNIC - System Password)")
                w_name = st.text_input("Employee Full Legal Name")
                w_fname = st.text_input("Father's / Guardian Name")
                w_dept = st.selectbox("Assign Segment Division", DEPARTMENTS)
                w_shift = st.text_input("Operational Shift Class")
                
                # Date of Joining & Retirement Additions
                col_date1, col_date2 = st.columns(2)
                w_doj = col_date1.text_input("Date of Joining (YYYY-MM-DD)", value=str(date.today()))
                w_dor = col_date2.text_input("Date of Retirement (YYYY-MM-DD)", value="2050-01-01")
                
                w_salary = st.number_input("Base Compensation Salary Scale", min_value=0.0, step=1000.0, value=25000.0)
                
                st.markdown("<p style='color:#1E3A8A; font-weight:bold; margin-top:15px;'>📋 Set Gaironova Annual Leave Entitlements:</p>", unsafe_allow_html=True)
                col_l1, col_l2 = st.columns(2)
                allow_am = col_l1.number_input("Annual Leave (M) Limit", min_value=0.0, value=8.0)
                allow_anm = col_l2.number_input("Annual Leave (NM) Limit", min_value=0.0, value=9.0)
                allow_casual = col_l1.number_input("Casual Leave Limit", min_value=0.0, value=8.5)
                allow_comp = col_l2.number_input("Compensatory Leave Limit", min_value=0.0, value=4.0)
                
                if st.form_submit_button("✅ Sync Profile to Database Registry"):
                    if w_id and w_name and w_cnic:
                        st.session_state.workers_list.append({
                            "id": w_id, "cnic": w_cnic, "name": w_name, "f_name": w_fname, "dept": w_dept, "shift": w_shift, "role": "Worker",
                            "doj": w_doj, "dor": w_dor, "basic_salary": w_salary,
                            "balances": {"annual_m": allow_am, "annual_nm": allow_anm, "casual": allow_casual, "compensatory": allow_comp},
                            "attendance": {}
                        })
                        st.success(f"Success: Record created for '{w_name}' with designated quotas.")
                        st.rerun()
                    else:
                        st.error("Validation Error: Profile ID, Full Legal Name, and Identity Token are non-nullable fields.")

            st.write("---")
            st.markdown("<h4 style='color: #0284C7;'>✍️ Executive Direct Override Authorization</h4>", unsafe_allow_html=True)
            all_workers_names = [w['name'] for w in st.session_state.workers_list]
            
            if all_workers_names:
                adm_select_worker = st.selectbox("Select Target Employee Profile:", all_workers_names, key="adm_sel_w")
                adm_worker_data = next((w for w in st.session_state.workers_list if w['name'] == adm_select_worker), None)
                
                if adm_worker_data:
                    adm_leave_pay = st.radio("Compensation Type:", ["Paid Approved Channels", "Without Pay Overrides"], key="adm_pay", horizontal=True)
                    
                    if adm_leave_pay == "Paid Approved Channels":
                        adm_leave_type = st.selectbox("Category Select:", ["Annual Leave (M)", "Annual Leave (NM)", "Casual Leave", "Compensatory Leave"], key="adm_l_type")
                    else:
                        adm_leave_type = "Without Pay"
                        
                    col_ad1, col_ad2 = st.columns(2)
                    adm_start = col_ad1.date_input("Activation Frame Start", key="adm_s_date")
                    adm_end = col_ad2.date_input("Activation Frame End", key="adm_e_date")
                    
                    if st.button("✅ Force Override Authorization", use_container_width=True):
                        if adm_end >= adm_start:
                            days_num = (adm_end - adm_start).days + 1
                            t_month_days = calendar.monthrange(adm_start.year, adm_start.month)[1]
                            
                            if "attendance" not in adm_worker_data:
                                adm_worker_data["attendance"] = {}
                            
                            for d in range(adm_start.day, min(adm_end.day + 1, t_month_days + 1)):
                                adm_worker_data["attendance"][d] = f"⚠️ {adm_leave_type}"
                            
                            if adm_leave_pay == "Paid Approved Channels":
                                map_k = {"Annual Leave (M)": "annual_m", "Annual Leave (NM)": "annual_nm", "Casual Leave": "casual", "Compensatory Leave": "compensatory"}
                                k = map_k[adm_leave_type]
                                adm_worker_data["balances"][k] = max(0.0, adm_worker_data["balances"].get(k, 0.0) - days_num)
                            
                            st.session_state.notifications.append(f"💼 Executive Override: Admin enforced {days_num} days of {adm_leave_type} onto profile: {adm_select_worker}.")
                            st.success(f"Success: Overrides written into profile matrix for {adm_select_worker}!")
                            st.rerun()
                        else:
                            st.error("Timeline Validation Error: End frame configuration fault.")

        with col_admin2:
            st.markdown("<h4 style='color: #E11D48;'>✏️ Modify Existing Enterprise Records</h4>", unsafe_allow_html=True)
            all_workers = [w['name'] for w in st.session_state.workers_list]
            if all_workers:
                edit_name = st.selectbox("Select Target Modification Record:", all_workers, key="edit_sel")
                to_edit = next((w for w in st.session_state.workers_list if w['name'] == edit_name), None)
                
                if to_edit:
                    u_name = st.text_input("Modify Profile Username", value=to_edit["name"])
                    u_fname = st.text_input("Modify Parentage/Father Legal Name", value=to_edit.get("f_name", ""))
                    u_cnic = st.text_input("Modify Secured Identity Token (CNIC)", value=to_edit["cnic"])
                    u_id = st.text_input("Modify System Asset ID", value=to_edit["id"])
                    u_dept = st.selectbox("Modify Branch Segment Allocation", DEPARTMENTS, index=DEPARTMENTS.index(to_edit["dept"]) if to_edit["dept"] in DEPARTMENTS else 0)
                    u_shift = st.text_input("Modify Assignment Shift Schedule", value=to_edit["shift"])
                    
                    # Dates Modification Input
                    u_doj = st.text_input("Modify Date of Joining (DOJ)", value=to_edit.get("doj", "2020-01-01"))
                    u_dor = st.text_input("Modify Date of Retirement (DOR)", value=to_edit.get("dor", "2045-01-01"))
                    
                    u_salary = st.number_input("Modify Assigned Base Contract Compensation", min_value=0.0, step=1000.0, value=to_edit.get("basic_salary", 25000.0))
                    
                    st.markdown("<p style='color:#E11D48; font-weight:bold; margin-top:15px;'>🔄 Direct Ledger Adjustments:</p>", unsafe
