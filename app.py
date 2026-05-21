import streamlit as st
from datetime import datetime, date
import json
import os

# 1. Page Config Setup
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

# 2. Safe Corporate Styling (Fixed to prevent any cloud crashes)
st.markdown("<style>div.block-container{padding-top:2rem;}</style>", unsafe_allowed_html=True)

# Main Dashboard Banner (Premium Dark Blue & Gold theme)
st.markdown("""
    <div style="background: linear-gradient(135deg, #0f2027, #203a43, #2c5364); padding: 25px; border-radius: 12px; text-align: center; border-bottom: 5px solid #ffb300; margin-bottom: 25px;">
        <h1 style="color: white; margin: 0; font-size: 35px; font-weight: bold; font-family: 'Arial';">🏭 INSTAPLAST PVT LTD</h1>
        <p style="color: #ffb300; margin: 5px 0 0 0; font-size: 16px; font-weight: bold;">Time Management & Leave Allocation System</p>
    </div>
""", unsafe_allowed_html=True)

# Sidebar Access Control
st.sidebar.markdown("<h2 style='color: #0c4a6e;'>🔒 Security Gate</h2>", unsafe_allowed_html=True)
access_role = st.sidebar.selectbox("Select Dashboard View:", ["Worker", "Admin Portal"])
st.sidebar.markdown("---")
st.sidebar.caption("⚡ INSTAPLAST Factory Sync v3.0")

# ==========================================
# WORKER PORTAL
# ==========================================
if access_role == "Worker":
    # Wrapper container using Streamlit native components to ensure 100% stability
    with st.container():
        st.markdown("<h3 style='color: #0f172a;'>👤 Employee Identity Verification</h3>", unsafe_allowed_html=True)
        
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
                    
                    # Fetch Balances safely
                    w_data = st.session_state.workers_dict[selected_worker]
                    cl_val = int(w_data.get("CL", 0))
                    sl_val = int(w_data.get("Sick", 0))
                    al_val = int(w_data.get("Annual", 0))
                    co_val = int(w_data.get("CO", 0))
                    
                    st.markdown("<br><h4 style='color: #1e3a8a;'>📊 Your Live Available Leave Balances</h4>", unsafe_allowed_html=True)
                    
                    # Beautiful Grid Layout for Balances using safe styling
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.markdown(f'<div style="background: linear-gradient(135deg, #1e3a8a, #3b82f6); padding: 15px; border-radius: 10px; color: white; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);"><div style="font-size: 14px; opacity: 0.9;">Casual Leave (CL)</div><div style="font-size: 28px; font-weight: bold; margin-top: 5px;">{cl_val}</div></div>', unsafe_allowed_html=True)
                    with col2:
                        st.markdown(f'<div style="background: linear-gradient(135deg, #10b981, #059669); padding: 15px; border-radius: 10px; color: white; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);"><div style="font-size: 14px; opacity: 0.9;">Sick Leave</div><div style="font-size: 28px; font-weight: bold; margin-top: 5px;">{sl_val}</div></div>', unsafe_allowed_html=True)
                    with col3:
                        st.markdown(f'<div style="background: linear-gradient(135deg, #f97316, #ea580c); padding: 15px; border-radius: 10px; color: white; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);"><div style="font-size: 14px; opacity: 0.9;">Annual Leave</div><div style="font-size: 28px; font-weight: bold; margin-top: 5px;">{al_val}</div></div>', unsafe_allowed_html=True)
                    with col4:
                        st.markdown(f'<div style="background: linear-gradient(135deg, #8b5cf6, #7c3aed); padding: 15px; border-radius: 10px; color: white; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);"><div style="font-size: 14px; opacity: 0.9;">Compensation (CO)</div><div style="font-size: 28px; font-weight: bold; margin-top: 5px;">{co_val}</div></div>', unsafe_allowed_html=True)
                    
                    # Leave Request Form
                    st.markdown("<br><h4 style='color: #1e3a8a;'>📝 Apply for New Leave</h4>", unsafe_allowed_html=True)
                    leave_type = st.selectbox("Select Leave Type Category:", ["Casual Leave (CL)", "Sick Leave", "Annual Leave", "Compensation (CO)"])
                    leave_days = st.number_input("Number of Leave Days Required:", min_value=1, max_value=30, value=1)
                    reason = st.text_area("State Reason for Leave:")
                    
                    if st.button("Submit Leave Request to Admin", use_container_width=True):
                        leave_key = "CL" if "Casual" in leave_type else "Sick" if "Sick" in leave_type else "Annual" if "Annual" in leave_type else "CO"
                        current_balance = int(w_data.get(leave_key, 0))
                        
                        if current_balance >= leave_days:
                            # Hold control with admin (No cutting on worker end)
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
    st.markdown("<h3 style='color: #0f172a;'>🛠️ Admin Management Control Panel</h3>", unsafe_allowed_html=True)
    admin_tab, requests_tab = st.tabs(["👥 Manage Workers Profiles", "📥 Pending Leave Requests"])
    
    with admin_tab:
        st.markdown("<h4 style='color: #1e3a8a;'>➕ Register New Factory Worker</h4>", unsafe_allowed_html=True)
        
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
            st.markdown("<hr><h4 style='color: #b91c1c;'>🗑️ Remove Profile From Records</h4>", unsafe_allowed_html=True)
            worker_to_delete = st.selectbox("Select Worker to Remove:", ["Select Worker"] + list(st.session_state.workers_dict.keys()))
            if worker_to_delete != "Select Worker":
                if st.button(f"Permanently Delete {worker_to_delete}", use_container_width=True):
                    del st.session_state.workers_dict[worker_to_delete]
                    st.session_state.leave_requests = [r for r in st.session_state.leave_requests if r["worker"] != worker_to_delete]
                    save_permanent_data()
                    st.success(f"🗑️ Profile data for '{worker_to_delete}' has been completely wiped out.")
                    st.rerun()

        # Company Master View Matrix
        if st.session_state.workers_dict:
            st.markdown("<hr>#### 📋 Factory Database Master Sheet View")
            st.json(st.session_state.workers_dict)

    with requests_tab:
        st.markdown("<h4 style='color: #1e3a8a;'>📥 Incoming Leave Applications Queue</h4>", unsafe_allowed_html=True)
        pending_reqs = [r for r in st.session_state.leave_requests if r["status"] == "Pending"]
        
        if not pending_reqs:
            st.info("🛋️ All clear! No pending leave applications found in the queue.")
        else:
            for req in pending_reqs:
                st.markdown(f"""
                    <div style="background-color: white; padding: 20px; border-radius: 8px; border-left: 6px solid #ffb300; box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 15px;">
                        <strong style="color: #1e3a8a; font-size: 16px;">👤 Worker: {req['worker']}</strong><br>
                        <span style="color: #334155;"><b>Category:</b> {req['leave_type']} | <b>Requested Duration:</b> <span style="color: #b91c1c; font-weight: bold;">{req['days']} Days</span></span><br>
                        <span style="color: #64748b; font-size: 13px;"><b>Date Received:</b> {req['date']}</span><br>
                        <div style="background-color: #f8fafc; padding: 10px; border-radius: 5px; margin-top: 8px; color: #475569; font-style: italic;">"Reason: {req['reason']}"</div>
                    </div>
                """, unsafe_allowed_html=True)
                
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
                                st.success(f"👍 Approved! {days_to_cut} days deducted from {w_name}.")
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
                st.markdown("<br>", unsafe_allowed_html=True)
