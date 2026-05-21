import streamlit as st
from datetime import datetime, date
import calendar
import json
import os

# 1. Page Config Setup
st.set_page_config(page_title="INSTAPLAST Leave Portal", page_icon="🏭", layout="wide")

# File path to permanently store data on local disk / cloud container
DATA_FILE = "workers_data.json"

# Helper function to load data from JSON file safely
def load_permanent_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
                # Ensure structure is correct
                if "workers" not in data:
                    data["workers"] = {}
                if "requests" not in data:
                    data["requests"] = []
                return data
        except:
            return {"workers": {}, "requests": []}
    return {"workers": {}, "requests": []}

# Helper function to save data to JSON file safely
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

# Initialize Session States from permanent file
if "db_loaded" not in st.session_state:
    db = load_permanent_data()
    st.session_state.workers_dict = db["workers"]
    st.session_state.leave_requests = db["requests"]
    st.session_state.db_loaded = True

# 2. Clean Corporate Theme Styling
st.markdown("""
    <style>
    .main-header {
        background-color: #0d47a1;
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 25px;
    }
    .sub-card {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid #0d47a1;
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allowed_html=True)

# Main Brand Header Banner
st.markdown("""
    <div class="main-header">
        <h1>🏭 INSTAPLAST PVT LTD</h1>
        <p>Time Management & Leave Allocation System</p>
    </div>
""", unsafe_allowed_html=True)

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
                
                # Show Current Balances
                w_data = st.session_state.workers_dict[selected_worker]
                st.markdown("#### 📊 Your Current Available Leave Balance")
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Casual Leave (CL)", w_data.get("CL", 0))
                col2.metric("Sick Leave", w_data.get("Sick", 0))
                col3.metric("Annual Leave", w_data.get("Annual", 0))
                col4.metric("Compensation (CO)", w_data.get("CO", 0))
                
                # Leave Application Form
                st.markdown("### 📝 Apply for New Leave")
                leave_type = st.selectbox("Select Leave Type:", ["Casual Leave (CL)", "Sick Leave", "Annual Leave", "Compensation (CO)"])
                leave_days = st.number_input("Number of Days Required:", min_value=1, max_value=30, value=1)
                reason = st.text_area("Reason for Leave:")
                
                if st.button("Submit Leave Application"):
                    # Map Selection to Key
                    leave_key = "CL" if "Casual" in leave_type else "Sick" if "Sick" in leave_type else "Annual" if "Annual" in leave_type else "CO"
                    current_balance = w_data.get(leave_key, 0)
                    
                    if current_balance >= leave_days:
                        # CRITICAL FIX: DO NOT CUT BALANCE HERE. Just create a pending request.
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
                        save_permanent_data() # Save to file
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
                    "CL": c_cl,
                    "Sick": c_sl,
                    "Annual": c_al,
                    "CO": c_co
                }
                save_permanent_data()
                st.success(f"💾 Profile for '{w_name}' has been successfully synced and saved!")
                st.rerun()
            else:
                st.error("❌ Name and Identity Token (CNIC) are mandatory fields.")
                
        # Delete/Remove Option
        if st.session_state.workers_dict:
            st.markdown("#### 🗑️ Remove Worker Profile")
            worker_to_delete = st.selectbox("Select Worker to Remove:", ["Select Worker"] + list(st.session_state.workers_dict.keys()))
            if worker_to_delete != "Select Worker":
                if st.button(f"Permanently Delete {worker_to_delete}"):
                    del st.session_state.workers_dict[worker_to_delete]
                    # Also remove pending requests for this worker to clean database
                    st.session_state.leave_requests = [r for r in st.session_state.leave_requests if r["worker"] != worker_to_delete]
                    save_permanent_data()
                    st.success(f"🗑️ Profile and leave records for '{worker_to_delete}' removed successfully.")
                    st.rerun()

        # View Master Sheet Data
        if st.session_state.workers_dict:
            st.markdown("#### 📋 Company Worker Registry Master Sheet")
            st.write(st.session_state.workers_dict)

    with requests_tab:
        st.markdown("#### 📥 Pending Applications Queue")
        
        pending_reqs = [r for r in st.session_state.leave_requests if r["status"] == "Pending"]
        
        if not pending_reqs:
            st.info("🛋️ No pending leave applications found in the queue.")
        else:
            for req in pending_reqs:
                st.markdown(f"""
                <div class="sub-card">
                    <b>Worker Name:</b> {req['worker']} <br>
                    <b>Leave Category:</b> {req['leave_type']} | <b>Requested Days:</b> {req['days']} Days <br>
                    <b>Applied Date:</b> {req['date']} <br>
                    <b>Reason provided:</b> {req['reason']}
                </div>
                """, unsafe_allowed_html=True)
                
                col_app, col_rej = st.columns(2)
                
                # APPROVE BUTTON - CUTS BALANCE HERE ONLY
                if col_app.button(f"✅ Okay / Approve (ID: {req['id']})"):
                    w_name = req['worker']
                    l_key = req['leave_type']
                    days_to_cut = req['days']
                    
                    # Double Check if worker exists and has balance
                    if w_name in st.session_state.workers_dict:
                        current_bal = st.session_state.workers_dict[w_name].get(l_key, 0)
                        if current_bal >= days_to_cut:
                            # Actual balance cutting happens here now!
                            st.session_state.workers_dict[w_name][l_key] -= days_to_cut
                            req["status"] = "Approved"
                            save_permanent_data()
                            st.success(f"👍 Approved! {days_to_cut} days deducted from {w_name}'s {l_key} balance.")
                            st.rerun()
                        else:
                            st.error("❌ Worker does not have enough balance left to approve this leave!")
                    else:
                        st.error("❌ Worker profile no longer exists in database.")
                
                # REJECT BUTTON - NO BALANCE DEDUCTION
                if col_rej.button(f"❌ Reject / Cancel (ID: {req['id']})"):
                    req["status"] = "Rejected"
                    save_permanent_data()
                    st.warning("⚠️ Leave request rejected. No changes made to balance.")
                    st.rerun()
