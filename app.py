import streamlit as st
from datetime import datetime, date
import calendar
import pandas as pd

# 1. Page Config Setup
st.set_page_config(page_title="Gaironova - INSTAPLAST Leave Portal", page_icon="🏭", layout="wide")

# 2. Clean Corporate Theme Styling (Gaironova UI Alignment)
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

# 3. Memory Database Initialization with Required Leaves
if 'workers_list' not in st.session_state:
    st.session_state.workers_list = [
        {
            "id": "IP-1022",
            "cnic": "4210112345671",
            "name": "Muhammad Raza-ul-Mustafa",
            "f_name": "Ghulam Mustafa",
            "dept": "Utilities (Electrical & Instrumentation)",
            "shift": "G28SHIFT",
            "doj": "2020-03-15",
            "dor": "2045-08-12",
            "role": "Worker",
            "basic_salary": 45000.0,
            "balances": {"casual": 8.5, "sick": 5.0, "annual": 8.0, "compensation": 4.0},
            "attendance": {5: "Annual Leave"} 
        },
        {
            "id": "IP-1024",
            "cnic": "4210198765432",
            "name": "Yasir Ali",
            "f_name": "Ali Nawaz",
            "dept": "Utilities (Electrical & Instrumentation)",
            "shift": "G28SHIFT",
            "doj": "2021-05-10",
            "dor": "2048-11-20",
            "role": "Worker",
            "basic_salary": 42000.0,
            "balances": {"casual": 8.0, "sick": 6.0, "annual": 14.0, "compensation": 0.0},
            "attendance": {20: "Casual Leave", 21: "Casual Leave"}
        },
        {
            "id": "IP-1023",
            "cnic": "4210176543213",
            "name": "Ali Ahmed",
            "f_name": "Ahmed Khan",
            "dept": "Production",
            "shift": "A-SHIFT",
            "doj": "2022-06-01",
            "dor": "2050-01-10",
            "role": "Worker",
            "basic_salary": 38000.0,
            "balances": {"casual": 12.0, "sick": 6.0, "annual": 10.0, "compensation": 2.0},
            "attendance": {15: "Sick Leave"}
        }
    ]

if 'notifications' not in st.session_state:
    st.session_state.notifications = [
        "💼 Executive Override: Admin enforced 2 days of Casual Leave onto profile: Yasir Ali.",
        "📢 Employee Yasir Ali submitted Casual Leave from day 20 to 21 (2 Days).",
        "📢 Ali Ahmed applied for Sick Leave on the 15th of this month.",
        "📢 Muhammad Raza-ul-Mustafa applied for Annual Leave on the 5th of this month."
    ]

DEPARTMENTS = [
    "Utilities (Electrical & Instrumentation)", "Production", "Mechanical", 
    "HR / Admin", "Quality Control", "Store / Logistics", "Finishing & Packing"
]

# 4. Sidebar Gateway Access Controller
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

# 5. Dashboard Branding Headers
st.markdown("""
    <div class="main-header">
        <h1 style="color:white; margin:0; font-family: 'Arial', sans-serif; font-weight:700; letter-spacing: 1px;">🏭 INSTAPLAST PVT LTD</h1>
        <p style="color:#E0F2FE; margin:6px 0 0 0; font-size:16px; font-weight: 400;">Gaironova Time Management & Leave Allocation System</p>
    </div>
""", unsafe_allow_html=True)

# Live Broadcast Operations Monitor
st.markdown("<h4 style='color: #0284C7; font-weight:600;'>🔔 System Broadcast Dashboard</h4>", unsafe_allow_html=True)
if st.session_state.notifications:
    for note in reversed(st.session_state.notifications[-5:]):
        st.markdown(f"<div class='notification-box'>{note}</div>", unsafe_allow_html=True)
else:
    st.info("Log Stream Clear. No active leave operations recorded.")
st.write("---")

