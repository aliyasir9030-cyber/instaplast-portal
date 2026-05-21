import streamlit as st
from datetime import datetime, date
import json
import os

# Page Setup
st.set_page_config(page_title="INSTAPLAST Leave Portal", page_icon="🏭", layout="wide")

DATA_FILE = "workers_db.json"
ADMIN_PASSWORD = "admin"  # ایڈمن پورٹل کا سیکیورٹی پاسورڈ

def load_permanent_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
                if "workers" not in data: data["workers"] = {}
                if "requests" not in data: data["requests"] = []
                return data
        except:
            return {"workers": {}, "requests": []}
    return {"workers": {}, "requests": []}

def save_permanent_data():
    try:
        data_to_save = {
            "workers": st.session_state.workers_dict,
            "requests": st.session_state.leave_requests
        }
        with open(DATA_FILE, "w") as f:
            json.dump(data_to_save, f, indent=4)
    except Exception as e:
        st.error(f"Data Saving Error: {e}")

if "db_loaded" not in st.session_state:
    db = load_permanent_data()
    st.session_state.workers_dict = db["workers"]
    st.session_state.leave_requests = db["requests"]
    st.session_state.db_loaded = True

# Corporate Header
st.html("""
    <div style="background-color: #1e3a8a; padding: 25px; border-radius: 12px; text-align: center; margin-bottom: 25px; border-left: 8px solid #e0a924;">
        <h1 style="color: #ffffff; margin: 0; font-size: 34px; font-family: 'Segoe UI', Arial, sans-serif; font-weight: bold;">🏭 INSTAPLAST PVT LTD</h1>
        <p style="color: #f1f5f9; margin: 8px 0 0 0; font-size: 17px; font-weight: 500;">Time Management & Leave Allocation System</p>
    </div>
""")

# Sidebar Navigation
st.sidebar.title("🔒 Gate Panel")
access_role = st.sidebar.selectbox("Select Access Role:", ["Worker", "Admin Portal"])
st.sidebar.divider()
st.sidebar.caption("⚡ Powered by INSTAPLAST Engine v12.0")

