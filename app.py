import streamlit as st
from datetime import datetime, date
import pandas as pd
import base64
import json

# Page Setup
st.set_page_config(page_title="INSTAPLAST Leave Portal", page_icon="🏭", layout="wide")

ADMIN_PASSWORD = "admin123"  

# Custom Professional Theme Injection
st.html("""
<style>
    div.block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
    .section-title {
        color: #1e3a8a;
        font-family: 'Segoe UI', Arial, sans-serif;
        font-weight: 700;
        border-bottom: 3px solid #e0a924;
        padding-bottom: 5px;
        margin-bottom: 15px;
    }
    .profile-card {
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 15px;
        color: white;
        font-family: 'Segoe UI', sans-serif;
    }
    .c-personal { background: linear-gradient(135deg, #3b82f6, #1d4ed8); }
    .c-job { background: linear-gradient(135deg, #10b981, #047857); }
    .c-time { background: linear-gradient(135deg, #f59e0b, #b45309); }
    .c-benefit { background: linear-gradient(135deg, #8b5cf6, #6d28d9); }
    .c-payroll { background: linear-gradient(135deg, #ec4899, #be185d); }
    
    .card-title { font-size: 18px; font-weight: bold; margin-bottom: 8px; display: flex; align-items: center; gap: 8px; }
    .card-content { font-size: 14px; opacity: 0.95; line-height: 1.6; }
</style>
""")

# Image handling functions
def get_image_base64(uploaded_file):
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        return base64.b64encode(bytes_data).decode()
    return None

def display_worker_photo(base64_str):
    if base64_str:
        st.markdown(f'<img src="data:image/png;base64,{base64_str}" style="width:130px; height:130px; border-radius:50%; object-fit:cover; border:3px solid #e0a924; display:block; margin-left:auto; margin-right:auto; margin-bottom:15px;">', unsafe_allow_html=True)
    else:
        st.markdown('<div style="width:130px; height:130px; border-radius:50%; background-color:#e2e8f0; border:3px dashed #cbd5e1; display:flex; align-items:center; justify-content:center; margin-left:auto; margin-right:auto; margin-bottom:15px; color:#64748b; font-weight:bold;">No Photo</div>', unsafe_allow_html=True)

# Session state initialization
if "workers_dict" not in st.session_state:
    st.session_state.workers_dict = {}
if "leave_requests" not in st.session_state:
    st.session_state.leave_requests = []

# Corporate Banner Display
st.html("""
    <div style="background-color: #1e3a8a; padding: 25px; border-radius: 12px; text-align: center; margin-bottom: 25px; border-left: 8px solid #e0a924;">
        <h1 style="color: #ffffff; margin: 0; font-size: 34px; font-family: 'Segoe UI', Arial, sans-serif; font-weight: bold;">🏭 INSTAPLAST PVT LTD</h1>
        <p style="color: #f1f5f9; margin: 8px 0 0 0; font-size: 17px; font-weight: 500;">Time Management & Leave Allocation System</p>
    </div>
""")

# Sidebar Navigation Control
st.sidebar.title("🔒 Gate Panel")
access_role = st.sidebar.selectbox("Select Access Role:", ["Worker", "Admin Portal"])
st.sidebar.divider()
st.sidebar.caption("⚡ Powered by INSTAPLAST Engine v14.0")

