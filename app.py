import streamlit as st
from datetime import datetime, date
import json
import os

# 1. Page Config Setup (Native Streamlit Controls)
st.set_page_config(page_title="INSTAPLAST Leave Portal", page_icon="🏭", layout="wide")

# File path to store data permanently
DATA_FILE = "workers_data.json"

# Helper function to load data safely
def load_permanent_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
                if "workers" not in data:
                    data["workers"] = {}
                if "requests" not in data:
                    data["requests"] = []
                return data
        except:
            return {"workers": {}, "requests": []}
    return {"workers": {}, "requests": []}

# Helper function to save data safely
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

# Initialize Session States
if "db_loaded" not in st.session_state:
    db = load_permanent_data()
    st.session_state.workers_dict = db["workers"]
    st.session_state.leave_requests = db["requests"]
    st.session_state.db_loaded = True

# 2. Main Title Banner (Using Native Safe Headers)
st.title("🏭 INSTAPLAST PVT LTD")
st.subheader("Time Management & Leave Allocation System")
st.divider()

# Sidebar Access Control
st.sidebar.header("🔒 Security Access")
access_role = st.sidebar.selectbox("Select Dashboard View:", ["Worker", "Admin Portal"])
st.sidebar.divider()
st.sidebar.caption("⚡ INSTAPLAST Factory Sync v4.0")

# ==========================================
# WORKER PORTAL
# ==========================================
if access_role == "Worker":
    st.header("👤 Employee Identity Verification")
    
    if not st.session_state.workers_dict:
        st.warning("⚠️ ڈیش بورڈ پر کوئی ورکر موجود نہیں ہے۔ برائے مہربانی ایڈمن پینل سے پہلے ورکرز کا ڈیٹا داخل کریں۔")
    else:
        worker_list = list(st.session_state.workers_dict.keys())
        selected_worker = st.selectbox("Select Your Profile Name:", worker_list)
        cnic_token = st.text_input("Enter Identity Token (CNIC without dashes):", type="password")
        
        if cnic_token:
            actual_cnic = st.session_state.workers_dict[selected_worker].get("cnic", "")
            if cnic_token == actual_cnic:
                st.success(f"🔓 Verification Successful. Welcome, {selected_worker}!")
                st.divider()
                
                # Fetch Balances safely
                w_data = st.session_state.workers_dict[selected_worker]
                cl_val = int(w_data.get("CL", 0))
                sl_val = int(w_data.get("Sick", 0))
                al_val = int(w_data.get("Annual", 0))
                co_val = int(w_data.get("CO", 0))
                
                st.markdown("### 📊 Your Live Available Leave Balances")
                
                # Using Official Native Metrics Grid for Premium Interface
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric(label="🔵 Casual Leave (CL)", value=f"{cl_val} Days")
                with col2:
                    st.metric(label="🟢 Sick Leave", value=f"{sl_val} Days")
                with col3:
                    st.metric(label="🟠 Annual Leave", value=f"{al_val} Days")
                with col4:
                    st.metric(label="🟣 Compensation (CO)", value=f"{co_val} Days")
                
                st.divider()
                
                # Leave Request Form
                st.markdown("### 📝 Apply for New Leave")
                leave_type = st.selectbox("Select Leave Type Category:", ["Casual Leave (CL)", "Sick Leave", "Annual Leave", "Compensation (CO)"])
                leave_days = st.number_input("Number of Leave Days Required:", min_value=1, max_value=30, value=1)
                reason = st.text_area("State Reason for Leave:")
                
                if st.button("Submit Leave Request to Admin", use_container_width=True):
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
                        st.success("✅ آپ کی درخواست ایڈمن پینل کو بھیج دی گئی ہے۔ جیسے ہی ایڈمن 'Okay' کریں گے، آپ کا بیلنس کٹ جائے گا۔")
                        st.rerun()
                    else:
                        st.error("❌ Request Rejected: Insufficient leave balance available!")
            else:
                st.error("❌ Incorrect Identity Token (CNIC). Access Denied.")