# ==========================================
# WORKER PORTAL
# ==========================================
if access_role == "Worker":
    st.header("👤 Employee Identity Verification")
    
    if not st.session_state.workers_dict:
        st.warning("⚠️ ڈیش بورڈ پر کوئی ورکر موجود نہیں ہے۔ برائے مہربانی پہلے ایڈمن پورٹل سے لاگ ان کر کے ورکرز کا پروفائل داخل کریں۔")
    else:
        worker_list = list(st.session_state.workers_dict.keys())
        
        col_sel1, col_sel2, col_sel3 = st.columns(3)
        with col_sel1:
            selected_worker = st.selectbox("Select Profile Name:", worker_list)
        with col_sel2:
            cnic_input = st.text_input("Enter ID Card Number (CNIC):")
        with col_sel3:
            password_input = st.text_input("Enter Worker Password:", type="password")
            
        if cnic_input and password_input:
            w_data = st.session_state.workers_dict[selected_worker]
            
            if cnic_input == w_data.get("cnic", "") and password_input == w_data.get("password", ""):
                st.success(f"🔓 Welcome, {selected_worker}!")
                st.divider()
                
                # Live Dashboard Display
                st.subheader("📊 Your Live Progress Dashboard")
                cl_val = int(w_data.get("CL", 0))
                sl_val = int(w_data.get("Sick", 0))
                al_val = int(w_data.get("Annual", 0))
                co_val = int(w_data.get("CO", 0))
                
                col_c1, col_c2, col_c3, col_c4 = st.columns(4)
                with col_c1: st.metric(label="🟢 Casual Leave (CL)", value=f"{cl_val} Days")
                with col_c2: st.metric(label="🟠 Sick Leave", value=f"{sl_val} Days")
                with col_c3: st.metric(label="🔵 Annual Leave", value=f"{al_val} Days")
                with col_c4: st.metric(label="🔴 Compensation (CO)", value=f"{co_val} Days")
                
                st.divider()
                
                # Leave Form & Profile Layout
                col_left_form, col_right_profile = st.columns([1.2, 0.8])
                
                with col_left_form:
                    st.markdown("### 📝 Leave Application Form")
                    leave_type = st.selectbox("Select Leave Type:", ["Casual Leave (CL)", "Sick Leave", "Annual Leave", "Compensation (CO)"])
                    
                    col_d1, col_d2 = st.columns(2)
                    with col_d1: date_from = st.date_input("Leave From:", value=date.today())
                    with col_d2: date_to = st.date_input("Leave To:", value=date.today())
                    
                    leave_days = st.number_input("Number of Days Required:", min_value=1, max_value=30, value=1)
                    reason = st.text_area("State Reason for Leave:")
                    
                    if st.button("Apply Now (Submit Request)", use_container_width=True):
                        leave_key = "CL" if "Casual" in leave_type else "Sick" if "Sick" in leave_type else "Annual" if "Annual" in leave_type else "CO"
                        current_balance = int(w_data.get(leave_key, 0))
                        
                        if current_balance >= leave_days:
                            req_id = len(st.session_state.leave_requests) + 1
                            new_req = {
                                "id": req_id,
                                "worker": selected_worker,
                                "leave_type": leave_key,
                                "days": leave_days,
                                "date_from": str(date_from),
                                "date_to": str(date_to),
                                "reason": reason,
                                "applied_on": str(date.today()),
                                "status": "Pending"
                            }
                            st.session_state.leave_requests.append(new_req)
                            save_permanent_data()
                            st.success(f"✅ درخواست ایڈمن کو بھیج دی گئی ہے! ({date_from} سے {date_to})")
                            st.rerun()
                        else:
                            st.error("❌ Request Rejected: Insufficient leave balance!")
                            
                with col_right_profile:
                    st.markdown("### 📋 Verification Details")
                    with st.container(border=True):
                        st.write(f"🆔 **Worker ID:** {w_data.get('id', 'N/A')}")
                        st.write(f"🧔 **Father's Name:** {w_data.get('father_name', 'N/A')}")
                        st.write(f"📱 **Mobile No:** {w_data.get('mobile', 'N/A')}")
                        st.write(f"📅 **Date of Joining:** {w_data.get('joining_date', 'N/A')}")
                        st.write(f"⏳ **Date of End:** {w_data.get('end_date', 'N/A')}")
                        st.write(f"💰 **Current Salary:** Rs. {w_data.get('salary', '0')}/-")
            else:
                st.error("❌ شناختی کارڈ نمبر یا ورکر پاسورڈ درست نہیں ہے۔")

