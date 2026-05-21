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

# 2. Complete Premium CSS Custom Design
st.markdown("""
    <style>
    /* Main Background color */
    .stApp {
        background-color: #f5f7fa;
    }
    
    /* Main Header Banner */
    .company-banner {
        background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
        padding: 30px;
        border-radius: 12px;
        text-align: center;
        color: white;
        margin-bottom: 25px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.15);
        border-bottom: 5px solid #ffb300;
    }
    .company-banner h1 {
        color: #ffffff !important;
        font-size: 36px !important;
        font-weight: bold !important;
        margin: 0 !important;
    }
    .company-banner p {
        color: #ffb300 !important;
        font-size: 18px !important;
        margin-top: 5px !important;
    }
    
    /* Beautiful Section Cards */
    .main-box {
        background-color: #ffffff;
        padding: 25px;
        border-radius: 12px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        border-top: 5px solid #0052cc;
        margin-bottom: 20px;
    }
    
    /* Colorful Leave Balance Cards */
    .balance-card {
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        font-weight: bold;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .cl-box { background: linear-gradient(135deg, #2193b0, #6dd5ed); }
    .sl-box { background: linear-gradient(135deg, #11998e, #38ef7d); }
    .al-box { background: linear-gradient(135deg, #ff9966, #ff5e62); }
    .co-box { background: linear-gradient(135deg, #7f00ff, #e100ff); }
    
    .balance-title { font-size: 15px !important; opacity: 0.9; margin-bottom: 5px; }
    .balance-number { font-size: 32px !important; font-weight: bold; }
    
    /* Request List Style for Admin */
    .request-box {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        border-left: 6px solid #ffb300;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allowed_html=True)

# Main Banner Display
st.markdown("""
    <div class="company-banner">
        <h1>🏭 INSTAPLAST PVT LTD</h1>
        <p>✨ Automated Leave Allocation & Production Control Portal ✨</p>
    </div>
""", unsafe_allowed_html=True)

# Sidebar Design
st.sidebar.markdown("## 🔒 Control Panel")
access_role = st.sidebar.selectbox("Choose Access Role:", ["Worker", "Admin Portal"])
st.sidebar.markdown("---")
st.sidebar.markdown("<p style='color:#666;'>INSTAPLAST System Sync v2.5</p>", unsafe_allowed_html=True)

# ==========================================
# WORKER PORTAL
# ==========================================
if access_role == "Worker":
    st.markdown('<div class="main-box">', unsafe_allowed_html=True)
    st.markdown("### 👤 Employee Verification & Application")
    
    if not st.session_state.workers_dict:
        st.warning("⚠️ ڈیش بورڈ پر کوئی ورکر موجود نہیں ہے۔ برائے مہربانی ایڈمن پینل سے پہلے ورکرز کا ڈیٹا داخل کریں۔")
    else:
        worker_list = list(st.session_state.workers_dict.keys())
        selected_worker = st.selectbox("Select Profile Username:", worker_list)
        cnic_token = st.text_input("Enter Identity Token (CNIC without dashes):", type="password")
        
        if cnic_token:
            actual_cnic = st.session_state.workers_dict[selected_worker].get("cnic", "")
            if cnic_token == actual_cnic:
                st.success(f"🔓 Verification Successful. Welcome back, {selected_worker}!")
                st.markdown('</div>', unsafe_allowed_html=True) # Close Verification Card
                
                # Fetch Data & Safeguard to Integer
                w_data = st.session_state.workers_dict[selected_worker]
                cl_val = int(w_data.get("CL", 0))
                sl_val = int(w_data.get("Sick", 0))
                al_val = int(w_data.get("Annual", 0))
                co_val = int(w_data.get("CO", 0))
                
                # Premium HTML Colorful Cards Grid (CRITICAL FIXED TO PREVENT METRICS ERROR)
                st.markdown("#### 📊 Your Live Available Leave Balances")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.markdown(f'<div class="balance-card cl-box"><div class="balance-title">Casual Leave (CL)</div><div class="balance-number">{cl_val}</div></div>', unsafe_allowed_html=True)
                with col2:
                    st.markdown(f'<div class="balance-card sl-box"><div class="balance-title">Sick Leave</div><div class="balance-number">{sl_val}</div></div>', unsafe_allowed_html=True)
                with col3:
                    st.markdown(f'<div class="balance-card al-box"><div class="balance-title">Annual Leave</div><div class="balance-number">{al_val}</div></div>', unsafe_allowed_html=True)
                with col4:
                    st.markdown(f'<div class="balance-card co-box"><div class="balance-title">Compensation (CO)</div><div class="balance-number">{co_val}</div></div>', unsafe_allowed_html=True)
                
                st.markdown("<br>", unsafe_allowed_html=True)
                
                # Form Container
                st.markdown('<div class="main-box" style="border-top-color: #ffb300;">', unsafe_allowed_html=True)
                st.markdown("### 📝 Apply for Factory Leave")
                leave_type = st.selectbox("Select Leave Type:", ["Casual Leave (CL)", "Sick Leave", "Annual Leave", "Compensation (CO)"])
                leave_days = st.number_input("Number of Days Required:", min_value=1, max_value=30, value=1)
                reason = st.text_area("Reason for Leave Application:")
                
                if st.button("Submit Leave Application", use_container_width=True):
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
                        st.success("✅ آپ کی چھٹی کی درخواست ایڈمن کو بھیج دی گئی ہے۔ ایڈمن کے اوکے (Approve) کرنے پر بیلنس کٹے گا۔")
                        st.rerun()
                    else:
                        st.error("❌ Action Denied: Requested days exceed your available balance!")
                st.markdown('</div>', unsafe_allowed_html=True)
            else:
                st.error("❌ Incorrect Identity Token (CNIC). Access Denied.")
    st.markdown('</div>', unsafe_allowed_html=True)

# ==========================================
# ADMIN PORTAL
# ==========================================
else:
    st.markdown("### 🛠️ Admin Management Control Panel")
    admin_tab, requests_tab = st.tabs(["👥 Manage Workers Profiles", "📥 Pending Leave Requests Queue"])
    
    with admin_tab:
        st.markdown('<div class="main-box">', unsafe_allowed_html=True)
        st.markdown("#### ➕ Register or Update Factory Worker Profile")
        
        col_inp1, col_inp2 = st.columns(2)
        with col_inp1:
            w_name = st.text_input("Worker Full Name:")
            w_cnic = st.text_input("ID Card Number / CNIC (Without Dashes):")
        with col_inp2:
            w_mobile = st.text_input("Mobile / WhatsApp Number:")
            w_joining = st.date_input("Date of Joining Company:", value=date.today())
        
        st.markdown("##### Set Initial Leave Allocations")
        bal1, bal2, bal3, bal4 = st.columns(4)
        with bal1: c_cl = st.number_input("Casual (CL) Initial:", min_value=0, value=10)
        with bal2: c_sl = st.number_input("Sick Initial:", min_value=0, value=8)
        with bal3: c_al = st.number_input("Annual Initial:", min_value=0, value=14)
        with bal4: c_co = st.number_input("Compensation (CO) Initial:", min_value=0, value=0)
        
        if st.button("Save Worker Registry Profile", use_container_width=True):
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
                st.success(f"💾 Profile for '{w_name}' has been successfully saved and synced!")
                st.rerun()
            else:
                st.error("❌ Name and Identity Token (CNIC) are mandatory fields.")
        st.markdown('</div>', unsafe_allowed_html=True)
                
        # Delete Profiles
        if st.session_state.workers_dict:
            st.markdown('<div class="main-box" style="border-top-color: #d32f2f;">', unsafe_allowed_html=True)
            st.markdown("#### 🗑️ Remove Worker Profile from System")
            worker_to_delete = st.selectbox("Select Target Worker to Remove:", ["Select Worker"] + list(st.session_state.workers_dict.keys()))
            if worker_to_delete != "Select Worker":
                if st.button(f"Permanently Delete {worker_to_delete}", use_container_width=True):
                    del st.session_state.workers_dict[worker_to_delete]
                    st.session_state.leave_requests = [r for r in st.session_state.leave_requests if r["worker"] != worker_to_delete]
                    save_permanent_data()
                    st.success(f"🗑️ Profile for '{worker_to_delete}' removed successfully.")
                    st.rerun()
            st.markdown('</div>', unsafe_allowed_html=True)

        # Database View
        if st.session_state.workers_dict:
            st.markdown('<div class="main-box" style="border-top-color: #2e7d32;">', unsafe_allowed_html=True)
            st.markdown("#### 📋 Company Master Sheet Database View")
            st.json(st.session_state.workers_dict)
            st.markdown('</div>', unsafe_allowed_html=True)

    with requests_tab:
        st.markdown("#### 📥 Pending Applications Queue")
        pending_reqs = [r for r in st.session_state.leave_requests if r["status"] == "Pending"]
        
        if not pending_reqs:
            st.info("🛋️ All clear! No pending leave applications found in the queue.")
        else:
            for req in pending_reqs:
                st.markdown(f"""
                <div class="request-box">
                    <span style="color:#0052cc; font-size:17px; font-weight:bold;">👤 Worker Name: {req['worker']}</span><br>
                    <span style="color:#2c3e50;"><b>Leave Type:</b> {req['leave_type']} | <b>Requested Duration:</b> <span style="color:#d32f2f; font-weight:bold;">{req['days']} Days</span></span><br>
                    <span style="color:#555;"><b>Date Applied:</b> {req['date']}</span><br>
                    <span style="color:#444; font-style: italic;"><b>Reason:</b> "{req['reason']}"</span>
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
                                st.success(f"👍 Approved! {days_to_cut} days deducted.")
                                st.rerun()
                            else:
                                st.error("❌ Cannot Approve: Worker does not have sufficient balance!")
                        else:
                            st.error("❌ Worker profile no longer exists.")
                
                with col_rej:
                    if st.button(f"❌ Reject / Cancel (ID: {req['id']})", key=f"rej_{req['id']}", use_container_width=True):
                        req["status"] = "Rejected"
                        save_permanent_data()
                        st.warning("⚠️ Application Rejected. Balances left unchanged.")
                        st.rerun()
                st.markdown("<br>", unsafe_allowed_html=True)