# 6. Worker User Workspace Interface Terminal
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
                st.markdown("<h4 style='color: #0D9488; font-weight:600;'>📊 Leave Account Balances</h4>", unsafe_allow_html=True)
                st.write("")
                b = worker_data["balances"]
                
                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    st.metric("Casual Leave", f"{b.get('casual', 0.0)} Days")
                with c2:
                    st.metric("Sick Leave", f"{b.get('sick', 0.0)} Days")
                with c3:
                    st.metric("Annual Leave", f"{b.get('annual', 0.0)} Days")
                with c4:
                    st.metric("Compensation Leave", f"{b.get('compensation', 0.0)} Days")

                st.write("---")
                
                st.markdown("<h4 style='color: #1E3A8A; font-weight:600;'>📝 Time Off Application Form</h4>", unsafe_allow_html=True)
                
                leave_type = st.selectbox("Select Leave Type:", [
                    "Casual Leave", 
                    "Sick Leave", 
                    "Annual Leave", 
                    "Compensation Leave"
                ])
                
                col_d1, col_d2 = st.columns(2)
                start_date = col_d1.date_input("Start Operation Date")
                end_date = col_d2.date_input("Terminating Operation Date")
                
                if st.button("🚀 Process Time Off Submission", use_container_width=True):
                    if end_date >= start_date:
                        days_requested = (end_date - start_date).days + 1
                        
                        if "attendance" not in worker_data:
                            worker_data["attendance"] = {}
                        
                        map_leave = {
                            "Casual Leave": "casual", 
                            "Sick Leave": "sick", 
                            "Annual Leave": "annual", 
                            "Compensation Leave": "compensation"
                        }
                        b_key = map_leave[leave_type]
                        
                        if worker_data["balances"].get(b_key, 0.0) >= days_requested:
                            worker_data["balances"][b_key] -= float(days_requested)
                            for d in range(start_date.day, min(end_date.day + 1, num_days + 1)):
                                worker_data["attendance"][d] = f"⚠️ {leave_type}"
                            st.session_state.notifications.append(f"⚠️ Employee {worker_data['name']} submitted {leave_type} from day {start_date.day} to {end_date.day} ({days_requested} Days).")
                            st.success(f"Success: Balance deduction adjusted. Total Days: {days_requested}")
                            st.balloons()
                            st.rerun()
                        else:
                            st.error(f"Quota Insufficient: Your requested allowance exceeds available {leave_type} credits.")
                    else:
                        st.error("Timeline Validation Error: Terminating date cannot precede starting operational date.")
        elif input_cnic != "":
            st.error("❌ Authentication Refused: Identity mismatch with profile username.")
        else:
            st.info("🔒 Secure Directory: Provide identity verification token to pull company records.")