# ==========================================
# WORKER PORTAL INTERFACE
# ==========================================
if access_role == "Worker":
    st.html("<h2 class='section-title'>👤 Employee Identity Verification & Leave Application</h2>")
    
    if not st.session_state.workers_dict:
        st.warning("⚠️ No worker database found. Please log in to the Admin Portal first to register profiles.")
    else:
        worker_list = list(st.session_state.workers_dict.keys())
        
        col_sel1, col_sel2, col_sel3 = st.columns(3)
        with col_sel1: selected_worker = st.selectbox("Select Profile Name:", worker_list)
        with col_sel2: cnic_input = st.text_input("Enter ID Card Number (CNIC):")
        with col_sel3: password_input = st.text_input("Enter Password (Your CNIC):", type="password")
            
        if cnic_input and password_input:
            w_data = st.session_state.workers_dict[selected_worker]
            saved_cnic = str(w_data.get("cnic", "")).strip()
            
            if str(cnic_input).strip() == saved_cnic and str(password_input).strip() == saved_cnic:
                st.success(f"🔓 Welcome, {selected_worker}!")
                st.divider()
                
                # Live Performance Dashboard
                st.html("<h3 class='section-title'>📊 Your Live Progress Dashboard</h3>")
                cl_val, sl_val = int(w_data.get("CL", 0)), int(w_data.get("Sick", 0))
                al_val, co_val = int(w_data.get("Annual", 0)), int(w_data.get("CO", 0))
                
                col_c1, col_c2, col_c3, col_c4 = st.columns(4)
                with col_c1: st.metric(label="🟢 Casual Leave (CL)", value=f"{cl_val} Days")
                with col_c2: st.metric(label="🟠 Sick Leave", value=f"{sl_val} Days")
                with col_c3: st.metric(label="🔵 Annual Leave", value=f"{al_val} Days")
                with col_c4: st.metric(label="🔴 Compensation (CO)", value=f"{co_val} Days")
                
                st.divider()
                
                col_left_form, col_right_profile = st.columns([1.1, 0.9])
                
                with col_left_form:
                    st.html("### 📝 Leave Application Form")
                    leave_type = st.selectbox("Select Leave Type:", ["Casual Leave (CL)", "Sick Leave", "Annual Leave", "Compensation (CO)"])
                    col_d1, col_d2 = st.columns(2)
                    with col_d1: date_from = st.date_input("Leave From:", value=date.today())
                    with col_d2: date_to = st.date_input("Leave To:", value=date.today())
                    
                    leave_days = st.number_input("Number of Days Required:", min_value=1, max_value=30, value=1)
                    reason = st.text_area("State Reason for Leave:")
                    
                    if st.button("Apply Now (Submit Request)", use_container_width=True):
                        leave_key = "CL" if "Casual" in leave_type else "Sick" if "Sick" in leave_type else "Annual" if "Annual" in leave_type else "CO"
                        if int(w_data.get(leave_key, 0)) >= leave_days:
                            new_req = {
                                "id": len(st.session_state.leave_requests) + 1,
                                "worker": selected_worker, "leave_type": leave_key, "days": leave_days,
                                "date_from": str(date_from), "date_to": str(date_to), "reason": reason,
                                "applied_on": str(date.today()), "status": "Pending"
                            }
                            st.session_state.leave_requests.append(new_req)
                            st.success("✅ Application submitted successfully! Please remind Admin to download database backup.")
                            st.rerun()
                        else:
                            st.error("❌ Request Rejected: Insufficient leave balance!")
                            
                with col_right_profile:
                    st.html("### 🌟 Worker Corporate Profile")
                    display_worker_photo(w_data.get("photo"))
                    
                    st.markdown(f"""<div class="profile-card c-personal"><div class="card-title">👤 Personal Data</div><div class="card-content">
                    <b>Full Name:</b> {selected_worker}<br><b>Father's Name:</b> {w_data.get('father_name', 'N/A')}<br>
                    <b>CNIC / Pass:</b> {w_data.get('cnic', 'N/A')}<br><b>Mobile:</b> {w_data.get('mobile', 'N/A')}</div></div>""", unsafe_allow_html=True)
                    
                    st.markdown(f"""<div class="profile-card c-job"><div class="card-title">💼 Job Data</div><div class="card-content">
                    <b>Worker ID:</b> {w_data.get('id', 'N/A')}<br><b>Date of Joining:</b> {w_data.get('joining_date', 'N/A')}<br>
                    <b>Contract End:</b> {w_data.get('end_date', 'N/A')}</div></div>""", unsafe_allow_html=True)
                    
                    st.markdown(f"""<div class="profile-card c-time"><div class="card-title">⏱️ Time Management</div><div class="card-content">
                    <b>Shift Details:</b> General Factory Shift<br><b>Duty Hours:</b> 08:00 AM - 05:00 PM</div></div>""", unsafe_allow_html=True)
                    
                    st.markdown(f"""<div class="profile-card c-payroll"><div class="card-title">💰 Payroll & Compensation</div><div class="card-content">
                    <b>Basic Monthly Salary:</b> Rs. {w_data.get('salary', '0')}/-<br><b>Benefit Details:</b> Verified Standard Pack<br><b>Succession Status:</b> Active Operational Track</div></div>""", unsafe_allow_html=True)
            else:
                st.error("❌ Invalid CNIC Number or Password.")