# ==========================================
# ADMIN PORTAL
# ==========================================
else:
    st.header("🛠️ Admin Management Control Panel")
    admin_tab, requests_tab = st.tabs(["👥 Manage Workers Profiles", "📥 Pending Leave Requests"])
    
    with admin_tab:
        st.subheader("➕ Register New Factory Worker")
        
        col_inp1, col_inp2 = st.columns(2)
        with col_inp1:
            w_name = st.text_input("Worker Full Name:")
            w_cnic = st.text_input("ID Card Number / CNIC (No Dashes):")
        with col_inp2:
            w_mobile = st.text_input("Mobile / WhatsApp Number:")
            w_joining = st.date_input("Date of Joining Company:", value=date.today())
        
        st.markdown("##### Set Initial Leave Allocations")
        bal1, bal2, bal3, bal4 = st.columns(4)
        with bal1: c_cl = st.number_input("Casual (CL) Initial Set:", min_value=0, value=10)
        with bal2: c_sl = st.number_input("Sick Initial Set:", min_value=0, value=8)
        with bal3: c_al = st.number_input("Annual Initial Set:", min_value=0, value=14)
        with bal4: c_co = st.number_input("Compensation (CO) Initial Set:", min_value=0, value=0)
        
        if st.button("Save Profile & Commit Registry", use_container_width=True):
            if w_name and w_cnic:
                st.session_state.workers_dict[w_name] = {
                    "cnic": w_cnic,
                    "mobile": w_mobile,
                    "joining_date": str(w_joining),
                    "CL": int(c_cl),
                    "Sick": int(c_sl),
                    "Annual": int(c_al),
                    "CO": int(c_co)
                }
                save_permanent_data()
                st.success(f"💾 Profile for '{w_name}' successfully saved and synced!")
                st.rerun()
            else:
                st.error("❌ Validation Error: Name and CNIC Identity fields are required.")
                
        # Profile Deletion Engine
        if st.session_state.workers_dict:
            st.divider()
            st.subheader("🗑️ Remove Profile From Records")
            worker_to_delete = st.selectbox("Select Worker to Remove:", ["Select Worker"] + list(st.session_state.workers_dict.keys()))
            if worker_to_delete != "Select Worker":
                if st.button(f"Permanently Delete {worker_to_delete}", use_container_width=True):
                    del st.session_state.workers_dict[worker_to_delete]
                    st.session_state.leave_requests = [r for r in st.session_state.leave_requests if r["worker"] != worker_to_delete]
                    save_permanent_data()
                    st.success(f"🗑️ Profile data for '{worker_to_delete}' has been completely wiped.")
                    st.rerun()

        # Company Master View Matrix
        if st.session_state.workers_dict:
            st.divider()
            st.subheader("📋 Factory Database Master Sheet View")
            st.json(st.session_state.workers_dict)

    with requests_tab:
        st.subheader("📥 Incoming Leave Applications Queue")
        pending_reqs = [r for r in st.session_state.leave_requests if r["status"] == "Pending"]
        
        if not pending_reqs:
            st.info("🛋️ All clear! No pending leave applications found in the queue.")
        else:
            for req in pending_reqs:
                with st.container():
                    st.markdown(f"### 👤 Worker: {req['worker']}")
                    st.write(f"**Leave Category:** {req['leave_type']} | **Duration:** {req['days']} Days")
                    st.write(f"**Date Received:** {req['date']}")
                    st.info(f"Reason: {req['reason']}")
                    
                    col_app, col_rej = st.columns(2)
                    with col_app:
                        if st.button(f"✅ Okay / Approve (ID: {req['id']})", key=f"app_{req['id']}", use_container_width=True):
                            w_name = req['worker']
                            l_key = req['leave_type']
                            days_to_cut = int(req['days'])
                            
                            if w_name in st.session_state.workers_dict:
                                current_bal = int(st.session_state.workers_dict[w_name].get(l_key, 0))
                                if current_bal >= days_to_cut:
                                    st.session_state.workers_dict[w_name][l_key] -= days_to_cut
                                    req["status"] = "Approved"
                                    save_permanent_data()
                                    st.success(f"👍 Approved! {days_to_cut} days deducted.")
                                    st.rerun()
                                else:
                                    st.error("❌ Error: Worker does not have sufficient balance.")
                            else:
                                st.error("❌ Error: Worker profile not found.")
                    
                    with col_rej:
                        if st.button(f"❌ Reject / Cancel (ID: {req['id']})", key=f"rej_{req['id']}", use_container_width=True):
                            req["status"] = "Rejected"
                            save_permanent_data()
                            st.warning("⚠️ Application Rejected. Leave balances unchanged.")
                            st.rerun()
                st.divider()