# 7. Enterprise Management/Admin Workspace Terminal
elif user_role == "Admin" and is_admin_authenticated:
    st.markdown("<h3 style='color: #1E3A8A; font-weight:600;'>🛠️ Enterprise Admin Control Center</h3>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["👥 Workforce Management", "📋 Leave Balances Registry", "📊 Financial Payroll Sheet"])
    
    with tab1:
        col_admin1, col_admin2 = st.columns(2)
        
        with col_admin1:
            st.markdown("<h4 style='color: #0D9488;'>➕ Onboard New Workforce Profile</h4>", unsafe_allow_html=True)
            with st.form("add_form", clear_on_submit=True):
                w_id = st.text_input("Assign Enterprise Worker ID")
                w_cnic = st.text_input("Identity Card Token (CNIC without dashes)")
                w_name = st.text_input("Employee Full Legal Name")
                w_fname = st.text_input("Father's Name")
                w_dept = st.selectbox("Assign Segment Division", DEPARTMENTS)
                w_shift = st.text_input("Operational Shift Class")
                
                col_date1, col_date2 = st.columns(2)
                w_doj = col_date1.text_input("Date of Joining (YYYY-MM-DD)", value=str(date.today()))
                w_dor = col_date2.text_input("Date of Retirement (YYYY-MM-DD)", value="2050-01-01")
                
                w_salary = st.number_input("Base Compensation Salary Scale", min_value=0.0, step=1000.0, value=25000.0)
                
                st.markdown("<p style='color:#1E3A8A; font-weight:bold; margin-top:15px;'>📋 Set Annual Leave Entitlements:</p>", unsafe_allow_html=True)
                col_l1, col_l2 = st.columns(2)
                allow_casual = col_l1.number_input("Casual Leave Limit", min_value=0.0, value=12.0)
                allow_sick = col_l2.number_input("Sick Leave Limit", min_value=0.0, value=6.0)
                allow_annual = col_l1.number_input("Annual Leave Limit", min_value=0.0, value=10.0)
                allow_comp = col_l2.number_input("Compensation Leave Limit", min_value=0.0, value=4.0)
                
                if st.form_submit_button("✅ Sync Profile to Database Registry"):
                    if w_id and w_name and w_cnic:
                        st.session_state.workers_list.append({
                            "id": w_id, "cnic": w_cnic, "name": w_name, "f_name": w_fname, "dept": w_dept, "shift": w_shift, "role": "Worker",
                            "doj": w_doj, "dor": w_dor, "basic_salary": w_salary,
                            "balances": {"casual": allow_casual, "sick": allow_sick, "annual": allow_annual, "compensation": allow_comp},
                            "attendance": {}
                        })
                        st.success(f"Success: Record created for '{w_name}'")
                        st.rerun()
                    else:
                        st.error("Validation Error: Profile ID, Full Name, and CNIC are mandatory fields.")

            st.write("---")
            st.markdown("<h4 style='color: #0284C7;'>✍️ Executive Direct Override Authorization</h4>", unsafe_allow_html=True)
            all_workers_names = [w['name'] for w in st.session_state.workers_list]
            
            if all_workers_names:
                adm_select_worker = st.selectbox("Select Target Employee Profile:", all_workers_names, key="adm_sel_w")
                adm_worker_data = next((w for w in st.session_state.workers_list if w['name'] == adm_select_worker), None)
                
                if adm_worker_data:
                    adm_leave_type = st.selectbox("Category Select:", ["Casual Leave", "Sick Leave", "Annual Leave", "Compensation Leave"], key="adm_l_type")
                        
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
                            
                            map_k = {"Casual Leave": "casual", "Sick Leave": "sick", "Annual Leave": "annual", "Compensation Leave": "compensation"}
                            k = map_k[adm_leave_type]
                            adm_worker_data["balances"][k] = max(0.0, float(adm_worker_data["balances"].get(k, 0.0)) - float(days_num))
                            
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
                    
                    u_doj = st.text_input("Modify Date of Joining (DOJ)", value=to_edit.get("doj", "2020-01-01"))
                    u_dor = st.text_input("Modify Date of Retirement (DOR)", value=to_edit.get("dor", "2045-01-01"))
                    
                    u_salary = st.number_input("Modify Assigned Base Contract Compensation", min_value=0.0, step=1000.0, value=to_edit.get("basic_salary", 25000.0))
                    
                    st.markdown("<p style='color:#E11D48; font-weight:bold; margin-top:15px;'>Direct Ledger Adjustments:</p>", unsafe_allow_html=True)
                    col_u1, col_u2 = st.columns(2)
                    u_casual = col_u1.number_input("Casual Leave Balance Allocation", min_value=0.0, value=float(to_edit["balances"].get("casual", 0.0)))
                    u_sick = col_u2.number_input("Sick Leave Balance Allocation", min_value=0.0, value=float(to_edit["balances"].get("sick", 0.0)))
                    u_annual = col_u1.number_input("Annual Leave Balance Allocation", min_value=0.0, value=float(to_edit["balances"].get("annual", 0.0)))
                    u_comp = col_u2.number_input("Compensation Leave Balance Allocation", min_value=0.0, value=float(to_edit["balances"].get("compensation", 0.0)))
                    
                    if st.button("🔄 Sync Operations to Enterprise Record", use_container_width=True):
                        to_edit["name"] = u_name
                        to_edit["f_name"] = u_fname
                        to_edit["cnic"] = u_cnic
                        to_edit["id"] = u_id
                        to_edit["dept"] = u_dept
                        to_edit["shift"] = u_shift
                        to_edit["doj"] = u_doj
                        to_edit["dor"] = u_dor
                        to_edit["basic_salary"] = u_salary
                        to_edit["balances"] = {"casual": u_casual, "sick": u_sick, "annual": u_annual, "compensation": u_comp}
                        st.success("Success: Operational variables committed to database stack.")
                        st.rerun()
                
    with tab2:
        st.markdown("<h4 style='color: #1E3A8A;'>📋 System Master Leave Ledger Records</h4>", unsafe_allow_html=True)
        
        records_data = []
        for w in st.session_state.workers_list:
            taken_leaves = []
            for day, status in w.get("attendance", {}).items():
                if "Leave" in str(status):
                    taken_leaves.append(f"Day {day} ({status})")
            
            if len(taken_leaves) > 0:
                leaves_summary = ", ".join(taken_leaves)
            else:
                leaves_summary = "Clear (No Active Logs)"
            
            records_data.append({
                "Worker ID": w["id"],
                "Employee Name": w["name"],
                "Father Name": w.get("f_name", "---"),
                "Department Segment": w["dept"],
                "Casual Leave": w["balances"].get("casual", 0.0),
                "Sick Leave": w["balances"].get("sick", 0.0),
                "Annual Leave": w["balances"].get("annual", 0.0),
                "Compensation Leave": w["balances"].get("compensation", 0.0),
                "Current Month Time Off Breakdown": leaves_summary
            })
        if records_data:
            df_records = pd.DataFrame(records_data)
            st.dataframe(df_records, use_container_width=True)
        else:
            st.info("System Alert: Master Ledger records stream empty.")

    with tab3:
        st.markdown("<h4 style='color: #1E3A8A;'>📊 Consolidated Payroll Operations Compensation Sheet</h4>", unsafe_allow_html=True)
        
        salary_sheet_data = []
        for w in st.session_state.workers_list:
            basic = w.get("basic_salary", 25000.0)
            
            salary_sheet_data.append({
                "Asset Worker ID": w["id"],
                "Legal Name": w["name"],
                "Father Name": w.get("f_name", "---"),
                "DOJ": w.get("doj", "---"),
                "DOR": w.get("dor", "---"),
                "Base Contract Allowance": f"Rs. {basic:,.2f}",
                "Net Salary Payable": f"Rs. {basic:,.2f}"
            })
            
        if salary_sheet_data:
            df_salary = pd.DataFrame(salary_sheet_data)
            st.dataframe(df_salary, use_container_width=True)

elif user_role == "Admin" and not is_admin_authenticated:
    st.info("🔒 Cryptographic Security: Authenticate management credentials within the gate layout to toggle access.")