# ==========================================
# ADMIN PORTAL INTERFACE
# ==========================================
else:
    st.html("<h2 class='section-title'>🛠️ Admin Management Control Panel</h2>")
    admin_auth = st.text_input("Enter Admin Security Password:", type="password")
    
    if admin_auth == ADMIN_PASSWORD:
        st.success("🔓 Admin Access Authorized")
        
        # Backup System Dashboard
        st.html("<h3>💾 Backup & Recovery Management</h3>")
        col_b1, col_b2 = st.columns(2)
        
        with col_b1:
            db_export = {
                "workers": st.session_state.workers_dict,
                "requests": st.session_state.leave_requests
            }
            json_string = json.dumps(db_export, indent=4)
            st.download_button(
                label="📥 Download Database Backup File (Save before closing)",
                data=json_string,
                file_name=f"instaplast_backup_{date.today()}.json",
                mime="application/json",
                use_container_width=True
            )
            st.caption("💡 Tip: Always download this file at the end of the day to keep your data safe on your local PC.")
            
        with col_b2:
            uploaded_backup = st.file_uploader("📤 Upload Backup File (Restore database if empty):", type=["json"])
            if uploaded_backup is not None:
                try:
                    backup_data = json.load(uploaded_backup)
                    st.session_state.workers_dict = backup_data.get("workers", {})
                    st.session_state.leave_requests = backup_data.get("requests", [])
                    st.success("🎯 Success! Entire data registry has been restored successfully.")
                except Exception as e:
                    st.error(f"Error importing backup file: {e}")

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
                    w_joining = st.date_input("Date of Joining Company:", value=date.today(), min_value=date(1980,1,1))
                    w_end = st.date_input("Date of End (Contract End):", value=date.today(), min_value=date(1980,1,1))
                    w_photo = st.file_uploader("Upload Worker Photo:", type=["jpg", "jpeg", "png"])
                
                st.html("<h5>📊 Initial Leave Quota Allocation</h5>")
                col_l1, col_l2, col_l3, col_l4 = st.columns(4)
                with col_l1: cl_q = st.number_input("Casual Leave (CL):", value=0)
                with col_l2: sl_q = st.number_input("Sick Leave:", value=0)
                with col_l3: al_q = st.number_input("Annual Leave:", value=0)
                with col_l4: co_q = st.number_input("Compensation (CO):", value=0)
                
                if st.button("Save Profile & Commit Registry", use_container_width=True):
                    if w_name and w_cnic and w_id:
                        photo_b64 = get_image_base64(w_photo)
                        st.session_state.workers_dict[w_name] = {
                            "id": w_id, "cnic": w_cnic, "father_name": w_father, "mobile": w_mobile,
                            "salary": w_salary, "joining_date": str(w_joining), "end_date": str(w_end),
                            "password": w_cnic, "photo": photo_b64, "CL": cl_q, "Sick": sl_q, "Annual": al_q, "CO": co_q
                        }
                        st.success(f"💾 Profile for '{w_name}' saved! Password is sync with CNIC. Please download backup above.")
                        st.rerun()

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
                            edit_salary = st.text_input("Monthly Salary:", value=current_w_data.get("salary", "0"))
                        with col_e3:
                            edit_joining = st.date_input("Joining Date:", value=date.today(), min_value=date(1980,1,1), key="ed_j")
                            edit_end = st.date_input("Contract End Date:", value=date.today(), min_value=date(1980,1,1), key="ed_e")
                            edit_photo = st.file_uploader("Update New Photo (Optional):", type=["jpg", "png"])
                        
                        col_eb1, col_eb2, col_eb3, col_eb4 = st.columns(4)
                        with col_eb1: edit_cl = st.number_input("Casual Leave (CL):", value=int(current_w_data.get("CL", 0)), key="e_cl")
                        with col_eb2: edit_sl = st.number_input("Sick Leave:", value=int(current_w_data.get("Sick", 0)), key="e_sl")
                        with col_eb3: edit_al = st.number_input("Annual Leave:", value=int(current_w_data.get("Annual", 0)), key="e_al")
                        with col_eb4: edit_co = st.number_input("Compensation (CO):", value=int(current_w_data.get("CO", 0)), key="e_co")
                        
                        if st.button("Update Profile & Save Changes", use_container_width=True):
                            photo_str = get_image_base64(edit_photo) if edit_photo else current_w_data.get("photo")
                            st.session_state.workers_dict[edit_worker_name] = {
                                "id": edit_id, "cnic": edit_cnic, "father_name": edit_father, "mobile": edit_mobile,
                                "salary": edit_salary, "joining_date": str(edit_joining), "end_date": str(edit_end),
                                "password": edit_cnic, "photo": photo_str, "CL": edit_cl, "Sick": edit_sl, "Annual": edit_al, "CO": edit_co
                            }
                            st.success("✅ Profile updated temporarily. Make sure to download the backup file to make it permanent.")
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
                            col_app, col_rej = st.columns(2)
                            with col_app:
                                if st.button("✅ Approve Request", key=f"app_{req['id']}", use_container_width=True):
                                    st.session_state.workers_dict[req['worker']][req['leave_type']] -= int(req['days'])
                                    req["status"] = "Approved"
                                    st.rerun()
                            with col_rej:
                                if st.button("❌ Reject Request", key=f"rej_{req['id']}", use_container_width=True):
                                    req["status"] = "Rejected"
                                    st.rerun()

            # TAB 4: COMPLETE SHEETS RECORD WITH SEARCH BAR
            with records_tab:
                st.html("<h4>📊 Factory Workers Sheets & Search Panel</h4>")
                search_query = st.text_input("🔍 Search Worker by Name or Worker ID:", "").lower()
                
                if not st.session_state.workers_dict:
                    st.info("No workers registered in the platform yet.")
                else:
                    for name, details in st.session_state.workers_dict.items():
                        if search_query in name.lower() or search_query in str(details.get('id', '')).lower():
                            with st.expander(f"📋 Profile: {name} (ID: {details.get('id', 'N/A')})"):
                                col_v1, col_v2, col_v3 = st.columns([0.6, 1.4, 1.4])
                                with col_v1: display_worker_photo(details.get("photo"))
                                with col_v2:
                                    st.write(f"🧔 **Father's Name:** {details.get('father_name', 'N/A')}")
                                    st.write(f"🆔 **CNIC / Password:** {details.get('cnic', 'N/A')}")
                                    st.write(f"📱 **Mobile:** {details.get('mobile', 'N/A')}")
                                with col_v3:
                                    st.write(f"📅 **Date of Joining:** {details.get('joining_date', 'N/A')}")
                                    st.write(f"💰 **Monthly Salary:** Rs. {details.get('salary', '0')}/-")
                                
                                st.markdown(f"""
                                <div style="display:flex; gap:10px; flex-wrap:wrap; margin-top:10px;">
                                    <span style="background:#3b82f6; color:white; padding:5px 10px; border-radius:5px;">Personal Data</span>
                                    <span style="background:#10b981; color:white; padding:5px 10px; border-radius:5px;">Job Data</span>
                                    <span style="background:#f59e0b; color:white; padding:5px 10px; border-radius:5px;">Time Management</span>
                                    <span style="background:#8b5cf6; color:white; padding:5px 10px; border-radius:5px;">Benefit</span>
                                    <span style="background:#ec4899; color:white; padding:5px 10px; border-radius:5px;">Payroll & Compensation</span>
                                </div>
                                """, unsafe_allow_html=True)
                                st.code(f"Casual (CL): {details.get('CL', 0)} Days | Sick: {details.get('Sick', 0)} Days | Annual: {details.get('Annual', 0)} Days | CO: {details.get('CO', 0)} Days")
    elif admin_auth:
        st.error("❌ Invalid Admin Security Password.")
