import streamlit as st
from datetime import datetime, date
import json
import os

# Page Setup - یہاں ہم نے آفیشل طریقہ استعمال کیا ہے جو ایپ کو ائیرر نہیں دے گا
st.set_page_config(page_title="INSTAPLAST Leave Portal", page_icon="🏭", layout="wide")

DATA_FILE = "workers_data.json"

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

# ==========================================
# OFFICIAL CORPORATE HEADER (SAFE METHOD)
# ==========================================
# یہ بالکل محفوظ طریقہ ہے جو ایپ کو کریش کیے بغیر خوبصورت نیلے رنگ کا بڑا ہیڈر بینر بنائے گا
st.html("""
    <div style="background-color: #1e3a8a; padding: 30px; border-radius: 12px; text-align: center; margin-bottom: 25px; border-left: 8px solid #e0a924;">
        <h1 style="color: #ffffff; margin: 0; font-size: 36px; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; font-weight: bold; letter-spacing: 1px;">🏭 INSTAPLAST PVT LTD</h1>
        <p style="color: #f1f5f9; margin: 10px 0 0 0; font-size: 18px; font-weight: 500; opacity: 0.95;">Time Management & Leave Allocation System</p>
    </div>
""")

# Sidebar Control
st.sidebar.title("🔒 Gate Panel")
access_role = st.sidebar.selectbox("Select Access Role:", ["Worker", "Admin Portal"])
st.sidebar.divider()
st.sidebar.caption("⚡ Powered by INSTAPLAST Engine v9.0")

# ==========================================
# WORKER PORTAL
# ==========================================
if access_role == "Worker":
    st.header("👤 Employee Identity Verification & Leave Application")
    
    with st.container(border=True):
        if not st.session_state.workers_dict:
            st.warning("⚠️ ڈیش بورڈ پر کوئی ورکر موجود نہیں ہے۔ برائے مہربانی ایڈمن پینل سے پہلے ورکرز کا ڈیٹا داخل کریں۔")
        else:
            worker_list = list(st.session_state.workers_dict.keys())
            
            col_sel1, col_sel2 = st.columns(2)
            with col_sel1:
                selected_worker = st.selectbox("Profile Name:", worker_list)
            with col_sel2:
                cnic_token = st.text_input("Enter Identity Token (CNIC):", type="password")
            
            if cnic_token:
                actual_cnic = st.session_state.workers_dict[selected_worker].get("cnic", "")
                if cnic_token == actual_cnic:
                    st.success(f"🔓 Welcome, {selected_worker}!")
                    st.divider()
                    
                    w_data = st.session_state.workers_dict[selected_worker]
                    cl_val = int(w_data.get("CL", 0))
                    sl_val = int(w_data.get("Sick", 0))
                    al_val = int(w_data.get("Annual", 0))
                    co_val = int(w_data.get("CO", 0))
                    
                    col_left_form, col_right_cards = st.columns([1.1, 0.9])
                    
                    with col_left_form:
                        st.subheader("📝 Leave Application Form")
                        leave_type = st.selectbox("Select Leave Type:", ["Casual Leave (CL)", "Sick Leave", "Annual Leave", "Compensation (CO)"])
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
                                    "reason": reason,
                                    "date": str(date.today()),
                                    "status": "Pending"
                                }
                                st.session_state.leave_requests.append(new_req)
                                save_permanent_data()
                                st.success("✅ آپ کی درخواست ایڈمن پینل کو کامیابی سے بھیج دی گئی ہے۔")
                                st.rerun()
                            else:
                                st.error("❌ Request Rejected: Insufficient balance!")
                    
                    with col_right_cards:
                        st.subheader("📊 Available Leave Tracks")
                        st.success(f"🟢 **Casual Leave (CL):** {cl_val} Days Available")
                        st.warning(f"🟠 **Sick Leave:** {sl_val} Days Available")
                        st.info(f"🔵 **Annual Leave:** {al_val} Days Available")
                        st.error(f"🔴 **Compensation (CO):** {co_val} Days Available")
                else:
                    st.error("❌ Incorrect Identity Token (CNIC).")

# ==========================================
# ADMIN PORTAL
# ==========================================
else:
    st.header("🛠️ Admin Management Control Panel")
    
    with st.container(border=True):
        admin_tab, requests_tab = st.tabs(["👥 Manage Workers Profiles", "📥 Pending Leave Requests"])
        
        with admin_tab:
            st.markdown("#### ➕ Register New Factory Worker")
            col_inp1, col_inp2 = st.columns(2)
            with col_inp1:
                w_name = st.text_input("Worker Full Name:")
                w_cnic = st.text_input("ID Card Number / CNIC (No Dashes):")
            with col_inp2:
                w_mobile = st.text_input("Mobile / WhatsApp Number:")
                w_joining = st.date_input("Date of Joining Company:", value=date.today())
            
            # یہاں آپ کی ڈیمانڈ کے مطابق ان پٹ فیلڈز مکمل غائب کر دی گئی ہیں
            if st.button("Save Profile & Commit Registry", use_container_width=True):
                if w_name and w_cnic:
                    # بیک اینڈ پر آٹومیٹک ڈیفالٹ کوٹہ الاٹ ہو جائے گا
                    st.session_state.workers_dict[w_name] = {
                        "cnic": w_cnic,
                        "mobile": w_mobile,
                        "joining_date": str(w_joining),
                        "CL": 10,
                        "Sick": 8,
                        "Annual": 14,
                        "CO": 0
                    }
                    save_permanent_data()
                    st.success(f"💾 Profile for '{w_name}' successfully saved into registry!")
                    st.rerun()
                    
            if st.session_state.workers_dict:
                st.divider()
                st.markdown("#### 🗑️ Remove Profile From Records")
                worker_to_delete = st.selectbox("Select Worker to Remove:", ["Select Worker"] + list(st.session_state.workers_dict.keys()))
                if worker_to_delete != "Select Worker":
                    if st.button(f"Permanently Delete {worker_to_delete}", use_container_width=True):
                        del st.session_state.workers_dict[worker_to_delete]
                        st.session_state.leave_requests = [r for r in st.session_state.leave_requests if r["worker"] != worker_to_delete]
                        save_permanent_data()
                        st.success(f"🗑️ Profile data for '{worker_to_delete}' has been removed.")
                        st.rerun()

        with requests_tab:
            st.markdown("#### 📥 Incoming Leave Applications Queue")
            pending_reqs = [r for r in st.session_state.leave_requests if r["status"] == "Pending"]
            
            if not pending_reqs:
                st.info("🛋️ No pending leave applications found in the queue.")
            else:
                for req in pending_reqs:
                    with st.container(border=True):
                        st.write(f"👤 **Worker Name:** {req['worker']}")
                        st.write(f"📋 **Leave Type:** {req['leave_type']} | **Duration:** {req['days']} Days")
                        st.write(f"💬 **Reason:** {req['reason']}")
                        
                        col_app, col_rej = st.columns(2)
                        with col_app:
                            if st.button(f"✅ Approve (ID: {req['id']})", key=f"app_{req['id']}", use_container_width=True):
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
                            if st.button(f"❌ Reject (ID: {req['id']})", key=f"rej_{req['id']}", use_container_width=True):
                                req["status"] = "Rejected"
                                save_permanent_data()
                                st.warning("Rejected.")
                                st.rerun()
