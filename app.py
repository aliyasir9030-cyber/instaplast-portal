import streamlit as st
from datetime import datetime, date
import json
import os

# 1. Page Config Setup
st.set_page_config(page_title="INSTAPLAST Leave Portal", page_icon="🏭", layout="wide")

# File path to permanently store data
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

# 2. Main Brand Header Banner (Simpler version to avoid markdown errors)
st.title("🏭 INSTAPLAST PVT LTD")
st.subheader("Time Management & Leave Allocation System")
st.markdown("---")

# Sidebar - Access Control
st.sidebar.markdown("## 🔒 INSTAPLAST Gate Panel")
access_role = st.sidebar.selectbox("Select Access Role", ["Worker", "Admin Portal"])

# ==========================================
# WORKER PORTAL
# ==========================================
if access_role == "Worker":
    st.markdown("### 👤 Employee Identity Verification & Leave Application")
    
    if not st.session_state.workers_dict:
        st.warning("⚠️ ڈیش بورڈ پر کوئی ورکر موجود نہیں ہے۔ برائے مہربانی ایڈمن پینل سے پہلے ورکرز کا ڈیٹا داخل کریں۔")
    else:
        worker_list = list(st.session_state.workers_dict.keys())
        selected_worker = st.selectbox("Select Profile Username:", worker_list)
        cnic_token = st.text_input("Enter Identity Token (CNIC without dashes):", type="password")
        
        if cnic_token:
            actual_cnic = st.session_state.workers_dict[selected_worker].get("cnic", "")
            if cnic_token == actual_cnic:
                st.success(f"🔓 Verification Successful. Welcome, {selected_worker}!")
                
                # Show Current Balances safely
                w_data = st.session_state.workers_dict[selected_worker]
                st.markdown("#### 📊 Your Current Available Leave Balance")
                
                col1, col2, col3, col4 = st.columns(4)
                # Safeguard: Convert values to integer before passing to metric
                cl_val = int(w_data.get("CL", 0))
                sl_val = int(w_data.get("Sick", 0))
                al_val = int(w_data.get("Annual", 0))
                co_val = int(w_data.get("CO", 0))
                
                col1.metric("Casual Leave (CL)", cl_val)
                col2.metric("Sick Leave", sl_val)
                col3.metric("Annual Leave", al_val)
                col4.metric("Compensation (CO)", co_val)
                
                # Leave Application Form
                st.markdown("### 📝 Apply for New Leave")
                leave_type = st.selectbox("Select Leave Type:", ["Casual Leave (CL)", "Sick Leave", "Annual Leave", "Compensation (CO)"])
                leave_days = st.number_input("Number of Days Required:", min_value=1, max_value=30, value=1)
                reason = st.text_area("Reason for Leave:")
                
                if st.button("Submit Leave Application"):
                    leave_key = "CL" if "Casual" in leave_type else "Sick" if "Sick" in leave_type else "Annual" if "Annual" in leave_type else "CO"
                    current_balance = int(w_data.get(leave_key, 0))
                    
                    if current_balance >= leave_days:
                        # Request created as Pending (No balance deduction yet)
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
                        st.success("✅ آپ کی چھٹی کی درخواست ایڈمن کو بھیج دی گئی ہے۔ اپروول کے بعد بیلنس اپڈیٹ ہوگا۔")
                        st.rerun()
                    else:
                        st.error("❌ Your requested days exceed your current available balance!")
            else:
                st.error("❌ Incorrect Identity Token (CNIC). Access Denied.")

# ==========================================
# ADMIN PORTAL
# ==========================================
else:
    st.markdown("### 🛠️ Admin Management Control Panel")
    
    admin_tab, requests_tab = st.tabs(["Manage Workers", "Pending Leave Requests"])
    
    with admin_tab:
        st.markdown("#### ➕ Register / Update Factory Worker Profile")
        w_name = st.text_input("Worker Full Name:")
        w_cnic = st.text_input("ID Card Number / CNIC (Without Dashes):")
        w_mobile = st.text_input("Mobile Number:")
        w_joining = st.date_input("Date of Joining:", value=date.today())
        
        st.markdown("##### Set Initial Leave Balances")
        c_cl = st.number_input("Casual Leave (CL) Balance:", min_value=0, value=10)
        c_sl = st.number_input("Sick Leave Balance:", min_value=0, value=8)
        c_al = st.number_input("Annual Leave Balance:", min_value=0, value=14)
        c_co = st.number_input("Compensation (CO) Leave Balance:", min_value=0, value=0)
        
        if st.button("Save Worker Registry"):
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
                st.success(f"💾 Profile for '{w_name}' has been successfully synced and saved!")
                st.rerun()
            else:
                st.error("❌ Name and Identity Token (CNIC) are mandatory fields.")
                
        if st.session_state.workers_dict:
            st.markdown("---")
            st.markdown("#### 🗑️ Remove Worker Profile")
            worker_to_delete = st.selectbox("Select Worker to Remove:", ["Select Worker"] + list(st.session_state.workers_dict.keys()))
            if worker_to_delete != "Select Worker":
                if st.button(f"Permanently Delete {worker_to_delete}"):
                    del st.session_state.workers_dict[worker_to_delete]
                    st.session_state.leave_requests = [r for r in st.session_state.leave_requests if r["worker"] != worker_to_delete]
                    save_permanent_data()
                    st.success(f"🗑️ Profile and leave records for '{worker_to_delete}' removed successfully.")
                    st.rerun()

        if st.session_state.workers_dict:
            st.markdown("---")
            st.markdown("#### 📋 Company Worker Registry Master Sheet")
            st.write(st.session_state.workers_dict)

    with requests_tab:
        st.markdown("#### 📥 Pending Applications Queue")
        
        pending_reqs = [r for r in st.session_state.leave_requests if r["status"] == "Pending"]
        
        if not pending_reqs:
            st.info("🛋️ No pending leave applications found in the queue.")
        else:
            for req in pending_reqs:
                st.write(f"**Worker:** {req['worker']} | **Type:** {req['leave_type']} | **Days:** {req['days']}")
                st.write(f"**Reason:** {req['reason']} | **Date:** {req['date']}")
                
                col_app, col_rej = st.columns(2)
                
                if col_app.button(f"✅ Okay / Approve (ID: {req['id']})"):
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
                            st.error("❌ Worker does not have enough balance left!")
                    else:
                        st.error("❌ Worker profile no longer exists.")
                
                if col_rej.button(f"❌ Reject / Cancel (ID: {req['id']})"):
                    req["status"] = "Rejected"
                    save_permanent_data()
                    st.warning("⚠️ Leave request rejected.")
                    st.rerun()
                st.markdown("---")