# ==========================================
# ADMIN PORTAL
# ==========================================
else:
    st.header("🛠️ Admin Management Control Panel")
    admin_auth = st.text_input("Enter Admin Security Password:", type="password")
    
    if admin_auth == ADMIN_PASSWORD:
        st.success("🔓 Admin Access Authorized")
        
        with st.container(border=True):
            admin_tab, edit_tab, requests_tab, records_tab = st.tabs([
                "👥 Register & Delete Workers", 
                "✏️ Edit Worker Balances & Profiles", 
                "📥 Leave Requests Queue", 
                "📊 Complete Factory Sheets"
            ])
            
            # TAB 1: REGISTER & DELETE
            with admin_tab:
                st.markdown("#### ➕ Register New Factory Worker Profile")
                col_p1, col_p2, col_p3 = st.columns(3)
                with col_p1:
                    w_id = st.text_input("Worker ID / Roll No:")
                    w_name = st.text_input("Worker Full Name:")
                    w_father = st.text_input("Father's Name (ولدیت):")
                with col_p2:
                    w_cnic = st.text_input("ID Card Number / CNIC:")
                    w_mobile = st.text_input("Mobile / WhatsApp Number:")
                    w_salary = st.text_input("Monthly Salary (Rs.):", value="0")
                with col_p3:
                    w_joining = st.date_input("Date of Joining Company:", value=date.today())
                    w_end = st.date_input("Date of End (Contract End):", value=date.today())
                    w_pass = st.text_input("Assign Worker Login Password:", type="password", value="1234")
                
                st.markdown("##### 📊 Initial Leave Quota Allocation (ڈیفالٹ زیرو)")
                col_l1, col_l2, col_l3, col_l4 = st.columns(4)
                # آپ کی فرمائش کے مطابق اب یہ پہلے سے سب 0 پر ہوں گی
                with col_l1: cl_q = st.number_input("Casual Leave (CL):", value=0)
                with col_l2: sl_q = st.number_input("Sick Leave:", value=0)
                with col_l3: al_q = st.number_input("Annual Leave:", value=0)
                with col_l4: co_q = st.number_input("Compensation (CO):", value=0)
                
                if st.button("Save Profile & Commit Registry", use_container_width=True):
                    if w_name and w_cnic and w_id:
                        st.session_state.workers_dict[w_name] = {
                            "id": w_id,
                            "cnic": w_cnic,
                            "father_name": w_father,
                            "mobile": w_mobile,
                            "salary": w_salary,
                            "joining_date": str(w_joining),
                            "end_date": str(w_end),
                            "password": w_pass,
                            "CL": cl_q,
                            "Sick": sl_q,
                            "Annual": al_q,
                            "CO": co_q
                        }
                        save_permanent_data()
                        st.success(f"💾 Profile for '{w_name}' successfully locked into database!")
                        st.rerun()
                
                if st.session_state.workers_dict:
                    st.divider()
                    st.markdown("#### 🗑️ Permanently Remove Profile From Records")
                    worker_to_delete = st.selectbox("Select Worker to Remove Profile:", ["Select Worker"] + list(st.session_state.workers_dict.keys()))
                    if worker_to_delete != "Select Worker":
                        if st.button(f"Permanently Delete {worker_to_delete}", use_container_width=True):
                            del st.session_state.workers_dict[worker_to_delete]
                            st.session_state.leave_requests = [r for r in st.session_state.leave_requests if r["worker"] != worker_to_delete]
                            save_permanent_data()
                            st.success(f"🗑️ Profile data for '{worker_to_delete}' has been completely wiped out.")
                            st.rerun()

            # NEW TAB 2: EDIT WORKER PROFILES & LEAVE BALANCES
            with edit_tab:
                st.markdown("#### ✏️ Audit & Edit Worker Balances / Profiles")
                if not st.session_state.workers_dict:
                    st.info("کوئی ورکر ڈیٹا بیس میں موجود نہیں ہے۔")
                else:
                    edit_worker_name = st.selectbox("Select Worker to Edit:", ["Select Worker"] + list(st.session_state.workers_dict.keys()), key="edit_worker_select")
                    
                    if edit_worker_name != "Select Worker":
                        current_w_data = st.session_state.workers_dict[edit_worker_name]
                        
                        st.markdown(f"**Editing Profile:** {edit_worker_name}")
                        col_e1, col_e2, col_e3 = st.columns(3)
                        
                        with col_e1:
                            edit_id = st.text_input("Worker ID:", value=current_w_data.get("id", ""))
                            edit_father = st.text_input("Father Name:", value=current_w_data.get("father_name", ""))
                            edit_password = st.text_input("Worker Password:", value=current_w_data.get("password", ""))
                        with col_e2:
                            edit_cnic = st.text_input("CNIC Number:", value=current_w_data.get("cnic", ""))
                            edit_mobile = st.text_input("Mobile Number:", value=current_w_data.get("mobile", ""))
                            edit_salary = st.text_input("Monthly Salary:", value=current_w_data.get("salary", "0"))
                        with col_e3:
                            # Dates Handling
                            try:
                                jd_obj = datetime.strptime(current_w_data.get("joining_date", str(date.today())), "%Y-%m-%d").date()
                                ed_obj = datetime.strptime(current_w_data.get("end_date", str(date.today())), "%Y-%m-%d").date()
                            except:
                                jd_obj = date.today()
                                ed_obj = date.today()
                                
                            edit_joining = st.date_input("Joining Date:", value=jd_obj, key="edit_j_date")
                            edit_end = st.date_input("Contract End Date:", value=ed_obj, key="edit_e_date")
                        
                        st.markdown("##### ⚙️ Adjust Leave Quota Balances Manually")
                        col_eb1, col_eb2, col_eb3, col_eb4 = st.columns(4)
                        with col_eb1: edit_cl = st.number_input("Casual Leave Balance (CL):", value=int(current_w_data.get("CL", 0)))
                        with col_eb2: edit_sl = st.number_input("Sick Leave Balance:", value=int(current_w_data.get("Sick", 0)))
                        with col_eb3: edit_al = st.number_input("Annual Leave Balance:", value=int(current_w_data.get("Annual", 0)))
                        with col_eb4: edit_co = st.number_input("Compensation Balance (CO):", value=int(current_w_data.get("CO", 0)))
                        
                        if st.button("Update Profile & Save Changes", use_container_width=True):
                            st.session_state.workers_dict[edit_worker_name] = {
                                "id": edit_id,
                                "cnic": edit_cnic,
                                "father_name": edit_father,
                                "mobile": edit_mobile,
                                "salary": edit_salary,
                                "joining_date": str(edit_joining),
                                "end_date": str(edit_end),
                                "password": edit_password,
                                "CL": edit_cl,
                                "Sick": edit_sl,
                                "Annual": edit_al,
                                "CO": edit_co
                            }
                            save_permanent_data()
                            st.success(f"✅ '{edit_worker_name}' کا ریکارڈ کامیابی سے اپڈیٹ اور سیو کر دیا گیا ہے!")
                            st.rerun()

            # TAB 3: REQUESTS QUEUE
            with requests_tab:
                st.markdown("#### 📥 Incoming Leave Applications Queue")
                pending_reqs = [r for r in st.session_state.leave_requests if r["status"] == "Pending"]
                
                if not pending_reqs:
                    st.info("🛋️ No pending leave applications found in the queue.")
                else:
                    for req in pending_reqs:
                        with st.container(border=True):
                            st.write(f"👤 **Worker Name:** {req['worker']}")
                            st.write(f"📅 **Requested Dates:** From `{req.get('date_from', 'N/A')}` to `{req.get('date_to', 'N/A')}`")
                            st.write(f"📋 **Leave Category:** {req['leave_type']} | **Total Duration:** {req['days']} Days")
                            st.write(f"💬 **Reason:** {req['reason']}")
                            st.caption(f"Applied on: {req.get('applied_on', 'N/A')}")
                            
                            col_app, col_rej = st.columns(2)
                            with col_app:
                                if st.button("✅ Approve Request", key=f"app_{req['id']}", use_container_width=True):
                                    w_name = req['worker']
                                    l_key = req['leave_type']
                                    days_to_cut = int(req['days'])
                                    
                                    if w_name in st.session_state.workers_dict:
                                        st.session_state.workers_dict[w_name][l_key] -= days_to_cut
                                        req["status"] = "Approved"
                                        save_permanent_data()
                                        st.success("Approved!")
                                        st.rerun()
                            with col_rej:
                                if st.button("❌ Reject Request", key=f"rej_{req['id']}", use_container_width=True):
                                    req["status"] = "Rejected"
                                    save_permanent_data()
                                    st.warning("Rejected.")
                                    st.rerun()

            # TAB 4: COMPLETE RECORDS
            with records_tab:
                st.markdown("#### 📊 Factory Workers Sheets & Live Leave Balance")
                if not st.session_state.workers_dict:
                    st.info("کوئی ورکر رجسٹرڈ نہیں ہے۔")
                else:
                    for name, details in st.session_state.workers_dict.items():
                        with st.expander(f"📋 Profile: {name} (ID: {details.get('id', 'N/A')})"):
                            col_v1, col_v2 = st.columns(2)
                            with col_v1:
                                st.write(f"🧔 **Father's Name:** {details.get('father_name', 'N/A')}")
                                st.write(f"🆔 **CNIC:** {details.get('cnic', 'N/A')}")
                                st.write(f"📱 **Mobile:** {details.get('mobile', 'N/A')}")
                                st.write(f"💰 **Monthly Salary:** Rs. {details.get('salary', '0')}/-")
                            with col_v2:
                                st.write(f"📅 **Date of Joining:** {details.get('joining_date', 'N/A')}")
                                st.write(f"⏳ **Date of End:** {details.get('end_date', 'N/A')}")
                                st.write(f"🔑 **Password:** {details.get('password', 'N/A')}")
                            
                            st.markdown("**Current Leave Balances Available:**")
                            st.code(f"Casual (CL): {details.get('CL', 0)} Days | Sick: {details.get('Sick', 0)} Days | Annual: {details.get('Annual', 0)} Days | CO: {details.get('CO', 0)} Days")
    elif admin_auth:
        st.error("❌ ایڈمن پورٹل کا پاسورڈ غلط ہے۔")
